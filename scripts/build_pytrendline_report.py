#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import html
import importlib
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.factors.pytrendline_bridge import PyTrendlineConfig, detect_pytrendlines, _ensure_pytrendline_compat  # noqa: E402

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
    table_html = df.to_html(index=index, classes="tbl", border=0, justify="left", escape=False)
    return f'<div class="table-wrap">{table_html}</div>'


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


def _duplicate_group_stats(df: pd.DataFrame, *, label: str, avg_candle_range: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    if df.empty or "duplicate_group_id" not in df.columns:
        empty = pd.DataFrame(columns=["metric", "value"])
        return empty, pd.DataFrame(columns=["group_id", "side", "group_size", "best_line_id", "best_score", "contains_breakout"])

    grouped = (
        df.groupby("duplicate_group_id")
        .agg(
            group_size=("id", "count"),
            best_line_id=("id", "first"),
            best_score=("score", "max"),
            contains_breakout=("is_breakout", "max"),
        )
        .reset_index()
        .rename(columns={"duplicate_group_id": "group_id"})
        .sort_values(["group_size", "best_score"], ascending=[False, False])
    )
    grouped.insert(1, "side", label)

    overview = pd.DataFrame(
        [
            [f"{label}_all_lines", int(len(df))],
            [f"{label}_duplicate_groups", int(grouped["group_id"].nunique())],
            [f"{label}_best_from_group_lines", int(df["is_best_from_duplicate_group"].sum()) if "is_best_from_duplicate_group" in df.columns else 0],
            [f"{label}_avg_group_size", round(float(grouped["group_size"].mean()), 2) if not grouped.empty else 0.0],
            [f"{label}_max_group_size", int(grouped["group_size"].max()) if not grouped.empty else 0],
            [f"{label}_dup_threshold_last_price", round(avg_candle_range * 0.2, 4)],
            [f"{label}_dup_threshold_slope", round(avg_candle_range * 0.05, 4)],
        ],
        columns=["metric", "value"],
    )
    return overview, grouped.head(8)


def _draw_candlesticks(ax, candles: pd.DataFrame, x: np.ndarray, *, width: float = 0.62) -> None:
    up_color = "#16a34a"
    down_color = "#dc2626"
    wick_color = "#334155"

    for i, row in enumerate(candles.itertuples(index=False)):
        o = float(row.Open)
        h = float(row.High)
        l = float(row.Low)
        c = float(row.Close)
        color = up_color if c >= o else down_color

        ax.vlines(x[i], l, h, color=wick_color, linewidth=0.8, alpha=0.95, zorder=2)

        lower = min(o, c)
        height = abs(c - o)
        if height < 1e-9:
            ax.hlines(o, x[i] - width / 2, x[i] + width / 2, color=color, linewidth=1.4, zorder=3)
        else:
            ax.add_patch(
                Rectangle(
                    (x[i] - width / 2, lower),
                    width,
                    height,
                    facecolor=color,
                    edgecolor=color,
                    linewidth=0.9,
                    alpha=0.9,
                    zorder=3,
                )
            )


def _format_time_axis(ax, candles: pd.DataFrame, x: np.ndarray) -> None:
    ts = pd.to_datetime(candles["Date"], utc=True)
    if len(x) == 0:
        return
    tick_count = min(8, len(x))
    tick_idx = np.linspace(0, len(x) - 1, tick_count, dtype=int)
    tick_idx = np.unique(tick_idx)
    tick_labels = [ts.iloc[i].strftime("%m-%d %H:%M") for i in tick_idx]
    ax.set_xticks(tick_idx)
    ax.set_xticklabels(tick_labels, rotation=0, fontsize=9)
    ax.set_xlim(-1, len(x))


def _plot_base(ax, candles: pd.DataFrame, *, add_pivots: bool = False, support_pivots: list[int] | None = None, resistance_pivots: list[int] | None = None) -> np.ndarray:
    x = np.arange(len(candles))
    _draw_candlesticks(ax, candles, x)

    if add_pivots and support_pivots:
        sp = candles.iloc[support_pivots]
        ax.scatter(support_pivots, sp["Low"], color="#14b8a6", marker="v", s=34, label="support pivots", zorder=4)
    if add_pivots and resistance_pivots:
        rp = candles.iloc[resistance_pivots]
        ax.scatter(resistance_pivots, rp["High"], color="#f59e0b", marker="^", s=34, label="resistance pivots", zorder=4)

    _format_time_axis(ax, candles, x)
    return x


def _annotate_pivot_labels(ax, candles: pd.DataFrame, pivots: list[int], *, kind: str) -> None:
    if not pivots:
        return

    y_col = 'Low' if kind == 'support' else 'High'
    color = '#0f766e' if kind == 'support' else '#b45309'
    avg_candle_range = max(float((candles['High'] - candles['Low']).mean()), 0.01)
    offset = avg_candle_range * 0.22
    va = 'top' if kind == 'support' else 'bottom'
    delta = -offset if kind == 'support' else offset

    for idx in pivots:
        if idx < 0 or idx >= len(candles):
            continue
        y = float(candles.iloc[idx][y_col]) + delta
        ax.text(
            idx,
            y,
            str(idx),
            fontsize=7.5,
            color=color,
            ha='center',
            va=va,
            zorder=7,
            bbox=dict(boxstyle='round,pad=0.16', facecolor='white', edgecolor='none', alpha=0.75),
        )


def _parse_index_list(value) -> list[int]:
    if isinstance(value, list):
        return [int(v) for v in value]
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return []
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return []
        try:
            parsed = ast.literal_eval(value)
            if isinstance(parsed, list):
                return [int(v) for v in parsed]
        except Exception:
            return []
    return []


def _parse_timestamp_list(value) -> list[str]:
    if isinstance(value, list):
        out = []
        for v in value:
            try:
                out.append(pd.to_datetime(v, utc=True).strftime('%m-%d %H:%M'))
            except Exception:
                out.append(str(v))
        return out
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return []
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return []
        try:
            parsed = ast.literal_eval(value)
            if isinstance(parsed, list):
                out = []
                for v in parsed:
                    try:
                        out.append(pd.to_datetime(v, utc=True).strftime('%m-%d %H:%M'))
                    except Exception:
                        out.append(str(v))
                return out
        except Exception:
            return []
    return []


def _compact_list_str(items: list[str] | list[int], *, sep: str = ', ') -> str:
    return sep.join(str(x) for x in items) if items else ''


def _prepare_display_lines(df: pd.DataFrame, *, top_n: int = 12) -> pd.DataFrame:
    show = _best_lines(df, top_n=top_n)
    if show.empty:
        return show

    out = show.copy()
    if 'pointset_indeces' in out.columns:
        out['pointset_indeces'] = out['pointset_indeces'].apply(lambda v: _compact_list_str(_parse_index_list(v)))
    if 'pointset_dates' in out.columns:
        out['pointset_dates'] = out['pointset_dates'].apply(lambda v: ' | '.join(_parse_timestamp_list(v)))

    keep = [
        'id', 'is_breakout', 'pointset_indeces', 'pointset_dates',
        'breakout_index', 'breakout_date', 'num_points', 'm', 'b', 'score',
        'starts_at_date', 'ends_at_date'
    ]
    keep = [c for c in keep if c in out.columns]
    return out[keep]


def _highlight_line_points(ax, candles: pd.DataFrame, row: pd.Series, *, kind: str, color: str, annotate: bool = True) -> None:
    point_idxs = [i for i in _parse_index_list(row.get("pointset_indeces")) if 0 <= i < len(candles)]
    if not point_idxs:
        return

    y_col = "Low" if kind == "support" else "High"
    vals = candles.iloc[point_idxs][y_col]
    ax.scatter(
        point_idxs,
        vals,
        s=90,
        facecolors=color,
        edgecolors="white",
        linewidths=1.9,
        zorder=8,
        label=f"{kind} line pivots",
    )
    if annotate:
        for idx, y in zip(point_idxs, vals):
            ax.text(
                idx,
                float(y),
                str(idx),
                color="white",
                fontsize=7,
                ha="center",
                va="center",
                zorder=9,
                fontweight="bold",
            )


def _highlight_breakout_bars(ax, candles: pd.DataFrame, lines: pd.DataFrame, *, kind: str) -> None:
    if lines.empty or "breakout_index" not in lines.columns:
        return

    idx_series = pd.to_numeric(lines["breakout_index"], errors="coerce").dropna().astype(int)
    if idx_series.empty:
        return

    idxs = sorted(set(i for i in idx_series.tolist() if 0 <= i < len(candles)))
    if not idxs:
        return

    color = "#16a34a" if kind == "support" else "#dc2626"
    y_col = "Low" if kind == "support" else "High"
    vals = candles.iloc[idxs][y_col]

    ax.scatter(
        idxs,
        vals,
        s=180,
        facecolors="none",
        edgecolors=color,
        linewidths=2.0,
        zorder=7,
        label=f"{kind} breakout bar",
    )

    for idx, y in zip(idxs, vals):
        ax.text(
            idx,
            float(y),
            "S" if kind == "support" else "R",
            color=color,
            fontsize=8,
            ha="center",
            va="bottom" if kind == "support" else "top",
            zorder=8,
        )



def _collect_line_pointset_indices(lines: pd.DataFrame, *, total_bars: int) -> list[int]:
    if lines.empty:
        return []
    idxs: set[int] = set()
    for _, row in lines.iterrows():
        idxs.update(i for i in _parse_index_list(row.get("pointset_indeces")) if 0 <= i < total_bars)
    return sorted(idxs)



def _highlight_selected_pivots(ax, candles: pd.DataFrame, pivots: list[int], *, kind: str, annotate: bool = False) -> None:
    if not pivots:
        return
    y_col = "Low" if kind == "support" else "High"
    color = "#14b8a6" if kind == "support" else "#f59e0b"
    vals = candles.iloc[pivots][y_col]
    ax.scatter(
        pivots,
        vals,
        color=color,
        marker="v" if kind == "support" else "^",
        s=56,
        alpha=0.95,
        linewidths=0.0,
        label=f"{kind} pivots used by shown lines",
        zorder=4,
    )
    if annotate:
        _annotate_pivot_labels(ax, candles, pivots, kind=kind)


def _safe_int(value) -> int | None:
    try:
        if pd.isna(value):
            return None
    except Exception:
        pass
    try:
        return int(value)
    except Exception:
        return None


def _line_plot_indices(row: pd.Series, *, total_bars: int, extension_target: str = "last") -> tuple[int, int, int]:
    point_idxs = [i for i in _parse_index_list(row.get("pointset_indeces")) if 0 <= i < total_bars]
    start_idx = _safe_int(row.get("starts_at_index"))
    end_idx = _safe_int(row.get("ends_at_index"))
    breakout_idx = _safe_int(row.get("breakout_index"))

    anchors = [i for i in [start_idx, end_idx] if i is not None and 0 <= i < total_bars]
    if point_idxs:
        fit_start = min(point_idxs)
        fit_end = max(point_idxs)
    elif anchors:
        fit_start = min(anchors)
        fit_end = max(anchors)
    else:
        fit_start = 0
        fit_end = total_bars - 1

    if extension_target == "breakout" and breakout_idx is not None and 0 <= breakout_idx < total_bars:
        projection_end = max(fit_end, breakout_idx)
    else:
        projection_end = total_bars - 1

    return fit_start, fit_end, projection_end


def _focus_bounds(lines: pd.DataFrame, *, total_bars: int, min_span: int = 24, pad: int = 4) -> tuple[int, int]:
    if lines.empty:
        return 0, max(total_bars - 1, 0)

    idxs: list[int] = []
    for _, row in lines.iterrows():
        idxs.extend(i for i in _parse_index_list(row.get("pointset_indeces")) if 0 <= i < total_bars)
        for key in ["starts_at_index", "ends_at_index", "breakout_index"]:
            value = _safe_int(row.get(key))
            if value is not None and 0 <= value < total_bars:
                idxs.append(value)

    if not idxs:
        return 0, max(total_bars - 1, 0)

    left = max(0, min(idxs) - pad)
    right = min(total_bars - 1, max(idxs) + pad)
    if right - left + 1 < min_span:
        center = (left + right) // 2
        half = min_span // 2
        left = max(0, center - half)
        right = min(total_bars - 1, left + min_span - 1)
        left = max(0, right - min_span + 1)
    return left, right


def _render_line_collection(
    ax,
    candles: pd.DataFrame,
    lines: pd.DataFrame,
    *,
    kind: str,
    breakout_only: bool = False,
    non_breakout_only: bool = False,
    highlight_pointsets: bool = False,
    top_n: int = 4,
    zoom_to_lines: bool = True,
) -> pd.DataFrame:
    x = np.arange(len(candles))
    show = _best_lines(lines, top_n=max(top_n * 8, top_n))
    if breakout_only and not show.empty and "is_breakout" in show.columns:
        show = show[show["is_breakout"] == True]  # noqa: E712
    if non_breakout_only and not show.empty and "is_breakout" in show.columns:
        show = show[show["is_breakout"] == False]  # noqa: E712
    show = show.head(top_n)

    base_color = "#2563eb" if kind == "support" else "#7c3aed"
    breakout_color = "#16a34a" if kind == "support" else "#dc2626"

    if show.empty:
        msg = (
            f"No non-breakout {kind} lines in current window\nSee Step 4 for breakout events"
            if non_breakout_only else
            f"No {kind} lines available in current window"
        )
        ax.text(
            0.5, 0.52, msg,
            transform=ax.transAxes,
            ha='center', va='center',
            fontsize=12,
            color='#334155',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='#cbd5e1', alpha=0.95),
            zorder=10,
        )
        return show

    for _, row in show.iterrows():
        y = _line_y(row, x)
        is_breakout = bool(row.get("is_breakout", False))
        color = breakout_color if is_breakout else base_color
        fit_start, fit_end, projection_end = _line_plot_indices(
            row,
            total_bars=len(candles),
            extension_target="breakout" if breakout_only else "last",
        )
        breakout_idx = _safe_int(row.get("breakout_index"))

        solid_label = f"{kind} fitted segment"
        projection_label = f"{kind} projection"
        if is_breakout:
            solid_label = f"{kind} pre-breakout segment"
            projection_label = f"{kind} post-breakout extension"

        solid_end = fit_end
        if is_breakout and breakout_idx is not None and fit_start <= breakout_idx <= projection_end:
            solid_end = min(max(breakout_idx, fit_start), projection_end)

        ax.plot(
            x[fit_start:solid_end + 1],
            y[fit_start:solid_end + 1],
            color=color,
            linestyle="-",
            linewidth=2.8 if not is_breakout else 2.4,
            alpha=1.0,
            label=solid_label,
            zorder=6,
        )
        if solid_end < projection_end:
            ax.plot(
                x[solid_end:projection_end + 1],
                y[solid_end:projection_end + 1],
                color=color,
                linestyle="--" if is_breakout else ":",
                linewidth=1.8,
                alpha=0.9,
                label=projection_label,
                zorder=5,
            )
        if highlight_pointsets:
            _highlight_line_points(ax, candles, row, kind=kind, color=color)

    if zoom_to_lines:
        left, right = _focus_bounds(show, total_bars=len(candles))
        ax.set_xlim(left - 0.5, right + 0.5)

    return show


