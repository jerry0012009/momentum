#!/usr/bin/env python3
"""PM-54: RankIC Robust Significance Layer — Newey-West / HAC robust t-stat.

Reads monthly period IC series from factor_level_period_ic_summary.csv and
computes overlap-aware robust significance using Newey-West standard errors.

Does NOT modify any existing fields (rankic_t_stat, scorecard, best_horizon).
Outputs NEW diagnostic files only.
"""

import csv
import json
import math
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

BASE = Path("research/factor_runs/crypto_top50_factor_library")
EVAL_DIR = BASE / "factor_level_evaluation"
DIAG_DIR = BASE / "factor_diagnostics"
STATE_PATH = BASE / "factor_library_state.json"

INPUT_CSV = EVAL_DIR / "factor_level_period_ic_summary.csv"
RANKIC_CSV = EVAL_DIR / "factor_level_rankic_summary.csv"

OUTPUT_CSV = DIAG_DIR / "factor_rankic_robust_significance_summary.csv"
OUTPUT_JSON = DIAG_DIR / "factor_rankic_robust_significance_summary.json"
OUTPUT_MANIFEST = DIAG_DIR / "factor_rankic_robust_significance_manifest.json"

HORIZONS = ["1h", "4h", "24h", "72h"]
HORIZON_HOURS = {"1h": 1, "4h": 4, "24h": 24, "72h": 72}

# Overlap warning classification
OVERLAP_CLASS = {
    1: "NO_MAJOR_OVERLAP",
    4: "MODERATE_OVERLAP",
    24: "HIGH_OVERLAP",
    72: "SEVERE_OVERLAP",
}

# Minimum periods required for robust inference
MIN_PERIODS = 8


def load_active_factors() -> set[str]:
    """Load active factor IDs from state JSON."""
    state = json.loads(STATE_PATH.read_text())
    return set(state.get("registered_factor_ids", []))


def load_existing_tstats() -> dict[tuple[str, str], dict]:
    """Load existing naive t-stat from rankic summary."""
    result = {}
    with open(RANKIC_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["factor_name"], row["horizon"])
            t_val = row.get("t_stat", "")
            n_val = row.get("n_periods", "")
            result[key] = {
                "naive_t_stat": float(t_val) if t_val else None,
                "naive_n_periods": int(n_val) if n_val else None,
            }
    return result


def load_period_ic_series() -> dict[tuple[str, str], list[dict]]:
    """Load monthly IC series grouped by (factor_name, horizon)."""
    series = defaultdict(list)
    with open(INPUT_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["factor_name"], row["horizon"])
            ic_val = row.get("raw_mean_rank_ic", "")
            n_val = row.get("n_periods", "")
            if ic_val and n_val:
                series[key].append({
                    "period": row["period"],
                    "ic": float(ic_val),
                    "n_periods": int(n_val),
                })
    # Sort by period
    for key in series:
        series[key].sort(key=lambda r: r["period"])
    return dict(series)


def compute_nw_lag(horizon_hours: int, n_periods: int) -> int:
    """Newey-West lag rule: min(horizon_hours, floor(sqrt(n_periods)))."""
    return min(horizon_hours, int(math.floor(math.sqrt(n_periods))))


def newey_west_se(ic_series: np.ndarray, lag: int) -> float:
    """Compute Newey-West / HAC standard error for the mean of a time series.

    Parameters
    ----------
    ic_series : 1D array of IC values (one per period)
    lag : NW lag parameter (number of autocovariance lags to include)

    Returns
    -------
    Robust standard error of the mean.

    Reference:
        Newey & West (1987), "A Simple, Positive Semi-Definite,
        Heteroskedasticity and Autocovariance Consistent Covariance Matrix"
    """
    n = len(ic_series)
    if n < 2:
        return float("nan")

    mean = np.mean(ic_series)
    resid = ic_series - mean

    # Gamma_0: variance term
    gamma_0 = np.sum(resid ** 2) / n

    # Weighted sum of autocovariances
    # Bartlett kernel: w_j = 1 - j/(lag+1)
    nw_sum = gamma_0
    for j in range(1, lag + 1):
        gamma_j = np.sum(resid[j:] * resid[:-j]) / n
        weight = 1.0 - j / (lag + 1.0)
        nw_sum += 2.0 * weight * gamma_j

    # Standard error of the mean
    se = math.sqrt(nw_sum / n)
    return se


