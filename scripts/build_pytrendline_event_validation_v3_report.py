#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.factors.pytrendline_bridge import PyTrendlineConfig, detect_pytrendlines  # noqa: E402

ART = ROOT / "reports" / "artifacts" / "pytrendline_event_validation_v3"
SITE = ROOT / "reports" / "site" / "factors" / "pytrendline_event_validation_v3"
CACHE = ART / "cache"

DEFAULT_SYMBOLS = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"]
DEFAULT_INTERVAL = "60m"
DEFAULT_PERIOD = "120d"
DEFAULT_WINDOW_BARS = 96
DEFAULT_SNAPSHOT_STEP_BARS = 24
DEFAULT_HORIZONS = [6, 24, 48, 72]
DEFAULT_CONFIRM_BARS = 2
DEFAULT_TOL_MULT = 0.08

EVENT_ORDER = [
    "support_touch_raw",
    "support_breakout_raw",
    "resistance_touch_raw",
    "resistance_breakout_raw",
    "support_rebound_confirm_1",
    "support_rebound_confirm_2",
    "resistance_rebound_confirm_1",
    "resistance_rebound_confirm_2",
    "support_breakout_confirm_1",
    "support_breakout_confirm_2",
    "resistance_breakout_confirm_1",
    "resistance_breakout_confirm_2",
]

FAMILY_ORDER = [
    "touch_raw",
    "breakout_raw",
    "rebound_confirm_1",
    "rebound_confirm_2",
    "breakout_confirm_1",
    "breakout_confirm_2",
]

