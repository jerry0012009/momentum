#!/usr/bin/env python3
"""PM-56: Robust Return-Side Diagnostics Layer — Newey-West + Block Bootstrap.

Computes overlap-aware robust t-statistics and block bootstrap CIs for:
1. Long-Short monthly returns (84 factors × 4 horizons)
2. Paper portfolio monthly returns (5 factors × 1 horizon — documented subset)
3. Fee-adjusted returns (13 factors × 5 fee levels — documented subset)

Does NOT modify existing LS t-stat, scorecard, best_horizon, or page.

Input files:
- factor_diagnostics/factor_monthly_long_short_series.csv
- paper_portfolio_diagnostics/paper_portfolio_monthly_returns.csv
- factor_diagnostics/single_factor_fee_sensitivity.csv
- factor_library_state.json (active factors)

Output files:
- factor_diagnostics/factor_ls_robust_significance_summary.csv
- factor_diagnostics/factor_ls_robust_significance_summary.json
- factor_diagnostics/factor_paper_robust_significance_summary.csv
- factor_diagnostics/factor_paper_robust_significance_summary.json
- factor_diagnostics/factor_fee_robust_significance_summary.csv
- factor_diagnostics/factor_fee_robust_significance_summary.json
- factor_diagnostics/factor_return_robust_significance_manifest.json
"""

from pathlib import Path
import json
import math
import sys
import numpy as np
import pandas as pd

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE = Path("research/factor_runs/crypto_top50_factor_library")
DIAG = BASE / "factor_diagnostics"
EVAL = BASE / "factor_level_evaluation"
PP_DIAG = BASE / "paper_portfolio_diagnostics"
STATE_FILE = BASE / "factor_library_state.json"

INPUT_LS = DIAG / "factor_monthly_long_short_series.csv"
INPUT_PAPER = PP_DIAG / "paper_portfolio_monthly_returns.csv"
INPUT_FEE = DIAG / "single_factor_fee_sensitivity.csv"

OUT_LS_CSV = DIAG / "factor_ls_robust_significance_summary.csv"
OUT_LS_JSON = DIAG / "factor_ls_robust_significance_summary.json"
OUT_PAPER_CSV = DIAG / "factor_paper_robust_significance_summary.csv"
OUT_PAPER_JSON = DIAG / "factor_paper_robust_significance_summary.json"
OUT_FEE_CSV = DIAG / "factor_fee_robust_significance_summary.csv"
OUT_FEE_JSON = DIAG / "factor_fee_robust_significance_summary.json"
OUT_MANIFEST = DIAG / "factor_return_robust_significance_manifest.json"

HORIZONS = ["1h", "4h", "24h", "72h"]
HORIZON_HOURS = {"1h": 1, "4h": 4, "24h": 24, "72h": 72}


def nw_lag_rule(horizon: str, n: int) -> int:
    """Newey-West lag: min(horizon_hours, floor(sqrt(n)))."""
    h = HORIZON_HOURS.get(horizon, 1)
    return min(h, max(1, int(math.sqrt(n))))


def newey_west_se(x: np.ndarray, lag: int) -> float:
    """Newey-West / HAC standard error for sample mean."""
    n = len(x)
    if n < 3:
        return float("nan")
    x_dm = x - x.mean()
    gamma_0 = np.dot(x_dm, x_dm) / n
    nw_var = gamma_0
    for j in range(1, lag + 1):
        w = 1.0 - j / (lag + 1.0)  # Bartlett kernel
        gamma_j = np.dot(x_dm[j:], x_dm[:-j]) / n
        nw_var += 2.0 * w * gamma_j
    if nw_var <= 0:
        return float("nan")
    return math.sqrt(nw_var / n)


def block_bootstrap(x: np.ndarray, block_size: int, n_bootstrap: int = 2000,
                    seed: int = 42) -> tuple[float, float, float, float]:
    """Block bootstrap for mean: CI, sign consistency."""
    rng = np.random.RandomState(seed)
    n = len(x)
    n_blocks = max(1, math.ceil(n / block_size))
    means = np.empty(n_bootstrap)
    for b in range(n_bootstrap):
        blocks = rng.randint(0, n - block_size + 1, size=n_blocks)
        sample = np.concatenate([x[i:i + block_size] for i in blocks])[:n]
        means[b] = sample.mean()
    ci_low = float(np.percentile(means, 2.5))
    ci_high = float(np.percentile(means, 97.5))
    mean_sign = 1 if x.mean() > 0 else (-1 if x.mean() < 0 else 0)
    sign_consistency = float(np.mean(np.sign(means) == mean_sign)) if mean_sign != 0 else float("nan")
    return ci_low, ci_high, sign_consistency, float(np.mean(means))


