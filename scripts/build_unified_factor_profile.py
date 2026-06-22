#!/usr/bin/env python3
"""PM-32: Unified Factor Evaluation Workflow Contract & Factor Profile.

Builds:
  1. factor_evaluation_workflow_contract.json  — stage-level pipeline contract
  2. factor_evaluation_evidence_matrix.csv/json — evidence block availability per factor
  3. factor_unified_profile_summary.csv/json   — unified per-factor profile
  4. factor_profile_component_scores.csv        — component score detail
  5. factor_profile_payload.json                — compact page-ready payload
  6. factor_profile_manifest.json               — source lineage manifest

NOT production. NOT live trading. Research diagnostics only.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

# ── Paths ───────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
STATE_PATH = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_library_state.json"
DIAG_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_diagnostics"

# ── Component weights ───────────────────────────────────────────────────────
COMPONENT_WEIGHTS = {
    "standalone_quality": 0.18,
    "paper": 0.14,
    "cost": 0.08,
    "regime": 0.10,
    "shape": 0.10,
    "stability": 0.14,
    "capacity": 0.08,
    "redundancy": 0.08,
    "marginal_info": 0.07,
    "evidence_completeness": 0.03,
}

assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9, "Weights must sum to 1.0"

# ── Profile classes ─────────────────────────────────────────────────────────
PROFILE_CLASSES = [
    "HIGH_QUALITY_DISTINCT",
    "HIGH_QUALITY_BUT_REDUNDANT",
    "STABLE_BUT_CAPACITY_CONSTRAINED",
    "PROMISING_BUT_REGIME_DEPENDENT",
    "UNIQUE_BUT_WEAK",
    "BROAD_WATCHLIST",
    "LOW_PRIORITY_DIAGNOSTIC",
    "INCOMPLETE_EVIDENCE",
    "INSUFFICIENT_DATA",
]

# ── Research actions ────────────────────────────────────────────────────────
RESEARCH_ACTIONS = [
    "PRIORITIZE_FOR_REVIEW",
    "KEEP_AS_CLUSTER_REFERENCE",
    "REVIEW_AS_REDUNDANT_ALTERNATIVE",
    "WATCH_FOR_REGIME_DEPENDENCE",
    "WATCH_FOR_CAPACITY_RISK",
    "WATCH_FOR_STABILITY_RISK",
    "KEEP_AS_DIAGNOSTIC_PROBE",
    "LOWER_PRIORITY_REVIEW",
    "COMPLETE_MISSING_EVIDENCE",
    "INSUFFICIENT_DATA_REVIEW",
]

# ── Evidence block definitions ──────────────────────────────────────────────
# Maps evidence block name → (file, required?):
EVIDENCE_BLOCKS = {
    "quality_scorecard": ("factor_quality_scorecard.csv", True),
    "diagnostics_summary": ("factor_diagnostics_summary.csv", True),
    "redundancy_summary": ("factor_redundancy_summary.csv", True),
    "redundancy_cluster_members": ("factor_redundancy_cluster_members.csv", True),
    "marginal_information": ("factor_marginal_information_summary.csv", True),
    "paper_summary": ("single_factor_paper_summary.csv", True),
    "fee_sensitivity": ("single_factor_fee_sensitivity.csv", True),
    "regime_exposure": ("factor_regime_exposure_summary.csv", True),
    "quantile_shape": ("factor_quantile_shape_summary.csv", True),
    "rolling_stability": ("factor_rolling_stability_summary.csv", True),
    "decile_shape": ("factor_decile_shape_summary.csv", True),
    "capacity_liquidity": ("factor_capacity_liquidity_summary.csv", True),
}


def load_state() -> dict:
    """Load factor library state JSON."""
    with open(STATE_PATH) as f:
        return json.load(f)


def load_csv_safe(name: str) -> pd.DataFrame | None:
    """Load a CSV from DIAG_DIR, returning None on error."""
    path = DIAG_DIR / name
    if not path.exists():
        return None
    try:
        return pd.read_csv(path)
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: Workflow Contract
# ═══════════════════════════════════════════════════════════════════════════

def build_workflow_contract() -> dict:
    """Build the factor_evaluation_workflow_contract.json."""
    stage_definitions = [
        {
            "stage_id": "registry-integrity",
            "display_name_zh": "注册表完整性检查",
            "display_name_en": "Registry Integrity Check",
            "script": "scripts/check_factor_registry_integrity.py",
            "is_expensive": False,
            "inputs": ["factor_formula_registry.py"],
            "outputs": ["factor_registry_integrity_report.csv", "factor_registry_integrity_report.json"],
            "must_run_after": [],
            "what_it_answers_zh": "注册表中的因子定义是否完整、无重复、无冲突？",
            "what_it_answers_en": "Are factor definitions in the registry complete, non-duplicate, and conflict-free?",
        },
        {
            "stage_id": "catalog",
            "display_name_zh": "因子目录构建",
            "display_name_en": "Factor Catalog Build",
            "script": "scripts/build_factor_catalog.py + scripts/check_factor_catalog_integrity.py",
            "is_expensive": False,
            "inputs": ["factor_formula_registry.py"],
            "outputs": ["factor_catalog.csv", "factor_catalog.json"],
            "must_run_after": ["registry-integrity"],
            "what_it_answers_zh": "注册表中定义了哪些因子？它们的元数据和分类是否正确？",
            "what_it_answers_en": "Which factors are defined in the registry? Is their metadata and classification correct?",
        },
        {
            "stage_id": "values",
            "display_name_zh": "因子值计算",
            "display_name_en": "Factor Value Computation",
            "script": "scripts/build_factor_values.py",
            "is_expensive": False,
            "inputs": ["factor_formula_registry.py", "raw bars parquet"],
            "outputs": ["factor_values.parquet (per factor)"],
            "must_run_after": ["catalog"],
            "what_it_answers_zh": "每个因子在给定行情数据上的数值序列是什么？",
            "what_it_answers_en": "What are the time-series values for each factor on the given market data?",
        },
        {
            "stage_id": "direction-audit",
            "display_name_zh": "方向语义审计",
            "display_name_en": "Direction Semantics Audit",
            "script": "scripts/audit_factor_direction_semantics.py",
            "is_expensive": False,
            "inputs": ["factor_formula_registry.py"],
            "outputs": ["direction_semantics_audit/"],
            "must_run_after": ["values"],
            "what_it_answers_zh": "每个因子的预期方向（正/负）是否与实际IC方向一致？",
            "what_it_answers_en": "Does each factor's expected direction match its actual IC direction?",
        },
        {
            "stage_id": "evaluate",
            "display_name_zh": "因子级评估（昂贵）",
            "display_name_en": "Factor-Level Evaluation (EXPENSIVE)",
            "script": "scripts/evaluate_factors.py",
            "is_expensive": True,
            "inputs": ["factor_values.parquet", "labels.parquet"],
            "outputs": ["factor_level_rankic_summary.csv", "factor_level_quantile_return_summary.csv", "..."],
            "must_run_after": ["direction-audit"],
            "what_it_answers_zh": "每个因子在4个时间窗口上的RankIC、分位数回报、覆盖率等统计量是多少？",
            "what_it_answers_en": "What are the RankIC, quantile returns, coverage, and other statistics for each factor across 4 horizons?",
        },
        {
            "stage_id": "diagnostics",
            "display_name_zh": "诊断指标构建",
            "display_name_en": "Diagnostics Metrics Build",
            "script": "scripts/build_factor_diagnostics_metrics.py",
            "is_expensive": False,
            "inputs": ["factor_level_evaluation/", "factor_library_state.json"],
            "outputs": ["factor_diagnostics_summary.csv", "factor_monthly_ic_series.csv", "factor_monthly_long_short_series.csv"],
            "must_run_after": ["evaluate"],
            "what_it_answers_zh": "每个因子的关键诊断指标（RankIC、夏普比率、最大回撤等）是什么？",
            "what_it_answers_en": "What are the key diagnostic metrics (RankIC, Sharpe, max drawdown, etc.) for each factor?",
        },
        {
            "stage_id": "metadata",
            "display_name_zh": "双语元数据卡片",
            "display_name_en": "Bilingual Factor Cards",
            "script": "scripts/build_factor_bilingual_cards.py",
            "is_expensive": False,
            "inputs": ["factor_formula_registry.py"],
            "outputs": ["factor_bilingual_cards.csv", "factor_bilingual_cards.json"],
            "must_run_after": ["diagnostics"],
            "what_it_answers_zh": "每个因子的中英文描述、分类和元数据卡片内容是什么？",
            "what_it_answers_en": "What are the bilingual descriptions, classifications, and metadata card contents for each factor?",
        },
        {
            "stage_id": "scorecard",
            "display_name_zh": "质量评分卡",
            "display_name_en": "Quality Scorecard",
            "script": "scripts/build_factor_quality_scorecard.py",
            "is_expensive": False,
            "inputs": ["factor_diagnostics_summary.csv", "factor_monthly_ic_series.csv", "factor_bilingual_cards.csv"],
            "outputs": ["factor_quality_scorecard.csv", "factor_quality_scorecard.json"],
            "must_run_after": ["metadata"],
            "what_it_answers_zh": "每个因子的综合质量评分是多少？属于哪个质量等级？",
            "what_it_answers_en": "What is the comprehensive quality score for each factor? What quality class does it belong to?",
        },
        {
            "stage_id": "redundancy",
            "display_name_zh": "两两冗余矩阵（昂贵）",
            "display_name_en": "Pairwise Redundancy Matrix (EXPENSIVE)",
            "script": "scripts/build_factor_pairwise_redundancy_matrix.py",
            "is_expensive": True,
            "inputs": ["factor_values.parquet (all)", "factor_bilingual_cards.csv"],
            "outputs": ["factor_pairwise_redundancy.csv", "factor_redundancy_matrix_pearson.csv", "factor_redundancy_matrix_spearman.csv"],
            "must_run_after": ["scorecard"],
            "what_it_answers_zh": "任意两个因子之间的皮尔逊和斯皮尔曼相关性是多少？哪些因子是冗余的？",
            "what_it_answers_en": "What are the Pearson and Spearman correlations between any two factors? Which factors are redundant?",
        },
        {
            "stage_id": "cluster",
            "display_name_zh": "冗余聚类与边际信息（PM-31）",
            "display_name_en": "Redundancy Clustering & Marginal Information (PM-31)",
            "script": "scripts/build_factor_redundancy_cluster_diagnostics.py",
            "is_expensive": False,
            "inputs": ["factor_pairwise_redundancy.csv", "factor_quality_scorecard.csv"],
            "outputs": ["factor_redundancy_cluster_members.csv", "factor_marginal_information_summary.csv", "factor_redundancy_summary.csv"],
            "must_run_after": ["redundancy"],
            "what_it_answers_zh": "因子聚类结果是什么？每个因子的边际信息增量是多少？",
            "what_it_answers_en": "What are the factor clusters? What is the marginal information value of each factor?",
        },
        {
            "stage_id": "paper-diagnostics",
            "display_name_zh": "单因子纸面组合诊断（昂贵）",
            "display_name_en": "Single-Factor Paper Portfolio Diagnostics (EXPENSIVE)",
            "script": "scripts/build_single_factor_paper_portfolio_diagnostics.py",
            "is_expensive": True,
            "inputs": ["factor_values.parquet (all)", "bars_1h.parquet"],
            "outputs": ["single_factor_paper_summary.csv", "single_factor_fee_sensitivity.csv"],
            "must_run_after": ["cluster"],
            "what_it_answers_zh": "如果只用这一个因子构建纸面组合，扣除不同费率后表现如何？",
            "what_it_answers_en": "If only this factor is used to build a paper portfolio, how does it perform at different fee levels?",
        },
        {
            "stage_id": "paper-page-payload",
            "display_name_zh": "纸面组合页面载荷",
            "display_name_en": "Paper Page Payload",
            "script": "scripts/build_single_factor_paper_page_payload.py",
            "is_expensive": False,
            "inputs": ["single_factor_paper_summary.csv"],
            "outputs": ["paper_page_payload.json"],
            "must_run_after": ["paper-diagnostics"],
            "what_it_answers_zh": "纸面组合诊断结果如何格式化为页面可用的JSON载荷？",
            "what_it_answers_en": "How are the paper portfolio diagnostic results formatted into a page-ready JSON payload?",
        },
        {
            "stage_id": "regime",
            "display_name_zh": "市场状态诊断（PM-23）",
            "display_name_en": "Market Regime Diagnostics (PM-23)",
            "script": "scripts/build_factor_market_regime_diagnostics.py",
            "is_expensive": False,
            "inputs": ["bars_1h.parquet (BTC)", "factor_monthly_ic_series.csv", "single_factor_paper_summary.csv"],
            "outputs": ["factor_regime_exposure_summary.csv", "factor_regime_diagnostics_payload.json"],
            "must_run_after": ["paper-diagnostics"],
            "what_it_answers_zh": "因子在牛市/熊市/高波动/回撤期间的表现有何差异？",
            "what_it_answers_en": "How does the factor perform during bull/bear/high-vol/drawdown regimes?",
        },
        {
            "stage_id": "quantile-shape",
            "display_name_zh": "分位数形状诊断",
            "display_name_en": "Quantile Shape Diagnostics",
            "script": "scripts/build_factor_quantile_shape_diagnostics.py",
            "is_expensive": False,
            "inputs": ["factor_level_evaluation/"],
            "outputs": ["factor_quantile_shape_summary.csv"],
            "must_run_after": ["evaluate"],
            "what_it_answers_zh": "因子分位数回报是否呈单调递增/递减形状？",
            "what_it_answers_en": "Do quantile returns show monotonic increasing/decreasing shape?",
        },
        {
            "stage_id": "rolling-stability",
            "display_name_zh": "滚动稳定性诊断",
            "display_name_en": "Rolling Stability Diagnostics",
            "script": "scripts/build_factor_rolling_stability_diagnostics.py",
            "is_expensive": False,
            "inputs": ["factor_level_evaluation/"],
            "outputs": ["factor_rolling_stability_summary.csv"],
            "must_run_after": ["evaluate"],
            "what_it_answers_zh": "因子的IC和夏普比率在滚动窗口中是否稳定？",
            "what_it_answers_en": "Are the factor's IC and Sharpe ratio stable across rolling windows?",
        },
        {
            "stage_id": "decile-shape",
            "display_name_zh": "十分位形状诊断",
            "display_name_en": "Decile Shape Diagnostics",
            "script": "scripts/build_factor_decile_shape_diagnostics.py",
            "is_expensive": False,
            "inputs": ["factor_level_evaluation/"],
            "outputs": ["factor_decile_shape_summary.csv"],
            "must_run_after": ["evaluate"],
            "what_it_answers_zh": "因子十分位回报的非线性特征（U型、单调等）是什么？",
            "what_it_answers_en": "What are the nonlinearity characteristics (U-shape, monotonic, etc.) of decile returns?",
        },
        {
            "stage_id": "capacity-liquidity",
            "display_name_zh": "容量与流动性诊断",
            "display_name_en": "Capacity & Liquidity Diagnostics",
            "script": "scripts/build_factor_capacity_liquidity_diagnostics.py",
            "is_expensive": False,
            "inputs": ["factor_values.parquet", "bars_1h.parquet"],
            "outputs": ["factor_capacity_liquidity_summary.csv"],
            "must_run_after": ["paper-diagnostics"],
            "what_it_answers_zh": "因子在不同资金规模下的可执行容量和流动性风险是什么？",
            "what_it_answers_en": "What is the executable capacity and liquidity risk at different capital levels?",
        },
        {
            "stage_id": "profile",
            "display_name_zh": "统一因子画像（PM-32）",
            "display_name_en": "Unified Factor Profile (PM-32)",
            "script": "scripts/build_unified_factor_profile.py",
            "is_expensive": False,
            "inputs": [
                "factor_quality_scorecard.csv", "factor_diagnostics_summary.csv",
                "factor_redundancy_summary.csv", "factor_redundancy_cluster_members.csv",
                "factor_marginal_information_summary.csv", "single_factor_paper_summary.csv",
                "single_factor_fee_sensitivity.csv", "factor_regime_exposure_summary.csv",
                "factor_quantile_shape_summary.csv", "factor_rolling_stability_summary.csv",
                "factor_decile_shape_summary.csv", "factor_capacity_liquidity_summary.csv",
                "factor_library_state.json",
            ],
            "outputs": [
                "factor_evaluation_workflow_contract.json",
                "factor_evaluation_evidence_matrix.csv", "factor_evaluation_evidence_matrix.json",
                "factor_unified_profile_summary.csv", "factor_unified_profile_summary.json",
                "factor_profile_component_scores.csv",
                "factor_profile_payload.json", "factor_profile_manifest.json",
            ],
            "must_run_after": [
                "scorecard", "cluster", "paper-diagnostics", "regime",
                "quantile-shape", "rolling-stability", "decile-shape", "capacity-liquidity",
            ],
            "what_it_answers_zh": "综合所有诊断维度，每个因子的统一画像、评分和优先级是什么？",
            "what_it_answers_en": "Across all diagnostic dimensions, what is the unified profile, score, and priority for each factor?",
        },
        {
            "stage_id": "staleness",
            "display_name_zh": "过时性检查",
            "display_name_en": "Staleness Check",
            "script": "scripts/check_factor_library_staleness.py",
            "is_expensive": False,
            "inputs": ["factor_library_state.json", "factor_diagnostics_summary.csv", "..."],
            "outputs": ["factor_library_staleness_report.csv", "factor_library_staleness_report.json"],
            "must_run_after": ["profile"],
            "what_it_answers_zh": "哪些产物已经过时？需要重新运行哪些阶段？",
            "what_it_answers_en": "Which artifacts are stale? Which stages need to be re-run?",
        },
        {
            "stage_id": "page",
            "display_name_zh": "页面构建",
            "display_name_en": "Page Build",
            "script": "scripts/_build_factor_eval_html.py",
            "is_expensive": False,
            "inputs": ["factor_diagnostics_summary.csv", "factor_quality_scorecard.csv", "..."],
            "outputs": ["factor-evaluation.html"],
            "must_run_after": ["staleness"],
            "what_it_answers_zh": "所有诊断结果如何渲染为人类可读的因子评估页面？",
            "what_it_answers_en": "How are all diagnostic results rendered into a human-readable factor evaluation page?",
        },
        {
            "stage_id": "state",
            "display_name_zh": "状态文件生成",
            "display_name_en": "State File Generation",
            "script": "scripts/build_factor_library_state.py",
            "is_expensive": False,
            "inputs": ["(all upstream artifacts)"],
            "outputs": ["factor_library_state.json", "factor_library_state.md"],
            "must_run_after": ["page"],
            "what_it_answers_zh": "当前因子库的完整状态快照是什么？",
            "what_it_answers_en": "What is the complete state snapshot of the current factor library?",
        },
    ]

    stage_order = [s["stage_id"] for s in stage_definitions]

    contract = {
        "workflow_name": "factor_evaluation_workflow",
        "workflow_version": "1.0.0",
        "purpose": "Canonical evaluation pipeline for the crypto top-50 factor library: from registry through diagnostics, redundancy, paper portfolio, regime analysis, unified profile, and page-ready outputs.",
        "not_production_disclaimer": "This workflow and all its outputs are research diagnostics ONLY. NOT production. NOT live trading. NOT investment advice. No factor should be deployed, traded, or used for allocation without independent validation.",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stage_order": stage_order,
        "stage_definitions": stage_definitions,
        "required_outputs_by_stage": {
            s["stage_id"]: s["outputs"] for s in stage_definitions
        },
        "expensive_stage_flags": {
            s["stage_id"]: s["is_expensive"] for s in stage_definitions
        },
        "rerun_rules": {
            "factor_added": "Run from 'values' through 'state' (--stage all --expensive-ok)",
            "evaluation_updated": "Run from 'diagnostics' through 'state'",
            "redundancy_updated": "Run from 'cluster' through 'state'",
            "scorecard_updated": "Run from 'profile' through 'state'",
            "any_upstream_changed": "Always regenerate 'state' last",
        },
        "factor_added_required_stages": [
            "values", "direction-audit", "evaluate", "diagnostics", "metadata",
            "scorecard", "redundancy", "cluster", "paper-diagnostics",
            "paper-page-payload", "regime", "quantile-shape", "rolling-stability",
            "decile-shape", "capacity-liquidity", "profile", "staleness", "page", "state",
        ],
        "profile_required_inputs": list(EVIDENCE_BLOCKS.keys()),
        "page_ready_required_outputs": [
            "factor_evaluation_workflow_contract.json",
            "factor_unified_profile_summary.csv",
            "factor_unified_profile_summary.json",
            "factor_profile_payload.json",
            "factor_profile_manifest.json",
            "factor_evaluation_evidence_matrix.csv",
            "factor_evaluation_evidence_matrix.json",
            "factor_profile_component_scores.csv",
        ],
    }
    return contract


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: Evidence Matrix
# ═══════════════════════════════════════════════════════════════════════════

def build_evidence_matrix(factor_ids: list[str]) -> tuple[list[dict], dict]:
    """Build evidence availability matrix for all factors.
    Returns (rows_for_csv, json_summary).
    """
    # Load all evidence files
    evidence_dfs: dict[str, pd.DataFrame | None] = {}
    for block_name, (filename, _) in EVIDENCE_BLOCKS.items():
        evidence_dfs[block_name] = load_csv_safe(filename)

    n_required = sum(1 for _, (_, req) in EVIDENCE_BLOCKS.items() if req)
    rows = []

    for fid in factor_ids:
        row = {"factor_id": fid}
        available_blocks = []
        missing_blocks = []
        stale_blocks = []  # placeholder — all current for now

        for block_name, (filename, required) in EVIDENCE_BLOCKS.items():
            df = evidence_dfs[block_name]
            has_col = f"has_{block_name}"
            if df is not None and "factor_id" in df.columns and fid in df["factor_id"].values:
                row[has_col] = True
                available_blocks.append(block_name)
            else:
                row[has_col] = False
                if required:
                    missing_blocks.append(block_name)

        n_available = len(available_blocks)
        row["n_available_evidence_blocks"] = n_available
        row["n_required_evidence_blocks"] = n_required
        row["evidence_completeness_rate"] = round(n_available / len(EVIDENCE_BLOCKS), 4) if EVIDENCE_BLOCKS else 0.0

        if n_available == len(EVIDENCE_BLOCKS):
            status = "COMPLETE"
        elif n_available >= n_required:
            status = "COMPLETE_WITH_WARNINGS"
        elif n_available > 0:
            status = "INCOMPLETE"
        else:
            status = "BLOCKED"

        row["evidence_status"] = status
        row["missing_evidence_blocks"] = "|".join(missing_blocks) if missing_blocks else ""
        row["stale_evidence_blocks"] = "|".join(stale_blocks) if stale_blocks else ""

        rows.append(row)

    # Summary
    status_counts = {}
    for r in rows:
        s = r["evidence_status"]
        status_counts[s] = status_counts.get(s, 0) + 1

    json_summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_factors": len(factor_ids),
        "total_evidence_blocks": len(EVIDENCE_BLOCKS),
        "n_required_evidence_blocks": n_required,
        "evidence_status_distribution": status_counts,
        "mean_completeness_rate": round(
            sum(r["evidence_completeness_rate"] for r in rows) / len(rows), 4
        ) if rows else 0.0,
    }

    return rows, json_summary


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: Component Score Functions
# ═══════════════════════════════════════════════════════════════════════════

def _safe_float(val, default=0.0) -> float:
    """Convert a value to float safely."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return default
    try:
        v = float(val)
        return default if math.isnan(v) or math.isinf(v) else v
    except (ValueError, TypeError):
        return default


