#!/usr/bin/env python3
"""
PM-16B: Factor Quality Scorecard Builder
=========================================

Rule-based scorecard synthesizing 7-dimension evidence into per-factor quality judgments.

Framework version: pm16b_v1
NOT a trading signal. Research triage tool only.

Dimensions:
  1. computation_integrity_score
  2. predictive_ranking_score
  3. portfolio_extraction_score
  4. stability_score
  5. quantile_shape_score
  6. direction_interpretability_score
  7. redundancy_novelty_score

Quality classes:
  STRONG_RESEARCH_CANDIDATE | PROMISING_BUT_INCONSISTENT | DIRECTION_DEPENDENT
  REDUNDANT_OR_WEAK | INSUFFICIENT_EVIDENCE | REVIEW_REQUIRED
"""

from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import numpy as np

# ── Paths ────────────────────────────────────────────────────────────────────

BASE = Path("research/factor_runs/crypto_top50_factor_library")
DIAG_DIR = BASE / "factor_diagnostics"
META_DIR = BASE / "factor_metadata"
EVAL_DIR = BASE / "factor_level_evaluation"

PATH_DIAG_SUMMARY = DIAG_DIR / "factor_diagnostics_summary.csv"
PATH_MONTHLY_IC = DIAG_DIR / "factor_monthly_ic_series.csv"
PATH_MONTHLY_LS = DIAG_DIR / "factor_monthly_long_short_series.csv"
PATH_CUM_LS = DIAG_DIR / "factor_cumulative_long_short_curve.csv"
PATH_FRAMEWORK = DIAG_DIR / "factor_quality_framework_spec.json"
PATH_EVIDENCE_INV = DIAG_DIR / "factor_evaluation_evidence_inventory.csv"

PATH_BILINGUAL = META_DIR / "factor_bilingual_cards.csv"
PATH_QA = META_DIR / "factor_card_qa_report.csv"

PATH_QUANTILE = EVAL_DIR / "factor_level_quantile_return_summary.csv"
PATH_QUANTILE_PERIOD = EVAL_DIR / "factor_level_period_quantile_return_summary.csv"
PATH_METRIC_PANEL = EVAL_DIR / "factor_level_metric_panel.csv"
PATH_REDUNDANCY = DIAG_DIR / "factor_pairwise_redundancy.csv"
PATH_REDUNDANCY_SUMMARY = DIAG_DIR / "factor_redundancy_summary.csv"
PATH_REDUNDANCY_CLUSTERS = DIAG_DIR / "factor_redundancy_clusters.csv"

# PM-43A: Canonical sources for scorecard fallback
PATH_CANONICAL_RANKIC = EVAL_DIR / "factor_level_rankic_summary.csv"
PATH_CANONICAL_LS = EVAL_DIR / "factor_level_long_short_summary.csv"
PATH_REGIME_EXPOSURE = DIAG_DIR / "factor_regime_exposure_summary.csv"

PATH_STATE = BASE / "factor_library_state.json"

OUT_CSV = DIAG_DIR / "factor_quality_scorecard.csv"
OUT_JSON = DIAG_DIR / "factor_quality_scorecard.json"
OUT_MANIFEST = DIAG_DIR / "factor_quality_scorecard_manifest.json"

# ── Constants ────────────────────────────────────────────────────────────────

DIMENSION_WEIGHTS = {
    "computation_integrity": 0.10,
    "predictive_ranking": 0.25,
    "portfolio_extraction": 0.20,
    "stability": 0.15,
    "quantile_shape": 0.10,
    "direction_interpretability": 0.10,
    "redundancy_novelty": 0.10,
}

QUALITY_CLASSES = [
    "STRONG_RESEARCH_CANDIDATE",
    "PROMISING_BUT_INCONSISTENT",
    "DIRECTION_DEPENDENT",
    "REDUNDANT_OR_WEAK",
    "INSUFFICIENT_EVIDENCE",
    "REVIEW_REQUIRED",
]

METADATA_QUALITY_VALUES = {"COMPLETE", "DIRECTION_AMBIGUOUS", "NEEDS_REVIEW", "FORMULA_AMBIGUOUS"}


# ── Utility helpers ──────────────────────────────────────────────────────────

def _clamp(v: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, v))


def _safe_float(v, default: float = 0.0) -> float:
    """Convert a value to float; return default on failure."""
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return default
    try:
        return float(v)
    except (ValueError, TypeError):
        return default


def _safe_str(v, default: str = "") -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return default
    return str(v).strip()


def _map_range(value: float, lo: float, hi: float, out_lo: float = 0.0, out_hi: float = 100.0) -> float:
    """Linearly map value from [lo, hi] to [out_lo, out_hi]. Clamped."""
    if hi == lo:
        return (out_lo + out_hi) / 2.0
    t = (value - lo) / (hi - lo)
    return _clamp(out_lo + t * (out_hi - out_lo))


# ── Loaders ──────────────────────────────────────────────────────────────────

def load_diagnostics_summary() -> pd.DataFrame:
    df = pd.read_csv(PATH_DIAG_SUMMARY)
    df["factor_id"] = df["factor_id"].astype(str).str.strip()
    return df.set_index("factor_id")


def load_bilingual_cards() -> pd.DataFrame:
    df = pd.read_csv(PATH_BILINGUAL)
    df["factor_id"] = df["factor_id"].astype(str).str.strip()
    return df.set_index("factor_id")


def load_qa_report() -> pd.DataFrame:
    df = pd.read_csv(PATH_QA)
    df["factor_id"] = df["factor_id"].astype(str).str.strip()
    return df.set_index("factor_id")


