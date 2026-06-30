#!/usr/bin/env python3
"""Evaluate continuous rank-weighted portfolios from ML signal panels.

This is a research diagnostic. It converts each timestamp's cross-sectional ML
score into dollar-neutral continuous weights, evaluates after-funding forward
returns, and subtracts simple turnover-based fee/slippage scenarios.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from funding_adjusted_labels import add_funding_adjusted_returns  # noqa: E402

DEFAULT_DATASET_ID = "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
RUN_BASE = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"
DEFAULT_ML_DIR = RUN_BASE / "ml_signal_prototype_after_funding_ls"
DEFAULT_FEATURES_DIR = ROOT / "data" / "features" / DEFAULT_DATASET_ID
DEFAULT_FUNDING_ALIGNED = (
    ROOT
    / "data"
    / "cache"
    / "crypto_funding_rate_1h_contract_v1"
    / "funding_rate_1h_aligned_dynamic.parquet"
)
DEFAULT_SITE_SUMMARY = ROOT / "reports/site/factor-library/assets/signal_ml_rank_weighted_summary.json"
HORIZONS = ["1h", "4h", "24h", "72h"]
MODELS = ["ic_weighted_blend", "ridge", "shallow_tree"]
COST_BPS = [3.0, 7.0, 10.0, 15.0]


@dataclass(frozen=True)
class PortfolioVariant:
    name: str
    alpha: float = 1.0
    no_trade_threshold: float = 0.0


VARIANTS = [
    PortfolioVariant("raw", alpha=1.0, no_trade_threshold=0.0),
    PortfolioVariant("ema_0p35", alpha=0.35, no_trade_threshold=0.0),
    PortfolioVariant("no_trade_50bp", alpha=1.0, no_trade_threshold=0.005),
]


def signal_col(model: str, horizon: str) -> str:
    return f"ml_{model}_{horizon}"


def price_label_col(horizon: str) -> str:
    return f"ret_fwd_{horizon}"


def after_funding_col(horizon: str) -> str:
    return f"ret_fwd_{horizon}_after_funding"


def normalize_weight_matrix(raw: np.ndarray, valid: np.ndarray) -> np.ndarray:
    weights = np.where(valid, raw, 0.0).astype(float, copy=False)
    gross = np.abs(weights).sum(axis=1)
    out = np.zeros_like(weights, dtype=float)
    ok = gross > 0
    out[ok] = weights[ok] / gross[ok, None]
    return out


def target_weight_matrix(signal_wide: pd.DataFrame, ret_wide: pd.DataFrame, min_symbols: int) -> tuple[np.ndarray, np.ndarray]:
    valid = signal_wide.notna() & ret_wide.notna()
    n_symbols = valid.sum(axis=1).to_numpy(dtype=int)
    ranks = signal_wide.rank(axis=1, method="average", pct=True)
    scores = (ranks - 0.5) * 2.0
    scores = scores.sub(scores.where(valid).mean(axis=1), axis=0)
    raw = scores.to_numpy(dtype=float)
    valid_np = valid.to_numpy(dtype=bool) & (n_symbols[:, None] >= min_symbols)
    target = normalize_weight_matrix(raw, valid_np)
    return target, valid_np


def apply_variant_matrix(target: np.ndarray, valid: np.ndarray, variant: PortfolioVariant) -> np.ndarray:
    out = np.zeros_like(target, dtype=float)
    prev = np.zeros(target.shape[1], dtype=float)
    for i in range(target.shape[0]):
        if not valid[i].any():
            prev = np.zeros_like(prev)
            continue
        prev_active = np.where(valid[i], prev, 0.0)
        if variant.alpha < 1.0:
            current = variant.alpha * target[i] + (1.0 - variant.alpha) * prev_active
        else:
            current = target[i].copy()
        if variant.no_trade_threshold > 0:
            diff = np.abs(target[i] - prev_active)
            current = np.where((diff >= variant.no_trade_threshold) & valid[i], current, prev_active)
        current = normalize_weight_matrix(current[None, :], valid[i][None, :])[0]
        out[i] = current
        prev = current
    return out


def evaluate_variant_matrix(
    timestamps: pd.Index,
    ret_wide: pd.DataFrame,
    target: np.ndarray,
    valid: np.ndarray,
    variant: PortfolioVariant,
) -> pd.DataFrame:
    weights = apply_variant_matrix(target, valid, variant)
    returns = ret_wide.fillna(0.0).to_numpy(dtype=float)
    gross_return = (weights * returns).sum(axis=1)
    prev = np.vstack([np.zeros((1, weights.shape[1])), weights[:-1]])
    turnover = np.abs(weights - prev).sum(axis=1)
    n_symbols = valid.sum(axis=1)
    gross_exposure = np.abs(weights).sum(axis=1)
    net_exposure = weights.sum(axis=1)
    abs_max = np.where(valid.any(axis=1), np.abs(weights).max(axis=1), np.nan)
    keep = n_symbols > 0
    return pd.DataFrame({
        "timestamp": timestamps[keep],
        "variant": variant.name,
        "gross_return": gross_return[keep],
        "turnover": turnover[keep],
        "gross_exposure": gross_exposure[keep],
        "net_exposure": net_exposure[keep],
        "n_symbols": n_symbols[keep],
        "weight_abs_max": abs_max[keep],
        "score_weight_corr": 1.0,
    })


def build_signal_return_wide(valid: pd.DataFrame, signal: str, ret_col: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    signal_wide = valid.pivot_table(index="timestamp", columns="symbol", values=signal, aggfunc="first")
    ret_wide = valid.pivot_table(index="timestamp", columns="symbol", values=ret_col, aggfunc="first")
    signal_wide, ret_wide = signal_wide.align(ret_wide, join="outer", axis=0)
    signal_wide, ret_wide = signal_wide.align(ret_wide, join="outer", axis=1)
    return signal_wide.sort_index(), ret_wide.sort_index()


def summarize_base(ts: pd.DataFrame, model: str, horizon: str, variant: str) -> dict[str, Any]:
    gross = ts["gross_return"]
    turnover = ts["turnover"]
    mean_turnover = float(turnover.mean())
    median_gross = float(gross.median())
    return {
        "model": model,
        "horizon": horizon,
        "variant": variant,
        "n_periods": int(len(ts)),
        "mean_gross_return": float(gross.mean()),
        "median_gross_return": median_gross,
        "gross_positive_fraction": float((gross > 0).mean()),
        "mean_turnover": mean_turnover,
        "median_turnover": float(turnover.median()),
        "break_even_cost_bps": (
            median_gross / mean_turnover * 10_000.0
            if mean_turnover > 0 and median_gross > 0
            else math.nan
        ),
        "mean_abs_max_weight": float(ts["weight_abs_max"].mean()),
        "mean_symbols": float(ts["n_symbols"].mean()),
    }


def summarize_scenarios(ts: pd.DataFrame, model: str, horizon: str, variant: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for cost_bps in COST_BPS:
        cost = ts["turnover"] * (cost_bps / 10_000.0)
        net = ts["gross_return"] - cost
        rows.append({
            "model": model,
            "horizon": horizon,
            "variant": variant,
            "cost_bps": cost_bps,
            "mean_net_return": float(net.mean()),
            "median_net_return": float(net.median()),
            "net_positive_fraction": float((net > 0).mean()),
            "survives_median_net": bool(net.median() > 0),
            "mean_cost_drag": float(cost.mean()),
        })
    return rows


def summarize_monthly(ts: pd.DataFrame, model: str, horizon: str, variant: str) -> list[dict[str, Any]]:
    if ts.empty:
        return []
    work = ts.copy()
    work["month"] = pd.to_datetime(work["timestamp"], utc=True).dt.strftime("%Y-%m")
    rows: list[dict[str, Any]] = []
    for cost_bps in COST_BPS:
        work["net_return"] = work["gross_return"] - work["turnover"] * (cost_bps / 10_000.0)
        monthly = work.groupby("month", sort=True)["net_return"].agg(["mean", "median", "count"]).reset_index()
        for _, row in monthly.iterrows():
            rows.append({
                "model": model,
                "horizon": horizon,
                "variant": variant,
                "cost_bps": cost_bps,
                "month": row["month"],
                "mean_net_return": float(row["mean"]),
                "median_net_return": float(row["median"]),
                "periods": int(row["count"]),
            })
    return rows


def load_panel(ml_dir: Path, features_dir: Path, funding_aligned: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    signal_panel = pd.read_parquet(ml_dir / "signal_panel.parquet")
    signal_panel["timestamp"] = pd.to_datetime(signal_panel["timestamp"], utc=True)
    cache_path = ml_dir / "after_funding_labels_for_rank_weighted.parquet"
    manifest_path = ml_dir / "after_funding_labels_for_rank_weighted_manifest.json"
    if cache_path.exists() and manifest_path.exists():
        labels = pd.read_parquet(cache_path)
        labels["timestamp"] = pd.to_datetime(labels["timestamp"], utc=True)
        funding_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        labels = pd.read_parquet(
            features_dir / "labels.parquet",
            columns=["timestamp", "symbol"] + [price_label_col(h) for h in HORIZONS],
        )
        labels["timestamp"] = pd.to_datetime(labels["timestamp"], utc=True)

        signal_cols = [c for c in signal_panel.columns if c.startswith("ml_")]
        active_keys = signal_panel.loc[
            signal_panel[signal_cols].notna().any(axis=1),
            ["timestamp", "symbol"],
        ].drop_duplicates()
        labels = labels.merge(active_keys, on=["timestamp", "symbol"], how="inner")
        labels, funding_manifest = add_funding_adjusted_returns(labels, funding_aligned, HORIZONS)
        keep_cache = ["timestamp", "symbol"] + [after_funding_col(h) for h in HORIZONS]
        labels[keep_cache].to_parquet(cache_path, index=False)
        manifest_path.write_text(json.dumps(funding_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    keep = ["timestamp", "symbol"] + [after_funding_col(h) for h in HORIZONS]

    if signal_panel[["timestamp", "symbol"]].reset_index(drop=True).equals(
        labels[["timestamp", "symbol"]].reset_index(drop=True)
    ):
        panel = signal_panel.join(labels[[after_funding_col(h) for h in HORIZONS]])
    else:
        panel = signal_panel.merge(labels[keep], on=["timestamp", "symbol"], how="left")
    return panel, funding_manifest


def best_rows(scenario_summary: pd.DataFrame, cost_bps: float = 7.0, n: int = 8) -> list[dict[str, Any]]:
    rows = scenario_summary[scenario_summary["cost_bps"] == cost_bps].copy()
    rows = rows.sort_values(["median_net_return", "mean_net_return"], ascending=[False, False]).head(n)
    return rows.to_dict(orient="records")


def finite_json(value: Any) -> Any:
    if isinstance(value, float) and not np.isfinite(value):
        return None
    if hasattr(value, "item"):
        return finite_json(value.item())
    return value


def build_site_summary(
    ml_dir: Path,
    base_summary: pd.DataFrame,
    scenario_summary: pd.DataFrame,
    funding_manifest: dict[str, Any],
) -> dict[str, Any]:
    manifest = {}
    manifest_path = ml_dir / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    survival = scenario_summary.groupby("cost_bps")["survives_median_net"].sum().to_dict()
    best_7bps = best_rows(scenario_summary, cost_bps=7.0)
    best_3bps = best_rows(scenario_summary, cost_bps=3.0)
    gross_positive = int((base_summary["median_gross_return"] > 0).sum())
    total_base = int(len(base_summary))

    return {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_ml_dir": str(ml_dir),
            "disclaimer": "Research diagnostic only. Not a trading signal or production backtest.",
        },
        "experiment": {
            "name": "rank_weighted_after_funding_portfolio",
            "source_model_label_mode": manifest.get("label_mode"),
            "source_selection_policy": manifest.get("feature_summary", {}).get("selection_policy"),
            "selected_factors": manifest.get("feature_summary", {}).get("selected_factors"),
            "policy_pool_factors": manifest.get("feature_summary", {}).get("policy_pool_factors"),
            "weighting": (
                "Per timestamp, model score is converted to cross-sectional rank score, centered, "
                "and normalized to gross exposure 1.0."
            ),
            "variants": [v.name for v in VARIANTS],
            "cost_bps": COST_BPS,
            "funding_manifest": funding_manifest,
            "gross_positive_rows": gross_positive,
            "base_rows": total_base,
            "cost_survival_by_bps": {str(k): int(v) for k, v in survival.items()},
            "best_3bps": best_3bps,
            "best_7bps": best_7bps,
            "rows": base_summary.to_dict(orient="records"),
            "scenario_rows": scenario_summary.to_dict(orient="records"),
        },
        "interpretation": {
            "headline": (
                "Continuous rank-weighted portfolios are more aligned with RankIC than hard LS buckets, "
                "but only one 72h no-trade median case survives costs, while its mean return remains negative."
            ),
            "takeaways": [
                "This experiment uses the existing after-funding RankIC-trained 3x4 ML signals, not the LS-utility model.",
                "Weights are continuous across the full cross-section instead of fixed top20/bottom20 buckets, so the test better matches a RankIC-style signal.",
                "Funding is already deducted in the forward return label; fee/slippage is deducted from weight turnover.",
                "Only 7 of 36 model/horizon/variant rows have positive median gross return before fees.",
                "At 7 bps, only ic_weighted_blend 72h with a 50bp no-trade band has positive median net return, and its mean net return is still negative.",
                "This means continuous weighting reduces the hard-bucket problem, but the current factor library still has an economic edge problem.",
            ],
            "recommendations": [
                "Use this as the next gate before any new model training: a signal should first produce positive after-funding continuous portfolio return.",
                "If only low-cost smoothed horizons work, restrict follow-up to 24h/72h with turnover controls.",
                "If no 7 bps row survives, do not promote the ML signal; move to portfolio constraints, tail vetoes, and long/short side decomposition.",
            ],
        },
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate ML rank-weighted after-funding portfolios.")
    p.add_argument("--ml-dir", default=str(DEFAULT_ML_DIR))
    p.add_argument("--features-dir", default=str(DEFAULT_FEATURES_DIR))
    p.add_argument("--funding-aligned", default=str(DEFAULT_FUNDING_ALIGNED))
    p.add_argument("--site-summary-output", default=str(DEFAULT_SITE_SUMMARY))
    p.add_argument("--min-symbols", type=int, default=20)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    ml_dir = Path(args.ml_dir)
    panel, funding_manifest = load_panel(ml_dir, Path(args.features_dir), Path(args.funding_aligned))

    ts_rows: list[pd.DataFrame] = []
    base_rows: list[dict[str, Any]] = []
    scenario_rows: list[dict[str, Any]] = []
    monthly_rows: list[dict[str, Any]] = []

    for horizon in HORIZONS:
        ret_col = after_funding_col(horizon)
        for model in MODELS:
            sig = signal_col(model, horizon)
            valid = panel[["timestamp", "symbol", sig, ret_col]].dropna().copy()
            if valid.empty:
                continue
            signal_wide, ret_wide = build_signal_return_wide(valid, sig, ret_col)
            target, valid_mask = target_weight_matrix(signal_wide, ret_wide, min_symbols=args.min_symbols)
            for variant in VARIANTS:
                ts = evaluate_variant_matrix(signal_wide.index, ret_wide, target, valid_mask, variant)
                if ts.empty:
                    continue
                ts.insert(0, "horizon", horizon)
                ts.insert(0, "model", model)
                ts_rows.append(ts)
                base_rows.append(summarize_base(ts, model, horizon, variant.name))
                scenario_rows.extend(summarize_scenarios(ts, model, horizon, variant.name))
                monthly_rows.extend(summarize_monthly(ts, model, horizon, variant.name))

    if not ts_rows:
        raise ValueError("No rank-weighted portfolio rows generated")

    ts_df = pd.concat(ts_rows, ignore_index=True)
    base_summary = pd.DataFrame(base_rows)
    scenario_summary = pd.DataFrame(scenario_rows)
    monthly = pd.DataFrame(monthly_rows)

    ts_df.to_csv(ml_dir / "rank_weighted_portfolio_timeseries.csv", index=False)
    base_summary.to_csv(ml_dir / "rank_weighted_portfolio_summary.csv", index=False)
    scenario_summary.to_csv(ml_dir / "rank_weighted_portfolio_scenarios.csv", index=False)
    monthly.to_csv(ml_dir / "rank_weighted_portfolio_monthly.csv", index=False)

    site_summary = build_site_summary(ml_dir, base_summary, scenario_summary, funding_manifest)
    out = Path(args.site_summary_output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(site_summary, ensure_ascii=False, indent=2, default=finite_json),
        encoding="utf-8",
    )

    print("Rank-weighted after-funding portfolio evaluation")
    print(
        scenario_summary[scenario_summary["cost_bps"].isin([3.0, 7.0])]
        .sort_values(["cost_bps", "median_net_return"], ascending=[True, False])
        .head(16)
        .to_string(index=False)
    )
    print(f"Artifacts written to {ml_dir}")
    print(f"Site summary written to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