def _map_class_to_score(class_val: str, mapping: dict[str, float], default: float = 50.0) -> float:
    """Map a class string to a numeric score."""
    if not class_val or not isinstance(class_val, str):
        return default
    return mapping.get(class_val, default)


def score_standalone_quality(sc_row: dict) -> float:
    """Score from quality scorecard (0-100)."""
    return _safe_float(sc_row.get("final_quality_score"), 50.0)


def score_paper(ps_row: dict) -> float:
    """Score from paper viability class."""
    mapping = {
        "PAPER_STRONG": 95.0, "PAPER_PROMISING": 80.0, "PAPER_MIXED": 50.0,
        "PAPER_REVIEW_REQUIRED": 30.0, "PAPER_WEAK": 15.0, "PAPER_INSUFFICIENT": 5.0,
    }
    return _map_class_to_score(ps_row.get("paper_viability_class", ""), mapping, 30.0)


def score_cost(ps_row: dict) -> float:
    """Score from cost sensitivity class (higher = less cost-sensitive = better)."""
    mapping = {
        "COST_ROBUST": 95.0, "MODERATELY_COST_SENSITIVE": 70.0,
        "COST_FRAGILE": 40.0, "COST_COLLAPSED": 10.0, "INSUFFICIENT_DATA": 30.0,
    }
    return _map_class_to_score(ps_row.get("cost_sensitivity_class", ""), mapping, 30.0)


