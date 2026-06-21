#!/usr/bin/env python3
"""Signal Evaluation Parity Harness — Phase 12D-H2-T.

Uses the PUBLIC signal_evaluation API with legacy_phase10a mode for spread.
Tests both standard and legacy spread modes.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd
import numpy as np
from momentum.signal_evaluation import (
    select_forward_return,
    compute_rank_ic,
    summarize_rank_ic,
    compute_quantile_spread,
    summarize_quantile_spread,
    check_rankic_spread_consistency,
)

RUN_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"
SIGNAL_PANEL = RUN_DIR / "phase9b_signal_panel.parquet"
OLD_LABEL_FILE = ROOT / "data" / "features" / "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1" / "labels.parquet"
LABEL_FILE = ROOT / "data" / "features" / "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1" / "labels.parquet"
OLD_RANKIC = RUN_DIR / "phase10a_signal_rankic_summary.csv"
OLD_SPREAD = RUN_DIR / "phase10a_signal_quantile_spread_summary.csv"

SIGNAL_NAMES = [
    "signal_v0_core_only",
    "signal_v0_pm_full_structured",
    "signal_v0_family_balanced_diagnostic",
]
HORIZONS = ["1h", "4h", "24h", "72h"]

# RankIC: strict tolerance
RANKIC_TOLERANCE = {
    "mean_rank_ic": 1e-9,
    "t_stat": 1e-6,
    "n_periods": 0,
}
ROUNDING_TOLERANCE = {
    "mean_rank_ic": 0.5e-6,
    "t_stat": 0.5e-4,
}

# Spread: legacy mode should be EXACT or PASS_ROUNDED_REFERENCE
SPREAD_TOLERANCE = {
    "mean_spread": 0.5e-6,  # 6 decimal places rounding
    "positive_fraction": 1e-2,
    "n_periods": 0,  # exact
}


def check_rankic_parity(new_val, old_val, strict_tol, rounding_tol):
    """RankIC parity: EXACT / PASS_ROUNDED_REFERENCE / NEEDS_INVESTIGATION."""
    if new_val is None or (isinstance(new_val, float) and np.isnan(new_val)):
        return "MISSING_NEW", 0
    if old_val is None or (isinstance(old_val, float) and np.isnan(old_val)):
        return "MISSING_OLD", 0
    diff = abs(float(new_val) - float(old_val))
    if strict_tol == 0:
        if int(new_val) == int(old_val):
            return "EXACT", 0
        return "NEEDS_INVESTIGATION", diff
    if diff <= strict_tol:
        return "EXACT", diff
    if diff <= rounding_tol:
        return "PASS_ROUNDED_REFERENCE", diff
    return "NEEDS_INVESTIGATION", diff


def check_spread_parity(new_val, old_val, tol, new_dir, old_dir, rounding_tol=None):
    """Spread parity: EXACT / PASS_ROUNDED_REFERENCE / BEHAVIORAL / NEEDS_INVESTIGATION."""
    if rounding_tol is None:
        rounding_tol = 0.5e-6  # default: 6 decimal places
    if new_val is None or (isinstance(new_val, float) and np.isnan(new_val)):
        return "MISSING_NEW", "new_value_missing"
    if old_val is None or (isinstance(old_val, float) and np.isnan(old_val)):
        return "MISSING_OLD", "old_value_missing"
    diff = abs(float(new_val) - float(old_val))
    if diff <= 1e-9:
        return "EXACT", "exact_match"
    if diff <= rounding_tol:
        return "PASS_ROUNDED_REFERENCE", f"old_csv_rounding_diff={diff:.2e}"
    if diff <= tol and new_dir == old_dir:
        return "BEHAVIORAL", f"same_direction_diff={diff:.2e}"
    if new_dir != old_dir:
        return "NEEDS_INVESTIGATION", f"direction_mismatch_new={new_dir}_old={old_dir}"
    return "NEEDS_INVESTIGATION", f"diff={diff:.2e}_exceeds_tolerance={tol:.0e}"


def determine_h3_gate(ric_levels, sp_legacy_levels):
    """
    H3 gate logic:
    - OPEN_FULL_WRAPPER: all ric EXACT/PASS_ROUNDED + all sp legacy EXACT/PASS_ROUNDED
    - OPEN_STANDARD_V2_ONLY: ric pass + sp legacy NOT EXACT/PASS_ROUNDED
    - BLOCKED: any NEEDS_INVESTIGATION or MISSING
    """
    ric_inv = any(l in ("NEEDS_INVESTIGATION", "MISSING") for l in ric_levels)
    sp_inv = any(l in ("NEEDS_INVESTIGATION", "MISSING") for l in sp_legacy_levels)
    sp_exact = all(l in ("EXACT", "PASS_ROUNDED_REFERENCE") for l in sp_legacy_levels)
    sp_behavioral = all(l in ("EXACT", "PASS_ROUNDED_REFERENCE", "BEHAVIORAL") for l in sp_legacy_levels)

    if ric_inv or sp_inv:
        return "BLOCKED"
    if sp_exact:
        return "OPEN_FULL_WRAPPER"
    if sp_behavioral:
        return "OPEN_STANDARD_V2_ONLY"
    return "BLOCKED"


def main():
    missing = []
    for name, path in [
        ("signal_panel", SIGNAL_PANEL),
        ("old_labels", OLD_LABEL_FILE),
        ("old_rankic", OLD_RANKIC),
        ("old_spread", OLD_SPREAD),
    ]:
        if not path.exists():
            missing.append(name)

    if missing:
        print(f"MISSING_INPUT: {missing}")
        summary = pd.DataFrame([{
            "check_group": "input_check", "total_checks": 1,
            "exact_count": 0, "rounded_reference_count": 0,
            "behavioral_count": 0, "investigate_count": 0,
            "missing_count": len(missing), "h3_gate_status": "BLOCKED",
            "overall_status": "BLOCKED",
        }])
        summary.to_csv(RUN_DIR / "phase12d_h2_t_signal_eval_parity_summary.csv", index=False)
        return

    # Load data
    print("Loading signal panel...")
    sp = pd.read_parquet(SIGNAL_PANEL, columns=["timestamp", "symbol"] + SIGNAL_NAMES)
    print(f"  Shape: {sp.shape}")

    print("Loading old labels...")
    old_labels = pd.read_parquet(OLD_LABEL_FILE)
    print(f"  Shape: {old_labels.shape}")

    print("Loading current labels...")
    cur_labels = pd.read_parquet(LABEL_FILE)
    print(f"  Shape: {cur_labels.shape}")

    old_ric = pd.read_csv(OLD_RANKIC)
    old_spread_df = pd.read_csv(OLD_SPREAD)

    # Filter signal panel to old label symbols
    old_label_symbols = set(old_labels["symbol"].unique())
    sp_old = sp[sp["symbol"].isin(old_label_symbols)].copy()
    print(f"SP filtered for old labels: {sp_old.shape}")

    # Prepare label dicts
    old_wide_map = {hz: f"ret_fwd_{hz}" for hz in HORIZONS}
    old_label_dict = {}
    for hz in HORIZONS:
        old_label_dict[hz] = select_forward_return(old_labels, hz, wide_column_map=old_wide_map)

    cur_label_dict = {}
    for hz in HORIZONS:
        cur_label_dict[hz] = select_forward_return(cur_labels, hz)

    # --- RankIC parity ---
    ric_rows = []
    for sig in SIGNAL_NAMES:
        for hz in HORIZONS:
            print(f"  RankIC: {sig} × {hz}", end=" ", flush=True)

            sig_df = sp_old[["timestamp", "symbol", sig]].rename(
                columns={sig: "signal_value"}
            ).dropna(subset=["signal_value"])
            sig_df["signal_name"] = sig

            label_h = old_label_dict[hz]
            ric_ts = compute_rank_ic(sig_df, label_h)
            ric_summary = summarize_rank_ic(ric_ts)

            new_mean = ric_summary["mean_rank_ic"]
            new_t = ric_summary["t_stat"]
            new_n = ric_summary["n_periods"]

            old_row = old_ric[(old_ric["signal_id"] == sig) & (old_ric["horizon"] == hz)]
            if old_row.empty:
                old_mean, old_t, old_n = np.nan, np.nan, np.nan
            else:
                old_mean = old_row["mean_rankic"].iloc[0]
                old_t = old_row["t_stat"].iloc[0]
                old_n = old_row["n_timestamps"].iloc[0]

            p_mean, diff_mean = check_rankic_parity(
                new_mean, old_mean, RANKIC_TOLERANCE["mean_rank_ic"], ROUNDING_TOLERANCE["mean_rank_ic"])
            p_t, diff_t = check_rankic_parity(
                new_t, old_t, RANKIC_TOLERANCE["t_stat"], ROUNDING_TOLERANCE["t_stat"])
            p_n, _ = check_rankic_parity(new_n, old_n, RANKIC_TOLERANCE["n_periods"], 0)

            levels = [p_mean, p_t, p_n]
            if any(l.startswith("MISSING") for l in levels):
                status = "MISSING"; level = "MISSING"
            elif all(l in ("EXACT", "PASS_ROUNDED_REFERENCE") for l in levels):
                status = "PASS"
                level = "PASS_ROUNDED_REFERENCE" if any(l == "PASS_ROUNDED_REFERENCE" for l in levels) else "EXACT"
            else:
                status = "NEEDS_INVESTIGATION"; level = "INVESTIGATE"

            print(f"new={new_mean:.9f} old={old_mean:.9f} diff={diff_mean:.2e} [{level}]")

            ric_rows.append({
                "signal_name": sig, "horizon": hz,
                "new_mean_rank_ic": new_mean, "old_mean_rank_ic": old_mean,
                "diff_mean_rank_ic": diff_mean,
                "new_t_stat": new_t, "old_t_stat": old_t,
                "diff_t_stat": diff_t,
                "new_n_periods": int(new_n),
                "old_n_periods": int(old_n) if not np.isnan(old_n) else np.nan,
                "parity_mean": p_mean, "parity_tstat": p_t, "parity_nperiods": p_n,
                "parity_status": status,
                "parity_level": level,
                "reference_precision_digits": 6,
                "rounding_tolerance": ROUNDING_TOLERANCE["mean_rank_ic"],
            })

    ric_df = pd.DataFrame(ric_rows)
    ric_df.to_csv(RUN_DIR / "phase12d_h2_t_signal_eval_parity_rankic.csv", index=False)

    # --- Quantile Spread parity: LEGACY mode ---
    print("\n--- Spread Parity (legacy_phase10a mode) ---")
    spread_legacy_rows = []
    for sig in SIGNAL_NAMES:
        for hz in HORIZONS:
            print(f"  Spread(legacy): {sig} × {hz}", end=" ", flush=True)

            sig_df = sp_old[["timestamp", "symbol", sig]].rename(
                columns={sig: "signal_value"}
            ).dropna(subset=["signal_value"])
            sig_df["signal_name"] = sig

            label_h = old_label_dict[hz]
            spread_ts = compute_quantile_spread(sig_df, label_h, mode="legacy_phase10a")
            spread_summary = summarize_quantile_spread(spread_ts)

            new_mean_s = spread_summary["mean_spread"]
            new_hit = spread_summary["positive_fraction"]
            new_n = spread_summary["n_periods"]

            old_row = old_spread_df[(old_spread_df["signal_id"] == sig) & (old_spread_df["horizon"] == hz)]
            if old_row.empty:
                old_mean_s, old_hit, old_n = np.nan, np.nan, np.nan
            else:
                old_mean_s = old_row["mean_spread"].iloc[0]
                old_hit = old_row["hit_rate"].iloc[0]
                old_n = old_row["n_timestamps"].iloc[0]

            new_dir = "negative" if new_mean_s < 0 else "positive"
            old_dir = "negative" if (not np.isnan(old_mean_s) and old_mean_s < 0) else "positive"

            p_mean, reason_mean = check_spread_parity(
                new_mean_s, old_mean_s, SPREAD_TOLERANCE["mean_spread"], new_dir, old_dir,
                rounding_tol=0.5e-6)  # old CSV mean_spread 6dp
            p_hit, reason_hit = check_spread_parity(
                new_hit, old_hit, SPREAD_TOLERANCE["positive_fraction"], new_dir, old_dir,
                rounding_tol=0.5e-4)  # old CSV hit_rate 4dp
            p_n, _ = check_rankic_parity(new_n, old_n, SPREAD_TOLERANCE["n_periods"], 0)

            levels = [p_mean, p_hit, p_n]
            if any(l.startswith("MISSING") for l in levels):
                status = "MISSING"; level = "MISSING"; reason = "missing_data"
            elif all(l == "EXACT" for l in levels):
                status = "PASS"; level = "EXACT"; reason = "exact_match"
            elif all(l in ("EXACT", "PASS_ROUNDED_REFERENCE") for l in levels):
                status = "PASS"; level = "PASS_ROUNDED_REFERENCE"
                reason = f"mean:{reason_mean};hit:{reason_hit}"
            elif all(l in ("EXACT", "PASS_ROUNDED_REFERENCE", "BEHAVIORAL") for l in levels):
                status = "PASS"; level = "BEHAVIORAL"
                reason = f"mean:{reason_mean};hit:{reason_hit}"
            else:
                status = "NEEDS_INVESTIGATION"; level = "INVESTIGATE"
                reason = f"mean:{reason_mean};hit:{reason_hit}"

            diff_s = new_mean_s - old_mean_s if not np.isnan(old_mean_s) else np.nan
            print(f"new={new_mean_s:.6f} old={old_mean_s:.6f} diff={diff_s:.2e} [{level}]")

            spread_legacy_rows.append({
                "signal_name": sig, "horizon": hz,
                "mode": "legacy_phase10a",
                "new_mean_spread": new_mean_s, "old_mean_spread": old_mean_s,
                "diff_mean_spread": diff_s,
                "new_positive_fraction": new_hit, "old_positive_fraction": old_hit,
                "diff_positive_fraction": new_hit - old_hit if not np.isnan(old_hit) else np.nan,
                "new_n_periods": int(new_n),
                "old_n_periods": int(old_n) if not np.isnan(old_n) else np.nan,
                "parity_mean": p_mean, "parity_hit": p_hit, "parity_nperiods": p_n,
                "parity_status": status,
                "parity_level": level,
                "difference_reason": reason,
            })

    spread_legacy_df = pd.DataFrame(spread_legacy_rows)
    spread_legacy_df.to_csv(RUN_DIR / "phase12d_h2_t_signal_eval_parity_spread_legacy.csv", index=False)

    # --- Quantile Spread parity: STANDARD mode (for reference) ---
    print("\n--- Spread Parity (standard qcut mode, for reference) ---")
    spread_standard_rows = []
    for sig in SIGNAL_NAMES:
        for hz in HORIZONS:
            print(f"  Spread(standard): {sig} × {hz}", end=" ", flush=True)

            sig_df = sp_old[["timestamp", "symbol", sig]].rename(
                columns={sig: "signal_value"}
            ).dropna(subset=["signal_value"])
            sig_df["signal_name"] = sig

            label_h = old_label_dict[hz]
            spread_ts = compute_quantile_spread(sig_df, label_h, mode="standard")
            spread_summary = summarize_quantile_spread(spread_ts)

            new_mean_s = spread_summary["mean_spread"]
            old_row = old_spread_df[(old_spread_df["signal_id"] == sig) & (old_spread_df["horizon"] == hz)]
            old_mean_s = old_row["mean_spread"].iloc[0] if not old_row.empty else np.nan

            diff_s = new_mean_s - old_mean_s if not np.isnan(old_mean_s) else np.nan
            print(f"new={new_mean_s:.6f} old={old_mean_s:.6f} diff={diff_s:.2e}")

            spread_standard_rows.append({
                "signal_name": sig, "horizon": hz,
                "mode": "standard",
                "new_mean_spread": new_mean_s, "old_mean_spread": old_mean_s,
                "diff_mean_spread": diff_s,
            })

    spread_standard_df = pd.DataFrame(spread_standard_rows)
    spread_standard_df.to_csv(RUN_DIR / "phase12d_h2_t_signal_eval_parity_spread_standard.csv", index=False)

    # --- Consistency check ---
    print("\nConsistency check (current labels, standard mode):")
    cur_label_symbols = set(cur_labels["symbol"].unique())
    sp_cur = sp[sp["symbol"].isin(cur_label_symbols)].copy()
    for sig in SIGNAL_NAMES:
        sig_df = sp_cur[["timestamp", "symbol", sig]].rename(
            columns={sig: "signal_value"}
        ).dropna(subset=["signal_value"])
        sig_df["signal_name"] = sig
        label_h = cur_label_dict["1h"]
        ric_ts = compute_rank_ic(sig_df, label_h)
        ric_s = summarize_rank_ic(ric_ts)
        spread_ts = compute_quantile_spread(sig_df, label_h, mode="standard")
        sp_s = summarize_quantile_spread(spread_ts)
        result = check_rankic_spread_consistency(ric_s, sp_s)
        print(f"  {sig} 1h: {result} (IC={ric_s['mean_rank_ic']:.6f}, spread={sp_s['mean_spread']:.6f})")

    # --- Summary with corrected gate logic ---
    ric_exact = (ric_df["parity_level"] == "EXACT").sum()
    ric_rounded = (ric_df["parity_level"] == "PASS_ROUNDED_REFERENCE").sum()
    ric_investigate = (ric_df["parity_level"] == "INVESTIGATE").sum()
    ric_missing = ric_df["parity_level"].isin(["MISSING"]).sum()

    sp_legacy_exact = (spread_legacy_df["parity_level"] == "EXACT").sum()
    sp_legacy_rounded = (spread_legacy_df["parity_level"] == "PASS_ROUNDED_REFERENCE").sum()
    sp_legacy_behavioral = (spread_legacy_df["parity_level"] == "BEHAVIORAL").sum()
    sp_legacy_investigate = (spread_legacy_df["parity_level"] == "INVESTIGATE").sum()
    sp_legacy_missing = spread_legacy_df["parity_level"].isin(["MISSING"]).sum()

    ric_levels = ric_df["parity_level"].tolist()
    sp_legacy_levels = spread_legacy_df["parity_level"].tolist()
    h3_gate = determine_h3_gate(ric_levels, sp_legacy_levels)

    if ric_missing + sp_legacy_missing > 0:
        overall = "BLOCKED"
    elif ric_investigate + sp_legacy_investigate > 0:
        overall = "NEEDS_INVESTIGATION"
    else:
        overall = "PARTIAL_PASS"

    summary = pd.DataFrame([
        {"check_group": "rankic_parity", "total_checks": len(ric_df),
         "exact_count": ric_exact, "rounded_reference_count": ric_rounded,
         "behavioral_count": 0, "investigate_count": ric_investigate,
         "missing_count": ric_missing, "h3_gate_status": h3_gate,
         "overall_status": "PASS" if ric_exact + ric_rounded == len(ric_df) else "NEEDS_INVESTIGATION"},
        {"check_group": "spread_legacy_parity", "total_checks": len(spread_legacy_df),
         "exact_count": sp_legacy_exact, "rounded_reference_count": sp_legacy_rounded,
         "behavioral_count": sp_legacy_behavioral, "investigate_count": sp_legacy_investigate,
         "missing_count": sp_legacy_missing, "h3_gate_status": h3_gate,
         "overall_status": "PASS" if sp_legacy_exact + sp_legacy_rounded == len(spread_legacy_df) else "NEEDS_INVESTIGATION"},
        {"check_group": "overall", "total_checks": len(ric_df) + len(spread_legacy_df),
         "exact_count": ric_exact + sp_legacy_exact,
         "rounded_reference_count": ric_rounded + sp_legacy_rounded,
         "behavioral_count": sp_legacy_behavioral,
         "investigate_count": ric_investigate + sp_legacy_investigate,
         "missing_count": ric_missing + sp_legacy_missing,
         "h3_gate_status": h3_gate,
         "overall_status": overall},
    ])
    summary.to_csv(RUN_DIR / "phase12d_h2_t_signal_eval_parity_summary.csv", index=False)

    print(f"\n{'='*60}")
    print(f"RankIC:       {ric_exact} EXACT / {ric_rounded} PASS_ROUNDED / {ric_investigate} INVESTIGATE / {ric_missing} MISSING")
    print(f"Spread(legacy): {sp_legacy_exact} EXACT / {sp_legacy_rounded} PASS_ROUNDED / {sp_legacy_behavioral} BEHAVIORAL / {sp_legacy_investigate} INVESTIGATE")
    print(f"H3 Gate:      {h3_gate}")
    print(f"Overall:      {overall}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
