#!/usr/bin/env python3
"""Summarize the LS-utility after-funding ML experiment for the static report."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RUN_BASE = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"
DEFAULT_ML_DIR = RUN_BASE / "ml_signal_prototype_ls_utility_after_funding"
DEFAULT_OUT = ROOT / "reports" / "site" / "factor-library" / "assets" / "signal_ml_ls_utility_summary.json"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def finite_or_none(value: Any) -> float | int | str | None:
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def cost_survival_by_model_horizon(cost_grid: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        cost_grid.groupby(["model", "horizon"], sort=False)["survives_full_ls_cost"]
        .agg(["sum", "count"])
        .reset_index()
        .rename(columns={"sum": "full_ls_scenarios_survived", "count": "scenarios_total"})
    )
    grouped["full_ls_scenarios_survived"] = grouped["full_ls_scenarios_survived"].astype(int)
    grouped["scenarios_total"] = grouped["scenarios_total"].astype(int)
    return grouped


def build_summary(ml_dir: Path) -> dict[str, Any]:
    manifest = load_json(ml_dir / "manifest.json")
    model = pd.read_csv(ml_dir / "model_comparison.csv")
    stats = pd.read_csv(ml_dir / "cost_direction_signal_stats.csv")
    cost = pd.read_csv(ml_dir / "cost_scenario_grid.csv")
    robust = pd.read_csv(ml_dir / "robust_tail_summary.csv")
    checks = pd.read_csv(ml_dir / "quality_checks.csv")
    cost_research = load_json(ml_dir / "cost_direction_research_summary.json")

    survival = cost_survival_by_model_horizon(cost)
    merged = (
        model.merge(stats, on=["model", "horizon"], how="left", suffixes=("_model", "_net"))
        .merge(survival, on=["model", "horizon"], how="left")
    )

    rows: list[dict[str, Any]] = []
    for _, row in merged.iterrows():
        rows.append({
            "model": row["model"],
            "horizon": row["horizon"],
            "mean_rankic": finite_or_none(row["mean_rankic"]),
            "mean_spread": finite_or_none(row["mean_spread_net"]),
            "median_spread": finite_or_none(row["median_spread_net"]),
            "positive_spread_fraction": finite_or_none(row["positive_spread_fraction"]),
            "consistency": row["rankic_spread_consistency"],
            "long_short_turnover_mean": finite_or_none(row["long_short_turnover_mean"]),
            "break_even_cost_bps_full_ls": finite_or_none(row["break_even_cost_bps_full_ls"]),
            "full_ls_scenarios_survived": int(row["full_ls_scenarios_survived"]),
        })

    feature_summary = manifest.get("feature_summary", {})
    utility_manifest = manifest.get("utility_manifest", {})
    run = {
        "name": "ls_utility_after_funding",
        "path": str(ml_dir),
        "selection_policy": feature_summary.get("selection_policy"),
        "label_mode": manifest.get("label_mode"),
        "train_label_columns": manifest.get("train_label_columns"),
        "eval_label_columns": manifest.get("eval_label_columns"),
        "eligible_factors": feature_summary.get("eligible_factors"),
        "policy_pool_factors": feature_summary.get("policy_pool_factors"),
        "selected_factors": feature_summary.get("selected_factors"),
        "strict_factors": feature_summary.get("strict_ls_ic_aligned_factors"),
        "fallback_factors": feature_summary.get("fallback_ls_ic_aligned_factors"),
        "selected_strict": feature_summary.get("selected_strict_ls_ic_aligned"),
        "selected_fallback": feature_summary.get("selected_fallback_ls_ic_aligned"),
        "model_horizon_rows": int(len(model)),
        "consistent_rows": int((model["rankic_spread_consistency"] == "CONSISTENT_POSITIVE").sum()),
        "cost_survival": int(cost["survives_full_ls_cost"].sum()),
        "cost_total": int(len(cost)),
        "positive_median_rows": int((stats["median_spread"] > 0).sum()),
        "utility_manifest": utility_manifest,
        "funding_manifest": manifest.get("funding_manifest"),
        "tail_counts": robust["diagnosis"].value_counts().to_dict(),
        "quality_checks": checks.to_dict(orient="records"),
        "rows": rows,
    }

    return {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": str(ml_dir),
            "disclaimer": "Research diagnostic only. Not a trading signal or investment advice.",
        },
        "runs": {
            "ls_utility_after_funding": run,
        },
        "interpretation": {
            "headline": (
                "LS utility target did not solve the after-funding LS extraction problem: "
                "1h remains too thin for costs, and 4h/24h/72h stay negative."
            ),
            "takeaways": [
                "This run keeps the after-funding LS factor pool: 239 eligible factors, 107 policy-pool factors, 60 selected, 24 strict net-LS factors.",
                "The training target is no longer raw RankIC regression: per timestamp, top after-funding return quintile is +1, bottom quintile is -1, and the middle 60% is 0.",
                "The model still learns ranking information: all 12 model-horizon rows have positive RankIC when evaluated on after-funding forward returns.",
                "But net LS extraction still fails beyond 1h: 4h, 24h, and 72h median after-funding spreads are negative for every model.",
                "1h median after-funding spread is positive, but break-even full-LS cost is only 0.44-0.95 bps, so it still cannot survive realistic fee/slippage.",
                "Full-LS cost survival remains 0/48, meaning no tested model-horizon-scenario clears the fee/slippage grid.",
            ],
            "recommendations": [
                "Do not promote this LS utility ML signal.",
                "Do not spend more cycles only changing the supervised label shape; the bottleneck is portfolio extraction and turnover/cost/tail control.",
                "The next viable direction is a constrained portfolio layer: hold threshold, turnover budget, tail veto, and possibly horizon-specific long-only/short-only admission.",
                "Keep after-funding returns as the mandatory evaluation target for all future signal work.",
            ],
        },
        "cost_direction_research": cost_research,
    }


def main() -> int:
    summary = build_summary(DEFAULT_ML_DIR)
    DEFAULT_OUT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {DEFAULT_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
