#!/usr/bin/env python3
"""Summarize universe availability and crypto-native factor priorities.

This script is intentionally light: it audits existing artifacts and writes a
planning summary. It does not rebuild universes, factors, or ML models.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RUN_BASE = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"
ML_DIR = RUN_BASE / "ml_signal_prototype"


def parquet_overview(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False}
    df = pd.read_parquet(path, columns=["timestamp", "symbol"])
    return {
        "exists": True,
        "rows": int(len(df)),
        "symbols": int(df["symbol"].nunique()),
        "timestamp_min": str(df["timestamp"].min()),
        "timestamp_max": str(df["timestamp"].max()),
    }


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def universe_audit() -> pd.DataFrame:
    candidates = [
        {
            "dataset_id": "crypto_top50_usdt_perp_1h",
            "role": "static_current_top50_short_window",
            "bars": ROOT / "data/cache/crypto_top50_usdt_perp_1h/bars_1h.parquet",
            "labels": ROOT / "data/features/crypto_top50_usdt_perp_1h/labels.parquet",
            "manifest": ROOT / "data/cache/crypto_top50_usdt_perp_1h/manifest.json",
        },
        {
            "dataset_id": "crypto_top50_usdt_perp_1h_long_v1",
            "role": "static_current_top50_long_window",
            "bars": ROOT / "data/cache/crypto_top50_usdt_perp_1h_long_v1/bars_1h.parquet",
            "labels": ROOT / "data/features/crypto_top50_usdt_perp_1h_long_v1/labels.parquet",
            "manifest": ROOT / "data/cache/crypto_top50_usdt_perp_1h_long_v1/manifest.json",
        },
        {
            "dataset_id": "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1",
            "role": "dynamic_top50_current_listed_baseline",
            "bars": ROOT / "data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet",
            "labels": ROOT / "data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/labels.parquet",
            "manifest": ROOT / "data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/manifest.json",
        },
        {
            "dataset_id": "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1_crypto_native_v1",
            "role": "dynamic_top50_with_taker_funding_enrichment",
            "bars": ROOT / "data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1_crypto_native_v1/bars_1h.parquet",
            "labels": ROOT / "data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1_crypto_native_v1/labels.parquet",
            "manifest": ROOT / "data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/manifest.json",
        },
    ]
    rows: list[dict[str, Any]] = []
    for item in candidates:
        bars = parquet_overview(item["bars"])
        labels = parquet_overview(item["labels"])
        manifest = load_json(item["manifest"])
        limitations = manifest.get("known_limitations") or [manifest.get("research_caveat", "")]
        rows.append({
            "dataset_id": item["dataset_id"],
            "role": item["role"],
            "bars_exists": bool(bars.get("exists")),
            "labels_exists": bool(labels.get("exists")),
            "bars_rows": bars.get("rows"),
            "labels_rows": labels.get("rows"),
            "symbols": bars.get("symbols"),
            "timestamp_min": bars.get("timestamp_min"),
            "timestamp_max": bars.get("timestamp_max"),
            "known_limitations": " | ".join(str(x) for x in limitations if x),
            "minimal_next_use": (
                "usable_for_baseline_contrast"
                if bars.get("exists") and labels.get("exists")
                else "missing_required_bars_or_labels"
            ),
        })

    for missing_id, role in [
        ("top20_liquid_majors", "desired_conservative_universe"),
        ("top100_or_top150_dynamic", "desired_wider_cross_section"),
        ("age_liquidity_filtered_dynamic", "desired_tail_control_universe"),
    ]:
        rows.append({
            "dataset_id": missing_id,
            "role": role,
            "bars_exists": False,
            "labels_exists": False,
            "bars_rows": None,
            "labels_rows": None,
            "symbols": None,
            "timestamp_min": None,
            "timestamp_max": None,
            "known_limitations": "No complete canonical bars/labels/factor-values artifact found in current audit.",
            "minimal_next_use": "plan_only_until_data_built",
        })
    return pd.DataFrame(rows)


def factor_priority_plan(scorecard: pd.DataFrame) -> pd.DataFrame:
    existing = set(scorecard["factor_id"].astype(str))
    rows = [
        {
            "priority": 1,
            "theme": "funding / basis / carry",
            "current_coverage": "partial: funding_rate_level_20h, funding_rate_zscore_80h, funding_rate_change_24h",
            "next_batch_candidates": "funding carry after-settlement, funding change acceleration, funding x trend regime",
            "data_status": "aligned funding cache exists; basis/cross-venue data not yet canonical",
            "rationale": "Funding-adjusted diagnostic shows funding can flip ML spread conclusions.",
        },
        {
            "priority": 2,
            "theme": "taker buy/sell pressure",
            "current_coverage": "partial: taker_buy_ratio_20h, taker_buy_zscore_20h, taker_buy_delta_5h",
            "next_batch_candidates": "taker pressure persistence, taker pressure reversal, taker x volatility regime",
            "data_status": "taker enriched cache exists for dynamic dataset",
            "rationale": "Directly targets short-horizon crowding and bucket-tail behavior.",
        },
        {
            "priority": 3,
            "theme": "listing age / event / abnormal volume",
            "current_coverage": "weak: mostly volume zscore and quote-volume liquidity proxies",
            "next_batch_candidates": "listing age bucket, abnormal quote-volume shock, new-listing exclusion/admission flags",
            "data_status": "universe manifests expose current-listed limitation; listing metadata needs audit",
            "rationale": "Tail contributors are concentrated in jumpy/newer symbols; top50 current-listed bias remains material.",
        },
        {
            "priority": 4,
            "theme": "volatility regime / liquidity depth proxy",
            "current_coverage": "moderate: volatility, realized shape, amihud, volume ratios",
            "next_batch_candidates": "vol regime state, illiquidity shock, cost-budget eligibility score",
            "data_status": "OHLCV-derived proxies available; order-book depth not canonical",
            "rationale": "Existing alpha is too thin after turnover costs; execution-aware admission is needed.",
        },
        {
            "priority": 5,
            "theme": "BTC/ETH beta residual and sector/theme relative strength",
            "current_coverage": "limited: beta_20h/30h and taxonomy work exist, but no mature residual signal family",
            "next_batch_candidates": "BTC residual momentum, ETH residual reversal, sector relative strength",
            "data_status": "price data exists; sector taxonomy still under review",
            "rationale": "May reduce market beta tail contamination and improve cross-sectional interpretability.",
        },
        {
            "priority": 6,
            "theme": "open interest / liquidation / crowding",
            "current_coverage": "missing in canonical factor library",
            "next_batch_candidates": "defer until reliable OI/liquidation data contract exists",
            "data_status": "no complete canonical OI/liquidation cache found in this audit",
            "rationale": "Likely relevant for crypto, but adding it now would create a fragile data dependency.",
        },
    ]
    out = pd.DataFrame(rows)
    out["covered_factor_count_hint"] = [
        sum(any(token in fid for token in ["funding_rate"]) for fid in existing),
        sum(any(token in fid for token in ["taker_buy"]) for fid in existing),
        sum(any(token in fid for token in ["volume", "qvol", "vol_zscore"]) for fid in existing),
        sum(any(token in fid for token in ["vol", "amihud", "liquidity"]) for fid in existing),
        sum(any(token in fid for token in ["beta", "rank_close"]) for fid in existing),
        sum(any(token in fid for token in ["open_interest", "liquidation", "oi_"]) for fid in existing),
    ]
    return out


def main() -> int:
    ML_DIR.mkdir(parents=True, exist_ok=True)
    scorecard = pd.read_csv(RUN_BASE / "factor_diagnostics/factor_quality_scorecard.csv")
    universe = universe_audit()
    factor_plan = factor_priority_plan(scorecard)
    universe.to_csv(ML_DIR / "universe_availability_audit.csv", index=False)
    factor_plan.to_csv(ML_DIR / "crypto_native_factor_priority_plan.csv", index=False)

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "universe_findings": {
            "available_for_contrast": universe[universe["minimal_next_use"] == "usable_for_baseline_contrast"]["dataset_id"].tolist(),
            "missing_requested_universes": universe[universe["minimal_next_use"] == "plan_only_until_data_built"]["dataset_id"].tolist(),
            "top50_current_listed_limitation": (
                "The active dynamic universe reduces static-current-top50 bias but still uses a current-listed candidate pool. "
                "It does not include delisted historical symbols and therefore cannot fully remove survivorship bias."
            ),
            "minimal_next_experiment": (
                "Run lightweight signal diagnostics on existing static_top50_long_v1 versus dynamic_top50_current_listed before "
                "building top100/top150 factor values."
            ),
        },
        "factor_priority_findings": {
            "top_themes": factor_plan.head(5)["theme"].tolist(),
            "defer": "open interest / liquidation / crowding until canonical data exists",
            "next_batch_size": "8-12 factors after bucket/funding/universe diagnostics are reviewed",
        },
        "outputs": {
            "universe_availability_audit": str(ML_DIR / "universe_availability_audit.csv"),
            "crypto_native_factor_priority_plan": str(ML_DIR / "crypto_native_factor_priority_plan.csv"),
            "summary": str(ML_DIR / "next_steps_research_plan.json"),
        },
        "disclaimer": "Research planning only. No production signal, live trading, or investment claim.",
    }
    (ML_DIR / "next_steps_research_plan.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("Wrote universe audit and crypto-native factor priority plan")
    print(universe[["dataset_id", "role", "bars_exists", "labels_exists", "symbols", "minimal_next_use"]].to_string(index=False))
    print(factor_plan[["priority", "theme", "data_status"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
