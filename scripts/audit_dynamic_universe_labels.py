#!/usr/bin/env python3
"""Audit label quality for dynamic-universe dataset.

Computes global and membership-aware label coverage, checks QA thresholds,
and outputs reports.

Usage:
    python scripts/audit_dynamic_universe_labels.py \
      --dataset-id crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1 \
      --universe-id crypto_usdt_perp_monthly_volume_top50_current_listed_v1
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"

HORIZONS = [1, 4, 24, 72]

# QA thresholds
THRESHOLDS = {
    1: 0.01,   # 1%
    4: 0.01,   # 1%
    24: 0.03,  # 3%
    72: 0.05,  # 5%
}


def compute_global_coverage(labels: pd.DataFrame) -> dict:
    """Global label missing rates per horizon."""
    result = {"n_label_rows": len(labels)}
    for h in HORIZONS:
        col = f"ret_fwd_{h}h"
        result[f"ret_fwd_{h}h_missing_rate"] = round(float(labels[col].isna().mean()), 6)
    return result


def compute_membership_aware_coverage(
    labels: pd.DataFrame,
    snapshots: pd.DataFrame,
) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    """Compute label coverage only during months when symbols are selected.

    Returns:
        (summary_dict, by_horizon_month_df, by_horizon_symbol_df)
    """
    # Build symbol→months from snapshots
    snap = snapshots.copy()
    snap["asof_time"] = pd.to_datetime(snap["asof_time"], utc=True)
    snap["month_str"] = snap["asof_time"].dt.strftime("%Y-%m")

    symbol_months: dict[str, set[str]] = {}
    for _, row in snap.iterrows():
        symbol_months.setdefault(row["symbol"], set()).add(row["month_str"])

    # Detect available horizons from label columns
    label_horizons = []
    for h in HORIZONS:
        if f"ret_fwd_{h}h" in labels.columns:
            label_horizons.append(h)
    horizon_cols = [f"ret_fwd_{h}h" for h in label_horizons]

    # Add month_str to labels
    lab = labels[["timestamp", "symbol"] + horizon_cols].copy()
    lab["month_str"] = lab["timestamp"].dt.strftime("%Y-%m")

    # Filter to selected symbol-months only
    def is_selected(row):
        months = symbol_months.get(row["symbol"])
        return months is not None and row["month_str"] in months

    mask = lab.apply(is_selected, axis=1)
    selected = lab[mask].copy()

    # Summary
    summary = {"selected_label_rows": len(selected)}
    for h in label_horizons:
        col = f"ret_fwd_{h}h"
        summary[f"selected_ret_fwd_{h}h_missing_rate"] = round(float(selected[col].isna().mean()), 6) if len(selected) > 0 else 0.0

    # By horizon × month
    hm_rows = []
    for h in label_horizons:
        col = f"ret_fwd_{h}h"
        for month, grp in selected.groupby("month_str"):
            total = len(grp)
            missing = int(grp[col].isna().sum())
            hm_rows.append({
                "month": month,
                "horizon": h,
                "selected_rows": total,
                "missing_rows": missing,
                "missing_rate": round(missing / total, 6) if total > 0 else 0.0,
            })
    by_horizon_month = pd.DataFrame(hm_rows).sort_values(["horizon", "month"]).reset_index(drop=True)

    # By horizon × symbol
    hs_rows = []
    for h in label_horizons:
        col = f"ret_fwd_{h}h"
        for sym, grp in selected.groupby("symbol"):
            total = len(grp)
            missing = int(grp[col].isna().sum())
            hs_rows.append({
                "symbol": sym,
                "horizon": h,
                "selected_rows": total,
                "missing_rows": missing,
                "missing_rate": round(missing / total, 6) if total > 0 else 0.0,
            })
    by_horizon_symbol = pd.DataFrame(hs_rows).sort_values(["horizon", "missing_rate"], ascending=[True, False]).reset_index(drop=True)

    return summary, by_horizon_month, by_horizon_symbol


def compute_qa_decision(selected_summary: dict) -> dict:
    """Check membership-aware missing rates against thresholds."""
    blocked = []
    for h, threshold in THRESHOLDS.items():
        rate = selected_summary.get(f"selected_ret_fwd_{h}h_missing_rate", 0.0)
        if rate > threshold:
            blocked.append(f"ret_fwd_{h}h: {rate:.4f} > {threshold:.4f}")

    decision = "BLOCKED" if blocked else "ALLOWED"
    reason = "; ".join(blocked) if blocked else "Membership-aware label coverage is acceptable"
    return {
        "decision": decision,
        "reason": reason,
        "thresholds": {f"ret_fwd_{h}h": t for h, t in THRESHOLDS.items()},
    }


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dataset-id", required=True)
    p.add_argument("--universe-id", required=True)
    args = p.parse_args()

    bars_path = DATA_DIR / "cache" / args.dataset_id / "bars_1h.parquet"
    labels_path = DATA_DIR / "features" / args.dataset_id / "labels.parquet"
    snapshots_path = DATA_DIR / "universe" / args.universe_id / "universe_snapshots.parquet"

    print(f"Loading labels: {labels_path}")
    labels = pd.read_parquet(labels_path)
    print(f"  {len(labels):,} rows, {labels['symbol'].nunique()} symbols")

    print(f"Loading snapshots: {snapshots_path}")
    snapshots = pd.read_parquet(snapshots_path)

    # Global coverage
    global_cov = compute_global_coverage(labels)
    print(f"\n=== Global Label Coverage ===")
    for h in HORIZONS:
        print(f"  ret_fwd_{h}h missing: {global_cov[f'ret_fwd_{h}h_missing_rate']:.4%}")

    # Membership-aware coverage
    print(f"\nComputing membership-aware coverage...")
    selected_summary, by_horizon_month, by_horizon_symbol = compute_membership_aware_coverage(labels, snapshots)

    print(f"\n=== Membership-Aware Label Coverage ===")
    print(f"  Selected label rows: {selected_summary['selected_label_rows']:,}")
    for h in HORIZONS:
        print(f"  selected ret_fwd_{h}h missing: {selected_summary[f'selected_ret_fwd_{h}h_missing_rate']:.4%}")

    # QA decision
    qa = compute_qa_decision(selected_summary)
    print(f"\n=== QA Decision: {qa['decision']} ===")
    print(f"  Reason: {qa['reason']}")

    # Write outputs
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Summary JSON
    summary = {
        **global_cov,
        **selected_summary,
        "qa_decision": qa["decision"],
        "qa_reason": qa["reason"],
        "thresholds": qa["thresholds"],
    }
    summary_path = OUTPUT_DIR / "phase6e_label_quality_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote: {summary_path}")

    # By horizon-month CSV
    hm_path = OUTPUT_DIR / "phase6e_label_missing_by_horizon_month.csv"
    by_horizon_month.to_csv(hm_path, index=False)
    print(f"Wrote: {hm_path}")

    # By horizon-symbol CSV
    hs_path = OUTPUT_DIR / "phase6e_label_missing_by_horizon_symbol.csv"
    by_horizon_symbol.to_csv(hs_path, index=False)
    print(f"Wrote: {hs_path}")


if __name__ == "__main__":
    main()
