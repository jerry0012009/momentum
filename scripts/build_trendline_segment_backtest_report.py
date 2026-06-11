#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import timezone
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

from momentum.signals.trendline_breakout_navigator import (  # noqa: E402
    TrendlineBreakoutNavigatorConfig,
    compute_trendline_breakout_navigator,
    extract_trendline_breakout_segments,
)
from momentum.analytics.trendline_segment_backtest import (  # noqa: E402
    TrendlineSegmentEventConfig,
    evaluate_trendline_segment_strategy,
)
from momentum.analytics.multi_tf_momentum_backtest import MultiTfMomentumBacktestConfig  # noqa: E402


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
    return bars[keep].dropna(subset=["open", "high", "low", "close"]).sort_values("timestamp").reset_index(drop=True)


def load_input_data(input_path: str | None, ticker: str, period: str, interval: str) -> pd.DataFrame:
    if input_path:
        path = Path(input_path)
        if not path.is_absolute():
            path = ROOT / path
        if not path.exists():
            raise ValueError(f"Input not found: {path}")
        if path.suffix.lower() == ".parquet":
            df = pd.read_parquet(path)
        else:
            df = pd.read_csv(path)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        return df.sort_values("timestamp").reset_index(drop=True)
    return download_bars(ticker=ticker, period=period, interval=interval)


def load_multi_symbol_data(tickers: list[str], period: str, interval: str) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    for ticker in tickers:
        bars = download_bars(ticker=ticker, period=period, interval=interval)
        bars["symbol"] = ticker
        parts.append(bars)
    if not parts:
        raise ValueError("No symbols provided")
    return pd.concat(parts, ignore_index=True).sort_values(["symbol", "timestamp"]).reset_index(drop=True)


def pct(v: float) -> str:
    return "nan" if pd.isna(v) else f"{v * 100:.2f}%"


def render_table(df: pd.DataFrame, max_rows: int = 50) -> str:
    if df is None or df.empty:
        return '<p class="muted">(empty)</p>'
    view = df.head(max_rows).copy()
    for c in view.columns:
        if pd.api.types.is_float_dtype(view[c]):
            view[c] = view[c].map(lambda x: round(float(x), 6) if pd.notna(x) else "")
    return view.to_html(index=False, classes="tbl", border=0)


def load_optional_slope_audit_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    artifacts = ROOT / "reports" / "artifacts" / "trendline_event_slope_audit"
    sample_meta_path = artifacts / "sample_meta.csv"
    verdict_path = artifacts / "core_verdicts.csv"
    sample_meta = pd.read_csv(sample_meta_path) if sample_meta_path.exists() else pd.DataFrame()
    verdicts = pd.read_csv(verdict_path) if verdict_path.exists() else pd.DataFrame()
    return sample_meta, verdicts


def build_cross_asset_summary(summary: pd.DataFrame) -> pd.DataFrame:
    if summary is None or summary.empty or "symbol" not in summary.columns:
        return pd.DataFrame()
    grp = (
        summary.groupby(["strategy", "timeframe"], dropna=False)
        .agg(
            assets=("symbol", "nunique"),
            total_trades=("trades", "sum"),
            positive_assets=("total_return", lambda s: int((pd.Series(s) > 0).sum())),
            mean_total_return=("total_return", "mean"),
            median_total_return=("total_return", "median"),
            min_total_return=("total_return", "min"),
            max_total_return=("total_return", "max"),
            mean_max_drawdown=("max_drawdown", "mean"),
        )
        .reset_index()
    )
    grp["positive_asset_ratio"] = grp["positive_assets"] / grp["assets"].replace(0, np.nan)
    return grp[[
        "strategy", "timeframe", "assets", "positive_assets", "positive_asset_ratio",
        "total_trades", "mean_total_return", "median_total_return", "min_total_return",
        "max_total_return", "mean_max_drawdown",
    ]]


def _draw_candles(ax, view: pd.DataFrame) -> None:
    ts = pd.to_datetime(view["timestamp"], utc=True)
    x = mdates.date2num(ts.dt.to_pydatetime())
    width = float(np.median(np.diff(x))) * 0.72 if len(x) > 1 else (5 / (24 * 60)) * 0.72
    min_body = max(float((view["high"] - view["low"]).median()) * 0.05, 1e-6)
    for xi, (_, row) in zip(x, view.iterrows()):
        o, h, l, c = map(float, (row["open"], row["high"], row["low"], row["close"]))
        if c >= o:
            wick_color, fill_color, edge_color = "#166534", "#d1fae5", "#166534"
        else:
            wick_color, fill_color, edge_color = "#991b1b", "#fee2e2", "#991b1b"
        ax.vlines(xi, l, h, color=wick_color, linewidth=0.8, alpha=0.95, zorder=2)
        rect = plt.Rectangle((xi - width / 2, min(o, c)), width, max(abs(c - o), min_body), facecolor=fill_color, edgecolor=edge_color, linewidth=0.9, alpha=0.92, zorder=3)
        ax.add_patch(rect)
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d\n%H:%M", tz=timezone.utc))


def plot_equity_curves(nav: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12.8, 6.0))
    if nav.empty:
        ax.text(0.5, 0.5, "No NAV data", ha="center", va="center")
    else:
        nav = nav.copy()
        nav["timestamp"] = pd.to_datetime(nav["timestamp"], utc=True)
        nav["label"] = nav["strategy"] + " | " + nav["timeframe"]
        for label, g in nav.groupby("label", sort=True):
            ax.plot(g["timestamp"], g["nav"], linewidth=1.4, label=label)
    ax.set_title("Trendline segment strategy NAV curves")
    ax.grid(alpha=0.2)
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_event_counts(events: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10.5, 5.4))
    if events.empty:
        ax.text(0.5, 0.5, "No events", ha="center", va="center")
    else:
        counts = events.groupby(["strategy", "timeframe", "direction"]).size().reset_index(name="count")
        counts["label"] = counts["strategy"] + "\n" + counts["timeframe"]
        pivot = counts.pivot_table(index="label", columns="direction", values="count", fill_value=0)
        pivot = pivot.reindex(sorted(pivot.index), axis=0)
        x = np.arange(len(pivot))
        ax.bar(x - 0.18, pivot.get("long", pd.Series(0, index=pivot.index)), width=0.36, label="long", color="#16a34a")
        ax.bar(x + 0.18, pivot.get("short", pd.Series(0, index=pivot.index)), width=0.36, label="short", color="#dc2626")
        ax.set_xticks(x)
        ax.set_xticklabels(pivot.index)
        ax.legend(loc="upper right")
    ax.set_title("Signal counts by strategy/timeframe")
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_strategy_overlay(
    bars: pd.DataFrame,
    events: pd.DataFrame,
    trades: pd.DataFrame,
    *,
    strategy: str,
    timeframe: str,
    out_path: Path,
    bars_window: int = 400,
) -> None:
    view = bars.tail(bars_window).copy().reset_index(drop=True)
    view_ts = pd.to_datetime(view["timestamp"], utc=True)
    start_ts = view_ts.iloc[0]

    ev = events[(events["strategy"] == strategy) & (events["timeframe"] == timeframe)].copy()
    tr = trades[(trades["strategy"] == strategy) & (trades["timeframe"] == timeframe)].copy() if not trades.empty else pd.DataFrame()
    if not ev.empty:
        ev["signal_ts"] = pd.to_datetime(ev["signal_ts"], utc=True)
        ev = ev[ev["signal_ts"] >= start_ts]
    if not tr.empty:
        tr["entry_ts"] = pd.to_datetime(tr["entry_ts"], utc=True)
        tr["exit_ts"] = pd.to_datetime(tr["exit_ts"], utc=True)
        tr = tr[(tr["entry_ts"] >= start_ts) | (tr["exit_ts"] >= start_ts)]

    fig, ax = plt.subplots(figsize=(13.2, 6.8))
    _draw_candles(ax, view)

    if not ev.empty:
        long_ev = ev[ev["direction"] == "long"]
        short_ev = ev[ev["direction"] == "short"]
        if not long_ev.empty:
            y = [float(view.loc[view_ts.eq(ts), "low"].iloc[0]) * 0.998 if (view_ts == ts).any() else np.nan for ts in long_ev["signal_ts"]]
            ax.scatter(long_ev["signal_ts"], y, marker="^", color="#16a34a", s=58, zorder=6, label="long signal")
        if not short_ev.empty:
            y = [float(view.loc[view_ts.eq(ts), "high"].iloc[0]) * 1.002 if (view_ts == ts).any() else np.nan for ts in short_ev["signal_ts"]]
            ax.scatter(short_ev["signal_ts"], y, marker="v", color="#dc2626", s=58, zorder=6, label="short signal")

    if not tr.empty:
        ax.scatter(tr["entry_ts"], tr["entry_price"], marker="o", facecolors="none", edgecolors="#111827", s=40, zorder=7, label="entry")
        ax.scatter(tr["exit_ts"], tr["exit_price"], marker="x", color="#111827", s=36, zorder=7, label="exit")

    ax.set_title(f"{strategy} | {timeframe} | signal & trade overlay")
    ax.grid(alpha=0.2)
    ax.legend(loc="upper left", ncol=2)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_trade_return_hist(trades: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10.4, 5.6))
    if trades.empty:
        ax.text(0.5, 0.5, "No trades", ha="center", va="center")
    else:
        trades = trades.copy()
        trades["label"] = trades["strategy"] + " | " + trades["timeframe"]
        for label, g in trades.groupby("label", sort=True):
            ax.hist(g["net_ret"], bins=20, alpha=0.45, label=label)
        ax.legend(loc="best", fontsize=8)
    ax.set_title("Trade return distribution")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def _timestamp_index(df: pd.DataFrame, ts_value: object) -> int:
    if ts_value is None or pd.isna(ts_value) or str(ts_value) == "":
        return -1
    ts = pd.to_datetime(ts_value, utc=True, errors="coerce")
    if pd.isna(ts):
        return -1
    matches = df.index[df["timestamp"] == ts]
    return int(matches[0]) if len(matches) else -1