def load_quantile_summary() -> pd.DataFrame:
    df = pd.read_csv(PATH_QUANTILE)
    df["factor_name"] = df["factor_name"].astype(str).str.strip()
    return df


def load_redundancy() -> pd.DataFrame:
    try:
        df = pd.read_csv(PATH_REDUNDANCY)
        if "factor_i" in df.columns:
            return df
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def load_redundancy_summary() -> pd.DataFrame:
    """Load per-factor redundancy summary from PM-18."""
    try:
        df = pd.read_csv(PATH_REDUNDANCY_SUMMARY)
        if "factor_id" in df.columns:
            return df
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def load_redundancy_clusters() -> pd.DataFrame:
    """Load per-factor cluster assignment from PM-18."""
    try:
        df = pd.read_csv(PATH_REDUNDANCY_CLUSTERS)
        if "factor_id" in df.columns:
            return df
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def load_canonical_rankic() -> dict[str, dict]:
    """PM-43A: Load canonical RankIC from factor-level evaluation."""
    try:
        df = pd.read_csv(PATH_CANONICAL_RANKIC)
        result = {}
        for _, row in df.iterrows():
            fid = str(row["factor_name"]).strip()
            hz = str(row["horizon"]).strip()
            if fid not in result:
                result[fid] = {}
            mean_ic = float(row.get("direction_adjusted_mean_rank_ic", 0) or 0)
            t_stat = float(row.get("t_stat", 0) or 0)
            # Compute IR from mean/t_stat if available
            rankic_ir = mean_ic / t_stat if t_stat != 0 else 0.0
            result[fid][hz] = {
                "rankic_mean": mean_ic,
                "rankic_ir": rankic_ir,
                "t_stat": t_stat,
                "coverage": float(row.get("coverage", 0) or 0),
            }
        return result
    except Exception:
        return {}


def load_canonical_ls() -> dict[str, dict]:
    """PM-43A: Load canonical LS aggregate from factor-level evaluation."""
    try:
        df = pd.read_csv(PATH_CANONICAL_LS)
        result = {}
        for _, row in df.iterrows():
            fid = str(row["factor_name"]).strip()
            hz = str(row["horizon"]).strip()
            if fid not in result:
                result[fid] = {}
            ls_mean = float(row.get("long_short_spread_mean", 0) or 0)
            ls_std = float(row.get("long_short_spread_std", 0) or 0)
            # Compute Sharpe from mean/std (annualized: monthly_sharpe * sqrt(12))
            ls_sharpe = (ls_mean / ls_std * (12 ** 0.5)) if ls_std > 0 else 0.0
            result[fid][hz] = {
                "ls_sharpe": ls_sharpe,
                "ls_std": ls_std,
                "ls_ann_return": float(row.get("long_short_spread_annualized_return", 0) or 0),
                "ls_max_dd": float(row.get("long_short_spread_max_drawdown", 0) or 0),
                "ls_pmr": float(row.get("long_short_spread_positive_period_rate", 0) or 0),
            }
        return result
    except Exception:
        return {}
    except Exception:
        return pd.DataFrame()


def load_library_state() -> dict:
    with open(PATH_STATE, "r") as f:
        return json.load(f)


# ── Quantile shape analysis ─────────────────────────────────────────────────

def compute_quantile_shapes(quantile_df: pd.DataFrame) -> dict[str, dict[str, str]]:
    """
    For each (factor_name, horizon), extract Q1–Q5 mean_forward_return
    and classify monotonicity.

    Returns:
        {factor_name: {horizon: "MONOTONIC_GOOD" | "NEAR_MONOTONIC" | "NON_MONOTONIC" | "INSUFFICIENT"}}
    """
    result: dict[str, dict[str, str]] = {}

    grouped = quantile_df.groupby(["factor_name", "horizon"])
    for (fname, horizon), grp in grouped:
        # Sort by bucket index (0–4)
        grp = grp.sort_values("bucket")
        means = grp["mean_forward_return"].values

        if len(means) < 3:
            result.setdefault(fname, {})[horizon] = "INSUFFICIENT"
            continue

        # Check monotonicity (increasing or decreasing)
        diffs = np.diff(means)
        all_same_sign = np.all(diffs >= 0) or np.all(diffs <= 0)

        if all_same_sign:
            result.setdefault(fname, {})[horizon] = "MONOTONIC_GOOD"
        else:
            # Near-monotonic: at most 1 violation
            violations = 0
            # Check if mostly increasing
            inc_violations = np.sum(diffs < 0)
            dec_violations = np.sum(diffs > 0)
            violations = min(inc_violations, dec_violations)
            if violations <= 1:
                result.setdefault(fname, {})[horizon] = "NEAR_MONOTONIC"
            else:
                result.setdefault(fname, {})[horizon] = "NON_MONOTONIC"

    return result


def get_quantile_shape_for_factor(
    quantile_shapes: dict[str, dict[str, str]],
    factor_id: str,
    best_horizon: str,
) -> tuple[str, float]:
    """Return (shape_label, shape_score) for factor at best_horizon."""
    shapes = quantile_shapes.get(factor_id, {})
    label = shapes.get(best_horizon, "INSUFFICIENT")

    score_map = {
        "MONOTONIC_GOOD": 90,
        "NEAR_MONOTONIC": 70,
        "NON_MONOTONIC": 40,
        "INSUFFICIENT": 50,
    }
    return label, score_map.get(label, 50)


# ── Redundancy lookup ────────────────────────────────────────────────────────

