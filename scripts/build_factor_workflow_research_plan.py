#!/usr/bin/env python3
"""Build lightweight universe and crypto-native factor research plan artifacts.

This script does not rebuild universes or factors. It audits existing artifacts,
summarizes the current universe limitations, and ranks the next crypto-native
factor candidates from existing backlog/public/rank sources.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"
DIAG_DIR = BASE / "factor_diagnostics"
OUT_UNIVERSE = DIAG_DIR / "factor_workflow_universe_contrast_plan.csv"
OUT_FACTORS = DIAG_DIR / "crypto_native_next_factor_candidates.csv"
OUT_SUMMARY = DIAG_DIR / "factor_workflow_research_plan.json"
OUT_UNIVERSE_RESULT = DIAG_DIR / "factor_workflow_universe_contrast_result.csv"
OUT_UNIVERSE_RESULT_JSON = DIAG_DIR / "factor_workflow_universe_contrast_result.json"
CANONICAL_EVAL = BASE / "factor_level_evaluation" / "factor_level_metric_panel.csv"


def parquet_overview(path: Path) -> dict:
    if not path.exists():
        return {"exists": False}
    try:
        df = pd.read_parquet(path, columns=["timestamp", "symbol"])
    except Exception as exc:
        return {"exists": True, "read_error": str(exc)}
    return {
        "exists": True,
        "rows": int(len(df)),
        "symbols": int(df["symbol"].nunique()),
        "timestamp_min": str(df["timestamp"].min()),
        "timestamp_max": str(df["timestamp"].max()),
    }


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def factor_values_overview(universe_id: str) -> dict:
    feature_dir = ROOT / "data" / "features" / universe_id
    paths = sorted(feature_dir.glob("*/factor_values.parquet"))
    return {
        "factor_values_files": int(len(paths)),
        "has_factor_values": bool(paths),
    }


def build_universe_plan() -> pd.DataFrame:
    candidates = [
        {
            "universe_id": "crypto_top50_usdt_perp_1h",
            "contrast_role": "static_top50_short_window",
            "bars": ROOT / "data/cache/crypto_top50_usdt_perp_1h/bars_1h.parquet",
            "labels": ROOT / "data/features/crypto_top50_usdt_perp_1h/labels.parquet",
            "manifest": ROOT / "data/cache/crypto_top50_usdt_perp_1h/manifest.json",
        },
        {
            "universe_id": "crypto_top50_usdt_perp_1h_long_v1",
            "contrast_role": "static_top50_long_window",
            "bars": ROOT / "data/cache/crypto_top50_usdt_perp_1h_long_v1/bars_1h.parquet",
            "labels": ROOT / "data/features/crypto_top50_usdt_perp_1h_long_v1/labels.parquet",
            "manifest": ROOT / "data/cache/crypto_top50_usdt_perp_1h_long_v1/manifest.json",
        },
        {
            "universe_id": "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1",
            "contrast_role": "dynamic_top50_current_listed_baseline",
            "bars": ROOT / "data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet",
            "labels": ROOT / "data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/labels.parquet",
            "manifest": ROOT / "data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/manifest.json",
        },
        {
            "universe_id": "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1_crypto_native_v1",
            "contrast_role": "dynamic_top50_crypto_native_enriched",
            "bars": ROOT / "data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1_crypto_native_v1/bars_1h.parquet",
            "labels": ROOT / "data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1_crypto_native_v1/labels.parquet",
            "manifest": ROOT / "data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/manifest.json",
        },
    ]
    rows = []
    for c in candidates:
        bars = parquet_overview(c["bars"])
        labels = parquet_overview(c["labels"])
        factor_values = factor_values_overview(c["universe_id"])
        manifest = load_json(c["manifest"])
        has_labels = bool(labels.get("exists"))
        has_bars = bool(bars.get("exists"))
        has_factor_values = bool(factor_values.get("has_factor_values"))
        if has_bars and has_labels and has_factor_values:
            status = "READY_FOR_FACTOR_EVALUATION_CONTRAST"
        elif has_bars and has_labels:
            status = "LABEL_ONLY_READY_FACTOR_VALUES_MISSING"
        else:
            status = "MISSING_CANONICAL_BARS_OR_LABELS"
        rows.append({
            "universe_id": c["universe_id"],
            "contrast_role": c["contrast_role"],
            "bars_exists": bool(bars.get("exists")),
            "labels_exists": bool(labels.get("exists")),
            "factor_values_files": factor_values.get("factor_values_files", 0),
            "bars_rows": bars.get("rows"),
            "labels_rows": labels.get("rows"),
            "symbols": bars.get("symbols"),
            "timestamp_min": bars.get("timestamp_min"),
            "timestamp_max": bars.get("timestamp_max"),
            "known_limitation": " | ".join(str(x) for x in manifest.get("known_limitations", []) if x)
            or str(manifest.get("research_caveat", "")),
            "minimal_contrast_status": status,
        })
    for universe_id, role in [
        ("top20_liquid_majors", "conservative_liquidity_control"),
        ("top100_or_top150_dynamic", "wider_cross_section_control"),
        ("age_liquidity_filtered_dynamic", "tail_and_listing_age_control"),
    ]:
        rows.append({
            "universe_id": universe_id,
            "contrast_role": role,
            "bars_exists": False,
            "labels_exists": False,
            "factor_values_files": 0,
            "bars_rows": None,
            "labels_rows": None,
            "symbols": None,
            "timestamp_min": None,
            "timestamp_max": None,
            "known_limitation": "No complete canonical bars/labels/factor-values artifact found.",
            "minimal_contrast_status": "PLAN_ONLY_UNTIL_DATA_BUILT",
        })
    return pd.DataFrame(rows)


def build_factor_candidates() -> pd.DataFrame:
    backlog = pd.read_csv(DIAG_DIR / "factor_expansion_backlog.csv")
    selected = []
    priority_themes = [
        "funding", "basis", "carry", "taker", "volume_pressure",
        "listing", "abnormal", "volatility", "liquidity", "beta", "sector",
    ]
    for _, row in backlog.iterrows():
        text = " ".join(str(row.get(c, "")) for c in backlog.columns).lower()
        if any(theme in text for theme in priority_themes):
            selected.append({
                "candidate_factor_id": row["candidate_factor_id"],
                "source": "factor_expansion_backlog",
                "theme": row.get("candidate_theme", ""),
                "formula": row.get("formula_sketch", ""),
                "required_inputs": row.get("required_inputs", ""),
                "data_status": row.get("available_inputs_check", ""),
                "expected_direction": row.get("expected_direction", ""),
                "priority_reason": row.get("expected_diagnostic_value", ""),
                "recommended_action": (
                    "INTAKE_AFTER_WORKFLOW_UPGRADE"
                    if str(row.get("requires_new_data", "")).upper() == "NO"
                    else "BACKLOG_UNTIL_DATA_CONTRACT"
                ),
            })

    rank_sources = [
        {
            "candidate_factor_id": "rank49_funding_basis_crowding_proxy",
            "source": "scripts/build_rank49_funding_basis_crowding_clean_replication.py",
            "theme": "funding / basis / crowded-long unwind",
            "formula": "funding_z and premium_z crowding proxy; adapt only after data contract review",
            "required_inputs": "funding_rate|premium_index",
            "data_status": "funding exists; premium/basis not canonical in factor workflow",
            "expected_direction": "conditional",
            "priority_reason": "Directly targets funding/basis crowding already researched in rank source.",
            "recommended_action": "BACKLOG_UNTIL_BASIS_DATA_CONTRACT",
        },
        {
            "candidate_factor_id": "rank368_funding_extreme_bandfade_proxy",
            "source": "scripts/run_rank368_funding_extreme_bandfade_paper_runner.py",
            "theme": "funding extreme / mean reversion",
            "formula": "funding extreme x price band stretch fade proxy",
            "required_inputs": "funding_rate|ohlcv",
            "data_status": "funding and OHLCV available; adapt formula to factor registry carefully",
            "expected_direction": "conditional",
            "priority_reason": "Existing rank300+ funding idea; avoids inventing a new formula from scratch.",
            "recommended_action": "CANDIDATE_FOR_NEXT_BATCH_REVIEW",
        },
    ]
    selected.extend(rank_sources)

    df = pd.DataFrame(selected).drop_duplicates("candidate_factor_id")
    if df.empty:
        return df
    backlog_df = df[df["source"] == "factor_expansion_backlog"].head(10)
    rank_df = df[df["source"] != "factor_expansion_backlog"].head(2)
    return pd.concat([backlog_df, rank_df], ignore_index=True).head(12)


def main() -> int:
    DIAG_DIR.mkdir(parents=True, exist_ok=True)
    universe = build_universe_plan()
    factors = build_factor_candidates()
    universe.to_csv(OUT_UNIVERSE, index=False)
    factors.to_csv(OUT_FACTORS, index=False)
    canonical_eval_exists = CANONICAL_EVAL.exists()
    universe_result = load_json(OUT_UNIVERSE_RESULT_JSON)
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "universe": {
            "ready_for_factor_evaluation_contrast": universe[
                universe["minimal_contrast_status"] == "READY_FOR_FACTOR_EVALUATION_CONTRAST"
            ]["universe_id"].tolist(),
            "label_only_ready_factor_values_missing": universe[
                universe["minimal_contrast_status"] == "LABEL_ONLY_READY_FACTOR_VALUES_MISSING"
            ]["universe_id"].tolist(),
            "plan_only": universe[
                universe["minimal_contrast_status"] == "PLAN_ONLY_UNTIL_DATA_BUILT"
            ]["universe_id"].tolist(),
            "interpretation": (
                "Existing top50 variants have bars/labels, but alternate universes still need "
                "per-factor factor_values before true factor-evaluation contrast. Top20, "
                "top100/top150, and age/liquidity filtered universes still need canonical data."
            ),
            "canonical_baseline_evaluation_exists": canonical_eval_exists,
            "lightweight_contrast_result_exists": OUT_UNIVERSE_RESULT.exists(),
            "lightweight_contrast_result": str(OUT_UNIVERSE_RESULT) if OUT_UNIVERSE_RESULT.exists() else "",
            "lightweight_contrast_interpretation": universe_result.get("interpretation", {}),
        },
        "crypto_native_next_batch": {
            "candidate_count": int(len(factors)),
            "sources": sorted(factors["source"].unique().tolist()) if not factors.empty else [],
            "principle": "Reuse existing backlog/public/rank sources; do not invent fragile one-off data dependencies.",
        },
        "outputs": {
            "universe_plan": str(OUT_UNIVERSE),
            "factor_candidates": str(OUT_FACTORS),
            "summary": str(OUT_SUMMARY),
        },
        "disclaimer": "Research workflow planning only. Not production, not live trading, not investment advice.",
    }
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT_UNIVERSE}")
    print(f"Wrote {OUT_FACTORS}")
    print(f"Wrote {OUT_SUMMARY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
