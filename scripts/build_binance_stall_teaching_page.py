#!/usr/bin/env python3
"""Build teaching page for Step 1.3 stall definition + evidence."""
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

CAND = ROOT / "reports" / "artifacts" / "binance_daily_event_study_v1_3" / "daily_stall_candidates_v1_3.csv"
CAND_SUMMARY = ROOT / "reports" / "artifacts" / "binance_daily_event_study_v1_3" / "daily_stall_summary_v1_3.csv"
INTRA_SUMMARY = ROOT / "reports" / "artifacts" / "binance_daily_event_study_v1_3" / "intraday_sample" / "intraday_sample_summary_v1_3.csv"
OUT = ROOT / "reports" / "site" / "paper" / "binance_stall_definition_and_evidence.html"


def p(text: str) -> str:
    return f"<p>{text}</p>"


def ul(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"


def main() -> None:
    df = pd.read_csv(CAND)
    intra = pd.read_csv(INTRA_SUMMARY)
    gain = df[df.event_type == "top_gainer_1d"].copy()

    summary = pd.read_csv(CAND_SUMMARY)
    gain_sum = summary[summary.event_type == "top_gainer_1d"].copy()
    intra_row = pd.read_csv(INTRA_SUMMARY).iloc[0]

    metrics = gain_sum[["candidate", "events", "fwd_5d_mean", "fwd_5d_mean_net10bps", "fwd_5d_win"]].copy()
    metrics = metrics.rename(columns={
        "candidate": "label",
        "fwd_5d_mean": "mean_return",
        "fwd_5d_mean_net10bps": "mean_return_net10bps",
        "fwd_5d_win": "win_rate",
    })

    base_mean = metrics.loc[metrics.label == "gainer_baseline_continue", "mean_return"].iloc[0]
    cand_mean = metrics.loc[metrics.label == "gainer_A_t2_reversal", "mean_return"].iloc[0]

    cards = [
        {"label": "先说结论", "value": "失速窗口不是玄学", "subtitle": "它有明确的日线操作性定义，且在小时线上也能观察到", "kind": "good"},
        {"label": "最关键对比", "value": f"候选 A 的 5d 均值 {fmt_pct(cand_mean)} vs {fmt_pct(base_mean)}", "subtitle": "失速候选 vs continuation"},
        {"label": "口径说明", "value": "这里都是 T+2 之后的 long forward return", "subtitle": "不是‘失速后立刻做空’的收益"},
        {"label": "日内风险证据", "value": f"日线 MAE {fmt_pct(float(intra_row['daily_mae_mean']))} -> 日内 MAE {fmt_pct(float(intra_row['intraday_mae_mean']))}", "subtitle": "日线会低估回撤"},
        {"label": "建议怎么看这张页", "value": "先看定义，再看证据", "subtitle": "这不是 live 策略，是研究阶段解释"},
    ]

    body = render_metric_cards(cards)

    body += render_section("0. 先回答你的关键问题", render_note("baseline 和候选比较的，都是同一类 forward return：从 T+2 往后看 5 天的 long forward return。不是‘baseline 做多，失速后做空’。", kind="warn") + ul([
        "<b>baseline_continue</b> 的意思是：如果 T+1 还继续涨，就把它作为对照组。",
        "<b>候选 A/B/C</b> 的意思是：如果出现了失速形态，就把它作为研究组。",
        "然后我们都看它们后续 5 天的表现，用来比较哪类状态更值得继续研究。",
        "所以你刚才理解里的 +0.05%/+0.06%，不是做空收益，是‘失速样本的后续 5 天多头 forward return 均值’。",
    ]))

    body += render_section("0a. 为什么要专门解释‘失速窗口’？", render_note("你提的问题非常关键：如果连‘失速’都没有清楚定义，那后面所有结论都只是感觉，不是研究。", kind="warn") + ul([
        "我们不是在说‘涨多了就一定跌’这种模糊判断。",
        "我们在测的是一个更具体的问题：新晋 top gainer 发生后，**第二天的状态**能不能把后续表现区分开。",
        "所以‘失速窗口’必须有可执行定义，不能只看结果。",
    ]))

    body += render_section("1. 什么是‘失速窗口’？操作性定义", render_table(pd.DataFrame([
        {"定义层": "直觉解释", "内容": "一个币刚进入涨幅榜后，不是继续稳步往上走，而是出现‘涨不动了’的证据。"},
        {"定义层": "操作性定义", "内容": "我们在日线侧把它拆成了几条可计算规则，比如：T+1 仍上涨，但 T+2 出现回落/成交量萎缩/累计动能不足。"},
        {"定义层": "为什么叫窗口", "内容": "因为它不是某一个瞬间，而是一段‘证据开始出现的时间区间’，所以叫失速窗口。"},
    ]), col_labels={"定义层": "定义层", "内容": "内容"}) + ul([
        "<b>候选 A</b>：T+1 还在涨，但 T+2 价格回落，也就是‘第二天还冲了一下，第三天开始掉头’。",
        "<b>候选 B</b>：T+1 还在涨，但 T+2 成交额明显缩下来，价格也走平/回落。",
        "<b>候选 C</b>：T+1 虽然涨，但两天累计还是偏弱，说明上涨动能没有积累起来。",
    ]))

    body += render_section("2. 我们用了哪些指标？", render_table(pd.DataFrame([
        {"指标": "fwd_ret_5d_from_t2", "意思": "从 T+2 往后看 5 天的价格收益；用来判断失速窗口之后，走势是继续好还是变差。"},
        {"指标": "win rate", "意思": "收益大于 0 的比例。不是暴利指标，但能看方向偏向。"},
        {"指标": "MAE", "意思": "最大逆向幅度，也就是最差会先亏多少。"},
        {"指标": "MFE", "意思": "最大正向幅度，也就是最好能冲到多少。"},
        {"指标": "Sharpe（此处为年化近似）", "意思": "把事件后收益均值除以波动，并年化；这里只作为粗比较，不是 live 策略 Sharpe。"},
        {"指标": "cumulative_event_sum", "意思": "把所有事件的收益直接加总，用于粗看整体方向，不是真正可复现资金曲线。"},
    ])) + render_note("这里的 Sharpe 和 cumulative sum 都是研究阶段的粗指标，用来比较哪组更强，不是用来证明已经可交易。", kind="warn"))

    body += render_section("3. 失速窗口比继续冲更值得关注的证据", render_table(
        metrics[["label", "events", "mean_return", "mean_return_net10bps", "win_rate"]],
        col_formats={"events": fmt_int, "mean_return": fmt_pct, "mean_return_net10bps": fmt_pct, "win_rate": fmt_pct},
        col_positive_good=["mean_return", "mean_return_net10bps", "win_rate"],
        col_labels={"label": "策略/分组", "events": "样本数", "mean_return": "5天收益均值", "mean_return_net10bps": "扣10bps后", "win_rate": "胜率"},
    ) + render_note("从这组证据看，候选 A/B/C 都比 baseline_continue 更好一点，但注意：改善幅度仍然是薄改善，不是厚 alpha。", kind="good"))

    body += render_section("4. 更直白地说：谁比谁高多少？", ul([
        f"<b>baseline_continue</b> 的 5 天收益均值：{fmt_pct(metrics.loc[metrics.label == 'gainer_baseline_continue', 'mean_return'].iloc[0])}",
        f"<b>候选 A</b> 的 5 天收益均值：{fmt_pct(metrics.loc[metrics.label == 'gainer_A_t2_reversal', 'mean_return'].iloc[0])}",
        f"<b>候选 B</b> 的 5 天收益均值：{fmt_pct(metrics.loc[metrics.label == 'gainer_B_volume_contraction_stall', 'mean_return'].iloc[0])}",
        f"<b>候选 C</b> 的 5 天收益均值：{fmt_pct(metrics.loc[metrics.label == 'gainer_C_two_day_exhaustion', 'mean_return'].iloc[0])}",
        "所以这不是‘失速窗口已经大胜’，而是‘失速窗口比简单 continuation 更合理一点’。",
    ]))

    body += render_section("5. 日内样本又说明了什么？", render_table(pd.DataFrame([
        {"指标": "日线 MAE 均值", "数值": fmt_pct(float(intra_row['daily_mae_mean']))},
        {"指标": "日内 MAE 均值", "数值": fmt_pct(float(intra_row['intraday_mae_mean']))},
        {"指标": "日线 MFE 均值", "数值": fmt_pct(float(intra_row['daily_mfe_mean']))},
        {"指标": "日内 MFE 均值", "数值": fmt_pct(float(intra_row['intraday_mfe_mean']))},
        {"指标": "失速确认均值时点", "数值": f"T+2 第 {float(intra_row['mean_stall_bar_idx']):.1f} 根小时线"},
        {"指标": "T+2 成交量萎缩占比", "数值": fmt_pct(float(intra_row['t2_volume_contraction']))},
    ])) + ul([
        "日内数据告诉我们：日线看到的失速不是假象，它在小时线上也存在。",
        "但同时，日内回撤比日线大很多，说明任何基于日线止损的策略都会低估真实风险。",
        "这也是为什么我说：现在不能直接把日线失速信号扩成 live。",
    ]))

    body += render_section("6. 我为什么建议先不做更大规模 1h 回测？", render_note("因为现在的证据说明：信号存在，但风险也被低估了。如果直接扩规模，很容易做出‘看起来可研究，其实很脆’的结论。", kind="warn") + ul([
        "下一步更该做的是：把候选 A/C 与 funding、成交额、连续上涨天数等拥挤条件叠加。",
        "先在更窄的样本里看，失速 + 拥挤 是否让 edge 更集中。",
        "如果这一步成立，再考虑更大范围回测。",
    ]))

    body += render_section("7. 结论", ul([
        "<b>失速窗口不是玄学</b>，它有明确的操作性定义。",
        "<b>证据支持失速窗口比 continuation 更值得关注</b>，但只是薄改善，不是厚 alpha。",
        "<b>日内证据支持失速窗口存在</b>，但同时显示日线 MAE 会低估真实回撤。",
        "所以下一步应该是：**继续收窄条件，而不是扩大样本**。",
    ]))

    body += render_section("8. 产物索引", render_table(pd.DataFrame([
        {"文件": "reports/artifacts/binance_daily_event_study_v1_3/daily_stall_candidates_v1_3.csv", "用途": "候选与远期收益的基础数据"},
        {"文件": "reports/artifacts/binance_daily_event_study_v1_3/daily_stall_summary_v1_3.csv", "用途": "候选汇总"},
        {"文件": "reports/artifacts/binance_daily_event_study_v1_3/intraday_sample/intraday_sample_summary_v1_3.csv", "用途": "日内样本汇总"},
        {"文件": "scripts/build_binance_stall_teaching_page.py", "用途": "本次讲解页脚本"},
    ])) + p("页面生成时间：" + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")))

    extra_css = PAGE_CSS_DARK + """
    .hero { background: radial-gradient(circle at top left, #0ea5e933, transparent 35%), linear-gradient(135deg, #0f172a 0%, #111827 100%); }
    """
    html = render_page(
        "先把‘失速窗口’讲清楚：定义、指标和证据",
        body,
        subtitle="在进入下一阶段前，把 H1.3 的操作性定义和比较证据解释明白",
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        css=extra_css,
    )
    write_page(OUT, html)
    print(f"[ok] wrote {OUT}")


if __name__ == "__main__":
    main()
