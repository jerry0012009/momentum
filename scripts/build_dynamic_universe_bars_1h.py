#!/usr/bin/env python3
"""Build 1h bars dataset for dynamic universe symbols.

Downloads Binance USDT-M perpetual 1h klines for all symbols selected by
a dynamic universe, producing a bars_1h.parquet compatible with the existing
factor-library pipeline.

Usage:
    python scripts/build_dynamic_universe_bars_1h.py \
        --universe-id crypto_usdt_perp_monthly_volume_top50_current_listed_v1 \
        --dataset-id crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1 \
        --start 2024-06-13 --end 2026-06-13
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import time
import urllib.error
import urllib.request
import zipfile
from datetime import timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

MONTHLY_URL = "https://data.binance.vision/data/futures/um/monthly/klines/{symbol}/1h/{symbol}-1h-{ym}.zip"
DAILY_URL = "https://data.binance.vision/data/futures/um/daily/klines/{symbol}/1h/{symbol}-1h-{ymd}.zip"

KLINE_COLUMNS = [
    "open_time", "open", "high", "low", "close", "volume",
    "close_time", "quote_volume", "trade_count", "taker_base", "taker_quote", "ignore",
]
NUMERIC_COLS = ["open", "high", "low", "close", "volume", "quote_volume", "trade_count"]


# ── Network helpers ───────────────────────────────────────────────

def _retry_after_seconds(err: urllib.error.HTTPError, default: float, attempt: int) -> float:
    try:
        header = err.headers.get("Retry-After") if err.headers else None
        if header:
            return max(float(header), default)
    except Exception:  # noqa: BLE001
        pass
    if err.code == 418:
        return max(60.0, default * (attempt + 1) * 5.0)
    return max(default, default * (attempt + 1))


def safe_download(url: str, dst: Path, *, retries: int = 7, sleep_sec: float = 2.0) -> bool:
    """Download url to dst. Returns True on success, False on 404."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and dst.stat().st_size > 0:
        return True
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                blob = r.read()
            dst.write_bytes(blob)
            return True
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return False
            if e.code in {418, 429, 500, 502, 503, 504} and attempt + 1 < retries:
                time.sleep(_retry_after_seconds(e, sleep_sec, attempt))
                continue
            raise
        except (urllib.error.URLError, ConnectionResetError, TimeoutError):
            if attempt + 1 < retries:
                time.sleep(max(sleep_sec, sleep_sec * (attempt + 1)))
                continue
            raise
    return False


# ── Kline parser ──────────────────────────────────────────────────

def read_kline_zip(path: Path) -> pd.DataFrame:
    """Parse a Binance kline zip into a DataFrame with proper columns."""
    blob = path.read_bytes()
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        members = zf.namelist()
        if not members:
            return pd.DataFrame()
        data = zf.read(members[0])
    df = pd.read_csv(io.BytesIO(data), header=None, names=KLINE_COLUMNS)
    # Convert numeric columns
    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["open_time"] = pd.to_numeric(df["open_time"], errors="coerce")
    df = df.dropna(subset=["open_time", "close"])
    if df.empty:
        return pd.DataFrame()
    # Timestamp convention: bar_open_time = open_time, bar_close_time = open_time + 1h, timestamp = bar_close_time
    df["bar_open_time"] = pd.to_datetime(df["open_time"].astype("int64"), unit="ms", utc=True)
    df["bar_close_time"] = df["bar_open_time"] + pd.Timedelta(hours=1)
    df["timestamp"] = df["bar_close_time"]
    return df


# ── Time helpers ──────────────────────────────────────────────────

def month_range(start: pd.Timestamp, end: pd.Timestamp) -> list[str]:
    """Generate YYYY-MM strings from start to end (inclusive)."""
    cur = pd.Timestamp(start.year, start.month, 1, tz="UTC")
    end_month = pd.Timestamp(end.year, end.month, 1, tz="UTC")
    out = []
    while cur <= end_month:
        out.append(cur.strftime("%Y-%m"))
        cur = cur + pd.offsets.MonthBegin(1)
    return out


# ── Download one symbol ───────────────────────────────────────────