def plot_price_with_pivots(candles: pd.DataFrame, support_pivots: list[int], resistance_pivots: list[int], out_path: Path, *, title: str) -> None:
    fig, ax = plt.subplots(figsize=(14, 6))
    _plot_base(ax, candles, add_pivots=True, support_pivots=support_pivots, resistance_pivots=resistance_pivots)
    _annotate_pivot_labels(ax, candles, support_pivots, kind='support')
    _annotate_pivot_labels(ax, candles, resistance_pivots, kind='resistance')
    ax.set_title(title)
    ax.grid(alpha=0.2)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_lines(candles: pd.DataFrame, lines: pd.DataFrame, out_path: Path, *, title: str, kind: str, breakout_only: bool = False, non_breakout_only: bool = False, highlight_pointsets: bool = False, top_n: int = 4) -> None:
    fig, ax = plt.subplots(figsize=(14, 6))
    _plot_base(ax, candles)
    _render_line_collection(
        ax,
        candles,
        lines,
        kind=kind,
        breakout_only=breakout_only,
        non_breakout_only=non_breakout_only,
        highlight_pointsets=highlight_pointsets,
        top_n=top_n,
    )

    handles, labels = ax.get_legend_handles_labels()
    seen = set()
    uniq_handles = []
    uniq_labels = []
    for h, l in zip(handles, labels):
        if l not in seen:
            uniq_handles.append(h)
            uniq_labels.append(l)
            seen.add(l)
    ax.set_title(title)
    ax.grid(alpha=0.2)
    if uniq_handles:
        ax.legend(uniq_handles, uniq_labels, loc="upper left")
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)



def _enumerate_raw_candidate_pairs(candles: pd.DataFrame, pivots: list[int], *, kind: str, max_lines: int = 140) -> pd.DataFrame:
    if len(pivots) < 2:
        return pd.DataFrame(columns=['start_idx', 'end_idx', 'span', 'm', 'b'])

    price_col = 'Low' if kind == 'support' else 'High'
    series = candles[price_col].reset_index(drop=True)
    rows = []
    for pos, i in enumerate(pivots):
        for j in pivots[pos + 1:]:
            m, b = np.polyfit([i, j], [series.iloc[i], series.iloc[j]], 1)
            rows.append([i, j, j - i, m, b])

    out = pd.DataFrame(rows, columns=['start_idx', 'end_idx', 'span', 'm', 'b'])
    if len(out) > max_lines:
        out = out.sort_values(['span', 'start_idx', 'end_idx'], ascending=[False, True, True]).reset_index(drop=True)
        take = np.linspace(0, len(out) - 1, max_lines, dtype=int)
        out = out.iloc[np.unique(take)].reset_index(drop=True)
    return out



def plot_candidate_lines_before_filter(candles: pd.DataFrame, support_pivots: list[int], resistance_pivots: list[int], out_path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharey=False)
    x = np.arange(len(candles))
    configs = [
        ('support', support_pivots, '#2563eb'),
        ('resistance', resistance_pivots, '#7c3aed'),
    ]

    for ax, (kind, pivots, color) in zip(axes, configs):
        if kind == 'support':
            _plot_base(ax, candles, add_pivots=True, support_pivots=pivots, resistance_pivots=None)
        else:
            _plot_base(ax, candles, add_pivots=True, support_pivots=None, resistance_pivots=pivots)

        candidates = _enumerate_raw_candidate_pairs(candles, pivots, kind=kind)
        for idx, row in candidates.iterrows():
            start = int(row['start_idx'])
            end = int(row['end_idx'])
            y = row['m'] * x[start:end + 1] + row['b']
            ax.plot(
                x[start:end + 1],
                y,
                color=color,
                linewidth=1.0,
                alpha=0.12,
                zorder=4,
                label=f'{kind} sampled raw candidates' if idx == 0 else None,
            )

        total_pairs = len(pivots) * (len(pivots) - 1) // 2
        shown = len(candidates)
        sampled = 'sampled' if shown < total_pairs else 'all'
        ax.text(
            0.02,
            0.98,
            f'pivots={len(pivots)}\npivot pairs={total_pairs}\nshown={shown} ({sampled})',
            transform=ax.transAxes,
            va='top',
            ha='left',
            fontsize=9,
            bbox=dict(boxstyle='round,pad=0.35', facecolor='white', edgecolor='#cbd5e1', alpha=0.92),
        )
        ax.set_title(f'{kind} candidate pivot-pair segments')
        ax.grid(alpha=0.2)

    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        axes[0].legend(handles, labels, loc='upper left')
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)



def _select_duplicate_group_examples(lines: pd.DataFrame, *, max_groups: int = 3, max_lines_per_group: int = 4) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if lines.empty or 'duplicate_group_id' not in lines.columns:
        empty = pd.DataFrame()
        return empty, empty, empty

    ranked = (
        lines.groupby('duplicate_group_id')
        .agg(group_size=('id', 'count'), best_score=('score', 'max'))
        .reset_index()
        .sort_values(['group_size', 'best_score'], ascending=[False, False])
    )
    ranked = ranked[ranked['group_size'] > 1].head(max_groups).reset_index(drop=True)
    if ranked.empty:
        empty = pd.DataFrame()
        return empty, empty, ranked

    chosen_ids = ranked['duplicate_group_id'].tolist()
    before = (
        lines[lines['duplicate_group_id'].isin(chosen_ids)]
        .sort_values(['duplicate_group_id', 'rank_within_group', 'score'], ascending=[True, True, False])
        .groupby('duplicate_group_id', as_index=False)
        .head(max_lines_per_group)
        .reset_index(drop=True)
    )
    after = before[before['is_best_from_duplicate_group'] == True].reset_index(drop=True)
    return before, after, ranked



def _plot_duplicate_group_panel(ax, candles: pd.DataFrame, lines: pd.DataFrame, *, kind: str, title: str, ranked_groups: pd.DataFrame) -> None:
    _plot_base(ax, candles)
    ax.set_title(title)
    ax.grid(alpha=0.2)
    if lines.empty:
        ax.text(0.5, 0.5, 'No duplicate groups with size > 1', transform=ax.transAxes, ha='center', va='center', fontsize=12)
        return

    x = np.arange(len(candles))
    group_ids = list(dict.fromkeys(lines['duplicate_group_id'].tolist()))
    palette = plt.get_cmap('tab10', max(len(group_ids), 1))
    colors = {gid: palette(i) for i, gid in enumerate(group_ids)}

    for _, row in lines.iterrows():
        fit_start, fit_end, _ = _line_plot_indices(row, total_bars=len(candles))
        y = _line_y(row, x)
        group_id = row['duplicate_group_id']
        color = colors[group_id]
        is_best = bool(row.get('is_best_from_duplicate_group', False))
        ax.plot(
            x[fit_start:fit_end + 1],
            y[fit_start:fit_end + 1],
            color=color,
            linewidth=2.8 if is_best else 1.25,
            alpha=0.95 if is_best else 0.38,
            linestyle='-' if is_best else '--',
            zorder=5,
        )

    ax.text(
        0.02,
        0.98,
        f'groups shown={len(ranked_groups)}\nlines shown={len(lines)}',
        transform=ax.transAxes,
        va='top',
        ha='left',
        fontsize=9,
        bbox=dict(boxstyle='round,pad=0.35', facecolor='white', edgecolor='#cbd5e1', alpha=0.92),
    )



def plot_duplicate_grouping_before_after(candles: pd.DataFrame, support: pd.DataFrame, resistance: pd.DataFrame, out_path: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(16, 10), sharex=False, sharey=False)

    support_before, support_after, support_ranked = _select_duplicate_group_examples(support)
    resistance_before, resistance_after, resistance_ranked = _select_duplicate_group_examples(resistance)

    _plot_duplicate_group_panel(axes[0, 0], candles, support_before, kind='support', title='support duplicate groups · before grouping compression', ranked_groups=support_ranked)
    _plot_duplicate_group_panel(axes[0, 1], candles, support_after, kind='support', title='support duplicate groups · after best-from-group', ranked_groups=support_ranked)
    _plot_duplicate_group_panel(axes[1, 0], candles, resistance_before, kind='resistance', title='resistance duplicate groups · before grouping compression', ranked_groups=resistance_ranked)
    _plot_duplicate_group_panel(axes[1, 1], candles, resistance_after, kind='resistance', title='resistance duplicate groups · after best-from-group', ranked_groups=resistance_ranked)

    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def _analyze_pipeline_side(candles: pd.DataFrame, trendlines_df: pd.DataFrame, pivots: list[int], *, kind: str, config: PyTrendlineConfig) -> dict:
    pytrendline = _ensure_pytrendline_compat()
    detect_mod = importlib.import_module('pytrendline.detect')
    util_mod = importlib.import_module('pytrendline.util')
    structs_mod = importlib.import_module('pytrendline.structs')

    candlestick_data = pytrendline.CandlestickData(
        df=candles,
        time_interval=config.time_interval,
        open_col='Open', high_col='High', low_col='Low', close_col='Close', datetime_col='Date',
    )

    tt = structs_mod.TrendlineTypes.SUPPORT if kind == 'support' else structs_mod.TrendlineTypes.RESISTANCE
    col = 'Low' if kind == 'support' else 'High'
    pseries = candles[col]
    last_index = len(candles) - 1
    last_price = pseries.iloc[last_index]
    avg_candle_range = util_mod.avg_candle_range(candlestick_data)

    max_allowable_slope = detect_mod.DEFAULT_CONFIG['max_allowable_support_slope'](candlestick_data) if kind == 'support' else detect_mod.DEFAULT_CONFIG['max_allowable_resistance_slope'](candlestick_data)
    min_allowable_slope = detect_mod.DEFAULT_CONFIG['min_allowable_support_slope'](candlestick_data) if kind == 'support' else detect_mod.DEFAULT_CONFIG['min_allowable_resistance_slope'](candlestick_data)
    max_allowable_last_price = detect_mod.DEFAULT_CONFIG['max_allowable_support_last_price'](candlestick_data) if kind == 'support' else detect_mod.DEFAULT_CONFIG['max_allowable_resistance_last_price'](candlestick_data)
    min_allowable_last_price = detect_mod.DEFAULT_CONFIG['min_allowable_support_last_price'](candlestick_data) if kind == 'support' else detect_mod.DEFAULT_CONFIG['min_allowable_resistance_last_price'](candlestick_data)
    max_allowable_error_pt_to_trend = detect_mod.DEFAULT_CONFIG['max_allowable_error_pt_to_trend'](candlestick_data)

    pivot_set = set(pivots)
    counts = {
        'pivot_count': len(pivots),
        'pivot_pairs_considered': 0,
        'rejected_slope': 0,
        'rejected_last_price': 0,
        'pass_basic_filters': 0,
        'rejected_min_points': 0,
        'rejected_duplicate_pointset': 0,
        'valid_results_pre_group': 0,
        'breakout_tagged': int(trendlines_df['is_breakout'].sum()) if not trendlines_df.empty and 'is_breakout' in trendlines_df.columns else 0,
        'duplicate_groups': int(trendlines_df['duplicate_group_id'].nunique()) if not trendlines_df.empty and 'duplicate_group_id' in trendlines_df.columns else 0,
        'best_from_group': int(trendlines_df['is_best_from_duplicate_group'].sum()) if not trendlines_df.empty and 'is_best_from_duplicate_group' in trendlines_df.columns else 0,
    }

    pointset_ids = set()
    for i in range(len(pseries)):
        if (config.first_pt_must_be_pivot or config.all_pts_must_be_pivots) and i not in pivot_set:
            continue
        for j in range(i + 1, len(pseries)):
            if (config.last_pt_must_be_pivot or config.all_pts_must_be_pivots) and j not in pivot_set:
                continue
            counts['pivot_pairs_considered'] += 1

            iprice = pseries.iloc[i]
            jprice = pseries.iloc[j]
            m, b = np.polyfit([i, j], [iprice, jprice], 1)
            slope = m * avg_candle_range
            trend_price_at_last = m * last_index + b

            if slope > max_allowable_slope or slope < min_allowable_slope:
                counts['rejected_slope'] += 1
                continue
            if trend_price_at_last > max_allowable_last_price or trend_price_at_last < min_allowable_last_price:
                counts['rejected_last_price'] += 1
                continue
            counts['pass_basic_filters'] += 1

            num_points = 2
            points_in_trendline = [i, j]
            for k in range(i, len(pseries)):
                if config.last_pt_must_be_pivot and k not in pivot_set:
                    continue
                if k == i or k == j:
                    continue
                trend_price_at_k = m * k + b
                if abs(trend_price_at_k - pseries.iloc[k]) < max_allowable_error_pt_to_trend:
                    num_points += 1
                    points_in_trendline.append(k)

            if num_points < config.min_points_required:
                counts['rejected_min_points'] += 1
                continue

            points_in_trendline = sorted(points_in_trendline)
            pointset_id = ('S' if kind == 'support' else 'R') + '-[' + ','.join(str(p) for p in points_in_trendline) + ']'
            if pointset_id in pointset_ids:
                counts['rejected_duplicate_pointset'] += 1
                continue
            pointset_ids.add(pointset_id)
            counts['valid_results_pre_group'] += 1

    counts['non_breakout_valid'] = counts['valid_results_pre_group'] - counts['breakout_tagged']
    return counts