def score_regime(rg_row: dict) -> float:
    """Score from regime dependency class (higher = more robust = better)."""
    mapping = {
        "REGIME_ROBUST": 90.0, "VOL_DEPENDENT": 50.0, "BULL_DEPENDENT": 40.0,
        "BEAR_DEPENDENT": 35.0, "DRAWDOWN_FRAGILE": 15.0,
    }
    return _map_class_to_score(rg_row.get("regime_dependency_class", ""), mapping, 40.0)


def score_shape(qs_row: dict) -> float:
    """Score from quantile shape class at best horizon."""
    mapping = {
        "EXCELLENT_MONOTONIC": 95.0, "MONOTONIC_STRONG": 85.0,
        "MONOTONIC_WEAK": 65.0, "WEAK_MONOTONIC": 55.0,
        "NEAR_MONOTONIC": 50.0, "MIXED_SHAPE": 40.0,
        "NO_CLEAR_SHAPE": 25.0, "NON_MONOTONIC": 20.0,
        "BOTH_TAILS_U_SHAPED": 30.0,
    }
    return _map_class_to_score(qs_row.get("quantile_shape_class", ""), mapping, 30.0)


def score_stability(rs_row: dict) -> float:
    """Score from rolling stability class."""
    mapping = {
        "STABLE_POSITIVE": 90.0, "STABLE_WEAK": 55.0,
        "REGIME_OR_PERIOD_DEPENDENT": 35.0, "UNSTABLE_SIGN_FLIP": 15.0,
    }
    return _map_class_to_score(rs_row.get("stability_class", ""), mapping, 40.0)


