#!/usr/bin/env python3
"""Rank154 postmortem factor attribution.

This script converts the rejected rank154 release candidate into a reproducible
factor autopsy.  It deliberately uses the cached causal long-history daily panel
built from Binance public archive data, not today's ticker universe.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PANEL_PATH = ROOT / "reports" / "artifacts" / "rank154_long_history" / "daily_panel.pkl"
ART_DIR = ROOT / "reports" / "artifacts" / "rank154_postmortem"

UNIVERSE_SIZE = 30
MIN_EFFECTIVE_WEIGHT = 0.005
MAX_ABS_WEIGHT = 0.10
HORIZONS = (1, 3, 5, 10)
FACTORS = {
    "carry": "carry_raw",
    "momo": "momo_10d",
    "breakout": "breakout_raw",
    "combined": "combined_score",
}


def _clean_float(x) -> float | None:
    try:
        f = float(x)
    except Exception:
        return None
    if math.isfinite(f):
        return f
    return None


def spearman_ic(x: pd.Series, y: pd.Series) -> float:
    z = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(z) < 6 or z["x"].nunique() < 2 or z["y"].nunique() < 2:
        return np.nan
    return float(z["x"].rank(method="average").corr(z["y"].rank(method="average")))


def assign_deciles(series: pd.Series) -> pd.Series:
    ranks = series.rank(method="first")
    q = max(2, min(10, int(ranks.notna().sum())))
    if q < 2:
        return pd.Series(np.nan, index=series.index)
    return pd.Series(pd.qcut(ranks, q=q, labels=False, duplicates="drop"), index=series.index, dtype=float) + 1.0


def centered_deciles(series: pd.Series) -> tuple[pd.Series, pd.Series]:
    dec = assign_deciles(series)
    centered = dec - dec.mean()
    return dec, centered


def add_forward_returns(panel: pd.DataFrame) -> pd.DataFrame:
    out = panel.sort_values(["symbol", "date"]).copy()
    for h in HORIZONS:
        fut = out.groupby("symbol", observed=True)["close"].shift(-h)
        out[f"fwd_ret_{h}d"] = fut / out["close"] - 1.0
    return out


def build_universe_panel(panel: pd.DataFrame) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    eligible = panel[panel["is_eligible"]].copy()
    eligible = eligible.dropna(subset=["trail_quote_volume_30d", "carry_raw", "momo_10d", "breakout_raw", "close"])
    for _, day in eligible.groupby("date", sort=True):
        u = day.sort_values(["trail_quote_volume_30d", "quote_volume"], ascending=False).head(UNIVERSE_SIZE).copy()
        if len(u) < 10:
            continue
        u["volume_rank_30d"] = np.arange(1, len(u) + 1)
        for name, col in [("carry", "carry_raw"), ("momo", "momo_10d"), ("breakout", "breakout_raw")]:
            dec, cen = centered_deciles(u[col])
            u[f"{name}_decile"] = dec
            u[f"{name}_centered"] = cen
        u["carry_contrib"] = 0.5 * u["carry_centered"]
        u["momo_contrib"] = 0.2 * u["momo_centered"]
        u["breakout_contrib"] = 0.3 * u["breakout_centered"]
        u["combined_score_raw"] = u["carry_contrib"] + u["momo_contrib"] + u["breakout_contrib"]
        u["combined_score"] = u["combined_score_raw"] - u["combined_score_raw"].mean()
        u["combined_decile"] = assign_deciles(u["combined_score"])
        denom = float(u["combined_score"].abs().sum())
        u["target_weight_raw"] = u["combined_score"] / denom if denom > 0 else 0.0
        u["target_weight_capped"] = u["target_weight_raw"].clip(-MAX_ABS_WEIGHT, MAX_ABS_WEIGHT)
        u["target_weight"] = np.where(u["target_weight_capped"].abs() >= MIN_EFFECTIVE_WEIGHT, u["target_weight_capped"], 0.0)
        u["side"] = np.where(u["target_weight"] > 0, "long", np.where(u["target_weight"] < 0, "short", "flat"))
        u["dominant_driver"] = u[["carry_contrib", "momo_contrib", "breakout_contrib"]].abs().idxmax(axis=1).str.replace("_contrib", "", regex=False)
        rows.append(u)
    if not rows:
        return pd.DataFrame()
    out = pd.concat(rows, ignore_index=True)
    out["year"] = out["date"].dt.year
    out["month"] = out["date"].dt.to_period("M").astype(str)
    out["age_bucket"] = pd.cut(
        out["listing_days"],
        bins=[-np.inf, 365, 730, 1095, np.inf],
        labels=["180-365d", "1-2y", "2-3y", "3y+"],
    ).astype(str)
    return out


def ic_by_date(universe: pd.DataFrame, by: Iterable[str] = ()) -> pd.DataFrame:
    keys = ["date", *by]
    records = []
    for key, g in universe.groupby(keys, observed=True, sort=True):
        key_tuple = key if isinstance(key, tuple) else (key,)
        base = dict(zip(keys, key_tuple))
        if len(g) < 6:
            continue
        for factor, col in FACTORS.items():
            for h in HORIZONS:
                records.append({
                    **base,
                    "factor": factor,
                    "horizon": h,
                    "ic": spearman_ic(g[col], g[f"fwd_ret_{h}d"]),
                    "n": int(g[[col, f"fwd_ret_{h}d"]].dropna().shape[0]),
                })
    return pd.DataFrame(records)


def summarize_ic(ic: pd.DataFrame, by: Iterable[str] = ()) -> pd.DataFrame:
    if ic.empty:
        return pd.DataFrame()
    keys = [*by, "factor", "horizon"]
    rows = []
    for key, g in ic.dropna(subset=["ic"]).groupby(keys, observed=True, sort=True):
        key_tuple = key if isinstance(key, tuple) else (key,)
        d = dict(zip(keys, key_tuple))
        mean_ic = float(g["ic"].mean())
        std_ic = float(g["ic"].std(ddof=1)) if len(g) > 1 else np.nan
        rows.append({
            **d,
            "days": int(len(g)),
            "mean_ic": mean_ic,
            "median_ic": float(g["ic"].median()),
            "ic_std": std_ic,
            "icir_daily": mean_ic / std_ic if std_ic and math.isfinite(std_ic) and std_ic > 0 else np.nan,
            "positive_ic_rate": float((g["ic"] > 0).mean()),
            "avg_cross_section_n": float(g["n"].mean()),
        })
    return pd.DataFrame(rows)


def decile_spreads(universe: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    detail_rows = []
    for (date, year), day in universe.groupby(["date", "year"], observed=True, sort=True):
        for factor in FACTORS:
            dec_col = f"{factor}_decile"
            if dec_col not in day.columns:
                continue
            max_dec = day[dec_col].max()
            min_dec = day[dec_col].min()
            if pd.isna(max_dec) or pd.isna(min_dec) or max_dec == min_dec:
                continue
            top = day[day[dec_col] == max_dec]
            bot = day[day[dec_col] == min_dec]
            for h in HORIZONS:
                rcol = f"fwd_ret_{h}d"
                detail_rows.append({
                    "date": date,
                    "year": int(year),
                    "factor": factor,
                    "horizon": h,
                    "top_decile": int(max_dec),
                    "bottom_decile": int(min_dec),
                    "top_ret": float(top[rcol].mean()),
                    "bottom_ret": float(bot[rcol].mean()),
                    "spread_top_minus_bottom": float(top[rcol].mean() - bot[rcol].mean()),
                    "n_top": int(top[rcol].notna().sum()),
                    "n_bottom": int(bot[rcol].notna().sum()),
                })
    detail = pd.DataFrame(detail_rows)
    summary_rows = []
    if not detail.empty:
        for keys, g in detail.dropna(subset=["spread_top_minus_bottom"]).groupby(["year", "factor", "horizon"], sort=True):
            year, factor, h = keys
            summary_rows.append({
                "year": int(year),
                "factor": factor,
                "horizon": int(h),
                "days": int(len(g)),
                "top_ret_mean": float(g["top_ret"].mean()),
                "bottom_ret_mean": float(g["bottom_ret"].mean()),
                "spread_mean": float(g["spread_top_minus_bottom"].mean()),
                "spread_median": float(g["spread_top_minus_bottom"].median()),
                "spread_positive_rate": float((g["spread_top_minus_bottom"] > 0).mean()),
            })
        for keys, g in detail.dropna(subset=["spread_top_minus_bottom"]).groupby(["factor", "horizon"], sort=True):
            factor, h = keys
            summary_rows.append({
                "year": "ALL",
                "factor": factor,
                "horizon": int(h),
                "days": int(len(g)),
                "top_ret_mean": float(g["top_ret"].mean()),
                "bottom_ret_mean": float(g["bottom_ret"].mean()),
                "spread_mean": float(g["spread_top_minus_bottom"].mean()),
                "spread_median": float(g["spread_top_minus_bottom"].median()),
                "spread_positive_rate": float((g["spread_top_minus_bottom"] > 0).mean()),
            })
    return detail, pd.DataFrame(summary_rows)


def leg_attribution(universe: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    for (date, year), day in universe.groupby(["date", "year"], observed=True, sort=True):
        d = day[day["target_weight"] != 0].copy()
        if d.empty:
            continue
        for h in HORIZONS:
            rcol = f"fwd_ret_{h}d"
            valid = d.dropna(subset=[rcol])
            if valid.empty:
                continue
            long = valid[valid["target_weight"] > 0]
            short = valid[valid["target_weight"] < 0]
            long_pnl = float((long["target_weight"] * long[rcol]).sum())
            short_pnl = float((short["target_weight"] * short[rcol]).sum())  # short weight is negative; positive when shorted coin falls
            gross = float(valid["target_weight"].abs().sum())
            rows.append({
                "date": date,
                "year": int(year),
                "horizon": h,
                "portfolio_ret": long_pnl + short_pnl,
                "long_contribution": long_pnl,
                "short_contribution": short_pnl,
                "long_equal_ret": float(long[rcol].mean()) if len(long) else np.nan,
                "short_underlying_ret": float(short[rcol].mean()) if len(short) else np.nan,
                "long_n": int(len(long)),
                "short_n": int(len(short)),
                "gross_weight": gross,
                "net_weight": float(valid["target_weight"].sum()),
            })
    detail = pd.DataFrame(rows)
    summary_rows = []
    if not detail.empty:
        for keys, g in detail.dropna(subset=["portfolio_ret"]).groupby(["year", "horizon"], sort=True):
            year, h = keys
            summary_rows.append({
                "year": int(year),
                "horizon": int(h),
                "days": int(len(g)),
                "portfolio_ret_mean": float(g["portfolio_ret"].mean()),
                "long_contribution_mean": float(g["long_contribution"].mean()),
                "short_contribution_mean": float(g["short_contribution"].mean()),
                "portfolio_positive_rate": float((g["portfolio_ret"] > 0).mean()),
                "long_equal_ret_mean": float(g["long_equal_ret"].mean()),
                "short_underlying_ret_mean": float(g["short_underlying_ret"].mean()),
                "avg_long_n": float(g["long_n"].mean()),
                "avg_short_n": float(g["short_n"].mean()),
                "avg_gross_weight": float(g["gross_weight"].mean()),
            })
        for h, g in detail.dropna(subset=["portfolio_ret"]).groupby("horizon", sort=True):
            summary_rows.append({
                "year": "ALL",
                "horizon": int(h),
                "days": int(len(g)),
                "portfolio_ret_mean": float(g["portfolio_ret"].mean()),
                "long_contribution_mean": float(g["long_contribution"].mean()),
                "short_contribution_mean": float(g["short_contribution"].mean()),
                "portfolio_positive_rate": float((g["portfolio_ret"] > 0).mean()),
                "long_equal_ret_mean": float(g["long_equal_ret"].mean()),
                "short_underlying_ret_mean": float(g["short_underlying_ret"].mean()),
                "avg_long_n": float(g["long_n"].mean()),
                "avg_short_n": float(g["short_n"].mean()),
                "avg_gross_weight": float(g["gross_weight"].mean()),
            })
    return detail, pd.DataFrame(summary_rows)


def age_bucket_summary(universe: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for keys, g in universe.groupby(["age_bucket", "year"], observed=True, sort=True):
        bucket, year = keys
        if len(g) < 30:
            continue
        for factor, col in FACTORS.items():
            for h in HORIZONS:
                rcol = f"fwd_ret_{h}d"
                rows.append({
                    "age_bucket": bucket,
                    "year": int(year),
                    "factor": factor,
                    "horizon": h,
                    "rows": int(g[[col, rcol]].dropna().shape[0]),
                    "mean_fwd_ret": float(g[rcol].mean()),
                    "mean_ic_pooled": spearman_ic(g[col], g[rcol]),
                })
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    all_rows = []
    for keys, g in universe.groupby("age_bucket", observed=True, sort=True):
        if len(g) < 30:
            continue
        for factor, col in FACTORS.items():
            for h in HORIZONS:
                rcol = f"fwd_ret_{h}d"
                all_rows.append({
                    "age_bucket": keys,
                    "year": "ALL",
                    "factor": factor,
                    "horizon": h,
                    "rows": int(g[[col, rcol]].dropna().shape[0]),
                    "mean_fwd_ret": float(g[rcol].mean()),
                    "mean_ic_pooled": spearman_ic(g[col], g[rcol]),
                })
    return pd.concat([df, pd.DataFrame(all_rows)], ignore_index=True)


def write_csv(df: pd.DataFrame, name: str) -> None:
    path = ART_DIR / name
    df.to_csv(path, index=False)
    print(f"[write] {path.relative_to(ROOT)} rows={len(df):,}")


def main() -> None:
    ART_DIR.mkdir(parents=True, exist_ok=True)
    if not PANEL_PATH.exists():
        raise SystemExit(f"missing panel: {PANEL_PATH}")
    panel = pd.read_pickle(PANEL_PATH)
    panel = add_forward_returns(panel)
    universe = build_universe_panel(panel)
    if universe.empty:
        raise SystemExit("empty causal rank154 universe")

    # Persist a compact daily universe sample for audit/debugging.
    keep_cols = [
        "date", "symbol", "year", "listing_days", "age_bucket", "close", "trail_quote_volume_30d",
        "carry_raw", "momo_10d", "breakout_raw", "combined_score", "carry_decile", "momo_decile",
        "breakout_decile", "combined_decile", "target_weight", "side", "dominant_driver",
        *[f"fwd_ret_{h}d" for h in HORIZONS],
    ]
    write_csv(universe[keep_cols], "rank154_causal_universe_with_forward_returns.csv")

    ic_daily = ic_by_date(universe)
    ic_summary = summarize_ic(ic_daily)
    yearly_ic = summarize_ic(ic_daily.assign(year=ic_daily["date"].dt.year), by=["year"])
    age_ic_daily = ic_by_date(universe, by=["age_bucket"])
    age_ic = summarize_ic(age_ic_daily, by=["age_bucket"])

    dec_detail, dec_summary = decile_spreads(universe)
    leg_detail, leg_summary = leg_attribution(universe)
    age_summary = age_bucket_summary(universe)

    write_csv(ic_daily, "factor_ic_daily.csv")
    write_csv(ic_summary, "factor_ic_summary.csv")
    write_csv(yearly_ic, "yearly_factor_ic.csv")
    write_csv(age_ic, "age_bucket_ic_summary.csv")
    write_csv(dec_detail, "decile_spread_daily.csv")
    write_csv(dec_summary, "decile_spread_summary.csv")
    write_csv(leg_detail, "long_short_leg_daily.csv")
    write_csv(leg_summary, "long_short_leg_summary.csv")
    write_csv(age_summary, "age_bucket_summary.csv")

    meta = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "panel_path": str(PANEL_PATH.relative_to(ROOT)),
        "panel_rows": int(len(panel)),
        "panel_symbols": int(panel["symbol"].nunique()),
        "panel_date_min": str(panel["date"].min()),
        "panel_date_max": str(panel["date"].max()),
        "universe_size": UNIVERSE_SIZE,
        "universe_rows": int(len(universe)),
        "universe_days": int(universe["date"].nunique()),
        "universe_symbols": int(universe["symbol"].nunique()),
        "horizons": list(HORIZONS),
        "factors": FACTORS,
        "causality_notes": [
            "daily universe is selected per historical date by trailing 30d quote volume among eligible symbols",
            "forward returns are shifted within each symbol after the signal date",
            "rank154 factor weights are carry=0.5, momo=0.2, breakout=0.3, matching the current strategy source",
        ],
    }
    (ART_DIR / "postmortem_manifest.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[write] {(ART_DIR / 'postmortem_manifest.json').relative_to(ROOT)}")
    print("[ok] rank154 postmortem attribution complete")


if __name__ == "__main__":
    main()