def download_symbol_1h(
    symbol: str,
    months: list[str],
    cache_dir: Path,
    download_log: list[dict],
) -> pd.DataFrame:
    """Download 1h klines for one symbol across all months. Returns DataFrame."""
    all_frames = []
    for ym in months:
        cache_path = cache_dir / f"{symbol}-1h-{ym}.parquet"
        if cache_path.exists():
            df = pd.read_parquet(cache_path)
            if not df.empty:
                all_frames.append(df)
            continue

        # Try monthly zip first
        url = MONTHLY_URL.format(symbol=symbol, ym=ym)
        zip_path = cache_dir / f"{symbol}-1h-{ym}.zip"
        ok = safe_download(url, zip_path)

        if not ok:
            # Try daily zips for this month
            zip_path.unlink(missing_ok=True)
            year, month = int(ym[:4]), int(ym[5:7])
            # Generate all days in this month
            first_day = pd.Timestamp(year, month, 1, tz="UTC")
            if month == 12:
                last_day = pd.Timestamp(year + 1, 1, 1, tz="UTC") - pd.Timedelta(days=1)
            else:
                last_day = pd.Timestamp(year, month + 1, 1, tz="UTC") - pd.Timedelta(days=1)

            day_frames = []
            for day in pd.date_range(first_day, last_day, freq="D"):
                ymd = day.strftime("%Y-%m-%d")
                day_url = DAILY_URL.format(symbol=symbol, ymd=ymd)
                day_zip = cache_dir / f"{symbol}-1h-{ymd}.zip"
                day_ok = safe_download(day_url, day_zip)
                if day_ok:
                    day_df = read_kline_zip(day_zip)
                    if not day_df.empty:
                        day_frames.append(day_df)
                else:
                    day_zip.unlink(missing_ok=True)
                    download_log.append({
                        "symbol": symbol, "url": day_url, "status": "404",
                        "type": "daily", "period": ymd,
                    })

            if day_frames:
                df = pd.concat(day_frames, ignore_index=True)
            else:
                df = pd.DataFrame()
                download_log.append({
                    "symbol": symbol, "url": url, "status": "404",
                    "type": "monthly", "period": ym,
                })
        else:
            df = read_kline_zip(zip_path)
            if df.empty:
                download_log.append({
                    "symbol": symbol, "url": url, "status": "empty_zip",
                    "type": "monthly", "period": ym,
                })

        # Cache parsed result
        if not df.empty:
            df.to_parquet(cache_path, index=False)
            all_frames.append(df)
        else:
            # Write empty marker
            pd.DataFrame().to_parquet(cache_path, index=False)

    if not all_frames:
        return pd.DataFrame()

    result = pd.concat(all_frames, ignore_index=True)
    result = result.drop_duplicates(subset=["timestamp", "symbol"] if "symbol" in result.columns else ["timestamp"])
    result = result.sort_values("timestamp").reset_index(drop=True)
    return result


# ── Build complete bars DataFrame ─────────────────────────────────

def build_symbol_bars(
    symbol: str,
    raw: pd.DataFrame,
) -> pd.DataFrame:
    """Convert raw kline data into pipeline-compatible bars DataFrame."""
    if raw.empty:
        return pd.DataFrame()

    bars = pd.DataFrame({
        "timestamp": raw["timestamp"],
        "bar_open_time": raw["bar_open_time"],
        "bar_close_time": raw["bar_close_time"],
        "symbol": symbol,
        "open": raw["open"],
        "high": raw["high"],
        "low": raw["low"],
        "close": raw["close"],
        "volume": raw["volume"],
        "quote_volume": raw["quote_volume"],
        "trade_count": raw["trade_count"].astype("Int64"),
        "source": "binance_fapi",
        "market": "crypto",
        "instrument_type": "usdt_margined_perpetual",
        "timeframe": "1h",
    })
    return bars


# ── Symbol availability ───────────────────────────────────────────

