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
from funding_adjusted_labels import add_funding_adjusted_returns, infer_funding_aligned_path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_ID = "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
FEATURES_DIR = ROOT / "data" / "features" / DEFAULT_DATASET_ID
LABELS_PATH = FEATURES_DIR / "labels.parquet"
OUTPUT_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_level_evaluation"

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

LABEL_HORIZONS = ["1h", "4h", "24h", "72h"]
LABEL_COLS = {h: f"ret_fwd_{h}" for h in LABEL_HORIZONS}
AFTER_FUNDING_LABEL_COLS = {h: f"ret_fwd_{h}_after_funding" for h in LABEL_HORIZONS}
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


def validate_partial_factor_ids(factor_ids: list[str], registry_ids: set[str]) -> None:
    """Fail fast for unknown or explicitly skipped public factor IDs."""
    from public_factor_manifest_guard import raise_for_skipped_public_factor_ids
    raise_for_skipped_public_factor_ids(factor_ids, action="evaluated")
    missing = [fid for fid in factor_ids if fid not in registry_ids]
    if missing:
        raise ValueError(f"Factor IDs not in REGISTRY: {missing}")


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


def tail_diagnosis(mean_spread, median_spread, top_tail_share, bottom_tail_share) -> str:
    if mean_spread is None or pd.isna(mean_spread):
        return "INSUFFICIENT"
    med = 0.0 if median_spread is None or pd.isna(median_spread) else float(median_spread)
    mean = float(mean_spread)
    tail_share = max(
        0.0 if top_tail_share is None or pd.isna(top_tail_share) else float(top_tail_share),
        0.0 if bottom_tail_share is None or pd.isna(bottom_tail_share) else float(bottom_tail_share),
    )
    if mean > 0 and med > 0:
        return "DIRECTIONALLY_CLEAN_THIN_EDGE"
    if mean < 0 and med > 0:
        return "MEAN_SPREAD_OUTLIER_DOMINATED"
    if mean < 0 and med < 0 and tail_share >= 0.10:
        return "TAIL_CONCENTRATED_NEGATIVE_MEAN"
    if mean < 0 and med < 0:
        return "ROBUST_SPREAD_NEGATIVE"
    return "MIXED_OR_WEAK"


