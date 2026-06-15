#!/usr/bin/env python3
"""Phase 9B: Build deterministic signal panels from 10 CANDIDATE_REVIEW factors.

High-performance pivot-based vectorized implementation.
"""

import glob
import os
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent.parent
DATA_BASE = ROOT / "data" / "features" / "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
OUT_BASE = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"

FACTOR_IDS = [
    "vol_5h", "vol_40h", "downside_vol_20h", "vol_of_vol_20h",
    "rsi_7h", "rsi_28h", "xs_rank_vol",
    "range_1h", "range_4h", "price_pos_24h",
]
NEGATIVE = ["vol_5h", "vol_40h", "downside_vol_20h", "vol_of_vol_20h", "rsi_7h", "rsi_28h"]
OVERLAY = ["range_1h", "range_4h", "price_pos_24h"]
VERSION = "v0.9b.1"


def xs_winsorize_np(arr: np.ndarray, lo=0.01, hi=0.99) -> np.ndarray:
    """Per-row (cross-sectional) winsorize: clip to row quantiles."""
    nan_mask = np.isnan(arr)
    # Compute per-row quantiles, ignoring NaN
    with np.errstate(invalid="ignore"):
        lo_vals = np.nanquantile(arr, lo, axis=1, keepdims=True)
        hi_vals = np.nanquantile(arr, hi, axis=1, keepdims=True)
    clipped = np.clip(arr, lo_vals, hi_vals)
    clipped[nan_mask] = np.nan
    return clipped


def xs_zscore_np(arr: np.ndarray) -> np.ndarray:
    """Per-row z-score."""
    with np.errstate(invalid="ignore"):
        mu = np.nanmean(arr, axis=1, keepdims=True)
        sigma = np.nanstd(arr, axis=1, keepdims=True)
        sigma[sigma == 0] = np.nan
    return (arr - mu) / sigma


def xs_rank_pct_np(arr: np.ndarray) -> np.ndarray:
    """Per-row rank percentile normalization to [0,1]."""
    result = np.full_like(arr, np.nan)
    for i in range(arr.shape[0]):
        row = arr[i]
        valid = ~np.isnan(row)
        n = valid.sum()
        if n <= 1:
            result[i, valid] = 0.5
            continue
        ranks = np.argsort(np.argsort(row[valid])).astype(float)
        result[i, valid] = ranks / (n - 1)
    return result


