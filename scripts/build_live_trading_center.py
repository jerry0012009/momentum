#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SITE_DIR = ROOT / "reports" / "site" / "factors" / "live_trading_center"
OUT_PATH = SITE_DIR / "report.html"

R29_STATE_PATH = ROOT / "reports" / "artifacts" / "rank29_gate_live" / "rank29_gate_live_state.json"
R29_STATUS_PATH = ROOT / "reports" / "artifacts" / "rank29_gate_live" / "rank29_gate_live_status.json"
R29_COMPARE_PATH = ROOT / "reports" / "artifacts" / "rank29_gate_live" / "rank29_gate_live_vs_shadow.csv"
R29_SHADOW_PATH = ROOT / "reports" / "artifacts" / "manual_narrow_paper_lanes" / "rank29_shadow_trade_view.csv"

C3_STATUS_PATH = ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase6_status.json"
C3_RUN_PATH = ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase6_last_run_summary.json"
C3_STATE_PATH = ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase6_state.json"
C3_CLOSED_PATH = ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase6_recent_closed_trades.json"
C3_SHADOW_PATH = ROOT / "reports" / "artifacts" / "rank32b_shadow_beat" / "paper_trades.json"
C3_SHADOW_SUMMARY_PATH = ROOT / "reports" / "artifacts" / "rank32b_shadow_beat" / "paper_summary.json"

G32_STATUS_PATH = ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_status.json"
G32_RUN_PATH = ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_last_run_summary.json"
G32_STATE_PATH = ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_state.json"
G32_CLOSED_PATH = ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_recent_closed_trades.json"
G32_COMPARE_PATH = ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_vs_shadow.csv"
G32_SHADOW_PATH = ROOT / "reports" / "artifacts" / "rank32b_shadow_global_winner" / "paper_trades.json"
G32_SHADOW_SUMMARY_PATH = ROOT / "reports" / "artifacts" / "rank32b_shadow_global_winner" / "paper_summary.json"

RANGE_OPTIONS: list[tuple[str, str, int | None]] = [
    ("7d", "近7天", 7),
    ("30d", "近30天", 30),
    ("90d", "近90天", 90),
    ("all", "全部", None),
]
DEFAULT_RANGE_KEY = "30d"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def fmt_ts(v: Any) -> str:
    if v is None or v == "" or pd.isna(v):
        return "-"
    try:
        return pd.to_datetime(v, utc=True).strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return str(v)


def money(v: Any, digits: int = 3) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f} USDT"


def pct(v: Any, digits: int = 1) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def num(v: Any, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def safe_float(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def summarize(df: pd.DataFrame, pnl_col: str = "pnl_usdt") -> dict[str, Any]:
    if df.empty or pnl_col not in df.columns:
        return {"trades": 0, "wins": 0, "losses": 0, "win_rate": None, "cum_pnl": 0.0}
    pnl = safe_float(df[pnl_col]).fillna(0.0)
    trades = len(df)
    wins = int((pnl > 0).sum())
    losses = int((pnl < 0).sum())
    return {
        "trades": trades,
        "wins": wins,
        "losses": losses,
        "win_rate": (wins / trades) if trades else None,
        "cum_pnl": float(pnl.sum()),
    }


def closed_to_df(
    rows: list[dict[str, Any]], *, ts_col: str, pnl_cols: list[str], symbol_col: str = "symbol", side_col: str = "side", reason_col: str = "exit_reason"
) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=["ts", "symbol", "side", "pnl_usdt", "exit_reason"])
    df = pd.DataFrame(rows).copy()
    df["ts"] = pd.to_datetime(df.get(ts_col), utc=True, errors="coerce")
    pnl = None
    for col in pnl_cols:
        if col in df.columns:
            series = safe_float(df[col])
            pnl = series if pnl is None else pnl.fillna(series)
    if pnl is None:
        pnl = pd.Series([0.0] * len(df), index=df.index, dtype=float)
    df["pnl_usdt"] = pnl.fillna(0.0)
    df["symbol"] = df.get(symbol_col, "").astype(str)
    df["side"] = df.get(side_col, "").astype(str)
    df["exit_reason"] = df.get(reason_col, "").astype(str)
    df = df[df["ts"].notna()].sort_values("ts").reset_index(drop=True)
    return df[["ts", "symbol", "side", "pnl_usdt", "exit_reason"] + [c for c in ["signal_id", "entry_time", "exit_time"] if c in df.columns]]


def shadow_to_df(rows: list[dict[str, Any]], *, ret_col: str, ts_col: str, notional: float) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=["ts", "symbol", "side", "pnl_usdt", "exit_reason"])
    df = pd.DataFrame(rows).copy()
    if "paper_trade_state" in df.columns:
        df = df[df["paper_trade_state"] == "closed"].copy()
    elif "status" in df.columns:
        df = df[df["status"].isin(["closed", "realized"])].copy()
    if df.empty:
        return pd.DataFrame(columns=["ts", "symbol", "side", "pnl_usdt", "exit_reason"])
    df["ts"] = pd.to_datetime(df.get(ts_col), utc=True, errors="coerce")
    df["pnl_usdt"] = safe_float(df.get(ret_col, 0.0)).fillna(0.0) * float(notional)
    df["symbol"] = df.get("symbol", "").astype(str)
    df["side"] = df.get("side", "").astype(str)
    df["exit_reason"] = df.get("exit_reason", "shadow_close").astype(str)
    df = df[df["ts"].notna()].sort_values("ts").reset_index(drop=True)
    return df[["ts", "symbol", "side", "pnl_usdt", "exit_reason"] + [c for c in ["signal_id"] if c in df.columns]]


