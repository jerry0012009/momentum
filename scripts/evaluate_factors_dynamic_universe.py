#!/usr/bin/env python3
"""Evaluate registered factors under dynamic-universe membership filtering.

Unlike evaluate_factors.py which uses global missing_bar_rate > 5% to exclude
symbols (wrong for dynamic universe), this script filters to only rows where
each symbol is actually selected by the dynamic universe in that month.

Supports optional factor subset via --factor-ids or --candidate-csv + --status.
When --candidate-csv is provided, expected_direction is loaded from it as
primary source (fallback: old catalog, then positive with warning).

Usage:
    python scripts/evaluate_factors_dynamic_universe.py \
      --dataset-id crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1 \
      --universe-id crypto_usdt_perp_monthly_volume_top50_current_listed_v1

    # Phase 7C mode: only evaluate 27 selected_for_7B factors
    python scripts/evaluate_factors_dynamic_universe.py \
      --dataset-id ... --universe-id ... \
      --candidate-csv research/factor_runs/crypto_top50_factor_library/factor_mining_candidates_v0_1.csv \
      --status selected_for_7B
"""
from __future__ import annotations

import argparse
import csv as _csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"
CATALOG = RUN / "factor_catalog_v0_1.csv"
LABEL_NAMES = ["ret_fwd_1h", "ret_fwd_4h", "ret_fwd_24h", "ret_fwd_72h"]
MIN_N = 10
OUTPUT_BASE = ROOT / "reports" / "artifacts" / "factor_eval_dynamic"

# Reuse evaluation kernel from evaluate_factors.py
import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate_factors import (
    clean_float, avg, std, tstat, ratio, turnover, fmt,
    evaluate_one_label, load_catalog_directions, _empty_metrics,
)


def load_selected_factor_ids(candidate_csv: Path, status: str = "selected_for_7B") -> list[str]:
    """Load factor_ids from candidate CSV filtered by status."""
    with open(candidate_csv, newline="") as f:
        rows = list(_csv.DictReader(f))
    ids = [r["factor_id"] for r in rows if r["status"] == status]
    if not ids:
        raise ValueError(f"No factors with status={status!r} in {candidate_csv}")
    return ids


def load_candidate_directions(candidate_csv: Path) -> dict[str, str]:
    """Load expected_direction from candidate CSV (all rows, not just selected)."""
    with open(candidate_csv, newline="") as f:
        rows = list(_csv.DictReader(f))
    return {r["factor_id"]: r["expected_direction"] for r in rows}


def discover_factors(dataset_id: str) -> list[str]:
    """Find factor_ids by looking for factor_values.parquet files."""
    features_dir = ROOT / "data" / "features" / dataset_id
    factors = []
    for d in sorted(features_dir.iterdir()):
        if d.is_dir() and (d / "factor_values.parquet").exists():
            factors.append(d.name)
    return factors


def load_universe_snapshots(universe_id: str) -> pd.DataFrame:
    """Load universe snapshots and add month_str column."""
    path = ROOT / "data" / "universe" / universe_id / "universe_snapshots.parquet"
    snap = pd.read_parquet(path)
    snap["asof_time"] = pd.to_datetime(snap["asof_time"], utc=True)
    snap["month_str"] = snap["asof_time"].dt.strftime("%Y-%m")
    return snap


def apply_universe_membership_filter(
    fv: pd.DataFrame,
    labels: pd.DataFrame,
    snapshots: pd.DataFrame,
) -> tuple[pd.DataFrame, int, int, int, int]:
    """Filter factor values and labels to only selected symbol-months."""
    merged = fv.merge(labels, on=["timestamp", "symbol"], how="inner")
    n_before = len(merged)
    merged["month_str"] = merged["timestamp"].dt.strftime("%Y-%m")
    snap_lookup = snapshots[["symbol", "month_str"]].drop_duplicates()
    filtered = merged.merge(snap_lookup, on=["symbol", "month_str"], how="inner")
    n_after = len(filtered)
    n_symbols = filtered["symbol"].nunique() if n_after > 0 else 0
    n_months = filtered["month_str"].nunique() if n_after > 0 else 0
    return filtered, n_before, n_after, n_symbols, n_months