def _trade_replay_window(df: pd.DataFrame, trade: pd.Series) -> dict[str, int]:
    signal_idx = int(trade["signal_bar_index"]) if pd.notna(trade.get("signal_bar_index", np.nan)) else _timestamp_index(df, trade.get("signal_ts"))
    entry_idx = int(trade["entry_bar_index"]) if pd.notna(trade.get("entry_bar_index", np.nan)) else _timestamp_index(df, trade.get("entry_ts"))
    candidate_idx = int(trade["candidate_bar"]) if pd.notna(trade.get("candidate_bar", np.nan)) else _timestamp_index(df, trade.get("candidate_ts"))
    if candidate_idx < 0:
        candidate_idx = max(0, signal_idx - 2 if signal_idx >= 0 else entry_idx - 2)
    exit_idx = _timestamp_index(df, trade.get("exit_ts"))
    computed_idx = _timestamp_index(df, trade.get("computed_timestamp"))
    anchor_idx = int(trade["anchor_origin"]) if pd.notna(trade.get("anchor_origin", np.nan)) else max(signal_idx, 0)
    pivot_idx = int(trade["pivot_origin"]) if pd.notna(trade.get("pivot_origin", np.nan)) and float(trade.get("pivot_origin", -1)) >= 0 else -1

    start_refs = [idx for idx in [anchor_idx, candidate_idx, computed_idx] if idx >= 0]
    end_refs = [idx for idx in [candidate_idx, signal_idx, entry_idx, exit_idx, pivot_idx] if idx >= 0]
    start = max(0, min(start_refs) - 24) if start_refs else 0
    end = min(len(df) - 1, max(end_refs) + 36) if end_refs else min(len(df) - 1, 120)

    return {
        "signal_idx": signal_idx,
        "entry_idx": entry_idx,
        "candidate_idx": candidate_idx,
        "exit_idx": exit_idx,
        "computed_idx": computed_idx,
        "anchor_idx": anchor_idx,
        "pivot_idx": pivot_idx,
        "start": start,
        "end": end,
    }


def _segment_slope_from_trade(trade: pd.Series, anchor_idx: int, pivot_idx: int) -> float:
    if pd.notna(trade.get("pivot_price", np.nan)) and pivot_idx >= 0 and pivot_idx != anchor_idx:
        return (float(trade["pivot_price"]) - float(trade["anchor_price"])) / max(pivot_idx - anchor_idx, 1)
    return 0.0


