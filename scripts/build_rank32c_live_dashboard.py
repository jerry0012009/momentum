#!/usr/bin/env python3
"""Build the Rank32c live trading dashboard HTML page.

Reads all rank32c artifacts and produces a self-contained report at:
  reports/site/factors/rank32c_live/report.html
"""
from __future__ import annotations

import csv
import io
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SITE_DIR = ROOT / "reports" / "site" / "factors" / "rank32c_live"
OUT_PATH = SITE_DIR / "report.html"

GATE_DIR = ROOT / "reports" / "artifacts" / "rank32c_pre_live_gate"
LIVE_DIR = ROOT / "reports" / "artifacts" / "rank32c_live"
STRATEGY_PY = ROOT / "src" / "momentum" / "strategies" / "rank32c_btc_utc_weak_cell.py"
LIVE_CONFIG = ROOT / "config" / "strategies" / "rank32c_btc_utc_weak_cell_v1_live.yaml"
TINY_CONFIG = ROOT / "config" / "strategies" / "rank32c_btc_utc_weak_cell_tiny_live.yaml"

BJ = timezone(timedelta(hours=8))
UTC = timezone.utc


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text("utf-8"))


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def bj_str(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(BJ)
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return iso


def utc_str(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return iso


def now_bj() -> str:
    return datetime.now(BJ).strftime("%Y-%m-%d %H:%M:%S 北京时间")


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text("utf-8")


def safe(v: Any, default: str = "—") -> str:
    if v is None or v == "":
        return default
    return escape(str(v))


def bps_fmt(v: Any) -> str:
    try:
        return f"{float(v):+.2f}"
    except Exception:
        return "—"


def pct_fmt(v: Any) -> str:
    try:
        return f"{float(v):+.2f}%"
    except Exception:
        return "—"


def dow_name(d: int) -> str:
    return ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][d] if 0 <= d <= 6 else str(d)


# ---------------------------------------------------------------------------
# data loading
# ---------------------------------------------------------------------------

def load_all() -> dict[str, Any]:
    d: dict[str, Any] = {}

    # gate artifacts
    d["release_decision"] = read_json(GATE_DIR / "release_decision.json")
    d["replay_summary"] = read_json(GATE_DIR / "recent_replay_summary.json")
    d["replay_trades"] = read_csv_rows(GATE_DIR / "recent_replay_trades.csv")
    d["gate_state"] = read_json(GATE_DIR / "state.json")
    d["gate_status"] = read_json(GATE_DIR / "status.json")
    d["gate_order_plan"] = read_json(GATE_DIR / "order_plan.json")
    d["gate_audit_md"] = read_text(GATE_DIR / "release_gate_audit.md")
    d["completion_audit_md"] = read_text(GATE_DIR / "completion_audit.md")

    # live artifacts
    d["live_order_plan"] = read_json(LIVE_DIR / "order_plan.json")
    d["live_last_run"] = read_json(LIVE_DIR / "last_run_summary.json")
    d["live_closed_trades"] = read_csv_rows(LIVE_DIR / "closed_trades.csv")
    d["live_events"] = []
    events_path = LIVE_DIR / "events.jsonl"
    if events_path.exists():
        for line in events_path.read_text("utf-8").strip().splitlines():
            if line.strip():
                d["live_events"].append(json.loads(line))
    d["live_shadow"] = read_csv_rows(GATE_DIR / "live_vs_shadow.csv")

    # configs
    d["live_config"] = read_text(LIVE_CONFIG)
    d["tiny_config"] = read_text(TINY_CONFIG)

    # strategy source (first 60 lines for overview)
    src_lines = read_text(STRATEGY_PY).splitlines()
    d["strategy_constants"] = "\n".join(src_lines[:40])

    # systemd timer status
    try:
        out = subprocess.check_output(
            ["systemctl", "list-timers", "--no-pager", "momentum-rank32c-*"],
            text=True, timeout=5,
        )
        d["timers_raw"] = out.strip()
    except Exception:
        d["timers_raw"] = ""

    return d


# ---------------------------------------------------------------------------
# SVG cumulative equity curve from replay trades
# ---------------------------------------------------------------------------

def build_equity_svg(trades: list[dict]) -> str:
    if not trades:
        return "<p class='muted'>No replay trades available.</p>"

    cum = 0.0
    points: list[tuple[int, float, str]] = []  # (idx, cum_pct, month)
    for i, t in enumerate(trades):
        try:
            bps = float(t.get("net_bps", 0))
        except Exception:
            bps = 0.0
        cum += bps / 10000 * 100  # convert bps to pct
        points.append((i, cum, t.get("month", "")))

    if not points:
        return "<p class='muted'>No valid data.</p>"

    W, H = 760, 260
    PAD_L, PAD_R, PAD_T, PAD_B = 56, 20, 20, 40
    plot_w = W - PAD_L - PAD_R
    plot_h = H - PAD_T - PAD_B

    y_vals = [p[1] for p in points]
    y_min = min(min(y_vals), 0)
    y_max = max(max(y_vals), 0)
    y_range = y_max - y_min or 1.0
    y_min -= y_range * 0.08
    y_max += y_range * 0.08
    y_range = y_max - y_min

    def x(i: int) -> float:
        return PAD_L + i / max(len(points) - 1, 1) * plot_w

    def y(v: float) -> float:
        return PAD_T + (1 - (v - y_min) / y_range) * plot_h

    # path
    path_d = " ".join(
        f"{'L' if i else 'M'}{x(i):.1f},{y(p[1]):.1f}"
        for i, p in enumerate(points)
    )
    # zero line
    zero_y = y(0)
    # area fill
    area_d = (
        path_d
        + f" L{x(len(points)-1):.1f},{y(0):.1f} L{x(0):.1f},{y(0):.1f} Z"
    )

    # y ticks
    y_ticks = []
    n_ticks = 5
    for i in range(n_ticks + 1):
        v = y_min + (y_max - y_min) * i / n_ticks
        yy = y(v)
        y_ticks.append(
            f'<line x1="{PAD_L}" y1="{yy:.1f}" x2="{W - PAD_R}" y2="{yy:.1f}" stroke="#e5e7eb" stroke-width="0.5"/>'
            f'<text x="{PAD_L - 6}" y="{yy:.1f}" text-anchor="end" fill="#6b7280" font-size="10" dominant-baseline="middle">{v:.1f}%</text>'
        )

    # x labels (every 3 months)
    x_labels = []
    for i, p in enumerate(points):
        if i % (max(len(points) // 6, 1)) == 0 or i == len(points) - 1:
            x_labels.append(
                f'<text x="{x(i):.1f}" y="{H - 6}" text-anchor="middle" fill="#6b7280" font-size="10">{p[2]}</text>'
            )

    # dots for loss trades
    dots = []
    for i, p in enumerate(points):
        color = "#ef4444" if p[1] < 0 else "#10b981"
        if i == 0 or abs(p[1] - points[i - 1][1]) > 0.3:
            dots.append(f'<circle cx="{x(i):.1f}" cy="{y(p[1]):.1f}" r="2.5" fill="{color}" opacity="0.7"/>')

    return f'''<svg viewBox="0 0 {W} {H}" style="width:100%;max-width:{W}px;height:auto;display:block;margin:0 auto">
  <defs>
    <linearGradient id="eqGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="#3b82f6" stop-opacity="0.02"/>
    </linearGradient>
  </defs>
  {"".join(y_ticks)}
  <line x1="{PAD_L}" y1="{zero_y:.1f}" x2="{W - PAD_R}" y2="{zero_y:.1f}" stroke="#9ca3af" stroke-width="0.8" stroke-dasharray="4,3"/>
  <path d="{area_d}" fill="url(#eqGrad)"/>
  <path d="{path_d}" fill="none" stroke="#3b82f6" stroke-width="1.8" stroke-linejoin="round"/>
  {"".join(dots)}
  {"".join(x_labels)}
  <text x="{PAD_L - 6}" y="{H - 6}" text-anchor="end" fill="#6b7280" font-size="10"></text>
</svg>'''


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------

def build_html(d: dict[str, Any]) -> str:
    decision = d["release_decision"]
    rs = d["replay_summary"]
    trades = d["replay_trades"]
    gate_state = d["gate_state"]
    gate_status = d["gate_status"]
    live_op = d["live_order_plan"]
    live_lr = d["live_last_run"]
    live_ct = d["live_closed_trades"]
    live_ev = d["live_events"]
    live_shadow = d["live_shadow"]
    timers_raw = d["timers_raw"]

    # ---- counts ----
    replay_total = len(trades)
    wins = sum(1 for t in trades if float(t.get("net_bps", 0)) > 0)
    losses = replay_total - wins
    win_rate = wins / replay_total * 100 if replay_total else 0
    cum_pct = rs.get("net_cum_pct", 0)
    mean_bps = rs.get("net_mean_bps", 0)

    # ---- current live state ----
    live_status = live_lr.get("status", "unknown")
    next_entry = live_lr.get("next_entry") or live_op.get("next_entry_ts", "")
    exit_ts = live_op.get("exit_ts", "")
    cell = live_op.get("selected_cell", {}) or {}
    kill_state = live_op.get("kill_switch_state", gate_state.get("kill_switch_state", ""))
    allow_live = gate_state.get("allow_live_orders", False)

    status_color = {
        "waiting": ("#3b82f6", "等待入场"),
        "entering": ("#f59e0b", "开仓中"),
        "holding": ("#10b981", "持仓中"),
        "exiting": ("#f59e0b", "平仓中"),
    }.get(live_status, ("#6b7280", safe(live_status)))
    status_badge_bg, status_label = status_color

    # ---- equity svg ----
    equity_svg = build_equity_svg(trades)

    # ---- replay trade table ----
    trade_rows = ""
    for t in trades:
        bps = float(t.get("net_bps", 0))
        color = "#dc2626" if bps < 0 else "#16a34a"
        trade_rows += f"""<tr>
  <td>{safe(t.get('month'))}</td>
  <td>{bj_str(t.get('signal_ts'))}</td>
  <td>{dow_name(int(t.get('dow', 0)))} {safe(t.get('hour'))}:00</td>
  <td>{safe(t.get('entry_open'))}</td>
  <td>{safe(t.get('exit_open'))}</td>
  <td>{bps_fmt(t.get('train_mean_long_bps'))}</td>
  <td style="color:{color};font-weight:600">{bps_fmt(bps)} bps</td>
</tr>"""

    # ---- live trade table ----
    live_rows = ""
    if live_ct:
        for t in live_ct:
            try:
                nr = float(t.get("net_ret", 0)) * 10000
            except Exception:
                nr = 0
            color = "#dc2626" if nr < 0 else "#16a34a"
            live_rows += f"""<tr>
  <td>{bj_str(t.get('entry_ts'))}</td>
  <td>{bj_str(t.get('exit_ts'))}</td>
  <td>{safe(t.get('side'))}</td>
  <td>{safe(t.get('notional_usdc'))}</td>
  <td>{safe(t.get('entry_price'))}</td>
  <td>{safe(t.get('exit_price'))}</td>
  <td>{safe(t.get('exit_reason'))}</td>
  <td style="color:{color};font-weight:600">{bps_fmt(nr)} bps</td>
</tr>"""
    else:
        live_rows = '<tr><td colspan="8" class="muted" style="text-align:center">暂无实盘交易记录 — 等待首次入场</td></tr>'

    # ---- live events ----
    events_html = ""
    if live_ev:
        for ev in live_ev[-20:]:  # last 20
            events_html += f"<tr><td>{safe(ev.get('ts'))}</td><td>{safe(ev.get('event'))}</td><td>{safe(ev.get('detail'), '')}</td></tr>"
    else:
        events_html = '<tr><td colspan="3" class="muted" style="text-align:center">暂无事件</td></tr>'

    # ---- honesty audit table (parsed from md) ----
    audit_rows = _parse_audit_table(d["gate_audit_md"])

    # ---- systemd timers ----
    timers_html = ""
    if timers_raw:
        for line in timers_raw.strip().splitlines()[1:]:  # skip header
            parts = line.split()
            timers_html += f"<tr><td><code>{safe(parts[-1]) if parts else '—'}</code></td><td>{safe(parts[0]) if len(parts) > 1 else '—'}</td></tr>"

    # ---- month-level stats ----
    month_stats = _compute_month_stats(trades)
    month_rows = ""
    for ms in month_stats:
        bps = ms["mean_bps"]
        color = "#dc2626" if bps < 0 else "#16a34a"
        month_rows += f"""<tr>
  <td>{safe(ms['month'])}</td>
  <td>{ms['count']}</td>
  <td>{ms['wins']}</td>
  <td>{ms['losses']}</td>
  <td style="color:{color};font-weight:600">{bps_fmt(bps)}</td>
  <td>{pct_fmt(ms['cum_pct'])}</td>
</tr>"""

    # ---- risk metrics ----
    bps_list = [float(t.get("net_bps", 0)) for t in trades]
    max_dd = 0.0
    peak = 0.0
    cum = 0.0
    for b in bps_list:
        cum += b
        if cum > peak:
            peak = cum
        dd = peak - cum
        if dd > max_dd:
            max_dd = dd
    sharpe_approx = (sum(bps_list) / len(bps_list)) / (max((sum((b - sum(bps_list)/len(bps_list))**2 for b in bps_list) / len(bps_list))**0.5, 0.01)) if bps_list else 0

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Rank32c BTCUSDT 实盘看板</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans SC',sans-serif;max-width:1200px;margin:0 auto;padding:24px 18px;line-height:1.6;color:#111827;background:#f1f5f9}}
h1{{font-size:26px;font-weight:700;margin-bottom:4px}}
h2{{font-size:18px;font-weight:700;margin:28px 0 10px;padding-bottom:6px;border-bottom:2px solid #e2e8f0}}
h3{{font-size:15px;font-weight:600;margin:16px 0 6px}}
.muted{{color:#6b7280;font-size:13px}}
.hero{{background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:20px 24px;margin-bottom:18px;box-shadow:0 1px 3px rgba(0,0,0,.04)}}
.card{{background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:16px 20px;margin-bottom:14px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
.grid3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px}}
.grid4{{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:14px}}
@media(max-width:720px){{.grid2,.grid3,.grid4{{grid-template-columns:1fr}}}}
.metric{{text-align:center;padding:14px 10px}}
.metric .val{{font-size:28px;font-weight:700;line-height:1.2}}
.metric .lbl{{font-size:12px;color:#6b7280;margin-top:2px}}
.pos{{color:#16a34a}}.neg{{color:#dc2626}}
.badge{{display:inline-block;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:600;color:#fff}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
th,td{{padding:7px 10px;text-align:left;border-bottom:1px solid #f1f5f9}}
th{{background:#f8fafc;font-weight:600;color:#475569;position:sticky;top:0}}
tr:hover{{background:#f8fafc}}
code{{background:#f1f5f9;padding:1px 5px;border-radius:4px;font-size:12px}}
.tag{{display:inline-block;padding:2px 8px;border-radius:6px;font-size:11px;font-weight:600;margin:1px 2px}}
.tag-pass{{background:#dcfce7;color:#166534}}.tag-fail{{background:#fee2e2;color:#991b1b}}
pre{{background:#1e293b;color:#e2e8f0;padding:14px 16px;border-radius:10px;overflow-x:auto;font-size:12px;line-height:1.5}}
.section-divider{{margin:32px 0 8px;font-size:13px;font-weight:600;color:#94a3b8;text-transform:uppercase;letter-spacing:1px}}
a{{color:#2563eb;text-decoration:none}}a:hover{{text-decoration:underline}}
.status-dot{{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px;vertical-align:middle}}
.progress-bar{{height:6px;background:#e2e8f0;border-radius:3px;overflow:hidden;margin-top:6px}}
.progress-fill{{height:100%;border-radius:3px;transition:width .3s}}
</style>
</head>
<body>

<!-- ===== HERO ===== -->
<div class="hero">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px">
    <div>
      <h1>Rank32c BTCUSDT 实盘看板</h1>
      <p class="muted">策略 <code>{safe(rs.get('strategy_id'))}</code> · {safe(rs.get('replay_start_month'))} ~ {safe(rs.get('replay_end_month_exclusive'))} 回测 · 实盘 tiny-live 100 USDC</p>
    </div>
    <div>
      <span class="badge" style="background:{status_badge_bg}">{status_label}</span>
      <span class="badge" style="background:#6366f1">KS: {safe(kill_state)}</span>
      <span class="badge" style="background:{'#16a34a' if allow_live else '#dc2626'}">{'LIVE' if allow_live else 'BLOCKED'}</span>
    </div>
  </div>
  <p class="muted" style="margin-top:8px">页面生成: {now_bj()}</p>
</div>

<!-- ===== KPI CARDS ===== -->
<div class="grid4">
  <div class="card metric"><div class="val pos">+{cum_pct:.2f}%</div><div class="lbl">累计净收益</div></div>
  <div class="card metric"><div class="val">+{mean_bps:.2f}</div><div class="lbl">均值净收益 (bps)</div></div>
  <div class="card metric"><div class="val">{replay_total}</div><div class="lbl">回测交易数</div></div>
  <div class="card metric"><div class="val">{win_rate:.1f}%</div><div class="lbl">胜率 ({wins}W / {losses}L)</div></div>
</div>
<div class="grid4">
  <div class="card metric"><div class="val">{sharpe_approx:.2f}</div><div class="lbl">Sharpe 近似 (月频)</div></div>
  <div class="card metric"><div class="val">{max_dd/100:.2f}%</div><div class="lbl">最大回撤 (bps→%)</div></div>
  <div class="card metric"><div class="val">{len(live_ct)}</div><div class="lbl">实盘完成交易</div></div>
  <div class="card metric"><div class="val">100 USDC</div><div class="lbl">每笔名义仓位</div></div>
</div>

<!-- ===== LIVE STATUS ===== -->
<h2>▸ 实盘运行状态</h2>
<div class="grid2">
  <div class="card">
    <h3>当前状态</h3>
    <table>
      <tr><td>运行状态</td><td><span class="status-dot" style="background:{status_badge_bg}"></span><b>{status_label}</b></td></tr>
      <tr><td>下次入场 (UTC)</td><td>{utc_str(next_entry)}</td></tr>
      <tr><td>下次入场 (北京)</td><td>{bj_str(next_entry)}</td></tr>
      <tr><td>预计出场 (UTC)</td><td>{utc_str(exit_ts)}</td></tr>
      <tr><td>预计出场 (北京)</td><td>{bj_str(exit_ts)}</td></tr>
      <tr><td>方向</td><td><b>{safe(live_op.get('side', '—')).upper()}</b></td></tr>
      <tr><td>Kill Switch</td><td><span class="badge" style="background:{'#16a34a' if kill_state=='armed' else '#dc2626'}">{safe(kill_state)}</span></td></tr>
      <tr><td>缓存最新 bar</td><td>{utc_str(live_op.get('cache_last_bar_utc'))}</td></tr>
    </table>
  </div>
  <div class="card">
    <h3>本月选中 Cell</h3>
    <table>
      <tr><td>Month</td><td>{safe(cell.get('month'))}</td></tr>
      <tr><td>Weekday</td><td>{dow_name(cell.get('dow', -1))} ({safe(cell.get('dow'))})</td></tr>
      <tr><td>Hour (UTC)</td><td>{safe(cell.get('hour'))}:00</td></tr>
      <tr><td>训练均值 (bps)</td><td style="color:#dc2626;font-weight:600">{bps_fmt(cell.get('train_mean_long_bps'))}</td></tr>
      <tr><td>训练事件数</td><td>{safe(cell.get('train_events'))}</td></tr>
      <tr><td>训练起始</td><td>{utc_str(cell.get('train_start_utc'))}</td></tr>
      <tr><td>训练结束</td><td>{utc_str(cell.get('train_end_exclusive_utc'))}</td></tr>
      <tr><td>Veto 高波</td><td>{'是 — 跳过' if live_op.get('veto_high_vol') else '否 — 允许'}</td></tr>
      <tr><td>Gate 通过</td><td>{'✓' if live_op.get('gate_pass') else '✗'}</td></tr>
    </table>
  </div>
</div>

<!-- systemd timers -->
<div class="card">
  <h3>systemd 定时任务</h3>
  <table>
    <tr><th>Timer Unit</th><th>最近/下次触发</th></tr>
    {timers_html if timers_html else '<tr><td colspan="2" class="muted">未检测到 timer 信息</td></tr>'}
  </table>
</div>

<!-- ===== STRATEGY OVERVIEW ===== -->
<h2>▸ 策略说明</h2>
<div class="card">
  <h3>原理概述</h3>
  <p>每月回顾过去 <b>60 个自然日</b> 的 BTCUSDT 15 分钟 K 线，按 (weekday, hour UTC) 分组统计未来 16 根 bar 的 long 收益率。
  选取均值最低（最弱）的 cell，在当月该 weekday/hour 对应时刻 <b>做空 BTCUSDT</b>，持仓 <b>4 小时</b>（16 根 15m bar），到期时间止损出场。</p>
  <p style="margin-top:8px">策略仅做空、不选币、无前瞻 — universe 固定 BTCUSDT，cell 选择严格使用历史数据。</p>
  <h3 style="margin-top:14px">核心参数</h3>
  <table>
    <tr><td>标的</td><td><b>BTCUSDT</b> (Binance Futures)</td></tr>
    <tr><td>K 线周期</td><td>15m</td></tr>
    <tr><td>方向</td><td>仅做空 (short only)</td></tr>
    <tr><td>持仓时间</td><td>16 bars = 4 小时</td></tr>
    <tr><td>训练窗口</td><td>前 60 个自然日</td></tr>
    <tr><td>Cell 选择</td><td>最弱 (weekday, hour) cell by long return</td></tr>
    <tr><td>回测成本假设</td><td>8 bps round-trip</td></tr>
    <tr><td>实盘成本假设</td><td>12 bps round-trip</td></tr>
    <tr><td>Veto 规则</td><td>前 24h 绝对收益 > 180d 均值 + 2σ 时跳过</td></tr>
    <tr><td>Gate 规则</td><td>cell train mean &lt; -round_trip_cost_bps 时才开仓</td></tr>
    <tr><td>No-overlap</td><td>同一时间只允许一笔持仓</td></tr>
  </table>
  <h3 style="margin-top:14px">Kill Switch</h3>
  <table>
    <tr><td>单笔亏损上限</td><td>-1.2%</td></tr>
    <tr><td>5 笔累计上限</td><td>-2.5%</td></tr>
    <tr><td>价差警戒</td><td>> 8 bps</td></tr>
    <tr><td>缺 bar 容忍</td><td>> 2 根</td></tr>
    <tr><td>滑点警戒</td><td>> 12 bps</td></tr>
    <tr><td>失败条件</td><td>≥8 笔 或 45 天后 realized mean net bps ≤ 0</td></tr>
  </table>
</div>

<!-- ===== HONESTY AUDIT ===== -->
<h2>▸ 诚实性审计 (Honesty Audit)</h2>
<div class="card">
  <p class="muted" style="margin-bottom:8px">放行决策: <span class="tag tag-pass">{safe(decision.get('decision'))}</span> — {safe(decision.get('release_reason'))}</p>
  <table>
    <tr><th>检查项</th><th>证据</th><th>结果</th></tr>
    {audit_rows}
  </table>
</div>

<!-- ===== BACKTEST EQUITY CURVE ===== -->
<h2>▸ 回测累计收益曲线</h2>
<div class="card">
  {equity_svg}
</div>

<!-- ===== MONTHLY BREAKDOWN ===== -->
<h2>▸ 逐月回测统计</h2>
<div class="card" style="overflow-x:auto">
  <table>
    <tr><th>Month</th><th>交易数</th><th>赢</th><th>亏</th><th>均值 (bps)</th><th>累计 %</th></tr>
    {month_rows}
  </table>
</div>

<!-- ===== REPLAY TRADES ===== -->
<h2>▸ 回测交易明细 ({replay_total} 笔)</h2>
<div class="card" style="overflow-x:auto;max-height:520px;overflow-y:auto">
  <table>
    <tr><th>Month</th><th>入场时间 (北京)</th><th>Cell</th><th>入场价</th><th>出场价</th><th>训练均值</th><th>净收益</th></tr>
    {trade_rows}
  </table>
</div>

<!-- ===== LIVE TRADES ===== -->
<h2>▸ 实盘交易记录</h2>
<div class="card" style="overflow-x:auto">
  <table>
    <tr><th>入场 (北京)</th><th>出场 (北京)</th><th>方向</th><th>名义</th><th>入场价</th><th>出场价</th><th>出场原因</th><th>净收益</th></tr>
    {live_rows}
  </table>
</div>

<!-- ===== LIVE EVENTS ===== -->
<h2>▸ 实盘事件日志 (最近 20 条)</h2>
<div class="card" style="overflow-x:auto;max-height:360px;overflow-y:auto">
  <table>
    <tr><th>时间</th><th>事件</th><th>详情</th></tr>
    {events_html}
  </table>
</div>

<!-- ===== LIVE VS BACKTEST ===== -->
<h2>▸ 实盘 vs 回测对照</h2>
<div class="card">
  {'<table><tr><th>信号</th><th>Shadow 入场</th><th>Live 入场</th><th>Shadow 收益</th><th>Live 收益</th><th>费用</th><th>滑点</th><th>偏差</th><th>对账</th></tr>' + "".join(
    f'<tr><td>{safe(r.get("entry_key"))}</td><td>{bj_str(r.get("shadow_entry_ts"))}</td><td>{bj_str(r.get("live_entry_ts"))}</td>'
    f'<td>{bps_fmt(r.get("shadow_ret"))}</td><td>{bps_fmt(r.get("live_ret"))}</td>'
    f'<td>{safe(r.get("fees_bps"))}</td><td>{safe(r.get("slippage_bps"))}</td><td>{safe(r.get("net_gap_bps"))}</td>'
    f'<td>{safe(r.get("reconciled"))}</td></tr>'
    for r in live_shadow
  ) + '</table>' if live_shadow else '<p class="muted">暂无对照数据 — 首笔实盘交易完成后自动生成。</p>'}
</div>

<!-- ===== KILL SWITCH DETAIL ===== -->
<h2>▸ 风控仪表盘</h2>
<div class="card">
  <div class="grid3">
    <div>
      <h3>当前 Kill Switch</h3>
      <p><span class="badge" style="background:{'#16a34a' if kill_state=='armed' else '#dc2626'}">{safe(kill_state)}</span></p>
      <p class="muted">触发后自动停止所有下单</p>
    </div>
    <div>
      <h3>回测风险指标</h3>
      <table>
        <tr><td>最大回撤</td><td>{max_dd/100:.2f}%</td></tr>
        <tr><td>最差单笔</td><td>{min(bps_list):.1f} bps</td></tr>
        <tr><td>最佳单笔</td><td>{max(bps_list):.1f} bps</td></tr>
        <tr><td>Sharpe (月频)</td><td>{sharpe_approx:.2f}</td></tr>
      </table>
    </div>
    <div>
      <h3>回测月度分布</h3>
      <table>
        <tr><td>盈利月</td><td>{sum(1 for m in month_stats if m['mean_bps']>0)}</td></tr>
        <tr><td>亏损月</td><td>{sum(1 for m in month_stats if m['mean_bps']<=0)}</td></tr>
        <tr><td>月均交易</td><td>{replay_total / max(len(month_stats),1):.1f}</td></tr>
      </table>
    </div>
  </div>
</div>

<!-- ===== CONFIG FILES ===== -->
<h2>▸ 配置文件</h2>
<div class="grid2">
  <div class="card">
    <h3>Live Config</h3>
    <pre>{safe(d['live_config'])}</pre>
  </div>
  <div class="card">
    <h3>Tiny-Live Spec</h3>
    <pre>{safe(d['tiny_config'])}</pre>
  </div>
</div>

<!-- ===== STRATEGY SOURCE CONSTANTS ===== -->
<h2>▸ 策略源码常量 (前 40 行)</h2>
<div class="card">
  <pre>{safe(d['strategy_constants'])}</pre>
</div>

<!-- ===== COMPLETION AUDIT ===== -->
<h2>▸ 上线完成审计</h2>
<div class="card">
  <pre style="white-space:pre-wrap">{safe(d['completion_audit_md'])}</pre>
</div>

<p class="muted" style="text-align:center;margin-top:32px;padding-bottom:18px">Rank32c Live Dashboard · Generated {now_bj()} · <a href="../">← Back to Hub</a></p>

</body>
</html>"""


def _parse_audit_table(md: str) -> str:
    """Parse the honesty audit markdown table into HTML rows."""
    rows = []
    in_table = False
    for line in md.splitlines():
        stripped = line.strip()
        if stripped.startswith("| Check") or stripped.startswith("| ---"):
            in_table = True
            continue
        if in_table and stripped.startswith("|"):
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if len(cells) >= 3:
                check, evidence, status = cells[0], cells[1], cells[2]
                tag = "tag-pass" if "pass" in status.lower() else "tag-fail"
                rows.append(
                    f"<tr><td>{safe(check)}</td><td>{safe(evidence)}</td>"
                    f"<td><span class='tag {tag}'>{safe(status)}</span></td></tr>"
                )
        elif in_table and not stripped.startswith("|"):
            in_table = False
    return "\n".join(rows) if rows else '<tr><td colspan="3" class="muted">未解析到审计记录</td></tr>'


def _compute_month_stats(trades: list[dict]) -> list[dict]:
    """Compute per-month summary stats."""
    months: dict[str, list[float]] = {}
    for t in trades:
        m = t.get("month", "")
        try:
            bps = float(t.get("net_bps", 0))
        except Exception:
            bps = 0.0
        months.setdefault(m, []).append(bps)

    stats = []
    cum = 0.0
    for m in sorted(months.keys()):
        bps_list = months[m]
        cum += sum(bps_list) / 10000 * 100
        stats.append({
            "month": m,
            "count": len(bps_list),
            "wins": sum(1 for b in bps_list if b > 0),
            "losses": sum(1 for b in bps_list if b <= 0),
            "mean_bps": sum(bps_list) / len(bps_list),
            "cum_pct": cum,
        })
    return stats


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    d = load_all()
    html = build_html(d)
    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"[ok] rank32c live dashboard → {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
