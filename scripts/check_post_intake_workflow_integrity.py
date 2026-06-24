#!/usr/bin/env python3
"""Post-Intake Workflow Integrity Checker — PM-43A.

Checks that all required post-intake workflow outputs exist and are consistent
for specified factors. Reports missing/stale/incomplete data.

Usage:
    python scripts/check_post_intake_workflow_integrity.py --factor-ids rev_2h,mom_vol_adjusted_20h
    python scripts/check_post_intake_workflow_integrity.py --all

Outputs:
    research/factor_runs/crypto_top50_factor_library/factor_diagnostics/post_intake_workflow_integrity_report.csv
    research/factor_runs/crypto_top50_factor_library/factor_diagnostics/post_intake_workflow_integrity_report.json

NOT production. Research diagnostics only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"
DIAG_DIR = BASE / "factor_diagnostics"
EVAL_DIR = BASE / "factor_level_evaluation"
META_DIR = BASE / "factor_metadata"
STATE_PATH = BASE / "factor_library_state.json"

# ── Check definitions ──────────────────────────────────────────────────────

def check_factor_level_rankic(fid: str) -> dict:
    """Check if factor has RankIC in canonical evaluation."""
    try:
        df = pd.read_csv(EVAL_DIR / "factor_level_rankic_summary.csv")
        rows = df[df["factor_name"] == fid]
        if rows.empty:
            return {"status": "MISSING", "detail": "Not in factor_level_rankic_summary.csv"}
        return {"status": "OK", "detail": f"{len(rows)} horizon(s)"}
    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}


def check_period_ic(fid: str) -> dict:
    """Check if factor has period IC data."""
    try:
        df = pd.read_csv(EVAL_DIR / "factor_level_period_ic_summary.csv")
        rows = df[df["factor_name"] == fid]
        if rows.empty:
            return {"status": "MISSING", "detail": "Not in factor_level_period_ic_summary.csv"}
        return {"status": "OK", "detail": f"{len(rows)} rows"}
    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}


def check_period_ls(fid: str) -> dict:
    """Check if factor has period LS data."""
    try:
        df = pd.read_csv(EVAL_DIR / "factor_level_period_long_short_summary.csv")
        rows = df[df["factor_name"] == fid]
        if rows.empty:
            return {"status": "MISSING", "detail": "Not in factor_level_period_long_short_summary.csv"}
        return {"status": "OK", "detail": f"{len(rows)} rows"}
    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}


def check_ls_aggregate(fid: str) -> dict:
    """Check if factor has LS aggregate metrics (PM-41).

    Two sources (same fallback as _build_factor_eval_html.py):
      1. factor_diagnostics_summary.csv — primary, has long_short_sharpe / long_short_max_drawdown
      2. factor_level_long_short_summary.csv — canonical, has long_short_spread_std / long_short_spread_annualized_return
    Report MISSING only if BOTH sources have NaN for the factor.
    """
    try:
        # Source 1: diagnostics summary (primary — same as page builder drow)
        diag_path = DIAG_DIR / "factor_diagnostics_summary.csv"
        if diag_path.exists():
            diag = pd.read_csv(diag_path)
            diag_row = diag[diag["factor_id"] == fid]
            if not diag_row.empty:
                s = diag_row.iloc[0]
                if pd.notna(s.get("long_short_sharpe")) or pd.notna(s.get("long_short_max_drawdown")):
                    return {"status": "OK", "detail": f"diagnostics summary: sharpe={s.get('long_short_sharpe')}, max_dd={s.get('long_short_max_drawdown')}"}

        # Source 2: canonical LS summary (fallback — same as page builder feval_ls_map)
        df = pd.read_csv(EVAL_DIR / "factor_level_long_short_summary.csv")
        rows = df[df["factor_name"] == fid]
        if not rows.empty:
            sample = rows.iloc[0]
            has_std = pd.notna(sample.get("long_short_spread_std"))
            has_ann = pd.notna(sample.get("long_short_spread_annualized_return"))
            if has_std or has_ann:
                return {"status": "OK", "detail": f"{len(rows)} horizon(s), canonical aggregate present"}

        return {"status": "MISSING", "detail": "LS aggregate fields are NaN in both diagnostics and canonical sources"}
    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}


def check_paper_payload(fid: str) -> dict:
    """Check if factor has paper page payload."""
    try:
        payload_path = DIAG_DIR / "single_factor_paper_page_payload.json"
        if not payload_path.exists():
            return {"status": "MISSING", "detail": "Payload file not found"}
        payload = json.loads(payload_path.read_text())
        factors = payload.get("factors", [])
        if isinstance(factors, list):
            fids_in_payload = {f["factor_id"] for f in factors if "factor_id" in f}
        elif isinstance(factors, dict):
            fids_in_payload = set(factors.keys())
        else:
            return {"status": "ERROR", "detail": "Unknown payload format"}
        if fid not in fids_in_payload:
            return {"status": "MISSING", "detail": "Not in payload"}
        return {"status": "OK", "detail": "Present in payload"}
    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}


def check_regime_btc(fid: str) -> dict:
    """Check if factor has regime/BTC diagnostics."""
    try:
        df = pd.read_csv(DIAG_DIR / "factor_regime_exposure_summary.csv")
        rows = df[df["factor_id"] == fid]
        if rows.empty:
            return {"status": "MISSING", "detail": "Not in factor_regime_exposure_summary.csv"}
        row = rows.iloc[0]
        regime = row.get("regime_dependency_class", "")
        if regime == "INSUFFICIENT_REGIME_DATA":
            return {"status": "WARNING", "detail": "INSUFFICIENT_REGIME_DATA"}
        return {"status": "OK", "detail": f"regime={regime}"}
    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}


def check_pairwise_redundancy(fid: str) -> dict:
    """Check if factor has pairwise redundancy data."""
    try:
        df = pd.read_csv(DIAG_DIR / "factor_pairwise_redundancy.csv")
        has_fid = fid in set(df["factor_i"].unique()) | set(df["factor_j"].unique())
        if not has_fid:
            return {"status": "MISSING", "detail": "Not in pairwise redundancy matrix"}
        pairs = df[(df["factor_i"] == fid) | (df["factor_j"] == fid)]
        return {"status": "OK", "detail": f"{len(pairs)} pairs"}
    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}


def check_cluster(fid: str) -> dict:
    """Check if factor has cluster assignment."""
    try:
        df = pd.read_csv(DIAG_DIR / "factor_redundancy_clusters.csv")
        rows = df[df["factor_id"] == fid]
        if rows.empty:
            return {"status": "MISSING", "detail": "Not in factor_redundancy_clusters.csv"}
        row = rows.iloc[0]
        cluster_id = row.get("cluster_id", "")
        return {"status": "OK", "detail": f"cluster={cluster_id}"}
    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}


def check_marginal_info(fid: str) -> dict:
    """Check if factor has marginal information."""
    try:
        df = pd.read_csv(DIAG_DIR / "factor_redundancy_summary.csv")
        rows = df[df["factor_id"] == fid]
        if rows.empty:
            return {"status": "MISSING", "detail": "Not in factor_redundancy_summary.csv"}
        row = rows.iloc[0]
        novelty = row.get("novelty_assessment", "")
        return {"status": "OK", "detail": f"novelty={novelty}"}
    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}


def check_scorecard_not_stale(fid: str) -> dict:
    """Check if scorecard has non-stale values."""
    try:
        df = pd.read_csv(DIAG_DIR / "factor_quality_scorecard.csv")
        rows = df[df["factor_id"] == fid]
        if rows.empty:
            return {"status": "MISSING", "detail": "Not in scorecard"}
        row = rows.iloc[0]
        rankic = float(row.get("rankic_mean", 0) or 0)
        coverage = float(row.get("coverage_rate", 0) or 0)
        if rankic == 0 and coverage == 0:
            return {"status": "STALE", "detail": "rankic_mean=0 and coverage_rate=0 — scorecard computed from stale data"}
        return {"status": "OK", "detail": f"rankic={rankic:.6f}, coverage={coverage:.4f}"}
    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}


def check_quantile_shape(fid: str) -> dict:
    """Check if factor has quantile shape diagnostics."""
    try:
        df = pd.read_csv(DIAG_DIR / "factor_quantile_shape_summary.csv")
        rows = df[df["factor_id"] == fid]
        if rows.empty:
            return {"status": "MISSING", "detail": "Not in factor_quantile_shape_summary.csv"}
        row = rows.iloc[0]
        shape = row.get("quantile_shape_class", "")
        return {"status": "OK", "detail": f"shape={shape}"}
    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}


def check_rolling_stability(fid: str) -> dict:
    """Check if factor has rolling stability diagnostics."""
    try:
        df = pd.read_csv(DIAG_DIR / "factor_rolling_stability_summary.csv")
        rows = df[df["factor_id"] == fid]
        if rows.empty:
            return {"status": "MISSING", "detail": "Not in factor_rolling_stability_summary.csv"}
        row = rows.iloc[0]
        stability = row.get("rolling_stability_class", "")
        if stability == "INSUFFICIENT_HISTORY":
            return {"status": "WARNING", "detail": "INSUFFICIENT_HISTORY"}
        return {"status": "OK", "detail": f"stability={stability}"}
    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}


def check_decile_shape(fid: str) -> dict:
    """Check if factor has decile shape diagnostics."""
    try:
        df = pd.read_csv(DIAG_DIR / "factor_decile_shape_summary.csv")
        rows = df[df["factor_id"] == fid]
        if rows.empty:
            return {"status": "MISSING", "detail": "Not in factor_decile_shape_summary.csv"}
        row = rows.iloc[0]
        shape = row.get("decile_shape_class", "")
        return {"status": "OK", "detail": f"shape={shape}"}
    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}


def check_capacity_liquidity(fid: str) -> dict:
    """Check if factor has capacity/liquidity diagnostics."""
    try:
        df = pd.read_csv(DIAG_DIR / "factor_capacity_liquidity_summary.csv")
        rows = df[df["factor_id"] == fid]
        if rows.empty:
            return {"status": "MISSING", "detail": "Not in factor_capacity_liquidity_summary.csv"}
        row = rows.iloc[0]
        cls = row.get("capacity_class", "")
        return {"status": "OK", "detail": f"class={cls}"}
    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}


def check_cumulative_ls(fid: str) -> dict:
    """Check if factor has cumulative LS curve data."""
    try:
        df = pd.read_csv(DIAG_DIR / "factor_cumulative_long_short_curve.csv")
        rows = df[df["factor_id"] == fid]
        if rows.empty:
            return {"status": "MISSING", "detail": "Not in factor_cumulative_long_short_curve.csv"}
        return {"status": "OK", "detail": f"{len(rows)} rows"}
    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}


def check_factor_values(fid: str) -> dict:
    """Check if factor has computed factor_values."""
    # Check canonical data/features path (same as build_factor_library_state.py)
    features_dir = ROOT / "data" / "features" / "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
    fv_path = features_dir / fid / "factor_values.parquet"
    if fv_path.exists():
        return {"status": "OK", "detail": "factor_values.parquet exists"}
    # Fallback: check research path
    fv_path2 = BASE / "factor_values" / fid / "factor_values.parquet"
    if fv_path2.exists():
        return {"status": "OK", "detail": "factor_values.parquet exists (research)"}
    return {"status": "MISSING", "detail": f"Not found in data/features or research/factor_runs"}


def check_unified_profile(fid: str) -> dict:
    """Check if factor has unified profile."""
    try:
        df = pd.read_csv(DIAG_DIR / "factor_unified_profile_summary.csv")
        rows = df[df["factor_id"] == fid]
        if rows.empty:
            return {"status": "MISSING", "detail": "Not in unified_factor_profile.csv"}
        row = rows.iloc[0]
        score = float(row.get("profile_score", 0) or 0)
        return {"status": "OK", "detail": f"score={score:.1f}"}
    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}


def check_ls_btc_corr(fid: str) -> dict:
    """PM-46B: Check LS-BTC correlation is not blank for factors with monthly LS."""
    try:
        df = pd.read_csv(DIAG_DIR / "factor_regime_exposure_summary.csv")
        rows = df[df["factor_id"] == fid]
        if rows.empty:
            return {"status": "MISSING", "detail": "Not in factor_regime_exposure_summary.csv"}
        row = rows.iloc[0]
        ls_corr = row.get("long_short_btc_corr")
        if pd.isna(ls_corr):
            # Check if factor has monthly LS data
            ls_df = pd.read_csv(EVAL_DIR / "factor_level_period_long_short_summary.csv")
            has_ls = not ls_df[ls_df["factor_name"] == fid].empty
            if has_ls:
                return {"status": "FAIL", "detail": "LS-BTC Corr is NaN despite having monthly LS data"}
            return {"status": "OK", "detail": "No monthly LS data, corr N/A is valid"}
        return {"status": "OK", "detail": f"ls_btc_corr={float(ls_corr):.4f}"}
    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}


def check_source_metadata(fid: str) -> dict:
    """PM-46B: Check source fields / required columns are not N/A."""
    try:
        cards = pd.read_csv(META_DIR / "factor_bilingual_cards.csv")
        rows = cards[cards["factor_id"] == fid]
        if rows.empty:
            return {"status": "MISSING", "detail": "Not in factor_bilingual_cards.csv"}
        row = rows.iloc[0]
        issues = []
        for col in ["data_source_type", "source_fields", "required_columns"]:
            val = row.get(col)
            if pd.isna(val) or str(val).strip() == "":
                issues.append(f"{col}=N/A")
        if issues:
            return {"status": "FAIL", "detail": f"Missing metadata: {', '.join(issues)}"}
        return {"status": "OK", "detail": "All source metadata present"}
    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}


# ── Main checks ────────────────────────────────────────────────────────────

def check_rankic_robust(fid: str) -> dict:
    """PM-54/56A: Check RankIC robust significance for all 4 horizons."""
    path = DIAG_DIR / "factor_rankic_robust_significance_summary.csv"
    if not path.exists():
        return {"status": "MISSING", "detail": "factor_rankic_robust_significance_summary.csv not found"}
    try:
        df = pd.read_csv(path)
        sub = df[df["factor_id"] == fid]
        if sub.empty:
            return {"status": "MISSING", "detail": f"{fid} not in rankic robust summary"}
        horizons = set(sub["horizon"].unique())
        expected = {"1h", "4h", "24h", "72h"}
        missing_hz = expected - horizons
        if missing_hz:
            return {"status": "MISSING", "detail": f"missing horizons: {sorted(missing_hz)}"}
        # Check required fields
        required_fields = ["naive_t_stat", "robust_t_stat", "nw_lag", "n_months",
                           "robust_standard_error", "tstat_inflation_ratio",
                           "significance_class_robust", "overlap_warning"]
        for field in required_fields:
            if field not in sub.columns:
                return {"status": "ERROR", "detail": f"missing column: {field}"}
        return {"status": "OK", "detail": f"4 horizons, {len(sub)} rows"}
    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}


def check_ls_robust(fid: str) -> dict:
    """PM-56/56A: Check LS robust significance for all 4 horizons."""
    path = DIAG_DIR / "factor_ls_robust_significance_summary.csv"
    if not path.exists():
        return {"status": "MISSING", "detail": "factor_ls_robust_significance_summary.csv not found"}
    try:
        df = pd.read_csv(path)
        sub = df[df["factor_id"] == fid]
        if sub.empty:
            return {"status": "MISSING", "detail": f"{fid} not in LS robust summary"}
        horizons = set(sub["horizon"].unique())
        expected = {"1h", "4h", "24h", "72h"}
        missing_hz = expected - horizons
        if missing_hz:
            return {"status": "MISSING", "detail": f"missing horizons: {sorted(missing_hz)}"}
        # Check required fields
        required_fields = ["naive_t_stat", "robust_t_stat", "nw_lag", "n_periods",
                           "robust_standard_error", "tstat_inflation_ratio",
                           "return_robust_class", "overlap_warning"]
        for field in required_fields:
            if field not in sub.columns:
                return {"status": "ERROR", "detail": f"missing column: {field}"}
        return {"status": "OK", "detail": f"4 horizons, {len(sub)} rows"}
    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}


ALL_CHECKS = [
    ("factor_values", check_factor_values),
    ("factor_level_rankic", check_factor_level_rankic),
    ("period_ic", check_period_ic),
    ("period_ls", check_period_ls),
    ("ls_aggregate", check_ls_aggregate),
    ("cumulative_ls", check_cumulative_ls),
    ("paper_payload", check_paper_payload),
    ("regime_btc", check_regime_btc),
    ("quantile_shape", check_quantile_shape),
    ("rolling_stability", check_rolling_stability),
    ("decile_shape", check_decile_shape),
    ("capacity_liquidity", check_capacity_liquidity),
    ("pairwise_redundancy", check_pairwise_redundancy),
    ("cluster", check_cluster),
    ("marginal_info", check_marginal_info),
    ("scorecard_not_stale", check_scorecard_not_stale),
    ("unified_profile", check_unified_profile),
    ("ls_btc_corr", check_ls_btc_corr),
    ("source_metadata", check_source_metadata),
    ("rankic_robust", check_rankic_robust),
    ("ls_robust", check_ls_robust),
]


def run_checks(fid: str) -> dict[str, dict]:
    """Run all checks for a single factor."""
    results = {}
    for name, check_fn in ALL_CHECKS:
        results[name] = check_fn(fid)
    return results


def check_ls_monthly_aggregate_completeness() -> list[dict]:
    """PM-58A: Check all active factors have complete LS monthly aggregate fields."""
    results = []
    state = json.loads(STATE_PATH.read_text())
    active_ids = set(state.get("registered_factor_ids", []))
    
    ls_path = EVAL_DIR / "factor_level_long_short_summary.csv"
    if not ls_path.exists():
        results.append({"check": "pm58a_ls_monthly", "status": "MISSING", "detail": "LS summary file not found"})
        return results
    
    df = pd.read_csv(ls_path)
    active_df = df[df["factor_name"].isin(active_ids)]
    
    required_fields = [
        "long_short_spread_std", "long_short_spread_annualized_return",
        "long_short_spread_annualized_vol", "long_short_spread_max_drawdown",
        "long_short_spread_positive_period_rate", "n_monthly_periods",
    ]
    
    # Check coverage
    n_expected = len(active_ids) * 4
    n_actual = len(active_df)
    if n_actual < n_expected:
        results.append({
            "check": "pm58a_ls_row_coverage",
            "status": "FAIL",
            "detail": f"Expected {n_expected} rows, found {n_actual}",
        })
    
    # Check each required field
    for fld in required_fields:
        n_null = active_df[fld].isna().sum()
        if n_null > 0:
            results.append({
                "check": f"pm58a_{fld}",
                "status": "FAIL",
                "detail": f"{n_null}/{n_actual} null",
            })
        else:
            results.append({
                "check": f"pm58a_{fld}",
                "status": "OK",
                "detail": f"{n_actual}/{n_actual} non-null",
            })
    
    # Check n_monthly_periods >= 2
    low = (active_df["n_monthly_periods"] < 2).sum()
    if low > 0:
        results.append({
            "check": "pm58a_n_monthly_periods_min",
            "status": "FAIL",
            "detail": f"{low} rows have n_monthly_periods < 2",
        })
    else:
        results.append({
            "check": "pm58a_n_monthly_periods_min",
            "status": "OK",
            "detail": f"All {n_actual} rows have n_monthly_periods >= 2",
        })
    
    return results

def _check_pm58b_ls_annualization_consistency() -> list[dict]:
    """PM-58B: Verify LS annualized return uses horizon-aware bars_per_year formula.

    Checks:
    1. For every row with non-null ann ret and mean, ann_ret == mean × bars_per_year
    2. annualization_method == "per_bar_mean_x_bars_per_year" for all rows with non-null ann ret
    """
    results = []
    ls_path = EVAL_DIR / "factor_level_long_short_summary.csv"
    if not ls_path.exists():
        results.append({"check": "pm58b_annualization", "status": "MISSING",
                         "detail": "factor_level_long_short_summary.csv not found"})
        return results

    BARS_PER_YEAR = {"1h": 8760, "4h": 2190, "24h": 365, "72h": 365 / 3}

    df = pd.read_csv(ls_path)
    required_cols = ["horizon", "long_short_spread_mean",
                     "long_short_spread_annualized_return", "annualization_method"]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        results.append({"check": "pm58b_annualization", "status": "MISSING",
                         "detail": f"Missing columns: {missing_cols}"})
        return results

    ann_ret_notnull = df[df["long_short_spread_annualized_return"].notna()]

    # Check 1: annualization_method == "per_bar_mean_x_bars_per_year"
    wrong_method = ann_ret_notnull[
        ann_ret_notnull["annualization_method"] != "per_bar_mean_x_bars_per_year"
    ]
    if len(wrong_method) > 0:
        sample = wrong_method[["factor_name", "horizon", "annualization_method"]].head(5)
        results.append({
            "check": "pm58b_annualization_method",
            "status": "FAIL",
            "detail": f"{len(wrong_method)} rows have wrong annualization_method; "
                      f"sample: {sample.to_dict('records')}",
        })
    else:
        results.append({
            "check": "pm58b_annualization_method",
            "status": "OK",
            "detail": f"All {len(ann_ret_notnull)} rows have "
                      "annualization_method=per_bar_mean_x_bars_per_year",
        })

    # Check 2: ann_ret == monthly_ls_mean × bars_per_year (within tolerance)
    # NOTE: long_short_spread_mean is per-bar mean, NOT monthly mean.
    # The canonical formula uses monthly_ls_mean from monthly series CSV.
    monthly_path = DIAG_DIR / "factor_monthly_long_short_series.csv"
    if not monthly_path.exists():
        results.append({"check": "pm58b_annualization_formula", "status": "MISSING",
                         "detail": "factor_monthly_long_short_series.csv not found"})
        return results

    monthly_df = pd.read_csv(monthly_path)
    monthly_agg = monthly_df.groupby(["factor_id", "horizon"]).agg(
        monthly_mean=("long_short_return", "mean")
    ).reset_index()
    monthly_agg = monthly_agg.rename(columns={"factor_id": "factor_name"})

    check_df = df[df["long_short_spread_annualized_return"].notna()].copy()
    check_df = pd.merge(check_df, monthly_agg, on=["factor_name", "horizon"], how="inner")
    check_df["bpy"] = check_df["horizon"].map(BARS_PER_YEAR)
    check_df["expected"] = check_df["monthly_mean"] * check_df["bpy"]
    check_df["abs_diff"] = (
        check_df["long_short_spread_annualized_return"] - check_df["expected"]
    ).abs()
    check_df["rel_diff"] = check_df["abs_diff"] / check_df["expected"].abs().clip(lower=1e-30)

    bad = check_df[(check_df["abs_diff"] > 1e-8) & (check_df["rel_diff"] > 1e-6)]
    if len(bad) > 0:
        sample = bad[["factor_name", "horizon",
                       "monthly_mean", "long_short_spread_annualized_return",
                       "expected"]].head(5)
        results.append({
            "check": "pm58b_annualization_formula",
            "status": "FAIL",
            "detail": f"{len(bad)} rows have ann_ret != monthly_mean × bars_per_year; "
                      f"sample: {sample.to_dict('records')}",
        })
    else:
        results.append({
            "check": "pm58b_annualization_formula",
            "status": "OK",
            "detail": f"All {len(check_df)} rows pass monthly_mean × bars_per_year consistency "
                      f"(tolerance: abs<=1e-8 or rel<=1e-6)",
        })

    return results


def _check_pm58c_window_diagnostics() -> list[dict]:
    """PM-58C: Verify window diagnostics CSV integrity.

    Checks:
    1. factor_ls_window_diagnostics.csv exists
    2. n_rows == n_factors × n_horizons
    3. window_ls_win_rate in [0, 1]
    4. overlap_warning is one of LOW_OVERLAP, MODERATE_OVERLAP, HIGH_OVERLAP, VERY_HIGH_OVERLAP
    """
    results = []
    wd_path = DIAG_DIR / "factor_ls_window_diagnostics.csv"
    if not wd_path.exists():
        results.append({"check": "pm58c_window_diag_file", "status": "MISSING",
                         "detail": "factor_ls_window_diagnostics.csv not found"})
        return results

    VALID_OVERLAP = {"LOW_OVERLAP", "MODERATE_OVERLAP", "HIGH_OVERLAP", "VERY_HIGH_OVERLAP"}

    try:
        df = pd.read_csv(wd_path)
    except Exception as e:
        results.append({"check": "pm58c_window_diag_read", "status": "ERROR",
                         "detail": str(e)})
        return results

    # Check 1: row count == factors × horizons
    n_rows = len(df)
    n_factors = df["factor_id"].nunique()
    n_horizons = df["horizon"].nunique()
    expected = n_factors * n_horizons
    if n_rows != expected:
        results.append({"check": "pm58c_row_count", "status": "FAIL",
                         "detail": f"n_rows={n_rows}, expected {n_factors}×{n_horizons}={expected}"})
    else:
        results.append({"check": "pm58c_row_count", "status": "OK",
                         "detail": f"{n_rows} rows = {n_factors} factors × {n_horizons} horizons"})

    # Check 2: window_ls_win_rate in [0, 1]
    if "window_ls_win_rate" in df.columns:
        bad = df[(df["window_ls_win_rate"] < 0) | (df["window_ls_win_rate"] > 1)]
        if len(bad) > 0:
            results.append({"check": "pm58c_win_rate_range", "status": "FAIL",
                             "detail": f"{len(bad)} rows have window_ls_win_rate outside [0,1]"})
        else:
            results.append({"check": "pm58c_win_rate_range", "status": "OK",
                             "detail": f"all {n_rows} rows in [0,1]"})
    else:
        results.append({"check": "pm58c_win_rate_range", "status": "MISSING",
                         "detail": "column window_ls_win_rate not found"})

    # Check 3: overlap_warning is valid
    if "overlap_warning" in df.columns:
        invalid = df[~df["overlap_warning"].isin(VALID_OVERLAP)]
        if len(invalid) > 0:
            bad_vals = sorted(invalid["overlap_warning"].unique())
            results.append({"check": "pm58c_overlap_warning_values", "status": "FAIL",
                             "detail": f"invalid values: {bad_vals}"})
        else:
            results.append({"check": "pm58c_overlap_warning_values", "status": "OK",
                             "detail": f"all {n_rows} rows valid ({sorted(df['overlap_warning'].unique())})"})
    else:
        results.append({"check": "pm58c_overlap_warning_values", "status": "MISSING",
                         "detail": "column overlap_warning not found"})

    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Post-Intake Workflow Integrity Checker — PM-43A",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--factor-ids", type=str, default=None,
        help="Comma-separated factor IDs to check",
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Check all registered factors",
    )
    parser.add_argument(
        "--all-active", action="store_true",
        help="PM-53B: Check all active factors with active-universe consistency gate",
    )
    parser.add_argument(
        "--output-dir", type=str, default=str(DIAG_DIR),
        help="Output directory for reports",
    )
    args = parser.parse_args()

    if args.factor_ids:
        fids = [f.strip() for f in args.factor_ids.split(",") if f.strip()]
    elif args.all or args.all_active:
        if not STATE_PATH.exists():
            print("ERROR: factor_library_state.json not found")
            return 1
        state = json.loads(STATE_PATH.read_text())
        fids = sorted(state.get("registered_factor_ids", []))
    else:
        print("ERROR: Must specify --factor-ids or --all")
        return 1

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Checking {len(fids)} factors...")
    all_results = {}
    total_pass = 0
    total_fail = 0
    total_warn = 0

    for fid in fids:
        results = run_checks(fid)
        all_results[fid] = results

        n_pass = sum(1 for r in results.values() if r["status"] == "OK")
        n_fail = sum(1 for r in results.values() if r["status"] in ("MISSING", "ERROR", "STALE"))
        n_warn = sum(1 for r in results.values() if r["status"] == "WARNING")

        status_icon = "✅" if n_fail == 0 else "❌"
        print(f"  {status_icon} {fid:30s} PASS={n_pass} FAIL={n_fail} WARN={n_warn}")

        if n_fail > 0:
            for check_name, result in results.items():
                if result["status"] in ("MISSING", "ERROR", "STALE"):
                    print(f"      ❌ {check_name}: {result['status']} — {result['detail']}")

        total_pass += n_pass
        total_fail += n_fail
        total_warn += n_warn

    # Write CSV report
    csv_rows = []
    for fid, results in all_results.items():
        for check_name, result in results.items():
            csv_rows.append({
                "factor_id": fid,
                "check": check_name,
                "status": result["status"],
                "detail": result["detail"],
            })
    csv_df = pd.DataFrame(csv_rows)
    csv_path = out_dir / "post_intake_workflow_integrity_report.csv"
    csv_df.to_csv(csv_path, index=False)

    # Write JSON report
    json_report = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "n_factors": len(fids),
        "total_checks": total_pass + total_fail + total_warn,
        "pass": total_pass,
        "fail": total_fail,
        "warn": total_warn,
        "factors": all_results,
    }
    json_path = out_dir / "post_intake_workflow_integrity_report.json"
    json_path.write_text(json.dumps(json_report, indent=2, default=str))

    print(f"\n{'='*60}")
    print(f"Integrity Check Summary")
    print(f"{'='*60}")
    print(f"  Factors: {len(fids)}")
    print(f"  Total checks: {total_pass + total_fail + total_warn}")
    print(f"  PASS: {total_pass}")
    print(f"  FAIL: {total_fail}")
    print(f"  WARN: {total_warn}")
    print(f"\n  CSV: {csv_path}")
    print(f"  JSON: {json_path}")

    # PM-53B: Active-universe consistency table (--all-active mode)
    if args.all_active:
        print(f"\n{'='*60}")
        print("Active-Universe Count Consistency (PM-53B)")
        print(f"{'='*60}")
        n_active = len(fids)
        active_set = set(fids)
        consistency_tables = [
            ("rankic", EVAL_DIR / "factor_level_rankic_summary.csv", "factor_name"),
            ("long_short", EVAL_DIR / "factor_level_long_short_summary.csv", "factor_name"),
            ("diagnostics_summary", DIAG_DIR / "factor_diagnostics_summary.csv", "factor_id"),
            ("shape", DIAG_DIR / "factor_quantile_shape_summary.csv", "factor_id"),
            ("rolling_stability", DIAG_DIR / "factor_rolling_stability_summary.csv", "factor_id"),
            ("decile", DIAG_DIR / "factor_decile_shape_summary.csv", "factor_id"),
            ("capacity", DIAG_DIR / "factor_capacity_liquidity_summary.csv", "factor_id"),
            ("scorecard", DIAG_DIR / "factor_quality_scorecard.csv", "factor_id"),
            ("redundancy_summary", DIAG_DIR / "factor_redundancy_summary.csv", "factor_id"),
            ("regime_exposure", DIAG_DIR / "factor_regime_exposure_summary.csv", "factor_id"),
            ("profile", DIAG_DIR / "factor_unified_profile_summary.csv", "factor_id"),
            ("bilingual_cards", META_DIR / "factor_bilingual_cards.csv", "factor_id"),
            # PM-56A: Robust diagnostics (full-universe required)
            ("rankic_robust", DIAG_DIR / "factor_rankic_robust_significance_summary.csv", "factor_id"),
            ("ls_robust", DIAG_DIR / "factor_ls_robust_significance_summary.csv", "factor_id"),
        ]
        consistency_rows = []
        any_consistency_fail = False
        for name, path, key_col in consistency_tables:
            if not path.exists():
                print(f"  ✗ {name:30s}: FILE MISSING (expected {n_active})")
                consistency_rows.append({"table": name, "count": 0, "expected": n_active, "status": "MISSING_FILE"})
                any_consistency_fail = True
                continue
            try:
                import csv as _csv
                ids = set()
                with open(path, newline="", encoding="utf-8") as f:
                    reader = _csv.DictReader(f)
                    actual_key = key_col
                    if actual_key not in (reader.fieldnames or []):
                        actual_key = "factor_id" if "factor_id" in (reader.fieldnames or []) else "factor_name"
                    for row in reader:
                        val = row.get(actual_key, "").strip()
                        if val:
                            ids.add(val)
                missing = active_set - ids
                status = "PASS" if not missing else "FAIL"
                icon = "✓" if status == "PASS" else "✗"
                print(f"  {icon} {name:30s}: {len(ids):3d}/{n_active}  {status}")
                if missing:
                    print(f"    missing: {', '.join(sorted(missing)[:5])}")
                    any_consistency_fail = True
                consistency_rows.append({"table": name, "count": len(ids), "expected": n_active, "status": status,
                                         "missing_count": len(missing)})
            except Exception as e:
                print(f"  ✗ {name:30s}: ERROR — {e}")
                consistency_rows.append({"table": name, "count": 0, "expected": n_active, "status": "ERROR"})
                any_consistency_fail = True

        consistency_verdict = "PASS" if not any_consistency_fail else "FAIL"
        print(f"\n  Active count consistency: {consistency_verdict}")
        
        # PM-58A: LS monthly aggregate field completeness
        print(f"\n{'='*60}")
        print("LS Monthly Aggregate Fields (PM-58A)")
        print(f"{'='*60}")
        pm58a_results = check_ls_monthly_aggregate_completeness()
        pm58a_fail = False
        for r in pm58a_results:
            icon = "✓" if r["status"] in ("OK", "PASS") else "✗"
            print(f"  {icon} {r['check']:35s}: {r['detail']}")
            if r["status"] not in ("OK", "PASS"):
                pm58a_fail = True
        pm58a_verdict = "PASS" if not pm58a_fail else "FAIL"
        print(f"\n  LS monthly aggregate: {pm58a_verdict}")

        # PM-58B: LS annualization consistency (bars_per_year formula)
        print(f"\n{'='*60}")
        print("LS Annualization Consistency (PM-58B)")
        print(f"{'='*60}")
        pm58b_results = _check_pm58b_ls_annualization_consistency()
        pm58b_fail = False
        for r in pm58b_results:
            icon = "✓" if r["status"] in ("OK", "PASS") else "✗"
            print(f"  {icon} {r['check']:35s}: {r['detail']}")
            if r["status"] not in ("OK", "PASS"):
                pm58b_fail = True
        pm58b_verdict = "PASS" if not pm58b_fail else "FAIL"
        print(f"\n  LS annualization consistency: {pm58b_verdict}")

        # Append consistency data to JSON report
        json_report["active_universe_consistency"] = {
            "active_count": n_active,
            "tables": consistency_rows,
            "verdict": consistency_verdict,
        }
        json_report["ls_monthly_aggregate"] = {
            "checks": pm58a_results,
            "verdict": pm58a_verdict,
        }
        json_report["ls_annualization_consistency"] = {
            "checks": pm58b_results,
            "verdict": pm58b_verdict,
        }

        # PM-58C: Window diagnostics integrity
        print(f"\n{'='*60}")
        print("Window Diagnostics (PM-58C)")
        print(f"{'='*60}")
        pm58c_results = _check_pm58c_window_diagnostics()
        pm58c_fail = False
        for r in pm58c_results:
            icon = "✓" if r["status"] in ("OK", "PASS") else "✗"
            print(f"  {icon} {r['check']:35s}: {r['detail']}")
            if r["status"] not in ("OK", "PASS"):
                pm58c_fail = True
        pm58c_verdict = "PASS" if not pm58c_fail else "FAIL"
        print(f"\n  Window diagnostics: {pm58c_verdict}")
        json_report["pm58c_window_diagnostics"] = {
            "checks": pm58c_results,
            "verdict": pm58c_verdict,
        }

        json_path.write_text(json.dumps(json_report, indent=2, default=str))

    return 1 if total_fail > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
