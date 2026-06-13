#!/usr/bin/env python3
"""Build monthly-volume dynamic universe for factor library.

For each calendar month M:
    - Use only previous full calendar month M-1
    - Sum Binance UM perpetual 1d quote_volume
    - Sort descending, select top N symbols
    - Universe is active for month M

Usage:
    python scripts/build_dynamic_universe_monthly_volume.py \
        --universe-id crypto_usdt_perp_monthly_volume_top50_current_listed_v1 \
        --start 2024-06-13 \
        --end 2026-06-13 \
        --top-n 50 \
        --rank-metric quote_volume \
        --selection-frequency monthly
"""
from __future__ import annotations

import argparse
import io
import json
import re
import time
import urllib.error
import urllib.request
import zipfile
from datetime import timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "universe"
CACHE_DIR = ROOT / "data" / "cache" / "dynamic_universe_build"

BINANCE_EXCHANGE_INFO = "https://fapi.binance.com/fapi/v1/exchangeInfo"
DATA_VISION_MONTHLY_1D = "https://data.binance.vision/data/futures/um/monthly/klines/{symbol}/1d/{symbol}-1d-{ym}.zip"
DATA_VISION_DAILY_1D = "https://data.binance.vision/data/futures/um/daily/klines/{symbol}/1d/{symbol}-1d-{ymd}.zip"


# ── Helpers ───────────────────────────────────────────────────────

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def to_iso(ts: pd.Timestamp) -> str:
    return ts.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_base_asset(base: str) -> str:
    return re.sub(r"^\d+", "", base.lower())


def contract_multiplier_from_base(base: str) -> float:
    m = re.match(r"^(\d+)", str(base))
    return float(m.group(1)) if m else 1.0


def month_range(start: pd.Timestamp, end: pd.Timestamp) -> list[str]:
    """Generate YYYY-MM strings from start to end (inclusive)."""
    cur = pd.Timestamp(start.year, start.month, 1, tz="UTC")
    end_month = pd.Timestamp(end.year, end.month, 1, tz="UTC")
    out = []
    while cur <= end_month:
        out.append(cur.strftime("%Y-%m"))
        cur = cur + pd.offsets.MonthBegin(1)
    return out


# ── HTTP helpers (neutral, no rank213 dependency) ─────────────────

def _retry_after(err: urllib.error.HTTPError, default: float, attempt: int) -> float:
    hdr = None
    try:
        hdr = err.headers.get("Retry-After") if err.headers else None
    except Exception:
        pass
    if hdr:
        try:
            return max(float(hdr), default)
        except Exception:
            pass
    if err.code == 418:
        return max(60.0, default * (attempt + 1) * 5.0)
    return max(default, default * (attempt + 1))


def safe_json_request(url: str, *, retries: int = 6, sleep_sec: float = 2.0):
    headers = {"User-Agent": "Mozilla/5.0"}
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in {418, 429, 500, 502, 503, 504} and attempt + 1 < retries:
                time.sleep(_retry_after(e, sleep_sec, attempt))
                continue
            raise
        except Exception as e:
            last_err = e
            if attempt + 1 < retries:
                time.sleep(sleep_sec * (attempt + 1))
                continue
            raise
    raise RuntimeError(f"failed: {url} ({last_err})")


def safe_download(url: str, dst: Path, *, retries: int = 7, sleep_sec: float = 2.0) -> bool:
    ensure_dir(dst.parent)
    if dst.exists() and dst.stat().st_size > 0:
        return True
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                blob = r.read()
            dst.write_bytes(blob)
            return True
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code == 404:
                return False
            if e.code in {418, 429, 500, 502, 503, 504} and attempt + 1 < retries:
                time.sleep(_retry_after(e, sleep_sec, attempt))
                continue
            raise
        except (urllib.error.URLError, ConnectionResetError, TimeoutError) as e:
            last_err = e
            if attempt + 1 < retries:
                time.sleep(max(sleep_sec, sleep_sec * (attempt + 1)))
                continue
            raise
        except Exception as e:
            last_err = e
            if attempt + 1 < retries:
                time.sleep(max(sleep_sec, sleep_sec * (attempt + 1)))
                continue
            raise
    raise RuntimeError(f"failed: {url} ({last_err})")