def _build_filter_waterfall_tables(candles: pd.DataFrame, support: pd.DataFrame, resistance: pd.DataFrame, support_pivots: list[int], resistance_pivots: list[int], config: PyTrendlineConfig) -> tuple[pd.DataFrame, pd.DataFrame, dict, dict]:
    support_counts = _analyze_pipeline_side(candles, support, support_pivots, kind='support', config=config)
    resistance_counts = _analyze_pipeline_side(candles, resistance, resistance_pivots, kind='resistance', config=config)

    waterfall = pd.DataFrame([
        ['pivots', support_counts['pivot_count'], resistance_counts['pivot_count'], '进入候选池的结构锚点数量'],
        ['pivot_pairs_considered', support_counts['pivot_pairs_considered'], resistance_counts['pivot_pairs_considered'], '在当前配置下真正被拿来拟合直线的 pivot 对数量'],
        ['pass_basic_filters', support_counts['pass_basic_filters'], resistance_counts['pass_basic_filters'], '通过 slope / last-price 合法性过滤后的候选对数量'],
        ['valid_results_pre_group', support_counts['valid_results_pre_group'], resistance_counts['valid_results_pre_group'], '通过最小命中点数与 pointset 去重之后留下的全部有效结果'],
        ['breakout_tagged', support_counts['breakout_tagged'], resistance_counts['breakout_tagged'], '这些有效结果里被标成 breakout 的数量'],
        ['duplicate_groups', support_counts['duplicate_groups'], resistance_counts['duplicate_groups'], 'duplicate grouping 之后形成的组数'],
        ['best_from_group', support_counts['best_from_group'], resistance_counts['best_from_group'], '页面最终优先展示的代表线数量'],
    ], columns=['stage', 'support_count', 'resistance_count', 'why_it_matters'])

    why_not_all_pairs = pd.DataFrame([
        ['为什么不能把所有 pivot 两两相连后都直接展示', '因为 2 点连线天然太多，而且很多线只是偶然穿过两个点，并不具备足够结构支撑。'],
        ['当前先过滤掉什么', '先过滤 slope 不合法、最后价格位置明显不合理的候选线。'],
        ['真正让一条线“像趋势线”的关键是什么', f'当前至少要求 `num_points >= {config.min_points_required}`，也就是除了起终点外，还要有更多价格点贴近这条线。'],
        ['为什么最后还要 duplicate grouping', '因为不同 pivot 对可能生成几乎重合的线；若不分组，页面会被视觉上重复的线淹没。'],
    ], columns=['question', 'current_answer'])

    return waterfall, why_not_all_pairs, support_counts, resistance_counts