def score_capacity(cl_row: dict) -> float:
    """Score from capacity/liquidity class (higher = more capacity-friendly)."""
    mapping = {
        "CAPACITY_FRIENDLY": 90.0, "WATCH_LIQUIDITY": 50.0,
        "WATCH_CAPACITY": 40.0, "WATCH_BOTH": 25.0,
        "CAPACITY_CONSTRAINED": 15.0,
    }
    return _map_class_to_score(cl_row.get("capacity_liquidity_class", ""), mapping, 40.0)


def score_redundancy(rr_row: dict) -> float:
    """Score from redundancy (higher novelty = higher score)."""
    mapping = {
        "LIKELY_DISTINCT": 95.0, "NEEDS_REVIEW": 50.0,
        "MODERATELY_REDUNDANT": 35.0, "HIGHLY_REDUNDANT": 15.0,
        "INSUFFICIENT_OVERLAP": 45.0,
    }
    return _map_class_to_score(rr_row.get("novelty_assessment", ""), mapping, 40.0)


def score_marginal_info(mi_row: dict) -> float:
    """Score from marginal information class."""
    mapping = {
        "HIGH_MARGINAL_INFO": 90.0, "MODERATE_MARGINAL_INFO": 65.0,
        "LOW_MARGINAL_INFO": 35.0, "DISTINCT_SINGLETON": 70.0,
    }
    return _map_class_to_score(mi_row.get("marginal_information_class", ""), mapping, 40.0)


