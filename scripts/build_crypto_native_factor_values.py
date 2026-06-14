#!/usr/bin/env python3
"""
Build crypto-native factor_values for Phase 7M-B.

1. Generate combined crypto-native bars cache (taker enriched + funding aligned)
2. Build factor_values for 6 Phase 7M-A factors only
3. Generate summary CSVs

Usage:
    python scripts/build_crypto_native_factor_values.py
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from factor_formula_registry import REGISTRY_BY_ID  # noqa: E402

# ── Phase 7M-A approved factor IDs ─────────────────────────────────
TAKER_FACTOR_IDS = ["taker_buy_ratio_20h", "taker_buy_zscore_20h", "taker_buy_delta_5h"]
FUNDING_FACTOR_IDS = ["funding_rate_level_20h", "funding_rate_zscore_80h", "funding_rate_change_24h"]
ALL_FACTOR_IDS = TAKER_FACTOR_IDS + FUNDING_FACTOR_IDS

# ── Dataset paths ───────────────────────────────────────────────────
STATIC_TAKER = ROOT / "data/cache/crypto_top50_usdt_perp_1h_taker_enriched/bars_1h.parquet"
DYNAMIC_TAKER = ROOT / "data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1_taker_enriched/bars_1h.parquet"
STATIC_FUNDING = ROOT / "data/cache/crypto_funding_rate_1h_contract_v1/funding_rate_1h_aligned_static.parquet"
DYNAMIC_FUNDING = ROOT / "data/cache/crypto_funding_rate_1h_contract_v1/funding_rate_1h_aligned_dynamic.parquet"

STATIC_COMBINED = ROOT / "data/cache/crypto_top50_usdt_perp_1h_crypto_native_v1/bars_1h.parquet"
DYNAMIC_COMBINED = ROOT / "data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1_crypto_native_v1/bars_1h.parquet"

REPORT_DIR = ROOT / "research/factor_runs/crypto_top50_factor_library"


def build_combined_bars(
    taker_path: Path,
    funding_path: Path,
    out_path: Path,
    variant: str,
) -> dict:
    """Combine taker enriched bars with funding aligned cache."""
    taker = pd.read_parquet(taker_path)
    funding = pd.read_parquet(funding_path)

    source_rows = len(taker)
    syms = sorted(taker["symbol"].unique())

    # Ensure timestamp dtype
    taker["timestamp"] = pd.to_datetime(taker["timestamp"], utc=True)
    funding["timestamp"] = pd.to_datetime(funding["timestamp"], utc=True)

    # Merge on (timestamp, symbol) — left join, taker is base
    funding_cols = ["timestamp", "symbol", "funding_rate", "funding_known_at",
                    "funding_interval_hours", "funding_age_hours"]
    combined = taker.merge(
        funding[funding_cols],
        on=["timestamp", "symbol"],
        how="left",
    )

    assert len(combined) == source_rows, (
        f"Row count mismatch: {len(combined)} != {source_rows}"
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(out_path, index=False)

    tbqv_cov = combined["taker_buy_quote_volume"].notna().mean() if "taker_buy_quote_volume" in combined.columns else 0.0
    fr_cov = combined["funding_rate"].notna().mean() if "funding_rate" in combined.columns else 0.0

    schema_status = "PASS"
    if tbqv_cov < 0.5 or fr_cov < 0.5:
        schema_status = "PARTIAL"

    return {
        "dataset_variant": variant,
        "source_taker_bars_path": str(taker_path),
        "source_funding_aligned_path": str(funding_path),
        "combined_bars_path": str(out_path),
        "source_rows": source_rows,
        "combined_rows": len(combined),
        "row_count_match": len(combined) == source_rows,
        "n_symbols": len(syms),
        "timestamp_min": str(combined["timestamp"].min()),
        "timestamp_max": str(combined["timestamp"].max()),
        "has_taker_buy_quote_volume": "taker_buy_quote_volume" in combined.columns,
        "taker_buy_quote_volume_coverage": round(tbqv_cov, 6),
        "has_funding_rate": "funding_rate" in combined.columns,
        "funding_rate_coverage": round(fr_cov, 6),
        "schema_status": schema_status,
        "notes": f"Combined: taker {tbqv_cov:.1%} + funding {fr_cov:.1%}",
    }


def build_factor_values(bars_path: Path, factor_ids: list[str], dataset_id: str) -> list[dict]:
    """Build factor_values for specified factors from combined bars."""
    bars = pd.read_parquet(bars_path)
    bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
    bars = bars.sort_values(["symbol", "timestamp"])

    syms = sorted(bars["symbol"].unique())
    feature_root = ROOT / "data" / "features" / dataset_id
    computed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    rows = []
    for fid in factor_ids:
        spec = REGISTRY_BY_ID[fid]
        parts = []
        for _sym, g in bars.groupby("symbol", sort=False):
            g = g.copy().sort_values("timestamp")
            g[fid] = spec.compute_fn(g)
            parts.append(g[["timestamp", "symbol", fid]])
        wide = pd.concat(parts, ignore_index=True)

        out = wide[["timestamp", "symbol", fid]].rename(columns={fid: "factor_value"})
        out.insert(2, "factor_name", fid)
        out["known_at"] = out["timestamp"]
        out["source_timeframe"] = "1h"
        out["computed_at"] = computed_at
        out = out[["timestamp", "symbol", "factor_name", "factor_value",
                    "known_at", "source_timeframe", "computed_at"]]

        target_dir = feature_root / fid
        target_dir.mkdir(parents=True, exist_ok=True)
        out.to_parquet(target_dir / "factor_values.parquet", index=False)

        coverage = out["factor_value"].notna().mean()
        if coverage >= 0.50:
            gate = "PASS"
        elif coverage >= 0.20:
            gate = "PARTIAL"
        else:
            gate = "FAIL"

        rows.append({
            "factor_id": fid,
            "family": spec.family,
            "dataset_id": dataset_id,
            "rows": len(out),
            "n_symbols": len(syms),
            "timestamp_min": str(out["timestamp"].min()),
            "timestamp_max": str(out["timestamp"].max()),
            "coverage": round(coverage, 6),
            "missing_rate": round(1 - coverage, 6),
            "gate": gate,
            "notes": f"{spec.notes[:80]}",
        })
        print(f"  {fid}: rows={len(out)} coverage={coverage:.3%} gate={gate}")

    return rows


def main():
    print("=" * 60)
    print("Phase 7M-B: Crypto-native Factor Values Build")
    print("=" * 60)

    # ── Step 1: Build combined bars ─────────────────────────────────
    print("\n=== Building combined crypto-native bars ===")

    static_join = build_combined_bars(STATIC_TAKER, STATIC_FUNDING, STATIC_COMBINED, "static")
    print(f"  static: {static_join['combined_rows']:,} rows, "
          f"taker {static_join['taker_buy_quote_volume_coverage']:.1%}, "
          f"funding {static_join['funding_rate_coverage']:.1%}")

    dynamic_join = build_combined_bars(DYNAMIC_TAKER, DYNAMIC_FUNDING, DYNAMIC_COMBINED, "dynamic")
    print(f"  dynamic: {dynamic_join['combined_rows']:,} rows, "
          f"taker {dynamic_join['taker_buy_quote_volume_coverage']:.1%}, "
          f"funding {dynamic_join['funding_rate_coverage']:.1%}")

    join_df = pd.DataFrame([static_join, dynamic_join])
    join_df.to_csv(REPORT_DIR / "phase7m_b_crypto_native_dataset_join_summary.csv", index=False)
    print("  Saved join summary")

    # ── Step 2: Build factor_values ─────────────────────────────────
    print("\n=== Building static factor_values ===")
    static_id = "crypto_top50_usdt_perp_1h_crypto_native_v1"
    static_rows = build_factor_values(STATIC_COMBINED, ALL_FACTOR_IDS, static_id)
    pd.DataFrame(static_rows).to_csv(
        REPORT_DIR / "phase7m_b_static_factor_values_build_summary.csv", index=False
    )

    print("\n=== Building dynamic factor_values ===")
    dynamic_id = "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1_crypto_native_v1"
    dynamic_rows = build_factor_values(DYNAMIC_COMBINED, ALL_FACTOR_IDS, dynamic_id)
    pd.DataFrame(dynamic_rows).to_csv(
        REPORT_DIR / "phase7m_b_dynamic_factor_values_build_summary.csv", index=False
    )

    print("\nDone.")


if __name__ == "__main__":
    main()