def build_redundancy_map(redundancy_df: pd.DataFrame) -> dict[str, dict[str, Any]]:
    """
    Build a map: factor_id → {nearest_factor, redundancy_level, abs_corr}
    from the pairwise redundancy CSV.
    """
    rmap: dict[str, dict[str, Any]] = {}

    if redundancy_df.empty:
        return rmap

    for _, row in redundancy_df.iterrows():
        fi = str(row.get("factor_i", "")).strip()
        fj = str(row.get("factor_j", "")).strip()
        level = str(row.get("redundancy_level", "")).strip()
        abs_corr = _safe_float(row.get("abs_spearman_corr", 0))

        for src, other in [(fi, fj), (fj, fi)]:
            existing = rmap.get(src)
            if existing is None or abs_corr > existing.get("abs_corr", 0):
                rmap[src] = {
                    "nearest_factor": other,
                    "redundancy_level": level,
                    "abs_corr": abs_corr,
                }

    return rmap


# ── PM-19: Calibrated redundancy confidence ─────────────────────────────────

def compute_calibrated_redundancy_confidence(
    n_valid_pairs: int,
    expected_pairs: int,
    strongest_level: str,
    novelty: str,
) -> str:
    """
    PM-19: Calibrate redundancy confidence based on valid-pair coverage,
    not on absence of insufficient-overlap pairs.

    A factor should not be globally penalized merely because a subset of
    its pairs has insufficient overlap (newer/shorter-horizon factors
    naturally have fewer overlapping observations with longer-horizon ones).

    Logic:
      HIGH:   valid-pair coverage >= 70% AND >= 40 valid pairs
      MEDIUM: valid-pair coverage >= 40% AND >= 20 valid pairs
      Also MEDIUM/HIGH if the factor has clear high-redundancy evidence
      (NEAR_DUPLICATE or HIGH_REDUNDANCY) even with fewer valid pairs.
      LOW:    otherwise
    """
    if expected_pairs <= 0:
        return "LOW"

    coverage = n_valid_pairs / expected_pairs

    # High-redundancy evidence overrides low coverage for confidence
    has_strong_evidence = strongest_level in ("NEAR_DUPLICATE", "HIGH_REDUNDANCY")

    if coverage >= 0.70 and n_valid_pairs >= 40:
        return "HIGH"
    elif coverage >= 0.40 and n_valid_pairs >= 20:
        return "MEDIUM"
    elif has_strong_evidence and n_valid_pairs >= 4:
        # Factor has clear redundancy signal despite low overlap coverage
        return "MEDIUM"
    else:
        return "LOW"


# ── Dimension scoring functions ──────────────────────────────────────────────

def score_computation_integrity(coverage: float, source_warning: str, metadata_quality: str) -> float:
    """6.1 computation_integrity_score"""
    if coverage >= 0.95:
        base = 90
    elif coverage >= 0.80:
        base = 60
    else:
        base = 30

    if _safe_str(source_warning):
        base -= 20

    if metadata_quality == "COMPLETE":
        base += 10

    return _clamp(base)


def score_predictive_ranking(
    abs_rankic: float,
    rankic_ir: float,
    rankic_t_stat: float,
    monthly_ic_positive_rate: float,
) -> float:
    """6.2 predictive_ranking_score"""
    # Base score from |RankIC|
    if abs_rankic >= 0.03:
        # Strong: 70-100 mapped from 0.03–0.10
        base = _map_range(abs_rankic, 0.03, 0.10, 70, 100)
    elif abs_rankic >= 0.01:
        # Medium: 40-70 mapped from 0.01–0.03
        base = _map_range(abs_rankic, 0.01, 0.03, 40, 70)
    else:
        # Weak: 0-40 mapped from 0–0.01
        base = _map_range(abs_rankic, 0.0, 0.01, 0, 40)

    # Adjust by ICIR significance
    abs_icir = abs(rankic_ir)
    if abs_icir >= 0.3:
        base = _clamp(base + 10)
    elif abs_icir < 0.1:
        base = _clamp(base - 10)

    # Adjust by t-stat significance
    abs_t = abs(rankic_t_stat)
    if abs_t >= 2.0:
        base = _clamp(base + 5)
    elif abs_t < 1.0:
        base = _clamp(base - 5)

    # Bonus for positive IC rate
    if monthly_ic_positive_rate > 0.7:
        base = _clamp(base + 5)

    return _clamp(base)


def score_portfolio_extraction(
    sharpe: float,
    annualized_return: float,
    max_drawdown: float,
    positive_month_rate: float,
) -> float:
    """6.3 portfolio_extraction_score"""
    # Map each metric to 0-100
    # Sharpe: -2 to 3 → 0-100
    sharpe_score = _map_range(sharpe, -2.0, 3.0, 0, 100)

    # Annualized return: -0.5 to 1.0 → 0-100
    ar_score = _map_range(annualized_return, -0.5, 1.0, 0, 100)

    # Max drawdown: -1.0 to 0.0 → 0-100 (less negative = better)
    dd_score = _map_range(max_drawdown, -1.0, 0.0, 0, 100)

    # Positive month rate: 0 to 1 → 0-100
    pmr_score = _map_range(positive_month_rate, 0.0, 1.0, 0, 100)

    # Weighted average
    score = (
        sharpe_score * 0.40
        + ar_score * 0.20
        + dd_score * 0.20
        + pmr_score * 0.20
    )
    return _clamp(score)


def score_stability(
    monthly_ic_positive_rate: float,
    long_short_positive_month_rate: float,
    max_drawdown: float,
) -> float:
    """6.4 stability_score"""
    ic_score = _map_range(monthly_ic_positive_rate, 0.0, 1.0, 0, 100)
    ls_pmr_score = _map_range(long_short_positive_month_rate, 0.0, 1.0, 0, 100)
    dd_score = _map_range(max_drawdown, -1.0, 0.0, 0, 100)

    score = (
        ic_score * 0.40
        + ls_pmr_score * 0.30
        + dd_score * 0.30
    )
    return _clamp(score)


