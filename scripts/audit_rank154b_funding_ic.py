#!/usr/bin/env python3
"""Factor IC audit for rank154b: funding-only young-coin signal.

Computes daily cross-sectional Spearman IC and top-bottom sleeve spreads for
`carry_raw = funding_rate_last` inside the same causal universe used by the
rank154b strict backtest.
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
ART_DIR = ROOT / "reports" / "artifacts" / "rank154b_young_funding_backtest"
HORIZONS = [1, 3, 5, 10]


def add_forward_returns(panel: pd.DataFrame, horizons=HORIZONS) -> pd.DataFrame:
    p = panel.sort_values(["symbol", "date"]).copy()
    out_parts = []
    for _, g in p.groupby("symbol", sort=False):
        g = g.copy()
        close = g["close"].astype(float)
        fr = g["funding_rate_sum"].astype(float).fillna(0.0)
        for h in horizons:
            g[f"fwd_price_{h}d"] = close.shift(-h) / close - 1.0
            g[f"fwd_funding_{h}d"] = fr.shift(-1).rolling(h, min_periods=h).sum().shift(-(h - 1))
            # Return earned by a LONG position including funding cashflow.
            g[f"fwd_long_total_{h}d"] = g[f"fwd_price_{h}d"] - g[f"fwd_funding_{h}d"]
        out_parts.append(g)
    return pd.concat(out_parts, ignore_index=True).sort_values(["date", "symbol"]).reset_index(drop=True)


def universe_day(day: pd.DataFrame, age_min: int, age_max: int, universe_size: int) -> pd.DataFrame:
    u = day[
        day["is_eligible"]
        & (day["listing_days"] >= age_min)
        & (day["listing_days"] < age_max)
        & day["trail_quote_volume_30d"].notna()
        & day["carry_raw"].notna()
    ].copy()
    return u.sort_values(["trail_quote_volume_30d", "quote_volume"], ascending=False).head(universe_size)


def daily_ic(panel: pd.DataFrame, *, label: str, age_min: int, age_max: int, universe_size: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ic_rows = []
    spread_rows = []
    decile_rows = []
    for d, day in panel.groupby("date", sort=True):
        u = universe_day(day, age_min, age_max, universe_size)
        if len(u) < max(8, min(15, universe_size // 2)):
            continue
        factor = u["carry_raw"].astype(float)
        for h in HORIZONS:
            for target_name in ["price", "long_total"]:
                col = f"fwd_{'price' if target_name == 'price' else 'long_total'}_{h}d"
                x = u[["symbol", "carry_raw", col]].dropna().copy()
                if len(x) < 8 or x["carry_raw"].nunique() < 2 or x[col].nunique() < 2:
                    continue
                ic = x["carry_raw"].corr(x[col], method="spearman")
                ic_rows.append({
                    "sample": label,
                    "date": str(pd.Timestamp(d).date()),
                    "horizon": h,
                    "target": target_name,
                    "n": int(len(x)),
                    "ic": float(ic),
                })
                k = max(2, int(round(len(x) * 0.2)))
                top = x.nlargest(k, "carry_raw")
                bot = x.nsmallest(k, "carry_raw")
                spread_rows.append({
                    "sample": label,
                    "date": str(pd.Timestamp(d).date()),
                    "horizon": h,
                    "target": target_name,
                    "n": int(len(x)),
                    "k": int(k),
                    "top_ret": float(top[col].mean()),
                    "bottom_ret": float(bot[col].mean()),
                    "top_minus_bottom": float(top[col].mean() - bot[col].mean()),
                    "top_factor_mean": float(top["carry_raw"].mean()),
                    "bottom_factor_mean": float(bot["carry_raw"].mean()),
                })
                # qcut deciles are noisy for 30 names, but useful as direction sanity.
                try:
                    q = max(2, min(10, len(x)))
                    x["bucket"] = pd.qcut(x["carry_raw"].rank(method="first"), q=q, labels=False, duplicates="drop") + 1
                    for b, bg in x.groupby("bucket"):
                        decile_rows.append({
                            "sample": label,
                            "date": str(pd.Timestamp(d).date()),
                            "horizon": h,
                            "target": target_name,
                            "bucket": int(b),
                            "n": int(len(bg)),
                            "ret": float(bg[col].mean()),
                            "factor_mean": float(bg["carry_raw"].mean()),
                        })
                except Exception:
                    pass
    return pd.DataFrame(ic_rows), pd.DataFrame(spread_rows), pd.DataFrame(decile_rows)


def summarize_ic(ic: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for keys, g in ic.groupby(["sample", "horizon", "target"], sort=True):
        sample, h, target = keys
        vals = g["ic"].dropna().astype(float)
        if len(vals) < 3:
            continue
        mean = vals.mean()
        std = vals.std(ddof=1)
        rows.append({
            "sample": sample,
            "horizon": int(h),
            "target": target,
            "days": int(len(vals)),
            "avg_n": float(g["n"].mean()),
            "ic_mean": float(mean),
            "ic_median": float(vals.median()),
            "ic_std": float(std),
            "icir_daily": float(mean / std) if std > 0 else np.nan,
            "icir_ann_sqrt365": float(mean / std * math.sqrt(365.25)) if std > 0 else np.nan,
            "t_stat": float(mean / (std / math.sqrt(len(vals)))) if std > 0 else np.nan,
            "positive_rate": float((vals > 0).mean()),
        })
    return pd.DataFrame(rows)


def summarize_spread(sp: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for keys, g in sp.groupby(["sample", "horizon", "target"], sort=True):
        sample, h, target = keys
        vals = g["top_minus_bottom"].dropna().astype(float)
        if len(vals) < 3:
            continue
        mean = vals.mean()
        std = vals.std(ddof=1)
        rows.append({
            "sample": sample,
            "horizon": int(h),
            "target": target,
            "days": int(len(vals)),
            "avg_n": float(g["n"].mean()),
            "top_ret_mean": float(g["top_ret"].mean()),
            "bottom_ret_mean": float(g["bottom_ret"].mean()),
            "spread_mean": float(mean),
            "spread_median": float(vals.median()),
            "spread_t_stat": float(mean / (std / math.sqrt(len(vals)))) if std > 0 else np.nan,
            "positive_rate": float((vals > 0).mean()),
            "top_factor_mean": float(g["top_factor_mean"].mean()),
            "bottom_factor_mean": float(g["bottom_factor_mean"].mean()),
        })
    return pd.DataFrame(rows)


def main() -> None:
    ART_DIR.mkdir(parents=True, exist_ok=True)
    panel = pd.read_pickle(PANEL_PATH)
    panel = panel[(panel["date"] >= pd.Timestamp("2021-05-01", tz="UTC")) & (panel["date"] <= pd.Timestamp("2026-04-30", tz="UTC"))].copy()
    panel = add_forward_returns(panel)
    specs = [
        {"label": "young_180_365_top30_core", "age_min": 180, "age_max": 365, "universe_size": 30},
        {"label": "young_180_365_top50_check", "age_min": 180, "age_max": 365, "universe_size": 50},
        {"label": "old_3y_top30_placebo", "age_min": 1095, "age_max": 10_000, "universe_size": 30},
    ]
    ics, spreads, deciles = [], [], []
    for spec in specs:
        print("[ic]", spec, flush=True)
        ic, sp, dec = daily_ic(panel, **spec)
        ics.append(ic); spreads.append(sp); deciles.append(dec)
    ic_daily = pd.concat(ics, ignore_index=True)
    spread_daily = pd.concat(spreads, ignore_index=True)
    decile_daily = pd.concat(deciles, ignore_index=True)
    ic_summary = summarize_ic(ic_daily)
    spread_summary = summarize_spread(spread_daily)
    # Yearly IC for core only.
    tmp = ic_daily.copy(); tmp["year"] = tmp["date"].str[:4]
    yearly = []
    for keys, g in tmp.groupby(["sample", "year", "horizon", "target"], sort=True):
        sample, year, h, target = keys
        vals = g["ic"].dropna()
        if len(vals) < 10:
            continue
        yearly.append({
            "sample": sample, "year": year, "horizon": int(h), "target": target,
            "days": int(len(vals)), "ic_mean": float(vals.mean()), "ic_median": float(vals.median()),
            "icir_daily": float(vals.mean()/vals.std(ddof=1)) if vals.std(ddof=1)>0 else np.nan,
            "positive_rate": float((vals>0).mean()),
        })
    yearly = pd.DataFrame(yearly)

    ic_daily.to_csv(ART_DIR / "rank154b_funding_ic_daily.csv", index=False)
    spread_daily.to_csv(ART_DIR / "rank154b_funding_spread_daily.csv", index=False)
    decile_daily.to_csv(ART_DIR / "rank154b_funding_decile_daily.csv", index=False)
    ic_summary.to_csv(ART_DIR / "rank154b_funding_ic_summary.csv", index=False)
    spread_summary.to_csv(ART_DIR / "rank154b_funding_spread_summary.csv", index=False)
    yearly.to_csv(ART_DIR / "rank154b_funding_ic_yearly.csv", index=False)
    results = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "factor_audit": {
            "rank154b_alpha_factor_count": 1,
            "factor": "carry_raw = funding_rate_last",
            "data_source": "daily_panel.pkl funding_rate_last derived from Binance funding records available by signal date",
            "ranking_direction": "higher funding -> higher rank -> long sleeve; lower funding -> short sleeve",
            "economic_interpretation": "attention/crowding continuation, NOT carry collection; positive Binance funding means longs pay shorts",
        },
        "ic_summary": ic_summary.to_dict(orient="records"),
        "spread_summary": spread_summary.to_dict(orient="records"),
    }
    (ART_DIR / "rank154b_funding_ic_results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("[ok] wrote IC artifacts", ART_DIR)
    print("\nIC summary core:")
    print(ic_summary[ic_summary["sample"].eq("young_180_365_top30_core")].to_string(index=False))
    print("\nSpread summary core:")
    print(spread_summary[spread_summary["sample"].eq("young_180_365_top30_core")].to_string(index=False))


if __name__ == "__main__":
    main()
