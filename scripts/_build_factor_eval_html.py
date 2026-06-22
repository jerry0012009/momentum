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


def load_json(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
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

        best_hz = ss(drow.get("best_horizon", "1h")) or "1h"

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

        factors.append(factor)

    return {"summary": summary, "factors": factors}


# ── HTML template ───────────────────────────────────────────────────────────
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Factor Library — Evaluation 因子评价</title>
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
.layout{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(340px,.6fr);gap:14px;align-items:start}
@media(max-width:1100px){.layout{grid-template-columns:1fr}}
.card{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:12px;margin-bottom:12px}
.detail{position:sticky;top:16px}
.controls{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}
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

<div id="statsSection"></div>

<div id="scorecardSummarySection"></div>

<div id="paperSummarySection"></div>
<div id="regimeSummarySection"></div>

<div id="caveatsSection"></div>

<div class="layout">
  <main>
    <div class="card">
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
  }

  card.innerHTML=`
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

    <div class="kv">
      <div>Data Source 数据源</div><div>${esc(f.data_source_type)}</div>
      <div>Required Columns 必要列</div><div>${esc(f.required_columns)}</div>
      <div>Horizon Notes 视野说明</div><div>${esc(f.horizon_notes_zh)}<br><span class="small">${esc(f.horizon_notes_en)}</span></div>
      <div>Status Explanation 状态说明</div><div>${esc(f.status_explanation_zh)}<br><span class="small">${esc(f.status_explanation_en)}</span></div>
    </div>

    <div class="section-divider"></div>
    <h3>Metadata Quality 元数据质量</h3>
    <div>${qualBadge(f.metadata_quality)}</div>
    ${f.needs_human_review==='yes'?'<div style="color:var(--amber);font-size:11px;margin:4px 0">⚠ Needs human review 需人工复核</div>':''}
    ${f.qa_notes_zh?`<div class="bilingual"><div class="zh" style="font-size:11px">${esc(f.qa_notes_zh)}</div><div class="en" style="font-size:10px">${esc(f.qa_notes_en)}</div></div>`:''}
    ${f.qa_reason?`<div class="small">Reason: ${esc(f.qa_reason)}</div>`:''}

    <div class="section-divider"></div>
    <h3>Best Horizon Metrics 最优视野指标 (${esc(f.best_horizon)})</h3>
    <div class="metric-grid">
      ${metricRow('RankIC Mean',num(f.rankic_mean),mcls(f.rankic_mean))}
      ${metricRow('RankIC Std',num(f.rankic_std,4,false))}
      ${metricRow('ICIR',num(f.rankic_ir,3))}
      ${metricRow('IC t-stat',num(f.rankic_t_stat,2,false))}
      ${metricRow('IC Win Rate IC胜率',pct(f.monthly_ic_positive_rate))}
      ${metricRow('LS Mean LS均值',num(f.long_short_mean,6))}
      ${metricRow('LS Std LS标准差',num(f.long_short_std,6))}
      ${metricRow('Sharpe',num(f.long_short_sharpe,2),mcls(f.long_short_sharpe,1.5,0.8))}
      ${metricRow('Ann Return 年化收益',pct(f.long_short_annualized_return))}
      ${metricRow('Ann Vol 年化波动',pct(f.long_short_annualized_vol))}
      ${metricRow('Max Drawdown 最大回撤',pct(f.long_short_max_drawdown))}
      ${metricRow('LS Win Rate LS月胜率',pct(f.long_short_positive_month_rate))}
      ${metricRow('Coverage 覆盖率',pct(f.coverage_rate))}
    </div>

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
      <div>Nearest Factor 最近相似因子</div><div>${esc(f.nearest_factor||'—')}</div>
      <div>Nearest abs Spearman 最近|Spearman|</div><div>${f.nearest_abs_spearman_corr!==null?Number(f.nearest_abs_spearman_corr).toFixed(4):'—'}</div>
      <div>Strongest Redundancy 最强冗余等级</div><div>${f.strongest_redundancy_level?redundancyLevelBadge(f.strongest_redundancy_level):'—'}</div>
      <div>Redundancy Confidence 冗余置信度</div><div>${f.redundancy_confidence?scConfBadge(f.redundancy_confidence):'—'}</div>
      <div>Valid Pairs 有效对</div><div>${f.valid_redundancy_pair_count!==null?Math.round(Number(f.valid_redundancy_pair_count))+' / '+Math.round(Number(f.expected_redundancy_pair_count)):'—'}</div>
      <div>Valid Pair Coverage 有效对覆盖率</div><div>${f.valid_redundancy_pair_coverage!==null?pct(f.valid_redundancy_pair_coverage):'—'}</div>
      <div>Insufficient Overlap 重叠不足对</div><div>${f.insufficient_overlap_pair_count!==null?Math.round(Number(f.insufficient_overlap_pair_count)):'—'}</div>
      <div>Cluster 聚类</div><div>${f.redundancy_cluster_id!==null?'#'+Math.round(Number(f.redundancy_cluster_id))+' ('+Math.round(Number(f.redundancy_cluster_size||0))+' factors)':'—'}</div>
    </div>
    <div style="margin-top:6px;font-size:10px;color:var(--muted)">
      冗余分析是研究相似性诊断，不是删除因子的理由。高冗余因子可保留用于方向/视野多样性。
      <br>Redundancy analysis is a research similarity diagnostic, not a reason by itself to delete a factor. High-redundancy factors may be retained for direction/horizon diversity.
    </div>

    <div class="section-divider"></div>
    <h3>Monthly RankIC 月度RankIC (${esc(f.best_horizon)})</h3>
    <div class="chart-container">
      <div class="chart-title">Monthly RankIC (adj) · 月度调整RankIC</div>
      ${svgLineChart(f.monthly_ic,'rank_ic_adj',600,140)}
    </div>

    <h3>Monthly Long-Short Return 月度多空收益 (${esc(f.best_horizon)})</h3>
    <div class="chart-container">
      <div class="chart-title">Monthly LS Return · 月度多空收益</div>
      ${svgBarChart(f.monthly_ls,'long_short_return',600,120)}
    </div>

    <h3>Cumulative Long-Short Curve 累计多空曲线 (${esc(f.best_horizon)})</h3>
    <div class="chart-container">
      <div class="chart-title">Cumulative LS (blue) with drawdown (red) · 累计多空(蓝)及回撤(红)</div>
      ${svgCumCurve(f.cum_curve,600,160)}
    </div>

    <h3>Drawdown Summary 回撤概要</h3>
    <div class="metric-grid">
      ${metricRow('Max DD 最大回撤',pct(f.long_short_max_drawdown))}
      ${metricRow('LS Month Win% 月胜率',pct(f.long_short_positive_month_rate))}
      ${metricRow('LS Sharpe',num(f.long_short_sharpe,2),mcls(f.long_short_sharpe,1.5,0.8))}
    </div>

    ${f.paper_viability_class?`
    <div class="section-divider"></div>
    <h3>Single-Factor Paper Portfolio / 单因子纸面组合</h3>
    <div style="margin:6px 0">
      ${paperViabBadge(f.paper_viability_class)}
      ${f.cost_sensitivity_class?costSensBadge(f.cost_sensitivity_class):''}
    </div>
    <div class="metric-grid">
      ${metricRow('Gross Sharpe 毛夏普',num(f.gross_sharpe,2))}
      ${metricRow('Gross Return 毛收益',num(f.gross_total_return,2))}
      ${metricRow('Max DD 最大回撤',pct(f.paper_max_drawdown))}
      ${metricRow('Positive Mo% 月胜率',pct(f.paper_positive_month_rate))}
      ${metricRow('Avg Turnover 平均换手',pct(f.paper_avg_turnover))}
      ${metricRow('Median Turnover 中位换手',pct(f.paper_median_turnover))}
      ${metricRow('B/E Fee 盈亏平衡',f.break_even_fee_bps!==null&&f.break_even_fee_bps!==undefined?Math.round(Number(f.break_even_fee_bps))+' bps':'—')}
      ${metricRow('0bps Return',num(f.fee_0bps_total_return,2))}
      ${metricRow('5bps Return',num(f.fee_5bps_total_return,2))}
      ${metricRow('10bps Return',num(f.fee_10bps_total_return,2),f.fee_10bps_total_return!==null&&f.fee_10bps_total_return<0?'':''}
      ${metricRow('20bps Return',num(f.fee_20bps_total_return,2))}
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
    `:''}

    ${f.regime_dependency_class?`
    <div class="section-divider"></div>
    <h3>BTC / Market Regime Diagnostics / BTC / 市场状态诊断</h3>
    <div style="margin:6px 0">
      ${regimeBadge(f.regime_dependency_class)}
      ${f.main_regime_note_zh?`<span style="font-size:11px;margin-left:6px">${esc(f.main_regime_note_zh)} / ${esc(f.main_regime_note_en)}</span>`:''}
    </div>
    <div class="metric-grid">
      ${metricRow('Paper-BTC Corr',num(f.paper_return_btc_corr,4))}
      ${metricRow('Paper-BTC Beta',num(f.paper_return_btc_beta,4))}
      ${metricRow('LS-BTC Corr',num(f.long_short_btc_corr,4))}
      ${metricRow('LS-BTC Beta',num(f.long_short_btc_beta,4))}
      ${metricRow('IC-BTC Corr',num(f.ic_btc_return_corr,4))}
      ${metricRow('Bull−Bear Δ',num(f.bull_minus_bear_paper_return,4),f.bull_minus_bear_paper_return!==null?(f.bull_minus_bear_paper_return>=0?'strong':'watch'):'')}
      ${metricRow('HV−LV Δ',num(f.highvol_minus_lowvol_paper_return,4))}
      ${metricRow('DD−Normal Δ',num(f.drawdown_minus_normal_paper_return,4),f.drawdown_minus_normal_paper_return!==null?(f.drawdown_minus_normal_paper_return<0?'watch':''):'')}
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
    `:''}
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

document.getElementById('genTime').textContent='Generated: '+new Date().toISOString().slice(0,16);
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