def score_evidence_completeness(completeness_rate: float) -> float:
    """Score from evidence completeness rate (0-1 → 0-100)."""
    return round(completeness_rate * 100.0, 2)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: Profile Classification
# ═══════════════════════════════════════════════════════════════════════════

def classify_profile(
    quality_score: float,
    evidence_completeness_rate: float,
    standalone_score: float,
    paper_score: float,
    cost_score: float,
    regime_score: float,
    shape_score: float,
    stability_score: float,
    capacity_score: float,
    redundancy_score: float,
    marginal_score: float,
    cluster_size: int,
    member_role: str,
    profile_score: float,
) -> tuple[str, str]:
    """Determine profile class and research action."""
    # Incomplete evidence gate
    if evidence_completeness_rate < 0.7:
        return "INCOMPLETE_EVIDENCE", "COMPLETE_MISSING_EVIDENCE"

    # Insufficient data gate — score too low overall
    if profile_score < 20:
        return "INSUFFICIENT_DATA", "INSUFFICIENT_DATA_REVIEW"

    # Classify by dominant pattern
    is_high_quality = standalone_score >= 70 and paper_score >= 60
    is_redundant = redundancy_score < 40 and cluster_size > 1
    is_regime_dep = regime_score < 50
    is_capacity_constrained = capacity_score < 40
    is_stability_weak = stability_score < 40
    is_unique = redundancy_score >= 70
    is_weak = standalone_score < 50 or paper_score < 40

    if is_high_quality and is_unique:
        return "HIGH_QUALITY_DISTINCT", "PRIORITIZE_FOR_REVIEW"
    if is_high_quality and is_redundant:
        if member_role in ("CLUSTER_REPRESENTATIVE",):
            return "HIGH_QUALITY_BUT_REDUNDANT", "KEEP_AS_CLUSTER_REFERENCE"
        return "HIGH_QUALITY_BUT_REDUNDANT", "REVIEW_AS_REDUNDANT_ALTERNATIVE"
    if is_high_quality and is_capacity_constrained:
        return "STABLE_BUT_CAPACITY_CONSTRAINED", "WATCH_FOR_CAPACITY_RISK"
    if is_high_quality and is_regime_dep:
        return "PROMISING_BUT_REGIME_DEPENDENT", "WATCH_FOR_REGIME_DEPENDENCE"
    if is_unique and is_weak:
        return "UNIQUE_BUT_WEAK", "KEEP_AS_DIAGNOSTIC_PROBE"
    if is_stability_weak and standalone_score >= 50:
        return "BROAD_WATCHLIST", "WATCH_FOR_STABILITY_RISK"
    if profile_score >= 35:
        return "BROAD_WATCHLIST", "LOWER_PRIORITY_REVIEW"
    return "LOW_PRIORITY_DIAGNOSTIC", "LOWER_PRIORITY_REVIEW"


def profile_confidence(score_confidence: str, evidence_completeness_rate: float) -> str:
    """Determine overall profile confidence."""
    if score_confidence == "HIGH" and evidence_completeness_rate >= 1.0:
        return "HIGH"
    if score_confidence in ("HIGH", "MEDIUM") and evidence_completeness_rate >= 0.8:
        return "MEDIUM"
    return "LOW"


def generate_strength_risk(
    profile_class: str,
    component_scores: dict,
) -> tuple[tuple[str, str], tuple[str, str], tuple[str, str]]:
    """Generate (zh, en) pairs for primary_strength, primary_risk, profile_summary."""
    strengths_zh_en = {
        "HIGH_QUALITY_DISTINCT": ("质量高且信息独特", "High quality with unique information"),
        "HIGH_QUALITY_BUT_REDUNDANT": ("质量高但与同类因子相关性强", "High quality but correlated with cluster peers"),
        "STABLE_BUT_CAPACITY_CONSTRAINED": ("信号稳定但流动性/容量受限", "Stable signal but liquidity/capacity constrained"),
        "PROMISING_BUT_REGIME_DEPENDENT": ("总体有潜力但依赖市场状态", "Promising overall but regime-dependent"),
        "UNIQUE_BUT_WEAK": ("信息独特但预测力偏弱", "Unique information but weak predictive power"),
        "BROAD_WATCHLIST": ("多个维度均有中等表现", "Moderate performance across multiple dimensions"),
        "LOW_PRIORITY_DIAGNOSTIC": ("各维度均偏弱，优先级低", "Weak across dimensions — low priority"),
        "INCOMPLETE_EVIDENCE": ("部分诊断证据缺失", "Some diagnostic evidence missing"),
        "INSUFFICIENT_DATA": ("数据不足以形成画像", "Insufficient data for profiling"),
    }

    risks_zh_en = {
        "HIGH_QUALITY_DISTINCT": ("需持续监控滚动稳定性", "Monitor rolling stability continuously"),
        "HIGH_QUALITY_BUT_REDUNDANT": ("冗余度高，边际价值可能有限", "High redundancy — limited marginal value"),
        "STABLE_BUT_CAPACITY_CONSTRAINED": ("资金容量受限，可能无法大规模使用", "Capacity constrained — limited scalability"),
        "PROMISING_BUT_REGIME_DEPENDENT": ("在特定市场状态下可能失效", "May fail in certain market regimes"),
        "UNIQUE_BUT_WEAK": ("预测信号弱，单独使用风险大", "Weak signal — high risk if used alone"),
        "BROAD_WATCHLIST": ("无突出优势，需进一步筛选", "No standout strength — needs further filtering"),
        "LOW_PRIORITY_DIAGNOSTIC": ("表现不佳，投入产出比低", "Poor performance — low ROI on further research"),
        "INCOMPLETE_EVIDENCE": ("诊断不完整，无法全面评估", "Incomplete diagnostics — cannot fully evaluate"),
        "INSUFFICIENT_DATA": ("数据不足，评估不可靠", "Insufficient data — evaluation unreliable"),
    }

    strength = strengths_zh_en.get(profile_class, ("待评估", "To be assessed"))
    risk = risks_zh_en.get(profile_class, ("待评估", "To be assessed"))

    # Summary
    score = component_scores.get("profile_score", 0)
    summary_zh = f"综合评分 {score:.0f}/100。{strength[0]}。{risk[0]}。"
    summary_en = f"Profile score {score:.0f}/100. {strength[1]}. {risk[1]}."

    return strength, risk, (summary_zh, summary_en)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: Unified Profile Builder
