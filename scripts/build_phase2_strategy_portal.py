#!/usr/bin/env python3
"""Build the current Phase2 strategy portal.

This page is the public routing layer for Phase2: it separates the active
SL-only forward runner from archived research and deprecated trailing-stop
variants.
"""
from __future__ import annotations

import csv
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "site" / "factors" / "phase2_strategy_portal" / "report.html"
STATUS_CSV = ROOT / "reports" / "artifacts" / "paper_phase2a_event_v4_sl_only" / "status.csv"
CONFIG_JSON = ROOT / "config" / "execution" / "phase2a_event_v4_trail_paper.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def esc(value: Any) -> str:
    return html.escape(str(value if value is not None else "-"))


def read_status() -> dict[str, str]:
    if not STATUS_CSV.exists():
        return {}
    with STATUS_CSV.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return rows[0] if rows else {}


def read_config() -> dict[str, Any]:
    if not CONFIG_JSON.exists():
        return {}
    return json.loads(CONFIG_JSON.read_text(encoding="utf-8"))


def bool_label(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    return "-"


def metric(label: str, value: Any, note: str = "", kind: str = "") -> str:
    cls = f"metric {kind}".strip()
    return (
        f'<div class="{cls}"><div class="label">{esc(label)}</div>'
        f'<div class="value">{esc(value)}</div>'
        f'<div class="note">{esc(note)}</div></div>'
    )


def row(cols: list[Any]) -> str:
    return "<tr>" + "".join(f"<td>{esc(c)}</td>" for c in cols) + "</tr>"


def link_row(kind: str, title: str, href: str, state: str, note: str) -> str:
    return (
        "<tr>"
        f"<td>{esc(kind)}</td>"
        f'<td><a href="{esc(href)}">{esc(title)}</a></td>'
        f"<td><code>{esc(href)}</code></td>"
        f"<td>{esc(state)}</td>"
        f"<td>{esc(note)}</td>"
        "</tr>"
    )


def build() -> str:
    status = read_status()
    cfg = read_config()
    live = cfg.get("live_trading") or {}

    live_armed = (
        live.get("enabled") is True
        and live.get("live_order_placement_enabled") is True
        and live.get("kill_switch") is False
        and live.get("dry_run_only") is False
    )
    live_state = "ARMED" if live_armed else "NOT ARMED"
    live_note = (
        "live canary 已开放：共享 paper 信号，入场后立即挂 STOP_MARKET，96h timeout 才市价平仓"
        if live_armed
        else "live canary 当前未完全开放；以配置里的 enabled/order_placement/kill_switch/dry_run 为准"
    )

    metrics = [
        metric("当前执行入口", "Phase2a SL-only", "唯一 current paper/live forward 入口", "good"),
        metric("Live canary", live_state, live_note, "good" if live_armed else "warn"),
        metric("Paper open", status.get("open_positions", "-"), "paper 当前持仓数"),
        metric("Live open", status.get("live_open_positions", "-"), "live 当前持仓数"),
        metric("Active events", status.get("active_events", "-"), "事件 watchlist 数"),
        metric("Last monitor", status.get("last_monitor_at_utc", "-"), "最近 monitor 写入 UTC"),
    ]

    live_rows = [
        row(["strategy_id", status.get("strategy_id", "-"), "状态表里的策略标识"]),
        row(["stage", status.get("stage", "-"), "forward runner 当前阶段"]),
        row(["runner_mode", status.get("runner_mode", "-"), "paper/shadow/live canary 组合模式"]),
        row(["updated_at_utc", status.get("updated_at_utc", "-"), "状态文件更新时间"]),
        row(["live_trading.enabled", bool_label(live.get("enabled")), "live canary 总开关"]),
        row(["live_order_placement_enabled", bool_label(live.get("live_order_placement_enabled")), "是否允许真实下单"]),
        row(["kill_switch", bool_label(live.get("kill_switch")), "必须为 false 才能开 live"]),
        row(["dry_run_only", bool_label(live.get("dry_run_only")), "必须为 false 才不是纯 dry-run"]),
        row(["live notional", live.get("notional_usdt", "-"), "单笔目标名义本金 USDT"]),
        row(["max_effective_notional", live.get("max_effective_notional_usdt", "-"), "数量取整后的硬上限 USDT"]),
    ]

    current_links = [
        link_row(
            "CURRENT",
            "Phase2a SL-only paper/live 审计页",
            "../paper_phase2a_event_v4_sl_only/report.html",
            "当前唯一执行入口",
            "展示 paper、live、信号、拒绝、持仓、订单和 SL-only 流程",
        ),
        link_row(
            "CURRENT-ROUTER",
            "Binance 事件研究统一入口",
            "../../paper/binance_event_study_hub.html",
            "研究路由",
            "用于追溯 Step 1.x 到 Rank450 的研究脉络",
        ),
        link_row(
            "CURRENT-AUDIT",
            "Phase2a 同小时V4 SL-only 回测审计",
            "../phase2a_same_hour_sl_only_audit/report.html",
            "时间口径审计",
            "回答 12:02 是否应允许直接用 11:00-12:00 完成K线交易；结论是不应放宽",
        ),
        link_row(
            "RESEARCH",
            "Rank 450 策略方向总览",
            "../../paper/rank450/index.html",
            "历史研究总览",
            "Phase2a/2b/2c 的规范命名和归档入口",
        ),
    ]

    archive_links = [
        link_row(
            "ARCHIVE",
            "Phase2a Momentum Ignition 研究页",
            "../../paper/rank450/phase2a_momentum_ignition.html",
            "归档研究，不是当前执行页",
            "保留 V4/trailing 研究证据；当前执行已迁移到 SL-only",
        ),
        link_row(
            "ARCHIVE",
            "Phase2b Short Reversal",
            "../../paper/rank450/phase2b_short_reversal.html",
            "WATCH only",
            "冲高回落做空方向，未进入 paper/live 执行",
        ),
        link_row(
            "ARCHIVE",
            "Phase2c Funding Squeeze Carry",
            "../../paper/rank450/phase2c_funding_squeeze_carry.html",
            "WATCH+ only",
            "样本内强但仍需 OOS/walk-forward，不是 live 策略",
        ),
        link_row(
            "DEPRECATED",
            "旧 Phase2a v1.6a 页面",
            "../../paper/binance_event_study_v1_6a_momentum_ignition_report.html",
            "旧链接已跳转",
            "保留兼容；不作为当前入口",
        ),
        link_row(
            "DEPRECATED",
            "旧 Phase2b 页面",
            "../../paper/binance_event_study_v1_6_2b_short_reversal.html",
            "旧链接已跳转",
            "保留兼容；不作为当前入口",
        ),
        link_row(
            "DEPRECATED",
            "旧 Phase2c 页面",
            "../../paper/binance_event_study_phase2c.html",
            "旧链接已跳转",
            "保留兼容；不作为当前入口",
        ),
    ]

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Phase2 策略总入口 · SL-only 当前执行与历史归档</title>
<style>
:root{{--bg:#0b1220;--panel:#111827;--panel2:#0f172a;--border:#273449;--text:#e5e7eb;--muted:#94a3b8;--blue:#60a5fa;--green:#34d399;--yellow:#fbbf24;--red:#f87171}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.65 -apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans SC',sans-serif}}
.wrap{{max-width:1240px;margin:0 auto;padding:28px 18px 72px}}
a{{color:#93c5fd;text-decoration:none}}a:hover{{text-decoration:underline}}
h1{{margin:0 0 10px;font-size:2rem;line-height:1.2;color:#f8fafc}}h2{{margin:26px 0 10px;font-size:1.25rem;color:#f8fafc}}h3{{margin:0 0 8px;font-size:1rem}}
p{{margin:8px 0}}.muted{{color:var(--muted)}}code{{background:#0b1324;border:1px solid #243047;border-radius:5px;padding:2px 6px;color:#dbeafe;font-size:.88em}}
.hero,.panel{{border:1px solid var(--border);background:var(--panel);border-radius:10px;padding:18px 20px;margin:0 0 16px}}
.hero{{background:#0f172a}}
.badge{{display:inline-block;border:1px solid #365171;background:#10243a;color:#bfdbfe;border-radius:999px;padding:3px 9px;font-size:12px;font-weight:700;margin:0 8px 8px 0}}
.badge.good{{border-color:#166534;background:#052e1b;color:#86efac}}.badge.warn{{border-color:#854d0e;background:#2a1905;color:#fde68a}}.badge.bad{{border-color:#7f1d1d;background:#2a0d0d;color:#fecaca}}
.metrics{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:16px 0}}
.metric{{border:1px solid var(--border);background:var(--panel2);border-radius:8px;padding:13px}}
.metric.good{{border-color:#14532d}}.metric.warn{{border-color:#854d0e}}
.metric .label{{color:var(--muted);font-size:12px}}.metric .value{{font-size:1.3rem;font-weight:750;margin:3px 0;color:#f8fafc}}.metric .note{{color:var(--muted);font-size:12px}}
.flow{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:14px 0}}
.step{{border:1px solid var(--border);background:var(--panel2);border-radius:8px;padding:13px;min-height:134px}}
.step strong{{display:block;color:#f8fafc;margin-bottom:5px}}.step .tag{{display:inline-block;color:#fbbf24;font-size:12px;font-weight:700;margin-bottom:6px}}
table{{width:100%;border-collapse:collapse;margin:10px 0 18px;border:1px solid var(--border);background:var(--panel2)}}
th,td{{border-bottom:1px solid var(--border);padding:9px 10px;text-align:left;vertical-align:top;font-size:.9rem}}th{{background:#101a2c;color:#cbd5e1;white-space:nowrap}}tr:last-child td{{border-bottom:0}}
.notice{{border-left:4px solid var(--yellow);background:rgba(251,191,36,.08);padding:12px 14px;border-radius:0 8px 8px 0;margin:12px 0}}
.notice.good{{border-left-color:var(--green);background:rgba(52,211,153,.08)}}.notice.bad{{border-left-color:var(--red);background:rgba(248,113,113,.08)}}
ul{{margin:8px 0 0 20px;padding:0}}li{{margin:5px 0}}
@media(max-width:900px){{.metrics,.flow{{grid-template-columns:1fr}}.wrap{{padding:20px 12px 48px}}table{{font-size:.82rem}}th,td{{padding:7px}}}}
</style>
</head>
<body>
<div class="wrap">
  <div class="hero">
    <span class="badge good">CURRENT: Phase2a SL-only</span>
    <span class="badge warn">ARCHIVE: Rank450 research</span>
    <span class="badge bad">DEPRECATED: trailing-stop execution</span>
    <h1>Phase2 策略总入口</h1>
    <p class="muted">这个页面负责把 Phase2 的当前执行、历史研究和弃用页面分开。当前策略流程只认 <b>Phase2a SL-only paper/live</b>；早期 V4/trailing 研究只保留为归档证据。</p>
    <p class="muted">页面生成时间：{utc_now()}</p>
  </div>

  <div class="metrics">{''.join(metrics)}</div>

  <div class="notice good">
    <b>当前口径：</b>Phase2a 已从移动止盈/trailing-stop 版本切换为 SL-only。Paper 与 live 共用事件检测和 V4 入场信号；退出只允许固定 8% SL 或 96h timeout。Phase2b/Phase2c 仍是研究/观察，不进入当前交易执行。
  </div>
  <div class="notice">
    <b>时间口径审计：</b>“12:02 直接用 11:00-12:00 完成K线作为同小时V4入场”已回测，交易数从 1,951 增至 2,703，但均值从 +1.77% 降到 +0.88%，PF 从 1.27 降到 1.13。新增 752 笔同小时交易均值 -6.06%、PF 0.18，因此当前策略不应放宽为同小时入场。
  </div>

  <h2>1. 当前业务流程</h2>
  <div class="flow">
    <div class="step"><span class="tag">Step 1</span><strong>事件扫描</strong><p>每小时后延迟扫描 Binance UM 24h ticker：rank≤20、24h 涨幅≥30%、quote volume≥5M、24h event cooldown。</p></div>
    <div class="step"><span class="tag">Step 2</span><strong>V4 入场确认</strong><p>只使用已完成 1h K 线：volume ratio≥3.0、1h return≥1%。信号小时之后，持仓语义从下一根小时 K 开始。</p></div>
    <div class="step"><span class="tag">Step 3</span><strong>Paper / Live 入场</strong><p>Paper 使用 bookTicker ask 记账；live canary 在相同信号后用真实 market entry，名义本金 25 USDT，取整后不超过 30 USDT。</p></div>
    <div class="step"><span class="tag">Step 4</span><strong>SL-only 退出</strong><p>Paper 按已完成 1h bar low≤entry*(1-8%) 或 96h timeout close；live 入场后立即挂 STOP_MARKET，96h timeout 才 market close。</p></div>
  </div>

  <h2>2. 当前入口和链接关系</h2>
  <table>
    <thead><tr><th>类型</th><th>页面</th><th>路径</th><th>状态</th><th>说明</th></tr></thead>
    <tbody>{''.join(current_links)}</tbody>
  </table>

  <h2>3. 历史页面和关闭口径</h2>
  <div class="notice">
    <b>关闭方式：</b>不删除历史页面；旧路径保留跳转或归档标记，首页只推荐本页和 SL-only 当前审计页。任何写着 trail / trailing stop / V4 trailing 的页面都不能作为当前 paper/live 执行依据。
  </div>
  <table>
    <thead><tr><th>类型</th><th>页面</th><th>路径</th><th>状态</th><th>说明</th></tr></thead>
    <tbody>{''.join(archive_links)}</tbody>
  </table>

  <h2>4. 当前 live / paper 状态快照</h2>
  <table>
    <thead><tr><th>字段</th><th>当前值</th><th>解释</th></tr></thead>
    <tbody>{''.join(live_rows)}</tbody>
  </table>

  <h2>5. 审计规则</h2>
  <div class="panel">
    <ul>
      <li><b>唯一 current execution source：</b><code>reports/site/factors/paper_phase2a_event_v4_sl_only/report.html</code> 和对应 artifact 目录。</li>
      <li><b>唯一 current config：</b><code>config/execution/phase2a_event_v4_trail_paper.json</code>，虽然文件名仍含 trail，但字段已切到 <code>stop_loss_pct=0.08</code> 与 <code>hard_timeout_hours=96</code>。</li>
      <li><b>不再使用：</b>任何 trailing take-profit、2% trailing、72h hard timeout 的旧执行口径。</li>
      <li><b>不可误读：</b>Rank450 是研究归档；Phase2b/Phase2c 没有 live/paper 权限。</li>
    </ul>
  </div>
</div>
</body>
</html>
"""


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build(), encoding="utf-8")
    print(f"[ok] wrote {OUT}")


if __name__ == "__main__":
    main()
