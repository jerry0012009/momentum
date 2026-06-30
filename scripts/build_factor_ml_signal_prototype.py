#!/usr/bin/env python3
"""Build the first minimal ML signal prototype from the factor library.

This is a research prototype, not a trading system. It reads the existing
factor quality scorecard, selects a compact feature set from ML-eligible
factors, trains simple time-aware models, and writes auditable research
artifacts under the factor run directory.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from momentum.signal_evaluation import (  # noqa: E402
    check_rankic_spread_consistency,
    compute_quantile_spread,
    compute_rank_ic,
    select_forward_return,
    summarize_quantile_spread,
    summarize_rank_ic,
)
from funding_adjusted_labels import add_funding_adjusted_returns, infer_funding_aligned_path  # noqa: E402

DEFAULT_DATASET_ID = "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
RUN_BASE = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"
DIAG_DIR = RUN_BASE / "factor_diagnostics"
DEFAULT_SCORECARD = DIAG_DIR / "factor_quality_scorecard.csv"
DEFAULT_OUT_DIR = RUN_BASE / "ml_signal_prototype"
HORIZONS = ["1h", "4h", "24h", "72h"]
PRICE_LABEL_COLS = {h: f"ret_fwd_{h}" for h in HORIZONS}
AFTER_FUNDING_LABEL_COLS = {h: f"ret_fwd_{h}_after_funding" for h in HORIZONS}
LS_UTILITY_AFTER_FUNDING_LABEL_COLS = {h: f"ls_utility_{h}_after_funding" for h in HORIZONS}
LABEL_COLS = PRICE_LABEL_COLS
HIGH_REDUNDANCY_LEVELS = {"NEAR_DUPLICATE", "HIGH_REDUNDANCY"}
SEVERE_RISK_FLAGS = {
    "low_coverage",
    "formula_ambiguous",
    "rankic_not_robust",
}


@dataclass(frozen=True)
class FeatureSelectionConfig:
    target_features: int = 100
    min_features: int = 80
    max_features: int = 120
    cluster_cap: int = 3
    selection_policy: str = "default"


@dataclass(frozen=True)
class ModelConfig:
    min_train_months: int = 12
    max_walk_forward_splits: int = 4
    max_train_rows: int = 160_000
    max_tree_train_rows: int = 40_000
    min_feature_fraction: float = 0.20
    random_seed: int = 7
    ridge_alpha: float = 25.0


def _safe_float(v: Any, default: float = 0.0) -> float:
    try:
        if pd.isna(v):
            return default
        return float(v)
    except Exception:
        return default


def parse_risk_flags(raw: Any) -> set[str]:
    if raw is None or (isinstance(raw, float) and math.isnan(raw)):
        return set()
    return {x.strip() for x in str(raw).split("|") if x.strip()}


def _safe_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in {"true", "1", "yes", "y"}


def label_cols_for_mode(label_mode: str) -> dict[str, str]:
    if label_mode == "price":
        return PRICE_LABEL_COLS
    if label_mode == "after_funding":
        return AFTER_FUNDING_LABEL_COLS
    if label_mode == "ls_utility_after_funding":
        return LS_UTILITY_AFTER_FUNDING_LABEL_COLS
    raise ValueError(f"Unsupported label mode: {label_mode}")


def eval_label_cols_for_mode(label_mode: str) -> dict[str, str]:
    if label_mode == "price":
        return PRICE_LABEL_COLS
    if label_mode in {"after_funding", "ls_utility_after_funding"}:
        return AFTER_FUNDING_LABEL_COLS
    raise ValueError(f"Unsupported label mode: {label_mode}")


def build_ls_utility_after_funding_targets(
    labels: pd.DataFrame,
    horizons: list[str],
    tail_fraction: float = 0.20,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    if not 0.0 < tail_fraction < 0.50:
        raise ValueError(f"tail_fraction must be between 0 and 0.5, got {tail_fraction}")

    out = labels.copy()
    coverage: list[dict[str, Any]] = []
    for horizon in horizons:
        source_col = AFTER_FUNDING_LABEL_COLS[horizon]
        target_col = LS_UTILITY_AFTER_FUNDING_LABEL_COLS[horizon]
        if source_col not in out.columns:
            raise ValueError(f"missing after-funding return column for LS utility target: {source_col}")

        utility = pd.Series(np.nan, index=out.index, dtype=np.float32)
        valid = out[["timestamp", source_col]].dropna()
        if not valid.empty:
            ranks = valid.groupby("timestamp", sort=False)[source_col].rank(method="first", pct=True)
            values = np.zeros(len(valid), dtype=np.float32)
            values[ranks.to_numpy() <= tail_fraction] = -1.0
            values[ranks.to_numpy() > (1.0 - tail_fraction)] = 1.0
            utility.loc[valid.index] = values
        out[target_col] = utility.astype(np.float32)

        finite = out[target_col].dropna()
        coverage.append({
            "horizon": horizon,
            "target_col": target_col,
            "source_col": source_col,
            "tail_fraction": tail_fraction,
            "rows": int(len(out)),
            "valid_rows": int(len(finite)),
            "valid_fraction": float(len(finite) / len(out)) if len(out) else math.nan,
            "long_rows": int((finite > 0).sum()),
            "short_rows": int((finite < 0).sum()),
            "middle_rows": int((finite == 0).sum()),
        })

    manifest = {
        "status": "LS_UTILITY_AFTER_FUNDING_LABELS_COMPUTED",
        "description": (
            "Per timestamp and horizon, top after-funding return quintile is +1, "
            "bottom quintile is -1, and the middle cross-section is 0."
        ),
        "coverage_by_horizon": coverage,
    }
    return out, manifest


def load_scorecard(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {
        "factor_id",
        "ml_gate_status",
        "review_substatus",
        "final_quality_score",
        "coverage_rate",
        "rankic_mean",
        "long_short_sharpe",
        "monthly_ic_positive_rate",
        "strongest_redundancy_level",
        "redundancy_cluster_id",
        "ml_gate_risk_flags",
    }
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"scorecard missing required columns: {missing}")
    return df


def score_feature_row(row: pd.Series) -> tuple[float, str]:
    flags = parse_risk_flags(row.get("ml_gate_risk_flags", ""))
    score = _safe_float(row.get("final_quality_score"))
    score += 20.0 * _safe_float(row.get("coverage_rate"))
    score += 18.0 * abs(_safe_float(row.get("rankic_mean")))
    score += 3.0 * max(_safe_float(row.get("long_short_sharpe")), 0.0)
    score += 8.0 * _safe_float(row.get("monthly_ic_positive_rate"))

    if row.get("review_substatus") == "REVIEW_METADATA_ONLY":
        score += 2.0
    if row.get("review_substatus") == "REVIEW_DIRECTION_SEMANTICS":
        score -= 1.0
    if row.get("strongest_redundancy_level") in HIGH_REDUNDANCY_LEVELS:
        score -= 8.0
    if "cost_collapsed" in flags:
        score -= 5.0
    if "non_monotonic_quantiles" in flags:
        score -= 4.0
    if "ls_not_robust" in flags:
        score -= 3.0
    if "rankic_not_robust" in flags:
        score -= 8.0
    if "low_coverage" in flags:
        score -= 20.0

    reason = [
        f"quality={_safe_float(row.get('final_quality_score')):.2f}",
        f"coverage={_safe_float(row.get('coverage_rate')):.3f}",
        f"abs_rankic={abs(_safe_float(row.get('rankic_mean'))):.4f}",
    ]
    if flags:
        reason.append("risk_flags=" + "|".join(sorted(flags)))
    return score, "; ".join(reason)


def select_core_features(
    scorecard: pd.DataFrame,
    cfg: FeatureSelectionConfig,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    candidates = scorecard[scorecard["ml_gate_status"] != "ML_HOLD"].copy()
    candidates[["selection_score", "selection_reason"]] = candidates.apply(
        lambda r: pd.Series(score_feature_row(r)),
        axis=1,
    )
    candidates["_risk_count"] = candidates["ml_gate_risk_flags"].apply(lambda x: len(parse_risk_flags(x)))
    candidates["_severe_risk_count"] = candidates["ml_gate_risk_flags"].apply(
        lambda x: len(parse_risk_flags(x) & SEVERE_RISK_FLAGS)
    )
    if cfg.selection_policy == "after_funding_ls":
        candidates["selection_score"] += candidates.apply(score_after_funding_row, axis=1)
    candidates = candidates.sort_values(
        ["selection_score", "coverage_rate", "final_quality_score"],
        ascending=[False, False, False],
    )
    if cfg.selection_policy == "ls_ic_aligned":
        candidates = candidates.copy()
        candidates["_is_strict_ls_ic_aligned"] = candidates.apply(is_strict_ls_ic_aligned, axis=1)
        candidates["_is_fallback_ls_ic_aligned"] = candidates.apply(is_fallback_ls_ic_aligned, axis=1)
        strict_candidates = candidates[candidates["_is_strict_ls_ic_aligned"]].copy()
        fallback_candidates = candidates[
            candidates["_is_fallback_ls_ic_aligned"] & ~candidates["_is_strict_ls_ic_aligned"]
        ].copy()
        pool = pd.concat([strict_candidates, fallback_candidates], ignore_index=True)
    elif cfg.selection_policy == "after_funding_ls":
        candidates = candidates.copy()
        candidates["_is_strict_ls_ic_aligned"] = candidates.apply(is_strict_after_funding_ls, axis=1)
        candidates["_is_fallback_ls_ic_aligned"] = candidates.apply(is_fallback_after_funding_ls, axis=1)
        strict_candidates = candidates[candidates["_is_strict_ls_ic_aligned"]].copy()
        fallback_candidates = candidates[
            candidates["_is_fallback_ls_ic_aligned"] & ~candidates["_is_strict_ls_ic_aligned"]
        ].copy()
        pool = pd.concat([strict_candidates, fallback_candidates], ignore_index=True)
    else:
        candidates["_is_strict_ls_ic_aligned"] = False
        candidates["_is_fallback_ls_ic_aligned"] = False
        strict_candidates = candidates.iloc[0:0].copy()
        fallback_candidates = candidates.iloc[0:0].copy()
        pool = candidates

    selected_rows: list[pd.Series] = []
    cluster_counts: dict[int, int] = {}
    excluded_by_cluster = 0
    excluded_by_risk = 0
    selected_strict = 0
    selected_fallback = 0

    for _, row in pool.iterrows():
        if len(selected_rows) >= cfg.target_features:
            break
        severe_count = int(row["_severe_risk_count"])
        if severe_count >= 2 and len(pool) >= cfg.min_features:
            excluded_by_risk += 1
            continue
        cluster_id = int(_safe_float(row.get("redundancy_cluster_id"), -1))
        current = cluster_counts.get(cluster_id, 0)
        if current >= cfg.cluster_cap:
            excluded_by_cluster += 1
            continue
        selected_rows.append(row)
        selected_strict += int(bool(row.get("_is_strict_ls_ic_aligned", False)))
        selected_fallback += int(bool(row.get("_is_fallback_ls_ic_aligned", False)) and not bool(row.get("_is_strict_ls_ic_aligned", False)))
        cluster_counts[cluster_id] = current + 1

    selected_ids = {str(r["factor_id"]) for r in selected_rows}
    if len(selected_rows) < cfg.min_features:
        for _, row in pool.iterrows():
            fid = str(row["factor_id"])
            if fid in selected_ids:
                continue
            selected_rows.append(row)
            selected_ids.add(fid)
            selected_strict += int(bool(row.get("_is_strict_ls_ic_aligned", False)))
            selected_fallback += int(bool(row.get("_is_fallback_ls_ic_aligned", False)) and not bool(row.get("_is_strict_ls_ic_aligned", False)))
            if len(selected_rows) >= min(cfg.min_features, len(candidates)):
                break

    selected = pd.DataFrame(selected_rows).head(cfg.max_features).copy()
    if selected.empty:
        raise ValueError("No ML features selected")
    selected["selected_rank"] = np.arange(1, len(selected) + 1)
    selected["selected"] = True

    summary = {
        "eligible_factors": int(len(candidates)),
        "selection_policy": cfg.selection_policy,
        "selected_factors": int(len(selected)),
        "target_features": cfg.target_features,
        "target_min": cfg.min_features,
        "target_max": cfg.max_features,
        "cluster_cap": cfg.cluster_cap,
        "policy_pool_factors": int(len(pool)),
        "strict_ls_ic_aligned_factors": int(len(strict_candidates)),
        "fallback_ls_ic_aligned_factors": int(len(fallback_candidates)),
        "selected_strict_ls_ic_aligned": int(selected_strict),
        "selected_fallback_ls_ic_aligned": int(selected_fallback),
        "excluded_by_cluster_cap_first_pass": int(excluded_by_cluster),
        "excluded_by_severe_risk_first_pass": int(excluded_by_risk),
        "selected_count_outside_target": bool(not (cfg.min_features <= len(selected) <= cfg.max_features)),
        "outside_target_reason": ""
        if cfg.min_features <= len(selected) <= cfg.max_features
        else "auditable filters and available candidate pool produced a count outside the target range",
    }
    return selected, summary


def score_after_funding_row(row: pd.Series) -> float:
    af_spread = _safe_float(row.get("after_funding_long_short_spread"), np.nan)
    af_cov = _safe_float(row.get("after_funding_coverage_rate"), 0.0)
    if not np.isfinite(af_spread):
        return -100.0
    score = 5000.0 * max(af_spread, 0.0)
    score += 10.0 * af_cov
    if row.get("after_funding_bucket_tail_diagnosis") == "DIRECTIONALLY_CLEAN_THIN_EDGE":
        score += 8.0
    if _safe_bool(row.get("funding_adjusted_edge_flip")):
        score -= 6.0
    if af_spread <= 0:
        score -= 40.0
    return score


def is_strict_ls_ic_aligned(row: pd.Series) -> bool:
    flags = parse_risk_flags(row.get("ml_gate_risk_flags", ""))
    if flags & {"rankic_ls_direction_conflict", "ls_not_robust", "cost_collapsed", "rankic_not_robust"}:
        return False
    if _safe_float(row.get("long_short_sharpe")) <= 0:
        return False
    if _safe_float(row.get("rankic_mean")) * _safe_float(row.get("long_short_sharpe")) <= 0:
        return False
    if row.get("strongest_redundancy_level") in HIGH_REDUNDANCY_LEVELS:
        return False
    return True


def is_fallback_ls_ic_aligned(row: pd.Series) -> bool:
    flags = parse_risk_flags(row.get("ml_gate_risk_flags", ""))
    if flags & {"rankic_ls_direction_conflict", "rankic_not_robust"}:
        return False
    if _safe_float(row.get("long_short_sharpe")) <= 0:
        return False
    if _safe_float(row.get("rankic_mean")) * _safe_float(row.get("long_short_sharpe")) <= 0:
        return False
    return True


def is_strict_after_funding_ls(row: pd.Series) -> bool:
    flags = parse_risk_flags(row.get("ml_gate_risk_flags", ""))
    af_spread = _safe_float(row.get("after_funding_long_short_spread"), np.nan)
    af_cov = _safe_float(row.get("after_funding_coverage_rate"), 0.0)
    if not np.isfinite(af_spread) or af_spread <= 0:
        return False
    if af_cov < 0.80:
        return False
    if _safe_bool(row.get("funding_adjusted_edge_flip")):
        return False
    if flags & {"funding_adjusted_edge_nonpositive", "rankic_not_robust", "low_coverage", "formula_ambiguous"}:
        return False
    if row.get("strongest_redundancy_level") in HIGH_REDUNDANCY_LEVELS:
        return False
    if row.get("after_funding_bucket_tail_diagnosis") != "DIRECTIONALLY_CLEAN_THIN_EDGE":
        return False
    return True


def is_fallback_after_funding_ls(row: pd.Series) -> bool:
    flags = parse_risk_flags(row.get("ml_gate_risk_flags", ""))
    af_spread = _safe_float(row.get("after_funding_long_short_spread"), np.nan)
    af_cov = _safe_float(row.get("after_funding_coverage_rate"), 0.0)
    if not np.isfinite(af_spread) or af_spread <= 0:
        return False
    if af_cov < 0.80:
        return False
    if flags & {"funding_adjusted_edge_nonpositive", "rankic_not_robust", "low_coverage"}:
        return False
    return True


def deterministic_take(idx: np.ndarray, max_rows: int, seed: int) -> np.ndarray:
    if len(idx) <= max_rows:
        return idx
    rng = np.random.default_rng(seed)
    take = rng.choice(idx, size=max_rows, replace=False)
    return np.sort(take)


def xs_rank_to_unit(values: np.ndarray, time_codes: np.ndarray) -> np.ndarray:
    ranks = pd.Series(values).groupby(time_codes, sort=False).rank(method="average", pct=True)
    out = (ranks.to_numpy(dtype=np.float32) - 0.5) * 2.0
    out[~np.isfinite(out)] = np.nan
    return out.astype(np.float32, copy=False)


def load_aligned_factor(
    factor_id: str,
    features_dir: Path,
    key_frame: pd.DataFrame,
) -> tuple[np.ndarray, dict[str, Any]]:
    path = features_dir / factor_id / "factor_values.parquet"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_parquet(path, columns=["timestamp", "symbol", "factor_value"])
    n_keys = len(key_frame)
    duplicate_policy = "none"

    if len(df) == n_keys and df[["timestamp", "symbol"]].reset_index(drop=True).equals(key_frame):
        values = df["factor_value"].to_numpy(dtype=np.float32, copy=True)
    elif len(df) % n_keys == 0 and len(df) >= n_keys:
        last = df.iloc[-n_keys:][["timestamp", "symbol"]].reset_index(drop=True)
        if last.equals(key_frame):
            duplicate_policy = f"last_of_{len(df) // n_keys}_aligned_blocks"
            values = df.iloc[-n_keys:]["factor_value"].to_numpy(dtype=np.float32, copy=True)
        else:
            duplicate_policy = "groupby_last"
            values = merge_factor_last(df, key_frame)
    else:
        duplicate_policy = "groupby_last"
        values = merge_factor_last(df, key_frame)

    meta = {
        "factor_id": factor_id,
        "raw_rows": int(len(df)),
        "aligned_rows": int(n_keys),
        "duplicate_policy": duplicate_policy,
        "raw_non_null": int(df["factor_value"].notna().sum()),
        "aligned_non_null": int(np.isfinite(values).sum()),
    }
    return values, meta


def merge_factor_last(df: pd.DataFrame, key_frame: pd.DataFrame) -> np.ndarray:
    dedup = (
        df.sort_values(["timestamp", "symbol"])
        .groupby(["timestamp", "symbol"], sort=False, as_index=False)["factor_value"]
        .last()
    )
    keys = key_frame.copy()
    keys["_row_id"] = np.arange(len(keys))
    merged = keys.merge(dedup, on=["timestamp", "symbol"], how="left").sort_values("_row_id")
    return merged["factor_value"].to_numpy(dtype=np.float32, copy=True)


def build_feature_matrix(
    feature_ids: list[str],
    features_dir: Path,
    labels: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray, list[dict[str, Any]]]:
    key_frame = labels[["timestamp", "symbol"]].reset_index(drop=True)
    time_codes = pd.factorize(labels["timestamp"], sort=False)[0]
    x = np.empty((len(labels), len(feature_ids)), dtype=np.float32)
    load_meta: list[dict[str, Any]] = []
    for j, fid in enumerate(feature_ids):
        t0 = time.time()
        raw_values, meta = load_aligned_factor(fid, features_dir, key_frame)
        x[:, j] = xs_rank_to_unit(raw_values, time_codes)
        meta["load_seconds"] = round(time.time() - t0, 3)
        meta["transformed_non_null"] = int(np.isfinite(x[:, j]).sum())
        load_meta.append(meta)
        print(f"  feature {j + 1:03d}/{len(feature_ids)} {fid}: {meta['duplicate_policy']} ({meta['load_seconds']}s)", flush=True)
    feature_valid_count = np.isfinite(x).sum(axis=1).astype(np.int16)
    np.nan_to_num(x, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
    return x, feature_valid_count, load_meta


def walk_forward_months(
    months: np.ndarray,
    min_train_months: int,
    max_splits: int,
) -> list[tuple[np.ndarray, str]]:
    unique_months = np.array(sorted(pd.unique(months)))
    splits: list[tuple[np.ndarray, str]] = []
    for i in range(min_train_months, len(unique_months)):
        splits.append((unique_months[:i], str(unique_months[i])))
    if max_splits and len(splits) > max_splits:
        splits = splits[-max_splits:]
    return splits


def fit_baseline_ic_weighted(x_train: np.ndarray, y_train: np.ndarray) -> np.ndarray:
    y = y_train.astype(np.float64, copy=False)
    x = x_train.astype(np.float64, copy=False)
    y_std = y.std()
    if y_std <= 0 or not np.isfinite(y_std):
        return np.zeros(x.shape[1], dtype=np.float32)
    weights = np.zeros(x.shape[1], dtype=np.float64)
    y_center = y - y.mean()
    for j in range(x.shape[1]):
        col = x[:, j]
        std = col.std()
        if std <= 0 or not np.isfinite(std):
            continue
        weights[j] = ((col - col.mean()) * y_center).mean() / (std * y_std)
    denom = np.abs(weights).sum()
    if denom > 0:
        weights = weights / denom
    return weights.astype(np.float32)


def fit_models(
    x_train: np.ndarray,
    y_train: np.ndarray,
    cfg: ModelConfig,
    split_seed: int,
) -> dict[str, Any]:
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.linear_model import Ridge

    models: dict[str, Any] = {}
    models["ic_weighted_blend"] = fit_baseline_ic_weighted(x_train, y_train)

    ridge = Ridge(alpha=cfg.ridge_alpha, fit_intercept=True, random_state=cfg.random_seed)
    ridge.fit(x_train, y_train)
    models["ridge"] = ridge

    tree_idx = deterministic_take(np.arange(len(y_train)), cfg.max_tree_train_rows, split_seed)
    tree = HistGradientBoostingRegressor(
        max_iter=40,
        learning_rate=0.05,
        max_leaf_nodes=15,
        l2_regularization=1.0,
        min_samples_leaf=80,
        random_state=cfg.random_seed,
    )
    tree.fit(x_train[tree_idx], y_train[tree_idx])
    models["shallow_tree"] = tree
    return models


def predict_model(model_name: str, model: Any, x_test: np.ndarray) -> np.ndarray:
    if model_name == "ic_weighted_blend":
        return x_test @ model
    return model.predict(x_test).astype(np.float32)


def build_oos_predictions(
    x: np.ndarray,
    labels: pd.DataFrame,
    feature_valid_count: np.ndarray,
    horizons: list[str],
    label_cols: dict[str, str],
    cfg: ModelConfig,
    label_transform: str = "xs_rank",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    months = labels["timestamp"].dt.strftime("%Y-%m").to_numpy()
    time_codes = pd.factorize(labels["timestamp"], sort=False)[0]
    min_features = max(3, int(math.ceil(x.shape[1] * cfg.min_feature_fraction)))

    signal_panel = labels[["timestamp", "symbol"]].copy()
    split_rows: list[dict[str, Any]] = []
    coef_rows: list[dict[str, Any]] = []
    models = ["ic_weighted_blend", "ridge", "shallow_tree"]
    for h in horizons:
        for m in models:
            signal_panel[f"ml_{m}_{h}"] = np.nan

    for horizon in horizons:
        y_raw = labels[label_cols[horizon]].to_numpy(dtype=np.float32, copy=True)
        if label_transform == "xs_rank":
            y = xs_rank_to_unit(y_raw, time_codes)
        elif label_transform == "raw":
            y = y_raw
        else:
            raise ValueError(f"Unsupported label transform: {label_transform}")
        valid_y = np.isfinite(y)
        splits = walk_forward_months(months, cfg.min_train_months, cfg.max_walk_forward_splits)
        if not splits:
            raise ValueError("Not enough months for walk-forward validation")

        for split_no, (train_months, test_month) in enumerate(splits, start=1):
            train_mask = np.isin(months, train_months) & valid_y & (feature_valid_count >= min_features)
            test_mask = (months == test_month) & valid_y & (feature_valid_count >= min_features)
            train_idx_all = np.flatnonzero(train_mask)
            test_idx = np.flatnonzero(test_mask)
            if len(train_idx_all) == 0 or len(test_idx) == 0:
                continue
            train_idx = deterministic_take(
                train_idx_all,
                cfg.max_train_rows,
                cfg.random_seed + split_no + len(horizon),
            )
            x_train = x[train_idx]
            y_train = y[train_idx]
            x_test = x[test_idx]

            fitted = fit_models(x_train, y_train, cfg, cfg.random_seed + split_no)
            for model_name, model in fitted.items():
                pred = predict_model(model_name, model, x_test)
                col = f"ml_{model_name}_{horizon}"
                signal_panel.loc[test_idx, col] = pred
                split_rows.append({
                    "horizon": horizon,
                    "model": model_name,
                    "split_no": split_no,
                    "train_month_start": str(train_months[0]),
                    "train_month_end": str(train_months[-1]),
                    "test_month": test_month,
                    "train_rows_available": int(len(train_idx_all)),
                    "train_rows_used": int(len(train_idx)),
                    "test_rows": int(len(test_idx)),
                    "min_feature_count": int(min_features),
                })
                if model_name == "ridge":
                    for j, coef in enumerate(model.coef_):
                        coef_rows.append({
                            "horizon": horizon,
                            "split_no": split_no,
                            "feature_index": j,
                            "coef": float(coef),
                        })

    return signal_panel, pd.DataFrame(split_rows), pd.DataFrame(coef_rows)


def compute_turnover_proxy(signal_df: pd.DataFrame, signal_col: str) -> dict[str, float]:
    valid = signal_df[["timestamp", "symbol", signal_col]].dropna()
    if valid.empty:
        return {"top_quintile_turnover_proxy": np.nan, "n_transitions": 0}
    turnovers: list[float] = []
    prev: set[str] | None = None
    for _, grp in valid.groupby("timestamp", sort=True):
        n = len(grp)
        if n < 10:
            continue
        top_n = max(1, int(n * 0.20))
        current = set(grp.nlargest(top_n, signal_col)["symbol"].astype(str))
        if prev is not None and current:
            turnovers.append(1.0 - len(current & prev) / len(current))
        prev = current
    if not turnovers:
        return {"top_quintile_turnover_proxy": np.nan, "n_transitions": 0}
    return {
        "top_quintile_turnover_proxy": float(np.mean(turnovers)),
        "n_transitions": int(len(turnovers)),
    }


def evaluate_signal_panel(
    signal_panel: pd.DataFrame,
    labels: pd.DataFrame,
    horizons: list[str],
    label_cols: dict[str, str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    summary_rows: list[dict[str, Any]] = []
    monthly_rows: list[dict[str, Any]] = []
    model_names = ["ic_weighted_blend", "ridge", "shallow_tree"]

    for horizon in horizons:
        label_h = select_forward_return(labels, horizon, wide_column_map=label_cols or LABEL_COLS)
        for model_name in model_names:
            col = f"ml_{model_name}_{horizon}"
            sig = signal_panel[["timestamp", "symbol", col]].rename(columns={col: "signal_value"})
            sig = sig.dropna(subset=["signal_value"])
            if sig.empty:
                continue

            ric_ts = compute_rank_ic(sig, label_h, min_symbols=10)
            ric_s = summarize_rank_ic(ric_ts)
            spread_ts = compute_quantile_spread(sig, label_h, mode="standard", min_cross_section=10)
            spread_s = summarize_quantile_spread(spread_ts)
            turnover = compute_turnover_proxy(signal_panel, col)
            consistency = check_rankic_spread_consistency(ric_s, spread_s)

            summary_rows.append({
                "model": model_name,
                "horizon": horizon,
                "mean_rankic": ric_s["mean_rank_ic"],
                "rankic_ir": (
                    ric_s["mean_rank_ic"] / ric_s["std_rank_ic"]
                    if ric_s.get("std_rank_ic") and ric_s["std_rank_ic"] > 0 else np.nan
                ),
                "rankic_t_stat": ric_s["t_stat"],
                "rankic_positive_fraction": ric_s["positive_fraction"],
                "mean_spread": spread_s["mean_spread"],
                "median_spread": spread_s["median_spread"],
                "spread_positive_fraction": spread_s["positive_fraction"],
                "n_rankic_periods": ric_s["n_periods"],
                "n_spread_periods": spread_s["n_periods"],
                "rankic_spread_consistency": consistency,
                **turnover,
            })

            ric_ts["month"] = pd.to_datetime(ric_ts["timestamp"], utc=True).dt.strftime("%Y-%m")
            spread_ts["month"] = pd.to_datetime(spread_ts["timestamp"], utc=True).dt.strftime("%Y-%m")
            ric_m = ric_ts.groupby("month")["rank_ic"].agg(["mean", "std", "count"]).reset_index()
            sp_m = spread_ts.groupby("month")["spread"].agg(["mean", "median", "std", "count"]).reset_index()
            merged = ric_m.merge(sp_m, on="month", how="outer", suffixes=("_rankic", "_spread"))
            for _, r in merged.iterrows():
                monthly_rows.append({
                    "model": model_name,
                    "horizon": horizon,
                    "month": r["month"],
                    "mean_rankic": r.get("mean_rankic"),
                    "rankic_std": r.get("std_rankic"),
                    "rankic_periods": r.get("count_rankic"),
                    "mean_spread": r.get("mean_spread"),
                    "median_spread": r.get("median"),
                    "spread_std": r.get("std_spread"),
                    "spread_periods": r.get("count_spread"),
                })

    return pd.DataFrame(summary_rows), pd.DataFrame(monthly_rows)


def write_summary_md(
    out_dir: Path,
    feature_summary: dict[str, Any],
    model_summary: pd.DataFrame,
    manifest: dict[str, Any],
) -> None:
    lines = [
        "# Factor ML Signal Prototype",
        "",
        "Research diagnostic only. Not a live signal, not a trading strategy, and not investment advice.",
        "",
        "## Feature Selection",
        "",
        f"- Eligible factors: {feature_summary['eligible_factors']}",
        f"- Selected factors: {feature_summary['selected_factors']}",
        f"- Target range: {feature_summary['target_min']}-{feature_summary['target_max']}",
        f"- Cluster cap first pass: {feature_summary['cluster_cap']}",
        f"- Outside target range: {feature_summary['selected_count_outside_target']}",
        "",
        "## Model Comparison",
        "",
    ]
    if model_summary.empty:
        lines.append("No model summary rows were generated.")
    else:
        cols = [
            "model",
            "horizon",
            "mean_rankic",
            "rankic_ir",
            "mean_spread",
            "rankic_spread_consistency",
            "top_quintile_turnover_proxy",
        ]
        show = model_summary[cols].copy()
        lines.extend(render_markdown_table(show))
    lines.extend([
        "",
        "## Validation",
        "",
        f"- Walk-forward min train months: {manifest['model_config']['min_train_months']}",
        f"- Max walk-forward splits per horizon: {manifest['model_config']['max_walk_forward_splits']}",
        f"- Max train rows per split: {manifest['model_config']['max_train_rows']}",
        f"- Tree challenger: {manifest['tree_challenger']}",
        "",
        "## Open Risks",
        "",
        "- This is a first research prototype; it does not include live execution, order book slippage, or portfolio risk controls.",
        "- Feature signs are learned by the model; direction-ambiguous factors are not manually forced positive or negative.",
        "- Cost awareness is limited to turnover proxy diagnostics in this prototype.",
    ])
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_markdown_table(df: pd.DataFrame) -> list[str]:
    """Render a small markdown table without adding a tabulate dependency."""
    cols = list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in df.iterrows():
        vals = []
        for c in cols:
            v = row[c]
            if isinstance(v, float):
                vals.append("" if not np.isfinite(v) else f"{v:.6g}")
            else:
                vals.append(str(v))
        out.append("| " + " | ".join(vals) + " |")
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build minimal factor ML signal prototype.")
    p.add_argument("--dataset-id", default=DEFAULT_DATASET_ID)
    p.add_argument("--scorecard", default=str(DEFAULT_SCORECARD))
    p.add_argument("--output-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--horizons", nargs="+", default=HORIZONS, choices=HORIZONS)
    p.add_argument("--target-features", type=int, default=100)
    p.add_argument("--min-features", type=int, default=80)
    p.add_argument("--max-features", type=int, default=120)
    p.add_argument("--cluster-cap", type=int, default=3)
    p.add_argument("--selection-policy", choices=["default", "ls_ic_aligned", "after_funding_ls"], default="default")
    p.add_argument("--label-mode", choices=["price", "after_funding", "ls_utility_after_funding"], default="price")
    p.add_argument("--funding-aligned", default="")
    p.add_argument("--min-train-months", type=int, default=12)
    p.add_argument("--max-walk-forward-splits", type=int, default=6)
    p.add_argument("--max-train-rows", type=int, default=160_000)
    p.add_argument("--max-tree-train-rows", type=int, default=40_000)
    p.add_argument("--random-seed", type=int, default=7)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    features_dir = ROOT / "data" / "features" / args.dataset_id
    labels_path = features_dir / "labels.parquet"
    if not labels_path.exists():
        raise FileNotFoundError(labels_path)

    print("Factor ML Signal Prototype")
    print(f"  dataset: {args.dataset_id}")
    print(f"  output:  {out_dir}")
    print(f"  horizons: {args.horizons}")
    print(f"  label mode: {args.label_mode}")

    scorecard = load_scorecard(Path(args.scorecard))
    fs_cfg = FeatureSelectionConfig(
        target_features=args.target_features,
        min_features=args.min_features,
        max_features=args.max_features,
        cluster_cap=args.cluster_cap,
        selection_policy=args.selection_policy,
    )
    selected, feature_summary = select_core_features(scorecard, fs_cfg)
    selected_cols = [
        "selected_rank",
        "factor_id",
        "selection_score",
        "selection_reason",
        "ml_gate_status",
        "review_substatus",
        "final_quality_score",
        "coverage_rate",
        "rankic_mean",
        "long_short_sharpe",
        "strongest_redundancy_level",
        "redundancy_cluster_id",
        "ml_gate_risk_flags",
    ]
    selected[selected_cols].to_csv(out_dir / "selected_features.csv", index=False)
    print(f"  selected features: {len(selected)} / {feature_summary['eligible_factors']}")

    train_label_cols = label_cols_for_mode(args.label_mode)
    eval_label_cols = eval_label_cols_for_mode(args.label_mode)
    labels = pd.read_parquet(labels_path, columns=["timestamp", "symbol"] + [PRICE_LABEL_COLS[h] for h in args.horizons])
    labels["timestamp"] = pd.to_datetime(labels["timestamp"], utc=True)
    labels = labels.reset_index(drop=True)
    funding_manifest = {"status": "NOT_REQUESTED", "coverage_by_horizon": []}
    utility_manifest = {"status": "NOT_REQUESTED", "coverage_by_horizon": []}
    if args.label_mode in {"after_funding", "ls_utility_after_funding"}:
        funding_path = Path(args.funding_aligned) if args.funding_aligned else infer_funding_aligned_path(ROOT, args.dataset_id)
        labels, funding_manifest = add_funding_adjusted_returns(labels, funding_path, args.horizons)
        missing_labels = [AFTER_FUNDING_LABEL_COLS[h] for h in args.horizons if AFTER_FUNDING_LABEL_COLS[h] not in labels.columns]
        if missing_labels:
            raise ValueError(f"after-funding labels missing after adjustment: {missing_labels}")
    if args.label_mode == "ls_utility_after_funding":
        labels, utility_manifest = build_ls_utility_after_funding_targets(labels, args.horizons)

    keep_cols = ["timestamp", "symbol"]
    for col in [train_label_cols[h] for h in args.horizons] + [eval_label_cols[h] for h in args.horizons]:
        if col not in keep_cols:
            keep_cols.append(col)
    labels = labels[keep_cols].reset_index(drop=True)

    feature_ids = selected["factor_id"].astype(str).tolist()
    x, feature_valid_count, load_meta = build_feature_matrix(feature_ids, features_dir, labels)

    model_cfg = ModelConfig(
        min_train_months=args.min_train_months,
        max_walk_forward_splits=args.max_walk_forward_splits,
        max_train_rows=args.max_train_rows,
        max_tree_train_rows=args.max_tree_train_rows,
        random_seed=args.random_seed,
    )
    signal_panel, split_summary, coef_df = build_oos_predictions(
        x,
        labels,
        feature_valid_count,
        args.horizons,
        train_label_cols,
        model_cfg,
        label_transform="raw" if args.label_mode == "ls_utility_after_funding" else "xs_rank",
    )
    signal_panel_path = out_dir / "signal_panel.parquet"
    signal_panel.to_parquet(signal_panel_path, index=False)
    split_summary.to_csv(out_dir / "walk_forward_splits.csv", index=False)
    coef_df.to_csv(out_dir / "ridge_coefficients.csv", index=False)

    model_summary, monthly_metrics = evaluate_signal_panel(signal_panel, labels, args.horizons, eval_label_cols)
    model_summary.to_csv(out_dir / "model_comparison.csv", index=False)
    monthly_metrics.to_csv(out_dir / "monthly_metrics.csv", index=False)
    direction_conflicts = int((model_summary["rankic_spread_consistency"] == "DIRECTION_CONFLICT").sum())

    checks = [
        {
            "check": "ml_hold_excluded",
            "status": "PASS" if not (selected["ml_gate_status"] == "ML_HOLD").any() else "FAIL",
            "detail": f"{int((selected['ml_gate_status'] == 'ML_HOLD').sum())} ML_HOLD selected",
        },
        {
            "check": "selected_count_target",
            "status": "PASS" if args.min_features <= len(selected) <= args.max_features else "WARN",
            "detail": f"selected={len(selected)}, target={args.min_features}-{args.max_features}",
        },
        {
            "check": "selection_policy_pool",
            "status": "PASS"
            if args.selection_policy == "default" or feature_summary["selected_strict_ls_ic_aligned"] > 0
            else "WARN",
            "detail": (
                f"policy={args.selection_policy}; pool={feature_summary['policy_pool_factors']}; "
                f"strict_selected={feature_summary['selected_strict_ls_ic_aligned']}; "
                f"fallback_selected={feature_summary['selected_fallback_ls_ic_aligned']}"
            ),
        },
        {
            "check": "label_mode",
            "status": "PASS"
            if args.label_mode == "price" or funding_manifest.get("status") == "FUNDING_ADJUSTED_LABELS_COMPUTED"
            else "FAIL",
            "detail": (
                f"label_mode={args.label_mode}; funding_status={funding_manifest.get('status')}; "
                f"utility_status={utility_manifest.get('status')}"
            ),
        },
        {
            "check": "no_label_columns_in_signal_panel",
            "status": "PASS" if not any("ret_fwd" in c or "forward" in c.lower() for c in signal_panel.columns) else "FAIL",
            "detail": ",".join(signal_panel.columns),
        },
        {
            "check": "walk_forward_no_lookahead",
            "status": "PASS"
            if (split_summary["train_month_end"] < split_summary["test_month"]).all()
            else "FAIL",
            "detail": f"{len(split_summary)} model split rows",
        },
        {
            "check": "all_three_model_families",
            "status": "PASS"
            if set(model_summary["model"].unique()) == {"ic_weighted_blend", "ridge", "shallow_tree"}
            else "FAIL",
            "detail": ",".join(sorted(model_summary["model"].unique())),
        },
        {
            "check": "rankic_spread_direction_conflicts",
            "status": "PASS" if direction_conflicts == 0 else "WARN",
            "detail": f"{direction_conflicts} of {len(model_summary)} model-horizon rows have RankIC/spread direction conflict",
        },
    ]
    pd.DataFrame(checks).to_csv(out_dir / "quality_checks.csv", index=False)

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset_id": args.dataset_id,
        "scorecard": str(Path(args.scorecard)),
        "labels": str(labels_path),
        "label_mode": args.label_mode,
        "train_label_columns": train_label_cols,
        "eval_label_columns": eval_label_cols,
        "funding_manifest": funding_manifest,
        "utility_manifest": utility_manifest,
        "horizons": args.horizons,
        "feature_summary": feature_summary,
        "model_config": model_cfg.__dict__,
        "duplicate_factor_value_policy": "prefer aligned last block; otherwise groupby(timestamp,symbol).last",
        "models": ["ic_weighted_blend", "ridge", "shallow_tree"],
        "tree_challenger": "sklearn HistGradientBoostingRegressor shallow configuration",
        "disclaimer": "Research prototype only. Not a trading signal or production execution path.",
        "outputs": {
            "selected_features": str(out_dir / "selected_features.csv"),
            "signal_panel": str(signal_panel_path),
            "model_comparison": str(out_dir / "model_comparison.csv"),
            "monthly_metrics": str(out_dir / "monthly_metrics.csv"),
            "walk_forward_splits": str(out_dir / "walk_forward_splits.csv"),
            "ridge_coefficients": str(out_dir / "ridge_coefficients.csv"),
            "quality_checks": str(out_dir / "quality_checks.csv"),
            "summary": str(out_dir / "summary.md"),
        },
        "factor_load_metadata": load_meta,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")
    write_summary_md(out_dir, feature_summary, model_summary, manifest)

    print("\nModel comparison:")
    if model_summary.empty:
        print("  no model rows")
    else:
        print(model_summary[["model", "horizon", "mean_rankic", "mean_spread", "top_quintile_turnover_proxy"]].to_string(index=False))
    print(f"\nArtifacts written to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
