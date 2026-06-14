#!/usr/bin/env python3
"""Build forward-return labels for a bars dataset.

Uses calendar-time join: ret_fwd_h = close[timestamp + h hours] / close[timestamp] - 1
NOT shift(-h) which is row-based and breaks on gaps.

Usage:
    python scripts/build_labels.py --dataset-id crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

HORIZONS = [1, 4, 24, 72]


def build_labels(bars: pd.DataFrame, horizons: list[int] | None = None) -> pd.DataFrame:
    """Build forward-return labels using calendar-time join.

    For each row (timestamp, symbol), look up close at timestamp + h hours
    by joining on the exact future timestamp. Gaps produce NaN (no fallback).

    Args:
        bars: DataFrame with columns [timestamp, symbol, close]
        horizons: list of forward horizons in hours (default: [1, 4, 24, 72])

    Returns:
        DataFrame with columns [timestamp, symbol, ret_fwd_{h}h, ...]
    """
    if horizons is None:
        horizons = HORIZONS

    # Base: timestamp + symbol + close
    base = bars[["timestamp", "symbol", "close"]].copy()
    base = base.sort_values(["symbol", "timestamp"]).reset_index(drop=True)

    # For each horizon, join future close via calendar-time lookup
    result = base[["timestamp", "symbol"]].copy()

    for h in horizons:
        # Close lookup: (symbol, timestamp) → close at that timestamp
        close_lookup = base[["symbol", "timestamp", "close"]].rename(
            columns={"close": "future_close", "timestamp": "target_ts"}
        )

        # For each row, compute the target timestamp we want to look up
        base_with_target = base[["timestamp", "symbol", "close"]].copy()
        base_with_target["target_ts"] = base_with_target["timestamp"] + pd.Timedelta(hours=h)

        # Left join: find close at (symbol, target_ts)
        merged = base_with_target.merge(
            close_lookup,
            on=["symbol", "target_ts"],
            how="left",
        )

        # Forward return: close[timestamp + h] / close[timestamp] - 1
        ret = merged["future_close"] / base["close"] - 1
        # Where join failed (gap), future_close is NaN → ret is NaN (correct)
        result[f"ret_fwd_{h}h"] = ret.values

    return result


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dataset-id", required=True)
    p.add_argument("--horizons", nargs="+", type=int, default=HORIZONS)
    args = p.parse_args()

    bars_path = DATA_DIR / "cache" / args.dataset_id / "bars_1h.parquet"
    output_dir = DATA_DIR / "features" / args.dataset_id
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading bars: {bars_path}")
    bars = pd.read_parquet(bars_path)
    print(f"  {len(bars):,} rows, {bars['symbol'].nunique()} symbols")

    print(f"Building labels with horizons: {args.horizons}")
    labels = build_labels(bars, args.horizons)

    # Write labels
    labels_path = output_dir / "labels.parquet"
    labels.to_parquet(labels_path, index=False)
    print(f"Wrote: {labels_path} ({len(labels):,} rows)")

    # Write manifest
    manifest = {
        "dataset_id": args.dataset_id,
        "source_bars_path": str(bars_path),
        "labels_path": str(labels_path),
        "timestamp_convention": "timestamp = bar_close_time = bar_open_time + 1h",
        "horizons": args.horizons,
        "label_definition": "ret_fwd_{h}h = close[timestamp + h hours] / close[timestamp] - 1; calendar-time join, no row-shift",
        "n_rows": len(labels),
        "created_at": pd.Timestamp.now(tz="UTC").isoformat(),
        "script": "scripts/build_labels.py",
        "known_limitations": [
            "Calendar-time join: gaps in bars produce NaN labels (no forward-fill).",
            "Tail rows lack future data — their labels are NaN by design.",
            "Universe is dynamic_from_current_listed_pool, not true point-in-time.",
        ],
    }
    manifest_path = output_dir / "labels_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote: {manifest_path}")

    # Summary
    print(f"\n=== Label Summary ===")
    for h in args.horizons:
        col = f"ret_fwd_{h}h"
        miss = labels[col].isna().mean()
        print(f"  {col}: missing={miss:.4f} ({miss*100:.2f}%)")


if __name__ == "__main__":
    main()