# ═══════════════════════════════════════════════════════════════════════════

def _pick_best_horizon_row(df: pd.DataFrame, fid: str, best_horizon: str) -> dict | None:
    """Pick the row matching best_horizon for a factor from a multi-horizon df."""
    if df is None:
        return None
    mask = (df["factor_id"] == fid) & (df["horizon"].astype(str) == best_horizon)
    sub = df[mask]
    if len(sub) == 0:
        # fallback: any row for this factor
        sub = df[df["factor_id"] == fid]
    if len(sub) == 0:
        return None
    return sub.iloc[0].to_dict()


def build_unified_profile(factor_ids: list[str], state: dict) -> tuple[list[dict], list[dict]]:
    """Build unified profile rows and component score rows."""
    # Load all input data
    sc_df = load_csv_safe("factor_quality_scorecard.csv")
    ds_df = load_csv_safe("factor_diagnostics_summary.csv")
    rr_df = load_csv_safe("factor_redundancy_summary.csv")
    cm_df = load_csv_safe("factor_redundancy_cluster_members.csv")
    mi_df = load_csv_safe("factor_marginal_information_summary.csv")
    ps_df = load_csv_safe("single_factor_paper_summary.csv")
    fs_df = load_csv_safe("single_factor_fee_sensitivity.csv")
    rg_df = load_csv_safe("factor_regime_exposure_summary.csv")
    qs_df = load_csv_safe("factor_quantile_shape_summary.csv")
    rs_df = load_csv_safe("factor_rolling_stability_summary.csv")
    dc_df = load_csv_safe("factor_decile_shape_summary.csv")
    cl_df = load_csv_safe("factor_capacity_liquidity_summary.csv")

    # Index by factor_id for fast lookup
    def _idx(df, key="factor_id"):
        if df is None:
            return {}
        return {row[key]: row for _, row in df.iterrows()}

    sc_map = _idx(sc_df)
    ds_map = _idx(ds_df)
    rr_map = _idx(rr_df)
    cm_map = _idx(cm_df)
    mi_map = _idx(mi_df)
    ps_map = _idx(ps_df)
    rg_map = _idx(rg_df)
    cl_map = _idx(cl_df)

    profile_rows = []
    component_rows = []

    for fid in factor_ids:
        sc = sc_map.get(fid, {})
        ds = ds_map.get(fid, {})
        rr = rr_map.get(fid, {})
        cm = cm_map.get(fid, {})
        mi = mi_map.get(fid, {})
        ps = ps_map.get(fid, {})
        rg = rg_map.get(fid, {})
        cl = cl_map.get(fid, {})

        best_horizon = str(sc.get("best_horizon", "4h"))

        # Pick best-horizon rows for multi-horizon tables
        qs = _pick_best_horizon_row(qs_df, fid, best_horizon) or {}
        rs = _pick_best_horizon_row(rs_df, fid, best_horizon) or {}
        dc = _pick_best_horizon_row(dc_df, fid, best_horizon) or {}

        # Compute component scores
        comp = {
            "standalone_quality": score_standalone_quality(sc),
            "paper": score_paper(ps),
            "cost": score_cost(ps),
            "regime": score_regime(rg),
            "shape": score_shape(qs),
            "stability": score_stability(rs),
            "capacity": score_capacity(cl),
            "redundancy": score_redundancy(rr),
            "marginal_info": score_marginal_info(mi),
        }

        # Evidence completeness — fast lookup from already-loaded data
        evidence_blocks_present = 0
        _local_dfs = {
            "quality_scorecard": sc_df, "diagnostics_summary": ds_df,
            "redundancy_summary": rr_df, "redundancy_cluster_members": cm_df,
            "marginal_information": mi_df, "paper_summary": ps_df,
            "fee_sensitivity": fs_df, "regime_exposure": rg_df,
            "quantile_shape": qs_df, "rolling_stability": rs_df,
            "decile_shape": dc_df, "capacity_liquidity": cl_df,
        }
        for block_name in EVIDENCE_BLOCKS:
            local_df = _local_dfs.get(block_name)
            if local_df is not None and "factor_id" in local_df.columns and fid in local_df["factor_id"].values:
                evidence_blocks_present += 1

        evidence_completeness_rate = round(evidence_blocks_present / len(EVIDENCE_BLOCKS), 4)
        comp["evidence_completeness"] = score_evidence_completeness(evidence_completeness_rate)

        # Weighted profile score
        profile_score = 0.0
        for comp_name, weight in COMPONENT_WEIGHTS.items():
            profile_score += comp[comp_name] * weight
        profile_score = round(profile_score, 2)

        # Classify
        cluster_size = int(cm.get("cluster_size", 1))
        member_role = str(cm.get("member_role", "DISTINCT_SINGLETON"))
        quality_score = _safe_float(sc.get("final_quality_score"), 0.0)

        profile_class, research_action = classify_profile(
            quality_score=quality_score,
            evidence_completeness_rate=evidence_completeness_rate,
            standalone_score=comp["standalone_quality"],
            paper_score=comp["paper"],
            cost_score=comp["cost"],
            regime_score=comp["regime"],
            shape_score=comp["shape"],
            stability_score=comp["stability"],
            capacity_score=comp["capacity"],
            redundancy_score=comp["redundancy"],
            marginal_score=comp["marginal_info"],
            cluster_size=cluster_size,
            member_role=member_role,
            profile_score=profile_score,
        )

        conf = profile_confidence(str(sc.get("score_confidence", "LOW")), evidence_completeness_rate)

        strength, risk, summary = generate_strength_risk(profile_class, {"profile_score": profile_score})

        # Source artifacts
        source_artifacts = [
            "factor_quality_scorecard.csv", "factor_diagnostics_summary.csv",
            "factor_redundancy_summary.csv", "factor_redundancy_cluster_members.csv",
            "factor_marginal_information_summary.csv", "single_factor_paper_summary.csv",
            "single_factor_fee_sensitivity.csv", "factor_regime_exposure_summary.csv",
            "factor_quantile_shape_summary.csv", "factor_rolling_stability_summary.csv",
            "factor_decile_shape_summary.csv", "factor_capacity_liquidity_summary.csv",
        ]

        n_required_blocks = sum(1 for _, (_, req) in EVIDENCE_BLOCKS.items() if req)
        if evidence_completeness_rate >= 1.0:
            ev_status = "COMPLETE"
        elif evidence_completeness_rate >= n_required_blocks / len(EVIDENCE_BLOCKS):
            ev_status = "COMPLETE_WITH_WARNINGS"
        elif evidence_completeness_rate > 0:
            ev_status = "INCOMPLETE"
        else:
            ev_status = "BLOCKED"

        profile_row = {
            "factor_id": fid,
            "family": str(sc.get("family", ds.get("family", ""))),
            "status": str(ds.get("lifecycle_status", "")),
            "expected_direction": str(ds.get("expected_direction", "")),
            "evidence_status": ev_status,
            "evidence_completeness_rate": evidence_completeness_rate,
            "profile_score": profile_score,
            "profile_class": profile_class,
            "profile_confidence": conf,
            "standalone_quality_class": str(sc.get("final_quality_class", "")),
            "paper_portfolio_class": str(ps.get("paper_viability_class", "")),
            "cost_risk_class": str(ps.get("cost_sensitivity_class", "")),
            "regime_dependency_class": str(rg.get("regime_dependency_class", "")),
            "shape_quality_class": str(qs.get("quantile_shape_class", "")),
            "rolling_stability_class": str(rs.get("stability_class", "")),
            "decile_shape_class": str(dc.get("decile_shape_class", "")),
            "capacity_liquidity_class": str(cl.get("capacity_liquidity_class", "")),
            "cluster_id": int(cm.get("cluster_id", -1)),
            "cluster_size": cluster_size,
            "cluster_member_role": member_role,
            "marginal_information_class": str(mi.get("marginal_information_class", "")),
            "primary_strength_zh": strength[0],
            "primary_strength_en": strength[1],
            "primary_risk_zh": risk[0],
            "primary_risk_en": risk[1],
            "profile_summary_zh": summary[0],
            "profile_summary_en": summary[1],
            "recommended_research_action": research_action,
            "source_artifact_count": len(source_artifacts),
            "source_artifacts": "|".join(source_artifacts),
        }

        component_row = {
            "factor_id": fid,
            "profile_score": profile_score,
            **{f"comp_{k}": round(v, 2) for k, v in comp.items()},
            **{f"weight_{k}": v for k, v in COMPONENT_WEIGHTS.items()},
        }

        profile_rows.append(profile_row)
        component_rows.append(component_row)

    return profile_rows, component_rows


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6: Payload & Manifest
# ═══════════════════════════════════════════════════════════════════════════