def classify_joint(naive_t: float | None, robust_t: float | None, mean_ic: float) -> tuple[str, str]:
    """Classify significance for both naive and robust t-stats.

    Returns (significance_class_naive, significance_class_robust).

    Rules:
    - robust_t >= 2 and mean > 0 → ROBUST_SIGNIFICANT_POSITIVE
    - robust_t <= -2 and mean < 0 → ROBUST_SIGNIFICANT_NEGATIVE
    - abs(naive_t) >= 2 but abs(robust_t) < 2 → NAIVE_ONLY_SIGNIFICANT
    - abs(robust_t) < 2 and abs(naive_t) < 2 → NOT_SIGNIFICANT
    """
    # Naive class
    if naive_t is None or math.isnan(naive_t):
        sig_naive = "INSUFFICIENT_PERIODS"
    elif abs(naive_t) >= 2.0:
        sig_naive = "ROBUST_SIGNIFICANT_POSITIVE" if mean_ic > 0 else "ROBUST_SIGNIFICANT_NEGATIVE"
    else:
        sig_naive = "NOT_SIGNIFICANT"

    # Robust class (uses both naive and robust to detect disagreement)
    if robust_t is None or math.isnan(robust_t):
        sig_robust = "INSUFFICIENT_PERIODS"
    elif abs(robust_t) >= 2.0:
        sig_robust = "ROBUST_SIGNIFICANT_POSITIVE" if mean_ic > 0 else "ROBUST_SIGNIFICANT_NEGATIVE"
    elif naive_t is not None and not math.isnan(naive_t) and abs(naive_t) >= 2.0:
        sig_robust = "NAIVE_ONLY_SIGNIFICANT"
    else:
        sig_robust = "NOT_SIGNIFICANT"

    return sig_naive, sig_robust


