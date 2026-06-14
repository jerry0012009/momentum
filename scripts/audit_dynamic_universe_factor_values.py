#!/usr/bin/env python3
"""Audit factor value quality for dynamic-universe dataset.

Computes global and membership-aware factor coverage, checks QA thresholds,
and outputs reports.

Usage:
    python scripts/audit_dynamic_universe_factor_values.py \
      --dataset-id crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1 \
      --universe-id crypto_usdt_perp_monthly_volume_top50_current_listed_v1
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"

# QA threshold: selected_missing_rate > 5% blocks Phase 6G
MISSING_RATE_THRESHOLD = 0.05

# Known factor lookback windows (from factor_formula_registry.py)
LOOKBACK_WINDOWS = {
    "mom_20h": 20,
    "reversal_5h": 5,
    "volatility_20h": 21,
    "rsi_14h": 14,
    "bb_zscore_20h": 20,
    "wq101_alpha101": 1,
    "wq101_alpha12": 2,
    "wq101_alpha53": 10,
    "q158_high_low_range": 1,
    "tech_macd": 26,
    "tech_atr": 15,
}


def discover_factors(dataset_id: str) -> list[str]:
    """Find factor_ids by looking for factor_values.parquet files."""
    features_dir = DATA_DIR / "features" / dataset_id
    factors = []
    for d in sorted(features_dir.iterdir()):
        if d.is_dir() and (d / "factor_values.parquet").exists():
            factors.append(d.name)
    return factors


def compute_global_coverage(fv: pd.DataFrame, factor_id: str) -> dict:
    """Global factor coverage stats."""
    return {
        "factor_id": factor_id,
        "n_rows": len(fv),
        "n_symbols": fv["symbol"].nunique(),
        "global_non_null_rate": round(float(fv["factor_value"].notna().mean()), 6),
        "global_missing_rate": round(float(fv["factor_value"].isna().mean()), 6),
    }


def compute_membership_aware_coverage(
    fv: pd.DataFrame,
    snapshots: pd.DataFrame,
    factor_id: str,
) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    """Compute factor coverage only during months when symbols are selected.

    Returns:
        (summary_dict, by_factor_month_df, by_factor_symbol_df)
    """
    # Build symbol→months from snapshots
    snap = snapshots.copy()
    snap["asof_time"] = pd.to_datetime(snap["asof_time"], utc=True)
    snap["month_str"] = snap["asof_time"].dt.strftime("%Y-%m")
    # Create lookup: (symbol, month_str) for merge
    snap_lookup = snap[["symbol", "month_str"]].drop_duplicates()

    # Add month_str to factor values
    fv = fv.copy()
    fv["month_str"] = fv["timestamp"].dt.strftime("%Y-%m")

    # Filter to selected symbol-months via merge (much faster than apply)
    selected = fv.merge(snap_lookup, on=["symbol", "month_str"], how="inner")

    # Summary
    n_selected = len(selected)
    selected_missing = float(selected["factor_value"].isna().mean()) if n_selected > 0 else 0.0
    lookback = LOOKBACK_WINDOWS.get(factor_id, 0)

    summary = {
        "factor_id": factor_id,
        "selected_rows": n_selected,
        "selected_non_null_rate": round(1 - selected_missing, 6),
        "selected_missing_rate": round(selected_missing, 6),
        "selected_symbols": selected["symbol"].nunique() if n_selected > 0 else 0,
        "selected_months": selected["month_str"].nunique() if n_selected > 0 else 0,
        "lookback_window": lookback,
        "qa_status": "PASS" if selected_missing <= MISSING_RATE_THRESHOLD else "FAIL",
    }

    # By factor × month
    hm_rows = []
    for month, grp in selected.groupby("month_str"):
        total = len(grp)
        missing = int(grp["factor_value"].isna().sum())
        hm_rows.append({
            "factor_id": factor_id,
            "month": month,
            "selected_rows": total,
            "missing_rows": missing,
            "missing_rate": round(missing / total, 6) if total > 0 else 0.0,
        })
    by_factor_month = pd.DataFrame(hm_rows).sort_values("month").reset_index(drop=True)

    # By factor × symbol
    hs_rows = []
    for sym, grp in selected.groupby("symbol"):
        total = len(grp)
        missing = int(grp["factor_value"].isna().sum())
        hs_rows.append({
            "factor_id": factor_id,
            "symbol": sym,
            "selected_rows": total,
            "missing_rows": missing,
            "missing_rate": round(missing / total, 6) if total > 0 else 0.0,
        })
    by_factor_symbol = pd.DataFrame(hs_rows).sort_values("missing_rate", ascending=False).reset_index(drop=True)

    return summary, by_factor_month, by_factor_symbol


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dataset-id", required=True)
    p.add_argument("--universe-id", required=True)
    args = p.parse_args()

    snapshots_path = DATA_DIR / "universe" / args.universe_id / "universe_snapshots.parquet"
    print(f"Loading snapshots: {snapshots_path}")
    snapshots = pd.read_parquet(snapshots_path)

    factors = discover_factors(args.dataset_id)
    print(f"Discovered {len(factors)} factors: {factors}")

    all_global = []
    all_selected = []
    all_by_month = []
    all_by_symbol = []

    for fid in factors:
        fv_path = DATA_DIR / "features" / args.dataset_id / fid / "factor_values.parquet"
        fv = pd.read_parquet(fv_path)
        fv["timestamp"] = pd.to_datetime(fv["timestamp"], utc=True)

        global_cov = compute_global_coverage(fv, fid)
        all_global.append(global_cov)

        selected_summary, by_month, by_symbol = compute_membership_aware_coverage(fv, snapshots, fid)
        all_selected.append(selected_summary)
        all_by_month.append(by_month)
        all_by_symbol.append(by_symbol)

        status = selected_summary["qa_status"]
        miss = selected_summary["selected_missing_rate"]
        print(f"  {fid}: selected_missing={miss:.4%} [{status}]")

    # QA decision
    blocked = [s for s in all_selected if s["qa_status"] == "FAIL"]
    decision = "BLOCKED" if blocked else "ALLOWED"
    blocked_ids = [s["factor_id"] for s in blocked] if blocked else []

    print(f"\n=== QA Decision: {decision} ===")
    if blocked_ids:
        print(f"  Blocked factors: {blocked_ids}")

    # Write outputs
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Summary JSON
    summary = {
        "dataset_id": args.dataset_id,
        "universe_id": args.universe_id,
        "n_factors": len(factors),
        "qa_decision": decision,
        "qa_threshold": MISSING_RATE_THRESHOLD,
        "blocked_factors": blocked_ids,
        "global_coverage": all_global,
        "membership_aware_coverage": all_selected,
    }
    summary_path = OUTPUT_DIR / "phase6f_factor_coverage_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote: {summary_path}")

    # By factor-month CSV
    by_month_df = pd.concat(all_by_month, ignore_index=True)
    hm_path = OUTPUT_DIR / "phase6f_factor_missing_by_factor_month.csv"
    by_month_df.to_csv(hm_path, index=False)
    print(f"Wrote: {hm_path}")

    # By factor-symbol CSV
    by_symbol_df = pd.concat(all_by_symbol, ignore_index=True)
    hs_path = OUTPUT_DIR / "phase6f_factor_missing_by_factor_symbol.csv"
    by_symbol_df.to_csv(hs_path, index=False)
    print(f"Wrote: {hs_path}")


if __name__ == "__main__":
    main()
