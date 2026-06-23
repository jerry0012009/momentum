#!/usr/bin/env python3
"""
PM-23: BTC Market Regime Diagnostics
=====================================

Classify each month by BTC market regime (trend, volatility, drawdown) and
analyse how each factor's performance (IC, long-short, paper return) varies
across regimes.  Computes per-factor BTC-correlation/beta exposure and a
regime-dependency classification.

NOT production. Research diagnostics only.

Usage:
    python scripts/build_factor_market_regime_diagnostics.py \\
        --btc-symbol auto --fee-bps 10 \\
        --output-dir research/factor_runs/crypto_top50_factor_library/factor_diagnostics
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

# ── Paths ────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parents[1]
BARS_PATH = ROOT / "data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet"
DIAG_DIR_DEFAULT = ROOT / "research/factor_runs/crypto_top50_factor_library/factor_diagnostics"

PATH_MONTHLY_IC = "factor_monthly_ic_series.csv"
PATH_MONTHLY_LS = "factor_monthly_long_short_series.csv"
PATH_PAPER_MONTHLY = "single_factor_paper_monthly_returns.csv"

# ── Helpers ──────────────────────────────────────────────────────────────────


def _find_btc_symbol(symbols: list[str], manual: str) -> str:
    """Auto-detect or validate the BTC symbol."""
    if manual != "auto":
        if manual not in symbols:
            print(f"ERROR: manual --btc-symbol {manual!r} not in bars. Available BTC symbols: "
                  f"{[s for s in symbols if 'BTC' in s.upper()]}")
            sys.exit(1)
        return manual

    # Prefer exact BTCUSDT, then anything containing BTC
    candidates = [s for s in symbols if s.upper() == "BTCUSDT"]
    if not candidates:
        candidates = [s for s in symbols if "BTC" in s.upper() and "PUMP" not in s.upper()]
    if not candidates:
        print(f"ERROR: no BTC symbol found in bars. Symbols sample: {symbols[:20]}")
        sys.exit(1)

    sym = candidates[0]
    print(f"Auto-detected BTC symbol: {sym}")
    return sym


def _build_btc_monthly_regimes(btc: pd.DataFrame) -> pd.DataFrame:
    """Build monthly BTC regime labels from hourly bars."""
    btc = btc.copy()
    btc["timestamp"] = pd.to_datetime(btc["timestamp"], utc=True)
    btc["month"] = btc["timestamp"].dt.to_period("M").astype(str)

    months = sorted(btc["month"].unique())
    records = []

    for m in months:
        bm = btc[btc["month"] == m].sort_values("timestamp")
        if len(bm) < 10:
            continue

        open_price = bm["close"].iloc[0]
        close_price = bm["close"].iloc[-1]
        high_price = bm["high"].max()
        low_price = bm["low"].min()

        monthly_return = close_price / open_price - 1

        # Realized vol from hourly log-returns
        log_rets = np.log(bm["close"] / bm["close"].shift(1)).dropna()
        realized_vol = log_rets.std() * np.sqrt(24 * 365)  # annualized

        # Max drawdown within month
        cum = bm["close"].values
        running_max = np.maximum.accumulate(cum)
        drawdowns = cum / running_max - 1
        max_drawdown = drawdowns.min()

        records.append({
            "month": m,
            "btc_monthly_return": monthly_return,
            "btc_monthly_realized_vol": realized_vol,
            "btc_monthly_max_drawdown": max_drawdown,
            "btc_open": open_price,
            "btc_close": close_price,
            "btc_high": high_price,
            "btc_low": low_price,
        })

    df = pd.DataFrame(records).sort_values("month").reset_index(drop=True)

    # Rolling 3-month return
    df["btc_rolling_3m_return"] = (
        df["btc_close"].pct_change(3).shift(-2)  # forward-looking 3m
    )
    # Actually we want trailing 3m: use close[-1] / close[-4] - 1
    # But simpler: shift
    closes = df["btc_close"].values
    rolling_3m = np.full(len(closes), np.nan)
    for i in range(3, len(closes)):
        rolling_3m[i] = closes[i] / closes[i - 3] - 1
    df["btc_rolling_3m_return"] = rolling_3m

    # Drawdown from peak (running)
    peak = df["btc_close"].cummax()
    df["btc_drawdown_from_peak"] = df["btc_close"] / peak - 1

    # Regime labels
    vol_median = df["btc_monthly_realized_vol"].median()

    def trend_regime(ret):
        if ret >= 0.05:
            return "BULL"
        elif ret <= -0.05:
            return "BEAR"
        return "SIDEWAYS"

    def vol_regime(v):
        return "HIGH_VOL" if v >= vol_median else "LOW_VOL"

    def dd_regime(dd):
        return "DEEP_DRAWDOWN" if dd <= -0.20 else "NORMAL"

    df["btc_trend_regime"] = df["btc_monthly_return"].apply(trend_regime)
    df["btc_vol_regime"] = df["btc_monthly_realized_vol"].apply(vol_regime)
    df["btc_drawdown_regime"] = df["btc_drawdown_from_peak"].apply(dd_regime)
    df["combined_regime"] = (
        df["btc_trend_regime"] + "_" + df["btc_vol_regime"]
    )

    return df


def _safe_float(v):
    """Convert to float, returning None for NaN/inf."""
    if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v))):
        return None
    return float(v)


def _summary_stats(values: pd.Series) -> dict:
    """Return summary stats for a numeric series."""
    v = values.dropna()
    n = len(v)
    if n == 0:
        return {"n_months": 0, "mean": None, "median": None, "std": None,
                "positive_rate": None, "min": None, "max": None}
    return {
        "n_months": int(n),
        "mean": _safe_float(v.mean()),
        "median": _safe_float(v.median()),
        "std": _safe_float(v.std()),
        "positive_rate": _safe_float((v > 0).mean()),
        "min": _safe_float(v.min()),
        "max": _safe_float(v.max()),
    }


def _regime_split_summary(
    data: pd.DataFrame,
    value_col: str,
    regime_col: str,
    factor_id: str,
) -> list[dict]:
    """For each value of regime_col, compute summary of value_col."""
    rows = []
    for regime_val, grp in data.groupby(regime_col):
        stats = _summary_stats(grp[value_col])
        rows.append({
            "factor_id": factor_id,
            "regime_dimension": regime_col,
            "regime_value": str(regime_val),
            **stats,
        })
    return rows


def _classify_regime_dependency(
    n_months: int,
    bull_minus_bear: float | None,
    hv_minus_lv: float | None,
    dd_minus_norm: float | None,
    paper_btc_corr: float | None,
    paper_btc_beta: float | None,
    ls_btc_corr: float | None,
    min_months: int,
) -> tuple[str, str, str]:
    """Return (classification_zh, classification_en, classification)."""
    if n_months < min_months * 2:
        return "数据不足", "Insufficient data", "INSUFFICIENT_REGIME_DATA"

    # Check BTC beta sensitivity
    if paper_btc_beta is not None and abs(paper_btc_beta) > 0.5:
        return "BTC高Beta敏感", "High BTC beta sensitivity", "BTC_BETA_SENSITIVE"
    if ls_btc_corr is not None and abs(ls_btc_corr) > 0.5:
        return "BTC高相关敏感", "High BTC correlation sensitivity", "BTC_BETA_SENSITIVE"

    # Check drawdown fragility
    if dd_minus_norm is not None and dd_minus_norm < -0.05:
        return "回撤脆弱", "Fragile during drawdowns", "DRAWDOWN_FRAGILE"

    # Check bull/bear dependence
    if bull_minus_bear is not None and abs(bull_minus_bear) > 0.05:
        if bull_minus_bear > 0:
            return "牛市依赖", "Bull-dependent", "BULL_DEPENDENT"
        else:
            return "熊市依赖", "Bear-dependent", "BEAR_DEPENDENT"

    # Check vol dependence
    if hv_minus_lv is not None and abs(hv_minus_lv) > 0.05:
        return "波动率依赖", "Volatility-dependent", "VOL_DEPENDENT"

    return "跨市场稳健", "Regime-robust", "REGIME_ROBUST"


# ── Main ─────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        description="PM-23: BTC Market Regime Diagnostics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--btc-symbol", type=str, default="auto",
                        help="BTC symbol in bars. 'auto' to detect.")
    parser.add_argument("--fee-bps", type=int, default=10,
                        help="Fee bps for paper returns (default 10)")
    parser.add_argument("--output-dir", type=str, default=str(DIAG_DIR_DEFAULT),
                        help="Output directory for diagnostics files")
    parser.add_argument("--min-months-per-regime", type=int, default=3,
                        help="Min months per regime bucket for reliable stats")
    parser.add_argument("--canonical-ic-path", type=str, default=None,
                        help="Path to canonical factor_level_period_ic_summary.csv for IC merge")
    parser.add_argument("--canonical-ls-path", type=str, default=None,
                        help="Path to canonical factor_level_period_long_short_summary.csv for LS merge")
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # ── 1. Load BTC bars and build monthly regimes ───────────────────────────
    print("Loading BTC bars...")
    all_bars = pd.read_parquet(BARS_PATH, columns=["timestamp", "symbol", "close", "high", "low"])
    btc_sym = _find_btc_symbol(all_bars["symbol"].unique().tolist(), args.btc_symbol)
    btc = all_bars[all_bars["symbol"] == btc_sym].copy()
    del all_bars  # free memory

    print(f"Building monthly regime labels for {btc_sym} ({len(btc)} bars)...")
    regimes = _build_btc_monthly_regimes(btc)
    print(f"  {len(regimes)} months, date range: {regimes['month'].iloc[0]} to {regimes['month'].iloc[-1]}")

    # Save monthly labels
    labels_path = out_dir / "market_regime_monthly_labels.csv"
    regimes.to_csv(labels_path, index=False)
    print(f"  Saved: {labels_path}")

    # Print regime distribution
    for dim in ["btc_trend_regime", "btc_vol_regime", "btc_drawdown_regime"]:
        dist = regimes[dim].value_counts()
        print(f"  {dim}: {dict(dist)}")

    # ── 2. Load factor diagnostic inputs ────────────────────────────────────
    print("\nLoading factor diagnostics...")
    ic_df = pd.read_csv(out_dir / PATH_MONTHLY_IC)
    ls_df = pd.read_csv(out_dir / PATH_MONTHLY_LS)
    paper_df = pd.read_csv(out_dir / PATH_PAPER_MONTHLY)

    # ── PM-43A: Merge canonical IC if old diagnostics is missing factors ──
    if args.canonical_ic_path:
        canon_ic = pd.read_csv(args.canonical_ic_path)
        missing_fids = set(ls_df["factor_id"].unique()) | set(paper_df["factor_id"].unique())
        missing_fids -= set(ic_df["factor_id"].unique())
        if missing_fids:
            print(f"  Canonical IC merge: {len(missing_fids)} factors missing from old IC, merging from canonical")
            canon_sub = canon_ic[canon_ic["factor_name"].isin(missing_fids)].copy()
            canon_sub = canon_sub.rename(columns={
                "factor_name": "factor_id",
                "period": "month",
                "raw_mean_rank_ic": "rank_ic",
                "direction_adjusted_mean_rank_ic": "rank_ic_adj",
                "n_periods": "n_obs",
            })
            canon_sub["positive_ic"] = canon_sub["rank_ic"] > 0
            canon_sub = canon_sub[["factor_id", "horizon", "month", "rank_ic", "rank_ic_adj", "n_obs", "positive_ic"]]
            ic_df = pd.concat([ic_df, canon_sub], ignore_index=True)
            print(f"  After merge: {ic_df['factor_id'].nunique()} factors in IC")

    # ── PM-46B: Merge canonical LS if old diagnostics is missing factors ──
    if args.canonical_ls_path:
        canon_ls = pd.read_csv(args.canonical_ls_path)
        missing_ls_fids = set(ic_df["factor_id"].unique()) | set(paper_df["factor_id"].unique())
        missing_ls_fids -= set(ls_df["factor_id"].unique())
        if missing_ls_fids:
            print(f"  Canonical LS merge: {len(missing_ls_fids)} factors missing from old LS, merging from canonical")
            canon_ls_sub = canon_ls[canon_ls["factor_name"].isin(missing_ls_fids)].copy()
            canon_ls_sub = canon_ls_sub.rename(columns={
                "factor_name": "factor_id",
                "period": "month",
            })
            # Keep only the columns that match old LS format
            keep_cols = ["factor_id", "horizon", "month", "long_short_return"]
            for extra_col in ["long_leg_return", "short_leg_return", "n_obs", "positive_ls"]:
                if extra_col in canon_ls_sub.columns:
                    keep_cols.append(extra_col)
            canon_ls_sub = canon_ls_sub[[c for c in keep_cols if c in canon_ls_sub.columns]]
            # Rename n_obs to n_long/n_short for compatibility
            if "n_obs" in canon_ls_sub.columns:
                canon_ls_sub["n_long"] = canon_ls_sub["n_obs"]
                canon_ls_sub["n_short"] = canon_ls_sub["n_obs"]
                canon_ls_sub = canon_ls_sub.drop(columns=["n_obs"])
            ls_df = pd.concat([ls_df, canon_ls_sub], ignore_index=True)
            print(f"  After merge: {ls_df['factor_id'].nunique()} factors in LS")

    # Filter paper to fee_bps
    paper_df = paper_df[paper_df["fee_bps"] == args.fee_bps].copy()
    print(f"  IC: {len(ic_df)} rows, {ic_df['factor_id'].nunique()} factors")
    print(f"  LS: {len(ls_df)} rows, {ls_df['factor_id'].nunique()} factors")
    print(f"  Paper (fee={args.fee_bps}bps): {len(paper_df)} rows, {paper_df['factor_id'].nunique()} factors")

    all_factors = sorted(set(ic_df["factor_id"].unique()) |
                         set(ls_df["factor_id"].unique()) |
                         set(paper_df["factor_id"].unique()))
    print(f"  Total unique factors: {len(all_factors)}")

    # ── 3. Merge regime labels into each dataframe ──────────────────────────
    regime_map = regimes.set_index("month")[[
        "btc_monthly_return", "btc_monthly_realized_vol", "btc_monthly_max_drawdown",
        "btc_rolling_3m_return", "btc_drawdown_from_peak",
        "btc_trend_regime", "btc_vol_regime", "btc_drawdown_regime", "combined_regime"
    ]].to_dict("index")

    def _add_regime_cols(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        for col in ["btc_trend_regime", "btc_vol_regime", "btc_drawdown_regime",
                     "combined_regime", "btc_monthly_return"]:
            df[col] = df["month"].map(lambda m: regime_map.get(m, {}).get(col))
        return df

    ic_reg = _add_regime_cols(ic_df)
    ls_reg = _add_regime_cols(ls_df)
    paper_reg = _add_regime_cols(paper_df)

    # ── 4. Per-factor × regime summary ──────────────────────────────────────
    print("\nComputing per-factor regime summaries...")
    regime_dims = ["btc_trend_regime", "btc_vol_regime", "btc_drawdown_regime"]
    all_regime_rows = []

    for fid in all_factors:
        fid_ic = ic_reg[ic_reg["factor_id"] == fid]
        fid_ls = ls_reg[ls_reg["factor_id"] == fid]
        fid_paper = paper_reg[paper_reg["factor_id"] == fid]

        for dim in regime_dims:
            # IC
            if len(fid_ic) > 0:
                for row in _regime_split_summary(fid_ic, "rank_ic", dim, fid):
                    row["metric_type"] = "ic_rank"
                    all_regime_rows.append(row)

            # Long-short
            if len(fid_ls) > 0:
                for row in _regime_split_summary(fid_ls, "long_short_return", dim, fid):
                    row["metric_type"] = "long_short"
                    all_regime_rows.append(row)

            # Paper
            if len(fid_paper) > 0:
                for row in _regime_split_summary(fid_paper, "monthly_return", dim, fid):
                    row["metric_type"] = "paper_return"
                    all_regime_rows.append(row)

    regime_summary = pd.DataFrame(all_regime_rows)
    regime_summary_path = out_dir / "factor_regime_summary.csv"
    regime_summary.to_csv(regime_summary_path, index=False)
    print(f"  {len(regime_summary)} regime × factor × metric rows saved to {regime_summary_path}")

    # ── 5. Per-factor exposure summary ──────────────────────────────────────
    print("\nComputing factor exposure summaries...")
    exposure_rows = []

    for fid in all_factors:
        fid_paper = paper_reg[paper_reg["factor_id"] == fid].sort_values("month")
        fid_ls = ls_reg[ls_reg["factor_id"] == fid].sort_values("month")
        fid_ic = ic_reg[ic_reg["factor_id"] == fid].sort_values("month")

        row = {"factor_id": fid}

        # ── BTC correlations & betas ──
        # Paper return vs BTC monthly return
        if len(fid_paper) >= 6:
            merged = fid_paper[["month", "monthly_return"]].merge(
                regimes[["month", "btc_monthly_return"]], on="month", how="inner"
            ).dropna()
            if len(merged) >= 4:
                corr = merged["monthly_return"].corr(merged["btc_monthly_return"])
                cov = merged["monthly_return"].cov(merged["btc_monthly_return"])
                var_btc = merged["btc_monthly_return"].var()
                beta = cov / var_btc if var_btc > 0 else np.nan
                row["paper_return_btc_corr"] = _safe_float(corr)
                row["paper_return_btc_beta"] = _safe_float(beta)
            else:
                row["paper_return_btc_corr"] = None
                row["paper_return_btc_beta"] = None
        else:
            row["paper_return_btc_corr"] = None
            row["paper_return_btc_beta"] = None

        # Long-short vs BTC monthly return
        if len(fid_ls) >= 6:
            merged = fid_ls[["month", "long_short_return"]].merge(
                regimes[["month", "btc_monthly_return"]], on="month", how="inner"
            ).dropna()
            if len(merged) >= 4:
                corr = merged["long_short_return"].corr(merged["btc_monthly_return"])
                cov = merged["long_short_return"].cov(merged["btc_monthly_return"])
                var_btc = merged["btc_monthly_return"].var()
                beta = cov / var_btc if var_btc > 0 else np.nan
                row["long_short_btc_corr"] = _safe_float(corr)
                row["long_short_btc_beta"] = _safe_float(beta)
            else:
                row["long_short_btc_corr"] = None
                row["long_short_btc_beta"] = None
        else:
            row["long_short_btc_corr"] = None
            row["long_short_btc_beta"] = None

        # IC vs BTC monthly return
        if len(fid_ic) >= 6:
            merged = fid_ic[["month", "rank_ic"]].merge(
                regimes[["month", "btc_monthly_return"]], on="month", how="inner"
            ).dropna()
            if len(merged) >= 4:
                row["ic_btc_return_corr"] = _safe_float(
                    merged["rank_ic"].corr(merged["btc_monthly_return"])
                )
            else:
                row["ic_btc_return_corr"] = None
        else:
            row["ic_btc_return_corr"] = None

        # ── Regime spread ──
        # Bull minus Bear paper return
        paper_trend = fid_paper.dropna(subset=["btc_trend_regime"])
        if len(paper_trend) > 0:
            bull_mean = paper_trend[paper_trend["btc_trend_regime"] == "BULL"]["monthly_return"].mean()
            bear_mean = paper_trend[paper_trend["btc_trend_regime"] == "BEAR"]["monthly_return"].mean()
            bmb = (bull_mean - bear_mean) if not (np.isnan(bull_mean) or np.isnan(bear_mean)) else None
            row["bull_minus_bear_paper_return"] = _safe_float(bmb)

            # High vol minus Low vol
            hv_mean = paper_trend[paper_trend["btc_vol_regime"] == "HIGH_VOL"]["monthly_return"].mean()
            lv_mean = paper_trend[paper_trend["btc_vol_regime"] == "LOW_VOL"]["monthly_return"].mean()
            hml = (hv_mean - lv_mean) if not (np.isnan(hv_mean) or np.isnan(lv_mean)) else None
            row["highvol_minus_lowvol_paper_return"] = _safe_float(hml)

            # Drawdown minus Normal
            dd_mean = paper_trend[paper_trend["btc_drawdown_regime"] == "DEEP_DRAWDOWN"]["monthly_return"].mean()
            norm_mean = paper_trend[paper_trend["btc_drawdown_regime"] == "NORMAL"]["monthly_return"].mean()
            dmn = (dd_mean - norm_mean) if not (np.isnan(dd_mean) or np.isnan(norm_mean)) else None
            row["drawdown_minus_normal_paper_return"] = _safe_float(dmn)
        else:
            row["bull_minus_bear_paper_return"] = None
            row["highvol_minus_lowvol_paper_return"] = None
            row["drawdown_minus_normal_paper_return"] = None

        # ── Classification ──
        n_months = len(fid_paper)
        zh, en, cls = _classify_regime_dependency(
            n_months=n_months,
            bull_minus_bear=row.get("bull_minus_bear_paper_return"),
            hv_minus_lv=row.get("highvol_minus_lowvol_paper_return"),
            dd_minus_norm=row.get("drawdown_minus_normal_paper_return"),
            paper_btc_corr=row.get("paper_return_btc_corr"),
            paper_btc_beta=row.get("paper_return_btc_beta"),
            ls_btc_corr=row.get("long_short_btc_corr"),
            min_months=args.min_months_per_regime,
        )
        row["regime_dependency_class"] = cls
        row["main_regime_note_zh"] = zh
        row["main_regime_note_en"] = en

        exposure_rows.append(row)

    exposure_df = pd.DataFrame(exposure_rows)
    exposure_path = out_dir / "factor_regime_exposure_summary.csv"
    exposure_df.to_csv(exposure_path, index=False)
    print(f"  {len(exposure_df)} factors saved to {exposure_path}")

    # Print distribution
    cls_dist = exposure_df["regime_dependency_class"].value_counts()
    print(f"  Regime dependency distribution:")
    for cls_name, count in cls_dist.items():
        print(f"    {cls_name}: {count}")

    # ── 6. Per-factor × regime detail (IC, LS, Paper each regime) ───────────
    # Already saved as factor_regime_summary.csv above

    # ── 7. Payload JSON ─────────────────────────────────────────────────────
    print("\nBuilding payload JSON...")
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pm_version": "pm23_v1",
        "btc_symbol": btc_sym,
        "fee_bps": args.fee_bps,
        "min_months_per_regime": args.min_months_per_regime,
        "n_months": len(regimes),
        "month_range": [regimes["month"].iloc[0], regimes["month"].iloc[-1]],
        "n_factors": len(all_factors),
        "regime_distributions": {
            "trend": regimes["btc_trend_regime"].value_counts().to_dict(),
            "volatility": regimes["btc_vol_regime"].value_counts().to_dict(),
            "drawdown": regimes["btc_drawdown_regime"].value_counts().to_dict(),
        },
        "dependency_class_distribution": exposure_df["regime_dependency_class"].value_counts().to_dict(),
        "files": {
            "monthly_labels": "market_regime_monthly_labels.csv",
            "regime_summary": "factor_regime_summary.csv",
            "exposure_summary": "factor_regime_exposure_summary.csv",
        },
        "not_for_production": True,
    }
    payload_path = out_dir / "factor_regime_diagnostics_payload.json"
    with open(payload_path, "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"  Saved: {payload_path}")

    # ── 8. Manifest JSON ────────────────────────────────────────────────────
    manifest = {
        "script": "scripts/build_factor_market_regime_diagnostics.py",
        "pm_version": "pm23_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "btc_symbol": btc_sym,
        "fee_bps": args.fee_bps,
        "n_months": len(regimes),
        "n_factors": len(all_factors),
        "output_files": [
            "market_regime_monthly_labels.csv",
            "factor_regime_summary.csv",
            "factor_regime_exposure_summary.csv",
            "factor_regime_diagnostics_payload.json",
            "factor_market_regime_manifest.json",
            "factor_regime_class_distribution.csv",
            "factor_regime_top_lists.csv",
        ],
        "not_for_production": True,
    }
    manifest_path = out_dir / "factor_market_regime_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2, default=str)
    print(f"  Saved: {manifest_path}")

    # ── 9. Class distribution CSV ───────────────────────────────────────────
    cls_csv = exposure_df[["factor_id", "regime_dependency_class",
                           "main_regime_note_zh", "main_regime_note_en",
                           "paper_return_btc_corr", "paper_return_btc_beta",
                           "long_short_btc_corr", "long_short_btc_beta",
                           "ic_btc_return_corr",
                           "bull_minus_bear_paper_return",
                           "highvol_minus_lowvol_paper_return",
                           "drawdown_minus_normal_paper_return"]].copy()
    cls_path = out_dir / "factor_regime_class_distribution.csv"
    cls_csv.to_csv(cls_path, index=False)
    print(f"  Saved: {cls_path}")

    # ── 10. Top lists CSV ───────────────────────────────────────────────────
    # Top 10 regime-robust (sorted by absolute paper_btc_corr ascending)
    robust = exposure_df[exposure_df["regime_dependency_class"] == "REGIME_ROBUST"].copy()
    robust["abs_corr"] = robust["paper_return_btc_corr"].abs()
    robust = robust.sort_values("abs_corr").head(10)

    # Top 10 BTC-beta-sensitive
    beta_sens = exposure_df[exposure_df["regime_dependency_class"] == "BTC_BETA_SENSITIVE"].copy()
    beta_sens["abs_beta"] = beta_sens["paper_return_btc_beta"].abs()
    beta_sens = beta_sens.sort_values("abs_beta", ascending=False).head(10)

    # Top 10 drawdown-fragile
    dd_frag = exposure_df[exposure_df["regime_dependency_class"] == "DRAWDOWN_FRAGILE"].copy()
    dd_frag = dd_frag.sort_values("drawdown_minus_normal_paper_return").head(10)

    top_lists = pd.concat([
        robust.assign(list_type="REGIME_ROBUST"),
        beta_sens.assign(list_type="BTC_BETA_SENSITIVE"),
        dd_frag.assign(list_type="DRAWDOWN_FRAGILE"),
    ], ignore_index=True)
    top_path = out_dir / "factor_regime_top_lists.csv"
    top_lists.to_csv(top_path, index=False)
    print(f"  Saved: {top_path}")

    # ── Summary ─────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"PM-23 BTC Market Regime Diagnostics — COMPLETE")
    print(f"{'='*60}")
    print(f"  BTC symbol:        {btc_sym}")
    print(f"  Months:            {len(regimes)} ({regimes['month'].iloc[0]} to {regimes['month'].iloc[-1]})")
    print(f"  Factors:           {len(all_factors)}")
    print(f"  Fee bps:           {args.fee_bps}")
    print(f"  Output files:      7 in {out_dir}")
    print(f"  Dependency classes:")
    for cls_name, count in cls_dist.items():
        print(f"    {cls_name}: {count}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
