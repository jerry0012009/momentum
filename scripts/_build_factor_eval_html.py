#!/usr/bin/env python3
"""Build the bilingual factor evaluation page with integrated quality scorecard.

Reads 8+ CSV/JSON data sources from the crypto_top50_factor_library and produces
a single static HTML file with embedded JSON, CSS, and JS.

Data sources:
  1. factor_diagnostics/factor_diagnostics_summary.csv
  2. factor_diagnostics/factor_monthly_ic_series.csv
  3. factor_diagnostics/factor_monthly_long_short_series.csv
  4. factor_diagnostics/factor_cumulative_long_short_curve.csv
  5. factor_metadata/factor_bilingual_cards.csv
  6. factor_metadata/factor_card_qa_report.csv
  7. factor_diagnostics/factor_quality_scorecard.csv
  8. factor_diagnostics/factor_quality_scorecard_manifest.json
  9. factor_diagnostics/single_factor_paper_page_payload.json (PM-22)
  10. factor_diagnostics/factor_regime_diagnostics_payload.json (PM-24)
  11. factor_diagnostics/factor_regime_exposure_summary.csv (PM-24)
  12. factor_diagnostics/factor_regime_summary.csv (PM-24)
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

# ── Paths ───────────────────────────────────────────────────────────────────
BASE = Path("research/factor_runs/crypto_top50_factor_library")
DIAG_DIR = BASE / "factor_diagnostics"
META_DIR = BASE / "factor_metadata"
OUT = Path("reports/site/factor-library/factor-evaluation.html")

HORIZONS = ["1h", "4h", "24h", "72h"]


# ── Helpers ─────────────────────────────────────────────────────────────────
def sf(v):
    """Safe float: return None for NaN, else rounded float."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    return round(float(v), 10)


