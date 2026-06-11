#!/usr/bin/env python3
"""Reflection page for Step 1 next-steps design."""
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

OUT = ROOT / "reports" / "site" / "paper" / "binance_daily_event_study_reflection.html"

TITLE = "Step 1 之后怎么做：从单日事件升级到状态事件研究"
SUBTITLE = "基于你提的三个问题：放宽 universe、研究事件后形态、定义连续事件"


def p(text: str) -> str:
    return f"<p>{text}</p>"


def ul(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"


def build_body() -> str:
    cards = [
        {"label": "我对你观点的判断", "value": "方向正确", "subtitle": "应该放一点 universe，但不能回到今天名单倒看历史", "kind": "good"},
        {"label": "最重要的升级点", "value": "状态事件", "subtitle": "不是“今天上榜”，而是“首次上榜 / 第N天仍在榜”", "kind": "warn"},
        {"label": "下一个研究重点", "value": "事件后形态", "subtitle": "动量、反转、减速、成交额、MA 回归，都比单看 5 天收益更有信息量", "kind": "warn"},
        {"label": "连续2天进榜怎么算", "value": "分层统计", "subtitle": "同时保留“仅首次进入”和“streak 第N天”两种口径"},
    ]

    body = render_metric_cards(cards)

    body += render_section("0. 先直接回答你的问题", ul([
        "<b>是否可以把 universe 放宽一点？</b><br>可以。我同意你对“前 30 天成交量低、突然爆发”的判断。下一步应该加入 <code>当日 quote volume Top200</code> 这类补充通道，而不是只靠 30 日活跃度。",
        "<b>是否应该只看涨跌？</b><br>不应该。下一步重点应该从“5 天后涨还是跌”升级为“事件后更像动量、反转、失速、还是震荡”。",
        "<b>连续涨两天算几个事件？</b><br>现在 v0 会被记成 2 个事件。这不够好。下一步应该改成：第一次进榜算一个事件，第 N 天仍留在榜算另一个状态维度，不要混在一起。",
    ]))

    body += render_section("1. 为什么我认为你的直觉是对的", ul([
        "你担心 30 日成交额 Top100 会漏掉突发妖币，这个担心非常合理。很多真正有意思的币，前一阶段往往不显眼，筹码可能还在积累。",
        "但如果我们直接改成“今天成交额高就算”，又可能回到“拿今天信息污染历史”的旧坑。所以不能一刀切，而是要分层。",
        "你说“事件后 K 线可能呈现某种特殊形态”，这其实比单纯收益更重要。因为同一个涨跌榜事件，内部可能完全不同：有些是第一天爆发，有些已经是第三天连续拉盘。",
    ]))

    body += render_section("2. Universe 的下一步建议：双轨制", p("我建议下一步保留两个入口：") + ul([
        "<b>主力 universe：</b>30d trailing quote volume TopN。它稳定，因果性强，不容易引入未来函数。",
        "<b>补充 universe：</b>当日 quote volume TopM。用来把“长期安静、当天突然放量”的币捡回来。",
        "为防止噪声，补充 universe 至少还要满足：<code>listing_days >= 14 或 30</code>，数据完整，不能是极端碎片币。",
    ]) + render_note("关键不是把 universe 拉得无限宽，而是让“当日开始爆发”的币有机会进入研究。", kind="warn"))

    body += render_section("3. 为什么要把“单日事件”改成“状态事件”？", p("你问的“连续涨两天算几个事件”本质上就说明了一个问题：单日事件太粗，不能区分事件阶段。") + p("我建议下一步至少区分这几种：") + ul([
        "<b>首次进入 top gainer / top loser</b>：过去 N 天不在榜，今天第一次进。它通常比“今天还在榜上”更有信息量。",
        "<b>连续进榜第 N 天</b>：比如 streak=1、2、3、4+。这样能看：第 1 天和第 3 天是不是完全不同。",
        "<b>首次 funding extreme</b>：今天第一次从正常 funding 变成异常高/低。",
        "<b>组合状态：</b>比如“涨幅榜第 2 天 + 高正 funding”，而不是简单标签叠加。",
    ]) + render_note("这一步升级后，我们才能区分“新鲜事件”和“持续状态”。", kind="good"))

    body += render_section("4. 下一个研究重点：事件后形态", p("你提的这一点我认为是这次最有价值的转折。") + p("我们下一步不要只问“5 天后涨不涨”，而要问：事件后 K 线更像哪一类？") + ul([
        "<b>短期动量：</b>事件后第 1 天是否继续同向？",
        "<b>短期反转：</b>第 2-3 天是否开始回落或反弹？",
        "<b>加速/减速：</b>后续是否还能创新高，但斜率下降、力度变弱？",
        "<b>成交额形态：</b>放量继续冲 vs 放量后缩量。",
        "<b>均值回归：</b>是否回到 5MA / 10MA / 20MA。",
        "<b>尾部风险：</b>是不是少量爆亏样本把均值拖下去了。",
    ]) + render_note("如果能回答“某类事件后更适合短动量、某类更适合短反转”，那才有机会变成策略结构。", kind="warn"))

    body += render_section("5. 我建议下一步具体做什么", p("我建议下一步做成 <b>Step 1.1：状态化事件研究 v1</b>，优先做以下四件事：") + render_table(pd.DataFrame([
        {"任务": "放宽 universe", "做法": "30d Top100 + 当日 quote volume Top200 双轨", "价值": "捞到更多突发新晋币"},
        {"任务": "状态化事件定义", "做法": "首次进入榜单、streak 第 N 天、首次 funding extreme", "价值": "区分新事件和持续状态"},
        {"任务": "研究事件后形态", "做法": "看 1d/3d 延续率、新高率、成交额变化、MA 回归、MAE/MFE", "价值": "判断事件后适合动量还是反转"},
        {"任务": "分层比较", "做法": "30d 活跃 vs 当日新晋；首次上榜 vs 第N天；高 funding vs 低 funding", "价值": "找到哪类状态最值得继续深挖"},
    ])))

    body += render_section("6. “连续涨两天”该怎么记录？", p("我建议不要简单回答“算 1 个还是 2 个”，而是同时保留两个口径：") + ul([
        "<b>去重口径</b>：只取状态首次出现，用于研究“信号首次触发”。",
        "<b>滚动口径</b>：保留 streak_day=1/2/3/4+，用于研究“已经在状态中的第 N 天还有没有 edge”。",
        "在 summary 里同时输出：全部样本、仅首次出现、streak=2、streak>=3。这样最诚实，也最不容易误导。",
    ]))

    body += render_section("7. 我对这三条方向的优先级排序", ul([
        "<b>第一优先：</b>状态事件定义。如果不把“第1天”和“第N天”拆开，后面所有结论都会混在一起。",
        "<b>第二优先：</b>事件后形态研究。这一步最可能把“看起来有/其实薄”的东西，变成“知道该怎么做”的结构。",
        "<b>第三优先：</b>放宽 universe。很重要，但可以和状态事件一起做，不是单独替代 v0。",
    ]))

    body += render_section("8. 我的结论", render_note("我完全支持你的方向：不要只看涨跌，不要被 30 日成交额卡死，要把事件从‘单日标签’升级成‘状态+形态’。", kind="good") + p("如果 Step 1.1 做完后，我们能回答下面这些问题，就说明研究方向成熟了：") + ul([
        "哪些币是当日新晋爆发？哪些是已经连续活跃？",
        "首次进入榜单 和 连续留在榜单，哪个更值得研究？",
        "事件后 1-3 天更像动量，还是更像失速？",
        "成交额是继续放大，还是开始萎缩？",
        "哪类事件形态稳定，哪类只是尾部噪声撑起来？",
    ]) + render_note("我建议先不要做 live，也不要做大规模 IC 挖掘。先把这次提出的问题吃透，再决定往哪种策略结构走。", kind="warn"))

    return body


def main() -> None:
    body = build_body()
    extra_css = PAGE_CSS_DARK + """
    .hero { background: radial-gradient(circle at top right, #7c3aed33, transparent 40%), linear-gradient(135deg, #0f172a 0%, #111827 100%); }
    """
    html = render_page(
        TITLE,
        body,
        subtitle=SUBTITLE,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        css=extra_css,
    )
    write_page(OUT, html)
    print(f"[ok] wrote {OUT}")


if __name__ == "__main__":
    main()