def score_direction_interpretability(metadata_quality: str) -> float:
    """6.6 direction_interpretability_score"""
    mapping = {
        "COMPLETE": 90,
        "DIRECTION_AMBIGUOUS": 60,
        "NEEDS_REVIEW": 30,
        "FORMULA_AMBIGUOUS": 20,
    }
    return float(mapping.get(metadata_quality, 30))


def score_redundancy_novelty(
    redundancy_map: dict[str, dict[str, Any]],
    factor_id: str,
    summary_map: dict[str, dict[str, Any]] | None = None,
    calibrated_confidence: str = "LOW",
) -> tuple[float, str]:
    """6.7 redundancy_novelty_score. Returns (score, confidence).
    Uses PM-18 redundancy summary if available, falls back to pairwise map.
    PM-19: Uses calibrated_confidence instead of PM-18 blanket LOW.
    """
    # Prefer summary map from PM-18
    if summary_map and factor_id in summary_map:
        entry = summary_map[factor_id]
        # PM-19: use calibrated confidence instead of PM-18 blanket LOW
        conf = calibrated_confidence
        novelty = entry.get("novelty_assessment", "INSUFFICIENT_OVERLAP")
        strongest = entry.get("strongest_redundancy_level", "")

        if novelty == "HIGHLY_REDUNDANT":
            return 20.0, conf
        elif novelty == "MODERATELY_REDUNDANT":
            return 40.0, conf
        elif novelty == "LIKELY_DISTINCT":
            return 70.0, conf
        elif novelty == "INSUFFICIENT_OVERLAP":
            return 40.0, "LOW"
        else:
            return 50.0, conf

    # Fallback to pairwise map
    entry = redundancy_map.get(factor_id)
    if entry is None:
        return 50.0, "LOW"

    level = entry.get("redundancy_level", "")
    if level == "NEAR_DUPLICATE":
        return 20.0, "MEDIUM"
    elif level == "MODERATE_REDUNDANCY":
        return 40.0, "MEDIUM"
    elif level == "LOW_REDUNDANCY":
        return 70.0, "MEDIUM"
    else:
        return 50.0, "LOW"


# ── Final score and class assignment ────────────────────────────────────────

def compute_final_score(scores: dict[str, float]) -> float:
    """Weighted average of all 7 dimension scores."""
    total = 0.0
    for dim, weight in DIMENSION_WEIGHTS.items():
        total += scores[dim] * weight
    return round(total, 2)


def assign_quality_class(
    final_score: float,
    metadata_quality: str,
    comp_score: float,
    pred_score: float,
    port_score: float,
    stability_score: float,
    dir_score: float,
) -> str:
    """Priority-ordered class assignment."""
    mq = metadata_quality

    # 1. REVIEW_REQUIRED if metadata quality flags
    if mq in ("NEEDS_REVIEW", "FORMULA_AMBIGUOUS"):
        return "REVIEW_REQUIRED"

    # 2. INSUFFICIENT_EVIDENCE if computation is low
    if comp_score < 50:
        return "INSUFFICIENT_EVIDENCE"

    # 3. INSUFFICIENT_EVIDENCE if both predictive and portfolio are very low
    if pred_score < 30 and port_score < 30:
        return "INSUFFICIENT_EVIDENCE"

    # 4. STRONG_RESEARCH_CANDIDATE
    if final_score >= 70 and mq == "COMPLETE" and stability_score >= 60:
        return "STRONG_RESEARCH_CANDIDATE"

    # 5. DIRECTION_DEPENDENT
    if dir_score < 60:
        return "DIRECTION_DEPENDENT"

    # 6. PROMISING_BUT_INCONSISTENT
    if pred_score >= 60 or port_score >= 60:
        return "PROMISING_BUT_INCONSISTENT"

    # 7. REDUNDANT_OR_WEAK
    if final_score < 40:
        return "REDUNDANT_OR_WEAK"

    # 8. Default
    return "PROMISING_BUT_INCONSISTENT"


def assign_score_confidence(
    metadata_quality: str,
    redundancy_confidence: str,
    coverage: float,
) -> str:
    if metadata_quality == "COMPLETE" and redundancy_confidence != "LOW" and coverage >= 0.95:
        return "HIGH"
    elif metadata_quality == "COMPLETE" or (coverage >= 0.95 and redundancy_confidence == "LOW"):
        return "MEDIUM"
    else:
        return "LOW"


def assign_next_action(quality_class: str, has_redundancy_evidence: bool) -> str:
    if quality_class == "STRONG_RESEARCH_CANDIDATE":
        return "KEEP_FOR_RESEARCH_REVIEW"
    elif quality_class == "DIRECTION_DEPENDENT":
        return "REVIEW_DIRECTION_BEFORE_USE"
    elif quality_class == "REVIEW_REQUIRED":
        return "REVIEW_FORMULA_OR_METADATA"
    elif quality_class == "REDUNDANT_OR_WEAK":
        if has_redundancy_evidence:
            return "REVIEW_REDUNDANCY_FIRST"
        else:
            return "LOW_PRIORITY_WEAK_EVIDENCE"
    elif quality_class == "INSUFFICIENT_EVIDENCE":
        return "INSUFFICIENT_DATA"
    elif quality_class == "PROMISING_BUT_INCONSISTENT":
        return "KEEP_FOR_RESEARCH_REVIEW"
    else:
        return "KEEP_FOR_RESEARCH_REVIEW"


