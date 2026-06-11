#!/usr/bin/env python3
"""Build Step 1.1 teaching page with streak comparison."""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from momentum.html_render import (  # noqa: E402
    PAGE_CSS_DARK,
    fmt_int,
    fmt_pct,
    render_metric_cards,
    render_note,
    render_page,
    render_section,
    render_table,
    write_page,
)

ART = ROOT / "reports" / "artifacts" / "binance_daily_event_study_v1"
OUT = ROOT / "reports" / "site" / "paper" / "binance_daily_event_study_v1.html"


def build_body() -> str:
    streak = pd.read_csv(ART / "streak_summary_v1.csv")
    type_sum = pd.read_csv(ART / "type_summary_v1.csv")
    events = pd.read_csv(ART / "events_v1.csv")
    manifest = {}

    cards = [
        {"label": "这版结论", "value": "有差异", "subtitle": "新晋事件 和 连续留榜事件 不像同一类", "kind": "warn"},
        {"label": "样本规模", "value": f"{len(events):,}", "subtitle": f"{events['event_date'].min()} → {events['event_date'].max()}"},
        {"label": "关键比较", "value": "new vs streak2/streak3+", "subtitle": "我们这次故意只做最小可控范围"},
        {"label": "最扎眼发现", "value": "streak3+ MAE 更大", "subtitle": "连续留榜事件的风险更高，不能简单当成 continuation"},
    ]
    body = render_metric_cards(cards)

    body += render_section("0. 这一版到底在做什么？", render_note("Step 1.1 的目标不是把所有事情都做完，而是只回答一个很小但关键的问题：新晋进榜 和 持续留榜 是不是同一类事件？", kind="warn") + ul([
        "Universe：当日 eligible 且 listing_days ≥ 30 的币，按当天 quote volume 取 Top150。",
        "事件：每天只看 top gainer Top15 和 top loser Top15。",
        "状态拆分：<code>new</code> / <code>streak2</code> / <code>streak3_plus</code>。",
        "这样可以控制样本量，先把逻辑验证清楚，再考虑放量。",
    ]))

    body += render_section("1. 为什么这一步很重要？", ul([
        "如果不把“第 1 天上榜”和“第 N 天仍留榜”拆开，后面所有结论都会混在一起。",
        "你之前提的“连续涨两天算几个事件”正好就是这个问题。这版我们直接把它拆开了。",
        "如果两个状态差异明显，后面才值得继续做“状态化 radar”。如果差异不大，就不值得继续在这条线上复杂化。",
    ]))

    body += render_section("2. 单类型总览", render_table(
        type_sum[["event_type", "events", "symbols", "ret_1d_mean", "ret_3d_mean", "ret_5d_mean", "ret_10d_mean", "long_total_5d_mean", "short_total_5d_mean", "mae_long_5d_median"]],
        col_formats={"events": fmt_int, "symbols": fmt_int, "ret_1d_mean": fmt_pct, "ret_3d_mean": fmt_pct, "ret_5d_mean": fmt_pct, "ret_10d_mean": fmt_pct, "long_total_5d_mean": fmt_pct, "short_total_5d_mean": fmt_pct, "mae_long_5d_median": fmt_pct},
        col_positive_good=["ret_1d_mean", "ret_3d_mean", "ret_5d_mean", "ret_10d_mean", "long_total_5d_mean", "short_total_5d_mean"],
        col_labels={"event_type": "事件类型", "events": "样本数", "symbols": "币数", "ret_1d_mean": "1天后价格", "ret_3d_mean": "3天后价格", "ret_5d_mean": "5天后价格", "ret_10d_mean": "10天后价格", "long_total_5d_mean": "5天多头含资金费", "short_total_5d_mean": "5天空头含资金费", "mae_long_5d_median": "5天多头MAE中位数"},
    ))

    body += render_section("3. 最关键的表：new / streak2 / streak3_plus", render_note("这里最值得你看的是：新晋事件是不是和持续留榜事件表现一致？如果一致，我们就不需要做 streak；如果不一致，后面才值得继续拆。", kind="good") + render_table(
        streak[["event_type", "streak_label", "events", "symbols", "ret_1d_mean", "ret_3d_mean", "ret_5d_mean", "ret_10d_mean", "long_total_5d_mean", "short_total_5d_mean", "mae_long_5d_median"]],
        col_formats={"events": fmt_int, "symbols": fmt_int, "ret_1d_mean": fmt_pct, "ret_3d_mean": fmt_pct, "ret_5d_mean": fmt_pct, "ret_10d_mean": fmt_pct, "long_total_5d_mean": fmt_pct, "short_total_5d_mean": fmt_pct, "mae_long_5d_median": fmt_pct},
        col_positive_good=["ret_1d_mean", "ret_3d_mean", "ret_5d_mean", "ret_10d_mean", "long_total_5d_mean", "short_total_5d_mean"],
        col_labels={"event_type": "事件类型", "streak_label": "状态", "events": "样本数", "symbols": "币数", "ret_1d_mean": "1天后价格", "ret_3d_mean": "3天后价格", "ret_5d_mean": "5天后价格", "ret_10d_mean": "10天后价格", "long_total_5d_mean": "5天多头含资金费", "short_total_5d_mean": "5天空头含资金费", "mae_long_5d_median": "5天多头MAE中位数"},
    ))

    body += render_section("4. 这版已经能看出什么？", ul([
        "<b>结论 A：新晋事件 和 连续留榜事件 不完全像同一类。</b><br>它们的 5 天收益、MAE、资金费后收益都有差异，不能简单合并。",
        "<b>结论 B：streak3+ 通常 MAE 更大，风险更高。</b><br>也就是说，币已经在榜单上连续停留时，后续路径可能更不稳定，不适合直接套用“第一天”的结论。",
        "<b>结论 C：涨幅榜仍不是追涨信号。</b><br>不管哪种状态，top gainer 整体依然偏负或偏弱，没有看到稳定的 continuation。",
        "<b>结论 D：跌幅榜的 streak2 看起来相对有趣一点。</b><br>它 5 天后价格仍负，但不如 streak3_plus 那么差。这说明“第一次大跌”和“持续大跌”可能不是同一种机会。",
    ]))

    body += render_section("5. 这版研究的边界在哪？", render_note("这一步只是最小验证。它已经证明“状态拆分”值得继续，但它还没告诉我们具体该怎么做。", kind="warn") + ul([
        "这版没有做形态研究：没看缩量、放量、是否新高、是否失速。",
        "这版没有做当日 quote volume Top200 的扩展 universe。",
        "这版没有做首发/续发事件的成交额分层。",
        "这些都留给下一步，但前提是先确认“状态拆分”有意义——我认为现在已经确认了。",
    ]))

    body += render_section("6. 我建议下一步怎么做？", ul([
        "<b>第一优先：</b>继续在状态化框架下做，但先不做大而全。",
        "<b>第二优先：</b>加入一个非常轻的形态过滤：事件日是否放量、事件后 1 天是否继续创新高。",
        "<b>第三优先：</b>如果上面两个都成立，再考虑把 universe 放到当日 quote volume Top200。",
    ]) + render_note("我的判断：现在可以进入 Step 1.2，但仍然要保持小步推进，不要一次性扩成全市场多因子研究。", kind="good"))

    body += render_section("7. 当前产物索引", render_table(pd.DataFrame([
        {"文件": "events_v1.csv", "用途": "v1 事件样本，包含 streak_day / streak_label"},
        {"文件": "streak_summary_v1.csv", "用途": "按 event_type + streak_label 汇总"},
        {"文件": "type_summary_v1.csv", "用途": "按 event_type 汇总"},
        {"文件": "STEP1_1_MINIMAL_SCOPE.md", "用途": "Step 1.1 最小范围设计"},
        {"文件": "scripts/build_binance_daily_event_study_v1.py", "用途": "生成 v1 样本的脚本"},
    ])) + p("页面生成时间：" + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")))
    return body


def ul(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"


def p(text: str) -> str:
    return f"<p>{text}</p>"


def main() -> None:
    body = build_body()
    extra_css = PAGE_CSS_DARK + """
    .hero { background: radial-gradient(circle at top left, #0ea5e933, transparent 35%), linear-gradient(135deg, #0f172a 0%, #111827 100%); }
    """
    html = render_page(
        "Step 1.1：新晋事件 vs 连续留榜事件，先把这个吃透",
        body,
        subtitle="最小可控范围：当日 quote volume Top150 + 涨跌榜 Top15 + streak1/2/3+",
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        css=extra_css,
    )
    write_page(OUT, html)
    print(f"[ok] wrote {OUT}")


if __name__ == "__main__":
    main()