def main():
    print("=" * 70)
    print("PM-54: RankIC Robust Significance Layer — Newey-West / HAC")
    print("=" * 70)

    # Load data
    active_factors = load_active_factors()
    existing_tstats = load_existing_tstats()
    period_series = load_period_ic_series()

    print(f"\n  Active factors: {len(active_factors)}")
    print(f"  Horizons: {HORIZONS}")
    print(f"  Expected rows: {len(active_factors) * len(HORIZONS)}")

    # Verify coverage
    missing_pairs = []
    for fid in sorted(active_factors):
        for h in HORIZONS:
            if (fid, h) not in period_series or len(period_series[(fid, h)]) == 0:
                missing_pairs.append((fid, h))

    if missing_pairs:
        print(f"\n  ✗ MISSING {len(missing_pairs)} factor × horizon pairs:")
        for fid, h in missing_pairs[:10]:
            print(f"    {fid} × {h}")
        sys.exit(1)

    print(f"  ✓ All {len(active_factors) * len(HORIZONS)} factor × horizon pairs present")

    # Compute robust significance
    rows = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for fid in sorted(active_factors):
        for h in HORIZONS:
            key = (fid, h)
            series_data = period_series[key]
            ic_values = np.array([d["ic"] for d in series_data])
            n_months = len(ic_values)
            horizon_hours = HORIZON_HOURS[h]

            # Existing naive t-stat (timestamp-level)
            existing = existing_tstats.get(key, {})
            naive_t_stat = existing.get("naive_t_stat")
            naive_n_periods = existing.get("naive_n_periods")

            # Monthly-level statistics
            rankic_mean = float(np.mean(ic_values))
            rankic_std = float(np.std(ic_values, ddof=1)) if n_months > 1 else float("nan")

            # Monthly naive t-stat
            monthly_naive_t = rankic_mean / (rankic_std / math.sqrt(n_months)) if n_months > 1 and rankic_std > 0 else float("nan")

            # NW lag
            nw_lag = compute_nw_lag(horizon_hours, n_months)

            # Robust SE and t-stat
            if n_months < MIN_PERIODS:
                robust_se = float("nan")
                robust_t = float("nan")
                robust_p = float("nan")
                effective_n = float("nan")
                overlap_warning = "INSUFFICIENT_PERIODS"
            else:
                robust_se = newey_west_se(ic_values, nw_lag)
                if robust_se > 0:
                    robust_t = rankic_mean / robust_se
                    # Two-tailed p-value using normal approximation (adequate for n >= 8)
                    # Using scipy-free approximation
                    robust_p = 2.0 * (1.0 - _norm_cdf(abs(robust_t)))
                else:
                    robust_t = float("nan")
                    robust_p = float("nan")

                # Effective n proxy: n / (1 + 2 * sum of autocorrelations up to lag)
                effective_n = _effective_n(ic_values, nw_lag)
                overlap_warning = OVERLAP_CLASS.get(horizon_hours, "UNKNOWN")

            # Overlap ratio: horizon_hours / 720 (approx monthly sampling interval in hours)
            overlap_ratio = horizon_hours / 720.0

            # T-stat inflation ratio
            if naive_t_stat is not None and robust_t is not None and not math.isnan(robust_t) and robust_t != 0:
                tstat_inflation = abs(naive_t_stat) / abs(robust_t)
            else:
                tstat_inflation = float("nan")

            # Significance classes (joint classification)
            sig_naive, sig_robust = classify_joint(naive_t_stat, robust_t, rankic_mean)

            # Override for insufficient periods
            if n_months < MIN_PERIODS:
                sig_robust = "INSUFFICIENT_PERIODS"

            row = {
                "factor_id": fid,
                "horizon": h,
                "horizon_hours": horizon_hours,
                "n_months": n_months,
                "rankic_mean": round(rankic_mean, 8),
                "rankic_std": round(rankic_std, 8) if not math.isnan(rankic_std) else None,
                "naive_t_stat": round(naive_t_stat, 4) if naive_t_stat is not None else None,
                "naive_n_periods": naive_n_periods,
                "monthly_naive_t_stat": round(monthly_naive_t, 4) if not math.isnan(monthly_naive_t) else None,
                "robust_standard_error": round(robust_se, 8) if not math.isnan(robust_se) else None,
                "robust_t_stat": round(robust_t, 4) if not math.isnan(robust_t) else None,
                "robust_p_value": round(robust_p, 6) if not math.isnan(robust_p) else None,
                "effective_n_proxy": round(effective_n, 2) if not math.isnan(effective_n) else None,
                "nw_lag": nw_lag,
                "overlap_ratio": round(overlap_ratio, 4),
                "tstat_inflation_ratio": round(tstat_inflation, 4) if not math.isnan(tstat_inflation) else None,
                "significance_class_naive": sig_naive,
                "significance_class_robust": sig_robust,
                "overlap_warning": overlap_warning,
            }
            rows.append(row)

    # Verify row count
    expected = len(active_factors) * len(HORIZONS)
    print(f"\n  Output rows: {len(rows)} (expected {expected})")
    if len(rows) != expected:
        print(f"  ✗ ROW COUNT MISMATCH")
        sys.exit(1)

    # Write CSV
    fieldnames = [
        "factor_id", "horizon", "horizon_hours", "n_months",
        "rankic_mean", "rankic_std",
        "naive_t_stat", "naive_n_periods", "monthly_naive_t_stat",
        "robust_standard_error", "robust_t_stat", "robust_p_value",
        "effective_n_proxy", "nw_lag", "overlap_ratio",
        "tstat_inflation_ratio",
        "significance_class_naive", "significance_class_robust",
        "overlap_warning",
    ]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  ✓ CSV: {OUTPUT_CSV}")

    # Write JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, default=str)
    print(f"  ✓ JSON: {OUTPUT_JSON}")

    # Write manifest
    manifest = {
        "pm": "PM-54",
        "title": "RankIC Robust Significance Layer — Newey-West / HAC",
        "created_utc": now,
        "input_file": str(INPUT_CSV),
        "input_rows": sum(len(v) for v in period_series.values()),
        "output_rows": len(rows),
        "active_factors": len(active_factors),
        "horizons": HORIZONS,
        "nw_lag_rule": "lag = min(horizon_hours, floor(sqrt(n_months)))",
        "min_periods_for_robust": MIN_PERIODS,
        "overlap_classification": OVERLAP_CLASS,
        "significance_classes": [
            "ROBUST_SIGNIFICANT_POSITIVE",
            "ROBUST_SIGNIFICANT_NEGATIVE",
            "NAIVE_ONLY_SIGNIFICANT",
            "NOT_SIGNIFICANT",
            "INSUFFICIENT_PERIODS",
        ],
        "fields_preserved": [
            "rankic_t_stat (existing naive t-stat unchanged)",
            "scorecard (unchanged)",
            "best_horizon (unchanged)",
            "expected_direction (unchanged)",
            "factor_values (unchanged)",
        ],
        "no_signal_construction": True,
        "no_trading_recommendation": True,
    }
    with open(OUTPUT_MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"  ✓ Manifest: {OUTPUT_MANIFEST}")

    # Summary statistics
    _print_summary(rows)

    print(f"\n  Verdict: PM54_RANKIC_ROBUST_SIGNIFICANCE_PASS")
    return 0


