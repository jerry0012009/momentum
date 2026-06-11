#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "execution" / "rank32b_canary.yaml"
STATUS_PATH = ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase6_status.json"
SUMMARY_PATH = ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase6_last_run_summary.json"
EVENTS_PATH = ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase6_events.jsonl"
BASE_ALPHA_SCRIPT = ROOT / "scripts" / "build_rank32_ema_slope_clean_replication.py"
OUT_DIR = ROOT / "reports" / "site" / "factors" / "rank32b"
OUT_PATH = OUT_DIR / "transparency.html"
BASE = "/momentum"

SRC_MAP = [
    ("信号扫描", "src/momentum/execution/canary32b/signal_adapter.py:80", "load_recent_signals()：扫 recent_hours 内的候选信号，并生成 signal_id / atr14 / slope_strength"),
    ("同窗最强选择", "scripts/run_rank32b_canary_phase6.py:201", "select_signals_for_execution()：同一 timestamp 只保留 slope_strength 最强的币"),
    ("风险拦截", "src/momentum/risk/canary32b_guard.py:53", "evaluate_entry_risk()：trade_enabled / kill_switch / 并发 / ATR / data_delay / API 健康等"),
    ("安全暂停 + 新鲜度", "scripts/run_rank32b_canary_phase6.py:1524-1602", "先检查 exit_attach failure 安全暂停，再做 signal_too_old 新鲜度过滤"),
    ("挂单成交 / TTL fallback", "scripts/run_rank32b_canary_phase6.py:1155", "manage_pending_entries()：limit_gtx 若超时，可 fallback 市价进场"),
    ("入场后挂退出计划", "scripts/run_rank32b_canary_phase6.py:558", "attach_exit_plan()：挂 STOP_MARKET 止损 + LIMIT 止盈 + timeout 时间"),
]


def load_json(path: Path, default: Any):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def parse_utc(v: str | None) -> datetime | None:
    if not v:
        return None
    text = str(v).strip()
    if not text:
        return None
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except Exception:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def fmt_ts(v: str | None) -> str:
    dt = parse_utc(v)
    if not dt:
        return "-"
    bj = dt.astimezone(timezone(timedelta(hours=8)))
    return f"{bj.strftime('%Y-%m-%d %H:%M:%S')} 北京时间 / {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC"


def yesno(v: bool) -> str:
    return "是" if bool(v) else "否"


def code_version() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short=12", "HEAD"], cwd=str(ROOT), text=True).strip()
    except Exception:
        return "unknown"


def table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{escape(h)}</th>" for h in headers)
    body_rows = []
    for row in rows:
        body_rows.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"


def metric_card(label: str, value: str, sub: str) -> str:
    return f"<div class='metric'><div class='k'>{escape(label)}</div><div class='v'>{value}</div><div class='s'>{escape(sub)}</div></div>"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text:
            continue
        try:
            rows.append(json.loads(text))
        except Exception:
            continue
    return rows


def summarize_payload(payload: Any) -> str:
    if not isinstance(payload, dict):
        return "-"
    if "risk" in payload and isinstance(payload["risk"], dict):
        risk = payload["risk"]
        return ", ".join(
            part for part in [
                f"reason={risk.get('reason')}" if risk.get("reason") else "",
                f"age={risk.get('signal_age_seconds')}s" if risk.get("signal_age_seconds") is not None else "",
                f"max={risk.get('max_signal_age_seconds')}s" if risk.get("max_signal_age_seconds") is not None else "",
            ] if part
        ) or "risk payload"
    if "signal_id" in payload:
        parts = [f"signal_id={payload.get('signal_id')}"]
        if payload.get("bar_key"):
            parts.append(f"bar_key={payload.get('bar_key')}")
        if payload.get("timestamp"):
            parts.append(f"signal_ts={payload.get('timestamp')}")
        return ", ".join(parts)
    if "entry" in payload and isinstance(payload["entry"], dict):
        entry = payload["entry"]
        return f"entry={entry.get('type')}/{entry.get('avg_price') or entry.get('price')}"
    if "trace_id" in payload and "exit_reason" in payload:
        return f"exit_reason={payload.get('exit_reason')}, pnl={payload.get('net_pnl') if payload.get('net_pnl') is not None else payload.get('gross_pnl')}"
    keys = [str(k) for k in payload.keys()][:3]
    return ", ".join(keys) if keys else "payload"


def read_slope_floor() -> float | None:
    if not BASE_ALPHA_SCRIPT.exists():
        return None
    text = BASE_ALPHA_SCRIPT.read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("SLOPE_FLOOR") and "=" in line:
            try:
                return float(line.split("=", 1)[1].strip())
            except Exception:
                return None
    return None


