#!/usr/bin/env python3
"""Signal Evaluation Parity Harness — Phase 12D-H2-R.

Uses the PUBLIC signal_evaluation API to verify parity with old Phase 10A outputs.
Does NOT use inline fast_rank_ic / fast_quantile_spread.
Does NOT modify old scripts, old outputs, signal panel, or labels.
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
OLD_LABEL_FILE = RUN_DIR / "alphalens_exports" / "crypto_top50_usdt_perp_1h_long_v1" / "wq101_alpha53" / "forward_returns_long.parquet"
LABEL_FILE = ROOT / "data" / "features" / "crypto_top50_usdt_perp_1h" / "labels.parquet"
OLD_RANKIC = RUN_DIR / "phase10a_signal_rankic_summary.csv"
OLD_SPREAD = RUN_DIR / "phase10a_signal_quantile_spread_summary.csv"

SIGNAL_NAMES = [
    "signal_v0_core_only",
    "signal_v0_pm_full_structured",
    "signal_v0_family_balanced_diagnostic",
]
HORIZONS = ["1h", "4h", "24h", "72h"]

# RankIC: strict parity (exact match expected)
RANKIC_TOLERANCE = {
    "mean_rank_ic": 1e-9,
    "t_stat": 1e-6,
    "n_periods": 0,  # exact
}

# Spread: behavioral compatibility (direction + order of magnitude)
SPREAD_TOLERANCE = {
    "mean_spread": 2e-3,      # bucket construction differs
    "positive_fraction": 1e-2, # bucket boundary differences
    "n_periods": 2,            # NaN filtering differs
}


def check_rankic_parity(new_val, old_val, tol):
    """Strict parity check for RankIC metrics."""
    if new_val is None or (isinstance(new_val, float) and np.isnan(new_val)):
        return "MISSING_NEW"
    if old_val is None or (isinstance(old_val, float) and np.isnan(old_val)):
        return "MISSING_OLD"
    if tol == 0:
        return "EXACT" if int(new_val) == int(old_val) else "NEEDS_INVESTIGATION"
    diff = abs(float(new_val) - float(old_val))
    if diff <= tol:
        return "EXACT"
    return "NEEDS_INVESTIGATION"


def check_spread_parity(new_val, old_val, tol, new_dir, old_dir):
    """Behavioral parity check for spread metrics."""
    if new_val is None or (isinstance(new_val, float) and np.isnan(new_val)):
        return "MISSING_NEW", "new_value_missing"
    if old_val is None or (isinstance(old_val, float) and np.isnan(old_val)):
        return "MISSING_OLD", "old_value_missing"
    diff = abs(float(new_val) - float(old_val))
    if diff <= 1e-9:
        return "EXACT", "exact_match"
    if diff <= tol and new_dir == old_dir:
        return "BEHAVIORAL", f"same_direction_diff={diff:.2e}"
    if new_dir != old_dir:
        return "NEEDS_INVESTIGATION", f"direction_mismatch_new={new_dir}_old={old_dir}"
    return "NEEDS_INVESTIGATION", f"diff={diff:.2e}_exceeds_tolerance={tol:.0e}"


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
            "check_group": "input_check", "total_checks": 1, "pass_count": 0,
            "fail_count": 0, "missing_count": len(missing), "overall_status": "BLOCKED",
        }])
        summary.to_csv(RUN_DIR / "phase12d_h2_r_signal_eval_parity_summary.csv", index=False)
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

    # Filter signal panel to old label symbols for parity
    old_label_symbols = set(old_labels["symbol"].unique())
    sp_old = sp[sp["symbol"].isin(old_label_symbols)].copy()
    print(f"SP filtered for old labels: {sp_old.shape}")

    # Prepare label dicts for each horizon
    # Old labels are wide format — use select_forward_return with wide_column_map
    old_wide_map = {hz: f"ret_fwd_{hz}" for hz in HORIZONS}
    old_label_dict = {}
    for hz in HORIZONS:
        old_label_dict[hz] = select_forward_return(old_labels, hz, wide_column_map=old_wide_map)

    cur_label_dict = {}
    for hz in HORIZONS:
        cur_label_dict[hz] = select_forward_return(cur_labels, hz)

    # --- RankIC parity (strict) ---
    ric_rows = []
    for sig in SIGNAL_NAMES:
        for hz in HORIZONS:
            print(f"  RankIC: {sig} × {hz}", end=" ", flush=True)

            # Prepare tidy signal_df
            sig_df = sp_old[["timestamp", "symbol", sig]].rename(
                columns={sig: "signal_value"}
            ).dropna(subset=["signal_value"])
            sig_df["signal_name"] = sig

            label_h = old_label_dict[hz]

            # PUBLIC API CALLS
            ric_ts = compute_rank_ic(sig_df, label_h)
            ric_summary = summarize_rank_ic(ric_ts)

            new_mean = ric_summary["mean_rank_ic"]
            new_t = ric_summary["t_stat"]
            new_n = ric_summary["n_periods"]

            # Old values
            old_row = old_ric[(old_ric["signal_id"] == sig) & (old_ric["horizon"] == hz)]
            if old_row.empty:
                old_mean, old_t, old_n = np.nan, np.nan, np.nan
            else:
                old_mean = old_row["mean_rankic"].iloc[0]
                old_t = old_row["t_stat"].iloc[0]
                old_n = old_row["n_timestamps"].iloc[0]

            p_mean = check_rankic_parity(new_mean, old_mean, RANKIC_TOLERANCE["mean_rank_ic"])
            p_t = check_rankic_parity(new_t, old_t, RANKIC_TOLERANCE["t_stat"])
            p_n = check_rankic_parity(new_n, old_n, RANKIC_TOLERANCE["n_periods"])

            # Overall: EXACT if all EXACT, else NEEDS_INVESTIGATION
            levels = [p_mean, p_t, p_n]
            if any(l.startswith("MISSING") for l in levels):
                status = "MISSING"
                level = "MISSING"
            elif all(l == "EXACT" for l in levels):
                status = "PASS"
                level = "EXACT"
            else:
                status = "NEEDS_INVESTIGATION"
                level = "INVESTIGATE"

            diff_mean = new_mean - old_mean if not np.isnan(old_mean) else np.nan
            print(f"new={new_mean:.9f} old={old_mean:.9f} diff={diff_mean:.2e} [{level}]")

            ric_rows.append({
                "signal_name": sig, "horizon": hz,
                "new_mean_rank_ic": new_mean, "old_mean_rank_ic": old_mean,
                "diff_mean_rank_ic": diff_mean,
                "new_t_stat": new_t, "old_t_stat": old_t,
                "diff_t_stat": new_t - old_t if not np.isnan(old_t) else np.nan,
                "new_n_periods": int(new_n),
                "old_n_periods": int(old_n) if not np.isnan(old_n) else np.nan,
                "parity_mean": p_mean, "parity_tstat": p_t, "parity_nperiods": p_n,
                "parity_status": status,
                "parity_level": level,
            })

    ric_df = pd.DataFrame(ric_rows)
    ric_df.to_csv(RUN_DIR / "phase12d_h2_r_signal_eval_parity_rankic.csv", index=False)

    # --- Quantile Spread parity (behavioral) ---
    spread_rows = []
    for sig in SIGNAL_NAMES:
        for hz in HORIZONS:
            print(f"  Spread: {sig} × {hz}", end=" ", flush=True)

            sig_df = sp_old[["timestamp", "symbol", sig]].rename(
                columns={sig: "signal_value"}
            ).dropna(subset=["signal_value"])
            sig_df["signal_name"] = sig

            label_h = old_label_dict[hz]

            # PUBLIC API CALLS
            spread_ts = compute_quantile_spread(sig_df, label_h, n_quantiles=5)
            spread_summary = summarize_quantile_spread(spread_ts)

            new_mean_s = spread_summary["mean_spread"]
            new_median_s = spread_summary["median_spread"]
            new_hit = spread_summary["positive_fraction"]
            new_n = spread_summary["n_periods"]

            # Old values
            old_row = old_spread_df[(old_spread_df["signal_id"] == sig) & (old_spread_df["horizon"] == hz)]
            if old_row.empty:
                old_mean_s, old_hit, old_n = np.nan, np.nan, np.nan
            else:
                old_mean_s = old_row["mean_spread"].iloc[0]
                old_hit = old_row["hit_rate"].iloc[0]
                old_n = old_row["n_timestamps"].iloc[0]

            # Direction: negative = short top bucket, positive = long top bucket
            new_dir = "negative" if new_mean_s < 0 else "positive"
            old_dir = "negative" if (not np.isnan(old_mean_s) and old_mean_s < 0) else "positive"

            p_mean, reason_mean = check_spread_parity(
                new_mean_s, old_mean_s, SPREAD_TOLERANCE["mean_spread"], new_dir, old_dir)
            p_hit, reason_hit = check_spread_parity(
                new_hit, old_hit, SPREAD_TOLERANCE["positive_fraction"], new_dir, old_dir)
            p_n = check_rankic_parity(new_n, old_n, SPREAD_TOLERANCE["n_periods"])

            levels = [p_mean, p_hit, p_n]
            if any(l.startswith("MISSING") for l in levels):
                status = "MISSING"
                level = "MISSING"
                reason = "missing_data"
            elif all(l == "EXACT" for l in levels):
                status = "PASS"
                level = "EXACT"
                reason = "exact_match"
            elif all(l in ("EXACT", "BEHAVIORAL") for l in levels):
                status = "PASS"
                level = "BEHAVIORAL"
                reason = f"mean:{reason_mean};hit:{reason_hit}"
            else:
                status = "NEEDS_INVESTIGATION"
                level = "INVESTIGATE"
                reason = f"mean:{reason_mean};hit:{reason_hit}"

            diff_s = new_mean_s - old_mean_s if not np.isnan(old_mean_s) else np.nan
            print(f"new={new_mean_s:.6f} old={old_mean_s:.6f} diff={diff_s:.2e} [{level}]")

            spread_rows.append({
                "signal_name": sig, "horizon": hz,
                "new_mean_spread": new_mean_s, "old_mean_spread": old_mean_s,
                "diff_mean_spread": diff_s,
                "new_median_spread": new_median_s, "old_median_spread": np.nan,
                "new_positive_fraction": new_hit, "old_positive_fraction": old_hit,
                "diff_positive_fraction": new_hit - old_hit if not np.isnan(old_hit) else np.nan,
                "new_n_periods": int(new_n),
                "old_n_periods": int(old_n) if not np.isnan(old_n) else np.nan,
                "parity_mean": p_mean, "parity_hit": p_hit, "parity_nperiods": p_n,
                "parity_status": status,
                "parity_level": level,
                "difference_reason": reason,
            })

    spread_df = pd.DataFrame(spread_rows)
    spread_df.to_csv(RUN_DIR / "phase12d_h2_r_signal_eval_parity_quantile_spread.csv", index=False)

    # --- Consistency check using PUBLIC API + current labels ---
    print("\nConsistency check (current labels):")
    cur_label_symbols = set(cur_labels["symbol"].unique())
    sp_cur = sp[sp["symbol"].isin(cur_label_symbols)].copy()
    for sig in SIGNAL_NAMES:
        sig_df = sp_cur[["timestamp", "symbol", sig]].rename(
            columns={sig: "signal_value"}
        ).dropna(subset=["signal_value"])
        sig_df["signal_name"] = sig

        label_h = cur_label_dict["1h"]

        # PUBLIC API CALLS
        ric_ts = compute_rank_ic(sig_df, label_h)
        ric_s = summarize_rank_ic(ric_ts)
        spread_ts = compute_quantile_spread(sig_df, label_h)
        sp_s = summarize_quantile_spread(spread_ts)
        result = check_rankic_spread_consistency(ric_s, sp_s)
        print(f"  {sig} 1h: {result} (IC={ric_s['mean_rank_ic']:.6f}, spread={sp_s['mean_spread']:.6f})")

    # --- Summary ---
    ric_exact = (ric_df["parity_level"] == "EXACT").sum()
    ric_investigate = (ric_df["parity_level"] == "INVESTIGATE").sum()
    ric_missing = ric_df["parity_level"].isin(["MISSING", "MISSING_NEW", "MISSING_OLD"]).sum()

    sp_exact = (spread_df["parity_level"] == "EXACT").sum()
    sp_behavioral = (spread_df["parity_level"] == "BEHAVIORAL").sum()
    sp_investigate = (spread_df["parity_level"] == "INVESTIGATE").sum()
    sp_missing = spread_df["parity_level"].isin(["MISSING", "MISSING_NEW", "MISSING_OLD"]).sum()

    ric_ok = ric_exact == len(ric_df)
    sp_ok = (sp_exact + sp_behavioral) == len(spread_df)
    overall = "PASS" if ric_ok and sp_ok else "NEEDS_INVESTIGATION"

    summary = pd.DataFrame([
        {"check_group": "rankic_parity", "total_checks": len(ric_df),
         "exact_count": ric_exact, "investigate_count": ric_investigate,
         "missing_count": ric_missing,
         "overall_status": "PASS" if ric_ok else "NEEDS_INVESTIGATION"},
        {"check_group": "quantile_spread_parity", "total_checks": len(spread_df),
         "exact_count": sp_exact, "behavioral_count": sp_behavioral,
         "investigate_count": sp_investigate, "missing_count": sp_missing,
         "overall_status": "PASS" if sp_ok else "NEEDS_INVESTIGATION"},
        {"check_group": "overall", "total_checks": len(ric_df) + len(spread_df),
         "exact_count": ric_exact + sp_exact,
         "behavioral_count": sp_behavioral,
         "investigate_count": ric_investigate + sp_investigate,
         "missing_count": ric_missing + sp_missing,
         "overall_status": overall},
    ])
    summary.to_csv(RUN_DIR / "phase12d_h2_r_signal_eval_parity_summary.csv", index=False)

    print(f"\n{'='*60}")
    print(f"RankIC:    {ric_exact} EXACT / {ric_investigate} INVESTIGATE / {ric_missing} MISSING")
    print(f"Spread:    {sp_exact} EXACT / {sp_behavioral} BEHAVIORAL / {sp_investigate} INVESTIGATE")
    print(f"Overall:   {overall}")
    print(f"H3 gate:   {'OPEN' if ric_ok and sp_ok else 'BLOCKED — investigate before H3'}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