# ── Strengths / Weaknesses / Notes generation ───────────────────────────────

DIMENSION_LABELS = {
    "computation_integrity": ("计算完整性", "Computation Integrity"),
    "predictive_ranking": ("预测排名能力", "Predictive Ranking"),
    "portfolio_extraction": ("组合提取能力", "Portfolio Extraction"),
    "stability": ("稳定性", "Stability"),
    "quantile_shape": ("分位形状", "Quantile Shape"),
    "direction_interpretability": ("方向可解释性", "Direction Interpretability"),
    "redundancy_novelty": ("新颖性与冗余度", "Redundancy / Novelty"),
}


def generate_strengths_weaknesses(scores: dict[str, float]) -> dict[str, str]:
    """Generate bilingual strengths/weaknesses from dimension scores."""
    # Sort dimensions by score
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    strengths_zh_parts = []
    strengths_en_parts = []
    weaknesses_zh_parts = []
    weaknesses_en_parts = []

    # Top 2 as strengths (score >= 60)
    for dim, score in ranked[:2]:
        if score >= 60:
            zh, en = DIMENSION_LABELS[dim]
            strengths_zh_parts.append(f"{zh}({score:.0f})")
            strengths_en_parts.append(f"{en}({score:.0f})")

    # Bottom 2 as weaknesses (score < 60)
    for dim, score in ranked[-2:]:
        if score < 60:
            zh, en = DIMENSION_LABELS[dim]
            weaknesses_zh_parts.append(f"{zh}({score:.0f})")
            weaknesses_en_parts.append(f"{en}({score:.0f})")

    # Fallbacks
    if not strengths_zh_parts:
        strengths_zh_parts.append("无突出优势")
        strengths_en_parts.append("No standout strengths")
    if not weaknesses_zh_parts:
        weaknesses_zh_parts.append("无明显短板")
        weaknesses_en_parts.append("No major weaknesses")

    return {
        "strengths_zh": "; ".join(strengths_zh_parts),
        "strengths_en": "; ".join(strengths_en_parts),
        "weaknesses_zh": "; ".join(weaknesses_zh_parts),
        "weaknesses_en": "; ".join(weaknesses_en_parts),
    }


def generate_review_notes(
    metadata_quality: str,
    quality_class: str,
    qa_notes_zh: str,
    qa_notes_en: str,
    source_warning: str,
    redundancy_confidence: str,
) -> dict[str, str]:
    zh_parts = []
    en_parts = []

    if metadata_quality != "COMPLETE":
        zh_parts.append(f"元数据质量: {metadata_quality}")
        en_parts.append(f"Metadata quality: {metadata_quality}")

    if quality_class == "REVIEW_REQUIRED":
        zh_parts.append("需人工审查公式或元数据")
        en_parts.append("Formula or metadata needs human review")

    if quality_class == "DIRECTION_DEPENDENT":
        zh_parts.append("方向依赖条件，需确认使用方式")
        en_parts.append("Direction is conditional; verify usage context")

    if _safe_str(source_warning):
        zh_parts.append(f"来源警告: {source_warning}")
        en_parts.append(f"Source warning: {source_warning}")

    if redundancy_confidence == "LOW":
        zh_parts.append("冗余数据不完整，无法充分评估新颖性")
        en_parts.append("Redundancy data incomplete; novelty not fully assessed")

    if _safe_str(qa_notes_zh):
        zh_parts.append(f"QA: {qa_notes_zh[:100]}")
    if _safe_str(qa_notes_en):
        en_parts.append(f"QA: {qa_notes_en[:100]}")

    if not zh_parts:
        zh_parts.append("无特殊标记")
    if not en_parts:
        en_parts.append("No special flags")

    return {
        "notes_zh": "; ".join(zh_parts),
        "notes_en": "; ".join(en_parts),
    }


# ── Main scorecard builder ──────────────────────────────────────────────────

