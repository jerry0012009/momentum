#!/usr/bin/env python3
"""Parity check: evaluate_factors.py boundary-based Spearman vs momentum.signal_evaluation.compute_rank_ic.

Selects 5 representative factors × 2 horizons (1h, 24h).
Compares per-timestamp IC values between the two methods.
Both rank on the merged subset (same approach as compute_rank_ic).

Usage:
    python scripts/check_factor_ic_parity.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FEATURES_DIR = ROOT / "data" / "features" / "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
LABELS_PATH = FEATURES_DIR / "labels.parquet"

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from momentum.signal_evaluation import compute_rank_ic

CHECK_FACTORS = ["vol_5h", "vol_40h", "rsi_7h", "range_1h", "price_pos_24h"]
CHECK_HORIZONS = {"1h": "ret_fwd_1h", "24h": "ret_fwd_24h"}
MIN_SYMBOLS = 10


def boundary_spearman(fv_rank, ret_rank, boundaries, n_ts):
    """Same as evaluate_factors.py: boundary-based Spearman from pre-ranked arrays."""
    ic_vals = []
    for t in range(n_ts):
        lo, hi = boundaries[t], boundaries[t + 1]
        if hi - lo < MIN_SYMBOLS:
            continue
        x = fv_rank[lo:hi]; y = ret_rank[lo:hi]
        valid = ~(np.isnan(x) | np.isnan(y))
        x, y = x[valid], y[valid]
        if len(x) < MIN_SYMBOLS:
            continue
        xm, ym = x.mean(), y.mean()
        dx, dy = x - xm, y - ym
        var_x = (dx * dx).sum()
        var_y = (dy * dy).sum()
        if var_x <= 0 or var_y <= 0:
            continue  # zero variance → undefined (matches API: NaN)
        ic_val = (dx * dy).sum() / np.sqrt(var_x * var_y)
        if not np.isnan(ic_val):
            ic_vals.append(ic_val)
    return ic_vals


def main():
    print("=" * 70)
    print("Factor-Level IC Parity Check")
    print("  Method A: boundary-based Spearman (evaluate_factors.py)")
    print("  Method B: momentum.signal_evaluation.compute_rank_ic (public API)")
    print("  Both rank on merged subset (factor × labels)")
    print("=" * 70)
    print()

    print("Loading labels...", end=" ", flush=True)
    labels = pd.read_parquet(LABELS_PATH)
    labels["timestamp"] = pd.to_datetime(labels["timestamp"], utc=True)
    print(f"{len(labels)} rows")

    results = []
    all_pass = True

    for fid in CHECK_FACTORS:
        fv_path = FEATURES_DIR / fid / "factor_values.parquet"
        if not fv_path.exists():
            print(f"  {fid}: SKIP (no factor_values)")
            for hz in CHECK_HORIZONS:
                results.append({"factor": fid, "horizon": hz, "status": "SKIP_NO_FV"})
            continue

        fv = pd.read_parquet(fv_path, columns=["timestamp", "symbol", "factor_value"])
        fv["timestamp"] = pd.to_datetime(fv["timestamp"], utc=True)

        for hz, ret_col in CHECK_HORIZONS.items():
            print(f"  {fid} × {hz}...", end=" ", flush=True)

            # Merge then dropna factor_value (matches evaluate_factors.py)
            label_cols = ["timestamp", "symbol", ret_col]
            merged = fv.merge(labels[label_cols], on=["timestamp", "symbol"], how="inner")
            merged = merged.dropna(subset=["factor_value"])
            merged = merged.sort_values("timestamp").reset_index(drop=True)

            if len(merged) == 0:
                print("NO_DATA")
                results.append({"factor": fid, "horizon": hz, "status": "NO_DATA"})
                continue

            # Drop NaN returns (matches API: dropna(subset=[signal, return]))
            merged_h = merged.dropna(subset=[ret_col])

            # === Method A: boundary (evaluate_factors.py) ===
            g = merged_h.groupby("timestamp")
            fv_rank = g["factor_value"].rank().values
            ret_rank = g[ret_col].rank().values  # rank on merged subset

            ts_m = merged_h["timestamp"].values
            _, first_idx = np.unique(ts_m, return_index=True)
            boundaries = np.append(first_idx, len(ts_m))
            n_ts = len(first_idx)

            ic_a = np.array(boundary_spearman(fv_rank, ret_rank, boundaries, n_ts))
            mean_a = ic_a.mean() if len(ic_a) > 0 else np.nan
            n_periods_a = len(ic_a)

            # === Method B: public API ===
            sig_df = fv[["timestamp", "symbol", "factor_value"]].rename(
                columns={"factor_value": "signal_value"}
            )
            label_api = labels[["timestamp", "symbol", ret_col]].rename(
                columns={ret_col: "forward_return"}
            )
            api = compute_rank_ic(sig_df, label_api, min_symbols=MIN_SYMBOLS)
            ic_b = api["rank_ic"].dropna().values
            mean_b = ic_b.mean() if len(ic_b) > 0 else np.nan
            n_periods_b = len(ic_b)

            # === Compare ===
            mean_diff = abs(mean_a - mean_b) if not (np.isnan(mean_a) or np.isnan(mean_b)) else float("inf")
            n_match = n_periods_a == n_periods_b
            pass_mean = mean_diff <= 1e-10
            pass_periods = n_match
            ok = pass_mean and pass_periods
            status = "PASS" if ok else "FAIL"
            if not ok:
                all_pass = False

            print(f"mean_diff={mean_diff:.2e} n_a={n_periods_a} n_b={n_periods_b} [{status}]")

            results.append({
                "factor": fid, "horizon": hz,
                "method_a_mean_ic": round(mean_a, 12),
                "method_b_mean_ic": round(mean_b, 12),
                "mean_diff": round(mean_diff, 15),
                "method_a_n_periods": n_periods_a,
                "method_b_n_periods": n_periods_b,
                "periods_match": n_match,
                "mean_pass_1e10": pass_mean,
                "status": status,
            })

    # Summary
    print()
    print("=" * 70)
    df = pd.DataFrame(results)
    n_checked = len(df[df["status"].isin(["PASS", "FAIL"])])
    n_pass = len(df[df["status"] == "PASS"])
    n_fail = len(df[df["status"] == "FAIL"])
    print(f"Checked: {n_checked} factor×horizon pairs")
    print(f"PASS: {n_pass}")
    print(f"FAIL: {n_fail}")

    if n_checked > 0:
        max_diff = df[df["status"].isin(["PASS", "FAIL"])]["mean_diff"].max()
        print(f"Max mean RankIC diff: {max_diff:.2e}")

    if all_pass:
        print("\n✓ PARITY VERIFIED")
    else:
        print("\n✗ PARITY FAILED — investigate before proceeding")

    print("=" * 70)
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