def _build_core_semantics_tables(
    candles: pd.DataFrame,
    config: PyTrendlineConfig,
    *,
    support_counts: dict,
    resistance_counts: dict,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    avg_candle_range = max((candles["High"] - candles["Low"]).mean(), 0.01)
    max_allowable_error_pt_to_trend = avg_candle_range * 0.06
    breakout_tolerance = avg_candle_range * 0.08

    decision_chain = pd.DataFrame(
        [
            [
                1,
                "pivot collection",
                f"先在当前 {len(candles)} 根 K 线窗口里找 support / resistance pivots。",
                f"support={support_counts['pivot_count']}，resistance={resistance_counts['pivot_count']}",
            ],
            [
                2,
                "pivot pair enumeration",
                "只允许 pivot-pair 进入拟合；不是任意两根 bar 都能拿来画线。",
                f"support={support_counts['pivot_pairs_considered']}，resistance={resistance_counts['pivot_pairs_considered']}",
            ],
            [
                3,
                "candidate line fitting",
                "对每个合法 pivot-pair 用两点拟合出一条直线（m / b）。",
                "这是候选线生成层，还不是最终趋势线。",
            ],
            [
                4,
                "validity filtering",
                "先过滤 slope / last-price 不合理的线，再检查有多少点足够贴近该线。",
                f"通过基础过滤后：support={support_counts['pass_basic_filters']}，resistance={resistance_counts['pass_basic_filters']}",
            ],
            [
                5,
                "valid trendline",
                f"只有命中点数达到 `num_points >= {config.min_points_required}` 的线，才进入有效结果池。",
                f"有效结果：support={support_counts['valid_results_pre_group']}，resistance={resistance_counts['valid_results_pre_group']}",
            ],
            [
                6,
                "breakout tagging",
                "对有效线再判断当前窗口里是否已经出现 breakout。",
                f"breakout tagged：support={support_counts['breakout_tagged']}，resistance={resistance_counts['breakout_tagged']}",
            ],
            [
                7,
                "duplicate grouping",
                "把几乎重合的线聚成 group，避免页面被视觉上重复的线淹没。",
                f"duplicate groups：support={support_counts['duplicate_groups']}，resistance={resistance_counts['duplicate_groups']}",
            ],
            [
                8,
                "best-from-group selection",
                "每组最终只保留 score 最好的代表线优先展示。",
                f"best-from-group：support={support_counts['best_from_group']}，resistance={resistance_counts['best_from_group']}",
            ],
        ],
        columns=["step", "stage", "what_happens_now", "current_window_evidence"],
    )

    validity_rules = pd.DataFrame(
        [
            [
                "什么线能进入候选池",
                "start / end 必须来自 pivots。",
                "若起点或终点不是 pivot，在当前配置下会直接跳过。",
            ],
            [
                "什么线能变成有效趋势线",
                f"除了两端外，还要有足够多的点贴近它，当前至少 `num_points >= {config.min_points_required}`。",
                "只靠两点定义出来的线解释力太弱，不进入最终有效结果。",
            ],
            [
                "贴近这条线是什么意思",
                f"价格点到线的误差要小于 `max_allowable_error ≈ {max_allowable_error_pt_to_trend:.4f}`。",
                "误差太大就不算命中，因此不会增加 num_points。",
            ],
            [
                "什么线会在第一层就被淘汰",
                "slope 不合法，或这条线在窗口最后一根 bar 的价格位置明显不合理。",
                "这些线连“基础几何位置”都不成立，所以不会继续参与后续评分。",
            ],
            [
                "breakout 会改变什么",
                f"若价格越线幅度超过 `breakout_tolerance ≈ {breakout_tolerance:.4f}`，这条有效线会被标记为 breakout。",
                "它不是被删除，而是从“静态结构线”变成“已发生事件的结构线”。",
            ],
            [
                "为什么有些线存在却不单独展示",
                "因为 duplicate grouping 会把几乎重合的线放进同一组。",
                "若它不是该组 score 最好的那条，就仍然存在于结果表里，但不会优先画在教学视图上。",
            ],
        ],
        columns=["question", "能成为趋势线的条件", "不能成为或不再单独展示的原因"],
    )
    return decision_chain, validity_rules


def _format_line_example(row: pd.Series, *, side: str, role: str, status: str, why: str) -> dict:
    pointset = _compact_list_str(_parse_index_list(row.get('pointset_indeces')))
    breakout_idx = _safe_int(row.get('breakout_index'))
    concrete_bits = [
        f"line_id={row.get('id')}",
        f"score={float(row.get('score', 0.0)):.2f}",
        f"num_points={int(row.get('num_points', 0))}",
    ]
    if pointset:
        concrete_bits.append(f"pointset=[{pointset}]")
    if breakout_idx is not None:
        concrete_bits.append(f"breakout_index={breakout_idx}")
    if 'duplicate_group_id' in row and not pd.isna(row.get('duplicate_group_id')):
        concrete_bits.append(f"group={int(row.get('duplicate_group_id'))}")
    return {
        'example_role': role,
        'side': side,
        'current_status': status,
        'concrete_case': ' | '.join(concrete_bits),
        'why_this_case_matters': why,
    }


def _collect_rejected_candidate_example(candles: pd.DataFrame, pivots: list[int], *, kind: str, config: PyTrendlineConfig) -> dict | None:
    pytrendline = _ensure_pytrendline_compat()
    detect_mod = importlib.import_module('pytrendline.detect')
    util_mod = importlib.import_module('pytrendline.util')

    candlestick_data = pytrendline.CandlestickData(
        df=candles,
        time_interval=config.time_interval,
        open_col='Open', high_col='High', low_col='Low', close_col='Close', datetime_col='Date',
    )
    pseries = candles['Low'] if kind == 'support' else candles['High']
    last_index = len(candles) - 1
    avg_candle_range = util_mod.avg_candle_range(candlestick_data)
    max_allowable_slope = detect_mod.DEFAULT_CONFIG['max_allowable_support_slope'](candlestick_data) if kind == 'support' else detect_mod.DEFAULT_CONFIG['max_allowable_resistance_slope'](candlestick_data)
    min_allowable_slope = detect_mod.DEFAULT_CONFIG['min_allowable_support_slope'](candlestick_data) if kind == 'support' else detect_mod.DEFAULT_CONFIG['min_allowable_resistance_slope'](candlestick_data)
    max_allowable_last_price = detect_mod.DEFAULT_CONFIG['max_allowable_support_last_price'](candlestick_data) if kind == 'support' else detect_mod.DEFAULT_CONFIG['max_allowable_resistance_last_price'](candlestick_data)
    min_allowable_last_price = detect_mod.DEFAULT_CONFIG['min_allowable_support_last_price'](candlestick_data) if kind == 'support' else detect_mod.DEFAULT_CONFIG['min_allowable_resistance_last_price'](candlestick_data)
    max_allowable_error_pt_to_trend = detect_mod.DEFAULT_CONFIG['max_allowable_error_pt_to_trend'](candlestick_data)

    pivot_set = set(pivots)
    pointset_ids = set()
    fallback = None
    for i in range(len(pseries)):
        if (config.first_pt_must_be_pivot or config.all_pts_must_be_pivots) and i not in pivot_set:
            continue
        for j in range(i + 1, len(pseries)):
            if (config.last_pt_must_be_pivot or config.all_pts_must_be_pivots) and j not in pivot_set:
                continue

            m, b = np.polyfit([i, j], [pseries.iloc[i], pseries.iloc[j]], 1)
            slope = m * avg_candle_range
            trend_price_at_last = m * last_index + b
            anchor_desc = f"pivot_pair=[{i},{j}] | slope={slope:.2f}"

            if slope > max_allowable_slope or slope < min_allowable_slope:
                if fallback is None:
                    fallback = {
                        'example_role': 'Rejected candidate',
                        'side': kind,
                        'current_status': 'rejected at slope filter',
                        'concrete_case': anchor_desc,
                        'why_this_case_matters': '这条 pivot-pair 拟合出来的斜率超出当前允许范围，所以连“基础几何形状”都不成立，直接在第一层被淘汰。',
                    }
                continue
            if trend_price_at_last > max_allowable_last_price or trend_price_at_last < min_allowable_last_price:
                if fallback is None:
                    fallback = {
                        'example_role': 'Rejected candidate',
                        'side': kind,
                        'current_status': 'rejected at last-price filter',
                        'concrete_case': anchor_desc + f" | last_price_on_line={trend_price_at_last:.2f}",
                        'why_this_case_matters': '这条线虽然能穿过起终点，但延伸到窗口末端时位置明显不合理，因此不会进入有效趋势线池。',
                    }
                continue

            num_points = 2
            points_in_trendline = [i, j]
            for k in range(i, len(pseries)):
                if config.last_pt_must_be_pivot and k not in pivot_set:
                    continue
                if k == i or k == j:
                    continue
                trend_price_at_k = m * k + b
                if abs(trend_price_at_k - pseries.iloc[k]) < max_allowable_error_pt_to_trend:
                    num_points += 1
                    points_in_trendline.append(k)

            points_in_trendline = sorted(points_in_trendline)
            pointset_desc = _compact_list_str(points_in_trendline)
            if num_points < config.min_points_required:
                return {
                    'example_role': 'Rejected candidate',
                    'side': kind,
                    'current_status': 'rejected at min-points filter',
                    'concrete_case': f"{anchor_desc} | pointset=[{pointset_desc}] | num_points={num_points}",
                    'why_this_case_matters': f"这条线只命中了 {num_points} 个点，低于当前 `min_points_required={config.min_points_required}`，所以它能被画出来，但还不够资格被当成有效趋势线。",
                }

            pointset_id = ('S' if kind == 'support' else 'R') + '-[' + ','.join(str(p) for p in points_in_trendline) + ']'
            if pointset_id in pointset_ids:
                return {
                    'example_role': 'Rejected candidate',
                    'side': kind,
                    'current_status': 'rejected as duplicate pointset',
                    'concrete_case': f"{anchor_desc} | pointset=[{pointset_desc}]",
                    'why_this_case_matters': '它和前面某条有效线命中了同一组结构点，因此不会重复保留为新的独立结果。',
                }
            pointset_ids.add(pointset_id)

    return fallback


def _build_accepted_rejected_examples(
    candles: pd.DataFrame,
    support: pd.DataFrame,
    resistance: pd.DataFrame,
    support_pivots: list[int],
    resistance_pivots: list[int],
    config: PyTrendlineConfig,
) -> pd.DataFrame:
    frames = []
    if not support.empty:
        frames.append(support.assign(side='support'))
    if not resistance.empty:
        frames.append(resistance.assign(side='resistance'))
    if not frames:
        return pd.DataFrame(columns=['example_role', 'side', 'current_status', 'concrete_case', 'why_this_case_matters'])

    all_lines = pd.concat(frames, ignore_index=True)
    examples: list[dict] = []

    accepted_non_breakout = all_lines[(all_lines['is_best_from_duplicate_group'] == True) & (all_lines['is_breakout'] == False)].sort_values('score', ascending=False).head(1)
    if not accepted_non_breakout.empty:
        row = accepted_non_breakout.iloc[0]
        examples.append(_format_line_example(
            row,
            side=row['side'],
            role='Accepted example',
            status='valid non-breakout representative',
            why='它同时满足有效趋势线条件，而且还是 duplicate group 里的最高分代表线，所以会直接出现在当前教学视图里。',
        ))

    accepted_breakout = all_lines[(all_lines['is_best_from_duplicate_group'] == True) & (all_lines['is_breakout'] == True)].sort_values('score', ascending=False).head(1)
    if not accepted_breakout.empty:
        row = accepted_breakout.iloc[0]
        examples.append(_format_line_example(
            row,
            side=row['side'],
            role='Accepted example',
            status='breakout-tagged representative',
            why='它先是一条有效结构线，随后又被标成 breakout；因此它不会消失，而是会在 Step 4 里以事件线的身份出现。',
        ))

    grouped_not_representative = all_lines[all_lines['is_best_from_duplicate_group'] != True].sort_values('score', ascending=False).head(1)
    if not grouped_not_representative.empty:
        row = grouped_not_representative.iloc[0]
        same_group = all_lines[all_lines['duplicate_group_id'] == row['duplicate_group_id']]
        best_row = same_group[same_group['is_best_from_duplicate_group'] == True].sort_values('score', ascending=False).head(1)
        best_desc = ''
        if not best_row.empty:
            best_desc = f"同组代表线 id={best_row.iloc[0].get('id')} score={float(best_row.iloc[0].get('score', 0.0)):.2f}"
        examples.append(_format_line_example(
            row,
            side=row['side'],
            role='Grouped-away example',
            status='valid but not shown as representative',
            why=('它其实已经是有效趋势线，但因为与另一条线几乎重合，被 duplicate grouping 压进同组；' + best_desc + '，所以页面默认优先展示代表线。').strip('；'),
        ))

    rejected_support = _collect_rejected_candidate_example(candles, support_pivots, kind='support', config=config)
    rejected_resistance = _collect_rejected_candidate_example(candles, resistance_pivots, kind='resistance', config=config)
    rejected_example = rejected_support or rejected_resistance
    if rejected_example is not None:
        examples.append(rejected_example)

    return pd.DataFrame(examples, columns=['example_role', 'side', 'current_status', 'concrete_case', 'why_this_case_matters'])


def _build_line_lifecycle_table(support: pd.DataFrame, resistance: pd.DataFrame, *, support_counts: dict, resistance_counts: dict) -> pd.DataFrame:
    grouped_away_support = int((support['is_best_from_duplicate_group'] != True).sum()) if not support.empty and 'is_best_from_duplicate_group' in support.columns else 0
    grouped_away_resistance = int((resistance['is_best_from_duplicate_group'] != True).sum()) if not resistance.empty and 'is_best_from_duplicate_group' in resistance.columns else 0

    rejected_support = support_counts['rejected_slope'] + support_counts['rejected_last_price'] + support_counts['rejected_min_points'] + support_counts['rejected_duplicate_pointset']
    rejected_resistance = resistance_counts['rejected_slope'] + resistance_counts['rejected_last_price'] + resistance_counts['rejected_min_points'] + resistance_counts['rejected_duplicate_pointset']

    return pd.DataFrame(
        [
            [
                'candidate pivot-pair',
                f"support={support_counts['pivot_pairs_considered']}，resistance={resistance_counts['pivot_pairs_considered']}",
                '只要起点/终点是当前窗口里允许的 pivots，这条线就先进入候选拟合层。此时它只是“可尝试拟合的一条线”，还不是有效结构。',
                '默认不直接展示；只在 filter waterfall 里体现总量。',
            ],
            [
                'rejected before result pool',
                f"support={rejected_support}，resistance={rejected_resistance}",
                '若 slope / last-price 不合法，或 `num_points` 不够，或命中点集合和已有结果重复，就会在进入最终结果池前被淘汰。',
                '默认不单独画图；当前只在 `accepted vs rejected examples` 里抽真实个案做解释。',
            ],
            [
                'valid non-breakout line',
                f"support={support_counts['non_breakout_valid']}，resistance={resistance_counts['non_breakout_valid']}",
                '通过基础过滤与最小命中点数后，且当前窗口里还没有被标成 breakout 的有效结构线。',
                '若它同时是 best-from-group，就会进入 Step 2 / Step 3 教学视图与代表线表。',
            ],
            [
                'breakout-tagged line',
                f"support={support_counts['breakout_tagged']}，resistance={resistance_counts['breakout_tagged']}",
                '它先是一条有效结构线，随后在当前窗口里又被打上 breakout 标签；这改变的是“状态解释”，不是把它从结果池里删除。',
                '会在 Step 4 与结果表里作为事件线继续保留。',
            ],
            [
                'grouped but not representative',
                f"support={grouped_away_support}，resistance={grouped_away_resistance}",
                '这条线本身仍然有效，只是它与别的线几乎重合，duplicate grouping 后没有拿到组内最高分。',
                '保留在 CSV / 原始结果里，但默认不优先画进教学图。',
            ],
            [
                'best-from-group representative',
                f"support={support_counts['best_from_group']}，resistance={resistance_counts['best_from_group']}",
                '这是 duplicate group 里 score 最好的代表线，属于页面默认最该先看的那一小部分。',
                '会优先出现在 Step 2 / Step 3 / Step 4 与 Best lines 表里。',
            ],
            [
                'expired / invalidated state?',
                '当前页面：未单独建模',
                '这页目前没有“线后来彻底失效、从结果里退休”的单独生命周期状态；当前实现一旦识别到 breakout，更接近把它保留成带事件标签的研究对象。',
                '因此页面更像“窗口末端回头看的一张状态快照”，而不是 bar-by-bar 的存活/退场审计。',
            ],
        ],
        columns=['lifecycle_state', 'current_window_evidence', 'what_it_means_now', 'how_it_shows_up_in_report'],
    )


def _line_lifecycle_state_diagram_svg() -> str:
    return """<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"1200\" height=\"520\" viewBox=\"0 0 1200 520\" role=\"img\" aria-label=\"pytrendline line lifecycle state diagram\">
  <defs>
    <marker id=\"arrow\" markerWidth=\"10\" markerHeight=\"10\" refX=\"9\" refY=\"5\" orient=\"auto-start-reverse\">
      <path d=\"M0,0 L10,5 L0,10 z\" fill=\"#475569\" />
    </marker>
  </defs>
  <rect x=\"0\" y=\"0\" width=\"1200\" height=\"520\" rx=\"20\" fill=\"#ffffff\" />

  <rect x=\"40\" y=\"160\" width=\"190\" height=\"90\" rx=\"14\" fill=\"#eff6ff\" stroke=\"#2563eb\" stroke-width=\"2\" />
  <text x=\"135\" y=\"192\" font-size=\"22\" text-anchor=\"middle\" fill=\"#1e3a8a\" font-family=\"Arial, sans-serif\">candidate</text>
  <text x=\"135\" y=\"220\" font-size=\"16\" text-anchor=\"middle\" fill=\"#1e3a8a\" font-family=\"Arial, sans-serif\">pivot-pair enters fitting layer</text>

  <rect x=\"320\" y=\"55\" width=\"230\" height=\"90\" rx=\"14\" fill=\"#fef2f2\" stroke=\"#dc2626\" stroke-width=\"2\" />
  <text x=\"435\" y=\"88\" font-size=\"22\" text-anchor=\"middle\" fill=\"#991b1b\" font-family=\"Arial, sans-serif\">rejected</text>
  <text x=\"435\" y=\"115\" font-size=\"16\" text-anchor=\"middle\" fill=\"#991b1b\" font-family=\"Arial, sans-serif\">slope / last-price / min-points</text>

  <rect x=\"320\" y=\"265\" width=\"230\" height=\"90\" rx=\"14\" fill=\"#ecfeff\" stroke=\"#0891b2\" stroke-width=\"2\" />
  <text x=\"435\" y=\"298\" font-size=\"22\" text-anchor=\"middle\" fill=\"#0f766e\" font-family=\"Arial, sans-serif\">valid result</text>
  <text x=\"435\" y=\"325\" font-size=\"16\" text-anchor=\"middle\" fill=\"#0f766e\" font-family=\"Arial, sans-serif\">enters final result pool</text>

  <rect x=\"620\" y=\"95\" width=\"230\" height=\"90\" rx=\"14\" fill=\"#eef2ff\" stroke=\"#4f46e5\" stroke-width=\"2\" />
  <text x=\"735\" y=\"128\" font-size=\"22\" text-anchor=\"middle\" fill=\"#3730a3\" font-family=\"Arial, sans-serif\">valid non-breakout</text>
  <text x=\"735\" y=\"155\" font-size=\"16\" text-anchor=\"middle\" fill=\"#3730a3\" font-family=\"Arial, sans-serif\">still a structure line</text>

  <rect x=\"620\" y=\"265\" width=\"230\" height=\"90\" rx=\"14\" fill=\"#f0fdf4\" stroke=\"#16a34a\" stroke-width=\"2\" />
  <text x=\"735\" y=\"298\" font-size=\"22\" text-anchor=\"middle\" fill=\"#166534\" font-family=\"Arial, sans-serif\">breakout tagged</text>
  <text x=\"735\" y=\"325\" font-size=\"16\" text-anchor=\"middle\" fill=\"#166534\" font-family=\"Arial, sans-serif\">same line, now event-labeled</text>

  <rect x=\"930\" y=\"85\" width=\"220\" height=\"90\" rx=\"14\" fill=\"#fff7ed\" stroke=\"#f97316\" stroke-width=\"2\" />
  <text x=\"1040\" y=\"118\" font-size=\"21\" text-anchor=\"middle\" fill=\"#9a3412\" font-family=\"Arial, sans-serif\">best-from-group</text>
  <text x=\"1040\" y=\"145\" font-size=\"16\" text-anchor=\"middle\" fill=\"#9a3412\" font-family=\"Arial, sans-serif\">default representative</text>

  <rect x=\"930\" y=\"275\" width=\"220\" height=\"90\" rx=\"14\" fill=\"#faf5ff\" stroke=\"#7c3aed\" stroke-width=\"2\" />
  <text x=\"1040\" y=\"308\" font-size=\"21\" text-anchor=\"middle\" fill=\"#5b21b6\" font-family=\"Arial, sans-serif\">grouped away</text>
  <text x=\"1040\" y=\"335\" font-size=\"16\" text-anchor=\"middle\" fill=\"#5b21b6\" font-family=\"Arial, sans-serif\">still valid, not default shown</text>

  <line x1=\"230\" y1=\"175\" x2=\"320\" y2=\"110\" stroke=\"#475569\" stroke-width=\"3\" marker-end=\"url(#arrow)\" />
  <line x1=\"230\" y1=\"235\" x2=\"320\" y2=\"310\" stroke=\"#475569\" stroke-width=\"3\" marker-end=\"url(#arrow)\" />
  <line x1=\"550\" y1=\"310\" x2=\"620\" y2=\"140\" stroke=\"#475569\" stroke-width=\"3\" marker-end=\"url(#arrow)\" />
  <line x1=\"550\" y1=\"310\" x2=\"620\" y2=\"310\" stroke=\"#475569\" stroke-width=\"3\" marker-end=\"url(#arrow)\" />
  <line x1=\"850\" y1=\"140\" x2=\"930\" y2=\"130\" stroke=\"#475569\" stroke-width=\"3\" marker-end=\"url(#arrow)\" />
  <line x1=\"850\" y1=\"150\" x2=\"930\" y2=\"310\" stroke=\"#475569\" stroke-width=\"3\" marker-end=\"url(#arrow)\" />
  <line x1=\"850\" y1=\"300\" x2=\"930\" y2=\"130\" stroke=\"#475569\" stroke-width=\"3\" marker-end=\"url(#arrow)\" />
  <line x1=\"850\" y1=\"320\" x2=\"930\" y2=\"320\" stroke=\"#475569\" stroke-width=\"3\" marker-end=\"url(#arrow)\" />

  <text x=\"285\" y=\"115\" font-size=\"14\" fill=\"#334155\" font-family=\"Arial, sans-serif\">fails filters</text>
  <text x=\"270\" y=\"285\" font-size=\"14\" fill=\"#334155\" font-family=\"Arial, sans-serif\">passes min-points</text>
  <text x=\"575\" y=\"205\" font-size=\"14\" fill=\"#334155\" font-family=\"Arial, sans-serif\">no breakout</text>
  <text x=\"575\" y=\"345\" font-size=\"14\" fill=\"#334155\" font-family=\"Arial, sans-serif\">breakout detected</text>
  <text x=\"883\" y=\"115\" font-size=\"14\" fill=\"#334155\" font-family=\"Arial, sans-serif\">wins group</text>
  <text x=\"884\" y=\"226\" font-size=\"14\" fill=\"#334155\" font-family=\"Arial, sans-serif\">loses group</text>

  <rect x=\"300\" y=\"420\" width=\"600\" height=\"58\" rx=\"12\" fill=\"#f8fafc\" stroke=\"#cbd5e1\" stroke-width=\"1.5\" />
  <text x=\"600\" y=\"448\" font-size=\"17\" text-anchor=\"middle\" fill=\"#334155\" font-family=\"Arial, sans-serif\">Note: current report has no separate expired / retired state.</text>
  <text x=\"600\" y=\"470\" font-size=\"15\" text-anchor=\"middle\" fill=\"#475569\" font-family=\"Arial, sans-serif\">After breakout, the line is kept as a research event line rather than aged out bar-by-bar.</text>
</svg>"""


def _build_time_semantics_table(candles: pd.DataFrame, *, support_counts: dict, resistance_counts: dict) -> pd.DataFrame:
    return pd.DataFrame(
        [
            [
                '当前页面整体视角',
                '窗口末端重新扫描后的回看快照',
                f"当前整页是对最近 {len(candles)} 根 bar 一次性重算后的结果汇总，而不是当时逐根 bar 在线更新的状态日志。",
                '最适合做结构解释 / 方法对照，不应直接当成实时信号审计结果。',
            ],
            [
                '原始 OHLC bars',
                '每根 bar 收盘后即可视为已知',
                '历史 K 线本身没有未来函数；一旦 bar 收完，OHLC 就能被当作当时已知的数据。',
                '所以图上的价格历史可以当基础事实，但后面的结构标签不一定能同一时点同步知道。',
            ],
            [
                'pivot 身份',
                '需要右侧若干根 bar 之后才能确认',
                '局部高/低点要和后面的 bars 比较，因此 pivot 的时间戳落在过去，但“它是 pivot”这件事带事后视角。',
                '可把 pivot 当成研究锚点；若要实时使用，必须单独审计确认时点。',
            ],
            [
                'candidate / valid line',
                '晚于 pivot 确认之后',
                f"候选线要先完成 pivot-pair 枚举，再经过基础过滤与 `num_points` 检查；当前窗口最终留下 support={support_counts['valid_results_pre_group']}、resistance={resistance_counts['valid_results_pre_group']} 条有效结果。",
                '因此页面里的线更接近“窗口末端重新回头看得到的结构对象”，不是当时逐 bar 持有的线集合。',
            ],
            [
                '`num_points` / `pointset_indeces`',
                '候选线扫描完后才稳定',
                '这些字段依赖整条线在窗口内命中了哪些点；它们更像结构解释字段，而不是实时逐根累加日志。',
                '适合解释“这条线为什么成立”，不应直接解读为交易时当场已知的完整证据。',
            ],
            [
                '`is_breakout` / `breakout_index` / `breakout_date`',
                '事件 bar 出现后，且在窗口扫描时统一打标',
                f"当前窗口里被标成 breakout 的有效结果：support={support_counts['breakout_tagged']}、resistance={resistance_counts['breakout_tagged']}。事件 bar 可以定位到历史某一根，但标签本身是整窗扫描后给出的研究标记。",
                '可用来解释“哪根 bar 触发了 breach”，但还不是经过 bar-by-bar 审计的正式实时触发器。',
            ],
            [
                '`duplicate_group_id` / `is_best_from_duplicate_group`',
                '窗口末端的展示压缩层',
                f"这些字段是为了把近似重合线压缩成更可读的代表线；当前 duplicate groups：support={support_counts['duplicate_groups']}、resistance={resistance_counts['duplicate_groups']}。",
                '它们更像报告页面的阅读辅助状态，而不是交易执行时序状态。',
            ],
            [
                'expired / retired state',
                '当前未单独建模',
                '当前页面会把 breakout 后的线保留为研究事件线，而不是继续追踪它何时完全失效、退场或被替换。',
                '如果后面要做正式 signal engine，需要另建 bar-by-bar state machine 来定义进入、确认、失效与退场。',
            ],
        ],
        columns=['object_or_field', 'when_it_can_be_treated_as_known', 'why_this_has_hindsight_or_delay', 'how_to_read_it_in_this_report'],
    )



def _pick_deep_dive_row(df: pd.DataFrame) -> pd.Series | None:
    if df.empty:
        return None
    work = df.copy()
    if 'duplicate_group_id' in work.columns:
        group_sizes = work.groupby('duplicate_group_id').size().rename('group_size')
        work = work.merge(group_sizes, on='duplicate_group_id', how='left')
    else:
        work['group_size'] = 1

    if 'is_best_from_duplicate_group' in work.columns:
        best = work[work['is_best_from_duplicate_group'] == True].copy()
    else:
        best = work.copy()

    if best.empty:
        best = work.copy()

    multi = best[best['group_size'] > 1].copy()
    target = multi if not multi.empty else best
    return target.sort_values(['score', 'num_points'], ascending=[False, False]).iloc[0]


def _build_selected_line_deep_dive_tables(candles: pd.DataFrame, df: pd.DataFrame, *, kind: str, config: PyTrendlineConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    if df.empty:
        return pd.DataFrame(columns=['aspect', 'current_window_answer']), pd.DataFrame(columns=['id', 'score', 'num_points', 'rank_within_group', 'is_breakout', 'pointset_indeces'])

    row = _pick_deep_dive_row(df)
    if row is None:
        return pd.DataFrame(columns=['aspect', 'current_window_answer']), pd.DataFrame(columns=['id', 'score', 'num_points', 'rank_within_group', 'is_breakout', 'pointset_indeces'])

    pytrendline = _ensure_pytrendline_compat()
    detect_mod = importlib.import_module('pytrendline.detect')
    util_mod = importlib.import_module('pytrendline.util')
    candlestick_data = pytrendline.CandlestickData(
        df=candles,
        time_interval=config.time_interval,
        open_col='Open', high_col='High', low_col='Low', close_col='Close', datetime_col='Date',
    )
    avg_candle_range = util_mod.avg_candle_range(candlestick_data)
    last_index = len(candles) - 1
    trend_price_at_last = float(row['m']) * last_index + float(row['b'])
    normalized_slope = float(row['m']) * avg_candle_range

    if kind == 'support':
        min_slope = detect_mod.DEFAULT_CONFIG['min_allowable_support_slope'](candlestick_data)
        max_slope = detect_mod.DEFAULT_CONFIG['max_allowable_support_slope'](candlestick_data)
        min_last = detect_mod.DEFAULT_CONFIG['min_allowable_support_last_price'](candlestick_data)
        max_last = detect_mod.DEFAULT_CONFIG['max_allowable_support_last_price'](candlestick_data)
        event_price_col = 'Low'
    else:
        min_slope = detect_mod.DEFAULT_CONFIG['min_allowable_resistance_slope'](candlestick_data)
        max_slope = detect_mod.DEFAULT_CONFIG['max_allowable_resistance_slope'](candlestick_data)
        min_last = detect_mod.DEFAULT_CONFIG['min_allowable_resistance_last_price'](candlestick_data)
        max_last = detect_mod.DEFAULT_CONFIG['max_allowable_resistance_last_price'](candlestick_data)
        event_price_col = 'High'

    point_idxs = _parse_index_list(row.get('pointset_indeces'))
    point_dates = _parse_timestamp_list(row.get('pointset_dates'))
    point_desc = ', '.join(f"{i}@{t}" for i, t in zip(point_idxs, point_dates)) if point_idxs and point_dates else _compact_list_str(point_idxs)

    same_group = df[df['duplicate_group_id'] == row['duplicate_group_id']].copy() if 'duplicate_group_id' in df.columns else df.copy()
    same_group = same_group.sort_values('score', ascending=False).copy()
    if 'pointset_indeces' in same_group.columns:
        same_group['pointset_indeces'] = same_group['pointset_indeces'].apply(lambda v: _compact_list_str(_parse_index_list(v)))
    peer_cols = [c for c in ['id', 'score', 'num_points', 'rank_within_group', 'is_breakout', 'pointset_indeces'] if c in same_group.columns]
    peer_table = same_group[peer_cols].reset_index(drop=True)

    if len(same_group) > 1:
        runner_up = same_group.iloc[1]
        best_from_group_text = f"group={int(row['duplicate_group_id'])}，共 {len(same_group)} 条近似线；当前这条 `score={float(row['score']):.2f}` 高于同组第二名 `{runner_up['id']}` 的 `score={float(runner_up['score']):.2f}`，所以它是默认代表线。"
        why_selected = '它不是全窗口绝对最高分线，而是“同组不止 1 条时”里最适合教学展开的代表线：既能讲结构点，也能具体解释 best-from-group 是怎么赢出来的。'
    else:
        best_from_group_text = f"group={int(row['duplicate_group_id'])} 里当前只有它 1 条线，因此它自然成为该组代表线。" if 'duplicate_group_id' in row and not pd.isna(row.get('duplicate_group_id')) else '当前没有可对照的同组近似线。'
        why_selected = '当前窗口里适合作为代表线展开的候选不多，所以这里退化为该侧 score 最高的代表线。'

    breakout_idx = _safe_int(row.get('breakout_index'))
    breakout_text = '当前未被标成 breakout。'
    if breakout_idx is not None and 0 <= breakout_idx < len(candles):
        event_bar = candles.iloc[breakout_idx]
        event_ts = pd.to_datetime(event_bar['Date'], utc=True).strftime('%m-%d %H:%M')
        breakout_text = (
            f"breakout_index={breakout_idx}（{event_ts} UTC） | "
            f"Open={float(event_bar['Open']):.2f}, High={float(event_bar['High']):.2f}, Low={float(event_bar['Low']):.2f}, Close={float(event_bar['Close']):.2f} | "
            f"{event_price_col} 是当前侧 breakout 判定更直接参考的价格列。"
        )

    detail = pd.DataFrame(
        [
            ['为什么选这条', why_selected],
            ['line id / side', f"{row['id']} / {kind}"],
            ['命中的 pivots', point_desc],
            ['m / b', f"m={float(row['m']):.6f}，b={float(row['b']):.6f}；也就是 `trend_price = m * bar_index + b`。"],
            ['num_points', f"{int(row['num_points'])}（当前阈值是 >= {config.min_points_required}）"],
            ['为什么通过 slope filter', f"归一化 slope ≈ {normalized_slope:.4f}，落在允许区间 [{min_slope:.4f}, {max_slope:.4f}] 内。"],
            ['为什么通过 last-price filter', f"线在窗口最后一根 bar 上的价格 ≈ {trend_price_at_last:.2f}，落在允许区间 [{min_last:.2f}, {max_last:.2f}] 内。"],
            ['为什么是 best-from-group', best_from_group_text],
            ['breakout 事件 bar', breakout_text],
        ],
        columns=['aspect', 'current_window_answer'],
    )
    return detail, peer_table


def plot_filter_waterfall(waterfall: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 5.8))
    stages = waterfall['stage'].tolist()
    x = np.arange(len(stages))
    width = 0.36
    ax.bar(x - width/2, waterfall['support_count'], width=width, color='#2563eb', label='support')
    ax.bar(x + width/2, waterfall['resistance_count'], width=width, color='#7c3aed', label='resistance')
    ax.set_xticks(x)
    ax.set_xticklabels(stages, rotation=20, ha='right')
    ax.set_ylabel('count')
    ax.set_title('PyTrendline filter waterfall (current window)')
    ax.grid(axis='y', alpha=0.2)
    ax.legend(loc='upper right')
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def build_summary_tables(candles: pd.DataFrame, config: PyTrendlineConfig, support: pd.DataFrame, resistance: pd.DataFrame, support_pivots: list[int], resistance_pivots: list[int], *, ticker: str, period: str, interval: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    params = pd.DataFrame(
        [
            ["ticker", ticker],
            ["period", period],
            ["interval", interval],
            ["window_bars", config.window_bars],
            ["min_points_required", config.min_points_required],
            ["ignore_breakouts", config.ignore_breakouts],
            ["all_pts_must_be_pivots", config.all_pts_must_be_pivots],
        ],
        columns=["parameter", "value"],
    )

    avg_candle_range = max((candles["High"] - candles["Low"]).mean(), 0.01)
    separation_threshold = avg_candle_range * 0.2
    grouping_threshold = avg_candle_range * 0.1

    window_semantics = pd.DataFrame(
        [
            ["period", "从数据源下载多长历史，用于拿到候选样本池。"],
            ["interval", "单根 bar 的时间粒度；它决定 pivot 密度、斜率尺度与图上噪声水平。"],
            ["window_bars", "真正送进 pytrendline 扫描的最近窗口长度；当前报告只对最近窗口做研究，而不是对整段历史全量扫描。"],
            ["为什么只看最近窗口", "因为 pytrendline 是高复杂度穷举搜索；最近窗口更适合 inspection / explainability，而不是实时全量引擎。"],
        ],
        columns=["concept", "operational_definition"],
    )

    steps = pd.DataFrame(
        [
            [1, "取 bars", "先下载 `period × interval` 的 OHLCV，再只保留最近 `window_bars` 根。"],
            [2, "找 pivots", "pytrendline 在窗口内给出 support pivots / resistance pivots；它们是原始 K 线高低点层面的结构锚点。"],
            [3, "枚举候选线", "从 pivots 组合中尝试构造 support / resistance trendlines。"],
            [4, "筛选合法线", "受 `min_points_required`、pivot 约束、breakout 约束等条件过滤。"],
            [5, "重复线分组", "把非常相似的线放在一起，保留每组 best line 便于阅读。"],
            [6, "标记 breakout", "对最终线判断是否已发生 breakout；当前更偏研究标记，不直接等价于可交易信号。"],
        ],
        columns=["step", "name", "operational_definition"],
    )

    counts = pd.DataFrame(
        [
            ["bars_in_window", len(candles)],
            ["support_pivots", len(support_pivots)],
            ["resistance_pivots", len(resistance_pivots)],
            ["support_lines_all", int(len(support))],
            ["resistance_lines_all", int(len(resistance))],
            ["support_lines_best", int(len(_best_lines(support, top_n=len(support))))],
            ["resistance_lines_best", int(len(_best_lines(resistance, top_n=len(resistance))))],
            ["support_breakouts", int(support["is_breakout"].sum()) if not support.empty and "is_breakout" in support.columns else 0],
            ["resistance_breakouts", int(resistance["is_breakout"].sum()) if not resistance.empty and "is_breakout" in resistance.columns else 0],
        ],
        columns=["metric", "value"],
    )

    glossary = pd.DataFrame(
        [
            ["m", "趋势线斜率；正值表示线向上倾斜，负值表示线向下倾斜。"],
            ["b", "截距；与 `m` 一起决定整条线在窗口内的价格位置。"],
            ["num_points", "这条线命中的结构点数量；通常越多，解释性越强。"],
            ["score", "pytrendline 对该线的排序分数；用于同类候选线比较，不应被误读为未来收益分数。"],
            ["starts_at_date / ends_at_date", "当前结果里该线覆盖的起止时间；用于说明线段在图上的定义区间。"],
            ["is_best_from_duplicate_group", "该线是否是相似线分组里的代表线。"],
            ["is_breakout", "该线在当前窗口里被标记为已发生 breakout；更像研究标签，不直接等于可实时交易信号。"],
            ["pointset_indeces / pointset_dates", "这条线命中的结构点索引与对应时间；用于把图上的白心圆点和表格里的锚点信息直接对上。"],
            ["breakout_index / breakout_date", "breakout 事件第一次被识别到的 bar 索引与日期；本地 bridge 会把日期对齐到真实 breakout bar。"],
        ],
        columns=["field", "operational_definition"],
    )

    boundaries = pd.DataFrame(
        [
            ["当前适合什么", "报告阅读、结构 inspection、外部方法对照、后续 parallel channel 研究输入。"],
            ["当前不适合什么", "直接当正式 signal engine、全量长样本高频扫描、未经 bar-by-bar 审计就上实盘。"],
            ["为什么不是正式信号", "因为 pivot / line / breakout 的最终结果更偏研究对象；是否能 bar-by-bar 使用，还需额外做因果审计。"],
            ["和 parallel channel 的关系", "它已经覆盖了 pivot → line → breakout 这半条链，但还没解决“双边平行约束 + 通道宽度 + 多周期共振”完整问题。"],
        ],
        columns=["question", "answer"],
    )

    parameter_rationale = pd.DataFrame(
        [
            ["window_bars = 96", "在 5m 粒度下约等于最近 8 小时。", "比 48 更不容易只看到局部噪声，比 144 更能控制 O(N^3) 穷举成本与页面可读性。"],
            ["min_points_required = 3", "要求一条线至少命中 3 个结构点。", "比 2 点连线更严格；2 点几乎总能画线，但解释力偏弱，3 点更适合作为研究报告里的代表线基线。"],
            ["all_pts_must_be_pivots = True", "要求命中的点都来自已识别的 pivots。", "牺牲部分灵活性，换来更清晰的结构语义；这样页面里的线更容易和锚点一一对照。"],
            ["ignore_breakouts = False", "保留 breakout 检测，而不是只保留静态结构线。", "这样报告既能展示结构线，也能区分哪些线已经被标成事件线，方便后续研究 breakout 语义。"],
        ],
        columns=["parameter_choice", "operational_meaning", "why_this_is_current_default"],
    )

    pivot_logic = pd.DataFrame(
        [
            ["support pivots 看哪里", "在原始 `Low` 序列上找局部低点。", "不是平滑曲线上的点，而是窗口内原始 K 线低点。"],
            ["resistance pivots 看哪里", "在原始 `High` 序列上找局部高点。", "同样直接使用原始 K 线高点。"],
            ["grouping threshold", f"≈ {grouping_threshold:.4f}", "若相邻若干根高/低点差异很小，会先被视作一组近似连续 pivots，再拿更远的前后点比较。"],
            ["separation threshold", f"≈ {separation_threshold:.4f}", "候选 pivot 需要和前后比较点拉开足够距离，避免把太小的局部抖动也当成结构点。"],
            ["局部极值条件", "support 要比前后低；resistance 要比前后高。", "源码里先检查局部高/低，再检查是否达到 separation 要求。"],
            ["首尾 bar", "窗口的 first / last index 总会被纳入 pivots。", "这样趋势线搜索不会完全失去窗口边界上的锚点。"],
            ["bar-by-bar 边界", "pivot 判断会看右侧若干根 bar。", "因此它更适合研究解释；若要实时使用，还需要额外审计“何时才算确认”这件事。"],
        ],
        columns=["rule", "current_window_value_or_logic", "why_it_matters"],
    )

    support_pair_count = len(support_pivots) * (len(support_pivots) - 1) // 2
    resistance_pair_count = len(resistance_pivots) * (len(resistance_pivots) - 1) // 2
    max_allowable_error_pt_to_trend = avg_candle_range * 0.06
    breakout_tolerance = avg_candle_range * 0.08

    candidate_logic = pd.DataFrame(
        [
            ["起点/终点从哪来", "在当前配置下，start/end 都必须来自 pivots。", "因为 `all_pts_must_be_pivots=True`，所以非 pivot 的 i/j 组合会直接跳过。"],
            ["support 候选对数量（理论上限）", str(support_pair_count), "这是当前窗口里 support pivots 两两配对的理论上限。"],
            ["resistance 候选对数量（理论上限）", str(resistance_pair_count), "这是当前窗口里 resistance pivots 两两配对的理论上限。"],
            ["每个候选对先做什么", "先用两个点拟合一条直线（`m`, `b`）。", "源码对每个 i<j 的 pivot pair 先做 `polyfit`。"],
            ["第一层过滤", "先过滤 slope 与 last-price 不合理的线。", "避免生成方向/位置明显不合要求的候选线。"],
            ["第二层过滤", f"再扫描从起点到窗口末尾的 bars，用 `max_allowable_error ≈ {max_allowable_error_pt_to_trend:.4f}` 统计有多少点贴近这条线。", "只有足够多的点贴着线，这条线才算有结构支撑。"],
            ["最小命中数", f"至少需要 `num_points >= {config.min_points_required}`。", "当前默认值是 3，因此只有 2 点撑起来的线不会进入最终结果。"],
            ["breakout 检测", f"如果价格越过线并超过 `breakout_tolerance ≈ {breakout_tolerance:.4f}`，就会标记 breakout。", "这一步决定它只是结构线，还是已经被标成事件线。"],
            ["去重前的重复来源", "不同 pivot 对可能收敛到几乎同一条线。", "所以后面还需要 duplicate grouping，而不是把所有近似重合线都展示出来。"],
            ["当前窗口最终保留", f"support all={len(support)}，resistance all={len(resistance)}", "这是通过最小命中数 / slope / last-price / breakout 规则后留下来的全部候选结果数。"],
        ],
        columns=["question", "current_answer", "why_it_matters"],
    )

    candidate_quality = pd.DataFrame(
        [
            ["`num_points` 怎么读", "它表示有多少个价格点足够贴近这条线。", "不是交易次数，而是结构支撑强度的粗略代理。"],
            ["为什么 2 点不够", "2 点几乎总能定义一条直线。", "如果只用 2 点，页面会充满解释力很弱的偶然连线。"],
            ["为什么还需要 `score`", "命中点数量相同的线，和价格贴合误差可能不同。", "`score` 让我们在同类线中优先看更贴近、点数更多的线。"],
        ],
        columns=["question", "current_answer", "why_it_matters"],
    )

    support_dup_overview, support_dup_groups = _duplicate_group_stats(support, label="support", avg_candle_range=avg_candle_range)
    resistance_dup_overview, resistance_dup_groups = _duplicate_group_stats(resistance, label="resistance", avg_candle_range=avg_candle_range)

    breakout_logic = pd.DataFrame(
        [
            ["support breakout 是什么", f"当 support 线在某个 bar 上方，且 `trend_price > Low + tolerance`。", "当前更接近 low-based breach，而不是 close-based cross。"],
            ["resistance breakout 是什么", f"当 resistance 线在某个 bar 下方，且 `trend_price < High - tolerance`。", "当前更接近 high-based breach，而不是 close-based cross。"],
            ["当前 tolerance", f"≈ {avg_candle_range * 0.08:.4f}", "源码用 `breakout_tolerance = avg_candle_range * 0.08`，避免太小的穿越也被标成 breakout。"],
            ["事件发生时点", "源码先记录 `breakout_index`，本地 bridge 会据此修正 `breakout_date` 到真实事件 bar。", "这样报告里的 breakout 日期就不再误指向起始锚点日期。"],
            ["实时可用性边界", "它是基于当前窗口扫描结果打出来的研究标签。", "可用于理解结构被突破了没有，但不能直接等同于已经审计过的实时交易信号。"],
        ],
        columns=["question", "current_answer", "why_it_matters"],
    )

    return params, window_semantics, steps, counts, glossary, boundaries, parameter_rationale, pivot_logic, candidate_logic, candidate_quality, support_dup_overview, resistance_dup_overview, support_dup_groups, resistance_dup_groups, breakout_logic


def build_html(*, ticker: str, period: str, interval: str, config: PyTrendlineConfig, support: pd.DataFrame, resistance: pd.DataFrame, support_pivots: list[int], resistance_pivots: list[int], candles: pd.DataFrame, artifacts_rel: str) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    support_show = _prepare_display_lines(support, top_n=12)
    resistance_show = _prepare_display_lines(resistance, top_n=12)

    params, window_semantics, steps, counts, glossary, boundaries, parameter_rationale, pivot_logic, candidate_logic, candidate_quality, support_dup_overview, resistance_dup_overview, support_dup_groups, resistance_dup_groups, breakout_logic = build_summary_tables(
        candles, config, support, resistance, support_pivots, resistance_pivots, ticker=ticker, period=period, interval=interval
    )
    filter_waterfall, why_not_all_pairs, support_pipeline_counts, resistance_pipeline_counts = _build_filter_waterfall_tables(
        candles, support, resistance, support_pivots, resistance_pivots, config
    )
    decision_chain, validity_rules = _build_core_semantics_tables(
        candles,
        config,
        support_counts=support_pipeline_counts,
        resistance_counts=resistance_pipeline_counts,
    )
    accepted_rejected_examples = _build_accepted_rejected_examples(
        candles,
        support,
        resistance,
        support_pivots,
        resistance_pivots,
        config,
    )
    line_lifecycle = _build_line_lifecycle_table(
        support,
        resistance,
        support_counts=support_pipeline_counts,
        resistance_counts=resistance_pipeline_counts,
    )
    time_semantics = _build_time_semantics_table(
        candles,
        support_counts=support_pipeline_counts,
        resistance_counts=resistance_pipeline_counts,
    )
    baseline_status = pd.DataFrame(
        [
            ['当前阶段', 'explainability baseline v1（可冻结的研究解释页）', '当前目标是把结构识别、候选线生成、duplicate grouping、breakout 标签与时间语义讲清楚，而不是直接给出可交易结论。'],
            ['它最适合做什么', '结构解释 / 外部方法映射 / 后续 foundation report 的前置教材', '后续 `trendline_event_foundation_report` 可以直接复用这里的 line lifecycle、candidate explosion、grouping 压缩与 breakout 语义。'],
            ['它当前不是什么', '正式交易信号 / bar-by-bar 审计引擎 / 最终收益证明', '如果读者想知道 event 是否有 alpha / feature 价值，需要进入下一阶段的 event foundation，而不是直接从这页跳到策略结论。'],
        ],
        columns=['status_question', 'current_answer', 'why_it_matters'],
    )
    trust_vs_overread = pd.DataFrame(
        [
            ['当前我应该相信什么', '这页已经能可靠说明：pytrendline 怎样从 pivots 走到 candidate lines、怎样过滤、怎样 grouping、怎样把部分结构线标成 breakout 事件线。'],
            ['当前不该过度解读什么', '不要把 `is_breakout=True` 直接读成“可追的突破信号”，也不要把高 `score` 直接读成“更高收益线”；这页解释的是结构对象，不是经过事件验证后的交易规则。'],
            ['当前最合理的使用方式', '把它当成 trendline / support-resistance 结构语义的基线页：先确认定义清楚，再去审计 slope、confirmation、feature value。'],
        ],
        columns=['judgement', 'current_take'],
    )
    next_step_guidance = pd.DataFrame(
        [
            [1, '进入 `trendline_event_foundation_report`', '把当前页面里的结构线对象转成 event taxonomy、confirmation ladder、slope buckets 与 go/no-go 审计。'],
            [2, '先做事件研究，再做策略', '优先比较 breakout vs rebound、raw vs confirmed、不同 slope bucket 的差异，而不是马上追求完整策略收益最大化。'],
            [3, 'parallel channel 暂时保持候选分支', '只有当 trendline event foundation 给出明确正面证据、且 channel 定义足够清晰时，再把它升回高优先级。'],
        ],
        columns=['priority', 'next_step', 'why_now'],
    )
    support_deep_dive, support_deep_dive_group = _build_selected_line_deep_dive_tables(
        candles, support, kind='support', config=config
    )
    resistance_deep_dive, resistance_deep_dive_group = _build_selected_line_deep_dive_tables(
        candles, resistance, kind='resistance', config=config
    )

    why = pd.DataFrame(
        [
            ["为什么不直接搬 PyIndicators breakout navigator", "因为该文件来源带 LuxAlgo / CC BY-NC-SA 4.0 / analytical use only 语义，代码来源边界不够干净。"],
            ["为什么这次选 pytrendline", "MIT，且原生就解决 pivot → support/resistance trendlines → breakout 研究这条链。"],
            ["当前定位", "研究功能，不是正式交易信号。"],
            ["当前边界", "只在最近一个窗口扫描，因为 pytrendline 是 O(N^3) 级别的穷举趋势线搜索。"],
        ],
        columns=["question", "answer"],
    )

    reading_guide = pd.DataFrame(
        [
            [1, "先看“页面导读”与“步骤总览”", "先建立这页的阅读顺序：数据从哪来、经过哪些中间层、最后展示什么。"],
            [2, "再看参数 / 窗口 / 来源边界", "先确认这次到底扫了什么样本、为什么只看最近窗口、这页能回答什么不能回答什么。"],
            [3, "再看 K 线 + pivots", "先看结构锚点，再理解后面的 trendline 不是凭空长出来的。"],
            [4, "然后看 support / resistance / breakout 图", "把线和锚点、事件线分开看，避免一上来就被最终总览图淹没。"],
            [5, "最后看表格与边界", "先用图形成直觉，再用字段解释、代表线表和边界卡片收束理解。"],
        ],
        columns=["step", "how_to_read", "why_it_matters"],
    )

    flow_overview = pd.DataFrame(
        [
            [1, "bars", "下载 period × interval 的 OHLCV，再裁成最近 `window_bars` 根。"],
            [2, "pivots", "在窗口内识别 support / resistance pivots，作为结构锚点。"],
            [3, "candidate lines", "从 pivots 组合中尝试构造候选趋势线。"],
            [4, "filtered lines", "受 `min_points_required`、pivot 约束、breakout 约束等规则筛掉不合格线。"],
            [5, "duplicate groups", "把非常接近的线分组，避免图上同类线过度堆叠。"],
            [6, "best lines + breakout labels", "保留更适合展示的代表线，并标出哪些线已经被识别成 breakout。"],
        ],
        columns=["stage", "object", "what_happens_here"],
    )

    chart_legend = pd.DataFrame(
        [
            ["绿色 K 线实体", "收盘价 >= 开盘价的上涨 bar。"],
            ["红色 K 线实体", "收盘价 < 开盘价的下跌 bar。"],
            ["灰色上下影线", "该 bar 的 high / low 范围。"],
            ["青绿色倒三角", "support pivots，表示支撑侧结构锚点。"],
            ["橙色正三角", "resistance pivots，表示阻力侧结构锚点。"],
            ["三角标旁的小数字", "对应该 pivot 的 bar index，让 Step 1 图能和 deep-dive / best lines 表里的 pivot index 直接对上。"],
            ["蓝色实线", "support best lines（未标成 breakout 的代表支撑线）。"],
            ["紫色实线", "resistance best lines（未标成 breakout 的代表阻力线）。"],
            ["蓝/紫实心圆点", "当前展示线命中的结构点（pointset pivots）；点内数字是对应的 pivot index，用来说明这条线到底是被哪些点支撑出来的。"],
            ["绿色虚线", "support breakout lines：已被 pytrendline 标为 breakout 的支撑线。"],
            ["红色虚线", "resistance breakout lines：已被 pytrendline 标为 breakout 的阻力线。"],
        ],
        columns=["chart_element", "meaning"],
    )

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>PyTrendline Research Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; max-width: 1180px; margin: 40px auto; padding: 0 18px; line-height: 1.65; color: #111; }}
    h1, h2, h3 {{ line-height: 1.25; }}
    .muted {{ color: #666; }}
    .card {{ border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px 18px; margin: 16px 0; }}
    .section-card {{ background: #f8fafc; border-color: #cbd5e1; }}
    .section-card h2 {{ margin-bottom: 6px; }}
    .pill-list {{ display:flex; flex-wrap:wrap; gap:10px; margin-top:10px; }}
    .pill {{ display:inline-block; padding:6px 10px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:13px; }}
    .table-wrap {{ width: 100%; overflow-x: auto; overflow-y: hidden; }}
    .tbl {{ border-collapse: collapse; width: 100%; font-size: 14px; min-width: 100%; }}
    .tbl th, .tbl td {{ border-bottom: 1px solid #e5e7eb; padding: 8px 10px; text-align: left; vertical-align: top; }}
    img {{ max-width: 100%; border: 1px solid #e5e7eb; border-radius: 10px; }}
    a {{ color: #2563eb; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .grid2 {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; }}
  </style>
</head>
<body>
  <h1>PyTrendline Research Report</h1>
  <p class="muted">样本：{html.escape(ticker)} | {html.escape(period)} / {html.escape(interval)} | 生成时间：{generated_at}</p>

  <div class="card">
    <h2>这次落地了什么</h2>
    <p class="muted">这个区块回答：这页相较于普通“结果页”，额外补了哪些 explainability 信息。</p>
    <ul>
      <li>把 <b>MIT</b> 的 <code>pytrendline</code> 接进了 <code>momentum</code></li>
      <li>不只给最终趋势线图，而是补了中间步骤图：窗口 / pivots / support / resistance / breakout-only</li>
      <li>把字段语义、窗口语义、research-only 边界写进同一页，方便后续映射到 parallel channel</li>
      <li>当前仍保留为研究功能，不直接当交易信号</li>
    </ul>
  </div>

  <div class="card section-card">
    <h2>四段式结构导航</h2>
    <p class="muted">这页现在按四段式结构组织：先定义，再计算，再看结果，最后单独收束边界与下一步。这样可以减少“定义、结果、限制”来回穿插造成的阅读负担。</p>
    <div class="pill-list">
      <span class="pill">1. 定义层：对象、参数、来源、读法</span>
      <span class="pill">2. 计算层：pivot → candidate → filter → grouping</span>
      <span class="pill">3. 结果层：图、代表线、事件线、总览</span>
      <span class="pill">4. 边界层：time semantics / research-only / next step</span>
    </div>
  </div>

  <div class="card section-card">
    <h2>第一层：定义层</h2>
    <p class="muted">先统一读法、输入边界、参数选择与图上元素语义。这个层只回答“这页在看什么、怎么读、对象分别是什么”。</p>
  </div>

  <div class="card">
    <h2>页面导读 / Reading guide</h2>
    <p class="muted">这个区块回答：这页应该按什么顺序看，哪些部分是“定义表”，哪些部分是“结果图/结果表”。</p>
    {render_table(reading_guide)}
  </div>

  <div class="card">
    <h2>步骤总览：从输入到结果</h2>
    <p class="muted">这个区块回答：数据是怎样一步步从 bars 走到 pivots、再走到代表线和 breakout 标签的。</p>
    {render_table(flow_overview)}
  </div>

  <div class="grid2">
    <div class="card">
      <h2>参数</h2>
      <p class="muted">这个区块回答：这次扫描到底看了什么数据、用了哪些关键参数。</p>
      {render_table(params)}
    </div>
    <div class="card">
      <h2>窗口 / 运行边界</h2>
      <p class="muted">这个区块回答：为什么当前只看最近窗口，以及这样做的代价和边界是什么。</p>
      {render_table(window_semantics)}
    </div>
  </div>

  <div class="card">
    <h2>来源与边界</h2>
    <p class="muted">这个区块回答：为什么选 pytrendline、为什么不直接搬别的实现、以及这页当前的定位是什么。</p>
    {render_table(why)}
  </div>

  <div class="card">
    <h2>为什么当前参数这样设</h2>
    <p class="muted">这个区块回答：`96 / 3 / pivot-only / breakout-on` 这些选择不是随意的，它们各自想在“解释力、复杂度、可读性”之间取什么平衡。</p>
    {render_table(parameter_rationale)}
  </div>

  <div class="card">
    <h2>图上元素字典</h2>
    <p class="muted">这个区块回答：图里每个颜色、线型、标记各代表什么，方便和后面的图一一对照。</p>
    {render_table(chart_legend)}
  </div>

  <div class="card section-card">
    <h2>第二层：计算层</h2>
    <p class="muted">这一层回答结构对象是怎样被算出来的：从 pivots、candidate pairs、过滤、duplicate grouping，一直到 breakout 标签与 lifecycle。</p>
  </div>

  <div class="card">
    <h2>逐步骤操作性定义</h2>
    <p class="muted">这个区块回答：每一步“具体在算什么”，避免把结果页误读成纯视觉画线。</p>
    {render_table(steps)}
  </div>

  <div class="card">
    <h2>Pivot points 是怎么来的</h2>
    <p class="muted">这个区块回答：support / resistance pivots 在源码里到底是怎么选出来的，以及这为什么会影响 bar-by-bar 可用性。</p>
    {render_table(pivot_logic)}
  </div>

  <div class="card">
    <h2>候选趋势线是怎么从 pivots 组合出来的</h2>
    <p class="muted">这个区块回答：是不是所有 pivot 组合都会尝试、它们经历了哪些过滤、以及为什么最后页面里只剩下一小部分线。</p>
    {render_table(candidate_logic)}
  </div>

  <div class="card">
    <h2>Candidate lines before filtering：原始 pivot-pair 候选线有多密</h2>
    <p class="muted">这个区块回答：在任何 slope / last-price / num_points / duplicate grouping 过滤生效之前，单靠 pivot-pair 组合会产生多密的原始候选线。这里展示的是示意性抽样 / 截断视图，目的是让读者直观看到“候选线爆炸”而不是把它误读成最终线集合。</p>
    <img src="{artifacts_rel}/candidate_lines_before_filter.png" alt="candidate lines before filtering" />
    <p class="muted">图下注释：每条浅色线段都只是某一对 pivots 直接定义出来的原始候选段，还没有经过 slope 合法性、last-price 合法性、最小命中点数与 duplicate grouping 压缩。它的作用是帮助理解：为什么页面最后只显示少数代表线，而不是把所有 pivot 两两相连后都堆出来。</p>
  </div>

  <div class="card">
    <h2>为什么不能把所有 pivot 两两相连</h2>
    <p class="muted">这个区块回答：为什么“把所有 pivot 都连起来”会失真，以及当前代码到底用了哪几层规则来压缩这些候选线。</p>
    {render_table(why_not_all_pairs)}
  </div>

  <div class="card">
    <h2>从 pivot 到 trendline：决策链总览</h2>
    <p class="muted">这个区块回答：pivot collection / pair enumeration / candidate fitting / filtering / breakout tagging / duplicate grouping / best-from-group selection 这一整条链，在当前窗口里各自对应什么动作与什么数量级。</p>
    {render_table(decision_chain)}
  </div>

  <div class="card">
    <h2>什么情况下能被当做趋势线，什么情况下不能</h2>
    <p class="muted">这个区块回答：一条线要满足哪些条件才会变成有效趋势线；又会因为什么原因被淘汰、被改标 breakout，或虽存在但不再单独展示。</p>
    {render_table(validity_rules)}
  </div>

  <div class="card">
    <h2>Filter waterfall：候选线是如何一层层被筛下来的</h2>
    <p class="muted">这个区块回答：从 pivot 到最终展示线，中间到底经过了多少层过滤。它是理解“为什么页面最后只剩少数代表线”的核心计数视角。</p>
    <img src="{artifacts_rel}/filter_waterfall.png" alt="filter waterfall" />
    {render_table(filter_waterfall)}
  </div>

  <div class="card">
    <h2>Accepted vs rejected examples：抽象规则对应到真实样例</h2>
    <p class="muted">这个区块回答：上面的规则如果落到当前窗口里的真实线，分别长什么样。这里刻意同时给出：被保留的、被改标 breakout 的、虽然有效但被并组压掉的、以及根本没进有效结果池的样例。</p>
    {render_table(accepted_rejected_examples)}
  </div>

  <div class="card">
    <h2>Line lifecycle：一条线从 candidate 到代表线会经历什么</h2>
    <p class="muted">这个区块回答：一条线什么时候还只是 candidate，什么时候已经是有效结构线，什么时候被标成 breakout，什么时候只是留在结果里但不再默认展示，以及当前页面有没有“失效/过期线”的概念。</p>
    {render_table(line_lifecycle)}
  </div>

  <div class="card">
    <h2>State diagram：line lifecycle 状态流转图</h2>
    <p class="muted">这个区块回答：上面的生命周期如果压缩成一张图，状态之间的流转顺序是什么；同时明确当前页面还没有单独建模 expired / retired state。</p>
    <img src="{artifacts_rel}/line_lifecycle_state_diagram.svg" alt="line lifecycle state diagram" />
  </div>



  <div class="card">
    <h2>`num_points` 应该怎么读</h2>
    <p class="muted">这个区块回答：`num_points` 不是交易次数，而是这条线被多少结构点支撑；它帮助判断这条线的解释力强弱。</p>
    {render_table(candidate_quality)}
  </div>

  <div class="card">
    <h2>`is_breakout` 应该怎么读</h2>
    <p class="muted">这个区块回答：support breakout / resistance breakout 到底分别是什么意思，它更接近 close-based 还是 high/low-based，以及它在当前页面里更像什么类型的标签。</p>
    {render_table(breakout_logic)}
  </div>

  <div class="grid2">
    <div class="card">
      <h2>Duplicate grouping：support 侧概览</h2>
      <p class="muted">这个区块回答：support 侧为什么会出现很多近似线，以及当前窗口下它们被压缩成了多少个 group。</p>
      {render_table(support_dup_overview)}
    </div>
    <div class="card">
      <h2>Duplicate grouping：resistance 侧概览</h2>
      <p class="muted">这个区块回答：resistance 侧为什么也会有大量相近线，以及 grouping 阈值当前大概落在什么数量级。</p>
      {render_table(resistance_dup_overview)}
    </div>
  </div>

  <div class="grid2">
    <div class="card">
      <h2>Support duplicate groups（样例）</h2>
      <p class="muted">这个区块回答：support 侧 group 内通常有多少条近似线，哪一条会被选成 best-from-group。</p>
      {render_table(support_dup_groups)}
    </div>
    <div class="card">
      <h2>Resistance duplicate groups（样例）</h2>
      <p class="muted">这个区块回答：resistance 侧 group 内的近似线如何聚类，以及 breakout / non-breakout 为什么不会混进同一组。</p>
      {render_table(resistance_dup_groups)}
    </div>
  </div>

  <div class="card">
    <h2>Duplicate grouping before/after：压缩前后到底差了什么</h2>
    <p class="muted">这个区块回答：duplicate grouping 不是抽象概念，而是把一批几乎重合的候选结果压缩成每组一条代表线。左侧子图展示 grouping 压缩前的重复线堆叠，右侧子图展示压缩后仅保留 best-from-group 的效果。</p>
    <img src="{artifacts_rel}/duplicate_grouping_before_after.png" alt="duplicate grouping before after" />
    <p class="muted">图下注释：颜色表示被选中的 duplicate groups；before 面板里同组内会看到多条非常接近的线，after 面板里只保留每组得分最高的代表线。这样更容易理解：页面默认不是忽略其它线，而是有意识地做了“视觉去重”。</p>
  </div>

  <div class="card">
    <h2>如何理解 duplicate grouping 与 score</h2>
    <p class="muted">这个区块回答：为什么会有很多相似线、group 内 best line 是怎么选的、以及为什么页面默认只展示 best-from-group。</p>
    <table class="tbl">
      <thead><tr><th>问题</th><th>当前回答</th></tr></thead>
      <tbody>
        <tr><td>为什么会有大量相近线？</td><td>因为不同 pivot-pairs 可能拟合出 slope 与最后价格都非常接近的线；它们在视觉上几乎重合，但在源码里仍是不同候选结果。</td></tr>
        <tr><td>group 是按什么聚的？</td><td>pytrendline 用二维条件聚类：同时比较 <code>price_at_last_date</code> 和 <code>slope</code> 的差异；两者都足够接近时才会归为同一组。</td></tr>
        <tr><td>breakout 线会和普通线混组吗？</td><td>不会。源码要求 <code>is_breakout</code> 相同才允许进同一组，所以 breakout / non-breakout 会分开聚类。</td></tr>
        <tr><td>best-from-group 怎么选？</td><td>每个 duplicate group 里最终按 <code>score</code> 选出代表线，并标成 <code>is_best_from_duplicate_group=True</code>。</td></tr>
        <tr><td>为什么页面默认只展示 best-from-group？</td><td>否则图上会堆满视觉上几乎重合的线，读者很难判断真正值得先看的结构；保留代表线能显著提升可读性。</td></tr>
        <tr><td>读图时该怎么理解 <code>rank_within_group</code>？</td><td>它表示同组内部按 score 排名的位置；数字越靠前，说明它越接近该组最值得展示的代表线。</td></tr>
      </tbody>
    </table>
  </div>



  <div class="card section-card">
    <h2>第三层：结果层</h2>
    <p class="muted">这一层只看当前窗口里真正保留下来的图、代表线、事件线与汇总结果。先有了前面的定义和计算，再回来看这些结果就不会误读成“所有线都是实时交易信号”。</p>
  </div>

  <div class="card">
    <h2>窗口内数量概览</h2>
    <p class="muted">这个区块回答：当前窗口里总共识别出了多少 pivots、多少候选/代表线、多少 breakout 标签。</p>
    {render_table(counts)}
  </div>

  <div class="card">
    <h2>Step 1 · 先看结构锚点：原始 K 线 + pivots</h2>
    <p class="muted">这个区块回答：趋势线依附的“结构点”到底在哪里。当前 pivots 来自原始 OHLC，而不是平滑后的曲线；每个三角标旁的小数字就是对应的 pivot index。</p>
    <img src="{artifacts_rel}/step1_close_and_pivots.png" alt="close and pivots" />
    <p class="muted">图下注释：先只看 K 线与 pivot 标记，不急着看趋势线。图上的小数字就是 pivot index，这样 Step 1 现在已经可以直接和 deep-dive / best lines 表里的 `pointset_indeces` 对照；读法上，先确认支撑/阻力锚点分布，再进入后面的支撑线与阻力线图。</p>
  </div>

  <div class="grid2">
    <div class="card">
      <h2>Step 2 · 再看支撑线如何从锚点长出来</h2>
      <p class="muted">这个区块回答：support line 在局部到底是怎么被“贴”到多个结构点上的。这里继续只保留 grouped 之后的代表线，但不再把 breakout 线排除在外；若某条线后来被突破，前半段仍会画出来，突破后的后半段再改成虚线。</p>
      <img src="{artifacts_rel}/step2_support_lines.png" alt="support lines" />
      <p class="muted">图下注释：蓝色实线 = 当前窗口里这条代表 support 线在 breakout 前的结构段；绿色虚线 = 同一条线在 breakout 后的延伸段；若某条线尚未 breakout，则仍按普通代表线显示。白边高亮点 = 这条线实际命中的 pivots（数字是 pivot index）。所以 Step 2 现在回答的是“代表线是怎么长出来的”，而不是“当前还剩多少 non-breakout 线”。</p>
    </div>
    <div class="card">
      <h2>Step 3 · 再看阻力线如何从锚点长出来</h2>
      <p class="muted">这个区块回答：resistance line 在局部到底是怎么被“贴”到多个结构点上的。这里同样只保留 grouped 之后的代表线；若后来发生 breakout，就把突破后的后半段改为虚线而不是整条线直接隐藏。</p>
      <img src="{artifacts_rel}/step3_resistance_lines.png" alt="resistance lines" />
      <p class="muted">图下注释：紫色实线 = breakout 前仍作为结构线的一段；红色虚线 = breakout 后的延伸段；白边高亮点 = 这条线命中的 pivots。这样你可以同时看到“线是怎么被定义出来的”和“它后来在哪里变成事件线”。</p>
    </div>
  </div>

  <div class="card">
    <h2>Step 4 · 最后只看事件线：breakout-only</h2>
    <p class="muted">这个区块回答：哪些线已经不只是“结构线”，而是被 pytrendline 标成了 breakout 事件线。这里改成 support / resistance 分面显示，减少不同侧事件线互相压在一起。</p>
    <img src="{artifacts_rel}/step4_breakout_only.png" alt="breakout only lines" />
    <p class="muted">图下注释：每个子图只保留少量 breakout 样例线。实线部分表示用于定义结构的拟合线段，虚线部分表示向 breakout bar 的延伸；带描边的事件圈和 `S/R` 标记，就是实际触发 breakout 的那根 K 线。这样你看到的是“这条线如何变成事件”，而不是一整屏互相重叠的无限延长线。</p>
  </div>

  <div class="card">
    <h2>最终总览图：把锚点、代表线与事件线叠在一起</h2>
    <p class="muted">这个区块回答：如果把 pivots、代表线和 breakout 线放回同一张图，整体画面是什么样。</p>
    <img src="{artifacts_rel}/trendlines_overlay.png" alt="trendlines overlay" />
    <p class="muted">图下注释：这张总览图现在与 Step 2 / Step 3 保持一致——同一条 breakout 线会拆成“break 前实线 + break 后虚线”，并额外圈出 breakout bar。为了减少视觉噪声，这里不再铺满当前窗口的全部 pivots，而只高亮当前代表线实际命中的那些 support / resistance pivots；如果你要看全量 pivot universe，请回到 Step 1。</p>
  </div>

  <div class="card">
    <h2>Selected line deep-dive：挑 1 条 support / 1 条 resistance 逐项拆开</h2>
    <p class="muted">这个区块回答：如果不只看抽象规则，而是直接挑两条真实代表线逐项拆开，它们到底命中了哪些 pivots、`m / b / num_points / score` 怎么读、为什么通过过滤、为什么是 best-from-group、以及 breakout 发生在哪根 bar。</p>
    <div class="grid2">
      <div>
        <h3>Support selected line</h3>
        {render_table(support_deep_dive)}
        <p class="muted">同组对照：下面列的是和这条 support 线处在同一个 duplicate group 的候选结果，方便直接看出它为什么成为代表线。</p>
        {render_table(support_deep_dive_group)}
      </div>
      <div>
        <h3>Resistance selected line</h3>
        {render_table(resistance_deep_dive)}
        <p class="muted">同组对照：下面列的是和这条 resistance 线处在同一个 duplicate group 的候选结果，方便直接看出它为什么成为代表线。</p>
        {render_table(resistance_deep_dive_group)}
      </div>
    </div>
  </div>

  <div class="card">
    <h2>Best support lines</h2>
    <p class="muted">这个区块回答：当前最值得先读的代表支撑线有哪些，它们各自的 `m / b / score / num_points` 是什么，以及它们命中了哪些结构点。</p>
    {render_table(support_show)}
  </div>

  <div class="card">
    <h2>Best resistance lines</h2>
    <p class="muted">这个区块回答：当前最值得先读的代表阻力线有哪些，它们和支撑线的差别是什么，以及它们命中了哪些结构点。</p>
    {render_table(resistance_show)}
  </div>


  <div class="card section-card">
    <h2>第四层：边界层</h2>
    <p class="muted">最后单独收束：哪些字段带事后视角、哪些结论现在能信、哪些不能直接跳到交易层，以及这页与后续 event foundation / channel 研究是什么关系。</p>
  </div>

  <div class="card">
    <h2>时间语义 / 生命周期边界：现在看到的线，到底是“当时知道的”还是“回头看知道的”？</h2>
    <p class="muted">这个区块回答：这页里的 bars、pivots、trendlines、breakout 标签、duplicate grouping 各自是在什么时点才算已知；也明确当前页面更接近窗口末端回看快照，而不是 bar-by-bar 在线状态机。</p>
    {render_table(time_semantics)}
  </div>

  <div class="card">
    <h2>字段解释</h2>
    <p class="muted">这个区块回答：表里的字段具体是什么意思，避免把 `score`、`is_breakout` 等字段误读成交易结论。</p>
    {render_table(glossary)}
  </div>

  <div class="card">
    <h2>bar-by-bar 可用性 / research-only 边界</h2>
    <p class="muted">这个区块回答：这页最适合支持什么判断，以及目前还不应该被过度解读成什么。</p>
    {render_table(boundaries)}
  </div>

  <div class="card">
    <h2>Baseline v1 status：这页当前处在什么阶段</h2>
    <p class="muted">这个区块回答：`pytrendline_research` 现在是一个什么性质的产物——它已经完成了哪些 explainability 任务，又明确还没有承担哪些策略层职责。</p>
    {render_table(baseline_status)}
  </div>

  <div class="card">
    <h2>当前我应该相信什么 / 不该过度解读什么</h2>
    <p class="muted">这个区块回答：看完前面所有定义、图和表之后，这页最适合支撑哪些判断，以及哪些结论还不能直接从这里跳到交易层。</p>
    {render_table(trust_vs_overread)}
  </div>

  <div class="card">
    <h2>下一步建议：从 explainability baseline 到 event foundation</h2>
    <p class="muted">这个区块回答：既然这页已经把结构定义讲清楚，后面最自然的推进顺序应该是什么；也明确不建议再回到“先追求策略净值”的旧路径。</p>
    {render_table(next_step_guidance)}
  </div>

  <div class="card">
    <h2>从 pytrendline 到 parallel channel 的映射</h2>
    <p class="muted">这个区块回答：当前这页对后续 parallel channel 研究到底已经提供了哪些可复用定义，还缺哪一半没有解决。</p>
    <table class="tbl">
      <thead><tr><th>问题</th><th>当前回答</th></tr></thead>
      <tbody>
        <tr><td>它已经解决了什么？</td><td>已经把 <code>pivot → candidate lines → best lines → breakout labels</code> 这条链跑通了。</td></tr>
        <tr><td>它还没解决什么？</td><td>还没有“双边平行约束 / 通道宽度定义 / mid-line 语义 / 多周期共振 / rebound 规则”的完整定义。</td></tr>
        <tr><td>对后续最有价值的是什么？</td><td>给我们一个可解释的外部基线：先把 line 是怎么来的讲清楚，再决定哪些定义要迁移进平行通道研究。</td></tr>
      </tbody>
    </table>
  </div>

  <div class="card">
    <h2>Artifacts</h2>
    <p class="muted">这个区块回答：如果你要回到原始产物进一步核对，这一页背后有哪些 CSV / PNG / JSON 文件可供复查。</p>
    <ul>
      <li><a href="{artifacts_rel}/candles_window.csv">candles_window.csv</a></li>
      <li><a href="{artifacts_rel}/support_trendlines.csv">support_trendlines.csv</a></li>
      <li><a href="{artifacts_rel}/resistance_trendlines.csv">resistance_trendlines.csv</a></li>
      <li><a href="{artifacts_rel}/summary.json">summary.json</a></li>
      <li><a href="{artifacts_rel}/filter_waterfall.png">filter_waterfall.png</a></li>
      <li><a href="{artifacts_rel}/candidate_lines_before_filter.png">candidate_lines_before_filter.png</a></li>
      <li><a href="{artifacts_rel}/duplicate_grouping_before_after.png">duplicate_grouping_before_after.png</a></li>
      <li><a href="{artifacts_rel}/line_lifecycle_state_diagram.svg">line_lifecycle_state_diagram.svg</a></li>
      <li><a href="{artifacts_rel}/step1_close_and_pivots.png">step1_close_and_pivots.png</a></li>
      <li><a href="{artifacts_rel}/step2_support_lines.png">step2_support_lines.png</a></li>
      <li><a href="{artifacts_rel}/step3_resistance_lines.png">step3_resistance_lines.png</a></li>
      <li><a href="{artifacts_rel}/step4_breakout_only.png">step4_breakout_only.png</a></li>
      <li><a href="{artifacts_rel}/trendlines_overlay.png">trendlines_overlay.png</a></li>
    </ul>
  </div>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Build pytrendline report")
    parser.add_argument("--ticker", default=DEFAULT_TICKER)
    parser.add_argument("--period", default=DEFAULT_PERIOD)
    parser.add_argument("--interval", default=DEFAULT_INTERVAL)
    parser.add_argument("--window-bars", type=int, default=96)
    args = parser.parse_args()

    bars = download_bars(args.ticker, args.period, args.interval)
    cfg = PyTrendlineConfig(window_bars=args.window_bars, min_points_required=3, ignore_breakouts=False, all_pts_must_be_pivots=True, time_interval=args.interval)
    result = detect_pytrendlines(bars, config=cfg)

    candles = result["candles_df"]
    support = result["support_trendlines"]
    resistance = result["resistance_trendlines"]
    support_pivots = result["support_pivots"]
    resistance_pivots = result["resistance_pivots"]

    artifacts_dir = ensure_dir(ROOT / "reports" / "artifacts" / "pytrendline_research")
    site_dir = ensure_dir(ROOT / "reports" / "site" / "factors" / "pytrendline_research")

    candles.to_csv(artifacts_dir / "candles_window.csv", index=False)
    support.to_csv(artifacts_dir / "support_trendlines.csv", index=False)
    resistance.to_csv(artifacts_dir / "resistance_trendlines.csv", index=False)

    filter_waterfall, why_not_all_pairs, support_pipeline_counts, resistance_pipeline_counts = _build_filter_waterfall_tables(
        candles, support, resistance, support_pivots, resistance_pivots, cfg
    )

    plot_filter_waterfall(filter_waterfall, artifacts_dir / "filter_waterfall.png")
    plot_candidate_lines_before_filter(candles, support_pivots, resistance_pivots, artifacts_dir / "candidate_lines_before_filter.png")
    plot_duplicate_grouping_before_after(candles, support, resistance, artifacts_dir / "duplicate_grouping_before_after.png")
    (artifacts_dir / "line_lifecycle_state_diagram.svg").write_text(_line_lifecycle_state_diagram_svg(), encoding="utf-8")
    plot_price_with_pivots(candles, support_pivots, resistance_pivots, artifacts_dir / "step1_close_and_pivots.png", title=f"{args.ticker} | candlesticks + pivots ({args.window_bars} bars)")
    plot_lines(candles, support, artifacts_dir / "step2_support_lines.png", title=f"{args.ticker} | support line examples (zoomed teaching view)", kind="support", highlight_pointsets=True, top_n=3)
    plot_lines(candles, resistance, artifacts_dir / "step3_resistance_lines.png", title=f"{args.ticker} | resistance line examples (zoomed teaching view)", kind="resistance", highlight_pointsets=True, top_n=3)

    # breakout-only chart: split support / resistance into separate teaching panels
    fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharey=False)
    for ax, lines, kind in zip(axes, [support, resistance], ["support", "resistance"]):
        _plot_base(ax, candles)
        show = _render_line_collection(
            ax,
            candles,
            lines,
            kind=kind,
            breakout_only=True,
            highlight_pointsets=False,
            top_n=3,
        )
        _highlight_breakout_bars(ax, candles, show, kind=kind)
        handles, labels = ax.get_legend_handles_labels()
        seen = set()
        uniq_h = []
        uniq_l = []
        for h, l in zip(handles, labels):
            if l not in seen:
                uniq_h.append(h)
                uniq_l.append(l)
                seen.add(l)
        ax.set_title(f"{args.ticker} | {kind} breakout examples")
        ax.grid(alpha=0.2)
        if uniq_h:
            ax.legend(uniq_h, uniq_l, loc="upper left")
    fig.tight_layout()
    fig.savefig(artifacts_dir / "step4_breakout_only.png", dpi=160)
    plt.close(fig)

    # final overlay
    fig, ax = plt.subplots(figsize=(14, 6))
    _plot_base(ax, candles, add_pivots=False)
    overlay_support = _best_lines(support, top_n=4)
    overlay_resistance = _best_lines(resistance, top_n=4)
    _highlight_selected_pivots(ax, candles, _collect_line_pointset_indices(overlay_support, total_bars=len(candles)), kind="support")
    _highlight_selected_pivots(ax, candles, _collect_line_pointset_indices(overlay_resistance, total_bars=len(candles)), kind="resistance")
    shown_support = _render_line_collection(
        ax,
        candles,
        overlay_support,
        kind="support",
        breakout_only=False,
        highlight_pointsets=False,
        top_n=4,
        zoom_to_lines=False,
    )
    shown_resistance = _render_line_collection(
        ax,
        candles,
        overlay_resistance,
        kind="resistance",
        breakout_only=False,
        highlight_pointsets=False,
        top_n=4,
        zoom_to_lines=False,
    )
    _highlight_breakout_bars(ax, candles, shown_support, kind="support")
    _highlight_breakout_bars(ax, candles, shown_resistance, kind="resistance")

    handles, labels = ax.get_legend_handles_labels()
    seen = set()
    uniq_h = []
    uniq_l = []
    for h, l in zip(handles, labels):
        if l not in seen:
            uniq_h.append(h)
            uniq_l.append(l)
            seen.add(l)

    ax.set_title(f"{args.ticker} | pytrendline research window ({args.window_bars} bars)")
    ax.grid(alpha=0.2)
    if uniq_h:
        ax.legend(uniq_h, uniq_l, loc="upper left")
    fig.tight_layout()
    fig.savefig(artifacts_dir / "trendlines_overlay.png", dpi=160)
    plt.close(fig)

    summary = {
        "ticker": args.ticker,
        "period": args.period,
        "interval": args.interval,
        "window_bars": args.window_bars,
        "support_pivots": len(support_pivots),
        "resistance_pivots": len(resistance_pivots),
        "support_lines": int(len(support)),
        "resistance_lines": int(len(resistance)),
        "support_breakouts": int(support["is_breakout"].sum()) if not support.empty and "is_breakout" in support.columns else 0,
        "resistance_breakouts": int(resistance["is_breakout"].sum()) if not resistance.empty and "is_breakout" in resistance.columns else 0,
        "support_pipeline": support_pipeline_counts,
        "resistance_pipeline": resistance_pipeline_counts,
    }
    (artifacts_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    html_text = build_html(
        ticker=args.ticker,
        period=args.period,
        interval=args.interval,
        config=cfg,
        support=support,
        resistance=resistance,
        support_pivots=support_pivots,
        resistance_pivots=resistance_pivots,
        candles=candles,
        artifacts_rel="../../artifacts/pytrendline_research",
    )
    (site_dir / "report.html").write_text(html_text, encoding="utf-8")
    print(f"Wrote report to {site_dir / 'report.html'}")


if __name__ == "__main__":
    main()