def build_scorecard() -> pd.DataFrame:
    print("[PM-16B] Loading input data...")

    diag = load_diagnostics_summary()
    cards = load_bilingual_cards()
    qa = load_qa_report()
    quantile_df = load_quantile_summary()
    redundancy_df = load_redundancy()
    redundancy_summary = load_redundancy_summary()
    redundancy_clusters = load_redundancy_clusters()
    state = load_library_state()

    registered_ids = state.get("registered_factor_ids", [])
    print(f"[PM-16B] {len(registered_ids)} registered factors in library state")
    print(f"[PM-16B] {len(diag)} rows in diagnostics summary")
    print(f"[PM-16B] {len(cards)} rows in bilingual cards")
    print(f"[PM-16B] {len(qa)} rows in QA report")
    print(f"[PM-16B] {len(quantile_df)} rows in quantile summary")
    print(f"[PM-16B] {len(redundancy_df)} rows in pairwise redundancy")
    print(f"[PM-16B] {len(redundancy_summary)} rows in redundancy summary")
    print(f"[PM-16B] {len(redundancy_clusters)} rows in redundancy clusters")

    # Build lookups
    quantile_shapes = compute_quantile_shapes(quantile_df)
    redundancy_map = build_redundancy_map(redundancy_df)

    # Build summary map from PM-18 redundancy summary
    summary_map: dict[str, dict[str, Any]] = {}
    if not redundancy_summary.empty:
        for _, row in redundancy_summary.iterrows():
            fid = str(row.get("factor_id", "")).strip()
            summary_map[fid] = {
                "redundancy_confidence": str(row.get("redundancy_confidence", "LOW")).strip(),
                "novelty_assessment": str(row.get("novelty_assessment", "INSUFFICIENT_OVERLAP")).strip(),
                "nearest_factor": str(row.get("nearest_factor", "")).strip(),
                "nearest_abs_spearman_corr": _safe_float(row.get("nearest_abs_spearman_corr", 0)),
                "strongest_redundancy_level": str(row.get("strongest_redundancy_level", "")).strip(),
                "n_high_redundancy_pairs": int(row.get("n_high_redundancy_pairs", 0)),
                "n_valid_pairs": int(row.get("n_valid_pairs", 0)),
            }

    # Build cluster map from PM-18 clusters
    cluster_map: dict[str, dict[str, Any]] = {}
    if not redundancy_clusters.empty:
        for _, row in redundancy_clusters.iterrows():
            fid = str(row.get("factor_id", "")).strip()
            cluster_map[fid] = {
                "cluster_id": int(row.get("cluster_id", -1)),
                "cluster_size": int(row.get("cluster_size", 1)),
                "cluster_members": str(row.get("cluster_members", "")).strip(),
            }

    # PM-19: Compute expected pair count (N-1 for N registered factors)
    n_factors = len(registered_ids)
    expected_pairs = max(n_factors - 1, 1)
    print(f"[PM-19] Expected redundancy pairs per factor: {expected_pairs}")

    # ── PM-43A: Load canonical sources for fallback ──
    canonical_rankic = load_canonical_rankic()
    canonical_ls = load_canonical_ls()
    print(f"  Canonical RankIC: {len(canonical_rankic)} factors")
    print(f"  Canonical LS: {len(canonical_ls)} factors")

    # Score each factor
    rows = []
    for fid in sorted(registered_ids):
        # ── Pull data from all sources ──
        diag_row = diag.loc[fid] if fid in diag.index else None
        card_row = cards.loc[fid] if fid in cards.index else None
        qa_row = qa.loc[fid] if fid in qa.index else None

        if diag_row is None:
            print(f"  [WARN] {fid}: missing from diagnostics_summary, using defaults")

        # Extract fields
        family = _safe_str(diag_row["family"]) if diag_row is not None else ""
        best_horizon = _safe_str(diag_row["best_horizon"]) if diag_row is not None else "4h"
        # PM-43A: fallback best_horizon from canonical if missing
        if not best_horizon and fid in canonical_rankic:
            # Use the first available horizon from canonical
            best_horizon = next(iter(canonical_rankic[fid]), "4h")
        coverage = _safe_float(diag_row["coverage_rate"], 0.0) if diag_row is not None else 0.0
        source_warning = _safe_str(diag_row.get("source_warning", "")) if diag_row is not None else ""

        # Metadata quality: from QA report (preferred) or bilingual cards
        metadata_quality = "NEEDS_REVIEW"
        if qa_row is not None:
            metadata_quality = _safe_str(qa_row.get("metadata_quality", "NEEDS_REVIEW"))
        elif card_row is not None:
            metadata_quality = _safe_str(card_row.get("metadata_quality", "NEEDS_REVIEW"))

        if metadata_quality not in METADATA_QUALITY_VALUES:
            metadata_quality = "NEEDS_REVIEW"

        # Bilingual names
        name_zh = ""
        name_en = ""
        if card_row is not None:
            name_zh = _safe_str(card_row.get("name_zh", ""))
            name_en = _safe_str(card_row.get("name_en", ""))

        # ── PM-43A: Canonical fallback for RankIC and LS metrics ──
        canon_rk = canonical_rankic.get(fid, {}).get(best_horizon, {})
        canon_ls_data = canonical_ls.get(fid, {}).get(best_horizon, {})

        # RankIC metrics — prefer diagnostics, fallback to canonical
        rankic_mean = _safe_float(diag_row["rankic_mean"]) if diag_row is not None else 0.0
        if rankic_mean == 0.0 and canon_rk:
            rankic_mean = canon_rk.get("rankic_mean", 0.0)
        rankic_ir = _safe_float(diag_row["rankic_ir"]) if diag_row is not None else 0.0
        if rankic_ir == 0.0 and canon_rk:
            rankic_ir = canon_rk.get("rankic_ir", 0.0)
        rankic_t_stat = _safe_float(diag_row["rankic_t_stat"]) if diag_row is not None else 0.0
        if rankic_t_stat == 0.0 and canon_rk:
            rankic_t_stat = canon_rk.get("t_stat", 0.0)
        monthly_ic_positive_rate = _safe_float(diag_row["monthly_ic_positive_rate"]) if diag_row is not None else 0.0

        # Coverage fallback: if diagnostics has 0 but canonical has data, factor is WORKFLOW_READY
        if coverage == 0.0 and canon_rk:
            coverage = 1.0

        # Portfolio metrics — prefer diagnostics, fallback to canonical
        ls_sharpe = _safe_float(diag_row["long_short_sharpe"]) if diag_row is not None else 0.0
        if ls_sharpe == 0.0 and canon_ls_data:
            ls_sharpe = canon_ls_data.get("ls_sharpe", 0.0)
        ls_ann_return = _safe_float(diag_row["long_short_annualized_return"]) if diag_row is not None else 0.0
        if ls_ann_return == 0.0 and canon_ls_data:
            ls_ann_return = canon_ls_data.get("ls_ann_return", 0.0)
        ls_max_dd = _safe_float(diag_row["long_short_max_drawdown"]) if diag_row is not None else 0.0
        if ls_max_dd == 0.0 and canon_ls_data:
            ls_max_dd = canon_ls_data.get("ls_max_dd", 0.0)
        ls_pmr = _safe_float(diag_row["long_short_positive_month_rate"]) if diag_row is not None else 0.0
        if ls_pmr == 0.0 and canon_ls_data:
            ls_pmr = canon_ls_data.get("ls_pmr", 0.0)

        abs_rankic = abs(rankic_mean)

        # ── Score each dimension ──
        comp_score = score_computation_integrity(coverage, source_warning, metadata_quality)
        pred_score = score_predictive_ranking(abs_rankic, rankic_ir, rankic_t_stat, monthly_ic_positive_rate)
        port_score = score_portfolio_extraction(ls_sharpe, ls_ann_return, ls_max_dd, ls_pmr)
        stab_score = score_stability(monthly_ic_positive_rate, ls_pmr, ls_max_dd)
        quant_label, quant_score = get_quantile_shape_for_factor(quantile_shapes, fid, best_horizon)
        dir_score = score_direction_interpretability(metadata_quality)

        # PM-19: Compute calibrated redundancy confidence
        summ = summary_map.get(fid, {})
        n_valid = summ.get("n_valid_pairs", 0)
        strongest_lvl = summ.get("strongest_redundancy_level", "")
        novelty_val = summ.get("novelty_assessment", "INSUFFICIENT_OVERLAP")
        cal_conf = compute_calibrated_redundancy_confidence(
            n_valid, expected_pairs, strongest_lvl, novelty_val,
        )
        red_score, red_conf = score_redundancy_novelty(
            redundancy_map, fid, summary_map, cal_conf,
        )

        scores = {
            "computation_integrity": comp_score,
            "predictive_ranking": pred_score,
            "portfolio_extraction": port_score,
            "stability": stab_score,
            "quantile_shape": quant_score,
            "direction_interpretability": dir_score,
            "redundancy_novelty": red_score,
        }

        final_score = compute_final_score(scores)

        has_red_evidence = fid in redundancy_map or fid in summary_map
        quality_class = assign_quality_class(
            final_score, metadata_quality, comp_score,
            pred_score, port_score, stab_score, dir_score,
        )
        score_conf = assign_score_confidence(metadata_quality, red_conf, coverage)
        next_action = assign_next_action(quality_class, has_red_evidence)

        # Strengths/weaknesses
        sw = generate_strengths_weaknesses(scores)

        # Review notes
        qa_zh = _safe_str(qa_row.get("qa_notes_zh", "")) if qa_row is not None else ""
        qa_en = _safe_str(qa_row.get("qa_notes_en", "")) if qa_row is not None else ""
        notes = generate_review_notes(
            metadata_quality, quality_class, qa_zh, qa_en,
            source_warning, red_conf,
        )

        row = {
            "factor_id": fid,
            "name_zh": name_zh,
            "name_en": name_en,
            "family": family,
            "metadata_quality": metadata_quality,
            "best_horizon": best_horizon,
            "final_quality_class": quality_class,
            "final_quality_score": final_score,
            "score_confidence": score_conf,
            "computation_integrity_score": round(comp_score, 1),
            "predictive_ranking_score": round(pred_score, 1),
            "portfolio_extraction_score": round(port_score, 1),
            "stability_score": round(stab_score, 1),
            "quantile_shape_score": round(quant_score, 1),
            "direction_interpretability_score": round(dir_score, 1),
            "redundancy_novelty_score": round(red_score, 1),
            "redundancy_confidence": red_conf,
            "coverage_rate": round(coverage, 6),
            "rankic_mean": round(rankic_mean, 6),
            "rankic_ir": round(rankic_ir, 4),
            "monthly_ic_positive_rate": round(monthly_ic_positive_rate, 4),
            "long_short_sharpe": round(ls_sharpe, 4),
            "long_short_annualized_return": round(ls_ann_return, 6),
            "long_short_max_drawdown": round(ls_max_dd, 6),
            "long_short_positive_month_rate": round(ls_pmr, 4),
            "quantile_shape": quant_label,
            "main_strengths_zh": sw["strengths_zh"],
            "main_weaknesses_zh": sw["weaknesses_zh"],
            "main_strengths_en": sw["strengths_en"],
            "main_weaknesses_en": sw["weaknesses_en"],
            "review_notes_zh": notes["notes_zh"],
            "review_notes_en": notes["notes_en"],
            "recommended_next_action": next_action,
        }

        # PM-19: Add calibrated redundancy detail fields
        insuff_count = 0
        if not redundancy_df.empty:
            mask_i = redundancy_df["factor_i"].astype(str).str.strip() == fid
            mask_j = redundancy_df["factor_j"].astype(str).str.strip() == fid
            pairs_for_fid = redundancy_df[mask_i | mask_j]
            insuff_count = int((pairs_for_fid["redundancy_level"] == "INSUFFICIENT_OVERLAP").sum())

        nearest_fid = summ.get("nearest_factor", "")
        nearest_corr = summ.get("nearest_abs_spearman_corr", 0.0)
        cl = cluster_map.get(fid, {})
        cl_id = cl.get("cluster_id", -1)
        cl_size = cl.get("cluster_size", 1)
        cl_members = cl.get("cluster_members", "")

        row["valid_redundancy_pair_count"] = n_valid
        row["expected_redundancy_pair_count"] = expected_pairs
        row["valid_redundancy_pair_coverage"] = round(n_valid / expected_pairs, 4) if expected_pairs > 0 else 0.0
        row["insufficient_overlap_pair_count"] = insuff_count
        row["nearest_factor"] = nearest_fid
        row["nearest_abs_spearman_corr"] = round(nearest_corr, 6) if nearest_corr else 0.0
        row["strongest_redundancy_level"] = strongest_lvl
        row["novelty_assessment"] = novelty_val
        row["redundancy_cluster_id"] = cl_id
        row["redundancy_cluster_size"] = cl_size

        rows.append(row)

    df = pd.DataFrame(rows)

    # Ensure column order matches spec
    col_order = [
        "factor_id", "name_zh", "name_en", "family", "metadata_quality",
        "best_horizon", "final_quality_class", "final_quality_score",
        "score_confidence", "computation_integrity_score", "predictive_ranking_score",
        "portfolio_extraction_score", "stability_score", "quantile_shape_score",
        "direction_interpretability_score", "redundancy_novelty_score",
        "redundancy_confidence", "coverage_rate", "rankic_mean", "rankic_ir",
        "monthly_ic_positive_rate", "long_short_sharpe", "long_short_annualized_return",
        "long_short_max_drawdown", "long_short_positive_month_rate", "quantile_shape",
        "main_strengths_zh", "main_weaknesses_zh", "main_strengths_en",
        "main_weaknesses_en", "review_notes_zh", "review_notes_en",
        "recommended_next_action",
        # PM-19 redundancy detail fields
        "valid_redundancy_pair_count", "expected_redundancy_pair_count",
        "valid_redundancy_pair_coverage", "insufficient_overlap_pair_count",
        "nearest_factor", "nearest_abs_spearman_corr",
        "strongest_redundancy_level", "novelty_assessment",
        "redundancy_cluster_id", "redundancy_cluster_size",
    ]
    df = df[col_order]

    return df