def build_payload(profile_rows: list[dict], component_rows: list[dict]) -> dict:
    """Build compact page-ready payload."""
    comp_map = {r["factor_id"]: r for r in component_rows}
    factors = []
    for row in profile_rows:
        fid = row["factor_id"]
        comp = comp_map.get(fid, {})
        factors.append({
            "factor_id": fid,
            "family": row["family"],
            "status": row["status"],
            "profile_score": row["profile_score"],
            "profile_class": row["profile_class"],
            "profile_confidence": row["profile_confidence"],
            "evidence_status": row["evidence_status"],
            "evidence_completeness_rate": row["evidence_completeness_rate"],
            "standalone_quality_class": row["standalone_quality_class"],
            "paper_portfolio_class": row["paper_portfolio_class"],
            "cost_risk_class": row["cost_risk_class"],
            "regime_dependency_class": row["regime_dependency_class"],
            "shape_quality_class": row["shape_quality_class"],
            "rolling_stability_class": row["rolling_stability_class"],
            "decile_shape_class": row["decile_shape_class"],
            "capacity_liquidity_class": row["capacity_liquidity_class"],
            "cluster_id": row["cluster_id"],
            "cluster_size": row["cluster_size"],
            "cluster_member_role": row["cluster_member_role"],
            "marginal_information_class": row["marginal_information_class"],
            "recommended_research_action": row["recommended_research_action"],
            "primary_strength_zh": row["primary_strength_zh"],
            "primary_strength_en": row["primary_strength_en"],
            "primary_risk_zh": row["primary_risk_zh"],
            "primary_risk_en": row["primary_risk_en"],
            "profile_summary_zh": row["profile_summary_zh"],
            "profile_summary_en": row["profile_summary_en"],
            "component_scores": {k.replace("comp_", ""): comp.get(k, 0) for k in comp if k.startswith("comp_")},
        })

    # Class distribution
    class_dist = {}
    for f in factors:
        c = f["profile_class"]
        class_dist[c] = class_dist.get(c, 0) + 1

    action_dist = {}
    for f in factors:
        a = f["recommended_research_action"]
        action_dist[a] = action_dist.get(a, 0) + 1

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workflow_version": "1.0.0",
        "not_production_disclaimer": "Research diagnostics ONLY. NOT production. NOT live trading.",
        "total_factors": len(factors),
        "profile_class_distribution": class_dist,
        "research_action_distribution": action_dist,
        "component_weights": COMPONENT_WEIGHTS,
        "factors": factors,
    }


def build_manifest(profile_rows: list[dict]) -> dict:
    """Build source lineage manifest."""
    source_artifact_set = set()
    for row in profile_rows:
        for art in row["source_artifacts"].split("|"):
            source_artifact_set.add(art)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workflow_version": "1.0.0",
        "not_production_disclaimer": "Research diagnostics ONLY. NOT production. NOT live trading.",
        "total_factors": len(profile_rows),
        "source_artifacts": sorted(source_artifact_set),
        "output_artifacts": [
            "factor_evaluation_workflow_contract.json",
            "factor_evaluation_evidence_matrix.csv",
            "factor_evaluation_evidence_matrix.json",
            "factor_unified_profile_summary.csv",
            "factor_unified_profile_summary.json",
            "factor_profile_component_scores.csv",
            "factor_profile_payload.json",
            "factor_profile_manifest.json",
        ],
        "factor_lineage": {
            row["factor_id"]: row["source_artifacts"].split("|") for row in profile_rows
        },
    }


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 7: Forbidden Language Check
# ═══════════════════════════════════════════════════════════════════════════

