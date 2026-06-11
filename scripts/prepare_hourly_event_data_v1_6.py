#!/usr/bin/env python3
"""Phase 1: Prepare hourly event data for v1.6 event study.

Downloads 1h klines for all v1.5 events (±3 days), loads existing fundingRate
archives, and builds a merged hourly event panel.

Output: reports/artifacts/binance_hourly_event_study_v1_6/
  - hourly_event_panel.pkl   — per-event, per-hour rows with OHLCV + funding + event meta
  - manifest.json            — metadata and stats
  - download_stats.csv       — per-symbol download status

Data sources:
  - 1h klines: Binance S3 monthly archive (data.binance.vision)
  - fundingRate: already cached at data/binance_vision_rank154/data/futures/um/monthly/fundingRate/
  - v1.5 events: jerry/wlfi/FR_Monitor/reports/artifacts/binance_daily_event_study_v1_5/
"""
from __future__ import annotations

import io
import json
import time
import zipfile
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
V1_5_EVENTS = ROOT / "jerry/wlfi/FR_Monitor/reports/artifacts/binance_daily_event_study_v1_5/enriched_gainer_events_v1_5.csv"

KLINE_CACHE = ROOT / "data/binance_vision_1h_v1_6/klines"  # consolidated flat cache: <sym>/<sym>-1h-<YYYY-MM>.zip
FUNDING_DIR = ROOT / "data/binance_vision_rank154/data/futures/um/monthly/fundingRate"
OUT_DIR = ROOT / "reports/artifacts/binance_hourly_event_study_v1_6"

S3_BASE = "https://data.binance.vision"

MAX_WORKERS = 32
DAYS_BUFFER = 3  # ±3 days around event date


# ── I/O helpers ────────────────────────────────────────────────────────────

def http_get(url: str, timeout: int = 45) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "v1.6-hourly-prepare/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def cached_download(url: str, path: Path, retries: int = 2) -> bytes | None:
    if path.exists() and path.stat().st_size > 0:
        return path.read_bytes()
    path.parent.mkdir(parents=True, exist_ok=True)
    last_err = None
    for attempt in range(retries + 1):
        try:
            data = http_get(url)
            if data and not data.startswith(b"<Error>"):
                tmp = path.with_suffix(path.suffix + ".tmp")
                tmp.write_bytes(data)
                tmp.replace(path)
                return data
        except Exception as e:
            last_err = e
            time.sleep(0.4 * (attempt + 1))
    return None


def read_zip_csv(data: bytes) -> pd.DataFrame:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        names = [n for n in zf.namelist() if n.endswith(".csv")]
        if not names:
            return pd.DataFrame()
        with zf.open(names[0]) as f:
            return pd.read_csv(f)


# ── 1h kline helpers ──────────────────────────────────────────────────────