def rank29_shadow_df() -> pd.DataFrame:
    df = read_csv(R29_SHADOW_PATH)
    if df.empty:
        return pd.DataFrame(columns=["ts", "symbol", "side", "pnl_usdt", "exit_reason"])
    df = df[df.get("candidate_id", "") == "rank29_trendline_breakout_gate_shadow"].copy()
    if df.empty:
        return pd.DataFrame(columns=["ts", "symbol", "side", "pnl_usdt", "exit_reason"])
    df["ts"] = pd.to_datetime(df.get("exit_ts"), utc=True, errors="coerce")
    df["pnl_usdt"] = safe_float(df.get("net_ret", 0.0)).fillna(0.0) * 100.0
    symbol_series = df["symbol"] if "symbol" in df.columns else pd.Series([None] * len(df), index=df.index)
    asset_series = df["asset"] if "asset" in df.columns else pd.Series([None] * len(df), index=df.index)
    side_series = df["direction"] if "direction" in df.columns else pd.Series([None] * len(df), index=df.index)
    exit_reason_series = df["exit_reason"] if "exit_reason" in df.columns else pd.Series([None] * len(df), index=df.index)
    df["symbol"] = symbol_series.fillna(asset_series).astype(str)
    df["side"] = side_series.fillna("").astype(str)
    df["exit_reason"] = exit_reason_series.fillna("shadow_close").astype(str)
    df = df[df["ts"].notna()].sort_values("ts").reset_index(drop=True)
    return df[["ts", "symbol", "side", "pnl_usdt", "exit_reason"]]


def filter_df_by_days(df: pd.DataFrame, days: int | None, now_ts: pd.Timestamp) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    if days is None or "ts" not in df.columns:
        return df.copy().reset_index(drop=True)
    cutoff = now_ts - pd.Timedelta(days=days)
    work = df.copy()
    work["ts"] = pd.to_datetime(work["ts"], utc=True, errors="coerce")
    work = work[work["ts"] >= cutoff]
    return work.reset_index(drop=True)


def filter_df_since_ts(df: pd.DataFrame, since_ts: pd.Timestamp | None) -> pd.DataFrame:
    if df.empty or since_ts is None or "ts" not in df.columns:
        return df.copy().reset_index(drop=True)
    work = df.copy()
    work["ts"] = pd.to_datetime(work["ts"], utc=True, errors="coerce")
    work = work[work["ts"] >= since_ts]
    return work.reset_index(drop=True)


def infer_compare_start_ts(live_df: pd.DataFrame, open_df: pd.DataFrame) -> pd.Timestamp | None:
    candidates: list[pd.Timestamp] = []
    if not live_df.empty and "ts" in live_df.columns:
        live_ts = pd.to_datetime(live_df["ts"], utc=True, errors="coerce").dropna()
        if not live_ts.empty:
            candidates.append(live_ts.min())
    if not open_df.empty and "entry_time" in open_df.columns:
        open_ts = pd.to_datetime(open_df["entry_time"], utc=True, errors="coerce").dropna()
        if not open_ts.empty:
            candidates.append(open_ts.min())
    if not candidates:
        return None
    return min(candidates)


def curve_series(df: pd.DataFrame, label: str, color: str) -> dict[str, Any] | None:
    if df.empty:
        return None
    work = df.sort_values("ts").copy().reset_index(drop=True)
    work["ts"] = pd.to_datetime(work["ts"], utc=True, errors="coerce")
    work = work[work["ts"].notna()].reset_index(drop=True)
    if work.empty:
        return None
    work["cum_pnl"] = safe_float(work["pnl_usdt"]).fillna(0.0).cumsum()
    points = [{"ts": ts.isoformat(), "value": float(val)} for ts, val in zip(work["ts"], work["cum_pnl"], strict=False)]
    return {"label": label, "color": color, "points": points}