def plot_trade_replay(bars: pd.DataFrame, trade: pd.Series, out_path: Path) -> None:
    df = bars.copy().reset_index(drop=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    window = _trade_replay_window(df, trade)
    entry_idx = window["entry_idx"]
    signal_idx = window["signal_idx"]
    candidate_idx = window["candidate_idx"]
    exit_idx = window["exit_idx"]
    computed_idx = window["computed_idx"]
    anchor_idx = window["anchor_idx"]
    pivot_idx = window["pivot_idx"]
    start = window["start"]
    end = window["end"]
    view = df.iloc[start:end + 1].copy()

    fig, ax = plt.subplots(figsize=(12.8, 6.8))
    _draw_candles(ax, view)

    seg_slope = _segment_slope_from_trade(trade, anchor_idx, pivot_idx)
    linestyle = "-" if str(trade.get("side_label", "")) == "support" else "--"
    color = "#2563eb" if str(trade.get("side_label", "")) == "support" else "#7c3aed"
    line_start = max(start, anchor_idx)
    live_end = min(end, candidate_idx)
    if live_end >= line_start:
        idxs = np.arange(line_start, live_end + 1)
        ts = pd.to_datetime(df.loc[idxs, "timestamp"], utc=True)
        y = float(trade["anchor_price"]) + seg_slope * (idxs - anchor_idx)
        ax.plot(ts, y, color=color, linewidth=2.0, linestyle=linestyle, zorder=4, label="segment line (live)")
    if end > max(candidate_idx, line_start):
        ext_start = max(candidate_idx, line_start)
        idxs = np.arange(ext_start, end + 1)
        ts = pd.to_datetime(df.loc[idxs, "timestamp"], utc=True)
        y = float(trade["anchor_price"]) + seg_slope * (idxs - anchor_idx)
        ax.plot(ts, y, color=color, linewidth=1.8, linestyle=":", alpha=0.75, zorder=4, label="frozen extension")

    anchor_ts = pd.to_datetime(trade["anchor_timestamp"], utc=True)
    ax.scatter([anchor_ts], [float(trade["anchor_price"])], marker="s", facecolors="white", edgecolors="#111827", linewidths=1.3, s=46, zorder=6, label="anchor")
    if pd.notna(trade.get("pivot_price", np.nan)) and str(trade.get("pivot_timestamp", "")):
        pivot_ts = pd.to_datetime(trade["pivot_timestamp"], utc=True)
        ax.scatter([pivot_ts], [float(trade["pivot_price"])], marker="D", facecolors="#0ea5e9", edgecolors="white", linewidths=0.9, s=44, zorder=6, label="slope pivot")

    for ts_str, label, color in [
        (trade.get("computed_timestamp", ""), "computed", "#94a3b8"),
        (trade["candidate_ts"], "candidate", "#6b7280"),
        (trade["signal_ts"], "signal", "#f59e0b"),
        (trade["entry_ts"], "entry", "#111827"),
        (trade.get("exit_ts", ""), "exit", "#ef4444"),
    ]:
        if not ts_str:
            continue
        ts = pd.to_datetime(ts_str, utc=True, errors="coerce")
        if pd.isna(ts):
            continue
        ax.axvline(ts, color=color, linewidth=1.1, linestyle=":", alpha=0.9, label=label)

    marker_specs = []
    if 0 <= candidate_idx < len(df):
        marker_specs.append((candidate_idx, float(df.loc[candidate_idx, "close"]), "candidate close", "X", "#6b7280", True))
    if 0 <= signal_idx < len(df):
        signal_color = "#16a34a" if str(trade.get("strategy", "")) == "breakout" else "#f59e0b"
        marker_specs.append((signal_idx, float(df.loc[signal_idx, "close"]), "signal close", "P", signal_color, True))
    if 0 <= entry_idx < len(df):
        marker_specs.append((entry_idx, float(trade["entry_price"]), "entry", "o", "#111827", False))
    if 0 <= exit_idx < len(df) and pd.notna(trade.get("exit_price", np.nan)):
        marker_specs.append((exit_idx, float(trade["exit_price"]), "exit", "x", "#ef4444", True))
    for idx, price, label, marker, color_value, filled in marker_specs:
        ts = pd.to_datetime(df.loc[idx, "timestamp"], utc=True)
        if filled:
            ax.scatter([ts], [price], marker=marker, color=color_value, s=56, zorder=7, label=label)
        else:
            ax.scatter([ts], [price], marker=marker, facecolors="none", edgecolors=color_value, s=56, zorder=7, label=label)

    ax.set_title(f"Trade Replay | {trade['strategy']} | {trade['timeframe']} | {trade['side']} | seg #{int(trade['segment_id'])}")
    ax.grid(alpha=0.2)
    ax.legend(loc="upper left", ncol=2)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def _build_trade_plot_payload(df: pd.DataFrame, trade: pd.Series, *, label: str, image_rel: str) -> dict[str, object]:
    window = _trade_replay_window(df, trade)
    signal_idx = window["signal_idx"]
    entry_idx = window["entry_idx"]
    candidate_idx = window["candidate_idx"]
    exit_idx = window["exit_idx"]
    computed_idx = window["computed_idx"]
    anchor_idx = window["anchor_idx"]
    pivot_idx = window["pivot_idx"]
    start = window["start"]
    end = window["end"]
    seg_slope = _segment_slope_from_trade(trade, anchor_idx, pivot_idx)
    side_label = str(trade.get("side_label", ""))

    return {
        "label": label,
        "image_rel": image_rel,
        "strategy": str(trade["strategy"]),
        "timeframe": str(trade["timeframe"]),
        "side": str(trade["side"]),
        "event_type": str(trade.get("event_type", "")),
        "segment_id": "" if pd.isna(trade.get("segment_id", np.nan)) else int(trade["segment_id"]),
        "side_label": side_label,
        "candidate_ts": str(trade.get("candidate_ts", "")),
        "signal_ts": str(trade.get("signal_ts", "")),
        "entry_ts": str(trade.get("entry_ts", "")),
        "exit_ts": str(trade.get("exit_ts", "")),
        "computed_timestamp": str(trade.get("computed_timestamp", "")),
        "segment_end_timestamp": str(trade.get("segment_end_timestamp", "")),
        "anchor_timestamp": str(trade.get("anchor_timestamp", "")),
        "anchor_price": "" if pd.isna(trade.get("anchor_price", np.nan)) else float(trade["anchor_price"]),
        "pivot_timestamp": str(trade.get("pivot_timestamp", "")),
        "pivot_price": "" if pd.isna(trade.get("pivot_price", np.nan)) else float(trade["pivot_price"]),
        "entry_price": "" if pd.isna(trade.get("entry_price", np.nan)) else float(trade["entry_price"]),
        "exit_price": "" if pd.isna(trade.get("exit_price", np.nan)) else float(trade["exit_price"]),
        "net_ret": "" if pd.isna(trade.get("net_ret", np.nan)) else float(trade["net_ret"]),
        "hold_bars": "" if pd.isna(trade.get("hold_bars", np.nan)) else int(trade["hold_bars"]),
        "exit_reason": str(trade.get("exit_reason", "")),
        "confirm_bars": "" if pd.isna(trade.get("confirm_bars", np.nan)) else int(trade["confirm_bars"]),
        "resolution_bars": "" if pd.isna(trade.get("resolution_bars", np.nan)) else int(trade["resolution_bars"]),
        "line_value_candidate": "" if pd.isna(trade.get("line_value_candidate", np.nan)) else float(trade["line_value_candidate"]),
        "line_value_signal": "" if pd.isna(trade.get("line_value_signal", np.nan)) else float(trade["line_value_signal"]),
        "segment_is_provisional": "" if pd.isna(trade.get("segment_is_provisional", np.nan)) else int(trade["segment_is_provisional"]),
        "window_start": start,
        "window_end": end,
        "anchor_idx": anchor_idx,
        "pivot_idx": pivot_idx,
        "computed_idx": computed_idx,
        "candidate_idx": candidate_idx,
        "signal_idx": signal_idx,
        "entry_idx": entry_idx,
        "exit_idx": exit_idx,
        "line_slope": float(seg_slope),
        "line_color": "#2563eb" if side_label == "support" else "#7c3aed",
        "line_dash": "solid" if side_label == "support" else "dash",
        "candidate_price": float(df.loc[candidate_idx, "close"]) if 0 <= candidate_idx < len(df) else None,
        "signal_price": float(df.loc[signal_idx, "close"]) if 0 <= signal_idx < len(df) else None,
    }


def build_trade_replay_items(bars: pd.DataFrame, trades: pd.DataFrame, artifacts_dir: Path, *, max_static_pngs: int = 0) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["label","image_rel","strategy","timeframe","side","segment_id","candidate_ts","signal_ts","entry_ts","anchor_timestamp","anchor_price","pivot_timestamp","pivot_price","computed_timestamp","side_label"])
    replay_dir = ensure_dir(artifacts_dir / "trade_replays") if max_static_pngs > 0 else None
    items = []
    ordered = trades.sort_values(["entry_ts", "strategy", "timeframe"]).reset_index(drop=True)
    render_start = max(len(ordered) - max_static_pngs, 0)
    for i, (_, tr) in enumerate(ordered.iterrows(), start=1):
        image_rel = ""
        if replay_dir is not None and (i - 1) >= render_start:
            filename = f"trade_{i:03d}_{tr['strategy']}_{tr['timeframe']}_{tr['side']}.png"
            plot_trade_replay(bars, tr, replay_dir / filename)
            image_rel = f"trade_replays/{filename}"
        items.append(
            {
                "label": f"#{i} | {tr['strategy']} | {tr['timeframe']} | {tr['side']} | seg {int(tr['segment_id']) if pd.notna(tr['segment_id']) else 'n/a'}",
                "image_rel": image_rel,
                "strategy": tr["strategy"],
                "timeframe": tr["timeframe"],
                "side": tr["side"],
                "segment_id": "" if pd.isna(tr.get("segment_id", np.nan)) else int(tr["segment_id"]),
                "candidate_ts": str(tr.get("candidate_ts", "")),
                "signal_ts": str(tr.get("signal_ts", "")),
                "entry_ts": str(tr.get("entry_ts", "")),
                "anchor_timestamp": str(tr.get("anchor_timestamp", "")),
                "anchor_price": "" if pd.isna(tr.get("anchor_price", np.nan)) else float(tr["anchor_price"]),
                "pivot_timestamp": str(tr.get("pivot_timestamp", "")),
                "pivot_price": "" if pd.isna(tr.get("pivot_price", np.nan)) else float(tr["pivot_price"]),
                "computed_timestamp": str(tr.get("computed_timestamp", "")),
                "side_label": str(tr.get("side_label", "")),
            }
        )
    return pd.DataFrame(items)