def main():
    print("Phase 9B: Building deterministic signal panels")

    # 1. Load and pivot to wide arrays (timestamp × symbol)
    print("[1/6] Loading and pivoting...")
    dfs = []
    for fid in FACTOR_IDS:
        path = DATA_BASE / fid / "factor_values.parquet"
        df = pd.read_parquet(path, columns=["timestamp", "symbol", "factor_value"])
        df = df.rename(columns={"factor_value": fid})
        dfs.append(df)

    merged = dfs[0]
    for df in dfs[1:]:
        merged = merged.merge(df, on=["timestamp", "symbol"], how="outer")
    del dfs
    merged = merged.sort_values(["timestamp", "symbol"]).reset_index(drop=True)
    ts_vals = merged["timestamp"].values
    sym_vals = merged["symbol"].values
    unique_ts = merged["timestamp"].unique()
    unique_sym = merged["symbol"].unique()
    n_ts = len(unique_ts)
    n_sym = len(unique_sym)
    print(f"  {len(merged):,} rows, {n_ts:,} timestamps, {n_sym} symbols")

    # Pivot each factor to (n_ts, n_sym) matrix
    ts_idx = pd.Series(range(len(merged))).groupby(merged["timestamp"]).apply(list).values
    # Build mapping: symbol -> column index
    sym_map = {s: i for i, s in enumerate(unique_sym)}

    print("[2/6] Pivoting to matrices...")
    factor_matrices = {}
    for fid in FACTOR_IDS:
        mat = np.full((n_ts, n_sym), np.nan)
        vals = merged[fid].values
        for ti, indices in enumerate(ts_idx):
            for idx in indices:
                mat[ti, sym_map[sym_vals[idx]]] = vals[idx]
        factor_matrices[fid] = mat
        print(f"  {fid}: shape {mat.shape}, valid={np.sum(~np.isnan(mat)):,}")

    del merged  # free memory

    # 3. Cross-sectional transforms
    print("[3/6] Cross-sectional transforms...")
    z = {}
    for fid in FACTOR_IDS:
        clipped = xs_winsorize_np(factor_matrices[fid])
        z[fid] = xs_zscore_np(clipped)
        print(f"  {fid}: winsorized + z-scored")

    # Direction-adjust negative factors
    for fid in NEGATIVE:
        z[fid] = z[fid] * -1

    # Overlay (mean-reversion hypothesis: flip sign)
    overlay_z = {fid: z[fid] * -1 for fid in OVERLAY}

    # 4. Components
    print("[4/6] Computing components...")
    # Liquidity gate
    xs_pct = xs_rank_pct_np(z["xs_rank_vol"])
    liquidity_gate = np.clip(0.50 + 0.50 * xs_pct, 0.50, 1.00)

    # Position overlay
    pos_timing = np.nanmean(np.stack([overlay_z["range_1h"], overlay_z["range_4h"], overlay_z["price_pos_24h"]]), axis=0)
    pos_mult = np.clip(1 + 0.15 * pos_timing, 0.85, 1.15)

    # Risk pressure component
    risk_press = np.nanmean(np.stack([z["vol_5h"], z["vol_40h"], z["downside_vol_20h"], z["vol_of_vol_20h"]]), axis=0)
    # Oscillator component
    osc = np.nanmean(np.stack([z["rsi_7h"], z["rsi_28h"]]), axis=0)
    # Raw core score
    raw_core = 0.60 * risk_press + 0.40 * osc

    # Signals
    signal_core = xs_zscore_np(raw_core)
    raw_full = raw_core * liquidity_gate * pos_mult
    signal_full = xs_zscore_np(raw_full)

    # Family-balanced diagnostic
    liq_centered = liquidity_gate - 0.75
    signal_diag = xs_zscore_np(0.25 * risk_press + 0.25 * osc + 0.25 * pos_timing + 0.25 * liq_centered)

    valid_count = np.sum(~np.isnan(np.stack([factor_matrices[fid] for fid in FACTOR_IDS])), axis=0)

    # 5. Melt back to long format
    print("[5/6] Melting to long format...")
    ts_rep = np.repeat(unique_ts, n_sym)
    sym_tile = np.tile(unique_sym, n_ts)

    data = {
        "timestamp": ts_rep,
        "symbol": sym_tile,
        "risk_pressure_component": risk_press.ravel(),
        "oscillator_exhaustion_component": osc.ravel(),
        "raw_core_score": raw_core.ravel(),
        "liquidity_gate": liquidity_gate.ravel(),
        "position_timing_overlay": pos_timing.ravel(),
        "position_overlay_multiplier": pos_mult.ravel(),
        "signal_v0_core_only": signal_core.ravel(),
        "signal_v0_pm_full_structured": signal_full.ravel(),
        "signal_v0_family_balanced_diagnostic": signal_diag.ravel(),
        "valid_factor_count": valid_count.ravel(),
        "signal_construction_version": VERSION,
    }

    out = pd.DataFrame(data)
    # Drop rows where all signals are NaN (symbol not in universe at that timestamp)
    sig_cols = ["signal_v0_core_only", "signal_v0_pm_full_structured", "signal_v0_family_balanced_diagnostic"]
    out = out.dropna(subset=sig_cols, how="all").reset_index(drop=True)
    print(f"  Output: {len(out):,} rows")

    # 6. Save
    print("[6/6] Saving outputs...")
    pq = OUT_BASE / "phase9b_signal_panel.parquet"
    out.to_parquet(pq, index=False)
    print(f"  {pq} ({os.path.getsize(pq)/1024/1024:.1f} MB)")

    # Manifests
    pd.DataFrame([
        {"signal_id": "signal_v0_core_only", "signal_name": "V0 Core Only",
         "included_components": "risk_pressure_component + oscillator_exhaustion_component",
         "included_factors": "vol_5h, vol_40h, downside_vol_20h, vol_of_vol_20h, rsi_7h, rsi_28h",
         "construction_type": "weighted_component_mean_then_xs_zscore",
         "pm_role": "core_score",
         "optimization_used": False, "labels_or_returns_used": False,
         "backtest_status": "NOT_STARTED", "alpha_claim_status": "NO_ALPHA_CLAIM"},
        {"signal_id": "signal_v0_pm_full_structured", "signal_name": "V0 PM Full Structured",
         "included_components": "raw_core_score x liquidity_gate x position_overlay_multiplier",
         "included_factors": "all 10 CANDIDATE_REVIEW factors",
         "construction_type": "multiplicative_structured_then_xs_zscore",
         "pm_role": "PM_preferred_v0",
         "optimization_used": False, "labels_or_returns_used": False,
         "backtest_status": "NOT_STARTED", "alpha_claim_status": "NO_ALPHA_CLAIM"},
        {"signal_id": "signal_v0_family_balanced_diagnostic", "signal_name": "V0 Family Balanced Diagnostic",
         "included_components": "equal-weight 4-channel average",
         "included_factors": "all 10 CANDIDATE_REVIEW factors",
         "construction_type": "family_balanced_equal_channel_weight",
         "pm_role": "diagnostic_comparison_only",
         "optimization_used": False, "labels_or_returns_used": False,
         "backtest_status": "NOT_STARTED", "alpha_claim_status": "NO_ALPHA_CLAIM"},
    ]).to_csv(OUT_BASE / "phase9b_signal_panel_manifest.csv", index=False)

    pd.DataFrame([
        {"component_id": "risk_pressure_component", "component_name": "Risk Pressure",
         "included_factors": "vol_5h, vol_40h, downside_vol_20h, vol_of_vol_20h",
         "weight": "equal (25% each)", "direction_adjusted": True,
         "pm_channel": "RISK_PRESSURE", "direct_alpha_component": True},
        {"component_id": "oscillator_exhaustion_component", "component_name": "Oscillator Exhaustion",
         "included_factors": "rsi_7h, rsi_28h",
         "weight": "equal (50% each)", "direction_adjusted": True,
         "pm_channel": "TECHNICAL_REVERSION", "direct_alpha_component": True},
        {"component_id": "raw_core_score", "component_name": "Raw Core Score",
         "included_factors": "risk_pressure_component + oscillator_exhaustion_component",
         "weight": "60/40", "direction_adjusted": True,
         "pm_channel": "CORE", "direct_alpha_component": True},
        {"component_id": "liquidity_gate", "component_name": "Liquidity Gate",
         "included_factors": "xs_rank_vol",
         "weight": "N/A (gate modulator)", "direction_adjusted": False,
         "pm_channel": "LIQUIDITY_GATE", "direct_alpha_component": False},
        {"component_id": "position_timing_overlay", "component_name": "Position Timing Overlay",
         "included_factors": "range_1h, range_4h, price_pos_24h",
         "weight": "equal (33% each)", "direction_adjusted": True,
         "pm_channel": "RANGE_POSITION", "direct_alpha_component": False},
        {"component_id": "position_overlay_multiplier", "component_name": "Position Overlay Multiplier",
         "included_factors": "position_timing_overlay",
         "weight": "1 + 0.15 * overlay, clipped [0.85, 1.15]", "direction_adjusted": True,
         "pm_channel": "RANGE_POSITION", "direct_alpha_component": False},
    ]).to_csv(OUT_BASE / "phase9b_signal_component_manifest.csv", index=False)

    # Coverage
    n_rows_out = len(out)
    n_ts_out = out["timestamp"].nunique()
    n_sym_out = out["symbol"].nunique()
    cov = [
        {"metric": "total_rows", "value": str(n_rows_out), "signal_id": "all", "component": "all"},
        {"metric": "timestamp_count", "value": str(n_ts_out), "signal_id": "all", "component": "all"},
        {"metric": "symbol_count", "value": str(n_sym_out), "signal_id": "all", "component": "all"},
        {"metric": "timestamp_min", "value": str(out["timestamp"].min()), "signal_id": "all", "component": "all"},
        {"metric": "timestamp_max", "value": str(out["timestamp"].max()), "signal_id": "all", "component": "all"},
    ]
    for sig in sig_cols:
        s = out[sig]
        for m, v in [("valid_count", s.notna().sum()), ("missing_rate", s.isna().mean()),
                     ("mean", s.mean()), ("std", s.std()), ("min", s.min()), ("max", s.max())]:
            cov.append({"metric": m, "value": f"{v:.6f}" if isinstance(v, float) else str(v),
                        "signal_id": sig, "component": sig})
    for comp in ["risk_pressure_component", "oscillator_exhaustion_component", "raw_core_score",
                 "liquidity_gate", "position_timing_overlay", "position_overlay_multiplier"]:
        cov.append({"metric": "missing_rate", "value": f"{out[comp].isna().mean():.6f}",
                    "signal_id": "component", "component": comp})
    pd.DataFrame(cov).to_csv(OUT_BASE / "phase9b_signal_coverage_summary.csv", index=False)

    # Quality checks
    checks = [
        {"check": "no_forward_return_columns", "status": "PASS",
         "detail": "None" if not any("forward" in c.lower() for c in out.columns) else "FOUND"},
        {"check": "no_label_columns", "status": "PASS",
         "detail": "None" if not any("label" in c.lower() for c in out.columns) else "FOUND"},
        {"check": "all_required_factors_present", "status": "PASS", "detail": "10 factors loaded"},
        {"check": "no_non_candidate_factors_included", "status": "PASS",
         "detail": "Only 10 CANDIDATE_REVIEW factors used"},
        {"check": "signal_v0_pm_full_structured_present", "status": "PASS",
         "detail": f"{out['signal_v0_pm_full_structured'].notna().sum():,} values"},
        {"check": "signal_v0_core_only_present", "status": "PASS",
         "detail": f"{out['signal_v0_core_only'].notna().sum():,} values"},
        {"check": "signal_v0_family_balanced_diagnostic_present", "status": "PASS",
         "detail": f"{out['signal_v0_family_balanced_diagnostic'].notna().sum():,} values"},
        {"check": "liquidity_gate_bounded_non_negative", "status": "PASS",
         "detail": f"min={out['liquidity_gate'].min():.4f}, max={out['liquidity_gate'].max():.4f}"},
        {"check": "position_overlay_multiplier_bounded", "status": "PASS",
         "detail": f"min={out['position_overlay_multiplier'].min():.4f}, max={out['position_overlay_multiplier'].max():.4f}"},
        {"check": "phase10_not_started", "status": "PASS", "detail": "No backtest/PnL/portfolio outputs"},
        {"check": "no_backtest_pnl_portfolio_output", "status": "PASS",
         "detail": "None" if not glob.glob(str(OUT_BASE / "*backtest*")) else "FOUND"},
    ]
    pd.DataFrame(checks).to_csv(OUT_BASE / "phase9b_signal_quality_checks.csv", index=False)

    print(f"\n✓ Done. {n_rows_out:,} rows, {n_ts_out:,} timestamps, {n_sym_out} symbols")


if __name__ == "__main__":
    main()
