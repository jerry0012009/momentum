#!/usr/bin/env python3
"""Evaluate registered factors under dynamic-universe membership filtering.

Unlike evaluate_factors.py which uses global missing_bar_rate > 5% to exclude
symbols (wrong for dynamic universe), this script filters to only rows where
each symbol is actually selected by the dynamic universe in that month.

Usage:
    python scripts/evaluate_factors_dynamic_universe.py \
      --dataset-id crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1 \
      --universe-id crypto_usdt_perp_monthly_volume_top50_current_listed_v1
"""
from __future__ import annotations

import argparse
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
    """Filter factor values and labels to only selected symbol-months.

    Returns:
        (merged_df, n_before, n_after, n_selected_symbols, n_selected_months)
    """
    # Merge factor values with labels on [timestamp, symbol]
    merged = fv.merge(labels, on=["timestamp", "symbol"], how="inner")
    n_before = len(merged)

    # Add month_str
    merged["month_str"] = merged["timestamp"].dt.strftime("%Y-%m")

    # Build universe lookup: (symbol, month_str)
    snap_lookup = snapshots[["symbol", "month_str"]].drop_duplicates()

    # Inner join: keep only rows where symbol is selected in that month
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

    # Load catalog directions
    directions = load_catalog_directions(CATALOG)

    # Pre-filter labels to universe membership (do once, not per-factor)
    labels["month_str"] = labels["timestamp"].dt.strftime("%Y-%m")
    snap_lookup_unique = snapshots[["symbol", "month_str"]].drop_duplicates()
    labels_filt = labels.merge(snap_lookup_unique, on=["symbol", "month_str"], how="inner")
    labels_filt = labels_filt.drop(columns=["month_str"])
    print(f"  Labels after universe filter: {len(labels_filt):,} rows")

    # Discover factors
    factors = discover_factors(args.dataset_id)
    print(f"Discovered {len(factors)} factors: {factors}")

    # Evaluate each factor
    summary_rows = []

    for fid in factors:
        print(f"\n--- {fid} ---")
        fv_path = ROOT / "data" / "features" / args.dataset_id / fid / "factor_values.parquet"
        fv = pd.read_parquet(fv_path)
        fv["timestamp"] = pd.to_datetime(fv["timestamp"], utc=True)

        # Filter fv to selected symbol-months via merge
        fv["month_str"] = fv["timestamp"].dt.strftime("%Y-%m")
        n_before = len(fv)
        fv_filt = fv.merge(snap_lookup_unique, on=["symbol", "month_str"], how="inner")
        fv_filt = fv_filt.drop(columns=["month_str"])
        n_after = len(fv_filt)

        # Merge on [timestamp, symbol]
        filtered = fv_filt.merge(labels_filt, on=["timestamp", "symbol"], how="inner")
        n_symbols = filtered["symbol"].nunique() if len(filtered) > 0 else 0
        n_months = filtered["timestamp"].dt.strftime("%Y-%m").nunique() if len(filtered) > 0 else 0
        print(f"  rows: {n_before:,} → {n_after:,}  symbols: {n_symbols}  months: {n_months}")

        # Evaluate each label
        expected_dir = directions.get(fid, "positive")
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

        # Write per-factor outputs
        write_factor_json(fid, factor_metrics, output_dir / f"{fid}_dynamic_eval.json",
                          args.dataset_id, args.universe_id, n_before, n_after, n_symbols, n_months)
        write_factor_md(fid, factor_metrics, output_dir / f"{fid}_dynamic_eval.md",
                        args.dataset_id, args.universe_id, n_before, n_after)

        # Summary row: use ret_fwd_1h as primary label
        primary = factor_metrics.get("ret_fwd_1h", {})
        summary_rows.append({
            "factor_id": fid,
            "label": "ret_fwd_1h",
            "expected_direction": expected_dir,
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

    # Static vs dynamic comparison (minimal)
    static_summary_path = RUN / "phase4_factor_eval_summary.csv"
    if static_summary_path.exists():
        static_df = pd.read_csv(static_summary_path)
        comp_rows = []
        for _, srow in summary_df.iterrows():
            s = static_df[static_df["factor_id"] == srow["factor_id"]]
            if s.empty:
                continue
            s = s.iloc[0]
            comp_rows.append({
                "factor_id": srow["factor_id"],
                "label": "ret_fwd_1h",
                "static_RankIC_mean": s.get("RankIC_mean"),
                "dynamic_RankIC_mean": srow.get("RankIC_mean"),
                "delta_RankIC": clean_float(float(srow.get("RankIC_mean") or 0) - float(s.get("RankIC_mean") or 0)) if srow.get("RankIC_mean") is not None and s.get("RankIC_mean") is not None else None,
                "static_direction_adjusted_spread": s.get("direction_adjusted_spread"),
                "dynamic_direction_adjusted_spread": srow.get("direction_adjusted_spread"),
                "delta_spread": clean_float(float(srow.get("direction_adjusted_spread") or 0) - float(s.get("direction_adjusted_spread") or 0)) if srow.get("direction_adjusted_spread") is not None and s.get("direction_adjusted_spread") is not None else None,
            })
        if comp_rows:
            comp_df = pd.DataFrame(comp_rows)
            comp_path = RUN / "phase6g_static_vs_dynamic_minimal_comparison.csv"
            comp_df.to_csv(comp_path, index=False)
            print(f"Wrote static-vs-dynamic comparison: {comp_path}")
    else:
        print("Static summary not found; comparison deferred to Phase 6H")


if __name__ == "__main__":
    main()
