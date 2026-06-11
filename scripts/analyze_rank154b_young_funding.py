#!/usr/bin/env python3
"""Rank154b evidence probe: young-coin funding/crowding continuation.

Hypothesis: among causally eligible young Binance USDT-M symbols, high funding is
not traditional carry but a crowding/attention continuation signal. The effect
should be stronger for 180-730d listing age than for old 3y+ coins.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PANEL_PATH = ROOT / "reports" / "artifacts" / "rank154_long_history" / "daily_panel.pkl"
OUT = ROOT / "reports" / "artifacts" / "rank154b_young_funding"
HORIZONS = (1, 3, 5, 10)
UNIVERSE_SIZES = (15, 30, 50)
AGE_SPECS = {
    "young_180_365d": (180, 365),
    "young_1_2y": (365, 730),
    "young_180_730d": (180, 730),
    "old_3y_plus": (1095, 10_000),
}
COST_BPS_RT = (0, 10, 20, 30)  # round-trip gross-cost haircut per horizon for top-bottom spread


def spearman_ic(x: pd.Series, y: pd.Series) -> float:
    z = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(z) < 6 or z["x"].nunique() < 2 or z["y"].nunique() < 2:
        return np.nan
    return float(z["x"].rank(method="average").corr(z["y"].rank(method="average")))


def add_forward_returns(panel: pd.DataFrame) -> pd.DataFrame:
    out = panel.sort_values(["symbol", "date"]).copy()
    for h in HORIZONS:
        out[f"fwd_ret_{h}d"] = out.groupby("symbol", observed=True)["close"].shift(-h) / out["close"] - 1.0
    return out


def qcut_decile(s: pd.Series) -> pd.Series:
    r = s.rank(method="first")
    q = max(2, min(10, int(r.notna().sum())))
    if q < 2:
        return pd.Series(np.nan, index=s.index)
    return pd.Series(pd.qcut(r, q=q, labels=False, duplicates="drop"), index=s.index, dtype=float) + 1


def build_daily_universe(panel: pd.DataFrame, age_name: str, age_min: int, age_max: int, topn: int) -> pd.DataFrame:
    eligible = panel[
        panel["is_eligible"]
        & (panel["listing_days"] >= age_min)
        & (panel["listing_days"] < age_max)
        & panel["trail_quote_volume_30d"].notna()
        & panel["carry_raw"].notna()
    ].copy()
    rows = []
    for date, g in eligible.groupby("date", sort=True, observed=True):
        u = g.sort_values(["trail_quote_volume_30d", "quote_volume"], ascending=False).head(topn).copy()
        if len(u) < max(8, min(15, topn // 2)):
            continue
        u["age_spec"] = age_name
        u["universe_size"] = topn
        u["funding_decile"] = qcut_decile(u["carry_raw"])
        rows.append(u)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def summarize_universe(u: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    daily_rows = []
    ic_rows = []
    for date, d in u.groupby("date", sort=True, observed=True):
        maxd, mind = d["funding_decile"].max(), d["funding_decile"].min()
        top = d[d["funding_decile"] == maxd]
        bot = d[d["funding_decile"] == mind]
        for h in HORIZONS:
            rcol = f"fwd_ret_{h}d"
            spread = float(top[rcol].mean() - bot[rcol].mean())
            top_ret = float(top[rcol].mean())
            bot_ret = float(bot[rcol].mean())
            daily_rows.append({
                "date": date,
                "year": int(pd.Timestamp(date).year),
                "age_spec": d["age_spec"].iloc[0],
                "universe_size": int(d["universe_size"].iloc[0]),
                "horizon": h,
                "n": int(d[rcol].notna().sum()),
                "top_n": int(top[rcol].notna().sum()),
                "bottom_n": int(bot[rcol].notna().sum()),
                "ic": spearman_ic(d["carry_raw"], d[rcol]),
                "top_ret": top_ret,
                "bottom_ret": bot_ret,
                "spread_top_minus_bottom": spread,
                "long_only_top_ret": top_ret,
                "short_low_funding_ret": -bot_ret,
            })
            ic_rows.append(daily_rows[-1])
    daily = pd.DataFrame(daily_rows)
    summary_rows = []
    yearly_rows = []
    for keys, g in daily.dropna(subset=["ic", "spread_top_minus_bottom"]).groupby(["age_spec", "universe_size", "horizon"], sort=True):
        age_spec, topn, h = keys
        row = {
            "age_spec": age_spec,
            "universe_size": int(topn),
            "horizon": int(h),
            "days": int(len(g)),
            "mean_ic": float(g["ic"].mean()),
            "median_ic": float(g["ic"].median()),
            "ic_std": float(g["ic"].std(ddof=1)),
            "icir_daily": float(g["ic"].mean() / g["ic"].std(ddof=1)) if g["ic"].std(ddof=1) > 0 else np.nan,
            "positive_ic_rate": float((g["ic"] > 0).mean()),
            "top_ret_mean": float(g["top_ret"].mean()),
            "bottom_ret_mean": float(g["bottom_ret"].mean()),
            "spread_mean": float(g["spread_top_minus_bottom"].mean()),
            "spread_median": float(g["spread_top_minus_bottom"].median()),
            "spread_positive_rate": float((g["spread_top_minus_bottom"] > 0).mean()),
            "long_only_top_ret_mean": float(g["long_only_top_ret"].mean()),
            "short_low_funding_ret_mean": float(g["short_low_funding_ret"].mean()),
        }
        for c in COST_BPS_RT:
            row[f"spread_net_{c}bps_rt"] = row["spread_mean"] - c / 10000.0
            row[f"top_long_net_{c}bps_rt"] = row["top_ret_mean"] - c / 10000.0
        summary_rows.append(row)
    for keys, g in daily.dropna(subset=["ic", "spread_top_minus_bottom"]).groupby(["age_spec", "universe_size", "year", "horizon"], sort=True):
        age_spec, topn, year, h = keys
        yearly_rows.append({
            "age_spec": age_spec,
            "universe_size": int(topn),
            "year": int(year),
            "horizon": int(h),
            "days": int(len(g)),
            "mean_ic": float(g["ic"].mean()),
            "icir_daily": float(g["ic"].mean() / g["ic"].std(ddof=1)) if g["ic"].std(ddof=1) > 0 else np.nan,
            "positive_ic_rate": float((g["ic"] > 0).mean()),
            "spread_mean": float(g["spread_top_minus_bottom"].mean()),
            "spread_positive_rate": float((g["spread_top_minus_bottom"] > 0).mean()),
            "top_ret_mean": float(g["top_ret"].mean()),
            "bottom_ret_mean": float(g["bottom_ret"].mean()),
        })
    return daily, pd.DataFrame(summary_rows), pd.DataFrame(yearly_rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    panel = pd.read_pickle(PANEL_PATH)
    panel = add_forward_returns(panel)
    all_daily = []
    all_summ = []
    all_yearly = []
    universe_meta = []
    for age_name, (lo, hi) in AGE_SPECS.items():
        for topn in UNIVERSE_SIZES:
            u = build_daily_universe(panel, age_name, lo, hi, topn)
            if u.empty:
                continue
            daily, summ, yearly = summarize_universe(u)
            all_daily.append(daily)
            all_summ.append(summ)
            all_yearly.append(yearly)
            universe_meta.append({
                "age_spec": age_name, "age_min": lo, "age_max_exclusive": hi, "universe_size": topn,
                "days": int(u["date"].nunique()), "rows": int(len(u)), "symbols": int(u["symbol"].nunique()),
                "date_min": str(u["date"].min()), "date_max": str(u["date"].max()),
            })
    daily_df = pd.concat(all_daily, ignore_index=True)
    summary_df = pd.concat(all_summ, ignore_index=True)
    yearly_df = pd.concat(all_yearly, ignore_index=True)
    daily_df.to_csv(OUT / "rank154b_young_funding_daily.csv", index=False)
    summary_df.to_csv(OUT / "rank154b_young_funding_summary.csv", index=False)
    yearly_df.to_csv(OUT / "rank154b_young_funding_yearly.csv", index=False)
    meta = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "hypothesis": "Young coins with high funding exhibit crowding/attention continuation, unlike old coins where high funding becomes crowding reversal risk.",
        "listing_age_definition": "listing_days = current date - first observed Binance archive daily kline date for each symbol; not exchangeInfo onboardDate.",
        "selection": "Per historical date, filter eligible symbols by listing_days age bucket, then rank by same-date trailing 30d quote_volume and take TopN. No current ticker prefilter.",
        "signal": "carry_raw = funding_rate_last; high carry_raw is long / low carry_raw is short for top-bottom spread.",
        "cost_note": "spread_net_Xbps_rt subtracts X bps round-trip haircut per horizon from top-minus-bottom spread; it is a rough capacity/cost screen, not a fill-level backtest.",
        "universe_meta": universe_meta,
    }
    (OUT / "rank154b_young_funding_manifest.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ok] wrote {OUT}")
    print(summary_df.sort_values(["age_spec", "universe_size", "horizon"]).to_string(index=False))


if __name__ == "__main__":
    main()
