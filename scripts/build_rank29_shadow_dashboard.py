#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "manual_narrow_paper_lanes"
ORD_ART_DIR = ROOT / "reports" / "artifacts" / "rank29_orderbook_shadow"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "rank29_shadow_dashboard"
OUT_PATH = SITE_DIR / "report.html"

ACTUAL_LEDGER_PATH = ART_DIR / "manual_narrow_paper_closed_trades.csv"
ACTUAL_STATUS_PATH = ART_DIR / "manual_narrow_paper_status.csv"
REPLAY_PATH = ART_DIR / "rank29_shadow_trade_view.csv"
RUN_SUMMARY_PATH = ART_DIR / "manual_narrow_paper_last_run_summary.json"

ORDERBOOK_STATUS_PATH = ORD_ART_DIR / "shadow_status.csv"
ORDERBOOK_SIGNALS_PATH = ORD_ART_DIR / "shadow_recent_signals.csv"
ORDERBOOK_REJECTIONS_PATH = ORD_ART_DIR / "shadow_recent_rejections.csv"

BASELINE_ID = "rank29_trendline_breakout_navigator"
GATE_ID = "rank29_trendline_breakout_gate_shadow"
LANE_ORDER = ["baseline", "gate_shadow"]
LANE_LABELS = {"baseline": "baseline", "gate_shadow": "gate shadow"}
WINDOWS = [
    ("12h", pd.Timedelta(hours=12)),
    ("1d", pd.Timedelta(days=1)),
    ("3d", pd.Timedelta(days=3)),
    ("7d", pd.Timedelta(days=7)),
    ("14d", pd.Timedelta(days=14)),
    ("30d", pd.Timedelta(days=30)),
]

