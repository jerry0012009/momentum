#!/usr/bin/env python3
"""Build Step 1 Binance daily event study from historical klines + funding.

Input panel is produced by momentum/scripts/validate_rank154_long_history.py and is
causal by construction: historical daily universe uses same-date trailing liquidity,
not today's ticker ranking.

This is intentionally an event-study, not a strategy backtest. It creates samples
for top-gainer/top-loser/funding-extreme events and summarizes forward returns.
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PANEL = Path("/root/clawd/jerry/momentum/reports/artifacts/rank154_long_history/daily_panel.pkl")
DEFAULT_OUT = ROOT / "reports" / "artifacts" / "binance_daily_event_study_v0"
HORIZONS = (1, 3, 5, 10)


def safe_float(x) -> float | None:
    try:
        v = float(x)
    except Exception:
        return None
    return v if math.isfinite(v) else None


def add_features(panel: pd.DataFrame) -> pd.DataFrame:
    p = panel.sort_values(["symbol", "date"]).copy()
    p["prev_close"] = p.groupby("symbol", observed=True)["close"].shift(1)
    p["ret_1d"] = p["close"] / p["prev_close"] - 1.0
    p["ret_3d"] = p["close"] / p.groupby("symbol", observed=True)["close"].shift(3) - 1.0
    p["ret_5d"] = p["close"] / p.groupby("symbol", observed=True)["close"].shift(5) - 1.0

    # funding_count is the observed number of settlements in the UTC day.
    # If 3 events/day -> 8h interval; 6 -> 4h; 24 -> 1h.
    p["funding_interval_est_hours"] = np.where(
        p["funding_count"].fillna(0) > 0,
        24.0 / p["funding_count"].astype(float),
        np.nan,
    )
    p["funding_per_hour_est"] = p["carry_raw"] / p["funding_interval_est_hours"]

    for h in HORIZONS:
        p[f"fwd_close_{h}d"] = p.groupby("symbol", observed=True)["close"].shift(-h)
        p[f"fwd_ret_{h}d"] = p[f"fwd_close_{h}d"] / p["close"] - 1.0
        # Sum realized funding events over the next h daily rows: t+1 ... t+h.
        # Do not use rolling on shift(-1): that accidentally mixes prior rows.
        future_funding_terms = [
            p.groupby("symbol", observed=True)["funding_rate_sum"].shift(-k)
            for k in range(1, h + 1)
        ]
        p[f"fwd_funding_sum_{h}d"] = pd.concat(future_funding_terms, axis=1).sum(axis=1, min_count=1)
        # Convention: positive funding = longs pay shorts.
        p[f"long_total_ret_{h}d"] = p[f"fwd_ret_{h}d"] - p[f"fwd_funding_sum_{h}d"]
        p[f"short_total_ret_{h}d"] = -p[f"fwd_ret_{h}d"] + p[f"fwd_funding_sum_{h}d"]

    # Close-path MAE/MFE over 5d and 10d. Daily close only; intraday risk is understated.
    for h in (5, 10):
        future_rets = []
        for k in range(1, h + 1):
            future_rets.append(p.groupby("symbol", observed=True)["close"].shift(-k) / p["close"] - 1.0)
        mat = pd.concat(future_rets, axis=1)
        p[f"mae_long_{h}d"] = mat.min(axis=1)
        p[f"mfe_long_{h}d"] = mat.max(axis=1)
        p[f"mae_short_{h}d"] = (-mat).min(axis=1)
        p[f"mfe_short_{h}d"] = (-mat).max(axis=1)
    return p


def tag_events_for_day(day: pd.DataFrame, top_k: int) -> dict[int, set[str]]:
    tags: dict[int, set[str]] = {}

    def add(indices: Iterable[int], tag: str) -> None:
        for idx in indices:
            tags.setdefault(idx, set()).add(tag)

    d_ret = day.dropna(subset=["ret_1d"])
    if len(d_ret) >= max(20, top_k * 2):
        top_ret_idx = set(d_ret.sort_values(["ret_1d", "trail_quote_volume_30d"], ascending=[False, False]).head(top_k).index)
        bot_ret_idx = set(d_ret.sort_values(["ret_1d", "trail_quote_volume_30d"], ascending=[True, False]).head(top_k).index) - top_ret_idx
        add(top_ret_idx, "top_gainer_1d")
        add(bot_ret_idx, "top_loser_1d")

    d_f = day.dropna(subset=["funding_per_hour_est"])
    if len(d_f) >= max(20, top_k * 2):
        top_f_idx = set(d_f.sort_values(["funding_per_hour_est", "trail_quote_volume_30d"], ascending=[False, False]).head(top_k).index)
        bot_f_idx = set(d_f.sort_values(["funding_per_hour_est", "trail_quote_volume_30d"], ascending=[True, False]).head(top_k).index) - top_f_idx
        add(top_f_idx, "funding_extreme_positive")
        add(bot_f_idx, "funding_extreme_negative")

    return tags


def build_events(panel: pd.DataFrame, universe_topn: int, event_topk: int, min_listing_days: int) -> pd.DataFrame:
    rows = []
    eligible = panel[
        panel["is_eligible"].fillna(False)
        & panel["trail_quote_volume_30d"].notna()
        & (panel["listing_days"] >= min_listing_days)
        & panel["close"].notna()
    ].copy()

    for date, g in eligible.groupby("date", sort=True, observed=True):
        u = g.sort_values(["trail_quote_volume_30d", "quote_volume"], ascending=False).head(universe_topn).copy()
        if len(u) < max(30, event_topk * 2):
            continue
        tagmap = tag_events_for_day(u, event_topk)
        if not tagmap:
            continue
        for idx, tags in tagmap.items():
            r = u.loc[idx]
            tag_list = sorted(tags)
            row = {
                "event_date": pd.Timestamp(date).strftime("%Y-%m-%d"),
                "year": int(pd.Timestamp(date).year),
                "symbol": r["symbol"],
                "tags": "+".join(tag_list),
                "tag_count": len(tag_list),
                "is_top_gainer": "top_gainer_1d" in tags,
                "is_top_loser": "top_loser_1d" in tags,
                "is_high_funding": "funding_extreme_positive" in tags,
                "is_negative_funding": "funding_extreme_negative" in tags,
                "close": safe_float(r["close"]),
                "ret_1d": safe_float(r.get("ret_1d")),
                "ret_3d": safe_float(r.get("ret_3d")),
                "ret_5d": safe_float(r.get("ret_5d")),
                "carry_raw": safe_float(r.get("carry_raw")),
                "funding_rate_sum": safe_float(r.get("funding_rate_sum")),
                "funding_count": safe_float(r.get("funding_count")),
                "funding_interval_est_hours": safe_float(r.get("funding_interval_est_hours")),
                "funding_per_hour_est": safe_float(r.get("funding_per_hour_est")),
                "listing_days": safe_float(r.get("listing_days")),
                "trail_quote_volume_30d": safe_float(r.get("trail_quote_volume_30d")),
                "quote_volume": safe_float(r.get("quote_volume")),
                "universe_topn": universe_topn,
                "event_topk": event_topk,
            }
            for h in HORIZONS:
                for col in [f"fwd_ret_{h}d", f"fwd_funding_sum_{h}d", f"long_total_ret_{h}d", f"short_total_ret_{h}d"]:
                    row[col] = safe_float(r.get(col))
            for h in (5, 10):
                for col in [f"mae_long_{h}d", f"mfe_long_{h}d", f"mae_short_{h}d", f"mfe_short_{h}d"]:
                    row[col] = safe_float(r.get(col))
            rows.append(row)
    return pd.DataFrame(rows)


def summarize_group(events: pd.DataFrame, group_col: str) -> pd.DataFrame:
    rows = []
    if events.empty:
        return pd.DataFrame()
    for key, g0 in events.groupby(group_col, dropna=False, sort=True):
        row = {group_col: key, "events": int(len(g0)), "symbols": int(g0["symbol"].nunique()), "years": int(g0["year"].nunique())}
        for h in HORIZONS:
            for side, col in [("price", f"fwd_ret_{h}d"), ("long_total", f"long_total_ret_{h}d"), ("short_total", f"short_total_ret_{h}d")]:
                g = g0[col].dropna()
                row[f"{side}_{h}d_n"] = int(len(g))
                row[f"{side}_{h}d_mean"] = float(g.mean()) if len(g) else np.nan
                row[f"{side}_{h}d_median"] = float(g.median()) if len(g) else np.nan
                row[f"{side}_{h}d_win_rate"] = float((g > 0).mean()) if len(g) else np.nan
        for h in (5, 10):
            for col in [f"mae_long_{h}d", f"mfe_long_{h}d", f"mae_short_{h}d", f"mfe_short_{h}d"]:
                g = g0[col].dropna()
                row[f"{col}_median"] = float(g.median()) if len(g) else np.nan
                row[f"{col}_p10"] = float(g.quantile(0.10)) if len(g) else np.nan
                row[f"{col}_p90"] = float(g.quantile(0.90)) if len(g) else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def summarize_atomic_tags(events: pd.DataFrame) -> pd.DataFrame:
    rows = []
    atomic = sorted({t for tags in events["tags"].dropna().astype(str) for t in tags.split("+")})
    for tag in atomic:
        g0 = events[events["tags"].astype(str).str.split("+").apply(lambda xs: tag in xs)]
        row = {"tag": tag, "events": int(len(g0)), "symbols": int(g0["symbol"].nunique()), "years": int(g0["year"].nunique())}
        for h in HORIZONS:
            for side, col in [("price", f"fwd_ret_{h}d"), ("long_total", f"long_total_ret_{h}d"), ("short_total", f"short_total_ret_{h}d")]:
                g = g0[col].dropna()
                row[f"{side}_{h}d_mean"] = float(g.mean()) if len(g) else np.nan
                row[f"{side}_{h}d_median"] = float(g.median()) if len(g) else np.nan
                row[f"{side}_{h}d_win_rate"] = float((g > 0).mean()) if len(g) else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", type=Path, default=DEFAULT_PANEL)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--universe-topn", type=int, default=100)
    ap.add_argument("--event-topk", type=int, default=20)
    ap.add_argument("--min-listing-days", type=int, default=30)
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    panel = pd.read_pickle(args.panel)
    panel = add_features(panel)
    events = build_events(panel, args.universe_topn, args.event_topk, args.min_listing_days)
    events.to_csv(args.out / "events_v0.csv", index=False)

    atomic = summarize_atomic_tags(events)
    atomic.to_csv(args.out / "summary_by_tag_v0.csv", index=False)
    combo = summarize_group(events, "tags")
    combo.to_csv(args.out / "combo_summary_v0.csv", index=False)
    yearly = summarize_group(events, "year")
    yearly.to_csv(args.out / "yearly_summary_v0.csv", index=False)

    manifest = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "input_panel": str(args.panel),
        "output_dir": str(args.out),
        "panel_rows": int(len(panel)),
        "panel_date_min": str(panel["date"].min()),
        "panel_date_max": str(panel["date"].max()),
        "panel_symbols": int(panel["symbol"].nunique()),
        "universe": {
            "is_eligible": True,
            "trail_quote_volume_30d": "not null",
            "min_listing_days": args.min_listing_days,
            "per_day_topn_by_trailing_quote_volume": args.universe_topn,
        },
        "events": {
            "top_gainer_1d": f"per-day Top {args.event_topk} ret_1d within universe",
            "top_loser_1d": f"per-day Bottom {args.event_topk} ret_1d within universe",
            "funding_extreme_positive": f"per-day Top {args.event_topk} funding_per_hour_est within universe",
            "funding_extreme_negative": f"per-day Bottom {args.event_topk} funding_per_hour_est within universe",
        },
        "funding_convention": "positive funding = longs pay shorts; long_total_ret = price_return - future funding sum; short_total_ret = -price_return + future funding sum",
        "limitations": [
            "Daily close data only; no intraday entry/exit or BBO/sweep tradability.",
            "MAE/MFE uses future daily closes, so intraday risk is understated.",
            "funding_per_hour_est uses observed daily funding_count; settlement interval changes should be verified in deeper studies.",
            "This is event discovery, not a live-ready strategy backtest.",
        ],
        "event_rows": int(len(events)),
        "event_symbols": int(events["symbol"].nunique()) if not events.empty else 0,
        "event_date_min": str(events["event_date"].min()) if not events.empty else None,
        "event_date_max": str(events["event_date"].max()) if not events.empty else None,
    }
    (args.out / "manifest_v0.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[ok] wrote {args.out}")
    print("\n[summary_by_tag]")
    cols = ["tag", "events", "symbols", "price_1d_mean", "price_3d_mean", "price_5d_mean", "price_10d_mean", "long_total_5d_mean", "short_total_5d_mean"]
    print(atomic[[c for c in cols if c in atomic.columns]].to_string(index=False))
    print("\n[top combos by abs 5d price mean]")
    if not combo.empty and "price_5d_mean" in combo.columns:
        cc = combo.copy()
        cc["abs_price_5d_mean"] = cc["price_5d_mean"].abs()
        show = cc.sort_values(["abs_price_5d_mean", "events"], ascending=[False, False]).head(20)
        cols2 = ["tags", "events", "symbols", "price_1d_mean", "price_3d_mean", "price_5d_mean", "price_5d_win_rate", "mae_long_5d_median", "mfe_long_5d_median"]
        print(show[[c for c in cols2 if c in show.columns]].to_string(index=False))


if __name__ == "__main__":
    main()