def normalize_1h(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """Normalize raw 1h kline CSV from Binance archive."""
    if df.empty:
        return df
    # Binance archive has two column variants:
    #   Newer: open_time,open,high,low,close,close_time,volume,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore
    #   Older: open_time,open,high,low,close,close_time,volume,quote_volume,trades,taker_buy_base,taker_buy_quote,ignore
    # We handle both by normalizing column names first.
    col_rename = {
        "count": "trades",
        "taker_buy_volume": "taker_buy_base",
    }
    df = df.rename(columns=col_rename)
    out = pd.DataFrame({
        "ts": pd.to_datetime(pd.to_numeric(df["open_time"], errors="coerce"), unit="ms", utc=True),
        "symbol": symbol,
        "open": pd.to_numeric(df["open"], errors="coerce"),
        "high": pd.to_numeric(df["high"], errors="coerce"),
        "low": pd.to_numeric(df["low"], errors="coerce"),
        "close": pd.to_numeric(df["close"], errors="coerce"),
        "volume": pd.to_numeric(df["volume"], errors="coerce"),
        "quote_volume": pd.to_numeric(df["quote_volume"], errors="coerce"),
        "trades": pd.to_numeric(df.get("trades", df.get("count", pd.Series(dtype=float))), errors="coerce"),
        "taker_buy_quote_volume": pd.to_numeric(df.get("taker_buy_quote_volume", df.get("taker_buy_quote", pd.Series(dtype=float))), errors="coerce"),
    }).dropna(subset=["ts", "close"])
    return out


def fetch_1h_month(symbol: str, month: str) -> pd.DataFrame | None:
    """Download and cache one month of 1h klines for a symbol."""
    cache_path = KLINE_CACHE / symbol / f"{symbol}-1h-{month}.zip"
    url = f"{S3_BASE}/data/futures/um/monthly/klines/{symbol}/1h/{symbol}-1h-{month}.zip"
    data = cached_download(url, cache_path)
    if data is None:
        return None
    try:
        return normalize_1h(read_zip_csv(data), symbol)
    except Exception:
        return None


# ── Funding helpers ────────────────────────────────────────────────────────

def load_funding_for_symbol(symbol: str) -> pd.DataFrame:
    """Load all fundingRate history for one symbol from local cache.

    The archive contains per-settlement records with:
      - calc_time: settlement timestamp (ms)
      - funding_interval_hours: actual interval at that settlement (1, 2, 4, or 8)
      - last_funding_rate: the settled rate

    ⚠️ IMPORTANT: funding_interval_hours can CHANGE over a symbol's lifetime.
    E.g. DOLO went from 8h → 4h at some point. We preserve all records with
    their actual timestamps so merge_asof handles this correctly.
    """
    sym_dir = FUNDING_DIR / symbol
    if not sym_dir.exists():
        return pd.DataFrame()
    files = sorted(sym_dir.glob(f"{symbol}-fundingRate-*.zip"))
    if not files:
        return pd.DataFrame()
    frames = []
    for f in files:
        try:
            with zipfile.ZipFile(f) as zf:
                names = [n for n in zf.namelist() if n.endswith(".csv")]
                if names:
                    with zf.open(names[0]) as fh:
                        frames.append(pd.read_csv(fh))
        except Exception:
            continue
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    df["ts"] = pd.to_datetime(pd.to_numeric(df["calc_time"], errors="coerce"), unit="ms", utc=True)
    df["funding_rate"] = pd.to_numeric(df["last_funding_rate"], errors="coerce")
    df["funding_interval_hours"] = pd.to_numeric(df["funding_interval_hours"], errors="coerce")
    df = df.dropna(subset=["ts", "funding_rate"]).sort_values("ts").drop_duplicates("ts")
    return df[["ts", "funding_rate", "funding_interval_hours"]]


def attach_funding_to_hourly(hourly: pd.DataFrame, funding: pd.DataFrame) -> pd.DataFrame:
    """Merge funding rate onto hourly kline timestamps.

    For each hourly bar, find the most recent funding settlement that occurred
    at or before that bar's timestamp (merge_asof, direction='backward').

    This correctly handles variable intervals because we use actual settlement
    timestamps, not assumed periodicity.
    """
    if funding.empty:
        hourly = hourly.copy()
        hourly["funding_rate"] = np.nan
        hourly["funding_interval_hours"] = np.nan
        hourly["funding_settlement_ts"] = pd.NaT
        return hourly

    hourly = hourly.sort_values("ts").reset_index(drop=True)
    funding_sorted = funding.sort_values("ts").reset_index(drop=True)

    merged = pd.merge_asof(
        hourly,
        funding_sorted.rename(columns={
            "ts": "funding_settlement_ts",
            "funding_rate": "funding_rate",
            "funding_interval_hours": "funding_interval_hours",
        }),
        left_on="ts",
        right_on="funding_settlement_ts",
        direction="backward",
    )
    return merged


# ── Month range helper ────────────────────────────────────────────────────

def months_for_range(start_date, end_date):
    months = set()
    d = start_date
    while d <= end_date:
        months.add(d.strftime("%Y-%m"))
        if d.month == 12:
            d = d.replace(year=d.year + 1, month=1, day=1)
        else:
            d = d.replace(month=d.month + 1, day=1)
    return sorted(months)


# ── Main pipeline ─────────────────────────────────────────────────────────

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ── Step 1: Load v1.5 events ──────────────────────────────────────────
    print("[step 1] Loading v1.5 events...")
    events = pd.read_csv(V1_5_EVENTS)
    events["event_date"] = pd.to_datetime(events["event_date"])
    print(f"  {len(events)} events, {events['symbol'].nunique()} symbols, "
          f"{events['event_date'].min().date()} to {events['event_date'].max().date()}")

    # ── Step 2: Compute required (symbol, month) for 1h klines ────────────
    print("[step 2] Computing required 1h kline files...")
    needed_kline = set()
    for _, row in events.iterrows():
        sym = row["symbol"]
        ed = row["event_date"]
        start = (ed - timedelta(days=DAYS_BUFFER))
        end = (ed + timedelta(days=DAYS_BUFFER))
        for m in months_for_range(start, end):
            needed_kline.add((sym, m))
    print(f"  {len(needed_kline)} unique (symbol, month) combos needed")

    # Scan cache for existing files
    cached = set()
    if KLINE_CACHE.exists():
        for sym_dir in KLINE_CACHE.iterdir():
            if sym_dir.is_dir():
                for f in sym_dir.glob(f"{sym_dir.name}-1h-*.zip"):
                    parts = f.name.split("-")
                    if len(parts) >= 4:
                        month = parts[2] + "-" + parts[3][:2]
                        cached.add((sym_dir.name, month))
    to_download = needed_kline - cached
    print(f"  Already cached: {len(cached)}, to download: {len(to_download)}")

    # ── Step 3: Download missing 1h klines ────────────────────────────────
    print(f"[step 3] Downloading {len(to_download)} 1h kline files (workers={MAX_WORKERS})...")
    download_tasks = sorted(to_download)
    results = {"ok": 0, "fail": 0}
    download_log = []

    def dl_one(task):
        sym, month = task
        t0 = time.time()
        df = fetch_1h_month(sym, month)
        elapsed = time.time() - t0
        status = "ok" if (df is not None and not df.empty) else "fail"
        n_rows = len(df) if df is not None else 0
        return sym, month, status, n_rows, round(elapsed, 2)

    done = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = {ex.submit(dl_one, t): t for t in download_tasks}
        for fut in as_completed(futs):
            sym, month, status, n_rows, elapsed = fut.result()
            results[status] += 1
            download_log.append({"symbol": sym, "month": month, "status": status,
                                 "rows": n_rows, "elapsed_s": elapsed})
            done += 1
            if done % 500 == 0 or done == len(download_tasks):
                print(f"  {done}/{len(download_tasks)} "
                      f"(ok={results['ok']}, fail={results['fail']})")

    dl_df = pd.DataFrame(download_log)
    dl_df.to_csv(OUT_DIR / "download_stats.csv", index=False)
    print(f"  Download complete: ok={results['ok']}, fail={results['fail']}")

    # ── Step 4: Load all 1h klines into memory ────────────────────────────
    print("[step 4] Loading 1h klines from cache...")
    symbols_needed = set(events["symbol"].unique())
    kline_data = {}
    missing_syms = []

    def load_1h_from_dir(cache_dir: Path, sym: str) -> pd.DataFrame | None:
        """Try to load all monthly 1h kline zips for a symbol from a flat cache dir."""
        if not cache_dir.exists():
            return None
        sym_dir = cache_dir / sym
        if not sym_dir.exists():
            return None
        files = sorted(sym_dir.glob(f"{sym}-1h-*.zip"))
        if not files:
            return None
        frames = []
        for f in files:
            try:
                with zipfile.ZipFile(f) as zf:
                    names = [n for n in zf.namelist() if n.endswith(".csv")]
                    if names:
                        with zf.open(names[0]) as fh:
                            raw = pd.read_csv(fh)
                            norm = normalize_1h(raw, sym)
                            if not norm.empty:
                                frames.append(norm)
            except Exception:
                continue
        if not frames:
            return None
        return pd.concat(frames, ignore_index=True).sort_values("ts").drop_duplicates("ts")

    for sym in sorted(symbols_needed):
        df = load_1h_from_dir(KLINE_CACHE, sym)
        if df is not None and not df.empty:
            kline_data[sym] = df
        else:
            missing_syms.append(sym)

    print(f"  Loaded 1h klines for {len(kline_data)} symbols, missing {len(missing_syms)}")
    if missing_syms:
        print(f"  Missing: {missing_syms[:20]}{'...' if len(missing_syms) > 20 else ''}")

    # ── Step 5: Load all funding data ─────────────────────────────────────
    print("[step 5] Loading fundingRate archives...")
    funding_data = {}
    funding_loaded = 0
    for sym in symbols_needed:
        fdf = load_funding_for_symbol(sym)
        if not fdf.empty:
            funding_data[sym] = fdf
            funding_loaded += 1
    print(f"  Loaded funding for {funding_loaded}/{len(symbols_needed)} symbols")

    # ── Step 6: Build hourly event panel ──────────────────────────────────
    print(f"[step 6] Building hourly event panel for {len(events)} events...")
    panel_rows = []
    stats = {"ok": 0, "no_kline": 0, "empty_window": 0}

    for i, (_, ev) in enumerate(events.iterrows()):
        sym = ev["symbol"]
        ed = pd.Timestamp(ev["event_date"], tz="UTC")

        if sym not in kline_data:
            stats["no_kline"] += 1
            continue

        # Window: [T-1day, T+5days) — T-1 for pre-event context
        window_start = ed - timedelta(days=1)
        window_end = ed + timedelta(days=5)

        kdf = kline_data[sym]
        hw = kdf[(kdf["ts"] >= window_start) & (kdf["ts"] < window_end)].copy()
        if hw.empty:
            stats["empty_window"] += 1
            continue

        # Attach funding (merge_asof with actual settlement timestamps)
        if sym in funding_data:
            hw = attach_funding_to_hourly(hw, funding_data[sym])
        else:
            hw["funding_rate"] = np.nan
            hw["funding_interval_hours"] = np.nan
            hw["funding_settlement_ts"] = pd.NaT

        # Compute derived columns
        hw["event_date"] = ed
        hw["hours_from_event"] = (hw["ts"] - ed).dt.total_seconds() / 3600.0
        hw["taker_buy_ratio"] = (
            hw["taker_buy_quote_volume"] / hw["quote_volume"].clip(lower=1e-8)
            if "taker_buy_quote_volume" in hw.columns else np.nan
        )

        # Copy event-level metadata
        for col in ["tags", "carry_raw", "funding_bucket", "structure",
                     "structure_relaxed", "vol_structure", "funding_traj",
                     "fwd_ret_1d", "fwd_ret_3d", "fwd_ret_5d", "fwd_ret_10d",
                     "long_total_ret_5d", "short_total_ret_5d"]:
            if col in ev.index:
                hw[f"ev_{col}"] = ev[col]

        panel_rows.append(hw)
        stats["ok"] += 1

        if (i + 1) % 5000 == 0:
            print(f"  processed {i + 1}/{len(events)} "
                  f"(ok={stats['ok']}, no_kline={stats['no_kline']})")

    print(f"  Panel building: {stats}")

    # ── Step 7: Concatenate and save ──────────────────────────────────────
    print("[step 7] Saving hourly event panel...")
    if panel_rows:
        panel = pd.concat(panel_rows, ignore_index=True)
        panel.to_pickle(OUT_DIR / "hourly_event_panel.pkl")
        print(f"  Saved: {len(panel):,} rows, "
              f"{panel['symbol'].nunique()} symbols, "
              f"{panel['event_date'].nunique()} events")
        # Quick sanity check
        sample_event = panel.groupby("event_date").size()
        print(f"  Hours per event: median={sample_event.median():.0f}, "
              f"mean={sample_event.mean():.0f}, "
              f"min={sample_event.min()}, max={sample_event.max()}")
    else:
        print("  ERROR: No panel rows produced!")
        panel = pd.DataFrame()

    # ── Step 8: Save manifest ─────────────────────────────────────────────
    manifest = {
        "version": "v1_6_phase1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_events": str(V1_5_EVENTS),
        "n_events_total": len(events),
        "n_events_in_panel": stats["ok"],
        "n_events_no_kline": stats["no_kline"],
        "n_events_empty_window": stats["empty_window"],
        "n_panel_rows": len(panel) if not panel.empty else 0,
        "n_symbols": int(panel["symbol"].nunique()) if not panel.empty else 0,
        "kline_files_downloaded_new": results.get("ok", 0),
        "kline_files_failed": results.get("fail", 0),
        "funding_symbols_loaded": funding_loaded,
        "days_buffer": DAYS_BUFFER,
        "window": "[-1d, +5d) around event",
    }
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2, default=str))
    print(f"\n✓ Done. Output in {OUT_DIR}")


if __name__ == "__main__":
    main()
