#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_shadow_beat"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "rank32b_shadow_beat"
OUT_PATH = SITE_DIR / "report.html"
RUN_SUMMARY_PATH = ART_DIR / "shadow_last_run_summary.json"
STATUS_PATH = ART_DIR / "shadow_status.json"
SIGNALS_PATH = ART_DIR / "shadow_recent_signals.json"
REJECTIONS_PATH = ART_DIR / "shadow_recent_rejections.json"
PAPER_SUMMARY_PATH = ART_DIR / "paper_summary.json"
PAPER_TRADES_PATH = ART_DIR / "paper_trades.json"
PAPER_CLOSED_PATH = ART_DIR / "paper_closed_trades.json"
PAPER_OPEN_PATH = ART_DIR / "paper_open_positions.json"
PAPER_SKIPPED_PATH = ART_DIR / "paper_skipped_signals.json"
CONFIG_PATH = ROOT / "config" / "execution" / "rank32b_canary.yaml"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def num(v, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def pct(v, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def fmt(v) -> str:
    if v is None or pd.isna(v):
        return "-"
    text = str(v).strip()
    if text.lower() == "nan":
        return "-"
    return text or "-"


def fmt_ts_bj(v) -> str:
    text = fmt(v)
    if text == "-":
        return "-"
    raw = text.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(raw)
    except Exception:
        return text
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    bj = dt.astimezone(timezone(timedelta(hours=8)))
    utc = dt.astimezone(timezone.utc)
    return f"{bj.strftime('%Y-%m-%d %H:%M:%S')} 北京时间 / {utc.strftime('%Y-%m-%d %H:%M:%S')} UTC"


def render_table(df: pd.DataFrame, digits_cols: dict[str, int] | None = None, percent_cols: set[str] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    digits_cols = digits_cols or {}
    percent_cols = percent_cols or set()
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            val = row[col]
            if col in percent_cols:
                text = pct(val, digits_cols.get(col, 2))
            elif isinstance(val, (int, float)) and not isinstance(val, bool):
                text = num(val, digits_cols.get(col, 2))
            else:
                text = fmt(val)
            cells.append(f"<td>{escape(text)}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def build_equity_curve_card(df: pd.DataFrame, *, time_col: str, ret_col: str, title: str, subtitle: str, width: int = 960, height: int = 240) -> str:
    if df.empty or time_col not in df.columns or ret_col not in df.columns:
        return f"<div class='card'><h3>{escape(title)}</h3><p class='muted'>暂无可绘制曲线的数据。</p></div>"
    work = df[[time_col, ret_col]].copy()
    work[time_col] = pd.to_datetime(work[time_col], utc=True, errors='coerce')
    work[ret_col] = pd.to_numeric(work[ret_col], errors='coerce')
    work = work.dropna().sort_values(time_col)
    if work.empty:
        return f"<div class='card'><h3>{escape(title)}</h3><p class='muted'>暂无可绘制曲线的数据。</p></div>"
    equity = []
    acc = 1.0
    for value in work[ret_col].tolist():
        acc *= 1.0 + float(value)
        equity.append(acc)
    min_y = min(min(equity), 1.0)
    max_y = max(max(equity), 1.0)
    if abs(max_y - min_y) < 1e-12:
        max_y += 0.01
        min_y -= 0.01
    pad_x = 28
    pad_y = 18
    plot_w = width - pad_x * 2
    plot_h = height - pad_y * 2

    def x_at(i: int) -> float:
        return pad_x + (plot_w * i / max(len(equity) - 1, 1))

    def y_at(v: float) -> float:
        return pad_y + (max_y - v) / (max_y - min_y) * plot_h

    points = " ".join(f"{x_at(i):.2f},{y_at(v):.2f}" for i, v in enumerate(equity))
    base_y = y_at(1.0)
    stroke = "#3ddc97" if equity[-1] >= 1.0 else "#ff6b6b"
    fill = "rgba(61,220,151,0.10)" if equity[-1] >= 1.0 else "rgba(255,107,107,0.10)"
    area_points = f"{pad_x:.2f},{base_y:.2f} " + points + f" {x_at(len(equity)-1):.2f},{base_y:.2f}"
    start_ts = work[time_col].iloc[0].strftime('%Y-%m-%d %H:%M UTC')
    end_ts = work[time_col].iloc[-1].strftime('%Y-%m-%d %H:%M UTC')
    return (
        f"<div class='card'><h3>{escape(title)}</h3>"
        f"<p class='muted'>{escape(subtitle)}</p>"
        f"<svg viewBox='0 0 {width} {height}' width='100%' height='{height}' role='img' aria-label='{escape(title)}'>"
        f"<line x1='{pad_x}' y1='{base_y:.2f}' x2='{width-pad_x}' y2='{base_y:.2f}' stroke='#5b6b7b' stroke-dasharray='4 4' stroke-width='1'/>"
        f"<polygon points='{area_points}' fill='{fill}' />"
        f"<polyline points='{points}' fill='none' stroke='{stroke}' stroke-width='3' stroke-linejoin='round' stroke-linecap='round'/>"
        f"</svg>"
        f"<p class='muted'>样本 {len(equity)} 笔｜起点 1.0000 ｜终点 {equity[-1]:.4f} ｜区间 {escape(start_ts)} → {escape(end_ts)}</p>"
        f"</div>"
    )


def run_text_command(command: str, *, timeout: int = 10) -> str:
    try:
        out = subprocess.check_output(["/bin/bash", "-lc", command], cwd=str(ROOT), stderr=subprocess.STDOUT, text=True, timeout=timeout)
        return out.strip()
    except Exception as exc:
        return f"命令执行失败：{exc}"


def build_symbol_summary(trades_df: pd.DataFrame) -> pd.DataFrame:
    if trades_df.empty:
        return pd.DataFrame()
    work = trades_df.copy()
    work["effective_ret"] = pd.to_numeric(work.get("paper_effective_net_ret"), errors="coerce").fillna(0.0)
    work["is_closed"] = work.get("paper_trade_state", "").eq("closed")
    rows = []
    for symbol, part in work.groupby("symbol"):
        effective = part["effective_ret"].tolist()
        total = 1.0
        for r in effective:
            total *= 1.0 + float(r)
        total -= 1.0
        closed = part[part["is_closed"]]
        rows.append({
            "symbol": symbol,
            "trades": int(len(part)),
            "closed": int(len(closed)),
            "open": int((~part["is_closed"]).sum()),
            "marked_total_return": float(total),
            "closed_win_rate": float((pd.to_numeric(closed.get("net_ret"), errors="coerce") > 0).mean()) if not closed.empty else None,
            "avg_effective_ret": float(part["effective_ret"].mean()) if not part.empty else None,
        })
    return pd.DataFrame(rows).sort_values(["marked_total_return", "trades"], ascending=[False, False]).reset_index(drop=True)


def prepare_cost_breakdown_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    work = df.copy()
    for col in [
        "entry_spread_bps", "entry_impact_bps", "entry_fee_bps",
        "exit_spread_bps", "exit_impact_bps", "exit_fee_bps",
        "paper_effective_net_ret",
    ]:
        if col in work.columns:
            work[col] = pd.to_numeric(work[col], errors="coerce")
    work["curve_ts"] = pd.to_datetime(work.get("exit_ts"), utc=True, errors="coerce")
    if "mark_ts" in work.columns:
        mt = pd.to_datetime(work.get("mark_ts"), utc=True, errors="coerce")
        work["curve_ts"] = work["curve_ts"].where(work["curve_ts"].notna(), mt)
    if "entry_ts" in work.columns:
        et = pd.to_datetime(work.get("entry_ts"), utc=True, errors="coerce")
        work["curve_ts"] = work["curve_ts"].where(work["curve_ts"].notna(), et)
    work["entry_modeled_cost_bps"] = work.get("entry_impact_bps", 0.0).fillna(0.0) + work.get("entry_fee_bps", 0.0).fillna(0.0)
    work["exit_modeled_cost_bps"] = work.get("exit_impact_bps", 0.0).fillna(0.0) + work.get("exit_fee_bps", 0.0).fillna(0.0)
    work["roundtrip_modeled_cost_bps"] = work["entry_modeled_cost_bps"] + work["exit_modeled_cost_bps"]
    work["effective_ret_bps"] = work.get("paper_effective_net_ret", 0.0) * 10000.0
    return work.dropna(subset=["curve_ts"])


def build_cost_cards_html(cost_df: pd.DataFrame, paper_summary: dict[str, object]) -> str:
    if cost_df.empty:
        return "<p class='muted'>暂无足够的 depth 成本数据。</p>"
    def avg(col: str) -> float | None:
        vals = pd.to_numeric(cost_df.get(col), errors='coerce').dropna()
        return float(vals.mean()) if not vals.empty else None
    def mx(col: str) -> float | None:
        vals = pd.to_numeric(cost_df.get(col), errors='coerce').dropna()
        return float(vals.max()) if not vals.empty else None
    rejected = paper_summary.get("paper_rejected_by_insufficient_depth")
    cards = [
        ("平均入场 spread", fmt_bps(avg("entry_spread_bps")), "盘口天然宽度；不是额外冲击，但能解释为什么小币更难真钱化"),
        ("平均入场成交成本", fmt_bps(avg("entry_modeled_cost_bps")), "entry impact + fee"),
        ("平均出场成交成本", fmt_bps(avg("exit_modeled_cost_bps")), "exit impact + fee"),
        ("平均 roundtrip friction", fmt_bps(avg("roundtrip_modeled_cost_bps")), "整笔往返的模型成本"),
        ("最差 roundtrip friction", fmt_bps(mx("roundtrip_modeled_cost_bps")), "窗口内最贵的一笔"),
        ("深度不足拒单", fmt(rejected), "500U / 20 档下无法诚实成交时直接拒绝"),
    ]
    return "<div class='grid'>" + "".join(
        f"<div class='card'><div class='k'>{escape(k)}</div><div class='v'>{escape(v)}</div><div class='s'>{escape(s)}</div></div>" for k, v, s in cards
    ) + "</div>"


def build_cost_curve_card(cost_df: pd.DataFrame, *, width: int = 960, height: int = 260) -> str:
    if cost_df.empty:
        return "<div class='card'><h3>成本时间序列</h3><p class='muted'>暂无足够的 depth 成本时间序列数据。</p></div>"
    work = cost_df[["curve_ts", "roundtrip_modeled_cost_bps", "effective_ret_bps"]].copy().dropna().sort_values("curve_ts")
    if work.empty:
        return "<div class='card'><h3>成本时间序列</h3><p class='muted'>暂无足够的 depth 成本时间序列数据。</p></div>"
    min_ts = work["curve_ts"].min(); max_ts = work["curve_ts"].max()
    if min_ts == max_ts:
        max_ts = min_ts + pd.Timedelta(minutes=1)
    min_y = min(float(work["roundtrip_modeled_cost_bps"].min()), float(work["effective_ret_bps"].min()), 0.0)
    max_y = max(float(work["roundtrip_modeled_cost_bps"].max()), float(work["effective_ret_bps"].max()), 0.0)
    if abs(max_y - min_y) < 1e-12:
        max_y += 1.0; min_y -= 1.0
    pad_x = 42; pad_y = 18; plot_w = width - pad_x * 2; plot_h = height - pad_y * 2
    def x_at(ts: pd.Timestamp) -> float:
        return pad_x + plot_w * ((ts - min_ts).total_seconds() / max((max_ts - min_ts).total_seconds(), 1))
    def y_at(v: float) -> float:
        return pad_y + (max_y - v) / (max_y - min_y) * plot_h
    zero_y = y_at(0.0)
    cost_points = " ".join(f"{x_at(ts):.2f},{y_at(v):.2f}" for ts, v in zip(work["curve_ts"], work["roundtrip_modeled_cost_bps"]))
    ret_points = " ".join(f"{x_at(ts):.2f},{y_at(v):.2f}" for ts, v in zip(work["curve_ts"], work["effective_ret_bps"]))
    circles = "".join(
        f"<circle cx='{x_at(ts):.2f}' cy='{y_at(v):.2f}' r='3.3' fill='#f59e0b' />" for ts, v in zip(work["curve_ts"], work["roundtrip_modeled_cost_bps"])
    ) + "".join(
        f"<circle cx='{x_at(ts):.2f}' cy='{y_at(v):.2f}' r='3.1' fill='#60a5fa' />" for ts, v in zip(work["curve_ts"], work["effective_ret_bps"])
    )
    return (
        "<div class='card'><h3>成本 vs 单笔收益（时间轴）</h3>"
        "<p class='muted'>橙线 = roundtrip modeled friction（bps），蓝线 = 单笔有效收益（bps）。如果橙线抬头而蓝线下沉，通常说明盘口成本在吃 edge。</p>"
        f"<svg viewBox='0 0 {width} {height}' width='100%' height='{height}'>"
        f"<line x1='{pad_x}' y1='{zero_y:.2f}' x2='{width-pad_x}' y2='{zero_y:.2f}' stroke='#5b6b7b' stroke-dasharray='4 4' stroke-width='1' />"
        f"<polyline points='{cost_points}' fill='none' stroke='#f59e0b' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round' />"
        f"<polyline points='{ret_points}' fill='none' stroke='#60a5fa' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round' />"
        f"{circles}</svg>"
        f"<p class='muted'>区间 {escape(fmt_ts_bj(min_ts.strftime('%Y-%m-%dT%H:%M:%SZ')))} → {escape(fmt_ts_bj(max_ts.strftime('%Y-%m-%dT%H:%M:%SZ')))}</p></div>"
    )


def build_cost_symbol_summary(cost_df: pd.DataFrame) -> pd.DataFrame:
    if cost_df.empty or "symbol" not in cost_df.columns:
        return pd.DataFrame()
    rows = []
    for symbol, part in cost_df.groupby("symbol", dropna=False):
        rows.append({
            "symbol": symbol,
            "trades": len(part),
            "avg_entry_spread_bps": float(pd.to_numeric(part.get("entry_spread_bps"), errors='coerce').dropna().mean()) if "entry_spread_bps" in part.columns else None,
            "avg_entry_cost_bps": float(pd.to_numeric(part.get("entry_modeled_cost_bps"), errors='coerce').dropna().mean()) if "entry_modeled_cost_bps" in part.columns else None,
            "avg_exit_cost_bps": float(pd.to_numeric(part.get("exit_modeled_cost_bps"), errors='coerce').dropna().mean()) if "exit_modeled_cost_bps" in part.columns else None,
            "avg_roundtrip_cost_bps": float(pd.to_numeric(part.get("roundtrip_modeled_cost_bps"), errors='coerce').dropna().mean()) if "roundtrip_modeled_cost_bps" in part.columns else None,
            "avg_effective_ret_bps": float(pd.to_numeric(part.get("effective_ret_bps"), errors='coerce').dropna().mean()) if "effective_ret_bps" in part.columns else None,
        })
    return pd.DataFrame(rows).sort_values(["avg_roundtrip_cost_bps", "avg_effective_ret_bps"], ascending=[False, False], na_position="last")


def main() -> int:
    ensure_dir(SITE_DIR)
    summary = load_json(RUN_SUMMARY_PATH, {})
    status = load_json(STATUS_PATH, {})
    signals = load_json(SIGNALS_PATH, [])
    rejections = load_json(REJECTIONS_PATH, [])
    paper_summary = load_json(PAPER_SUMMARY_PATH, {})
    paper_trades = load_json(PAPER_TRADES_PATH, [])
    paper_closed = load_json(PAPER_CLOSED_PATH, [])
    paper_open = load_json(PAPER_OPEN_PATH, [])
    paper_skipped = load_json(PAPER_SKIPPED_PATH, [])

    sig_df = pd.DataFrame(signals if isinstance(signals, list) else [])
    rej_df = pd.DataFrame(rejections if isinstance(rejections, list) else [])
    paper_df = pd.DataFrame(paper_trades if isinstance(paper_trades, list) else [])
    paper_closed_df = pd.DataFrame(paper_closed if isinstance(paper_closed, list) else [])
    paper_open_df = pd.DataFrame(paper_open if isinstance(paper_open, list) else [])
    paper_skipped_df = pd.DataFrame(paper_skipped if isinstance(paper_skipped, list) else [])
    symbol_summary = build_symbol_summary(paper_df)
    alt_curve_df = pd.DataFrame()
    if not paper_df.empty:
        alt_curve_df = paper_df.copy()
        alt_curve_df["curve_ts"] = alt_curve_df.get("exit_ts")
        if "mark_ts" in alt_curve_df.columns:
            alt_curve_df["curve_ts"] = alt_curve_df["curve_ts"].where(alt_curve_df["curve_ts"].notna(), alt_curve_df["mark_ts"])
        if "entry_ts" in alt_curve_df.columns:
            alt_curve_df["curve_ts"] = alt_curve_df["curve_ts"].where(alt_curve_df["curve_ts"].notna(), alt_curve_df["entry_ts"])
    alt_curve_card = build_equity_curve_card(
        alt_curve_df,
        time_col="curve_ts",
        ret_col="paper_effective_net_ret",
        title="Alt shadow 累计收益曲线",
        subtitle="基于 alt shadow paper trades 的 effective return 复利累计；已平仓用 realized，未平仓用最新 mark。",
    )

    if not sig_df.empty:
        meta_df = pd.json_normalize(sig_df.get("metadata", pd.Series([{}] * len(sig_df))))
        activity_df = pd.json_normalize(sig_df.get("shadow_activity_snapshot", pd.Series([{}] * len(sig_df))))
        sig_df = sig_df.drop(columns=[c for c in ["metadata", "shadow_activity_snapshot"] if c in sig_df.columns])
        for col in meta_df.columns:
            sig_df[f"meta.{col}"] = meta_df[col]
        for col in activity_df.columns:
            sig_df[f"activity.{col}"] = activity_df[col]
        sig_df["mode"] = sig_df.get("meta.signal_mode", "-")
        sig_df["activity.percentile"] = pd.to_numeric(sig_df.get("activity.percentile"), errors="coerce")
        sig_df["activity.min_percentile"] = pd.to_numeric(sig_df.get("activity.min_percentile"), errors="coerce")
        sig_df = sig_df.sort_values("timestamp").tail(40)
        sig_view = sig_df[[c for c in [
            "timestamp", "signal_confirmed_at", "symbol", "mode", "side", "signal_price",
            "activity.percentile", "activity.min_percentile", "shadow_would_block_reason", "shadow_live_universe_enabled"
        ] if c in sig_df.columns]].copy()
        sig_view = sig_view.rename(columns={
            "timestamp": "信号时间",
            "signal_confirmed_at": "确认时间",
            "symbol": "标的",
            "mode": "模式",
            "side": "方向",
            "signal_price": "信号价",
            "activity.percentile": "活跃度分位数",
            "activity.min_percentile": "当前门槛",
            "shadow_would_block_reason": "若进live会被拦截原因",
            "shadow_live_universe_enabled": "当前live universe已启用",
        })
        for col in ["信号时间", "确认时间"]:
            if col in sig_view.columns:
                sig_view[col] = sig_view[col].apply(fmt_ts_bj)
    else:
        sig_view = pd.DataFrame()

    if not rej_df.empty:
        rej_df["mode"] = rej_df.get("metadata", pd.Series([{}] * len(rej_df))).apply(lambda x: x.get("signal_mode") if isinstance(x, dict) else None)
        rej_df["reason"] = rej_df.get("risk", pd.Series([{}] * len(rej_df))).apply(lambda x: x.get("reason") if isinstance(x, dict) else None)
        rej_view = rej_df[[c for c in ["timestamp", "symbol", "mode", "side", "reason"] if c in rej_df.columns]].copy()
        rej_view = rej_view.rename(columns={"timestamp": "时间", "symbol": "标的", "mode": "模式", "side": "方向", "reason": "原因"})
        if "时间" in rej_view.columns:
            rej_view["时间"] = rej_view["时间"].apply(fmt_ts_bj)
        rej_view = rej_view.tail(40)
    else:
        rej_view = pd.DataFrame()

    if not paper_closed_df.empty:
        paper_closed_df = paper_closed_df.sort_values("exit_ts").tail(30)
        closed_view = paper_closed_df[[c for c in ["exit_ts", "symbol", "side", "mode", "entry_ts", "entry_price", "exit_price", "exit_reason", "net_ret", "hold_minutes"] if c in paper_closed_df.columns]].copy()
        closed_view = closed_view.rename(columns={"exit_ts": "平仓时间", "symbol": "标的", "side": "方向", "mode": "模式", "entry_ts": "入场时间", "entry_price": "入场价", "exit_price": "出场价", "exit_reason": "原因", "net_ret": "净收益", "hold_minutes": "持有分钟"})
        for col in ["平仓时间", "入场时间"]:
            if col in closed_view.columns:
                closed_view[col] = closed_view[col].apply(fmt_ts_bj)
    else:
        closed_view = pd.DataFrame()

    if not paper_open_df.empty:
        paper_open_df = paper_open_df.sort_values("mark_ts").tail(20)
        open_view = paper_open_df[[c for c in ["mark_ts", "symbol", "side", "mode", "entry_ts", "entry_price", "mark_price", "mark_net_ret", "hold_minutes"] if c in paper_open_df.columns]].copy()
        open_view = open_view.rename(columns={"mark_ts": "标记时间", "symbol": "标的", "side": "方向", "mode": "模式", "entry_ts": "入场时间", "entry_price": "入场价", "mark_price": "最新价", "mark_net_ret": "浮动净收益", "hold_minutes": "持有分钟"})
        for col in ["标记时间", "入场时间"]:
            if col in open_view.columns:
                open_view[col] = open_view[col].apply(fmt_ts_bj)
    else:
        open_view = pd.DataFrame()

    if not paper_skipped_df.empty:
        paper_skipped_df = paper_skipped_df.sort_values("timestamp").tail(20)
        paper_skipped_view = paper_skipped_df[[c for c in ["timestamp", "signal_confirmed_at", "symbol", "side", "reason", "paper_active_positions", "paper_max_concurrent_positions"] if c in paper_skipped_df.columns]].copy()
        paper_skipped_view = paper_skipped_view.rename(columns={"timestamp": "信号时间", "signal_confirmed_at": "确认时间", "symbol": "标的", "side": "方向", "reason": "paper拒单原因", "paper_active_positions": "当时占用仓位数", "paper_max_concurrent_positions": "最大并发仓位"})
        for col in ["信号时间", "确认时间"]:
            if col in paper_skipped_view.columns:
                paper_skipped_view[col] = paper_skipped_view[col].apply(fmt_ts_bj)
    else:
        paper_skipped_view = pd.DataFrame()

    code_version = run_text_command("git rev-parse --short=12 HEAD")
    shadow_name = str(summary.get('shadow_name') or status.get('name') or 'Alt shadow sidecar')
    shadow_bucket = str(summary.get('shadow_bucket') or '-')
    shadow_symbols = summary.get('shadow_symbols') if isinstance(summary.get('shadow_symbols'), dict) else {}
    shadow_symbol_count = len(shadow_symbols)
    paper_cfg = paper_summary.get('assumptions') if isinstance(paper_summary.get('assumptions'), dict) else {}
    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8'>
  <title>{escape(shadow_name)}</title>
  <style>
    body {{ font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; margin: 24px; color: #e8ecf1; background:#0f141a; }}
    h1,h2,h3 {{ margin: 0 0 12px 0; }}
    .muted {{ color: #9fb0c2; }}
    .grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(220px,1fr)); gap:12px; margin: 16px 0 24px 0; }}
    .card {{ background:#151d26; border:1px solid #263241; border-radius:12px; padding:14px 16px; }}
    .k {{ color:#8ea0b5; font-size:12px; margin-bottom:6px; }}
    .v {{ font-size:22px; font-weight:700; }}
    .s {{ color:#9fb0c2; font-size:12px; margin-top:6px; line-height:1.4; }}
    table {{ width:100%; border-collapse: collapse; margin: 10px 0 24px 0; }}
    th,td {{ border:1px solid #263241; padding:8px 10px; font-size:13px; vertical-align: top; }}
    th {{ background:#151d26; text-align:left; }}
    td {{ background:#101720; }}
    code {{ background:#151d26; padding:2px 6px; border-radius:6px; }}
  </style>
</head>
<body>
  <h1>{escape(shadow_name)}</h1>
  <p class='muted'><strong>这页回答的问题：</strong>“如果我把 alt 候选池本身当成一个独立 pocket 来观察，它最近有没有 edge？”它会记录 <strong>所有 alt 候选信号</strong>，并给出 paper PnL。它<strong>不做 global strongest-only 淘汰赛</strong>。</p>
  <p class='muted'><strong>和 global shadow 的区别：</strong>alt shadow 是看“alt 池本身值不值得碰”；global shadow 是看“全市场同一 bar 只留最强者”这个 selector 是否能选出更好的组合。一个回答“alt pocket 好不好”，一个回答“selector 好不好”。</p>
  <div class='grid'>
    <div class='card'><div class='k'>当前代码版本</div><div class='v'>{escape(fmt(code_version))}</div><div class='s'>sidecar 与主 runner 共用同一个 signal adapter / execution probe</div></div>
    <div class='card'><div class='k'>最近一次运行</div><div class='v'>{escape(fmt_ts_bj(summary.get('generated_at_utc')))}</div><div class='s'>状态：{escape(fmt(summary.get('status')))}</div></div>
    <div class='card'><div class='k'>观察池</div><div class='v'>{escape(fmt(shadow_bucket))}</div><div class='s'>当前 shadow symbols：{escape(fmt(shadow_symbol_count))}</div></div>
    <div class='card'><div class='k'>最近信号总数</div><div class='v'>{escape(fmt(summary.get('total_signals')))}</div><div class='s'>preview {escape(fmt(summary.get('preview_signals')))} / official {escape(fmt(summary.get('official_signals')))}</div></div>
    <div class='card'><div class='k'>本轮新增信号</div><div class='v'>{escape(fmt(summary.get('new_signal_count')))}</div><div class='s'>新增 shadow veto/reject 记录：{escape(fmt(summary.get('new_rejection_count')))}</div></div>
    <div class='card'><div class='k'>最新观察到的信号</div><div class='v'>{escape(fmt_ts_bj(summary.get('latest_signal_time')))}</div><div class='s'>symbol: {escape(fmt(summary.get('latest_signal_symbol')))}</div></div>
  </div>

  <div class='grid'>
    <div class='card'><div class='k'>paper 已实现总收益</div><div class='v'>{escape(pct(paper_summary.get('paper_realized_total_return')))}</div><div class='s'>只统计已平仓 trades</div></div>
    <div class='card'><div class='k'>paper 标记总收益</div><div class='v'>{escape(pct(paper_summary.get('paper_marked_total_return')))}</div><div class='s'>已平仓 + 未平仓按最新价估值</div></div>
    <div class='card'><div class='k'>paper 已平仓笔数</div><div class='v'>{escape(fmt(paper_summary.get('paper_closed_trades')))}</div><div class='s'>closed win rate = {escape(pct(paper_summary.get('paper_closed_win_rate')))}</div></div>
    <div class='card'><div class='k'>paper 未平仓仓位</div><div class='v'>{escape(fmt(paper_summary.get('paper_open_positions')))}</div><div class='s'>当前纸上仍在持有的 alt 候选</div></div>
    <div class='card'><div class='k'>paper 并发拒单</div><div class='v'>{escape(fmt(paper_summary.get('paper_skipped_by_max_concurrent')))}</div><div class='s'>因为 max_concurrent 被跳过的 alt 候选</div></div>
    <div class='card'><div class='k'>paper 口径</div><div class='v'>{escape(fmt(paper_cfg.get('entry_style')))}</div><div class='s'>TP {escape(fmt(paper_cfg.get('tp_atr_mult')))} ATR / SL {escape(fmt(paper_cfg.get('sl_atr_mult')))} ATR / timeout {escape(fmt(paper_cfg.get('timeout_15m')))}x15m</div></div>
  </div>

  {alt_curve_card}

  <h3>最近信号</h3>
  {render_table(sig_view, digits_cols={'信号价':6, '活跃度分位数':3, '当前门槛':3})}

  <h3>paper 最近平仓</h3>
  {render_table(closed_view, digits_cols={'入场价':6, '出场价':6, '净收益':4, '持有分钟':0}, percent_cols={'净收益'})}

  <h3>paper 当前持仓</h3>
  {render_table(open_view, digits_cols={'入场价':6, '最新价':6, '浮动净收益':4, '持有分钟':0}, percent_cols={'浮动净收益'})}

  <h3>paper 按标的汇总</h3>
  {render_table(symbol_summary, digits_cols={'trades':0, 'closed':0, 'open':0, 'avg_effective_ret':4}, percent_cols={'marked_total_return','closed_win_rate','avg_effective_ret'})}

  <h3>paper 并发拒单记录</h3>
  {render_table(paper_skipped_view, digits_cols={'当时占用仓位数':0, '最大并发仓位':0})}

  <h3>shadow veto / reject 记录</h3>
  {render_table(rej_view)}

  <p class='muted'>源配置：<code>{escape(str(CONFIG_PATH))}</code></p>
</body>
</html>
"""
    OUT_PATH.write_text(html, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
