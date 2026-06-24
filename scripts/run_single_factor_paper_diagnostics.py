#!/usr/bin/env python3
"""Single-Factor Paper Portfolio Diagnostics.

For each registered factor, builds a cross-sectional long-short paper portfolio
(top quintile long, bottom quintile short, equal-weighted), then computes
diagnostic metrics:

  - Per-timestamp portfolio return (long - short spread)
  - Cumulative equity curve & max drawdown
  - Monthly returns & Sharpe ratios
  - Turnover (cross-sectional rank change between adjacent timestamps)
  - Rolling 30-day Sharpe
  - Calmar ratio, Sortino ratio
  - Drawdown duration

All outputs are diagnostic-only. No real execution. No exchange connection.

Usage:
    python scripts/run_single_factor_paper_diagnostics.py
    python scripts/run_single_factor_paper_diagnostics.py --factor-ids mom_20h reversal_5h
    python scripts/run_single_factor_paper_diagnostics.py --horizon 1h
    python scripts/run_single_factor_paper_diagnostics.py --n-buckets 5
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_ID = "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
FEATURES_DIR = ROOT / "data" / "features" / DEFAULT_DATASET_ID
LABELS_PATH = FEATURES_DIR / "labels.parquet"
OUTPUT_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "paper_portfolio_diagnostics"

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

# ── Constants ────────────────────────────────────────────────────────
LABEL_HORIZONS = ["1h", "4h", "24h", "72h"]
LABEL_COLS = {h: f"ret_fwd_{h}" for h in LABEL_HORIZONS}
MIN_SYMBOLS_PER_TS = 10
DEFAULT_N_BUCKETS = 5
TOP_BUCKET_FRAC = 0.20  # top 20%
BOT_BUCKET_FRAC = 0.20  # bottom 20%
ROLLING_SHARPE_WINDOW = 30 * 24  # 30 days in hourly bars for 1h horizon


def load_factor_registry() -> list[dict]:
    """Load factor metadata from registry."""
    from factor_formula_registry import REGISTRY
    return [{
        "factor_id": fs.factor_id,
        "family": getattr(fs, "family", "unknown"),
        "expected_direction": getattr(fs, "expected_direction", "conditional"),
    } for fs in REGISTRY]


def compute_turnover(prev_ranks: np.ndarray, curr_ranks: np.ndarray) -> float:
    """Compute cross-sectional turnover: 1 - Spearman(prev, curr).

    Returns NaN if either series is all-NaN or has insufficient data.
    """
    valid = ~(np.isnan(prev_ranks) | np.isnan(curr_ranks))
    x, y = prev_ranks[valid], curr_ranks[valid]
    if len(x) < 5:
        return np.nan
    xm, ym = x.mean(), y.mean()
    dx, dy = x - xm, y - ym
    denom = np.sqrt((dx * dx).sum() * (dy * dy).sum())
    if denom <= 0:
        return np.nan
    rho = (dx * dy).sum() / denom
    return 1.0 - rho


def compute_max_drawdown(cum_returns: np.ndarray) -> tuple[float, int, int]:
    """Compute max drawdown from cumulative returns array.

    Returns (max_dd, peak_idx, trough_idx).
    """
    if len(cum_returns) == 0:
        return 0.0, 0, 0
    running_max = np.maximum.accumulate(cum_returns)
    drawdowns = cum_returns - running_max
    trough_idx = int(np.argmin(drawdowns))
    peak_idx = int(np.argmax(cum_returns[:trough_idx + 1]))
    return float(drawdowns[trough_idx]), peak_idx, trough_idx


def compute_drawdown_durations(cum_returns: np.ndarray) -> tuple[int, int]:
    """Compute max drawdown duration and current drawdown duration (in bars).

    A drawdown period starts when cum_return drops below running max and
    ends when cum_return exceeds the previous peak.
    """
    if len(cum_returns) < 2:
        return 0, 0
    running_max = np.maximum.accumulate(cum_returns)
    in_dd = cum_returns < running_max

    max_dur = 0
    curr_dur = 0
    for v in in_dd:
        if v:
            curr_dur += 1
            max_dur = max(max_dur, curr_dur)
        else:
            curr_dur = 0
    return max_dur, curr_dur


def build_portfolio_returns(
    factor_values: pd.DataFrame,
    labels: pd.DataFrame,
    horizon: str,
    expected_direction: str,
    n_buckets: int = DEFAULT_N_BUCKETS,
    skip_turnover: bool = False,
) -> pd.DataFrame:
    """Build per-timestamp long-short portfolio returns for a single factor.

    Returns DataFrame with columns:
        timestamp, ls_return, long_return, short_return, n_symbols, turnover
    """
    ret_col = LABEL_COLS[horizon]

    # Merge factor values with labels
    merged = factor_values.merge(labels[["timestamp", "symbol", ret_col]],
                                  on=["timestamp", "symbol"], how="inner")
    merged = merged.dropna(subset=["factor_value", ret_col])
    if len(merged) == 0:
        return pd.DataFrame()

    merged = merged.sort_values(["timestamp", "symbol"]).reset_index(drop=True)

    # Direction-adjust: if expected_direction is "negative", negate the factor
    # so that higher = better, consistent with long top / short bottom
    if expected_direction == "negative":
        merged["_sort_val"] = -merged["factor_value"]
    else:
        merged["_sort_val"] = merged["factor_value"]

    # Cross-sectional rank per timestamp (vectorized)
    merged["_rank"] = merged.groupby("timestamp")["_sort_val"].rank(method="first")
    merged["_count"] = merged.groupby("timestamp")["_sort_val"].transform("count")

    # Assign to quantile buckets
    merged["bucket"] = ((merged["_rank"] - 1) * n_buckets / merged["_count"]).astype(int).clip(0, n_buckets - 1)

    # Compute per-timestamp bucket returns (vectorized groupby)
    bucket_ts = merged.groupby(["timestamp", "bucket"])[ret_col].mean().unstack(fill_value=np.nan)

    top_b = n_buckets - 1
    bot_b = 0

    # Build vectorized results
    timestamps_sorted = bucket_ts.index.sort_values()
    long_rets = bucket_ts.loc[timestamps_sorted, top_b].values if top_b in bucket_ts.columns else np.full(len(timestamps_sorted), np.nan)
    short_rets = bucket_ts.loc[timestamps_sorted, bot_b].values if bot_b in bucket_ts.columns else np.full(len(timestamps_sorted), np.nan)
    ls_rets = long_rets - short_rets
    # NaN out if either leg is NaN
    ls_rets = np.where(np.isnan(long_rets) | np.isnan(short_rets), np.nan, ls_rets)

    # Count symbols per timestamp (vectorized)
    n_symbols = merged.groupby("timestamp")["symbol"].nunique().reindex(timestamps_sorted).values

    # Turnover: compute rank correlation between consecutive timestamps
    turnover_arr = np.full(len(timestamps_sorted), np.nan)
    if not skip_turnover:
        # Pre-build rank lookup per timestamp for efficient merging
        rank_by_ts = {}
        for ts, grp in merged.groupby("timestamp"):
            rank_by_ts[ts] = grp.set_index("symbol")["_rank"].to_dict()

        for idx in range(1, len(timestamps_sorted)):
            prev_ts = timestamps_sorted[idx - 1]
            curr_ts = timestamps_sorted[idx]
            prev_dict = rank_by_ts.get(prev_ts, {})
            curr_dict = rank_by_ts.get(curr_ts, {})
            if not prev_dict or not curr_dict:
                continue
            # Find common symbols
            common = set(prev_dict.keys()) & set(curr_dict.keys())
            if len(common) < MIN_SYMBOLS_PER_TS:
                continue
            prev_r = np.array([prev_dict[s] for s in common])
            curr_r = np.array([curr_dict[s] for s in common])
            turnover_arr[idx] = compute_turnover(prev_r, curr_r)

    port_ret = pd.DataFrame({
        "timestamp": timestamps_sorted,
        "ls_return": ls_rets,
        "long_return": long_rets,
        "short_return": short_rets,
        "n_symbols": n_symbols,
        "turnover": turnover_arr,
    })
    return port_ret

def compute_portfolio_metrics(port_returns: pd.DataFrame, horizon: str) -> dict:
    """Compute comprehensive portfolio-level metrics from per-timestamp returns."""
    ls = port_returns["ls_return"].dropna().values
    n = len(ls)
    if n == 0:
        return {"status": "NO_DATA", "n_periods": 0}

    # Basic stats
    ls_mean = float(np.mean(ls))
    ls_std = float(np.std(ls, ddof=1)) if n > 1 else 0.0
    ls_t = ls_mean / (ls_std / np.sqrt(n)) if ls_std > 0 else 0.0
    ls_win_rate = float((ls > 0).sum() / n)

    # Annualization factor (bars per year)
    if horizon == "1h":
        ann_factor = 365 * 24
    elif horizon == "4h":
        ann_factor = 365 * 6
    elif horizon == "24h":
        ann_factor = 365
    elif horizon == "72h":
        ann_factor = 365 / 3
    else:
        ann_factor = 365 * 24

    ann_return = ls_mean * ann_factor
    ann_vol = ls_std * np.sqrt(ann_factor)
    sharpe = ann_return / ann_vol if ann_vol > 0 else 0.0

    # Cumulative equity
    cum = np.cumsum(ls)
    cum_with_zero = np.concatenate([[0], cum])
    max_dd, peak_idx, trough_idx = compute_max_drawdown(cum_with_zero)

    # Drawdown durations
    max_dd_dur, curr_dd_dur = compute_drawdown_durations(cum_with_zero)

    # Sortino: using downside deviation
    downside = ls[ls < 0]
    downside_std = float(np.std(downside, ddof=1)) if len(downside) > 1 else 0.0
    downside_ann = downside_std * np.sqrt(ann_factor)
    sortino = ann_return / downside_ann if downside_ann > 0 else 0.0

    # Calmar: annualized return / |max drawdown|
    calmar = ann_return / abs(max_dd) if max_dd != 0 else 0.0

    # Long/short leg stats
    long_rets = port_returns["long_return"].dropna().values
    short_rets = port_returns["short_return"].dropna().values
    long_mean = float(np.mean(long_rets)) if len(long_rets) > 0 else 0.0
    short_mean = float(np.mean(short_rets)) if len(short_rets) > 0 else 0.0

    # Turnover stats
    to = port_returns["turnover"].dropna().values
    turnover_mean = float(np.mean(to)) if len(to) > 0 else np.nan
    turnover_std = float(np.std(to, ddof=1)) if len(to) > 1 else np.nan

    # Skewness & kurtosis
    ls_skew = float(pd.Series(ls).skew()) if n > 2 else 0.0
    ls_kurt = float(pd.Series(ls).kurtosis()) if n > 3 else 0.0

    return {
        "status": "COMPUTED",
        "n_periods": n,
        "ls_mean": round(ls_mean, 10),
        "ls_std": round(ls_std, 10),
        "ls_t_stat": round(ls_t, 4),
        "ls_win_rate": round(ls_win_rate, 4),
        "ann_return": round(ann_return, 6),
        "ann_vol": round(ann_vol, 6),
        "sharpe": round(sharpe, 4),
        "sortino": round(sortino, 4),
        "calmar": round(calmar, 4),
        "max_drawdown": round(max_dd, 8),
        "max_dd_duration_bars": max_dd_dur,
        "current_dd_duration_bars": curr_dd_dur,
        "long_leg_mean": round(long_mean, 10),
        "short_leg_mean": round(short_mean, 10),
        "turnover_mean": round(turnover_mean, 4) if not np.isnan(turnover_mean) else None,
        "turnover_std": round(turnover_std, 4) if not np.isnan(turnover_std) else None,
        "skewness": round(ls_skew, 4),
        "kurtosis": round(ls_kurt, 4),
    }


def compute_monthly_returns(port_returns: pd.DataFrame) -> list[dict]:
    """Compute monthly aggregated returns from per-timestamp portfolio returns."""
    df = port_returns.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["month"] = df["timestamp"].dt.to_period("M")

    monthly = []
    for month, grp in df.groupby("month"):
        ls = grp["ls_return"].dropna().values
        long_r = grp["long_return"].dropna().values
        short_r = grp["short_return"].dropna().values

        if len(ls) == 0:
            continue

        monthly.append({
            "month": str(month),
            "ls_return_sum": round(float(np.nansum(ls)), 8),
            "ls_return_mean": round(float(np.nanmean(ls)), 10),
            "long_return_mean": round(float(np.nanmean(long_r)), 10) if len(long_r) > 0 else None,
            "short_return_mean": round(float(np.nanmean(short_r)), 10) if len(short_r) > 0 else None,
            "n_timestamps": len(ls),
            "positive_ls": bool(np.nansum(ls) > 0),
            "turnover_mean": round(float(grp["turnover"].dropna().mean()), 4) if grp["turnover"].notna().any() else None,
        })
    return monthly


def compute_rolling_sharpe(ls_returns: np.ndarray, window: int = ROLLING_SHARPE_WINDOW) -> np.ndarray:
    """Compute rolling annualized Sharpe ratio from a return series."""
    n = len(ls_returns)
    if n < window:
        return np.full(n, np.nan)

    rolling_sharpe = np.full(n, np.nan)
    for i in range(window - 1, n):
        w = ls_returns[i - window + 1:i + 1]
        m = np.mean(w)
        s = np.std(w, ddof=1)
        if s > 0:
            rolling_sharpe[i] = m / s * np.sqrt(365 * 24)  # annualize for 1h
        else:
            rolling_sharpe[i] = 0.0
    return rolling_sharpe


def main():
    parser = argparse.ArgumentParser(description="Single-Factor Paper Portfolio Diagnostics")
    parser.add_argument("--factor-ids", nargs="*", help="Specific factor IDs (default: all)")
    parser.add_argument("--horizon", choices=LABEL_HORIZONS, default=None,
                        help="Run for a single horizon (default: all 4)")
    parser.add_argument("--n-buckets", type=int, default=DEFAULT_N_BUCKETS,
                        help="Number of quantile buckets (default: 5)")
    parser.add_argument("--dataset-id", type=str, default=DEFAULT_DATASET_ID)
    parser.add_argument("--output-dir", type=str, default=None)
    parser.add_argument("--skip-turnover", action="store_true",
                        help="Skip turnover computation (faster)")
    parser.add_argument("--rolling-window", type=int, default=ROLLING_SHARPE_WINDOW,
                        help="Rolling Sharpe window in bars (default: 720 = 30d*24h)")
    args = parser.parse_args()

    features_dir = ROOT / "data" / "features" / args.dataset_id
    labels_path = features_dir / "labels.parquet"
    out_dir = Path(args.output_dir) if args.output_dir else OUTPUT_DIR
    horizons = [args.horizon] if args.horizon else LABEL_HORIZONS

    print("=" * 80)
    print("Single-Factor Paper Portfolio Diagnostics")
    print("=" * 80)
    print(f"  Dataset:      {args.dataset_id}")
    print(f"  Horizons:     {', '.join(horizons)}")
    print(f"  Buckets:      {args.n_buckets}")
    print(f"  Turnover:     {'SKIP' if args.skip_turnover else 'COMPUTE'}")
    print(f"  Rolling Win:  {args.rolling_window} bars")
    print(f"  Output:       {out_dir}")
    print()

    # Load registry
    registry = load_factor_registry()
    if args.factor_ids:
        registry = [r for r in registry if r["factor_id"] in args.factor_ids]
    print(f"  Factors to evaluate: {len(registry)}")

    # Load labels
    print("  Loading labels...", end=" ", flush=True)
    t0 = time.time()
    if not labels_path.exists():
        print(f"\nERROR: labels not found: {labels_path}")
        sys.exit(1)
    labels = pd.read_parquet(labels_path)
    labels["timestamp"] = pd.to_datetime(labels["timestamp"], utc=True)
    print(f"done ({time.time() - t0:.1f}s, {len(labels)} rows)")

    # ── Output dirs ──────────────────────────────────────────────────
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "equity_curves").mkdir(exist_ok=True)
    (out_dir / "monthly_returns").mkdir(exist_ok=True)

    # ── Main loop ────────────────────────────────────────────────────
    summary_rows = []
    all_monthly_rows = []
    monthly_path = out_dir / "paper_portfolio_monthly_returns.csv"  # default, may not exist
    lb_path = out_dir / "paper_portfolio_leaderboard.csv"  # default, may not exist
    t_start = time.time()
    errors = []

    for i, spec in enumerate(registry):
        fid = spec["factor_id"]
        expected_dir = spec["expected_direction"]
        family = spec["family"]
        print(f"\n  [{i+1}/{len(registry)}] {fid} ({family}, dir={expected_dir})", flush=True)

        fv_path = features_dir / fid / "factor_values.parquet"
        if not fv_path.exists():
            print(f"    SKIP: missing factor_values.parquet", flush=True)
            for hz in horizons:
                summary_rows.append({
                    "factor_id": fid, "family": family, "horizon": hz,
                    "expected_direction": expected_dir,
                    "status": "MISSING_FACTOR_VALUES",
                })
            continue

        # Load factor values
        fv = pd.read_parquet(fv_path, columns=["timestamp", "symbol", "factor_value"])
        fv["timestamp"] = pd.to_datetime(fv["timestamp"], utc=True)
        fv = fv.dropna(subset=["factor_value"])

        if len(fv) == 0:
            print(f"    SKIP: no valid factor values", flush=True)
            for hz in horizons:
                summary_rows.append({
                    "factor_id": fid, "family": family, "horizon": hz,
                    "expected_direction": expected_dir,
                    "status": "NO_VALID_FACTOR_VALUES",
                })
            continue

        for hz in horizons:
            print(f"    {hz}...", end=" ", flush=True)
            try:
                port_ret = build_portfolio_returns(
                    fv, labels, hz, expected_dir, args.n_buckets,
                    skip_turnover=args.skip_turnover,
                )
            except Exception as e:
                print(f"ERROR: {e}", flush=True)
                errors.append({"factor_id": fid, "horizon": hz, "error": str(e)})
                summary_rows.append({
                    "factor_id": fid, "family": family, "horizon": hz,
                    "expected_direction": expected_dir,
                    "status": f"ERROR: {e}",
                })
                continue

            if len(port_ret) == 0:
                print("NO_DATA", flush=True)
                summary_rows.append({
                    "factor_id": fid, "family": family, "horizon": hz,
                    "expected_direction": expected_dir,
                    "status": "NO_DATA",
                })
                continue

            # Compute metrics
            metrics = compute_portfolio_metrics(port_ret, hz)
            metrics.update({
                "factor_id": fid,
                "family": family,
                "horizon": hz,
                "expected_direction": expected_dir,
            })
            summary_rows.append(metrics)

            # Monthly returns
            monthly = compute_monthly_returns(port_ret)
            for m in monthly:
                m["factor_id"] = fid
                m["family"] = family
                m["horizon"] = hz
                m["expected_direction"] = expected_dir
            all_monthly_rows.extend(monthly)

            # Save equity curve
            ls_cum = port_ret["ls_return"].fillna(0).cumsum().values
            eq_df = port_ret[["timestamp", "ls_return", "long_return", "short_return", "n_symbols"]].copy()
            eq_df["cum_ls_return"] = ls_cum
            eq_df["drawdown"] = ls_cum - np.maximum.accumulate(ls_cum)

            # Rolling Sharpe
            ls_vals = port_ret["ls_return"].fillna(0).values
            rs = compute_rolling_sharpe(ls_vals, args.rolling_window)
            eq_df["rolling_sharpe"] = rs

            eq_path = out_dir / "equity_curves" / f"{fid}__{hz}.csv"
            eq_df.to_csv(eq_path, index=False)

            # Print summary
            if metrics["status"] == "COMPUTED":
                print(f"sharpe={metrics['sharpe']:+.3f}  "
                      f"ann_ret={metrics['ann_return']*100:+.2f}%  "
                      f"max_dd={metrics['max_drawdown']*100:.4f}%  "
                      f"t={metrics['ls_t_stat']:.1f}  "
                      f"n={metrics['n_periods']}  "
                      f"win={metrics['ls_win_rate']:.0%}",
                      flush=True)
            else:
                print(metrics["status"], flush=True)

    elapsed = time.time() - t_start

    # ── Write summary ────────────────────────────────────────────────
    print(f"\n{'='*80}")
    print(f"Writing outputs...")
    summary_df = pd.DataFrame(summary_rows)

    # Main summary CSV
    summary_path = out_dir / "paper_portfolio_diagnostics_summary.csv"
    summary_df.to_csv(summary_path, index=False)
    print(f"  {summary_path} ({len(summary_df)} rows)")

    # JSON version
    json_path = out_dir / "paper_portfolio_diagnostics_summary.json"
    with open(json_path, "w") as f:
        json.dump(summary_rows, f, indent=2, default=str)
    print(f"  {json_path}")

    # Monthly returns
    if all_monthly_rows:
        monthly_df = pd.DataFrame(all_monthly_rows)
        monthly_path = out_dir / "paper_portfolio_monthly_returns.csv"
        monthly_df.to_csv(monthly_path, index=False)
        print(f"  {monthly_path} ({len(monthly_df)} rows)")

    # Leaderboard: ranked by Sharpe
    computed = summary_df[summary_df["status"] == "COMPUTED"].copy()
    if len(computed) > 0:
        leaderboard = computed.sort_values("sharpe", ascending=False)
        lb_cols = ["factor_id", "family", "horizon", "expected_direction",
                    "sharpe", "sortino", "calmar", "ann_return", "ann_vol",
                    "max_drawdown", "ls_t_stat", "ls_win_rate", "n_periods",
                    "turnover_mean", "skewness", "kurtosis"]
        lb_cols = [c for c in lb_cols if c in leaderboard.columns]
        lb = leaderboard[lb_cols].copy()
        lb_path = out_dir / "paper_portfolio_leaderboard.csv"
        lb.to_csv(lb_path, index=False)
        print(f"  {lb_path} ({len(lb)} rows)")

        # Top/bottom 10
        print(f"\n  {'='*60}")
        print(f"  LEADERBOARD (top 15 by Sharpe):")
        print(f"  {'='*60}")
        for rank, (_, row) in enumerate(lb.head(15).iterrows(), 1):
            print(f"  {rank:3d}. {row['factor_id']:30s} {row['horizon']:4s} "
                  f"sharpe={row['sharpe']:+7.3f}  "
                  f"ann_ret={row['ann_return']*100:+8.2f}%  "
                  f"max_dd={row['max_drawdown']*100:8.4f}%  "
                  f"t={row['ls_t_stat']:+7.1f}")

        if len(lb) > 15:
            print(f"  ...")
            print(f"  BOTTOM 5:")
            for _, row in lb.tail(5).iterrows():
                print(f"       {row['factor_id']:30s} {row['horizon']:4s} "
                      f"sharpe={row['sharpe']:+7.3f}  "
                      f"ann_ret={row['ann_return']*100:+8.2f}%  "
                      f"max_dd={row['max_drawdown']*100:8.4f}%  "
                      f"t={row['ls_t_stat']:+7.1f}")

    # Horizon-level summary
    if len(computed) > 0:
        print(f"\n  {'='*60}")
        print(f"  HORIZON SUMMARY (mean across factors):")
        print(f"  {'='*60}")
        for hz in horizons:
            hz_data = computed[computed["horizon"] == hz]
            if len(hz_data) == 0:
                continue
            print(f"  {hz}: n_factors={len(hz_data)}  "
                  f"mean_sharpe={hz_data['sharpe'].mean():+.3f}  "
                  f"median_sharpe={hz_data['sharpe'].median():+.3f}  "
                  f"mean_t={hz_data['ls_t_stat'].mean():+.1f}  "
                  f"mean_win={hz_data['ls_win_rate'].mean():.0%}  "
                  f"mean_turnover={hz_data['turnover_mean'].mean():.3f}")

    # Family-level summary
    if len(computed) > 0:
        print(f"\n  {'='*60}")
        print(f"  FAMILY SUMMARY (mean Sharpe, 1h horizon):")
        print(f"  {'='*60}")
        hz1 = computed[computed["horizon"] == "1h"] if "1h" in horizons else computed
        if len(hz1) > 0:
            fam_agg = hz1.groupby("family").agg(
                n=("sharpe", "count"),
                mean_sharpe=("sharpe", "mean"),
                median_sharpe=("sharpe", "median"),
                mean_t=("ls_t_stat", "mean"),
            ).sort_values("mean_sharpe", ascending=False)
            for fam, row in fam_agg.iterrows():
                print(f"  {fam:30s}  n={row['n']:3.0f}  "
                      f"mean_sharpe={row['mean_sharpe']:+7.3f}  "
                      f"median_sharpe={row['median_sharpe']:+7.3f}  "
                      f"mean_t={row['mean_t']:+7.1f}")

    # Errors
    if errors:
        err_path = out_dir / "paper_portfolio_errors.json"
        with open(err_path, "w") as f:
            json.dump(errors, f, indent=2)
        print(f"\n  ERRORS: {len(errors)} (see {err_path})")

    # Manifest
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "script": "scripts/run_single_factor_paper_diagnostics.py",
        "diagnostic_type": "SINGLE_FACTOR_PAPER_PORTFOLIO",
        "status": "DIAGNOSTIC_ONLY",
        "no_real_execution": True,
        "dataset_id": args.dataset_id,
        "horizons": horizons,
        "n_buckets": args.n_buckets,
        "factors_evaluated": len(registry),
        "factors_computed": len(computed) if len(computed) > 0 else 0,
        "errors": len(errors),
        "elapsed_seconds": round(elapsed, 1),
        "outputs": {
            "summary_csv": str(summary_path.relative_to(ROOT)),
            "summary_json": str(json_path.relative_to(ROOT)),
            "monthly_returns": str(monthly_path.relative_to(ROOT)) if all_monthly_rows else None,
            "equity_curves": str((out_dir / "equity_curves").relative_to(ROOT)),
            "leaderboard": str(lb_path.relative_to(ROOT)) if len(computed) > 0 else None,
        },
    }
    manifest_path = out_dir / "paper_portfolio_diagnostics_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"  {manifest_path}")

    print(f"\n  Total elapsed: {elapsed:.1f}s")
    print("Done.")


if __name__ == "__main__":
    main()