MIRRORED_BREAKOUT_FAMILIES = {"breakout_raw", "breakout_confirm_1", "breakout_confirm_2"}
MIRRORED_BREAKOUT_GROUP_COLS = [
    "symbol",
    "event_family",
    "event_timestamp",
    "confirm_timestamp",
    "action_timestamp",
]


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def flatten_yf_columns(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    return df


def download_bars(symbol: str, period: str, interval: str, *, refresh: bool = False) -> pd.DataFrame:
    ensure_dir(CACHE)
    cache_name = f"{symbol.replace('-', '_')}__{period}__{interval}.csv"
    cache_path = CACHE / cache_name
    if cache_path.exists() and not refresh:
        bars = pd.read_csv(cache_path, parse_dates=["timestamp"])
        bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
        return bars.sort_values("timestamp").reset_index(drop=True)

    raw = yf.download(symbol, period=period, interval=interval, auto_adjust=False, progress=False)
    if raw is None or raw.empty:
        raise ValueError(f"No data for {symbol}")
    raw = flatten_yf_columns(raw)
    bars = raw.reset_index().rename(
        columns={
            "Datetime": "timestamp",
            "Date": "timestamp",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    )
    bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
    keep = [c for c in ["timestamp", "open", "high", "low", "close", "volume"] if c in bars.columns]
    bars = bars[keep].dropna(subset=["open", "high", "low", "close"]).sort_values("timestamp").reset_index(drop=True)
    bars.to_csv(cache_path, index=False)
    return bars


def representative_lines(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    rep = df[df.get("is_best_from_duplicate_group", False).fillna(False)].copy()
    if rep.empty:
        rep = df.copy()
    return rep.reset_index(drop=True)


def line_value(row: pd.Series, local_idx: float) -> float:
    return float(row["m"]) * float(local_idx) + float(row["b"])


def confidence_tier(n: int) -> str:
    if n >= 250:
        return "high"
    if n >= 100:
        return "medium"
    if n >= 40:
        return "low"
    return "very_low"


def directional_label(up_ratio: float, mean_ret: float) -> str:
    if pd.isna(up_ratio) or pd.isna(mean_ret):
        return "unknown"
    if up_ratio >= 0.55 and mean_ret > 0:
        return "more_likely_up"
    if up_ratio <= 0.45 and mean_ret < 0:
        return "more_likely_down"
    return "mixed"


def event_family(event_type: str) -> str:
    e = str(event_type)
    if e.endswith("touch_raw"):
        return "touch_raw"
    if e.endswith("breakout_raw"):
        return "breakout_raw"
    if "rebound_confirm_1" in e:
        return "rebound_confirm_1"
    if "rebound_confirm_2" in e:
        return "rebound_confirm_2"
    if "breakout_confirm_1" in e:
        return "breakout_confirm_1"
    if "breakout_confirm_2" in e:
        return "breakout_confirm_2"
    return "other"


def add_event_family(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "event_type" in out.columns:
        out["event_family"] = out["event_type"].astype(str).map(event_family)
        out["event_family"] = pd.Categorical(out["event_family"], categories=FAMILY_ORDER, ordered=True)
    return out


def summarize(df: pd.DataFrame, horizons: list[int], *, key_col: str = "event_type") -> pd.DataFrame:
    rows: list[dict] = []
    if df.empty:
        return pd.DataFrame(columns=[key_col, "horizon", "events", "mean_ret", "median_ret", "up_ratio", "confidence_tier", "direction_label"])

    for h in horizons:
        col = f"fwd_ret_h{h}"
        g = (
            df.groupby(key_col, dropna=False)[col]
            .agg(events="size", mean_ret="mean", median_ret="median", up_ratio=lambda s: float((s > 0).mean()))
            .reset_index()
        )
        g["horizon"] = h
        g["confidence_tier"] = g["events"].map(confidence_tier)
        g["direction_label"] = g.apply(lambda r: directional_label(float(r["up_ratio"]), float(r["mean_ret"])), axis=1)
        rows.append(g)

    out = pd.concat(rows, ignore_index=True)
    if key_col == "event_type":
        out[key_col] = pd.Categorical(out[key_col], categories=EVENT_ORDER, ordered=True)
    out = out.sort_values([key_col, "horizon"]).reset_index(drop=True)
    return out


def purge_events(df: pd.DataFrame, purge_gap: int) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    keep_indices: list[int] = []
    for (symbol, event_type), g in df.sort_values(["symbol", "event_type", "action_index"]).groupby(["symbol", "event_type"], sort=False):
        _ = (symbol, event_type)
        last_kept = -10**9
        for idx, row in g.iterrows():
            ai = int(row["action_index"])
            if ai > last_kept + purge_gap:
                keep_indices.append(int(idx))
                last_kept = ai
    out = df.loc[sorted(set(keep_indices))].copy().reset_index(drop=True)
    return out


def resolve_exact_mirrored_breakout_pairs(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if df.empty:
        summary_cols = [
            "event_family",
            "paired_groups",
            "rows_in_paired_groups",
            "dropped_rows",
            "survivor_rows",
            "score_tie_groups",
        ]
        detail_cols = [
            *MIRRORED_BREAKOUT_GROUP_COLS,
            "group_rows",
            "support_rows",
            "resistance_rows",
            "winner_event_type",
            "winner_engine_line_id",
            "winner_line_score",
            "winner_side",
            "score_tie",
            "dropped_event_types",
            "dropped_engine_line_ids",
            "dropped_line_scores",
        ]
        return (
            df.copy(),
            pd.DataFrame(columns=summary_cols),
            pd.DataFrame(columns=detail_cols),
            pd.DataFrame(columns=list(df.columns) + ["drop_reason"]),
        )

    work = add_event_family(df)
    families = work["event_family"].astype(str)
    mask = families.isin(MIRRORED_BREAKOUT_FAMILIES)
    if not mask.any():
        return work.copy(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(columns=list(work.columns) + ["drop_reason"])

    paired_details: list[dict] = []
    dropped_frames: list[pd.DataFrame] = []
    drop_indices: list[int] = []

    subset = work.loc[mask].copy()
    subset["_event_type_str"] = subset["event_type"].astype(str)
    subset["_side"] = np.where(subset["_event_type_str"].str.startswith("support_"), "support", "resistance")
    subset["_line_score_for_sort"] = subset["line_score"].fillna(-1e18).astype(float)
    subset["_engine_line_id_str"] = subset["engine_line_id"].astype(str)

    for group_key, g in subset.groupby(MIRRORED_BREAKOUT_GROUP_COLS, dropna=False, sort=False):
        sides = set(g["_side"].tolist())
        if len(g) < 2 or sides != {"support", "resistance"}:
            continue

        ranked = g.sort_values(
            ["_line_score_for_sort", "_event_type_str", "_engine_line_id_str"],
            ascending=[False, True, True],
        ).copy()
        winner = ranked.iloc[0]
        losers = ranked.iloc[1:].copy()
        score_tie = bool((ranked["_line_score_for_sort"] == float(winner["_line_score_for_sort"])).sum() > 1)

        if not losers.empty:
            loser_frame = work.loc[losers.index].copy()
            loser_frame["drop_reason"] = "exact_mirrored_breakout_pair_lower_score"
            dropped_frames.append(loser_frame)
            drop_indices.extend(losers.index.tolist())

        paired_details.append(
            {
                **dict(zip(MIRRORED_BREAKOUT_GROUP_COLS, group_key)),
                "group_rows": int(len(g)),
                "support_rows": int((g["_side"] == "support").sum()),
                "resistance_rows": int((g["_side"] == "resistance").sum()),
                "winner_event_type": str(winner["event_type"]),
                "winner_engine_line_id": str(winner["engine_line_id"]),
                "winner_line_score": float(winner["line_score"]) if pd.notna(winner["line_score"]) else np.nan,
                "winner_side": str(winner["_side"]),
                "score_tie": bool(score_tie),
                "dropped_event_types": " | ".join(losers["event_type"].astype(str).tolist()),
                "dropped_engine_line_ids": " | ".join(losers["engine_line_id"].astype(str).tolist()),
                "dropped_line_scores": " | ".join(
                    [f"{float(v):.6f}" if pd.notna(v) else "nan" for v in losers["line_score"].tolist()]
                ),
            }
        )

    filtered = work.drop(index=sorted(set(drop_indices))).copy().reset_index(drop=True)
    detail_df = pd.DataFrame(paired_details)
    dropped_df = pd.concat(dropped_frames, ignore_index=True) if dropped_frames else pd.DataFrame(columns=list(work.columns) + ["drop_reason"])

    summary_rows: list[dict] = []
    for family in FAMILY_ORDER:
        if family not in MIRRORED_BREAKOUT_FAMILIES:
            continue
        fg = detail_df[detail_df["event_family"] == family] if not detail_df.empty else pd.DataFrame()
        summary_rows.append(
            {
                "event_family": family,
                "paired_groups": int(len(fg)),
                "rows_in_paired_groups": int(fg["group_rows"].sum()) if not fg.empty else 0,
                "dropped_rows": int((fg["group_rows"] - 1).sum()) if not fg.empty else 0,
                "survivor_rows": int(len(fg)),
                "score_tie_groups": int(fg["score_tie"].sum()) if not fg.empty else 0,
            }
        )
    summary_df = pd.DataFrame(summary_rows)
    return filtered, summary_df, detail_df, dropped_df


def _detect_snapshot_lines(
    bars: pd.DataFrame,
    as_of_idx: int,
    window_bars: int,
    cfg: PyTrendlineConfig,
    tol_mult: float,
) -> tuple[pd.DataFrame, int, float]:
    start_idx = as_of_idx - window_bars + 1
    window = bars.iloc[start_idx : as_of_idx + 1].copy()
    result = detect_pytrendlines(window, config=cfg)

    support = representative_lines(result.get("support_trendlines", pd.DataFrame())).copy()
    resistance = representative_lines(result.get("resistance_trendlines", pd.DataFrame())).copy()
    if not support.empty:
        support["line_side"] = "support"
    if not resistance.empty:
        resistance["line_side"] = "resistance"

    lines = pd.concat([support, resistance], ignore_index=True) if (not support.empty or not resistance.empty) else pd.DataFrame()
    if lines.empty:
        return lines, start_idx, 0.0

    lines = lines.copy()
    keep_cols = [
        "id",
        "line_side",
        "m",
        "b",
        "score",
        "slope",
        "is_breakout",
        "starts_at_date",
        "ends_at_date",
        "breakout_date",
        "num_points",
    ]
    out_cols = [c for c in keep_cols if c in lines.columns]
    lines = lines[out_cols].copy()
    for c in ["starts_at_date", "ends_at_date", "breakout_date"]:
        if c in lines.columns:
            lines[c] = pd.to_datetime(lines[c], utc=True, errors="coerce")

    avg_range = float((window["high"] - window["low"]).mean())
    tolerance = max(1e-12, avg_range * tol_mult)
    return lines, start_idx, tolerance


def _candidate_events_for_line(
    *,
    symbol: str,
    line: pd.Series,
    bars: pd.DataFrame,
    start_idx: int,
    as_of_idx: int,
    t: int,
    tolerance: float,
    horizons: list[int],
) -> list[dict]:
    side = str(line["line_side"])

    local_tm1 = (t - 1) - start_idx
    local_asof = as_of_idx - start_idx
    local_t = t - start_idx
    local_t1 = (t + 1) - start_idx
    local_t2 = (t + 2) - start_idx

    lv_prev = line_value(line, local_tm1)
    lv_asof = line_value(line, local_asof)
    lv_t = line_value(line, local_t)
    lv_t1 = line_value(line, local_t1)
    lv_t2 = line_value(line, local_t2)

    asof_close = float(bars.loc[as_of_idx, "close"])
    prev_close = float(bars.loc[t - 1, "close"])
    o = float(bars.loc[t, "open"])
    h = float(bars.loc[t, "high"])
    l = float(bars.loc[t, "low"])
    c = float(bars.loc[t, "close"])
    c1 = float(bars.loc[t + 1, "close"])
    c2 = float(bars.loc[t + 2, "close"])

    if side == "support":
        # Geometry guard: a visible support line should still sit at or below price
        # when the snapshot is taken. Otherwise we are really labeling an already-
        # invalid / crossed line as future support and can create mirror duplicates.
        if lv_asof > (asof_close + tolerance):
            return []

        was_above = prev_close >= (lv_prev - tolerance)
        breakout_raw = was_above and (c < (lv_t - tolerance))
        touch_raw = was_above and (l <= lv_t + tolerance) and (c >= lv_t - tolerance) and (not breakout_raw)
        rebound_confirm_1 = touch_raw and (c1 > lv_t1 + tolerance)
        rebound_confirm_2 = touch_raw and (c1 > lv_t1 + tolerance) and (c2 > lv_t2 + tolerance)
        breakout_confirm_1 = breakout_raw and (c1 < lv_t1 - tolerance)
        breakout_confirm_2 = breakout_raw and (c1 < lv_t1 - tolerance) and (c2 < lv_t2 - tolerance)

        # Event-time geometry gate: a support breakout row is unreliable if the
        # support line already sits above the entire event candle's high.
        if breakout_raw and (lv_t > h):
            breakout_raw = False
            breakout_confirm_1 = False
            breakout_confirm_2 = False

        event_map = [
            ("support_touch_raw", touch_raw, 0),
            ("support_breakout_raw", breakout_raw, 0),
            ("support_rebound_confirm_1", rebound_confirm_1, 1),
            ("support_rebound_confirm_2", rebound_confirm_2, 2),
            ("support_breakout_confirm_1", breakout_confirm_1, 1),
            ("support_breakout_confirm_2", breakout_confirm_2, 2),
        ]
    else:
        # Mirror guard for resistance: it should still be at or above price when
        # the snapshot becomes visible.
        if lv_asof < (asof_close - tolerance):
            return []

        was_below = prev_close <= (lv_prev + tolerance)
        breakout_raw = was_below and (c > (lv_t + tolerance))
        touch_raw = was_below and (h >= lv_t - tolerance) and (c <= lv_t + tolerance) and (not breakout_raw)
        rebound_confirm_1 = touch_raw and (c1 < lv_t1 - tolerance)
        rebound_confirm_2 = touch_raw and (c1 < lv_t1 - tolerance) and (c2 < lv_t2 - tolerance)
        breakout_confirm_1 = breakout_raw and (c1 > lv_t1 + tolerance)
        breakout_confirm_2 = breakout_raw and (c1 > lv_t1 + tolerance) and (c2 > lv_t2 + tolerance)

        # Mirror event-time geometry gate for resistance breakouts.
        if breakout_raw and (lv_t < l):
            breakout_raw = False
            breakout_confirm_1 = False
            breakout_confirm_2 = False

        event_map = [
            ("resistance_touch_raw", touch_raw, 0),
            ("resistance_breakout_raw", breakout_raw, 0),
            ("resistance_rebound_confirm_1", rebound_confirm_1, 1),
            ("resistance_rebound_confirm_2", rebound_confirm_2, 2),
            ("resistance_breakout_confirm_1", breakout_confirm_1, 1),
            ("resistance_breakout_confirm_2", breakout_confirm_2, 2),
        ]

    rows: list[dict] = []
    for event_type, flag, confirm_level in event_map:
        if not flag:
            continue

        confirm_bar_idx = t + confirm_level
        action_idx = confirm_bar_idx + 1

        rec = {
            "symbol": symbol,
            "event_type": event_type,
            "event_side": side,
            "confirm_level": int(confirm_level),
            "snapshot_asof_index": int(as_of_idx),
            "snapshot_asof_timestamp": bars.loc[as_of_idx, "timestamp"],
            "event_index": int(t),
            "event_timestamp": bars.loc[t, "timestamp"],
            "confirm_index": int(confirm_bar_idx),
            "confirm_timestamp": bars.loc[confirm_bar_idx, "timestamp"],
            "action_index": int(action_idx),
            "action_timestamp": bars.loc[action_idx, "timestamp"],
            "snapshot_age_bars": int(t - as_of_idx),
            "engine_line_id": str(line.get("id")),
            "line_score": float(line.get("score", np.nan)) if pd.notna(line.get("score", np.nan)) else np.nan,
            "line_slope": float(line.get("slope", np.nan)) if pd.notna(line.get("slope", np.nan)) else np.nan,
            "line_value_event": float(lv_t),
            "line_value_confirm": float(line_value(line, confirm_bar_idx - start_idx)),
            "event_open": o,
            "event_high": h,
            "event_low": l,
            "event_close": c,
            "confirm_close": float(bars.loc[confirm_bar_idx, "close"]),
            "action_open": float(bars.loc[action_idx, "open"]),
            "tolerance": float(tolerance),
        }

        entry = float(bars.loc[action_idx, "open"])
        for hh in horizons:
            fut_close = float(bars.loc[action_idx + hh, "close"])
            rec[f"fwd_ret_h{hh}"] = fut_close / entry - 1.0
        rows.append(rec)

    return rows


def collect_events_for_symbol(
    symbol: str,
    bars: pd.DataFrame,
    *,
    window_bars: int,
    snapshot_step_bars: int,
    horizons: list[int],
    confirm_bars: int,
    tol_mult: float,
    cfg: PyTrendlineConfig,
) -> pd.DataFrame:
    rows: list[dict] = []
    max_h = max(horizons)
    # Need room for t+2 confirmation and action from next bar: t + confirm_bars + 1 + max_h <= len-1
    max_t = len(bars) - (confirm_bars + 1 + max_h) - 1

    if max_t <= window_bars:
        return pd.DataFrame()

    snapshot_points = range(window_bars - 1, max_t, snapshot_step_bars)
    for snap_i, as_of_idx in enumerate(snapshot_points, start=1):
        lines, start_idx, tolerance = _detect_snapshot_lines(
            bars=bars,
            as_of_idx=as_of_idx,
            window_bars=window_bars,
            cfg=cfg,
            tol_mult=tol_mult,
        )

        if snap_i % 20 == 0:
            print(f"snapshot symbol={symbol} i={snap_i} asof={bars.loc[as_of_idx, 'timestamp'].isoformat()} lines={len(lines)}", flush=True)

        if lines.empty:
            continue

        t_start = as_of_idx + 1
        t_end = min(as_of_idx + snapshot_step_bars, max_t)

        for t in range(t_start, t_end + 1):
            cand: list[dict] = []
            for _, line in lines.iterrows():
                cand.extend(
                    _candidate_events_for_line(
                        symbol=symbol,
                        line=line,
                        bars=bars,
                        start_idx=start_idx,
                        as_of_idx=as_of_idx,
                        t=t,
                        tolerance=tolerance,
                        horizons=horizons,
                    )
                )

            if not cand:
                continue

            cdf = pd.DataFrame(cand)
            # Per symbol+bar keep top-score line per event_type to avoid same-bar line explosion
            cdf["line_score"] = cdf["line_score"].fillna(-1e18)
            idx = cdf.groupby("event_type", sort=False)["line_score"].idxmax()
            selected = cdf.loc[idx].copy()
            rows.extend(selected.to_dict("records"))

    out = pd.DataFrame(rows)
    if out.empty:
        return out

    out = out.drop_duplicates(
        subset=[
            "symbol",
            "event_type",
            "event_index",
            "action_index",
            "engine_line_id",
        ]
    ).reset_index(drop=True)

    return out


def render_table(df: pd.DataFrame, limit: int = 60) -> str:
    if df is None or df.empty:
        return "<p><em>empty</em></p>"
    shown = df.head(limit).copy()
    for col in shown.columns:
        if pd.api.types.is_datetime64_any_dtype(shown[col]):
            shown[col] = shown[col].dt.strftime("%Y-%m-%d %H:%M")
        elif pd.api.types.is_float_dtype(shown[col]):
            shown[col] = shown[col].map(lambda x: round(float(x), 6) if pd.notna(x) else "")
    return shown.to_html(index=False, classes="tbl", border=0)


def build_baseline_summary(symbols: list[str], period: str, interval: str, horizons: list[int]) -> pd.DataFrame:
    rows: list[dict] = []
    for symbol in symbols:
        bars = download_bars(symbol, period, interval, refresh=False)
        for h in horizons:
            eligible = len(bars) - 1 - h
            if eligible <= 0:
                continue
            opens = bars["open"].iloc[1 : 1 + eligible].to_numpy(float)
            closes = bars["close"].iloc[1 + h : 1 + h + eligible].to_numpy(float)
            ret = closes / opens - 1.0
            rows.append(
                {
                    "symbol": symbol,
                    "horizon": int(h),
                    "baseline_mean": float(np.mean(ret)),
                    "baseline_median": float(np.median(ret)),
                    "baseline_up_ratio": float(np.mean(ret > 0)),
                    "eligible": int(eligible),
                }
            )
    return pd.DataFrame(rows)


def build_excess_summary(events: pd.DataFrame, baseline: pd.DataFrame, horizons: list[int], *, key_col: str) -> pd.DataFrame:
    rows: list[dict] = []
    if events.empty:
        return pd.DataFrame()

    for name, g in events.groupby(key_col, dropna=False):
        for h in horizons:
            col = f"fwd_ret_h{h}"
            symbol_excess: list[float] = []
            pos = neg = zero = 0
            for symbol, sg in g.groupby("symbol"):
                b = baseline[(baseline["symbol"] == symbol) & (baseline["horizon"] == h)]
                if b.empty:
                    continue
                base_mean = float(b.iloc[0]["baseline_mean"])
                ex = float(sg[col].mean()) - base_mean
                symbol_excess.append(ex)
                if ex > 0:
                    pos += 1
                elif ex < 0:
                    neg += 1
                else:
                    zero += 1

            base_h = baseline[baseline["horizon"] == h]
            rows.append(
                {
                    key_col: name,
                    "horizon": int(h),
                    "events": int(len(g)),
                    "mean_ret": float(g[col].mean()),
                    "median_ret": float(g[col].median()),
                    "up_ratio": float((g[col] > 0).mean()),
                    "baseline_mean_avg": float(base_h["baseline_mean"].mean()) if not base_h.empty else np.nan,
                    "avg_excess_ret": float(np.mean(symbol_excess)) if symbol_excess else np.nan,
                    "pos_symbols_excess": int(pos),
                    "neg_symbols_excess": int(neg),
                    "zero_symbols_excess": int(zero),
                    "consistency": float(max(pos, neg) / max(1, pos + neg + zero)),
                }
            )

    out = pd.DataFrame(rows)
    if out.empty:
        return out
    if key_col == "event_type":
        out[key_col] = pd.Categorical(out[key_col], categories=EVENT_ORDER, ordered=True)
    if key_col == "event_family":
        out[key_col] = pd.Categorical(out[key_col], categories=FAMILY_ORDER, ordered=True)
    out = out.sort_values([key_col, "horizon"]).reset_index(drop=True)
    return out


def build_alpha_shortlist(event_excess_h24: pd.DataFrame, family_excess_h24: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []

    if not family_excess_h24.empty:
        fam = family_excess_h24.set_index("event_family")
        if "breakout_confirm_2" in fam.index:
            r = fam.loc["breakout_confirm_2"]
            rows.append(
                {
                    "candidate": "confirmed breakout family (2-bar confirm)",
                    "lens": "short / continuation",
                    "status": "keep",
                    "why": "24h 下绝对收益最差，且相对同周期无条件基线也更差。",
                    "events": int(r["events"]),
                    "h24_mean_ret": float(r["mean_ret"]),
                    "h24_avg_excess_ret": float(r["avg_excess_ret"]),
                    "symbol_consistency": f"{int(r['neg_symbols_excess'])}/4 negative-excess",
                }
            )
        if "rebound_confirm_1" in fam.index:
            r = fam.loc["rebound_confirm_1"]
            rows.append(
                {
                    "candidate": "rebound family (1-bar confirm)",
                    "lens": "relative long / mean reversion",
                    "status": "watch",
                    "why": "相对基线有正 excess，但绝对收益并不强，说明更像抗跌而不是强上涨。",
                    "events": int(r["events"]),
                    "h24_mean_ret": float(r["mean_ret"]),
                    "h24_avg_excess_ret": float(r["avg_excess_ret"]),
                    "symbol_consistency": f"{int(r['pos_symbols_excess'])}/4 positive-excess",
                }
            )

    if not event_excess_h24.empty:
        et = event_excess_h24.set_index("event_type")
        if "support_rebound_confirm_1" in et.index:
            r = et.loc["support_rebound_confirm_1"]
            rows.append(
                {
                    "candidate": "support rebound confirm_1",
                    "lens": "best long candidate so far",
                    "status": "watch",
                    "why": "当前更像多头观察候选：相对基线略强，但绝对收益还不够强，样本也不大。",
                    "events": int(r["events"]),
                    "h24_mean_ret": float(r["mean_ret"]),
                    "h24_avg_excess_ret": float(r["avg_excess_ret"]),
                    "symbol_consistency": f"{int(r['pos_symbols_excess'])}/4 positive-excess",
                }
            )
        if "support_breakout_confirm_2" in et.index:
            r = et.loc["support_breakout_confirm_2"]
            rows.append(
                {
                    "candidate": "support breakout confirm_2",
                    "lens": "short candidate",
                    "status": "keep",
                    "why": "24h 绝对收益和相对基线都显著偏负；和 breakout family 结论一致。",
                    "events": int(r["events"]),
                    "h24_mean_ret": float(r["mean_ret"]),
                    "h24_avg_excess_ret": float(r["avg_excess_ret"]),
                    "symbol_consistency": f"{int(r['neg_symbols_excess'])}/4 negative-excess",
                }
            )

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["status", "h24_avg_excess_ret"], ascending=[True, True]).reset_index(drop=True)
    return out


def build_side_comparison_h24(event_excess_h24: pd.DataFrame) -> pd.DataFrame:
    if event_excess_h24.empty:
        return pd.DataFrame()

    pairs = [
        ("breakout_raw", "support_breakout_raw", "resistance_breakout_raw"),
        ("breakout_confirm_1", "support_breakout_confirm_1", "resistance_breakout_confirm_1"),
        ("breakout_confirm_2", "support_breakout_confirm_2", "resistance_breakout_confirm_2"),
        ("rebound_confirm_1", "support_rebound_confirm_1", "resistance_rebound_confirm_1"),
        ("rebound_confirm_2", "support_rebound_confirm_2", "resistance_rebound_confirm_2"),
    ]

    idx = event_excess_h24.copy()
    idx["event_type"] = idx["event_type"].astype(str)
    idx = idx.set_index("event_type")

    rows: list[dict] = []
    for family, support_key, resistance_key in pairs:
        if support_key not in idx.index or resistance_key not in idx.index:
            continue
        s = idx.loc[support_key]
        r = idx.loc[resistance_key]
        gap = float(s["avg_excess_ret"] - r["avg_excess_ret"])
        if family.startswith("breakout"):
            reading = "数字上 support 更弱 / 更偏空；但 breakout side 审计还没 clean，先只按 family-level 看。"
            reliability = "breakout 数字差异: low_to_medium；不宜独立解读: high"
        elif gap > 0:
            reading = "当前是 support 略强，但差距还不够稳定到能宣布单边胜出。"
            reliability = "medium"
        elif gap < 0:
            reading = "当前是 resistance 略强，但这还不等于已经形成稳定单边优势。"
            reliability = "medium"
        else:
            reading = "当前两边几乎没差。"
            reliability = "low_to_medium"

        rows.append(
            {
                "family": family,
                "support_events": int(s["events"]),
                "resistance_events": int(r["events"]),
                "support_h24_avg_excess_ret": float(s["avg_excess_ret"]),
                "resistance_h24_avg_excess_ret": float(r["avg_excess_ret"]),
                "support_minus_resistance": gap,
                "reading": reading,
                "reliability": reliability,
            }
        )

    return pd.DataFrame(rows)


def build_breakout_mirror_summary(events: pd.DataFrame, *, sample_label: str) -> pd.DataFrame:
    if events.empty:
        return pd.DataFrame()

    pairs = [
        ("breakout_raw", "support_breakout_raw", "resistance_breakout_raw"),
        ("breakout_confirm_1", "support_breakout_confirm_1", "resistance_breakout_confirm_1"),
        ("breakout_confirm_2", "support_breakout_confirm_2", "resistance_breakout_confirm_2"),
    ]

    df = events.copy()
    df["event_type"] = df["event_type"].astype(str)
    rows: list[dict] = []

    for family, support_key, resistance_key in pairs:
        s = df[df["event_type"] == support_key][["symbol", "event_timestamp", "confirm_timestamp", "action_timestamp", "line_value_event"]].copy()
        r = df[df["event_type"] == resistance_key][["symbol", "event_timestamp", "confirm_timestamp", "action_timestamp", "line_value_event"]].copy()
        m = s.merge(
            r,
            on=["symbol", "event_timestamp", "confirm_timestamp", "action_timestamp"],
            suffixes=("_support", "_resistance"),
        )
        rows.append(
            {
                "sample": sample_label,
                "family": family,
                "exact_mirrored_pairs": int(len(m)),
                "support_above_resistance_share": float((m["line_value_event_support"] > m["line_value_event_resistance"]).mean()) if len(m) else np.nan,
            }
        )

    return pd.DataFrame(rows)


def build_reference_compare_tables(current_period: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    ref_art = ROOT / "reports" / "artifacts" / "pytrendline_event_validation_v3"
    if Path(ART).resolve() == ref_art.resolve():
        return pd.DataFrame(), pd.DataFrame()

    ref_event_path = ref_art / "event_excess_summary.csv"
    ref_family_path = ref_art / "family_excess_summary.csv"
    if not ref_event_path.exists() or not ref_family_path.exists():
        return pd.DataFrame(), pd.DataFrame()

    ref_event = pd.read_csv(ref_event_path)
    ref_family = pd.read_csv(ref_family_path)
    ref_event_h24 = ref_event[ref_event["horizon"] == 24].copy().set_index("event_type") if not ref_event.empty else pd.DataFrame()
    ref_family_h24 = ref_family[ref_family["horizon"] == 24].copy().set_index("event_family") if not ref_family.empty else pd.DataFrame()

    cur_event_path = Path(ART) / "event_excess_summary.csv"
    cur_family_path = Path(ART) / "family_excess_summary.csv"
    cur_event = pd.read_csv(cur_event_path)
    cur_family = pd.read_csv(cur_family_path)
    cur_event_h24 = cur_event[cur_event["horizon"] == 24].copy().set_index("event_type") if not cur_event.empty else pd.DataFrame()
    cur_family_h24 = cur_family[cur_family["horizon"] == 24].copy().set_index("event_family") if not cur_family.empty else pd.DataFrame()

    family_rows: list[dict] = []
    for family in ["breakout_raw", "breakout_confirm_1", "breakout_confirm_2", "rebound_confirm_1", "rebound_confirm_2", "touch_raw"]:
        if family not in ref_family_h24.index or family not in cur_family_h24.index:
            continue
        r = ref_family_h24.loc[family]
        c = cur_family_h24.loc[family]
        family_rows.append(
            {
                "family": family,
                "h24_excess_120d": float(r["avg_excess_ret"]),
                f"h24_excess_{current_period}": float(c["avg_excess_ret"]),
                "delta_long_minus_120d": float(c["avg_excess_ret"] - r["avg_excess_ret"]),
                "reading": "长样本里更弱" if abs(float(c["avg_excess_ret"])) < abs(float(r["avg_excess_ret"])) else "长样本里更强或方向翻转",
            }
        )

    event_rows: list[dict] = []
    for event_type in [
        "support_breakout_raw",
        "support_breakout_confirm_1",
        "support_breakout_confirm_2",
        "resistance_breakout_confirm_1",
        "resistance_breakout_confirm_2",
        "support_rebound_confirm_1",
        "resistance_rebound_confirm_2",
    ]:
        if event_type not in ref_event_h24.index or event_type not in cur_event_h24.index:
            continue
        r = ref_event_h24.loc[event_type]
        c = cur_event_h24.loc[event_type]
        if float(r["avg_excess_ret"]) > 0 and float(c["avg_excess_ret"]) <= 0:
            reading = "短样本里看着偏强，但长样本里消退/翻负"
        elif float(r["avg_excess_ret"]) <= 0 and float(c["avg_excess_ret"]) < 0 and abs(float(c["avg_excess_ret"])) < abs(float(r["avg_excess_ret"])):
            reading = "仍为负，但长样本里明显变弱"
        elif float(r["avg_excess_ret"]) <= 0 and float(c["avg_excess_ret"]) < 0:
            reading = "长样本里仍保持负向"
        elif float(c["avg_excess_ret"]) > 0:
            reading = "长样本里转成相对偏强/抗跌"
        else:
            reading = "方向不稳，样本期敏感"
        event_rows.append(
            {
                "event_type": event_type,
                "h24_excess_120d": float(r["avg_excess_ret"]),
                f"h24_excess_{current_period}": float(c["avg_excess_ret"]),
                "delta_long_minus_120d": float(c["avg_excess_ret"] - r["avg_excess_ret"]),
                "reading": reading,
            }
        )

    return pd.DataFrame(family_rows), pd.DataFrame(event_rows)


def chart_compare_mean(
    raw_sum: pd.DataFrame,
    purged_sum: pd.DataFrame,
    *,
    horizon: int,
    out_path: Path,
) -> None:
    r = raw_sum[raw_sum["horizon"] == horizon][["event_type", "mean_ret"]].rename(columns={"mean_ret": "raw_mean"})
    p = purged_sum[purged_sum["horizon"] == horizon][["event_type", "mean_ret"]].rename(columns={"mean_ret": "purged_mean"})
    d = r.merge(p, on="event_type", how="outer").fillna(0.0)
    if d.empty:
        return
    d["event_type"] = pd.Categorical(d["event_type"], categories=EVENT_ORDER, ordered=True)
    d = d.sort_values("event_type").reset_index(drop=True)

    x = np.arange(len(d))
    w = 0.38
    fig, ax = plt.subplots(figsize=(12, 5.6))
    ax.bar(x - w / 2, d["raw_mean"], width=w, color="#2563eb", label="raw")
    ax.bar(x + w / 2, d["purged_mean"], width=w, color="#f59e0b", label="purged")
    ax.axhline(0, color="#334155", linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(d["event_type"], rotation=35, ha="right", fontsize=9)
    ax.set_ylabel("mean return")
    ax.set_title(f"v3a mean return by event type (h={horizon})")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close(fig)


def chart_family_excess(family_excess: pd.DataFrame, *, horizon: int, out_path: Path) -> None:
    d = family_excess[family_excess["horizon"] == horizon].copy()
    if d.empty:
        return
    d["event_family"] = pd.Categorical(d["event_family"], categories=FAMILY_ORDER, ordered=True)
    d = d.sort_values("event_family").reset_index(drop=True)
    plt.figure(figsize=(10, 4.8))
    colors = ["#16a34a" if v > 0 else "#dc2626" for v in d["avg_excess_ret"]]
    plt.bar(d["event_family"].astype(str), d["avg_excess_ret"], color=colors)
    plt.axhline(0, color="#334155", linewidth=1)
    plt.xticks(rotation=30, ha="right")
    plt.ylabel("avg excess return vs symbol baseline")
    plt.title(f"Event family alpha lens (h={horizon})")
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close()


def build_report(
    *,
    symbols: list[str],
    period: str,
    interval: str,
    window_bars: int,
    snapshot_step_bars: int,
    horizons: list[int],
    confirm_bars: int,
    tol_mult: float,
    raw_events: pd.DataFrame,
    purged_events: pd.DataFrame,
    raw_summary: pd.DataFrame,
    purged_summary: pd.DataFrame,
    baseline_summary: pd.DataFrame,
    family_excess_summary: pd.DataFrame,
    event_excess_summary: pd.DataFrame,
    alpha_shortlist: pd.DataFrame,
) -> None:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    family_h24 = family_excess_summary[family_excess_summary["horizon"] == 24].copy()
    event_h24 = event_excess_summary[event_excess_summary["horizon"] == 24].copy()
    family_h24_idx = family_h24.set_index("event_family") if not family_h24.empty else pd.DataFrame()
    event_h24_idx = event_h24.set_index("event_type") if not event_h24.empty else pd.DataFrame()
    best_short = family_h24.sort_values("avg_excess_ret").iloc[0] if not family_h24.empty else None
    if not event_h24.empty and "support_rebound_confirm_1" in event_h24_idx.index:
        best_long = event_h24_idx.loc["support_rebound_confirm_1"]
        best_long_label = "support_rebound_confirm_1"
    elif not family_h24.empty and "rebound_confirm_1" in family_h24_idx.index:
        best_long = family_h24_idx.loc["rebound_confirm_1"]
        best_long_label = "rebound_confirm_1"
    else:
        best_long = family_h24.sort_values("avg_excess_ret", ascending=False).iloc[0] if not family_h24.empty else None
        best_long_label = str(best_long["event_family"]) if best_long is not None and "event_family" in best_long else "n/a"
    baseline_h24 = baseline_summary[baseline_summary["horizon"] == 24].copy()
    side_compare_h24 = build_side_comparison_h24(event_h24)
    breakout_mirror_summary = pd.concat(
        [
            build_breakout_mirror_summary(raw_events, sample_label="raw"),
            build_breakout_mirror_summary(purged_events, sample_label="purged"),
        ],
        ignore_index=True,
    )

    breakout_family_row = family_h24_idx.loc["breakout_confirm_2"] if not family_h24.empty and "breakout_confirm_2" in family_h24_idx.index else None
    support_rebound_row = event_h24_idx.loc["support_rebound_confirm_1"] if not event_h24.empty and "support_rebound_confirm_1" in event_h24_idx.index else None
    compare_family_h24, compare_event_h24 = build_reference_compare_tables(period)
    compare_event_idx = compare_event_h24.set_index("event_type") if not compare_event_h24.empty else pd.DataFrame()
    cmp_support_breakout_raw = compare_event_idx.loc["support_breakout_raw"] if not compare_event_h24.empty and "support_breakout_raw" in compare_event_idx.index else None
    cmp_support_breakout_c1 = compare_event_idx.loc["support_breakout_confirm_1"] if not compare_event_h24.empty and "support_breakout_confirm_1" in compare_event_idx.index else None
    cmp_resistance_breakout_c1 = compare_event_idx.loc["resistance_breakout_confirm_1"] if not compare_event_h24.empty and "resistance_breakout_confirm_1" in compare_event_idx.index else None
    cmp_support_rebound_c1 = compare_event_idx.loc["support_rebound_confirm_1"] if not compare_event_h24.empty and "support_rebound_confirm_1" in compare_event_idx.index else None

    def fmt_pct(x: float) -> str:
        return "n/a" if pd.isna(x) else f"{float(x):.2%}"

    def fmt_signed_pct(x: float) -> str:
        return "n/a" if pd.isna(x) else f"{float(x):+.2%}"

    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>PyTrendline Event Validation v3 (visible-line)</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #f8fafc; color: #0f172a; }}
    .wrap {{ max-width: 1220px; margin: 0 auto; padding: 28px 18px 48px; }}
    .card {{ background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 20px 22px; margin-bottom: 18px; }}
    .muted {{ color: #64748b; }}
    .warn {{ background: #fff7ed; border: 1px solid #fed7aa; color: #9a3412; border-radius: 10px; padding: 10px 12px; }}
    .pill {{ display: inline-block; margin-right: 8px; margin-top: 8px; padding: 5px 10px; border-radius: 999px; background: #eef2ff; color: #3730a3; font-size: 12px; }}
    .tbl {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    .tbl th, .tbl td {{ border: 1px solid #e2e8f0; padding: 8px 10px; text-align: left; vertical-align: top; }}
    .tbl th {{ background: #f8fafc; }}
    ul {{ line-height: 1.7; }}
    img.chart {{ width: 100%; max-width: 1000px; border: 1px solid #e2e8f0; border-radius: 12px; background: white; }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <p><a href=\"../../index.html\">← 返回站点首页</a></p>

    <div class=\"card\">
      <h1>PyTrendline Event Validation v3 (visible-line, v3a)</h1>
      <p class=\"muted\">核心目标：研究“当时已可见 line 上的事件”是否能预测未来收益，同时尽量避免未来函数。</p>
      <div>
        <span class=\"pill\">Generated: {escape(generated_at)}</span>
        <span class=\"pill\">symbols: {escape(', '.join(symbols))}</span>
        <span class=\"pill\">interval: {escape(interval)}</span>
        <span class=\"pill\">period: {escape(period)}</span>
        <span class=\"pill\">window_bars: {window_bars}</span>
        <span class=\"pill\">snapshot_step_bars: {snapshot_step_bars}</span>
        <span class=\"pill\">horizons: {escape(', '.join(map(str, horizons)))}</span>
        <span class=\"pill\">raw_events: {len(raw_events)}</span>
        <span class=\"pill\">purged_events: {len(purged_events)}</span>
      </div>
    </div>

    <div class=\"card\">
      <h2>v3 定义（极简）</h2>
      <ul>
        <li><b>先有可见线</b>：事件 bar 只能使用 t-1 时刻已经可见的 support / resistance 线。</li>
        <li><b>再有事件</b>：raw touch / raw breakout + confirm_1 / confirm_2（响应 1~2 根 K 线确认需求）。</li>
        <li><b>最后算收益</b>：从对应确认 bar 的下一根 open 开始，计算未来 h 小时收益。</li>
      </ul>
      <p class=\"warn\"><b>v3a 边界：</b>首版采用 stepwise visible snapshots（每 {snapshot_step_bars} 根 bar 重算一次可见线）以平衡计算量；后续可升级为更细粒度 as-of 引擎。</p>
    </div>

    <div class=\"card\">
      <h2>先说结论：哪些结果更像 alpha baseline？</h2>
      <ul>
        <li><b>当前最像的短线基线：</b>{escape(str(best_short['event_family'])) if best_short is not None else 'n/a'}。在 h=24 下，平均收益 {best_short['mean_ret']:.2%}，相对同周期资产无条件基线的平均 excess return 为 {best_short['avg_excess_ret']:.2%}，跨资产一致性 {int(best_short['consistency']*4)}/4。</li>
        <li><b>当前最像的多头观察候选：</b>{escape(best_long_label)}。它目前更像“相对更抗跌 / 更不差”，还不等于已经形成可以 headline 的强多头 alpha。</li>
        <li><b>判断口径：</b>不能只看事件后的绝对收益，因为这段样本期 24h 无条件基线本来就偏负；真正更像 alpha 的，是对基线的 excess。</li>
      </ul>
    </div>

    <div class=\"card\">
      <h2>这页怎么读（先看这个）</h2>
      <ul>
        <li><b>先看 Alpha candidate shortlist：</b>它相当于“候选名单”。不是已经毕业的 alpha，只是当前最值得继续审的对象。</li>
        <li><b>再看 Chart 2（family alpha lens）：</b>这张图最接近研究判断。<b>高于 0</b> 代表“比同周期随便挑时点更强”，<b>低于 0</b> 代表“比基线更弱”。</li>
        <li><b>Chart 1 用来防自欺：</b>如果 raw 和 purged 差很大，说明结果可能主要来自重叠事件堆积；如果两者方向接近，说明结论没那么依赖重复记账。</li>
        <li><b>最重要的防误读：</b>这页不是在证明“看到 trendline 就能直接交易”。它只是在审：哪些事件<b>可能</b>有信息量，哪些更像样本噪音。</li>
      </ul>
      <p class=\"warn\"><b>一句人话总结：</b>这轮 {escape(period)} 长样本里，breakout short 还没死，但已经比短样本看上去弱了很多；rebound long 也还没有站稳成可直接 headline 的多头 alpha。</p>
    </div>

    {f'''<div class=\"card\">\n      <h2>和 120d 比，这轮 {escape(period)} 说明了什么？</h2>\n      <p class=\"muted\">这个区块专门回答“长样本是在强化原来的判断，还是在拆穿短样本幻觉”。如果一个现象在 120d 很好看、到 {escape(period)} 却明显变弱或翻负，那通常更像样本期 lucky hit，而不是稳健 alpha。</p>\n      {render_table(compare_family_h24, limit=20)}\n      {render_table(compare_event_h24, limit=20)}\n      <ul>\n        <li><b>breakout family 还活着，但明显降温：</b><code>breakout_raw</code> 的 h24 excess 从 <b>{fmt_signed_pct(cmp_support_breakout_raw['h24_excess_120d']) if cmp_support_breakout_raw is not None else 'n/a'}</b>（这里只看 support_raw 事件层的代表行）到 <b>{fmt_signed_pct(cmp_support_breakout_raw[f'h24_excess_{period}']) if cmp_support_breakout_raw is not None else 'n/a'}</b>。翻成人话：负向方向还在，但强度没短样本看起来那么夸张。</li>\n        <li><b>当前更像 short 候选的是 support breakout confirm_1 / raw，而不是“所有 breakout 都很强”：</b><code>support_breakout_confirm_1</code> 在 {escape(period)} 里仍保持负 excess（<b>{fmt_signed_pct(cmp_support_breakout_c1[f'h24_excess_{period}']) if cmp_support_breakout_c1 is not None else 'n/a'}</b>），但也比 120d 更保守。</li>\n        <li><b>短样本里最漂亮的那种“resistance breakout confirm_1 偏强”基本没了：</b>它从 120d 的 <b>{fmt_signed_pct(cmp_resistance_breakout_c1['h24_excess_120d']) if cmp_resistance_breakout_c1 is not None else 'n/a'}</b> 收敛到 {escape(period)} 的 <b>{fmt_signed_pct(cmp_resistance_breakout_c1[f'h24_excess_{period}']) if cmp_resistance_breakout_c1 is not None else 'n/a'}</b>。这更像是在提醒我们：之前那种正向结果不够稳。</li>\n        <li><b>rebound long 还是没毕业：</b><code>support_rebound_confirm_1</code> 在 {escape(period)} 里仍没有转成干净正 excess（当前约 <b>{fmt_signed_pct(cmp_support_rebound_c1[f'h24_excess_{period}']) if cmp_support_rebound_c1 is not None else 'n/a'}</b>），所以更合理的身份还是 watchlist，而不是正式多头 alpha。</li>\n      </ul>\n    </div>''' if not compare_family_h24.empty or not compare_event_h24.empty else ''}

    <div class=\"card\">
      <h2>这轮市场基线是什么？</h2>
      <p class=\"muted\">如果完全不挑事件，只在同一时期随机拿 action time 看未来收益，市场本来是什么样。事件只有明显优于/劣于这个基线，才更像 alpha。</p>
      {render_table(baseline_h24, limit=20)}
    </div>

    <div class=\"card\">
      <h2>Alpha candidate shortlist（purged, h=24）</h2>
      <p class=\"muted\">这张表把绝对收益、相对基线 excess、跨资产一致性合在一起看，帮助判断哪些事件更值得进入 baseline 池。</p>
      {render_table(alpha_shortlist, limit=20)}
      <p class=\"warn\"><b>重要 caveat：</b>当前 breakout 的 support / resistance 两侧结果不能直接当成独立 alpha 结论。A 类审计已经说明：breakout side 的几何 / 归属还没完全 clean，所以更稳的解释仍应先落在 breakout family 层面。对应审计见：<a href=\"../pytrendline_event_validation_v3_breakout_side_audit/report.html\">breakout side audit</a>；对其中“100% inversion”指标的纠偏复核见：<a href=\"../pytrendline_event_validation_v3_breakout_metric_reaudit/report.html\">breakout metric re-audit</a>。</p>
    </div>

    <div class=\"card\">
      <h2>support / resistance 到底有没有区别？</h2>
      <p class=\"muted\">这张小结只读当前 v3 主页面的 {escape(period)} / {len(symbols)}-asset / h=24 artifacts，再结合 A 类审计，回答“现在能不能把两边当成不同信号”。</p>
      {render_table(side_compare_h24, limit=10)}
      <ul>
        <li><b>先说最重要的：</b>当前 <b>breakout 不能先按 side-level alpha 解读</b>。虽然数字上三档 breakout 都出现了 support / resistance 差异，甚至有的已经一正一负，但这更像是在提醒我们 side 标签还受几何 / 归属问题影响；高置信能说的是 <b>breakout family 值得继续看</b>，而不是“support breakout 和 resistance breakout 已经是两条干净独立的 alpha”。</li>
        <li><b>rebound 确实开始出现 side difference</b>，但还没收敛成单边赢家：在 <code>confirm_1</code>，support 相对基线略强；但到 <code>confirm_2</code>，反而是 resistance 略强。所以现在更诚实的说法是“rebound 对 side 有点敏感”，还不是“哪一边已经稳赢”。</li>
        <li><b>这页明确找到了什么：</b>breakout 的数值差异不是简单的“完全一样”；rebound 侧也确实出现了 support / resistance 分化。</li>
        <li><b>这页明确没找到什么：</b>还没找到足够干净的证据，支持把 breakout 的 support / resistance 当成独立结论；也还没找到一个在 rebound 的 <code>confirm_1</code> 和 <code>confirm_2</code> 都稳定胜出的单边。</li>
        <li><b>可靠度怎么读：</b>对“breakout 先别做 side-level 宣判”的判断是 <b>high</b>；对“rebound 已出现一些 side sensitivity”的判断是 <b>medium</b>；对“哪一边最终会赢”的判断当前仍只是 <b>low_to_medium</b>。</li>
      </ul>
    </div>

    <div class=\"card\">
      <h2>为什么同为 breakout，support / resistance 会看起来一样？</h2>
      <p class=\"muted\">最短答案：旧版采样器把“已经站到错误一侧的线”也继续当成 breakout 候选，而且 breakout 更像“当前处在突破状态”而不是“这一根 bar 才刚发生穿越”。这样一来，同一根 bar 就可能被同时记成 support breakout 和 resistance breakout。</p>
      {render_table(breakout_mirror_summary, limit=10)}
      <ul>
        <li><b>这不是 summary 打印 bug。</b> 问题发生在事件采样层：同一个 <code>symbol + event/confirm/action timestamps</code>，确实可能同时留下 support breakout 与 resistance breakout 两条记录。</li>
        <li><b>为什么会这样？</b> 如果 snapshot 时没有先检查“support 仍在价格下方 / resistance 仍在价格上方”，那一些其实已经被价格穿过的旧线，仍会被当成合法 side 继续向后监控。</li>
        <li><b>再叠加 breakout 判定过宽，</b> 只要当前 close 在线的一侧，就会被记成 breakout；这样它更像“状态标签”，而不是“从上一根到这一根真的发生了穿越事件”。</li>
        <li><b>本轮已经做的修复：</b>补了 snapshot 时的 side geometry / visibility gate，并把 breakout 改成“上一根还在正确一侧，这一根才真正穿越”。所以 mirrored pair 已从大批量重复，降到只剩极少数尾部个案。</li>
        <li><b>当前怎么解读？</b> 这说明 breakout family 还能继续研究，但 breakout 的 side-level 结论仍要谨慎：在 mirrored pair 没完全归零前，更稳的解释单位仍是 <b>family</b>，不是单边标签。</li>
      </ul>
    </div>

    <div class=\"card\">
      <h2>这次我们到底发现了什么 / 没发现什么？</h2>
      <p class=\"muted\">这是给读者的 plain-language 摘要：只基于当前 v3 主报告（{escape(period)}、{len(symbols)} 个资产、主观察窗 h=24）的结果，不把后续 OOS 扩展或更长样本的判断提前混进来。</p>
      <ul>
        <li><b>发现 1：</b><code>confirmed breakout family</code> 仍是当前最像的负向主候选。按当前主页口径，<code>breakout_confirm_2</code> 在 h=24 的 family-level 平均收益约 <b>{fmt_pct(breakout_family_row['mean_ret']) if breakout_family_row is not None else 'n/a'}</b>，相对同段基线的平均 excess 约 <b>{fmt_pct(breakout_family_row['avg_excess_ret']) if breakout_family_row is not None else 'n/a'}</b>。翻成人话：它更像“后面 24 小时继续走弱”的候选，而不是反转做多信号。<b>可靠度：medium</b>。</li>
        <li><b>发现 2：</b><code>support_rebound_confirm_1</code> 仍可先留在多头观察名单里，但级别只能算 <b>weak watch</b>。它的 h=24 相对基线 excess 约 <b>{fmt_pct(support_rebound_row['avg_excess_ret']) if support_rebound_row is not None else 'n/a'}</b>，绝对平均收益约 <b>{fmt_pct(support_rebound_row['mean_ret']) if support_rebound_row is not None else 'n/a'}</b>。翻成人话：这不是“已经找到 long alpha”，而是“在 rebound 线里暂时还没被完全排除”的候选。<b>可靠度：low_to_medium</b>。</li>
        <li><b>没发现 1：</b>我们还<b>没有</b>拿到足够干净的证据，证明 <code>support breakout</code> 和 <code>resistance breakout</code> 已经是两条可分开交易的独立 alpha。A 类审计仍提示：breakout 的 side 几何 / 归属问题需要继续严审，所以当前最稳的解读单位仍是 <b>family</b>，不是单边标签。<b>可靠度：high</b>。</li>
        <li><b>没发现 2：</b>我们也还<b>没有</b>找到一个“绝对收益明显为正、相对基线也稳定更强、并且在 rebound 确认层里持续胜出”的多头赢家。换句话说，当前有 long watchlist，但还没有 clean long verdict。<b>可靠度：medium</b>。</li>
      </ul>
    </div>

    <div class=\"card\">
      <h2>Chart 1 · mean return by event type (raw vs purged, h=24)</h2>
      <img class=\"chart\" src=\"event_mean_h24_raw_vs_purged.png\" alt=\"event mean chart\" />
      <p class=\"muted\">先看 raw 与 purged 的差别，确认结果不是仅靠重叠事件堆出来的。</p>
    </div>

    <div class=\"card\">
      <h2>Chart 2 · family alpha lens (h=24, excess vs baseline)</h2>
      <img class=\"chart\" src=\"family_excess_h24.png\" alt=\"family excess chart\" />
      <p class=\"muted\">这张图更接近 alpha 视角：正值代表“比无条件基线更强”，负值代表“比基线更弱”。</p>
    </div>

    <div class=\"card\">
      <h2>Family summary（purged, alpha lens）</h2>
      {render_table(family_excess_summary, limit=80)}
    </div>

    <div class=\"card\">
      <h2>Event-type summary（purged, alpha lens）</h2>
      {render_table(event_excess_summary, limit=120)}
    </div>

    <div class=\"card\">
      <h2>Raw summary (all horizons)</h2>
      {render_table(raw_summary, limit=200)}
    </div>

    <div class=\"card\">
      <h2>Purged summary (all horizons)</h2>
      {render_table(purged_summary, limit=200)}
    </div>

    <div class=\"card\">
      <h2>下一步优化建议</h2>
      <ul>
        <li><b>O1. 先把 breakout family 做细：</b>重点比较 raw / confirm_1 / confirm_2 在 24h 与 48h 的 trade-off，优先挑最像 short baseline 的版本。</li>
        <li><b>O2. 把 rebound 家族继续审计：</b>当前 support_rebound_confirm_1 看起来最像多头候选，但更像“抗跌”而不是“强上涨”，要继续扩样本看是否能站住。</li>
        <li><b>O3. 审计 side 归属镜像问题：</b>对同一 bar 同时触发 support / resistance breakout 的情况做更严格归属，避免把一类事件拆成两个镜像标签。</li>
        <li><b>O4. 下一轮扩大样本：</b>把 period 拉长、资产池扩展，并保留当前 baseline/excess 视角，不要再只看绝对收益均值。</li>
      </ul>
    </div>

    <div class=\"card\">
      <h2>如果目标是尽快给 v3 一个“可用 / 不可用”结论，最短还缺什么？</h2>
      <p class=\"muted\">这里不是把所有研究愿望都继续做下去，而是只挑最能帮助我们“尽快收工”的步骤。</p>
      <ol>
        <li><b>先做 180d core4 的 OOS honesty：</b>只盯 <code>support_breakout_raw</code> 和 <code>support_breakout_confirm_1</code>，主看 <code>h24</code>。目标不是再找更漂亮的数，而是确认它们在 validate / test 里是不是还稳定偏负。</li>
        <li><b>再做最小参数邻域检查：</b>不要一上来全网格爆搜，只检查候选附近 1 小圈参数（例如 confirm 与 tolerance 的相邻档），看方向是不是一碰就碎。如果一碰就碎，它更像样本噪音，不像可用 alpha。</li>
        <li><b>最后写 final verdict 页：</b>把 v3 的对象分成 <code>keep as alpha candidate</code>、<code>keep as feature/watch</code>、<code>park</code> 三类。到这一步就该给出是否收工，而不是无限加样本。</li>
      </ol>
      <p class=\"warn\"><b>当前最诚实的预判：</b>v3 现在最像的收工方向，不是“确认了一个强多头 alpha”，而是——<b>如果后续 OOS 还能站住，保留 breakout short 候选；如果 OOS 站不住，就把它降级成 feature/watch 或直接 park。</b></p>
    </div>

    <div class=\"card\">
      <h2>Artifacts</h2>
      <ul>
        <li><a href='../../artifacts/pytrendline_event_validation_v3/event_sample_raw.csv'>event_sample_raw.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v3/event_sample_purged.csv'>event_sample_purged.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v3/summary_raw.csv'>summary_raw.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v3/summary_purged.csv'>summary_purged.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v3/baseline_summary.csv'>baseline_summary.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v3/family_excess_summary.csv'>family_excess_summary.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v3/event_excess_summary.csv'>event_excess_summary.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v3/alpha_shortlist_h24.csv'>alpha_shortlist_h24.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v3/symbol_summary_h24_raw.csv'>symbol_summary_h24_raw.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v3/symbol_summary_h24_purged.csv'>symbol_summary_h24_purged.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v3/summary.json'>summary.json</a></li>
        <li><a href='../pytrendline_event_validation_v3_breakout_side_audit/report.html'>breakout side audit report</a></li>
        <li><a href='../pytrendline_event_validation_v3_breakout_metric_reaudit/report.html'>breakout metric re-audit report</a></li>
      </ul>
    </div>
  </div>
</body>
</html>
"""

    (SITE / "report.html").write_text(html, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build pytrendline event validation v3 (visible-line, v3a)")
    p.add_argument("--symbols", default=",".join(DEFAULT_SYMBOLS), help="comma-separated symbols")
    p.add_argument("--period", default=DEFAULT_PERIOD)
    p.add_argument("--interval", default=DEFAULT_INTERVAL)
    p.add_argument("--window-bars", type=int, default=DEFAULT_WINDOW_BARS)
    p.add_argument("--snapshot-step-bars", type=int, default=DEFAULT_SNAPSHOT_STEP_BARS)
    p.add_argument("--horizons", default=",".join(map(str, DEFAULT_HORIZONS)))
    p.add_argument("--confirm-bars", type=int, default=DEFAULT_CONFIRM_BARS)
    p.add_argument("--tol-mult", type=float, default=DEFAULT_TOL_MULT)
    p.add_argument("--purge-gap", type=int, default=max(DEFAULT_HORIZONS))
    p.add_argument("--artifact-dir", help="override artifact output directory")
    p.add_argument("--site-dir", help="override site output directory")
    p.add_argument("--cache-dir", help="override cache directory (defaults to <artifact-dir>/cache)")
    p.add_argument("--refresh-data", action="store_true", help="ignore cached bars and redownload")
    p.add_argument("--use-existing-artifacts", action="store_true", help="skip pytrendline recomputation and rebuild analysis/report from existing CSV artifacts")
    return p.parse_args()


def main() -> int:
    global ART, SITE, CACHE

    args = parse_args()
    symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
    horizons = sorted({int(x.strip()) for x in args.horizons.split(",") if x.strip()})

    if args.artifact_dir:
        ART = Path(args.artifact_dir).resolve()
    if args.site_dir:
        SITE = Path(args.site_dir).resolve()
    if args.cache_dir:
        CACHE = Path(args.cache_dir).resolve()
    else:
        CACHE = ART / "cache"

    ensure_dir(ART)
    ensure_dir(SITE)

    cfg = PyTrendlineConfig(
        window_bars=int(args.window_bars),
        min_points_required=3,
        ignore_breakouts=False,
        trend_type="BOTH",
        first_pt_must_be_pivot=False,
        last_pt_must_be_pivot=False,
        all_pts_must_be_pivots=True,
        trendline_must_include_global_maxmin_pt=False,
        time_interval="1h",
    )

    if args.use_existing_artifacts:
        events_raw = pd.read_csv(ART / "event_sample_raw.csv", parse_dates=["snapshot_asof_timestamp", "event_timestamp", "confirm_timestamp", "action_timestamp"])
        events_purged = pd.read_csv(ART / "event_sample_purged.csv", parse_dates=["snapshot_asof_timestamp", "event_timestamp", "confirm_timestamp", "action_timestamp"])
        symbol_meta_df = pd.read_csv(ART / "symbol_meta.csv", parse_dates=["start", "end"])
        if not symbol_meta_df.empty:
            symbols = symbol_meta_df["symbol"].astype(str).tolist()
        events_raw["event_type"] = pd.Categorical(events_raw["event_type"], categories=EVENT_ORDER, ordered=True)
        events_purged["event_type"] = pd.Categorical(events_purged["event_type"], categories=EVENT_ORDER, ordered=True)
        events_raw = add_event_family(events_raw)
        events_purged = add_event_family(events_purged)
        summary_raw = summarize(events_raw, horizons)
        summary_purged = summarize(events_purged, horizons)
        symbol_summary_h24_raw = summarize(events_raw, [24], key_col="symbol")
        symbol_summary_h24_purged = summarize(events_purged, [24], key_col="symbol")
    else:
        events_frames: list[pd.DataFrame] = []
        symbol_meta: list[dict] = []

        for symbol in symbols:
            bars = download_bars(symbol, args.period, args.interval, refresh=bool(args.refresh_data))
            symbol_meta.append(
                {
                    "symbol": symbol,
                    "rows": int(len(bars)),
                    "start": bars["timestamp"].iloc[0],
                    "end": bars["timestamp"].iloc[-1],
                }
            )
            print(f"downloaded symbol={symbol} rows={len(bars)}", flush=True)

            ev = collect_events_for_symbol(
                symbol=symbol,
                bars=bars,
                window_bars=int(args.window_bars),
                snapshot_step_bars=int(args.snapshot_step_bars),
                horizons=horizons,
                confirm_bars=int(args.confirm_bars),
                tol_mult=float(args.tol_mult),
                cfg=cfg,
            )
            print(f"events symbol={symbol} count={0 if ev.empty else len(ev)}", flush=True)
            if not ev.empty:
                events_frames.append(ev)

        events_raw = pd.concat(events_frames, ignore_index=True) if events_frames else pd.DataFrame()
        if events_raw.empty:
            raise SystemExit("No events produced for v3")

        events_raw["event_type"] = pd.Categorical(events_raw["event_type"], categories=EVENT_ORDER, ordered=True)
        events_raw = add_event_family(events_raw)
        events_raw = events_raw.sort_values(["symbol", "event_timestamp", "event_type"]).reset_index(drop=True)
        events_raw, mirrored_pair_raw_summary, mirrored_pair_raw_details, mirrored_pair_raw_dropped = resolve_exact_mirrored_breakout_pairs(events_raw)

        events_purged = purge_events(events_raw, purge_gap=int(args.purge_gap))
        events_purged = add_event_family(events_purged)
        events_purged, mirrored_pair_purged_summary, mirrored_pair_purged_details, mirrored_pair_purged_dropped = resolve_exact_mirrored_breakout_pairs(events_purged)

        summary_raw = summarize(events_raw, horizons)
        summary_purged = summarize(events_purged, horizons)

        symbol_summary_h24_raw = summarize(events_raw, [24], key_col="symbol")
        symbol_summary_h24_purged = summarize(events_purged, [24], key_col="symbol")

        symbol_meta_df = pd.DataFrame(symbol_meta)

        events_raw.to_csv(ART / "event_sample_raw.csv", index=False)
        events_purged.to_csv(ART / "event_sample_purged.csv", index=False)
        summary_raw.to_csv(ART / "summary_raw.csv", index=False)
        summary_purged.to_csv(ART / "summary_purged.csv", index=False)
        symbol_summary_h24_raw.to_csv(ART / "symbol_summary_h24_raw.csv", index=False)
        symbol_summary_h24_purged.to_csv(ART / "symbol_summary_h24_purged.csv", index=False)
        symbol_meta_df.to_csv(ART / "symbol_meta.csv", index=False)
        mirrored_pair_raw_summary.to_csv(ART / "mirrored_breakout_pair_resolution_raw_summary.csv", index=False)
        mirrored_pair_raw_details.to_csv(ART / "mirrored_breakout_pair_resolution_raw_details.csv", index=False)
        mirrored_pair_raw_dropped.to_csv(ART / "mirrored_breakout_pair_resolution_raw_dropped_rows.csv", index=False)
        mirrored_pair_purged_summary.to_csv(ART / "mirrored_breakout_pair_resolution_purged_summary.csv", index=False)
        mirrored_pair_purged_details.to_csv(ART / "mirrored_breakout_pair_resolution_purged_details.csv", index=False)
        mirrored_pair_purged_dropped.to_csv(ART / "mirrored_breakout_pair_resolution_purged_dropped_rows.csv", index=False)

    baseline_summary = build_baseline_summary(symbols, args.period, args.interval, horizons)
    family_excess_summary = build_excess_summary(events_purged, baseline_summary, horizons, key_col="event_family")
    event_excess_summary = build_excess_summary(events_purged, baseline_summary, horizons, key_col="event_type")
    alpha_shortlist = build_alpha_shortlist(
        event_excess_summary[event_excess_summary["horizon"] == 24].copy(),
        family_excess_summary[family_excess_summary["horizon"] == 24].copy(),
    )

    baseline_summary.to_csv(ART / "baseline_summary.csv", index=False)
    family_excess_summary.to_csv(ART / "family_excess_summary.csv", index=False)
    event_excess_summary.to_csv(ART / "event_excess_summary.csv", index=False)
    alpha_shortlist.to_csv(ART / "alpha_shortlist_h24.csv", index=False)

    chart_compare_mean(summary_raw, summary_purged, horizon=24, out_path=SITE / "event_mean_h24_raw_vs_purged.png")
    chart_family_excess(family_excess_summary, horizon=24, out_path=SITE / "family_excess_h24.png")

    min_events_for_top = 20 if len(events_purged) >= 200 else 5
    top_rows = event_excess_summary[(event_excess_summary["horizon"] == 24) & (event_excess_summary["events"] >= min_events_for_top)].copy()
    top_rows = top_rows.sort_values("avg_excess_ret", ascending=False)
    top_positive = top_rows.head(3)[["event_type", "events", "mean_ret", "avg_excess_ret", "consistency"]].to_dict("records")
    top_negative = top_rows.tail(3)[["event_type", "events", "mean_ret", "avg_excess_ret", "consistency"]].to_dict("records")

    summary_payload = {
        "symbols": symbols,
        "interval": args.interval,
        "period": args.period,
        "window_bars": int(args.window_bars),
        "snapshot_step_bars": int(args.snapshot_step_bars),
        "horizons": horizons,
        "confirm_bars": int(args.confirm_bars),
        "tol_mult": float(args.tol_mult),
        "events_raw": int(len(events_raw)),
        "events_purged": int(len(events_purged)),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "top_positive_h24_excess": top_positive,
        "top_negative_h24_excess": top_negative,
        "min_events_for_top": int(min_events_for_top),
        "notes": [
            "v3a uses stepwise visible snapshots; lines are recalculated every snapshot_step_bars.",
            "Events are only allowed after line visibility (as-of window end).",
            "Returns start from next-bar open after event confirmation.",
        ],
    }
    (ART / "summary.json").write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    build_report(
        symbols=symbols,
        period=args.period,
        interval=args.interval,
        window_bars=int(args.window_bars),
        snapshot_step_bars=int(args.snapshot_step_bars),
        horizons=horizons,
        confirm_bars=int(args.confirm_bars),
        tol_mult=float(args.tol_mult),
        raw_events=events_raw,
        purged_events=events_purged,
        raw_summary=summary_raw,
        purged_summary=summary_purged,
        baseline_summary=baseline_summary,
        family_excess_summary=family_excess_summary,
        event_excess_summary=event_excess_summary,
        alpha_shortlist=alpha_shortlist,
    )

    print(f"[ok] v3 report -> {SITE / 'report.html'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