# ── Output writers ───────────────────────────────────────────────────────────

def write_csv(df: pd.DataFrame) -> None:
    df.to_csv(OUT_CSV, index=False)
    print(f"[PM-16B] Wrote {len(df)} rows to {OUT_CSV}")


def write_json(df: pd.DataFrame) -> None:
    records = df.to_dict(orient="records")
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False, default=str)
    print(f"[PM-16B] Wrote {len(records)} records to {OUT_JSON}")


def write_manifest(df: pd.DataFrame) -> None:
    # Class distribution
    class_dist = df["final_quality_class"].value_counts().to_dict()
    for c in QUALITY_CLASSES:
        class_dist.setdefault(c, 0)

    conf_dist = df["score_confidence"].value_counts().to_dict()
    for c in ("HIGH", "MEDIUM", "LOW"):
        conf_dist.setdefault(c, 0)

    # PM-19: Redundancy confidence distribution
    red_conf_dist = df["redundancy_confidence"].value_counts().to_dict()
    for c in ("HIGH", "MEDIUM", "LOW"):
        red_conf_dist.setdefault(c, 0)

    action_dist = df["recommended_next_action"].value_counts().to_dict()

    # Score statistics
    score_cols = [
        "computation_integrity_score", "predictive_ranking_score",
        "portfolio_extraction_score", "stability_score", "quantile_shape_score",
        "direction_interpretability_score", "redundancy_novelty_score",
    ]
    score_stats = {}
    for col in score_cols:
        score_stats[col] = {
            "mean": round(float(df[col].mean()), 2),
            "median": round(float(df[col].median()), 2),
            "min": round(float(df[col].min()), 2),
            "max": round(float(df[col].max()), 2),
        }

    manifest = {
        "framework_version": "pm16b_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_factors": len(df),
        "disclaimer": "Research triage tool. Not a trading signal.",
        "do_not_use_as_trade_signal": True,
        "dimension_weights": DIMENSION_WEIGHTS,
        "quality_class_distribution": class_dist,
        "score_confidence_distribution": conf_dist,
        "redundancy_confidence_distribution": red_conf_dist,
        "recommended_action_distribution": action_dist,
        "score_statistics": score_stats,
        "quality_classes": QUALITY_CLASSES,
        "input_files": [
            str(PATH_DIAG_SUMMARY),
            str(PATH_BILINGUAL),
            str(PATH_QA),
            str(PATH_QUANTILE),
            str(PATH_REDUNDANCY),
            str(PATH_STATE),
        ],
        "output_files": [
            str(OUT_CSV),
            str(OUT_JSON),
            str(OUT_MANIFEST),
        ],
    }

    with open(OUT_MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False, default=str)
    print(f"[PM-16B] Wrote manifest to {OUT_MANIFEST}")