FORBIDDEN_TERMS = [
    "trade this factor", "deploy this factor", "remove this factor", "drop this factor",
    "only keep", "portfolio allocation", "signal weight",
    "交易该因子", "上线该因子", "删除", "剔除", "淘汰", "只保留", "配置权重", "买入", "卖出",
]

# Short English terms that need word-boundary matching to avoid false positives
# (e.g., "buy" in "taker_buy" is a factor name, not trading language)
FORBIDDEN_TERMS_REGEX = [
    r"\bbuy\b", r"\bsell\b",
]


def run_forbidden_language_check(paths: list[Path]) -> dict:
    """Check output files for forbidden trading/deployment language."""
    import re
    results = {}
    for p in paths:
        if not p.exists():
            results[p.name] = {"status": "FILE_MISSING", "hits": []}
            continue
        txt = p.read_text(encoding="utf-8", errors="ignore").lower()
        hits = [b for b in FORBIDDEN_TERMS if b.lower() in txt]
        for pattern in FORBIDDEN_TERMS_REGEX:
            if re.search(pattern, txt):
                hits.append(pattern)
        results[p.name] = {
            "status": "FAIL" if hits else "PASS",
            "hits": hits,
        }
    return results


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def write_csv(rows: list[dict], path: Path) -> None:
    """Write list of dicts to CSV."""
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> int:
    parser = argparse.ArgumentParser(description="PM-32: Unified Factor Profile Builder")
    parser.add_argument("--output-dir", type=str, default=str(DIAG_DIR),
                        help="Output directory for all artifacts")
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load state to get dynamic factor list
    print("Loading factor library state...")
    state = load_state()
    factor_ids = sorted(state.get("registered_factor_ids", []))
    n_factors = len(factor_ids)
    print(f"  Registered factors: {n_factors}")

    # ── 1. Workflow contract ─────────────────────────────────────────────
    print("\n[1/6] Building workflow contract...")
    contract = build_workflow_contract()
    contract_path = out_dir / "factor_evaluation_workflow_contract.json"
    with open(contract_path, "w") as f:
        json.dump(contract, f, indent=2, ensure_ascii=False)
    print(f"  → {contract_path} ({len(contract['stage_order'])} stages)")

    # ── 2. Evidence matrix ───────────────────────────────────────────────
    print("\n[2/6] Building evidence matrix...")
    evidence_rows, evidence_summary = build_evidence_matrix(factor_ids)
    ev_csv_path = out_dir / "factor_evaluation_evidence_matrix.csv"
    ev_json_path = out_dir / "factor_evaluation_evidence_matrix.json"
    write_csv(evidence_rows, ev_csv_path)
    with open(ev_json_path, "w") as f:
        json.dump(evidence_summary, f, indent=2, ensure_ascii=False)
    print(f"  → {ev_csv_path} ({len(evidence_rows)} factors)")
    print(f"  → {ev_json_path}")
    print(f"  Status distribution: {evidence_summary['evidence_status_distribution']}")
    print(f"  Mean completeness: {evidence_summary['mean_completeness_rate']:.2%}")

    # ── 3. Unified profile ───────────────────────────────────────────────
    print("\n[3/6] Building unified profile...")
    profile_rows, component_rows = build_unified_profile(factor_ids, state)
    profile_csv_path = out_dir / "factor_unified_profile_summary.csv"
    profile_json_path = out_dir / "factor_unified_profile_summary.json"
    write_csv(profile_rows, profile_csv_path)
    with open(profile_json_path, "w") as f:
        json.dump(profile_rows, f, indent=2, ensure_ascii=False, default=str)
    print(f"  → {profile_csv_path} ({len(profile_rows)} factors)")

    # ── 4. Component scores ──────────────────────────────────────────────
    print("\n[4/6] Writing component scores...")
    comp_csv_path = out_dir / "factor_profile_component_scores.csv"
    write_csv(component_rows, comp_csv_path)
    print(f"  → {comp_csv_path} ({len(component_rows)} factors)")

    # ── 5. Payload & manifest ────────────────────────────────────────────
    print("\n[5/6] Building payload & manifest...")
    payload = build_payload(profile_rows, component_rows)
    manifest = build_manifest(profile_rows)
    payload_path = out_dir / "factor_profile_payload.json"
    manifest_path = out_dir / "factor_profile_manifest.json"
    with open(payload_path, "w") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False, default=str)
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False, default=str)
    print(f"  → {payload_path}")
    print(f"  → {manifest_path}")

    # ── 6. Forbidden language check ──────────────────────────────────────
    print("\n[6/6] Running forbidden language check...")
    check_paths = [profile_csv_path, payload_path, contract_path]
    check_results = run_forbidden_language_check(check_paths)
    all_pass = True
    for fname, result in check_results.items():
        status = result["status"]
        if status == "FAIL":
            print(f"  FAIL {fname}: {result['hits']}")
            all_pass = False
        else:
            print(f"  {status} {fname}")

    if not all_pass:
        print("\nERROR: Forbidden language detected in outputs!")
        return 1

    # ── Summary ──────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"PM-32 Unified Factor Profile — Build Complete")
    print(f"{'='*60}")
    print(f"Factors profiled: {n_factors}")
    print(f"Workflow stages: {len(contract['stage_order'])}")
    print(f"Evidence status: {evidence_summary['evidence_status_distribution']}")
    print(f"Mean evidence completeness: {evidence_summary['mean_completeness_rate']:.2%}")

    class_dist = payload["profile_class_distribution"]
    print(f"\nProfile class distribution:")
    for cls in PROFILE_CLASSES:
        count = class_dist.get(cls, 0)
        if count > 0:
            print(f"  {cls}: {count}")

    action_dist = payload["research_action_distribution"]
    print(f"\nResearch action distribution:")
    for act in RESEARCH_ACTIONS:
        count = action_dist.get(act, 0)
        if count > 0:
            print(f"  {act}: {count}")

    print(f"\nComponent weights:")
    for name, weight in COMPONENT_WEIGHTS.items():
        print(f"  {name}: {weight:.0%}")

    print(f"\nOutputs:")
    print(f"  {contract_path}")
    print(f"  {ev_csv_path}")
    print(f"  {ev_json_path}")
    print(f"  {profile_csv_path}")
    print(f"  {profile_json_path}")
    print(f"  {comp_csv_path}")
    print(f"  {payload_path}")
    print(f"  {manifest_path}")
    print(f"{'='*60}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
