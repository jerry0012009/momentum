#!/usr/bin/env python3
"""PM-58A: Backfill LS monthly aggregate fields in canonical LS summary.

Reads monthly LS returns from factor_monthly_long_short_series.csv and fills
missing aggregate fields in factor_level_long_short_summary.csv.

Calculation rules match evaluate_factors.py PM-41 logic exactly:
  std = monthly.std(ddof=1)
  mean = monthly.mean()
  annualized_return = mean * 12
  annualized_vol = std * sqrt(12)
  cum = cumprod(1 + monthly)
  peak = maximum.accumulate(cum)
  drawdown = (cum - peak) / peak
  max_drawdown = drawdown.min()
  positive_period_rate = mean(monthly > 0)
  n_monthly_periods = len(monthly)
  annualization_method = "monthly_x12"

Usage:
  python scripts/backfill_ls_monthly_aggregate_fields.py [--dry-run]
"""

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RUN = Path("research/factor_runs/crypto_top50_factor_library")
DIAG = RUN / "factor_diagnostics"
EVAL = RUN / "factor_level_evaluation"

FIELDS = [
    "long_short_spread_std",
    "long_short_spread_annualized_return",
    "long_short_spread_annualized_vol",
    "long_short_spread_max_drawdown",
    "long_short_spread_positive_period_rate",
    "n_monthly_periods",
    "annualization_method",
]


def compute_aggregates(ls_returns: np.ndarray) -> dict:
    """Compute monthly LS aggregate stats matching evaluate_factors.py PM-41."""
    n = len(ls_returns)
    if n < 2:
        return {}
    std = float(np.std(ls_returns, ddof=1))
    mean = float(np.mean(ls_returns))
    ann_ret = mean * 12
    ann_vol = std * math.sqrt(12)
    cum = np.cumprod(1 + ls_returns)
    peak = np.maximum.accumulate(cum)
    dd = (cum - peak) / peak
    max_dd = float(dd.min())
    pos_rate = float(np.mean(ls_returns > 0))
    return {
        "long_short_spread_std": round(std, 8),
        "long_short_spread_annualized_return": round(ann_ret, 8),
        "long_short_spread_annualized_vol": round(ann_vol, 8),
        "long_short_spread_max_drawdown": round(max_dd, 8),
        "long_short_spread_positive_period_rate": round(pos_rate, 4),
        "n_monthly_periods": n,
        "annualization_method": "monthly_x12",
    }


def main():
    parser = argparse.ArgumentParser(description="PM-58A: Backfill LS monthly aggregate fields")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing")
    args = parser.parse_args()

    # Load inputs
    monthly = pd.read_csv(DIAG / "factor_monthly_long_short_series.csv")
    ls_summary = pd.read_csv(EVAL / "factor_level_long_short_summary.csv")

    print(f"Monthly LS series: {len(monthly)} rows, {monthly['factor_id'].nunique()} factors")
    print(f"LS summary: {len(ls_summary)} rows, {ls_summary['factor_name'].nunique()} factors")

    # Build lookup: (factor_id, horizon) -> list of monthly LS returns
    monthly_lookup = {}
    for (fid, hz), grp in monthly.groupby(["factor_id", "horizon"]):
        returns = grp["long_short_return"].dropna().values
        if len(returns) > 0:
            monthly_lookup[(fid, hz)] = returns

    print(f"Monthly LS lookup: {len(monthly_lookup)} factor×horizon combos")

    # Backfill
    filled = 0
    skipped_has_data = 0
    skipped_no_series = 0
    details = []

    for idx, row in ls_summary.iterrows():
        fid = row["factor_name"]
        hz = row["horizon"]

        # Skip if already has data
        if pd.notna(row.get("long_short_spread_std")):
            skipped_has_data += 1
            continue

        # Get monthly series
        key = (fid, hz)
        ls_rets = monthly_lookup.get(key)
        if ls_rets is None or len(ls_rets) < 2:
            skipped_no_series += 1
            details.append(f"  SKIP {fid}/{hz}: no monthly series (len={0 if ls_rets is None else len(ls_rets)})")
            continue

        # Compute aggregates
        agg = compute_aggregates(ls_rets)
        if not agg:
            skipped_no_series += 1
            continue

        # Apply to summary
        for field, val in agg.items():
            ls_summary.at[idx, field] = val
        filled += 1
        details.append(f"  FILL {fid}/{hz}: {len(ls_rets)} months, std={agg['long_short_spread_std']:.6f}")

    print(f"\nResults:")
    print(f"  Filled: {filled}")
    print(f"  Skipped (already has data): {skipped_has_data}")
    print(f"  Skipped (no monthly series): {skipped_no_series}")

    if details and len(details) <= 20:
        print("\nDetails:")
        for d in details:
            print(d)

    # Verify no remaining gaps where series exists
    remaining_missing = 0
    for idx, row in ls_summary.iterrows():
        fid = row["factor_name"]
        hz = row["horizon"]
        if pd.isna(row.get("long_short_spread_std")):
            if (fid, hz) in monthly_lookup:
                remaining_missing += 1
                print(f"  WARNING: {fid}/{hz} still missing but has monthly series!")

    if remaining_missing > 0:
        print(f"\nERROR: {remaining_missing} rows still missing despite having monthly series!")
        return 1

    if args.dry_run:
        print("\n[DRY RUN] No files written.")
        return 0

    # Write CSV
    ls_summary.to_csv(EVAL / "factor_level_long_short_summary.csv", index=False)
    print(f"\nWrote CSV: {EVAL / 'factor_level_long_short_summary.csv'}")

    # Write JSON
    records = ls_summary.to_dict(orient="records")
    with open(EVAL / "factor_level_long_short_summary.json", "w") as f:
        json.dump(records, f, indent=2, default=str)
    print(f"Wrote JSON: {EVAL / 'factor_level_long_short_summary.json'}")

    # Final verification
    final = pd.read_csv(EVAL / "factor_level_long_short_summary.csv")
    still_missing = final["long_short_spread_std"].isna().sum()
    print(f"\nFinal: {still_missing}/{len(final)} rows still missing long_short_spread_std")
    return 0


if __name__ == "__main__":
    sys.exit(main())
