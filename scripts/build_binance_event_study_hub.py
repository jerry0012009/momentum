#!/usr/bin/env python3
"""Build unified hub page for Binance event-study research."""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from momentum.html_render import (  # noqa: E402
    PAGE_CSS_DARK,
    render_metric_cards,
    render_note,
    render_page,
    render_section,
    render_table,
    write_page,
)

OUT = ROOT / "reports" / "site" / "paper" / "binance_event_study_hub.html"


def p(text: str) -> str:
    return f"<p>{text}</p>"


def ul(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"


def linked_page_table(rows: list[dict[str, str]]) -> str:
    out = "<table><thead><tr><th>优先级</th><th>页面</th><th>链接</th><th>说明</th></tr></thead><tbody>"
    for row in rows:
        out += (
            "<tr>"
            f"<td>{row['priority']}</td>"
            f"<td>{row['page']}</td>"
            f"<td><a href=\"{row['href']}\">{row['href']}</a></td>"
            f"<td>{row['note']}</td>"
            "</tr>"
        )
    return out + "</tbody></table>"


def main() -> None:
    cards = [
        {"label": "当前执行入口", "value": "Phase2 SL-only", "subtitle": "paper/live forward 只认 SL-only", "kind": "good"},
        {"label": "研究归档入口", "value": "Rank 450 总览", "subtitle": "三条 Phase 2 策略方向已整理"},
        {"label": "Phase 2a", "value": "二次点火追多", "subtitle": "Momentum Ignition / 旧 trail 已弃用"},
        {"label": "Phase 2b", "value": "冲高回落做空", "subtitle": "Short Reversal / 买盘衰竭回吐"},
        {"label": "Phase 2c", "value": "负费率延续做多", "subtitle": "Funding Squeeze Carry"},
    ]

    body = render_metric_cards(cards)

    body += render_section("0. 为什么做一个统一入口页？", render_note("网页太多会让人搞不清主线。当前交易执行入口已升级为 Phase2 策略总入口；Rank 450 只作为研究归档和命名目录。", kind="warn") + ul([
        "做当前 paper/live 审计时，先看 Phase2 策略总入口和 Phase2a SL-only 页面。",
        "追溯研究来源时，再看 Rank 450 总览，并按 Phase 2a/2b/2c 进入具体研究报告。",
        "旧 trailing-stop 页面留作历史证据，但不再作为执行依据。",
    ]))

    body += render_section("1. 主线页面", linked_page_table([
        {"priority": "当前执行", "page": "Phase2 策略总入口", "href": "../factors/phase2_strategy_portal/report.html", "note": "当前/归档/弃用边界，以及 Phase2a SL-only paper/live 流程"},
        {"priority": "当前执行", "page": "Phase2a SL-only paper/live 审计页", "href": "../factors/paper_phase2a_event_v4_sl_only/report.html", "note": "当前唯一执行页；8% SL + 96h timeout；paper/live 状态和订单审计"},
        {"priority": "研究归档", "page": "Rank 450 策略方向总览", "href": "rank450/index.html", "note": "三条 Phase 2 策略方向、命名、路径、互跳关系"},
        {"priority": "Phase 2a", "page": "二次点火追多 / Momentum Ignition", "href": "rank450/phase2a_momentum_ignition.html", "note": "旧 V4/trailing 研究证据；当前执行已迁移到 SL-only"},
        {"priority": "Phase 2b", "page": "冲高回落做空 / Short Reversal", "href": "rank450/phase2b_short_reversal.html", "note": "放量冲高后回落，测试买盘衰竭后的短线做空"},
        {"priority": "Phase 2c", "page": "负费率延续做多 / Funding Squeeze Carry", "href": "rank450/phase2c_funding_squeeze_carry.html", "note": "极端负 funding + continuation 的拥挤空头挤压方向"},
        {"priority": "背景", "page": "Step 1.4 讲明白：日频口径、funding-adjusted 收益、结构分类结果", "href": "binance_daily_event_study_v1_4_taxonomy_report.html", "note": "理解日线分类与 funding-adjusted 收益"},
        {"priority": "背景", "page": "先把'失速窗口'讲清楚：定义、指标和证据", "href": "binance_stall_definition_and_evidence.html", "note": "理解早期事件研究里的失速窗口概念"},
        {"priority": "背景", "page": "Step 1 事件研究", "href": "binance_daily_event_study_v0.html", "note": "最早期事件研究，可作为背景参考"},
    ]))

    body += render_section("2. 推荐阅读顺序", ul([
        "<b>第一：</b>先看 Phase2 策略总入口，确认当前执行、历史归档、弃用页面的边界。",
        "<b>第二：</b>看 Phase2a SL-only 审计页，确认 paper/live 实际如何跑。",
        "<b>第三：</b>再看 Rank 450 总览，确认三条策略方向的命名和路径。",
        "<b>第四：</b>看 Phase 2a、Phase 2b、Phase 2c，对比三条研究方向。",
        "<b>最后：</b>再回看 Step 1.x 页面作为研究背景。",
    ]))

    body += render_section("3. 当前研究阶段判断", render_note("当前 live/paper 策略包只包含 Phase2a SL-only。Rank 450 目录是研究归档，不等于当前执行包。", kind="warn") + ul([
        "Phase 2a：旧 trailing-stop 执行已弃用；当前执行为 SL-only，固定 8% SL + 96h timeout。",
        "Phase 2b：短反转方向为 WATCH，必须做 walk-forward 和真实成交回放。",
        "Phase 2c：样本内很强，但需要 OOS / walk-forward 证明不是结构确认后的选择偏差。",
        "旧口径里的“Phase 2b 去事件化测试”不再作为策略方向命名，而归入 Phase 2a 的反偏差验证模块。",
    ]))

    body += render_section("4. 产物索引", render_table(pd.DataFrame([
        {"文件": "jerry/wlfi/FR_Monitor/docs/STEP1_BINANCE_DAILY_EVENT_STUDY_PLAN.md", "用途": "Step 1 设计"},
        {"文件": "jerry/wlfi/FR_Monitor/docs/STEP1_REVIEW_AND_NEXT_STEPS.md", "用途": "Step 1 复盘后的方向"},
        {"文件": "jerry/wlfi/FR_Monitor/docs/STEP1_1_MINIMAL_SCOPE.md", "用途": "Step 1.1 范围设计"},
        {"文件": "reports/site/paper/rank450/index.html", "用途": "Rank 450 策略方向总览"},
        {"文件": "reports/site/paper/rank450/phase2a_momentum_ignition.html", "用途": "Phase 2a 二次点火追多"},
        {"文件": "reports/site/paper/rank450/phase2b_short_reversal.html", "用途": "Phase 2b 冲高回落做空"},
        {"文件": "reports/site/paper/rank450/phase2c_funding_squeeze_carry.html", "用途": "Phase 2c 负费率延续做多"},
        {"文件": "reports/site/factors/phase2_strategy_portal/report.html", "用途": "Phase2 当前执行/归档/弃用总入口"},
        {"文件": "reports/site/factors/paper_phase2a_event_v4_sl_only/report.html", "用途": "当前 Phase2a SL-only paper/live 审计页"},
    ])) + p("页面生成时间：" + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")))

    extra_css = PAGE_CSS_DARK + """
    .hero { background: linear-gradient(135deg, #111827 0%, #0f172a 100%); }
    """
    html = render_page(
        "Binance 事件研究统一入口：Phase2 / Rank 450 路由",
        body,
        subtitle="当前执行入口是 Phase2 SL-only；Rank 450 是 Phase 2a/2b/2c 研究归档",
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        css=extra_css,
    )
    write_page(OUT, html)
    print(f"[ok] wrote {OUT}")


if __name__ == "__main__":
    main()