def build_svg_alpha_principle(*, slope_floor: float | None) -> str:
    sf = f"{slope_floor:.4f}" if slope_floor is not None else "?"
    # Simple two-column schematic: LONG vs SHORT, with the exact boolean columns used in frame.
    return f"""
<svg viewBox='0 0 980 360' role='img' aria-label='32b alpha 信号逻辑示意图'>
  <defs>
    <linearGradient id='alphaG' x1='0' y1='0' x2='1' y2='1'>
      <stop offset='0%' stop-color='#10253b'/>
      <stop offset='100%' stop-color='#13233f'/>
    </linearGradient>
  </defs>

  <rect x='18' y='18' width='944' height='324' rx='18' fill='#0f172a' stroke='#274768' stroke-width='1.4'/>
  <text x='40' y='52' fill='#e5e7eb' font-size='18' font-weight='800'>Alpha：ema_cross_plus_slope_floor（信号触发）</text>
  <text x='40' y='78' fill='#94a3b8' font-size='13'>结构（1h EMA） + 触发（15m close 穿越 fast EMA） + 动量（slope floor） ⇒ signal</text>

  <!-- LONG column -->
  <rect x='40' y='104' width='440' height='214' rx='16' fill='url(#alphaG)' stroke='#274768' stroke-width='1.2'/>
  <text x='62' y='134' fill='#dbeafe' font-size='16' font-weight='800'>LONG signal</text>
  <text x='62' y='160' fill='#cbd5e1' font-size='13'>1) long_structure = (ema_fast_1h &gt; ema_slow_1h)</text>
  <text x='62' y='184' fill='#cbd5e1' font-size='13'>2) cross_only_long：prev_close ≤ prev_fast 且 close &gt; ema_fast_1h</text>
  <text x='62' y='208' fill='#cbd5e1' font-size='13'>3) slope_floor_long：fast_slope &gt; {sf} 且 slow_slope &gt; 0</text>
  <text x='62' y='232' fill='#cbd5e1' font-size='13'>4) slope_floor_long_signal = cross_only_long ∧ slope_floor_long</text>
  <text x='62' y='270' fill='#93c5fd' font-size='12'>注意：fast_slope/slow_slope = 1h EMA 的 pct_change</text>
  <text x='62' y='292' fill='#93c5fd' font-size='12'>spread_mid = (ema_fast_1h + ema_slow_1h) / 2</text>

  <!-- SHORT column -->
  <rect x='522' y='104' width='440' height='214' rx='16' fill='url(#alphaG)' stroke='#274768' stroke-width='1.2'/>
  <text x='544' y='134' fill='#dbeafe' font-size='16' font-weight='800'>SHORT signal</text>
  <text x='544' y='160' fill='#cbd5e1' font-size='13'>1) short_structure = (ema_fast_1h &lt; ema_slow_1h)</text>
  <text x='544' y='184' fill='#cbd5e1' font-size='13'>2) cross_only_short：prev_close ≥ prev_fast 且 close &lt; ema_fast_1h</text>
  <text x='544' y='208' fill='#cbd5e1' font-size='13'>3) slope_floor_short：fast_slope &lt; -{sf} 且 slow_slope &lt; 0</text>
  <text x='544' y='232' fill='#cbd5e1' font-size='13'>4) slope_floor_short_signal = cross_only_short ∧ slope_floor_short</text>
  <text x='544' y='270' fill='#93c5fd' font-size='12'>slope_strength = |fast_slope| + |slow_slope|（用于 strongest-only 选币）</text>
  <text x='544' y='292' fill='#93c5fd' font-size='12'>信号 timestamp 是 15m bar 的 close 时间（完成 bar）</text>
</svg>
""".strip()


def build_svg_flowchart(steps: list[dict[str, str]]) -> str:
    card_w = 320
    card_h = 96
    gap_y = 44
    x = 30
    total_h = 24 + len(steps) * card_h + (len(steps) - 1) * gap_y + 24
    svg_parts = [
        f"<svg viewBox='0 0 380 {total_h}' role='img' aria-label='32b live 流程图'>",
        "<defs>",
        "<linearGradient id='g1' x1='0' y1='0' x2='1' y2='1'>",
        "<stop offset='0%' stop-color='#10253b'/><stop offset='100%' stop-color='#13233f'/>",
        "</linearGradient>",
        "<marker id='arrow' markerWidth='10' markerHeight='10' refX='6' refY='3' orient='auto'><path d='M0,0 L0,6 L7,3 z' fill='#7dd3fc'/></marker>",
        "</defs>",
    ]
    for i, step in enumerate(steps):
        y = 20 + i * (card_h + gap_y)
        svg_parts.append(f"<rect x='{x}' y='{y}' width='{card_w}' height='{card_h}' rx='18' fill='url(#g1)' stroke='#274768' stroke-width='1.4' />")
        svg_parts.append(f"<text x='{x+18}' y='{y+28}' fill='#e5e7eb' font-size='16' font-weight='700'>{escape(step['title'])}</text>")
        svg_parts.append(f"<text x='{x+18}' y='{y+52}' fill='#93c5fd' font-size='12'>{escape(step['meta'])}</text>")
        svg_parts.append(f"<text x='{x+18}' y='{y+74}' fill='#94a3b8' font-size='12'>{escape(step['desc'])}</text>")
        if i < len(steps) - 1:
            y1 = y + card_h
            y2 = y + card_h + gap_y - 10
            svg_parts.append(f"<line x1='{x + card_w/2}' y1='{y1 + 4}' x2='{x + card_w/2}' y2='{y2}' stroke='#7dd3fc' stroke-width='2.2' marker-end='url(#arrow)' />")
    svg_parts.append("</svg>")
    return "".join(svg_parts)


