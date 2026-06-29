#!/usr/bin/env python3
"""Build Factor Conclusion Cards — per-factor diagnostic summary.

Reads evaluation outputs from an intake run directory and produces
a conclusion card per factor with all key metrics, redundancy info,
and a conservative decision bucket.

Usage:
    python scripts/build_factor_conclusion_cards.py --run-dir <path> --factor-ids rev_1h mom_72h
    python scripts/build_factor_conclusion_cards.py --run-dir <path>  # all factors in run

Phase 13A-P3. Not production. Not live trading.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

sys.path.insert(0, str(SCRIPTS))

from public_factor_manifest_guard import raise_for_skipped_public_factor_ids


def load_csv(path: Path, name: str | None = None) -> pd.DataFrame:
    """Load CSV if it exists. Warn if missing or empty. Validate expected columns."""
    if not path.exists():
        if name:
            print(f"  WARN: {name} not found at {path} — will use defaults")
        return pd.DataFrame()
    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        if name:
            print(f"  WARN: {name} is empty (no columns) at {path}")
        return pd.DataFrame()
    if name and df.empty:
        print(f"  WARN: {name} is empty at {path}")
    return df


def compute_monthly_stability(period_df: pd.DataFrame, fid: str, hz: str) -> str:
    """Summarize monthly IC stability for a factor × horizon."""
    sub = period_df[(period_df["factor_name"] == fid) & (period_df["horizon"] == hz)]
    if len(sub) == 0:
        return "NO_DATA"
    adj_ics = sub["direction_adjusted_mean_rank_ic"].dropna()
    if len(adj_ics) == 0:
        return "NO_DATA"
    pos_months = (adj_ics > 0).sum()
    total = len(adj_ics)
    ratio = pos_months / total if total > 0 else 0
    if ratio >= 0.8:
        return f"STABLE ({pos_months}/{total} months positive)"
    elif ratio >= 0.6:
        return f"MODERATE ({pos_months}/{total} months positive)"
    elif ratio >= 0.4:
        return f"MIXED ({pos_months}/{total} months positive)"
    else:
        return f"UNSTABLE ({pos_months}/{total} months positive)"


def compute_quantile_monotonicity(quantile_df: pd.DataFrame, fid: str, hz: str) -> str:
    """Check if quantile returns are monotonically increasing/decreasing."""
    sub = quantile_df[(quantile_df["factor_name"] == fid) & (quantile_df["horizon"] == hz)]
    if len(sub) == 0:
        return "NO_DATA"
    buckets = sub[sub["bucket"] != "LONG_SHORT"].sort_values("bucket")
    if len(buckets) < 3:
        return "INSUFFICIENT_QUANTILES"
    means = buckets["mean_forward_return"].dropna().values
    if len(means) < 3:
        return "INSUFFICIENT_QUANTILES"
    # Check monotonicity
    diffs = np.diff(means)
    all_pos = all(d > 0 for d in diffs)
    all_neg = all(d < 0 for d in diffs)
    if all_pos:
        return "MONOTONIC_INCREASING"
    elif all_neg:
        return "MONOTONIC_DECREASING"
    else:
        # Count direction changes
        sign_changes = sum(1 for i in range(1, len(diffs)) if diffs[i] * diffs[i-1] < 0)
        if sign_changes <= 1:
            return "NEARLY_MONOTONIC"
        else:
            return f"NON_MONOTONIC ({sign_changes} sign changes)"


def find_nearest_existing(
    fid: str,
    redundancy_df: pd.DataFrame,
    n: int = 3,
) -> list[str]:
    """Find the nearest existing factors by redundancy correlation."""
    if redundancy_df.empty:
        return []
    sub = redundancy_df[
        (redundancy_df["factor_i"] == fid) | (redundancy_df["factor_j"] == fid)
    ].copy()
    if len(sub) == 0:
        return []
    sub = sub.sort_values("abs_spearman_corr", ascending=False)
    nearest = []
    for _, row in sub.head(n).iterrows():
        other = row["factor_j"] if row["factor_i"] == fid else row["factor_i"]
        corr = row["abs_spearman_corr"]
        level = row["redundancy_level"]
        nearest.append(f"{other} (|ρ|={corr:.3f}, {level})")
    return nearest


def determine_decision_bucket(
    review_bucket: str,
    rl_consistency: str,
    best_adj_ic: float | None,
    best_adj_icir: float | None,
    best_ls_t: float | None,
    redundancy_level: str,
    monotonicity: str,
    stability: str,
    in_signal: bool,
) -> tuple[str, str, list[str]]:
    """Determine decision bucket, recommended action, and caveats."""
    caveats = []

    if in_signal:
        return "ACTIVE_IN_SIGNAL", "No action needed. Already in signal panel.", caveats

    if review_bucket == "MISSING_INPUT":
        return "MISSING_INPUT", "Acquire required data source before evaluation.", caveats

    if review_bucket == "MISSING_INPUT_DATA":
        return "MISSING_INPUT", "Acquire required data source before evaluation.", caveats

    # Divergent or direction review
    if review_bucket in ("DIRECTION_REVIEW_REQUIRED", "TAIL_OR_MONOTONICITY_REVIEW_REQUIRED"):
        caveats.append("RankIC-longshort divergence. Direction semantics need review.")
        return "REVIEW_REQUIRED", "Do not promote. Investigate direction semantics.", caveats

    # Redundancy
    if redundancy_level in ("NEAR_DUPLICATE", "HIGH_REDUNDANCY"):
        caveats.append(f"Redundancy level: {redundancy_level}. Consider dropping one factor.")
        return "REDUNDANT_WITH_EXISTING", "Do not promote. Resolve redundancy first.", caveats

    # Conditional direction
    if review_bucket == "CONDITIONAL_DIRECTION_REVIEW":
        caveats.append("Conditional direction — no expected sign to adjust IC.")
        return "CONDITIONAL_DIRECTION_REVIEW", "Keep for diagnostic. Do not promote without direction analysis.", caveats

    # Strong candidate checks
    if review_bucket == "STRONG_DIAGNOSTIC_CANDIDATE":
        # Additional checks
        if "NON_MONOTONIC" in monotonicity:
            caveats.append("Non-monotonic quantile returns. Check tail behavior.")
            return "TAIL_OR_MONOTONICITY_REVIEW_REQUIRED", "Do not promote. Quantile monotonicity issue.", caveats
        if "UNSTABLE" in stability:
            caveats.append("Unstable monthly IC. May not generalize.")
            return "REVIEW_REQUIRED", "Do not promote. Monthly IC stability insufficient.", caveats
        if rl_consistency == "DIVERGENT":
            caveats.append("RankIC-longshort divergence despite strong IC.")
            return "DIRECTION_REVIEW_REQUIRED", "Do not promote. Resolve divergence.", caveats
        return "PASS_DIAGNOSTIC", "Candidate for future signal research. Not auto-promoted.", caveats

    # RankIC strong, long-short weak
    if review_bucket == "RANKIC_STRONG_LONGSHORT_WEAK":
        caveats.append("RankIC significant but long-short spread not significant.")
        return "RANKIC_STRONG_LONGSHORT_WEAK", "Monitor. May improve with better quantile construction.", caveats

    # Long-short strong, RankIC weak
    if review_bucket == "LONGSHORT_STRONG_RANKIC_WEAK":
        caveats.append("Long-short spread significant but RankIC weak.")
        return "LONGSHORT_STRONG_RANKIC_WEAK", "Monitor. May be driven by tail quantiles.", caveats

    # Weak
    if review_bucket == "WEAK_OR_NOISY":
        return "WEAK_OR_NOISY", "Keep in registry for completeness. No action needed.", caveats

    # Default
    return "REVIEW_REQUIRED", "Manual review needed.", caveats


def build_cards(
    run_dir: Path,
    factor_ids: list[str] | None = None,
) -> pd.DataFrame:
    """Build conclusion cards from an intake run directory."""
    # Load all inputs
    review_df = load_csv(run_dir / "factor_candidate_review.csv", "candidate_review")
    metric_df = load_csv(run_dir / "factor_metric_panel.csv", "metric_panel")
    period_df = load_csv(run_dir / "factor_period_ic_summary.csv", "period_ic_summary")
    quantile_df = load_csv(run_dir / "factor_quantile_return_summary.csv", "quantile_return_summary")
    redundancy_df = load_csv(run_dir / "factor_redundancy.csv", "redundancy")
    inventory_df = load_csv(run_dir / "factor_inventory.csv", "inventory")

    # Determine factor IDs (with schema guards)
    if factor_ids is None:
        if not review_df.empty and "factor_name" in review_df.columns:
            factor_ids = review_df["factor_name"].tolist()
        elif not inventory_df.empty and "factor_id" in inventory_df.columns:
            factor_ids = inventory_df["factor_id"].tolist()
        else:
            print("  ERROR: no factor IDs found — review_df or inventory_df missing expected columns")
            print(f"    review_df columns: {list(review_df.columns)}")
            print(f"    inventory_df columns: {list(inventory_df.columns)}")
            return pd.DataFrame()

    raise_for_skipped_public_factor_ids(factor_ids, action="conclusion-carded")

    cards = []
    for fid in factor_ids:
        # From review (with schema guard)
        if review_df.empty or "factor_name" not in review_df.columns:
            rev_row = pd.DataFrame()
        else:
            rev_row = review_df[review_df["factor_name"] == fid]
        if len(rev_row) > 0:
            r = rev_row.iloc[0]
            family = r.get("category", "unknown")
            expected_direction = r.get("expected_direction", "unknown")
            best_adj_ic = r.get("best_adj_ic")
            best_adj_ic_hz = r.get("best_adj_ic_horizon")
            best_adj_icir = r.get("best_direction_adjusted_icir")
            best_ls_hz = r.get("best_long_short_horizon")
            best_ls_spread = r.get("best_long_short_spread")
            best_ls_t = r.get("best_long_short_t_stat")
            best_win = r.get("best_ic_win_rate_adjusted")
            coverage_min = r.get("coverage_min")
            missing_rate_max = r.get("missing_rate_max")
            rl_consistency = r.get("rankic_longshort_consistency", "N/A")
            review_bucket = r.get("review_bucket", "UNKNOWN")
            in_signal = r.get("used_in_current_signal", False)
        else:
            family = "unknown"
            expected_direction = "unknown"
            best_adj_ic = best_adj_ic_hz = best_adj_icir = None
            best_ls_hz = best_ls_spread = best_ls_t = best_win = None
            coverage_min = missing_rate_max = None
            rl_consistency = "N/A"
            review_bucket = "UNKNOWN"
            in_signal = False

        # From inventory
        inv_row = inventory_df[inventory_df["factor_id"] == fid]
        if len(inv_row) > 0:
            inv = inv_row.iloc[0]
            formula_proxy = inv.get("formula_proxy", "")
            req_cols = inv.get("required_columns", "")
            lb_window = inv.get("lookback_window")
        else:
            formula_proxy = ""
            req_cols = ""
            lb_window = None

        # Monthly stability (use best horizon)
        stability = "NO_DATA"
        if best_adj_ic_hz and not period_df.empty:
            stability = compute_monthly_stability(period_df, fid, best_adj_ic_hz)

        # Quantile monotonicity (use best horizon)
        monotonicity = "NO_DATA"
        if best_adj_ic_hz and not quantile_df.empty:
            monotonicity = compute_quantile_monotonicity(quantile_df, fid, best_adj_ic_hz)

        # Redundancy
        red_level = "UNKNOWN"
        nearest = []
        if not redundancy_df.empty:
            sub = redundancy_df[
                (redundancy_df["factor_i"] == fid) | (redundancy_df["factor_j"] == fid)
            ]
            if len(sub) > 0:
                worst = sub.loc[sub["abs_spearman_corr"].idxmax()]
                red_level = worst["redundancy_level"]
                nearest = find_nearest_existing(fid, redundancy_df)

        # Decision bucket
        bucket, action, caveats = determine_decision_bucket(
            review_bucket, rl_consistency, best_adj_ic, best_adj_icir,
            best_ls_t, red_level, monotonicity, stability, in_signal,
        )

        # Data availability
        fv_path = ROOT / "data" / "features" / "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1" / fid / "factor_values.parquet"
        data_avail = "EXISTS" if fv_path.exists() else "MISSING"

        cards.append({
            "factor_id": fid,
            "family": family,
            "expected_direction": expected_direction,
            "formula_proxy": formula_proxy,
            "required_columns": req_cols,
            "lookback_window": lb_window,
            "data_availability": data_avail,
            "coverage": coverage_min,
            "missing_rate": missing_rate_max,
            "best_horizon": best_adj_ic_hz,
            "best_adj_ic": best_adj_ic,
            "best_adj_icir": best_adj_icir,
            "best_long_short_horizon": best_ls_hz,
            "best_long_short_spread": best_ls_spread,
            "best_long_short_t_stat": best_ls_t,
            "ic_win_rate": best_win,
            "monthly_stability_summary": stability,
            "quantile_monotonicity_summary": monotonicity,
            "rankic_longshort_consistency": rl_consistency,
            "redundancy_level": red_level,
            "nearest_existing_factors": "; ".join(nearest) if nearest else "",
            "decision_bucket": bucket,
            "recommended_action": action,
            "caveats": "; ".join(caveats) if caveats else "",
        })

    return pd.DataFrame(cards)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run-dir", required=True,
                        help="Intake run directory")
    parser.add_argument("--factor-ids", nargs="*", default=None,
                        help="Factor IDs (default: all in run)")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    if not run_dir.exists():
        print(f"  ERROR: run directory not found: {run_dir}")
        sys.exit(1)

    print(f"Building conclusion cards")
    print(f"  Run dir: {run_dir}")

    cards_df = build_cards(run_dir, args.factor_ids)

    if cards_df.empty:
        print("  ERROR: no cards generated")
        sys.exit(1)

    # Write CSV
    csv_path = run_dir / "factor_conclusion_cards.csv"
    cards_df.to_csv(csv_path, index=False)

    # Write JSON
    json_path = run_dir / "factor_conclusion_cards.json"
    with open(json_path, "w") as f:
        json.dump(cards_df.to_dict(orient="records"), f, indent=2, default=str)

    print(f"  Generated {len(cards_df)} conclusion cards")
    print(f"  Output: {csv_path}")
    print(f"  Output: {json_path}")

    # Summary
    bucket_counts = cards_df["decision_bucket"].value_counts()
    for bucket, count in bucket_counts.items():
        print(f"    {bucket}: {count}")


if __name__ == "__main__":
    main()
