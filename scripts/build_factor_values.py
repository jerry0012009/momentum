#!/usr/bin/env python3
"""Build registered research factor values for the crypto Top50 1h universe.

Now uses factor_formula_registry.REGISTRY for all factor computation.
Iterates FactorSpec list — no hand-coded factor logic in this file.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))
from factor_formula_registry import REGISTRY


def calc_group(g: pd.DataFrame) -> pd.DataFrame:
    """Compute all registered factors for a single-symbol group."""
    g = g.copy().sort_values("timestamp")
    result_cols = ["timestamp", "symbol"]
    for spec in REGISTRY:
        g[spec.factor_id] = spec.compute_fn(g)
        result_cols.append(spec.factor_id)
    return g[result_cols]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset-id", default="crypto_top50_usdt_perp_1h",
                    help="Dataset ID under data/cache/ and data/features/")
    args = p.parse_args()

    cache = ROOT / "data" / "cache" / args.dataset_id
    feature = ROOT / "data" / "features" / args.dataset_id
    bars_path = cache / "bars_1h.parquet"

    print(f"Build factor values (registry mode)")
    print(f"Dataset: {args.dataset_id}")
    print(f"Registered factors: {len(REGISTRY)}")

    if not bars_path.exists():
        raise FileNotFoundError(bars_path)
    bars = pd.read_parquet(bars_path)
    if bars.empty:
        raise ValueError("bars_1h.parquet is empty; fetch bars first")
    bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
    bars = bars.sort_values(["symbol", "timestamp"])

    parts = []
    for _sym, g in bars.groupby("symbol", sort=False):
        parts.append(calc_group(g))
    wide = pd.concat(parts, ignore_index=True)

    computed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    factor_ids = [spec.factor_id for spec in REGISTRY]

    for name in factor_ids:
        out = wide[["timestamp", "symbol", name]].rename(columns={name: "factor_value"})
        out.insert(2, "factor_name", name)
        out["known_at"] = out["timestamp"]
        out["source_timeframe"] = "1h"
        out["computed_at"] = computed_at
        out = out[["timestamp", "symbol", "factor_name", "factor_value",
                    "known_at", "source_timeframe", "computed_at"]]
        target_dir = feature / name
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / "factor_values.parquet"
        out.to_parquet(target, index=False)
        print(f"  {name}: rows={len(out)} coverage={out['factor_value'].notna().mean():.3%}")


if __name__ == "__main__":
    main()