COLORS = {
    "baseline": "#60a5fa",
    "gate_shadow": "#22c55e",
    "signal": "#38bdf8",
    "reject": "#f59e0b",
    "loss": "#ef4444",
    "grid": "#1f2937",
    "text": "#cbd5e1",
    "muted": "#94a3b8",
}


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def pct(v, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def num(v, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def nav_fmt(v, digits: int = 3) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}x"


def fmt_ts(v) -> str:
    if v is None or pd.isna(v):
        return "-"
    return pd.to_datetime(v, utc=True).strftime("%Y-%m-%d %H:%M UTC")


def render_table(df: pd.DataFrame, *, percent_cols: set[str] | None = None, nav_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    percent_cols = percent_cols or set()
    nav_cols = nav_cols or set()
    digits_cols = digits_cols or {}
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            v = row[col]
            if col in percent_cols:
                text = pct(v, digits_cols.get(col, 2))
            elif col in nav_cols:
                text = nav_fmt(v, digits_cols.get(col, 3))
            elif isinstance(v, (int, float, np.integer, np.floating)) and not isinstance(v, bool):
                text = num(v, digits_cols.get(col, 2))
            else:
                text = str(v)
            cells.append(f"<td>{escape(text)}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def chart_svg_placeholder(text: str, *, height: int = 320) -> str:
    return f"""
    <svg viewBox=\"0 0 1120 {height}\" class=\"chart\" role=\"img\" aria-label=\"{escape(text)}\">
      <rect x=\"0\" y=\"0\" width=\"1120\" height=\"{height}\" rx=\"16\" fill=\"#0b1220\" stroke=\"#1f2937\" />
      <text x=\"560\" y=\"{height/2:.0f}\" text-anchor=\"middle\" fill=\"#94a3b8\" font-size=\"20\">{escape(text)}</text>
    </svg>
    """


def _scale(values: pd.Series, lo: float, hi: float, out_lo: float, out_hi: float) -> pd.Series:
    if hi <= lo:
        return pd.Series([(out_lo + out_hi) / 2.0] * len(values), index=values.index)
    return out_lo + (values - lo) * (out_hi - out_lo) / (hi - lo)


def _lane_from_candidate_id(s: pd.Series) -> pd.Series:
    return s.map({BASELINE_ID: "baseline", GATE_ID: "gate_shadow"}).fillna("other")


def prepare_trades(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    for col in ["entry_ts", "exit_ts"]:
        if col in out.columns:
            out[col] = pd.to_datetime(out[col], utc=True)
    out["net_ret"] = pd.to_numeric(out["net_ret"], errors="coerce")
    out = out[out["candidate_id"].isin([BASELINE_ID, GATE_ID])].copy()
    if out.empty:
        return out
    out["lane"] = _lane_from_candidate_id(out["candidate_id"])
    out["lane_label"] = out["lane"].map(LANE_LABELS).fillna(out["candidate_id"])
    out = out.sort_values(["exit_ts", "asset", "candidate_id"]).reset_index(drop=True)
    out["cum_return"] = out.groupby("lane")["net_ret"].transform(lambda s: (1.0 + s).cumprod() - 1.0)
    out["nav"] = out.groupby("lane")["net_ret"].transform(lambda s: (1.0 + s).cumprod())
    return out


def build_summary(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame()
    return (
        trades.groupby("lane", as_index=False)
        .agg(
            trades=("net_ret", "size"),
            total_return=("net_ret", lambda s: float((1.0 + s).prod() - 1.0)),
            ending_nav=("nav", "last"),
            win_rate=("net_ret", lambda s: float((s > 0).mean())),
            avg_trade=("net_ret", "mean"),
            median_trade=("net_ret", "median"),
            first_entry=("entry_ts", "min"),
            last_exit=("exit_ts", "max"),
        )
        .sort_values("lane")
        .reset_index(drop=True)
    )


def build_window_table(trades: pd.DataFrame, *, anchor_ts: pd.Timestamp | None = None) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame()
    if anchor_ts is None:
        anchor_ts = pd.to_datetime(trades["exit_ts"].max(), utc=True)
    rows = []
    for label, delta in WINDOWS:
        row: dict[str, object] = {"window": label, "anchor_end_utc": anchor_ts.strftime("%Y-%m-%d %H:%M UTC")}
        cutoff = anchor_ts - delta
        for lane in LANE_ORDER:
            sub = trades[(trades["lane"] == lane) & (trades["exit_ts"] >= cutoff)].copy()
            prefix = lane if lane != "gate_shadow" else "gate"
            if sub.empty:
                row[f"{prefix}_trades"] = 0
                row[f"{prefix}_net_total"] = np.nan
                row[f"{prefix}_ending_nav"] = np.nan
                row[f"{prefix}_win_rate"] = np.nan
                row[f"{prefix}_avg_trade"] = np.nan
            else:
                row[f"{prefix}_trades"] = int(len(sub))
                row[f"{prefix}_net_total"] = float((1.0 + sub["net_ret"]).prod() - 1.0)
                row[f"{prefix}_ending_nav"] = float((1.0 + sub["net_ret"]).prod())
                row[f"{prefix}_win_rate"] = float((sub["net_ret"] > 0).mean())
                row[f"{prefix}_avg_trade"] = float(sub["net_ret"].mean())
        rows.append(row)

    all_row: dict[str, object] = {"window": "all", "anchor_end_utc": anchor_ts.strftime("%Y-%m-%d %H:%M UTC")}
    for lane in LANE_ORDER:
        sub = trades[trades["lane"] == lane].copy()
        prefix = lane if lane != "gate_shadow" else "gate"
        if sub.empty:
            all_row[f"{prefix}_trades"] = 0
            all_row[f"{prefix}_net_total"] = np.nan
            all_row[f"{prefix}_ending_nav"] = np.nan
            all_row[f"{prefix}_win_rate"] = np.nan
            all_row[f"{prefix}_avg_trade"] = np.nan
        else:
            all_row[f"{prefix}_trades"] = int(len(sub))
            all_row[f"{prefix}_net_total"] = float((1.0 + sub["net_ret"]).prod() - 1.0)
            all_row[f"{prefix}_ending_nav"] = float((1.0 + sub["net_ret"]).prod())
            all_row[f"{prefix}_win_rate"] = float((sub["net_ret"] > 0).mean())
            all_row[f"{prefix}_avg_trade"] = float(sub["net_ret"].mean())
    rows.append(all_row)
    return pd.DataFrame(rows)


def build_asset_table(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame()
    rows = []
    for asset, sub in trades.groupby("asset"):
        row: dict[str, object] = {"asset": asset}
        for lane in LANE_ORDER:
            lane_sub = sub[sub["lane"] == lane].copy()
            prefix = lane if lane != "gate_shadow" else "gate"
            row[f"{prefix}_trades"] = int(len(lane_sub))
            row[f"{prefix}_net_total"] = float((1.0 + lane_sub["net_ret"]).prod() - 1.0) if len(lane_sub) else np.nan
            row[f"{prefix}_ending_nav"] = float((1.0 + lane_sub["net_ret"]).prod()) if len(lane_sub) else np.nan
            row[f"{prefix}_win_rate"] = float((lane_sub["net_ret"] > 0).mean()) if len(lane_sub) else np.nan
            row[f"{prefix}_avg_trade"] = float(lane_sub["net_ret"].mean()) if len(lane_sub) else np.nan
        rows.append(row)
    return pd.DataFrame(rows).sort_values("asset").reset_index(drop=True)


def build_recent_trade_table(trades: pd.DataFrame, *, limit: int = 24) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame()
    view = trades.sort_values(["exit_ts", "asset"], ascending=[False, True]).head(limit).copy()
    keep = [c for c in ["lane_label", "asset", "entry_ts", "exit_ts", "net_ret", "trigger_tf", "exit_reason"] if c in view.columns]
    view = view[keep]
    rename_map = {
        "lane_label": "lane",
        "entry_ts": "entry_ts_utc",
        "exit_ts": "exit_ts_utc",
        "net_ret": "trade_net_ret",
    }
    view = view.rename(columns=rename_map)
    if "entry_ts_utc" in view.columns:
        view["entry_ts_utc"] = view["entry_ts_utc"].map(fmt_ts)
    if "exit_ts_utc" in view.columns:
        view["exit_ts_utc"] = view["exit_ts_utc"].map(fmt_ts)
    return view


def build_pair_table(trades: pd.DataFrame, *, limit: int = 24) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame()
    base = trades[trades["candidate_id"] == BASELINE_ID][["asset", "entry_ts", "exit_ts", "net_ret"]].rename(columns={"net_ret": "baseline_net_ret"})
    gate = trades[trades["candidate_id"] == GATE_ID][["asset", "entry_ts", "exit_ts", "net_ret"]].rename(columns={"net_ret": "gate_shadow_net_ret"})
    paired = base.merge(gate, on=["asset", "entry_ts", "exit_ts"], how="outer").sort_values(["exit_ts", "asset"], ascending=[False, True]).head(limit).copy()
    if paired.empty:
        return paired
    paired["shadow_minus_baseline"] = paired["gate_shadow_net_ret"] - paired["baseline_net_ret"]
    paired["entry_ts"] = paired["entry_ts"].map(fmt_ts)
    paired["exit_ts"] = paired["exit_ts"].map(fmt_ts)
    return paired.rename(columns={"entry_ts": "entry_ts_utc", "exit_ts": "exit_ts_utc"})


def build_line_chart(df: pd.DataFrame, *, x_col: str, series: list[tuple[str, str, str]], title: str, y_mode: str = "pct") -> str:
    if df.empty:
        return chart_svg_placeholder(f"{title}：暂无数据")
    width, height = 1120, 360
    left, right, top, bottom = 70, 24, 28, 46
    plot_w = width - left - right
    plot_h = height - top - bottom

    x = pd.to_datetime(df[x_col], utc=True)
    x_num = x.astype("int64") / 1e9
    xmin, xmax = float(x_num.min()), float(x_num.max())
    xs = _scale(pd.Series(x_num), xmin, xmax, left, left + plot_w)

    y_vals = []
    for _, col, _ in series:
        if col in df.columns:
            y_vals.extend(pd.to_numeric(df[col], errors="coerce").dropna().tolist())
    if not y_vals:
        return chart_svg_placeholder(f"{title}：暂无有效数值")

    ymin, ymax = min(y_vals), max(y_vals)
    if y_mode == "pct":
        if ymin > 0:
            ymin = 0.0
        if ymax < 0:
            ymax = 0.0
        pad = max((ymax - ymin) * 0.08, 0.005)
    else:
        pad = max((ymax - ymin) * 0.08, 0.01)
    ymin -= pad
    ymax += pad

    def y_text(v: float) -> str:
        return pct(v) if y_mode == "pct" else nav_fmt(v)

    grid = []
    labels = []
    for frac in np.linspace(0, 1, 5):
        yv = ymin + (ymax - ymin) * frac
        yp = top + plot_h - (plot_h * frac)
        grid.append(f'<line x1="{left}" y1="{yp:.1f}" x2="{left+plot_w}" y2="{yp:.1f}" stroke="{COLORS["grid"]}" stroke-width="1" />')
        labels.append(f'<text x="{left-10}" y="{yp+4:.1f}" text-anchor="end" fill="{COLORS["muted"]}" font-size="12">{escape(y_text(yv))}</text>')

    zero_line = ""
    if y_mode == "pct" and ymin <= 0 <= ymax:
        zero_frac = (0 - ymin) / (ymax - ymin)
        zero_y = top + plot_h - plot_h * zero_frac
        zero_line = f'<line x1="{left}" y1="{zero_y:.1f}" x2="{left+plot_w}" y2="{zero_y:.1f}" stroke="#475569" stroke-width="1.2" stroke-dasharray="5 5" />'

    paths = []
    dots = []
    legend = []
    for i, (label, col, color) in enumerate(series):
        if col not in df.columns:
            continue
        ys_raw = pd.to_numeric(df[col], errors="coerce")
        ys = _scale(ys_raw, ymin, ymax, top + plot_h, top)
        pts = [(float(xs.iloc[idx]), float(ys.iloc[idx]), ys_raw.iloc[idx]) for idx in range(len(df)) if not pd.isna(ys_raw.iloc[idx])]
        if not pts:
            continue
        d = "M " + " L ".join(f"{xp:.1f} {yp:.1f}" for xp, yp, _ in pts)
        paths.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2.5" />')
        dots.extend(
            f'<circle cx="{xp:.1f}" cy="{yp:.1f}" r="3.4" fill="{color}"><title>{escape(label)} · {escape(y_text(float(rv)))}</title></circle>'
            for xp, yp, rv in pts
        )
        legend.append(
            f'<g transform="translate({left + i*220}, {height-14})"><line x1="0" y1="0" x2="26" y2="0" stroke="{color}" stroke-width="3" /><text x="34" y="4" fill="{COLORS["text"]}" font-size="13">{escape(label)}</text></g>'
        )

    xticks = []
    for frac in np.linspace(0, 1, min(6, max(2, len(df)))):
        idx = min(len(df) - 1, int(round((len(df) - 1) * frac)))
        xp = float(xs.iloc[idx])
        label = pd.to_datetime(df[x_col].iloc[idx], utc=True).strftime("%m-%d")
        xticks.append(f'<text x="{xp:.1f}" y="{height-24}" text-anchor="middle" fill="{COLORS["muted"]}" font-size="12">{label}</text>')

    return f"""
    <svg viewBox=\"0 0 {width} {height}\" class=\"chart\" role=\"img\" aria-label=\"{escape(title)}\">
      <rect x=\"0\" y=\"0\" width=\"{width}\" height=\"{height}\" rx=\"16\" fill=\"#0b1220\" stroke=\"#1f2937\" />
      <text x=\"24\" y=\"22\" fill=\"#e5e7eb\" font-size=\"18\" font-weight=\"700\">{escape(title)}</text>
      {''.join(grid)}
      {zero_line}
      {''.join(labels)}
      {''.join(paths)}
      {''.join(dots)}
      {''.join(xticks)}
      {''.join(legend)}
    </svg>
    """


def build_scatter_chart(df: pd.DataFrame, *, x_col: str, y_col: str, lane_col: str, title: str) -> str:
    if df.empty:
        return chart_svg_placeholder(f"{title}：暂无数据")
    width, height = 1120, 360
    left, right, top, bottom = 70, 24, 28, 46
    plot_w = width - left - right
    plot_h = height - top - bottom

    x = pd.to_datetime(df[x_col], utc=True)
    x_num = x.astype("int64") / 1e9
    xmin, xmax = float(x_num.min()), float(x_num.max())
    xs = _scale(pd.Series(x_num), xmin, xmax, left, left + plot_w)
    y_raw = pd.to_numeric(df[y_col], errors="coerce")
    ymin, ymax = float(y_raw.min()), float(y_raw.max())
    ymin = min(ymin, 0.0)
    ymax = max(ymax, 0.0)
    pad = max((ymax - ymin) * 0.1, 0.004)
    ymin -= pad
    ymax += pad
    ys = _scale(y_raw, ymin, ymax, top + plot_h, top)

    grid = []
    labels = []
    for frac in np.linspace(0, 1, 5):
        yv = ymin + (ymax - ymin) * frac
        yp = top + plot_h - (plot_h * frac)
        grid.append(f'<line x1="{left}" y1="{yp:.1f}" x2="{left+plot_w}" y2="{yp:.1f}" stroke="{COLORS["grid"]}" stroke-width="1" />')
        labels.append(f'<text x="{left-10}" y="{yp+4:.1f}" text-anchor="end" fill="{COLORS["muted"]}" font-size="12">{escape(pct(yv))}</text>')

    zero_frac = (0 - ymin) / (ymax - ymin) if ymax > ymin else 0.5
    zero_y = top + plot_h - plot_h * zero_frac
    dots = []
    lane_map = {"baseline": COLORS["baseline"], "gate_shadow": COLORS["gate_shadow"]}
    for idx in range(len(df)):
        lane = str(df[lane_col].iloc[idx])
        color = lane_map.get(lane, "#9ca3af")
        rv = float(y_raw.iloc[idx])
        stroke = COLORS["loss"] if rv < 0 else color
        fill = color if rv >= 0 else "#111827"
        tt = f"{df['lane_label'].iloc[idx]} | {df['asset'].iloc[idx]} | {pd.to_datetime(df[x_col].iloc[idx], utc=True).strftime('%Y-%m-%d %H:%M')} | {pct(rv)}"
        dots.append(f'<circle cx="{float(xs.iloc[idx]):.1f}" cy="{float(ys.iloc[idx]):.1f}" r="4.2" fill="{fill}" stroke="{stroke}" stroke-width="1.5"><title>{escape(tt)}</title></circle>')

    xticks = []
    for frac in np.linspace(0, 1, min(6, max(2, len(df)))):
        idx = min(len(df) - 1, int(round((len(df) - 1) * frac)))
        xp = float(xs.iloc[idx])
        label = pd.to_datetime(df[x_col].iloc[idx], utc=True).strftime("%m-%d")
        xticks.append(f'<text x="{xp:.1f}" y="{height-24}" text-anchor="middle" fill="{COLORS["muted"]}" font-size="12">{label}</text>')

    legend = (
        f'<g transform="translate({left}, {height-14})"><circle cx="0" cy="0" r="4" fill="{COLORS["baseline"]}" /><text x="12" y="4" fill="{COLORS["text"]}" font-size="13">baseline</text></g>'
        f'<g transform="translate({left+140}, {height-14})"><circle cx="0" cy="0" r="4" fill="{COLORS["gate_shadow"]}" /><text x="12" y="4" fill="{COLORS["text"]}" font-size="13">gate shadow</text></g>'
        f'<g transform="translate({left+310}, {height-14})"><circle cx="0" cy="0" r="4" fill="#111827" stroke="{COLORS["loss"]}" stroke-width="1.5" /><text x="12" y="4" fill="{COLORS["text"]}" font-size="13">negative trade</text></g>'
    )

    return f"""
    <svg viewBox=\"0 0 {width} {height}\" class=\"chart\" role=\"img\" aria-label=\"{escape(title)}\">
      <rect x=\"0\" y=\"0\" width=\"{width}\" height=\"{height}\" rx=\"16\" fill=\"#0b1220\" stroke=\"#1f2937\" />
      <text x=\"24\" y=\"22\" fill=\"#e5e7eb\" font-size=\"18\" font-weight=\"700\">{escape(title)}</text>
      {''.join(grid)}
      <line x1=\"{left}\" y1=\"{zero_y:.1f}\" x2=\"{left+plot_w}\" y2=\"{zero_y:.1f}\" stroke=\"#475569\" stroke-width=\"1.2\" stroke-dasharray=\"5 5\" />
      {''.join(labels)}
      {''.join(dots)}
      {''.join(xticks)}
      {legend}
    </svg>
    """


def build_event_timeline(events: pd.DataFrame, title: str) -> str:
    if events.empty:
        return chart_svg_placeholder(f"{title}：暂无 signal / rejection 事件")
    width, height = 1120, 250
    left, right, top, bottom = 70, 24, 28, 42
    plot_w = width - left - right
    baseline_y = 140

    x = pd.to_datetime(events["event_ts"], utc=True)
    x_num = x.astype("int64") / 1e9
    xmin, xmax = float(x_num.min()), float(x_num.max())
    xs = _scale(pd.Series(x_num), xmin, xmax, left, left + plot_w)

    marks = []
    for idx in range(len(events)):
        kind = str(events["kind"].iloc[idx])
        color = COLORS["signal"] if kind == "signal" else COLORS["reject"]
        y = baseline_y - 24 if kind == "signal" else baseline_y + 24
        symbol = str(events["symbol"].iloc[idx])
        label = str(events.get("reason", pd.Series([""] * len(events))).iloc[idx]) if kind == "reject" else str(events.get("side", pd.Series([""] * len(events))).iloc[idx])
        tt = f"{kind} | {symbol} | {pd.to_datetime(events['event_ts'].iloc[idx], utc=True).strftime('%Y-%m-%d %H:%M')} | {label}"
        marks.append(
            f'<line x1="{float(xs.iloc[idx]):.1f}" y1="{baseline_y}" x2="{float(xs.iloc[idx]):.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="2" />'
            f'<circle cx="{float(xs.iloc[idx]):.1f}" cy="{y:.1f}" r="5" fill="{color}"><title>{escape(tt)}</title></circle>'
        )

    xticks = []
    for frac in np.linspace(0, 1, min(6, max(2, len(events)))):
        idx = min(len(events) - 1, int(round((len(events) - 1) * frac)))
        xp = float(xs.iloc[idx])
        label = pd.to_datetime(events["event_ts"].iloc[idx], utc=True).strftime("%m-%d %H:%M")
        xticks.append(f'<text x="{xp:.1f}" y="{height-18}" text-anchor="middle" fill="{COLORS["muted"]}" font-size="11">{label}</text>')

    return f"""
    <svg viewBox=\"0 0 {width} {height}\" class=\"chart\" role=\"img\" aria-label=\"{escape(title)}\">
      <rect x=\"0\" y=\"0\" width=\"{width}\" height=\"{height}\" rx=\"16\" fill=\"#0b1220\" stroke=\"#1f2937\" />
      <text x=\"24\" y=\"22\" fill=\"#e5e7eb\" font-size=\"18\" font-weight=\"700\">{escape(title)}</text>
      <line x1=\"{left}\" y1=\"{baseline_y}\" x2=\"{left+plot_w}\" y2=\"{baseline_y}\" stroke=\"#334155\" stroke-width=\"1.2\" />
      <text x=\"{left-12}\" y=\"{baseline_y-20}\" text-anchor=\"end\" fill=\"{COLORS['signal']}\" font-size=\"12\">signal</text>
      <text x=\"{left-12}\" y=\"{baseline_y+28}\" text-anchor=\"end\" fill=\"{COLORS['reject']}\" font-size=\"12\">reject</text>
      {''.join(marks)}
      {''.join(xticks)}
      <g transform=\"translate({left}, {height-6})\"><circle cx=\"0\" cy=\"0\" r=\"4\" fill=\"{COLORS['signal']}\" /><text x=\"10\" y=\"4\" fill=\"{COLORS['text']}\" font-size=\"13\">recent signal</text></g>
      <g transform=\"translate({left+170}, {height-6})\"><circle cx=\"0\" cy=\"0\" r=\"4\" fill=\"{COLORS['reject']}\" /><text x=\"10\" y=\"4\" fill=\"{COLORS['text']}\" font-size=\"13\">recent rejection</text></g>
    </svg>
    """


def line_input_from_trades(trades: pd.DataFrame, *, value_col: str) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame()
    parts = []
    for lane in LANE_ORDER:
        sub = trades[trades["lane"] == lane][["exit_ts", value_col]].copy()
        if sub.empty:
            continue
        sub = sub.rename(columns={value_col: lane})
        parts.append(sub)
    if not parts:
        return pd.DataFrame()
    merged = parts[0]
    for part in parts[1:]:
        merged = merged.merge(part, on="exit_ts", how="outer")
    merged = merged.sort_values("exit_ts").reset_index(drop=True)
    return merged


def build_actual_views() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ledger = prepare_trades(read_csv(ACTUAL_LEDGER_PATH))
    if ledger.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    return ledger, build_summary(ledger), build_window_table(ledger), build_asset_table(ledger), build_recent_trade_table(ledger)


def build_replay_views() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    replay = prepare_trades(read_csv(REPLAY_PATH))
    if replay.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    return replay, build_summary(replay), build_window_table(replay), build_asset_table(replay), build_pair_table(replay)


def build_orderbook_views() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    status = read_csv(ORDERBOOK_STATUS_PATH)
    signals = read_csv(ORDERBOOK_SIGNALS_PATH)
    rejects = read_csv(ORDERBOOK_REJECTIONS_PATH)
    if not signals.empty:
        signals["event_ts"] = pd.to_datetime(signals["signal_ts_utc"], utc=True)
        signals["kind"] = "signal"
    if not rejects.empty:
        rejects["event_ts"] = pd.to_datetime(rejects["signal_ts_utc"], utc=True)
        rejects["kind"] = "reject"
    events = pd.concat([
        signals[[c for c in ["event_ts", "kind", "symbol", "side"] if c in signals.columns]] if not signals.empty else pd.DataFrame(),
        rejects[[c for c in ["event_ts", "kind", "symbol", "reason"] if c in rejects.columns]] if not rejects.empty else pd.DataFrame(),
    ], ignore_index=True)
    if not events.empty:
        events = events.sort_values("event_ts").reset_index(drop=True)
    return status, signals, rejects if not rejects.empty else pd.DataFrame(), events


def card_html(title: str, value: str, sub: str) -> str:
    return f"<div class='card stat'><div class='k'>{escape(title)}</div><div class='v'>{escape(value)}</div><div class='s'>{sub}</div></div>"


def build_dashboard() -> str:
    actual_trades, actual_summary, actual_windows, actual_assets, actual_recent = build_actual_views()
    replay_trades, replay_summary, replay_windows, replay_assets, replay_pairs = build_replay_views()
    orderbook_status, signals, rejects, events = build_orderbook_views()
    run_summary = read_csv(RUN_SUMMARY_PATH) if RUN_SUMMARY_PATH.suffix == '.csv' else None

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    actual_cards = []
    if not actual_summary.empty:
        for lane in LANE_ORDER:
            row = actual_summary[actual_summary["lane"] == lane]
            if row.empty:
                actual_cards.append(card_html(f"actual {LANE_LABELS[lane]}", "0 closed", "还没有真实 append-only closed trades 入账"))
                continue
            r = row.iloc[0]
            actual_cards.append(
                card_html(
                    f"actual {LANE_LABELS[lane]}",
                    pct(r["total_return"]),
                    f"trades={int(r['trades'])} · ending NAV={nav_fmt(r['ending_nav'])} · win rate={pct(r['win_rate'])} · avg/trade={pct(r['avg_trade'])}",
                )
            )
    else:
        actual_cards.append(card_html("actual paper", "no data", "当前 append-only ledger 里还没有 Rank29 closed trades"))

    replay_cards = []
    if not replay_summary.empty:
        for lane in LANE_ORDER:
            row = replay_summary[replay_summary["lane"] == lane]
            if row.empty:
                continue
            r = row.iloc[0]
            replay_cards.append(
                card_html(
                    f"replay {LANE_LABELS[lane]}",
                    pct(r["total_return"]),
                    f"trades={int(r['trades'])} · ending NAV={nav_fmt(r['ending_nav'])} · win rate={pct(r['win_rate'])} · avg/trade={pct(r['avg_trade'])}",
                )
            )

    if not orderbook_status.empty:
        row = orderbook_status.iloc[0]
        replay_cards.append(
            card_html(
                "orderbook shadow",
                pct(row.get("lifetime_total_return")),
                f"closed={int(row.get('closed_trades', 0) or 0)} · recent signals={int(row.get('recent_signal_count', 0) or 0)} · recent rejects={int(row.get('recent_rejection_count', 0) or 0)}",
            )
        )

    actual_nav_chart = build_line_chart(
        line_input_from_trades(actual_trades, value_col="nav"),
        x_col="exit_ts",
        series=[("actual baseline NAV", "baseline", COLORS["baseline"]), ("actual gate shadow NAV", "gate_shadow", COLORS["gate_shadow"])],
        title="真实 append-only paper：净值折线图（每个点就是一笔 closed trade）",
        y_mode="nav",
    ) if not actual_trades.empty else chart_svg_placeholder("真实 append-only paper：暂无 closed trades")

    actual_scatter = build_scatter_chart(
        actual_trades,
        x_col="exit_ts",
        y_col="net_ret",
        lane_col="lane",
        title="真实 append-only paper：每笔交易盈亏点位图",
    ) if not actual_trades.empty else chart_svg_placeholder("真实 append-only paper：暂无逐笔盈亏点位")

    replay_nav_chart = build_line_chart(
        line_input_from_trades(replay_trades, value_col="nav"),
        x_col="exit_ts",
        series=[("replay baseline NAV", "baseline", COLORS["baseline"]), ("replay gate shadow NAV", "gate_shadow", COLORS["gate_shadow"])],
        title="历史 replay overlay：净值折线图（只用于研究，不是当前真实 paper）",
        y_mode="nav",
    ) if not replay_trades.empty else chart_svg_placeholder("历史 replay overlay：暂无数据")

    replay_scatter = build_scatter_chart(
        replay_trades,
        x_col="exit_ts",
        y_col="net_ret",
        lane_col="lane",
        title="历史 replay overlay：每笔交易盈亏点位图",
    ) if not replay_trades.empty else chart_svg_placeholder("历史 replay overlay：暂无逐笔盈亏点位")

    orderbook_chart = build_event_timeline(events, "orderbook shadow：最近 signal / rejection 事件时间线")
    orderbook_note = ""
    if not orderbook_status.empty and int(orderbook_status.iloc[0].get("closed_trades", 0) or 0) == 0:
        orderbook_note = (
            "<p class='warn'>注意：orderbook shadow 当前还没有 closed trades，所以它现在不能像真实 paper 一样画已成交净值曲线。"
            "我在这里先用 signal / rejection 时间线展示它目前卡在执行层的哪个环节。</p>"
        )

    signals_slice = pd.DataFrame()
    if not signals.empty:
        signals_slice = signals.copy().sort_values("signal_ts_utc", ascending=False).head(10)
        keep = [c for c in ["symbol", "signal_ts_utc", "planned_exit_ts_utc", "side", "trigger_tf", "composite_trend"] if c in signals_slice.columns]
        signals_slice = signals_slice[keep]

    rejects_slice = pd.DataFrame()
    if not rejects.empty:
        rejects_slice = rejects.copy().sort_values("signal_ts_utc", ascending=False).head(10)
        keep = [c for c in ["symbol", "signal_ts_utc", "side", "reason", "entry_age_minutes"] if c in rejects_slice.columns]
        rejects_slice = rejects_slice[keep]

    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Rank29 actual paper vs replay vs shadows</title>
  <style>
    body {{ font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #020617; color: #e5e7eb; }}
    .wrap {{ max-width: 1260px; margin: 0 auto; padding: 32px 20px 64px; }}
    h1,h2,h3 {{ margin: 0 0 12px; }}
    p, li {{ line-height: 1.65; }}
    .muted {{ color: #94a3b8; }}
    .warn {{ color: #fbbf24; }}
    .good {{ color: #86efac; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; margin: 18px 0 28px; }}
    .card {{ background: #0f172a; border: 1px solid #1f2937; border-radius: 16px; padding: 16px 18px; }}
    .hero {{ border-color: #334155; background: linear-gradient(180deg, #0f172a 0%, #0b1220 100%); }}
    .stat .k {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: .05em; }}
    .stat .v {{ font-size: 30px; font-weight: 800; margin-top: 8px; }}
    .stat .s {{ margin-top: 8px; color: #9ca3af; font-size: 13px; }}
    .chart {{ width: 100%; height: auto; display: block; margin: 10px 0 6px; }}
    table {{ width: 100%; border-collapse: collapse; background: #0f172a; border: 1px solid #1f2937; border-radius: 16px; overflow: hidden; margin: 12px 0 28px; }}
    th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid #1f2937; font-size: 13px; vertical-align: top; }}
    th {{ background: #111827; color: #cbd5e1; position: sticky; top: 0; }}
    tr:last-child td {{ border-bottom: none; }}
    code {{ background: #111827; color: #cbd5e1; padding: 2px 6px; border-radius: 6px; }}
    a {{ color: #60a5fa; }}
    .list li {{ margin: 6px 0; }}
    .section {{ margin-top: 30px; }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <p class=\"muted\">Generated: {generated}</p>
    <p><a href=\"../rank29_monitoring_hub/report.html\">← 返回 Rank29 archive / audit</a> ｜ <a href=\"../scout_rank29_trendline_breakout_navigator_15m/report.html\">Rank29 主报告</a></p>
    <h1>Rank29 · actual paper first, causal shadow second</h1>
    <p>这页现在降级为 <b>research / archive</b> 视角：最上面只看 <b>真实 append-only paper</b>，下面放的是 <b>causal / live-safe shadow</b> 和 <b>orderbook shadow</b>。这样你不会再把“事后回看很强”误读成“当时 live 本来就应该做出来”。现在 Rank29 已停实盘并降为 <b>P0 archived</b>；总览审计请看 <a href="../rank29_monitoring_hub/report.html">Rank29 archive / audit</a>，真钱 100u lane 的留档细节在 <a href="../rank29_gate_live/report.html">rank29 retired debug</a>。</p>

    <div class=\"card hero\">
      <h2>先看读法</h2>
      <ul class=\"list muted\">
        <li><b>真实 append-only paper</b>：来自 <code>manual_narrow_paper_closed_trades.csv</code>，这是我们之前发现 Rank29 最近偏弱、因此去找 regime 的那条真实跟踪线。</li>
        <li><b>causal / live-safe shadow</b>：来自 <code>rank29_shadow_trade_view.csv</code>，它按当时可见 bars 重放，不再允许第二天把昨天的信号补出来；因此更适合拿来和 live 做 apples-to-apples 对照。</li>
        <li><b>orderbook shadow</b>：回答执行层问题，不跟真实 paper 做 apples-to-apples 的净值比较。</li>
        <li><b>gate live 100u</b>：真钱 lane 单独看，入口在 <a href="../rank29_gate_live/report.html">rank29_gate_live/report.html</a>。</li>
      </ul>
    </div>

    <div class=\"section\">
      <h2>1) 真实 append-only paper（重点）</h2>
      <p class=\"muted\">这一部分才是你最该盯的：净值折线图里每个点都是一笔真实 closed trade；下方的时间窗表直接回答你问的 <code>12h / 1d / 3d / 7d / 14d / 30d</code> 这段时间到底盈亏如何。</p>
      <div class=\"grid\">{''.join(actual_cards)}</div>
      {actual_nav_chart}
      {actual_scatter}
      <h3>真实 paper：分时间窗表现</h3>
      {render_table(actual_windows, percent_cols={'baseline_net_total','baseline_win_rate','baseline_avg_trade','gate_net_total','gate_win_rate','gate_avg_trade'}, nav_cols={'baseline_ending_nav','gate_ending_nav'}, digits_cols={'baseline_trades':0,'gate_trades':0})}
      <h3>真实 paper：按资产拆开看</h3>
      {render_table(actual_assets, percent_cols={'baseline_net_total','baseline_win_rate','baseline_avg_trade','gate_net_total','gate_win_rate','gate_avg_trade'}, nav_cols={'baseline_ending_nav','gate_ending_nav'}, digits_cols={'baseline_trades':0,'gate_trades':0})}
      <h3>真实 paper：最近 closed trades</h3>
      {render_table(actual_recent, percent_cols={'trade_net_ret'})}
    </div>

    <div class=\"section\">
      <h2>2) causal shadow overlay（研究辅助，但已去掉未来函数）</h2>
      <p class=\"muted\">这一部分保留，是为了回答“如果用 live-safe 口径重放，baseline 与 gate shadow 的长期形状分别如何”。它仍是研究辅助，但现在已经去掉了事后补信号的问题，更适合和 live 对照。</p>
      <div class=\"grid\">{''.join(replay_cards)}</div>
      {replay_nav_chart}
      {replay_scatter}
      <h3>causal shadow：分时间窗表现</h3>
      {render_table(replay_windows, percent_cols={'baseline_net_total','baseline_win_rate','baseline_avg_trade','gate_net_total','gate_win_rate','gate_avg_trade'}, nav_cols={'baseline_ending_nav','gate_ending_nav'}, digits_cols={'baseline_trades':0,'gate_trades':0})}
      <h3>causal shadow：按资产拆开看</h3>
      {render_table(replay_assets, percent_cols={'baseline_net_total','baseline_win_rate','baseline_avg_trade','gate_net_total','gate_win_rate','gate_avg_trade'}, nav_cols={'baseline_ending_nav','gate_ending_nav'}, digits_cols={'baseline_trades':0,'gate_trades':0})}
      <h3>causal shadow：最近 baseline vs gate 配对交易</h3>
      {render_table(replay_pairs, percent_cols={'baseline_net_ret','gate_shadow_net_ret','shadow_minus_baseline'})}
    </div>

    <div class=\"section\">
      <h2>3) orderbook shadow（执行层）</h2>
      <p class=\"muted\">这部分专门回答：如果以后要往更真实的执行推进，最近 signal 有没有被盘口吃掉、还是大多被拒掉 / 过期了。它不和上面的真实 paper 直接拼成同一条净值曲线。</p>
      {orderbook_note}
      {orderbook_chart}
      <h3>最近 signals</h3>
      {render_table(signals_slice)}
      <h3>最近 rejections</h3>
      {render_table(rejects_slice, digits_cols={'entry_age_minutes':1})}
    </div>

    <div class=\"section\">
      <h2>Artifacts / data sources</h2>
      <ul class=\"list\">
        <li><a href=\"../../artifacts/manual_narrow_paper_lanes/manual_narrow_paper_closed_trades.csv\">manual_narrow_paper_closed_trades.csv</a>（真实 append-only paper）</li>
        <li><a href=\"../../artifacts/manual_narrow_paper_lanes/rank29_shadow_trade_view.csv\">rank29_shadow_trade_view.csv</a>（causal / live-safe shadow）</li>
        <li><a href=\"../../artifacts/manual_narrow_paper_lanes/manual_narrow_paper_status.csv\">manual_narrow_paper_status.csv</a></li>
        <li><a href=\"../../artifacts/rank29_orderbook_shadow/shadow_status.csv\">shadow_status.csv</a></li>
        <li><a href=\"../../artifacts/rank29_orderbook_shadow/shadow_recent_signals.csv\">shadow_recent_signals.csv</a></li>
        <li><a href=\"../../artifacts/rank29_orderbook_shadow/shadow_recent_rejections.csv\">shadow_recent_rejections.csv</a></li>
      </ul>
    </div>
  </div>
</body>
</html>
"""
    return html


def main() -> int:
    ensure_dir(SITE_DIR)
    OUT_PATH.write_text(build_dashboard(), encoding="utf-8")
    print(OUT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
