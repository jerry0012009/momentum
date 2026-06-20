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
QUANTILE_BUCKETS = 5

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
                             min_symbols: int = MIN_SYMBOLS) -> tuple[list[float], list[int]]:
    """Compute per-timestamp Spearman IC from pre-ranked arrays and group boundaries.

    Returns (ic_vals, valid_indices) where valid_indices tracks which timestamps
    produced valid IC values.
    """
    ic_vals = []
    valid_indices = []
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
        var_x = (dx * dx).sum()
        var_y = (dy * dy).sum()
        if var_x <= 0 or var_y <= 0:
            continue  # zero variance → undefined correlation (matches API: NaN)
        ic_val = (dx * dy).sum() / np.sqrt(var_x * var_y)
        if not np.isnan(ic_val):
            ic_vals.append(ic_val)
            valid_indices.append(t)
    return ic_vals, valid_indices


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
    parser.add_argument("--output-suffix", type=str, default=None,
                        help="Suffix for output files (e.g. 'scratch_rev3h'). Required for partial runs.")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Custom output directory. Required for partial runs.")
    args = parser.parse_args()

    is_partial = bool(args.factor_ids)

    # Safety guard: partial runs must not overwrite canonical outputs
    if is_partial and not args.output_suffix and not args.output_dir:
        print("ERROR: --factor-ids partial evaluation cannot write canonical outputs.", flush=True)
        print("Use --output-suffix or --output-dir.", flush=True)
        print("", flush=True)
        print("Examples:", flush=True)
        print("  python scripts/evaluate_factors.py --factor-ids rev_3h --output-suffix scratch_rev3h", flush=True)
        print("  python scripts/evaluate_factors.py --factor-ids rev_3h --output-dir /tmp/eval_scratch/", flush=True)
        sys.exit(1)

    # Resolve output directory and suffix
    if args.output_dir:
        out_dir = Path(args.output_dir)
    else:
        out_dir = OUTPUT_DIR
    suffix = f"_{args.output_suffix}" if args.output_suffix else ""

    print("Factor-Level IC Evaluation", flush=True)
    if is_partial:
        print(f"  Mode: PARTIAL ({len(args.factor_ids)} factors)", flush=True)
    else:
        print("  Mode: FULL (all registered factors)", flush=True)
    print(f"  Features: {FEATURES_DIR}", flush=True)
    print(f"  Labels:   {LABELS_PATH}", flush=True)
    print(f"  Output:   {out_dir}\n", flush=True)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load registry
    registry = load_factor_registry()
    if args.factor_ids:
        registry = [r for r in registry if r["factor_id"] in args.factor_ids]
    print(f"  Registered factors: {len(registry)}", flush=True)

    # Load labels (no pre-ranking — rank on merged subset to match API)
    print("  Loading labels...", end=" ", flush=True)
    t0 = time.time()
    labels = pd.read_parquet(LABELS_PATH)
    labels["timestamp"] = pd.to_datetime(labels["timestamp"], utc=True)
    labels = labels.sort_values("timestamp").reset_index(drop=True)
    print(f"done ({time.time() - t0:.1f}s, {len(labels)} rows)\n", flush=True)

    results = []
    missing_factors = []
    detailed_ics = {}  # (fid, hz) -> list of (timestamp, ic_val)
    quantile_long_short = []  # quantile + long-short rows
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

        # Drop NaN factor_value before ranking (matches API: dropna before pivot)
        merged = merged.dropna(subset=["factor_value"])
        if len(merged) == 0:
            print("NO_VALID_FACTOR_VALUES", flush=True)
            for hz in LABEL_HORIZONS:
                results.append({
                    "factor_name": fid, "category": spec["category"],
                    "expected_direction": spec["expected_direction"],
                    "direction_source": "factor_registry", "horizon": hz,
                    "raw_mean_rank_ic": None, "direction_adjusted_mean_rank_ic": None,
                    "t_stat": None, "n_periods": 0, "n_symbols_avg": None,
                    "coverage": 0, "missing_rate": miss_rate,
                    "used_in_current_signal": fid in SIGNAL_FACTOR_IDS,
                    "status": "NO_VALID_FACTOR_VALUES", "notes": spec["notes"],
                })
            continue

        # Rank factor values per timestamp (on merged subset, same as API)
        g_merged = merged.groupby("timestamp")
        fv_rank = g_merged["factor_value"].rank().values
        coverage = len(merged)
        n_symbols_avg = merged.groupby("timestamp")["symbol"].nunique().mean()

        # Group boundaries on merged data
        ts_m = merged["timestamp"].values
        _, m_first = np.unique(ts_m, return_index=True)
        m_boundaries = np.append(m_first, len(ts_m))
        n_ts_m = len(m_first)

        # Compute IC for all 4 horizons (single groupby, NaN returns handled by boundary loop)
        horizon_ics = {}
        # Get the actual timestamps from merged data (sorted by group boundaries)
        ts_unique = merged["timestamp"].values[m_boundaries[:-1]]
        for hz in LABEL_HORIZONS:
            ret_rank = g_merged[LABEL_COLS[hz]].rank().values
            ic_vals, valid_ts_indices = rank_ic_from_boundaries(fv_rank, ret_rank, m_boundaries, n_ts_m)
            horizon_ics[hz] = summarize_ic(ic_vals)
            # Store raw IC values with timestamps for detailed analysis
            # valid_ts_indices maps IC values back to their timestamp positions
            valid_ts = ts_unique[valid_ts_indices] if len(valid_ts_indices) > 0 else np.array([])
            detailed_ics[(fid, hz)] = list(zip(valid_ts, ic_vals)) if len(ic_vals) > 0 else []

        # Pre-compute status for this factor (used by quantile/long-short)
        d = spec["expected_direction"]
        any_hz_computed = any(horizon_ics[hz]["n_periods"] > 0 for hz in LABEL_HORIZONS)
        if any_hz_computed:
            base_status = "DIRECTION_UNKNOWN" if d not in ("positive", "negative") else "COMPUTED"
            if fid in SIGNAL_FACTOR_IDS:
                base_status = "ACTIVE_IN_SIGNAL_COMPUTED"
        else:
            base_status = "NO_VALID_PERIODS"

        # Compute quantile returns and long-short per horizon
        for hz in LABEL_HORIZONS:
            ret_col = LABEL_COLS[hz]
            hz_merged = merged.dropna(subset=[ret_col])
            if len(hz_merged) < MIN_SYMBOLS * QUANTILE_BUCKETS:
                continue

            # Direction-adjusted sorting for long-short
            d = spec["expected_direction"]
            if d == "negative":
                hz_merged = hz_merged.copy()
                hz_merged["_sort_val"] = -hz_merged["factor_value"]
            elif d == "positive":
                hz_merged = hz_merged.copy()
                hz_merged["_sort_val"] = hz_merged["factor_value"]
            else:
                hz_merged = hz_merged.copy()
                hz_merged["_sort_val"] = hz_merged["factor_value"]

            # Quantile bucketing (vectorized)
            hz_merged = hz_merged.copy()
            hz_merged["_rank"] = hz_merged.groupby("timestamp")["_sort_val"].rank(method="first")
            hz_merged["_count"] = hz_merged.groupby("timestamp")["_sort_val"].transform("count")
            hz_merged["bucket"] = ((hz_merged["_rank"] - 1) * QUANTILE_BUCKETS / hz_merged["_count"]).astype(int).clip(0, QUANTILE_BUCKETS - 1)

            # Compute per-timestamp bucket means, then aggregate
            bucket_ts = hz_merged.groupby(["timestamp", "bucket"])[ret_col].mean().unstack(fill_value=np.nan)

            for b in range(QUANTILE_BUCKETS):
                if b in bucket_ts.columns:
                    br = bucket_ts[b].dropna()
                    quantile_long_short.append({
                        "factor_name": fid, "category": spec["category"],
                        "expected_direction": spec["expected_direction"],
                        "horizon": hz, "bucket": b,
                        "bucket_label": f"Q{b+1}",
                        "mean_forward_return": round(float(br.mean()), 8) if len(br) > 0 else None,
                        "median_forward_return": round(float(br.median()), 8) if len(br) > 0 else None,
                        "n_obs": int(hz_merged.groupby("timestamp").size().sum()) if len(hz_merged) > 0 else 0,
                        "n_periods": len(br),
                        "status": base_status,
                    })

            # Long-short: top - bottom per timestamp
            ls_arr = None
            if QUANTILE_BUCKETS - 1 in bucket_ts.columns and 0 in bucket_ts.columns:
                ls_spread = bucket_ts[QUANTILE_BUCKETS - 1] - bucket_ts[0]
                ls_spread = ls_spread.dropna()
                ls_arr = ls_spread.values
                if len(ls_arr) > 0:
                    ls_mean = float(ls_arr.mean())
                    ls_std = float(ls_arr.std(ddof=1)) if len(ls_arr) > 1 else 0.0
                    ls_t = ls_mean / (ls_std / np.sqrt(len(ls_arr))) if ls_std > 0 else 0.0
                    ls_win = float((ls_arr > 0).sum() / len(ls_arr))
                    top_mean = float(bucket_ts[QUANTILE_BUCKETS - 1].mean())
                    bot_mean = float(bucket_ts[0].mean())
                else:
                    ls_mean, ls_t, ls_win, top_mean, bot_mean = None, None, None, None, None
            else:
                ls_mean, ls_t, ls_win, top_mean, bot_mean = None, None, None, None, None

            ls_status = base_status
            quantile_long_short.append({
                "factor_name": fid, "category": spec["category"],
                "expected_direction": spec["expected_direction"],
                "horizon": hz, "bucket": "LONG_SHORT",
                "bucket_label": "Long-Short",
                "mean_forward_return": round(ls_mean, 8) if ls_mean is not None else None,
                "median_forward_return": None,
                "n_obs": None,
                "n_periods": len(ls_arr) if ls_arr is not None and len(ls_arr) > 0 else 0,
                "status": ls_status,
                "top_bucket_mean_return": round(top_mean, 8) if top_mean is not None else None,
                "bottom_bucket_mean_return": round(bot_mean, 8) if bot_mean is not None else None,
                "long_short_spread_mean": round(ls_mean, 8) if ls_mean is not None else None,
                "long_short_spread_t_stat": round(ls_t, 4) if ls_t is not None else None,
                "long_short_win_rate": round(ls_win, 4) if ls_win is not None else None,
            })

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
    out_dir.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(results)
    csv_path = out_dir / f"factor_level_rankic_summary{suffix}.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n  Wrote {csv_path} ({len(df)} rows)", flush=True)

    json_path = out_dir / f"factor_level_rankic_summary{suffix}.json"
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
    cov_path = out_dir / f"factor_level_coverage_summary{suffix}.csv"
    cov_df.to_csv(cov_path, index=False)
    print(f"  Wrote {cov_path}", flush=True)

    # === NEW OUTPUTS (Phase 13A-P1) ===

    # A. Metric panel: one row per factor × horizon
    metric_rows = []
    for _, row in df.iterrows():
        fid = row["factor_name"]
        hz = row["horizon"]
        ic_list_raw = [v for _, v in detailed_ics.get((fid, hz), [])]
        raw_ic = row.get("raw_mean_rank_ic")
        adj_ic = row.get("direction_adjusted_mean_rank_ic")

        if ic_list_raw and len(ic_list_raw) > 1:
            ic_arr = np.array(ic_list_raw)
            rank_ic_std = float(ic_arr.std(ddof=1))
            raw_mean = float(ic_arr.mean())
            icir = round(raw_mean / rank_ic_std, 6) if rank_ic_std > 0 else None
            ic_win_raw = float((ic_arr > 0).sum() / len(ic_arr))
            # Direction-adjusted win rate
            d = row["expected_direction"]
            if d == "negative":
                adj_arr = -ic_arr
            elif d == "positive":
                adj_arr = ic_arr
            else:
                adj_arr = ic_arr  # conditional → raw
            ic_win_adj = float((adj_arr > 0).sum() / len(adj_arr))
        else:
            rank_ic_std = None
            icir = None
            ic_win_raw = None
            ic_win_adj = None

        # Find quantile/long-short data for this factor × horizon
        ls_row = None
        for qls in quantile_long_short:
            if qls["factor_name"] == fid and qls["horizon"] == hz and qls.get("bucket") == "LONG_SHORT":
                ls_row = qls
                break

        metric_rows.append({
            "factor_name": fid,
            "category": row["category"],
            "expected_direction": row["expected_direction"],
            "horizon": hz,
            "raw_mean_rank_ic": raw_ic,
            "direction_adjusted_mean_rank_ic": adj_ic,
            "rank_ic_std": round(rank_ic_std, 8) if rank_ic_std is not None else None,
            "icir": icir,
            "t_stat": row.get("t_stat"),
            "ic_win_rate_raw": round(ic_win_raw, 4) if ic_win_raw is not None else None,
            "ic_win_rate_adjusted": round(ic_win_adj, 4) if ic_win_adj is not None else None,
            "n_periods": row.get("n_periods"),
            "n_symbols_avg": row.get("n_symbols_avg"),
            "coverage": row.get("coverage"),
            "missing_rate": row.get("missing_rate"),
            "used_in_current_signal": row.get("used_in_current_signal"),
            "status": row["status"],
            "formula_proxy": row.get("notes", ""),
            "required_columns_if_available": "",
            "lookback_window_if_available": "",
            "notes": row.get("notes", ""),
            # Long-short fields
            "top_bucket_mean_return": ls_row.get("top_bucket_mean_return") if ls_row else None,
            "bottom_bucket_mean_return": ls_row.get("bottom_bucket_mean_return") if ls_row else None,
            "long_short_spread_mean": ls_row.get("long_short_spread_mean") if ls_row else None,
            "long_short_spread_t_stat": ls_row.get("long_short_spread_t_stat") if ls_row else None,
            "long_short_win_rate": ls_row.get("long_short_win_rate") if ls_row else None,
        })

    mp_df = pd.DataFrame(metric_rows)
    mp_csv_path = out_dir / f"factor_level_metric_panel{suffix}.csv"
    mp_df.to_csv(mp_csv_path, index=False)
    print(f"  Wrote {mp_csv_path} ({len(mp_df)} rows)", flush=True)

    mp_json_path = out_dir / f"factor_level_metric_panel{suffix}.json"
    with open(mp_json_path, "w") as f:
        json.dump(metric_rows, f, indent=2, default=str)
    print(f"  Wrote {mp_json_path}", flush=True)

    # C. Period IC summary (monthly)
    period_rows = []
    for (fid, hz), ts_ic_list in detailed_ics.items():
        spec_entry = next((r for r in registry if r["factor_id"] == fid), None)
        if not spec_entry:
            continue
        d = spec_entry["expected_direction"]

        # Group by month
        monthly = {}
        for ts, ic_val in ts_ic_list:
            if ts is None:
                continue
            period = pd.Timestamp(ts).strftime("%Y-%m")
            if period not in monthly:
                monthly[period] = []
            monthly[period].append(ic_val)

        for period, ics in sorted(monthly.items()):
            arr = np.array(ics)
            raw_mean = float(arr.mean())
            adj_mean = -raw_mean if d == "negative" else raw_mean
            std = float(arr.std(ddof=1)) if len(arr) > 1 else 0.0
            icir_val = round(raw_mean / std, 6) if std > 0 else None
            win_raw = float((arr > 0).sum() / len(arr))
            if d == "negative":
                adj_arr = -arr
            elif d == "positive":
                adj_arr = arr
            else:
                adj_arr = arr
            win_adj = float((adj_arr > 0).sum() / len(adj_arr))

            period_rows.append({
                "factor_name": fid,
                "category": spec_entry["category"],
                "expected_direction": d,
                "horizon": hz,
                "period": period,
                "raw_mean_rank_ic": round(raw_mean, 8),
                "direction_adjusted_mean_rank_ic": round(adj_mean, 8),
                "rank_ic_std": round(std, 8),
                "icir": icir_val,
                "ic_win_rate_raw": round(win_raw, 4),
                "ic_win_rate_adjusted": round(win_adj, 4),
                "n_periods": len(ics),
                "status": "COMPUTED",
            })

    period_df = pd.DataFrame(period_rows)
    period_csv_path = out_dir / f"factor_level_period_ic_summary{suffix}.csv"
    period_df.to_csv(period_csv_path, index=False)
    print(f"  Wrote {period_csv_path} ({len(period_df)} rows)", flush=True)

    # D. Quantile return summary
    qr_rows = [r for r in quantile_long_short if r.get("bucket") != "LONG_SHORT"]
    qr_df = pd.DataFrame(qr_rows)
    qr_csv_path = out_dir / f"factor_level_quantile_return_summary{suffix}.csv"
    qr_df.to_csv(qr_csv_path, index=False)
    print(f"  Wrote {qr_csv_path} ({len(qr_df)} rows)", flush=True)

    # E. Long-short summary
    ls_rows = [r for r in quantile_long_short if r.get("bucket") == "LONG_SHORT"]
    ls_df = pd.DataFrame(ls_rows)
    ls_csv_path = out_dir / f"factor_level_long_short_summary{suffix}.csv"
    ls_df.to_csv(ls_csv_path, index=False)
    print(f"  Wrote {ls_csv_path} ({len(ls_df)} rows)", flush=True)

    # F. Formula catalog
    formula_catalog_rows = []
    for spec_entry in registry:
        fid = spec_entry["factor_id"]
        fv_exists = (FEATURES_DIR / fid / "factor_values.parquet").exists()
        in_signal = fid in SIGNAL_FACTOR_IDS
        cat_row = cov_df[cov_df["factor_name"] == fid]
        cat_status = cat_row.iloc[0]["status"] if len(cat_row) > 0 else "UNKNOWN"
        cat_dir = spec_entry["expected_direction"]
        cat_cat = spec_entry["category"]

        if not fv_exists:
            fc_status = "MISSING_FACTOR_VALUES"
        elif in_signal:
            fc_status = "ACTIVE_IN_SIGNAL"
        elif cat_dir == "conditional":
            fc_status = "DIAGNOSTIC_ONLY"
        else:
            fc_status = "COMPUTED"

        formula_catalog_rows.append({
            "factor_name": fid,
            "category": cat_cat,
            "expected_direction": cat_dir,
            "formula_proxy": spec_entry["notes"],
            "notes": spec_entry["notes"],
            "used_in_current_signal": in_signal,
            "status": fc_status,
        })

    fc_df = pd.DataFrame(formula_catalog_rows)
    fc_csv_path = out_dir / f"factor_level_formula_catalog{suffix}.csv"
    fc_df.to_csv(fc_csv_path, index=False)
    print(f"  Wrote {fc_csv_path} ({len(fc_df)} rows)", flush=True)

    # Manifest
    computed_fids = df[df["status"].str.contains("COMPUTED", na=False)]["factor_name"].unique()
    # Also count factors with factor_values but non-COMPUTED status (e.g. DIRECTION_UNKNOWN)
    fids_with_fv = [fid for fid in df["factor_name"].unique()
                    if (FEATURES_DIR / fid / "factor_values.parquet").exists()
                    and fid not in missing_factors]
    manifest = {
        "phase": "13A-P1",
        "generated": datetime.now(timezone.utc).isoformat(),
        "run_mode": "partial" if is_partial else "full",
        "factor_ids": args.factor_ids if is_partial else "ALL",
        "canonical_output": not is_partial,
        "output_safety": "scratch_only" if is_partial else "canonical",
        "dataset_id": "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1",
        "labels_path": str(LABELS_PATH),
        "features_dir": str(FEATURES_DIR),
        "total_registered_factors": len(registry),
        "computed_factors": len(fids_with_fv),
        "missing_factor_values": len(missing_factors),
        "missing_factor_ids": missing_factors,
        "active_in_signal": len([r for r in registry if r["factor_id"] in SIGNAL_FACTOR_IDS]),
        "horizons": LABEL_HORIZONS,
        "evaluation_method": "RankIC (Spearman): rank per timestamp, Pearson of ranks",
        "direction_adjustment": "positive→raw, negative→-raw, conditional→raw (DIRECTION_UNKNOWN)",
        "new_outputs": [
            "factor_level_metric_panel.csv",
            "factor_level_metric_panel.json",
            "factor_level_period_ic_summary.csv",
            "factor_level_quantile_return_summary.csv",
            "factor_level_long_short_summary.csv",
            "factor_level_formula_catalog.csv",
        ],
        "elapsed_seconds": round(elapsed, 1),
        "disclaimer": "Factor-level IC, not signal-level. Not tradeable alpha.",
    }
    manifest_path = out_dir / f"factor_level_evaluation_manifest{suffix}.json"
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
