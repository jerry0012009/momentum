#!/usr/bin/env python3
"""Export factor data in Alphalens-compatible format.

Produces parquet files that can be loaded into Alphalens format without
requiring the Alphalens package itself.

Usage:
    python scripts/export_alphalens_factor_data.py \
        --dataset-id crypto_top50_usdt_perp_1h_long_v1 \
        --factor-id mom_20h \
        --horizons 1h 4h 24h 72h
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache"
FEATURES = ROOT / "data" / "features"
EXPORT_BASE = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "alphalens_exports"


def load_data(dataset_id: str, factor_id: str):
    """Load bars, factor_values, and labels."""
    bars_path = CACHE / dataset_id / "bars_1h.parquet"
    fv_path = FEATURES / dataset_id / factor_id / "factor_values.parquet"
    labels_path = FEATURES / dataset_id / "labels.parquet"

    if not bars_path.exists():
        raise FileNotFoundError(f"Bars not found: {bars_path}")
    if not fv_path.exists():
        raise FileNotFoundError(f"Factor values not found: {fv_path}")
    if not labels_path.exists():
        raise FileNotFoundError(f"Labels not found: {labels_path}")

    bars = pd.read_parquet(bars_path)
    fv = pd.read_parquet(fv_path)
    labels = pd.read_parquet(labels_path)
    return bars, fv, labels


def build_factor_series(fv: pd.DataFrame) -> pd.DataFrame:
    """Extract factor_series: timestamp, symbol, factor_value."""
    return fv[["timestamp", "symbol", "factor_value"]].copy()


def build_prices_wide(bars: pd.DataFrame) -> pd.DataFrame:
    """Pivot close prices to wide format: index=timestamp, columns=symbol."""
    prices = bars.pivot(index="timestamp", columns="symbol", values="close")
    prices.index.name = "timestamp"
    return prices


def build_forward_returns(labels: pd.DataFrame, horizons: list[str]) -> pd.DataFrame:
    """Extract forward returns for specified horizons."""
    cols = ["timestamp", "symbol"]
    for h in horizons:
        col = f"ret_fwd_{h}"
        if col not in labels.columns:
            raise ValueError(f"Label column '{col}' not found. Available: {list(labels.columns)}")
        cols.append(col)
    return labels[cols].copy()


def build_alphalens_factor_data(
    factor_series: pd.DataFrame,
    forward_returns: pd.DataFrame,
    horizons: list[str],
) -> pd.DataFrame:
    """Combine factor values with forward returns and add quantile labels."""
    merged = factor_series.merge(forward_returns, on=["timestamp", "symbol"], how="inner")

    # Cross-sectional quantile per timestamp (5 buckets)
    merged["factor_quantile"] = merged.groupby("timestamp")["factor_value"].transform(
        lambda x: pd.qcut(x, 5, labels=False, duplicates="drop") + 1
    )

    # Rename for Alphalens convention
    rename = {"factor_value": "factor"}
    for h in horizons:
        rename[f"ret_fwd_{h}"] = f"forward_return_{h}"
    merged = merged.rename(columns=rename)

    return merged


def build_manifest(
    dataset_id: str,
    factor_id: str,
    horizons: list[str],
    n_rows: int,
    n_symbols: int,
    date_range: tuple[str, str],
    output_dir: Path,
) -> dict:
    """Create export manifest."""
    return {
        "dataset_id": dataset_id,
        "factor_id": factor_id,
        "horizons": horizons,
        "n_rows": n_rows,
        "n_symbols": n_symbols,
        "date_range": list(date_range),
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "files": sorted(str(p.relative_to(output_dir)) for p in output_dir.glob("*.parquet")),
        "schema_notes": {
            "factor_series": "timestamp, symbol, factor_value",
            "prices_wide": "index=timestamp, columns=symbol, values=close",
            "forward_returns_long": "timestamp, symbol, ret_fwd_{h}",
            "alphalens_factor_data": "timestamp, symbol, factor, forward_return_{h}, factor_quantile",
        },
        "source_of_truth": "evaluate_factors.py (not Alphalens)",
        "no_status_upgrade_from_alphalens": True,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dataset-id", required=True)
    p.add_argument("--factor-id", required=True)
    p.add_argument("--horizons", nargs="+", default=["1h", "4h", "24h", "72h"])
    args = p.parse_args()

    horizons = args.horizons
    dataset_id = args.dataset_id
    factor_id = args.factor_id

    # Load data
    bars, fv, labels = load_data(dataset_id, factor_id)
    print(f"Loaded bars={len(bars)}, factor_values={len(fv)}, labels={len(labels)}")

    # Build exports
    factor_series = build_factor_series(fv)
    prices_wide = build_prices_wide(bars)
    forward_returns = build_forward_returns(labels, horizons)
    alphalens_data = build_alphalens_factor_data(factor_series, forward_returns, horizons)

    # Output directory
    output_dir = EXPORT_BASE / dataset_id / factor_id
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write parquet files
    factor_series.to_parquet(output_dir / "factor_series.parquet", index=False)
    prices_wide.to_parquet(output_dir / "prices_wide.parquet")
    forward_returns.to_parquet(output_dir / "forward_returns_long.parquet", index=False)
    alphalens_data.to_parquet(output_dir / "alphalens_factor_data.parquet", index=False)

    # Write manifest
    manifest = build_manifest(
        dataset_id=dataset_id,
        factor_id=factor_id,
        horizons=horizons,
        n_rows=len(factor_series),
        n_symbols=factor_series["symbol"].nunique(),
        date_range=(
            factor_series["timestamp"].min().isoformat(),
            factor_series["timestamp"].max().isoformat(),
        ),
        output_dir=output_dir,
    )
    (output_dir / "export_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Exported to {output_dir}/")
    print(f"  factor_series: {len(factor_series)} rows")
    print(f"  prices_wide: {prices_wide.shape}")
    print(f"  forward_returns: {len(forward_returns)} rows")
    print(f"  alphalens_factor_data: {len(alphalens_data)} rows")
    print(f"  quantile range: {alphalens_data['factor_quantile'].min()}-{alphalens_data['factor_quantile'].max()}")


if __name__ == "__main__":
    main()
