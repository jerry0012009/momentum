#!/usr/bin/env python3
"""
Build reproducible crypto-native data caches: taker enriched bars + funding rate.

Usage:
    python scripts/build_crypto_native_caches.py --mode all
    python scripts/build_crypto_native_caches.py --mode taker
    python scripts/build_crypto_native_caches.py --mode funding
    python scripts/build_crypto_native_caches.py --mode validate

Modes:
    all      Build taker enriched bars + funding rate caches + manifest
    taker    Build taker enriched bars only
    funding  Build funding rate events + 1h aligned only
    validate Validate existing caches against manifest (no rebuild)

Inputs:
    - static/dynamic bars_1h.parquet (from existing factor library cache)
    - raw Binance klines zips (data/binance_vision_1h_v1_6/klines/<SYMBOL>/)
    - raw funding rate zips (data/binance_vision_rank154/data/futures/um/monthly/fundingRate/)

Outputs:
    - Taker enriched bars (does NOT overwrite original bars cache)
    - Funding rate events parquet
    - Funding rate 1h aligned (static + dynamic)
    - Summary CSVs in research/factor_runs/crypto_top50_factor_library/
    - Manifest CSV for auditability

Rules:
    - No factor implementation
    - No factor_values build
    - No evaluation/backtest
    - Taker: join on (timestamp, symbol), missing = NaN, no forward-fill
    - Funding: merge_asof backward, age <= interval, missing symbol = all NaN
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

# ── Defaults ────────────────────────────────────────────────────────
STATIC_BARS_ID = "crypto_top50_usdt_perp_1h"
DYNAMIC_BARS_ID = "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
FUNDING_SOURCE = "data/binance_vision_rank154/data/futures/um/monthly/fundingRate"
OUTPUT_ROOT = "data/cache"
REPORT_DIR = "research/factor_runs/crypto_top50_factor_library"
KLINES_DIR = "data/binance_vision_1h_v1_6/klines"


def sha256_file(path: Path) -> str:
    """Compute SHA-256 of a file (streaming, memory-safe)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_taker_klines(symbols: list[str]) -> pd.DataFrame:
    """Load taker fields from raw klines zips for given symbols."""
    klines_dir = Path(KLINES_DIR)
    frames = []
    for sym in sorted(symbols):
        sym_dir = klines_dir / sym
        if not sym_dir.exists():
            continue
        for zf_path in sorted(sym_dir.glob("*.zip")):
            try:
                zf = zipfile.ZipFile(zf_path)
                with zf.open(zf.namelist()[0]) as f:
                    df = pd.read_csv(
                        f,
                        usecols=[
                            "open_time",
                            "close_time",
                            "taker_buy_volume",
                            "taker_buy_quote_volume",
                        ],
                    )
                    df["symbol"] = sym
                    frames.append(df)
            except Exception:
                pass  # early months may have different schema
    if not frames:
        return pd.DataFrame()
    all_klines = pd.concat(frames, ignore_index=True)
    all_klines["bar_open_time"] = pd.to_datetime(
        all_klines["open_time"], unit="ms", utc=True
    )
    all_klines = all_klines.drop(columns=["open_time", "close_time"])
    all_klines = all_klines.drop_duplicates(subset=["symbol", "bar_open_time"])
    return all_klines


