#!/usr/bin/env python3
"""Build canonical Binance funding-rate event and 1h-aligned caches.

The factor workflow consumes:
  data/cache/crypto_funding_rate_1h_contract_v1/funding_rate_events.parquet
  data/cache/crypto_funding_rate_1h_contract_v1/funding_rate_1h_aligned_static.parquet
  data/cache/crypto_funding_rate_1h_contract_v1/funding_rate_1h_aligned_dynamic.parquet

This script repairs those artifacts from Binance public monthly fundingRate
archives and the canonical bars datasets. Monthly archives are preferred
because they include funding_interval_hours. REST API is only used as a
fallback for missing monthly files.
"""
from __future__ import annotations

import argparse
import io
import json
import time
import urllib.parse
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "binance_funding_rate"
OUT_DIR = ROOT / "data" / "cache" / "crypto_funding_rate_1h_contract_v1"

DATA_VISION_BASE = "https://data.binance.vision/data/futures/um/monthly/fundingRate"
FUNDING_API = "https://fapi.binance.com/fapi/v1/fundingRate"

DATASETS = {
    "static": "crypto_top50_usdt_perp_1h_long_v1",
    "dynamic": "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1",
}


def month_floor(ts: pd.Timestamp) -> pd.Timestamp:
    return pd.Timestamp(year=ts.year, month=ts.month, day=1, tz="UTC")


def add_month(ts: pd.Timestamp) -> pd.Timestamp:
    if ts.month == 12:
        return pd.Timestamp(year=ts.year + 1, month=1, day=1, tz="UTC")
    return pd.Timestamp(year=ts.year, month=ts.month + 1, day=1, tz="UTC")


def month_range(start: pd.Timestamp, end: pd.Timestamp) -> list[str]:
    cur = month_floor(start)
    last = month_floor(end)
    months: list[str] = []
    while cur <= last:
        months.append(cur.strftime("%Y-%m"))
        cur = add_month(cur)
    return months


def month_bounds(month: str) -> tuple[int, int]:
    start = pd.Timestamp(f"{month}-01", tz="UTC")
    end = add_month(start) - pd.Timedelta(milliseconds=1)
    return int(start.timestamp() * 1000), int(end.timestamp() * 1000)


def funding_zip_path(symbol: str, month: str) -> Path:
    return RAW_DIR / symbol / f"{symbol}-fundingRate-{month}.zip"


def read_zip_csv(path: Path) -> pd.DataFrame:
    with zipfile.ZipFile(path) as zf:
        names = [n for n in zf.namelist() if n.endswith(".csv")]
        if not names:
            return pd.DataFrame()
        with zf.open(names[0]) as fh:
            return pd.read_csv(fh)