def read_kline_zip(path: Path) -> pd.DataFrame:
    """Parse Binance kline zip into DataFrame with timestamp, close, quote_volume."""
    blob = path.read_bytes()
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        members = zf.namelist()
        if not members:
            return pd.DataFrame(columns=["timestamp", "close", "quote_volume"])
        data = zf.read(members[0])
    df = pd.read_csv(
        io.BytesIO(data),
        header=None,
        names=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_volume", "trade_count", "taker_base", "taker_quote", "ignore",
        ],
    )
    df["open_time"] = pd.to_numeric(df["open_time"], errors="coerce")
    for col in ["close", "quote_volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["open_time", "close"])
    if df.empty:
        return pd.DataFrame(columns=["timestamp", "close", "quote_volume"])
    return pd.DataFrame({
        "timestamp": pd.to_datetime(df["open_time"].astype("int64"), unit="ms", utc=True),
        "close": df["close"].astype(float),
        "quote_volume": df["quote_volume"].astype(float),
    }).drop_duplicates("timestamp").sort_values("timestamp")


# ── Candidate pool ────────────────────────────────────────────────

def fetch_candidate_pool(cache_dir: Path) -> pd.DataFrame:
    """Fetch Binance UM exchangeInfo and build candidate pool.

    Filters: quoteAsset=USDT, contractType=PERPETUAL, status=TRADING.
    This is current-listed only — delisted historical symbols are NOT included.
    """
    exchange_cache = cache_dir / "binance_exchange_info.json"
    if exchange_cache.exists():
        ex = json.loads(exchange_cache.read_text(encoding="utf-8"))
    else:
        ex = safe_json_request(BINANCE_EXCHANGE_INFO)
        ensure_dir(cache_dir)
        exchange_cache.write_text(json.dumps(ex), encoding="utf-8")

    rows = []
    for s in ex["symbols"]:
        if s.get("quoteAsset") != "USDT":
            continue
        if s.get("contractType") != "PERPETUAL":
            continue
        if s.get("status") != "TRADING":
            continue
        symbol = str(s["symbol"])
        base = str(s.get("baseAsset", ""))
        if not re.fullmatch(r"[A-Z0-9]+USDT", symbol):
            continue
        if not re.fullmatch(r"[A-Z0-9]+", base):
            continue
        rows.append({
            "symbol": symbol,
            "base_asset": base,
            "normalized_base": normalize_base_asset(base),
            "contract_multiplier": contract_multiplier_from_base(base),
            "onboard_utc": to_iso(pd.to_datetime(int(s["onboardDate"]), unit="ms", utc=True)),
            "onboard_ms": int(s["onboardDate"]),
            "quote_asset": "USDT",
            "contract_type": "PERPETUAL",
            "status": "TRADING",
            "source": "binance_fapi_exchangeInfo",
        })
    return pd.DataFrame(rows).sort_values(["onboard_ms", "symbol"]).reset_index(drop=True)


# ── Daily quote_volume fetch ──────────────────────────────────────

def load_daily_quote_volume(symbol: str, start: pd.Timestamp, end: pd.Timestamp, cache_dir: Path) -> pd.DataFrame:
    """Load daily 1d klines for a symbol, return timestamp + quote_volume."""
    cache_path = cache_dir / "daily_1d" / f"{symbol}.csv"
    need_start = start.floor("1D")
    need_end = end.floor("1D")

    # Check cache
    if cache_path.exists():
        old = pd.read_csv(cache_path)
        old["timestamp"] = pd.to_datetime(old["timestamp"], utc=True, errors="coerce")
        old["quote_volume"] = pd.to_numeric(old["quote_volume"], errors="coerce")
        old = old.dropna(subset=["timestamp"]).drop_duplicates("timestamp").sort_values("timestamp")
        if not old.empty and old["timestamp"].min() <= need_start and old["timestamp"].max() >= need_end - pd.Timedelta(days=1):
            return old[(old["timestamp"] >= need_start) & (old["timestamp"] <= need_end)].reset_index(drop=True)
    else:
        old = pd.DataFrame(columns=["timestamp", "quote_volume"])

    months = month_range(need_start, need_end)
    current_month = need_end.strftime("%Y-%m")
    parts: list[pd.DataFrame] = [old] if not old.empty else []

    for ym in months:
        if ym == current_month:
            continue
        p = cache_dir / "raw_1d" / "monthly" / symbol / f"{symbol}-1d-{ym}.zip"
        ok = safe_download(DATA_VISION_MONTHLY_1D.format(symbol=symbol, ym=ym), p)
        if ok:
            part = read_kline_zip(p)
            if not part.empty:
                parts.append(part)
        time.sleep(0.003)

    # Current month: use daily files
    cur = pd.Timestamp(need_end.year, need_end.month, 1, tz="UTC")
    if cur < need_start.normalize():
        cur = need_start.normalize()
    while cur <= need_end.normalize():
        ymd = cur.strftime("%Y-%m-%d")
        p = cache_dir / "raw_1d" / "daily" / symbol / f"{symbol}-1d-{ymd}.zip"
        ok = safe_download(DATA_VISION_DAILY_1D.format(symbol=symbol, ymd=ymd), p)
        if ok:
            part = read_kline_zip(p)
            if not part.empty:
                parts.append(part)
        cur += pd.Timedelta(days=1)
        time.sleep(0.001)

    if not parts:
        return pd.DataFrame(columns=["timestamp", "quote_volume"])

    out = pd.concat(parts, ignore_index=True).drop_duplicates("timestamp").sort_values("timestamp")
    out = out[["timestamp", "quote_volume"]].copy()
    ensure_dir(cache_path.parent)
    out.to_csv(cache_path, index=False)
    return out[(out["timestamp"] >= need_start) & (out["timestamp"] <= need_end)].reset_index(drop=True)


# ── Monthly universe construction ─────────────────────────────────

def build_monthly_universe(
    candidates: pd.DataFrame,
    start: pd.Timestamp,
    end: pd.Timestamp,
    top_n: int,
    rank_metric: str,
    universe_id: str,
    cache_dir: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build monthly universe snapshots and selection detail.

    Returns (universe_snapshots, monthly_selection_detail).
    """
    month_starts = pd.date_range(
        start=pd.Timestamp(start.year, start.month, 1, tz="UTC"),
        end=pd.Timestamp(end.year, end.month, 1, tz="UTC"),
        freq="MS",
        tz="UTC",
    )

    # Pre-fetch daily data for all candidates
    print(f"  Fetching daily 1d klines for {len(candidates)} candidates...")
    daily_cache: dict[str, pd.DataFrame] = {}
    for i, (_, cand) in enumerate(candidates.iterrows()):
        sym = cand["symbol"]
        daily = load_daily_quote_volume(sym, start - pd.Timedelta(days=40), end + pd.Timedelta(days=7), cache_dir)
        if not daily.empty:
            daily_cache[sym] = daily
        if (i + 1) % 50 == 0:
            print(f"    {i+1}/{len(candidates)} fetched")

    print(f"  Daily data cached for {len(daily_cache)} symbols")

    snapshot_rows = []
    detail_rows = []
    prev_selected: set[str] = set()

    for month_start in month_starts:
        prev_month_start = month_start - pd.offsets.MonthBegin(1)

        eligible = []
        for _, cand in candidates.iterrows():
            sym = cand["symbol"]
            onboard = pd.to_datetime(int(cand["onboard_ms"]), unit="ms", utc=True)

            # Symbol must be listed before month_start
            if onboard > month_start:
                continue

            daily = daily_cache.get(sym)
            if daily is None or daily.empty:
                continue

            sub = daily[(daily["timestamp"] >= prev_month_start) & (daily["timestamp"] < month_start)].copy()
            if sub.empty:
                continue

            qv = pd.to_numeric(sub["quote_volume"], errors="coerce").fillna(0.0)
            qv_sum = float(qv.sum())
            if not np.isfinite(qv_sum) or qv_sum <= 0:
                continue

            eligible.append((sym, qv_sum))

        # Sort and select top N
        eligible.sort(key=lambda x: x[1], reverse=True)
        selected_with_metrics = eligible[:top_n]
        selected = [sym for sym, _ in selected_with_metrics]
        selected_set = set(selected)

        entered = sorted(selected_set - prev_selected)
        exited = sorted(prev_selected - selected_set)

        # Build snapshot rows for each selected symbol
        for rank_idx, (sym, qv_sum) in enumerate(selected_with_metrics):
            cand_row = candidates[candidates["symbol"] == sym].iloc[0]
            snapshot_rows.append({
                "universe_id": universe_id,
                "asof_time": to_iso(month_start),
                "selection_time_start": to_iso(prev_month_start),
                "selection_time_end": to_iso(month_start),
                "symbol": sym,
                "rank": rank_idx + 1,
                "rank_metric": f"prev_full_month_{rank_metric}_sum",
                "rank_metric_value": qv_sum,
                "eligible": True,
                "known_at": to_iso(month_start),
                "source": "binance_um_perp_1d_klines",
                "universe_mode": "dynamic_from_current_listed_pool",
                "notes": "",
            })

        detail_rows.append({
            "month": month_start.strftime("%Y-%m"),
            "month_start_utc": to_iso(month_start),
            "selection_basis": f"prev_full_month_{rank_metric}_sum_usdt",
            "selection_time_start": to_iso(prev_month_start),
            "selection_time_end": to_iso(month_start),
            "candidate_count": len(eligible),
            "selected_count": len(selected),
            "selected_symbols": ",".join(selected),
            "entered_symbols": ",".join(entered),
            "exited_symbols": ",".join(exited),
        })

        prev_selected = selected_set

    return pd.DataFrame(snapshot_rows), pd.DataFrame(detail_rows)


# ── Manifest ──────────────────────────────────────────────────────

def write_manifest(
    universe_id: str,
    start: pd.Timestamp,
    end: pd.Timestamp,
    top_n: int,
    rank_metric: str,
    selection_frequency: str,
    candidates: pd.DataFrame,
    snapshots: pd.DataFrame,
    detail: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Write universe_manifest.json."""
    months = detail["month"].unique().tolist() if not detail.empty else []
    manifest = {
        "universe_id": universe_id,
        "universe_mode": "dynamic_from_current_listed_pool",
        "description": (
            "Monthly rolling universe based on previous full month's quote_volume. "
            "Candidate pool is current-listed only (Binance UM exchangeInfo at build time). "
            "Delisted historical symbols are NOT included. "
            "This reduces static-top-N bias but does NOT eliminate survivorship bias."
        ),
        "known_limitations": [
            "Candidate pool is current-listed only. Delisted historical symbols are not included.",
            "This universe is dynamic_from_current_listed_pool, not true_point_in_time_universe.",
            "It reduces static-current-top50 bias but does not eliminate delisted-symbol survivorship bias.",
            "Symbols that were delisted between their listing month and now are missing from all months.",
        ],
        "parameters": {
            "top_n": top_n,
            "rank_metric": rank_metric,
            "selection_frequency": selection_frequency,
            "selection_basis": f"previous full calendar month's Binance UM perpetual 1d {rank_metric} sum",
        },
        "date_range": {
            "start": to_iso(start),
            "end": to_iso(end),
        },
        "months_generated": months,
        "months_count": len(months),
        "candidate_count": len(candidates),
        "snapshot_rows": len(snapshots),
        "data_source": {
            "exchange_info": "https://fapi.binance.com/fapi/v1/exchangeInfo",
            "klines": "https://data.binance.vision/data/futures/um/monthly/klines/{symbol}/1d/",
        },
        "output_files": [
            "universe_snapshots.parquet",
            "universe_manifest.json",
            "candidate_symbols.parquet",
            "monthly_selection_detail.parquet",
        ],
        "generated_at": pd.Timestamp.now(timezone.utc).isoformat(),
    }
    (output_dir / "universe_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )


# ── Main ──────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--universe-id", default="crypto_usdt_perp_monthly_volume_top50_current_listed_v1")
    p.add_argument("--start", default="2024-06-13")
    p.add_argument("--end", default="2026-06-13")
    p.add_argument("--top-n", type=int, default=50)
    p.add_argument("--rank-metric", default="quote_volume")
    p.add_argument("--selection-frequency", default="monthly")
    args = p.parse_args()

    universe_id = args.universe_id
    start = pd.Timestamp(args.start, tz="UTC")
    end = pd.Timestamp(args.end, tz="UTC")
    top_n = args.top_n
    rank_metric = args.rank_metric
    selection_frequency = args.selection_frequency

    output_dir = DATA_DIR / universe_id
    cache_dir = CACHE_DIR / universe_id
    ensure_dir(output_dir)
    ensure_dir(cache_dir)

    print(f"Universe ID: {universe_id}")
    print(f"Date range:  {to_iso(start)} → {to_iso(end)}")
    print(f"Top N:       {top_n}")
    print(f"Rank metric: {rank_metric}")
    print(f"Frequency:   {selection_frequency}")
    print()

    # 1. Candidate pool
    print("Step 1: Fetching candidate pool from Binance exchangeInfo...")
    candidates = fetch_candidate_pool(cache_dir)
    print(f"  Candidates: {len(candidates)} (USDT PERPETUAL TRADING)")
    candidates.to_parquet(output_dir / "candidate_symbols.parquet", index=False)

    # 2. Build monthly universe
    print("Step 2: Building monthly universe...")
    snapshots, detail = build_monthly_universe(
        candidates, start, end, top_n, rank_metric, universe_id, cache_dir,
    )
    print(f"  Months: {len(detail)}")
    print(f"  Snapshot rows: {len(snapshots)}")

    # 3. Write outputs
    print("Step 3: Writing outputs...")
    snapshots.to_parquet(output_dir / "universe_snapshots.parquet", index=False)
    detail.to_parquet(output_dir / "monthly_selection_detail.parquet", index=False)
    write_manifest(universe_id, start, end, top_n, rank_metric, selection_frequency, candidates, snapshots, detail, output_dir)

    print(f"\nOutputs in: {output_dir}")
    print(f"  universe_snapshots.parquet:     {len(snapshots)} rows")
    print(f"  candidate_symbols.parquet:      {len(candidates)} rows")
    print(f"  monthly_selection_detail.parquet: {len(detail)} rows")
    print(f"  universe_manifest.json")


if __name__ == "__main__":
    main()