def _print_summary(rows: list[dict]):
    """Print summary statistics."""
    print(f"\n{'='*70}")
    print("Summary Statistics")
    print(f"{'='*70}")

    # By horizon
    for h in HORIZONS:
        h_rows = [r for r in rows if r["horizon"] == h]
        robust_sig = sum(1 for r in h_rows if "ROBUST_SIGNIFICANT" in (r["significance_class_robust"] or ""))
        naive_only = sum(1 for r in h_rows if r["significance_class_robust"] == "NAIVE_ONLY_SIGNIFICANT")
        not_sig = sum(1 for r in h_rows if r["significance_class_robust"] == "NOT_SIGNIFICANT")
        inflations = [r["tstat_inflation_ratio"] for r in h_rows if r["tstat_inflation_ratio"] is not None and not math.isnan(r["tstat_inflation_ratio"])]
        avg_inflation = np.mean(inflations) if inflations else 0
        print(f"\n  {h}: {len(h_rows)} factors")
        print(f"    Robust significant: {robust_sig}")
        print(f"    Naive-only significant: {naive_only}")
        print(f"    Not significant: {not_sig}")
        print(f"    Avg t-stat inflation: {avg_inflation:.2f}x")

    # Top disagreements
    disagreements = [r for r in rows if r["significance_class_robust"] == "NAIVE_ONLY_SIGNIFICANT"]
    if disagreements:
        print(f"\n  Top naive-only significant (robust disagrees): {len(disagreements)} total")
        disagreements.sort(key=lambda r: abs(r.get("tstat_inflation_ratio") or 0), reverse=True)
        for r in disagreements[:10]:
            print(f"    {r['factor_id']:40s} {r['horizon']:3s}  naive={r['naive_t_stat']:+.2f}  robust={r['robust_t_stat']:+.2f}  inflation={r['tstat_inflation_ratio']:.2f}x")

    # Top inflation ratios (24h and 72h)
    print(f"\n  Top t-stat inflation (24h/72h):")
    high_overlap = [r for r in rows if r["horizon"] in ("24h", "72h") and r["tstat_inflation_ratio"] is not None and not math.isnan(r["tstat_inflation_ratio"])]
    high_overlap.sort(key=lambda r: r["tstat_inflation_ratio"], reverse=True)
    for r in high_overlap[:10]:
        print(f"    {r['factor_id']:40s} {r['horizon']:3s}  naive={r['naive_t_stat']:+.2f}  robust={r['robust_t_stat']:+.2f}  inflation={r['tstat_inflation_ratio']:.2f}x")

    # Example factors
    examples = ["clv_20h", "rev_2h", "a101_volume_cap_alpha_min_80_80", "a101_volume_cap_alpha_min_56_84"]
    print(f"\n  Example factors:")
    for ex in examples:
        ex_rows = [r for r in rows if r["factor_id"] == ex]
        if ex_rows:
            for r in ex_rows:
                print(f"    {r['factor_id']:40s} {r['horizon']:3s}  mean={r['rankic_mean']:+.6f}  naive_t={r['naive_t_stat']:+.2f}  robust_t={r['robust_t_stat']:+.2f}  sig_naive={r['significance_class_naive']:30s}  sig_robust={r['significance_class_robust']:30s}  nw_lag={r['nw_lag']}  overlap={r['overlap_warning']}")


def _norm_cdf(x: float) -> float:
    """Approximate standard normal CDF using error function."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _effective_n(ic_series: np.ndarray, lag: int) -> float:
    """Estimate effective sample size: n / (1 + 2 * sum of autocorrelations)."""
    n = len(ic_series)
    if n < 3:
        return float(n)

    mean = np.mean(ic_series)
    resid = ic_series - mean
    var = np.sum(resid ** 2) / n
    if var == 0:
        return float(n)

    autocorr_sum = 0.0
    for j in range(1, min(lag + 1, n)):
        gamma_j = np.sum(resid[j:] * resid[:-j]) / n
        autocorr_sum += gamma_j / var

    denom = 1.0 + 2.0 * autocorr_sum
    if denom <= 0:
        return float(n)
    return n / denom


if __name__ == "__main__":
    sys.exit(main())