def tail_abs_share(values: pd.Series, q: float = 0.99) -> float | None:
    arr = values.dropna().abs()
    if len(arr) == 0:
        return None
    denom = float(arr.sum())
    if denom <= 0:
        return 0.0
    cutoff = float(arr.quantile(q))
    return float(arr[arr >= cutoff].sum() / denom)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--factor-ids", nargs="*",
                        help="Factor IDs to evaluate (space or comma separated)")
    parser.add_argument("--output-suffix", type=str, default=None,
                        help="Suffix for output files (e.g. 'scratch_rev3h'). Required for partial runs.")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Custom output directory. Required for partial runs.")
    parser.add_argument("--dataset-id", type=str, default=DEFAULT_DATASET_ID,
                        help="Dataset ID (default: %(default)s)")
    parser.add_argument("--funding-aligned-path", type=str, default=None,
                        help="Optional funding_rate_1h_aligned parquet path. Defaults from dataset id.")
    parser.add_argument("--skip-funding-adjusted", action="store_true",
                        help="Skip funding-adjusted label diagnostics.")
    args = parser.parse_args()

    # Resolve dataset-dependent paths
    features_dir = ROOT / "data" / "features" / args.dataset_id
    labels_path = features_dir / "labels.parquet"
    funding_aligned_path = (
        Path(args.funding_aligned_path)
        if args.funding_aligned_path
        else infer_funding_aligned_path(ROOT, args.dataset_id)
    )

    is_partial = bool(args.factor_ids)
    # Support comma-separated factor IDs (from post-intake workflow)
    if args.factor_ids and len(args.factor_ids) == 1 and "," in args.factor_ids[0]:
        args.factor_ids = [s.strip() for s in args.factor_ids[0].split(",") if s.strip()]

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

    # Validate partial factor IDs before loading large artifacts.
    registry = load_factor_registry()
    if args.factor_ids:
        try:
            validate_partial_factor_ids(
                args.factor_ids,
                {r["factor_id"] for r in registry},
            )
        except ValueError as exc:
            print(f"ERROR: {exc}", flush=True)
            sys.exit(1)

    print("Factor-Level IC Evaluation", flush=True)
    if is_partial:
        print(f"  Mode: PARTIAL ({len(args.factor_ids)} factors)", flush=True)
    else:
        print("  Mode: FULL (all registered factors)", flush=True)
    print(f"  Dataset:  {args.dataset_id}", flush=True)
    print(f"  Features: {features_dir}", flush=True)
    print(f"  Labels:   {labels_path}", flush=True)
    print(f"  Funding:  {'SKIPPED' if args.skip_funding_adjusted else funding_aligned_path}", flush=True)
    print(f"  Output:   {out_dir}\n", flush=True)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Filter registry for the requested partial run.
    if args.factor_ids:
        registry = [r for r in registry if r["factor_id"] in args.factor_ids]
    print(f"  Registered factors: {len(registry)}", flush=True)

    # Load labels (no pre-ranking — rank on merged subset to match API)
    print("  Loading labels...", end=" ", flush=True)
    if not labels_path.exists():
        print(f"\nERROR: labels file not found: {labels_path}", flush=True)
        print(f"  Dataset ID: {args.dataset_id}", flush=True)
        print(f"  Expected:   data/features/{args.dataset_id}/labels.parquet", flush=True)
        sys.exit(1)
    t0 = time.time()
    labels = pd.read_parquet(labels_path)
    labels["timestamp"] = pd.to_datetime(labels["timestamp"], utc=True)
    labels = labels.sort_values("timestamp").reset_index(drop=True)
    funding_manifest = {
        "status": "FUNDING_ADJUSTED_SKIPPED",
        "funding_aligned_path": str(funding_aligned_path),
        "coverage_by_horizon": [],
    }
    if not args.skip_funding_adjusted:
        labels, funding_manifest = add_funding_adjusted_returns(
            labels,
            funding_aligned_path,
            LABEL_HORIZONS,
        )
    label_keep_cols = ["timestamp", "symbol"] + list(LABEL_COLS.values())
    label_keep_cols += [c for c in AFTER_FUNDING_LABEL_COLS.values() if c in labels.columns]
    labels = labels[label_keep_cols]
    print(f"done ({time.time() - t0:.1f}s, {len(labels)} rows)\n", flush=True)

    results = []
    missing_factors = []
    detailed_ics = {}  # (fid, hz) -> list of (timestamp, ic_val)
    quantile_long_short = []  # quantile + long-short rows
    period_quantile_long_short = []  # period-level quantile + long-short rows
    t_start = time.time()

    for i, spec in enumerate(registry):
        fid = spec["factor_id"]
        print(f"  [{i + 1}/{len(registry)}] {fid}...", end=" ", flush=True)

        fv_path = features_dir / fid / "factor_values.parquet"
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
        merged = fv.merge(labels, on=["timestamp", "symbol"], how="inner", sort=False, copy=False)
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
        horizon_ics_after_funding = {}
        # Get the actual timestamps from merged data (sorted by group boundaries)
        ts_unique = merged["timestamp"].values[m_boundaries[:-1]]
        for hz in LABEL_HORIZONS:
            ret_rank = g_merged[LABEL_COLS[hz]].rank().values
            ic_vals, valid_ts_indices = rank_ic_from_boundaries(fv_rank, ret_rank, m_boundaries, n_ts_m)
            horizon_ics[hz] = summarize_ic(ic_vals)
            af_col = AFTER_FUNDING_LABEL_COLS[hz]
            if af_col in merged.columns:
                af_ret_rank = g_merged[af_col].rank().values
                af_ic_vals, _ = rank_ic_from_boundaries(fv_rank, af_ret_rank, m_boundaries, n_ts_m)
                horizon_ics_after_funding[hz] = summarize_ic(af_ic_vals)
            else:
                horizon_ics_after_funding[hz] = {"mean": None, "t_stat": None, "n_periods": 0}
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
            af_col = AFTER_FUNDING_LABEL_COLS[hz]
            if af_col in hz_merged.columns:
                bucket_ts_af = hz_merged.groupby(["timestamp", "bucket"])[af_col].mean().unstack(fill_value=np.nan)
            else:
                bucket_ts_af = pd.DataFrame(index=bucket_ts.index)

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

            af_ls_arr = None
            af_mean = af_median = af_t = af_win = af_top_mean = af_bot_mean = None
            af_coverage_rate = None
            af_top_tail_share = af_bottom_tail_share = None
            if QUANTILE_BUCKETS - 1 in bucket_ts_af.columns and 0 in bucket_ts_af.columns:
                af_ls_spread = (bucket_ts_af[QUANTILE_BUCKETS - 1] - bucket_ts_af[0]).dropna()
                af_ls_arr = af_ls_spread.values
                if len(af_ls_arr) > 0:
                    af_mean = float(af_ls_arr.mean())
                    af_median = float(np.median(af_ls_arr))
                    af_std = float(af_ls_arr.std(ddof=1)) if len(af_ls_arr) > 1 else 0.0
                    af_t = af_mean / (af_std / np.sqrt(len(af_ls_arr))) if af_std > 0 else 0.0
                    af_win = float((af_ls_arr > 0).sum() / len(af_ls_arr))
                    af_top = bucket_ts_af[QUANTILE_BUCKETS - 1].dropna()
                    af_bot = bucket_ts_af[0].dropna()
                    af_top_mean = float(af_top.mean()) if len(af_top) else None
                    af_bot_mean = float(af_bot.mean()) if len(af_bot) else None
                    af_top_tail_share = tail_abs_share(af_top)
                    af_bottom_tail_share = tail_abs_share(af_bot)
                    af_coverage_rate = len(af_ls_spread) / len(ls_spread) if len(ls_spread) else None

            ls_median = float(np.median(ls_arr)) if ls_arr is not None and len(ls_arr) > 0 else None
            top_tail_share = tail_abs_share(bucket_ts[QUANTILE_BUCKETS - 1]) if QUANTILE_BUCKETS - 1 in bucket_ts.columns else None
            bottom_tail_share = tail_abs_share(bucket_ts[0]) if 0 in bucket_ts.columns else None
            price_tail_label = tail_diagnosis(ls_mean, ls_median, top_tail_share, bottom_tail_share)
            af_tail_label = tail_diagnosis(af_mean, af_median, af_top_tail_share, af_bottom_tail_share)
            funding_flip = (
                ls_mean is not None and af_mean is not None
                and np.sign(ls_mean) != 0 and np.sign(af_mean) != 0
                and np.sign(ls_mean) != np.sign(af_mean)
            )

            ls_status = base_status
            # PM-41: LS summary row is appended AFTER the period loop
            # so we can include monthly aggregate stats.
            _ls_summary_pending = {
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
                "long_short_spread_median": round(ls_median, 8) if ls_median is not None else None,
                "long_short_spread_t_stat": round(ls_t, 4) if ls_t is not None else None,
                "long_short_win_rate": round(ls_win, 4) if ls_win is not None else None,
                "top_bucket_top1pct_abs_share": round(top_tail_share, 6) if top_tail_share is not None else None,
                "bottom_bucket_top1pct_abs_share": round(bottom_tail_share, 6) if bottom_tail_share is not None else None,
                "bucket_tail_diagnosis": price_tail_label,
                "after_funding_top_bucket_mean_return": round(af_top_mean, 8) if af_top_mean is not None else None,
                "after_funding_bottom_bucket_mean_return": round(af_bot_mean, 8) if af_bot_mean is not None else None,
                "after_funding_long_short_spread_mean": round(af_mean, 8) if af_mean is not None else None,
                "after_funding_long_short_spread_median": round(af_median, 8) if af_median is not None else None,
                "after_funding_long_short_spread_t_stat": round(af_t, 4) if af_t is not None else None,
                "after_funding_long_short_win_rate": round(af_win, 4) if af_win is not None else None,
                "after_funding_coverage_rate": round(af_coverage_rate, 6) if af_coverage_rate is not None else None,
                "after_funding_bucket_tail_diagnosis": af_tail_label,
                "funding_adjusted_edge_flip": bool(funding_flip),
                # PM-41: monthly aggregate fields (populated after period loop)
                "long_short_spread_std": None,
                "long_short_spread_annualized_return": None,
                "long_short_spread_annualized_vol": None,
                "long_short_spread_max_drawdown": None,
                "long_short_spread_positive_period_rate": None,
                "n_monthly_periods": 0,
                "annualization_method": "per_bar_mean_x_bars_per_year",
            }

            # --- Period-level (monthly) quantile returns and long-short ---
            monthly_ls_returns = []  # PM-41: collect monthly LS for aggregate stats
            bucket_ts_period = bucket_ts.copy()
            bucket_ts_period.index = pd.to_datetime(bucket_ts_period.index)
            bucket_ts_period["_period"] = bucket_ts_period.index.tz_convert(None).to_period("M")

            for period_val, period_grp in bucket_ts_period.groupby("_period"):
                period_str = str(period_val)
                # Per-bucket period stats
                for b in range(QUANTILE_BUCKETS):
                    if b in period_grp.columns:
                        pbr = period_grp[b].dropna()
                        if len(pbr) > 0:
                            period_quantile_long_short.append({
                                "factor_name": fid, "category": spec["category"],
                                "expected_direction": spec["expected_direction"],
                                "horizon": hz, "period": period_str,
                                "bucket": b, "bucket_label": f"Q{b+1}",
                                "mean_forward_return": round(float(pbr.mean()), 8),
                                "median_forward_return": round(float(pbr.median()), 8),
                                "n_timestamps": int(len(pbr)),
                                "n_obs": None,
                                "status": base_status,
                            })

                # Period long-short
                if QUANTILE_BUCKETS - 1 in period_grp.columns and 0 in period_grp.columns:
                    p_ls = period_grp[QUANTILE_BUCKETS - 1] - period_grp[0]
                    p_ls = p_ls.dropna()
                    if len(p_ls) > 0:
                        p_ls_mean = float(p_ls.mean())
                        p_top_mean = float(period_grp[QUANTILE_BUCKETS - 1].dropna().mean()) if len(period_grp[QUANTILE_BUCKETS - 1].dropna()) > 0 else None
                        p_bot_mean = float(period_grp[0].dropna().mean()) if len(period_grp[0].dropna()) > 0 else None
                        period_quantile_long_short.append({
                            "factor_name": fid, "category": spec["category"],
                            "expected_direction": spec["expected_direction"],
                            "horizon": hz, "period": period_str,
                            "bucket": "LONG_SHORT", "bucket_label": "Long-Short",
                            "mean_forward_return": round(p_ls_mean, 8),
                            "median_forward_return": None,
                            "n_timestamps": int(len(p_ls)),
                            "n_obs": None,
                            "status": base_status,
                            "long_short_return": round(p_ls_mean, 8),
                            "long_leg_return": round(p_top_mean, 8) if p_top_mean is not None else None,
                            "short_leg_return": round(p_bot_mean, 8) if p_bot_mean is not None else None,
                            "positive_ls": bool(p_ls_mean > 0),
                        })
                        monthly_ls_returns.append(p_ls_mean)  # PM-41: collect for aggregate

            # PM-41: Compute LS aggregate stats from monthly period returns
            if _ls_summary_pending is not None:
                if monthly_ls_returns and len(monthly_ls_returns) >= 2:
                    import numpy as _np
                    _ls_arr_monthly = _np.array(monthly_ls_returns, dtype=float)
                    _ls_std_m = float(_ls_arr_monthly.std(ddof=1))
                    _ls_mean_m = float(_ls_arr_monthly.mean())
                    _n_m = len(_ls_arr_monthly)
                    _BARS_PER_YEAR = {"1h": 8760, "4h": 2190, "24h": 365, "72h": 365 / 3}
                    _bpy = _BARS_PER_YEAR.get(hz, 8760)
                    # Ann Return: per-bar LS mean × bars_per_year (horizon-aware annualization)
                    _ls_ann_ret = _ls_mean_m * _bpy
                    # Sharpe/Vol: monthly edge stability metrics × √12
                    # These are NOT portfolio Sharpe/Vol — they measure per-bar LS return stability.
                    _ls_ann_vol = _ls_std_m * _np.sqrt(12)
                    _ls_cum = _np.cumprod(1 + _ls_arr_monthly)
                    _ls_peak = _np.maximum.accumulate(_ls_cum)
                    _ls_dd = (_ls_cum - _ls_peak) / _ls_peak
                    _ls_max_dd = float(_ls_dd.min())
                    _ls_pos_rate = float((_ls_arr_monthly > 0).sum() / _n_m)
                    _ls_summary_pending["long_short_spread_std"] = round(_ls_std_m, 8)
                    _ls_summary_pending["long_short_spread_annualized_return"] = round(_ls_ann_ret, 8)
                    _ls_summary_pending["long_short_spread_annualized_vol"] = round(_ls_ann_vol, 8)
                    _ls_summary_pending["long_short_spread_max_drawdown"] = round(_ls_max_dd, 8)
                    _ls_summary_pending["long_short_spread_positive_period_rate"] = round(_ls_pos_rate, 4)
                    _ls_summary_pending["n_monthly_periods"] = _n_m
                quantile_long_short.append(_ls_summary_pending)

        # Print summary and build results
        d = spec["expected_direction"]
        any_computed = False
        for hz in LABEL_HORIZONS:
            ic = horizon_ics[hz]
            af_ic = horizon_ics_after_funding.get(hz, {"mean": None, "t_stat": None, "n_periods": 0})
            if ic["n_periods"] > 0:
                any_computed = True
                raw = ic["mean"]
                adj = -raw if d == "negative" else raw
                af_raw = af_ic["mean"]
                af_adj = -af_raw if (af_raw is not None and d == "negative") else af_raw
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
                    "after_funding_raw_mean_rank_ic": round(af_raw, 8) if af_raw is not None else None,
                    "after_funding_direction_adjusted_mean_rank_ic": round(af_adj, 8) if af_adj is not None else None,
                    "after_funding_t_stat": round(af_ic["t_stat"], 4) if af_ic.get("t_stat") is not None else None,
                    "after_funding_n_periods": af_ic.get("n_periods", 0),
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
                    "after_funding_raw_mean_rank_ic": None,
                    "after_funding_direction_adjusted_mean_rank_ic": None,
                    "after_funding_t_stat": None,
                    "after_funding_n_periods": 0,
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
        af_raw_ic = row.get("after_funding_raw_mean_rank_ic")
        af_adj_ic = row.get("after_funding_direction_adjusted_mean_rank_ic")
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
            "after_funding_raw_mean_rank_ic": af_raw_ic,
            "after_funding_direction_adjusted_mean_rank_ic": af_adj_ic,
            "after_funding_t_stat": row.get("after_funding_t_stat"),
            "after_funding_n_periods": row.get("after_funding_n_periods"),
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
            "long_short_spread_median": ls_row.get("long_short_spread_median") if ls_row else None,
            "long_short_spread_t_stat": ls_row.get("long_short_spread_t_stat") if ls_row else None,
            "long_short_win_rate": ls_row.get("long_short_win_rate") if ls_row else None,
            "top_bucket_top1pct_abs_share": ls_row.get("top_bucket_top1pct_abs_share") if ls_row else None,
            "bottom_bucket_top1pct_abs_share": ls_row.get("bottom_bucket_top1pct_abs_share") if ls_row else None,
            "bucket_tail_diagnosis": ls_row.get("bucket_tail_diagnosis") if ls_row else None,
            "after_funding_top_bucket_mean_return": ls_row.get("after_funding_top_bucket_mean_return") if ls_row else None,
            "after_funding_bottom_bucket_mean_return": ls_row.get("after_funding_bottom_bucket_mean_return") if ls_row else None,
            "after_funding_long_short_spread_mean": ls_row.get("after_funding_long_short_spread_mean") if ls_row else None,
            "after_funding_long_short_spread_median": ls_row.get("after_funding_long_short_spread_median") if ls_row else None,
            "after_funding_long_short_spread_t_stat": ls_row.get("after_funding_long_short_spread_t_stat") if ls_row else None,
            "after_funding_long_short_win_rate": ls_row.get("after_funding_long_short_win_rate") if ls_row else None,
            "after_funding_coverage_rate": ls_row.get("after_funding_coverage_rate") if ls_row else None,
            "after_funding_bucket_tail_diagnosis": ls_row.get("after_funding_bucket_tail_diagnosis") if ls_row else None,
            "funding_adjusted_edge_flip": ls_row.get("funding_adjusted_edge_flip") if ls_row else None,
            # PM-41: LS aggregate fields from monthly period returns
            "long_short_spread_std": ls_row.get("long_short_spread_std") if ls_row else None,
            "long_short_spread_annualized_return": ls_row.get("long_short_spread_annualized_return") if ls_row else None,
            "long_short_spread_annualized_vol": ls_row.get("long_short_spread_annualized_vol") if ls_row else None,
            "long_short_spread_max_drawdown": ls_row.get("long_short_spread_max_drawdown") if ls_row else None,
            "long_short_spread_positive_period_rate": ls_row.get("long_short_spread_positive_period_rate") if ls_row else None,
            "n_monthly_periods": ls_row.get("n_monthly_periods") if ls_row else None,
            "annualization_method": ls_row.get("annualization_method") if ls_row else None,
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

    # D2. Period-level quantile return summary (monthly)
    pqr_rows = [r for r in period_quantile_long_short if r.get("bucket") != "LONG_SHORT"]
    pqr_df = pd.DataFrame(pqr_rows)
    pqr_csv_path = out_dir / f"factor_level_period_quantile_return_summary{suffix}.csv"
    pqr_df.to_csv(pqr_csv_path, index=False)
    print(f"  Wrote {pqr_csv_path} ({len(pqr_df)} rows)", flush=True)

    # E2. Period-level long-short summary (monthly)
    pls_rows = [r for r in period_quantile_long_short if r.get("bucket") == "LONG_SHORT"]
    pls_df = pd.DataFrame(pls_rows)
    pls_csv_path = out_dir / f"factor_level_period_long_short_summary{suffix}.csv"
    pls_df.to_csv(pls_csv_path, index=False)
    print(f"  Wrote {pls_csv_path} ({len(pls_df)} rows)", flush=True)

    # F. Formula catalog
    formula_catalog_rows = []
    for spec_entry in registry:
        fid = spec_entry["factor_id"]
        fv_exists = (features_dir / fid / "factor_values.parquet").exists()
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
        fv_exists = (features_dir / fid / "factor_values.parquet").exists()

        # Best adjusted IC across horizons
        best_adj_ic = None
        best_adj_ic_hz = None
        best_adj_icir = None
        best_adj_icir_hz = None
        best_ls_spread = None
        best_ls_hz = None
        best_ls_t = None
        best_af_ls_spread = None
        best_af_ls_hz = None
        best_af_coverage = None
        best_tail_label = None
        best_af_tail_label = None
        any_funding_flip = False
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
                af_ls_val = r.get("after_funding_long_short_spread_mean")
                af_cov_val = r.get("after_funding_coverage_rate")
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
                    best_tail_label = r.get("bucket_tail_diagnosis")
                    best_af_tail_label = r.get("after_funding_bucket_tail_diagnosis")
                if pd.notna(af_ls_val) and (best_af_ls_spread is None or abs(af_ls_val) > abs(best_af_ls_spread)):
                    best_af_ls_spread = af_ls_val
                    best_af_ls_hz = hz
                    best_af_coverage = af_cov_val if pd.notna(af_cov_val) else None
                if bool(r.get("funding_adjusted_edge_flip")):
                    any_funding_flip = True
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

        review_reasons = []
        if best_af_coverage is not None and best_af_coverage < 0.80:
            review_reasons.append("funding coverage insufficient")
        if any_funding_flip:
            review_reasons.append("funding-adjusted edge flips")
        if best_af_ls_spread is not None and best_ls_spread is not None and best_ls_spread > 0 and best_af_ls_spread <= 0:
            review_reasons.append("positive price-only spread turns non-positive after funding")
        if rl_consistency == "DIVERGENT":
            review_reasons.append("RankIC/spread direction conflict")
        if best_tail_label in {"TAIL_CONCENTRATED_NEGATIVE_MEAN", "MEAN_SPREAD_OUTLIER_DOMINATED"}:
            review_reasons.append(best_tail_label.lower())
        if best_af_tail_label in {"TAIL_CONCENTRATED_NEGATIVE_MEAN", "MEAN_SPREAD_OUTLIER_DOMINATED"}:
            review_reasons.append("after_funding_" + str(best_af_tail_label).lower())
        if best_ls_spread is not None and abs(best_ls_spread) < 0.0002:
            review_reasons.append("cost too thin")

        # Review bucket
        if not fv_exists:
            review_bucket = "MISSING_INPUT"
            review_notes = "Factor values not computed; raw bars lack required columns."
        elif in_signal:
            review_bucket = "ACTIVE_IN_SIGNAL_REVIEW"
            review_notes = "Currently used in current research signal panel. Review before modifying."
        elif d == "conditional":
            if best_adj_ic is not None and abs(best_adj_ic) >= 0.02:
                review_bucket = "CONDITIONAL_DIRECTION_REVIEW"
                review_notes = "Conditional direction but shows IC signal strength."
            else:
                review_bucket = "CONDITIONAL_DIRECTION_REVIEW"
                review_notes = "Conditional direction; weak or no clear IC signal."
        elif any_funding_flip or (best_af_ls_spread is not None and best_ls_spread is not None and best_ls_spread > 0 and best_af_ls_spread <= 0):
            review_bucket = "FUNDING_ADJUSTED_REVIEW_REQUIRED"
            review_notes = "Price-only edge weakens or flips after funding adjustment. Do not use price-only spread as economic evidence."
        elif rl_consistency == "DIVERGENT" and best_adj_ic is not None and abs(best_adj_ic) >= 0.02:
            review_bucket = "DIRECTION_REVIEW_REQUIRED"
            review_notes = "RankIC and long-short spread point in opposite directions. Direction semantics need review."
        elif rl_consistency == "DIVERGENT":
            review_bucket = "TAIL_OR_MONOTONICITY_REVIEW_REQUIRED"
            review_notes = "RankIC-longshort divergence detected. Check quantile monotonicity and tail behavior."
        elif best_tail_label in {"TAIL_CONCENTRATED_NEGATIVE_MEAN", "MEAN_SPREAD_OUTLIER_DOMINATED"}:
            review_bucket = "TAIL_OR_MONOTONICITY_REVIEW_REQUIRED"
            review_notes = "Bucket tail diagnostics show mean/median split or tail-concentrated negative mean."
        elif best_adj_ic is not None and abs(best_adj_ic) >= 0.02 and best_ls_spread is not None and best_ls_t is not None and abs(best_ls_t) >= 2.0:
            review_bucket = "STRONG_DIAGNOSTIC_CANDIDATE"
            review_notes = "Strong RankIC and significant long-short spread. Consistent signals."
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
            "best_after_funding_long_short_horizon": best_af_ls_hz,
            "best_after_funding_long_short_spread": round(float(best_af_ls_spread), 8) if best_af_ls_spread is not None else None,
            "best_after_funding_coverage_rate": round(float(best_af_coverage), 6) if best_af_coverage is not None else None,
            "best_bucket_tail_diagnosis": best_tail_label,
            "best_after_funding_bucket_tail_diagnosis": best_af_tail_label,
            "funding_adjusted_edge_flip": any_funding_flip,
            "best_ic_win_rate_adjusted": round(float(best_win_adj), 4) if best_win_adj is not None else None,
            "coverage_min": cov_min,
            "missing_rate_max": miss_max,
            "direction_status": direction_status,
            "rankic_longshort_consistency": rl_consistency,
            "review_bucket": review_bucket,
            "review_reasons": "|".join(sorted(set(review_reasons))),
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
                    if (features_dir / fid / "factor_values.parquet").exists()
                    and fid not in missing_factors]
    manifest = {
        "phase": "13A-P1",
        "generated": datetime.now(timezone.utc).isoformat(),
        "run_mode": "partial" if is_partial else "full",
        "factor_ids": args.factor_ids if is_partial else "ALL",
        "canonical_output": not is_partial,
        "output_safety": "scratch_only" if is_partial else "canonical",
        "dataset_id": args.dataset_id,
        "labels_path": str(labels_path),
        "funding_adjustment": funding_manifest,
        "features_dir": str(features_dir),
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
        "funding_aware_outputs": [
            "after_funding_* columns in factor_level_rankic_summary.csv",
            "after_funding_* columns in factor_level_metric_panel.csv",
            "after_funding_* and bucket_tail_diagnosis columns in factor_level_long_short_summary.csv",
            "funding/cost/tail review reasons in factor_level_candidate_review.csv",
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
