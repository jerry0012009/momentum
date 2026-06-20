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
        "required_columns": getattr(fs, "required_columns", []),
        "lookback_window": getattr(fs, "lookback_window", None),
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
        d = row["expected_direction"]

        # Look up required_columns and lookback_window from registry
        spec_entry = next((r for r in registry if r["factor_id"] == fid), None)
        req_cols = spec_entry.get("required_columns", []) if spec_entry else []
        lb_window = spec_entry.get("lookback_window", None) if spec_entry else None
        req_cols_str = "|".join(req_cols) if req_cols else ""

        if ic_list_raw and len(ic_list_raw) > 1:
            ic_arr = np.array(ic_list_raw)
            raw_rank_ic_std = float(ic_arr.std(ddof=1))
            raw_mean = float(ic_arr.mean())
            raw_icir = round(raw_mean / raw_rank_ic_std, 6) if raw_rank_ic_std > 0 else None
            ic_win_raw = float((ic_arr > 0).sum() / len(ic_arr))
            # Direction-adjusted IC series
            if d == "negative":
                adj_arr = -ic_arr
            elif d == "positive":
                adj_arr = ic_arr
            else:
                adj_arr = ic_arr  # conditional → raw
            adj_rank_ic_std = float(adj_arr.std(ddof=1))
            adj_mean = float(adj_arr.mean())
            adj_icir = round(adj_mean / adj_rank_ic_std, 6) if adj_rank_ic_std > 0 else None
            ic_win_adj = float((adj_arr > 0).sum() / len(adj_arr))
        else:
            raw_rank_ic_std = None
            raw_icir = None
            adj_rank_ic_std = None
            adj_icir = None
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
            "raw_rank_ic_std": round(raw_rank_ic_std, 8) if raw_rank_ic_std is not None else None,
            "direction_adjusted_rank_ic_std": round(adj_rank_ic_std, 8) if adj_rank_ic_std is not None else None,
            "raw_icir": raw_icir,
            "direction_adjusted_icir": adj_icir,
            "icir": raw_icir,  # backward-compat alias
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
            "required_columns": req_cols_str,
            "lookback_window": lb_window,
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

            # Direction-adjusted ICIR for period
            adj_std = float(adj_arr.std(ddof=1)) if len(adj_arr) > 1 else 0.0
            adj_icir_val = round(float(adj_arr.mean()) / adj_std, 6) if adj_std > 0 else None

            period_rows.append({
                "factor_name": fid,
                "category": spec_entry["category"],
                "expected_direction": d,
                "horizon": hz,
                "period": period,
                "raw_mean_rank_ic": round(raw_mean, 8),
                "direction_adjusted_mean_rank_ic": round(adj_mean, 8),
                "raw_rank_ic_std": round(std, 8),
                "direction_adjusted_rank_ic_std": round(adj_std, 8),
                "raw_icir": icir_val,
                "direction_adjusted_icir": adj_icir_val,
                "icir": icir_val,  # backward-compat alias
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

    # G. Candidate review (one row per factor)
    review_rows = []
    for spec_entry in registry:
        fid = spec_entry["factor_id"]
        d = spec_entry["expected_direction"]
        cat = spec_entry["category"]
        in_signal = fid in SIGNAL_FACTOR_IDS
        req_cols = spec_entry.get("required_columns", [])
        lb_window = spec_entry.get("lookback_window", None)
        req_cols_str = "|".join(req_cols) if req_cols else ""

        fdf = mp_df[mp_df["factor_name"] == fid]
        fv_exists = (FEATURES_DIR / fid / "factor_values.parquet").exists()

        # Best adjusted IC across horizons
        best_adj_ic = None
        best_adj_ic_hz = None
        best_adj_icir = None
        best_adj_icir_hz = None
        best_ls_spread = None
        best_ls_hz = None
        best_ls_t = None
        best_win_adj = None
        cov_min = None
        miss_max = None

        if len(fdf) > 0 and fv_exists:
            for hz in LABEL_HORIZONS:
                hz_row = fdf[fdf["horizon"] == hz]
                if len(hz_row) == 0:
                    continue
                r = hz_row.iloc[0]
                adj_val = r.get("direction_adjusted_mean_rank_ic")
                adj_icir_val = r.get("direction_adjusted_icir")
                ls_val = r.get("long_short_spread_mean")
                ls_t_val = r.get("long_short_spread_t_stat")
                win_val = r.get("ic_win_rate_adjusted")
                cov_val = r.get("coverage")
                miss_val = r.get("missing_rate")

                if pd.notna(adj_val) and (best_adj_ic is None or abs(adj_val) > abs(best_adj_ic)):
                    best_adj_ic = adj_val
                    best_adj_ic_hz = hz
                if pd.notna(adj_icir_val) and (best_adj_icir is None or abs(adj_icir_val) > abs(best_adj_icir)):
                    best_adj_icir = adj_icir_val
                    best_adj_icir_hz = hz
                if pd.notna(ls_val) and pd.notna(ls_t_val) and (best_ls_spread is None or abs(ls_val) > abs(best_ls_spread)):
                    best_ls_spread = ls_val
                    best_ls_hz = hz
                    best_ls_t = ls_t_val
                if pd.notna(win_val) and (best_win_adj is None or win_val > best_win_adj):
                    best_win_adj = win_val
                if pd.notna(cov_val) and (cov_min is None or cov_val < cov_min):
                    cov_min = cov_val
                if pd.notna(miss_val) and (miss_max is None or miss_val > miss_max):
                    miss_max = miss_val

        # Direction status
        if d == "conditional":
            direction_status = "CONDITIONAL"
        elif d in ("positive", "negative"):
            direction_status = "KNOWN"
        else:
            direction_status = "UNKNOWN"

        # RankIC-LongShort consistency
        rl_consistency = "N/A"
        if best_adj_ic is not None and best_ls_spread is not None:
            ic_sign = 1 if best_adj_ic > 0 else -1
            ls_sign = 1 if best_ls_spread > 0 else -1
            if ic_sign == ls_sign:
                rl_consistency = "CONSISTENT"
            else:
                rl_consistency = "DIVERGENT"

        # Review bucket
        if not fv_exists:
            review_bucket = "MISSING_INPUT"
            review_notes = "Factor values not computed; raw bars lack required columns."
        elif in_signal:
            review_bucket = "ACTIVE_IN_SIGNAL_REVIEW"
            review_notes = "Currently used in production signal. Review before modifying."
        elif d == "conditional":
            if best_adj_ic is not None and abs(best_adj_ic) >= 0.02:
                review_bucket = "CONDITIONAL_DIRECTION_REVIEW"
                review_notes = "Conditional direction but shows IC signal strength."
            else:
                review_bucket = "CONDITIONAL_DIRECTION_REVIEW"
                review_notes = "Conditional direction; weak or no clear IC signal."
        elif best_adj_ic is not None and abs(best_adj_ic) >= 0.02 and best_ls_spread is not None and best_ls_t is not None and abs(best_ls_t) >= 2.0:
            review_bucket = "STRONG_DIAGNOSTIC_CANDIDATE"
            review_notes = "Strong RankIC and significant long-short spread."
        elif best_adj_ic is not None and abs(best_adj_ic) >= 0.02 and (best_ls_spread is None or best_ls_t is None or abs(best_ls_t) < 2.0):
            review_bucket = "RANKIC_STRONG_LONGSHORT_WEAK"
            review_notes = "RankIC suggests signal but long-short spread not significant."
        elif best_ls_spread is not None and best_ls_t is not None and abs(best_ls_t) >= 2.0 and (best_adj_ic is None or abs(best_adj_ic) < 0.015):
            review_bucket = "LONGSHORT_STRONG_RANKIC_WEAK"
            review_notes = "Long-short spread significant but RankIC weak."
        elif best_adj_ic is not None and abs(best_adj_ic) < 0.01:
            review_bucket = "WEAK_OR_NOISY"
            review_notes = "Adjusted IC below 0.01 across all horizons."
        else:
            review_bucket = "METADATA_REVIEW"
            review_notes = "Needs manual review for classification."

        review_rows.append({
            "factor_name": fid,
            "category": cat,
            "expected_direction": d,
            "status": fdf.iloc[0]["status"] if len(fdf) > 0 else ("MISSING_FACTOR_VALUES" if not fv_exists else "UNKNOWN"),
            "used_in_current_signal": in_signal,
            "required_columns": req_cols_str,
            "lookback_window": lb_window,
            "best_adj_ic_horizon": best_adj_ic_hz,
            "best_adj_ic": round(float(best_adj_ic), 8) if best_adj_ic is not None else None,
            "best_direction_adjusted_icir_horizon": best_adj_icir_hz,
            "best_direction_adjusted_icir": round(float(best_adj_icir), 6) if best_adj_icir is not None else None,
            "best_long_short_horizon": best_ls_hz,
            "best_long_short_spread": round(float(best_ls_spread), 8) if best_ls_spread is not None else None,
            "best_long_short_t_stat": round(float(best_ls_t), 4) if best_ls_t is not None else None,
            "best_ic_win_rate_adjusted": round(float(best_win_adj), 4) if best_win_adj is not None else None,
            "coverage_min": cov_min,
            "missing_rate_max": miss_max,
            "direction_status": direction_status,
            "rankic_longshort_consistency": rl_consistency,
            "review_bucket": review_bucket,
            "review_notes": review_notes,
        })

    review_df = pd.DataFrame(review_rows)
    review_csv_path = out_dir / f"factor_level_candidate_review{suffix}.csv"
    review_df.to_csv(review_csv_path, index=False)
    print(f"  Wrote {review_csv_path} ({len(review_df)} rows)", flush=True)

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
            "factor_level_candidate_review.csv",
        ],
        "raw_icir_definition": "mean(raw per-timestamp RankIC) / std(raw per-timestamp RankIC)",
        "direction_adjusted_icir_definition": "mean(direction-adjusted per-timestamp RankIC) / std(direction-adjusted per-timestamp RankIC); positive→raw, negative→-raw, conditional→raw",
        "candidate_review_output": "factor_level_candidate_review.csv",
        "required_columns_source": "FactorSpec.required_columns via factor_formula_registry.py",
        "lookback_window_source": "FactorSpec.lookback_window via factor_formula_registry.py",
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
