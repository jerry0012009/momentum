#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_shadow_global_winner"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "rank32b_shadow_global_winner"
OUT_PATH = SITE_DIR / "report.html"
RUN_SUMMARY_PATH = ART_DIR / "shadow_last_run_summary.json"
STATUS_PATH = ART_DIR / "shadow_status.json"
SIGNALS_PATH = ART_DIR / "shadow_recent_signals.json"
SELECTED_PATH = ART_DIR / "shadow_selected_signals.json"
SKIPPED_PATH = ART_DIR / "shadow_skipped_signals.json"
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


def normalize_signal_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    meta_df = pd.json_normalize(df.get("metadata", pd.Series([{}] * len(df))))
    df = df.drop(columns=[c for c in ["metadata"] if c in df.columns])
    for col in meta_df.columns:
        df[f"meta.{col}"] = meta_df[col]
    df["mode"] = df.get("meta.signal_mode", "-")
    return df


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


def main() -> int:
    ensure_dir(SITE_DIR)
    summary = load_json(RUN_SUMMARY_PATH, {})
    status = load_json(STATUS_PATH, {})
    signals = load_json(SIGNALS_PATH, [])
    selected = load_json(SELECTED_PATH, [])
    skipped = load_json(SKIPPED_PATH, [])
    paper_summary = load_json(PAPER_SUMMARY_PATH, {})
    paper_trades = load_json(PAPER_TRADES_PATH, [])
    paper_closed = load_json(PAPER_CLOSED_PATH, [])
    paper_open = load_json(PAPER_OPEN_PATH, [])
    paper_skipped = load_json(PAPER_SKIPPED_PATH, [])

    sig_df = normalize_signal_df(pd.DataFrame(signals if isinstance(signals, list) else []))
    selected_df = normalize_signal_df(pd.DataFrame(selected if isinstance(selected, list) else []))
    skipped_df = normalize_signal_df(pd.DataFrame(skipped if isinstance(skipped, list) else []))
    paper_df = pd.DataFrame(paper_trades if isinstance(paper_trades, list) else [])
    paper_closed_df = pd.DataFrame(paper_closed if isinstance(paper_closed, list) else [])
    paper_open_df = pd.DataFrame(paper_open if isinstance(paper_open, list) else [])
    paper_skipped_df = pd.DataFrame(paper_skipped if isinstance(paper_skipped, list) else [])
    symbol_summary = build_symbol_summary(paper_df)
    global_curve_df = pd.DataFrame()
    if not paper_df.empty:
        global_curve_df = paper_df.copy()
        global_curve_df["curve_ts"] = global_curve_df.get("exit_ts")
        if "mark_ts" in global_curve_df.columns:
            global_curve_df["curve_ts"] = global_curve_df["curve_ts"].where(global_curve_df["curve_ts"].notna(), global_curve_df["mark_ts"])
        if "entry_ts" in global_curve_df.columns:
            global_curve_df["curve_ts"] = global_curve_df["curve_ts"].where(global_curve_df["curve_ts"].notna(), global_curve_df["entry_ts"])
    global_curve_card = build_equity_curve_card(
        global_curve_df,
        time_col="curve_ts",
        ret_col="paper_effective_net_ret",
        title="Global shadow 累计收益曲线",
        subtitle="基于 global strongest-only paper trades 的 effective return 复利累计；已平仓用 realized，未平仓用最新 mark。",
    )

    if not sig_df.empty:
        sig_df = sig_df.sort_values("timestamp").tail(40)
        sig_view = sig_df[[c for c in [
            "timestamp", "signal_confirmed_at", "symbol", "mode", "side", "signal_price",
            "shadow_selected", "shadow_selection_reason", "shadow_selection_metric"
        ] if c in sig_df.columns]].copy()
        sig_view = sig_view.rename(columns={
            "timestamp": "信号时间",
            "signal_confirmed_at": "确认时间",
            "symbol": "标的",
            "mode": "模式",
            "side": "方向",
            "signal_price": "信号价",
            "shadow_selected": "是否入选全局最强",
            "shadow_selection_reason": "selector结果",
            "shadow_selection_metric": "强度指标",
        })
        for col in ["信号时间", "确认时间"]:
            if col in sig_view.columns:
                sig_view[col] = sig_view[col].apply(fmt_ts_bj)
    else:
        sig_view = pd.DataFrame()

    if not selected_df.empty:
        selected_df = selected_df.sort_values("timestamp").tail(40)
        selected_view = selected_df[[c for c in [
            "timestamp", "signal_confirmed_at", "symbol", "mode", "side", "signal_price", "meta.slope_strength"
        ] if c in selected_df.columns]].copy()
        selected_view = selected_view.rename(columns={
            "timestamp": "入选时间",
            "signal_confirmed_at": "确认时间",
            "symbol": "入选标的",
            "mode": "模式",
            "side": "方向",
            "signal_price": "信号价",
            "meta.slope_strength": "slope_strength",
        })
        for col in ["入选时间", "确认时间"]:
            if col in selected_view.columns:
                selected_view[col] = selected_view[col].apply(fmt_ts_bj)
    else:
        selected_view = pd.DataFrame()

    if not skipped_df.empty:
        skipped_df = skipped_df.sort_values("timestamp").tail(40)
        skipped_view = skipped_df[[c for c in [
            "timestamp", "symbol", "mode", "side", "reason", "selected_symbol", "selected_strength", "signal_strength"
        ] if c in skipped_df.columns]].copy()
        skipped_view = skipped_view.rename(columns={
            "timestamp": "时间",
            "symbol": "落选标的",
            "mode": "模式",
            "side": "方向",
            "reason": "原因",
            "selected_symbol": "胜出标的",
            "selected_strength": "胜出强度",
            "signal_strength": "本信号强度",
        })
        if "时间" in skipped_view.columns:
            skipped_view["时间"] = skipped_view["时间"].apply(fmt_ts_bj)
    else:
        skipped_view = pd.DataFrame()

    if not paper_closed_df.empty:
        paper_closed_df = paper_closed_df.sort_values("exit_ts").tail(30)
        closed_view = paper_closed_df[[c for c in [
            "exit_ts", "symbol", "side", "mode", "entry_ts", "entry_price", "exit_price", "exit_reason", "net_ret", "hold_minutes"
        ] if c in paper_closed_df.columns]].copy()
        closed_view = closed_view.rename(columns={
            "exit_ts": "平仓时间",
            "symbol": "标的",
            "side": "方向",
            "mode": "模式",
            "entry_ts": "入场时间",
            "entry_price": "入场价",
            "exit_price": "出场价",
            "exit_reason": "原因",
            "net_ret": "净收益",
            "hold_minutes": "持有分钟",
        })
        for col in ["平仓时间", "入场时间"]:
            if col in closed_view.columns:
                closed_view[col] = closed_view[col].apply(fmt_ts_bj)
    else:
        closed_view = pd.DataFrame()

    if not paper_open_df.empty:
        paper_open_df = paper_open_df.sort_values("mark_ts").tail(20)
        open_view = paper_open_df[[c for c in [
            "mark_ts", "symbol", "side", "mode", "entry_ts", "entry_price", "mark_price", "mark_net_ret", "hold_minutes"
        ] if c in paper_open_df.columns]].copy()
        open_view = open_view.rename(columns={
            "mark_ts": "标记时间",
            "symbol": "标的",
            "side": "方向",
            "mode": "模式",
            "entry_ts": "入场时间",
            "entry_price": "入场价",
            "mark_price": "最新价",
            "mark_net_ret": "浮动净收益",
            "hold_minutes": "持有分钟",
        })
        for col in ["标记时间", "入场时间"]:
            if col in open_view.columns:
                open_view[col] = open_view[col].apply(fmt_ts_bj)
    else:
        open_view = pd.DataFrame()

    if not paper_skipped_df.empty:
        paper_skipped_df = paper_skipped_df.sort_values("timestamp").tail(20)
        paper_skipped_view = paper_skipped_df[[c for c in [
            "timestamp", "signal_confirmed_at", "symbol", "side", "reason", "paper_active_positions", "paper_max_concurrent_positions"
        ] if c in paper_skipped_df.columns]].copy()
        paper_skipped_view = paper_skipped_view.rename(columns={
            "timestamp": "信号时间",
            "signal_confirmed_at": "确认时间",
            "symbol": "标的",
            "side": "方向",
            "reason": "paper拒单原因",
            "paper_active_positions": "当时占用仓位数",
            "paper_max_concurrent_positions": "最大并发仓位",
        })
        for col in ["信号时间", "确认时间"]:
            if col in paper_skipped_view.columns:
                paper_skipped_view[col] = paper_skipped_view[col].apply(fmt_ts_bj)
    else:
        paper_skipped_view = pd.DataFrame()

    code_version = run_text_command("git rev-parse --short=12 HEAD")
    shadow_name = str(summary.get("shadow_name") or status.get("name") or "Global strongest-only shadow")
    selection_cfg = summary.get("selection") if isinstance(summary.get("selection"), dict) else {}
    paper_cfg = paper_summary.get("assumptions") if isinstance(paper_summary.get("assumptions"), dict) else {}
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
  <p class='muted'><strong>这页回答的问题：</strong>“如果把 core + alt 全 universe 放在一起，同一 bar 只留 1 个最强者，这个 selector 会不会比当前 live 更会选票？”上半部分看 <strong>selector</strong>，下半部分看 <strong>paper PnL</strong>。</p>
  <p class='muted'><strong>和 alt shadow 的区别：</strong>global shadow 会做 <strong>全市场 strongest-only 淘汰赛</strong>，它要验证的是 selector 是否有效；alt shadow 不做这层淘汰赛，它是看 alt 候选池本身有没有 edge。一个回答“谁该赢”，一个回答“alt 池值不值得碰”。</p>
  <div class='grid'>
    <div class='card'><div class='k'>当前代码版本</div><div class='v'>{escape(fmt(code_version))}</div><div class='s'>与主 runner 共用同一套 signal adapter / selector / execution probe 函数</div></div>
    <div class='card'><div class='k'>最近一次运行</div><div class='v'>{escape(fmt_ts_bj(summary.get('generated_at_utc')))}</div><div class='s'>状态：{escape(fmt(summary.get('status')))}</div></div>
    <div class='card'><div class='k'>本轮 snapshot signals</div><div class='v'>{escape(fmt(summary.get('snapshot_signal_count')))}</div><div class='s'>近期全部候选信号</div></div>
    <div class='card'><div class='k'>本轮入选 winners</div><div class='v'>{escape(fmt(summary.get('selected_signal_count')))}</div><div class='s'>同 bar 只留一个 strongest</div></div>
    <div class='card'><div class='k'>最近累计 winners</div><div class='v'>{escape(fmt(summary.get('recent_selected_signal_count')))}</div><div class='s'>selector shadow 历史入选样本</div></div>
    <div class='card'><div class='k'>最近累计落选</div><div class='v'>{escape(fmt(summary.get('recent_skipped_signal_count')))}</div><div class='s'>被更强信号挤掉的样本</div></div>
    <div class='card'><div class='k'>selector 规则</div><div class='v'>{escape(fmt(selection_cfg.get('strength_metric')))}</div><div class='s'>strongest_only_per_bar={escape(fmt(selection_cfg.get('strongest_only_per_bar')))}</div></div>
  </div>

  <div class='grid'>
    <div class='card'><div class='k'>paper 已实现总收益</div><div class='v'>{escape(pct(paper_summary.get('paper_realized_total_return')))}</div><div class='s'>只统计已平仓 trades</div></div>
    <div class='card'><div class='k'>paper 标记总收益</div><div class='v'>{escape(pct(paper_summary.get('paper_marked_total_return')))}</div><div class='s'>已平仓 + 未平仓按最新价估值</div></div>
    <div class='card'><div class='k'>paper 已平仓笔数</div><div class='v'>{escape(fmt(paper_summary.get('paper_closed_trades')))}</div><div class='s'>closed win rate = {escape(pct(paper_summary.get('paper_closed_win_rate')))}</div></div>
    <div class='card'><div class='k'>paper 未平仓仓位</div><div class='v'>{escape(fmt(paper_summary.get('paper_open_positions')))}</div><div class='s'>当前纸上仍在持有的 winners</div></div>
    <div class='card'><div class='k'>paper 并发拒单</div><div class='v'>{escape(fmt(paper_summary.get('paper_skipped_by_max_concurrent')))}</div><div class='s'>因为 max_concurrent 被跳过的 winners</div></div>
    <div class='card'><div class='k'>paper 口径</div><div class='v'>{escape(fmt(paper_cfg.get('entry_style')))}</div><div class='s'>TP {escape(fmt(paper_cfg.get('tp_atr_mult')))} ATR / SL {escape(fmt(paper_cfg.get('sl_atr_mult')))} ATR / timeout {escape(fmt(paper_cfg.get('timeout_15m')))}x15m</div></div>
  </div>

  {global_curve_card}

  <h3>最近入选 winners</h3>
  {render_table(selected_view, digits_cols={'信号价':6, 'slope_strength':6})}

  <h3>paper 最近平仓</h3>
  {render_table(closed_view, digits_cols={'入场价':6, '出场价':6, '净收益':4, '持有分钟':0}, percent_cols={'净收益'})}

  <h3>paper 当前持仓</h3>
  {render_table(open_view, digits_cols={'入场价':6, '最新价':6, '浮动净收益':4, '持有分钟':0}, percent_cols={'浮动净收益'})}

  <h3>paper 按标的汇总</h3>
  {render_table(symbol_summary, digits_cols={'trades':0, 'closed':0, 'open':0, 'avg_effective_ret':4}, percent_cols={'marked_total_return','closed_win_rate','avg_effective_ret'})}

  <h3>paper 并发拒单记录</h3>
  {render_table(paper_skipped_view, digits_cols={'当时占用仓位数':0, '最大并发仓位':0})}

  <h3>最近被挤掉的 selector signals</h3>
  {render_table(skipped_view, digits_cols={'胜出强度':6, '本信号强度':6})}

  <h3>最近全部候选信号</h3>
  {render_table(sig_view, digits_cols={'信号价':6})}

  <p class='muted'>源配置：<code>{escape(str(CONFIG_PATH))}</code></p>
</body>
</html>
"""
    OUT_PATH.write_text(html, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