def ss(v):
    """Safe string."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    return str(v).strip()


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def _sanitize_nan(obj):
    """Recursively replace float NaN/inf with None in dicts/lists (JSON-safe)."""
    if isinstance(obj, float):
        if obj != obj or obj == float("inf") or obj == float("-inf"):
            return None
        return obj
    if isinstance(obj, dict):
        return {k: _sanitize_nan(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_nan(v) for v in obj]
    return obj


def load_json(path: Path) -> dict:
    if path.exists():
        raw = json.loads(path.read_text(encoding="utf-8"))
        return _sanitize_nan(raw)
    return {}


# ── Build JSON payload ──────────────────────────────────────────────────────
def build_payload() -> dict:
    diag = load_csv(DIAG_DIR / "factor_diagnostics_summary.csv")
    ic_series = load_csv(DIAG_DIR / "factor_monthly_ic_series.csv")
    ls_series = load_csv(DIAG_DIR / "factor_monthly_long_short_series.csv")
    cum_series = load_csv(DIAG_DIR / "factor_cumulative_long_short_curve.csv")
    cards = load_csv(META_DIR / "factor_bilingual_cards.csv")
    qa = load_csv(META_DIR / "factor_card_qa_report.csv")
    scorecard = load_csv(DIAG_DIR / "factor_quality_scorecard.csv")
    manifest = load_json(DIAG_DIR / "factor_quality_scorecard_manifest.json")

    # PM-22: Load single-factor paper payload
    paper_payload = load_json(DIAG_DIR / "single_factor_paper_page_payload.json")
    paper_map = {}
    for pf in paper_payload.get("factors", []):
        paper_map[pf["factor_id"]] = pf

    # PM-24: Load BTC market regime diagnostics
    regime_payload = load_json(DIAG_DIR / "factor_regime_diagnostics_payload.json")
    regime_exposure = load_csv(DIAG_DIR / "factor_regime_exposure_summary.csv")
    regime_summary = load_csv(DIAG_DIR / "factor_regime_summary.csv")

    # PM-28: Load shape stability and decile shape payloads
    shape_stability_payload = load_json(DIAG_DIR / "factor_shape_stability_payload.json")
    decile_shape_payload = load_json(DIAG_DIR / "factor_decile_shape_payload.json")

    # PM-30: Load capacity / liquidity proxy diagnostics
    cap_liq_payload = load_json(DIAG_DIR / "factor_capacity_liquidity_payload.json")
    cap_liq_summary = load_csv(DIAG_DIR / "factor_capacity_liquidity_summary.csv")

    # PM-35: Load factor-level evaluation data (fallback for new factors)
    EVAL_DIR = BASE / "factor_level_evaluation"
    feval_rankic = load_csv(EVAL_DIR / "factor_level_rankic_summary.csv")
    feval_ls = load_csv(EVAL_DIR / "factor_level_long_short_summary.csv")
    feval_period_ic = load_csv(EVAL_DIR / "factor_level_period_ic_summary.csv")
    feval_period_ls = load_csv(EVAL_DIR / "factor_level_period_long_short_summary.csv")
    feval_coverage = load_csv(EVAL_DIR / "factor_level_coverage_summary.csv")

    # PM-33: Load unified profile workflow data
    profile_payload = load_json(DIAG_DIR / "factor_profile_payload.json")
    unified_profile_list = profile_payload.get("factors", [])
    evidence_matrix_csv = load_csv(DIAG_DIR / "factor_evaluation_evidence_matrix.csv")
    component_scores_csv = load_csv(DIAG_DIR / "factor_profile_component_scores.csv")
    profile_manifest = load_json(DIAG_DIR / "factor_profile_manifest.json")
    workflow_contract = load_json(DIAG_DIR / "factor_evaluation_workflow_contract.json")
    evidence_matrix_json = load_json(DIAG_DIR / "factor_evaluation_evidence_matrix.json")

    # PM-49: Load factor interpretation review
    pm49_reviews = load_json(DIAG_DIR / "recent_factor_interpretation_review.json")
    pm49_map = {r["factor_id"]: r for r in pm49_reviews.get("reviews", [])}

    # PM-51: Load metric glossary
    import json as _json
    _glossary_path = Path(__file__).parent / "factor_metric_glossary.json"
    if _glossary_path.exists():
        with open(_glossary_path) as _gf:
            metric_glossary = _json.load(_gf)
    else:
        metric_glossary = {}

    # ── Summary stats ──
    all_months = sorted(ic_series["month"].unique().tolist()) if not ic_series.empty else []
    quality_counts = cards["metadata_quality"].value_counts().to_dict() if not cards.empty else {}

    # Scorecard summary stats
    sc_class_counts = {}
    sc_confidence_counts = {}
    sc_action_counts = {}
    sc_red_conf_counts = {}
    sc_novelty_counts = {}
    sc_red_level_counts = {}
    sc_cluster_count = 0
    sc_largest_cluster = 0
    if not scorecard.empty:
        sc_class_counts = scorecard["final_quality_class"].value_counts().to_dict()
        sc_confidence_counts = scorecard["score_confidence"].value_counts().to_dict()
        sc_action_counts = scorecard["recommended_next_action"].value_counts().to_dict()
        sc_red_conf_counts = scorecard["redundancy_confidence"].value_counts().to_dict() if "redundancy_confidence" in scorecard.columns else {}
        sc_novelty_counts = scorecard["novelty_assessment"].value_counts().to_dict() if "novelty_assessment" in scorecard.columns else {}
        sc_red_level_counts = scorecard["strongest_redundancy_level"].value_counts().to_dict() if "strongest_redundancy_level" in scorecard.columns else {}
        if "redundancy_cluster_id" in scorecard.columns:
            sc_cluster_count = scorecard["redundancy_cluster_id"].nunique()
        if "redundancy_cluster_size" in scorecard.columns:
            sc_largest_cluster = int(scorecard["redundancy_cluster_size"].max())

    summary = {
        "factor_count": len(diag),
        "horizons": HORIZONS,
        "months": all_months,
        "month_count": len(all_months),
        "quality_counts": quality_counts,
        "scorecard_class_counts": sc_class_counts,
        "scorecard_confidence_counts": sc_confidence_counts,
        "scorecard_action_counts": sc_action_counts,
        "scorecard_red_conf_counts": sc_red_conf_counts,
        "scorecard_novelty_counts": sc_novelty_counts,
        "scorecard_red_level_counts": sc_red_level_counts,
        "cluster_count": sc_cluster_count,
        "largest_cluster_size": sc_largest_cluster,
        "scorecard_manifest": manifest,
    }

    # PM-22: Paper viability summary counts
    paper_class_counts = {}
    cost_class_counts = {}
    for pf in paper_payload.get("factors", []):
        pvc = pf.get("paper_viability_class", "")
        csc = pf.get("cost_sensitivity_class", "")
        if pvc:
            paper_class_counts[pvc] = paper_class_counts.get(pvc, 0) + 1
        if csc:
            cost_class_counts[csc] = cost_class_counts.get(csc, 0) + 1
    summary["paper_viability_counts"] = paper_class_counts
    summary["cost_sensitivity_counts"] = cost_class_counts

    # PM-24: Regime summary stats
    summary["regime_class_counts"] = regime_payload.get("dependency_class_distribution", {})
    summary["regime_distributions"] = regime_payload.get("regime_distributions", {})
    summary["regime_month_range"] = regime_payload.get("month_range", [])
    summary["regime_n_months"] = regime_payload.get("n_months", 0)

    # ── Build lookup dicts ──
    card_map = {}
    if not cards.empty:
        for _, r in cards.iterrows():
            card_map[r["factor_id"]] = r

    qa_map = {}
    if not qa.empty:
        for _, r in qa.iterrows():
            qa_map[r["factor_id"]] = r

    scorecard_map = {}
    if not scorecard.empty:
        for _, r in scorecard.iterrows():
            scorecard_map[r["factor_id"]] = r

    # PM-24: Regime lookup maps
    regime_map = {}
    if not regime_exposure.empty:
        for _, r in regime_exposure.iterrows():
            regime_map[r["factor_id"]] = r

    # Regime detail map: factor_id -> list of regime summary rows
    regime_detail_map: dict[str, list[dict]] = {}
    if not regime_summary.empty:
        for _, r in regime_summary.iterrows():
            fid = r["factor_id"]
            if fid not in regime_detail_map:
                regime_detail_map[fid] = []
            regime_detail_map[fid].append({
                "dimension": ss(r["regime_dimension"]),
                "regime": ss(r["regime_value"]),
                "n_months": int(r["n_months"]) if not pd.isna(r.get("n_months")) else 0,
                "mean": sf(r["mean"]),
                "positive_rate": sf(r["positive_rate"]),
                "metric_type": ss(r["metric_type"]),
            })

    # PM-28: Shape stability and decile shape lookup maps
    ss_map: dict[str, dict] = {}
    for sf_entry in shape_stability_payload.get("factors", []):
        ss_map[sf_entry["factor_id"]] = sf_entry

    ds_map: dict[str, dict] = {}
    for ds_entry in decile_shape_payload.get("factors", []):
        ds_map[ds_entry["factor_id"]] = ds_entry

    # PM-30: Capacity / liquidity lookup maps (CSV has more detail than JSON)
    cap_liq_csv_map: dict[str, dict] = {}
    if not cap_liq_summary.empty:
        for _, r in cap_liq_summary.iterrows():
            cap_liq_csv_map[str(r["factor_id"])] = r.to_dict()

    # PM-33: Unified profile lookup maps
    up_map: dict[str, dict] = {}
    for up in unified_profile_list:
        up_map[up["factor_id"]] = up

    ev_map: dict[str, dict] = {}
    if not evidence_matrix_csv.empty:
        for _, r in evidence_matrix_csv.iterrows():
            ev_map[str(r["factor_id"])] = r.to_dict()

    cs_map: dict[str, dict] = {}
    if not component_scores_csv.empty:
        for _, r in component_scores_csv.iterrows():
            cs_map[str(r["factor_id"])] = r.to_dict()

    # PM-35: Factor-level evaluation lookup maps
    feval_rankic_map: dict[tuple, object] = {}
    if not feval_rankic.empty:
        for _, r in feval_rankic.iterrows():
            feval_rankic_map[(r["factor_name"], r["horizon"])] = r

    feval_ls_map: dict[tuple, object] = {}
    if not feval_ls.empty:
        for _, r in feval_ls.iterrows():
            feval_ls_map[(r["factor_name"], r["horizon"])] = r

    feval_pic_map: dict[tuple, object] = {}
    if not feval_period_ic.empty:
        for _, r in feval_period_ic.iterrows():
            feval_pic_map[(r["factor_name"], r["horizon"], r["period"])] = r

    feval_pls_map: dict[tuple, object] = {}
    if not feval_period_ls.empty:
        for _, r in feval_period_ls.iterrows():
            feval_pls_map[(r["factor_name"], r["horizon"], r["period"])] = r

    feval_cov_map: dict[str, object] = {}
    if not feval_coverage.empty:
        for _, r in feval_coverage.iterrows():
            feval_cov_map[r["factor_name"]] = r

    # ── Build factor list ──
    factors = []
    for _, drow in diag.iterrows():
        fid = str(drow["factor_id"])
        card = card_map.get(fid)
        qa_row = qa_map.get(fid)
        sc_row = scorecard_map.get(fid)

        # Time series for this factor (all horizons)
        fic = ic_series[ic_series["factor_id"] == fid] if not ic_series.empty else pd.DataFrame()
        fls = ls_series[ls_series["factor_id"] == fid] if not ls_series.empty else pd.DataFrame()
        fcum = cum_series[cum_series["factor_id"] == fid] if not cum_series.empty else pd.DataFrame()

        best_hz = ss(drow.get("best_horizon", ""))
        if not best_hz:
            # Fallback to factor-level coverage best horizon
            cov_row = feval_cov_map.get(fid)
            if cov_row is not None:
                best_hz = ss(cov_row.get("best_adj_ic_horizon", "")) or ""
        if not best_hz:
            best_hz = "1h"

        # Monthly IC for best horizon
        fic_best = fic[fic["horizon"] == best_hz].sort_values("month") if not fic.empty else pd.DataFrame()
        monthly_ic = []
        for _, r in fic_best.iterrows():
            monthly_ic.append({
                "month": ss(r["month"]),
                "rank_ic": sf(r["rank_ic"]),
                "rank_ic_adj": sf(r["rank_ic_adj"]),
                "n_obs": int(r["n_obs"]) if not pd.isna(r.get("n_obs")) else None,
                "positive_ic": bool(r["positive_ic"]) if not pd.isna(r.get("positive_ic")) else None,
            })

        # PM-35: If no monthly IC from old diagnostics, try factor-level period IC
        if not monthly_ic and not feval_period_ic.empty:
            for (fz, hz, period), row in feval_pic_map.items():
                if fz == fid and hz == best_hz:
                    adj_val = sf(row.get("direction_adjusted_mean_rank_ic"))
                    monthly_ic.append({
                        "month": str(period),
                        "rank_ic": sf(row.get("raw_mean_rank_ic")),
                        "rank_ic_adj": adj_val,
                        "n_obs": int(row["n_periods"]) if not pd.isna(row.get("n_periods")) else None,
                        "positive_ic": bool(adj_val > 0) if adj_val is not None else None,
                    })
            monthly_ic.sort(key=lambda x: x["month"])

        # Monthly LS for best horizon
        fls_best = fls[fls["horizon"] == best_hz].sort_values("month") if not fls.empty else pd.DataFrame()
        monthly_ls = []
        for _, r in fls_best.iterrows():
            monthly_ls.append({
                "month": ss(r["month"]),
                "long_short_return": sf(r["long_short_return"]),
                "long_leg_return": sf(r["long_leg_return"]),
                "short_leg_return": sf(r["short_leg_return"]),
                "n_long": int(r["n_long"]) if not pd.isna(r.get("n_long")) else None,
                "n_short": int(r["n_short"]) if not pd.isna(r.get("n_short")) else None,
                "positive_ls": bool(r["positive_ls"]) if not pd.isna(r.get("positive_ls")) else None,
            })

        # PM-35: If no monthly LS from old diagnostics, try factor-level period LS
        if not monthly_ls and not feval_period_ls.empty:
            for (fz, hz, period), row in feval_pls_map.items():
                if fz == fid and hz == best_hz:
                    n_obs_val = int(row["n_obs"]) if not pd.isna(row.get("n_obs")) else None
                    ls_ret = sf(row.get("long_short_return"))
                    monthly_ls.append({
                        "month": str(period),
                        "long_short_return": ls_ret,
                        "long_leg_return": sf(row.get("long_leg_return")),
                        "short_leg_return": sf(row.get("short_leg_return")),
                        "n_long": n_obs_val,
                        "n_short": n_obs_val,
                        "positive_ls": bool(row.get("positive_ls", False)) if not pd.isna(row.get("positive_ls")) else None,
                    })
            monthly_ls.sort(key=lambda x: x["month"])

        # Cumulative LS for best horizon
        fcum_best = fcum[fcum["horizon"] == best_hz].sort_values("month") if not cum_series.empty else pd.DataFrame()
        cum_curve = []
        for _, r in fcum_best.iterrows():
            cum_curve.append({
                "month": ss(r["month"]),
                "long_short_return": sf(r["long_short_return"]),
                "cum_long_short_return": sf(r["cum_long_short_return"]),
                "drawdown": sf(r["drawdown"]),
            })

        # Card data
        c = card if card is not None else {}
        q = qa_row if qa_row is not None else {}
        sc = sc_row if sc_row is not None else {}

        factor = {
            "factor_id": fid,
            "family": ss(drow.get("family", "")),
            "lifecycle_status": ss(drow.get("lifecycle_status", "")),
            "expected_direction": ss(drow.get("expected_direction", "")),
            "best_horizon": best_hz,

            # Bilingual card
            "name_en": ss(c.get("name_en", "")),
            "name_zh": ss(c.get("name_zh", "")),
            "family_en": ss(c.get("family_en", "")),
            "family_zh": ss(c.get("family_zh", "")),
            "formula_en": ss(c.get("formula_en", "")),
            "formula_zh": ss(c.get("formula_zh", "")),
            "intuition_en": ss(c.get("intuition_en", "")),
            "intuition_zh": ss(c.get("intuition_zh", "")),
            "expected_direction_explanation_en": ss(c.get("expected_direction_explanation_en", "")),
            "expected_direction_explanation_zh": ss(c.get("expected_direction_explanation_zh", "")),
            "known_limitations_en": ss(c.get("known_limitations_en", "")),
            "known_limitations_zh": ss(c.get("known_limitations_zh", "")),
            "data_source_type": ss(c.get("data_source_type", "")),
            "horizon_notes_en": ss(c.get("horizon_notes_en", "")),
            "horizon_notes_zh": ss(c.get("horizon_notes_zh", "")),
            "status_explanation_en": ss(c.get("status_explanation_en", "")),
            "status_explanation_zh": ss(c.get("status_explanation_zh", "")),
            "review_required_flag": ss(c.get("review_required_flag", "")),
            "metadata_quality": ss(c.get("metadata_quality", drow.get("metadata_quality", ""))),
            "source_fields": ss(c.get("source_fields", "")),
            "required_columns": ss(c.get("required_columns", drow.get("required_columns", ""))),

            # Diagnostics metrics
            "rankic_mean": sf(drow.get("rankic_mean")),
            "rankic_std": sf(drow.get("rankic_std")),
            "rankic_ir": sf(drow.get("rankic_ir")),
            "rankic_t_stat": sf(drow.get("rankic_t_stat")),
            "monthly_ic_positive_rate": sf(drow.get("monthly_ic_positive_rate")),
            "long_short_mean": sf(drow.get("long_short_mean")),
            "long_short_std": sf(drow.get("long_short_std")),
            "long_short_sharpe": sf(drow.get("long_short_sharpe")),
            "long_short_annualized_return": sf(drow.get("long_short_annualized_return")),
            "long_short_annualized_vol": sf(drow.get("long_short_annualized_vol")),
            "long_short_max_drawdown": sf(drow.get("long_short_max_drawdown")),
            "long_short_positive_month_rate": sf(drow.get("long_short_positive_month_rate")),
            "coverage_rate": sf(drow.get("coverage_rate")),
            "redundancy_level": ss(drow.get("redundancy_level", "")),
            "nearest_redundant_factor": ss(drow.get("nearest_redundant_factor", "")),
            "decision_bucket": ss(drow.get("decision_bucket", "")),
            "recommended_action": ss(drow.get("recommended_action", "")),
            "source_warning": ss(drow.get("source_warning", "")),

            # QA
            "qa_notes_zh": ss(q.get("qa_notes_zh", "")),
            "qa_notes_en": ss(q.get("qa_notes_en", "")),
            "needs_human_review": ss(q.get("needs_human_review", "")),
            "qa_reason": ss(q.get("reason", "")),

            # Scorecard (PM-16B / PM-17)
            # PM-19: Redundancy detail fields
            "valid_redundancy_pair_count": sf(sc.get("valid_redundancy_pair_count")),
            "expected_redundancy_pair_count": sf(sc.get("expected_redundancy_pair_count")),
            "valid_redundancy_pair_coverage": sf(sc.get("valid_redundancy_pair_coverage")),
            "insufficient_overlap_pair_count": sf(sc.get("insufficient_overlap_pair_count")),
            "nearest_factor": ss(sc.get("nearest_factor", "")),
            "nearest_abs_spearman_corr": sf(sc.get("nearest_abs_spearman_corr")),
            "strongest_redundancy_level": ss(sc.get("strongest_redundancy_level", "")),
            "novelty_assessment": ss(sc.get("novelty_assessment", "")),
            "redundancy_cluster_id": sf(sc.get("redundancy_cluster_id")),
            "redundancy_cluster_size": sf(sc.get("redundancy_cluster_size")),
            "final_quality_class": ss(sc.get("final_quality_class", "")),
            "final_quality_score": sf(sc.get("final_quality_score")),
            "score_confidence": ss(sc.get("score_confidence", "")),
            "computation_integrity_score": sf(sc.get("computation_integrity_score")),
            "predictive_ranking_score": sf(sc.get("predictive_ranking_score")),
            "portfolio_extraction_score": sf(sc.get("portfolio_extraction_score")),
            "stability_score": sf(sc.get("stability_score")),
            "quantile_shape_score": sf(sc.get("quantile_shape_score")),
            "direction_interpretability_score": sf(sc.get("direction_interpretability_score")),
            "redundancy_novelty_score": sf(sc.get("redundancy_novelty_score")),
            "redundancy_confidence": ss(sc.get("redundancy_confidence", "")),
            "quantile_shape": ss(sc.get("quantile_shape", "")),
            "main_strengths_zh": ss(sc.get("main_strengths_zh", "")),
            "main_weaknesses_zh": ss(sc.get("main_weaknesses_zh", "")),
            "main_strengths_en": ss(sc.get("main_strengths_en", "")),
            "main_weaknesses_en": ss(sc.get("main_weaknesses_en", "")),
            "review_notes_zh": ss(sc.get("review_notes_zh", "")),
            "review_notes_en": ss(sc.get("review_notes_en", "")),
            "recommended_next_action": ss(sc.get("recommended_next_action", "")),

            # Time series
            "monthly_ic": monthly_ic,
            "monthly_ls": monthly_ls,
            "cum_curve": cum_curve,
        }

        # PM-35: Merge factor-level eval data as fallback for missing diagnostics
        if factor["rankic_mean"] is None:
            feval_row = feval_rankic_map.get((fid, best_hz))
            if feval_row is not None:
                factor["rankic_mean"] = sf(feval_row.get("direction_adjusted_mean_rank_ic"))
                # direction_adjusted_rank_ic_std is only in period IC summary, not rankic summary
                factor["rankic_t_stat"] = sf(feval_row.get("t_stat"))
                # coverage in rankic summary is a raw count; derive rate from missing_rate
                missing_rate = sf(feval_row.get("missing_rate"))
                factor["coverage_rate"] = round(1.0 - missing_rate, 6) if missing_rate is not None else None
                if not ss(factor.get("best_horizon")):
                    factor["best_horizon"] = best_hz

            # Also try LS data for missing LS metrics (PM-41: includes aggregates)
            feval_ls_row = feval_ls_map.get((fid, best_hz))
            if feval_ls_row is not None:
                if factor.get("long_short_mean") is None:
                    factor["long_short_mean"] = sf(feval_ls_row.get("long_short_spread_mean"))
                if factor.get("long_short_sharpe") is None:
                    factor["long_short_sharpe"] = sf(feval_ls_row.get("long_short_spread_t_stat"))
                if factor.get("long_short_positive_month_rate") is None:
                    factor["long_short_positive_month_rate"] = sf(feval_ls_row.get("long_short_win_rate"))
                # PM-41: LS aggregate fields from canonical factor-level evaluation
                if factor.get("long_short_std") is None:
                    factor["long_short_std"] = sf(feval_ls_row.get("long_short_spread_std"))
                if factor.get("long_short_annualized_return") is None:
                    factor["long_short_annualized_return"] = sf(feval_ls_row.get("long_short_spread_annualized_return"))
                if factor.get("long_short_annualized_vol") is None:
                    factor["long_short_annualized_vol"] = sf(feval_ls_row.get("long_short_spread_annualized_vol"))
                if factor.get("long_short_max_drawdown") is None:
                    factor["long_short_max_drawdown"] = sf(feval_ls_row.get("long_short_spread_max_drawdown"))

            # Clear source_warning if we found data
            if factor.get("rankic_mean") is not None and factor.get("source_warning"):
                old_warn = factor["source_warning"]
                factor["source_warning"] = old_warn.replace("no_horizon_data", "").replace("monthly_ls_unavailable", "").strip("; ")

        # PM-35: Compute rankic_std / rankic_ir from monthly_ic if still None
        if factor.get("rankic_std") is None and monthly_ic:
            adj_vals = [m["rank_ic_adj"] for m in monthly_ic if m.get("rank_ic_adj") is not None]
            if len(adj_vals) > 1:
                import statistics
                factor["rankic_std"] = round(statistics.stdev(adj_vals), 8)
                if factor.get("rankic_ir") is None and factor["rankic_std"] > 0:
                    factor["rankic_ir"] = round(statistics.mean(adj_vals) / factor["rankic_std"], 6)

        # PM-35: Compute monthly_ic_positive_rate if still None and we have data
        if factor.get("monthly_ic_positive_rate") is None and monthly_ic:
            adj_vals = [m["rank_ic_adj"] for m in monthly_ic if m.get("rank_ic_adj") is not None]
            if adj_vals:
                factor["monthly_ic_positive_rate"] = round(sum(1 for v in adj_vals if v > 0) / len(adj_vals), 4)

        # PM-22 / PM-22B: Merge paper diagnostics into factor
        paper = paper_map.get(fid, {})
        if paper:
            factor.update({
                "paper_viability_class": paper.get("paper_viability_class", ""),
                "cost_sensitivity_class": paper.get("cost_sensitivity_class", ""),
                "gross_sharpe": paper.get("gross_sharpe"),
                "gross_total_return": paper.get("gross_total_return"),
                "paper_max_drawdown": paper.get("max_drawdown"),
                "paper_positive_month_rate": paper.get("positive_month_rate"),
                "paper_avg_turnover": paper.get("avg_turnover"),
                "paper_median_turnover": paper.get("median_turnover"),
                "break_even_fee_bps": paper.get("break_even_fee_bps"),
                "fee_0bps_total_return": paper.get("fee_0bps_total_return"),
                "fee_5bps_total_return": paper.get("fee_5bps_total_return"),
                "fee_10bps_total_return": paper.get("fee_10bps_total_return"),
                "fee_20bps_total_return": paper.get("fee_20bps_total_return"),
                "main_diagnostic_note_zh": paper.get("main_diagnostic_note_zh", ""),
                "main_diagnostic_note_en": paper.get("main_diagnostic_note_en", ""),
                "monthly_nav_series_compact": paper.get("monthly_nav_series_compact", {}),
                "fee_sensitivity_series": paper.get("fee_sensitivity_series", []),
                "monthly_return_series": paper.get("monthly_return_series", []),
                # PM-22B: New series from repaired PM-21B payload
                "turnover_series": paper.get("turnover_series", []),
                "leg_decomposition_series": paper.get("leg_decomposition_series", []),
                "drawdown_series": paper.get("drawdown_series", []),
            })

        # PM-24: Merge regime diagnostics into factor
        rg = regime_map.get(fid)
        if rg is not None:
            factor.update({
                "regime_dependency_class": ss(rg.get("regime_dependency_class", "")),
                "paper_return_btc_corr": sf(rg.get("paper_return_btc_corr")),
                "paper_return_btc_beta": sf(rg.get("paper_return_btc_beta")),
                "long_short_btc_corr": sf(rg.get("long_short_btc_corr")),
                "long_short_btc_beta": sf(rg.get("long_short_btc_beta")),
                "ic_btc_return_corr": sf(rg.get("ic_btc_return_corr")),
                "bull_minus_bear_paper_return": sf(rg.get("bull_minus_bear_paper_return")),
                "highvol_minus_lowvol_paper_return": sf(rg.get("highvol_minus_lowvol_paper_return")),
                "drawdown_minus_normal_paper_return": sf(rg.get("drawdown_minus_normal_paper_return")),
                "main_regime_note_zh": ss(rg.get("main_regime_note_zh", "")),
                "main_regime_note_en": ss(rg.get("main_regime_note_en", "")),
            })
        # Add regime summary data for charts
        factor["regime_detail"] = regime_detail_map.get(fid, [])

        # PM-28: Merge shape stability and decile shape data
        ss_entry = ss_map.get(fid, {})
        ds_entry = ds_map.get(fid, {})
        if ss_entry or ds_entry:
            shape_data = {}
            for hz in HORIZONS:
                hz_shape: dict = {}
                # Shape + stability from PM-26 payload
                hz_ss = ss_entry.get("horizons", {}).get(hz, {})
                if hz_ss:
                    hz_shape["shape"] = hz_ss.get("shape", {})
                    hz_shape["stability"] = hz_ss.get("stability", {})
                # Decile from PM-27B payload
                hz_ds = ds_entry.get("horizons", {}).get(hz, {})
                if hz_ds:
                    eodr = hz_ds.get("expected_order_decile_returns", [])
                    hz_shape["decile"] = {
                        "expected_direction": hz_ds.get("expected_direction", ""),
                        "direction_handling": hz_ds.get("direction_handling", ""),
                        "expected_d10_minus_d1_spread": hz_ds.get("expected_d10_minus_d1_spread"),
                        "direction_aware_slope": hz_ds.get("direction_aware_slope"),
                        "direction_aware_spearman_corr": hz_ds.get("direction_aware_spearman_corr"),
                        "direction_aware_monotonicity_score": hz_ds.get("direction_aware_monotonicity_score"),
                        "direction_aware_monotonicity_class": hz_ds.get("direction_aware_monotonicity_class", ""),
                        "tail_concentration_score": hz_ds.get("tail_concentration_score"),
                        "tail_concentration_class": hz_ds.get("tail_concentration_class", ""),
                        "decile_shape_class": hz_ds.get("decile_shape_class", ""),
                        "q5_shape_class_from_pm26": hz_ds.get("q5_shape_class_from_pm26", ""),
                        "shape_consistency_with_q5": hz_ds.get("shape_consistency_with_q5", ""),
                        "note_zh": hz_ds.get("note_zh", ""),
                        "note_en": hz_ds.get("note_en", ""),
                    }
                    # Derive Q1–Q5 mean returns from expected_order_decile_returns (D1+D2=Q1 … D9+D10=Q5)
                    if len(eodr) == 10:
                        hz_shape["q_returns"] = [
                            (eodr[i * 2] + eodr[i * 2 + 1]) / 2.0 for i in range(5)
                        ]
                    # Raw expected-order decile returns for D1–D10 chart
                    hz_shape["decile"]["expected_order_decile_returns"] = eodr
                shape_data[hz] = hz_shape
            factor["shape_stability"] = shape_data

        # PM-30: Merge capacity / liquidity proxy diagnostics
        cl_row = cap_liq_csv_map.get(fid)
        if cl_row:
            factor.update({
                "cap_liq_proxy_method": ss(cl_row.get("liquidity_proxy_method", "")),
                "cap_liq_capacity_risk_class": ss(cl_row.get("capacity_risk_class", "")),
                "cap_liq_liquidity_risk_class": ss(cl_row.get("liquidity_risk_class", "")),
                "cap_liq_capacity_liquidity_class": ss(cl_row.get("capacity_liquidity_class", "")),
                "cap_liq_volume_concentration_class": ss(cl_row.get("volume_concentration_class", "")),
                "cap_liq_factor_quality_cross_flag": ss(cl_row.get("factor_quality_cross_flag", "")),
                "cap_liq_avg_turnover": sf(cl_row.get("avg_turnover")),
                "cap_liq_median_turnover": sf(cl_row.get("median_turnover")),
                "cap_liq_p90_turnover": sf(cl_row.get("p90_turnover")),
                "cap_liq_selected_basket_volume_median": sf(cl_row.get("selected_basket_volume_median")),
                "cap_liq_selected_basket_volume_p10": sf(cl_row.get("selected_basket_volume_p10")),
                "cap_liq_selected_symbol_count_median": sf(cl_row.get("selected_symbol_count_median")),
                "cap_liq_long_basket_volume_median": sf(cl_row.get("long_basket_volume_median")),
                "cap_liq_short_basket_volume_median": sf(cl_row.get("short_basket_volume_median")),
                "cap_liq_low_volume_symbol_share": sf(cl_row.get("low_volume_symbol_share")),
                "cap_liq_selected_top_symbol_volume_share_median": sf(cl_row.get("selected_top_symbol_volume_share_median")),
                "cap_liq_capacity_at_1pct": sf(cl_row.get("capacity_at_1pct_participation_selected")),
                "cap_liq_capacity_at_5pct": sf(cl_row.get("capacity_at_5pct_participation_selected")),
                "cap_liq_capacity_at_10pct": sf(cl_row.get("capacity_at_10pct_participation_selected")),
                "cap_liq_participation_100k_median": sf(cl_row.get("participation_100000_selected_median")),
                "cap_liq_participation_100k_p10": sf(cl_row.get("participation_100000_selected_p10")),
                "cap_liq_participation_1M_median": sf(cl_row.get("participation_1000000_selected_median")),
                "cap_liq_participation_1M_p10": sf(cl_row.get("participation_1000000_selected_p10")),
                "cap_liq_participation_10M_median": sf(cl_row.get("participation_10000000_selected_median")),
                "cap_liq_participation_10M_p10": sf(cl_row.get("participation_10000000_selected_p10")),
            })

        # PM-33: Merge unified profile data
        up = up_map.get(fid, {})
        if up:
            factor.update({
                "profile_score": sf(up.get("profile_score")),
                "profile_class": ss(up.get("profile_class", "")),
                "profile_confidence": ss(up.get("profile_confidence", "")),
                "workflow_ready_status": ss(up.get("workflow_ready_status", "")),
                "evidence_status": ss(up.get("evidence_status", "")),
                "evidence_completeness_rate": sf(up.get("evidence_completeness_rate")),
                "registry_or_data_status": ss(up.get("registry_or_data_status", "")),
                "recommended_research_action": ss(up.get("recommended_research_action", "")),
                "primary_strength_zh": ss(up.get("primary_strength_zh", "")),
                "primary_strength_en": ss(up.get("primary_strength_en", "")),
                "primary_risk_zh": ss(up.get("primary_risk_zh", "")),
                "primary_risk_en": ss(up.get("primary_risk_en", "")),
                "profile_summary_zh": ss(up.get("profile_summary_zh", "")),
                "profile_summary_en": ss(up.get("profile_summary_en", "")),
                "workflow_missing_or_stale_blocks": ss(up.get("workflow_missing_or_stale_blocks", "")),
                "cluster_member_role": ss(up.get("cluster_member_role", "")),
                "marginal_information_class": ss(up.get("marginal_information_class", "")),
                "source_artifact_count": int(up.get("source_artifact_count", 0)) if up.get("source_artifact_count") else 0,
                "source_artifacts": ss(up.get("source_artifacts", "")),
                "profile_cluster_id": sf(up.get("cluster_id")),
                "profile_cluster_size": sf(up.get("cluster_size")),
            })

        # PM-33: Merge component scores
        # PM-40C: Scorecard override from unified profile when scorecard is stale
        # Scorecard is stale when its underlying metrics are all zero/None
        # (computed before factor-level evaluation was available)
        if hasattr(sc, "get"):
            sc_rankic = sf(sc.get("rankic_mean"))
            sc_coverage = sf(sc.get("coverage_rate"))
            scorecard_is_stale = (sc_rankic is None or sc_rankic == 0) and (sc_coverage is None or sc_coverage == 0)
            if scorecard_is_stale and factor.get("profile_score") is not None:
                # Override stale scorecard with unified profile data
                factor["final_quality_score"] = factor["profile_score"]
                factor["final_quality_class"] = factor.get("profile_class", "")
                factor["recommended_next_action"] = factor.get("recommended_research_action", "")
                factor["score_confidence"] = factor.get("profile_confidence", "")
                factor["review_notes_en"] = factor.get("profile_summary_en", "")
                factor["review_notes_zh"] = factor.get("profile_summary_zh", "")
                factor["main_strengths_en"] = factor.get("primary_strength_en", "")
                factor["main_strengths_zh"] = factor.get("primary_strength_zh", "")
                factor["main_weaknesses_en"] = factor.get("primary_risk_en", "")
                factor["main_weaknesses_zh"] = factor.get("primary_risk_zh", "")
                # Redundancy fields from profile
                mi = factor.get("marginal_information_class", "")
                if mi == "DISTINCT_SINGLETON":
                    factor["novelty_assessment"] = "NOVEL_DISTINCT"
                    factor["strongest_redundancy_level"] = "LOW_REDUNDANCY"
                elif mi == "MOSTLY_REDUNDANT":
                    factor["novelty_assessment"] = "REDUNDANT_NOVELTY_DERIVED"
                    factor["strongest_redundancy_level"] = "MODERATE_REDUNDANCY"
                # Clear stale redundancy pair data
                factor["valid_redundancy_pair_count"] = None
                factor["expected_redundancy_pair_count"] = None
                factor["valid_redundancy_pair_coverage"] = None
                factor["insufficient_overlap_pair_count"] = None
                factor["nearest_factor"] = None
                factor["nearest_abs_spearman_corr"] = None
                factor["redundancy_source"] = "unified_profile"

        cs = cs_map.get(fid, {})
        if cs:
            factor.update({
                "comp_standalone_quality": sf(cs.get("comp_standalone_quality")),
                "comp_paper": sf(cs.get("comp_paper")),
                "comp_cost": sf(cs.get("comp_cost")),
                "comp_regime": sf(cs.get("comp_regime")),
                "comp_shape": sf(cs.get("comp_shape")),
                "comp_stability": sf(cs.get("comp_stability")),
                "comp_capacity": sf(cs.get("comp_capacity")),
                "comp_redundancy": sf(cs.get("comp_redundancy")),
                "comp_marginal_info": sf(cs.get("comp_marginal_info")),
                "comp_evidence_completeness": sf(cs.get("comp_evidence_completeness")),
            })

        # PM-33: Merge evidence matrix
        ev = ev_map.get(fid, {})
        if ev:
            factor.update({
                "ev_has_quality_scorecard": bool(ev.get("has_quality_scorecard", False)),
                "ev_has_diagnostics_summary": bool(ev.get("has_diagnostics_summary", False)),
                "ev_has_redundancy_summary": bool(ev.get("has_redundancy_summary", False)),
                "ev_has_redundancy_cluster_members": bool(ev.get("has_redundancy_cluster_members", False)),
                "ev_has_marginal_information": bool(ev.get("has_marginal_information", False)),
                "ev_has_paper_summary": bool(ev.get("has_paper_summary", False)),
                "ev_has_fee_sensitivity": bool(ev.get("has_fee_sensitivity", False)),
                "ev_has_regime_exposure": bool(ev.get("has_regime_exposure", False)),
                "ev_has_quantile_shape": bool(ev.get("has_quantile_shape", False)),
                "ev_has_rolling_stability": bool(ev.get("has_rolling_stability", False)),
                "ev_has_decile_shape": bool(ev.get("has_decile_shape", False)),
                "ev_has_capacity_liquidity": bool(ev.get("has_capacity_liquidity", False)),
                "ev_has_factor_values": bool(ev.get("has_factor_values", False)),
                "ev_has_factor_level_evaluation": bool(ev.get("has_factor_level_evaluation", False)),
                "ev_has_unified_profile": bool(ev.get("has_unified_profile", False)),
            })


        # PM-40C: Clear stale old redundancy fields that conflict with profile
        if factor.get("workflow_ready_status") == "WORKFLOW_READY":
            # If profile has real cluster data but old scorecard has stale pair counts
            profile_cid = factor.get("profile_cluster_id")
            sc_pair_count = factor.get("valid_redundancy_pair_count")
            if profile_cid is not None and (sc_pair_count is None or sc_pair_count == 0):
                # Old scorecard has no valid pairs — clear stale fields
                factor["valid_redundancy_pair_count"] = None
                factor["expected_redundancy_pair_count"] = None
                factor["valid_redundancy_pair_coverage"] = None
                factor["insufficient_overlap_pair_count"] = None
                factor["nearest_factor"] = None
                factor["nearest_abs_spearman_corr"] = None
                # Mark that redundancy data comes from unified profile, not pairwise
                factor["redundancy_source"] = "unified_profile"
        # PM-40B: Reconcile old redundancy with unified profile
        if factor.get("redundancy_cluster_id") is None or factor.get("redundancy_cluster_id") == -1:
            profile_cid = factor.get("profile_cluster_id")
            if profile_cid is not None:
                factor["redundancy_cluster_id"] = profile_cid
                factor["redundancy_cluster_size"] = factor.get("profile_cluster_size", 1)
        if not factor.get("novelty_assessment") or factor.get("novelty_assessment") == "INSUFFICIENT_OVERLAP":
            role = factor.get("cluster_member_role", "")
            if role == "DISTINCT_SINGLETON":
                factor["novelty_assessment"] = "NOVEL_DISTINCT"
            elif role and "REDUNDANT" in role:
                factor["novelty_assessment"] = "REDUNDANT_NOVELTY_DERIVED"
        if not factor.get("redundancy_level") or factor.get("redundancy_level") == "UNKNOWN":
            mi = factor.get("marginal_information_class", "")
            if mi == "DISTINCT_SINGLETON":
                factor["redundancy_level"] = "LOW_REDUNDANCY"
            elif mi == "MOSTLY_REDUNDANT":
                factor["redundancy_level"] = "MODERATE_REDUNDANCY"


        # PM-40C: Add unavailable reasons for empty LS metrics
        ls_std = factor.get("long_short_std")
        ls_ann_ret = factor.get("long_short_annualized_return")
        ls_ann_vol = factor.get("long_short_annualized_vol")
        ls_max_dd = factor.get("long_short_max_drawdown")
        if any(v is None for v in [ls_std, ls_ann_ret, ls_ann_vol, ls_max_dd]):
            factor["ls_metrics_unavailable_reason"] = "not available from factor-level summary; see paper portfolio diagnostics"
        else:
            factor["ls_metrics_unavailable_reason"] = None

        # PM-49: Add factor interpretation data
        pm49 = pm49_map.get(fid, {})
        factor["pm49_research_decision"] = pm49.get("research_decision", "")
        factor["pm49_direction_status"] = pm49.get("direction_status", "")
        factor["pm49_main_issue_zh"] = pm49.get("main_issue_zh", "")
        factor["pm49_main_issue_en"] = pm49.get("main_issue_en", "")
        factor["pm49_suggested_action_zh"] = pm49.get("suggested_action_zh", "")
        factor["pm49_suggested_action_en"] = pm49.get("suggested_action_en", "")
        factor["pm49_red_flags"] = pm49.get("red_flags", [])

        # PM-52: Per-horizon data
        horizon_metrics = {}
        horizon_monthly_ic = {}
        horizon_monthly_ls = {}
        horizon_cumulative_ls = {}

        for hz in HORIZONS:
            rk = feval_rankic_map.get((fid, hz))
            ls = feval_ls_map.get((fid, hz))
            hm = {}
            if rk is not None:
                hm["rankic_mean"] = sf(rk.get("direction_adjusted_mean_rank_ic"))
                hm["rankic_t_stat"] = sf(rk.get("t_stat"))
                n_periods = sf(rk.get("n_periods"))
                t_val = sf(rk.get("t_stat"))
                if n_periods and t_val and n_periods > 0:
                    hm["rankic_ir"] = round(t_val / (n_periods ** 0.5), 6)
                else:
                    hm["rankic_ir"] = None
                missing_rate = sf(rk.get("missing_rate"))
                hm["coverage_rate"] = round(1.0 - missing_rate, 6) if missing_rate is not None else None
            else:
                hm["rankic_mean"] = None
                hm["rankic_t_stat"] = None
                hm["rankic_ir"] = None
                hm["coverage_rate"] = None
            if ls is not None:
                hm["long_short_mean"] = sf(ls.get("long_short_spread_mean"))
                hm["long_short_std"] = sf(ls.get("long_short_spread_std"))
                hm["long_short_sharpe"] = sf(ls.get("long_short_spread_t_stat"))
                hm["long_short_annualized_return"] = sf(ls.get("long_short_spread_annualized_return"))
                hm["long_short_annualized_vol"] = sf(ls.get("long_short_spread_annualized_vol"))
                hm["long_short_max_drawdown"] = sf(ls.get("long_short_spread_max_drawdown"))
                hm["long_short_positive_month_rate"] = sf(ls.get("long_short_spread_positive_period_rate"))
            else:
                hm["long_short_mean"] = None
                hm["long_short_std"] = None
                hm["long_short_sharpe"] = None
                hm["long_short_annualized_return"] = None
                hm["long_short_annualized_vol"] = None
                hm["long_short_max_drawdown"] = None
                hm["long_short_positive_month_rate"] = None
            # Compute ic_win_rate from monthly IC series
            fic_hz = ic_series[(ic_series["factor_id"] == fid) & (ic_series["horizon"] == hz)] if not ic_series.empty else pd.DataFrame()
            if not fic_hz.empty:
                adj_vals = [sf(r["rank_ic_adj"]) for _, r in fic_hz.iterrows() if sf(r["rank_ic_adj"]) is not None]
                hm["monthly_ic_positive_rate"] = round(sum(1 for v in adj_vals if v > 0) / len(adj_vals), 4) if adj_vals else None
                hm["rankic_std"] = round(float(pd.Series(adj_vals).std()), 8) if len(adj_vals) > 1 else None
            else:
                hm["monthly_ic_positive_rate"] = None
                hm["rankic_std"] = None
            horizon_metrics[hz] = hm

            # Monthly IC series for this horizon
            fic_hz = ic_series[(ic_series["factor_id"] == fid) & (ic_series["horizon"] == hz)].sort_values("month") if not ic_series.empty else pd.DataFrame()
            hmic = []
            for _, r in fic_hz.iterrows():
                hmic.append({
                    "month": ss(r["month"]),
                    "rank_ic": sf(r["rank_ic"]),
                    "rank_ic_adj": sf(r["rank_ic_adj"]),
                    "n_obs": int(r["n_obs"]) if not pd.isna(r.get("n_obs")) else None,
                    "positive_ic": bool(r["positive_ic"]) if not pd.isna(r.get("positive_ic")) else None,
                })
            horizon_monthly_ic[hz] = hmic

            # Monthly LS series for this horizon
            fls_hz = ls_series[(ls_series["factor_id"] == fid) & (ls_series["horizon"] == hz)].sort_values("month") if not ls_series.empty else pd.DataFrame()
            hmls = []
            for _, r in fls_hz.iterrows():
                hmls.append({
                    "month": ss(r["month"]),
                    "long_short_return": sf(r["long_short_return"]),
                    "long_leg_return": sf(r["long_leg_return"]),
                    "short_leg_return": sf(r["short_leg_return"]),
                    "n_long": int(r["n_long"]) if not pd.isna(r.get("n_long")) else None,
                    "n_short": int(r["n_short"]) if not pd.isna(r.get("n_short")) else None,
                    "positive_ls": bool(r["positive_ls"]) if not pd.isna(r.get("positive_ls")) else None,
                })
            horizon_monthly_ls[hz] = hmls

            # Cumulative LS curve for this horizon
            fc_hz = cum_series[(cum_series["factor_id"] == fid) & (cum_series["horizon"] == hz)].sort_values("month") if not cum_series.empty else pd.DataFrame()
            hmcl = []
            for _, r in fc_hz.iterrows():
                hmcl.append({
                    "month": ss(r["month"]),
                    "long_short_return": sf(r["long_short_return"]),
                    "cum_long_short_return": sf(r["cum_long_short_return"]),
                    "drawdown": sf(r["drawdown"]),
                })
            horizon_cumulative_ls[hz] = hmcl

        # Classify horizon pattern
        significant_horizons = []
        direction_signs = []
        for hz in HORIZONS:
            hm = horizon_metrics.get(hz, {})
            t = hm.get("rankic_t_stat")
            mean = hm.get("rankic_mean")
            if t is not None and mean is not None:
                is_sig = abs(t) > 2.0
                if is_sig:
                    significant_horizons.append(hz)
                direction_signs.append(1 if mean > 0 else -1)

        short_sig = [h for h in significant_horizons if h in ("1h", "4h")]
        long_sig = [h for h in significant_horizons if h in ("24h", "72h")]

        if len(set(direction_signs)) > 1 and significant_horizons:
            horizon_pattern = "HORIZON_REVERSAL"
        elif len(significant_horizons) >= 2:
            sig_means = [horizon_metrics[h]["rankic_mean"] for h in significant_horizons if horizon_metrics.get(h, {}).get("rankic_mean") is not None]
            if len(set(1 if m > 0 else -1 for m in sig_means)) == 1:
                horizon_pattern = "HORIZON_CONSISTENT_POSITIVE" if sig_means[0] > 0 else "HORIZON_CONSISTENT_NEGATIVE"
            else:
                horizon_pattern = "MIXED_WEAK"
        elif short_sig and not long_sig:
            horizon_pattern = "SHORT_TERM_ONLY"
        elif long_sig and not short_sig:
            horizon_pattern = "LONG_TERM_ONLY"
        elif len(significant_horizons) == 1:
            horizon_pattern = "SINGLE_HORIZON_SPIKE"
        elif not significant_horizons:
            any_data = any(horizon_metrics.get(h, {}).get("rankic_mean") is not None for h in HORIZONS)
            horizon_pattern = "MIXED_WEAK" if any_data else "INSUFFICIENT_HORIZON_DATA"
        else:
            horizon_pattern = "MIXED_WEAK"

        factor["horizon_metrics"] = horizon_metrics
        factor["horizon_monthly_ic"] = horizon_monthly_ic
        factor["horizon_monthly_ls"] = horizon_monthly_ls
        factor["horizon_cumulative_ls"] = horizon_cumulative_ls
        factor["horizon_pattern"] = horizon_pattern

        factors.append(factor)

    # PM-30: Capacity / liquidity summary stats (after factors are built)
    cap_liq_class_counts: dict[str, int] = {}
    for f in factors:
        clc = f.get("cap_liq_capacity_liquidity_class", "")
        if clc:
            cap_liq_class_counts[clc] = cap_liq_class_counts.get(clc, 0) + 1
        cf = f.get("cap_liq_factor_quality_cross_flag", "")
        if cf:
            cap_liq_class_counts[cf] = cap_liq_class_counts.get(cf, 0) + 1
    summary["cap_liq_class_counts"] = cap_liq_class_counts

    # PM-33: Unified profile workflow summary stats
    summary["workflow_version"] = workflow_contract.get("workflow_version", profile_manifest.get("workflow_version", ""))
    summary["number_of_stages"] = len(workflow_contract.get("stage_order", []))
    summary["evidence_status_distribution"] = evidence_matrix_json.get("evidence_status_distribution", {})
    summary["mean_completeness_rate"] = evidence_matrix_json.get("mean_completeness_rate", 0)
    profile_class_counts: dict[str, int] = {}
    workflow_ready_counts: dict[str, int] = {}
    recommended_action_counts: dict[str, int] = {}
    for up in unified_profile_list:
        pc = up.get("profile_class", "")
        wr = up.get("workflow_ready_status", "")
        ra = up.get("recommended_research_action", "")
        if pc:
            profile_class_counts[pc] = profile_class_counts.get(pc, 0) + 1
        if wr:
            workflow_ready_counts[wr] = workflow_ready_counts.get(wr, 0) + 1
        if ra:
            recommended_action_counts[ra] = recommended_action_counts.get(ra, 0) + 1
    summary["profile_class_counts"] = profile_class_counts
    summary["workflow_ready_counts"] = workflow_ready_counts
    summary["recommended_action_counts"] = recommended_action_counts
    summary["profile_manifest_source_artifacts"] = profile_manifest.get("source_artifacts", [])
    summary["component_weights"] = profile_payload.get("component_weights", {})

    # PM-40: Add page generation time and data last modified time
    summary["page_generation_time"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    latest_mtime = 0.0
    for _p in list(DIAG_DIR.glob("*.csv")) + list(DIAG_DIR.glob("*.json")):
        try:
            mt = _p.stat().st_mtime
            if mt > latest_mtime:
                latest_mtime = mt
        except OSError:
            pass
    if latest_mtime > 0:
        summary["data_last_modified"] = datetime.fromtimestamp(latest_mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    else:
        summary["data_last_modified"] = ""

    return {"summary": summary, "factors": factors, "metric_glossary": metric_glossary}


# ── HTML template ───────────────────────────────────────────────────────────
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Factor Library — Evaluation 因子评价</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📊</text></svg>">
<style>
:root{--bg:#0f172a;--panel:#111c31;--panel2:#17243a;--border:#26364f;--text:#e5edf8;--muted:#8ea0b8;--blue:#60a5fa;--green:#34d399;--amber:#fbbf24;--red:#f87171;--purple:#c084fc}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;line-height:1.5;padding:20px}
a{color:var(--blue);text-decoration:none}
h1{font-size:22px;margin:0 0 4px}
h2{font-size:16px;margin:20px 0 8px}
h3{font-size:13px;margin:14px 0 6px;color:#cbd5e1}
.topbar{display:flex;justify-content:space-between;gap:16px;align-items:flex-start;margin-bottom:12px}
.subtitle{color:var(--muted);font-size:12px}
.nav a{margin-right:10px}
.disclaimer{background:#2b1820;border:1px solid #7f1d1d;color:#fecaca;border-radius:8px;padding:10px 12px;margin:10px 0;font-size:12px}
.stats{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0}
.stat{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:8px 10px;min-width:100px}
.stat strong{display:block;font-size:20px}.stat span{color:var(--muted);font-size:10px}
.quality-grid{display:flex;gap:6px;flex-wrap:wrap;margin:8px 0}
.quality-badge{display:inline-block;border-radius:999px;padding:2px 8px;font-size:10px;white-space:nowrap}
.quality-badge.complete{background:#166534;color:#bbf7d0}
.quality-badge.direction_ambiguous{background:#92400e;color:#fef3c7}
.quality-badge.needs_review{background:#7f1d1d;color:#fecaca}
.quality-badge.formula_ambiguous{background:#581c87;color:#e9d5ff}
.layout{display:flex;flex-direction:column;gap:14px}
.card{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:12px;margin-bottom:12px}
.detail{scroll-margin-top:12px}
.controls{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}
.back-to-table{display:inline-flex;align-items:center;gap:4px;background:#142035;border:1px solid var(--border);border-radius:6px;padding:5px 10px;font-size:11px;color:var(--muted);cursor:pointer;margin-bottom:8px;transition:background .15s}
.back-to-table:hover{background:#1d2d47;color:var(--text)}
input,select{background:#0b1220;color:var(--text);border:1px solid var(--border);border-radius:7px;padding:6px 8px;font-size:12px}
input[type="text"]{min-width:200px;flex:1}
table{width:100%;border-collapse:collapse;font-size:11px}
th{background:#142035;color:var(--muted);text-align:left;padding:6px 7px;position:sticky;top:0;z-index:1;cursor:pointer;user-select:none;white-space:nowrap}
th:hover{color:#e5edf8}
th .sort-arrow{font-size:9px;margin-left:2px}
td{border-bottom:1px solid var(--border);padding:5px 7px;vertical-align:middle}
tr.factor-row{cursor:pointer}tr.factor-row:hover,tr.factor-row.selected{background:#1d2d47}
.num{text-align:right;font-variant-numeric:tabular-nums;font-size:11px}
.strong{color:var(--green);font-weight:700}.watch{color:var(--amber);font-weight:700}.plain{color:var(--text)}.muted-c{color:var(--muted)}
.table-wrap{overflow-x:auto;max-height:70vh;overflow-y:auto}
.factor-link{background:none;border:0;color:var(--blue);font:inherit;font-weight:650;cursor:pointer;padding:0;text-align:left}
.bucket-badge{display:inline-block;border-radius:999px;padding:2px 7px;font-size:9px;background:#334155;color:#e2e8f0;white-space:nowrap}
.dir-badge{display:inline-block;border-radius:999px;padding:2px 7px;font-size:9px;white-space:nowrap}
.dir-badge.positive{background:#166534;color:#bbf7d0}
.dir-badge.negative{background:#7f1d1d;color:#fecaca}
.dir-badge.conditional{background:#581c87;color:#e9d5ff}
.metric-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}
@media(max-width:700px){.metric-grid{grid-template-columns:1fr 1fr}}
.metric{background:var(--panel2);border:1px solid var(--border);border-radius:8px;padding:7px}
.metric span{display:block;color:var(--muted);font-size:9px;text-transform:uppercase}
.metric strong{font-size:14px}
.chart-container{background:#0b1220;border:1px solid var(--border);border-radius:8px;padding:8px;margin:8px 0;overflow:hidden}
.chart-title{color:var(--muted);font-size:10px;margin-bottom:4px;text-transform:uppercase}
.kv{display:grid;grid-template-columns:120px 1fr;gap:4px;font-size:11px;margin-top:8px}
.kv div:nth-child(odd){color:var(--muted)}
.bilingual{margin:4px 0}.bilingual .zh{font-size:13px}.bilingual .en{font-size:11px;color:var(--muted)}
.formula-block{background:#0b1220;border:1px solid var(--border);border-radius:6px;padding:8px;font-family:'Fira Code',monospace;font-size:12px;margin:4px 0;word-break:break-all}
.section-divider{border-top:1px solid var(--border);margin:12px 0 8px}
.small{font-size:11px;color:var(--muted)}
.footer{margin-top:20px;border-top:1px solid var(--border);padding-top:10px;color:var(--muted);font-size:11px;display:flex;gap:12px;flex-wrap:wrap}

/* ── Scorecard styles ── */
.sc-class-badge{display:inline-block;border-radius:999px;padding:3px 10px;font-size:10px;font-weight:600;white-space:nowrap}
.sc-class-badge.strong_research{background:#166534;color:#bbf7d0}
.sc-class-badge.promising{background:#92400e;color:#fef3c7}
.sc-class-badge.review_req{background:#7f1d1d;color:#fecaca}
.sc-class-badge.other_class{background:#334155;color:#e2e8f0}
.sc-confidence-badge{display:inline-block;border-radius:999px;padding:2px 8px;font-size:9px;font-weight:600;white-space:nowrap}
.sc-confidence-badge.high-conf{background:#166534;color:#bbf7d0}
.sc-confidence-badge.medium-conf{background:#92400e;color:#fef3c7}
.sc-confidence-badge.low-conf{background:#7f1d1d;color:#fecaca}
.sc-action-badge{display:inline-block;border-radius:999px;padding:2px 7px;font-size:9px;background:#334155;color:#e2e8f0;white-space:nowrap}
.sc-bar-wrap{display:flex;align-items:center;gap:6px;margin:3px 0;font-size:10px}
.sc-bar-label{width:200px;flex-shrink:0;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sc-bar-track{flex:1;height:14px;background:#0b1220;border:1px solid var(--border);border-radius:4px;overflow:hidden;min-width:60px}
.sc-bar-fill{height:100%;border-radius:3px;display:flex;align-items:center;justify-content:flex-end;padding-right:4px;font-size:9px;font-weight:600;color:#fff;min-width:24px}
.sc-bar-fill.sc-green{background:#22c55e}
.sc-bar-fill.sc-yellow{background:#eab308;color:#1a1a1a}
.sc-bar-fill.sc-red{background:#ef4444}
.sc-score-bar{margin:6px 0}
.sc-score-bar-track{height:20px;background:#0b1220;border:1px solid var(--border);border-radius:6px;overflow:hidden}
.sc-score-bar-fill{height:100%;border-radius:5px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:#fff}
.sc-summary-grid{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0}
.sc-summary-card{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:8px 12px;min-width:140px;text-align:center}
.sc-summary-card strong{display:block;font-size:20px}
.sc-summary-card span{color:var(--muted);font-size:10px;display:block}
.sc-caveat{background:#1a1a2e;border:1px solid #3b3b5c;color:#c4b5fd;border-radius:8px;padding:10px 12px;margin:10px 0;font-size:11px;line-height:1.6}
.sc-caveat strong{color:#e9d5ff}
.sc-strengths{color:var(--green);font-size:11px}
.sc-weaknesses{color:var(--amber);font-size:11px}
.sc-review-notes{color:var(--muted);font-size:11px;font-style:italic}

/* ── Paper diagnostics styles (PM-22) ── */
.paper-badge{display:inline-block;border-radius:999px;padding:2px 8px;font-size:10px;font-weight:600;white-space:nowrap}
.paper-badge.paper_strong{background:#166534;color:#bbf7d0}
.paper-badge.paper_promising{background:#92400e;color:#fef3c7}
.paper-badge.paper_mixed{background:#7f1d1d;color:#fecaca}
.paper-badge.paper_weak{background:#450a0a;color:#fecaca}
.paper-badge.paper_review{background:#581c87;color:#e9d5ff}
.paper-badge.cost_robust{background:#166534;color:#bbf7d0}
.paper-badge.cost_sensitive{background:#92400e;color:#fef3c7}
.paper-badge.cost_collapsed{background:#7f1d1d;color:#fecaca}
.paper-badge.cost_insufficient{background:#334155;color:#e2e8f0}
.paper-caveat{background:#1a1a2e;border:1px solid #3b3b5c;color:#c4b5fd;border-radius:8px;padding:10px 12px;margin:10px 0;font-size:11px;line-height:1.6}
.paper-caveat strong{color:#e9d5ff}

/* ── Regime dependency badges (PM-24) ── */
.regime-badge{display:inline-block;border-radius:999px;padding:2px 8px;font-size:10px;font-weight:600;white-space:nowrap}
.regime-badge.REGIME_ROBUST{background:#166534;color:#bbf7d0}
.regime-badge.BULL_DEPENDENT{background:#92400e;color:#fef3c7}
.regime-badge.BEAR_DEPENDENT{background:#7f1d1d;color:#fecaca}
.regime-badge.VOL_DEPENDENT{background:#581c87;color:#e9d5ff}
.regime-badge.DRAWDOWN_FRAGILE{background:#450a0a;color:#fecaca}
.regime-caveat{background:#1a1a2e;border:1px solid #3b3b5c;color:#c4b5fd;border-radius:8px;padding:10px 12px;margin:10px 0;font-size:11px;line-height:1.6}
.regime-caveat strong{color:#e9d5ff}

/* ── Shape / stability / decile badges (PM-28) ── */
.shape-badge{display:inline-block;border-radius:999px;padding:2px 8px;font-size:10px;font-weight:600;white-space:nowrap}
.shape-badge.EXCELLENT_MONOTONIC{background:#166534;color:#bbf7d0}
.shape-badge.WEAK_MONOTONIC{background:#92400e;color:#fef3c7}
.shape-badge.NON_MONOTONIC{background:#7f1d1d;color:#fecaca}
.shape-badge.DECILE_MONOTONIC_STRONG{background:#166534;color:#bbf7d0}
.shape-badge.DECILE_MONOTONIC_WEAK{background:#92400e;color:#fef3c7}
.shape-badge.DECILE_NONLINEAR{background:#581c87;color:#e9d5ff}
.shape-badge.DECILE_REVEALS_NONLINEARITY{background:#581c87;color:#e9d5ff}
.shape-badge.CONSISTENT{background:#166534;color:#bbf7d0}
.shape-badge.STABLE_POSITIVE{background:#166534;color:#bbf7d0}
.shape-badge.STABLE_WEAK{background:#92400e;color:#fef3c7}
.shape-badge.STABLE_NEGATIVE{background:#7f1d1d;color:#fecaca}
.shape-badge.UNSTABLE{background:#450a0a;color:#fecaca}
.shape-badge.TAIL_DOMINANT{background:#581c87;color:#e9d5ff}
.shape-badge.MODERATE{background:#334155;color:#e2e8f0}
.shape-badge.BOTH_TAILS_U_SHAPED{background:#581c87;color:#e9d5ff}
.shape-badge.NONLINEAR_MIXED{background:#7f1d1d;color:#fecaca}
.shape-badge.COST_SENSITIVE{background:#92400e;color:#fef3c7}
.shape-badge.COST_COLLAPSED{background:#7f1d1d;color:#fecaca}
.shape-caveat{background:#1a1a2e;border:1px solid #3b3b5c;color:#c4b5fd;border-radius:8px;padding:10px 12px;margin:10px 0;font-size:11px;line-height:1.6}
.shape-caveat strong{color:#e9d5ff}

/* ── Capacity / liquidity badges (PM-30) ── */
.cap-badge{display:inline-block;border-radius:999px;padding:2px 8px;font-size:10px;font-weight:600;white-space:nowrap}
.cap-badge.CAPACITY_FRIENDLY{background:#166534;color:#bbf7d0}
.cap-badge.MODERATE_CAPACITY_RISK{background:#92400e;color:#fef3c7}
.cap-badge.CAPACITY_FRAGILE{background:#7f1d1d;color:#fecaca}
.cap-badge.LIQUIDITY_FRAGILE{background:#7f1d1d;color:#fecaca}
.cap-badge.LIQUIDITY_ADEQUATE{background:#166534;color:#bbf7d0}
.cap-badge.WATCH_LIQUIDITY{background:#92400e;color:#fef3c7}
.cap-badge.WATCH_BOTH{background:#7f1d1d;color:#fecaca}
.cap-badge.CAPACITY_OK{background:#166534;color:#bbf7d0}
.cap-badge.DIVERSIFIED_LIQUIDITY{background:#166534;color:#bbf7d0}
.cap-badge.CONCENTRATED_LIQUIDITY{background:#92400e;color:#fef3c7}
.cap-badge.STABLE_BUT_TOO_ILLIQUID{background:#7f1d1d;color:#fecaca}
.cap-badge.NONE_FLAG{background:#334155;color:#e2e8f0}
.cap-caveat{background:#1a1a2e;border:1px solid #3b3b5c;color:#c4b5fd;border-radius:8px;padding:10px 12px;margin:10px 0;font-size:11px;line-height:1.6}
.cap-caveat strong{color:#e9d5ff}

/* ── PM-33: Unified profile badges ── */
.profile-class-badge{display:inline-block;border-radius:999px;padding:2px 8px;font-size:10px;font-weight:600;white-space:nowrap}
.profile-class-badge.BROAD_WATCHLIST{background:#334155;color:#e2e8f0}
.profile-class-badge.PROMISING_BUT_REGIME_DEPENDENT{background:#92400e;color:#fef3c7}
.profile-class-badge.UNIQUE_BUT_WEAK{background:#7f1d1d;color:#fecaca}
.workflow-ready-badge{display:inline-block;border-radius:999px;padding:2px 8px;font-size:10px;font-weight:600;white-space:nowrap}
.workflow-ready-badge.WORKFLOW_READY{background:#166534;color:#bbf7d0}
.workflow-ready-badge.WORKFLOW_NOT_READY{background:#7f1d1d;color:#fecaca}
.evidence-badge{display:inline-block;border-radius:999px;padding:2px 8px;font-size:10px;font-weight:600;white-space:nowrap}
.evidence-badge.COMPLETE{background:#166534;color:#bbf7d0}
.evidence-badge.COMPLETE_WITH_WARNINGS{background:#92400e;color:#fef3c7}
.evidence-badge.INCOMPLETE{background:#7f1d1d;color:#fecaca}
.research-action-badge{display:inline-block;border-radius:999px;padding:2px 7px;font-size:9px;background:#334155;color:#e2e8f0;white-space:nowrap}
.ev-block-badge{display:inline-block;border-radius:4px;padding:2px 6px;font-size:9px;font-weight:600;white-space:nowrap}
.ev-block-badge.ev-pass{background:#166534;color:#bbf7d0}
.ev-block-badge.ev-miss{background:#7f1d1d;color:#fecaca}
.up-caveat{background:#1a1a2e;border:1px solid #3b3b5c;color:#c4b5fd;border-radius:8px;padding:10px 12px;margin:10px 0;font-size:11px;line-height:1.6}
.up-caveat strong{color:#e9d5ff}

/* ── PM-49: Tooltip styles ── */
.tooltip-trigger { position: relative; cursor: help; border-bottom: 1px dashed rgba(148,163,184,0.4); display: inline; }
.tooltip-content { visibility: hidden; opacity: 0; position: fixed; z-index: 9999; background: #1e293b; border: 1px solid #475569; border-radius: 8px; padding: 10px 14px; max-width: 420px; min-width: 200px; font-size: 12px; line-height: 1.6; color: #cbd5e1; box-shadow: 0 8px 24px rgba(0,0,0,0.5); transition: opacity 0.15s ease; pointer-events: none; }
.tooltip-trigger:hover .tooltip-content { visibility: visible; opacity: 1; }
.tooltip-content strong { color: #f1f5f9; }
.tooltip-content .tt-warn { color: #fbbf24; }

/* ── PM-51: Detail panel (click-expanded) ── */
.detail-panel { position: fixed; z-index: 10000; background: #0f172a; border: 1px solid #475569; border-radius: 12px; max-width: 420px; min-width: 320px; max-height: 80vh; overflow-y: auto; box-shadow: 0 12px 40px rgba(0,0,0,0.6); font-size: 13px; color: #cbd5e1; }
.detail-header { padding: 12px 16px; border-bottom: 1px solid #334155; display: flex; align-items: center; gap: 8px; position: sticky; top: 0; background: #0f172a; z-index: 1; }
.detail-header strong { color: #f1f5f9; flex: 1; }
.detail-close { cursor: pointer; color: #64748b; font-size: 18px; padding: 0 4px; }
.detail-close:hover { color: #f87171; }
.detail-body { padding: 12px 16px; }
.detail-section { margin-bottom: 10px; }
.detail-label { font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase; margin-bottom: 3px; }
.detail-warn { color: #fbbf24; }
.detail-linked { display: inline-block; padding: 2px 8px; margin: 2px; background: #1e293b; border: 1px solid #334155; border-radius: 4px; font-size: 11px; cursor: pointer; color: #60a5fa; }
.detail-linked:hover { background: #334155; }

/* ── PM-51: Inference guardrail badges ── */
.guard-badge { display: inline-block; padding: 1px 6px; border-radius: 3px; font-size: 10px; font-weight: 600; vertical-align: middle; }
.guard-evidence { background: #1e3a5f; color: #93c5fd; }
.guard-interpretation { background: #3b2f63; color: #c4b5fd; }
.guard-inference { background: #365314; color: #bef264; }
.guard-notsignal { background: #451a1a; color: #fca5a5; }
.guard-validation { background: #451a03; color: #fdba74; }
.guard-diagnostic { background: #1e3a5f; color: #93c5fd; }

/* ── PM-51: Chart reading guide ── */
.chart-guide { background: #1e293b; border: 1px solid #334155; border-radius: 6px; margin: 8px 0; font-size: 12px; }
.chart-guide summary { padding: 6px 12px; cursor: pointer; color: #94a3b8; font-size: 11px; }
.chart-guide summary:hover { color: #e2e8f0; }
.chart-guide-body { padding: 0 12px 10px; color: #94a3b8; line-height: 1.6; }

/* ── PM-49: How-to-Read section styles ── */
.how-to-read { background: #1e293b; border: 1px solid #334155; border-radius: 8px; margin: 16px 0; }
.how-to-read summary { padding: 12px 16px; cursor: pointer; font-weight: 600; color: #94a3b8; }
.how-to-read summary:hover { color: #e2e8f0; }
.how-to-read-body { padding: 0 16px 16px; font-size: 14px; line-height: 1.8; color: #94a3b8; }
.how-to-read-body ol { padding-left: 20px; }
.how-to-read-body .warn { color: #fbbf24; font-weight: 600; }

/* ── PM-49: Research interpretation badge styles ── */
.pm49-badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; margin: 2px; }
.pm49-decision { background: #312e81; color: #a5b4fc; }
.pm49-direction-aligned { background: #064e3b; color: #6ee7b7; }
.pm49-direction-conflict { background: #7f1d1d; color: #fca5a5; }
.pm49-direction-reversal { background: #78350f; color: #fcd34d; }
.pm49-not-signal { background: #44403c; color: #a8a29e; font-style: italic; }

/* ── PM-49: Red flag badge styles ── */
.rf-badge { display: inline-block; padding: 2px 6px; border-radius: 3px; font-size: 10px; font-weight: 700; margin: 1px; text-transform: uppercase; letter-spacing: 0.5px; }
.rf-DIRECTION_CONFLICT { background: #7f1d1d; color: #fca5a5; }
.rf-SHORT_HORIZON_REVERSAL { background: #78350f; color: #fcd34d; }
.rf-COST_COLLAPSED { background: #4c1d95; color: #c4b5fd; }
.rf-REGIME_DEPENDENT { background: #1e3a5f; color: #93c5fd; }
.rf-HIGH_REDUNDANCY { background: #3f3f46; color: #a1a1aa; }
.rf-LOW_MARGINAL_INFO { background: #3f3f46; color: #a1a1aa; }
.rf-FORMULA_REVIEW_CANDIDATE { background: #7f1d1d; color: #fca5a5; }
.rf-DIRECTION_SEMANTICS_REVIEW_REQUIRED { background: #7f1d1d; color: #fca5a5; }
.rf-CANDIDATE_POOL_WATCHLIST { background: #064e3b; color: #6ee7b7; }
.rf-DIAGNOSTIC_ONLY { background: #44403c; color: #a8a29e; }

/* ── PM-49: Evidence vs Judgment section styles ── */
.evidence-section { border-left: 3px solid #3b82f6; padding-left: 12px; margin: 8px 0; }
.judgment-section { border-left: 3px solid #f59e0b; padding-left: 12px; margin: 8px 0; background: rgba(245,158,11,0.05); border-radius: 0 4px 4px 0; padding: 8px 12px; }
.judgment-label { font-size: 10px; text-transform: uppercase; letter-spacing: 1px; color: #f59e0b; font-weight: 700; margin-bottom: 4px; }
.evidence-label { font-size: 10px; text-transform: uppercase; letter-spacing: 1px; color: #3b82f6; font-weight: 700; margin-bottom: 4px; }

/* ── PM-52: Horizon Transparency Layer ── */
.horizon-switch{display:flex;gap:4px;margin:8px 0;flex-wrap:wrap;align-items:center}
.horizon-btn{background:#142035;border:1px solid var(--border);border-radius:6px;padding:4px 12px;font-size:11px;color:var(--muted);cursor:pointer;transition:all .15s;white-space:nowrap}
.horizon-btn:hover{background:#1d2d47;color:var(--text)}
.horizon-btn.active{background:#1e3a5f;border-color:var(--blue);color:var(--blue);font-weight:600}
.horizon-btn .best-tag{font-size:8px;background:var(--green);color:#000;border-radius:3px;padding:1px 4px;margin-left:4px;font-weight:700}
.horizon-btn.active .best-tag{background:var(--green);color:#000}
.horizon-alt-label{font-size:10px;color:var(--amber);margin-left:8px;font-style:italic}
.horizon-summary-table{width:100%;border-collapse:collapse;font-size:10px;margin:8px 0}
.horizon-summary-table th{background:#142035;color:var(--muted);padding:4px 6px;text-align:right;white-space:nowrap;font-size:9px}
.horizon-summary-table th:first-child{text-align:left}
.horizon-summary-table td{padding:4px 6px;border-bottom:1px solid var(--border);text-align:right;font-variant-numeric:tabular-nums}
.horizon-summary-table td:first-child{text-align:left;font-weight:600}
.horizon-summary-table tr.best-row{background:#1e3a5f20}
.horizon-summary-table tr.best-row td:first-child::after{content:' ★ Best';font-size:8px;color:var(--green);font-weight:400}
.horizon-summary-table .conflict-cell{color:var(--red)}
.horizon-summary-table .tension-cell{color:var(--amber)}
.horizon-pattern-badge{display:inline-block;border-radius:999px;padding:2px 8px;font-size:9px;font-weight:600;white-space:nowrap;margin-left:8px}
.horizon-pattern-badge.hz-consistent-pos{background:#166534;color:#bbf7d0}
.horizon-pattern-badge.hz-consistent-neg{background:#7f1d1d;color:#fecaca}
.horizon-pattern-badge.hz-short-only{background:#92400e;color:#fef3c7}
.horizon-pattern-badge.hz-long-only{background:#581c87;color:#e9d5ff}
.horizon-pattern-badge.hz-reversal{background:#991b1b;color:#fecaca}
.horizon-pattern-badge.hz-spike{background:#78350f;color:#fef3c7}
.horizon-pattern-badge.hz-mixed{background:#334155;color:#e2e8f0}
.horizon-pattern-badge.hz-insufficient{background:#1e293b;color:#94a3b8}
</style>
</head>
<body>

<div class="topbar">
  <div>
    <h1>Factor Library · Evaluation</h1>
    <h1 style="font-size:15px;color:var(--muted)">因子库 · 因子诊断评价</h1>
  </div>
  <div class="subtitle nav">
    <a href="index.html">Home</a> · <a href="actual-script-map.html">Pipeline Map</a> · <a href="signal-evaluation-summary.html">Signal Evaluation</a>
  </div>
</div>

<div class="disclaimer">⚠ 仅作研究诊断 · Diagnostic only — this page evaluates factor behavior for research; it does not promote factors into signals and does not make production or alpha claims.</div>

<details class="how-to-read">
  <summary>📖 如何阅读本页 / How to Read This Page</summary>
  <div class="how-to-read-body">
    <p><strong>阅读顺序 / Reading Order:</strong></p>
    <ol>
      <li><strong>Evidence Completeness</strong> — 数据完整性，不等于因子好</li>
      <li><strong>RankIC</strong> — 排序信息系数，不是收益</li>
      <li><strong>Long-Short</strong> — 多空收益，不是交易策略</li>
      <li><strong>Paper Portfolio</strong> — 纸面组合诊断，不是实盘</li>
      <li><strong>Fee Sensitivity</strong> — 成本敏感度</li>
      <li><strong>Regime/BTC</strong> — 市场状态依赖</li>
      <li><strong>Quantile/Decile Shape</strong> — 收益分布形状</li>
      <li><strong>Capacity/Liquidity</strong> — 容量和流动性</li>
      <li><strong>Redundancy/Marginal</strong> — 冗余和边际信息</li>
      <li><strong>Scorecard/Profile</strong> — 综合评分</li>
      <li><strong>Research Interpretation</strong> — PM-49 研究解释（Judgment，非信号）</li>
    </ol>
    <p class="warn">⚠️ Evidence complete ≠ 因子好 | RankIC ≠ 收益 | Paper ≠ 交易策略 | Profile Score ≠ 交易建议 | Research Interpretation ≠ Signal</p>

    <h4 style="color:#cbd5e1;margin-top:16px">🕐 How to Read Horizons / 如何阅读不同视野</h4>
    <ol>
      <li><strong>Best Horizon</strong> 是历史评价中综合表现最值得关注的视野，不代表其他视野也好。</li>
      <li><strong>多个视野同向</strong>（HORIZON_CONSISTENT），说明因子方向更稳健。</li>
      <li><strong>只有一个视野好</strong>（SINGLE_HORIZON_SPIKE），可能是 horizon-specific，也可能是偶然。</li>
      <li><strong>短期和长期方向相反</strong>（HORIZON_REVERSAL），说明因子可能存在 horizon-dependent semantics——短期是反转，长期是动量。</li>
      <li><strong>Horizon Switch</strong> 是研究诊断工具，不是交易周期选择器。不能因为某个 horizon 好就直接做信号。</li>
      <li><strong>All-Horizon Summary Table</strong> 中 ⚠️ = 该视野RankIC方向与expected_direction冲突；⚡ = IC显著但LS弱（IC-LS Tension）。</li>
    </ol>
    <p class="warn">⚠️ Horizon comparison is a research diagnostic, not a trading signal. 视野对比是研究诊断工具，不是交易信号。</p>
  </div>
</details>

<div id="statsSection"></div>

<div id="scorecardSummarySection"></div>

<div id="paperSummarySection"></div>
<div id="regimeSummarySection"></div>
<div id="capLiqSummarySection"></div>

<div id="unifiedWorkflowSummarySection"></div>

<div id="caveatsSection"></div>

<div class="layout">
  <main>
    <div class="card" id="scoreboardCard" style="scroll-margin-top:12px">
      <h2>Factor Scoreboard 因子排行榜</h2>
      <div class="small">Click column headers to sort. 点击列头排序。Default sort: quality score descending (研究分诊分数，非交易建议). Best horizon metrics from diagnostics. 最优视野指标来自诊断摘要。</div>
      <div class="controls">
        <input type="text" id="search" placeholder="搜索因子 / Search factor...">
        <select id="familyFilter"><option value="">All families 全部家族</option></select>
        <select id="qualityFilter"><option value="">All quality 全部质量</option></select>
        <select id="horizonFilter"><option value="">All horizons 全部视野</option></select>
        <select id="scClassFilter"><option value="">All quality classes 全部质量分类</option></select>
        <select id="scConfFilter"><option value="">All confidence 全部置信度</option></select>
        <select id="paperViabFilter"><option value="">All paper viab. 纸面可行性</option></select>
        <select id="regimeFilter"><option value="">All regime dep. 市场状态依赖</option></select>
      </div>
      <div class="table-wrap">
        <table id="factorTable">
          <thead><tr>
            <th data-col="factor_id">Factor</th>
            <th data-col="name_zh">名称 Name</th>
            <th data-col="family_zh">Family 家族</th>
            <th data-col="final_quality_class">Quality Class 质量分类</th>
            <th data-col="final_quality_score">Score 分数</th>
            <th data-col="score_confidence">Confidence 置信度</th>
            <th data-col="metadata_quality">Meta Quality 元数据</th>
            <th data-col="best_horizon">Best H 最优视野</th>
            <th data-col="rankic_mean">RankIC</th>
            <th data-col="rankic_ir">ICIR</th>
            <th data-col="monthly_ic_positive_rate">IC Win% IC胜率</th>
            <th data-col="long_short_sharpe">Sharpe</th>
            <th data-col="long_short_annualized_return">Ann Ret 年化收益</th>
            <th data-col="long_short_max_drawdown">Max DD 最大回撤</th>
            <th data-col="long_short_positive_month_rate">LS Win% LS胜率</th>
            <th data-col="coverage_rate">Coverage 覆盖率</th>
            <th data-col="novelty_assessment">Novelty 新颖性</th>
            <th data-col="nearest_factor">Nearest 最近因子</th>
            <th data-col="strongest_redundancy_level">Redundancy 冗余</th>
            <th data-col="redundancy_confidence">Red Conf 冗余置信度</th>
            <th data-col="redundancy_cluster_id">Cluster 聚类</th>
            <th data-col="recommended_next_action">Main Action 建议动作</th>
            <th data-col="decision_bucket">Decision 决策</th>
            <th data-col="paper_viability_class">Paper Viab. 纸面可行性</th>
            <th data-col="cost_sensitivity_class">Cost Sens. 费用敏感</th>
            <th data-col="fee_10bps_total_return">10bps Ret 10bps收益</th>
            <th data-col="break_even_fee_bps">B/E Fee 盈亏平衡</th>
            <th data-col="paper_avg_turnover">Avg TO 平均换手</th>
            <th data-col="regime_dependency_class">Regime Dep. 状态依赖</th>
            <th data-col="paper_return_btc_beta">BTC Beta</th>
            <th data-col="paper_return_btc_corr">BTC Corr</th>
            <th data-col="bull_minus_bear_paper_return">Bull-Bear Δ</th>
            <th data-col="drawdown_minus_normal_paper_return">DD Fragility 回撤脆弱</th>
          </tr></thead>
          <tbody id="tableBody"></tbody>
        </table>
      </div>
    </div>
  </main>
  <aside class="detail">
    <div class="card" id="detailCard">
      <button class="back-to-table" onclick="document.getElementById('scoreboardCard').scrollIntoView({behavior:'smooth',block:'start'})">↑ 回到因子列表 / Back to table</button>
      <h2>Factor Detail 因子详情</h2>
      <div class="small">Select a factor from the table.<br>从表格中选择一个因子查看详情。</div>
    </div>
  </aside>
</div>

<div class="footer">
  <span id="genTime"></span>
  <a href="https://github.com/jerry0012009/momentum/tree/main/docs/factor_library/START_HERE.md">Start Here</a>
  <a href="https://github.com/jerry0012009/momentum/tree/main/docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md">Governance</a>
</div>

<script id="factorPayload" type="application/json">PAYLOAD_PLACEHOLDER</script>
<script>
// ── Data ──
const DATA = JSON.parse(document.getElementById('factorPayload').textContent);
const S = DATA.summary;
const factors = DATA.factors;
const byId = new Map(factors.map(f => [f.factor_id, f]));
const METRIC_GLOSSARY = DATA.metric_glossary || {};

// ── Quality label map ──
const QUALITY_LABELS = {
  COMPLETE: {zh:'完整', en:'COMPLETE', cls:'complete'},
  DIRECTION_AMBIGUOUS: {zh:'方向模糊', en:'DIRECTION_AMBIGUOUS', cls:'direction_ambiguous'},
  NEEDS_REVIEW: {zh:'需复核', en:'NEEDS_REVIEW', cls:'needs_review'},
  FORMULA_AMBIGUOUS: {zh:'公式模糊', en:'FORMULA_AMBIGUOUS', cls:'formula_ambiguous'}
};
const DIR_LABELS = {positive:'正向', negative:'负向', conditional:'条件式'};

// ── Scorecard label maps ──
const SC_CLASS_LABELS = {
  STRONG_RESEARCH_CANDIDATE: {zh:'强研究候选', en:'STRONG_RESEARCH_CANDIDATE', cls:'strong_research'},
  PROMISING_BUT_INCONSISTENT: {zh:'有前景但不一致', en:'PROMISING_BUT_INCONSISTENT', cls:'promising'},
  REVIEW_REQUIRED: {zh:'需复核', en:'REVIEW_REQUIRED', cls:'review_req'},
  DIRECTION_DEPENDENT: {zh:'方向依赖', en:'DIRECTION_DEPENDENT', cls:'other_class'},
  REDUNDANT_OR_WEAK: {zh:'冗余或弱', en:'REDUNDANT_OR_WEAK', cls:'other_class'},
  INSUFFICIENT_EVIDENCE: {zh:'证据不足', en:'INSUFFICIENT_EVIDENCE', cls:'other_class'}
};
const SC_CONF_LABELS = {
  HIGH: {zh:'高', cls:'high-conf'},
  MEDIUM: {zh:'中', cls:'medium-conf'},
  LOW: {zh:'低', cls:'low-conf'}
};
const SC_ACTION_LABELS = {
  KEEP_FOR_RESEARCH_REVIEW: {zh:'保留研究复核', en:'KEEP_FOR_RESEARCH_REVIEW'},
  REVIEW_FORMULA_OR_METADATA: {zh:'复核公式或元数据', en:'REVIEW_FORMULA_OR_METADATA'}
};
// PM-19: Novelty and redundancy level labels
const NOVELTY_LABELS = {
  HIGHLY_REDUNDANT: {zh:'高度冗余', en:'HIGHLY_REDUNDANT', cls:'needs_review'},
  MODERATELY_REDUNDANT: {zh:'中度冗余', en:'MODERATELY_REDUNDANT', cls:'direction_ambiguous'},
  LIKELY_DISTINCT: {zh:'可能独立', en:'LIKELY_DISTINCT', cls:'complete'},
  NEEDS_REVIEW: {zh:'需复核', en:'NEEDS_REVIEW', cls:'direction_ambiguous'},
  INSUFFICIENT_OVERLAP: {zh:'重叠不足', en:'INSUFFICIENT_OVERLAP', cls:'formula_ambiguous'}
};
const REDUNDANCY_LEVEL_LABELS = {
  NEAR_DUPLICATE: {zh:'近似重复', en:'NEAR_DUPLICATE', cls:'needs_review'},
  HIGH_REDUNDANCY: {zh:'高度冗余', en:'HIGH_REDUNDANCY', cls:'needs_review'},
  MODERATE_REDUNDANCY: {zh:'中度冗余', en:'MODERATE_REDUNDANCY', cls:'direction_ambiguous'},
  LOW_REDUNDANCY: {zh:'低冗余', en:'LOW_REDUNDANCY', cls:'complete'},
  INSUFFICIENT_OVERLAP: {zh:'重叠不足', en:'INSUFFICIENT_OVERLAP', cls:'formula_ambiguous'}
};

// Sub-score bilingual labels
const SUB_SCORE_LABELS = {
  computation_integrity_score: '计算完整性 Computation',
  predictive_ranking_score: '预测排名 Predictive',
  portfolio_extraction_score: '组合提取 Portfolio',
  stability_score: '稳定性 Stability',
  quantile_shape_score: '分位形状 Quantile',
  direction_interpretability_score: '方向可解释性 Direction',
  redundancy_novelty_score: '冗余新颖性 Redundancy'
};

// PM-22: Paper diagnostics labels
const PAPER_VIAB_LABELS = {
  PAPER_STRONG: {zh:'纸面强', en:'PAPER_STRONG', cls:'paper_strong'},
  PAPER_PROMISING: {zh:'纸面有前景', en:'PAPER_PROMISING', cls:'paper_promising'},
  PAPER_MIXED: {zh:'纸面混合', en:'PAPER_MIXED', cls:'paper_mixed'},
  PAPER_WEAK: {zh:'纸面弱', en:'PAPER_WEAK', cls:'paper_weak'},
  PAPER_REVIEW_REQUIRED: {zh:'纸面需复核', en:'PAPER_REVIEW_REQUIRED', cls:'paper_review'}
};
const COST_SENS_LABELS = {
  COST_ROBUST: {zh:'费用稳健', en:'COST_ROBUST', cls:'cost_robust'},
  COST_SENSITIVE: {zh:'费用敏感', en:'COST_SENSITIVE', cls:'cost_sensitive'},
  COST_COLLAPSED: {zh:'费用崩溃', en:'COST_COLLAPSED', cls:'cost_collapsed'},
  INSUFFICIENT_DATA: {zh:'数据不足', en:'INSUFFICIENT_DATA', cls:'cost_insufficient'}
};
function paperViabBadge(cls){
  const l=PAPER_VIAB_LABELS[cls]||{zh:cls||'—',en:cls||'—',cls:''};
  return `<span class="paper-badge ${l.cls}">${esc(l.zh)} / ${esc(l.en)}</span>`;
}
function costSensBadge(cls){
  const l=COST_SENS_LABELS[cls]||{zh:cls||'—',en:cls||'—',cls:''};
  return `<span class="paper-badge ${l.cls}">${esc(l.zh)} / ${esc(l.en)}</span>`;
}

// PM-24: Regime dependency labels
const REGIME_CLASS_LABELS = {
  REGIME_ROBUST: {zh:'跨市场稳健', en:'REGIME_ROBUST', cls:'REGIME_ROBUST'},
  BULL_DEPENDENT: {zh:'牛市依赖', en:'BULL_DEPENDENT', cls:'BULL_DEPENDENT'},
  BEAR_DEPENDENT: {zh:'熊市依赖', en:'BEAR_DEPENDENT', cls:'BEAR_DEPENDENT'},
  VOL_DEPENDENT: {zh:'波动率依赖', en:'VOL_DEPENDENT', cls:'VOL_DEPENDENT'},
  DRAWDOWN_FRAGILE: {zh:'回撤脆弱', en:'DRAWDOWN_FRAGILE', cls:'DRAWDOWN_FRAGILE'}
};
function regimeBadge(cls){
  const l=REGIME_CLASS_LABELS[cls]||{zh:cls||'—',en:cls||'—',cls:''};
  return `<span class="regime-badge ${l.cls}">${esc(l.zh)} / ${esc(l.en)}</span>`;
}

// PM-28: Shape / stability / decile label maps
const QUANTILE_SHAPE_LABELS = {
  EXCELLENT_MONOTONIC: {zh:'优秀单调',en:'EXCELLENT_MONOTONIC',cls:'EXCELLENT_MONOTONIC'},
  WEAK_MONOTONIC: {zh:'弱单调',en:'WEAK_MONOTONIC',cls:'WEAK_MONOTONIC'},
  NON_MONOTONIC: {zh:'非单调',en:'NON_MONOTONIC',cls:'NON_MONOTONIC'}
};
const STABILITY_CLASS_LABELS = {
  STABLE_POSITIVE: {zh:'稳定正向',en:'STABLE_POSITIVE',cls:'STABLE_POSITIVE'},
  STABLE_WEAK: {zh:'稳定偏弱',en:'STABLE_WEAK',cls:'STABLE_WEAK'},
  STABLE_NEGATIVE: {zh:'稳定负向',en:'STABLE_NEGATIVE',cls:'STABLE_NEGATIVE'},
  UNSTABLE: {zh:'不稳定',en:'UNSTABLE',cls:'UNSTABLE'}
};
const DECILE_SHAPE_LABELS = {
  DECILE_MONOTONIC_STRONG: {zh:'十分位强单调',en:'DECILE_MONOTONIC_STRONG',cls:'DECILE_MONOTONIC_STRONG'},
  DECILE_MONOTONIC_WEAK: {zh:'十分位弱单调',en:'DECILE_MONOTONIC_WEAK',cls:'DECILE_MONOTONIC_WEAK'},
  BOTH_TAILS_U_SHAPED: {zh:'U型双尾',en:'BOTH_TAILS_U_SHAPED',cls:'BOTH_TAILS_U_SHAPED'},
  NONLINEAR_MIXED: {zh:'非线性混合',en:'NONLINEAR_MIXED',cls:'NONLINEAR_MIXED'}
};
const SHAPE_CONSISTENCY_LABELS = {
  CONSISTENT: {zh:'一致',en:'CONSISTENT',cls:'CONSISTENT'},
  DECILE_REVEALS_NONLINEARITY: {zh:'十分位揭示非线性',en:'DECILE_REVEALS_NONLINEARITY',cls:'DECILE_REVEALS_NONLINEARITY'},
  DECILE_REVEALS_TAIL_EFFECT: {zh:'十分位揭示尾部效应',en:'DECILE_REVEALS_TAIL_EFFECT',cls:'DECILE_REVEALS_NONLINEARITY'}
};
const TAIL_CONC_LABELS = {
  TAIL_DOMINANT: {zh:'尾部主导',en:'TAIL_DOMINANT',cls:'TAIL_DOMINANT'},
  MODERATE: {zh:'中等',en:'MODERATE',cls:'MODERATE'}
};
const DIR_HANDLING_LABELS = {
  negative_flipped: {zh:'负向(已翻转)',en:'negative (flipped)',cls:''},
  positive_asis: {zh:'正向(保持)',en:'positive (as-is)',cls:''}
};
function shapeBadge(cls){
  const l=QUANTILE_SHAPE_LABELS[cls]||{zh:cls||'—',en:cls||'—',cls:''};
  return `<span class="shape-badge ${l.cls}">${esc(l.zh)} / ${esc(l.en)}</span>`;
}
function stabilityBadge(cls){
  const l=STABILITY_CLASS_LABELS[cls]||{zh:cls||'—',en:cls||'—',cls:''};
  return `<span class="shape-badge ${l.cls}">${esc(l.zh)} / ${esc(l.en)}</span>`;
}
function decileShapeBadge(cls){
  const l=DECILE_SHAPE_LABELS[cls]||{zh:cls||'—',en:cls||'—',cls:''};
  return `<span class="shape-badge ${l.cls}">${esc(l.zh)} / ${esc(l.en)}</span>`;
}
function shapeConsistencyBadge(cls){
  const l=SHAPE_CONSISTENCY_LABELS[cls]||{zh:cls||'—',en:cls||'—',cls:''};
  return `<span class="shape-badge ${l.cls}">${esc(l.zh)} / ${esc(l.en)}</span>`;
}
function tailConcBadge(cls){
  const l=TAIL_CONC_LABELS[cls]||{zh:cls||'—',en:cls||'—',cls:''};
  return `<span class="shape-badge ${l.cls}">${esc(l.zh)} / ${esc(l.en)}</span>`;
}

// PM-30: Capacity / liquidity label maps
const CAP_RISK_LABELS = {
  CAPACITY_FRIENDLY: {zh:'容量友好',en:'CAPACITY_FRIENDLY',cls:'CAPACITY_FRIENDLY'},
  MODERATE_CAPACITY_RISK: {zh:'中等容量风险',en:'MODERATE_CAPACITY_RISK',cls:'MODERATE_CAPACITY_RISK'},
  CAPACITY_FRAGILE: {zh:'容量脆弱',en:'CAPACITY_FRAGILE',cls:'CAPACITY_FRAGILE'}
};
const LIQ_RISK_LABELS = {
  LIQUIDITY_FRAGILE: {zh:'流动性脆弱',en:'LIQUIDITY_FRAGILE',cls:'LIQUIDITY_FRAGILE'},
  LIQUIDITY_ADEQUATE: {zh:'流动性充足',en:'LIQUIDITY_ADEQUATE',cls:'LIQUIDITY_ADEQUATE'}
};
const CAP_LIQ_CLASS_LABELS = {
  WATCH_LIQUIDITY: {zh:'关注流动性',en:'WATCH_LIQUIDITY',cls:'WATCH_LIQUIDITY'},
  WATCH_BOTH: {zh:'关注两者',en:'WATCH_BOTH',cls:'WATCH_BOTH'},
  CAPACITY_OK: {zh:'容量正常',en:'CAPACITY_OK',cls:'CAPACITY_OK'}
};
const VOL_CONC_LABELS = {
  DIVERSIFIED_LIQUIDITY: {zh:'分散流动性',en:'DIVERSIFIED_LIQUIDITY',cls:'DIVERSIFIED_LIQUIDITY'},
  CONCENTRATED_LIQUIDITY: {zh:'集中流动性',en:'CONCENTRATED_LIQUIDITY',cls:'CONCENTRATED_LIQUIDITY'}
};
const CROSS_FLAG_LABELS = {
  STABLE_BUT_TOO_ILLIQUID: {zh:'稳定但流动性不足',en:'STABLE_BUT_TOO_ILLIQUID',cls:'STABLE_BUT_TOO_ILLIQUID'}
};
function capBadge(cls,map){
  const l=map[cls]||{zh:cls||'—',en:cls||'—',cls:cls||''};
  return `<span class="cap-badge ${l.cls}">${esc(l.zh)} / ${esc(l.en)}</span>`;
}

// PM-33: Unified profile label maps
const PROFILE_CLASS_LABELS = {
  BROAD_WATCHLIST: {zh:'广泛观察',en:'BROAD_WATCHLIST',cls:'BROAD_WATCHLIST'},
  PROMISING_BUT_REGIME_DEPENDENT: {zh:'有前景但状态依赖',en:'PROMISING_BUT_REGIME_DEPENDENT',cls:'PROMISING_BUT_REGIME_DEPENDENT'},
  UNIQUE_BUT_WEAK: {zh:'独立但偏弱',en:'UNIQUE_BUT_WEAK',cls:'UNIQUE_BUT_WEAK'}
};
const WORKFLOW_READY_LABELS = {
  WORKFLOW_READY: {zh:'工作流就绪',en:'WORKFLOW_READY',cls:'WORKFLOW_READY'},
  WORKFLOW_NOT_READY: {zh:'工作流未就绪',en:'WORKFLOW_NOT_READY',cls:'WORKFLOW_NOT_READY'}
};
const EVIDENCE_STATUS_LABELS = {
  COMPLETE: {zh:'完整',en:'COMPLETE',cls:'COMPLETE'},
  COMPLETE_WITH_WARNINGS: {zh:'完整(有警告)',en:'COMPLETE_WITH_WARNINGS',cls:'COMPLETE_WITH_WARNINGS'},
  INCOMPLETE: {zh:'不完整',en:'INCOMPLETE',cls:'INCOMPLETE'}
};
const RESEARCH_ACTION_LABELS = {
  LOWER_PRIORITY_REVIEW: {zh:'降低优先级复核',en:'LOWER_PRIORITY_REVIEW'},
  WATCH_FOR_STABILITY_RISK: {zh:'关注稳定性风险',en:'WATCH_FOR_STABILITY_RISK'},
  WATCH_FOR_REGIME_DEPENDENCE: {zh:'关注状态依赖',en:'WATCH_FOR_REGIME_DEPENDENCE'},
  KEEP_AS_DIAGNOSTIC_PROBE: {zh:'保留为诊断探针',en:'KEEP_AS_DIAGNOSTIC_PROBE'}
};
function profileClassBadge(cls){
  const l=PROFILE_CLASS_LABELS[cls]||{zh:cls||'—',en:cls||'—',cls:''};
  return `<span class="profile-class-badge ${l.cls}">${esc(l.zh)} / ${esc(l.en)}</span>`;
}
function workflowReadyBadge(cls){
  const l=WORKFLOW_READY_LABELS[cls]||{zh:cls||'—',en:cls||'—',cls:''};
  return `<span class="workflow-ready-badge ${l.cls}">${esc(l.zh)} / ${esc(l.en)}</span>`;
}
function evidenceStatusBadge(cls){
  const l=EVIDENCE_STATUS_LABELS[cls]||{zh:cls||'—',en:cls||'—',cls:''};
  return `<span class="evidence-badge ${l.cls}">${esc(l.zh)} / ${esc(l.en)}</span>`;
}
function researchActionBadge(cls){
  const l=RESEARCH_ACTION_LABELS[cls]||{zh:cls||'—',en:cls||'—'};
  return `<span class="research-action-badge">${esc(l.zh)} / ${esc(l.en)}</span>`;
}
function evBlockBadge(label,pass){
  return `<span class="ev-block-badge ${pass?'ev-pass':'ev-miss'}">${esc(label)}: ${pass?'✓':'✗'}</span>`;
}

// ── PM-51: Enhanced Glossary & Tooltip + Click-expanded detail ──
// Backward compat: GLOSSARY now reads from METRIC_GLOSSARY (loaded from JSON)
const GLOSSARY = new Proxy(METRIC_GLOSSARY, {
  get(target, prop) {
    const g = target[prop];
    if (!g) return null;
    return { what: g.tooltip_zh, high: g.high_zh, warn: g.misread_zh, signal: g.signal !== 'NOT_A_SIGNAL' };
  }
});

// Signal status badge helper
function signalBadge(status) {
  const map = {
    'RESEARCH_DIAGNOSTIC_ONLY': {label:'📊 Evidence', cls:'guard-evidence', tip:'机器计算的历史证据'},
    'SUPPORTS_FACTOR_REVIEW': {label:'🔬 Diagnostic', cls:'guard-diagnostic', tip:'支持因子研究复核'},
    'REQUIRES_SIGNAL_LEVEL_VALIDATION': {label:'⚠️ Needs Validation', cls:'guard-validation', tip:'需要信号级验证'},
    'NOT_A_SIGNAL': {label:'🚫 Not a Signal', cls:'guard-notsignal', tip:'不是交易信号'}
  };
  const m = map[status] || map['NOT_A_SIGNAL'];
  return `<span class="guard-badge ${m.cls}" title="${m.tip}">${m.label}</span>`;
}

// Inference guardrail labels
const GUARD_LABELS = {
  evidence: '<span class="guard-badge guard-evidence">📊 Evidence</span>',
  interpretation: '<span class="guard-badge guard-interpretation">🔬 Interpretation</span>',
  inference: '<span class="guard-badge guard-inference">💡 Inference</span>',
  notsignal: '<span class="guard-badge guard-notsignal">🚫 Not a Signal</span>',
  needsval: '<span class="guard-badge guard-validation">⚠️ Requires Validation</span>'
};

// ── PM-52: Horizon Pattern Classification Labels ──
const HORIZON_PATTERN_LABELS = {
  HORIZON_CONSISTENT_POSITIVE: {zh:'视野一致正向',en:'HORIZON_CONSISTENT_POSITIVE',cls:'hz-consistent-pos',tip:'四个视野RankIC同向为正且至少两个显著'},
  HORIZON_CONSISTENT_NEGATIVE: {zh:'视野一致负向',en:'HORIZON_CONSISTENT_NEGATIVE',cls:'hz-consistent-neg',tip:'四个视野RankIC同向为负且至少两个显著'},
  SHORT_TERM_ONLY: {zh:'仅短期有效',en:'SHORT_TERM_ONLY',cls:'hz-short-only',tip:'仅1h/4h视野显著'},
  LONG_TERM_ONLY: {zh:'仅长期有效',en:'LONG_TERM_ONLY',cls:'hz-long-only',tip:'仅24h/72h视野显著'},
  HORIZON_REVERSAL: {zh:'视野反转',en:'HORIZON_REVERSAL',cls:'hz-reversal',tip:'短期与长期RankIC方向相反'},
  SINGLE_HORIZON_SPIKE: {zh:'单视野尖峰',en:'SINGLE_HORIZON_SPIKE',cls:'hz-spike',tip:'仅一个视野显著，其他接近零'},
  MIXED_WEAK: {zh:'混合偏弱',en:'MIXED_WEAK',cls:'hz-mixed',tip:'各视野信号弱或混乱'},
  INSUFFICIENT_HORIZON_DATA: {zh:'视野数据不足',en:'INSUFFICIENT_HORIZON_DATA',cls:'hz-insufficient',tip:'缺少视野数据'}
};
function horizonPatternBadge(pat) {
  const l = HORIZON_PATTERN_LABELS[pat];
  if (!l) return '';
  return `<span class="horizon-pattern-badge ${l.cls}" title="${esc(l.tip)}">${esc(l.zh)} / ${esc(l.en)}</span>`;
}

// ── PM-52: Horizon Switch Logic ──
function buildHorizonSwitch(f, containerId) {
  const hzs = ['1h','4h','24h','72h'];
  const bestHz = f.best_horizon;
  let html = '<div class="horizon-switch">';
  hzs.forEach(hz => {
    const isBest = hz === bestHz;
    const active = hz === bestHz ? 'active' : '';
    html += `<button class="horizon-btn ${active}" onclick="switchHorizon('${f.factor_id}','${hz}')">${hz}${isBest?'<span class="best-tag">Best</span>':''}</button>`;
  });
  html += '<span class="horizon-alt-label" id="hz-alt-label-'+f.factor_id+'"></span>';
  html += '</div>';
  return html;
}
function switchHorizon(fid, hz) {
  const f = DATA.factors.find(x => x.factor_id === fid);
  if (!f || !f.horizon_metrics) return;
  const hm = f.horizon_metrics[hz];
  if (!hm) return;
  // Update metric grid
  const grid = document.getElementById('hz-metrics-'+fid);
  if (grid) {
    grid.innerHTML = buildMetricGrid(hm);
  }
  // Update title
  const title = document.getElementById('hz-title-'+fid);
  if (title) {
    const isBest = hz === f.best_horizon;
    title.innerHTML = isBest
      ? `Best Horizon Metrics 最优视野指标 (${hz})`
      : `Horizon Metrics 视野指标 (${hz}) <span class="horizon-alt-label">Alternative Horizon / 对照视野</span>`;
  }
  // Update monthly IC chart
  const icChart = document.getElementById('hz-ic-chart-'+fid);
  if (icChart && f.horizon_monthly_ic && f.horizon_monthly_ic[hz]) {
    const icData = f.horizon_monthly_ic[hz];
    if (icData.length > 0) {
      icChart.innerHTML = svgLineChart(icData, 'rank_ic_adj', 600, 140);
    } else {
      icChart.innerHTML = '<div style="padding:12px;color:var(--muted);font-size:12px">No monthly IC data for this horizon.</div>';
    }
  }
  // Update monthly IC title
  const icTitle = document.getElementById('hz-ic-title-'+fid);
  if (icTitle) icTitle.textContent = `Monthly RankIC 月度RankIC (${hz})`;
  // Update monthly LS chart
  const lsChart = document.getElementById('hz-ls-chart-'+fid);
  if (lsChart && f.horizon_monthly_ls && f.horizon_monthly_ls[hz]) {
    const lsData = f.horizon_monthly_ls[hz];
    if (lsData.length > 0) {
      lsChart.innerHTML = svgBarChart(lsData, 'long_short_return', 600, 120);
    } else {
      lsChart.innerHTML = '<div style="padding:12px;color:var(--muted);font-size:12px">No monthly LS data for this horizon.</div>';
    }
  }
  const lsTitle = document.getElementById('hz-ls-title-'+fid);
  if (lsTitle) lsTitle.textContent = `Monthly Long-Short Return 月度多空收益 (${hz})`;
  // Update cumulative LS chart
  const cumChart = document.getElementById('hz-cum-chart-'+fid);
  if (cumChart && f.horizon_cumulative_ls && f.horizon_cumulative_ls[hz]) {
    const cumData = f.horizon_cumulative_ls[hz];
    if (cumData.length > 0) {
      cumChart.innerHTML = svgCumCurve(cumData, 600, 160);
    } else {
      cumChart.innerHTML = '<div style="padding:12px;color:var(--muted);font-size:12px">No cumulative LS data for this horizon.</div>';
    }
  }
  const cumTitle = document.getElementById('hz-cum-title-'+fid);
  if (cumTitle) cumTitle.textContent = `Cumulative Long-Short Curve 累计多空曲线 (${hz})`;
  // Update active button state
  const container = document.getElementById('hz-switch-'+fid);
  if (container) {
    container.querySelectorAll('.horizon-btn').forEach(btn => {
      btn.classList.toggle('active', btn.textContent.includes(hz));
    });
  }
}
function buildMetricGrid(hm) {
  const rows = [
    ['RankIC Mean', hm.rankic_mean, mcls(hm.rankic_mean)],
    ['RankIC Std', hm.rankic_std != null ? Number(hm.rankic_std).toFixed(4) : '—', ''],
    ['ICIR', hm.rankic_ir != null ? Number(hm.rankic_ir).toFixed(3) : '—', ''],
    ['IC t-stat', hm.rankic_t_stat != null ? Number(hm.rankic_t_stat).toFixed(2) : '—', ''],
    ['IC Win Rate', hm.monthly_ic_positive_rate != null ? (Number(hm.monthly_ic_positive_rate)*100).toFixed(1)+'%' : '—', ''],
    ['LS Mean', hm.long_short_mean != null ? (Number(hm.long_short_mean)>=0?'+':'')+Number(hm.long_short_mean).toFixed(6) : '—', ''],
    ['LS Std', hm.long_short_std != null ? Number(hm.long_short_std).toFixed(6) : '—', ''],
    ['LS Sharpe', hm.long_short_sharpe != null ? Number(hm.long_short_sharpe).toFixed(2) : '—', mcls(hm.long_short_sharpe,1.5,0.8)],
    ['Ann Return', hm.long_short_annualized_return != null ? (Number(hm.long_short_annualized_return)*100).toFixed(1)+'%' : '—', ''],
    ['Ann Vol', hm.long_short_annualized_vol != null ? (Number(hm.long_short_annualized_vol)*100).toFixed(1)+'%' : '—', ''],
    ['Max Drawdown', hm.long_short_max_drawdown != null ? (Number(hm.long_short_max_drawdown)*100).toFixed(1)+'%' : '—', ''],
    ['LS Win Rate', hm.long_short_positive_month_rate != null ? (Number(hm.long_short_positive_month_rate)*100).toFixed(1)+'%' : '—', ''],
    ['Coverage', hm.coverage_rate != null ? (Number(hm.coverage_rate)*100).toFixed(1)+'%' : '—', ''],
  ];
  return rows.map(([label, val, cls]) => {
    const v = val === null || val === undefined || val === '—' ? '—' : val;
    const c = cls || (v === '—' ? 'muted-c' : '');
    return `<div class="metric"><span>${renderTooltip(label)}</span><strong class="${c}">${v}</strong></div>`;
  }).join('');
}
function buildAllHorizonTable(f) {
  if (!f.horizon_metrics) return '';
  const hzs = ['1h','4h','24h','72h'];
  const bestHz = f.best_horizon;
  const expDir = f.expected_direction;
  let html = '<table class="horizon-summary-table"><thead><tr><th>Horizon</th><th>RankIC</th><th>t-stat</th><th>ICIR</th><th>IC Win%</th><th>LS Sharpe</th><th>Ann Ret</th><th>MaxDD</th><th>LS Win%</th><th>Coverage</th></tr></thead><tbody>';
  hzs.forEach(hz => {
    const hm = f.horizon_metrics[hz] || {};
    const isBest = hz === bestHz;
    const rowCls = isBest ? 'best-row' : '';
    // Check direction conflict
    const rankicMean = hm.rankic_mean;
    let conflict = false;
    if (rankicMean !== null && rankicMean !== undefined && expDir) {
      if (expDir === 'positive' && rankicMean < 0) conflict = true;
      if (expDir === 'negative' && rankicMean > 0) conflict = true;
    }
    // Check IC-LS tension: significant IC but weak LS
    const tStat = hm.rankic_t_stat;
    const lsSharpe = hm.long_short_sharpe;
    const tension = tStat !== null && tStat !== undefined && Math.abs(tStat) > 2.0 && (lsSharpe === null || lsSharpe === undefined || Math.abs(lsSharpe) < 0.8);
    const rankicCls = conflict ? 'conflict-cell' : '';
    const tensionCls = tension ? 'tension-cell' : '';
    html += `<tr class="${rowCls}">`;
    html += `<td>${hz}${conflict?' ⚠️':''}${tension?' ⚡':''}</td>`;
    html += `<td class="${rankicCls}">${hm.rankic_mean != null ? Number(hm.rankic_mean).toFixed(5) : '—'}</td>`;
    html += `<td>${hm.rankic_t_stat != null ? Number(hm.rankic_t_stat).toFixed(2) : '—'}</td>`;
    html += `<td>${hm.rankic_ir != null ? Number(hm.rankic_ir).toFixed(3) : '—'}</td>`;
    html += `<td>${hm.monthly_ic_positive_rate != null ? (Number(hm.monthly_ic_positive_rate)*100).toFixed(1)+'%' : '—'}</td>`;
    html += `<td class="${tensionCls}">${hm.long_short_sharpe != null ? Number(hm.long_short_sharpe).toFixed(2) : '—'}</td>`;
    html += `<td>${hm.long_short_annualized_return != null ? (Number(hm.long_short_annualized_return)*100).toFixed(1)+'%' : '—'}</td>`;
    html += `<td>${hm.long_short_max_drawdown != null ? (Number(hm.long_short_max_drawdown)*100).toFixed(1)+'%' : '—'}</td>`;
    html += `<td>${hm.long_short_positive_month_rate != null ? (Number(hm.long_short_positive_month_rate)*100).toFixed(1)+'%' : '—'}</td>`;
    html += `<td>${hm.coverage_rate != null ? (Number(hm.coverage_rate)*100).toFixed(1)+'%' : '—'}</td>`;
    html += '</tr>';
  });
  html += '</tbody></table>';
  html += '<div style="font-size:9px;color:var(--muted);margin:2px 0">⚠️ = direction conflicts with expected_direction | ⚡ = IC-LS tension (significant IC but weak LS) | ★ Best = best_horizon</div>';
  html += '<div style="font-size:9px;color:var(--muted)">Horizon comparison is a research diagnostic, not a trading signal. 视野对比是研究诊断，不是交易信号。</div>';
  return html;
}

// Global tooltip singleton (hover - brief)
const _tipDiv = document.createElement('div');
_tipDiv.className = 'tooltip-content';
document.body.appendChild(_tipDiv);

// Global expanded detail panel (click - full)
const _detailPanel = document.createElement('div');
_detailPanel.className = 'detail-panel';
_detailPanel.style.display = 'none';
document.body.appendChild(_detailPanel);
let _detailOpen = false;

function showTip(el, ev, term) {
  const g = METRIC_GLOSSARY[term]; if (!g) return;
  const signalHtml = signalBadge(g.signal);
  const benchHint = g.benchmark_zh ? `<div style="margin-top:6px;padding-top:6px;border-top:1px solid #334155;font-size:11px;color:#94a3b8"><strong style="color:#60a5fa">📏 参照:</strong> ${g.benchmark_zh.split('\n').filter(l=>l.startsWith('•')).slice(0,3).join('<br>')}</div>` : '';
  _tipDiv.innerHTML = `<strong>${term}</strong> ${signalHtml}<br>${g.tooltip_zh}${benchHint}<br><em style="color:#64748b;font-size:11px">点击展开详细解释 / Click for details</em>`;
  _tipDiv.style.visibility = 'visible'; _tipDiv.style.opacity = '1';
  moveTip(ev);
}
function moveTip(ev) {
  let x = ev.clientX + 12, y = ev.clientY + 12;
  const r = _tipDiv.getBoundingClientRect();
  if (x + 420 > window.innerWidth) x = ev.clientX - 430;
  if (y + r.height > window.innerHeight) y = ev.clientY - r.height - 12;
  _tipDiv.style.left = x + 'px'; _tipDiv.style.top = y + 'px';
}
function hideTip() { _tipDiv.style.visibility = 'hidden'; _tipDiv.style.opacity = '0'; }

function toggleDetail(term, ev) {
  ev.stopPropagation();
  if (_detailOpen && _detailPanel.dataset.term === term) {
    _detailPanel.style.display = 'none'; _detailOpen = false; return;
  }
  const g = METRIC_GLOSSARY[term]; if (!g) return;
  _detailPanel.dataset.term = term;
  const signalHtml = signalBadge(g.signal);
  const linked = (g.linked||[]).map(l => `<span class="detail-linked" onclick="toggleDetail('${l}',event)">${l}</span>`).join(' ');
  _detailPanel.innerHTML = `
    <div class="detail-header">
      <strong>${g.display_zh} / ${g.display_en}</strong> ${signalHtml}
      <span class="detail-close" onclick="_detailPanel.style.display='none';_detailOpen=false">✕</span>
    </div>
    <div class="detail-body">
      <div class="detail-section">
        <div class="detail-label">📖 它是什么 / What</div>
        <div>${g.tooltip_zh}<br><em style="color:#94a3b8">${g.tooltip_en}</em></div>
      </div>
      <div class="detail-section">
        <div class="detail-label">🔢 怎么算 / Formula</div>
        <div>${g.formula_zh}<br><em style="color:#94a3b8">${g.formula_en}</em></div>
      </div>
      <div class="detail-section">
        <div class="detail-label">📁 数据来源 / Source</div>
        <div><code>${g.source_file}</code> → <code>${g.source_columns}</code></div>
      </div>
      <div class="detail-section">
        <div class="detail-label">⬆️ 高值含义 / High = </div>
        <div>${g.high_zh}</div>
      </div>
      <div class="detail-section">
        <div class="detail-label">⬇️ 低值含义 / Low = </div>
        <div>${g.low_zh}</div>
      </div>
      ${g.benchmark_zh ? `<div class="detail-section">
        <div class="detail-label">📏 行业参照范围 / Industry Benchmarks</div>
        <div style="white-space:pre-line;font-size:12px;line-height:1.7;color:#cbd5e1">${g.benchmark_zh.replace(/\n/g,'<br>')}</div>
        ${g.benchmark_en ? `<div style="margin-top:6px;white-space:pre-line;font-size:11px;line-height:1.6;color:#94a3b8">${g.benchmark_en.replace(/\n/g,'<br>')}</div>` : ''}
      </div>` : ''}
      <div class="detail-section">
        <div class="detail-label">⚠️ 常见误读 / Misreading</div>
        <div class="detail-warn">${g.misread_zh}</div>
      </div>
      <div class="detail-section">
        <div class="detail-label">${GUARD_LABELS.inference} 可以推断 / Can Infer</div>
        <div>${g.infer_zh}</div>
      </div>
      <div class="detail-section">
        <div class="detail-label">${GUARD_LABELS.notsignal} 不能推断 / Cannot Infer</div>
        <div>${g.cannot_infer_zh}</div>
      </div>
      ${linked ? `<div class="detail-section"><div class="detail-label">🔗 关联指标 / Linked</div><div>${linked}</div></div>` : ''}
    </div>`;
  _detailPanel.style.display = 'block'; _detailOpen = true;
  // Position near click
  let x = Math.min(ev.clientX - 200, window.innerWidth - 440);
  let y = Math.min(ev.clientY + 10, window.innerHeight - _detailPanel.offsetHeight - 20);
  if (x < 10) x = 10; if (y < 10) y = 10;
  _detailPanel.style.left = x + 'px'; _detailPanel.style.top = y + 'px';
}

// Close detail panel on outside click
document.addEventListener('click', (e) => {
  if (_detailOpen && !_detailPanel.contains(e.target) && !e.target.closest('.tooltip-trigger')) {
    _detailPanel.style.display = 'none'; _detailOpen = false;
  }
});

function renderTooltip(term) {
  const g = METRIC_GLOSSARY[term];
  if (!g) return term;
  return `<span class="tooltip-trigger" onmouseenter="showTip(this,event,'${term}')" onmousemove="moveTip(event)" onmouseleave="hideTip()" onclick="toggleDetail('${term}',event)">${term}</span>`;
}

// Chart reading guide helper
function chartGuide(title, guide) {
  return `<details class="chart-guide"><summary>📖 How to read: ${title}</summary><div class="chart-guide-body">${guide}</div></details>`;
}

const CHART_GUIDES = {
  monthlyIC: chartGuide('Monthly RankIC', `
    <strong>看什么：</strong>每月IC值的走势和正负分布。<br>
    <strong>横轴：</strong>月份（2024-06 至 2026-06）。<br>
    <strong>纵轴：</strong>RankIC值（Spearman相关系数）。<br>
    <strong>上升：</strong>因子排序能力增强。<br>
    <strong>好：</strong>多数月份IC为正且稳定。<br>
    <strong>风险：</strong>IC大幅波动或持续为负。<br>
    ${GUARD_LABELS.evidence} 机器计算的历史IC，${GUARD_LABELS.notsignal} 不是交易信号。
  `),
  monthlyLS: chartGuide('Monthly Long-Short Return', `
    <strong>看什么：</strong>每月多空收益的正负和幅度。<br>
    <strong>横轴：</strong>月份。<br>
    <strong>纵轴：</strong>月度多空收益（%）。<br>
    <strong>上升：</strong>多空收益增加。<br>
    <strong>好：</strong>多数月份为正。<br>
    <strong>风险：</strong>大幅亏损月份。<br>
    ${GUARD_LABELS.evidence} 毛收益，未扣费。${GUARD_LABELS.notsignal} 不是可交易收益。
  `),
  cumLS: chartGuide('Cumulative Long-Short Curve', `
    <strong>看什么：</strong>累计收益的趋势和回撤。<br>
    <strong>横轴：</strong>月份。<br>
    <strong>纵轴：</strong>累计收益（%）。<br>
    <strong>上升：</strong>收益累积。<br>
    <strong>好：</strong>稳定上升，回撤小。<br>
    <strong>风险：</strong>大幅回撤或长期横盘。<br>
    ${GUARD_LABELS.evidence} 毛收益曲线。${GUARD_LABELS.inference} 可以判断收益趋势，但不能推断实盘表现。
  `),
  paperNav: chartGuide('Paper Portfolio NAV', `
    <strong>看什么：</strong>纸面组合净值走势，含不同费率。<br>
    <strong>横轴：</strong>月份。<br>
    <strong>纵轴：</strong>NAV（起始=1.0）。<br>
    <strong>上升：</strong>净值增长。<br>
    <strong>好：</strong>所有费率曲线都在1.0以上。<br>
    <strong>风险：</strong>10bps/20bps曲线大幅低于0bps。<br>
    ${GUARD_LABELS.evidence} 纸面净值，${GUARD_LABELS.notsignal} 不是实盘净值。
  `),
  feeSensitivity: chartGuide('Fee Sensitivity', `
    <strong>看什么：</strong>不同费率下的累计收益。<br>
    <strong>横轴：</strong>手续费（bps）。<br>
    <strong>纵轴：</strong>累计收益。<br>
    <strong>下降快：</strong>费用敏感。<br>
    <strong>好：</strong>曲线平缓（COST_ROBUST）。<br>
    <strong>风险：</strong>在合理费率下（5-10bps）收益为负。<br>
    ${GUARD_LABELS.evidence} 历史费率敏感度。${GUARD_LABELS.inference} 可以判断成本容忍度，但不含滑点。
  `),
  turnover: chartGuide('Monthly Turnover', `
    <strong>看什么：</strong>月度换手率走势。<br>
    <strong>横轴：</strong>月份。<br>
    <strong>纵轴：</strong>换手率。<br>
    <strong>高：</strong>交易频繁，成本高。<br>
    <strong>好：</strong>换手率稳定且低。<br>
    <strong>风险：</strong>换手率突然飙升。<br>
    ${GUARD_LABELS.evidence} 历史换手率。${GUARD_LABELS.inference} 可以估算成本，但不能推断滑点。
  `),
  regimeIC: chartGuide('Regime: IC by Market State', `
    <strong>看什么：</strong>不同市场状态下IC的差异。<br>
    <strong>横轴：</strong>市场状态（牛/熊/横盘，高/低波动）。<br>
    <strong>纵轴：</strong>IC均值。<br>
    <strong>差异大：</strong>因子依赖市场环境。<br>
    <strong>好：</strong>各状态下IC都为正（REGIME_ROBUST）。<br>
    <strong>风险：</strong>仅在特定状态下有效。<br>
    ${GUARD_LABELS.evidence} 历史状态IC。${GUARD_LABELS.inference} 可以判断适用范围，但不能推断未来状态。
  `),
  regimeLS: chartGuide('Regime: LS by Market State', `
    <strong>看什么：</strong>不同市场状态下多空收益的差异。<br>
    <strong>横轴：</strong>市场状态。<br>
    <strong>纵轴：</strong>多空收益均值。<br>
    <strong>差异大：</strong>策略依赖市场环境。<br>
    <strong>好：</strong>各状态下都盈利。<br>
    <strong>风险：</strong>熊市大幅亏损。<br>
    ${GUARD_LABELS.evidence} 历史状态收益。${GUARD_LABELS.notsignal} 不是交易建议。
  `),
  regimePaper: chartGuide('Regime: Paper Return by State', `
    <strong>看什么：</strong>不同市场状态下纸面收益。<br>
    <strong>横轴：</strong>市场状态。<br>
    <strong>纵轴：</strong>纸面月均收益。<br>
    <strong>差异大：</strong>策略依赖市场环境。<br>
    <strong>好：</strong>各状态下都盈利。<br>
    <strong>风险：</strong>深度回撤期大幅亏损。<br>
    ${GUARD_LABELS.evidence} 历史纸面收益。${GUARD_LABELS.notsignal} 不是实盘收益。
  `),
  quantileShape: chartGuide('Q1-Q5 Quantile Shape', `
    <strong>看什么：</strong>5个分位组的收益分布。<br>
    <strong>横轴：</strong>分位组（Q1=最低，Q5=最高）。<br>
    <strong>纵轴：</strong>月均收益。<br>
    <strong>单调递增：</strong>因子值越高收益越高（MONOTONIC_GOOD）。<br>
    <strong>好：</strong>单调且Spread大。<br>
    <strong>风险：</strong>U型或无规律。<br>
    ${GUARD_LABELS.evidence} 历史分位收益。${GUARD_LABELS.inference} 可以判断分层能力，但不能推断未来分层。
  `),
  decileShape: chartGuide('D1-D10 Decile Shape', `
    <strong>看什么：</strong>10个十分位组的收益分布。<br>
    <strong>横轴：</strong>十分位（D1=最低，D10=最高）。<br>
    <strong>纵轴：</strong>月均收益。<br>
    <strong>单调递增：</strong>因子分层能力强。<br>
    <strong>好：</strong>单调且尾部收益高。<br>
    <strong>风险：</strong>仅尾部有效（TAIL_DOMINATED）。<br>
    ${GUARD_LABELS.evidence} 历史十分位收益。${GUARD_LABELS.inference} 可以判断细粒度分层，但噪声更大。
  `)
};

function renderRedFlags(flags) {
  if (!flags || !flags.length) return '';
  return flags.map(f => `<span class="rf-badge rf-${f}">${f.replace(/_/g, ' ')}</span>`).join('');
}

function renderPM49Interpretation(f) {
  if (!f.pm49_research_decision) return '';
  const dirClass = f.pm49_direction_status === 'DIRECTION_ALIGNED' ? 'pm49-direction-aligned' :
                   f.pm49_direction_status === 'EXPECTED_DIRECTION_CONFLICT' ? 'pm49-direction-conflict' :
                   f.pm49_direction_status === 'SHORT_HORIZON_REVERSAL' ? 'pm49-direction-reversal' : '';
  return `
    <div class="judgment-section">
      <div class="judgment-label">🔬 Research Interpretation (PM-49 Judgment — 非交易信号)</div>
      <div style="margin:6px 0">${renderRedFlags(f.pm49_red_flags)}</div>
      <div style="margin:4px 0"><strong>Research Decision:</strong> <span class="pm49-badge pm49-decision">${f.pm49_research_decision}</span></div>
      <div style="margin:4px 0"><strong>Direction Status:</strong> <span class="pm49-badge ${dirClass}">${f.pm49_direction_status}</span></div>
      <div style="margin:4px 0"><strong>Issue:</strong> ${esc(f.pm49_main_issue_zh)}</div>
      <div style="margin:4px 0"><strong>Suggested Action:</strong> ${esc(f.pm49_suggested_action_zh)}</div>
      <div class="pm49-not-signal" style="margin-top:8px">⚠️ 以上为研究判断，不是交易信号。Factor evaluation indicates... requires further signal-level validation.</div>
    </div>`;
}

// ── Helpers ──
function esc(v){return String(v??'').replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function num(v,d=4,signed=true){if(v===null||v===undefined||Number.isNaN(v))return '—';const s=signed&&v>=0?'+':'';return s+Number(v).toFixed(d)}
function pct(v){if(v===null||v===undefined||Number.isNaN(v))return '—';return(Number(v)*100).toFixed(1)+'%'}
function mcls(v,strong=0.03,watch=0.02){if(v===null||v===undefined||Number.isNaN(v))return 'muted-c';const a=Math.abs(Number(v));return a>=strong?'strong':a>=watch?'watch':'plain'}
function qualBadge(q){
  const l=QUALITY_LABELS[q]||{zh:q,en:q,cls:''};
  return `<span class="quality-badge ${l.cls}">${esc(l.zh)} / ${esc(l.en)}</span>`;
}
function dirBadge(d){
  const lbl=DIR_LABELS[d]||d;
  const cls=d==='positive'?'positive':d==='negative'?'negative':'conditional';
  return `<span class="dir-badge ${cls}">${esc(lbl)} / ${esc(d)}</span>`;
}
function scClassBadge(cls){
  const l=SC_CLASS_LABELS[cls]||{zh:cls,en:cls,cls:'other_class'};
  return `<span class="sc-class-badge ${l.cls}">${esc(l.zh)} / ${esc(l.en)}</span>`;
}
function scConfBadge(conf){
  const l=SC_CONF_LABELS[conf]||{zh:conf,cls:''};
  return `<span class="sc-confidence-badge ${l.cls}">${esc(l.zh)} / ${esc(conf)}</span>`;
}
function scActionBadge(action){
  const l=SC_ACTION_LABELS[action]||{zh:action,en:action};
  return `<span class="sc-action-badge">${esc(l.zh)} / ${esc(l.en)}</span>`;
}
function noveltyBadge(nov){
  const l=NOVELTY_LABELS[nov]||{zh:nov,en:nov,cls:''};
  return `<span class="quality-badge ${l.cls}">${esc(l.zh)} / ${esc(l.en)}</span>`;
}
function redundancyLevelBadge(lev){
  const l=REDUNDANCY_LEVEL_LABELS[lev]||{zh:lev,en:lev,cls:''};
  return `<span class="quality-badge ${l.cls}">${esc(l.zh)} / ${esc(l.en)}</span>`;
}
function scBarColor(v){if(v===null||v===undefined)return 'sc-red';return v>=70?'sc-green':v>=40?'sc-yellow':'sc-red'}
function scScoreBar(score,label){
  if(score===null||score===undefined)return '';
  const w=Math.max(2,Math.min(100,Number(score)));
  const c=scBarColor(score);
  return `<div class="sc-score-bar">
    <div style="font-size:10px;color:var(--muted);margin-bottom:2px">${esc(label)}</div>
    <div class="sc-score-bar-track"><div class="sc-score-bar-fill ${c}" style="width:${w}%">${Number(score).toFixed(1)}</div></div>
  </div>`;
}
function scSubBar(key,score){
  if(score===null||score===undefined)return '';
  const w=Math.max(2,Math.min(100,Number(score)));
  const c=scBarColor(score);
  const label=SUB_SCORE_LABELS[key]||key;
  return `<div class="sc-bar-wrap">
    <span class="sc-bar-label" title="${esc(label)}">${esc(label)}</span>
    <div class="sc-bar-track"><div class="sc-bar-fill ${c}" style="width:${w}%">${Number(score).toFixed(0)}</div></div>
  </div>`;
}

// ── Stats section ──
(function(){
  const el=document.getElementById('statsSection');
  const qc=S.quality_counts||{};
  const qcHtml=Object.entries(qc).map(([k,v])=>`<div class="quality-badge ${(QUALITY_LABELS[k]||{cls:''}).cls}" style="font-size:11px;padding:4px 10px"><strong>${v}</strong> ${esc((QUALITY_LABELS[k]||{zh:k,en:k}).zh)} / ${esc((QUALITY_LABELS[k]||{zh:k,en:k}).en)}</div>`).join('');
  el.innerHTML=`
    <div class="stats">
      <div class="stat"><strong>${S.factor_count}</strong><span>Factors 因子数</span></div>
      <div class="stat"><strong>${S.horizons.join(' / ')}</strong><span>Horizons 视野</span></div>
      <div class="stat"><strong>${S.month_count}</strong><span>Months covered 月份数</span></div>
    </div>
    <div class="quality-grid">${qcHtml}</div>
  `;
})();

// ── Scorecard summary section ──
(function(){
  const el=document.getElementById('scorecardSummarySection');
  const cc=S.scorecard_class_counts||{};
  const conf=S.scorecard_confidence_counts||{};
  const strong=cc.STRONG_RESEARCH_CANDIDATE||0;
  const review=cc.REVIEW_REQUIRED||0;
  const promising=cc.PROMISING_BUT_INCONSISTENT||0;
  const high=conf.HIGH||0;
  const med=conf.MEDIUM||0;
  const low=conf.LOW||0;

  // PM-19: Redundancy stats
  const redLevel=S.scorecard_red_level_counts||{};
  const nearDup=redLevel.NEAR_DUPLICATE||0;
  const highRed=redLevel.HIGH_REDUNDANCY||0;
  const clusters=S.cluster_count||0;
  const largestCluster=S.largest_cluster_size||0;

  el.innerHTML=`
    <h2 style="margin-bottom:6px">Factor Quality Scorecard Summary 因子质量记分卡概要</h2>
    <div class="sc-summary-grid">
      <div class="sc-summary-card"><strong style="color:var(--green)">${strong}</strong><span>Strong Research Candidates<br>强研究候选</span></div>
      <div class="sc-summary-card"><strong style="color:var(--amber)">${promising}</strong><span>Promising But Inconsistent<br>有前景但不一致</span></div>
      <div class="sc-summary-card"><strong style="color:var(--red)">${review}</strong><span>Review Required<br>需复核</span></div>
      <div class="sc-summary-card"><strong style="color:var(--green)">${high}</strong><span>High Confidence<br>高置信度</span></div>
      <div class="sc-summary-card"><strong style="color:var(--amber)">${med}</strong><span>Medium Confidence<br>中置信度</span></div>
      <div class="sc-summary-card"><strong style="color:var(--red)">${low}</strong><span>Low Confidence<br>低置信度</span></div>
      <div class="sc-summary-card"><strong style="color:var(--red)">${nearDup}</strong><span>Near-Duplicate Pairs<br>近似重复对</span></div>
      <div class="sc-summary-card"><strong style="color:var(--amber)">${highRed}</strong><span>High-Redundancy Pairs<br>高度冗余对</span></div>
      <div class="sc-summary-card"><strong style="color:var(--green)">${clusters}</strong><span>Redundancy Clusters<br>冗余聚类</span></div>
      <div class="sc-summary-card"><strong style="color:var(--amber)">${largestCluster}</strong><span>Largest Cluster<br>最大聚类</span></div>
    </div>
    <div class="sc-caveat">
      <strong>⚠ 冗余矩阵已扩展至 2485/2485 对（PM-18）。置信度基于有效对覆盖率。</strong><br>
      <span style="color:var(--muted)">Redundancy matrix expanded to 2485/2485 pairs (PM-18). Confidence based on valid-pair coverage.</span>
    </div>
  `;
})();

// ── PM-22: Paper diagnostics summary section ──
(function(){
  const el=document.getElementById('paperSummarySection');
  const pvc=S.paper_viability_counts||{};
  const csc=S.cost_sensitivity_counts||{};
  const strong=pvc.PAPER_STRONG||0;
  const promising=pvc.PAPER_PROMISING||0;
  const mixed=pvc.PAPER_MIXED||0;
  const weak=pvc.PAPER_WEAK||0;
  const review=pvc.PAPER_REVIEW_REQUIRED||0;
  const robust=csc.COST_ROBUST||0;
  const sensitive=csc.COST_SENSITIVE||0;
  const collapsed=csc.COST_COLLAPSED||0;

  el.innerHTML=`
    <h2 style="margin-bottom:6px">Single-Factor Paper Portfolio Summary 单因子纸面组合概要</h2>
    <div class="sc-summary-grid">
      <div class="sc-summary-card"><strong style="color:var(--green)">${strong}</strong><span>Paper Strong<br>纸面强</span></div>
      <div class="sc-summary-card"><strong style="color:var(--amber)">${promising}</strong><span>Paper Promising<br>纸面有前景</span></div>
      <div class="sc-summary-card"><strong style="color:var(--red)">${mixed}</strong><span>Paper Mixed<br>纸面混合</span></div>
      <div class="sc-summary-card"><strong style="color:#dc2626">${weak}</strong><span>Paper Weak<br>纸面弱</span></div>
      <div class="sc-summary-card"><strong style="color:#a855f7">${review}</strong><span>Review Required<br>需复核</span></div>
      <div class="sc-summary-card"><strong style="color:var(--green)">${robust}</strong><span>Cost Robust<br>费用稳健</span></div>
      <div class="sc-summary-card"><strong style="color:var(--amber)">${sensitive}</strong><span>Cost Sensitive<br>费用敏感</span></div>
      <div class="sc-summary-card"><strong style="color:var(--red)">${collapsed}</strong><span>Cost Collapsed<br>费用崩溃</span></div>
    </div>
    <div class="paper-caveat">
      <strong>⚠ 单因子纸面组合仅为研究诊断 / Single-factor paper portfolio is a research diagnostic only</strong><br>
      <span style="color:var(--muted)">Equal-weight long/short at 1h horizon. No slippage/order book. Not a backtest. Not a strategy.<br>
      等权多空，1h视野，无滑点/订单簿。不是回测。不是交易策略。</span>
    </div>
  `;
})();

// ── PM-24: Regime summary section ──
(function(){
  const el=document.getElementById('regimeSummarySection');
  const rc=S.regime_class_counts||{};
  const rd=S.regime_distributions||{};
  const trend=rd.trend||{};
  const vol=rd.volatility||{};
  const dd=rd.drawdown||{};
  const robust=rc.REGIME_ROBUST||0;
  const bullDep=rc.BULL_DEPENDENT||0;
  const bearDep=rc.BEAR_DEPENDENT||0;
  const volDep=rc.VOL_DEPENDENT||0;
  const ddFrag=rc.DRAWDOWN_FRAGILE||0;
  const monthRange=S.regime_month_range||[];
  const nMonths=S.regime_n_months||0;
  el.innerHTML=`
    <h2 style="margin-bottom:6px">BTC / Market Regime Diagnostics Summary · BTC / 市场状态诊断概要</h2>
    <div class="sc-summary-grid">
      <div class="sc-summary-card"><strong style="color:var(--green)">${robust}</strong><span>Regime Robust<br>跨市场稳健</span></div>
      <div class="sc-summary-card"><strong style="color:var(--amber)">${bullDep}</strong><span>Bull Dependent<br>牛市依赖</span></div>
      <div class="sc-summary-card"><strong style="color:var(--red)">${bearDep}</strong><span>Bear Dependent<br>熊市依赖</span></div>
      <div class="sc-summary-card"><strong style="color:#a855f7">${volDep}</strong><span>Vol Dependent<br>波动率依赖</span></div>
      <div class="sc-summary-card"><strong style="color:#dc2626">${ddFrag}</strong><span>DD Fragile<br>回撤脆弱</span></div>
    </div>
    <div style="margin:8px 0;font-size:11px;color:var(--muted)">
      <strong>BTC Regime Coverage 市场状态覆盖:</strong>
      BULL ${trend.BULL||0} / BEAR ${trend.BEAR||0} / SIDEWAYS ${trend.SIDEWAYS||0} ·
      HIGH_VOL ${vol.HIGH_VOL||0} / LOW_VOL ${vol.LOW_VOL||0} ·
      NORMAL ${dd.NORMAL||0} / DEEP_DRAWDOWN ${dd.DEEP_DRAWDOWN||0}
      <span style="margin-left:8px">${monthRange.length?monthRange[0]+' → '+monthRange[1]:''} (${nMonths} months)</span>
    </div>
    <div class="regime-caveat">
      <strong>⚠ Regime diagnostics identify conditional behavior, not trade rules / 市场状态诊断识别条件行为，非交易规则</strong><br>
      <span style="color:var(--muted)">Regime labels are ex-post classifications of BTC market conditions. They show how factor returns vary with market state, but do not predict future regime transitions or constitute timing signals.<br>
      市场状态标签是事后分类。展示因子收益如何随市场状态变化，但不预测未来状态转换或构成择时信号。</span>
    </div>
  `;
})();

// ── PM-30: Capacity / liquidity summary section ──
(function(){
  const el=document.getElementById('capLiqSummarySection');
  if(!el)return;
  const clc=S.cap_liq_class_counts||{};
  const crr=clc.CAPACITY_FRIENDLY||0;
  const cmr=clc.MODERATE_CAPACITY_RISK||0;
  const cfr=clc.CAPACITY_FRAGILE||0;
  const lfr=clc.LIQUIDITY_FRAGILE||0;
  const wcl=clc.WATCH_LIQUIDITY||0;
  const wcb=clc.WATCH_BOTH||0;
  const illq=clc.STABLE_BUT_TOO_ILLIQUID||0;
  el.innerHTML=`
    <h2 style="margin-bottom:6px">Capacity / Liquidity Proxy Summary · 容量 / 流动性代理概要</h2>
    <div class="sc-summary-grid">
      <div class="sc-summary-card"><strong style="color:var(--green)">${crr}</strong><span>Capacity Friendly<br>容量友好</span></div>
      <div class="sc-summary-card"><strong style="color:var(--amber)">${cmr}</strong><span>Moderate Cap Risk<br>中等容量风险</span></div>
      <div class="sc-summary-card"><strong style="color:var(--red)">${cfr}</strong><span>Capacity Fragile<br>容量脆弱</span></div>
      <div class="sc-summary-card"><strong style="color:var(--red)">${lfr}</strong><span>Liquidity Fragile<br>流动性脆弱</span></div>
      <div class="sc-summary-card"><strong style="color:var(--amber)">${wcl}</strong><span>Watch Liquidity<br>关注流动性</span></div>
      <div class="sc-summary-card"><strong style="color:var(--red)">${wcb}</strong><span>Watch Both<br>关注两者</span></div>
      <div class="sc-summary-card"><strong style="color:#dc2626">${illq}</strong><span>Stable but Illiquid<br>稳定但流动性不足</span></div>
    </div>
    <div class="cap-caveat">
      <strong>⚠ Selected-basket proxy warning · 选中篮子代理警告</strong><br>
      <span style="color:var(--muted)">These are capacity/liquidity proxies based on selected-basket volume and turnover. They are not order-book simulation, slippage estimates, or real execution capacity.<br>
      这些是基于选中篮子成交量与换手率的容量 / 流动性代理指标，不是订单簿模拟、滑点估计或真实可交易容量结论。</span>
    </div>
  `;
})();

// ── PM-33: Unified Factor Evaluation Workflow summary section ──
(function(){
  const el=document.getElementById('unifiedWorkflowSummarySection');
  if(!el)return;
  const wv=S.workflow_version||'';
  const nstg=S.number_of_stages||0;
  const esd=S.evidence_status_distribution||{};
  const wrc=S.workflow_ready_counts||{};
  const pcc=S.profile_class_counts||{};
  const rac=S.recommended_action_counts||{};
  const mcr=S.mean_completeness_rate||0;
  const cw=S.component_weights||{};
  const sa=S.profile_manifest_source_artifacts||[];

  const esdHtml=Object.entries(esd).map(([k,v])=>{
    const l=EVIDENCE_STATUS_LABELS[k]||{zh:k,cls:''};
    return `<div class="sc-summary-card"><strong style="color:${k==='COMPLETE'?'var(--green)':'var(--amber)'}">${v}</strong><span>${esc(l.zh)}<br>${esc(k)}</span></div>`;
  }).join('');
  const wrcHtml=Object.entries(wrc).map(([k,v])=>{
    const l=WORKFLOW_READY_LABELS[k]||{zh:k,cls:''};
    return `<div class="sc-summary-card"><strong style="color:var(--green)">${v}</strong><span>${esc(l.zh)}<br>${esc(k)}</span></div>`;
  }).join('');
  const pccHtml=Object.entries(pcc).map(([k,v])=>{
    const l=PROFILE_CLASS_LABELS[k]||{zh:k,cls:''};
    const c=k==='BROAD_WATCHLIST'?'var(--muted)':k==='PROMISING_BUT_REGIME_DEPENDENT'?'var(--amber)':'var(--red)';
    return `<div class="sc-summary-card"><strong style="color:${c}">${v}</strong><span>${esc(l.zh)}<br>${esc(k)}</span></div>`;
  }).join('');
  const racHtml=Object.entries(rac).map(([k,v])=>{
    const l=RESEARCH_ACTION_LABELS[k]||{zh:k};
    return `<div class="sc-summary-card"><strong>${v}</strong><span>${esc(l.zh)}<br>${esc(k)}</span></div>`;
  }).join('');

  el.innerHTML=`
    <h2 style="margin-bottom:6px">Unified Factor Evaluation Workflow / 统一因子评价工作流</h2>
    <div class="stats">
      <div class="stat"><strong>${esc(wv)}</strong><span>Workflow Version 工作流版本</span></div>
      <div class="stat"><strong>${nstg}</strong><span>Stages 阶段数</span></div>
      <div class="stat"><strong>${(mcr*100).toFixed(0)}%</strong><span>Mean Evidence Completeness 平均证据完整率</span></div>
      <div class="stat"><strong>${sa.length}</strong><span>Source Artifacts 源工件数</span></div>
    </div>
    <h3 style="margin:10px 0 4px">Evidence Status Distribution 证据状态分布</h3>
    <div class="sc-summary-grid">${esdHtml}</div>
    <h3 style="margin:10px 0 4px">Workflow Ready Status 工作流就绪状态</h3>
    <div class="sc-summary-grid">${wrcHtml}</div>
    <h3 style="margin:10px 0 4px">Profile Class Distribution 画像分类分布</h3>
    <div class="sc-summary-grid">${pccHtml}</div>
    <h3 style="margin:10px 0 4px">Recommended Research Action Distribution 建议研究动作分布</h3>
    <div class="sc-summary-grid">${racHtml}</div>
    <h3 style="margin:10px 0 4px">Component Weights 组件权重</h3>
    <div style="display:flex;gap:4px;flex-wrap:wrap;font-size:10px">
      ${Object.entries(cw).map(([k,v])=>`<span class="bucket-badge">${esc(k)}: ${(v*100).toFixed(0)}%</span>`).join(' ')}
    </div>
    <div class="up-caveat">
      <strong>⚠ Unified profiles are research diagnostics. They summarize evidence; they do not select signals, construct portfolios, or recommend trading.</strong><br>
      <span style="color:var(--muted)">统一因子画像是研究性诊断汇总，用于整理证据；它不选择信号、不构建组合，也不构成交易建议。不是交易策略。</span>
    </div>
  `;
})();

// ── Interpretation caveats section ──
(function(){
  const el=document.getElementById('caveatsSection');
  el.innerHTML=`
    <div class="sc-caveat" style="margin-top:6px">
      <strong>Scorecard Interpretation 记分卡解读</strong><br>
      <div style="margin-top:6px">
        <span class="sc-class-badge strong_research" style="font-size:9px">STRONG_RESEARCH_CANDIDATE</span> = 强研究证据，<strong>不是</strong>可部署策略 / strong research evidence, <strong>NOT</strong> a deployable strategy<br>
        <span class="sc-class-badge promising" style="font-size:9px">PROMISING_BUT_INCONSISTENT</span> = 有意义但混合的证据 / meaningful evidence but mixed<br>
        <span class="sc-class-badge review_req" style="font-size:9px">REVIEW_REQUIRED</span> = 需在质量判断前复核 / needs review before quality judgment<br><br>
        <span style="color:var(--muted)">Score confidence may be capped by sparse redundancy confidence / 分数置信度可能因冗余置信度稀疏而受限 / redundancy confidence coverage</span><br>
        <strong style="color:#e9d5ff">本记分卡为研究分诊工具，不是交易建议 / This scorecard is a research triage tool, not a trading recommendation</strong>
      </div>
    </div>
  `;
})();

// ── Populate filters ──
const families=[...new Set(factors.map(f=>f.family_zh||f.family))].sort();
const qualities=[...new Set(factors.map(f=>f.metadata_quality))].sort();
const scClasses=[...new Set(factors.map(f=>f.final_quality_class).filter(Boolean))].sort();
const scConfs=['HIGH','MEDIUM','LOW'];
const familyFilter=document.getElementById('familyFilter');
const qualityFilter=document.getElementById('qualityFilter');
const horizonFilter=document.getElementById('horizonFilter');
const scClassFilter=document.getElementById('scClassFilter');
const scConfFilter=document.getElementById('scConfFilter');
families.forEach(f=>{const o=document.createElement('option');o.value=f;o.textContent=f;familyFilter.appendChild(o)});
qualities.forEach(q=>{const o=document.createElement('option');o.value=q;o.textContent=(QUALITY_LABELS[q]||{zh:q}).zh+' / '+q;qualityFilter.appendChild(o)});
S.horizons.forEach(h=>{const o=document.createElement('option');o.value=h;o.textContent=h;horizonFilter.appendChild(o)});
scClasses.forEach(c=>{const o=document.createElement('option');o.value=c;o.textContent=(SC_CLASS_LABELS[c]||{zh:c}).zh+' / '+c;scClassFilter.appendChild(o)});
scConfs.forEach(c=>{const o=document.createElement('option');o.value=c;o.textContent=(SC_CONF_LABELS[c]||{zh:c}).zh+' / '+c;scConfFilter.appendChild(o)});
// PM-22: Paper viability filter
const paperViabFilter=document.getElementById('paperViabFilter');
const paperViabs=[...new Set(factors.map(f=>f.paper_viability_class).filter(Boolean))].sort();
paperViabs.forEach(p=>{const o=document.createElement('option');o.value=p;o.textContent=(PAPER_VIAB_LABELS[p]||{zh:p}).zh+' / '+p;paperViabFilter.appendChild(o)});
// PM-24: Regime dependency filter
const regimeFilter=document.getElementById('regimeFilter');
const regimeClasses=[...new Set(factors.map(f=>f.regime_dependency_class).filter(Boolean))].sort();
regimeClasses.forEach(r=>{const o=document.createElement('option');o.value=r;o.textContent=(REGIME_CLASS_LABELS[r]||{zh:r}).zh+' / '+r;regimeFilter.appendChild(o)});

// ── Sort state (default: final_quality_score descending) ──
let sortCol='final_quality_score';
let sortDir=-1; // -1=desc

// ── Render table ──
function renderTable(){
  const q=document.getElementById('search').value.toLowerCase();
  const fam=familyFilter.value;
  const qual=qualityFilter.value;
  const hz=horizonFilter.value;
  const scCls=scClassFilter.value;
  const scConf=scConfFilter.value;
  const pViab=paperViabFilter.value;
  const rCls=regimeFilter.value;

  let filtered=factors.filter(f=>{
    const text=[f.factor_id,f.name_zh,f.name_en,f.family_zh,f.family,f.decision_bucket,f.final_quality_class,f.recommended_next_action,f.paper_viability_class,f.cost_sensitivity_class].join(' ').toLowerCase();
    if(q&&!text.includes(q))return false;
    if(fam&&(f.family_zh!==fam&&f.family!==fam))return false;
    if(qual&&f.metadata_quality!==qual)return false;
    if(hz&&f.best_horizon!==hz)return false;
    if(scCls&&f.final_quality_class!==scCls)return false;
    if(scConf&&f.score_confidence!==scConf)return false;
    if(pViab&&f.paper_viability_class!==pViab)return false;
    if(rCls&&f.regime_dependency_class!==rCls)return false;
    return true;
  });

  filtered.sort((a,b)=>{
    let va=a[sortCol],vb=b[sortCol];
    if(typeof va==='string')return sortDir*va.localeCompare(vb);
    va=va??-Infinity;vb=vb??-Infinity;
    return sortDir*(va-vb);
  });

  const tbody=document.getElementById('tableBody');
  tbody.innerHTML=filtered.map(f=>{
    const fid=esc(f.factor_id);
    return `<tr data-factor="${fid}" class="factor-row">
      <td><button class="factor-link" type="button">${fid}</button></td>
      <td><span class="zh">${esc(f.name_zh)}</span><br><span class="en small">${esc(f.name_en)}</span></td>
      <td>${esc(f.family_zh||f.family)}</td>
      <td>${scClassBadge(f.final_quality_class)}</td>
      <td class="num">${f.final_quality_score!==null&&f.final_quality_score!==undefined?Number(f.final_quality_score).toFixed(1):'—'}</td>
      <td>${f.score_confidence?scConfBadge(f.score_confidence):'—'}</td>
      <td>${qualBadge(f.metadata_quality)}</td>
      <td>${esc(f.best_horizon)}</td>
      <td class="num ${mcls(f.rankic_mean)}">${num(f.rankic_mean)}</td>
      <td class="num">${num(f.rankic_ir,3)}</td>
      <td class="num">${pct(f.monthly_ic_positive_rate)}</td>
      <td class="num ${mcls(f.long_short_sharpe,1.5,0.8)}">${num(f.long_short_sharpe,2)}</td>
      <td class="num">${pct(f.long_short_annualized_return)}</td>
      <td class="num">${pct(f.long_short_max_drawdown)}</td>
      <td class="num">${pct(f.long_short_positive_month_rate)}</td>
      <td class="num">${pct(f.coverage_rate)}</td>
      <td>${f.novelty_assessment?`<span class="bucket-badge">${esc(f.novelty_assessment)}</span>`:'—'}</td>
      <td>${esc(f.nearest_factor||'—')}</td>
      <td>${esc(f.strongest_redundancy_level||'—')}</td>
      <td>${f.redundancy_confidence?scConfBadge(f.redundancy_confidence):'—'}</td>
      <td class="num">${f.redundancy_cluster_id!==null&&f.redundancy_cluster_id!==undefined?Math.round(Number(f.redundancy_cluster_id)):'—'}</td>
      <td>${f.recommended_next_action?scActionBadge(f.recommended_next_action):'—'}</td>
      <td><span class="bucket-badge">${esc(f.decision_bucket)}</span></td>
      <td>${f.paper_viability_class?paperViabBadge(f.paper_viability_class):'—'}</td>
      <td>${f.cost_sensitivity_class?costSensBadge(f.cost_sensitivity_class):'—'}</td>
      <td class="num">${f.fee_10bps_total_return!==null&&f.fee_10bps_total_return!==undefined?num(f.fee_10bps_total_return,2):'—'}</td>
      <td class="num">${f.break_even_fee_bps!==null&&f.break_even_fee_bps!==undefined?Math.round(Number(f.break_even_fee_bps))+'bps':'—'}</td>
      <td class="num">${f.paper_avg_turnover!==null&&f.paper_avg_turnover!==undefined?pct(f.paper_avg_turnover):'—'}</td>
      <td>${f.regime_dependency_class?regimeBadge(f.regime_dependency_class):'—'}</td>
      <td class="num">${f.paper_return_btc_beta!==null&&f.paper_return_btc_beta!==undefined?num(f.paper_return_btc_beta,4):'—'}</td>
      <td class="num">${f.paper_return_btc_corr!==null&&f.paper_return_btc_corr!==undefined?num(f.paper_return_btc_corr,4):'—'}</td>
      <td class="num ${f.bull_minus_bear_paper_return!==null?((f.bull_minus_bear_paper_return>=0?'strong':'watch')):''}">${f.bull_minus_bear_paper_return!==null&&f.bull_minus_bear_paper_return!==undefined?num(f.bull_minus_bear_paper_return,4):'—'}</td>
      <td class="num ${f.drawdown_minus_normal_paper_return!==null?((f.drawdown_minus_normal_paper_return<0?'watch':'plain')):''}">${f.drawdown_minus_normal_paper_return!==null&&f.drawdown_minus_normal_paper_return!==undefined?num(f.drawdown_minus_normal_paper_return,4):'—'}</td>
    </tr>`;
  }).join('');

  // Re-attach row click
  tbody.querySelectorAll('tr').forEach(tr=>tr.addEventListener('click',()=>{
    tbody.querySelectorAll('tr.selected').forEach(r=>r.classList.remove('selected'));
    tr.classList.add('selected');
    renderDetail(tr.dataset.factor);
    // Scroll detail card into full view
    const dc=document.getElementById('detailCard');
    if(dc)dc.scrollIntoView({behavior:'smooth',block:'start'});
  }));
}

// ── Sort click ──
document.querySelectorAll('#factorTable th[data-col]').forEach(th=>{
  th.addEventListener('click',()=>{
    const col=th.dataset.col;
    if(sortCol===col){sortDir*=-1}else{sortCol=col;sortDir=-1}
    // Update visual
    document.querySelectorAll('#factorTable th').forEach(h=>{
      h.innerHTML=h.textContent.replace(/ [▲▼]/g,'');
    });
    th.innerHTML=th.textContent.replace(/ [▲▼]/g,'')+(sortDir>0?' ▲':' ▼');
    renderTable();
  });
});

// ── SVG chart helpers ──
function svgLineChart(data, yKey, w, h, opts={}){
  if(!data||data.length===0)return '<div class="small">No data</div>';
  const padL=50,padR=10,padT=10,padB=20;
  const cw=w-padL-padR,ch=h-padT-padB;
  const vals=data.map(d=>Number(d[yKey])||0);
  const ymin=Math.min(0,...vals),ymax=Math.max(0,...vals);
  const yrange=ymax-ymin||1;
  function xPos(i){return padL+(i/(data.length-1||1))*cw}
  function yPos(v){return padT+ch-((v-ymin)/yrange)*ch}

  let svg=`<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" style="width:100%;height:auto">`;
  // Zero line
  const zy=yPos(0);
  svg+=`<line x1="${padL}" y1="${zy}" x2="${w-padR}" y2="${zy}" stroke="#334155" stroke-dasharray="3"/>`;
  // Line
  const points=data.map((d,i)=>`${xPos(i)},${yPos(Number(d[yKey])||0)}`).join(' ');
  svg+=`<polyline points="${points}" fill="none" stroke="${opts.color||'#60a5fa'}" stroke-width="1.5"/>`;
  // Dots
  data.forEach((d,i)=>{
    const v=Number(d[yKey])||0;
    const c=v>=0?'#34d399':'#f87171';
    svg+=`<circle cx="${xPos(i)}" cy="${yPos(v)}" r="2" fill="${c}"/>`;
  });
  // X labels (sparse)
  const step=Math.max(1,Math.floor(data.length/6));
  data.forEach((d,i)=>{
    if(i%step===0||i===data.length-1){
      svg+=`<text x="${xPos(i)}" y="${h-2}" text-anchor="middle" fill="#8ea0b8" font-size="8">${esc(d.month)}</text>`;
    }
  });
  // Y axis label
  svg+=`<text x="4" y="${zy}" fill="#8ea0b8" font-size="8" dominant-baseline="middle">0</text>`;
  svg+=`<text x="4" y="${padT}" fill="#8ea0b8" font-size="8">${num(ymax,3)}</text>`;
  svg+=`<text x="4" y="${h-padB}" fill="#8ea0b8" font-size="8">${num(ymin,3)}</text>`;
  svg+='</svg>';
  return svg;
}

function svgBarChart(data, yKey, w, h){
  if(!data||data.length===0)return '<div class="small">No data</div>';
  const padL=50,padR=10,padT=10,padB=20;
  const cw=w-padL-padR,ch=h-padT-padB;
  const vals=data.map(d=>Number(d[yKey])||0);
  const maxAbs=Math.max(0.000001,...vals.map(v=>Math.abs(v)));
  const bw=Math.max(1,Math.min(8,cw/data.length-1));
  function yPos(v){return padT+ch/2-(v/maxAbs)*(ch/2)}

  let svg=`<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" style="width:100%;height:auto">`;
  const mid=padT+ch/2;
  svg+=`<line x1="${padL}" y1="${mid}" x2="${w-padR}" y2="${mid}" stroke="#334155" stroke-dasharray="3"/>`;
  data.forEach((d,i)=>{
    const v=Number(d[yKey])||0;
    const x=padL+(i/data.length)*cw;
    const barH=Math.abs(v/maxAbs)*(ch/2);
    const y=v>=0?mid-barH:mid;
    const c=v>=0?'#34d399':'#f87171';
    svg+=`<rect x="${x}" y="${y}" width="${bw}" height="${barH}" fill="${c}" rx="1"/>`;
  });
  // X labels
  const step=Math.max(1,Math.floor(data.length/6));
  data.forEach((d,i)=>{
    if(i%step===0||i===data.length-1){
      const x=padL+(i/data.length)*cw+bw/2;
      svg+=`<text x="${x}" y="${h-2}" text-anchor="middle" fill="#8ea0b8" font-size="8">${esc(d.month)}</text>`;
    }
  });
  svg+=`<text x="4" y="${mid}" fill="#8ea0b8" font-size="8" dominant-baseline="middle">0</text>`;
  svg+='</svg>';
  return svg;
}

function svgCumCurve(data, w, h){
  if(!data||data.length===0)return '<div class="small">No data</div>';
  const padL=50,padR=10,padT=10,padB=20;
  const cw=w-padL-padR,ch=h-padT-padB;
  const cumVals=data.map(d=>Number(d.cum_long_short_return)||0);
  const ddVals=data.map(d=>Number(d.drawdown)||0);
  const ymin=Math.min(0,...cumVals,...ddVals);
  const ymax=Math.max(0,...cumVals);
  const yrange=ymax-ymin||1;
  function xPos(i){return padL+(i/(data.length-1||1))*cw}
  function yPos(v){return padT+ch-((v-ymin)/yrange)*ch}

  let svg=`<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" style="width:100%;height:auto">`;
  const zy=yPos(0);
  svg+=`<line x1="${padL}" y1="${zy}" x2="${w-padR}" y2="${zy}" stroke="#334155" stroke-dasharray="3"/>`;

  // Drawdown shading
  if(data.length>1){
    let ddPath=`M${xPos(0)},${yPos(0)}`;
    data.forEach((d,i)=>{ddPath+=` L${xPos(i)},${yPos(Math.min(0,Number(d.cum_long_short_return)||0))}`});
    ddPath+=` L${xPos(data.length-1)},${yPos(0)} Z`;
    svg+=`<path d="${ddPath}" fill="#f8717133" stroke="none"/>`;
  }

  // Cumulative line
  const points=data.map((d,i)=>`${xPos(i)},${yPos(Number(d.cum_long_short_return)||0)}`).join(' ');
  svg+=`<polyline points="${points}" fill="none" stroke="#60a5fa" stroke-width="1.5"/>`;

  // Drawdown line
  const ddPoints=data.map((d,i)=>`${xPos(i)},${yPos(Number(d.drawdown)||0)}`).join(' ');
  svg+=`<polyline points="${ddPoints}" fill="none" stroke="#f87171" stroke-width="1" stroke-dasharray="3"/>`;

  // X labels
  const step=Math.max(1,Math.floor(data.length/6));
  data.forEach((d,i)=>{
    if(i%step===0||i===data.length-1){
      svg+=`<text x="${xPos(i)}" y="${h-2}" text-anchor="middle" fill="#8ea0b8" font-size="8">${esc(d.month)}</text>`;
    }
  });
  svg+=`<text x="4" y="${zy}" fill="#8ea0b8" font-size="8" dominant-baseline="middle">0</text>`;
  svg+=`<text x="4" y="${padT}" fill="#8ea0b8" font-size="8">${num(ymax,4)}</text>`;
  svg+=`<text x="4" y="${h-padB}" fill="#8ea0b8" font-size="8">${num(ymin,4)}</text>`;
  svg+='</svg>';
  return svg;
}

// ── Render detail ──
function renderDetail(fid){
  const f=byId.get(fid);if(!f)return;
  const card=document.getElementById('detailCard');

  const metricRow=(label,val,cls='')=>`<div class="metric"><span>${label}</span><strong class="${cls}">${val}</strong></div>`;

  // Build scorecard section HTML
  let scorecardHtml='';
  if(f.final_quality_class){
    const subScores=[
      ['computation_integrity_score',f.computation_integrity_score],
      ['predictive_ranking_score',f.predictive_ranking_score],
      ['portfolio_extraction_score',f.portfolio_extraction_score],
      ['stability_score',f.stability_score],
      ['quantile_shape_score',f.quantile_shape_score],
      ['direction_interpretability_score',f.direction_interpretability_score],
      ['redundancy_novelty_score',f.redundancy_novelty_score],
    ];
    const subBarsHtml=subScores.map(([k,v])=>scSubBar(k,v)).join('');

    scorecardHtml=`
      <div class="section-divider"></div>
      <h3>Factor Quality Scorecard / 因子质量记分卡</h3>
      <div style="margin:6px 0">
        ${scClassBadge(f.final_quality_class)}
        ${f.score_confidence?scConfBadge(f.score_confidence):''}
        ${f.redundancy_confidence?`<span class="sc-confidence-badge" style="background:#334155;color:#e2e8f0">Redundancy confidence 冗余置信度: ${esc(f.redundancy_confidence)}</span>`:''}
      </div>
      ${scScoreBar(f.final_quality_score,'Quality Score 质量分数')}
      ${f.recommended_next_action?`<div style="margin:6px 0"><strong style="font-size:11px;color:var(--muted)">Recommended Action 建议动作:</strong> ${scActionBadge(f.recommended_next_action)}</div>`:''}

      ${f.main_strengths_zh||f.main_strengths_en?`<div style="margin:6px 0"><div class="sc-strengths"><strong>Strengths 优势:</strong></div><div class="bilingual"><div class="zh" style="font-size:11px">${esc(f.main_strengths_zh)}</div><div class="en" style="font-size:10px">${esc(f.main_strengths_en)}</div></div></div>`:''}
      ${f.main_weaknesses_zh||f.main_weaknesses_en?`<div style="margin:6px 0"><div class="sc-weaknesses"><strong>Weaknesses 弱点:</strong></div><div class="bilingual"><div class="zh" style="font-size:11px">${esc(f.main_weaknesses_zh)}</div><div class="en" style="font-size:10px">${esc(f.main_weaknesses_en)}</div></div></div>`:''}
      ${f.review_notes_zh||f.review_notes_en?`<div style="margin:6px 0"><div class="sc-review-notes"><strong>Review Notes 复核说明:</strong></div><div class="bilingual"><div class="zh" style="font-size:11px">${esc(f.review_notes_zh)}</div><div class="en" style="font-size:10px">${esc(f.review_notes_en)}</div></div></div>`:''}

      <div style="margin-top:8px">
        <div style="font-size:10px;color:var(--muted);margin-bottom:4px;font-weight:600">Sub-Scores 子分数 (7 dimensions 维度):</div>
        ${subBarsHtml}
      </div>
    `;
  } else {
    scorecardHtml=`
      <div class="section-divider"></div>
      <h3>Factor Quality Scorecard / 因子质量记分卡</h3>
      <div style="margin:6px 0;font-size:11px;color:var(--muted)">N/A — No quality scorecard data available<br>无质量记分卡数据</div>
    `;
  }

  card.innerHTML=`
    <button class="back-to-table" onclick="document.getElementById('scoreboardCard').scrollIntoView({behavior:'smooth',block:'start'})">↑ 回到因子列表 / Back to table</button>
    <h2>${esc(f.factor_id)}</h2>
    <div class="bilingual">
      <div class="zh" style="font-size:15px;font-weight:600">${esc(f.name_zh)}</div>
      <div class="en">${esc(f.name_en)}</div>
    </div>
    <div class="small">${esc(f.family_zh||f.family)} · ${esc(f.family_en||'')} · ${dirBadge(f.expected_direction)} · best=${esc(f.best_horizon)}</div>

    ${f.final_quality_class?`<div style="margin:8px 0">${scClassBadge(f.final_quality_class)} ${f.final_quality_score!==null?`<span style="font-size:13px;font-weight:700">${Number(f.final_quality_score).toFixed(1)}</span>`:''} ${f.score_confidence?scConfBadge(f.score_confidence):''}</div>`:''}

    <div class="section-divider"></div>
    <h3>Formula 公式</h3>
    <div class="formula-block">
      <div><strong>ZH:</strong> ${esc(f.formula_zh)}</div>
      <div style="color:var(--muted)"><strong>EN:</strong> ${esc(f.formula_en)}</div>
    </div>

    <h3>Intuition 直觉解释</h3>
    <div class="bilingual"><div class="zh">${esc(f.intuition_zh)}</div><div class="en">${esc(f.intuition_en)}</div></div>

    <h3>Expected Direction 预期方向</h3>
    <div class="bilingual"><div class="zh">${esc(f.expected_direction_explanation_zh)}</div><div class="en">${esc(f.expected_direction_explanation_en)}</div></div>

    <h3>Known Limitations 已知局限</h3>
    <div class="bilingual"><div class="zh">${esc(f.known_limitations_zh)}</div><div class="en">${esc(f.known_limitations_en)}</div></div>

    <div class="section-divider"></div>
    <h3>Source Info & Timestamps 源信息与时间戳</h3>
    <div class="kv">
      <div>Data Source 数据源</div><div>${esc(f.data_source_type) || '<span style="color:var(--muted)">N/A</span>'}</div>
      <div>Source Fields 源字段</div><div>${esc(f.source_fields) || '<span style="color:var(--muted)">N/A</span>'}</div>
      <div>Required Columns 必要列</div><div>${esc(f.required_columns) || '<span style="color:var(--muted)">N/A</span>'}</div>
      <div>Horizon Notes 视野说明</div><div>${esc(f.horizon_notes_zh)||'<span style="color:var(--muted)">N/A</span>'}<br><span class="small">${esc(f.horizon_notes_en)}</span></div>
      <div>Status Explanation 状态说明</div><div>${esc(f.status_explanation_zh)||'<span style="color:var(--muted)">N/A</span>'}<br><span class="small">${esc(f.status_explanation_en)}</span></div>
    </div>
    <div style="margin-top:8px;font-size:10px;color:var(--muted)">
      <div>Page Generated 页面生成: ${esc(S.page_generation_time||'N/A')}</div>
      <div>Data Last Modified 数据最后更新: ${esc(S.data_last_modified||'N/A')}</div>
    </div>

    <div class="section-divider"></div>
    <h3>Metadata Quality 元数据质量</h3>
    <div>${qualBadge(f.metadata_quality)}</div>
    ${f.needs_human_review==='yes'?'<div style="color:var(--amber);font-size:11px;margin:4px 0">⚠ Needs human review 需人工复核</div>':''}
    ${f.qa_notes_zh?`<div class="bilingual"><div class="zh" style="font-size:11px">${esc(f.qa_notes_zh)}</div><div class="en" style="font-size:10px">${esc(f.qa_notes_en)}</div></div>`:''}
    ${f.qa_reason?`<div class="small">Reason: ${esc(f.qa_reason)}</div>`:''}

    <div class="section-divider"></div>
    <div class="evidence-label">📊 Evidence — 机器计算指标</div>
    <div style="display:flex;align-items:center;gap:8px;margin:4px 0">
      <h3 id="hz-title-${f.factor_id}" style="margin:0">Best Horizon Metrics 最优视野指标 (${esc(f.best_horizon)})</h3>
      ${f.horizon_pattern?horizonPatternBadge(f.horizon_pattern):''}
    </div>
    <div id="hz-switch-${f.factor_id}">${buildHorizonSwitch(f)}</div>
    <div id="hz-metrics-${f.factor_id}" class="metric-grid">
      ${metricRow(renderTooltip('RankIC Mean'),num(f.rankic_mean),mcls(f.rankic_mean))}
      ${metricRow(renderTooltip('RankIC Std'),num(f.rankic_std,4,false))}
      ${metricRow(renderTooltip('ICIR'),num(f.rankic_ir,3))}
      ${metricRow(renderTooltip('IC t-stat'),num(f.rankic_t_stat,2,false))}
      ${metricRow(renderTooltip('IC Win Rate'),pct(f.monthly_ic_positive_rate))}
      ${metricRow(renderTooltip('LS Mean'),num(f.long_short_mean,6))}
      ${metricRow(renderTooltip('LS Std'),num(f.long_short_std,6))}
      ${metricRow(renderTooltip('LS Sharpe'),num(f.long_short_sharpe,2),mcls(f.long_short_sharpe,1.5,0.8))}
      ${metricRow(renderTooltip('Ann Return'),pct(f.long_short_annualized_return))}
      ${metricRow(renderTooltip('Ann Vol'),pct(f.long_short_annualized_vol))}
      ${metricRow(renderTooltip('Max Drawdown'),pct(f.long_short_max_drawdown))}
      ${metricRow(renderTooltip('LS Win Rate'),pct(f.long_short_positive_month_rate))}
      ${metricRow(renderTooltip('Coverage'),pct(f.coverage_rate))}
    </div>
    ${f.ls_metrics_unavailable_reason?`<div style="margin:4px 0;font-size:10px;color:var(--muted);font-style:italic">${esc(f.ls_metrics_unavailable_reason)}</div>`:''}

    ${f.horizon_metrics?`<h3 style="margin-top:12px">All-Horizon Summary 全视野摘要</h3>${buildAllHorizonTable(f)}`:''}

    ${renderPM49Interpretation(f)}

    <div class="kv" style="margin-top:8px">
      <div>Redundancy 冗余度</div><div>${esc(f.redundancy_level)}</div>
      <div>Nearest Factor 最近因子</div><div>${esc(f.nearest_redundant_factor||'—')}</div>
      <div>Decision Bucket 决策桶</div><div><span class="bucket-badge">${esc(f.decision_bucket)}</span></div>
      <div>Recommended Action 建议操作</div><div>${esc(f.recommended_action||'—')}</div>
      <div>Source Warning 源警告</div><div>${esc(f.source_warning||'—')}</div>
    </div>

    ${scorecardHtml}

    <div class="section-divider"></div>
    <h3>Redundancy & Novelty / 冗余与新颖性</h3>
    <div class="kv">
      <div>Novelty Assessment 新颖性评估</div><div>${f.novelty_assessment?noveltyBadge(f.novelty_assessment):'—'}</div>
      ${f.redundancy_source!=='unified_profile'?`
        <div>Nearest Factor 最近相似因子</div><div>${esc(f.nearest_factor||'—')}</div>
        <div>Nearest abs Spearman 最近|Spearman|</div><div>${f.nearest_abs_spearman_corr!==null?Number(f.nearest_abs_spearman_corr).toFixed(4):'—'}</div>
      `:`
        <div>Marginal Info 边际信息</div><div>${esc(f.marginal_information_class||'—')}</div>
        <div>Cluster Role 聚类角色</div><div>${esc(f.cluster_member_role||'—')}</div>
      `}
      <div>Strongest Redundancy 最强冗余等级</div><div>${f.strongest_redundancy_level?redundancyLevelBadge(f.strongest_redundancy_level):'—'}</div>
      <div>Redundancy Confidence 冗余置信度</div><div>${f.redundancy_confidence?scConfBadge(f.redundancy_confidence):'—'}</div>
      ${f.redundancy_source!=='unified_profile'?`
        <div>Valid Pairs 有效对</div><div>${f.valid_redundancy_pair_count!==null?Math.round(Number(f.valid_redundancy_pair_count))+' / '+Math.round(Number(f.expected_redundancy_pair_count)):'—'}</div>
        <div>Valid Pair Coverage 有效对覆盖率</div><div>${f.valid_redundancy_pair_coverage!==null?pct(f.valid_redundancy_pair_coverage):'—'}</div>
        <div>Insufficient Overlap 重叠不足对</div><div>${f.insufficient_overlap_pair_count!==null?Math.round(Number(f.insufficient_overlap_pair_count)):'—'}</div>
      `:''}
      <div>Cluster 聚类</div><div>${f.redundancy_cluster_id!==null?'#'+Math.round(Number(f.redundancy_cluster_id))+' ('+Math.round(Number(f.redundancy_cluster_size||0))+' factors)':'—'}</div>
    </div>
    <div style="margin-top:6px;font-size:10px;color:var(--muted)">
      冗余分析是研究相似性诊断，不是删除因子的理由。高冗余因子可保留用于方向/视野多样性。
      <br>Redundancy analysis is a research similarity diagnostic, not a reason by itself to delete a factor. High-redundancy factors may be retained for direction/horizon diversity.
    </div>

    <div class="section-divider"></div>
    <h3 id="hz-ic-title-${f.factor_id}">Monthly RankIC 月度RankIC (${esc(f.best_horizon)})</h3>
    ${CHART_GUIDES.monthlyIC}
    <div class="chart-container">
      <div class="chart-title">Monthly RankIC (adj) · 月度调整RankIC</div>
      <div id="hz-ic-chart-${f.factor_id}">
      ${f.monthly_ic&&f.monthly_ic.length>0
        ? svgLineChart(f.monthly_ic,'rank_ic_adj',600,140)
        : (f.rankic_mean!==null&&f.rankic_mean!==undefined
          ? '<div style="padding:12px;color:var(--muted);font-size:12px">📊 Summary RankIC available: <strong>'+num(f.rankic_mean)+'</strong> (t='+num(f.rankic_t_stat,2,false)+')<br>Monthly IC series unavailable — factor-level evaluation provides aggregate stats only.<br>月度IC序列暂不可用 — 因子级评价仅提供汇总统计。</div>'
          : '<div class="small">No data</div>')}
      </div>
    </div>

    <h3 id="hz-ls-title-${f.factor_id}">Monthly Long-Short Return 月度多空收益 (${esc(f.best_horizon)})</h3>
    ${CHART_GUIDES.monthlyLS}
    <div class="chart-container">
      <div class="chart-title">Monthly LS Return · 月度多空收益</div>
      <div id="hz-ls-chart-${f.factor_id}">
      ${svgBarChart(f.monthly_ls,'long_short_return',600,120)}
      </div>
    </div>

    <h3 id="hz-cum-title-${f.factor_id}">Cumulative Long-Short Curve 累计多空曲线 (${esc(f.best_horizon)})</h3>
    ${CHART_GUIDES.cumLS}
    <div class="chart-container">
      <div class="chart-title">Cumulative LS (blue) with drawdown (red) · 累计多空(蓝)及回撤(红)</div>
      <div id="hz-cum-chart-${f.factor_id}">
      ${svgCumCurve(f.cum_curve,600,160)}
      </div>
    </div>

    <h3>Drawdown Summary 回撤概要</h3>
    <div class="metric-grid">
      ${metricRow('Max DD 最大回撤',pct(f.long_short_max_drawdown))}
      ${metricRow('LS Month Win% 月胜率',pct(f.long_short_positive_month_rate))}
      ${metricRow(renderTooltip('LS Sharpe'),num(f.long_short_sharpe,2),mcls(f.long_short_sharpe,1.5,0.8))}
    </div>

    ${f.paper_viability_class?`
    <div class="section-divider"></div>
    <h3>Single-Factor Paper Portfolio / 单因子纸面组合</h3>
    ${CHART_GUIDES.paperNav}
    <div style="margin:6px 0">
      ${paperViabBadge(f.paper_viability_class)}
      ${f.cost_sensitivity_class?costSensBadge(f.cost_sensitivity_class):''}
    </div>
    <div class="metric-grid">
      ${metricRow(renderTooltip('Gross Sharpe'),num(f.gross_sharpe,2))}
      ${metricRow(renderTooltip('Gross Return'),num(f.gross_total_return,2))}
      ${metricRow('Max DD 最大回撤',pct(f.paper_max_drawdown))}
      ${metricRow(renderTooltip('Positive Mo%'),pct(f.paper_positive_month_rate))}
      ${metricRow(renderTooltip('Avg Turnover'),pct(f.paper_avg_turnover))}
      ${metricRow(renderTooltip('Median Turnover'),pct(f.paper_median_turnover))}
      ${metricRow(renderTooltip('B/E Fee'),f.break_even_fee_bps!==null&&f.break_even_fee_bps!==undefined?Math.round(Number(f.break_even_fee_bps))+' bps':'—')}
      ${metricRow(renderTooltip('0bps Return'),num(f.fee_0bps_total_return,2))}
      ${metricRow(renderTooltip('5bps Return'),num(f.fee_5bps_total_return,2))}
      ${metricRow(renderTooltip('10bps Return'),num(f.fee_10bps_total_return,2),f.fee_10bps_total_return!==null&&f.fee_10bps_total_return<0?'':'')}
      ${metricRow(renderTooltip('20bps Return'),num(f.fee_20bps_total_return,2))}
    </div>
    ${f.main_diagnostic_note_zh||f.main_diagnostic_note_en?`<div class="bilingual" style="margin:6px 0"><div class="zh" style="font-size:11px">${esc(f.main_diagnostic_note_zh)}</div><div class="en" style="font-size:10px;color:var(--muted)">${esc(f.main_diagnostic_note_en)}</div></div>`:''}

    <div class="chart-container">
      <div class="chart-title">Monthly NAV: 0bps (blue) vs 10bps (red) · 月度净值: 0bps(蓝) vs 10bps(红)</div>
      ${(()=>{
        const nav0=f.monthly_nav_series_compact&&f.monthly_nav_series_compact['0']?f.monthly_nav_series_compact['0']:[];
        const nav10=f.monthly_nav_series_compact&&f.monthly_nav_series_compact['10']?f.monthly_nav_series_compact['10']:[];
        if(!nav0.length&&!nav10.length)return '<div class="small">No data</div>';
        const allPts=[...nav0.map(d=>d.nav),...nav10.map(d=>d.nav)];
        const ymin=Math.min(0,...allPts),ymax=Math.max(0,...allPts);
        const yrange=ymax-ymin||1;
        const w=600,h=150,padL=50,padR=10,padT=10,padB=20;
        const cw=w-padL-padR,ch=h-padT-padB;
        const maxLen=Math.max(nav0.length,nav10.length,1);
        function xPos(i){return padL+(i/(maxLen-1||1))*cw}
        function yPos(v){return padT+ch-((v-ymin)/yrange)*ch}
        let svg='<svg width="'+w+'" height="'+h+'" viewBox="0 0 '+w+' '+h+'" style="width:100%;height:auto">';
        svg+='<line x1="'+padL+'" y1="'+yPos(0)+'" x2="'+(w-padR)+'" y2="'+yPos(0)+'" stroke="#334155" stroke-dasharray="3"/>';
        if(nav0.length>1){svg+='<polyline points="'+nav0.map((d,i)=>xPos(i)+','+yPos(d.nav)).join(' ')+'" fill="none" stroke="#60a5fa" stroke-width="1.5"/>';}
        if(nav10.length>1){svg+='<polyline points="'+nav10.map((d,i)=>xPos(i)+','+yPos(d.nav)).join(' ')+'" fill="none" stroke="#f87171" stroke-width="1.5"/>';}
        const step=Math.max(1,Math.floor(maxLen/6));
        nav0.forEach((d,i)=>{if(i%step===0||i===nav0.length-1){svg+='<text x="'+xPos(i)+'" y="'+(h-2)+'" text-anchor="middle" fill="#8ea0b8" font-size="8">'+esc(d.month)+'</text>'}});
        svg+='<text x="4" y="'+yPos(0)+'" fill="#8ea0b8" font-size="8" dominant-baseline="middle">0</text>';
        svg+='<text x="4" y="'+padT+'" fill="#8ea0b8" font-size="8">'+num(ymax,3)+'</text>';
        svg+='<text x="4" y="'+(h-padB)+'" fill="#8ea0b8" font-size="8">'+num(ymin,3)+'</text>';
        svg+='</svg>';
        return svg;
      })()}
    </div>

    <div class="chart-container">
      ${CHART_GUIDES.feeSensitivity}
      <div class="chart-title">Fee Sensitivity: Total Return & Sharpe by fee_bps · 费用敏感性</div>
      ${(()=>{
        const fs=f.fee_sensitivity_series||[];
        if(!fs.length)return '<div class="small">No data</div>';
        const w=600,h=120,padL=50,padR=10,padT=10,padB=20;
        const cw=w-padL-padR,ch=h-padT-padB;
        const vals=fs.map(d=>d.total_return||0);
        const maxAbs=Math.max(0.001,...vals.map(v=>Math.abs(v)));
        const bw=Math.max(8,Math.min(30,Math.floor(cw/fs.length)-4));
        function yPos(v){return padT+ch/2-(v/maxAbs)*(ch/2)}
        let svg='<svg width="'+w+'" height="'+h+'" viewBox="0 0 '+w+' '+h+'" style="width:100%;height:auto">';
        const mid=padT+ch/2;
        svg+='<line x1="'+padL+'" y1="'+mid+'" x2="'+(w-padR)+'" y2="'+mid+'" stroke="#334155" stroke-dasharray="3"/>';
        fs.forEach((d,i)=>{
          const v=d.total_return||0;
          const x=padL+(i/fs.length)*cw+(cw/fs.length-bw)/2;
          const barH=Math.abs(v/maxAbs)*(ch/2);
          const y=v>=0?mid-barH:mid;
          const c=v>=0?'#34d399':'#f87171';
          svg+='<rect x="'+x+'" y="'+y+'" width="'+bw+'" height="'+barH+'" fill="'+c+'" rx="2"/>';
          svg+='<text x="'+(x+bw/2)+'" y="'+(h-2)+'" text-anchor="middle" fill="#8ea0b8" font-size="8">'+d.fee_bps+'bps</text>';
        });
        svg+='<text x="4" y="'+mid+'" fill="#8ea0b8" font-size="8" dominant-baseline="middle">0</text>';
        svg+='</svg>';
        return svg;
      })()}
    </div>

    <div class="chart-container">
      <div class="chart-title">Monthly Returns (10bps) · 月度收益 (10bps)</div>
      ${(()=>{
        const mr=f.monthly_return_series||[];
        if(!mr.length)return '<div class="small">No data</div>';
        return svgBarChart(mr,'monthly_return',600,120);
      })()}
    </div>

    ${(()=>{
      const ts=f.turnover_series||[];
      if(!ts.length)return '';
      return `
        <div class="chart-container">
          <div class="chart-title">Monthly Turnover · 月度换手率</div>
          ${svgLineChart(ts,'avg_turnover',600,120,{color:'#fbbf24'})}
        </div>`;
    })()}

    ${(()=>{
      const ld=f.leg_decomposition_series||[];
      if(!ld.length)return '';
      const w=600,h=140,padL=50,padR=10,padT=10,padB=20;
      const cw=w-padL-padR,ch=h-padT-padB;
      const longVals=ld.map(d=>Number(d.long_leg_return)||0);
      const shortVals=ld.map(d=>Number(d.short_leg_return)||0);
      const netVals=ld.map(d=>Number(d.net_long_short_return)||0);
      const allVals=[...longVals,...shortVals,...netVals];
      const ymin=Math.min(0,...allVals),ymax=Math.max(0,...allVals);
      const yrange=ymax-ymin||1;
      function xPos(i){return padL+(i/(ld.length-1||1))*cw}
      function yPos(v){return padT+ch-((v-ymin)/yrange)*ch}
      let svg='<svg width="'+w+'" height="'+h+'" viewBox="0 0 '+w+' '+h+'" style="width:100%;height:auto">';
      svg+='<line x1="'+padL+'" y1="'+yPos(0)+'" x2="'+(w-padR)+'" y2="'+yPos(0)+'" stroke="#334155" stroke-dasharray="3"/>';
      const lp=ld.map((d,i)=>xPos(i)+','+yPos(Number(d.long_leg_return)||0)).join(' ');
      const sp=ld.map((d,i)=>xPos(i)+','+yPos(Number(d.short_leg_return)||0)).join(' ');
      const np=ld.map((d,i)=>xPos(i)+','+yPos(Number(d.net_long_short_return)||0)).join(' ');
      svg+='<polyline points="'+lp+'" fill="none" stroke="#34d399" stroke-width="1.2"/>';
      svg+='<polyline points="'+sp+'" fill="none" stroke="#f87171" stroke-width="1.2"/>';
      svg+='<polyline points="'+np+'" fill="none" stroke="#60a5fa" stroke-width="1.5"/>';
      const step=Math.max(1,Math.floor(ld.length/6));
      ld.forEach((d,i)=>{if(i%step===0||i===ld.length-1){svg+='<text x="'+xPos(i)+'" y="'+(h-2)+'" text-anchor="middle" fill="#8ea0b8" font-size="8">'+esc(d.month)+'</text>'}});
      svg+='<text x="4" y="'+yPos(0)+'" fill="#8ea0b8" font-size="8" dominant-baseline="middle">0</text>';
      svg+='<text x="4" y="'+padT+'" fill="#8ea0b8" font-size="7">'+num(ymax,4)+'</text>';
      svg+='<text x="4" y="'+(h-padB)+'" fill="#8ea0b8" font-size="7">'+num(ymin,4)+'</text>';
      svg+='<text x="'+(w-padR)+'" y="'+padT+'" text-anchor="end" fill="#34d399" font-size="8">Long</text>';
      svg+='<text x="'+(w-padR)+'" y="'+(padT+10)+'" text-anchor="end" fill="#f87171" font-size="8">Short</text>';
      svg+='<text x="'+(w-padR)+'" y="'+(padT+20)+'" text-anchor="end" fill="#60a5fa" font-size="8">Net L/S</text>';
      svg+='</svg>';
      return '<div class="chart-container"><div class="chart-title">Leg Decomposition: Long (green) / Short (red) / Net L/S (blue) · 多空腿分解</div>'+svg+'</div>';
    })()}

    ${(()=>{
      const dd=f.drawdown_series||[];
      if(!dd.length)return '';
      const w=600,h=140,padL=50,padR=10,padT=10,padB=20;
      const cw=w-padL-padR,ch=h-padT-padB;
      const navVals=dd.map(d=>Number(d.nav)||0);
      const ddVals=dd.map(d=>Number(d.drawdown)||0);
      const navMax=Math.max(0,...navVals),navMin=Math.min(0,...navVals);
      const navRange=navMax-navMin||1;
      function xPos(i){return padL+(i/(dd.length-1||1))*cw}
      function navY(v){return padT+ch-((v-navMin)/navRange)*ch}
      const ddMax=Math.max(0.001,...ddVals);
      function ddY(v){return padT+ch-(v/ddMax)*ch}
      let svg='<svg width="'+w+'" height="'+h+'" viewBox="0 0 '+w+' '+h+'" style="width:100%;height:auto">';
      svg+='<line x1="'+padL+'" y1="'+navY(1)+'" x2="'+(w-padR)+'" y2="'+navY(1)+'" stroke="#334155" stroke-dasharray="3"/>';
      if(dd.length>1){let ddPath='M'+xPos(0)+','+ddY(0);dd.forEach((d,i)=>{ddPath+=' L'+xPos(i)+','+ddY(Number(d.drawdown)||0)});ddPath+=' L'+xPos(dd.length-1)+','+ddY(0)+' Z';svg+='<path d="'+ddPath+'" fill="#f8717122" stroke="none"/>';}
      const navPts=dd.map((d,i)=>xPos(i)+','+navY(Number(d.nav)||0)).join(' ');
      const ddPts=dd.map((d,i)=>xPos(i)+','+ddY(Number(d.drawdown)||0)).join(' ');
      svg+='<polyline points="'+navPts+'" fill="none" stroke="#60a5fa" stroke-width="1.5"/>';
      svg+='<polyline points="'+ddPts+'" fill="none" stroke="#f87171" stroke-width="1" stroke-dasharray="3"/>';
      const step=Math.max(1,Math.floor(dd.length/6));
      dd.forEach((d,i)=>{if(i%step===0||i===dd.length-1){svg+='<text x="'+xPos(i)+'" y="'+(h-2)+'" text-anchor="middle" fill="#8ea0b8" font-size="8">'+esc(d.month)+'</text>'}});
      svg+='<text x="4" y="'+navY(navMax)+'" fill="#8ea0b8" font-size="7">'+num(navMax,3)+'</text>';
      svg+='<text x="4" y="'+navY(navMin)+'" fill="#8ea0b8" font-size="7">'+num(navMin,3)+'</text>';
      svg+='<text x="'+(w-padR)+'" y="'+padT+'" text-anchor="end" fill="#60a5fa" font-size="8">NAV (blue)</text>';
      svg+='<text x="'+(w-padR)+'" y="'+(padT+10)+'" text-anchor="end" fill="#f87171" font-size="8">Drawdown (red)</text>';
      svg+='</svg>';
      return '<div class="chart-container"><div class="chart-title">Paper Portfolio NAV & Drawdown (10bps) · 纸面组合净值与回撤</div>'+svg+'</div>';
    })()}

    <div class="paper-caveat">
      <strong>⚠ This is a research diagnostic, not a strategy / 这是研究诊断，不是交易策略</strong><br>
      <span style="color:var(--muted)">Equal-weight long/short at 1h horizon. No slippage/order book modeling. 等权多空，1h视野，无滑点/订单簿建模。</span>
    </div>
    `:`<div class="section-divider"></div><h3>Single-Factor Paper Portfolio / 单因子纸面组合</h3><div style="margin:6px 0;font-size:11px;color:var(--muted)">N/A — No paper portfolio data available<br>无纸面组合数据</div>`}

    ${f.regime_dependency_class?`
    <div class="section-divider"></div>
    <h3>BTC / Market Regime Diagnostics / BTC / 市场状态诊断</h3>
    ${CHART_GUIDES.regimeIC}
    <div style="margin:6px 0">
      ${regimeBadge(f.regime_dependency_class)}
      ${f.main_regime_note_zh?`<span style="font-size:11px;margin-left:6px">${esc(f.main_regime_note_zh)} / ${esc(f.main_regime_note_en)}</span>`:''}
    </div>
    <div class="metric-grid">
      ${metricRow(renderTooltip('Paper-BTC Corr'),num(f.paper_return_btc_corr,4))}
      ${metricRow(renderTooltip('Paper-BTC Beta'),num(f.paper_return_btc_beta,4))}
      ${metricRow(renderTooltip('LS-BTC Corr'),num(f.long_short_btc_corr,4))}
      ${metricRow(renderTooltip('LS-BTC Beta'),num(f.long_short_btc_beta,4))}
      ${metricRow(renderTooltip('IC-BTC Corr'),num(f.ic_btc_return_corr,4))}
      ${metricRow(renderTooltip('Bull−Bear Δ'),num(f.bull_minus_bear_paper_return,4),f.bull_minus_bear_paper_return!==null?(f.bull_minus_bear_paper_return>=0?'strong':'watch'):'')}
      ${metricRow(renderTooltip('HV−LV Δ'),num(f.highvol_minus_lowvol_paper_return,4))}
      ${metricRow(renderTooltip('DD−Normal Δ'),num(f.drawdown_minus_normal_paper_return,4),f.drawdown_minus_normal_paper_return!==null?(f.drawdown_minus_normal_paper_return<0?'watch':''):'')}
    </div>
    ${(()=>{
      const rd=f.regime_detail||[];
      if(!rd.length)return '<div class="small">No regime detail data</div>';
      // Helper: get regime data for a specific dimension+metric
      function getRegimeMeans(dimension,metricType){
        return rd.filter(r=>r.dimension===dimension&&r.metric_type===metricType)
          .map(r=>({regime:r.regime,mean:r.mean||0,positive_rate:r.positive_rate||0,n_months:r.n_months}));
      }
      function regimeBarChart(items,label,w,h){
        if(!items.length)return '';
        const padL=70,padR=10,padT=10,padB=20;
        const cw=w-padL-padR,ch=h-padT-padB;
        const maxAbs=Math.max(0.000001,...items.map(d=>Math.abs(d.mean)));
        const bw=Math.max(20,Math.min(60,Math.floor(cw/items.length)-8));
        function yPos(v){return padT+ch/2-(v/maxAbs)*(ch/2)}
        let svg='<svg width="'+w+'" height="'+h+'" viewBox="0 0 '+w+' '+h+'" style="width:100%;height:auto">';
        const mid=padT+ch/2;
        svg+='<line x1="'+padL+'" y1="'+mid+'" x2="'+(w-padR)+'" y2="'+mid+'" stroke="#334155" stroke-dasharray="3"/>';
        items.forEach((d,i)=>{
          const x=padL+(i/items.length)*cw+(cw/items.length-bw)/2;
          const barH=Math.abs(d.mean/maxAbs)*(ch/2);
          const y=d.mean>=0?mid-barH:mid;
          const c=d.mean>=0?'#34d399':'#f87171';
          svg+='<rect x="'+x+'" y="'+y+'" width="'+bw+'" height="'+barH+'" fill="'+c+'" rx="2"/>';
          svg+='<text x="'+(x+bw/2)+'" y="'+(h-2)+'" text-anchor="middle" fill="#8ea0b8" font-size="8">'+esc(d.regime)+'</text>';
          svg+='<text x="'+(x+bw/2)+'" y="'+(y-3)+'" text-anchor="middle" fill="#8ea0b8" font-size="7">'+num(d.mean,4)+'</text>';
        });
        svg+='<text x="4" y="'+mid+'" fill="#8ea0b8" font-size="8" dominant-baseline="middle">0</text>';
        svg+='<text x="4" y="'+padT+'" fill="#8ea0b8" font-size="7">'+label+'</text>';
        svg+='</svg>';
        return svg;
      }
      const trendPr=getRegimeMeans('btc_trend_regime','paper_return');
      const trendIc=getRegimeMeans('btc_trend_regime','ic_rank');
      const volPr=getRegimeMeans('btc_vol_regime','paper_return');
      const ddPr=getRegimeMeans('btc_drawdown_regime','paper_return');
      return `
        <div class="chart-container">
          <div class="chart-title">Paper Return by Trend Regime · 趋势状态纸面收益</div>
          ${regimeBarChart(trendPr,'Paper Return',300,110)}
        </div>
        <div class="chart-container">
          <div class="chart-title">RankIC by Trend Regime · 趋势状态RankIC</div>
          ${regimeBarChart(trendIc,'RankIC',300,110)}
        </div>
        <div class="chart-container">
          <div class="chart-title">Paper Return by Volatility Regime · 波动率状态纸面收益</div>
          ${regimeBarChart(volPr,'Paper Return',250,110)}
        </div>
        <div class="chart-container">
          <div class="chart-title">Paper Return by Drawdown Regime · 回撤状态纸面收益</div>
          ${regimeBarChart(ddPr,'Paper Return',250,110)}
        </div>
      `;
    })()}
    <div class="regime-caveat">
      <strong>⚠ Regime diagnostics identify conditional behavior, not trade rules / 市场状态诊断识别条件行为，非交易规则</strong><br>
      <span style="color:var(--muted)">BTC regime labels classify market conditions ex-post. Factor performance differences across regimes are informational, not actionable timing signals.<br>
      BTC市场状态标签为事后分类。因子在不同状态下的表现差异仅供参考，不构成可操作的择时信号。</span>
    </div>
    `:`<div class="section-divider"></div><h3>BTC / Market Regime Diagnostics / BTC / 市场状态诊断</h3><div style="margin:6px 0;font-size:11px;color:var(--muted)">N/A — No regime diagnostics data available<br>无市场状态诊断数据</div>`}

    ${(()=>{
      const ss=f.shape_stability;
      if(!ss)return '';
      const hz=ss[f.best_horizon];
      if(!hz)return '';
      const sh=hz.shape||{};
      const st=hz.stability||{};
      const dc=hz.decile||{};
      const qr=hz.q_returns||[];
      const eodr=dc.expected_order_decile_returns||[];
      if(!sh.quantile_shape_class&&!st.stability_class&&!dc.decile_shape_class)return '';

      // Q1–Q5 bar chart
      function qBarChart(returns,w,h){
        if(!returns||returns.length===0)return '<div class="small">No data</div>';
        const padL=60,padR=10,padT=10,padB=22;
        const cw=w-padL-padR,ch=h-padT-padB;
        const maxAbs=Math.max(0.000001,...returns.map(v=>Math.abs(v)));
        const bw=Math.max(16,Math.min(50,Math.floor(cw/returns.length)-8));
        function yPos(v){return padT+ch/2-(v/maxAbs)*(ch/2)}
        let svg='<svg width="'+w+'" height="'+h+'" viewBox="0 0 '+w+' '+h+'" style="width:100%;height:auto">';
        const mid=padT+ch/2;
        svg+='<line x1="'+padL+'" y1="'+mid+'" x2="'+(w-padR)+'" y2="'+mid+'" stroke="#334155" stroke-dasharray="3"/>';
        returns.forEach((v,i)=>{
          const x=padL+(i/returns.length)*cw+(cw/returns.length-bw)/2;
          const barH=Math.abs(v/maxAbs)*(ch/2);
          const y=v>=0?mid-barH:mid;
          const c=v>=0?'#34d399':'#f87171';
          svg+='<rect x="'+x+'" y="'+y+'" width="'+bw+'" height="'+barH+'" fill="'+c+'" rx="2"/>';
          svg+='<text x="'+(x+bw/2)+'" y="'+(h-4)+'" text-anchor="middle" fill="#8ea0b8" font-size="10">Q'+(i+1)+'</text>';
          svg+='<text x="'+(x+bw/2)+'" y="'+(y-3)+'" text-anchor="middle" fill="#8ea0b8" font-size="7">'+num(v,5)+'</text>';
        });
        svg+='<text x="4" y="'+mid+'" fill="#8ea0b8" font-size="8" dominant-baseline="middle">0</text>';
        svg+='</svg>';
        return svg;
      }

      // D1–D10 bar chart
      function decileBarChart(returns,w,h){
        if(!returns||returns.length===0)return '<div class="small">No data</div>';
        const padL=60,padR=10,padT=10,padB=22;
        const cw=w-padL-padR,ch=h-padT-padB;
        const maxAbs=Math.max(0.000001,...returns.map(v=>Math.abs(v)));
        const bw=Math.max(10,Math.min(30,Math.floor(cw/returns.length)-4));
        function yPos(v){return padT+ch/2-(v/maxAbs)*(ch/2)}
        let svg='<svg width="'+w+'" height="'+h+'" viewBox="0 0 '+w+' '+h+'" style="width:100%;height:auto">';
        const mid=padT+ch/2;
        svg+='<line x1="'+padL+'" y1="'+mid+'" x2="'+(w-padR)+'" y2="'+mid+'" stroke="#334155" stroke-dasharray="3"/>';
        returns.forEach((v,i)=>{
          const x=padL+(i/returns.length)*cw+(cw/returns.length-bw)/2;
          const barH=Math.abs(v/maxAbs)*(ch/2);
          const y=v>=0?mid-barH:mid;
          const c=v>=0?'#34d399':'#f87171';
          svg+='<rect x="'+x+'" y="'+y+'" width="'+bw+'" height="'+barH+'" fill="'+c+'" rx="1"/>';
          svg+='<text x="'+(x+bw/2)+'" y="'+(h-4)+'" text-anchor="middle" fill="#8ea0b8" font-size="9">D'+(i+1)+'</text>';
          svg+='<text x="'+(x+bw/2)+'" y="'+(y-3)+'" text-anchor="middle" fill="#8ea0b8" font-size="6">'+num(v,5)+'</text>';
        });
        svg+='<text x="4" y="'+mid+'" fill="#8ea0b8" font-size="8" dominant-baseline="middle">0</text>';
        svg+='</svg>';
        return svg;
      }

      // Stability metrics mini-chart (bars for 3M/6M values)
      function stabilityMiniChart(st,w,h){
        const items=[];
        if(st.rolling_ic_3m_mean_latest!==null&&st.rolling_ic_3m_mean_latest!==undefined) items.push({label:'IC 3M',val:st.rolling_ic_3m_mean_latest});
        if(st.rolling_ic_6m_mean_latest!==null&&st.rolling_ic_6m_mean_latest!==undefined) items.push({label:'IC 6M',val:st.rolling_ic_6m_mean_latest});
        if(st.rolling_ls_3m_mean_latest!==null&&st.rolling_ls_3m_mean_latest!==undefined) items.push({label:'LS 3M',val:st.rolling_ls_3m_mean_latest});
        if(st.rolling_ls_6m_mean_latest!==null&&st.rolling_ls_6m_mean_latest!==undefined) items.push({label:'LS 6M',val:st.rolling_ls_6m_mean_latest});
        if(!items.length)return '';
        const padL=60,padR=10,padT=10,padB=22;
        const cw=w-padL-padR,ch=h-padT-padB;
        const maxAbs=Math.max(0.000001,...items.map(d=>Math.abs(d.val)));
        const bw=Math.max(20,Math.min(60,Math.floor(cw/items.length)-8));
        function yPos(v){return padT+ch/2-(v/maxAbs)*(ch/2)}
        let svg='<svg width="'+w+'" height="'+h+'" viewBox="0 0 '+w+' '+h+'" style="width:100%;height:auto">';
        const mid=padT+ch/2;
        svg+='<line x1="'+padL+'" y1="'+mid+'" x2="'+(w-padR)+'" y2="'+mid+'" stroke="#334155" stroke-dasharray="3"/>';
        items.forEach((d,i)=>{
          const x=padL+(i/items.length)*cw+(cw/items.length-bw)/2;
          const barH=Math.abs(d.val/maxAbs)*(ch/2);
          const y=d.val>=0?mid-barH:mid;
          const c=d.val>=0?'#34d399':'#f87171';
          svg+='<rect x="'+x+'" y="'+y+'" width="'+bw+'" height="'+barH+'" fill="'+c+'" rx="2"/>';
          svg+='<text x="'+(x+bw/2)+'" y="'+(h-4)+'" text-anchor="middle" fill="#8ea0b8" font-size="9">'+esc(d.label)+'</text>';
          svg+='<text x="'+(x+bw/2)+'" y="'+(y-3)+'" text-anchor="middle" fill="#8ea0b8" font-size="7">'+num(d.val,5)+'</text>';
        });
        svg+='<text x="4" y="'+mid+'" fill="#8ea0b8" font-size="8" dominant-baseline="middle">0</text>';
        svg+='</svg>';
        return svg;
      }

      return `
        <div class="section-divider"></div>
        <h3>Quantile Shape & Rolling Stability / 分位收益形状与滚动稳定性</h3>
    ${CHART_GUIDES.quantileShape}
        <div style="margin:6px 0;display:flex;gap:6px;flex-wrap:wrap">
          ${sh.quantile_shape_class?shapeBadge(sh.quantile_shape_class):''}
          ${st.stability_class?stabilityBadge(st.stability_class):''}
          ${dc.decile_shape_class?decileShapeBadge(dc.decile_shape_class):''}
          ${dc.shape_consistency_with_q5?shapeConsistencyBadge(dc.shape_consistency_with_q5):''}
          ${dc.expected_direction?`<span class="shape-badge" style="background:#334155;color:#e2e8f0">Dir: ${esc(dc.expected_direction)}</span>`:''}
          ${dc.direction_handling?`<span class="shape-badge" style="background:#334155;color:#e2e8f0">${esc(dc.direction_handling)}</span>`:''}
        </div>
        <div class="metric-grid">
          ${st.stability_score!==null&&st.stability_score!==undefined?metricRow(renderTooltip('Stability Score'),num(st.stability_score,1)):''}
          ${st.ic_positive_month_rate!==null&&st.ic_positive_month_rate!==undefined?metricRow('IC Win% IC月胜率',pct(st.ic_positive_month_rate)):''}
          ${sh.monotonicity_score!==null&&sh.monotonicity_score!==undefined?metricRow('Monotonicity 单调性',num(sh.monotonicity_score,2)):''}
          ${sh.monotonicity_class?metricRow('Mono. Class 单调性分类','<span style="font-size:10px">'+esc(sh.monotonicity_class)+'</span>'):''}
          ${sh.q_spread_return!==null&&sh.q_spread_return!==undefined?metricRow(renderTooltip('Q Spread Return'),num(sh.q_spread_return,6)):''}
          ${sh.q_spearman_corr!==null&&sh.q_spearman_corr!==undefined?metricRow(renderTooltip('Q Spearman'),num(sh.q_spearman_corr,4)):''}
          ${sh.positive_spread_month_rate!==null&&sh.positive_spread_month_rate!==undefined?metricRow(renderTooltip('Positive Spread%'),pct(sh.positive_spread_month_rate)):''}
          ${dc.direction_aware_spearman_corr!==null&&dc.direction_aware_spearman_corr!==undefined?metricRow(renderTooltip('Dir-aware ρ'),num(dc.direction_aware_spearman_corr,4)):''}
          ${dc.direction_aware_monotonicity_class?metricRow(renderTooltip('Decile Mono.'),'<span style="font-size:10px">'+esc(dc.direction_aware_monotonicity_class)+'</span>'):''}
          ${dc.tail_concentration_class?metricRow(renderTooltip('Tail Conc.'),dc.tail_concentration_class?tailConcBadge(dc.tail_concentration_class):'—'):''}
          ${st.recent_vs_full_ic_delta!==null&&st.recent_vs_full_ic_delta!==undefined?metricRow(renderTooltip('Recent ΔIC'),num(st.recent_vs_full_ic_delta,4)):''}
          ${st.recent_vs_full_ls_delta!==null&&st.recent_vs_full_ls_delta!==undefined?metricRow(renderTooltip('Recent ΔLS'),num(st.recent_vs_full_ls_delta,6)):''}
        </div>

        ${qr.length?`
        <div class="chart-container">
          <div class="chart-title">Q1–Q5 Quantile Shape (expected-order mean returns) · 分位收益形状（预期方向排序）</div>
          ${qBarChart(qr,500,130)}
        </div>`:''}

        ${eodr.length?`
        <div class="chart-container">
          <div class="chart-title">Expected-order decile D1–D10 returns · 预期方向十分位收益</div>
          ${decileBarChart(eodr,600,130)}
        </div>`:''}

        ${(()=>{
          const sChart=stabilityMiniChart(st,400,110);
          if(!sChart)return '';
          return '<div class="chart-container"><div class="chart-title">Rolling IC/LS (3M & 6M latest) · 滚动IC/LS</div>'+sChart+'</div>';
        })()}

        ${sh.note_zh||dc.note_zh||st.note_zh?`
        <div style="margin:6px 0">
          ${sh.note_zh?`<div class="bilingual"><div class="zh" style="font-size:11px"><strong>Q5 Shape 分位形状:</strong> ${esc(sh.note_zh)}</div><div class="en" style="font-size:10px;color:var(--muted)">${esc(sh.note_en)}</div></div>`:''}
          ${st.note_zh?`<div class="bilingual" style="margin-top:4px"><div class="zh" style="font-size:11px"><strong>Stability 稳定性:</strong> ${esc(st.note_zh)}</div><div class="en" style="font-size:10px;color:var(--muted)">${esc(st.note_en)}</div></div>`:''}
          ${dc.note_zh?`<div class="bilingual" style="margin-top:4px"><div class="zh" style="font-size:11px"><strong>Decile 十分位:</strong> ${esc(dc.note_zh)}</div><div class="en" style="font-size:10px;color:var(--muted)">${esc(dc.note_en)}</div></div>`:''}
        </div>`:''}

        ${dc.shape_consistency_with_q5?`
        <div class="shape-caveat">
          <strong>⚠ Shape consistency 形状一致性:</strong> ${esc(dc.shape_consistency_with_q5)}<br>
          <span style="color:var(--muted)">Q5 quantile classification: ${esc(dc.q5_shape_class_from_pm26||'—')}. Decile shape may reveal nonlinear effects not visible in 5-bucket quantile analysis.<br>
          Q5分位分类: ${esc(dc.q5_shape_class_from_pm26||'—')}。十分位形状可能揭示5桶分位分析中不可见的非线性效应。</span>
        </div>`:''}
      `;
    })()}

    ${f.cap_liq_capacity_risk_class?`
    <div class="section-divider"></div>
    <h3>Capacity / Liquidity Proxy Diagnostics / 容量 / 流动性代理诊断</h3>
    <div style="margin:6px 0;display:flex;gap:6px;flex-wrap:wrap">
      ${capBadge(f.cap_liq_capacity_risk_class,CAP_RISK_LABELS)}
      ${capBadge(f.cap_liq_liquidity_risk_class,LIQ_RISK_LABELS)}
      ${capBadge(f.cap_liq_capacity_liquidity_class,CAP_LIQ_CLASS_LABELS)}
      ${f.cap_liq_volume_concentration_class?capBadge(f.cap_liq_volume_concentration_class,VOL_CONC_LABELS):''}
      ${f.cap_liq_factor_quality_cross_flag?capBadge(f.cap_liq_factor_quality_cross_flag,CROSS_FLAG_LABELS):''}
    </div>
    <div style="margin:4px 0;font-size:10px;color:var(--muted)">Proxy Method 代理方法: ${esc(f.cap_liq_proxy_method||'—')}</div>
    <div class="metric-grid">
      ${f.cap_liq_avg_turnover!==null&&f.cap_liq_avg_turnover!==undefined?metricRow(renderTooltip('Avg Turnover'),num(f.cap_liq_avg_turnover,4,false)):''}
      ${f.cap_liq_median_turnover!==null&&f.cap_liq_median_turnover!==undefined?metricRow(renderTooltip('Median Turnover'),num(f.cap_liq_median_turnover,4,false)):''}
      ${f.cap_liq_p90_turnover!==null&&f.cap_liq_p90_turnover!==undefined?metricRow(renderTooltip('P90 Turnover'),num(f.cap_liq_p90_turnover,4,false)):''}
      ${f.cap_liq_selected_basket_volume_median!==null&&f.cap_liq_selected_basket_volume_median!==undefined?metricRow(renderTooltip('Basket Vol Median'),f.cap_liq_selected_basket_volume_median!==null?Number(f.cap_liq_selected_basket_volume_median).toLocaleString('en',{maximumFractionDigits:0}):'—'):''}
      ${f.cap_liq_selected_basket_volume_p10!==null&&f.cap_liq_selected_basket_volume_p10!==undefined?metricRow(renderTooltip('Basket Vol P10'),f.cap_liq_selected_basket_volume_p10!==null?Number(f.cap_liq_selected_basket_volume_p10).toLocaleString('en',{maximumFractionDigits:0}):'—'):''}
      ${f.cap_liq_selected_symbol_count_median!==null?metricRow('Symbol Count Med 中位符号数',f.cap_liq_selected_symbol_count_median!==null?Math.round(Number(f.cap_liq_selected_symbol_count_median)):'—'):''}
      ${f.cap_liq_long_basket_volume_median!==null&&f.cap_liq_long_basket_volume_median!==undefined?metricRow('Long Basket Vol 多头篮子成交量',f.cap_liq_long_basket_volume_median!==null?Number(f.cap_liq_long_basket_volume_median).toLocaleString('en',{maximumFractionDigits:0}):'—'):''}
      ${f.cap_liq_short_basket_volume_median!==null&&f.cap_liq_short_basket_volume_median!==undefined?metricRow('Short Basket Vol 空头篮子成交量',f.cap_liq_short_basket_volume_median!==null?Number(f.cap_liq_short_basket_volume_median).toLocaleString('en',{maximumFractionDigits:0}):'—'):''}
      ${f.cap_liq_low_volume_symbol_share!==null&&f.cap_liq_low_volume_symbol_share!==undefined?metricRow(renderTooltip('Low-Vol Share'),pct(f.cap_liq_low_volume_symbol_share)):''}
      ${f.cap_liq_selected_top_symbol_volume_share_median!==null?metricRow(renderTooltip('Top Symbol Vol Share'),pct(f.cap_liq_selected_top_symbol_volume_share_median)):''}
    </div>

    <div style="margin-top:8px;font-size:11px;font-weight:600;color:var(--muted)">Capacity Estimates 容量估计 (USD)</div>
    <div class="metric-grid">
      ${f.cap_liq_capacity_at_1pct!==null&&f.cap_liq_capacity_at_1pct!==undefined?metricRow(renderTooltip('1% Participation'),f.cap_liq_capacity_at_1pct!==null?'$'+Number(f.cap_liq_capacity_at_1pct).toLocaleString('en',{maximumFractionDigits:0}):'—'):''}
      ${f.cap_liq_capacity_at_5pct!==null&&f.cap_liq_capacity_at_5pct!==undefined?metricRow(renderTooltip('5% Participation'),f.cap_liq_capacity_at_5pct!==null?'$'+Number(f.cap_liq_capacity_at_5pct).toLocaleString('en',{maximumFractionDigits:0}):'—'):''}
      ${f.cap_liq_capacity_at_10pct!==null&&f.cap_liq_capacity_at_10pct!==undefined?metricRow(renderTooltip('10% Participation'),f.cap_liq_capacity_at_10pct!==null?'$'+Number(f.cap_liq_capacity_at_10pct).toLocaleString('en',{maximumFractionDigits:0}):'—'):''}
    </div>

    <div style="margin-top:8px;font-size:11px;font-weight:600;color:var(--muted)">Participation Rates by Notional 参与率（按名义金额）</div>
    <div class="metric-grid">
      ${f.cap_liq_participation_100k_median!==null&&f.cap_liq_participation_100k_median!==undefined?metricRow(renderTooltip('$100K Median'),pct(f.cap_liq_participation_100k_median)):''}
      ${f.cap_liq_participation_100k_p10!==null&&f.cap_liq_participation_100k_p10!==undefined?metricRow(renderTooltip('$100K P10'),pct(f.cap_liq_participation_100k_p10)):''}
      ${f.cap_liq_participation_1M_median!==null&&f.cap_liq_participation_1M_median!==undefined?metricRow(renderTooltip('$1M Median'),pct(f.cap_liq_participation_1M_median)):''}
      ${f.cap_liq_participation_1M_p10!==null&&f.cap_liq_participation_1M_p10!==undefined?metricRow(renderTooltip('$1M P10'),pct(f.cap_liq_participation_1M_p10)):''}
      ${f.cap_liq_participation_10M_median!==null&&f.cap_liq_participation_10M_median!==undefined?metricRow(renderTooltip('$10M Median'),pct(f.cap_liq_participation_10M_median)):''}
      ${f.cap_liq_participation_10M_p10!==null&&f.cap_liq_participation_10M_p10!==undefined?metricRow(renderTooltip('$10M P10'),pct(f.cap_liq_participation_10M_p10)):''}
    </div>

    <div class="cap-caveat">
      <strong>⚠ Selected-basket proxy warning · 选中篮子代理警告</strong><br>
      <span style="color:var(--muted)">These are capacity/liquidity proxies based on selected-basket volume and turnover. They are not order-book simulation, slippage estimates, or real execution capacity.<br>
      这些是基于选中篮子成交量与换手率的容量 / 流动性代理指标，不是订单簿模拟、滑点估计或真实可交易容量结论。</span>
    </div>
    <div style="margin-top:6px;font-size:10px;color:var(--muted)">
      <strong>Interpretation 解读:</strong><br>
      <span style="font-size:10px">Capacity estimates assume uniform daily volume distribution; real liquidity is clustered. Participation rates show how much of daily selected-basket volume a notional allocation would consume. Lower is better.<br>
      容量估计假设每日成交量均匀分布；真实流动性是集中的。参与率显示特定名义金额占每日选中篮子成交量的比例，越低越好。</span>
    </div>
    `:`<div class="section-divider"></div><h3>Capacity / Liquidity Proxy Diagnostics / 容量 / 流动性代理诊断</h3><div style="margin:6px 0;font-size:11px;color:var(--muted)">N/A — No capacity/liquidity data available<br>无容量/流动性数据</div>`}

    ${f.profile_class?`
    <div class="section-divider"></div>
    <h3>Unified Factor Profile / 统一因子画像</h3>
    <div style="margin:6px 0;display:flex;gap:6px;flex-wrap:wrap">
      ${profileClassBadge(f.profile_class)}
      ${f.workflow_ready_status?workflowReadyBadge(f.workflow_ready_status):''}
      ${f.evidence_status?evidenceStatusBadge(f.evidence_status):''}
      ${f.profile_confidence?scConfBadge(f.profile_confidence):''}
      ${f.recommended_research_action?researchActionBadge(f.recommended_research_action):''}
    </div>
    <div class="metric-grid">
      ${f.profile_score!==null&&f.profile_score!==undefined?metricRow(renderTooltip('Profile Score'),'<strong style="font-size:16px">'+Number(f.profile_score).toFixed(1)+'</strong>/100'):''}
      ${f.evidence_completeness_rate!==null?metricRow(renderTooltip('Evidence Completeness'),pct(f.evidence_completeness_rate)):''}
      ${f.registry_or_data_status?metricRow('Registry Status 注册状态',esc(f.registry_or_data_status)):''}
      ${f.cluster_member_role?metricRow(renderTooltip('Cluster Role'),esc(f.cluster_member_role)):''}
      ${f.marginal_information_class?metricRow(renderTooltip('Marginal Info'),esc(f.marginal_information_class)):''}
      ${f.source_artifact_count?metricRow('Source Artifacts 源工件数',f.source_artifact_count):''}
    </div>

    ${f.primary_strength_zh||f.primary_risk_zh?`
    <div style="margin:6px 0">
      ${f.primary_strength_zh?`<div class="bilingual"><div class="zh" style="font-size:11px"><strong style="color:var(--green)">Strength 优势:</strong> ${esc(f.primary_strength_zh)}</div><div class="en" style="font-size:10px;color:var(--muted)">${esc(f.primary_strength_en)}</div></div>`:''}
      ${f.primary_risk_zh?`<div class="bilingual" style="margin-top:4px"><div class="zh" style="font-size:11px"><strong style="color:var(--amber)">Risk 风险:</strong> ${esc(f.primary_risk_zh)}</div><div class="en" style="font-size:10px;color:var(--muted)">${esc(f.primary_risk_en)}</div></div>`:''}
    </div>`:''}

    ${f.profile_summary_zh?`
    <div class="bilingual" style="margin:6px 0;background:var(--panel2);border:1px solid var(--border);border-radius:6px;padding:8px">
      <div class="zh" style="font-size:12px">${esc(f.profile_summary_zh)}</div>
      <div class="en" style="font-size:10px;color:var(--muted)">${esc(f.profile_summary_en)}</div>
    </div>`:''}

    ${f.workflow_missing_or_stale_blocks?`
    <div style="margin:6px 0;font-size:11px;color:var(--amber)">⚠ Missing/stale blocks 缺失/过时模块: ${esc(f.workflow_missing_or_stale_blocks)}</div>`:''}

    <h4 style="margin:10px 0 4px;font-size:11px;color:var(--muted)">Component Scores 组件分数 (10 dimensions 维度)</h4>
    ${(()=>{
      const comps=[
        ['standalone_quality','独立质量',f.comp_standalone_quality],
        ['paper','纸面组合',f.comp_paper],
        ['cost','费用',f.comp_cost],
        ['regime','市场状态',f.comp_regime],
        ['shape','形状',f.comp_shape],
        ['stability','稳定性',f.comp_stability],
        ['capacity','容量',f.comp_capacity],
        ['redundancy','冗余',f.comp_redundancy],
        ['marginal_info','边际信息',f.comp_marginal_info],
        ['evidence_completeness','证据完整',f.comp_evidence_completeness],
      ];
      const hasAny=comps.some(c=>c[2]!==null&&c[2]!==undefined);
      if(!hasAny)return '<div class="small">No component scores</div>';
      return comps.map(([key,label,score])=>{
        if(score===null||score===undefined)return '';
        const w=Math.max(2,Math.min(100,Number(score)));
        const c=scBarColor(score);
        return `<div class="sc-bar-wrap"><span class="sc-bar-label" title="${esc(label)}">${esc(label)}</span><div class="sc-bar-track"><div class="sc-bar-fill ${c}" style="width:${w}%">${Number(score).toFixed(0)}</div></div></div>`;
      }).join('')+
      `<div class="sc-bar-wrap" style="margin-top:4px;border-top:1px solid var(--border);padding-top:4px"><span class="sc-bar-label" style="font-weight:700">Profile Score 画像分数</span><div class="sc-bar-track"><div class="sc-bar-fill ${scBarColor(f.profile_score)}" style="width:${Math.max(2,Math.min(100,Number(f.profile_score||0)))}%">${Number(f.profile_score||0).toFixed(1)}</div></div></div>`;
    })()}

    <h4 style="margin:10px 0 4px;font-size:11px;color:var(--muted)">Evidence Matrix 证据矩阵 (15 blocks 模块)</h4>
    <div style="display:flex;gap:3px;flex-wrap:wrap;margin:4px 0">
      ${evBlockBadge('Scorecard',f.ev_has_quality_scorecard)}
      ${evBlockBadge('Diagnostics',f.ev_has_diagnostics_summary)}
      ${evBlockBadge('Redundancy',f.ev_has_redundancy_summary)}
      ${evBlockBadge('Cluster',f.ev_has_redundancy_cluster_members)}
      ${evBlockBadge('Marginal',f.ev_has_marginal_information)}
      ${evBlockBadge('Paper',f.ev_has_paper_summary)}
      ${evBlockBadge('FeeSens',f.ev_has_fee_sensitivity)}
      ${evBlockBadge('Regime',f.ev_has_regime_exposure)}
      ${evBlockBadge('QShape',f.ev_has_quantile_shape)}
      ${evBlockBadge('RollStab',f.ev_has_rolling_stability)}
      ${evBlockBadge('Decile',f.ev_has_decile_shape)}
      ${evBlockBadge('CapLiq',f.ev_has_capacity_liquidity)}
      ${evBlockBadge('Values',f.ev_has_factor_values)}
      ${evBlockBadge('LevelEval',f.ev_has_factor_level_evaluation)}
      ${evBlockBadge('Profile',f.ev_has_unified_profile)}
    </div>
    ${(()=>{
      const evBlocks=[f.ev_has_quality_scorecard,f.ev_has_diagnostics_summary,f.ev_has_redundancy_summary,f.ev_has_redundancy_cluster_members,f.ev_has_marginal_information,f.ev_has_paper_summary,f.ev_has_fee_sensitivity,f.ev_has_regime_exposure,f.ev_has_quantile_shape,f.ev_has_rolling_stability,f.ev_has_decile_shape,f.ev_has_capacity_liquidity,f.ev_has_factor_values,f.ev_has_factor_level_evaluation,f.ev_has_unified_profile];
      const present=evBlocks.filter(Boolean).length;
      const total=evBlocks.length;
      const rate=total?Math.round(present/total*100):0;
      const color=rate>=80?'var(--green)':rate>=60?'var(--amber)':'var(--red)';
      return `<div style="margin:4px 0;font-size:10px;color:var(--muted)">Evidence completeness 证据完整率: <strong style="color:${color}">${present}/${total} (${rate}%)</strong>${f.evidence_completeness_rate!==null?' · Profile rate 画像完整率: '+pct(f.evidence_completeness_rate):''}</div>`;
    })()}

    ${f.source_artifacts?`
    <h4 style="margin:10px 0 4px;font-size:11px;color:var(--muted)">Source Lineage 源工件 (${f.source_artifact_count||0})</h4>
    <div style="display:flex;gap:3px;flex-wrap:wrap;font-size:9px">
      ${f.source_artifacts.split('|').map(a=>`<span class="bucket-badge">${esc(a)}</span>`).join(' ')}
    </div>`:''}

    <div class="up-caveat">
      <strong>⚠ Unified profiles are research diagnostics, not trading signals / 统一画像是研究诊断，非交易信号</strong><br>
      <span style="color:var(--muted)">Profile scores summarize evidence completeness and cross-dimensional quality. They do not select signals, construct portfolios, or recommend trading.<br>
      画像分数汇总证据完整性与跨维度质量。它不选择信号、不构建组合，也不构成交易建议。不是交易策略。</span>
    </div>
    `:`<div class="section-divider"></div><h3>Unified Factor Profile / 统一因子画像</h3><div style="margin:6px 0;font-size:11px;color:var(--muted)">N/A — No unified profile data available<br>无统一画像数据</div>`}
  `;
}

// ── Init ──
const searchEl=document.getElementById('search');
[searchEl,familyFilter,qualityFilter,horizonFilter,scClassFilter,scConfFilter,paperViabFilter,regimeFilter].forEach(el=>el.addEventListener('input',renderTable));
[familyFilter,qualityFilter,horizonFilter,scClassFilter,scConfFilter,paperViabFilter,regimeFilter].forEach(el=>el.addEventListener('change',renderTable));

// Set initial sort arrow
const initSortTh=document.querySelector(`th[data-col="${sortCol}"]`);
if(initSortTh) initSortTh.innerHTML+=' ▼';

renderTable();
if(factors.length)renderDetail(factors[0].factor_id);

document.getElementById('genTime').textContent='Generated: '+(S.page_generation_time||new Date().toISOString().slice(0,16));
</script>
</body>
</html>"""


# ── Main ────────────────────────────────────────────────────────────────────
def render() -> str:
    payload = build_payload()
    payload_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    # Escape for embedding in <script> tag
    payload_json = payload_json.replace("<", "\\u003c").replace("</", "<\\/")
    return HTML_TEMPLATE.replace("PAYLOAD_PLACEHOLDER", payload_json)


if __name__ == "__main__":
    html_out = render()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html_out, encoding="utf-8")
    print(f"Wrote {OUT} ({len(html_out):,} bytes)")
