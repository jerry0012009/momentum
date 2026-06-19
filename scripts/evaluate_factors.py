#!/usr/bin/env python3
"""Evaluate factor-level IC for all registered factors.

Reuses factor_formula_registry.py for factor metadata.
Computes RankIC (Spearman) by ranking factor values per timestamp,
then computing Pearson of ranks against pre-ranked forward returns.

This is the canonical factor-level evaluator (replaces the stale
evaluate_factors_dynamic_universe.py which depended on a missing module).

Usage:
    python scripts/evaluate_factors.py
    python scripts/evaluate_factors.py --factor-ids mom_20h reversal_5h
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FEATURES_DIR = ROOT / "data" / "features" / "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
LABELS_PATH = FEATURES_DIR / "labels.parquet"
OUTPUT_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_level_evaluation"

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

LABEL_HORIZONS = ["1h", "4h", "24h", "72h"]
LABEL_COLS = {h: f"ret_fwd_{h}" for h in LABEL_HORIZONS}
MIN_SYMBOLS = 10

SIGNAL_FACTOR_IDS = {
    "vol_5h", "vol_40h", "downside_vol_20h", "vol_of_vol_20h",
    "rsi_7h", "rsi_28h", "xs_rank_vol",
    "range_1h", "range_4h", "price_pos_24h",
}


def load_factor_registry() -> list[dict]:
    from factor_formula_registry import REGISTRY
    return [{
        "factor_id": fs.factor_id,
        "family": getattr(fs, "family", "unknown"),
        "category": getattr(fs, "family", "unknown"),
        "expected_direction": getattr(fs, "expected_direction", "conditional"),
        "notes": getattr(fs, "notes", ""),
    } for fs in REGISTRY]


def rank_ic_from_boundaries(fv_rank: np.ndarray, ret_rank: np.ndarray,
                             boundaries: np.ndarray, n_ts: int,
                             min_symbols: int = MIN_SYMBOLS) -> list[float]:
    """Compute per-timestamp Spearman IC from pre-ranked arrays and group boundaries."""
    ic_vals = []
    for t in range(n_ts):
        lo, hi = boundaries[t], boundaries[t + 1]
        n = hi - lo
        if n < min_symbols:
            continue
        x = fv_rank[lo:hi]
        y = ret_rank[lo:hi]
        valid = ~(np.isnan(x) | np.isnan(y))
        x = x[valid]; y = y[valid]
        if len(x) < min_symbols:
            continue
        xm = x.mean(); ym = y.mean()
        dx = x - xm; dy = y - ym
        cov = (dx * dy).sum()
        denom = np.sqrt((dx * dx).sum() * (dy * dy).sum())
        if denom > 0:
            ic_vals.append(cov / denom)
    return ic_vals


def summarize_ic(ic_vals: list[float]) -> dict:
    if not ic_vals:
        return {"mean": None, "t_stat": None, "n_periods": 0}
    arr = np.array(ic_vals)
    m = arr.mean()
    s = arr.std(ddof=1) if len(arr) > 1 else 0.0
    t = m / (s / np.sqrt(len(arr))) if s > 0 else 0.0
    return {"mean": float(m), "t_stat": float(t), "n_periods": len(arr)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--factor-ids", nargs="*")
    args = parser.parse_args()

    print("Factor-Level IC Evaluation", flush=True)
    print(f"  Features: {FEATURES_DIR}", flush=True)
    print(f"  Labels:   {LABELS_PATH}", flush=True)
    print(f"  Output:   {OUTPUT_DIR}\n", flush=True)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load registry
    registry = load_factor_registry()
    if args.factor_ids:
        registry = [r for r in registry if r["factor_id"] in args.factor_ids]
    print(f"  Registered factors: {len(registry)}", flush=True)

    # Load labels ONCE and pre-rank all return horizons
    print("  Loading and pre-ranking labels...", end=" ", flush=True)
    t0 = time.time()
    labels = pd.read_parquet(LABELS_PATH)
    labels["timestamp"] = pd.to_datetime(labels["timestamp"], utc=True)
    labels = labels.sort_values("timestamp").reset_index(drop=True)
    g_lab = labels.groupby("timestamp")
    for hz, col in LABEL_COLS.items():
        labels[f"_rank_{hz}"] = g_lab[col].rank()
    print(f"done ({time.time() - t0:.1f}s, {len(labels)} rows)", flush=True)

    # Pre-compute group boundaries for labels
    ts_lab = labels["timestamp"].values
    _, lab_first = np.unique(ts_lab, return_index=True)
    lab_boundaries = np.append(lab_first, len(ts_lab))
    n_ts_lab = len(lab_first)
    print(f"  {n_ts_lab} unique timestamps\n", flush=True)

    results = []
    missing_factors = []
    t_start = time.time()

    for i, spec in enumerate(registry):
        fid = spec["factor_id"]
        print(f"  [{i + 1}/{len(registry)}] {fid}...", end=" ", flush=True)

        fv_path = FEATURES_DIR / fid / "factor_values.parquet"
        if not fv_path.exists():
            missing_factors.append(fid)
            print("MISSING_FACTOR_VALUES", flush=True)
            for hz in LABEL_HORIZONS:
                results.append({
                    "factor_name": fid, "category": spec["category"],
                    "expected_direction": spec["expected_direction"],
                    "direction_source": "factor_registry", "horizon": hz,
                    "raw_mean_rank_ic": None, "direction_adjusted_mean_rank_ic": None,
                    "t_stat": None, "n_periods": 0, "n_symbols_avg": None,
                    "coverage": None, "missing_rate": None,
                    "used_in_current_signal": fid in SIGNAL_FACTOR_IDS,
                    "status": "MISSING_FACTOR_VALUES", "notes": spec["notes"],
                })
            continue

        # Load factor values
        fv = pd.read_parquet(fv_path, columns=["timestamp", "symbol", "factor_value"])
        fv["timestamp"] = pd.to_datetime(fv["timestamp"], utc=True)
        n_total = len(fv)
        n_valid = fv["factor_value"].notna().sum()
        miss_rate = round(1.0 - n_valid / n_total, 6) if n_total > 0 else 1.0

        # Merge with labels (all horizons at once)
        merged = fv.merge(labels, on=["timestamp", "symbol"], how="inner")
        merged = merged.sort_values("timestamp").reset_index(drop=True)

        if len(merged) == 0:
            print("NO_ALIGNED_DATA", flush=True)
            for hz in LABEL_HORIZONS:
                results.append({
                    "factor_name": fid, "category": spec["category"],
                    "expected_direction": spec["expected_direction"],
                    "direction_source": "factor_registry", "horizon": hz,
                    "raw_mean_rank_ic": None, "direction_adjusted_mean_rank_ic": None,
                    "t_stat": None, "n_periods": 0, "n_symbols_avg": None,
                    "coverage": 0, "missing_rate": miss_rate,
                    "used_in_current_signal": fid in SIGNAL_FACTOR_IDS,
                    "status": "NO_ALIGNED_DATA", "notes": spec["notes"],
                })
            continue

        # Rank factor values per timestamp
        g_merged = merged.groupby("timestamp")
        fv_rank = g_merged["factor_value"].rank().values
        coverage = len(merged)
        n_symbols_avg = merged.groupby("timestamp")["symbol"].nunique().mean()

        # Group boundaries on merged data
        ts_m = merged["timestamp"].values
        _, m_first = np.unique(ts_m, return_index=True)
        m_boundaries = np.append(m_first, len(ts_m))
        n_ts_m = len(m_first)

        # Compute IC for all 4 horizons
        horizon_ics = {}
        for hz in LABEL_HORIZONS:
            ret_rank = merged[f"_rank_{hz}"].values
            ic_vals = rank_ic_from_boundaries(fv_rank, ret_rank, m_boundaries, n_ts_m)
            horizon_ics[hz] = summarize_ic(ic_vals)

        # Print summary and build results
        d = spec["expected_direction"]
        any_computed = False
        for hz in LABEL_HORIZONS:
            ic = horizon_ics[hz]
            if ic["n_periods"] > 0:
                any_computed = True
                raw = ic["mean"]
                adj = -raw if d == "negative" else raw
                status = "COMPUTED"
                if d not in ("positive", "negative"):
                    status = "DIRECTION_UNKNOWN"
                if fid in SIGNAL_FACTOR_IDS:
                    status = "ACTIVE_IN_SIGNAL_COMPUTED"
                results.append({
                    "factor_name": fid, "category": spec["category"],
                    "expected_direction": d,
                    "direction_source": "factor_registry", "horizon": hz,
                    "raw_mean_rank_ic": round(raw, 8),
                    "direction_adjusted_mean_rank_ic": round(adj, 8),
                    "t_stat": round(ic["t_stat"], 4),
                    "n_periods": ic["n_periods"],
                    "n_symbols_avg": round(n_symbols_avg, 1),
                    "coverage": coverage,
                    "missing_rate": miss_rate,
                    "used_in_current_signal": fid in SIGNAL_FACTOR_IDS,
                    "status": status, "notes": spec["notes"],
                })
            else:
                results.append({
                    "factor_name": fid, "category": spec["category"],
                    "expected_direction": d,
                    "direction_source": "factor_registry", "horizon": hz,
                    "raw_mean_rank_ic": None, "direction_adjusted_mean_rank_ic": None,
                    "t_stat": None, "n_periods": 0, "n_symbols_avg": None,
                    "coverage": coverage, "missing_rate": miss_rate,
                    "used_in_current_signal": fid in SIGNAL_FACTOR_IDS,
                    "status": "NO_VALID_PERIODS", "notes": spec["notes"],
                })

        if any_computed:
            ic1 = horizon_ics["1h"]
            raw1 = ic1["mean"] if ic1["mean"] is not None else 0
            adj1 = -raw1 if d == "negative" else raw1
            sig_mark = "★" if fid in SIGNAL_FACTOR_IDS else " "
            print(f"{sig_mark} adj_1h={adj1:+.6f} t={ic1['t_stat']:.2f} n={ic1['n_periods']}", flush=True)
        else:
            print("NO_VALID_PERIODS", flush=True)

    elapsed = time.time() - t_start

    # === Write outputs ===
    df = pd.DataFrame(results)
    csv_path = OUTPUT_DIR / "factor_level_rankic_summary.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n  Wrote {csv_path} ({len(df)} rows)", flush=True)

    json_path = OUTPUT_DIR / "factor_level_rankic_summary.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"  Wrote {json_path}", flush=True)

    # Coverage summary
    cov_rows = []
    for fid in df["factor_name"].unique():
        fdf = df[df["factor_name"] == fid]
        comp = fdf[fdf["status"].str.contains("COMPUTED", na=False)]
        adj = fdf["direction_adjusted_mean_rank_ic"]
        cov_rows.append({
            "factor_name": fid,
            "category": fdf.iloc[0]["category"],
            "expected_direction": fdf.iloc[0]["expected_direction"],
            "used_in_current_signal": fdf.iloc[0]["used_in_current_signal"],
            "status": fdf.iloc[0]["status"],
            "horizons_computed": len(comp),
            "horizons_total": len(fdf),
            "best_adj_ic_horizon": fdf.loc[adj.abs().idxmax(), "horizon"] if adj.notna().any() else None,
            "best_adj_ic": round(float(adj.max()), 8) if adj.notna().any() else None,
        })
    cov_df = pd.DataFrame(cov_rows)
    cov_path = OUTPUT_DIR / "factor_level_coverage_summary.csv"
    cov_df.to_csv(cov_path, index=False)
    print(f"  Wrote {cov_path}", flush=True)

    # Manifest
    computed_fids = df[df["status"].str.contains("COMPUTED", na=False)]["factor_name"].unique()
    manifest = {
        "phase": "12D-H8",
        "generated": datetime.now(timezone.utc).isoformat(),
        "dataset_id": "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1",
        "labels_path": str(LABELS_PATH),
        "features_dir": str(FEATURES_DIR),
        "total_registered_factors": len(registry),
        "computed_factors": int(len(computed_fids)),
        "missing_factor_values": len(missing_factors),
        "missing_factor_ids": missing_factors,
        "active_in_signal": len([r for r in registry if r["factor_id"] in SIGNAL_FACTOR_IDS]),
        "horizons": LABEL_HORIZONS,
        "evaluation_method": "RankIC (Spearman): rank per timestamp, Pearson of ranks",
        "direction_adjustment": "positive→raw, negative→-raw, conditional→raw (DIRECTION_UNKNOWN)",
        "elapsed_seconds": round(elapsed, 1),
        "disclaimer": "Factor-level IC, not signal-level. Not tradeable alpha.",
    }
    manifest_path = OUTPUT_DIR / "factor_level_evaluation_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"  Wrote {manifest_path}", flush=True)

    # Summary
    print(f"\n=== Summary ({elapsed:.0f}s) ===", flush=True)
    print(f"  Registered: {manifest['total_registered_factors']}", flush=True)
    print(f"  Computed:   {manifest['computed_factors']}", flush=True)
    print(f"  Missing FV: {manifest['missing_factor_values']} ({', '.join(missing_factors)})", flush=True)
    print(f"  Active in signal: {manifest['active_in_signal']}", flush=True)

    # Top 10 by adj IC (1h)
    top1h = df[(df["horizon"] == "1h") & (df["status"].str.contains("COMPUTED", na=False))].nlargest(10, "direction_adjusted_mean_rank_ic")
    print(f"\n  Top 10 by direction-adjusted IC (1h):", flush=True)
    for _, row in top1h.iterrows():
        sig_mark = "★" if row["used_in_current_signal"] else " "
        print(f"    {sig_mark} {row['factor_name']:30s} adj={row['direction_adjusted_mean_rank_ic']:+.6f}  t={row['t_stat']:.2f}  dir={row['expected_direction']}", flush=True)


if __name__ == "__main__":
    main()