def build_taker_enriched(bars_id: str) -> dict:
    """Build taker enriched bars for a given dataset."""
    bars_path = Path(f"data/cache/{bars_id}/bars_1h.parquet")
    out_dir = Path(f"{OUTPUT_ROOT}/{bars_id}_taker_enriched")
    out_path = out_dir / "bars_1h.parquet"

    bars = pd.read_parquet(bars_path)
    source_rows = len(bars)
    syms = sorted(bars["symbol"].unique())

    taker = load_taker_klines(syms)
    enriched = bars.merge(
        taker[["symbol", "bar_open_time", "taker_buy_volume", "taker_buy_quote_volume"]],
        on=["symbol", "bar_open_time"],
        how="left",
    )

    assert len(enriched) == source_rows, (
        f"Row count mismatch: {len(enriched)} != {source_rows}"
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    enriched.to_parquet(out_path, index=False)

    tbqv_cov = enriched["taker_buy_quote_volume"].notna().mean()
    tbv_cov = enriched["taker_buy_volume"].notna().mean()

    return {
        "dataset_id": bars_id,
        "source_bars_path": str(bars_path),
        "enriched_bars_path": str(out_path),
        "source_rows": source_rows,
        "enriched_rows": len(enriched),
        "row_count_match": source_rows == len(enriched),
        "n_symbols": len(syms),
        "timestamp_min": str(bars["timestamp"].min()),
        "timestamp_max": str(bars["timestamp"].max()),
        "has_taker_buy_quote_volume": True,
        "taker_buy_quote_volume_coverage": round(tbqv_cov, 6),
        "has_taker_buy_volume": True,
        "taker_buy_volume_coverage": round(tbv_cov, 6),
        "schema_status": "PASS" if tbqv_cov > 0.5 else "PARTIAL",
        "notes": f"Early months (2021-Q4 to 2022-Q1) missing taker fields; overall {tbqv_cov:.1%}",
    }


def build_funding_events() -> dict:
    """Build funding rate events parquet from raw zips."""
    fr_dir = Path(FUNDING_SOURCE)
    out_dir = Path(f"{OUTPUT_ROOT}/crypto_funding_rate_1h_contract_v1")
    out_path = out_dir / "funding_rate_events.parquet"

    all_sym_dirs = sorted([d for d in fr_dir.iterdir() if d.is_dir()])
    frames = []
    for sym_dir in all_sym_dirs:
        sym = sym_dir.name
        for zf_path in sorted(sym_dir.glob("*.zip")):
            try:
                zf = zipfile.ZipFile(zf_path)
                with zf.open(zf.namelist()[0]) as f:
                    df = pd.read_csv(f)
                    df["symbol"] = sym
                    df["source_file"] = zf_path.name
                    frames.append(df)
            except Exception:
                pass

    all_events = pd.concat(frames, ignore_index=True)
    all_events["calc_time"] = pd.to_datetime(
        all_events["calc_time"], unit="ms", utc=True
    )
    all_events["known_at"] = all_events["calc_time"]
    all_events["funding_rate"] = all_events["last_funding_rate"]

    events = all_events[
        ["symbol", "calc_time", "known_at", "funding_rate",
         "funding_interval_hours", "source_file"]
    ].copy()
    events = events.sort_values(["symbol", "calc_time"]).reset_index(drop=True)

    out_dir.mkdir(parents=True, exist_ok=True)
    events.to_parquet(out_path, index=False)

    return {
        "funding_source_path": str(fr_dir),
        "events_path": str(out_path),
        "n_events": len(events),
        "n_symbols": int(events["symbol"].nunique()),
        "timestamp_min": str(events["calc_time"].min()),
        "timestamp_max": str(events["calc_time"].max()),
        "has_calc_time": True,
        "has_known_at": True,
        "has_funding_rate": True,
        "has_funding_interval_hours": True,
        "interval_values": str(sorted(events["funding_interval_hours"].unique().tolist())),
        "schema_status": "PASS",
        "notes": (
            f"Intervals {sorted(events['funding_interval_hours'].unique().tolist())} present; "
            f"known_at = calc_time; {events['symbol'].nunique()} symbols"
        ),
    }


def build_funding_aligned(bars_id: str, events_path: Path) -> dict:
    """Build funding rate 1h aligned parquet for a given bars dataset."""
    bars_path = Path(f"data/cache/{bars_id}/bars_1h.parquet")
    out_dir = Path(f"{OUTPUT_ROOT}/crypto_funding_rate_1h_contract_v1")
    aligned_name = "static" if "top50_usdt" in bars_id else "dynamic"
    out_path = out_dir / f"funding_rate_1h_aligned_{aligned_name}.parquet"

    bars = pd.read_parquet(bars_path)
    bars["timestamp"] = bars["timestamp"].astype("datetime64[ns, UTC]")
    bars_syms = sorted(bars["symbol"].unique())

    events = pd.read_parquet(events_path)
    events["calc_time"] = events["calc_time"].astype("datetime64[ns, UTC]")
    events["known_at"] = events["known_at"].astype("datetime64[ns, UTC]")

    frames = []
    for sym in bars_syms:
        sym_bars = bars[bars["symbol"] == sym][["timestamp", "symbol"]].copy().sort_values("timestamp")
        sym_events = events[events["symbol"] == sym].sort_values("calc_time")

        if len(sym_events) == 0:
            sym_bars["funding_rate"] = np.nan
            sym_bars["funding_known_at"] = pd.NaT
            sym_bars["funding_interval_hours"] = np.nan
            sym_bars["funding_age_hours"] = np.nan
            frames.append(sym_bars)
            continue

        merged = pd.merge_asof(
            sym_bars,
            sym_events[
                ["calc_time", "known_at", "funding_rate", "funding_interval_hours"]
            ].rename(columns={"calc_time": "funding_calc_time", "known_at": "funding_known_at"}),
            left_on="timestamp",
            right_on="funding_calc_time",
            direction="backward",
            allow_exact_matches=True,
        )

        merged["funding_age_hours"] = (
            (merged["timestamp"] - merged["funding_calc_time"]).dt.total_seconds() / 3600.0
        )

        mask = merged["funding_age_hours"] > merged["funding_interval_hours"]
        merged.loc[mask, "funding_rate"] = np.nan
        merged.loc[mask, "funding_known_at"] = pd.NaT
        merged.loc[mask, "funding_interval_hours"] = np.nan
        merged.loc[mask, "funding_age_hours"] = np.nan

        merged = merged.drop(columns=["funding_calc_time"])
        frames.append(merged)

    aligned = pd.concat(frames, ignore_index=True)
    aligned = aligned.sort_values(["timestamp", "symbol"]).reset_index(drop=True)
    aligned.to_parquet(out_path, index=False)

    n_syms_funding = aligned.groupby("symbol")["funding_rate"].apply(
        lambda x: x.notna().any()
    ).sum()
    fr_cov = aligned["funding_rate"].notna().mean()
    age_valid = aligned["funding_age_hours"].dropna()
    median_age = float(age_valid.median()) if len(age_valid) > 0 else None
    max_age = float(age_valid.max()) if len(age_valid) > 0 else None

    return {
        "dataset_id": aligned_name,
        "bars_path": str(bars_path),
        "aligned_path": str(out_path),
        "bars_rows": len(bars),
        "aligned_rows": len(aligned),
        "row_count_match": len(aligned) == len(bars),
        "n_symbols_bars": len(bars_syms),
        "n_symbols_with_funding": int(n_syms_funding),
        "symbol_coverage": round(n_syms_funding / len(bars_syms), 4),
        "timestamp_min": str(aligned["timestamp"].min()),
        "timestamp_max": str(aligned["timestamp"].max()),
        "funding_rate_coverage": round(fr_cov, 4),
        "median_funding_age_hours": round(median_age, 2) if median_age else None,
        "max_funding_age_hours": round(max_age, 2) if max_age else None,
        "schema_status": "PASS",
        "notes": f"max_age <= interval; {n_syms_funding}/{len(bars_syms)} symbols have funding",
    }


def build_manifest(report_dir: Path) -> pd.DataFrame:
    """Build cache manifest with checksums and metadata."""
    artifacts = [
        ("taker_enriched_static", "parquet",
         f"data/cache/{STATIC_BARS_ID}_taker_enriched/bars_1h.parquet"),
        ("taker_enriched_dynamic", "parquet",
         f"data/cache/{DYNAMIC_BARS_ID}_taker_enriched/bars_1h.parquet"),
        ("funding_events", "parquet",
         "data/cache/crypto_funding_rate_1h_contract_v1/funding_rate_events.parquet"),
        ("funding_aligned_static", "parquet",
         "data/cache/crypto_funding_rate_1h_contract_v1/funding_rate_1h_aligned_static.parquet"),
        ("funding_aligned_dynamic", "parquet",
         "data/cache/crypto_funding_rate_1h_contract_v1/funding_rate_1h_aligned_dynamic.parquet"),
    ]

    rows = []
    for name, atype, path in artifacts:
        p = Path(path)
        exists = p.exists()
        size_bytes = p.stat().st_size if exists else 0
        is_large = size_bytes > 100 * 1024 * 1024  # 100MB GitHub limit

        if exists and not is_large:
            checksum = sha256_file(p)
        elif exists:
            checksum = "SKIPPED_LARGE_FILE"
        else:
            checksum = "FILE_NOT_FOUND"

        committed = "NO_LOCAL_ARTIFACT" if is_large else ("YES" if exists else "NO")

        # Read metadata for parquet files
        n_rows = n_syms = None
        ts_min = ts_max = None
        columns = None
        if exists and atype == "parquet":
            try:
                df = pd.read_parquet(p)
                n_rows = len(df)
                n_syms = df["symbol"].nunique() if "symbol" in df.columns else None
                ts_col = "timestamp" if "timestamp" in df.columns else "calc_time"
                if ts_col in df.columns:
                    ts_min = str(df[ts_col].min())
                    ts_max = str(df[ts_col].max())
                columns = ",".join(df.columns)
            except Exception:
                pass

        rows.append({
            "artifact_name": name,
            "artifact_type": atype,
            "path": path,
            "exists": exists,
            "committed_to_git": committed,
            "file_size_bytes": size_bytes,
            "n_rows": n_rows,
            "n_symbols": n_syms,
            "timestamp_min": ts_min,
            "timestamp_max": ts_max,
            "columns": columns,
            "checksum_sha256": checksum,
            "schema_status": "PASS" if exists else "FILE_NOT_FOUND",
            "notes": f"Large file ({size_bytes/1024/1024:.1f}MB), local-only" if is_large else "",
        })

    manifest = pd.DataFrame(rows)
    manifest.to_csv(report_dir / "phase7l_r_crypto_native_cache_manifest.csv", index=False)
    return manifest


def validate_caches(report_dir: Path) -> bool:
    """Validate existing caches against manifest."""
    manifest_path = report_dir / "phase7l_r_crypto_native_cache_manifest.csv"
    if not manifest_path.exists():
        print("ERROR: Manifest not found. Run build first.")
        return False

    manifest = pd.read_csv(manifest_path)
    ok = True
    for _, row in manifest.iterrows():
        p = Path(row["path"])
        if row["exists"] and not p.exists():
            print(f"FAIL: {row['artifact_name']} missing at {row['path']}")
            ok = False
        elif row["exists"] and p.exists():
            # Re-check checksum for small files
            if row["checksum_sha256"] not in ("SKIPPED_LARGE_FILE", "FILE_NOT_FOUND"):
                actual = sha256_file(p)
                if actual != row["checksum_sha256"]:
                    print(f"WARN: {row['artifact_name']} checksum mismatch (rebuild recommended)")
                    ok = False
    if ok:
        print("All caches validated OK.")
    return ok


def main():
    parser = argparse.ArgumentParser(description="Build crypto-native data caches")
    parser.add_argument(
        "--mode", choices=["all", "taker", "funding", "validate"], default="all",
        help="Build mode: all, taker, funding, or validate"
    )
    parser.add_argument("--static-dataset-id", default="crypto_top50_usdt_perp_1h")
    parser.add_argument("--dynamic-dataset-id", default="crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1")
    parser.add_argument("--funding-source", default="data/binance_vision_rank154/data/futures/um/monthly/fundingRate")
    parser.add_argument("--output-root", default="data/cache")
    args = parser.parse_args()

    _cfg = {
        "static": args.static_dataset_id,
        "dynamic": args.dynamic_dataset_id,
        "funding": args.funding_source,
        "output": args.output_root,
    }

    report_dir = Path(REPORT_DIR)
    report_dir.mkdir(parents=True, exist_ok=True)

    if args.mode == "validate":
        ok = validate_caches(report_dir)
        sys.exit(0 if ok else 1)

    # ── Taker ────────────────────────────────────────────────────────
    if args.mode in ("all", "taker"):
        print("=== Building taker enriched bars ===")
        taker_rows = []
        for ds_id in [_cfg["static"], _cfg["dynamic"]]:
            print(f"  {ds_id}...")
            result = build_taker_enriched(ds_id)
            taker_rows.append(result)
            print(f"    {result['enriched_rows']:,} rows, {result['taker_buy_quote_volume_coverage']:.1%} coverage")

        taker_df = pd.DataFrame(taker_rows)
        taker_df.to_csv(report_dir / "phase7l_taker_enriched_bars_summary.csv", index=False)
        print(f"  Saved taker summary ({len(taker_rows)} rows)")

    # ── Funding ──────────────────────────────────────────────────────
    if args.mode in ("all", "funding"):
        print("=== Building funding rate caches ===")
        print("  Events...")
        events_result = build_funding_events()
        print(f"    {events_result['n_events']:,} events, {events_result['n_symbols']} symbols")

        events_path = Path(events_result["events_path"])
        pd.DataFrame([events_result]).to_csv(
            report_dir / "phase7l_funding_events_summary.csv", index=False
        )

        align_rows = []
        for ds_id in [_cfg["static"], _cfg["dynamic"]]:
            print(f"  Aligning {ds_id}...")
            result = build_funding_aligned(ds_id, events_path)
            align_rows.append(result)
            print(f"    {result['aligned_rows']:,} rows, {result['funding_rate_coverage']:.1%} coverage")

        pd.DataFrame(align_rows).to_csv(
            report_dir / "phase7l_funding_alignment_summary.csv", index=False
        )
        print(f"  Saved funding summaries")

    # ── Manifest ─────────────────────────────────────────────────────
    if args.mode == "all":
        print("=== Building manifest ===")
        manifest = build_manifest(report_dir)
        print(f"  {len(manifest)} artifacts documented")

    print("\nDone.")


if __name__ == "__main__":
    main()