def compute_symbol_availability(
    all_bars: pd.DataFrame,
    symbols: list[str],
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> pd.DataFrame:
    """Compute per-symbol data availability."""
    rows = []
    expected_hours = int((end - start).total_seconds() / 3600)
    for sym in symbols:
        sym_data = all_bars[all_bars["symbol"] == sym] if not all_bars.empty else pd.DataFrame()
        if sym_data.empty:
            rows.append({
                "symbol": sym,
                "first_bar_time": pd.NaT,
                "last_bar_time": pd.NaT,
                "n_bars": 0,
                "expected_bars": expected_hours,
                "missing_bars": expected_hours,
                "missing_bar_rate": 1.0,
                "listed_in_dynamic_universe": True,
                "download_status": "no_data",
            })
        else:
            n_bars = len(sym_data)
            missing = expected_hours - n_bars
            rows.append({
                "symbol": sym,
                "first_bar_time": sym_data["timestamp"].min(),
                "last_bar_time": sym_data["timestamp"].max(),
                "n_bars": n_bars,
                "expected_bars": expected_hours,
                "missing_bars": missing,
                "missing_bar_rate": round(missing / expected_hours, 6) if expected_hours > 0 else 0.0,
                "listed_in_dynamic_universe": True,
                "download_status": "ok",
            })
    return pd.DataFrame(rows)


# ── Membership-aware coverage ─────────────────────────────────────

def compute_membership_aware_availability(
    bars: pd.DataFrame,
    snapshots: pd.DataFrame,
    dataset_start: pd.Timestamp,
    dataset_end: pd.Timestamp,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compute coverage only during months when each symbol is selected.

    Uses vectorized groupby instead of per-symbol-month loops.

    Returns:
        (membership_availability, membership_monthly_coverage)
    """
    # Build symbol→months mapping from snapshots
    snap = snapshots.copy()
    snap["asof_time"] = pd.to_datetime(snap["asof_time"], utc=True)
    snap["month_str"] = snap["asof_time"].dt.strftime("%Y-%m")

    # symbol → sorted list of selected months
    symbol_months_sets: dict[str, set[str]] = {}
    for _, row in snap.iterrows():
        sym = row["symbol"]
        m = row["month_str"]
        symbol_months_sets.setdefault(sym, set()).add(m)
    symbol_months = {k: sorted(v) for k, v in symbol_months_sets.items()}

    # Build (symbol, month_str) → observed bar count via groupby
    if not bars.empty:
        bars_month = bars[["symbol", "timestamp"]].copy()
        bars_month["month_str"] = bars_month["timestamp"].dt.strftime("%Y-%m")
        observed_counts = (
            bars_month.groupby(["symbol", "month_str"])
            .size()
            .rename("observed_bars")
            .reset_index()
        )
    else:
        observed_counts = pd.DataFrame(columns=["symbol", "month_str", "observed_bars"])

    # Build all expected (symbol, month) pairs with expected_bars
    expected_rows = []
    for sym, months_list in symbol_months.items():
        for m in months_list:
            period = pd.Period(m, freq="M")
            month_start = max(period.start_time.tz_localize("UTC"), dataset_start)
            # Use start of next month as exclusive end boundary
            month_end_excl = (period + 1).start_time.tz_localize("UTC")
            month_end = min(month_end_excl, dataset_end)
            if month_start >= month_end:
                continue
            expected_hours = int((month_end - month_start).total_seconds() / 3600)
            expected_rows.append({
                "symbol": sym,
                "month_str": m,
                "asof_time": period.start_time.tz_localize("UTC"),
                "expected_bars": expected_hours,
            })
    expected_df = pd.DataFrame(expected_rows)

    # Merge expected with observed
    monthly_cov = expected_df.merge(observed_counts, on=["symbol", "month_str"], how="left")
    monthly_cov["observed_bars"] = monthly_cov["observed_bars"].fillna(0).astype(int)
    monthly_cov["missing_bars"] = monthly_cov["expected_bars"] - monthly_cov["observed_bars"]
    monthly_cov["missing_bar_rate"] = (
        monthly_cov["missing_bars"] / monthly_cov["expected_bars"]
    ).round(6).fillna(0.0)
    monthly_cov["coverage_status"] = np.where(
        monthly_cov["missing_bar_rate"] <= 0.05, "ok", "missing",
    )
    monthly_cov = monthly_cov.rename(columns={"month_str": "month"})
    monthly_cov = monthly_cov[["month", "symbol", "asof_time", "expected_bars",
                                "observed_bars", "missing_bars", "missing_bar_rate", "coverage_status"]]
    monthly_cov = monthly_cov.sort_values(["symbol", "month"]).reset_index(drop=True)

    # Per-symbol aggregation
    if monthly_cov.empty:
        return pd.DataFrame(), monthly_cov

    agg = monthly_cov.groupby("symbol").agg(
        selected_months=("month", "nunique"),
        first_selected_month=("month", "min"),
        last_selected_month=("month", "max"),
        member_expected_bars=("expected_bars", "sum"),
        member_observed_bars=("observed_bars", "sum"),
    ).reset_index()
    agg["member_missing_bars"] = agg["member_expected_bars"] - agg["member_observed_bars"]
    agg["member_missing_bar_rate"] = (
        agg["member_missing_bars"] / agg["member_expected_bars"]
    ).round(6).fillna(0.0)

    # Global missing rate
    full_expected = int((dataset_end - dataset_start).total_seconds() / 3600)
    if not bars.empty:
        global_obs = bars.groupby("symbol").size().rename("global_observed").reset_index()
    else:
        global_obs = pd.DataFrame(columns=["symbol", "global_observed"])
    agg = agg.merge(global_obs, on="symbol", how="left")
    agg["global_observed"] = agg["global_observed"].fillna(0).astype(int)
    agg["global_missing_bar_rate"] = (
        (full_expected - agg["global_observed"]) / full_expected
    ).round(6).fillna(0.0)

    # Coverage status
    agg["coverage_status"] = "ok"
    degraded_mask = (agg["member_expected_bars"] > 0) & (agg["member_missing_bar_rate"] > 0.05)
    zero_mask = (agg["member_expected_bars"] > 0) & (agg["member_observed_bars"] == 0)
    agg.loc[degraded_mask, "coverage_status"] = "degraded"
    agg.loc[zero_mask, "coverage_status"] = "zero_bars"

    avail = agg[["symbol", "selected_months", "first_selected_month", "last_selected_month",
                 "member_expected_bars", "member_observed_bars", "member_missing_bars",
                 "member_missing_bar_rate", "global_missing_bar_rate", "coverage_status"]]
    return avail, monthly_cov


def compute_qa_conclusion(
    membership_avail: pd.DataFrame,
    membership_monthly: pd.DataFrame,
) -> dict:
    """Determine whether Phase 6E labels build is allowed."""
    zero_months = membership_monthly[membership_monthly["observed_bars"] == 0]
    high_missing_months = membership_monthly[membership_monthly["missing_bar_rate"] > 0.05]

    n_zero = len(zero_months)
    n_high_missing = len(high_missing_months)
    n_total_months = len(membership_monthly)

    # Rule 1: any selected symbol-month with zero bars → BLOCK
    if n_zero > 0:
        decision = "BLOCKED"
        reason = f"{n_zero} selected symbol-month(s) have zero bars"
    # Rule 2: many selected symbol-months with >5% missing → BLOCK
    elif n_high_missing > n_total_months * 0.1:
        decision = "BLOCKED"
        reason = f"{n_high_missing}/{n_total_months} selected symbol-months have >5% missing bars"
    # Rule 3: high global missing but good selected-month coverage → ALLOW
    else:
        decision = "ALLOWED"
        reason = "Membership-aware coverage is acceptable"

    return {
        "decision": decision,
        "reason": reason,
        "n_zero_bar_months": n_zero,
        "n_high_missing_months": n_high_missing,
        "n_total_selected_months": n_total_months,
    }


# ── Data quality report ───────────────────────────────────────────

def write_quality_report(
    dataset_id: str,
    universe_id: str,
    start: str,
    end: str,
    n_requested: int,
    n_with_data: int,
    n_rows: int,
    availability: pd.DataFrame,
    download_log: list[dict],
) -> str:
    """Generate data_quality_report.md."""
    zero_rows = availability[availability["n_bars"] == 0]["symbol"].tolist()
    high_missing = availability[availability["missing_bar_rate"] > 0.05].sort_values("missing_bar_rate", ascending=False)
    top_missing = high_missing.head(20)

    lines = [
        f"# Data Quality Report — {dataset_id}",
        "",
        f"- universe_id: `{universe_id}`",
        f"- dataset_id: `{dataset_id}`",
        f"- date_range: {start} → {end}",
        f"- n_symbols_requested: {n_requested}",
        f"- n_symbols_with_data: {n_with_data}",
        f"- n_rows: {n_rows:,}",
        f"- symbols_with_zero_rows: {len(zero_rows)}",
        f"- symbols_with_missing_bar_rate_gt_5pct: {len(high_missing)}",
        "",
        "## Timestamp Convention",
        "",
        "- bar_open_time = Binance kline open_time",
        "- bar_close_time = bar_open_time + 1h",
        "- timestamp = bar_close_time",
        "",
        "## Symbols with Zero Rows",
        "",
    ]
    if zero_rows:
        for sym in zero_rows[:30]:
            lines.append(f"- {sym}")
        if len(zero_rows) > 30:
            lines.append(f"- ... and {len(zero_rows) - 30} more")
    else:
        lines.append("None")

    lines.extend(["", "## Top Missing Symbols (>5% missing bars)", ""])
    if not top_missing.empty:
        lines.append("| Symbol | n_bars | expected | missing_rate |")
        lines.append("|--------|--------|----------|--------------|")
        for _, row in top_missing.iterrows():
            lines.append(f"| {row['symbol']} | {row['n_bars']} | {row['expected_bars']} | {row['missing_bar_rate']:.1%} |")
    else:
        lines.append("None — all symbols have <5% missing bars.")

    lines.extend([
        "",
        "## Download Errors",
        "",
    ])
    if download_log:
        lines.append(f"{len(download_log)} 404/download errors recorded. See download_log.csv for details.")
    else:
        lines.append("No download errors.")

    lines.extend([
        "",
        "## Known Limitations",
        "",
        "- Universe is dynamic_from_current_listed_pool, not true_point_in_time_universe.",
        "- Candidate pool excludes delisted historical symbols.",
        "- This dataset is built only for symbols selected by the dynamic universe snapshots.",
    ])

    return "\n".join(lines) + "\n"


# ── Main ──────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--universe-id", default="crypto_usdt_perp_monthly_volume_top50_current_listed_v1")
    p.add_argument("--dataset-id", default="crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1")
    p.add_argument("--start", default="2024-06-13")
    p.add_argument("--end", default="2026-06-13")
    p.add_argument("--timeframe", default="1h")
    p.add_argument("--qa-only", action="store_true", help="Only run membership-aware QA on existing data")
    args = p.parse_args()

    start = pd.Timestamp(args.start, tz="UTC")
    end = pd.Timestamp(args.end, tz="UTC")
    months = month_range(start, end)

    # Load universe snapshots
    uni_path = DATA_DIR / "universe" / args.universe_id / "universe_snapshots.parquet"
    if not uni_path.exists():
        raise FileNotFoundError(f"universe_snapshots.parquet not found: {uni_path}")
    snap = pd.read_parquet(uni_path)
    symbols = sorted(snap["symbol"].unique())

    print(f"Universe:   {args.universe_id}")
    print(f"Dataset:    {args.dataset_id}")
    print(f"Date range: {args.start} → {args.end}")
    print(f"Symbols:    {len(symbols)}")
    print(f"Months:     {len(months)}")
    print()

    # Setup directories
    cache_dir = DATA_DIR / "cache" / "dynamic_universe_build" / args.dataset_id / "kline_1h"
    output_dir = DATA_DIR / "cache" / args.dataset_id
    output_dir.mkdir(parents=True, exist_ok=True)

    # QA-only mode: skip download, use existing bars_1h.parquet
    if args.qa_only:
        bars_path = output_dir / "bars_1h.parquet"
        if not bars_path.exists():
            raise FileNotFoundError(f"bars_1h.parquet not found: {bars_path}")
        combined = pd.read_parquet(bars_path)
        n_rows = len(combined)
        n_with_data = combined["symbol"].nunique()
        availability = compute_symbol_availability(combined, symbols, start, end)
        download_log = []

        print(f"QA-only mode: loaded existing bars_1h.parquet ({n_rows:,} rows, {n_with_data} symbols)")
    else:
        download_log: list[dict] = []
        all_bars: list[pd.DataFrame] = []

        # Download each symbol
        print(f"Downloading 1h klines for {len(symbols)} symbols...")
        for i, sym in enumerate(symbols, 1):
            raw = download_symbol_1h(sym, months, cache_dir, download_log)
            if not raw.empty:
                bars = build_symbol_bars(sym, raw)
                if not bars.empty:
                    all_bars.append(bars)
            if i % 25 == 0 or i == len(symbols):
                print(f"  {i}/{len(symbols)} processed ({len(all_bars)} with data)")

        # Combine all bars
        if all_bars:
            combined = pd.concat(all_bars, ignore_index=True)
            combined = combined.sort_values(["symbol", "timestamp"]).reset_index(drop=True)
        else:
            combined = pd.DataFrame()

        n_rows = len(combined)
        n_with_data = combined["symbol"].nunique() if not combined.empty else 0

        print(f"\nTotal rows: {n_rows:,}")
        print(f"Symbols with data: {n_with_data}/{len(symbols)}")

        # Write bars_1h.parquet
        bars_path = output_dir / "bars_1h.parquet"
        combined.to_parquet(bars_path, index=False)
        print(f"Wrote: {bars_path}")

        # Compute symbol availability
        availability = compute_symbol_availability(combined, symbols, start, end)
        avail_path = output_dir / "symbol_availability.parquet"
        availability.to_parquet(avail_path, index=False)
        print(f"Wrote: {avail_path}")

        # Write download log
        log_path = output_dir / "download_log.csv"
        if download_log:
            pd.DataFrame(download_log).to_csv(log_path, index=False)
        else:
            pd.DataFrame(columns=["symbol", "url", "status", "type", "period"]).to_csv(log_path, index=False)
        print(f"Wrote: {log_path}")

    # Write manifest
    actual_start = combined["timestamp"].min() if not combined.empty else None
    actual_end = combined["timestamp"].max() if not combined.empty else None
    uni_first = snap["asof_time"].min() if not snap.empty else None
    uni_last = snap["asof_time"].max() if not snap.empty else None

    manifest = {
        "dataset_id": args.dataset_id,
        "universe_id": args.universe_id,
        "timeframe": args.timeframe,
        "source": "data.binance.vision",
        "requested_start": args.start,
        "requested_end": args.end,
        "actual_data_start": str(actual_start) if actual_start is not None else None,
        "actual_data_end": str(actual_end) if actual_end is not None else None,
        "universe_first_asof_time": str(uni_first) if uni_first is not None else None,
        "universe_last_asof_time": str(uni_last) if uni_last is not None else None,
        "timestamp_convention": "timestamp = bar_close_time = bar_open_time + 1h",
        "bar_open_time_convention": "Binance kline open_time (ms epoch)",
        "bar_close_time_convention": "bar_open_time + 1 hour",
        "n_symbols_requested": len(symbols),
        "n_symbols_with_data": n_with_data,
        "n_rows": n_rows,
        "created_at": pd.Timestamp.now(timezone.utc).isoformat(),
        "script": "scripts/build_dynamic_universe_bars_1h.py",
        "known_limitations": [
            "Universe is dynamic_from_current_listed_pool, not true_point_in_time_universe.",
            "Candidate pool excludes delisted historical symbols.",
            "This dataset is built only for symbols selected by the dynamic universe snapshots.",
        ],
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote: {manifest_path}")

    # Compute membership-aware coverage
    print("\nComputing membership-aware coverage...")
    membership_avail, membership_monthly = compute_membership_aware_availability(
        combined, snap, start, end,
    )
    mem_avail_path = output_dir / "membership_availability.parquet"
    membership_avail.to_parquet(mem_avail_path, index=False)
    print(f"Wrote: {mem_avail_path}")

    mem_monthly_path = output_dir / "membership_monthly_coverage.parquet"
    membership_monthly.to_parquet(mem_monthly_path, index=False)
    print(f"Wrote: {mem_monthly_path}")

    # QA conclusion
    qa = compute_qa_conclusion(membership_avail, membership_monthly)
    qa_path = output_dir / "qa_conclusion.json"
    qa_path.write_text(json.dumps(qa, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote: {qa_path}")

    # Write data quality report
    report = write_quality_report(
        args.dataset_id, args.universe_id, args.start, args.end,
        len(symbols), n_with_data, n_rows, availability, download_log,
    )
    report_path = output_dir / "data_quality_report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"Wrote: {report_path}")

    # Summary
    high_missing = availability[availability["missing_bar_rate"] > 0.05]
    zero_rows = availability[availability["n_bars"] == 0]
    print(f"\n=== Summary ===")
    print(f"Rows: {n_rows:,}")
    print(f"Symbols with data: {n_with_data}/{len(symbols)}")
    print(f"Symbols with zero rows: {len(zero_rows)}")
    print(f"Symbols with >5% missing bars: {len(high_missing)}")
    print(f"Download errors: {len(download_log)}")

    # Membership-aware summary
    print(f"\n=== Membership-Aware Coverage ===")
    print(f"Selected symbol-months: {len(membership_monthly)}")
    print(f"Symbol-months with zero bars: {qa['n_zero_bar_months']}")
    print(f"Symbol-months with >5% missing: {qa['n_high_missing_months']}")
    print(f"Median member_missing_bar_rate: {membership_avail['member_missing_bar_rate'].median():.1%}")
    print(f"Actual data range: {actual_start} → {actual_end}")
    print(f"QA decision: {qa['decision']}")
    print(f"Reason: {qa['reason']}")


if __name__ == "__main__":
    main()
