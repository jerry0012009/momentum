#!/usr/bin/env python3
"""Build registered research factor values for the crypto Top50 1h universe.

Now uses factor_formula_registry.REGISTRY for all factor computation.
Iterates FactorSpec list — no hand-coded factor logic in this file.

Supports optional factor subset via --factor-ids or --candidate-csv + --status.
"""
from __future__ import annotations

import argparse
import csv as _csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_ID = "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))
from factor_formula_registry import REGISTRY, REGISTRY_BY_ID


def load_selected_factor_ids(candidate_csv: Path, status: str = "selected_for_7B") -> list[str]:
    """Load factor_ids from candidate CSV filtered by status."""
    with open(candidate_csv, newline="") as f:
        rows = list(_csv.DictReader(f))
    ids = [r["factor_id"] for r in rows if r["status"] == status]
    if not ids:
        raise ValueError(f"No factors with status={status!r} in {candidate_csv}")
    return ids


def validate_factor_ids(factor_ids: Sequence[str]) -> None:
    """Fail fast if any factor_id is not in REGISTRY."""
    registry_ids = set(REGISTRY_BY_ID.keys())
    missing = [fid for fid in factor_ids if fid not in registry_ids]
    if missing:
        raise ValueError(f"Factor IDs not in REGISTRY: {missing}")


def apply_cross_sectional_postprocess(wide: pd.DataFrame) -> pd.DataFrame:
    """Apply cross-sectional rank normalization to xs_rank_* factors.

    For factors that require ranking across symbols at each timestamp,
    this replaces the per-symbol raw metric with a percentile rank.
    """
    wide = wide.copy()
    xs_factors = ["xs_rank_ret_1h", "xs_rank_vol"]
    for factor in xs_factors:
        if factor in wide.columns:
            wide[factor] = (
                wide.groupby("timestamp")[factor]
                .rank(pct=True, method="average")
            )
    return wide


def calc_group(g: pd.DataFrame, factor_ids: Sequence[str] | None = None) -> pd.DataFrame:
    """Compute registered factors for a single-symbol group.

    Args:
        g: DataFrame for one symbol (must have timestamp, OHLCV).
        factor_ids: If provided, only compute these factor_ids.
                    If None, compute all REGISTRY factors.
    """
    g = g.copy().sort_values("timestamp")
    result_cols = ["timestamp", "symbol"]
    specs = REGISTRY if factor_ids is None else [REGISTRY_BY_ID[fid] for fid in factor_ids]
    for spec in specs:
        g[spec.factor_id] = spec.compute_fn(g)
        result_cols.append(spec.factor_id)
    return g[result_cols]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset-id", default=DEFAULT_DATASET_ID,
                    help="Dataset ID under data/cache/ and data/features/")
    p.add_argument("--factor-ids", default=None,
                    help="Comma-separated factor_ids to build (default: all REGISTRY)")
    p.add_argument("--candidate-csv", default=None,
                    help="Path to candidate CSV; use with --status to select factors")
    p.add_argument("--status", default="selected_for_7B",
                    help="Status filter for --candidate-csv (default: selected_for_7B)")
    args = p.parse_args()

    # Determine which factors to build
    if args.factor_ids:
        factor_ids = [s.strip() for s in args.factor_ids.split(",")]
    elif args.candidate_csv:
        csv_path = Path(args.candidate_csv)
        if not csv_path.is_absolute():
            csv_path = ROOT / csv_path
        factor_ids = load_selected_factor_ids(csv_path, args.status)
    else:
        factor_ids = [spec.factor_id for spec in REGISTRY]

    validate_factor_ids(factor_ids)

    cache = ROOT / "data" / "cache" / args.dataset_id
    feature = ROOT / "data" / "features" / args.dataset_id
    bars_path = cache / "bars_1h.parquet"

    print(f"Build factor values (registry mode)")
    print(f"Dataset: {args.dataset_id}")
    print(f"Building {len(factor_ids)} factors: {factor_ids}")

    if not bars_path.exists():
        print(f"ERROR: bars file not found: {bars_path}", flush=True)
        print(f"  Dataset ID: {args.dataset_id}", flush=True)
        print(f"  Expected:   data/cache/{args.dataset_id}/bars_1h.parquet", flush=True)
        print(f"  Hint: pass --dataset-id explicitly if using a non-default dataset", flush=True)
        _sys.exit(1)
    bars = pd.read_parquet(bars_path)
    if bars.empty:
        raise ValueError("bars_1h.parquet is empty; fetch bars first")
    bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
    bars = bars.sort_values(["symbol", "timestamp"])

    parts = []
    for _sym, g in bars.groupby("symbol", sort=False):
        parts.append(calc_group(g, factor_ids))
    wide = pd.concat(parts, ignore_index=True)
    wide = apply_cross_sectional_postprocess(wide)

    computed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

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
