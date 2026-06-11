#!/usr/bin/env python3
"""Step 1.1 minimal stateful event study.

Scope: top gainer / top loser only, but split into new vs streak2 vs streak3+.
Universe: same-day eligible symbols ranked by daily quote_volume (top 150 by default).
Goal: check whether first-entry events and continuation events are meaningfully different.
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PANEL = Path("/root/clawd/jerry/momentum/reports/artifacts/rank154_long_history/daily_panel.pkl")
DEFAULT_OUT = ROOT / "reports" / "artifacts" / "binance_daily_event_study_v1"
HORIZONS = (1, 3, 5, 10)


def safe_float(v):
    try:
        x = float(v)
    except Exception:
        return None
    return x if math.isfinite(x) else None


def compute_derived(panel: pd.DataFrame) -> pd.DataFrame:
    p = panel.sort_values(["symbol", "date"]).copy()
    p["ret_1d"] = p["close"] / p.groupby("symbol", observed=True)["close"].shift(1) - 1.0
    p["fwd_ret_1d"] = p.groupby("symbol", observed=True)["close"].shift(-1) / p["close"] - 1.0
    p["fwd_ret_3d"] = p.groupby("symbol", observed=True)["close"].shift(-3) / p["close"] - 1.0
    p["fwd_ret_5d"] = p.groupby("symbol", observed=True)["close"].shift(-5) / p["close"] - 1.0
    p["fwd_ret_10d"] = p.groupby("symbol", observed=True)["close"].shift(-10) / p["close"] - 1.0

    p["fwd_funding_sum_5d"] = sum(
        p.groupby("symbol", observed=True)["funding_rate_sum"].shift(-k) for k in range(1, 6)
    )
    p["long_total_ret_5d"] = p["fwd_ret_5d"] - p["fwd_funding_sum_5d"]
    p["short_total_ret_5d"] = -p["fwd_ret_5d"] + p["fwd_funding_sum_5d"]

    future_rets = [p.groupby("symbol", observed=True)["close"].shift(-k) / p["close"] - 1.0 for k in range(1, 6)]
    mat = pd.concat(future_rets, axis=1)
    p["mae_long_5d"] = mat.min(axis=1)
    p["mfe_long_5d"] = mat.max(axis=1)
    return p


def tag_events_for_day(day: pd.DataFrame, event_topk: int) -> dict[int, dict[str, str]]:
    tags: dict[int, dict[str, str]] = {}
    d = day.dropna(subset=["ret_1d", "quote_volume"])
    if len(d) < max(20, event_topk * 2):
        return tags

    gainer_idx = set(d.sort_values(["ret_1d", "quote_volume"], ascending=[False, False]).head(event_topk).index)
    loser_idx = set(d.sort_values(["ret_1d", "quote_volume"], ascending=[True, False]).head(event_topk).index) - gainer_idx

    for idx in gainer_idx:
        tags[idx] = {"event_type": "top_gainer_1d"}
    for idx in loser_idx:
        tags[idx] = {"event_type": "top_loser_1d"}
    return tags


def classify_streaks(events: pd.DataFrame) -> pd.DataFrame:
    if events.empty:
        events["streak_day"] = []
        events["streak_label"] = []
        return events
    e = events.sort_values(["event_type", "symbol", "event_date"]).copy()
    e["event_date_ts"] = pd.to_datetime(e["event_date"])
    e["prev_event_date"] = e.groupby(["event_type", "symbol"], observed=True)["event_date_ts"].shift(1)
    e["gap_days"] = (e["event_date_ts"] - e["prev_event_date"]).dt.days
    streak_day = []
    streak_label = []
    prev_gap = e["gap_days"].to_numpy()
    prev_dates = e["prev_event_date"].to_numpy()
    for gap, prev in zip(prev_gap, prev_dates):
        if pd.isna(prev) or pd.isna(gap) or gap != 1:
            streak_day.append(1)
            streak_label.append("new")
        else:
            # Extend the streak computed so far by +1. We can do it iteratively
            # because rows are already sorted by (event_type, symbol, date).
            # But vectorized approach would be clearer; here we use a rolling counter instead.
            streak_day.append(0)
            streak_label.append("")
    # Correct iterative streak after initial placeholder
    # Use a fast loop per (event_type, symbol)
    streak_day_series = pd.Series(streak_day, index=e.index, dtype=int)
    streak_label_series = pd.Series(streak_label, index=e.index, dtype=object)
    for _, idx in e.groupby(["event_type", "symbol"], observed=True).groups.items():
        prev_gap_local = prev_gap[list(idx - e.index[0])] if False else e.loc[idx, "gap_days"].to_numpy()
        # The above branch intentionally never runs; recalc cleanly.
        g = e.loc[idx, "gap_days"].to_numpy()
        cur = 1
        out = []
        for gap, has_prev in zip(g, e.loc[idx, "prev_event_date"].notna().to_numpy()):
            if has_prev and gap == 1:
                cur += 1
            else:
                cur = 1
            out.append(cur)
        streak_day_series.loc[idx] = out
        streak_label_series.loc[idx] = ["new" if x == 1 else ("streak2" if x == 2 else "streak3_plus") for x in out]
    e["streak_day"] = streak_day_series
    e["streak_label"] = streak_label_series
    return e.drop(columns=["event_date_ts", "prev_event_date", "gap_days"])


def build_events(panel: pd.DataFrame, universe_topn: int, event_topk: int, min_listing_days: int) -> pd.DataFrame:
    eligible = panel[
        panel["is_eligible"].fillna(False)
        & (panel["listing_days"] >= min_listing_days)
        & panel["quote_volume"].notna()
        & panel["close"].notna()
    ].copy()

    rows = []

    for date, g in eligible.groupby("date", sort=True, observed=True):
        u = g.sort_values("quote_volume", ascending=False).head(universe_topn).copy()
        if len(u) < max(40, event_topk * 2):
            continue
        tagmap = tag_events_for_day(u, event_topk)
        for idx, meta in tagmap.items():
            r = u.loc[idx]
            event_type = meta["event_type"]
            rows.append({
                "event_date": pd.Timestamp(date).strftime("%Y-%m-%d"),
                "year": int(pd.Timestamp(date).year),
                "symbol": r["symbol"],
                "event_type": event_type,
                "close": safe_float(r["close"]),
                "ret_1d": safe_float(r.get("ret_1d")),
                "quote_volume": safe_float(r.get("quote_volume")),
                "listing_days": safe_float(r.get("listing_days")),
                "fwd_ret_1d": safe_float(r.get("fwd_ret_1d")),
                "fwd_ret_3d": safe_float(r.get("fwd_ret_3d")),
                "fwd_ret_5d": safe_float(r.get("fwd_ret_5d")),
                "fwd_ret_10d": safe_float(r.get("fwd_ret_10d")),
                "long_total_ret_5d": safe_float(r.get("long_total_ret_5d")),
                "short_total_ret_5d": safe_float(r.get("short_total_ret_5d")),
                "mae_long_5d": safe_float(r.get("mae_long_5d")),
                "mfe_long_5d": safe_float(r.get("mfe_long_5d")),
            })
    events = pd.DataFrame(rows)
    return classify_streaks(events)


def summarize(events: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    rows = []
    if events.empty:
        return pd.DataFrame()
    for keys, g0 in events.groupby(group_cols, sort=True):
        if not isinstance(keys, tuple):
            keys = (keys,)
        row = {c: k for c, k in zip(group_cols, keys)}
        row.update({"events": int(len(g0)), "symbols": int(g0["symbol"].nunique()), "years": int(g0["year"].nunique())})
        for h in HORIZONS:
            col = f"fwd_ret_{h}d"
            x = g0[col].dropna()
            row[f"ret_{h}d_n"] = int(len(x))
            row[f"ret_{h}d_mean"] = float(x.mean()) if len(x) else np.nan
            row[f"ret_{h}d_median"] = float(x.median()) if len(x) else np.nan
            row[f"ret_{h}d_win"] = float((x > 0).mean()) if len(x) else np.nan
        for side, col in [("long_total_5d", "long_total_ret_5d"), ("short_total_5d", "short_total_ret_5d")]:
            x = g0[col].dropna()
            row[f"{side}_mean"] = float(x.mean()) if len(x) else np.nan
            row[f"{side}_win"] = float((x > 0).mean()) if len(x) else np.nan
        for col in ["mae_long_5d", "mfe_long_5d"]:
            x = g0[col].dropna()
            row[f"{col}_median"] = float(x.median()) if len(x) else np.nan
            row[f"{col}_p10"] = float(x.quantile(0.10)) if len(x) else np.nan
            row[f"{col}_p90"] = float(x.quantile(0.90)) if len(x) else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", type=Path, default=DEFAULT_PANEL)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--universe-topn", type=int, default=150)
    ap.add_argument("--event-topk", type=int, default=15)
    ap.add_argument("--min-listing-days", type=int, default=30)
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    panel = pd.read_pickle(args.panel)
    panel = compute_derived(panel)
    events = build_events(panel, args.universe_topn, args.event_topk, args.min_listing_days)
    events.to_csv(args.out / "events_v1.csv", index=False)

    streak_summary = summarize(events, ["event_type", "streak_label"])
    type_summary = summarize(events, ["event_type"])
    streak_summary.to_csv(args.out / "streak_summary_v1.csv", index=False)
    type_summary.to_csv(args.out / "type_summary_v1.csv", index=False)

    manifest = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "input_panel": str(args.panel),
        "output_dir": str(args.out),
        "universe": f"eligible + listing_days >= {args.min_listing_days} + same-day quote_volume Top{args.universe_topn}",
        "events": f"Top {args.event_topk} top_gainer_1d / top_loser_1d",
        "streak_logic": "stateful streak_day per (symbol, event_type) in local universe",
        "focus": "Compare new vs streak2 vs streak3_plus",
        "limitations": [
            "Daily close data only",
            "No intraday pattern features yet",
            "No separate daily-quote-volume-only expansion yet",
            "This is a minimal control-size study, not a full stateful radar",
        ],
        "event_rows": int(len(events)),
        "event_symbols": int(events["symbol"].nunique()) if not events.empty else 0,
        "event_date_min": str(events["event_date"].min()) if not events.empty else None,
        "event_date_max": str(events["event_date"].max()) if not events.empty else None,
    }
    (args.out / "manifest_v1.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[ok] wrote {args.out}")
    print("\n[streak_summary]")
    cols = ["event_type", "streak_label", "events", "symbols", "ret_1d_mean", "ret_3d_mean", "ret_5d_mean", "ret_10d_mean", "long_total_5d_mean", "short_total_5d_mean", "mae_long_5d_median"]
    print(streak_summary[[c for c in cols if c in streak_summary.columns]].to_string(index=False))


if __name__ == "__main__":
    main()
