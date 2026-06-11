#!/usr/bin/env python3
"""Build Step 1.4 teaching page with daily-frequency confirmation and funding-adjusted view."""
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

TAX = ROOT / "reports" / "artifacts" / "binance_daily_event_study_v1_4" / "taxonomy_summary_v1_4.csv"
OUT = ROOT / "reports" / "site" / "paper" / "binance_daily_event_study_v1_4_taxonomy_report.html"


def p(text: str) -> str:
    return f"<p>{text}</p>"


def ul(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"


def main() -> None:
    t = pd.read_csv(TAX)

    highlight_buckets = [
        "G_all_stall",
        "G_all_other",
        "G_neg_extreme_stall",
        "G_neg_extreme",
        "G_neg_stall",
        "G_neg_other",
        "G_pos_extreme_stall",
        "G_squeeze_candidate",
        "L_neg_extreme",
        "L_neg_stall",
        "L_neg_other",
    ]

    compare = t[t.bucket.isin(highlight_buckets)].copy()
    top_gainer = t[t.bucket.str.startswith("G_") & (t.n >= 50)].sort_values("fwd_ret_5d_mean", ascending=False).head(10).copy()
    top_total = t[t.bucket.str.startswith("G_") & (t.n >= 50)].sort_values("long_total_ret_5d_mean", ascending=False).head(10).copy()

    cards = [
        {"label": "确认第 1 点", "value": "是，这次 1.4 是日频数据", "subtitle": "基于日线收盘 K 线 + 当日 funding 结算汇总，不是小时线", "kind": "good"},
        {"label": "确认第 2 点", "value": "收益要看 price + funding", "subtitle": "所以我们同时看 long_total_ret_5d / short_total_ret_5d"},
        {"label": "关键结论", "value": "funding 负不等于逼空", "subtitle": "要和价格结构一起看"},
        {"label": "最扎眼桶", "value": "G_neg_extreme_stall", "subtitle": "样本很小，但必须先讲清楚"},
    ]

    body = render_metric_cards(cards)

    body += render_section("0. 先回答你最关心的两个问题", render_note("这两个问题都很关键，先把口径讲明白，再看结论。", kind="warn") + ul([
        "<b>第一：</b>是的，这次 1.4 是在 <code>日频</code> 数据上做的：日线收盘价、日线成交额、当日 funding 结算汇总。",
        "<b>第二：</b>你提的对，单看价格涨跌不够。真实 PnL 是价格变化 + funding 收付的结果。所以我这次特别把 <code>long_total_ret_5d</code> 和 <code>short_total_ret_5d</code> 一起放上来。",
        "这里 <code>long_total_ret_5d</code> 可以理解为：假设做多 5 天，价格收益再扣/加这段时间资金费后的结果；<code>short_total_ret_5d</code> 则是做空 5 天的同类口径。",
        "所以这张页不是只看‘涨了吗’，而是看‘涨跌 + 资金费’一起算出来的结果。",
        "这里的 <code>long_total_ret_5d</code> 是做多 5 天后的资金费后收益，<code>short_total_ret_5d</code> 是做空 5 天后的资金费后收益。"
    ]))

    body += render_section("1. 为什么这一步要单独做 funding-adjusted 报告？", ul([
        "因为很多暴涨币的收益结构，不是纯靠价格涨跌解释的。",
        "尤其你说的那类情况：负 funding 很大、借币成本高、空头承压。这种时候，资金费会明显改变多空双方的真实损益。",
        "所以我们不能只看 5 天价格收益，要看 5 天总收益，否则会误判。",
    ]))

    body += render_section("2. 1.4 的研究对象是什么？", ul([
        "只研究 <code>new</code> 事件：第一次进入涨跌榜的样本。",
        "主要看 <code>top_gainer_1d</code>，同时保留 <code>top_loser_1d</code> 作为对照。",
        "把事件按 funding 结构、价格结构、成交额结构、是否集群事件等分成不同桶。",
        "然后比较每个桶的后续收益和资金费后收益。",
    ]))

    body += render_section("2.5 我是怎么分桶的？小白版字典", render_note("下面这张表不是结果，而是‘分类规则’。你先看懂规则，再回去看后面的结果表。", kind="good") + render_table(pd.DataFrame([
        {"桶名": "G_neg_extreme", "维度": "funding 极端性", "通俗解释": "涨幅榜事件当天，资金费率很低/很负，属于最极端的 5%。"},
        {"桶名": "G_pos_extreme", "维度": "funding 极端性", "通俗解释": "涨幅榜事件当天，资金费率很高/很正，属于最极端的 5%。"},
        {"桶名": "G_neg_moderate", "维度": "funding 分布", "通俗解释": "涨幅榜事件当天，资金费偏负，但没到最极端。"},
        {"桶名": "stall", "维度": "价格结构", "通俗解释": "事件后出现‘涨不动’的证据，比如 T+2 回落、成交额萎缩、动能不足。"},
        {"桶名": "other", "维度": "价格结构", "通俗解释": "没有进入 stall 定义的其他样本。"},
        {"桶名": "neg_stall", "维度": "funding + 结构", "通俗解释": "负 funding 涨幅榜样本里，出现了失速结构。"},
        {"桶名": "neg_other", "维度": "funding + 结构", "通俗解释": "负 funding 涨幅榜样本里，没有出现失速结构。"},
        {"桶名": "squeeze_candidate", "维度": "逼空候选", "通俗解释": "极端负 funding + 成交量突然放大，看起来像空头被迫回补。"},
        {"桶名": "in_cluster", "维度": "事件聚集", "通俗解释": "不是孤立事件，而是同一币在短期内反复出现新晋事件。"},
        {"桶名": "isolated", "维度": "事件聚集", "通俗解释": "只有这一次事件，短期没有反复出现。"},
        {"桶名": "after_runup", "维度": "前期走势", "通俗解释": "事件前已经连涨一段时间。"},
        {"桶名": "after_drawdown", "维度": "前期走势", "通俗解释": "事件前刚经历明显下跌。"},
    ]), col_labels={"桶名": "桶名", "维度": "维度", "通俗解释": "通俗解释"}) + ul([
        "<b>G/L</b>：Gainer 是涨幅榜，Loser 是跌幅榜。",
        "<b>extreme/moderate/zero</b>：用来描述 funding 是极端、中等、还是接近 0。",
        "<b>stall/other</b>：用来描述事件后价格是‘涨不动了’，还是‘没看出明显失速’。",
        "<b>in_cluster/isolated</b>：用来描述这个事件是一个单独事件，还是连续事件的一部分。",
        "所以你看到的 <code>G_neg_extreme_stall</code>，可以读成：**涨幅榜 + 极端负 funding + 失速结构**。",
    ]))

    body += render_section("3. 桶名怎么看？", ul([
        "<b>G/L</b>：G 是涨幅榜，L 是跌幅榜。",
        "<b>neg/pos/extreme/moderate/zero</b>：描述 funding 是很负、偏负、很正、偏正，还是接近 0。",
        "<b>stall/other</b>：描述事件后是出现失速证据，还是没出现。",
        "<b>squeeze_candidate</b>：极端负 funding + 放量冲击。",
        "<b>in_cluster/isolated</b>：短期反复出现 vs 只出现一次。",
        "比如你看到的 <code>G_neg_extreme_stall</code>，就是：<b>涨幅榜 + 极端负 funding + 失速结构</b>。",
    ]))

    body += render_section("4. 最关键的对比：价格收益 vs 资金费后收益", render_table(
        compare[["bucket", "n", "fwd_ret_5d_mean", "win_rate_5d", "long_total_ret_5d_mean", "short_total_ret_5d_mean", "funding_rate_last_mean"]],
        col_formats={"n": fmt_int, "fwd_ret_5d_mean": fmt_pct, "win_rate_5d": fmt_pct, "long_total_ret_5d_mean": fmt_pct, "short_total_ret_5d_mean": fmt_pct, "funding_rate_last_mean": fmt_pct},
        col_positive_good=["fwd_ret_5d_mean", "win_rate_5d", "long_total_ret_5d_mean", "short_total_ret_5d_mean"],
        col_labels={"bucket": "桶", "n": "样本数", "fwd_ret_5d_mean": "5天价格收益", "win_rate_5d": "5天价格胜率", "long_total_ret_5d_mean": "5天做多含资金费", "short_total_ret_5d_mean": "5天做空含资金费", "funding_rate_last_mean": "事件日 funding 均值"},
    ) + render_note("这一步的目的就是你说的那个：把价格收益和资金费放在一起看，而不是分开看。", kind="good"))

    body += render_section("5. 这张表里最值得注意的点", ul([
        "<b>G_neg_extreme</b> 的 5 天价格收益是负的，但 <code>long_total_ret_5d</code> 变成了正。说明负 funding 会明显改变多头真实损益。",
        "<b>G_neg_extreme_stall</b> 的价格收益和资金费后收益都更强，但样本只有 101，不能直接当结论。",
        "<b>G_squeeze_candidate</b> 虽然听起来像逼空，但价格收益和资金费后收益都不强，说明‘负 funding + 放量’不等于稳定 continuation。",
        "所以不能简单说‘负 funding 就是逼空’，而要说：**负 funding + 某种价格结构，才会变成不同结果**。",
    ]))

    body += render_section("6. 如果只看日线价格收益，哪些桶更强？", render_table(
        top_gainer[["bucket", "n", "fwd_ret_5d_mean", "win_rate_5d", "long_total_ret_5d_mean", "short_total_ret_5d_mean", "funding_rate_last_mean"]],
        col_formats={"n": fmt_int, "fwd_ret_5d_mean": fmt_pct, "win_rate_5d": fmt_pct, "long_total_ret_5d_mean": fmt_pct, "short_total_ret_5d_mean": fmt_pct, "funding_rate_last_mean": fmt_pct},
        col_positive_good=["fwd_ret_5d_mean", "win_rate_5d", "long_total_ret_5d_mean", "short_total_ret_5d_mean"],
        col_labels={"bucket": "桶", "n": "样本数", "fwd_ret_5d_mean": "5天价格收益", "win_rate_5d": "5天价格胜率", "long_total_ret_5d_mean": "5天做多含资金费", "short_total_ret_5d_mean": "5天做空含资金费", "funding_rate_last_mean": "事件日 funding 均值"},
    ) + render_note("这一步还是日线结果，不能直接当成策略。但它能看出哪类结构比哪类结构更值得继续深挖。", kind="warn"))

    body += render_section("7. 如果看资金费后收益，排序会不会变？", render_table(
        top_total[["bucket", "n", "fwd_ret_5d_mean", "win_rate_5d", "long_total_ret_5d_mean", "short_total_ret_5d_mean", "funding_rate_last_mean"]],
        col_formats={"n": fmt_int, "fwd_ret_5d_mean": fmt_pct, "win_rate_5d": fmt_pct, "long_total_ret_5d_mean": fmt_pct, "short_total_ret_5d_mean": fmt_pct, "funding_rate_last_mean": fmt_pct},
        col_positive_good=["fwd_ret_5d_mean", "win_rate_5d", "long_total_ret_5d_mean", "short_total_ret_5d_mean"],
        col_labels={"bucket": "桶", "n": "样本数", "fwd_ret_5d_mean": "5天价格收益", "win_rate_5d": "5天价格胜率", "long_total_ret_5d_mean": "5天做多含资金费", "short_total_ret_5d_mean": "5天做空含资金费", "funding_rate_last_mean": "事件日 funding 均值"},
    ) + render_note("这正是你说的关键：如果把资金费算进去，有些桶的结论会变化。所以我们后续不能只看价格收益。", kind="good"))

    body += render_section("8. 结合 GTC 这类实时币，怎么理解？", ul([
        "GTC 这种状态，更像我们研究里的‘暴涨 + 负 funding 压力样本’。",
        "但它现在还不是‘负 funding + 失速结构确认’。",
        "如果后续它出现‘价格不再猛冲、开始失速、但 funding 仍负很深’，那才更像 1.4 里最值得研究的那条结构。",
        "所以现在看 GTC，更适合当活教材，不适合直接当结论。",
    ]))

    body += render_section("9. 我对 1.4 的最终判断", render_note("当前 1.4 的核心价值，不是给出一个可交易结论，而是把‘价格收益’和‘资金费后收益’一起拆开看。", kind="good") + ul([
        "日频研究已经足够说明：funding 结构确实重要。",
        "但单看价格收益会误判，必须看 funding-adjusted 收益。",
        "下一步不要继续泛扩样本，而应该继续做：**负 funding + 结构确认**。",
    ]))

    body += render_section("10. 产物索引", render_table(pd.DataFrame([
        {"文件": "reports/artifacts/binance_daily_event_study_v1_4/taxonomy_summary_v1_4.csv", "用途": "1.4 分桶汇总"},
        {"文件": "reports/artifacts/binance_daily_event_study_v1_4/findings_v1_4.md", "用途": "1.4 文字结论"},
        {"文件": "reports/artifacts/binance_daily_event_study_v1_4/manifest_v1_4.json", "用途": "1.4 元数据"},
        {"文件": "scripts/build_binance_daily_event_study_v1_4.py", "用途": "1.4 研究脚本"},
    ])) + p("页面生成时间：" + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")))

    extra_css = PAGE_CSS_DARK + """
    .hero { background: radial-gradient(circle at top right, #a855f733, transparent 35%), linear-gradient(135deg, #0f172a 0%, #111827 100%); }
    """
    html = render_page(
        "Step 1.4 讲明白：日频口径、funding-adjusted 收益、结构分类结果",
        body,
        subtitle="先把口径确认清楚，再决定 1.5 怎么做",
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        css=extra_css,
    )
    write_page(OUT, html)
    print(f"[ok] wrote {OUT}")


if __name__ == "__main__":
    main()