def line_chart_svg(series_list: list[dict[str, Any] | None], *, width: int = 760, height: int = 220) -> str:
    valid = [s for s in series_list if s and s.get("points")]
    if not valid:
        return '<div class="empty">当前时间窗口内暂无可绘制的收益曲线。</div>'

    all_y = [0.0]
    all_t: list[pd.Timestamp] = []
    normalized: list[dict[str, Any]] = []
    for s in valid:
        pts: list[tuple[pd.Timestamp, float]] = []
        for p in s.get("points", []):
            ts = pd.to_datetime(p.get("ts"), utc=True, errors="coerce")
            val = p.get("value")
            if pd.isna(ts) or val is None:
                continue
            pts.append((ts, float(val)))
            all_y.append(float(val))
            all_t.append(ts)
        if pts:
            normalized.append({**s, "points_norm": pts})
    if not normalized or not all_t:
        return '<div class="empty">当前时间窗口内暂无可绘制的收益曲线。</div>'

    ymin, ymax = min(all_y), max(all_y)
    span = max(ymax - ymin, 1e-9)
    ymin -= span * 0.12 + 1e-9
    ymax += span * 0.12 + 1e-9
    plot_x, plot_y, plot_w, plot_h = 44, 16, width - 56, height - 38
    tmin, tmax = min(all_t), max(all_t)
    trange = max((tmax - tmin).total_seconds(), 1.0)

    def xy(ts: pd.Timestamp, val: float) -> tuple[float, float]:
        if trange <= 1.0:
            x = plot_x + plot_w / 2
        else:
            x = plot_x + (((ts - tmin).total_seconds()) / trange) * plot_w
        y = plot_y + plot_h - ((val - ymin) / (ymax - ymin)) * plot_h
        return x, y

    zero_y = xy(tmin, 0.0)[1]
    parts = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" role="img">',
        f'<line x1="{plot_x}" y1="{zero_y:.2f}" x2="{plot_x + plot_w}" y2="{zero_y:.2f}" stroke="#334155" stroke-dasharray="4 4" />',
        f'<rect x="{plot_x}" y="{plot_y}" width="{plot_w}" height="{plot_h}" rx="10" fill="none" stroke="#1f2937" />',
    ]
    legend_x = plot_x
    for s in normalized:
        pts = [xy(ts, val) for ts, val in s["points_norm"]]
        if len(pts) == 1:
            x, y = pts[0]
            parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4.2" fill="{s["color"]}" />')
        else:
            path = " ".join(("M" if i == 0 else "L") + f" {x:.2f} {y:.2f}" for i, (x, y) in enumerate(pts))
            parts.append(f'<path d="{path}" fill="none" stroke="{s["color"]}" stroke-width="2.4" />')
            for x, y in pts:
                parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="2.6" fill="{s["color"]}" />')
        last_x, last_y = pts[-1]
        parts.append(f'<circle cx="{last_x:.2f}" cy="{last_y:.2f}" r="3.4" fill="{s["color"]}" />')
        parts.append(f'<rect x="{legend_x}" y="{height - 16}" width="10" height="10" rx="3" fill="{s["color"]}" />')
        parts.append(f'<text x="{legend_x + 16}" y="{height - 7}" fill="#cbd5e1" font-size="12">{escape(str(s["label"]))}</text>')
        legend_x += 138
    parts.append(f'<text x="6" y="{plot_y + 10}" fill="#94a3b8" font-size="11">{money(ymax, 1)}</text>')
    parts.append(f'<text x="6" y="{zero_y - 4:.2f}" fill="#64748b" font-size="11">0</text>')
    parts.append(f'<text x="6" y="{plot_y + plot_h}" fill="#94a3b8" font-size="11">{money(ymin, 1)}</text>')
    parts.append(f'<text x="{plot_x}" y="{height - 24}" fill="#64748b" font-size="11">{escape(tmin.strftime("%m-%d %H:%M"))}</text>')
    parts.append(f'<text x="{plot_x + plot_w - 74}" y="{height - 24}" fill="#64748b" font-size="11">{escape(tmax.strftime("%m-%d %H:%M"))}</text>')
    parts.append("</svg>")
    return "".join(parts)


def trade_strip_svg(df: pd.DataFrame, *, width: int = 760, height: int = 120) -> str:
    if df.empty:
        return '<div class="empty">当前时间窗口内暂无已平仓逐笔交易。</div>'
    pnl = safe_float(df["pnl_usdt"]).fillna(0.0).tolist()
    max_abs = max(max(abs(v) for v in pnl), 1e-9)
    plot_x, plot_y, plot_w, plot_h = 28, 12, width - 40, height - 24
    center_y = plot_y + plot_h / 2
    parts = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" role="img">',
        f'<line x1="{plot_x}" y1="{center_y:.2f}" x2="{plot_x + plot_w}" y2="{center_y:.2f}" stroke="#334155" stroke-dasharray="4 4" />',
    ]
    total = len(pnl)
    for i, value in enumerate(pnl):
        x = plot_x + (plot_w / max(total - 1, 1)) * i if total > 1 else plot_x + plot_w / 2
        y = center_y - (value / max_abs) * (plot_h * 0.38)
        color = "#22c55e" if value > 0 else ("#ef4444" if value < 0 else "#94a3b8")
        parts.append(f'<line x1="{x:.2f}" y1="{center_y:.2f}" x2="{x:.2f}" y2="{y:.2f}" stroke="{color}" stroke-width="2.2" />')
        parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3" fill="{color}" />')
    parts.append(f'<text x="4" y="14" fill="#94a3b8" font-size="11">win</text>')
    parts.append(f'<text x="4" y="{center_y + 4:.2f}" fill="#64748b" font-size="11">0</text>')
    parts.append(f'<text x="4" y="{height - 6}" fill="#94a3b8" font-size="11">loss</text>')
    parts.append("</svg>")
    return "".join(parts)


def aggregate_live_closed(strategies: list[dict[str, Any]]) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    for s in strategies:
        df = s["live_df"].copy()
        if df.empty:
            continue
        df.insert(0, "strategy", s["title"])
        parts.append(df)
    if not parts:
        return pd.DataFrame(columns=["strategy", "ts", "symbol", "side", "pnl_usdt", "exit_reason"])
    out = pd.concat(parts, ignore_index=True)
    out["ts"] = pd.to_datetime(out["ts"], utc=True, errors="coerce")
    out = out[out["ts"].notna()].sort_values("ts").reset_index(drop=True)
    return out


