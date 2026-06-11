#!/usr/bin/env python3
"""Build Step 1.2 T+1 state study report page."""
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

ART = ROOT / "reports" / "artifacts" / "binance_daily_event_study_v1_2"
OUT = ROOT / "reports" / "site" / "paper" / "binance_daily_event_study_v1_2.html"


def p(text: str) -> str:
    return f"<p>{text}</p>"


def ul(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"


def load():
    manifest = json.loads((ART / "manifest_v1_2.json").read_text(encoding="utf-8"))
    summary = pd.read_csv(ART / "summary_t1_state_v1_2.csv")
    findings = (ART / "summary_findings_v1_2.md").read_text(encoding="utf-8")
    return manifest, summary, findings


def build_body(manifest: dict, summary: pd.DataFrame, findings: str) -> str:
    g = summary[summary.event_type == "top_gainer_1d"].copy()
    l = summary[summary.event_type == "top_loser_1d"].copy()

    cards = [
        {"label": "这轮研究目的", "value": "验证 T+1 状态", "subtitle": "新晋事件后，第二天继续冲 vs 失速反转，哪个更值得研究"},
        {"label": "样本量", "value": f"{manifest.get('n_events_new', manifest.get('event_rows', 0)):,}", "subtitle": "只看 streak_label=new 的事件"},
        {"label": "最重要的发现 A", "value": "涨幅榜续涨更差", "subtitle": "T+1 继续涨时，之后 5 天反而更弱；continuation 不像 alpha"},
        {"label": "最重要的发现 B", "value": "跌幅榜延续更抗", "subtitle": "T+1 继续跌的 group，之后 5 天比反弹组更稳一点"},
    ]

    body = render_metric_cards(cards)

    body += render_section("0. 先说结论：这个试验有没有白做？", render_note("没有白做。虽然 T+1 精度确实粗，但它已经告诉我们一个重要事实：**新晋事件不是‘继续冲就更强’**。换句话说，continuation 不是这份 alpha。", kind="warn") + ul([
        "对 **top gainer** 来说，T+1 继续涨的样本，之后 5 天反而更差。",
        "对 **top loser** 来说，T+1 继续跌的样本，比 T+1 反弹的样本更抗一点。",
        "整体看，所有组别的 5 天胜率都低于 50%，说明 **new 事件后整体仍然偏弱**。",
    ]))

    body += render_section("1. 我们这次到底在测什么？", ul([
        "只看 v1 里的 <code>new</code> 事件，也就是**首次进入涨跌榜**。",
        "对每条事件看 T+1：第二天是继续同向，还是失速/反转。",
        "然后从 T+1 往后看 2/3/5 天，判断哪类状态更像 alpha。",
        "这次没有扩 universe，也没有加复杂形态，就是最小试验。",
    ]))

    if not g.empty:
        body += render_section("2. 涨幅榜：T+1 继续涨 vs 失速反转", render_table(
            g[["t1_category", "count", "mean_t1_ret", "mean_fwd_2d_from_t1", "mean_fwd_3d_from_t1", "mean_fwd_5d_from_t1", "win_rate_2d_from_t1", "win_rate_5d_from_t1", "median_qvol_ratio"]],
            col_formats={"count": fmt_int, "mean_t1_ret": fmt_pct, "mean_fwd_2d_from_t1": fmt_pct, "mean_fwd_3d_from_t1": fmt_pct, "mean_fwd_5d_from_t1": fmt_pct, "win_rate_2d_from_t1": fmt_pct, "win_rate_5d_from_t1": fmt_pct, "median_qvol_ratio": fmt_pct},
            col_positive_good=["mean_t1_ret", "mean_fwd_2d_from_t1", "mean_fwd_3d_from_t1", "mean_fwd_5d_from_t1"],
            col_labels={"t1_category": "T+1 状态", "count": "样本数", "mean_t1_ret": "T+1 收益", "mean_fwd_2d_from_t1": "T+1后2天", "mean_fwd_3d_from_t1": "T+1后3天", "mean_fwd_5d_from_t1": "T+1后5天", "win_rate_2d_from_t1": "2天胜率", "win_rate_5d_from_t1": "5天胜率", "median_qvol_ratio": "T+1成交额比"},
        ) + render_note("这说明：对于新晋涨幅榜，**第二天继续涨并不是好信号**。更像短期动量耗散，而不是 continuation alpha。", kind="bad"))

    if not l.empty:
        body += render_section("3. 跌幅榜：T+1 继续跌 vs 失速反弹", render_table(
            l[["t1_category", "count", "mean_t1_ret", "mean_fwd_2d_from_t1", "mean_fwd_3d_from_t1", "mean_fwd_5d_from_t1", "win_rate_2d_from_t1", "win_rate_5d_from_t1", "median_qvol_ratio"]],
            col_formats={"count": fmt_int, "mean_t1_ret": fmt_pct, "mean_fwd_2d_from_t1": fmt_pct, "mean_fwd_3d_from_t1": fmt_pct, "mean_fwd_5d_from_t1": fmt_pct, "win_rate_2d_from_t1": fmt_pct, "win_rate_5d_from_t1": fmt_pct, "median_qvol_ratio": fmt_pct},
            col_positive_good=["mean_t1_ret", "mean_fwd_2d_from_t1", "mean_fwd_3d_from_t1", "mean_fwd_5d_from_t1"],
            col_labels={"t1_category": "T+1 状态", "count": "样本数", "mean_t1_ret": "T+1 收益", "mean_fwd_2d_from_t1": "T+1后2天", "mean_fwd_3d_from_t1": "T+1后3天", "mean_fwd_5d_from_t1": "T+1后5天", "win_rate_2d_from_t1": "2天胜率", "win_rate_5d_from_t1": "5天胜率", "median_qvol_ratio": "T+1成交额比"},
        ) + render_note("这说明：对于新晋跌幅榜，**T+1 继续跌的样本比立刻反弹的样本更稳一点**。这可能值得继续拆，但还不是可以直接交易的结论。", kind="good"))

    body += render_section("4. 这结果对我们意味着什么？", ul([
        "你的直觉是对的：**只看 T+1 的日线精度太粗，很难直接做出策略。**",
        "但它已经帮我们排除了一个很常见的错误假设：**新晋榜单后继续冲 ≠ 更强 alpha。**",
        "对涨幅榜来说，continuation 反而更差；对跌幅榜来说，continuation 倒没有更差，但也谈不上厚。",
        "所以这个试验的价值，不是找到策略，而是**把错误路线标记出来**。",
    ]))

    body += render_section("5. 我现在对 alpha 的判断", render_note("如果还有 alpha，它大概率不在‘榜单当天’，也不在‘T+1 简单方向’，而在‘更细的状态确认’。", kind="warn") + ul([
        "<b>可能方向 A：</b>T+1/T+2 的减速、成交额萎缩、创新高失败。",
        "<b>可能方向 B：</b>首次异常 + 连续两天未创新高 + funding 仍在高位。",
        "<b>可能方向 C：</b>不是做新晋榜单，而是做‘控盘后第二阶段失速’。",
        "换句话说，下一步不是看更大样本，而是看更细状态。",
    ]))

    body += render_section("6. 我建议下一步做什么？", p("既然 T+1 粗线已经验证过，我建议下一步不要继续扩 universe，而是继续做更细的事件后状态拆分。") + render_table(pd.DataFrame([
        {"假设": "H1.3：失速形态假设", "做法": "在 new 事件后，看 T+1/T+2 是否创新高失败、是否放量但涨幅缩水", "价值": "比 T+1 方向更接近 alpha 窗口"},
        {"假设": "H1.4：拥挤+失速假设", "做法": "把 funding 重新引入，只研究 funding 极端 + 动量掉速的子集", "价值": "更贴近你说的控盘币/拥挤币"},
        {"假设": "H1.5：局部小级别样本回放", "做法": "只抽最典型的 200-500 个事件下载 1h K 线", "价值": "验证真实入场、止损、日内 MAE"},
    ])))

    body += render_section("7. 产物索引", render_table(pd.DataFrame([
        {"文件": "events_t1_state_v1_2.csv", "用途": "每个 new 事件的 T+1 状态与远期收益"},
        {"文件": "summary_t1_state_v1_2.csv", "用途": "按 event_type × t1_category 的汇总"},
        {"文件": "summary_findings_v1_2.md", "用途": "文字结论"},
        {"文件": "manifest_v1_2.json", "用途": "元数据与输入输出记录"},
        {"文件": "scripts/step1_2_new_coin_t1_state.py", "用途": "本次研究脚本"},
    ])) + p("页面生成时间：" + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")))

    return body


def main() -> None:
    manifest, summary, findings = load()
    body = build_body(manifest, summary, findings)
    extra_css = PAGE_CSS_DARK + """
    .hero { background: radial-gradient(circle at bottom right, #22c55e33, transparent 35%), linear-gradient(135deg, #0f172a 0%, #111827 100%); }
    """
    html = render_page(
        "Step 1.2：新晋事件的 T+1 状态，验证 continuation 是否更厚",
        body,
        subtitle="只验证一个假设：T+1 继续冲 vs 失速反转，哪边更值得继续研究？",
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        css=extra_css,
    )
    write_page(OUT, html)
    print(f"[ok] wrote {OUT}")


if __name__ == "__main__":
    main()
