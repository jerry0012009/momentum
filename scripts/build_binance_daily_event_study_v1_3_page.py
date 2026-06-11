#!/usr/bin/env python3
"""Build Step 1.3 combined report page."""
from __future__ import annotations

import json
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

DAILY_ART = ROOT / "reports" / "artifacts" / "binance_daily_event_study_v1_3"
INTRA_ART = DAILY_ART / "intraday_sample"
OUT = ROOT / "reports" / "site" / "paper" / "binance_daily_event_study_v1_3.html"


def p(text: str) -> str:
    return f"<p>{text}</p>"


def ul(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"


def load():
    daily_manifest = json.loads((DAILY_ART / "manifest_v1_3.json").read_text(encoding="utf-8"))
    daily_summary = pd.read_csv(DAILY_ART / "daily_stall_summary_v1_3.csv")
    daily_findings = (DAILY_ART / "findings_v1_3.md").read_text(encoding="utf-8")
    intra_manifest = json.loads((INTRA_ART / "intraday_sample_manifest_v1_3.json").read_text(encoding="utf-8"))
    intra_summary = pd.read_csv(INTRA_ART / "intraday_sample_summary_v1_3.csv")
    intra_findings = (INTRA_ART / "intraday_findings_v1_3.md").read_text(encoding="utf-8")
    return daily_manifest, daily_summary, daily_findings, intra_manifest, intra_summary, intra_findings


def build_body(daily_manifest, daily_summary, daily_findings, intra_manifest, intra_summary, intra_findings) -> str:
    gainer = daily_summary[daily_summary.event_type == "top_gainer_1d"].copy()
    best_row = gainer.sort_values("fwd_5d_mean", ascending=False).iloc[0]
    baseline_row = gainer[gainer.candidate == "gainer_baseline_continue"].iloc[0]
    delta = float(best_row["fwd_5d_mean"] - baseline_row["fwd_5d_mean"]) * 100

    cards = [
        {"label": "这轮研究结论", "value": "边际有效", "subtitle": "日线失速形态存在，但日内风险被严重低估", "kind": "warn"},
        {"label": "日线侧最重要变化", "value": f"+{delta:.2f}%", "subtitle": f"最佳候选 5d 均值相对 baseline_continue 的改善"},
        {"label": "日内样本结论", "value": intra_manifest.get("recommendation", "marginal"), "subtitle": "失速确认来得早，但日内 MAE 大幅变差"},
        {"label": "日线 MAE vs 日内 MAE", "value": f"{intra_summary.iloc[0]['daily_mae_mean']*100:.2f}% -> {intra_summary.iloc[0]['intraday_mae_mean']*100:.2f}%", "subtitle": "日线严重低估了真实回撤"},
    ]

    body = render_metric_cards(cards)

    body += render_section("0. 这一步到底在干什么？", render_note("Step 1.3 的目标不是直接找策略，而是验证一个更细的假设：新晋事件后，是不是‘失速窗口’比‘继续冲’更值得研究？", kind="warn") + ul([
        "先做日线侧 H1.3 初筛，看哪些失速候选比 baseline_continue 更好。",
        "如果日线证据都不成立，就不再扩到小时线。",
        "如果日线证据有苗头，再抽一个小样本做 1h 局部验证。",
        "这次用户提醒得很关键：很多爆拉币可能几个小时就见高点，只看日线会丢掉证据。",
    ]))

    body += render_section("1. 日线侧发现了什么？", render_table(
        daily_summary[daily_summary.event_type == "top_gainer_1d"][["candidate", "events", "fwd_5d_mean", "fwd_5d_win", "fwd_5d_mean_net10bps", "qvol_ratio_t2_t1_median"]],
        col_formats={"events": fmt_int, "fwd_5d_mean": fmt_pct, "fwd_5d_win": fmt_pct, "fwd_5d_mean_net10bps": fmt_pct, "qvol_ratio_t2_t1_median": fmt_pct},
        col_positive_good=["fwd_5d_mean", "fwd_5d_win"],
        col_labels={"candidate": "候选模式", "events": "样本数", "fwd_5d_mean": "5天后价格", "fwd_5d_win": "5天胜率", "fwd_5d_mean_net10bps": "扣10bps后", "qvol_ratio_t2_t1_median": "T+2/T+1成交额中位数"},
    ) + ul([
        "涨幅榜三个失速候选都比 baseline_continue 好一点。",
        "但注意：这里的改善幅度仍然是**薄改善**，不是厚 alpha。",
        "真正值得继续看的原因，不是因为日线收益大，而是因为它把‘榜单 continuation’从错误路线里拉出来了。",
    ]))

    body += render_section("2. 为什么还要做日内样本？", render_note("因为你直觉是对的：很多妖币可能几小时就冲到最高点。只看日线收盘，会把真正的失速时点掩盖掉。", kind="good") + ul([
        "这次我们只抽了 150 个典型事件样本做 1h 回放。",
        "目的不是做全量回测，而是验证两件事：<br>1）日线失速形态在小时线上是否存在；<br>2）日内真实 MAE 是否比日线大很多。",
    ]))

    body += render_section("3. 日内样本最重要的发现", render_table(
        pd.DataFrame([
            {"指标": "MAE 日线均值", "数值": f"{intra_summary.iloc[0]['daily_mae_mean']*100:.2f}%"},
            {"指标": "MAE 日内均值", "数值": f"{intra_summary.iloc[0]['intraday_mae_mean']*100:.2f}%"},
            {"指标": "MFE 日线均值", "数值": f"{intra_summary.iloc[0]['daily_mfe_mean']*100:.2f}%"},
            {"指标": "MFE 日内均值", "数值": f"{intra_summary.iloc[0]['intraday_mfe_mean']*100:.2f}%"},
            {"指标": "失速确认均值时点", "数值": f"T+2 第 {intra_summary.iloc[0]['mean_stall_bar_idx']:.1f} 根小时线"},
            {"指标": "T+2 成交量萎缩占比", "数值": f"{intra_summary.iloc[0]['t2_volume_contraction']*100:.1f}%"},
        ])
    ) + ul([
        "100% 的样本日内 MAE 都比日线 MAE 更差。",
        "100% 的样本日内 MFE 也都比日线 MFE 更高。",
        "翻译成人话：这类事件的真实波动比日线看到的更大，既更容易打止损，也更容易冲得更高。",
        "失速确认平均在 T+2 第 1.9 根小时线就出现了，说明信号来得很早。",
    ]))

    body += render_section("4. 这说明了什么？", ul([
        "<b>结论 A：</b>日线失速形态在小时级别是成立的，不是日线噪声虚构出来的。",
        "<b>结论 B：</b>日线回测严重低估真实回撤风险。任何基于日线信号的止损都必须放宽，否则会频繁被打掉。",
        "<b>结论 C：</b>这还不是可以直接扩成 live 的策略，只是证明这条路线值得继续细化。",
    ]))

    body += render_section("5. 我的建议：不要立刻扩全市场 1h 回测", render_note("下一步不是‘更多数据’，而是‘更严格风险预算 + 更窄样本深挖’。", kind="warn") + ul([
        "先不要把这件事扩成大规模小时线研究。",
        "下一步更应该做的是：在日线候选里加入更严格条件，比如失速 + funding 仍高、或失速 + 之前连涨且成交额异常。",
        "如果这些条件能进一步集中样本，并且 MAE 仍然可接受，再考虑扩到更大范围。",
    ]))

    body += render_section("6. 当前产物索引", render_table(pd.DataFrame([
        {"文件": "daily_stall_summary_v1_3.csv", "用途": "日线侧候选汇总"},
        {"文件": "candidate_selection_v1_3.csv", "用途": "候选筛选结果"},
        {"文件": "findings_v1_3.md", "用途": "日线侧中文结论"},
        {"文件": "intraday_sample/intraday_sample_summary_v1_3.csv", "用途": "日内样本汇总"},
        {"文件": "intraday_sample/intraday_findings_v1_3.md", "用途": "日内样本中文结论"},
        {"文件": "intraday_sample/intraday_sample_manifest_v1_3.json", "用途": "日内样本元数据"},
        {"文件": "scripts/build_binance_daily_event_study_v1_3.py", "用途": "日线侧研究脚本"},
        {"文件": "scripts/build_intraday_sample_v1_3.py", "用途": "日内样本研究脚本"},
    ])) + p("页面生成时间：" + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")))

    return body


def main() -> None:
    daily_manifest, daily_summary, daily_findings, intra_manifest, intra_summary, intra_findings = load()
    body = build_body(daily_manifest, daily_summary, daily_findings, intra_manifest, intra_summary, intra_findings)
    extra_css = PAGE_CSS_DARK + """
    .hero { background: radial-gradient(circle at top left, #f9731633, transparent 35%), linear-gradient(135deg, #0f172a 0%, #111827 100%); }
    """
    html = render_page(
        "Step 1.3：失速形态验证，日线有苗头，日内风险更大",
        body,
        subtitle="先做日线侧 H1.3 初筛，再做小样本 1h 局部验证",
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        css=extra_css,
    )
    write_page(OUT, html)
    print(f"[ok] wrote {OUT}")


if __name__ == "__main__":
    main()