def daily_pnl_bar_svg(df: pd.DataFrame, *, width: int = 760, height: int = 220) -> str:
    if df.empty:
        return '<div class="empty">当前时间窗口内暂无按日统计的已平仓收益。</div>'
    work = df.copy()
    work["ts"] = pd.to_datetime(work["ts"], utc=True, errors="coerce")
    work = work[work["ts"].notna()].copy()
    if work.empty:
        return '<div class="empty">当前时间窗口内暂无按日统计的已平仓收益。</div>'
    work["day"] = work["ts"].dt.strftime("%m-%d")
    daily = work.groupby("day", as_index=False)["pnl_usdt"].sum()
    vals = pd.to_numeric(daily["pnl_usdt"], errors="coerce").fillna(0.0).tolist()
    if not vals:
        return '<div class="empty">当前时间窗口内暂无按日统计的已平仓收益。</div>'
    max_abs = max(max(abs(v) for v in vals), 1e-9)
    plot_x, plot_y, plot_w, plot_h = 40, 16, width - 52, height - 46
    center_y = plot_y + plot_h / 2
    bar_w = max(min(plot_w / max(len(vals), 1) * 0.68, 26), 6)
    gap = plot_w / max(len(vals), 1)
    parts = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" role="img">',
        f'<line x1="{plot_x}" y1="{center_y:.2f}" x2="{plot_x + plot_w}" y2="{center_y:.2f}" stroke="#334155" stroke-dasharray="4 4" />',
    ]
    for i, (_, row) in enumerate(daily.iterrows()):
        value = float(row["pnl_usdt"])
        x = plot_x + gap * i + (gap - bar_w) / 2
        h = abs(value) / max_abs * (plot_h * 0.42)
        y = center_y - h if value >= 0 else center_y
        color = "#22c55e" if value > 0 else ("#ef4444" if value < 0 else "#94a3b8")
        parts.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_w:.2f}" height="{max(h,1.5):.2f}" rx="3" fill="{color}" />')
        if len(daily) <= 16 or i % max(len(daily) // 8, 1) == 0 or i == len(daily) - 1:
            parts.append(f'<text x="{x + bar_w / 2:.2f}" y="{height - 12}" text-anchor="middle" fill="#64748b" font-size="11">{escape(str(row["day"]))}</text>')
    parts.append(f'<text x="4" y="{plot_y + 10}" fill="#94a3b8" font-size="11">{money(max_abs, 1)}</text>')
    parts.append(f'<text x="4" y="{center_y + 4:.2f}" fill="#64748b" font-size="11">0</text>')
    parts.append(f'<text x="4" y="{plot_y + plot_h}" fill="#94a3b8" font-size="11">-{money(max_abs, 1)}</text>')
    parts.append("</svg>")
    return "".join(parts)


def metric_card(title: str, value: str, sub: str) -> str:
    return f"<div class='metric'><div class='k'>{escape(title)}</div><div class='v'>{escape(value)}</div><div class='s'>{sub}</div></div>"


def table_html(df: pd.DataFrame, *, strategy_colored: bool = False) -> str:
    if df.empty:
        return '<p class="empty">暂无数据。</p>'
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows: list[str] = []
    for _, row in df.iterrows():
        row_class = ""
        pnl_val = None
        if "pnl_usdt" in df.columns:
            try:
                pnl_val = float(row.get("pnl_usdt"))
            except Exception:
                pnl_val = None
        if pnl_val is not None:
            row_class = "pos" if pnl_val > 0 else ("neg" if pnl_val < 0 else "flat")
        tds = []
        for col in df.columns:
            value = row[col]
            if col.endswith("time") or col == "ts":
                text = fmt_ts(value)
            elif col == "pnl_usdt":
                text = money(value, 3)
            elif col == "win_rate":
                text = pct(value, 1)
            else:
                text = str(value)
            cls = "strategy" if strategy_colored and col == "strategy" else ""
            tds.append(f"<td class='{cls}'>{escape(text)}</td>")
        rows.append(f"<tr class='{row_class}'>{''.join(tds)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def build_strategy_section(spec: dict[str, Any]) -> str:
    live_summary = summarize(spec["live_df"])
    shadow_summary = summarize(spec["shadow_df"])
    detail_link = spec["detail_link"]
    lane_label = "live closed" if spec.get("is_active", True) else "archived live"
    pnl_label = "live cumulative pnl" if spec.get("is_active", True) else "legacy live pnl"
    notice_html = ""
    if spec.get("notice"):
        notice_html = f"<p class='muted' style='margin-top:8px;color:#fca5a5;'>{escape(spec['notice'])}</p>"
    metrics = "".join(
        [
            metric_card(lane_label, str(live_summary["trades"]), f"wins={live_summary['wins']} · win rate={pct(live_summary['win_rate'])}"),
            metric_card(pnl_label, money(live_summary["cum_pnl"]), f"open={len(spec['open_df'])} · last run={escape(fmt_ts(spec['last_run']))}"),
            metric_card("shadow reference", money(shadow_summary["cum_pnl"]), f"closed={shadow_summary['trades']} · win rate={pct(shadow_summary['win_rate'])}"),
            metric_card("pairing mode", spec["pairing_mode"], f"warnings={spec['warnings']} · <a href='{detail_link}'>打开详页</a>"),
        ]
    )

    recent_live = spec["live_df"].copy().sort_values("ts", ascending=False).head(12)
    if not recent_live.empty:
        recent_live["result"] = recent_live["pnl_usdt"].map(lambda x: "win" if x > 0 else ("loss" if x < 0 else "flat"))
        recent_live = recent_live[[c for c in ["ts", "symbol", "side", "pnl_usdt", "result", "exit_reason"] if c in recent_live.columns]]

    open_df = spec["open_df"].copy()
    if not open_df.empty:
        open_df = open_df[[c for c in ["symbol", "side", "entry_time", "entry_price", "timeout_at"] if c in open_df.columns]]

    curve_note = spec.get("curve_note") or "看累计 PnL 是否大体跟得上 shadow；若口径不是 exact pair，这里会明确标记为 reference。"

    return f"""
<section class='panel'>
  <div class='panel-head'>
    <div>
      <h2>{escape(spec['title'])}</h2>
      <p class='muted'>{escape(spec['subtitle'])}</p>
      {notice_html}
    </div>
    <div class='pill'>{escape(spec['pairing_badge'])}</div>
  </div>
  <div class='metric-grid'>{metrics}</div>
  <div class='viz-grid'>
    <div class='viz-card'>
      <h3>收益曲线：live vs shadow</h3>
      <p class='muted'>{escape(curve_note)}</p>
      {line_chart_svg([spec['live_curve'], spec['shadow_curve']])}
    </div>
    <div class='viz-card'>
      <h3>逐笔交易：赢 / 亏</h3>
      <p class='muted'>每一根就是一笔已平仓 live trade：向上是赢，向下是亏。</p>
      {trade_strip_svg(spec['live_df'])}
    </div>
  </div>
  <div class='dual-grid'>
    <div>
      <h3>最近 live 已平仓</h3>
      {table_html(recent_live)}
    </div>
    <div>
      <h3>当前 open positions</h3>
      {table_html(open_df)}
    </div>
  </div>
</section>
"""


def build_range_buttons() -> str:
    buttons: list[str] = []
    for key, label, _ in RANGE_OPTIONS:
        active = " active" if key == DEFAULT_RANGE_KEY else ""
        buttons.append(f"<button class='range-btn{active}' type='button' data-range='{key}'>{escape(label)}</button>")
    return "".join(buttons)


def build_dashboard_content(strategies: list[dict[str, Any]], *, range_label: str, shadow_ref_text: str) -> str:
    active_specs = [s for s in strategies if s.get('is_active', True)]
    aggregate_specs = active_specs if active_specs else strategies
    total_live_positions = sum(len(s["open_df"]) for s in aggregate_specs)
    total_live_pnl = sum(summarize(s["live_df"])["cum_pnl"] for s in aggregate_specs)
    total_closed = sum(summarize(s["live_df"])["trades"] for s in aggregate_specs)
    total_warnings = sum(int(s["warnings"]) for s in aggregate_specs)

    active_lane_names = ' / '.join(s['key'] for s in active_specs) if active_specs else 'none'
    top_cards = "".join(
        [
            metric_card("active live lanes", str(len(active_specs)), active_lane_names),
            metric_card("current open positions", str(total_live_positions), "open positions 始终显示当前持仓"),
            metric_card("window live closed trades", str(total_closed), f"统计窗口：{escape(range_label)}"),
            metric_card("window realized pnl", money(total_live_pnl), f"warnings={total_warnings}"),
        ]
    )

    overall_live = aggregate_live_closed(aggregate_specs)
    overall_curve = curve_series(overall_live, "all active live lanes", "#f8fafc")
    lane_curves = [curve_series(s["live_df"], s["title"], s["live_color"]) for s in aggregate_specs]

    open_tables: list[pd.DataFrame] = []
    for s in aggregate_specs:
        if s["open_df"].empty:
            continue
        df = s["open_df"].copy()
        df.insert(0, "strategy", s["title"])
        open_tables.append(df[[c for c in ["strategy", "symbol", "side", "entry_time", "entry_price", "timeout_at"] if c in df.columns]])
    open_combined = pd.concat(open_tables, ignore_index=True) if open_tables else pd.DataFrame()

    recent_closed_parts: list[pd.DataFrame] = []
    for s in strategies:
        df = s["live_df"].copy()
        if df.empty:
            continue
        df.insert(0, "strategy", s["title"])
        recent_closed_parts.append(df[[c for c in ["strategy", "ts", "symbol", "side", "pnl_usdt", "exit_reason"] if c in df.columns]])
    recent_closed = pd.concat(recent_closed_parts, ignore_index=True).sort_values("ts", ascending=False).head(24) if recent_closed_parts else pd.DataFrame()

    return f"""
<section class='panel'>
  <div class='panel-head'>
    <div>
      <h2>统计窗口：{escape(range_label)}</h2>
      <p class='muted'>已平仓、收益曲线、最近交易列表都会按这个窗口过滤；open positions 始终显示当前实时持仓。</p>
    </div>
    <div class='pill'>shadow refs · {escape(shadow_ref_text)}</div>
  </div>
  <div class='metric-grid'>{top_cards}</div>
</section>

<section class='panel'>
  <div class='panel-head'>
    <div>
      <h2>跨策略总收益曲线</h2>
      <p class='muted'>这里把三条真钱 live 合并成一条总曲线；下面再拆成各 lane 自己的累计 PnL，方便你看是哪个策略在拖累或贡献。</p>
    </div>
  </div>
  <div class='viz-grid'>
    <div class='viz-card'>
      <h3>总累计 realized PnL</h3>
      <p class='muted'>按真实平仓时间累计。只统计这个时间窗口内已经平掉的真钱单。</p>
      {line_chart_svg([overall_curve])}
    </div>
    <div class='viz-card'>
      <h3>各 lane 累计 PnL</h3>
      <p class='muted'>同一窗口下，把 core3 / global32b / rank29 三条线拆开叠在一张图上看。</p>
      {line_chart_svg(lane_curves)}
    </div>
  </div>
  <div class='viz-grid'>
    <div class='viz-card'>
      <h3>按天 realized PnL</h3>
      <p class='muted'>看最近一段时间是某几天集中亏损，还是一直慢慢磨损。</p>
      {daily_pnl_bar_svg(overall_live)}
    </div>
    <div class='viz-card'>
      <h3>跨策略逐笔交易：赢 / 亏</h3>
      <p class='muted'>每一根就是一笔已平仓真钱单：向上是赢，向下是亏。</p>
      {trade_strip_svg(overall_live)}
    </div>
  </div>
</section>

<section class='panel'>
  <div class='panel-head'>
    <div>
      <h2>跨策略当前状态</h2>
      <p class='muted'>这里先看全局：谁在场内、最近哪几笔是盈利/亏损、以及整体真钱表现。</p>
    </div>
  </div>
  <div class='dual-grid'>
    <div>
      <h3>当前 open positions</h3>
      {table_html(open_combined, strategy_colored=True)}
    </div>
    <div>
      <h3>最近真钱已平仓（跨三条 live）</h3>
      {table_html(recent_closed, strategy_colored=True)}
    </div>
  </div>
</section>

{''.join(build_strategy_section(s) for s in strategies)}
"""


def main() -> int:
    ensure_dir(SITE_DIR)

    generated_at = datetime.now(timezone.utc)
    now_ts = pd.Timestamp(generated_at)

    r29_state = read_json(R29_STATE_PATH, {}) or {}
    r29_status = read_json(R29_STATUS_PATH, {}) or {}
    c3_status = read_json(C3_STATUS_PATH, {}) or {}
    c3_run = read_json(C3_RUN_PATH, {}) or {}
    c3_state = read_json(C3_STATE_PATH, {}) or {}
    c3_shadow_summary = read_json(C3_SHADOW_SUMMARY_PATH, {}) or {}
    g32_status = read_json(G32_STATUS_PATH, {}) or {}
    g32_run = read_json(G32_RUN_PATH, {}) or {}
    g32_state = read_json(G32_STATE_PATH, {}) or {}
    g32_shadow_summary = read_json(G32_SHADOW_SUMMARY_PATH, {}) or {}

    r29_live = closed_to_df(r29_state.get("closed_trades", []) or [], ts_col="exit_time", pnl_cols=["net_pnl", "gross_pnl"]).tail(160).reset_index(drop=True)
    r29_shadow = rank29_shadow_df().tail(160).reset_index(drop=True)

    c3_live = closed_to_df(read_json(C3_CLOSED_PATH, []) or [], ts_col="exit_time", pnl_cols=["net_pnl", "gross_pnl"]).tail(160).reset_index(drop=True)
    c3_shadow = shadow_to_df(read_json(C3_SHADOW_PATH, []) or [], ret_col="paper_effective_net_ret", ts_col="exit_ts", notional=100.0).tail(160).reset_index(drop=True)

    g32_live = closed_to_df(read_json(G32_CLOSED_PATH, []) or [], ts_col="exit_time", pnl_cols=["net_pnl", "gross_pnl"]).tail(160).reset_index(drop=True)
    g32_shadow = shadow_to_df(read_json(G32_SHADOW_PATH, []) or [], ret_col="paper_effective_net_ret", ts_col="exit_ts", notional=100.0).tail(160).reset_index(drop=True)

    r29_open = pd.DataFrame(r29_state.get("live_positions", []) or [])
    c3_open = pd.DataFrame(c3_state.get("live_positions", []) or [])
    g32_open = pd.DataFrame(g32_state.get("live_positions", []) or [])

    base_strategies = [
        {
            "key": "core3",
            "title": "core3 live",
            "subtitle": "主 live 线。这里用 32b 的 Alt shadow sidecar 作为参考对照，方便看 live 是否大致跟随 shadow。",
            "pairing_mode": "proxy shadow",
            "pairing_badge": "core3 ↔ alt shadow (reference)",
            "detail_link": "/momentum/factors/rank32b_canary/report.html",
            "live_df": c3_live,
            "shadow_df": c3_shadow,
            "open_df": c3_open,
            "live_label": "core3 live",
            "live_color": "#60a5fa",
            "shadow_label": "alt shadow",
            "shadow_color": "#f59e0b",
            "last_run": c3_run.get("run_finished_at") or c3_status.get("last_run_utc"),
            "warnings": int(c3_run.get("warnings", 0) or 0),
            "compare_start_ts": None,
            "curve_note": "看累计 PnL 是否大体跟得上 shadow；若口径不是 exact pair，这里会明确标记为 reference。",
        },
        {
            "key": "global32b",
            "title": "global32b official live",
            "subtitle": "当前重点主线。它已经切到 15m official-close only，后续要拿它直接对照 365d / 720d official-close backtest，而不是再和 preview 口径混看。",
            "pairing_mode": "same strategy shadow",
            "pairing_badge": "global32b official live ↔ official-close benchmark",
            "detail_link": "/momentum/factors/rank32b_global_live/report.html",
            "live_df": g32_live,
            "shadow_df": g32_shadow,
            "open_df": g32_open,
            "live_label": "global32b official live",
            "live_color": "#22c55e",
            "shadow_label": "global official shadow",
            "shadow_color": "#a855f7",
            "last_run": g32_run.get("run_finished_at") or g32_status.get("last_run_utc"),
            "warnings": int(g32_run.get("warnings", 0) or 0),
            "compare_start_ts": infer_compare_start_ts(g32_live, g32_open),
            "curve_note": "横轴按真实时间绘制；当前 global32b 已重置为 official-close live，新账本的目标是逐步贴近 official-close 回测基准。正式基准解释页见 global_live_like_stability 页面。",
        },
        {
            "key": "rank29",
            "title": "rank29 archived",
            "subtitle": "Rank29 已停实盘并降为 P0。保留这块只为说明旧 live / shadow 轨迹和审计结论，不再把它当 active lane。",
            "pairing_mode": "archived / audit only",
            "pairing_badge": "rank29 retired ↔ shadow kept for audit",
            "detail_link": "/momentum/factors/rank29_monitoring_hub/report.html",
            "live_df": r29_live,
            "shadow_df": r29_shadow,
            "open_df": r29_open,
            "live_label": "rank29 legacy live",
            "live_color": "#38bdf8",
            "shadow_label": "rank29 archived shadow",
            "shadow_color": "#f97316",
            "last_run": r29_status.get("generated_at_utc") or r29_state.get("last_run_utc"),
            "warnings": len(r29_status.get("recent_warnings", []) or []),
            "compare_start_ts": infer_compare_start_ts(r29_live, r29_open),
            "curve_note": "这条线已归档；曲线只保留作 future-leak 审计与历史对照，不再表示可继续运行的实盘策略。",
            "is_active": False,
            "notice": "P0 archived · live timer disabled · do not restart until signal definition is rewritten under strict-causal rules.",
        },
    ]

    shadow_ref_text = (
        "global32b 已切到 official-close 主口径，主要对照页为 "
        "/momentum/factors/rank32b/global_live_like_stability.html；"
        f"core3 shadow marked={pct(c3_shadow_summary.get('paper_marked_total_return'))} · "
        f"global official shadow marked={pct(g32_shadow_summary.get('paper_marked_total_return'))} · "
        "rank29 shadow 仅保留作 archived audit 参考。"
    )

    range_panes: list[str] = []
    for key, label, days in RANGE_OPTIONS:
        filtered_strategies: list[dict[str, Any]] = []
        for spec in base_strategies:
            live_df = filter_df_by_days(spec["live_df"], days, now_ts)
            shadow_df = filter_df_by_days(spec["shadow_df"], days, now_ts)
            compare_start_ts = spec.get("compare_start_ts")
            if compare_start_ts is not None:
                live_df = filter_df_since_ts(live_df, compare_start_ts)
                shadow_df = filter_df_since_ts(shadow_df, compare_start_ts)
            filtered_strategies.append(
                {
                    **spec,
                    "live_df": live_df,
                    "shadow_df": shadow_df,
                    "live_curve": curve_series(live_df, spec["live_label"], spec["live_color"]),
                    "shadow_curve": curve_series(shadow_df, spec["shadow_label"], spec["shadow_color"]),
                }
            )
        active = " active" if key == DEFAULT_RANGE_KEY else ""
        range_panes.append(
            f"<div class='range-pane{active}' data-range='{key}'>{build_dashboard_content(filtered_strategies, range_label=label, shadow_ref_text=shadow_ref_text)}</div>"
        )

    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Live Trading Center</title>
  <style>
    :root {{
      --bg: #020617;
      --panel: #0f172a;
      --panel-2: #111827;
      --line: #1f2937;
      --muted: #94a3b8;
      --text: #e5e7eb;
      --good: #22c55e;
      --bad: #ef4444;
      --flat: #94a3b8;
      --accent: #60a5fa;
      --accent-2: #1d4ed8;
    }}
    body {{ margin: 0; background: var(--bg); color: var(--text); font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
    .wrap {{ max-width: 1360px; margin: 0 auto; padding: 28px 18px 80px; }}
    h1,h2,h3 {{ margin: 0 0 10px; }}
    p, li {{ line-height: 1.65; }}
    a {{ color: #60a5fa; }}
    .muted {{ color: var(--muted); }}
    .hero, .panel, .viz-card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 18px; }}
    .hero {{ padding: 20px 22px; margin-bottom: 18px; }}
    .panel {{ padding: 18px; margin-top: 18px; }}
    .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-top: 14px; }}
    .metric {{ background: var(--panel-2); border: 1px solid var(--line); border-radius: 14px; padding: 14px; }}
    .metric .k {{ font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: .05em; }}
    .metric .v {{ font-size: 28px; font-weight: 800; margin-top: 8px; }}
    .metric .s {{ margin-top: 8px; color: #9ca3af; font-size: 13px; }}
    .panel-head {{ display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; }}
    .pill {{ background: #0b1220; border: 1px solid #334155; border-radius: 999px; padding: 6px 10px; font-size: 12px; color: #cbd5e1; white-space: nowrap; }}
    .viz-grid {{ display: grid; grid-template-columns: 1.25fr 1fr; gap: 14px; margin-top: 16px; }}
    .viz-card {{ padding: 14px; }}
    .dual-grid {{ display: grid; grid-template-columns: 1.25fr 1fr; gap: 16px; margin-top: 16px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 10px; background: var(--panel-2); border: 1px solid var(--line); border-radius: 14px; overflow: hidden; }}
    th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--line); font-size: 13px; vertical-align: top; }}
    th {{ background: #0b1220; color: #cbd5e1; }}
    tr:last-child td {{ border-bottom: none; }}
    tr.pos td {{ background: rgba(34,197,94,0.05); }}
    tr.neg td {{ background: rgba(239,68,68,0.05); }}
    .empty {{ color: var(--muted); padding: 18px 0; }}
    .top-links {{ margin-bottom: 8px; }}
    .toolbar {{ display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-top: 18px; }}
    .range-btn {{ appearance: none; border: 1px solid #334155; background: #0b1220; color: #cbd5e1; border-radius: 999px; padding: 8px 14px; font-size: 13px; cursor: pointer; transition: all .16s ease; }}
    .range-btn:hover {{ border-color: #60a5fa; color: #eff6ff; }}
    .range-btn.active {{ background: linear-gradient(180deg, #1d4ed8, #1e40af); border-color: #60a5fa; color: white; box-shadow: 0 0 0 1px rgba(96,165,250,0.2) inset; }}
    .toolbar-note {{ font-size: 13px; color: var(--muted); }}
    .range-pane {{ display: none; }}
    .range-pane.active {{ display: block; }}
    @media (max-width: 980px) {{
      .viz-grid, .dual-grid {{ grid-template-columns: 1fr; }}
      .toolbar {{ align-items: stretch; }}
    }}
  </style>
</head>
<body>
  <div class='wrap'>
    <div class='top-links muted'>Generated: {escape(generated_at.strftime('%Y-%m-%d %H:%M:%S UTC'))}</div>
    <div class='hero'>
      <p class='top-links'><a href='/momentum/factors/rank32b_canary/report.html'>32b 主页</a> ｜ <a href='/momentum/factors/rank32b_global_live/report.html'>global32b official live</a> ｜ <a href='/momentum/factors/rank32b/global_live_like_stability.html'>official-close 基准页</a> ｜ <a href='/momentum/factors/rank29_monitoring_hub/report.html'>rank29 archive / audit</a></p>
      <h1>Live Trading Center</h1>
      <p>这是默认运维入口，但对 32b 来说现在有一个更明确的主线：<b>historical official-close backtest</b> 对照 <b>current official-close live</b>。所以这里的重点不是 preview，也不是把所有 lane 混成一团，而是先看 global32b official live 是否按新定义稳定运行、是否开始积累可和回测对照的账本。</p>
      <p class='muted'>当前配对关系：<b>global32b official live ↔ official-close benchmark（主口径）</b>；<b>core3 live ↔ alt shadow（reference）</b>；<b>rank29 已归档，仅保留 legacy 审计对照</b>。{escape(shadow_ref_text)}</p>
      <p class='muted'>后续目标：先让 live 和 official-close 回测在信号、开仓、仓位、退出上可对照；只有这一步成立，才谈“live 会不会像回测一样盈利”。</p>
      <div class='toolbar'>
        <div>{build_range_buttons()}</div>
        <div class='toolbar-note'>前端时间范围切换：已平仓 / 收益曲线 / 列表随窗口切换，当前持仓不受影响；收益曲线横轴按真实时间绘制。</div>
      </div>
    </div>

    {''.join(range_panes)}
  </div>

  <script>
    (() => {{
      const buttons = Array.from(document.querySelectorAll('.range-btn'));
      const panes = Array.from(document.querySelectorAll('.range-pane'));
      const valid = new Set(buttons.map(btn => btn.dataset.range));
      const storageKey = 'live-trading-center-range';
      const defaultRange = '{DEFAULT_RANGE_KEY}';

      function activate(range) {{
        const target = valid.has(range) ? range : defaultRange;
        buttons.forEach(btn => btn.classList.toggle('active', btn.dataset.range === target));
        panes.forEach(pane => pane.classList.toggle('active', pane.dataset.range === target));
        try {{ localStorage.setItem(storageKey, target); }} catch (err) {{}}
        if (window.location.hash !== '#' + target) {{
          history.replaceState(null, '', '#' + target);
        }}
      }}

      buttons.forEach(btn => btn.addEventListener('click', () => activate(btn.dataset.range)));

      const hashRange = window.location.hash ? window.location.hash.slice(1) : '';
      let initialRange = valid.has(hashRange) ? hashRange : '';
      if (!initialRange) {{
        try {{
          const stored = localStorage.getItem(storageKey) || '';
          if (valid.has(stored)) initialRange = stored;
        }} catch (err) {{}}
      }}
      activate(initialRange || defaultRange);
    }})();
  </script>
</body>
</html>
"""
    OUT_PATH.write_text(html, encoding="utf-8")
    print({"generated_at_utc": generated_at.strftime("%Y-%m-%dT%H:%M:%SZ"), "out": str(OUT_PATH)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