def write_factor_json(factor_id: str, metrics: dict, path: Path,
                      dataset_id: str, universe_id: str,
                      n_before: int, n_after: int,
                      n_symbols: int, n_months: int) -> None:
    """Write per-factor evaluation JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "dataset_id": dataset_id,
        "universe_id": universe_id,
        "factor_id": factor_id,
        "evaluation_mode": "dynamic_universe_membership",
        "universe_mode": "dynamic_from_current_listed_pool",
        "n_merged_rows_before_universe_filter": n_before,
        "n_rows_after_universe_filter": n_after,
        "n_selected_symbols": n_symbols,
        "n_selected_months": n_months,
        "label_metrics": metrics,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "known_limitations": [
            "Universe is dynamic_from_current_listed_pool, not true point-in-time.",
            "No global missing_bar_rate exclusion applied.",
            "Membership-aware filtering: only selected symbol-months evaluated.",
        ],
    }
    path.write_text(json.dumps(output, indent=2, default=str) + "\n", encoding="utf-8")


def write_factor_md(factor_id: str, metrics: dict[str, dict], path: Path,
                    dataset_id: str, universe_id: str,
                    n_before: int, n_after: int) -> None:
    """Write per-factor evaluation markdown."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Factor Evaluation: {factor_id} (Dynamic Universe)",
        "",
        f"- dataset_id: `{dataset_id}`",
        f"- universe_id: `{universe_id}`",
        f"- evaluation_mode: dynamic_universe_membership",
        f"- rows before filter: {n_before:,}",
        f"- rows after filter: {n_after:,}",
        "",
    ]
    for label, m in metrics.items():
        lines.append(f"## {label}")
        lines.append(f"- expected_direction: {m.get('expected_direction', 'positive')}")
        lines.append(f"- IC_mean: {fmt(m.get('IC_mean'))}  ICIR: {fmt(m.get('ICIR'))}")
        lines.append(f"- RankIC_mean: {fmt(m.get('RankIC_mean'))}  RankICIR: {fmt(m.get('RankICIR'))}")
        lines.append(f"- direction_adjusted_spread: {fmt(m.get('direction_adjusted_spread'))}  tstat: {fmt(m.get('direction_adjusted_tstat'))}")
        lines.append(f"- turnover: {fmt(m.get('turnover'))}  coverage: {fmt(m.get('coverage'))}")
        lines.append(f"- n_timestamps: {m.get('n_timestamps', 0)}  n_symbols_avg: {fmt(m.get('n_symbols_avg'))}  n_valid_rows: {m.get('n_valid_rows', 0)}")
        lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dataset-id", required=True)
    p.add_argument("--universe-id", required=True)
    p.add_argument("--factor-ids", default=None,
                    help="Comma-separated factor_ids to evaluate (default: auto-discover)")
    p.add_argument("--candidate-csv", default=None,
                    help="Path to candidate CSV for factor selection and direction lookup")
    p.add_argument("--status", default="selected_for_7B",
                    help="Status filter for --candidate-csv (default: selected_for_7B)")
    args = p.parse_args()

    output_dir = OUTPUT_BASE / args.dataset_id / args.universe_id
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load universe snapshots
    print(f"Loading universe snapshots: {args.universe_id}")
    snapshots = load_universe_snapshots(args.universe_id)
    print(f"  {len(snapshots)} snapshot rows, {snapshots['symbol'].nunique()} unique symbols")

    # Load labels
    labels_path = ROOT / "data" / "features" / args.dataset_id / "labels.parquet"
    print(f"Loading labels: {labels_path}")
    labels = pd.read_parquet(labels_path)
    labels["timestamp"] = pd.to_datetime(labels["timestamp"], utc=True)
    print(f"  {len(labels):,} label rows")

    # Build direction lookup: candidate CSV (primary) → old catalog (fallback) → positive (last resort)
    candidate_directions: dict[str, str] = {}
    if args.candidate_csv:
        csv_path = Path(args.candidate_csv)
        if not csv_path.is_absolute():
            csv_path = ROOT / csv_path
        candidate_directions = load_candidate_directions(csv_path)
        print(f"  Loaded {len(candidate_directions)} candidate directions from {csv_path.name}")

    catalog_directions = load_catalog_directions(CATALOG)

    def get_direction(factor_id: str) -> tuple[str, str]:
        """Return (direction, source) for a factor_id."""
        if factor_id in candidate_directions:
            return candidate_directions[factor_id], "candidate_csv"
        if factor_id in catalog_directions:
            return catalog_directions[factor_id], "catalog"
        return "positive", "fallback_positive"

    # Pre-filter labels to universe membership
    labels["month_str"] = labels["timestamp"].dt.strftime("%Y-%m")
    snap_lookup_unique = snapshots[["symbol", "month_str"]].drop_duplicates()
    labels_filt = labels.merge(snap_lookup_unique, on=["symbol", "month_str"], how="inner")
    labels_filt = labels_filt.drop(columns=["month_str"])
    print(f"  Labels after universe filter: {len(labels_filt):,} rows")

    # Determine which factors to evaluate
    if args.factor_ids:
        factors = [s.strip() for s in args.factor_ids.split(",")]
    elif args.candidate_csv:
        csv_path = Path(args.candidate_csv)
        if not csv_path.is_absolute():
            csv_path = ROOT / csv_path
        factors = load_selected_factor_ids(csv_path, args.status)
    else:
        factors = discover_factors(args.dataset_id)

    # Verify all have factor_values
    features_dir = ROOT / "data" / "features" / args.dataset_id
    available = set()
    missing_fv = []
    for fid in factors:
        fv_path = features_dir / fid / "factor_values.parquet"
        if fv_path.exists():
            available.add(fid)
        else:
            missing_fv.append(fid)

    explicit_mode = bool(args.factor_ids or args.candidate_csv)
    if missing_fv and explicit_mode:
        raise FileNotFoundError(
            f"Missing factor_values for explicitly requested factors: {missing_fv}"
        )
    if missing_fv:
        print(f"  WARNING: {len(missing_fv)} factors have no factor_values.parquet: {missing_fv}")
    factors = [fid for fid in factors if fid in available]

    # In candidate mode, verify expected count
    if args.candidate_csv and args.status == "selected_for_7B" and len(factors) != 27:
        raise ValueError(
            f"Expected 27 selected_for_7B factors but got {len(factors)}: {factors}"
        )

    print(f"Evaluating {len(factors)} factors")

    # Track direction sources
    direction_sources: dict[str, str] = {}
    fallback_factors: list[str] = []

    # Evaluate each factor
    summary_rows = []

    for fid in factors:
        print(f"\n--- {fid} ---")
        fv_path = features_dir / fid / "factor_values.parquet"
        fv = pd.read_parquet(fv_path)
        fv["timestamp"] = pd.to_datetime(fv["timestamp"], utc=True)

        fv["month_str"] = fv["timestamp"].dt.strftime("%Y-%m")
        n_before = len(fv)
        fv_filt = fv.merge(snap_lookup_unique, on=["symbol", "month_str"], how="inner")
        fv_filt = fv_filt.drop(columns=["month_str"])
        n_after = len(fv_filt)

        filtered = fv_filt.merge(labels_filt, on=["timestamp", "symbol"], how="inner")
        n_symbols = filtered["symbol"].nunique() if len(filtered) > 0 else 0
        n_months = filtered["timestamp"].dt.strftime("%Y-%m").nunique() if len(filtered) > 0 else 0
        print(f"  rows: {n_before:,} → {n_after:,}  symbols: {n_symbols}  months: {n_months}")

        expected_dir, dir_source = get_direction(fid)
        direction_sources[fid] = dir_source
        if dir_source == "fallback_positive":
            if explicit_mode:
                raise ValueError(
                    f"Factor {fid} has no expected_direction in candidate CSV or catalog; "
                    f"fallback positive is not allowed in explicit/candidate mode"
                )
            fallback_factors.append(fid)
            print(f"  WARNING: no direction found, fallback to positive")

        factor_metrics = {}

        for label in LABEL_NAMES:
            if label not in filtered.columns:
                continue
            if filtered[label].notna().sum() == 0:
                factor_metrics[label] = _empty_metrics(label, None, n_after, expected_dir)
                continue
            m = evaluate_one_label(filtered, label, expected_dir)
            factor_metrics[label] = m
            print(f"  {label}: RankIC={fmt(m.get('RankIC_mean'))} spread={fmt(m.get('direction_adjusted_spread'))}")

        write_factor_json(fid, factor_metrics, output_dir / f"{fid}_dynamic_eval.json",
                          args.dataset_id, args.universe_id, n_before, n_after, n_symbols, n_months)
        write_factor_md(fid, factor_metrics, output_dir / f"{fid}_dynamic_eval.md",
                        args.dataset_id, args.universe_id, n_before, n_after)

        primary = factor_metrics.get("ret_fwd_1h", {})
        summary_rows.append({
            "factor_id": fid,
            "label": "ret_fwd_1h",
            "expected_direction": expected_dir,
            "direction_source": dir_source,
            "IC_mean": primary.get("IC_mean"),
            "ICIR": primary.get("ICIR"),
            "RankIC_mean": primary.get("RankIC_mean"),
            "RankICIR": primary.get("RankICIR"),
            "quantile_spread_mean": primary.get("quantile_spread_mean"),
            "direction_adjusted_spread": primary.get("direction_adjusted_spread"),
            "turnover": primary.get("turnover"),
            "coverage": primary.get("coverage"),
            "n_timestamps": primary.get("n_timestamps"),
            "n_symbols_avg": primary.get("n_symbols_avg"),
            "n_valid_rows": primary.get("n_valid_rows"),
        })

    # Write summary
    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(output_dir / "factor_eval_dynamic_summary.csv", index=False)
    summary_path = output_dir / "factor_eval_dynamic_summary.json"
    summary_path.write_text(json.dumps(summary_rows, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"\nWrote summary: {summary_path}")

    # Report direction sources
    if fallback_factors:
        print(f"\nWARNING: {len(fallback_factors)} factors used fallback positive direction: {fallback_factors}")
    else:
        print(f"\nAll {len(factors)} factors have explicit expected_direction (no fallback positive)")


if __name__ == "__main__":
    main()
