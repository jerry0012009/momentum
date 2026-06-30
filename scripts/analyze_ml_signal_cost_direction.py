#!/usr/bin/env python3
"""Analyze ML signal costs, direction conflicts, and funding coverage.

This is a research diagnostic. It does not model fills, live execution, or
portfolio accounting. The goal is to make the current ML prototype's economic
limits explicit before any composite signal work.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from funding_adjusted_labels import add_funding_adjusted_returns  # noqa: E402

DEFAULT_DATASET_ID = "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
RUN_BASE = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"
DEFAULT_ML_DIR = RUN_BASE / "ml_signal_prototype"
DEFAULT_FEATURES_DIR = ROOT / "data" / "features" / DEFAULT_DATASET_ID
DEFAULT_FUNDING_DIR = ROOT / "data" / "binance_funding_rate"
DEFAULT_FUNDING_ALIGNED = ROOT / "data" / "cache" / "crypto_funding_rate_1h_contract_v1" / "funding_rate_1h_aligned_dynamic.parquet"
HORIZONS = ["1h", "4h", "24h", "72h"]
MODELS = ["ic_weighted_blend", "ridge", "shallow_tree"]
TAIL_TOP_N = 50
SCENARIOS = [
    {"scenario": "best_case", "fee_bps": 2.0, "slippage_bps": 1.0},
    {"scenario": "low_cost", "fee_bps": 2.0, "slippage_bps": 5.0},
    {"scenario": "moderate", "fee_bps": 5.0, "slippage_bps": 5.0},
    {"scenario": "conservative", "fee_bps": 5.0, "slippage_bps": 10.0},
]


@dataclass(frozen=True)
class SignalStats:
    mean_spread: float
    median_spread: float
    positive_spread_fraction: float
    top_turnover_mean: float
    bottom_turnover_mean: float
    avg_side_turnover_mean: float
    long_short_turnover_mean: float
    break_even_cost_bps_avg_side: float
    break_even_cost_bps_full_ls: float
    n_timestamps: int


def signal_col(model: str, horizon: str) -> str:
    return f"ml_{model}_{horizon}"


def label_col(horizon: str) -> str:
    return f"ret_fwd_{horizon}"


def after_funding_col(horizon: str) -> str:
    return f"ret_fwd_{horizon}_after_funding"


def eval_label_col(horizon: str, return_mode: str) -> str:
    if return_mode == "price":
        return label_col(horizon)
    if return_mode == "after_funding":
        return after_funding_col(horizon)
    raise ValueError(f"Unsupported return mode: {return_mode}")


def assign_quintiles(df: pd.DataFrame, signal: str) -> pd.Series:
    ranks = df.groupby("timestamp", sort=False)[signal].rank(method="first", pct=True)
    buckets = np.ceil(ranks.to_numpy() * 5.0).astype(np.int8)
    return pd.Series(np.clip(buckets, 1, 5), index=df.index)


def turnover_for_side(side: pd.Series) -> float:
    prev: set[str] | None = None
    vals: list[float] = []
    for _, symbols in side.groupby(level=0, sort=True):
        current = set(symbols.astype(str))
        if prev is not None and current:
            vals.append(1.0 - len(current & prev) / len(current))
        prev = current
    return float(np.mean(vals)) if vals else math.nan


def evaluate_signal(df: pd.DataFrame, signal: str, ret: str) -> tuple[SignalStats, pd.DataFrame]:
    return summarize_bucketed_signal(bucketed_signal_frame(df, signal, ret), signal, ret)


def summarize_bucketed_signal(valid: pd.DataFrame, signal: str, ret: str) -> tuple[SignalStats, pd.DataFrame]:
    _ = signal

    bucket_returns = (
        valid.groupby(["bucket"], sort=True)[ret]
        .agg(["mean", "median", "count"])
        .reset_index()
        .rename(columns={"mean": "return_mean", "median": "return_median", "count": "rows"})
    )

    per_ts = valid.groupby(["timestamp", "bucket"], sort=True)[ret].mean().unstack()
    spread_ts = per_ts[5] - per_ts[1]
    top_symbols = valid.loc[valid["bucket"] == 5].set_index("timestamp")["symbol"]
    bottom_symbols = valid.loc[valid["bucket"] == 1].set_index("timestamp")["symbol"]
    top_turnover = turnover_for_side(top_symbols)
    bottom_turnover = turnover_for_side(bottom_symbols)
    avg_side_turnover = float(np.nanmean([top_turnover, bottom_turnover]))
    long_short_turnover = float(np.nansum([top_turnover, bottom_turnover]))
    median_spread = float(spread_ts.median())

    def break_even(turnover: float) -> float:
        if not np.isfinite(turnover) or turnover <= 0 or median_spread <= 0:
            return math.nan
        return median_spread / turnover * 10_000.0

    stats = SignalStats(
        mean_spread=float(spread_ts.mean()),
        median_spread=median_spread,
        positive_spread_fraction=float((spread_ts > 0).mean()),
        top_turnover_mean=float(top_turnover),
        bottom_turnover_mean=float(bottom_turnover),
        avg_side_turnover_mean=avg_side_turnover,
        long_short_turnover_mean=long_short_turnover,
        break_even_cost_bps_avg_side=break_even(avg_side_turnover),
        break_even_cost_bps_full_ls=break_even(long_short_turnover),
        n_timestamps=int(spread_ts.notna().sum()),
    )
    return stats, bucket_returns


def bucketed_signal_frame(df: pd.DataFrame, signal: str, ret: str) -> pd.DataFrame:
    cols = ["timestamp", "symbol", signal, ret]
    if "_month" in df.columns:
        cols.append("_month")
    valid = df[cols].dropna().copy()
    valid["bucket"] = assign_quintiles(valid, signal)
    return valid


def monthly_bucket_rows(valid: pd.DataFrame, model: str, horizon: str, ret: str) -> list[dict[str, Any]]:
    month_col = "_month" if "_month" in valid.columns else "month"
    if month_col not in valid.columns:
        valid = valid.copy()
        valid[month_col] = valid["timestamp"].dt.strftime("%Y-%m")
    grouped = (
        valid.groupby([month_col, "bucket"], sort=True)[ret]
        .agg(["mean", "median", "count"])
        .reset_index()
        .rename(columns={month_col: "month", "mean": "return_mean", "median": "return_median", "count": "rows"})
    )
    grouped.insert(0, "horizon", horizon)
    grouped.insert(0, "model", model)
    return grouped.to_dict(orient="records")


def tail_contributor_rows(
    valid: pd.DataFrame,
    model: str,
    horizon: str,
    signal: str,
    ret: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    working = valid.copy()
    working["abs_return"] = working[ret].abs()
    for bucket, side in [(1, "bottom_bucket"), (5, "top_bucket")]:
        bucket_df = working[working["bucket"] == bucket]
        tail = bucket_df.nlargest(TAIL_TOP_N, "abs_return")
        total_abs = float(bucket_df["abs_return"].sum())
        for rank, (_, row) in enumerate(tail.iterrows(), start=1):
            rows.append({
                "model": model,
                "horizon": horizon,
                "side": side,
                "rank": rank,
                "timestamp": row["timestamp"],
                "symbol": row["symbol"],
                "signal_value": row[signal],
                "forward_return": row[ret],
                "abs_return": row["abs_return"],
                "contribution_share": row["abs_return"] / total_abs if total_abs > 0 else math.nan,
            })
    return rows


def robust_tail_row(valid: pd.DataFrame, model: str, horizon: str, ret: str) -> dict[str, Any]:
    per_ts = valid.groupby(["timestamp", "bucket"], sort=True)[ret].mean().unstack()
    mean_spread = float((per_ts[5] - per_ts[1]).mean())
    median_spread = float((per_ts[5] - per_ts[1]).median())

    top = valid[valid["bucket"] == 5][ret]
    bottom = valid[valid["bucket"] == 1][ret]
    top_abs = top.abs().sort_values(ascending=False)
    bottom_abs = bottom.abs().sort_values(ascending=False)
    top_total = float(top_abs.sum())
    bottom_total = float(bottom_abs.sum())
    top_1pct_share = float(top_abs.iloc[:max(1, len(top_abs) // 100)].sum() / top_total) if top_total > 0 else math.nan
    bottom_1pct_share = float(bottom_abs.iloc[:max(1, len(bottom_abs) // 100)].sum() / bottom_total) if bottom_total > 0 else math.nan

    def winsorized_bucket_spread(lo: float, hi: float) -> float:
        top_lo, top_hi = top.quantile([lo, hi])
        bot_lo, bot_hi = bottom.quantile([lo, hi])
        return float(top.clip(top_lo, top_hi).mean() - bottom.clip(bot_lo, bot_hi).mean())

    if mean_spread < 0 < median_spread:
        diagnosis = "MEAN_SPREAD_OUTLIER_DOMINATED"
    elif mean_spread < 0 and (top_1pct_share > 0.10 or bottom_1pct_share > 0.10):
        diagnosis = "TAIL_CONCENTRATED_NEGATIVE_MEAN"
    elif mean_spread > 0 and median_spread > 0:
        diagnosis = "DIRECTIONALLY_CLEAN_THIN_EDGE"
    elif mean_spread < 0 and median_spread < 0:
        diagnosis = "ROBUST_SPREAD_NEGATIVE"
    else:
        diagnosis = "MIXED_BUCKET_SHAPE"

    return {
        "model": model,
        "horizon": horizon,
        "mean_spread": mean_spread,
        "median_spread": median_spread,
        "winsorized_1_99_spread": winsorized_bucket_spread(0.01, 0.99),
        "winsorized_5_95_spread": winsorized_bucket_spread(0.05, 0.95),
        "top_bucket_mean": float(top.mean()),
        "top_bucket_median": float(top.median()),
        "bottom_bucket_mean": float(bottom.mean()),
        "bottom_bucket_median": float(bottom.median()),
        "top_bucket_top1pct_abs_share": top_1pct_share,
        "bottom_bucket_top1pct_abs_share": bottom_1pct_share,
        "diagnosis": diagnosis,
    }


def build_cost_rows(model_summary: pd.DataFrame, signal_stats: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    merged = model_summary.merge(
        signal_stats,
        on=["model", "horizon"],
        how="left",
        suffixes=("_model_summary", "_bucket"),
    )
    for _, row in merged.iterrows():
        for scenario in SCENARIOS:
            cost_bps = float(scenario["fee_bps"] + scenario["slippage_bps"])
            unit_cost = cost_bps / 10_000.0
            avg_side_drag = unit_cost * float(row["avg_side_turnover_mean"])
            full_ls_drag = unit_cost * float(row["long_short_turnover_mean"])
            rows.append({
                "model": row["model"],
                "horizon": row["horizon"],
                "scenario": scenario["scenario"],
                "fee_bps": scenario["fee_bps"],
                "slippage_bps": scenario["slippage_bps"],
                "total_cost_bps": cost_bps,
                "gross_median_spread": row["median_spread_bucket"],
                "gross_mean_spread": row["mean_spread_bucket"],
                "avg_side_turnover_mean": row["avg_side_turnover_mean"],
                "long_short_turnover_mean": row["long_short_turnover_mean"],
                "net_median_spread_avg_side_cost": row["median_spread_bucket"] - avg_side_drag,
                "net_median_spread_full_ls_cost": row["median_spread_bucket"] - full_ls_drag,
                "survives_avg_side_cost": bool(row["median_spread_bucket"] - avg_side_drag > 0),
                "survives_full_ls_cost": bool(row["median_spread_bucket"] - full_ls_drag > 0),
            })
    return pd.DataFrame(rows)


def funding_coverage(signal_panel: pd.DataFrame, funding_dir: Path) -> dict[str, Any]:
    funding_symbols = {p.name for p in funding_dir.iterdir() if p.is_dir()} if funding_dir.exists() else set()
    active = signal_panel.dropna(subset=[signal_col("ridge", "1h")])["symbol"].astype(str)
    active_symbols = set(active.unique())
    covered_symbols = active_symbols & funding_symbols
    covered_rows = int(active.isin(covered_symbols).sum())
    total_rows = int(len(active))
    return {
        "funding_dir": str(funding_dir),
        "active_signal_symbols": len(active_symbols),
        "symbols_with_funding_dir_match": len(covered_symbols),
        "symbol_coverage_rate": len(covered_symbols) / len(active_symbols) if active_symbols else math.nan,
        "active_rows": total_rows,
        "rows_with_funding_dir_match": covered_rows,
        "row_coverage_rate": covered_rows / total_rows if total_rows else math.nan,
        "missing_symbol_sample": sorted(active_symbols - funding_symbols)[:40],
        "covered_symbol_sample": sorted(covered_symbols)[:40],
        "status": "PARTIAL_COVERAGE_NOT_DEDUCTED_FROM_LABELS",
        "note": (
            "The canonical labels are pure forward close-to-close returns. "
            "Funding data exists separately and is not yet aligned into future net-return labels."
        ),
    }


def add_after_funding_returns(panel: pd.DataFrame, funding_path: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    labels = panel[["timestamp", "symbol"] + [label_col(h) for h in HORIZONS]].copy()
    adjusted_labels, manifest = add_funding_adjusted_returns(labels, funding_path, HORIZONS)
    keep = ["timestamp", "symbol"] + [after_funding_col(h) for h in HORIZONS if after_funding_col(h) in adjusted_labels.columns]
    adjusted = panel.merge(adjusted_labels[keep], on=["timestamp", "symbol"], how="left")
    manifest = dict(manifest)
    manifest["note"] = (
        "Funding-adjusted diagnostics use scripts/funding_adjusted_labels.py, the same helper used by "
        "after-funding ML training. Funding cost is aligned on hourly windows before merging back to the signal panel."
    )
    return adjusted, manifest


def funding_adjusted_diagnostics(panel: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for horizon in HORIZONS:
        before = label_col(horizon)
        after = after_funding_col(horizon)
        if after not in panel.columns:
            continue
        for model in MODELS:
            col = signal_col(model, horizon)
            before_valid = bucketed_signal_frame(panel, col, before)
            after_valid = bucketed_signal_frame(panel, col, after)
            before_stats, _ = summarize_bucketed_signal(before_valid, col, before)
            after_stats, _ = summarize_bucketed_signal(after_valid, col, after)
            rows.append({
                "model": model,
                "horizon": horizon,
                "before_rows": int(len(before_valid)),
                "after_funding_rows": int(len(after_valid)),
                "after_funding_row_fraction": len(after_valid) / len(before_valid) if len(before_valid) else math.nan,
                "before_mean_spread": before_stats.mean_spread,
                "after_funding_mean_spread": after_stats.mean_spread,
                "before_median_spread": before_stats.median_spread,
                "after_funding_median_spread": after_stats.median_spread,
                "before_positive_spread_fraction": before_stats.positive_spread_fraction,
                "after_funding_positive_spread_fraction": after_stats.positive_spread_fraction,
            })
    return pd.DataFrame(rows)


def conflict_summary(model_summary: pd.DataFrame, monthly: pd.DataFrame) -> dict[str, Any]:
    conflicts = model_summary[model_summary["rankic_spread_consistency"] == "DIRECTION_CONFLICT"]
    monthly = monthly.copy()
    monthly["direction_conflict"] = monthly["mean_rankic"] * monthly["mean_spread"] < 0
    by_horizon = (
        monthly.groupby("horizon")["direction_conflict"]
        .agg(["sum", "count", "mean"])
        .reset_index()
        .rename(columns={"sum": "conflict_model_month_rows", "count": "model_month_rows", "mean": "conflict_fraction"})
    )
    return {
        "model_horizon_conflicts": int(len(conflicts)),
        "model_horizon_rows": int(len(model_summary)),
        "monthly_conflict_by_horizon": by_horizon.to_dict(orient="records"),
        "interpretation": (
            "The conflict is not only a display issue: it appears in model-level and monthly diagnostics. "
            "The most likely causes are bucket-tail behavior, top-minus-bottom spread convention, and "
            "crypto cross-sectional tails where a positive rank relationship can coexist with weak or adverse extremes."
        ),
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze ML signal cost and direction diagnostics.")
    p.add_argument("--ml-dir", default=str(DEFAULT_ML_DIR))
    p.add_argument("--features-dir", default=str(DEFAULT_FEATURES_DIR))
    p.add_argument("--funding-dir", default=str(DEFAULT_FUNDING_DIR))
    p.add_argument("--funding-aligned", default=str(DEFAULT_FUNDING_ALIGNED))
    p.add_argument("--return-mode", choices=["price", "after_funding"], default="price")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    ml_dir = Path(args.ml_dir)
    labels_path = Path(args.features_dir) / "labels.parquet"
    signal_panel_path = ml_dir / "signal_panel.parquet"

    signal_panel = pd.read_parquet(signal_panel_path)
    labels = pd.read_parquet(labels_path, columns=["timestamp", "symbol"] + [label_col(h) for h in HORIZONS])
    labels["timestamp"] = pd.to_datetime(labels["timestamp"], utc=True)
    if signal_panel[["timestamp", "symbol"]].reset_index(drop=True).equals(labels[["timestamp", "symbol"]].reset_index(drop=True)):
        panel = signal_panel.join(labels[[label_col(h) for h in HORIZONS]])
    else:
        panel = signal_panel.merge(labels, on=["timestamp", "symbol"], how="left")
    panel["_month"] = panel["timestamp"].dt.strftime("%Y-%m")

    model_summary = pd.read_csv(ml_dir / "model_comparison.csv")
    monthly = pd.read_csv(ml_dir / "monthly_metrics.csv")

    stat_rows: list[dict[str, Any]] = []
    bucket_rows: list[pd.DataFrame] = []
    monthly_rows: list[dict[str, Any]] = []
    tail_rows: list[dict[str, Any]] = []
    robust_rows: list[dict[str, Any]] = []
    panel_after_funding, funding_adjustment = add_after_funding_returns(panel, Path(args.funding_aligned))
    eval_panel = panel_after_funding if args.return_mode == "after_funding" else panel

    for horizon in HORIZONS:
        ret = eval_label_col(horizon, args.return_mode)
        for model in MODELS:
            col = signal_col(model, horizon)
            valid = bucketed_signal_frame(eval_panel, col, ret)
            stats, buckets = summarize_bucketed_signal(valid, col, ret)
            stat_rows.append({"model": model, "horizon": horizon, **stats.__dict__})
            buckets.insert(0, "horizon", horizon)
            buckets.insert(0, "model", model)
            bucket_rows.append(buckets)
            monthly_rows.extend(monthly_bucket_rows(valid, model, horizon, ret))
            tail_rows.extend(tail_contributor_rows(valid, model, horizon, col, ret))
            robust_rows.append(robust_tail_row(valid, model, horizon, ret))

    signal_stats = pd.DataFrame(stat_rows)
    bucket_profile = pd.concat(bucket_rows, ignore_index=True)
    monthly_bucket_profile = pd.DataFrame(monthly_rows)
    tail_contributors = pd.DataFrame(tail_rows)
    robust_tail_summary = pd.DataFrame(robust_rows)
    cost_grid = build_cost_rows(model_summary, signal_stats)
    funding_adjusted = funding_adjusted_diagnostics(panel_after_funding)
    funding = funding_coverage(signal_panel, Path(args.funding_dir))
    conflicts = conflict_summary(model_summary, monthly)

    signal_stats.to_csv(ml_dir / "cost_direction_signal_stats.csv", index=False)
    cost_grid.to_csv(ml_dir / "cost_scenario_grid.csv", index=False)
    bucket_profile.to_csv(ml_dir / "bucket_return_profile.csv", index=False)
    monthly_bucket_profile.to_csv(ml_dir / "monthly_bucket_profile.csv", index=False)
    tail_contributors.to_csv(ml_dir / "tail_contributors.csv", index=False)
    robust_tail_summary.to_csv(ml_dir / "robust_tail_summary.csv", index=False)
    funding_adjusted.to_csv(ml_dir / "funding_adjusted_diagnostics.csv", index=False)

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": str(ml_dir),
        "return_mode": args.return_mode,
        "cost_model_note": (
            "Cost scenarios use fee_bps + slippage_bps multiplied by observed top/bottom bucket turnover. "
            "They are pressure tests, not realized fills."
        ),
        "funding_coverage": funding,
        "funding_adjustment": funding_adjustment,
        "direction_conflicts": conflicts,
        "tail_diagnostics": {
            "diagnosis_counts": robust_tail_summary["diagnosis"].value_counts().to_dict(),
            "mean_median_split_rows": int((robust_tail_summary["diagnosis"] == "MEAN_SPREAD_OUTLIER_DOMINATED").sum()),
            "robust_negative_rows": int((robust_tail_summary["diagnosis"] == "ROBUST_SPREAD_NEGATIVE").sum()),
            "clean_thin_edge_rows": int((robust_tail_summary["diagnosis"] == "DIRECTIONALLY_CLEAN_THIN_EDGE").sum()),
            "interpretation": (
                "ML signal tail diagnostics are aligned with the earlier Phase 10 paper-signal finding: "
                "many negative mean spreads are driven by bucket-tail behavior rather than a uniformly negative median edge."
            ),
        },
        "outputs": {
            "signal_stats": str(ml_dir / "cost_direction_signal_stats.csv"),
            "cost_scenario_grid": str(ml_dir / "cost_scenario_grid.csv"),
            "bucket_return_profile": str(ml_dir / "bucket_return_profile.csv"),
            "monthly_bucket_profile": str(ml_dir / "monthly_bucket_profile.csv"),
            "tail_contributors": str(ml_dir / "tail_contributors.csv"),
            "robust_tail_summary": str(ml_dir / "robust_tail_summary.csv"),
            "funding_adjusted_diagnostics": str(ml_dir / "funding_adjusted_diagnostics.csv"),
            "summary": str(ml_dir / "cost_direction_research_summary.json"),
        },
        "answers": {
            "cost_profitability": (
                "1h is directionally clean before costs, but median gross spreads are very thin. "
                "Under full long-short turnover cost, the 1h model rows do not survive even the best tested cost scenario. "
                "Ridge 72h survives several median-spread cost scenarios, but it still has mean-spread direction conflict and is not promotion-ready."
            ),
            "funding": (
                "Funding is not deducted from the canonical ML labels. This diagnostic computes partial after-funding labels only where aligned hourly funding coverage is complete inside the forward horizon."
            ),
            "conflict_frequency": (
                "RankIC/spread direction conflict is common in the current research artifacts, especially beyond 1h."
            ),
            "how_to_use_signal": (
                "Use the ML score as a ranking diagnostic or gated input only after bucket-tail and cost tests pass; do not trade the raw top-minus-bottom spread blindly."
            ),
        },
    }
    (ml_dir / "cost_direction_research_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("ML cost/direction diagnostics")
    print(signal_stats[["model", "horizon", "median_spread", "avg_side_turnover_mean", "break_even_cost_bps_full_ls"]].to_string(index=False))
    print(f"Artifacts written to {ml_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
