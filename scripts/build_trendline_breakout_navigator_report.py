#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.factors.pytrendline_bridge import PyTrendlineConfig, detect_pytrendlines  # noqa: E402
from momentum.signals.trendline_breakout_navigator import (  # noqa: E402
    TrendlineBreakoutNavigatorConfig,
    compute_trendline_breakout_navigator,
    extract_trendline_breakout_segments,
)

DEFAULT_TICKER = "BTC-USD"
DEFAULT_PERIOD = "10d"
DEFAULT_INTERVAL = "5m"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def flatten_yf_columns(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    return df


def download_bars(ticker: str, period: str, interval: str) -> pd.DataFrame:
    raw = yf.download(ticker, period=period, interval=interval, auto_adjust=False, progress=False)
    if raw is None or raw.empty:
        raise ValueError(f"No data for {ticker}")
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
    return bars[keep].dropna().sort_values("timestamp").reset_index(drop=True)


def render_table(df: pd.DataFrame, *, index: bool = False) -> str:
    if df.empty:
        return "<p><em>empty</em></p>"
    return df.to_html(index=index, classes="tbl", border=0, justify="left", escape=False)


def _line_y(line: pd.Series, x: np.ndarray) -> np.ndarray:
    return line["m"] * x + line["b"]


def _best_lines(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    out = df.copy()
    if "is_best_from_duplicate_group" in out.columns:
        out = out[out["is_best_from_duplicate_group"] == True]  # noqa: E712
    if "score" in out.columns:
        out = out.sort_values("score", ascending=False)
    return out.head(top_n).reset_index(drop=True)


def _slice_recent(df: pd.DataFrame, bars: int) -> pd.DataFrame:
    return df.tail(bars).copy() if len(df) > bars else df.copy()


def _find_best_active_window(df: pd.DataFrame, window: int) -> pd.DataFrame:
    line_mask = df[["tbn_long_line_value", "tbn_medium_line_value", "tbn_short_line_value"]].notna().any(axis=1)
    if int(line_mask.sum()) == 0:
        return _slice_recent(df, window)

    best_start = 0
    best_score = -1
    for start in range(0, max(len(df) - window + 1, 1), max(window // 8, 1)):
        end = min(start + window, len(df))
        score = int(line_mask.iloc[start:end].sum())
        if score > best_score:
            best_score = score
            best_start = start
    return df.iloc[best_start : best_start + window].copy()


def _draw_market_candles(ax, view: pd.DataFrame) -> None:
    ts = pd.to_datetime(view["timestamp"], utc=True)
    x = mdates.date2num(ts.dt.to_pydatetime())
    if len(x) > 1:
        width = float(np.median(np.diff(x))) * 0.72
    else:
        width = (5 / (24 * 60)) * 0.72
    min_body = max(float((view["high"] - view["low"]).median()) * 0.05, 1e-6)

    for xi, (_, row) in zip(x, view.iterrows()):
        o = float(row["open"])
        h = float(row["high"])
        l = float(row["low"])
        c = float(row["close"])
        if c >= o:
            wick_color = "#166534"
            fill_color = "#d1fae5"
            edge_color = "#166534"
        else:
            wick_color = "#991b1b"
            fill_color = "#fee2e2"
            edge_color = "#991b1b"
        ax.vlines(xi, l, h, color=wick_color, linewidth=0.8, alpha=0.95, zorder=2)
        body_low = min(o, c)
        body_h = max(abs(c - o), min_body)
        rect = plt.Rectangle((xi - width / 2, body_low), width, body_h, facecolor=fill_color, edgecolor=edge_color, linewidth=0.9, alpha=0.92, zorder=3)
        ax.add_patch(rect)

    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d\n%H:%M", tz=timezone.utc))


def _plot_timeframe_segmented_line(ax, full_df: pd.DataFrame, view: pd.DataFrame, segments: pd.DataFrame, *, prefix: str, color: str, label_base: str) -> None:
    view_start = int(view.index.min())
    view_end = int(view.index.max())
    segs = segments[segments["timeframe"] == prefix].copy()
    if segs.empty:
        return
    segs = segs[(segs["start_bar"] <= view_end) & (segs["end_bar"] >= view_start)].sort_values(["start_bar", "segment_id"])
    if segs.empty:
        return

    support_labeled = False
    resistance_labeled = False
    anchor_labeled = False
    pivot_labeled = False
    hh_labeled = False
    ll_labeled = False

    for _, seg in segs.iterrows():
        plot_start = max(int(seg["anchor_origin"]), view_start)
        plot_end = min(int(seg["end_bar"]), view_end)
        if plot_end < plot_start:
            continue
        idxs = np.arange(plot_start, plot_end + 1)
        ts = pd.to_datetime(full_df.loc[idxs, "timestamp"], utc=True)
        y = float(seg["anchor_price"]) + float(seg["slope"]) * (idxs - int(seg["anchor_origin"]))
        side = int(seg["side"])
        if side == 1:
            ax.plot(ts, y, color=color, linewidth=1.2, alpha=0.98, linestyle="-", zorder=4, label=f"{label_base} support" if not support_labeled else None)
            support_labeled = True
        elif side == -1:
            ax.plot(ts, y, color=color, linewidth=1.2, alpha=0.98, linestyle="--", zorder=4, label=f"{label_base} resistance" if not resistance_labeled else None)
            resistance_labeled = True

        anchor_idx = int(seg["anchor_origin"])
        if view_start <= anchor_idx <= view_end:
            anchor_ts = pd.to_datetime(full_df.loc[anchor_idx, "timestamp"], utc=True)
            anchor_y = float(seg["anchor_price"])
            ax.scatter([anchor_ts], [anchor_y], marker="s", facecolors="white", edgecolors=color, linewidths=1.4, s=34, zorder=5, label=f"{label_base} anchor" if not anchor_labeled else None)
            anchor_labeled = True

        pivot_idx = int(seg["pivot_origin"])
        if pivot_idx >= 0 and view_start <= pivot_idx <= view_end:
            pivot_ts = pd.to_datetime(full_df.loc[pivot_idx, "timestamp"], utc=True)
            pivot_y = float(seg["pivot_price"])
            ax.scatter([pivot_ts], [pivot_y], marker="D", facecolors=color, edgecolors="white", linewidths=0.8, s=34, zorder=5, label=f"{label_base} slope pivot" if not pivot_labeled else None)
            pivot_labeled = True

    hh_rows = view[view[f"{prefix}_hh"] == 1]
    if not hh_rows.empty:
        hh_plot = hh_rows[[f"{prefix}_pivot_high_origin", f"{prefix}_pivot_high_price"]].dropna().drop_duplicates()
        hh_x = []
        hh_y = []
        for _, row in hh_plot.iterrows():
            idx = int(row[f"{prefix}_pivot_high_origin"])
            if view_start <= idx <= view_end:
                hh_x.append(pd.to_datetime(full_df.loc[idx, "timestamp"], utc=True))
                hh_y.append(float(row[f"{prefix}_pivot_high_price"]))
        if hh_x:
            ax.scatter(hh_x, hh_y, marker="^", facecolors="white", edgecolors="#b45309", linewidths=1.2, s=38, zorder=6, label=f"{label_base} HH" if not hh_labeled else None)
            hh_labeled = True

    ll_rows = view[view[f"{prefix}_ll"] == 1]
    if not ll_rows.empty:
        ll_plot = ll_rows[[f"{prefix}_pivot_low_origin", f"{prefix}_pivot_low_price"]].dropna().drop_duplicates()
        ll_x = []
        ll_y = []
        for _, row in ll_plot.iterrows():
            idx = int(row[f"{prefix}_pivot_low_origin"])
            if view_start <= idx <= view_end:
                ll_x.append(pd.to_datetime(full_df.loc[idx, "timestamp"], utc=True))
                ll_y.append(float(row[f"{prefix}_pivot_low_price"]))
        if ll_x:
            ax.scatter(ll_x, ll_y, marker="v", facecolors="white", edgecolors="#7f1d1d", linewidths=1.2, s=38, zorder=6, label=f"{label_base} LL" if not ll_labeled else None)
            ll_labeled = True


def plot_our_navigator(df: pd.DataFrame, segments: pd.DataFrame, out_path: Path, *, title: str, mode: str = "recent", bars: int = 288) -> None:
    if mode == "best_active":
        view = _find_best_active_window(df, bars)
    else:
        view = _slice_recent(df, bars)
    ts = pd.to_datetime(view["timestamp"], utc=True)
    fig, ax = plt.subplots(figsize=(14.8, 7.4))
    _draw_market_candles(ax, view)

    for prefix, color, label in [
        ("tbn_long", "#7c3aed", "long"),
        ("tbn_medium", "#2563eb", "medium"),
        ("tbn_short", "#16a34a", "short"),
    ]:
        _plot_timeframe_segmented_line(ax, df, view, segments, prefix=prefix, color=color, label_base=label)

    wb = view[view["tbn_wick_bull"] == 1]
    wr = view[view["tbn_wick_bear"] == 1]
    bb = view[view["tbn_breakout_bull"] == 1]
    br = view[view["tbn_breakout_bear"] == 1]
    if not wb.empty:
        ax.scatter(pd.to_datetime(wb["timestamp"], utc=True), wb["close"], marker="o", facecolors="none", edgecolors="#14b8a6", s=42, label="wick bull / support rebound")
    if not wr.empty:
        ax.scatter(pd.to_datetime(wr["timestamp"], utc=True), wr["close"], marker="o", facecolors="none", edgecolors="#ef4444", s=42, label="wick bear / resistance rejection")
    if not bb.empty:
        ax.scatter(pd.to_datetime(bb["timestamp"], utc=True), bb["close"], marker="X", color="#16a34a", s=54, label="true breakout bull")
    if not br.empty:
        ax.scatter(pd.to_datetime(br["timestamp"], utc=True), br["close"], marker="X", color="#dc2626", s=54, label="true breakout bear")

    ax.set_title(title)
    ax.grid(alpha=0.2)
    ax.legend(loc="upper left", ncol=2)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_segment_replay(df: pd.DataFrame, seg: pd.Series, out_path: Path) -> None:
    anchor_idx = int(seg["anchor_origin"])
    start_idx = int(seg["start_bar"])
    end_idx = int(seg["end_bar"])
    pivot_idx = int(seg["pivot_origin"])
    window_start = max(0, min(anchor_idx, start_idx) - 12)
    window_end = min(len(df) - 1, end_idx + 12)
    view = df.iloc[window_start : window_end + 1].copy()

    fig, ax = plt.subplots(figsize=(12.8, 6.6))
    _draw_market_candles(ax, view)

    idxs = np.arange(anchor_idx, end_idx + 1)
    idxs = idxs[(idxs >= window_start) & (idxs <= window_end)]
    if len(idxs):
        ts = pd.to_datetime(df.loc[idxs, "timestamp"], utc=True)
        y = float(seg["anchor_price"]) + float(seg["slope"]) * (idxs - anchor_idx)
        linestyle = "-" if int(seg["side"]) == 1 else "--"
        color = "#2563eb" if int(seg["side"]) == 1 else "#7c3aed"
        ax.plot(ts, y, color=color, linewidth=2.0, linestyle=linestyle, zorder=4, label=f"segment #{int(seg['segment_id'])}")

    anchor_ts = pd.to_datetime(df.loc[anchor_idx, "timestamp"], utc=True)
    ax.scatter([anchor_ts], [float(seg["anchor_price"])], marker="s", facecolors="white", edgecolors="#111827", linewidths=1.3, s=46, zorder=6, label="anchor")

    if pivot_idx >= 0:
        pivot_ts = pd.to_datetime(df.loc[pivot_idx, "timestamp"], utc=True)
        ax.scatter([pivot_ts], [float(seg["pivot_price"])], marker="D", facecolors="#0ea5e9", edgecolors="white", linewidths=0.9, s=44, zorder=6, label="slope pivot")

    computed_ts = pd.to_datetime(df.loc[start_idx, "timestamp"], utc=True)
    ended_ts = pd.to_datetime(df.loc[end_idx, "timestamp"], utc=True)
    ax.axvline(computed_ts, color="#f59e0b", linewidth=1.1, linestyle=":", alpha=0.9, label="computed at")
    ax.axvline(ended_ts, color="#ef4444", linewidth=1.1, linestyle=":", alpha=0.9, label="segment end")

    ax.set_title(
        f"Replay | {seg['timeframe']} #{int(seg['segment_id'])} | {seg['side_label']} | end={seg['end_reason']}"
    )
    ax.grid(alpha=0.2)
    ax.legend(loc="upper left", ncol=2)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def build_segment_replay_items(df: pd.DataFrame, segments: pd.DataFrame, artifacts_dir: Path) -> pd.DataFrame:
    if segments.empty:
        return pd.DataFrame(
            columns=[
                "segment_id",
                "timeframe",
                "label",
                "image_rel",
                "side_label",
                "end_reason",
                "computed_timestamp",
                "end_timestamp",
                "anchor_timestamp",
                "pivot_timestamp",
                "anchor_price",
                "pivot_price",
                "bars_visible",
                "is_provisional",
            ]
        )
    replay_dir = ensure_dir(artifacts_dir / "segment_replays")
    items: list[dict[str, object]] = []
    ordered = segments.sort_values(["end_timestamp", "segment_id"]).reset_index(drop=True)
    for _, seg in ordered.iterrows():
        filename = f"{seg['timeframe']}_segment_{int(seg['segment_id']):03d}.png"
        plot_segment_replay(df, seg, replay_dir / filename)
        items.append(
            {
                "segment_id": int(seg["segment_id"]),
                "timeframe": str(seg["timeframe"]),
                "label": f"{seg['timeframe']} #{int(seg['segment_id'])} | {seg['side_label']} | end={seg['end_reason']}",
                "image_rel": f"segment_replays/{filename}",
                "side_label": str(seg["side_label"]),
                "end_reason": str(seg["end_reason"]),
                "computed_timestamp": str(seg["start_timestamp"]),
                "end_timestamp": str(seg["end_timestamp"]),
                "anchor_timestamp": str(seg["anchor_timestamp"]),
                "pivot_timestamp": str(seg.get("pivot_timestamp", "") or ""),
                "anchor_price": float(seg["anchor_price"]),
                "pivot_price": "" if pd.isna(seg["pivot_price"]) else float(seg["pivot_price"]),
                "bars_visible": int(seg["bars_visible"]),
                "is_provisional": int(seg["is_provisional"]),
            }
        )
    return pd.DataFrame(items)


def plot_pytrendline_compare(candles: pd.DataFrame, support: pd.DataFrame, resistance: pd.DataFrame, support_pivots: list[int], resistance_pivots: list[int], out_path: Path, *, title: str) -> None:
    ts = pd.to_datetime(candles["Date"], utc=True)
    x = np.arange(len(candles))
    fig, ax = plt.subplots(figsize=(14.8, 7.2))
    _draw_market_candles(
        ax,
        candles.rename(columns={"Date": "timestamp", "Open": "open", "High": "high", "Low": "low", "Close": "close"})[["timestamp", "open", "high", "low", "close"]],
    )
    if support_pivots:
        sp = candles.iloc[support_pivots]
        ax.scatter(pd.to_datetime(sp["Date"], utc=True), sp["Low"], color="#14b8a6", marker="v", s=34, label="support pivots")
    if resistance_pivots:
        rp = candles.iloc[resistance_pivots]
        ax.scatter(pd.to_datetime(rp["Date"], utc=True), rp["High"], color="#f59e0b", marker="^", s=34, label="resistance pivots")

    for _, row in _best_lines(support, top_n=3).iterrows():
        ax.plot(ts, _line_y(row, x), color="#2563eb", linewidth=1.2, linestyle="--" if bool(row.get("is_breakout", False)) else "-")
    for _, row in _best_lines(resistance, top_n=3).iterrows():
        ax.plot(ts, _line_y(row, x), color="#7c3aed", linewidth=1.2, linestyle="--" if bool(row.get("is_breakout", False)) else "-")

    ax.set_title(title)
    ax.grid(alpha=0.2)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def _draw_teaching_candles(ax, ohlc: pd.DataFrame) -> None:
    width = 0.55
    for _, row in ohlc.iterrows():
        x = row["x"]
        o = row["open"]
        h = row["high"]
        l = row["low"]
        c = row["close"]
        color = "#16a34a" if c >= o else "#dc2626"
        ax.vlines(x, l, h, color=color, linewidth=1.2, zorder=2)
        body_low = min(o, c)
        body_h = max(abs(c - o), 0.08)
        rect = plt.Rectangle((x - width / 2, body_low), width, body_h, facecolor=color, edgecolor=color, alpha=0.9, zorder=3)
        ax.add_patch(rect)


def plot_teaching_structure_labels(out_path: Path) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(11, 8.5), sharex=False)

    bull = pd.DataFrame(
        {
            "x": np.arange(8),
            "open":  [100.0, 99.2, 99.6, 100.8, 101.2, 100.6, 101.5, 102.5],
            "high":  [100.6, 99.8, 101.7, 101.4, 103.0, 101.3, 104.2, 103.9],
            "low":   [99.4, 98.4, 99.1, 100.1, 100.8, 100.2, 101.0, 101.9],
            "close": [99.5, 98.8, 101.2, 101.1, 102.6, 100.9, 103.8, 102.9],
        }
    )
    ax = axes[0]
    _draw_teaching_candles(ax, bull)
    p_low1 = (1, float(bull.loc[1, "low"]))
    p_high1 = (4, float(bull.loc[4, "high"]))
    p_low2 = (5, float(bull.loc[5, "low"]))
    p_high2 = (6, float(bull.loc[6, "high"]))
    ax.scatter([p_high1[0], p_high2[0]], [p_high1[1], p_high2[1]], marker="^", color="#f59e0b", s=70)
    ax.scatter([p_low1[0], p_low2[0]], [p_low1[1], p_low2[1]], marker="v", color="#14b8a6", s=70)
    ax.annotate("high #1", xy=p_high1, xytext=(p_high1[0]-0.9, p_high1[1]+1.5), arrowprops=dict(arrowstyle='->', color='#f59e0b'), color='#b45309')
    ax.annotate("HH = higher high", xy=p_high2, xytext=(p_high2[0]-0.2, p_high2[1]+1.8), arrowprops=dict(arrowstyle='->', color='#f59e0b'), color='#b45309')
    ax.annotate("low #1", xy=p_low1, xytext=(p_low1[0]-0.8, p_low1[1]-2.0), arrowprops=dict(arrowstyle='->', color='#14b8a6'), color='#0f766e')
    ax.annotate("HL = higher low", xy=p_low2, xytext=(p_low2[0]-0.4, p_low2[1]-2.2), arrowprops=dict(arrowstyle='->', color='#14b8a6'), color='#0f766e')
    ax.set_title("Teaching Diagram 0A: Uptrend labels = HL + HH")
    ax.grid(alpha=0.2)
    ax.set_xticks(bull["x"])

    bear = pd.DataFrame(
        {
            "x": np.arange(8),
            "open":  [104.8, 104.2, 103.9, 103.6, 103.0, 103.4, 102.8, 102.1],
            "high":  [105.2, 104.6, 104.4, 103.9, 103.4, 103.8, 103.0, 102.4],
            "low":   [104.1, 103.6, 103.2, 102.8, 102.0, 102.5, 101.1, 100.8],
            "close": [104.3, 103.8, 103.5, 103.0, 102.4, 102.9, 101.4, 101.0],
        }
    )
    ax = axes[1]
    _draw_teaching_candles(ax, bear)
    p_high1 = (1, float(bear.loc[1, "high"]))
    p_low1 = (4, float(bear.loc[4, "low"]))
    p_high2 = (5, float(bear.loc[5, "high"]))
    p_low2 = (7, float(bear.loc[7, "low"]))
    ax.scatter([p_high1[0], p_high2[0]], [p_high1[1], p_high2[1]], marker="^", color="#f59e0b", s=70)
    ax.scatter([p_low1[0], p_low2[0]], [p_low1[1], p_low2[1]], marker="v", color="#14b8a6", s=70)
    ax.annotate("high #1", xy=p_high1, xytext=(p_high1[0]-0.8, p_high1[1]+1.3), arrowprops=dict(arrowstyle='->', color='#f59e0b'), color='#b45309')
    ax.annotate("LH = lower high", xy=p_high2, xytext=(p_high2[0]-0.3, p_high2[1]+1.5), arrowprops=dict(arrowstyle='->', color='#f59e0b'), color='#b45309')
    ax.annotate("low #1", xy=p_low1, xytext=(p_low1[0]-0.7, p_low1[1]-1.9), arrowprops=dict(arrowstyle='->', color='#14b8a6'), color='#0f766e')
    ax.annotate("LL = lower low", xy=p_low2, xytext=(p_low2[0]-0.2, p_low2[1]-2.0), arrowprops=dict(arrowstyle='->', color='#14b8a6'), color='#0f766e')
    ax.set_title("Teaching Diagram 0B: Downtrend labels = LH + LL")
    ax.grid(alpha=0.2)
    ax.set_xticks(bear["x"])

    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_teaching_hh_ll_active_line(out_path: Path) -> None:
    ohlc = pd.DataFrame(
        {
            "x": np.arange(10),
            "open":  [100.0, 99.2, 99.0, 100.6, 101.8, 101.2, 101.6, 103.8, 104.8, 106.0],
            "high":  [100.8, 99.5, 101.8, 101.4, 104.4, 101.9, 104.8, 104.2, 107.4, 106.8],
            "low":   [99.4, 97.6, 98.8, 99.8, 101.4, 99.8, 101.2, 102.0, 104.0, 105.2],
            "close": [99.6, 98.3, 101.2, 101.0, 103.6, 100.3, 104.2, 102.5, 106.9, 105.9],
        }
    )
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    _draw_teaching_candles(ax, ohlc)

    high1 = (4, float(ohlc.loc[4, "high"]))
    low2 = (5, float(ohlc.loc[5, "low"]))
    high2 = (8, float(ohlc.loc[8, "high"]))

    ax.scatter([high1[0], high2[0]], [high1[1], high2[1]], marker="^", color="#f59e0b", s=75, label="confirmed highs")
    ax.scatter([low2[0]], [low2[1]], marker="v", color="#14b8a6", s=75, label="anchor low")
    ax.annotate("old high", xy=high1, xytext=(high1[0]-1.0, high1[1]+1.7), arrowprops=dict(arrowstyle='->', color='#f59e0b'), color='#b45309')
    ax.annotate("new HH", xy=high2, xytext=(high2[0]-0.5, high2[1]+1.7), arrowprops=dict(arrowstyle='->', color='#f59e0b'), color='#b45309')
    ax.annotate("prior swing low", xy=low2, xytext=(low2[0]-1.7, low2[1]-2.4), arrowprops=dict(arrowstyle='->', color='#14b8a6'), color='#0f766e')

    horiz_x = np.arange(low2[0], high2[0] + 1)
    horiz_y = np.full_like(horiz_x, low2[1], dtype=float)
    ax.plot(horiz_x, horiz_y, color="#2563eb", linewidth=2.0, label="provisional support line")
    ax.text(5.3, low2[1] + 1.0, "HH confirmed -> start horizontal\nprovisional support line", color="#2563eb")

    low3 = (9, float(ohlc.loc[9, "low"]))
    ax.scatter([low3[0]], [low3[1]], marker="v", color="#0ea5e9", s=75, label="next pivot low")
    ax.annotate("next pivot low", xy=low3, xytext=(low3[0]-1.8, low3[1]-2.2), arrowprops=dict(arrowstyle='->', color='#0ea5e9'), color='#0369a1')

    slope = (low3[1] - low2[1]) / max(low3[0] - low2[0], 1)
    line_x = np.arange(low2[0], 10)
    line_y = low2[1] + slope * (line_x - low2[0])
    ax.plot(line_x, line_y, color="#1d4ed8", linewidth=2.2, linestyle="--", label="final support line (low→low)")
    ax.text(7.2, line_y[2] + 0.9, "next pivot low arrives ->\nline becomes low→low", color="#1d4ed8")

    ax.set_xticks(ohlc["x"])
    ax.set_title("Teaching Diagram A: HH starts horizontal line, later pivot low sets slope")
    ax.grid(alpha=0.2)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_teaching_hh_ll_vs_channel_logic(out_path: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(16.0, 4.8), constrained_layout=True)

    ax = axes[0]
    x = np.arange(10)
    price = np.array([99, 96, 99, 102, 100, 103, 106, 104, 101, 108], dtype=float)
    ax.plot(x, price, color="#111827", linewidth=1.8)
    ax.scatter([1, 3, 6, 8], [96, 102, 106, 101], color=["#2563eb", "#ef4444", "#ef4444", "#2563eb"], s=45, zorder=5)
    ax.annotate("prev swing low", (1, 96), xytext=(0.2, 94.3), arrowprops=dict(arrowstyle='->', color='#2563eb'), color='#2563eb', fontsize=9)
    ax.annotate("H1", (3, 102), xytext=(2.7, 103.7), color='#b91c1c', fontsize=9)
    ax.annotate("HH", (6, 106), xytext=(5.8, 107.6), color='#b91c1c', fontsize=9)
    ax.hlines(96, 6, 8.1, colors='#60a5fa', linestyles='--', linewidth=2, label='provisional support')
    ax.plot([1, 8], [96, 101], color='#2563eb', linewidth=2.4, label='bullish support line')
    ax.annotate('after HH, model tracks\nwhere bullish structure should hold', (6.6, 97.5), xytext=(4.4, 92.8), arrowprops=dict(arrowstyle='->', color='#2563eb'), color='#1d4ed8', fontsize=9)
    ax.set_title('A. HH -> bullish support line')
    ax.set_xlabel('bars')
    ax.set_ylabel('price')
    ax.grid(alpha=0.2)
    ax.legend(loc='lower right', fontsize=8)

    ax = axes[1]
    x = np.arange(10)
    price = np.array([101, 104, 101, 98, 100, 97, 94, 96, 99, 92], dtype=float)
    ax.plot(x, price, color='#111827', linewidth=1.8)
    ax.scatter([1, 3, 6, 8], [104, 98, 94, 99], color=['#7c3aed', '#16a34a', '#16a34a', '#7c3aed'], s=45, zorder=5)
    ax.annotate('prev swing high', (1, 104), xytext=(0.0, 106.0), arrowprops=dict(arrowstyle='->', color='#7c3aed'), color='#7c3aed', fontsize=9)
    ax.annotate('L1', (3, 98), xytext=(2.7, 96.4), color='#166534', fontsize=9)
    ax.annotate('LL', (6, 94), xytext=(5.8, 92.2), color='#166534', fontsize=9)
    ax.hlines(104, 6, 8.1, colors='#c4b5fd', linestyles='--', linewidth=2, label='provisional resistance')
    ax.plot([1, 8], [104, 99], color='#7c3aed', linewidth=2.4, label='bearish resistance line')
    ax.annotate('after LL, model tracks\nwhere bearish structure should fail', (6.4, 102.0), xytext=(4.2, 107.8), arrowprops=dict(arrowstyle='->', color='#7c3aed'), color='#6d28d9', fontsize=9)
    ax.set_title('B. LL -> bearish resistance line')
    ax.set_xlabel('bars')
    ax.grid(alpha=0.2)
    ax.legend(loc='lower left', fontsize=8)

    ax = axes[2]
    x = np.arange(12)
    price = np.array([100, 102, 101, 103, 102, 104, 103, 105, 104, 106, 105, 103.5], dtype=float)
    upper = 103 + 0.25 * x
    lower = 98 + 0.25 * x
    ax.plot(x, price, color='#111827', linewidth=1.8, label='price')
    ax.plot(x, upper, color='#ef4444', linewidth=2, label='upper boundary')
    ax.plot(x, lower, color='#2563eb', linewidth=2, label='lower boundary')
    ax.fill_between(x, lower, upper, color='#e0f2fe', alpha=0.35)
    ax.annotate('channel logic:\nupper + lower exist together', (5.5, 101.2), xytext=(1.0, 96.5), arrowprops=dict(arrowstyle='->', color='#0f766e'), color='#0f766e', fontsize=9)
    ax.annotate('fake breakout example:\npierce upper line then fall back inside', (9, upper[9]), xytext=(6.8, 108.0), arrowprops=dict(arrowstyle='->', color='#b91c1c'), color='#b91c1c', fontsize=9)
    ax.set_title('C. channel hypothesis')
    ax.set_xlabel('bars')
    ax.grid(alpha=0.2)
    ax.legend(loc='lower right', fontsize=8)

    fig.suptitle('Trendline Navigator vs Channel Assumption', fontsize=14, y=1.03)
    fig.savefig(out_path, dpi=160, bbox_inches='tight')
    plt.close(fig)


def plot_teaching_support_rebound_and_breakdown(out_path: Path) -> None:
    ohlc = pd.DataFrame(
        {
            "x": np.arange(12),
            "open":  [100.4, 100.8, 101.0, 101.3, 101.7, 101.8, 101.9, 102.1, 102.4, 101.8, 101.2, 100.0],
            "high":  [100.9, 101.1, 101.5, 101.8, 102.0, 102.0, 102.3, 102.6, 102.8, 102.1, 101.4, 100.2],
            "low":   [100.1, 100.6, 100.8, 101.0, 101.5, 100.0, 101.7, 101.9, 102.2, 100.9, 99.6, 99.3],
            "close": [100.7, 101.0, 101.3, 101.6, 101.9, 101.2, 102.2, 102.4, 102.6, 101.2, 100.2, 99.6],
        }
    )
    x = ohlc["x"].to_numpy()
    support = 100.2 + 0.18 * x

    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    _draw_teaching_candles(ax, ohlc)
    ax.plot(x, support, color="#2563eb", linewidth=2.0, label="active support line")

    rebound_bar = 5
    breakdown_bar = 10
    ax.scatter([rebound_bar], [ohlc.loc[rebound_bar, "close"]], marker="o", facecolors="none", edgecolors="#14b8a6", s=95, label="wick_bull / rebound")
    ax.annotate("wick_bull / rebound\nlow pierces line, close recovers", xy=(rebound_bar, ohlc.loc[rebound_bar, "close"]), xytext=(rebound_bar-2.6, ohlc.loc[rebound_bar, "close"]-2.1), arrowprops=dict(arrowstyle='->', color='#14b8a6'), color='#0f766e')

    ax.scatter([breakdown_bar], [ohlc.loc[breakdown_bar, "close"]], marker="X", color="#dc2626", s=95, label="true breakout bear")
    ax.annotate("true breakout bear\nclose breaks below support", xy=(breakdown_bar, ohlc.loc[breakdown_bar, "close"]), xytext=(breakdown_bar-2.4, ohlc.loc[breakdown_bar, "close"]-2.4), arrowprops=dict(arrowstyle='->', color='#dc2626'), color='#b91c1c')

    ax.set_xticks(ohlc["x"])
    ax.set_title("Teaching Diagram B: support rebound vs true bearish breakout")
    ax.grid(alpha=0.2)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_teaching_resistance_rejection_and_breakout(out_path: Path) -> None:
    ohlc = pd.DataFrame(
        {
            "x": np.arange(12),
            "open":  [105.2, 104.8, 104.5, 104.0, 103.8, 103.2, 102.9, 102.7, 102.4, 102.8, 103.6, 104.8],
            "high":  [105.6, 105.0, 104.8, 104.3, 104.1, 104.6, 103.2, 103.0, 102.8, 104.8, 105.6, 106.2],
            "low":   [104.8, 104.2, 104.0, 103.7, 103.2, 102.9, 102.5, 102.2, 102.0, 102.5, 103.2, 104.4],
            "close": [105.0, 104.5, 104.2, 103.9, 103.5, 103.1, 102.7, 102.4, 102.2, 103.0, 105.0, 105.8],
        }
    )
    x = ohlc["x"].to_numpy()
    resistance = 105.0 - 0.16 * x

    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    _draw_teaching_candles(ax, ohlc)
    ax.plot(x, resistance, color="#7c3aed", linewidth=2.0, label="active resistance line")

    rejection_bar = 5
    breakout_bar = 10
    ax.scatter([rejection_bar], [ohlc.loc[rejection_bar, "close"]], marker="o", facecolors="none", edgecolors="#ef4444", s=95, label="wick_bear / rejection")
    ax.annotate("wick_bear / rejection\nhigh pierces line, close falls back", xy=(rejection_bar, ohlc.loc[rejection_bar, "close"]), xytext=(rejection_bar-2.8, ohlc.loc[rejection_bar, "close"]+1.4), arrowprops=dict(arrowstyle='->', color='#ef4444'), color='#b91c1c')

    ax.scatter([breakout_bar], [ohlc.loc[breakout_bar, "close"]], marker="X", color="#16a34a", s=95, label="true breakout bull")
    ax.annotate("true breakout bull\nclose breaks above resistance", xy=(breakout_bar, ohlc.loc[breakout_bar, "close"]), xytext=(breakout_bar-2.7, ohlc.loc[breakout_bar, "close"]+1.2), arrowprops=dict(arrowstyle='->', color='#16a34a'), color='#166534')

    ax.set_xticks(ohlc["x"])
    ax.set_title("Teaching Diagram C: resistance rejection vs true bullish breakout")
    ax.grid(alpha=0.2)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def build_html(*, ticker: str, period: str, interval: str, nav_cfg: TrendlineBreakoutNavigatorConfig, py_cfg: PyTrendlineConfig, nav_stats: pd.DataFrame, support: pd.DataFrame, resistance: pd.DataFrame, artifacts_rel: str, window_notes: pd.DataFrame, recent_segments: pd.DataFrame, replay_items: pd.DataFrame) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    py_support = _best_lines(support, top_n=10)
    py_resistance = _best_lines(resistance, top_n=10)
    if not py_support.empty:
        py_support = py_support[[c for c in ["id", "is_breakout", "num_points", "m", "b", "score", "starts_at_date", "ends_at_date"] if c in py_support.columns]]
    if not py_resistance.empty:
        py_resistance = py_resistance[[c for c in ["id", "is_breakout", "num_points", "m", "b", "score", "starts_at_date", "ends_at_date"] if c in py_resistance.columns]]

    decisions = pd.DataFrame(
        [
            ["为什么不直接搬外部 breakout 代码", "因为来源语义不干净；这次改成学习逻辑后 clean reimplementation。"],
            ["这次正式入库的是什么", "`trendline_breakout_navigator.py` —— 我们自己的状态机实现。"],
            ["和 pytrendline 的关系", "同页对照：前者偏逐 bar 趋势状态，后者偏趋势线搜索/scoring。"],
        ],
        columns=["question", "answer"],
    )

    legend = pd.DataFrame(
        [
            ["support line（实线）", "bullish active line，按当前仓库逻辑分开绘制；不会再和 resistance 硬连成一条折线。"],
            ["resistance line（虚线）", "bearish active line，和 support 分开画，趋势切换处自然断线。"],
            ["anchor（方块）", "当前这条线的起点，也就是 anchor pivot。"],
            ["slope pivot（菱形）", "当前这条线真正用于定斜率的第二个 pivot；如果还没出现，说明这条线仍是 provisional。"],
            ["wick_bull", "支撑线被下探但收盘守住，等价于 bullish rebound / false break down。"],
            ["wick_bear", "压力线被上刺但收盘压回，等价于 bearish rejection / false break up。"],
            ["breakout_bear", "收盘真正跌破 active support line，记作真 bearish breakout。"],
            ["breakout_bull", "收盘真正站上 active resistance line，记作真 bullish breakout。"],
        ],
        columns=["label", "meaning"],
    )

    reading_steps = pd.DataFrame(
        [
            ["1", "先看 HH / LL 标记：它们是趋势切换的触发点。"],
            ["2", "看到 HH 后，会先从前一个 swing low 启动一条水平 provisional support line；看到 LL 后，会先从前一个 swing high 启动水平 provisional resistance line。"],
            ["3", "只有后续同侧 pivot 出现后，active line 才会从水平线更新成真正的 low→low / high→high 斜线。"],
            ["4", "现在 support 和 resistance 会分开画：support 用实线，resistance 用虚线，趋势切换处断线，不再强行相连。"],
            ["5", "方块是 anchor 点，菱形是当前 slope pivot，所以你能直接看到这条线到底连的是哪两个点。"],
            ["6", "如果是 wick_bull / wick_bear，表示线被测试但收盘仍守在正确一侧，更像反弹 / rejection。"],
            ["7", "如果是 breakout_bear / breakout_bull，表示收盘真正穿过 active line，这才算真突破。"],
            ["8", "现在每条线也会以 segment state 存档：可以看到它的 start/end、end_reason，以及它是 provisional 还是 final。"],
            ["9", "你还可以在 Segment Replay 里点选某一段，查看它何时被计算出来、何时结束、以及它使用了哪些点。"],
            ["10", "最后看 `tbn_composite_trend` / `tbn_signal`，它们是 long/medium/short 三层结果的合成。"],
        ],
        columns=["step", "how_to_read"],
    )

    support_lifecycle = pd.DataFrame(
        [
            ["第 0 步：还没 HH", "还没有 bullish 结构被确认", "不要把未来可能的上升线画出来"],
            ["第 1 步：HH 刚确认", "先从前一个 swing low 启动水平 provisional support line", "这不是最终斜率，只是先声明：若结构转强，最该守住的是这个低点"],
            ["第 2 步：价格继续运行", "active line 暂时保持水平", "此时它更像‘结构失效线’，不是成熟通道下轨"],
            ["第 3 步：后续 pivot low 确认", "用 anchor low + 新 pivot low 计算 slope，线更新为 low→low 斜线", "到这一步才真正有了‘动态支撑线’"],
            ["第 4 步：后续交易", "看价格是守住这条线、下探收回，还是收盘真跌破", "分别对应 rebound / breakdown 两类含义"],
        ],
        columns=["阶段", "active line 怎么定义", "你应该怎么理解"],
    )

    trading_mapping = pd.DataFrame(
        [
            ["close 仍在线上方", "bullish 结构仍存活", "继续观察，不等于立刻追多"],
            ["low 跌破但 close 收回线之上", "更像测试支撑 / wick_bull / false break down", "可作为‘结构仍在’的证据，但最好叠加别的确认"],
            ["close 真跌破 support", "bullish 结构失效", "更像退出多头 / 禁止新多，而不是单独作为主入场"],
            ["后续再形成新 HH + 新 HL", "结构重新转强", "才考虑新一轮顺势入场"],
        ],
        columns=["盘面现象", "业务解释", "交易含义（更稳妥的理解）"],
    )

    difference_vs_channel = pd.DataFrame(
        [
            ["navigator active line", "单边结构失效线", "HH 后优先盯支撑；LL 后优先盯压力"],
            ["channel assumption", "双边边界区间", "上轨/下轨同时存在，真假突破相对于整个通道定义"],
        ],
        columns=["框架", "核心对象", "你在图上真正看的是什么"],
    )

    replay_payload = []
    if not replay_items.empty:
        replay_payload = replay_items.to_dict(orient="records")
    replay_json = json.dumps(replay_payload, ensure_ascii=False)

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Trendline Breakout Navigator Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; max-width: 1080px; margin: 40px auto; padding: 0 18px; line-height: 1.65; color: #111; }}
    h1, h2, h3 {{ line-height: 1.25; }}
    .muted {{ color: #666; }}
    .card {{ border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px 18px; margin: 16px 0; }}
    .tbl {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
    .tbl th, .tbl td {{ border-bottom: 1px solid #e5e7eb; padding: 8px 10px; text-align: left; vertical-align: top; }}
    img {{ max-width: 100%; border: 1px solid #e5e7eb; border-radius: 10px; }}
    a {{ color: #2563eb; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .replay-grid {{ display: grid; grid-template-columns: 320px 1fr; gap: 16px; align-items: start; }}
    .replay-meta {{ background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 10px; padding: 12px; font-size: 14px; }}
    .replay-meta dl {{ margin: 0; }}
    .replay-meta dt {{ font-weight: 600; margin-top: 8px; }}
    .replay-meta dd {{ margin: 2px 0 0 0; color: #374151; }}
    select {{ width: 100%; padding: 8px 10px; border-radius: 8px; border: 1px solid #d1d5db; background: white; }}
    @media (max-width: 860px) {{ .replay-grid {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <h1>Trendline Breakout Navigator Report</h1>
  <p class="muted">样本：{html.escape(ticker)} | {html.escape(period)} / {html.escape(interval)} | 生成时间：{generated_at}</p>

  <div class="card">
    <h2>这次做了什么</h2>
    <ul>
      <li>学习 breakout navigator 的逻辑路径</li>
      <li>做成我们自己的 <b>clean reimplementation</b></li>
      <li>并排对照 <code>pytrendline</code> 研究结果</li>
    </ul>
  </div>

  <div class="card">
    <h2>关键决定</h2>
    {render_table(decisions)}
  </div>

  <div class="card">
    <h2>怎么读这张图</h2>
    {render_table(legend)}
  </div>

  <div class="card">
    <h2>教学示意图 0：HH / HL / LH / LL 先是什么</h2>
    <img src="{artifacts_rel}/teaching_structure_labels.png" alt="teaching structure labels" />
    <p class="muted">先记这个：上升结构常见是 HL + HH；下降结构常见是 LH + LL。</p>
  </div>

  <div class="card">
    <h2>教学示意图 A：HH / LL 与 active line</h2>
    <img src="{artifacts_rel}/teaching_hh_ll_active_line.png" alt="teaching hh ll active line" />
    <p class="muted">短理解：先确认 HH / LL，再从前一个关键 swing 点启动水平 provisional line；等后续同侧 pivot 出现后，才更新成真正斜线。</p>
  </div>

  <div class="card">
    <h2>教学示意图 A2：为什么 HH 后盯支撑、LL 后盯压力，而不是直接画通道</h2>
    <img src="{artifacts_rel}/teaching_hh_ll_vs_channel_logic.png" alt="teaching hh ll vs channel logic" />
    <p class="muted">这套 navigator 不是“上下轨同时存在”的 channel 模型，而是“结构刚转强/转弱后，先盯最关键失效边”的状态机模型。</p>
    {render_table(difference_vs_channel)}
  </div>

  <div class="card">
    <h2>active support / resistance line 的生命周期</h2>
    {render_table(support_lifecycle)}
    <p class="muted">最关键一句：<b>HH 刚出现时的那条水平线，不是成熟趋势线本身，而是一个 provisional 结构底线。</b> 先用它回答“转强结构最起码不能跌回哪里下面”，等后续同侧 pivot 出现，再把它升级成真正 low→low / high→high 斜线。</p>
  </div>

  <div class="card">
    <h2>这条 support line 到底怎么用于交易</h2>
    {render_table(trading_mapping)}
    <p class="muted">更稳妥的教学口径：这条线首先是 <b>risk / invalidation line</b>，其次才可能被你拿来做入场辅助。也就是说，它更擅长回答“什么时候结构失效”，而不是单独回答“现在该不该冲进去买”。</p>
  </div>

  <div class="card">
    <h2>教学示意图 B：支撑线的反弹 vs 真跌破</h2>
    <img src="{artifacts_rel}/teaching_support_rebound_breakdown.png" alt="teaching support rebound breakdown" />
    <p class="muted">短理解：下探支撑但收盘收回，记作 <code>wick_bull</code>；收盘真正跌破支撑，记作 <code>breakout_bear</code>。</p>
  </div>

  <div class="card">
    <h2>教学示意图 C：压力线的回落 vs 真上破</h2>
    <img src="{artifacts_rel}/teaching_resistance_rejection_breakout.png" alt="teaching resistance rejection breakout" />
    <p class="muted">短理解：上刺压力但收盘压回，记作 <code>wick_bear</code>；收盘真正站上压力，记作 <code>breakout_bull</code>。</p>
  </div>

  <div class="card">
    <h2>读图顺序</h2>
    {render_table(reading_steps)}
  </div>

  <div class="card">
    <h2>展示窗口说明</h2>
    {render_table(window_notes)}
  </div>

  <div class="card">
    <h2>我们的图 1：最近 288 根（纯最近视角）</h2>
    <img src="{artifacts_rel}/our_navigator_recent_288.png" alt="our navigator recent 288" />
  </div>

  <div class="card">
    <h2>我们的图 2：最近 1000 根（更长上下文）</h2>
    <img src="{artifacts_rel}/our_navigator_recent_1000.png" alt="our navigator recent 1000" />
  </div>

  <div class="card">
    <h2>我们的图 3：自动挑出的 active line 最清楚窗口</h2>
    <img src="{artifacts_rel}/our_navigator_best_active_576.png" alt="our navigator best active 576" />
  </div>

  <div class="card">
    <h2>pytrendline 对照窗口（最近 {py_cfg.window_bars} 根）</h2>
    <img src="{artifacts_rel}/pytrendline_compare.png" alt="pytrendline compare" />
  </div>

  <div class="card">
    <h2>我们的模块统计</h2>
    {render_table(nav_stats)}
  </div>

  <div class="card">
    <h2>Recent segment audit（最近线段状态）</h2>
    {render_table(recent_segments)}
  </div>

  <div class="card">
    <h2>Segment Replay（点选线段回放）</h2>
    <p class="muted">点选某个 segment 后，会展示它何时被计算出来（computed at）、何时结束、用了哪些点（anchor / slope pivot），以及对应的局部 K 线回放图。</p>
    <div class="replay-grid">
      <div>
        <label for="segment-select"><b>选择 segment</b></label>
        <select id="segment-select"></select>
        <div id="segment-meta" class="replay-meta" style="margin-top:12px;"></div>
      </div>
      <div>
        <img id="segment-replay-img" alt="segment replay" />
      </div>
    </div>
  </div>

  <div class="card">
    <h2>pytrendline best support lines</h2>
    {render_table(py_support)}
  </div>

  <div class="card">
    <h2>pytrendline best resistance lines</h2>
    {render_table(py_resistance)}
  </div>

  <div class="card">
    <h2>Artifacts</h2>
    <ul>
      <li><a href="{artifacts_rel}/navigator_signals.csv">navigator_signals.csv</a></li>
      <li><a href="{artifacts_rel}/navigator_segments.csv">navigator_segments.csv</a></li>
      <li><a href="{artifacts_rel}/window_notes.csv">window_notes.csv</a></li>
      <li><a href="{artifacts_rel}/pytrendline_support.csv">pytrendline_support.csv</a></li>
      <li><a href="{artifacts_rel}/pytrendline_resistance.csv">pytrendline_resistance.csv</a></li>
      <li><a href="{artifacts_rel}/summary.json">summary.json</a></li>
    </ul>
  </div>
  <script>
    const SEGMENT_REPLAYS = {replay_json};
    const selectEl = document.getElementById('segment-select');
    const metaEl = document.getElementById('segment-meta');
    const imgEl = document.getElementById('segment-replay-img');

    function renderSegment(idx) {{
      const item = SEGMENT_REPLAYS[idx];
      if (!item) {{
        metaEl.innerHTML = '<em>No segment data.</em>';
        imgEl.removeAttribute('src');
        return;
      }}
      imgEl.src = `{artifacts_rel}/` + item.image_rel;
      imgEl.alt = item.label;
      metaEl.innerHTML = `
        <dl>
          <dt>segment</dt><dd>${{item.label}}</dd>
          <dt>computed at</dt><dd>${{item.computed_timestamp}}</dd>
          <dt>end at</dt><dd>${{item.end_timestamp}}</dd>
          <dt>end reason</dt><dd>${{item.end_reason}}</dd>
          <dt>anchor</dt><dd>${{item.anchor_timestamp}} @ ${{item.anchor_price}}</dd>
          <dt>slope pivot</dt><dd>${{item.pivot_timestamp ? `${{item.pivot_timestamp}} @ ${{item.pivot_price}}` : 'none yet (provisional)'}} </dd>
          <dt>bars visible</dt><dd>${{item.bars_visible}}</dd>
          <dt>state</dt><dd>${{item.is_provisional ? 'provisional' : 'final'}} / ${{item.side_label}}</dd>
        </dl>
      `;
    }}

    if (SEGMENT_REPLAYS.length) {{
      SEGMENT_REPLAYS.forEach((item, idx) => {{
        const opt = document.createElement('option');
        opt.value = String(idx);
        opt.textContent = item.label;
        selectEl.appendChild(opt);
      }});
      selectEl.addEventListener('change', (e) => renderSegment(Number(e.target.value)));
      renderSegment(SEGMENT_REPLAYS.length - 1);
      selectEl.value = String(SEGMENT_REPLAYS.length - 1);
    }} else {{
      metaEl.innerHTML = '<em>No segment data.</em>';
    }}
  </script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Build trendline breakout navigator report")
    parser.add_argument("--ticker", default=DEFAULT_TICKER)
    parser.add_argument("--period", default=DEFAULT_PERIOD)
    parser.add_argument("--interval", default=DEFAULT_INTERVAL)
    parser.add_argument("--window-bars", type=int, default=96)
    args = parser.parse_args()

    bars = download_bars(args.ticker, args.period, args.interval)
    bars["symbol"] = args.ticker
    nav_cfg = TrendlineBreakoutNavigatorConfig()
    nav_input = bars[["timestamp", "symbol", "open", "high", "low", "close"]].copy()
    nav = compute_trendline_breakout_navigator(nav_input, config=nav_cfg)
    segments = extract_trendline_breakout_segments(nav_input, config=nav_cfg)

    py_cfg = PyTrendlineConfig(window_bars=args.window_bars, min_points_required=3, ignore_breakouts=False, all_pts_must_be_pivots=True, time_interval=args.interval)
    py = detect_pytrendlines(bars.copy(), config=py_cfg)

    artifacts_dir = ensure_dir(ROOT / "reports" / "artifacts" / "trendline_breakout_navigator")
    site_dir = ensure_dir(ROOT / "reports" / "site" / "factors" / "trendline_breakout_navigator")

    nav.to_csv(artifacts_dir / "navigator_signals.csv", index=False)
    segments.to_csv(artifacts_dir / "navigator_segments.csv", index=False)
    py["support_trendlines"].to_csv(artifacts_dir / "pytrendline_support.csv", index=False)
    py["resistance_trendlines"].to_csv(artifacts_dir / "pytrendline_resistance.csv", index=False)
    replay_items = build_segment_replay_items(nav, segments, artifacts_dir)

    plot_teaching_structure_labels(artifacts_dir / "teaching_structure_labels.png")
    plot_teaching_hh_ll_active_line(artifacts_dir / "teaching_hh_ll_active_line.png")
    plot_teaching_hh_ll_vs_channel_logic(artifacts_dir / "teaching_hh_ll_vs_channel_logic.png")
    plot_teaching_support_rebound_and_breakdown(artifacts_dir / "teaching_support_rebound_breakdown.png")
    plot_teaching_resistance_rejection_and_breakout(artifacts_dir / "teaching_resistance_rejection_breakout.png")

    plot_our_navigator(
        nav,
        segments,
        artifacts_dir / "our_navigator_recent_288.png",
        title=f"{args.ticker} | clean reimplementation | recent 288 bars",
        mode="recent",
        bars=288,
    )
    plot_our_navigator(
        nav,
        segments,
        artifacts_dir / "our_navigator_recent_1000.png",
        title=f"{args.ticker} | clean reimplementation | recent 1000 bars",
        mode="recent",
        bars=1000,
    )
    plot_our_navigator(
        nav,
        segments,
        artifacts_dir / "our_navigator_best_active_576.png",
        title=f"{args.ticker} | clean reimplementation | best active 576-bar window",
        mode="best_active",
        bars=576,
    )
    plot_pytrendline_compare(py["candles_df"], py["support_trendlines"], py["resistance_trendlines"], py["support_pivots"], py["resistance_pivots"], artifacts_dir / "pytrendline_compare.png", title=f"{args.ticker} | pytrendline compare ({args.window_bars} bars)")

    nav_stats = pd.DataFrame(
        [
            ["bars", len(nav)],
            ["HH count", int(nav["tbn_hh"].sum())],
            ["LL count", int(nav["tbn_ll"].sum())],
            ["wick bull / rebound", int(nav["tbn_wick_bull"].sum())],
            ["wick bear / rejection", int(nav["tbn_wick_bear"].sum())],
            ["true breakout bull", int(nav["tbn_breakout_bull"].sum())],
            ["true breakout bear", int(nav["tbn_breakout_bear"].sum())],
            ["composite bullish bars", int((nav["tbn_composite_trend"] > 0).sum())],
            ["composite bearish bars", int((nav["tbn_composite_trend"] < 0).sum())],
            ["active long bars", int(nav["tbn_long_line_value"].notna().sum())],
            ["active medium bars", int(nav["tbn_medium_line_value"].notna().sum())],
            ["active short bars", int(nav["tbn_short_line_value"].notna().sum())],
            ["segment count", int(len(segments))],
            ["segment ended by breakout", int((segments["end_reason"] == "breakout").sum()) if not segments.empty else 0],
            ["segment ended by pivot_update", int((segments["end_reason"] == "pivot_update").sum()) if not segments.empty else 0],
            ["segment ended by trend_switch", int((segments["end_reason"] == "trend_switch").sum()) if not segments.empty else 0],
            ["segment ended by window_end", int((segments["end_reason"] == "window_end").sum()) if not segments.empty else 0],
        ],
        columns=["metric", "value"],
    )

    def _line_count(window: int) -> int:
        view = nav.tail(window)
        return int(view[["tbn_long_line_value", "tbn_medium_line_value", "tbn_short_line_value"]].notna().any(axis=1).sum())

    window_notes = pd.DataFrame(
        [
            ["最近 288 根", "保留纯最近视角", _line_count(288)],
            ["最近 1000 根", "给更长上下文，避免最近窗口刚好没有 active line", _line_count(1000)],
            ["自动挑出的 576 根窗口", "按 active line 最密集原则自动选择，优先保证看得到线", int(_find_best_active_window(nav, 576)[["tbn_long_line_value", "tbn_medium_line_value", "tbn_short_line_value"]].notna().any(axis=1).sum())],
        ],
        columns=["window", "why", "bars_with_active_line"],
    )
    window_notes.to_csv(artifacts_dir / "window_notes.csv", index=False)

    recent_segments = pd.DataFrame()
    if not segments.empty:
        recent_segments = (
            segments.sort_values(["end_timestamp", "segment_id"])
            .tail(18)
            [[
                "timeframe",
                "segment_id",
                "side_label",
                "is_provisional",
                "start_timestamp",
                "end_timestamp",
                "bars_visible",
                "end_reason",
                "anchor_price",
                "pivot_price",
                "slope",
            ]]
            .copy()
        )

    summary = {
        "ticker": args.ticker,
        "period": args.period,
        "interval": args.interval,
        "our_hh": int(nav["tbn_hh"].sum()),
        "our_ll": int(nav["tbn_ll"].sum()),
        "our_wick_bull": int(nav["tbn_wick_bull"].sum()),
        "our_wick_bear": int(nav["tbn_wick_bear"].sum()),
        "our_breakout_bull": int(nav["tbn_breakout_bull"].sum()),
        "our_breakout_bear": int(nav["tbn_breakout_bear"].sum()),
        "segment_count": int(len(segments)),
        "segment_end_breakout": int((segments["end_reason"] == "breakout").sum()) if not segments.empty else 0,
        "segment_end_pivot_update": int((segments["end_reason"] == "pivot_update").sum()) if not segments.empty else 0,
        "segment_end_trend_switch": int((segments["end_reason"] == "trend_switch").sum()) if not segments.empty else 0,
        "segment_end_window": int((segments["end_reason"] == "window_end").sum()) if not segments.empty else 0,
        "recent_288_active_bars": _line_count(288),
        "recent_1000_active_bars": _line_count(1000),
        "pytrendline_support_lines": int(len(py["support_trendlines"])),
        "pytrendline_resistance_lines": int(len(py["resistance_trendlines"])),
    }
    (artifacts_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    html_text = build_html(
        ticker=args.ticker,
        period=args.period,
        interval=args.interval,
        nav_cfg=nav_cfg,
        py_cfg=py_cfg,
        nav_stats=nav_stats,
        support=py["support_trendlines"],
        resistance=py["resistance_trendlines"],
        artifacts_rel="../../artifacts/trendline_breakout_navigator",
        window_notes=window_notes,
        recent_segments=recent_segments,
        replay_items=replay_items,
    )
    (site_dir / "report.html").write_text(html_text, encoding="utf-8")
    print(f"Wrote report to {site_dir / 'report.html'}")


if __name__ == "__main__":
    main()
