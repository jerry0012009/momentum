#!/usr/bin/env python3
"""Build a lightweight universe contrast with the upgraded factor workflow metrics."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from backfill_factor_funding_tail_review import compute_factor_rows, load_registry_map
from evaluate_factors import LABEL_HORIZONS
from funding_adjusted_labels import add_funding_adjusted_returns, infer_funding_aligned_path

DIAG_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_diagnostics"
OUT_CSV = DIAG_DIR / "factor_workflow_universe_contrast_result.csv"
OUT_JSON = DIAG_DIR / "factor_workflow_universe_contrast_result.json"

UNIVERSES = {
    "static_top50_short": "crypto_top50_usdt_perp_1h",
    "static_top50_long": "crypto_top50_usdt_perp_1h_long_v1",
    "dynamic_top50_current_listed": "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1",
    "dynamic_top50_crypto_native": "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1_crypto_native_v1",
}

CONTRAST_GROUPS = {
    "static_long_vs_dynamic": [
        "bb_zscore_20h",
        "mom_20h",
        "q158_high_low_range",
        "reversal_5h",
        "rsi_14h",
        "tech_atr",
        "tech_macd",
        "volatility_20h",
        "wq101_alpha101",
        "wq101_alpha12",
        "wq101_alpha53",
    ],
    "crypto_native_overlay_vs_dynamic": [
        "funding_rate_change_24h",
        "funding_rate_level_20h",
        "funding_rate_zscore_80h",
        "taker_buy_delta_5h",
        "taker_buy_ratio_20h",
        "taker_buy_zscore_20h",
    ],
}


def load_labels(dataset_id: str) -> tuple[pd.DataFrame, dict]:
    features_dir = ROOT / "data" / "features" / dataset_id
    labels = pd.read_parquet(features_dir / "labels.parquet")
    funding_path = infer_funding_aligned_path(ROOT, dataset_id)
    labels, manifest = add_funding_adjusted_returns(labels, funding_path, LABEL_HORIZONS)
    keep = ["timestamp", "symbol"] + [f"ret_fwd_{h}" for h in LABEL_HORIZONS]
    keep += [f"ret_fwd_{h}_after_funding" for h in LABEL_HORIZONS if f"ret_fwd_{h}_after_funding" in labels.columns]
    return labels[keep], manifest


def summarize_factor(rows: list[dict], contrast_group: str, universe_role: str, dataset_id: str, factor_id: str) -> dict:
    if not rows:
        return {
            "contrast_group": contrast_group,
            "universe_role": universe_role,
            "dataset_id": dataset_id,
            "factor_name": factor_id,
            "status": "NO_EVALUATION_ROWS",
        }
    df = pd.DataFrame(rows)
    af = pd.to_numeric(df["after_funding_long_short_spread_mean"], errors="coerce")
    idx = af.abs().idxmax() if af.notna().any() else df.index[0]
    best = df.loc[idx]
    return {
        "contrast_group": contrast_group,
        "universe_role": universe_role,
        "dataset_id": dataset_id,
        "factor_name": factor_id,
        "status": "COMPUTED",
        "best_horizon": best.get("horizon", ""),
        "price_long_short_spread_mean": best.get("long_short_spread_mean", np.nan),
        "after_funding_long_short_spread_mean": best.get("after_funding_long_short_spread_mean", np.nan),
        "after_funding_coverage_rate": best.get("after_funding_coverage_rate", np.nan),
        "bucket_tail_diagnosis": best.get("bucket_tail_diagnosis", ""),
        "after_funding_bucket_tail_diagnosis": best.get("after_funding_bucket_tail_diagnosis", ""),
        "funding_adjusted_edge_flip": bool(best.get("funding_adjusted_edge_flip", False)),
    }


def main() -> int:
    registry = load_registry_map()
    labels_cache: dict[str, tuple[pd.DataFrame, dict]] = {}
    rows: list[dict] = []
    manifests: dict[str, dict] = {}

    work = [
        ("static_long_vs_dynamic", "static_top50_long"),
        ("static_long_vs_dynamic", "dynamic_top50_current_listed"),
        ("crypto_native_overlay_vs_dynamic", "dynamic_top50_crypto_native"),
        ("crypto_native_overlay_vs_dynamic", "dynamic_top50_current_listed"),
    ]
    for contrast_group, universe_role in work:
        dataset_id = UNIVERSES[universe_role]
        features_dir = ROOT / "data" / "features" / dataset_id
        if dataset_id not in labels_cache:
            labels_cache[dataset_id] = load_labels(dataset_id)
            manifests[dataset_id] = labels_cache[dataset_id][1]
        labels = labels_cache[dataset_id][0]
        for factor_id in CONTRAST_GROUPS[contrast_group]:
            path = features_dir / factor_id / "factor_values.parquet"
            if factor_id not in registry or not path.exists():
                rows.append({
                    "contrast_group": contrast_group,
                    "universe_role": universe_role,
                    "dataset_id": dataset_id,
                    "factor_name": factor_id,
                    "status": "MISSING_FACTOR_VALUES",
                })
                continue
            factor_rows = compute_factor_rows(
                factor_id=factor_id,
                spec=registry[factor_id],
                factor_values_path=path,
                labels=labels,
            )
            rows.append(summarize_factor(factor_rows, contrast_group, universe_role, dataset_id, factor_id))
            print(f"{contrast_group} {universe_role} {factor_id}: {len(factor_rows)} horizon rows", flush=True)

    out = pd.DataFrame(rows)
    DIAG_DIR.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_CSV, index=False)
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "rows": int(len(out)),
        "computed_rows": int((out["status"] == "COMPUTED").sum()),
        "contrast_groups": sorted(out["contrast_group"].unique().tolist()),
        "funding_manifests": manifests,
        "outputs": {"csv": str(OUT_CSV), "json": str(OUT_JSON)},
        "disclaimer": "Research universe contrast only. Not production, not live trading, not investment advice.",
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