# ── Entry point ──────────────────────────────────────────────────────────────

def main() -> int:
    print("=" * 60)
    print("PM-16B: Factor Quality Scorecard Builder")
    print("Framework: pm16b_v1")
    print("NOT a trading signal. Research triage tool only.")
    print("=" * 60)

    df = build_scorecard()

    write_csv(df)
    write_json(df)
    write_manifest(df)

    # Print summary
    print("\n" + "=" * 60)
    print("QUALITY CLASS DISTRIBUTION:")
    for cls in QUALITY_CLASSES:
        count = len(df[df["final_quality_class"] == cls])
        print(f"  {cls}: {count}")

    print("\nSCORE CONFIDENCE DISTRIBUTION:")
    for conf in ("HIGH", "MEDIUM", "LOW"):
        count = len(df[df["score_confidence"] == conf])
        print(f"  {conf}: {count}")

    print("\nREDUNDANCY CONFIDENCE DISTRIBUTION (PM-19 calibrated):")
    for conf in ("HIGH", "MEDIUM", "LOW"):
        count = len(df[df["redundancy_confidence"] == conf])
        print(f"  {conf}: {count}")

    print(f"\nFinal score range: {df['final_quality_score'].min():.1f} – {df['final_quality_score'].max():.1f}")
    print(f"Mean final score: {df['final_quality_score'].mean():.1f}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
