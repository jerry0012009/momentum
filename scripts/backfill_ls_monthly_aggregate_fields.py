#!/usr/bin/env python3
"""PM-58B: Backfill LS monthly aggregate fields with canonical annualization.

Reads monthly LS returns from factor_monthly_long_short_series.csv and
RECOMPUTES all aggregate fields in factor_level_long_short_summary.csv
using the horizon-aware bars_per_year formula.

Calculation rules (aligned with evaluate_factors.py PM-58B):
  std = monthly.std(ddof=1)
  mean = monthly.mean()
  annualized_return = mean * bars_per_year   # horizon-aware
  annualized_vol = std * sqrt(12)            # monthly edge stability
  cum = cumprod(1 + monthly)
  peak = maximum.accumulate(cum)
  drawdown = (cum - peak) / peak
  max_drawdown = drawdown.min()
  positive_period_rate = mean(monthly > 0)
  n_monthly_periods = len(monthly)
  annualization_method = "per_bar_mean_x_bars_per_year"

bars_per_year: 1h=8760, 4h=2190, 24h=365, 72h=365/3

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

_BARS_PER_YEAR = {"1h": 8760, "4h": 2190, "24h": 365, "72h": 365 / 3}

FIELDS = [
    "long_short_spread_std",
    "long_short_spread_annualized_return",
    "long_short_spread_annualized_vol",
    "long_short_spread_max_drawdown",
    "long_short_spread_positive_period_rate",
    "n_monthly_periods",
    "annualization_method",
]


def compute_aggregates(ls_returns: np.ndarray, horizon: str) -> dict:
    """Compute monthly LS aggregate stats matching evaluate_factors.py PM-58B."""
    n = len(ls_returns)
    if n < 2:
        return {}
    std = float(np.std(ls_returns, ddof=1))
    mean = float(np.mean(ls_returns))
    bpy = _BARS_PER_YEAR.get(horizon, 8760)
    # Ann Return: per-bar LS mean × bars_per_year (horizon-aware annualization)
    ann_ret = mean * bpy
    # Sharpe/Vol: monthly edge stability metrics × √12
    # These are NOT portfolio Sharpe/Vol — they measure per-bar LS return stability.
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
        "annualization_method": "per_bar_mean_x_bars_per_year",
    }


def main():
    parser = argparse.ArgumentParser(description="PM-58B: Backfill LS monthly aggregate fields")
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

    # Recompute ALL rows (not just missing) — old formula was wrong
    filled = 0
    skipped_no_series = 0
    details = []

    for idx, row in ls_summary.iterrows():
        fid = row["factor_name"]
        hz = row["horizon"]

        # Get monthly series
        key = (fid, hz)
        ls_rets = monthly_lookup.get(key)
        if ls_rets is None or len(ls_rets) < 2:
            skipped_no_series += 1
            continue

        # Compute aggregates with new formula
        agg = compute_aggregates(ls_rets, hz)
        if not agg:
            skipped_no_series += 1
            continue

        # Apply to summary (overwrites old values)
        for field, val in agg.items():
            ls_summary.at[idx, field] = val
        filled += 1

    print(f"\nResults:")
    print(f"  Recomputed: {filled}")
    print(f"  Skipped (no monthly series): {skipped_no_series}")

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
