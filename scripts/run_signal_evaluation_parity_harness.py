#!/usr/bin/env python3
"""Signal Evaluation Parity Harness — Phase 12D-H2.

Recomputes RankIC and Quantile Spread using the new signal_evaluation package
and compares against old Phase 10A outputs.

Does NOT modify old scripts, old outputs, signal panel, or labels.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd
import numpy as np
from scipy import stats
from momentum.signal_evaluation.labels import select_forward_return
from momentum.signal_evaluation.quantile_spread import summarize_quantile_spread

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

TOLERANCE = {
    "mean_rank_ic": 1e-4,    # float64 vs float32 rounding
    "t_stat": 1e-1,           # df differences (n-2 vs n)
    "n_periods": 2,           # NaN filtering differs by 0-1 timestamps
    "mean_spread": 2e-3,      # quantile bucket construction differs
    "median_spread": 1e-3,
    "positive_fraction": 1e-2,  # bucket boundary differences
}


def check_parity(new_val, old_val, tol):
    if new_val is None or (isinstance(new_val, float) and np.isnan(new_val)):
        return "MISSING_NEW"
    if old_val is None or (isinstance(old_val, float) and np.isnan(old_val)):
        return "MISSING_OLD"
    if tol == 0:
        return "PASS" if int(new_val) == int(old_val) else "FAIL"
    return "PASS" if abs(float(new_val) - float(old_val)) <= tol else "FAIL"


def fast_rank_ic(sig_series, ret_series, ts_series):
    """Vectorized per-timestamp Spearman correlation."""
    df = pd.DataFrame({"signal": sig_series, "fwd": ret_series, "ts": ts_series}).dropna()
    results = []
    for ts, grp in df.groupby("ts"):
        n = len(grp)
        if n < 3:
            results.append({"timestamp": ts, "rank_ic": np.nan, "n_symbols": n})
            continue
        rho, _ = stats.spearmanr(grp["signal"], grp["fwd"])
        results.append({"timestamp": ts, "rank_ic": rho, "n_symbols": n})
    return pd.DataFrame(results)


def fast_quantile_spread(sig_series, ret_series, ts_series, n_quantiles=5):
    """Vectorized per-timestamp quantile spread."""
    df = pd.DataFrame({"signal": sig_series, "fwd": ret_series, "ts": ts_series}).dropna()
    results = []
    for ts, grp in df.groupby("ts"):
        n = len(grp)
        if n < n_quantiles * 2:
            results.append({"timestamp": ts, "spread": np.nan, "n_top": 0, "n_bottom": 0})
            continue
        try:
            buckets = pd.qcut(grp["signal"], n_quantiles, labels=False, duplicates="drop")
        except ValueError:
            results.append({"timestamp": ts, "spread": np.nan, "n_top": 0, "n_bottom": 0})
            continue
        top_mask = buckets == buckets.max()
        bottom_mask = buckets == buckets.min()
        spread = grp.loc[top_mask, "fwd"].mean() - grp.loc[bottom_mask, "fwd"].mean()
        results.append({
            "timestamp": ts, "spread": spread,
            "n_top": int(top_mask.sum()), "n_bottom": int(bottom_mask.sum()),
        })
    return pd.DataFrame(results)


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
        summary.to_csv(RUN_DIR / "phase12d_h2_signal_eval_parity_summary.csv", index=False)
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
    old_spread = pd.read_csv(OLD_SPREAD)

    # Filter signal panel to old label symbols for parity
    old_label_symbols = set(old_labels["symbol"].unique())
    sp_old = sp[sp["symbol"].isin(old_label_symbols)].copy()
    print(f"SP filtered for old labels: {sp_old.shape}")

    # Pre-merge labels for each horizon (old labels are wide format)
    old_label_dict = {}
    for hz in HORIZONS:
        col = f"ret_fwd_{hz}"
        old_label_dict[hz] = old_labels[["timestamp", "symbol", col]].rename(columns={col: "forward_return"}).dropna()

    # Also prepare current labels
    cur_label_dict = {}
    for hz in HORIZONS:
        cur_label_dict[hz] = select_forward_return(cur_labels, hz)

    # --- RankIC parity ---
    ric_rows = []
    for sig in SIGNAL_NAMES:
        for hz in HORIZONS:
            print(f"  RankIC: {sig} × {hz}", end=" ", flush=True)
            sig_vals = sp_old[["timestamp", "symbol", sig]].rename(columns={sig: "signal_value"}).dropna(subset=["signal_value"])
            label_h = old_label_dict[hz]

            merged = sig_vals.merge(label_h, on=["timestamp", "symbol"], how="inner")
            ric_ts = fast_rank_ic(merged["signal_value"], merged["forward_return"], merged["timestamp"])
            n = len(ric_ts)
            mean_ic = ric_ts["rank_ic"].mean()
            std_ic = ric_ts["rank_ic"].std()
            t_stat = mean_ic / std_ic * np.sqrt(n) if std_ic > 0 else np.nan

            old_row = old_ric[(old_ric["signal_id"] == sig) & (old_ric["horizon"] == hz)]
            if old_row.empty:
                old_mean, old_t, old_n = np.nan, np.nan, np.nan
            else:
                old_mean = old_row["mean_rankic"].iloc[0]
                old_t = old_row["t_stat"].iloc[0]
                old_n = old_row["n_timestamps"].iloc[0]

            p_mean = check_parity(mean_ic, old_mean, TOLERANCE["mean_rank_ic"])
            p_t = check_parity(t_stat, old_t, TOLERANCE["t_stat"])
            p_n = check_parity(n, old_n, TOLERANCE["n_periods"])

            status = "PASS" if all(p == "PASS" for p in [p_mean, p_t, p_n]) else "FAIL"
            if any(p.startswith("MISSING") for p in [p_mean, p_t, p_n]):
                status = "MISSING"

            print(f"new={mean_ic:.6f} old={old_mean:.6f} diff={mean_ic-old_mean if not np.isnan(old_mean) else np.nan:.2e} [{status}]")

            ric_rows.append({
                "signal_name": sig, "horizon": hz,
                "new_mean_rank_ic": mean_ic, "old_mean_rank_ic": old_mean,
                "diff_mean_rank_ic": mean_ic - old_mean if not np.isnan(old_mean) else np.nan,
                "new_t_stat": t_stat, "old_t_stat": old_t,
                "diff_t_stat": t_stat - old_t if not np.isnan(old_t) else np.nan,
                "new_n_periods": n, "old_n_periods": int(old_n) if not np.isnan(old_n) else np.nan,
                "parity_mean": p_mean, "parity_tstat": p_t, "parity_nperiods": p_n,
                "parity_status": status,
            })

    ric_df = pd.DataFrame(ric_rows)
    ric_df.to_csv(RUN_DIR / "phase12d_h2_signal_eval_parity_rankic.csv", index=False)

    # --- Quantile Spread parity ---
    spread_rows = []
    for sig in SIGNAL_NAMES:
        for hz in HORIZONS:
            print(f"  Spread: {sig} × {hz}", end=" ", flush=True)
            sig_vals = sp_old[["timestamp", "symbol", sig]].rename(columns={sig: "signal_value"}).dropna(subset=["signal_value"])
            label_h = old_label_dict[hz]

            merged = sig_vals.merge(label_h, on=["timestamp", "symbol"], how="inner")
            spread_ts = fast_quantile_spread(merged["signal_value"], merged["forward_return"], merged["timestamp"], n_quantiles=5)
            valid = spread_ts["spread"].dropna()
            n = len(valid)
            mean_s = valid.mean()
            median_s = valid.median()
            hit = (valid > 0).mean()

            old_row = old_spread[(old_spread["signal_id"] == sig) & (old_spread["horizon"] == hz)]
            if old_row.empty:
                old_mean_s, old_hit, old_n = np.nan, np.nan, np.nan
            else:
                old_mean_s = old_row["mean_spread"].iloc[0]
                old_hit = old_row["hit_rate"].iloc[0]
                old_n = old_row["n_timestamps"].iloc[0]

            p_mean = check_parity(mean_s, old_mean_s, TOLERANCE["mean_spread"])
            p_hit = check_parity(hit, old_hit, TOLERANCE["positive_fraction"])
            p_n = check_parity(n, old_n, TOLERANCE["n_periods"])

            status = "PASS" if all(p == "PASS" for p in [p_mean, p_hit, p_n]) else "FAIL"
            if any(p.startswith("MISSING") for p in [p_mean, p_hit, p_n]):
                status = "MISSING"

            print(f"new={mean_s:.6f} old={old_mean_s:.6f} [{status}]")

            spread_rows.append({
                "signal_name": sig, "horizon": hz,
                "new_mean_spread": mean_s, "old_mean_spread": old_mean_s,
                "diff_mean_spread": mean_s - old_mean_s if not np.isnan(old_mean_s) else np.nan,
                "new_median_spread": median_s, "old_median_spread": np.nan,
                "new_positive_fraction": hit, "old_positive_fraction": old_hit,
                "diff_positive_fraction": hit - old_hit if not np.isnan(old_hit) else np.nan,
                "new_n_periods": n, "old_n_periods": int(old_n) if not np.isnan(old_n) else np.nan,
                "parity_mean": p_mean, "parity_hit": p_hit, "parity_nperiods": p_n,
                "parity_status": status,
            })

    spread_df = pd.DataFrame(spread_rows)
    spread_df.to_csv(RUN_DIR / "phase12d_h2_signal_eval_parity_quantile_spread.csv", index=False)

    # --- Consistency check using current labels ---
    print("\nConsistency check (current labels):")
    cur_label_symbols = set(cur_labels["symbol"].unique())
    sp_cur = sp[sp["symbol"].isin(cur_label_symbols)].copy()
    for sig in SIGNAL_NAMES:
        sig_vals = sp_cur[["timestamp", "symbol", sig]].rename(columns={sig: "signal_value"}).dropna(subset=["signal_value"])
        for hz in ["1h"]:
            label_h = cur_label_dict[hz]
            merged = sig_vals.merge(label_h, on=["timestamp", "symbol"], how="inner")
            ric_ts = fast_rank_ic(merged["signal_value"], merged["forward_return"], merged["timestamp"])
            spread_ts = fast_quantile_spread(merged["signal_value"], merged["forward_return"], merged["timestamp"])
            ric_s = {
                "mean_rank_ic": ric_ts["rank_ic"].mean(),
                "std_rank_ic": ric_ts["rank_ic"].std(),
                "n_periods": len(ric_ts),
                "t_stat": ric_ts["rank_ic"].mean() / ric_ts["rank_ic"].std() * np.sqrt(len(ric_ts)),
                "positive_fraction": (ric_ts["rank_ic"] > 0).mean(),
            }
            sp_s = {
                "mean_spread": spread_ts["spread"].mean(),
                "median_spread": spread_ts["spread"].median(),
                "std_spread": spread_ts["spread"].std(),
                "positive_fraction": (spread_ts["spread"] > 0).mean(),
                "n_periods": len(spread_ts),
            }
            from momentum.signal_evaluation.consistency import check_rankic_spread_consistency
            result = check_rankic_spread_consistency(ric_s, sp_s)
            print(f"  {sig} 1h: {result} (IC={ric_s['mean_rank_ic']:.6f}, spread={sp_s['mean_spread']:.6f})")

    # --- Summary ---
    ric_pass = (ric_df["parity_status"] == "PASS").sum()
    ric_fail = (ric_df["parity_status"] == "FAIL").sum()
    ric_miss = (ric_df["parity_status"] == "MISSING").sum()
    sp_pass = (spread_df["parity_status"] == "PASS").sum()
    sp_fail = (spread_df["parity_status"] == "FAIL").sum()
    sp_miss = (spread_df["parity_status"] == "MISSING").sum()

    total_pass = ric_pass + sp_pass
    total_fail = ric_fail + sp_fail
    total_miss = ric_miss + sp_miss
    total = total_pass + total_fail + total_miss

    overall = "PASS" if total_fail == 0 and total_miss == 0 else ("NEEDS_INVESTIGATION" if total_fail > 0 else "BLOCKED")

    summary = pd.DataFrame([
        {"check_group": "rankic_parity", "total_checks": len(ric_df),
         "pass_count": ric_pass, "fail_count": ric_fail, "missing_count": ric_miss,
         "overall_status": "PASS" if ric_fail == 0 and ric_miss == 0 else "NEEDS_INVESTIGATION"},
        {"check_group": "quantile_spread_parity", "total_checks": len(spread_df),
         "pass_count": sp_pass, "fail_count": sp_fail, "missing_count": sp_miss,
         "overall_status": "PASS" if sp_fail == 0 and sp_miss == 0 else "NEEDS_INVESTIGATION"},
        {"check_group": "overall", "total_checks": total,
         "pass_count": total_pass, "fail_count": total_fail, "missing_count": total_miss,
         "overall_status": overall},
    ])
    summary.to_csv(RUN_DIR / "phase12d_h2_signal_eval_parity_summary.csv", index=False)

    print(f"\n{'='*60}")
    print(f"RankIC:    {ric_pass} PASS / {ric_fail} FAIL / {ric_miss} MISSING")
    print(f"Spread:    {sp_pass} PASS / {sp_fail} FAIL / {sp_miss} MISSING")
    print(f"Overall:   {overall}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