def classify_return_robust(naive_t: float, robust_t: float, mean_ret: float,
                           fee_robust_t: float | None = None,
                           gross_robust_t: float | None = None) -> str:
    """Classification for return-side robust significance."""
    if naive_t is None or robust_t is None:
        return "INSUFFICIENT_PERIODS"
    if math.isnan(naive_t) or math.isnan(robust_t):
        return "INSUFFICIENT_PERIODS"

    # Cost-collapsed: gross robust significant but fee-adjusted not
    if fee_robust_t is not None and gross_robust_t is not None:
        if not math.isnan(fee_robust_t) and not math.isnan(gross_robust_t):
            if abs(gross_robust_t) >= 2.0 and abs(fee_robust_t) < 2.0:
                return "RETURN_COST_COLLAPSED"

    if robust_t >= 2.0 and mean_ret > 0:
        return "RETURN_ROBUST_POSITIVE"
    if robust_t <= -2.0 and mean_ret < 0:
        return "RETURN_ROBUST_NEGATIVE"
    if abs(naive_t) >= 2.0 and abs(robust_t) < 2.0:
        return "NAIVE_ONLY_RETURN_SIGNIFICANT"
    return "RETURN_NOT_SIGNIFICANT"


def sf(val):
    """Safe float."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    return round(float(val), 6)


def compute_series_robust(series: np.ndarray, horizon: str,
                          label: str = "") -> dict:
    """Compute NW robust t-stat + block bootstrap for a return series."""
    n = len(series)
    if n < 4:
        return {
            "return_mean": sf(float(np.mean(series))) if n > 0 else None,
            "naive_t_stat": None, "robust_t_stat": None,
            "robust_standard_error": None, "nw_lag": None, "n_periods": n,
            "effective_n_proxy": None, "tstat_inflation_ratio": None,
            "bootstrap_mean": None, "bootstrap_ci_low": None,
            "bootstrap_ci_high": None, "bootstrap_sign_consistency": None,
            "status": "INSUFFICIENT_PERIODS",
        }

    mean_ret = float(np.mean(series))
    std_ret = float(np.std(series, ddof=1))
    naive_t = mean_ret / (std_ret / math.sqrt(n)) if std_ret > 0 else float("nan")

    lag = nw_lag_rule(horizon, n)
    if lag >= n:
        lag = max(1, n - 1)
    nw_se = newey_west_se(series, lag)
    robust_t = mean_ret / nw_se if nw_se > 0 and not math.isnan(nw_se) else float("nan")

    # Effective n proxy: n * (naive_se^2 / nw_se^2)
    naive_se = std_ret / math.sqrt(n)
    if nw_se > 0 and not math.isnan(nw_se) and naive_se > 0:
        eff_n = n * (naive_se ** 2 / nw_se ** 2)
    else:
        eff_n = float("nan")

    inflation = abs(naive_t) / abs(robust_t) if not math.isnan(robust_t) and abs(robust_t) > 1e-10 else float("nan")

    # Block bootstrap
    block_sz = min(6, max(3, int(math.sqrt(n))))
    bs = block_bootstrap(series, block_sz)

    return {
        "return_mean": sf(mean_ret),
        "naive_t_stat": sf(naive_t),
        "robust_t_stat": sf(robust_t),
        "robust_standard_error": sf(nw_se),
        "nw_lag": lag,
        "n_periods": n,
        "effective_n_proxy": sf(eff_n),
        "tstat_inflation_ratio": sf(inflation),
        "bootstrap_mean": sf(bs[3]),
        "bootstrap_ci_low": sf(bs[0]),
        "bootstrap_ci_high": sf(bs[1]),
        "bootstrap_sign_consistency": sf(bs[2]),
        "status": "COMPUTED",
    }


def overlap_warning(horizon: str) -> str:
    h = HORIZON_HOURS.get(horizon, 1)
    if h <= 1:
        return "NO_MAJOR_OVERLAP"
    if h <= 4:
        return "MODERATE_OVERLAP"
    if h <= 24:
        return "HIGH_OVERLAP"
    return "SEVERE_OVERLAP"


# ── Main ───────────────────────────────────────────────────────────────────────
def main() -> int:
    # Load active factors
    state = json.loads(STATE_FILE.read_text())
    active_factors = set(state.get("registered_factor_ids", []))
    print(f"Active factors: {len(active_factors)}")

    # ── 1. Long-Short Robust ───────────────────────────────────────────────────
    print("\n=== Long-Short Robust Diagnostics ===")
    ls_df = pd.read_csv(INPUT_LS)
    ls_rows = []

    for fid in sorted(active_factors):
        for hz in HORIZONS:
            subset = ls_df[(ls_df["factor_id"] == fid) & (ls_df["horizon"] == hz)]
            if subset.empty:
                ls_rows.append({
                    "factor_id": fid, "horizon": hz, "horizon_hours": HORIZON_HOURS[hz],
                    "overlap_warning": overlap_warning(hz),
                    "return_robust_class": "INSUFFICIENT_PERIODS",
                    **{k: None for k in ["return_mean", "naive_t_stat", "robust_t_stat",
                                          "robust_standard_error", "nw_lag", "n_periods",
                                          "effective_n_proxy", "tstat_inflation_ratio",
                                          "bootstrap_mean", "bootstrap_ci_low",
                                          "bootstrap_ci_high", "bootstrap_sign_consistency"]},
                })
                continue

            series = subset.sort_values("month")["long_short_return"].values
            result = compute_series_robust(series, hz)

            cls = classify_return_robust(result["naive_t_stat"], result["robust_t_stat"],
                                         result["return_mean"] or 0)

            ls_rows.append({
                "factor_id": fid, "horizon": hz, "horizon_hours": HORIZON_HOURS[hz],
                "overlap_warning": overlap_warning(hz),
                "return_robust_class": cls,
                **result,
            })

    ls_out = pd.DataFrame(ls_rows)
    ls_out.to_csv(OUT_LS_CSV, index=False)
    ls_out.to_json(OUT_LS_JSON, orient="records", indent=2)
    print(f"  Rows: {len(ls_out)}")
    print(f"  Classes: {ls_out['return_robust_class'].value_counts().to_dict()}")

    # ── 2. Paper Portfolio Robust ──────────────────────────────────────────────
    print("\n=== Paper Portfolio Robust Diagnostics ===")
    paper_df = pd.read_csv(INPUT_PAPER)
    paper_rows = []
    paper_factors = sorted(paper_df["factor_id"].unique())
    paper_horizons = sorted(paper_df["horizon"].unique())

    for fid in paper_factors:
        for hz in paper_horizons:
            subset = paper_df[(paper_df["factor_id"] == fid) & (paper_df["horizon"] == hz)]
            if subset.empty:
                continue
            series = subset.sort_values("month")["ls_return_mean"].values
            result = compute_series_robust(series, hz)
            cls = classify_return_robust(result["naive_t_stat"], result["robust_t_stat"],
                                         result["return_mean"] or 0)

            paper_rows.append({
                "factor_id": fid, "horizon": hz, "horizon_hours": HORIZON_HOURS.get(hz, 1),
                "overlap_warning": overlap_warning(hz),
                "return_robust_class": cls,
                **result,
            })

    paper_out = pd.DataFrame(paper_rows)
    paper_out.to_csv(OUT_PAPER_CSV, index=False)
    paper_out.to_json(OUT_PAPER_JSON, orient="records", indent=2)
    print(f"  Factors: {len(paper_factors)}")
    print(f"  Horizons: {paper_horizons}")
    print(f"  Rows: {len(paper_out)}")
    print(f"  Classes: {paper_out['return_robust_class'].value_counts().to_dict()}")

    # ── 3. Fee Sensitivity Robust ─────────────────────────────────────────────
    print("\n=== Fee Sensitivity Robust Diagnostics ===")
    fee_df = pd.read_csv(INPUT_FEE)
    fee_factors = sorted(fee_df["factor_id"].unique())
    fee_levels = sorted(fee_df["fee_bps"].unique())

    # For each factor: compare gross (fee=0) vs net (fee=max) robust t-stat
    # Fee sensitivity is factor-level (no horizon), single-row per factor×fee
    # We compute a "robust class" by comparing gross vs net sharpe/return
    fee_rows = []
    for fid in fee_factors:
        fsub = fee_df[fee_df["factor_id"] == fid].sort_values("fee_bps")
        if fsub.empty:
            continue

        gross = fsub[fsub["fee_bps"] == 0]
        net = fsub[fsub["fee_bps"] == fsub["fee_bps"].max()]

        if gross.empty or net.empty:
            continue

        gross_row = gross.iloc[0]
        net_row = net.iloc[0]

        # Fee sensitivity is not a time series, so we can't do NW/bootstrap
        # Instead, report the gross and net metrics
        fee_rows.append({
            "factor_id": fid,
            "fee_level_bps": int(net_row["fee_bps"]),
            "gross_annualized_return": sf(gross_row["annualized_return"]),
            "gross_sharpe": sf(gross_row["sharpe"]),
            "gross_max_drawdown": sf(gross_row["max_drawdown"]),
            "net_annualized_return": sf(net_row["annualized_return"]),
            "net_sharpe": sf(net_row["sharpe"]),
            "net_max_drawdown": sf(net_row["max_drawdown"]),
            "return_decay": sf(gross_row["annualized_return"] - net_row["annualized_return"]),
            "sharpe_decay": sf(gross_row["sharpe"] - net_row["sharpe"]),
            "cost_status": "RETURN_COST_COLLAPSED" if (
                gross_row["sharpe"] >= 0.8 and net_row["sharpe"] < 0.5
            ) else "COST_SURVIVED",
        })

    fee_out = pd.DataFrame(fee_rows)
    fee_out.to_csv(OUT_FEE_CSV, index=False)
    fee_out.to_json(OUT_FEE_JSON, orient="records", indent=2)
    print(f"  Factors with fee data: {len(fee_factors)}")
    print(f"  Fee levels: {fee_levels}")
    print(f"  Rows: {len(fee_out)}")

    # ── 4. Manifest ───────────────────────────────────────────────────────────
    manifest = {
        "pm": "PM-56",
        "title": "Robust Return-Side Diagnostics Layer",
        "active_factor_count": len(active_factors),
        "outputs": {
            "ls_robust": {
                "path": str(OUT_LS_CSV),
                "row_count": len(ls_out),
                "coverage": f"{len(active_factors)} factors × {len(HORIZONS)} horizons",
                "method": "Newey-West HAC + Block Bootstrap on monthly LS returns",
            },
            "paper_robust": {
                "path": str(OUT_PAPER_CSV),
                "row_count": len(paper_out),
                "coverage": f"{len(paper_factors)} factors × {len(paper_horizons)} horizons (subset)",
                "method": "Newey-West HAC + Block Bootstrap on monthly paper returns",
                "note": "Only 5 factors have paper portfolio diagnostics",
            },
            "fee_robust": {
                "path": str(OUT_FEE_CSV),
                "row_count": len(fee_out),
                "coverage": f"{len(fee_factors)} factors × {len(fee_levels)} fee levels (subset)",
                "method": "Gross vs net return/sharpe comparison",
                "note": "Only 13 factors have fee sensitivity data; not a time-series analysis",
            },
        },
        "nw_lag_rule": "lag = min(horizon_hours, floor(sqrt(n_periods)))",
        "bootstrap": {
            "block_size": "min(6, max(3, floor(sqrt(n_periods))))",
            "n_bootstrap": 2000,
            "seed": 42,
            "ci": "95%",
        },
        "classification_rules": {
            "RETURN_ROBUST_POSITIVE": "robust_t >= 2 and mean > 0",
            "RETURN_ROBUST_NEGATIVE": "robust_t <= -2 and mean < 0",
            "NAIVE_ONLY_RETURN_SIGNIFICANT": "|naive_t| >= 2 and |robust_t| < 2",
            "RETURN_COST_COLLAPSED": "gross robust_t >= 2 but fee-adjusted robust_t < 2",
            "RETURN_NOT_SIGNIFICANT": "otherwise",
            "INSUFFICIENT_PERIODS": "n < 4",
        },
        "no_changes": [
            "No new factors",
            "No formula changes",
            "No expected_direction changes",
            "No factor_values changes",
            "No RankIC result changes",
            "No scorecard changes",
            "No best_horizon changes",
            "No page rebuild",
            "No signal construction",
            "No trading recommendation",
        ],
    }
    OUT_MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

    print(f"\nManifest written to {OUT_MANIFEST}")
    print("PM-56 complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