def normalize_funding_frame(df: pd.DataFrame, symbol: str, source_file: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    if {"calc_time", "last_funding_rate"}.issubset(df.columns):
        out = pd.DataFrame({
            "symbol": symbol,
            "calc_time": pd.to_numeric(df["calc_time"], errors="coerce"),
            "funding_rate": pd.to_numeric(df["last_funding_rate"], errors="coerce"),
            "funding_interval_hours": pd.to_numeric(df.get("funding_interval_hours"), errors="coerce"),
            "source_file": source_file,
        })
    elif {"fundingTime", "fundingRate"}.issubset(df.columns):
        out = pd.DataFrame({
            "symbol": symbol,
            "calc_time": pd.to_numeric(df["fundingTime"], errors="coerce"),
            "funding_rate": pd.to_numeric(df["fundingRate"], errors="coerce"),
            "funding_interval_hours": np.nan,
            "source_file": source_file,
        })
    else:
        return pd.DataFrame()

    out = out.dropna(subset=["calc_time", "funding_rate"]).copy()
    out["calc_time"] = out["calc_time"].round().astype("int64")
    out["known_at"] = pd.to_datetime(out["calc_time"], unit="ms", utc=True)
    return out[["symbol", "calc_time", "known_at", "funding_rate", "funding_interval_hours", "source_file"]]


def http_get(url: str, timeout: int = 30) -> bytes | None:
    req = urllib.request.Request(url, headers={"User-Agent": "momentum-funding-cache/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            if data.startswith(b"<Error>") or data.startswith(b"<?xml"):
                return None
            return data
    except Exception:
        return None


def download_monthly_zip(symbol: str, month: str) -> bool:
    path = funding_zip_path(symbol, month)
    if path.exists() and path.stat().st_size > 0:
        return True
    url = f"{DATA_VISION_BASE}/{symbol}/{symbol}-fundingRate-{month}.zip"
    data = http_get(url)
    if not data:
        return False
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            if not any(n.endswith(".csv") for n in zf.namelist()):
                return False
    except zipfile.BadZipFile:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(path)
    return True


def api_funding_month(symbol: str, month: str) -> pd.DataFrame:
    start_ms, end_ms = month_bounds(month)
    params = urllib.parse.urlencode({
        "symbol": symbol,
        "startTime": start_ms,
        "endTime": end_ms,
        "limit": 1000,
    })
    data = http_get(f"{FUNDING_API}?{params}", timeout=20)
    if not data:
        return pd.DataFrame()
    try:
        raw = json.loads(data.decode("utf-8"))
    except Exception:
        return pd.DataFrame()
    if not isinstance(raw, list) or not raw:
        return pd.DataFrame()
    df = pd.DataFrame(raw)
    if not {"fundingTime", "fundingRate"}.issubset(df.columns):
        return pd.DataFrame()
    out = pd.DataFrame({
        "calc_time": pd.to_numeric(df["fundingTime"], errors="coerce"),
        "last_funding_rate": pd.to_numeric(df["fundingRate"], errors="coerce"),
    }).dropna()
    if out.empty:
        return out
    out = out.sort_values("calc_time").drop_duplicates("calc_time")
    times = out["calc_time"].to_numpy(dtype="int64")
    if len(times) > 1:
        next_diff = np.diff(times, append=np.nan) / 3_600_000.0
        prev_diff = np.diff(times, prepend=np.nan) / 3_600_000.0
        interval = np.where(np.isfinite(next_diff), next_diff, prev_diff)
        interval = np.where(np.isin(np.round(interval), [1, 2, 4, 8]), np.round(interval), np.nan)
    else:
        interval = np.array([np.nan])
    out["funding_interval_hours"] = interval
    return out[["calc_time", "funding_interval_hours", "last_funding_rate"]]


def write_api_zip(symbol: str, month: str, df: pd.DataFrame) -> bool:
    if df.empty:
        return False
    path = funding_zip_path(symbol, month)
    path.parent.mkdir(parents=True, exist_ok=True)
    csv_name = f"{symbol}-fundingRate-{month}.csv"
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    tmp = path.with_suffix(path.suffix + ".tmp")
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(csv_name, csv_bytes)
    tmp.replace(path)
    return True


def ensure_symbol_month(symbol: str, month: str, allow_api: bool) -> tuple[str, str, str]:
    path = funding_zip_path(symbol, month)
    if path.exists() and path.stat().st_size > 0:
        return symbol, month, "cached"
    if download_monthly_zip(symbol, month):
        return symbol, month, "downloaded_monthly"
    if allow_api:
        df = api_funding_month(symbol, month)
        if write_api_zip(symbol, month, df):
            time.sleep(0.03)
            return symbol, month, "downloaded_api"
    return symbol, month, "missing"


def load_bars(dataset_id: str) -> pd.DataFrame:
    path = ROOT / "data" / "cache" / dataset_id / "bars_1h.parquet"
    if not path.exists():
        raise FileNotFoundError(path)
    bars = pd.read_parquet(path, columns=["timestamp", "symbol"])
    bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
    bars["symbol"] = bars["symbol"].astype(str)
    return bars.drop_duplicates(["timestamp", "symbol"]).sort_values(["symbol", "timestamp"])


def required_symbol_months(bars_by_role: dict[str, pd.DataFrame], extra_hours: int) -> set[tuple[str, str]]:
    needed: set[tuple[str, str]] = set()
    for bars in bars_by_role.values():
        for symbol, grp in bars.groupby("symbol", sort=False):
            start = grp["timestamp"].min()
            end = grp["timestamp"].max() + pd.Timedelta(hours=extra_hours)
            for month in month_range(start, end):
                needed.add((str(symbol), month))
    return needed


def load_events(symbols: Iterable[str]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for symbol in sorted(set(symbols)):
        for path in sorted((RAW_DIR / symbol).glob(f"{symbol}-fundingRate-*.zip")):
            try:
                norm = normalize_funding_frame(read_zip_csv(path), symbol, str(path.relative_to(ROOT)))
            except Exception:
                continue
            if not norm.empty:
                frames.append(norm)
    if not frames:
        return pd.DataFrame(columns=["symbol", "calc_time", "known_at", "funding_rate", "funding_interval_hours", "source_file"])
    events = pd.concat(frames, ignore_index=True)
    events = events.sort_values(["symbol", "calc_time", "source_file"]).drop_duplicates(["symbol", "calc_time"], keep="last")
    events["funding_interval_hours"] = infer_missing_intervals(events)
    return events


def infer_missing_intervals(events: pd.DataFrame) -> pd.Series:
    intervals = pd.to_numeric(events["funding_interval_hours"], errors="coerce").copy()
    inferred_parts: list[pd.Series] = []
    for _symbol, grp in events.sort_values(["symbol", "calc_time"]).groupby("symbol", sort=False):
        idx = grp.index
        existing = intervals.loc[idx]
        times = grp["calc_time"].to_numpy(dtype="int64")
        if len(times) > 1:
            next_diff = np.diff(times, append=np.nan) / 3_600_000.0
            prev_diff = np.diff(times, prepend=np.nan) / 3_600_000.0
            inferred = np.where(np.isfinite(next_diff), next_diff, prev_diff)
            inferred = np.where(np.isin(np.round(inferred), [1, 2, 4, 8]), np.round(inferred), np.nan)
        else:
            inferred = np.array([np.nan])
        s = pd.Series(inferred, index=idx, dtype="float64")
        inferred_parts.append(existing.fillna(s))
    out = pd.concat(inferred_parts).sort_index()
    return out


def align_events_to_bars(bars: pd.DataFrame, events: pd.DataFrame, extra_hours: int = 0) -> pd.DataFrame:
    pieces: list[pd.DataFrame] = []
    events = events.copy()
    events["known_at"] = pd.to_datetime(events["known_at"], utc=True)
    for symbol, b in bars.groupby("symbol", sort=False):
        ev = events[events["symbol"] == symbol].sort_values("known_at")
        start = pd.to_datetime(b["timestamp"].min(), utc=True)
        end = pd.to_datetime(b["timestamp"].max(), utc=True) + pd.Timedelta(hours=extra_hours)
        base = pd.DataFrame({
            "timestamp": pd.date_range(start, end, freq="h", tz="UTC"),
            "symbol": symbol,
        })
        base["timestamp"] = base["timestamp"].astype("datetime64[ns, UTC]")
        if ev.empty:
            base["funding_rate"] = np.nan
            base["funding_known_at"] = pd.NaT
            base["funding_interval_hours"] = np.nan
            base["funding_age_hours"] = np.nan
            pieces.append(base)
            continue
        ev = ev.copy()
        ev["known_at"] = pd.to_datetime(ev["known_at"], utc=True).astype("datetime64[ns, UTC]")
        merged = pd.merge_asof(
            base,
            ev[["known_at", "funding_rate", "funding_interval_hours"]].rename(columns={"known_at": "funding_known_at"}),
            left_on="timestamp",
            right_on="funding_known_at",
            direction="backward",
        )
        merged["funding_age_hours"] = (
            (merged["timestamp"] - merged["funding_known_at"]).dt.total_seconds() / 3600.0
        )
        interval = pd.to_numeric(merged["funding_interval_hours"], errors="coerce")
        age = pd.to_numeric(merged["funding_age_hours"], errors="coerce")
        valid = interval.notna() & (interval > 0) & age.notna() & (age >= 0) & (age < interval)
        merged.loc[~valid, ["funding_rate", "funding_interval_hours"]] = np.nan
        pieces.append(merged)
    out = pd.concat(pieces, ignore_index=True)
    return out[["timestamp", "symbol", "funding_rate", "funding_known_at", "funding_interval_hours", "funding_age_hours"]]


def write_manifest(manifest: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "funding_rate_cache_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Binance funding-rate event/aligned cache")
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--no-download", action="store_true", help="Use existing raw zip files only")
    parser.add_argument("--no-api-fallback", action="store_true", help="Do not use REST API for missing months")
    parser.add_argument("--extra-hours", type=int, default=96, help="Download funding through max bar timestamp + this many hours")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    bars_by_role = {role: load_bars(ds) for role, ds in DATASETS.items()}
    needed = sorted(required_symbol_months(bars_by_role, args.extra_hours))
    symbols = sorted({s for s, _ in needed})

    statuses: dict[str, int] = {}
    if args.no_download:
        for symbol, month in needed:
            status = "cached" if funding_zip_path(symbol, month).exists() else "missing"
            statuses[status] = statuses.get(status, 0) + 1
    else:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = [
                pool.submit(ensure_symbol_month, symbol, month, not args.no_api_fallback)
                for symbol, month in needed
            ]
            for i, fut in enumerate(as_completed(futures), start=1):
                _symbol, _month, status = fut.result()
                statuses[status] = statuses.get(status, 0) + 1
                if i % 250 == 0 or i == len(futures):
                    print(f"  funding downloads {i}/{len(futures)} {statuses}", flush=True)

    events = load_events(symbols)
    events_path = OUT_DIR / "funding_rate_events.parquet"
    events.to_parquet(events_path, index=False)

    aligned_stats: dict[str, dict] = {}
    for role, bars in bars_by_role.items():
        aligned = align_events_to_bars(bars, events, extra_hours=args.extra_hours)
        out_path = OUT_DIR / f"funding_rate_1h_aligned_{role}.parquet"
        aligned.to_parquet(out_path, index=False)
        aligned_stats[role] = {
            "dataset_id": DATASETS[role],
            "rows": int(len(aligned)),
            "symbols": int(aligned["symbol"].nunique()),
            "timestamp_min": str(aligned["timestamp"].min()),
            "timestamp_max": str(aligned["timestamp"].max()),
            "funding_rate_coverage": float(aligned["funding_rate"].notna().mean()),
            "funding_interval_coverage": float(aligned["funding_interval_hours"].notna().mean()),
            "output": str(out_path.relative_to(ROOT)),
        }
        print(f"{role}: rows={len(aligned)} coverage={aligned_stats[role]['funding_rate_coverage']:.2%}", flush=True)

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "raw_dir": str(RAW_DIR.relative_to(ROOT)),
        "needed_symbol_months": len(needed),
        "needed_symbols": len(symbols),
        "download_status_counts": statuses,
        "events": {
            "rows": int(len(events)),
            "symbols": int(events["symbol"].nunique()) if not events.empty else 0,
            "timestamp_min": str(events["known_at"].min()) if not events.empty else None,
            "timestamp_max": str(events["known_at"].max()) if not events.empty else None,
            "funding_interval_missing_rate": float(events["funding_interval_hours"].isna().mean()) if not events.empty else None,
            "output": str(events_path.relative_to(ROOT)),
        },
        "aligned": aligned_stats,
        "notes": [
            "Monthly Binance Vision fundingRate zips are preferred because they include funding_interval_hours.",
            "REST API fallback is cached as normalized monthly zip only when monthly archive is unavailable.",
            "Aligned rows use the latest funding settlement only while timestamp - funding_known_at < funding_interval_hours.",
        ],
    }
    write_manifest(manifest)
    print(f"Wrote {OUT_DIR / 'funding_rate_cache_manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