def build_trade_plot_data(bars: pd.DataFrame, trades: pd.DataFrame, trade_replays: pd.DataFrame) -> dict[str, object]:
    df = bars.copy().reset_index(drop=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    market = {
        "timestamp": df["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%SZ").tolist(),
        "open": [round(float(v), 6) for v in df["open"].tolist()],
        "high": [round(float(v), 6) for v in df["high"].tolist()],
        "low": [round(float(v), 6) for v in df["low"].tolist()],
        "close": [round(float(v), 6) for v in df["close"].tolist()],
    }
    items: list[dict[str, object]] = []
    if not trades.empty:
        ordered = trades.sort_values(["entry_ts", "strategy", "timeframe"]).reset_index(drop=True)
        replay_rows = trade_replays.to_dict(orient="records") if trade_replays is not None and not trade_replays.empty else []
        for i, (_, tr) in enumerate(ordered.iterrows()):
            replay_row = replay_rows[i] if i < len(replay_rows) else {}
            label = str(replay_row.get("label", f"#{i+1} | {tr['strategy']} | {tr['timeframe']} | {tr['side']}"))
            image_rel = str(replay_row.get("image_rel", ""))
            items.append(_build_trade_plot_payload(df, tr, label=label, image_rel=image_rel))
    return {"market": market, "items": items}


def select_pivot_diagnostic_trade(trades: pd.DataFrame) -> pd.Series | None:
    if trades is None or trades.empty:
        return None
    ordered = trades.sort_values(["entry_ts", "strategy", "timeframe"]).reset_index(drop=True)
    for strategy, timeframe in [("breakout", "long"), ("rebound", "long"), ("breakout", "medium"), ("rebound", "medium")]:
        sub = ordered[(ordered["strategy"] == strategy) & (ordered["timeframe"] == timeframe)]
        if not sub.empty:
            return sub.tail(1).iloc[0]
    return ordered.tail(1).iloc[0]


def build_pivot_diagnostic_table(nav: pd.DataFrame, trade: pd.Series) -> pd.DataFrame:
    if trade is None or len(trade) == 0:
        return pd.DataFrame()
    tf_prefix = f"tbn_{trade['timeframe']}"
    low_origin_col = f"{tf_prefix}_pivot_low_origin"
    low_price_col = f"{tf_prefix}_pivot_low_price"
    high_origin_col = f"{tf_prefix}_pivot_high_origin"
    high_price_col = f"{tf_prefix}_pivot_high_price"

    df = nav.copy().reset_index(drop=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    anchor_idx = int(trade["anchor_origin"])
    pivot_idx = int(trade["pivot_origin"])
    anchor_ts = pd.to_datetime(trade["anchor_timestamp"], utc=True)
    candidate_ts = pd.to_datetime(trade["candidate_ts"], utc=True)
    start_ts = anchor_ts - pd.Timedelta(hours=4)
    end_ts = candidate_ts + pd.Timedelta(minutes=45)

    rows: list[dict[str, object]] = []

    lows = df[df[low_origin_col].fillna(-1).astype(int) >= 0].copy()
    for _, row in lows.iterrows():
        origin_idx = int(row[low_origin_col])
        origin_ts = pd.to_datetime(df.loc[origin_idx, "timestamp"], utc=True)
        if origin_ts < start_ts or origin_ts > end_ts:
            continue
        role = "unused confirmed swing low"
        note = "confirmed low, but not used by current active segment"
        used = "no"
        if origin_idx == anchor_idx:
            role = "anchor"
            note = "selected as the first point of the current segment"
            used = "yes"
        elif origin_idx == pivot_idx:
            role = "pivot"
            note = "selected as the active slope point of the current segment"
            used = "yes"
        elif origin_ts < anchor_ts:
            note = "confirmed low exists, but it belongs to an earlier structure before the current anchor"
        else:
            note = "confirmed low exists after anchor, but navigator did not promote it to the segment pivot"
        rows.append(
            {
                "point_type": "swing_low",
                "origin_ts": origin_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "confirm_ts": pd.to_datetime(row["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "price": float(row[low_price_col]),
                "role": role,
                "used_in_segment": used,
                "note": note,
            }
        )

    highs = df[df[high_origin_col].fillna(-1).astype(int) >= 0].copy()
    for _, row in highs.iterrows():
        origin_idx = int(row[high_origin_col])
        origin_ts = pd.to_datetime(df.loc[origin_idx, "timestamp"], utc=True)
        if origin_ts < start_ts or origin_ts > end_ts:
            continue
        rows.append(
            {
                "point_type": "swing_high",
                "origin_ts": origin_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "confirm_ts": pd.to_datetime(row["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "price": float(row[high_price_col]),
                "role": "context high",
                "used_in_segment": "no",
                "note": "confirmed swing high shown for context; not the pivot of this segment",
            }
        )

    if not rows:
        return pd.DataFrame()
    out = pd.DataFrame(rows)
    out["origin_ts"] = pd.to_datetime(out["origin_ts"], utc=True)
    out = out.sort_values(["origin_ts", "point_type"]).reset_index(drop=True)
    out["origin_ts"] = out["origin_ts"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return out


def plot_pivot_diagnostic(bars: pd.DataFrame, nav: pd.DataFrame, segments: pd.DataFrame, trade: pd.Series, out_path: Path) -> None:
    if trade is None or len(trade) == 0:
        return

    tf_prefix = f"tbn_{trade['timeframe']}"
    low_origin_col = f"{tf_prefix}_pivot_low_origin"
    low_price_col = f"{tf_prefix}_pivot_low_price"
    high_origin_col = f"{tf_prefix}_pivot_high_origin"
    high_price_col = f"{tf_prefix}_pivot_high_price"

    df = bars.copy().reset_index(drop=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    nav_df = nav.copy().reset_index(drop=True)
    nav_df["timestamp"] = pd.to_datetime(nav_df["timestamp"], utc=True)
    seg_df = segments.copy().reset_index(drop=True)
    if not seg_df.empty:
        for c in ["start_timestamp", "end_timestamp", "anchor_timestamp", "pivot_timestamp"]:
            if c in seg_df.columns:
                seg_df[c] = pd.to_datetime(seg_df[c], utc=True, errors="coerce")

    anchor_ts = pd.to_datetime(trade["anchor_timestamp"], utc=True)
    pivot_ts = pd.to_datetime(trade["pivot_timestamp"], utc=True)
    computed_ts = pd.to_datetime(trade["computed_timestamp"], utc=True)
    candidate_ts = pd.to_datetime(trade["candidate_ts"], utc=True)
    anchor_idx = int(trade["anchor_origin"])
    pivot_idx = int(trade["pivot_origin"])
    seg_slope = _segment_slope_from_trade(trade, anchor_idx, pivot_idx)

    start_ts = anchor_ts - pd.Timedelta(hours=4)
    end_ts = candidate_ts + pd.Timedelta(minutes=45)
    view = df[(df["timestamp"] >= start_ts) & (df["timestamp"] <= end_ts)].copy().reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(15.2, 8.2))
    _draw_candles(ax, view)

    line_mask = (df["timestamp"] >= anchor_ts) & (df["timestamp"] <= candidate_ts)
    idxs = df.index[line_mask].to_numpy()
    if len(idxs):
        ts = pd.to_datetime(df.loc[idxs, "timestamp"], utc=True)
        y = float(trade["anchor_price"]) + seg_slope * (idxs - anchor_idx)
        live_mask = ts < candidate_ts
        if live_mask.any():
            ax.plot(ts[live_mask], y[live_mask], color="#7c3aed", linewidth=2.2, linestyle="--", zorder=4, label="current segment line")
        ax.plot(ts[ts >= candidate_ts], y[ts >= candidate_ts], color="#7c3aed", linewidth=2.2, linestyle=":", alpha=0.85, zorder=4, label="frozen extension")

    lows = nav_df[nav_df[low_origin_col].fillna(-1).astype(int) >= 0].copy()
    lows = lows.assign(origin_idx=lows[low_origin_col].astype(int))
    lows["origin_ts"] = lows["origin_idx"].map(df["timestamp"])
    lows = lows[(lows["origin_ts"] >= start_ts) & (lows["origin_ts"] <= end_ts)]
    if not lows.empty:
        unused = lows[(lows["origin_idx"] != anchor_idx) & (lows["origin_idx"] != pivot_idx)]
        if not unused.empty:
            ax.scatter(unused["origin_ts"], unused[low_price_col], marker="o", facecolors="#f8fafc", edgecolors="#0f172a", linewidths=1.0, s=52, zorder=6, label="confirmed swing low (unused)")
        anchor_rows = lows[lows["origin_idx"] == anchor_idx]
        if not anchor_rows.empty:
            ax.scatter(anchor_rows["origin_ts"], anchor_rows[low_price_col], marker="s", facecolors="white", edgecolors="#111827", linewidths=1.5, s=86, zorder=7, label="anchor (used)")
        pivot_rows = lows[lows["origin_idx"] == pivot_idx]
        if not pivot_rows.empty:
            ax.scatter(pivot_rows["origin_ts"], pivot_rows[low_price_col], marker="D", facecolors="#0ea5e9", edgecolors="white", linewidths=1.0, s=84, zorder=7, label="pivot (used)")

    highs = nav_df[nav_df[high_origin_col].fillna(-1).astype(int) >= 0].copy()
    highs = highs.assign(origin_idx=highs[high_origin_col].astype(int))
    highs["origin_ts"] = highs["origin_idx"].map(df["timestamp"])
    highs = highs[(highs["origin_ts"] >= start_ts) & (highs["origin_ts"] <= end_ts)]
    if not highs.empty:
        ax.scatter(highs["origin_ts"], highs[high_price_col], marker="^", color="#ef4444", s=48, alpha=0.85, zorder=5, label="confirmed swing high (context)")

    related_segments = pd.DataFrame()
    if not seg_df.empty:
        related_segments = seg_df[
            (seg_df["timeframe"] == tf_prefix)
            & (seg_df["anchor_origin"].astype(int) == anchor_idx)
            & (seg_df["start_timestamp"] >= start_ts)
            & (seg_df["start_timestamp"] <= end_ts)
        ].copy()
    if not related_segments.empty:
        for _, seg_row in related_segments.sort_values("start_timestamp").iterrows():
            ts = pd.to_datetime(seg_row["start_timestamp"], utc=True)
            label = "segment starts (computed)" if int(seg_row.get("is_provisional", 0)) == 0 else "provisional segment starts"
            color = "#94a3b8" if int(seg_row.get("is_provisional", 0)) == 0 else "#cbd5e1"
            ax.axvline(ts, color=color, linewidth=1.15, linestyle="--", alpha=0.9, zorder=3, label=label)

    ax.axvline(candidate_ts, color="#6b7280", linewidth=1.2, linestyle=":", alpha=0.95, zorder=3, label="candidate breakout")
    candidate_close = float(df.loc[df["timestamp"] == candidate_ts, "close"].iloc[0]) if (df["timestamp"] == candidate_ts).any() else np.nan
    if pd.notna(candidate_close):
        ax.scatter([candidate_ts], [candidate_close], marker="X", color="#6b7280", s=86, zorder=8, label="candidate close")

    ax.annotate("anchor\nused by current segment", xy=(anchor_ts, float(trade["anchor_price"])), xytext=(10, 18), textcoords="offset points", fontsize=10, color="#111827", arrowprops=dict(arrowstyle="->", color="#111827", lw=1))
    ax.annotate("pivot\nused by current segment", xy=(pivot_ts, float(trade["pivot_price"])), xytext=(10, 18), textcoords="offset points", fontsize=10, color="#0369a1", arrowprops=dict(arrowstyle="->", color="#0ea5e9", lw=1))
    ax.annotate("computed_at\nline becomes tradable", xy=(computed_ts, float(trade["anchor_price"]) + seg_slope * (_timestamp_index(df, computed_ts) - anchor_idx)), xytext=(8, -44), textcoords="offset points", fontsize=10, color="#475569", arrowprops=dict(arrowstyle="->", color="#94a3b8", lw=1))
    ax.annotate("candidate\nfirst break attempt", xy=(candidate_ts, candidate_close), xytext=(10, 18), textcoords="offset points", fontsize=10, color="#4b5563", arrowprops=dict(arrowstyle="->", color="#6b7280", lw=1))

    handles, labels = ax.get_legend_handles_labels()
    dedup = dict(zip(labels, handles))
    ax.legend(dedup.values(), dedup.keys(), loc="upper left", ncol=2)
    ax.set_title(f"Pivot Diagnostic | {trade['strategy']} | {trade['timeframe']} | seg #{int(trade['segment_id'])}")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def build_html(*, ticker: str, period: str, interval: str, sample_desc: str, event_cfg: TrendlineSegmentEventConfig, bt_cfg: MultiTfMomentumBacktestConfig, summary: pd.DataFrame, aggregate_summary: pd.DataFrame, event_counts: pd.DataFrame, recent_events: pd.DataFrame, recent_trades: pd.DataFrame, artifacts_rel: str, trade_replays: pd.DataFrame, trade_plot_data: dict[str, object], pivot_diagnostic_title: str, pivot_diagnostic_rel: str, pivot_diagnostic_table: pd.DataFrame, slope_audit_meta: pd.DataFrame, slope_audit_verdicts: pd.DataFrame) -> str:
    rule_table = pd.DataFrame(
        [
            ["Round A (core focus)", "核心结论只保留 breakout-long 与 rebound-long；medium / short 只做辅助统计"],
            ["breakout strategy", f"首次穿线 close 算确认 #1；连续 {event_cfg.breakout_confirm_bars} 根 close 都在突破方向 → 下一根 open 入场"],
            ["rebound strategy", f"首次穿线后未达 {event_cfg.breakout_confirm_bars} 连续确认；close 回到原区间，再额外 {event_cfg.rebound_confirm_bars} 根 inside-range close 确认 → 下一根 open 反向入场"],
            ["Round B regime filter", "medium 用 long 趋势过滤；short 用 medium 趋势过滤。higher timeframe > 0 才允许 long，< 0 才允许 short" if event_cfg.regime_filter_medium_short else "disabled"],
            ["reference line", "冻结被突破的旧 segment 延长线，不跟随后续新线一起漂移"],
            ["segment filter", "默认只用 final segments（is_provisional = 0）" if event_cfg.only_final_segments else "使用 provisional + final segments"],
            ["resolution window", f"每个 breakout candidate 最多观察 {event_cfg.max_resolution_bars} 根 bar"],
            ["Round C exit", f"启用 ATR trailing stop：ATR({bt_cfg.atr_period}) × {bt_cfg.atr_trailing_mult:.1f}；若未触发则仍允许反向信号反手，最后一根 close 强平" if bt_cfg.enable_atr_trailing_stop else "反向信号反手；最后一根 close 强平"],
            ["cost model", f"fee {bt_cfg.fee_bps_per_side:.1f} bps / side + slippage {bt_cfg.slippage_bps_per_side:.1f} bps / side"],
        ],
        columns=["item", "definition"],
    )
    core_aggregate = aggregate_summary[(aggregate_summary["timeframe"] == "long") & (aggregate_summary["strategy"].isin(["breakout", "rebound"]))].copy() if not aggregate_summary.empty else pd.DataFrame()
    secondary_aggregate = aggregate_summary[aggregate_summary["timeframe"].isin(["medium", "short"])].copy() if not aggregate_summary.empty else pd.DataFrame()
    core_detail = summary[(summary["timeframe"] == "long") & (summary["strategy"].isin(["breakout", "rebound"]))].copy() if not summary.empty else pd.DataFrame()
    long_focus_verdicts = slope_audit_verdicts[slope_audit_verdicts["sample_key"].isin(["60m_365d", "60m_730d"])].copy() if not slope_audit_verdicts.empty and "sample_key" in slope_audit_verdicts.columns else pd.DataFrame()
    trade_plot_json = json.dumps(trade_plot_data if trade_plot_data else {"market": {}, "items": []}, ensure_ascii=False)
    return f"""<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8' />
  <title>Trendline Segment Backtest Report</title>
  <script src='https://cdn.plot.ly/plotly-2.35.2.min.js'></script>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background:#f8fafc; color:#0f172a; margin:0; padding:24px; }}
    .wrap {{ max-width: 1280px; margin: 0 auto; }}
    .card {{ background:white; border:1px solid #e2e8f0; border-radius:14px; padding:18px 20px; margin-bottom:18px; box-shadow:0 1px 2px rgba(0,0,0,0.04); }}
    h1,h2,h3 {{ margin:0 0 10px 0; }}
    .muted {{ color:#475569; }}
    .tbl {{ width:100%; border-collapse: collapse; font-size: 14px; }}
    .tbl th,.tbl td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    img {{ max-width:100%; border:1px solid #e5e7eb; border-radius:10px; }}
    a {{ color:#2563eb; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
    .replay-grid {{ display:grid; grid-template-columns:320px 1fr; gap:16px; align-items:start; }}
    .replay-meta {{ background:#f8fafc; border:1px solid #e5e7eb; border-radius:10px; padding:12px; font-size:14px; }}
    .replay-meta dl {{ margin:0; }}
    .replay-meta dt {{ font-weight:600; margin-top:8px; }}
    .replay-meta dd {{ margin:2px 0 0 0; color:#374151; }}
    .trade-plot {{ width:100%; min-height:640px; border:1px solid #e5e7eb; border-radius:10px; background:white; }}
    .mini-link {{ font-size:13px; margin-top:10px; display:inline-block; }}
    select {{ width:100%; padding:8px 10px; border-radius:8px; border:1px solid #d1d5db; background:white; }}
    @media (max-width:860px) {{ .replay-grid {{ grid-template-columns:1fr; }} .trade-plot {{ min-height:520px; }} }}
  </style>
</head>
<body>
<div class='wrap'>
  <div class='card'>
    <h1>Trendline Segment Backtest Report</h1>
    <p class='muted'>Ticker: <b>{ticker}</b> | Period: <b>{period}</b> | Interval: <b>{interval}</b></p>
    <p class='muted'>{sample_desc}</p>
    <p class='muted'>这份报告把 segment-state 趋势线正式转成两套可回测策略：<b>confirmed breakout</b> 与 <b>failed-breakout rebound</b>。</p>
  </div>

  <div class='card'>
    <h2>Code-level strategy definitions</h2>
    {render_table(rule_table)}
  </div>

  <div class='card'>
    <h2>Round A · Core conclusion (long timeframe only)</h2>
    <p class='muted'>这里只保留 <b>breakout-long</b> 与 <b>rebound-long</b> 作为核心结论；判断时优先看 <b>positive_asset_ratio</b>、<b>mean_total_return</b>、<b>mean_max_drawdown</b>。</p>
    {render_table(core_aggregate, max_rows=10)}
    <div style='margin-top:12px;'>{render_table(core_detail, max_rows=40)}</div>
  </div>

  <div class='card'>
    <h2>Appendix · slope-conditioned audit (crypto quick + 1Y/2Y)</h2>
    <p class='muted'>这是把当前这套 segment backtest 口径继续往前推进的一层附录：不再只看“整体 breakout / rebound 是否有效”，而是检查 <b>不同 slope bucket</b> 下的结果是否明显不同。</p>
    <p class='muted'>说明：Yahoo 的 30m 只支持最近 60d，所以长样本复核重点放在 <b>60m / 365d</b> 与 <b>60m / 730d</b>。完整细页见：<a href='../trendline_event_slope_audit/report.html'>trendline_event_slope_audit/report.html</a></p>
    <div style='margin-top:10px;'>{render_table(slope_audit_meta, max_rows=20)}</div>
    <div style='margin-top:14px;'>{render_table(long_focus_verdicts, max_rows=80)}</div>
  </div>

  <div class='card'>
    <h2>Round B · Medium / short (supporting only)</h2>
    <p class='muted'>这部分已经加入 higher-timeframe regime filter：medium 受 long 过滤，short 受 medium 过滤；仅做辅助观察，不作为核心结论。</p>
    {render_table(secondary_aggregate, max_rows=20)}
  </div>

  <div class='card'>
    <h2>Full performance summary</h2>
    {render_table(summary, max_rows=120)}
  </div>

  <div class='card'>
    <h2>Event counts</h2>
    {render_table(event_counts)}
    <img src='{artifacts_rel}/event_counts.png' alt='event counts' />
  </div>

  <div class='card'>
    <h2>Equity curves</h2>
    <img src='{artifacts_rel}/equity_curves.png' alt='equity curves' />
  </div>

  <div class='card'>
    <h2>Breakout strategy overlay (focus timeframe)</h2>
    <img src='{artifacts_rel}/overlay_breakout.png' alt='breakout overlay' />
  </div>

  <div class='card'>
    <h2>Rebound strategy overlay (focus timeframe)</h2>
    <img src='{artifacts_rel}/overlay_rebound.png' alt='rebound overlay' />
  </div>

  <div class='card'>
    <h2>Trade return distribution</h2>
    <img src='{artifacts_rel}/trade_return_hist.png' alt='trade return histogram' />
  </div>

  <div class='card'>
    <h2>Recent events</h2>
    {render_table(recent_events)}
  </div>

  <div class='card'>
    <h2>Pivot diagnostic example</h2>
    <p class='muted'>{pivot_diagnostic_title}</p>
    <p class='muted'>这张诊断图会把<strong>当前例子窗口里的 confirmed swing low / high</strong> 全部画出来，并明确区分：<strong>被当前 segment 选成 anchor 的点</strong>、<strong>被选成 pivot 的点</strong>、以及<strong>虽然是 confirmed swing 但没有被当前 active segment 采用的点</strong>。</p>
    <img src='{artifacts_rel}/{pivot_diagnostic_rel}' alt='pivot diagnostic example' />
    <div style='margin-top:12px;'>
      {render_table(pivot_diagnostic_table, max_rows=30)}
    </div>
  </div>

  <div class='card'>
    <h2>Trade Replay（按交易审计，可缩放）</h2>
    <p class='muted'>点选某一笔 trade 后，会直接在交互图里标出：<strong>趋势线 live 段</strong>、<strong>冻结延长线</strong>、<strong>anchor / slope pivot</strong>、<strong>candidate breakout</strong>、<strong>signal</strong>、<strong>entry / exit</strong>。支持鼠标滚轮缩放、框选放大、双击复位。</p>
    <div class='replay-grid'>
      <div>
        <label for='trade-select'><b>选择 trade</b></label>
        <select id='trade-select'></select>
        <div id='trade-meta' class='replay-meta' style='margin-top:12px;'></div>
        <a id='trade-replay-link' class='mini-link' target='_blank' rel='noreferrer'>打开静态 PNG 回放</a>
      </div>
      <div>
        <div id='trade-plot' class='trade-plot'></div>
      </div>
    </div>
  </div>

  <div class='card'>
    <h2>Recent trades</h2>
    {render_table(recent_trades)}
  </div>

  <div class='card'>
    <h2>Artifacts</h2>
    <ul>
      <li><a href='{artifacts_rel}/bars.csv'>bars.csv</a></li>
      <li><a href='{artifacts_rel}/navigator_signals.csv'>navigator_signals.csv</a></li>
      <li><a href='{artifacts_rel}/navigator_segments.csv'>navigator_segments.csv</a></li>
      <li><a href='{artifacts_rel}/segment_strategy_events.csv'>segment_strategy_events.csv</a></li>
      <li><a href='{artifacts_rel}/segment_strategy_signals.csv'>segment_strategy_signals.csv</a></li>
      <li><a href='{artifacts_rel}/segment_strategy_trades.csv'>segment_strategy_trades.csv</a></li>
      <li><a href='{artifacts_rel}/segment_strategy_nav.csv'>segment_strategy_nav.csv</a></li>
      <li><a href='{artifacts_rel}/segment_strategy_summary.csv'>segment_strategy_summary.csv</a></li>
      <li><a href='{artifacts_rel}/cross_asset_summary.csv'>cross_asset_summary.csv</a></li>
      <li><a href='{artifacts_rel}/pivot_diagnostic_example.csv'>pivot_diagnostic_example.csv</a></li>
      <li><a href='{artifacts_rel}/{pivot_diagnostic_rel}'>{pivot_diagnostic_rel}</a></li>
      <li><a href='{artifacts_rel}/summary.json'>summary.json</a></li>
      <li><a href='../../artifacts/trendline_event_slope_audit/sample_meta.csv'>trendline_event_slope_audit/sample_meta.csv</a></li>
      <li><a href='../../artifacts/trendline_event_slope_audit/core_verdicts.csv'>trendline_event_slope_audit/core_verdicts.csv</a></li>
      <li><a href='../trendline_event_slope_audit/report.html'>trendline_event_slope_audit/report.html</a></li>
    </ul>
  </div>
</div>
<script>
  const TRADE_PLOT_DATA = {trade_plot_json};
  const MARKET = TRADE_PLOT_DATA.market || {{}};
  const TRADE_REPLAYS = TRADE_PLOT_DATA.items || [];
  const tradeSelectEl = document.getElementById('trade-select');
  const tradeMetaEl = document.getElementById('trade-meta');
  const tradePlotEl = document.getElementById('trade-plot');
  const tradeReplayLinkEl = document.getElementById('trade-replay-link');

  function pct(v) {{
    return (v === '' || v === null || Number.isNaN(v)) ? 'n/a' : `${{(v * 100).toFixed(2)}}%`;
  }}

  function fmt(v) {{
    return (v === '' || v === null || Number.isNaN(v)) ? 'n/a' : String(v);
  }}

  function explainSignal(item) {{
    if (item.strategy === 'breakout') {{
      return '真突破延续：candidate breakout 之后，连续确认成立，再于下一根 open 入场。';
    }}
    return '假突破反手：candidate breakout 没有延续，价格回到线内并确认，再于下一根 open 反向入场。';
  }}

  function buildLineTrace(item, fromIdx, toIdx, name, dash, opacity) {{
    const x = [];
    const y = [];
    for (let i = fromIdx; i <= toIdx; i += 1) {{
      x.push(MARKET.timestamp[i]);
      y.push(item.anchor_price + item.line_slope * (i - item.anchor_idx));
    }}
    return {{
      type: 'scatter',
      mode: 'lines',
      x,
      y,
      name,
      line: {{ color: item.line_color, width: 2, dash }},
      opacity,
      hovertemplate: '%{{x}}<br>line=%{{y:.2f}}<extra>' + name + '</extra>',
    }};
  }}

  function buildMarkerTrace(name, x, y, symbol, color, fill = true) {{
    if (!x || y === null || y === '' || Number.isNaN(y)) return null;
    return {{
      type: 'scatter',
      mode: 'markers+text',
      x: [x],
      y: [y],
      name,
      text: [name],
      textposition: 'top center',
      marker: {{
        symbol,
        size: 11,
        color: fill ? color : '#ffffff',
        line: {{ color, width: 2 }},
      }},
      hovertemplate: '%{{x}}<br>%{{y:.2f}}<extra>' + name + '</extra>',
    }};
  }}

  function buildVerticalLine(ts, color, label) {{
    if (!ts) return null;
    return {{
      type: 'line',
      xref: 'x',
      yref: 'paper',
      x0: ts,
      x1: ts,
      y0: 0,
      y1: 1,
      line: {{ color, width: 1.2, dash: 'dot' }},
      label: {{ text: label, textposition: 'top' }},
    }};
  }}

  function renderTrade(idx) {{
    const item = TRADE_REPLAYS[idx];
    if (!item || !MARKET.timestamp) {{
      tradeMetaEl.innerHTML = '<em>No trade replay data.</em>';
      tradeReplayLinkEl.removeAttribute('href');
      if (tradePlotEl) tradePlotEl.innerHTML = '';
      return;
    }}

    const start = item.window_start;
    const end = item.window_end;
    const x = MARKET.timestamp.slice(start, end + 1);
    const open = MARKET.open.slice(start, end + 1);
    const high = MARKET.high.slice(start, end + 1);
    const low = MARKET.low.slice(start, end + 1);
    const close = MARKET.close.slice(start, end + 1);

    const data = [
      {{
        type: 'candlestick',
        x,
        open,
        high,
        low,
        close,
        name: 'candles',
        increasing: {{ line: {{ color: '#166534' }}, fillcolor: '#d1fae5' }},
        decreasing: {{ line: {{ color: '#991b1b' }}, fillcolor: '#fee2e2' }},
        hoverlabel: {{ namelength: -1 }},
      }},
    ];

    const lineStart = Math.max(start, item.anchor_idx);
    const liveEnd = Math.min(end, item.candidate_idx);
    if (liveEnd >= lineStart) {{
      data.push(buildLineTrace(item, lineStart, liveEnd, 'segment line (live)', item.line_dash, 1.0));
    }}
    const extStart = Math.max(item.candidate_idx, lineStart);
    if (end > extStart) {{
      data.push(buildLineTrace(item, extStart, end, 'frozen extension', 'dot', 0.8));
    }}

    const markerTraces = [
      buildMarkerTrace('anchor', item.anchor_timestamp, item.anchor_price, 'square-open', '#111827', false),
      buildMarkerTrace('slope pivot', item.pivot_timestamp, item.pivot_price, 'diamond', '#0ea5e9', true),
      buildMarkerTrace('candidate', item.candidate_ts, item.candidate_price, 'x', '#6b7280', true),
      buildMarkerTrace(item.strategy === 'breakout' ? 'confirmed breakout' : 'failed-break confirmed', item.signal_ts, item.signal_price, item.strategy === 'breakout' ? 'star' : 'hexagram', item.strategy === 'breakout' ? '#16a34a' : '#f59e0b', true),
      buildMarkerTrace('entry', item.entry_ts, item.entry_price, 'circle-open', '#111827', false),
      buildMarkerTrace('exit', item.exit_ts, item.exit_price, 'x-thin', '#ef4444', true),
    ].filter(Boolean);
    markerTraces.forEach((trace) => data.push(trace));

    const shapes = [
      buildVerticalLine(item.computed_timestamp, '#94a3b8', 'computed'),
      buildVerticalLine(item.candidate_ts, '#6b7280', 'candidate'),
      buildVerticalLine(item.signal_ts, '#f59e0b', 'signal'),
      buildVerticalLine(item.entry_ts, '#111827', 'entry'),
      buildVerticalLine(item.exit_ts, '#ef4444', 'exit'),
    ].filter(Boolean);

    const layout = {{
      title: `${{item.label}}`,
      dragmode: 'zoom',
      hovermode: 'x unified',
      paper_bgcolor: '#ffffff',
      plot_bgcolor: '#ffffff',
      margin: {{ l: 56, r: 24, t: 56, b: 40 }},
      legend: {{ orientation: 'h', yanchor: 'bottom', y: 1.02, xanchor: 'left', x: 0 }},
      xaxis: {{
        type: 'date',
        rangeslider: {{ visible: true }},
        showgrid: true,
        gridcolor: '#e2e8f0',
      }},
      yaxis: {{
        showgrid: true,
        gridcolor: '#e2e8f0',
        fixedrange: false,
      }},
      shapes,
    }};

    Plotly.react(tradePlotEl, data, layout, {{ responsive: true, scrollZoom: true, displaylogo: false }});

    if (item.image_rel) {{
      tradeReplayLinkEl.href = `{artifacts_rel}/` + item.image_rel;
      tradeReplayLinkEl.textContent = '打开静态 PNG 回放';
    }} else {{
      tradeReplayLinkEl.removeAttribute('href');
      tradeReplayLinkEl.textContent = '该笔仅保留交互图（未单独导出 PNG）';
    }}
    tradeMetaEl.innerHTML = `
      <dl>
        <dt>trade</dt><dd>${{item.label}}</dd>
        <dt>interpretation</dt><dd>${{explainSignal(item)}}</dd>
        <dt>reference line</dt><dd>${{item.side_label}} / segment #${{fmt(item.segment_id)}} / ${{item.segment_is_provisional === 1 ? 'provisional' : 'final'}}</dd>
        <dt>computed at</dt><dd>${{fmt(item.computed_timestamp)}}</dd>
        <dt>candidate breakout</dt><dd>${{fmt(item.candidate_ts)}} @ line=${{fmt(item.line_value_candidate)}}</dd>
        <dt>signal</dt><dd>${{fmt(item.signal_ts)}} @ line=${{fmt(item.line_value_signal)}} / confirm=${{fmt(item.confirm_bars)}} / resolution=${{fmt(item.resolution_bars)}} bars</dd>
        <dt>entry</dt><dd>${{fmt(item.entry_ts)}} @ ${{fmt(item.entry_price)}}</dd>
        <dt>exit</dt><dd>${{fmt(item.exit_ts)}} @ ${{fmt(item.exit_price)}} / ${{fmt(item.exit_reason)}}</dd>
        <dt>anchor</dt><dd>${{fmt(item.anchor_timestamp)}} @ ${{fmt(item.anchor_price)}}</dd>
        <dt>slope pivot</dt><dd>${{item.pivot_timestamp ? `${{item.pivot_timestamp}} @ ${{item.pivot_price}}` : 'none yet'}}</dd>
        <dt>return</dt><dd>${{pct(item.net_ret)}} / hold=${{fmt(item.hold_bars)}} bars</dd>
        <dt>how to read</dt><dd>实线 = candidate 前这条线真实活着的阶段；点虚线 = candidate 之后用于确认真突破/假突破的冻结延长线。</dd>
      </dl>
    `;
  }}

  if (TRADE_REPLAYS.length) {{
    TRADE_REPLAYS.forEach((item, idx) => {{
      const opt = document.createElement('option');
      opt.value = String(idx);
      opt.textContent = item.label;
      tradeSelectEl.appendChild(opt);
    }});
    tradeSelectEl.addEventListener('change', (e) => renderTrade(Number(e.target.value)));
    renderTrade(TRADE_REPLAYS.length - 1);
    tradeSelectEl.value = String(TRADE_REPLAYS.length - 1);
  }} else {{
    tradeMetaEl.innerHTML = '<em>No trade replay data.</em>';
    tradeReplayLinkEl.removeAttribute('href');
  }}
</script>
</body>
</html>
"""


def main() -> None:
    ap = argparse.ArgumentParser(description="Build segment-based trendline backtest report")
    ap.add_argument("--ticker", default="BTC-USD")
    ap.add_argument("--tickers", default=None, help="Comma-separated symbols for multi-asset expansion, e.g. BTC-USD,ETH-USD")
    ap.add_argument("--period", default="60d")
    ap.add_argument("--interval", default="5m")
    ap.add_argument("--input", default=None)
    ap.add_argument("--focus-timeframe", default="short", choices=["short", "medium", "long"])
    ap.add_argument("--max-resolution-bars", type=int, default=12)
    ap.add_argument("--breakout-confirm-bars", type=int, default=3)
    ap.add_argument("--rebound-confirm-bars", type=int, default=1)
    ap.add_argument("--include-provisional", action="store_true")
    args = ap.parse_args()

    artifacts_dir = ensure_dir(ROOT / "reports" / "artifacts" / "trendline_segment_backtest")
    site_dir = ensure_dir(ROOT / "reports" / "site" / "factors" / "trendline_segment_backtest")

    tickers = [t.strip() for t in str(args.tickers).split(",") if t.strip()] if args.tickers else []
    if args.input:
        bars = load_input_data(args.input, args.ticker, args.period, args.interval)
        if "symbol" not in bars.columns:
            bars["symbol"] = args.ticker
    elif tickers:
        bars = load_multi_symbol_data(tickers, args.period, args.interval)
    else:
        bars = load_input_data(args.input, args.ticker, args.period, args.interval)
        bars["symbol"] = args.ticker

    sample_symbols = sorted(pd.Series(bars["symbol"]).dropna().astype(str).unique().tolist())
    if len(sample_symbols) == 1:
        sample_desc = f"单标的样本：<b>{sample_symbols[0]}</b>"
    else:
        shown = ", ".join(sample_symbols[:8])
        suffix = "" if len(sample_symbols) <= 8 else f" ... (+{len(sample_symbols)-8})"
        sample_desc = f"扩样样本：<b>{len(sample_symbols)}</b> 个币种（{shown}{suffix}）"

    nav_cfg = TrendlineBreakoutNavigatorConfig()
    nav_input = bars[["timestamp", "symbol", "open", "high", "low", "close"]].copy()
    nav = compute_trendline_breakout_navigator(nav_input, config=nav_cfg)
    segments = extract_trendline_breakout_segments(nav_input, config=nav_cfg)

    event_cfg = TrendlineSegmentEventConfig(
        breakout_confirm_bars=args.breakout_confirm_bars,
        rebound_confirm_bars=args.rebound_confirm_bars,
        max_resolution_bars=args.max_resolution_bars,
        only_final_segments=not args.include_provisional,
        regime_filter_medium_short=True,
    )
    bt_cfg = MultiTfMomentumBacktestConfig(
        enable_atr_trailing_stop=True,
        atr_period=14,
        atr_trailing_mult=2.5,
    )
    result = evaluate_trendline_segment_strategy(nav, segments, event_config=event_cfg, backtest_config=bt_cfg)

    summary = result.summary.copy()
    if not summary.empty:
        summary = summary[[c for c in ["strategy", "timeframe", "symbol", "trades", "win_rate", "avg_ret", "median_ret", "total_return", "max_drawdown", "long_trades", "short_trades"] if c in summary.columns]]
        summary = summary.sort_values(["strategy", "timeframe"]).reset_index(drop=True)

    aggregate_summary = build_cross_asset_summary(summary)

    event_counts = (
        result.events.groupby(["strategy", "timeframe", "direction"]).size().reset_index(name="count")
        if not result.events.empty
        else pd.DataFrame(columns=["strategy", "timeframe", "direction", "count"])
    )

    recent_events = result.events.sort_values(["signal_ts", "event_type"]).tail(20) if not result.events.empty else pd.DataFrame()
    if not recent_events.empty:
        recent_events = recent_events[[c for c in ["strategy", "timeframe", "event_type", "direction", "signal_ts", "entry_ts", "segment_id", "side_label", "confirm_bars", "resolution_bars"] if c in recent_events.columns]]

    recent_trades = result.trades.sort_values(["entry_ts", "side"]).tail(20) if not result.trades.empty else pd.DataFrame()
    if not recent_trades.empty:
        recent_trades = recent_trades[[c for c in ["strategy", "timeframe", "side", "event_type", "segment_id", "side_label", "computed_timestamp", "candidate_ts", "signal_ts", "entry_ts", "anchor_timestamp", "anchor_price", "pivot_timestamp", "pivot_price", "entry_price", "exit_ts", "exit_price", "net_ret", "hold_bars", "exit_reason"] if c in recent_trades.columns]]

    bars.to_csv(artifacts_dir / "bars.csv", index=False)
    nav.to_csv(artifacts_dir / "navigator_signals.csv", index=False)
    segments.to_csv(artifacts_dir / "navigator_segments.csv", index=False)
    result.events.to_csv(artifacts_dir / "segment_strategy_events.csv", index=False)
    result.strategy_signals.to_csv(artifacts_dir / "segment_strategy_signals.csv", index=False)
    result.trades.to_csv(artifacts_dir / "segment_strategy_trades.csv", index=False)
    result.nav.to_csv(artifacts_dir / "segment_strategy_nav.csv", index=False)
    summary.to_csv(artifacts_dir / "segment_strategy_summary.csv", index=False)
    aggregate_summary.to_csv(artifacts_dir / "cross_asset_summary.csv", index=False)
    trade_replays = build_trade_replay_items(bars, result.trades, artifacts_dir)
    trade_plot_data = build_trade_plot_data(bars, result.trades, trade_replays)

    pivot_trade = select_pivot_diagnostic_trade(result.trades)
    pivot_diagnostic_table = build_pivot_diagnostic_table(nav, pivot_trade) if pivot_trade is not None else pd.DataFrame()
    pivot_diagnostic_rel = "pivot_diagnostic_example.png"
    pivot_diagnostic_title = "No example trade available."
    if pivot_trade is not None:
        pivot_diagnostic_title = (
            f"Example trade: {pivot_trade['strategy']} | {pivot_trade['timeframe']} | {pivot_trade['side']} | "
            f"seg #{int(pivot_trade['segment_id']) if pd.notna(pivot_trade['segment_id']) else 'n/a'} | "
            f"anchor {pivot_trade.get('anchor_timestamp', '')} -> pivot {pivot_trade.get('pivot_timestamp', '')} -> computed {pivot_trade.get('computed_timestamp', '')}"
        )
        plot_pivot_diagnostic(bars, nav, segments, pivot_trade, artifacts_dir / pivot_diagnostic_rel)
        pivot_diagnostic_table.to_csv(artifacts_dir / "pivot_diagnostic_example.csv", index=False)

    plot_equity_curves(result.nav, artifacts_dir / "equity_curves.png")
    plot_event_counts(result.events, artifacts_dir / "event_counts.png")
    plot_strategy_overlay(bars, result.events, result.trades, strategy="breakout", timeframe=args.focus_timeframe, out_path=artifacts_dir / "overlay_breakout.png")
    plot_strategy_overlay(bars, result.events, result.trades, strategy="rebound", timeframe=args.focus_timeframe, out_path=artifacts_dir / "overlay_rebound.png")
    plot_trade_return_hist(result.trades, artifacts_dir / "trade_return_hist.png")

    summary_json = {
        "ticker": args.ticker,
        "tickers": sample_symbols,
        "symbol_count": len(sample_symbols),
        "period": args.period,
        "interval": args.interval,
        "focus_timeframe": args.focus_timeframe,
        "breakout_confirm_bars": args.breakout_confirm_bars,
        "rebound_confirm_bars": args.rebound_confirm_bars,
        "max_resolution_bars": args.max_resolution_bars,
        "only_final_segments": not args.include_provisional,
        "regime_filter_medium_short": True,
        "atr_period": bt_cfg.atr_period,
        "atr_trailing_mult": bt_cfg.atr_trailing_mult,
        "enable_atr_trailing_stop": bt_cfg.enable_atr_trailing_stop,
        "event_count": int(len(result.events)),
        "trade_count": int(len(result.trades)),
    }
    (artifacts_dir / "summary.json").write_text(json.dumps(summary_json, ensure_ascii=False, indent=2), encoding="utf-8")

    slope_audit_meta, slope_audit_verdicts = load_optional_slope_audit_tables()

    html = build_html(
        ticker=args.ticker,
        period=args.period,
        interval=args.interval,
        sample_desc=sample_desc,
        event_cfg=event_cfg,
        bt_cfg=bt_cfg,
        summary=summary,
        aggregate_summary=aggregate_summary,
        event_counts=event_counts,
        recent_events=recent_events,
        recent_trades=recent_trades,
        artifacts_rel="../../artifacts/trendline_segment_backtest",
        trade_replays=trade_replays,
        trade_plot_data=trade_plot_data,
        pivot_diagnostic_title=pivot_diagnostic_title,
        pivot_diagnostic_rel=pivot_diagnostic_rel,
        pivot_diagnostic_table=pivot_diagnostic_table,
        slope_audit_meta=slope_audit_meta,
        slope_audit_verdicts=slope_audit_verdicts,
    )
    out_path = site_dir / "report.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"Wrote report to {out_path}")


if __name__ == "__main__":
    main()