def recent_run_events(summary: dict[str, Any], events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    start = parse_utc(summary.get("run_started_at"))
    end = parse_utc(summary.get("run_finished_at")) or parse_utc(summary.get("generated_at_utc"))
    if not start or not end:
        return []
    picked: list[dict[str, Any]] = []
    for row in events:
        ts = parse_utc(row.get("timestamp"))
        if not ts:
            continue
        if start <= ts <= end:
            picked.append(row)
    return picked[-16:]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    cfg = load_yaml(CONFIG_PATH)
    status = load_json(STATUS_PATH, {})
    summary = load_json(SUMMARY_PATH, {})
    events = load_jsonl(EVENTS_PATH)

    phase6 = cfg.get("phase6", {})
    safety = phase6.get("safety", {}) if isinstance(phase6.get("safety"), dict) else {}
    selection = phase6.get("selection", {}) if isinstance(phase6.get("selection"), dict) else {}
    sizing = phase6.get("sizing", {}) if isinstance(phase6.get("sizing"), dict) else {}
    entry = phase6.get("entry", {}) if isinstance(phase6.get("entry"), dict) else {}
    exit_cfg = phase6.get("exit", {}) if isinstance(phase6.get("exit"), dict) else {}
    risk = cfg.get("risk", {})
    signal_adapter = cfg.get("signal_adapter", {})
    universe = list(cfg.get("universe", {}).get("symbols", []))

    generated_at_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    generated_at = fmt_ts(generated_at_iso)
    recent_hours = int(signal_adapter.get("recent_hours", 72) or 72)
    freshness_minutes = float(safety.get("max_signal_age_minutes", 30) or 30)
    freshness_ratio = freshness_minutes / float(recent_hours * 60) if recent_hours > 0 else 0.0
    window_desc = f"扫描最近 {recent_hours}h 信号，但只允许 <= {freshness_minutes:.0f} 分钟的信号真正进入交易队列"
    current_order_type = str(entry.get("order_type", "market"))
    selection_mode = str(selection.get("mode", "-") or "-")
    strength_metric = str(selection.get("strength_metric", "-") or "-")
    max_positions = int(risk.get("max_concurrent_positions", 1) or 1)
    max_new = int(phase6.get("max_new_signals_per_run", 1) or 1)
    leverage = int(phase6.get("default_leverage", 1) or 1)
    desired_notional = float(sizing.get("desired_notional_usdt", 0.0) or 0.0)
    timeout_minutes = int(exit_cfg.get("timeout_minutes", 120) or 120)
    data_delay_s = int(risk.get("max_data_delay_seconds", 0) or 0)
    data_delay_h = data_delay_s / 3600.0 if data_delay_s else 0.0

    config_rows = [
        ["运行模式", escape(str(phase6.get("mode", "-")))],
        ["Universe", escape(", ".join(universe))],
        ["Signal variant", escape(str(signal_adapter.get("variant", "-")))],
        ["Signal lookback days", escape(str(signal_adapter.get("lookback_days", "-")))],
        ["Signal scan window", escape(f"{recent_hours}h")],
        ["Trade freshness gate", escape(f"<= {freshness_minutes:.0f}m")],
        ["Selection", escape(f"{selection_mode} / {strength_metric}")],
        ["Max new signals per run", escape(str(max_new))],
        ["Max concurrent positions", escape(str(max_positions))],
        ["Require ATR", escape(yesno(bool(risk.get('require_atr', True))))],
        ["Entry order type", escape(current_order_type)],
        ["Entry TTL", escape(f"{int(entry.get('ttl_minutes', 15) or 15)}m")],
        ["Limit TTL fallback to market", escape(yesno(bool(entry.get('fallback_to_market_on_ttl', True))))],
        ["Desired notional", escape(f"{desired_notional:.2f} USDT / symbol")],
        ["Default leverage", escape(f"{leverage}x")],
        ["TP / SL / Timeout", escape(f"{float(exit_cfg.get('tp_atr_mult', 1.25)):.2f} ATR / {float(exit_cfg.get('sl_atr_mult', 1.0)):.2f} ATR / {timeout_minutes}m")],
        ["Safety pause cooldown", escape(f"{int(safety.get('pause_new_entries_minutes_after_exit_attach_failure', 0) or 0)}m (当前关闭)")],
        ["Data delay coarse limit", escape(f"{data_delay_s}s ≈ {data_delay_h:.1f}h")],
    ]

    debug_rows = [
        ["phase6_status.json", "当前 live 总状态：latest bar、trade_enabled、kill_switch、system_health"],
        ["phase6_last_run_summary.json", "最近一轮到底看到了几个信号、处理了几个、下了几笔单、有没有 safety pause"],
        ["phase6_state.json", "seen_signal_ids / consumed_signal_bars / pending_entries / live_positions / closed_trades 的真实 checkpoint"],
        ["phase6_recent_rejections.json", "为什么没交易：signal_too_old / same_bar / risk reject / safety pause"],
        ["phase6_recent_orders.json", "下单明细：entry / stop_loss / take_profit / timeout_close"],
        ["phase6_recent_closed_trades.json", "已平仓明细：exit_reason / pnl / fee / code_version / config_version"],
        ["phase6_warnings.json", "attach 失败、query 失败、外部仓位干扰等告警"],
        ["phase6_events.jsonl", "最细的逐步事件时间线，适合还原一次 run 的全过程"],
    ]

    bug_rows = [
        ["历史信号 backlog", f"当前 adapter 仍扫描最近 {recent_hours}h；真正防 bug 的是 {freshness_minutes:.0f}m 新鲜度门。", "优先看 phase6_recent_rejections.json 是否出现 signal_too_old"],
        ["同窗多币竞争", "同一 timestamp 只留最强 slope_strength；其余会被 weaker_than_strongest_signal_in_same_bar 拒掉。", "不要把“没下 ETH”误判成“没看到 ETH 信号”"],
        ["单席位限制", f"max_concurrent_positions={max_positions}；有 live/pending 后，后续新币信号会被 too_many_positions 拦截。", "看 recent_rejections 和 phase6_state"],
        ["entry 配置双轨", f"当前 live 真正使用的是 phase6.entry.order_type={current_order_type}；execution.entry 更像旧 phase/辅助配置。", "改配置时优先改 phase6.entry，避免改错块"],
        ["外部账户干扰", "交易所里存在非 whitelist 仓位时，Dashboard 可能提示 unexpected_exchange_positions。", "它不会自动替你清仓，但会影响保证金和判断"],
        ["安全暂停", "当前已关闭；若未来打开，只会看当前 code_version 之后发生的 attach-failure。", "旧版本失败不应继续封锁新版本测试"],
    ]

    step_docs = [
        {
            "title": "① 定时器唤醒",
            "meta": "systemd timer / 每 5 分钟 / 但逻辑 bar 仍按 15m",
            "desc": "每轮先同步 pending/live，再看新的交易候选。",
            "why": "先同步状态，避免系统以为自己 flat，但交易所里其实还有仓或挂单。",
            "watch": "phase6_last_run_summary.json 的 latest_evaluated_bar_time、managed_pending_entries、managed_live_positions。",
            "src": "ops/systemd/momentum-rank32b-canary-phase6.timer + run_rank32b_canary_phase6.py main()",
        },
        {
            "title": "② 扫描候选信号",
            "meta": f"variant={signal_adapter.get('variant', '-')}, recent_hours={recent_hours}h",
            "desc": "Signal adapter 从最近窗口里捞出候选信号，附带 ATR14、slope_strength。",
            "why": "这里负责“看到什么机会”，不是最终是否能交易。",
            "watch": "phase6_status.json 的 recent_signal_count、phase6_events.jsonl 里的 SignalReceived。",
            "src": "src/momentum/execution/canary32b/signal_adapter.py:80",
        },
        {
            "title": "③ strongest-only 选币",
            "meta": f"selection={selection_mode}, metric={strength_metric}",
            "desc": "同一 timestamp 多币同时触发时，只保留 strongest 一个。",
            "why": "把策略从“多币全追”收敛成“同窗只打最强”。",
            "watch": "phase6_last_run_summary.json 的 skipped_weaker_signals、recent_rejections 的 weaker_than_strongest_signal_in_same_bar。",
            "src": "run_rank32b_canary_phase6.py:201",
        },
        {
            "title": "④ 新鲜度过滤",
            "meta": f"扫描 {recent_hours}h，但 trade freshness <= {freshness_minutes:.0f}m",
            "desc": "即使 adapter 扫到了旧信号，只要超龄，也会被 signal_too_old 拒绝。",
            "why": "这是修复陈旧信号 bug 的关键逻辑。",
            "watch": "phase6_recent_rejections.json 是否出现 signal_too_old；payload 里看 signal_age_seconds。",
            "src": "run_rank32b_canary_phase6.py:1554-1602",
        },
        {
            "title": "⑤ 风控放行 / 拒绝",
            "meta": f"trade_enabled={yesno(bool(risk.get('trade_enabled', False)))}, kill_switch={yesno(bool(risk.get('kill_switch', True)))}, max_positions={max_positions}",
            "desc": "检查 symbol、并发、live/pending、ATR、data_delay、API 健康等。",
            "why": "它回答的是“这个信号能不能真的变成一笔交易”。",
            "watch": "recent_rejections 的 reason；phase6_last_run_summary.json 的 risk_rejections。",
            "src": "src/momentum/risk/canary32b_guard.py:53",
        },
        {
            "title": "⑥ 入场",
            "meta": f"当前 live entry={current_order_type}, TTL={int(entry.get('ttl_minutes', 15) or 15)}m",
            "desc": "当前 live 默认走 MARKET；如果未来改回 limit_gtx，则可能走 TTL 后 fallback。",
            "why": "这里决定 admission/fill 确定性与成本结构。",
            "watch": "phase6_recent_orders.json 的 order_role=entry；events 里的 ORDER_PLACED / PositionOpened。",
            "src": "run_rank32b_canary_phase6.py:1720+ / 1155+",
        },
        {
            "title": "⑦ 挂退出计划",
            "meta": f"TP={float(exit_cfg.get('tp_atr_mult', 1.25)):.2f} ATR, SL={float(exit_cfg.get('sl_atr_mult', 1.0)):.2f} ATR, timeout={timeout_minutes}m",
            "desc": "入场后立即挂 STOP_MARKET 止损 + LIMIT 止盈，并设置 timeout。",
            "why": "这是 live 风险闭环；任何 attach 失败都要被重点监控。",
            "watch": "warnings.json、recent_orders、recent_closed_trades 的 exit_reason。",
            "src": "run_rank32b_canary_phase6.py:558",
        },
        {
            "title": "⑧ 写状态与回放",
            "meta": "status.json / state.json / recent_* / events.jsonl",
            "desc": "所有页面、巡检、邮件、排障都依赖这些文件。",
            "why": "如果状态文件不透明，后面就只能靠猜。",
            "watch": "phase6_status.json、phase6_state.json、phase6_events.jsonl。",
            "src": "run_rank32b_canary_phase6.py run end checkpoint + dashboard builders",
        },
    ]

    svg = build_svg_flowchart(step_docs)
    alpha_svg = build_svg_alpha_principle(slope_floor=read_slope_floor())
    src_rows = [[escape(a), f"<code>{escape(b)}</code>", escape(c)] for a, b, c in SRC_MAP]

    metrics = "".join(
        [
            metric_card("当前代码版本", f"<span>{escape(code_version())}</span>", "页面生成时 HEAD commit"),
            metric_card("当前 config hash", f"<span>{escape(str(status.get('current_config_hash', '-')))}</span>", "phase6_status.json 记录"),
            metric_card("最近完成 bar", f"<span>{escape(fmt_ts(status.get('latest_evaluated_bar_time')))}</span>", "最近真的参与计算的 bar"),
            metric_card("最近信号时间", f"<span>{escape(fmt_ts(status.get('last_signal_time')))}</span>", "最近一次生成信号，不等于最近计算时间"),
            metric_card("窗口信号 / 新处理 / 风险拒绝", f"<span>{int(summary.get('signals_seen_this_window', 0) or 0)} / {int(summary.get('new_signals_processed', 0) or 0)} / {int(summary.get('risk_rejections', 0) or 0)}</span>", "最近一轮 run 的统计"),
            metric_card("外部仓位告警", f"<span>{int(summary.get('unexpected_exchange_positions', 0) or 0)}</span>", "非 canary 白名单仓位数"),
        ]
    )

    replay_rows: list[list[str]] = []
    for row in recent_run_events(summary, events):
        replay_rows.append([
            escape(fmt_ts(row.get("timestamp"))),
            f"<code>{escape(str(row.get('event_type') or '-'))}</code>",
            escape(str(row.get("symbol") or "-")),
            escape(str(row.get("message") or "-")),
            escape(summarize_payload(row.get("payload"))),
        ])
    replay_html = (
        table(["时间", "事件", "币种", "说明", "关键 payload"], replay_rows)
        if replay_rows
        else "<p class='small'>最近一次 run 没有留下可展示的逐步事件，通常意味着这轮只是常规同步，没有新 signal / intention / order / rejection。</p>"
    )

    accordion_html = "".join(
        f"""
        <details class='accordion'>
          <summary>{escape(step['title'])}｜{escape(step['meta'])}</summary>
          <div class='accordion-body'>
            <p><b>这一步在做什么：</b>{escape(step['desc'])}</p>
            <p><b>为什么重要：</b>{escape(step['why'])}</p>
            <p><b>排障先看：</b>{escape(step['watch'])}</p>
            <p><b>源码位置：</b><code>{escape(step['src'])}</code></p>
          </div>
        </details>
        """
        for step in step_docs
    )

    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>32b 实盘交易逻辑透明页</title>
  <style>
    :root{{--bg:#0b1120;--panel:#111827;--panel2:#0f172a;--line:#24324a;--text:#e5e7eb;--muted:#94a3b8;--accent:#7dd3fc;--good:#34d399;--warn:#fbbf24;--bad:#f87171;}}
    *{{box-sizing:border-box}}
    body{{margin:0;background:linear-gradient(180deg,#0b1120,#0f172a 28%,#0b1120);color:var(--text);font:16px/1.7 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif}}
    .wrap{{max-width:1180px;margin:0 auto;padding:30px 20px 64px}}
    h1,h2,h3{{margin:0 0 10px}}
    p{{margin:0 0 12px;color:var(--muted)}}
    a{{color:var(--accent);text-decoration:none;font-weight:700}}
    .hero,.card,.step,.callout,.table-card,.svg-card,.accordion{{background:rgba(17,24,39,.96);border:1px solid var(--line);border-radius:18px;box-shadow:0 14px 36px rgba(0,0,0,.20)}}
    .hero{{padding:24px 24px 18px;margin-bottom:18px}}
    .card,.table-card,.svg-card{{padding:18px 18px 16px;margin-bottom:16px}}
    .nav{{display:flex;flex-wrap:wrap;gap:10px 12px;margin-top:10px}}
    .badge{{display:inline-block;padding:4px 10px;border-radius:999px;border:1px solid #28456d;background:#13233f;color:#bfdbfe;font-size:12px;margin-right:8px;margin-bottom:8px}}
    .lead{{color:#dbeafe;font-size:18px}}
    .metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin:18px 0}}
    .metric{{background:#0f172a;border:1px solid #1f2d45;border-radius:16px;padding:14px}}
    .metric .k{{font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:#93c5fd}}
    .metric .v{{font-size:22px;font-weight:800;margin-top:8px;word-break:break-word}}
    .metric .s{{margin-top:8px;color:var(--muted);font-size:13px}}
    .section-title{{margin:26px 0 12px}}
    .flow{{display:grid;gap:12px;margin-top:12px}}
    .step{{padding:16px 18px;position:relative}}
    .step h3{{font-size:18px;margin-bottom:6px}}
    .step .meta{{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0 10px}}
    .chip{{display:inline-block;padding:3px 8px;border-radius:999px;background:#10253b;border:1px solid #274768;color:#c7d2fe;font-size:12px}}
    .arrow{{text-align:center;color:#7dd3fc;font-size:28px;line-height:1}}
    .cols{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}}
    .callout{{padding:16px 18px}}
    .good{{border-color:#1f6c4d;background:rgba(7,61,42,.22)}}
    .warn{{border-color:#7c5a14;background:rgba(92,58,6,.22)}}
    .bad{{border-color:#7f1d1d;background:rgba(79,20,20,.22)}}
    .svg-wrap{{width:100%;overflow:auto}}
    svg{{width:100%;min-width:360px;height:auto;display:block}}
    table{{width:100%;border-collapse:collapse;margin-top:10px}}
    th,td{{text-align:left;padding:10px 12px;border-bottom:1px solid #1f2937;vertical-align:top;font-size:14px}}
    th{{background:#0f172a;color:#cbd5e1}}
    tr:last-child td{{border-bottom:none}}
    code{{background:#0f172a;border:1px solid #1f2937;border-radius:8px;padding:2px 6px;color:#dbeafe}}
    ul{{margin:8px 0 0 18px;color:#cbd5e1}}
    li{{margin:5px 0}}
    .muted-strong{{color:#cbd5e1}}
    .small{{font-size:13px;color:var(--muted)}}
    .accordion{{margin-bottom:10px;overflow:hidden}}
    .accordion summary{{cursor:pointer;list-style:none;padding:16px 18px;font-weight:700;color:#dbeafe}}
    .accordion summary::-webkit-details-marker{{display:none}}
    .accordion-body{{padding:0 18px 16px 18px;border-top:1px solid #1f2937}}
  </style>
</head>
<body>
  <div class='wrap'>
    <div class='hero'>
      <div>
        <span class='badge'>32b</span>
        <span class='badge'>透明化</span>
        <span class='badge'>流程图 + Source of Truth</span>
        <span class='badge'>Run Replay</span>
      </div>
      <h1>32b 实盘交易逻辑透明页</h1>
      <p class='lead'>这页不是回测页，也不是只看结果的 Dashboard。它专门把 <strong>信号 → 选币 → 新鲜度 → 风控 → 下单 → 挂 TP/SL → timeout → 状态文件</strong> 整条链路透明化，方便你以后更快定位 bug 和理解能力边界。</p>
      <p>页面生成时间：{generated_at}</p>
      <div class='nav'>
        <a href='{BASE}/factors/rank32b/report.html'>32b 主页面</a>
        <a href='{BASE}/factors/rank32b_canary/report.html'>实盘 Dashboard</a>
        <a href='{BASE}/canary-doc/'>实盘控制台</a>
        <a href='{BASE}/factors/scout_rank32b_slope_floor_continuation_15m/report.html'>主研究报告</a>
      </div>
    </div>

    <div class='card'>
      <h2>当前 live 配置快照</h2>
      <p>先记住一句最重要的：<span class='muted-strong'>{escape(window_desc)}</span>。这就是“陈旧信号”问题最核心的透明化结论。</p>
      <div class='metrics'>{metrics}</div>
    </div>

    <h2 class='section-title'>总览流程图（SVG）</h2>
    <div class='svg-card'>
      <p>先看这张图，知道 32b 实盘现在到底是怎么从一根 K 线走到一笔交易的。后面每一步都有展开说明。</p>
      <div class='svg-wrap'>{svg}</div>
    </div>

    <h2 class='section-title'>Alpha 基本原理（信号层）</h2>
    <div class='svg-card'>
      <p>如果你只想先搞懂 32b 的 alpha 到底在“看什么”，先看这张图。它回答的是 <strong>哪根 15m bar 会被认成 long/short 信号</strong>，还没进入 strongest-only、freshness、risk、下单这些执行层。</p>
      <div class='svg-wrap'>{alpha_svg}</div>
    </div>

    <div class='cols'>
      <div class='callout good'>
        <h3>一句话版本</h3>
        <p>32b 不是裸追涨杀跌。它先用 <code>1h EMA fast/slow</code> 定结构方向，再要求 <code>15m close</code> 穿越 fast EMA，同时要求 <code>EMA slope</code> 够强，才把这根 bar 记成可交易信号。</p>
      </div>
      <div class='callout warn'>
        <h3>边界要分清</h3>
        <p>这张图只解释 <strong>alpha 信号如何触发</strong>。信号触发后，是否真的变成交易，还要继续经过 <code>same-bar strongest-only</code>、<code>signal_too_old</code>、风控、并发和下单链路。</p>
      </div>
    </div>

    <div class='card'>
      <h3>把图翻成人话</h3>
      <ul>
        <li><strong>结构层：</strong><code>ema_fast_1h &gt; ema_slow_1h</code> 只允许看多；<code>ema_fast_1h &lt; ema_slow_1h</code> 只允许看空。</li>
        <li><strong>触发层：</strong>不是一直持有，而是等 <code>15m close</code> 从 fast EMA 一侧重新穿回另一侧，形成一次 close-confirmed cross。</li>
        <li><strong>动量层：</strong>除了方向对，还要求 <code>fast_slope</code> 和 <code>slow_slope</code> 不只是同向，而且达到最小斜率门槛，避免把太弱的均线结构也当 continuation。</li>
        <li><strong>排序层：</strong><code>slope_strength = |fast_slope| + |slow_slope|</code> 不是新信号条件，而是多个币同窗竞争时用来选“谁更强”。</li>
      </ul>
    </div>

    <h2 class='section-title'>逐步拆解（适合排障时展开看）</h2>
    <div>{accordion_html}</div>

    <h2 class='section-title'>一张图看懂：从 K 线到成交的完整流程</h2>
    <div class='flow'>
      <div class='step'>
        <h3>① 定时器唤醒 Phase6</h3>
        <div class='meta'><span class='chip'>systemd timer</span><span class='chip'>OnUnitActiveSec=5min</span><span class='chip'>先同步再看新信号</span></div>
        <p>Runner 大约每 5 分钟跑一次，但信号本身仍然是按 15m bar 来定义。每次 run 会先同步 pending/live/交易所状态，再看新的交易机会。</p>
      </div>
      <div class='arrow'>↓</div>
      <div class='step'>
        <h3>② 扫描候选信号</h3>
        <div class='meta'><span class='chip'>variant={escape(str(signal_adapter.get('variant', '-')))}</span><span class='chip'>lookback={escape(str(signal_adapter.get('lookback_days', '-')))}d</span><span class='chip'>scan={recent_hours}h</span></div>
        <p>Signal adapter 会为 {len(universe)} 个币读取 bars、构建 frame、计算 ATR14，并在最近 {recent_hours} 小时窗口内找出满足 <code>ema_cross_plus_slope_floor</code> 的信号，同时产出 <code>slope_strength</code>、<code>atr14</code>、<code>signal_id</code> 等元数据。</p>
      </div>
      <div class='arrow'>↓</div>
      <div class='step'>
        <h3>③ 先做“同窗最强”筛选</h3>
        <div class='meta'><span class='chip'>{escape(selection_mode)}</span><span class='chip'>strongest_only_per_bar={escape(yesno(bool(selection.get('strongest_only_per_bar', False))))}</span><span class='chip'>metric={escape(strength_metric)}</span></div>
        <p>若多个币在同一个 timestamp 同时出信号，系统只保留 <code>{escape(strength_metric)}</code> 最强的那个，其余信号会被记录成 <code>weaker_than_strongest_signal_in_same_bar</code>，而不是“静默消失”。</p>
      </div>
      <div class='arrow'>↓</div>
      <div class='step'>
        <h3>④ 再做“新鲜度”过滤</h3>
        <div class='meta'><span class='chip'>freshness &lt;= {freshness_minutes:.0f}m</span><span class='chip'>当前占扫描窗口的 {freshness_ratio:.2%}</span></div>
        <p>这里是陈旧信号 bug 的核心修复点：即便 adapter 扫描最近 {recent_hours}h，真正进入交易决策的信号也必须满足 <code>now - signal.timestamp &lt;= {freshness_minutes:.0f} 分钟</code>。超龄信号会被记为 <code>signal_too_old</code>，并写入 rejections / warnings。</p>
      </div>
      <div class='arrow'>↓</div>
      <div class='step'>
        <h3>⑤ 风控判定：到底能不能交易</h3>
        <div class='meta'><span class='chip'>trade_enabled={escape(yesno(bool(risk.get('trade_enabled', False))))}</span><span class='chip'>kill_switch={escape(yesno(bool(risk.get('kill_switch', True))))}</span><span class='chip'>max_concurrent_positions={max_positions}</span></div>
        <p>风控会依次检查：交易开关、kill switch、symbol 是否在 universe、同币是否已有 live/pending、总并发是否超限、是否达到日内交易数上限、API 健康、data delay、ATR 是否可用等。任何一条不过，都会给出明确 reject reason。</p>
      </div>
      <div class='arrow'>↓</div>
      <div class='step'>
        <h3>⑥ 选币与仓位</h3>
        <div class='meta'><span class='chip'>Universe={len(universe)} symbols</span><span class='chip'>max_new_signals_per_run={max_new}</span><span class='chip'>desired_notional={desired_notional:.0f}U</span></div>
        <p>当前是“六选一、单席位”模型：Universe 为 {escape(', '.join(universe))}，每轮最多只处理 {max_new} 个新信号，同时总并发仓位上限为 {max_positions}。这意味着它更像“扩机会池”，而不是“6 个币一起上仓”。</p>
      </div>
      <div class='arrow'>↓</div>
      <div class='step'>
        <h3>⑦ 下单执行</h3>
        <div class='meta'><span class='chip'>当前 live entry={escape(current_order_type)}</span><span class='chip'>TTL={int(entry.get('ttl_minutes', 15) or 15)}m</span><span class='chip'>fallback_to_market={escape(yesno(bool(entry.get('fallback_to_market_on_ttl', True))))}</span></div>
        <p><strong>当前 live 默认是市价单入场。</strong> 如果以后切回 <code>limit_gtx</code>，则会先挂限价单，等到 TTL 到期后，若配置允许，可自动 fallback 到 market。这里要特别注意：<code>phase6.entry</code> 才是当前 live 的主配置入口。</p>
      </div>
      <div class='arrow'>↓</div>
      <div class='step'>
        <h3>⑧ 入场后立即挂退出计划</h3>
        <div class='meta'><span class='chip'>TP={float(exit_cfg.get('tp_atr_mult', 1.25)):.2f} ATR</span><span class='chip'>SL={float(exit_cfg.get('sl_atr_mult', 1.0)):.2f} ATR</span><span class='chip'>timeout={timeout_minutes}m</span></div>
        <p>一旦 entry 成交，系统会立即尝试挂：<code>STOP_MARKET</code> 止损 + <code>LIMIT</code> 止盈，并记录 timeout 时间。若既没 hit TP、也没 hit SL，到 {timeout_minutes} 分钟会走 <code>timeout_market</code> 市价平仓。</p>
      </div>
      <div class='arrow'>↓</div>
      <div class='step'>
        <h3>⑨ 写状态文件，供 Dashboard / 邮件 / 巡检读取</h3>
        <div class='meta'><span class='chip'>status.json</span><span class='chip'>run_summary.json</span><span class='chip'>state.json</span><span class='chip'>events.jsonl</span></div>
        <p>每轮 run 结束后，phase6 会写出状态、最近订单、最近仓位、最近平仓、最近拒绝、warnings、以及带 checkpoint 的 <code>phase6_state.json</code>。这就是你以后定位“策略到底在想什么”的透明化基础设施。</p>
      </div>
    </div>

    <div class='cols' style='margin-top:18px'>
      <div class='callout good'>
        <h3>当前最重要的透明结论</h3>
        <p>现在的逻辑已经把“历史扫描窗口”和“真实可交易新鲜度”拆开了：</p>
        <ul>
          <li>扫描窗口：<code>{recent_hours}h</code></li>
          <li>交易新鲜度：<code>&lt;= {freshness_minutes:.0f}m</code></li>
          <li>超龄信号：显式记为 <code>signal_too_old</code></li>
        </ul>
      </div>
      <div class='callout warn'>
        <h3>当前最容易被误解的地方</h3>
        <p><code>execution.entry</code> 这块配置还留着旧 phase/辅助语义，容易让人误以为 live 还在用 post-only maker-first 入口。<strong>当前真正 controlling live 入场行为的是 <code>phase6.entry</code></strong>。</p>
      </div>
    </div>

    <h2 class='section-title'>最近一次 run 回放</h2>
    <div class='table-card'>
      <p>这不是历史大盘，而是 <strong>最近一轮 phase6</strong> 自己留下的事件时间线。以后你想知道“这轮到底做了什么”，先看这里，不用先翻日志。</p>
      <p class='small'>本次 run：{escape(fmt_ts(summary.get('run_started_at')))} → {escape(fmt_ts(summary.get('run_finished_at')))}</p>
      {replay_html}
    </div>

    <h2 class='section-title'>“信号是否延迟”到底怎么判定？</h2>
    <div class='card'>
      <p>你之前最痛的 bug 就卡在这里，所以这块我单独拆清楚：</p>
      <ul>
        <li><strong>第一层：</strong>adapter 只负责“把最近 {recent_hours}h 候选捞出来”</li>
        <li><strong>第二层：</strong>phase6 再计算 <code>signal_age_seconds = now - signal.timestamp</code></li>
        <li><strong>第三层：</strong>若 <code>signal_age_seconds &gt; {int(freshness_minutes * 60)}</code>，则拒绝交易，并记录成 <code>signal_too_old</code></li>
        <li><strong>第四层：</strong>即使信号足够新，也还要通过 same-bar 去重、同窗最强选择、风控、并发限制</li>
      </ul>
      <p class='small'>所以“最近 {recent_hours}h 扫描”本身不等于“最近 {recent_hours}h 都能下单”。真正能下单的是：最近 {freshness_minutes:.0f} 分钟内、未 seen、未 same-bar consumed、且风控放行的信号。</p>
    </div>

    <h2 class='section-title'>下单路径：当前 live 与可选路径</h2>
    <div class='cols'>
      <div class='card'>
        <h3>当前 live 路径（默认）</h3>
        <ul>
          <li>入场：<code>MARKET</code></li>
          <li>挂止损：<code>STOP_MARKET</code></li>
          <li>挂止盈：<code>LIMIT</code></li>
          <li>超时退出：<code>MARKET</code></li>
          <li>优点：admission/fill 更确定，适合 canary 小仓位</li>
          <li>代价：成本通常高于纯 maker-first</li>
        </ul>
      </div>
      <div class='card'>
        <h3>备用路径（若切回 maker-first）</h3>
        <ul>
          <li>入场：<code>limit_gtx</code></li>
          <li>等待：最多 <code>{int(entry.get('ttl_minutes', 15) or 15)}m</code></li>
          <li>若没成交：视配置决定是否 fallback 到 <code>MARKET</code></li>
          <li>适合：更想压手续费 / 滑点时</li>
          <li>风险：挂单未成、TTL、fallback 链路更复杂</li>
        </ul>
      </div>
    </div>

    <h2 class='section-title'>真实配置（Source of Truth）</h2>
    <div class='table-card'>
      {table(['配置项', '当前值'], [[escape(a), escape(b)] for a, b in config_rows])}
    </div>

    <h2 class='section-title'>最容易出 bug / 误判的地方</h2>
    <div class='table-card'>
      {table(['风险点', '为什么容易出问题', '你该先看什么'], [[escape(a), escape(b), escape(c)] for a, b, c in bug_rows])}
    </div>

    <h2 class='section-title'>排障时该看哪些文件</h2>
    <div class='table-card'>
      {table(['文件', '它回答什么问题'], [[f"<code>{escape(a)}</code>", escape(b)] for a, b in debug_rows])}
    </div>

    <h2 class='section-title'>源码地图：这页内容对应哪里</h2>
    <div class='table-card'>
      {table(['逻辑块', '源码位置', '说明'], src_rows)}
    </div>

    <div class='card'>
      <h2>这页适合怎么用？</h2>
      <ul>
        <li>改策略前：先来这里确认自己改的是哪一层（信号 / 新鲜度 / 风控 / 选币 / 下单 / exit）</li>
        <li>看 Dashboard 时：若发现“没下单”或“行为不符合直觉”，先对照这页再去看 rejections / warnings</li>
        <li>发现 bug 时：把问题映射到具体步骤，再去对应 source file 和 artifact 文件查</li>
      </ul>
      <p class='small'>目标不是把页面做得花，而是把“策略现在到底怎么工作”说人话、说透明、说能排障。</p>
    </div>
  </div>
</body>
</html>
"""
    OUT_PATH.write_text(html, encoding="utf-8")
    print({"out": str(OUT_PATH), "generated_at": generated_at_iso})


if __name__ == "__main__":
    main()
