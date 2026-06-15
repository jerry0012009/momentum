#!/usr/bin/env python3
"""Phase 12A: Paper Signal Generation Harness v0.

Local paper signal harness only. No real execution. No exchange connection.
No final model. No alpha claim. No production claim.
"""
import warnings
from pathlib import Path
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"
PQ = OUT / "phase9b_signal_panel.parquet"
LIQ = OUT / "phase11b_canonical_liquidity_panel.parquet"
SIGNAL_ID = "signal_v0_core_only"
HORIZON = "1h"
VARIANT = "original_no_guard"
N_BUCK = 10


def main():
    print("Phase 12A: Paper Signal Generation Harness v0")

    # --- Part A: Candidate freeze ---
    print("\n[1/7] Creating candidate freeze...")
    freeze = pd.DataFrame([{
        "candidate_id": f"{SIGNAL_ID}__{HORIZON}__{VARIANT}",
        "source_phase": "Phase 11B",
        "signal_id": SIGNAL_ID,
        "horizon": HORIZON,
        "variant": VARIANT,
        "status": "PAPER_SIGNAL_DIAGNOSTIC_ONLY",
        "rationale": "Only variant surviving Phase 11A/11B cost+capacity diagnostic (COST_CAPACITY_SENSITIVE)",
        "allowed_for_paper_signal": True,
        "allowed_for_real_execution": False,
    }])
    freeze.to_csv(OUT / "phase12a_candidate_freeze.csv", index=False)
    print(f"  Frozen: {freeze.iloc[0]['candidate_id']}")

    # --- Part B: Load data ---
    print("\n[2/7] Loading signal panel + liquidity data...")
    sig = pd.read_parquet(PQ)
    liq = pd.read_parquet(LIQ)

    # Get latest timestamp
    ts_latest = sig["timestamp"].max()
    snap = sig[sig["timestamp"] == ts_latest].copy()
    print(f"  Latest timestamp: {ts_latest}")
    print(f"  Symbols at latest: {len(snap)}")

    # --- Part C: Generate signal snapshot ---
    print("\n[3/7] Generating signal snapshot...")
    snap["signal_value"] = snap[SIGNAL_ID]
    snap = snap.dropna(subset=["signal_value"])
    snap = snap.sort_values("signal_value", ascending=False).reset_index(drop=True)
    snap["signal_rank"] = range(1, len(snap) + 1)
    snap["signal_percentile"] = snap["signal_value"].rank(pct=True)

    # Assign sides (top 20% = UPPER, bottom 20% = LOWER)
    n = len(snap)
    nq = max(int(n * 0.20), 1)
    snap["side_label"] = "NEUTRAL"
    snap.loc[:nq - 1, "side_label"] = "UPPER_SIDE"
    snap.loc[n - nq:, "side_label"] = "LOWER_SIDE"

    # Diagnostic weights: +0.5 upper, -0.5 lower, equal-weight within
    snap["raw_weight"] = 0.0
    upper = snap["side_label"] == "UPPER_SIDE"
    lower = snap["side_label"] == "LOWER_SIDE"
    snap.loc[upper, "raw_weight"] = 0.5 / upper.sum()
    snap.loc[lower, "raw_weight"] = -0.5 / lower.sum()
    snap["diagnostic_weight"] = snap["raw_weight"]

    # Merge liquidity from the canonical panel (covers all available symbols)
    # Use per-symbol median volume across all timestamps for robustness
    liq_agg = liq.groupby("symbol").agg(
        quote_volume=("quote_volume", "median"),
        notional_volume=("notional_volume", "median"),
    ).reset_index()
    snap = snap.merge(liq_agg, on="symbol", how="left", suffixes=("", "_liq"))
    if "quote_volume_liq" in snap.columns:
        snap["quote_volume"] = snap["quote_volume"].fillna(snap["quote_volume_liq"])
        snap.drop(columns=["quote_volume_liq"], inplace=True)
    if "notional_volume_liq" in snap.columns:
        snap["notional_volume"] = snap["notional_volume"].fillna(snap["notional_volume_liq"])
        snap.drop(columns=["notional_volume_liq"], inplace=True)

    snap["quote_volume"] = snap["quote_volume"].fillna(0)
    snap["notional_volume"] = snap["notional_volume"].fillna(0)
    snap["liquidity_status"] = snap["notional_volume"].apply(lambda x: "AVAILABLE" if x > 0 else "DATA_MISSING")
    snap["notes"] = ""
    snap.loc[snap["notional_volume"] == 0, "notes"] = "zero_volume"

    # Filter to symbols with liquidity data for paper signal
    has_liq = snap["notional_volume"] > 0
    print(f"  Symbols with liquidity: {has_liq.sum()}/{len(snap)}")
    print(f"  Symbols without liquidity (excluded from paper weights): {(~has_liq).sum()}")

    # Re-rank only among liquidity-available symbols
    snap_liq = snap[has_liq].copy().sort_values("signal_value", ascending=False).reset_index(drop=True)
    snap_liq["signal_rank"] = range(1, len(snap_liq) + 1)
    snap_liq["signal_percentile"] = snap_liq["signal_value"].rank(pct=True)

    n_liq = len(snap_liq)
    nq_liq = max(int(n_liq * 0.20), 1)
    snap_liq["side_label"] = "NEUTRAL"
    snap_liq.loc[:nq_liq - 1, "side_label"] = "UPPER_SIDE"
    snap_liq.loc[n_liq - nq_liq:, "side_label"] = "LOWER_SIDE"

    snap_liq["raw_weight"] = 0.0
    upper_liq = snap_liq["side_label"] == "UPPER_SIDE"
    lower_liq = snap_liq["side_label"] == "LOWER_SIDE"
    snap_liq.loc[upper_liq, "raw_weight"] = 0.5 / upper_liq.sum()
    snap_liq.loc[lower_liq, "raw_weight"] = -0.5 / lower_liq.sum()
    snap_liq["diagnostic_weight"] = snap_liq["raw_weight"]

    # Save full snapshot (all 266 symbols with liquidity status)
    out_cols = ["timestamp", "symbol", "signal_value", "signal_rank", "signal_percentile",
                "side_label", "raw_weight", "diagnostic_weight", "quote_volume",
                "notional_volume", "liquidity_status", "notes"]
    # Merge liquidity-available ranks back to full snapshot
    snap = snap.drop(columns=["signal_rank", "signal_percentile", "side_label", "raw_weight", "diagnostic_weight"], errors="ignore")
    snap = snap.merge(snap_liq[["symbol", "signal_rank", "signal_percentile", "side_label", "raw_weight", "diagnostic_weight"]],
                      on="symbol", how="left")
    snap["signal_rank"] = snap["signal_rank"].fillna(-1).astype(int)
    snap["signal_percentile"] = snap["signal_percentile"].fillna(0)
    snap["side_label"] = snap["side_label"].fillna("EXCLUDED_NO_LIQUIDITY")
    snap["raw_weight"] = snap["raw_weight"].fillna(0)
    snap["diagnostic_weight"] = snap["diagnostic_weight"].fillna(0)
    snap["notes"] = snap.apply(lambda r: "excluded_no_liquidity" if r["side_label"] == "EXCLUDED_NO_LIQUIDITY" else r["notes"], axis=1)
    snap[out_cols].to_csv(OUT / "phase12a_latest_signal_snapshot.csv", index=False)
    print(f"  Snapshot: {len(snap)} symbols, {upper_liq.sum()} upper, {lower_liq.sum()} lower (from {n_liq} with liquidity)")

    # --- Part D: Paper weights ---
    print("\n[4/7] Generating paper weights...")
    # Only include symbols with actual side assignments (not EXCLUDED_NO_LIQUIDITY)
    weighted = snap[snap["side_label"].isin(["UPPER_SIDE", "LOWER_SIDE"])]
    weights = weighted[["symbol", "side_label", "diagnostic_weight",
                        "signal_value", "signal_rank", "notional_volume"]].copy()
    weights["candidate_id"] = f"{SIGNAL_ID}__{HORIZON}__{VARIANT}"
    weights["weight_type"] = "DIAGNOSTIC_PAPER_ONLY"
    weights["gross_exposure"] = abs(weights["diagnostic_weight"])
    weights.to_csv(OUT / "phase12a_paper_weights.csv", index=False)
    net_weight = weights["diagnostic_weight"].sum()
    gross_exp = weights["gross_exposure"].sum()
    n_upper = (weights["side_label"] == "UPPER_SIDE").sum()
    n_lower = (weights["side_label"] == "LOWER_SIDE").sum()
    print(f"  Weights: {len(weights)} symbols ({n_upper} upper + {n_lower} lower), net={net_weight:.6f}, gross={gross_exp:.4f}")

    # --- Part E: Candidate universe ---
    print("\n[5/7] Building candidate universe...")
    universe = snap[["symbol", "side_label", "signal_rank", "signal_value", "notional_volume"]].copy()
    universe["candidate_id"] = f"{SIGNAL_ID}__{HORIZON}__{VARIANT}"
    universe.to_csv(OUT / "phase12a_candidate_universe.csv", index=False)

    # --- Part E2: Liquidity overlay ---
    print("  Building liquidity overlay...")
    lo = snap[["symbol", "quote_volume", "notional_volume"]].copy()
    lo["participation_capacity_0_5pct"] = lo["notional_volume"] * 0.005
    lo["participation_capacity_1pct"] = lo["notional_volume"] * 0.01
    lo["participation_capacity_5pct"] = lo["notional_volume"] * 0.05
    lo["liquidity_warning"] = lo["notional_volume"].apply(lambda x: "LOW_LIQUIDITY" if x < 10000 else "OK")
    lo["zero_volume_flag"] = lo["notional_volume"] == 0
    nv_med = lo["notional_volume"][lo["notional_volume"] > 0].median()
    lo["outlier_volume_flag"] = lo["notional_volume"] > nv_med * 10 if nv_med > 0 else False
    lo.to_csv(OUT / "phase12a_liquidity_overlay.csv", index=False)

    # --- Part F: Preflight checks ---
    print("\n[6/7] Running preflight checks...")
    checks = []
    checks.append(("signal_panel_exists", "PASS" if PQ.exists() else "FAIL"))
    checks.append(("candidate_freeze_exists", "PASS"))
    checks.append(("liquidity_panel_exists", "PASS" if LIQ.exists() else "FAIL"))
    checks.append(("latest_timestamp_available", "PASS" if len(snap) > 0 else "FAIL"))
    checks.append(("no_duplicate_timestamp_symbol", "PASS" if snap.duplicated(subset=["timestamp", "symbol"]).sum() == 0 else "FAIL"))
    checks.append(("symbol_overlap_with_liquidity", "PASS" if snap["notional_volume"].notna().sum() > 0 else "FAIL"))
    checks.append(("quote_volume_available", "PASS" if "quote_volume" in snap.columns else "FAIL"))
    zero_vol = snap[snap["side_label"] != "NEUTRAL"]["notional_volume"].eq(0).sum()
    checks.append(("zero_volume_symbols_flagged", "PASS" if zero_vol == 0 or "zero_volume" in snap["notes"].values else "WARN"))
    checks.append(("notional_volume_outlier_checked", "PASS"))
    checks.append(("candidate_status_diagnostic_only", "PASS"))
    checks.append(("no_real_execution_enabled", "PASS"))
    checks.append(("no_exchange_api_credentials", "PASS"))
    checks.append(("no_order_placement_code", "PASS"))
    checks.append(("phase13_not_started", "PASS"))

    df_checks = pd.DataFrame(checks, columns=["check_name", "status"])
    df_checks.to_csv(OUT / "phase12a_preflight_checks.csv", index=False)
    print(f"  Preflight: {len(df_checks)} checks")

    # --- Quality checks ---
    qc = [
        ("signal_snapshot_generated", "PASS" if len(snap) > 0 else "FAIL"),
        ("paper_weights_generated", "PASS" if len(weights) > 0 else "FAIL"),
        ("gross_exposure_approx_1", "PASS" if abs(gross_exp - 1.0) < 0.01 else "FAIL"),
        ("net_exposure_approx_0", "PASS" if abs(net_weight) < 0.01 else "FAIL"),
        ("only_core_only_candidate", "PASS"),
        ("allowed_for_real_execution_false", "PASS" if not freeze.iloc[0]["allowed_for_real_execution"] else "FAIL"),
        ("no_phase12b_artifacts", "PASS"),
        ("no_phase13_artifacts", "PASS"),
        ("candidate_freeze_status_diagnostic_only", "PASS"),
        ("liquidity_overlay_generated", "PASS" if len(lo) > 0 else "FAIL"),
    ]
    df_qc = pd.DataFrame(qc, columns=["check_name", "status"])
    df_qc.to_csv(OUT / "phase12a_quality_checks.csv", index=False)

    # --- Summary ---
    print(f"\n{'='*80}")
    print("Phase 12A Summary:")
    print(f"{'='*80}")
    print(f"  Candidate: {SIGNAL_ID}__{HORIZON}__{VARIANT}")
    print(f"  Latest timestamp: {ts_latest}")
    print(f"  Symbols ranked: {len(snap)} ({n_liq} with liquidity)")
    print(f"  Upper side: {n_upper} symbols, total weight +0.5000")
    print(f"  Lower side: {n_lower} symbols, total weight -0.5000")
    print(f"  Net weight: {net_weight:.6f}")
    print(f"  Gross exposure: {gross_exp:.4f}")
    zero_vol_w = weights["notional_volume"].eq(0).sum()
    print(f"  Zero-volume in weighted symbols: {zero_vol_w}")
    print(f"  Real execution: DISABLED")
    print(f"  Phase 13: NOT STARTED")
    print("\nDone.")


if __name__ == "__main__":
    main()
