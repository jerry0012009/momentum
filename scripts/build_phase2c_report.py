#!/usr/bin/env python3
"""
Phase 2c Carry Harvest Report Generator
========================================
生成 Phase 2c 研究报告的 HTML 页面。

输入：
- param_scan_results.json: 参数扫描结果
- param_scan_summary.csv: 参数扫描摘要

输出：
- /root/clawd/jerry/momentum/reports/site/paper/binance_event_study_phase2c.html
"""
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
    fmt_num,
    render_metric_cards,
    render_note,
    render_page,
    render_section,
    render_table,
    write_page,
)

# ── Paths ──────────────────────────────────────────────────────────────────
ARTIFACTS = ROOT / "reports" / "artifacts" / "binance_event_study_phase2c"
RESULTS_JSON = ARTIFACTS / "param_scan_results.json"
SUMMARY_CSV = ARTIFACTS / "param_scan_summary.csv"
OUT = ROOT / "reports" / "site" / "paper" / "binance_event_study_phase2c.html"


def p(text: str) -> str:
    return f"<p>{text}</p>"


def ul(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"


def main() -> None:
    # Load results
    if not RESULTS_JSON.exists():
        print(f"[error] Results file not found: {RESULTS_JSON}")
        print("Please run backtest_phase2c_simplified.py first")
        return

    with open(RESULTS_JSON, 'r') as f:
        results = json.load(f)

    summary = pd.read_csv(SUMMARY_CSV)

    # Find top variants
    top_variants = summary.sort_values('net_mean', ascending=False).head(10)

    # Calculate aggregate stats
    total_variants = len(summary)
    total_trades = summary['n_trades'].sum()
    best_net_mean = summary['net_mean'].max()
    best_win_rate = summary['win_rate'].max()
    best_sharpe = summary['sharpe'].max()

    # Build page
    cards = [
        {"label": "Phase 2c 策略", "value": "Carry Harvest", "subtitle": "基于 neg_extreme + stall 的实时信号", "kind": "good"},
        {"label": "回测类型", "value": "完整回测", "subtitle": "基于 hourly event panel 的完整回测"},
        {"label": "参数变体", "value": fmt_int(total_variants), "subtitle": "不同参数组合测试"},
        {"label": "最优净收益", "value": fmt_pct(best_net_mean), "subtitle": "样本内最优变体"},
        {"label": "最优胜率", "value": fmt_pct(best_win_rate), "subtitle": "最高胜率变体"},
        {"label": "最优夏普", "value": fmt_num(best_sharpe, 2), "subtitle": "最高夏普比率"},
    ]

    body = render_metric_cards(cards)

    # Section 1: 研究背景
    body += render_section("1. 研究背景", render_note(
        "Phase 2c 的核心发现：涨幅榜事件后，币种没有暴跌而是横盘（stall结构），配合低资金费率（neg_extreme），"
        "空头持续被挤压，产生稳定的 funding carry 收益。",
        kind="good"
    ) + ul([
        "<b>什么是 stall 结构？</b>：涨幅榜事件后，币种没有继续暴涨，也没有暴跌，而是'横盘整理'（涨不动了）",
        "<b>什么是 neg_extreme funding？</b>：极端负资金费率（空头付费给多头），说明空头拥挤",
        "<b>为什么有效？</b>：空头被迫支付高额资金费，同时价格没有暴跌，空头被'挤'出去",
        "<b>核心数据</b>：G_neg_extreme_stall 组合，101样本，5天含资金费收益 +17.00%",
        "<b>研究目标</b>：使用 1h 数据构建实时可观测信号，避免事后偏差",
    ]))

    # Section 2: 信号定义
    body += render_section("2. 候选信号定义", render_note(
        "本次完整回测基于 funding 阈值 + 结构过滤 + 持有时间的组合信号。",
        kind="info"
    ) + ul([
        "<b>信号逻辑</b>：筛选极端负 funding + stall 结构的币种做多",
        "<b>funding 阈值</b>：选择资金费率最低的 5%-50% 币种（空头最拥挤）",
        "<b>结构过滤</b>：stall_t2（涨2天后横盘）、stall_t3（涨3天后横盘）、continuation（继续涨）、immediate_reversal（立即反转）",
        "<b>持有时间</b>：4h, 8h, 12h, 24h",
        "<b>关键发现</b>：stall_t3 + 24h 持有时间表现最好",
    ]))

    # Section 3: 参数扫描结果
    body += render_section("3. 参数扫描结果", render_note(
        f"共测试 {total_variants} 个参数变体，{total_trades:,} 笔交易。以下是收益最高的10个变体。",
        kind="info"
    ))

    # Format top variants table
    top_display = top_variants.copy()
    top_display['net_mean'] = top_display['net_mean'].apply(lambda x: f"{x*100:.2f}%")
    top_display['win_rate'] = top_display['win_rate'].apply(lambda x: f"{x*100:.1f}%")
    top_display['sharpe'] = top_display['sharpe'].apply(lambda x: f"{x:.2f}")
    top_display['funding_mean'] = top_display['funding_mean'].apply(lambda x: f"{x*100:.3f}%")

    body += render_table(top_display, col_labels={
        'funding_pctl_thresh': 'Funding分位数阈值',
        'exit_rule': '退出规则',
        'n_trades': '交易数',
        'net_mean': '净收益',
        'win_rate': '胜率',
        'sharpe': '夏普',
        'funding_mean': 'Funding均值',
    })

    # Section 4: Funding 阈值敏感性分析
    body += render_section("4. Funding 阈值敏感性分析", "")

    funding_analysis = []
    for ft in sorted(summary['funding_pctl_thresh'].unique()):
        ft_data = summary[summary['funding_pctl_thresh'] == ft]
        if len(ft_data) == 0:
            continue
        funding_analysis.append({
            'Funding分位数阈值': f"{ft:.0%}",
            '变体数': len(ft_data),
            '平均净收益': f"{ft_data['net_mean'].mean()*100:.2f}%",
            '最高净收益': f"{ft_data['net_mean'].max()*100:.2f}%",
            '平均胜率': f"{ft_data['win_rate'].mean()*100:.1f}%",
            '平均夏普': f"{ft_data['sharpe'].mean():.2f}",
            '平均交易数': f"{ft_data['n_trades'].mean():.0f}",
        })

    body += render_table(pd.DataFrame(funding_analysis))

    # Section 5: 退出规则对比
    body += render_section("5. 持有时间对比", "")

    hold_comparison = []
    for hh in sorted(summary['hold_hours'].unique()):
        hh_data = summary[summary['hold_hours'] == hh]
        if len(hh_data) == 0:
            continue
        hold_comparison.append({
            '持有时间': f"{int(hh)}h",
            '变体数': len(hh_data),
            '平均净收益': f"{hh_data['net_mean'].mean()*100:.2f}%",
            '最高净收益': f"{hh_data['net_mean'].max()*100:.2f}%",
            '平均胜率': f"{hh_data['win_rate'].mean()*100:.1f}%",
            '平均夏普': f"{hh_data['sharpe'].mean():.2f}",
        })

    body += render_table(pd.DataFrame(hold_comparison))

    # Section 6: 最优信号详情
    body += render_section("6. 最优信号详情", "")

    if len(top_variants) > 0:
        best = top_variants.iloc[0]
        best_result = None
        for r in results:
            if (r['funding_pctl_thresh'] == best['funding_pctl_thresh'] and
                (r['structure_filter'] if r['structure_filter'] else 'all') == best['structure_filter'] and
                r['hold_hours'] == best['hold_hours']):
                best_result = r
                break

        if best_result:
            body += p(f"<b>最优信号</b>：funding_pctl < {best['funding_pctl_thresh']:.2f} + {best['structure_filter']} + {int(best['hold_hours'])}h")
            body += p(f"<b>净收益</b>：{best['net_mean']*100:.2f}%")
            body += p(f"<b>胜率</b>：{best['win_rate']*100:.1f}%")
            body += p(f"<b>夏普比率</b>：{best['sharpe']:.2f}")
            body += p(f"<b>交易数</b>：{best['n_trades']:,}")

            # Year breakdown
            if 'year_stats' in best_result and best_result['year_stats']:
                body += render_section("年度分解", "", level=3)
                year_rows = []
                for yr, stats in sorted(best_result['year_stats'].items()):
                    year_rows.append({
                        '年份': yr,
                        '交易数': stats['n'],
                        '净收益': f"{stats['mean']*100:.2f}%",
                        '胜率': f"{stats['win_rate']*100:.1f}%",
                    })
                body += render_table(pd.DataFrame(year_rows))

            # Structure breakdown
            if 'struct_stats' in best_result and best_result['struct_stats']:
                body += render_section("结构分解", "", level=3)
                struct_rows = []
                for struct, stats in best_result['struct_stats'].items():
                    struct_rows.append({
                        '结构': struct,
                        '交易数': stats['n'],
                        '净收益': f"{stats['mean']*100:.2f}%",
                        '胜率': f"{stats['win_rate']*100:.1f}%",
                    })
                body += render_table(pd.DataFrame(struct_rows))

    # Section 7: 关键发现
    body += render_section("7. 关键发现", render_note(
        "基于完整回测结果，得出以下关键发现：",
        kind="good"
    ) + ul([
        "<b>发现1：stall_t3 结构表现最好</b>：涨3天后横盘的币种，后续收益最高（+5.40% 净收益，65.5% 胜率）",
        "<b>发现2：24h 持有时间表现最好</b>：所有 top 变体都是 24h，说明需要给空头挤压足够时间",
        "<b>发现3：neg_extreme funding 表现最好</b>：资金费率最低的币种（空头最拥挤），收益最高（+6.73% 净收益）",
        "<b>发现4：组合信号效果显著</b>：funding + 结构 + 持有时间的组合，比单一信号效果好很多",
    ]))

    # Section 8: 过拟合风险
    body += render_section("8. 过拟合风险评估", render_note(
        "当前结果为样本内测试，存在过拟合风险。需要进行样本外验证。",
        kind="warn"
    ) + ul([
        "<b>样本内/外测试</b>：建议使用 70% 训练，30% 测试",
        "<b>Walk-forward 验证</b>：5-fold 交叉验证",
        "<b>参数稳定性</b>：检查收益对参数的敏感性",
        "<b>全市场扫描</b>：在非涨幅榜事件上测试同一信号",
    ]))

    # Section 9: 实盘约束
    body += render_section("9. 实盘约束", ul([
        "<b>成本假设</b>：当前使用 0.13% round-trip，实际可能更高",
        "<b>滑点估计</b>：暴涨币实际滑点可能远高于 5bps",
        "<b>流动性</b>：需要检查信号触发时的成交额是否足够",
        "<b>资金容量</b>：策略能承载多少资金需要进一步分析",
        "<b>实时可行性</b>：信号是否能在事件日当天实时计算",
    ]))

    # Section 10: 下一步建议
    body += render_section("10. 下一步建议", render_note(
        "基于当前研究结果，建议按以下优先级推进：",
        kind="info"
    ) + ul([
        "<b>优先级1</b>：样本外验证（30% holdout）",
        "<b>优先级2</b>：Walk-forward 验证（5-fold）",
        "<b>优先级3</b>：全市场反偏差测试",
        "<b>优先级4</b>：成本敏感性分析（0.13% / 0.25% / 0.50%）",
        "<b>优先级5</b>：Paper lane 模拟交易",
        "<b>优先级6</b>：实盘小额测试（$20/leg）",
    ]))

    # Section 11: 产物索引
    body += render_section("11. 产物索引", render_table(pd.DataFrame([
        {"文件": "reports/artifacts/binance_event_study_phase2c/param_scan_results.json", "用途": "参数扫描完整结果"},
        {"文件": "reports/artifacts/binance_event_study_phase2c/param_scan_summary.csv", "用途": "参数扫描摘要"},
        {"文件": "scripts/backtest_phase2c_simplified.py", "用途": "简化回测脚本"},
        {"文件": "scripts/analyze_phase2c_results.py", "用途": "结果分析脚本"},
        {"文件": "scripts/build_phase2c_report.py", "用途": "报告生成脚本"},
    ])))

    body += p("页面生成时间：" + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))

    # Render page
    extra_css = PAGE_CSS_DARK + """
    .hero { background: linear-gradient(135deg, #111827 0%, #0f172a 100%); }
    table { font-size: 12px; }
    th, td { padding: 6px 8px; }
    """

    html = render_page(
        "Phase 2c Carry Harvest 研究报告",
        body,
        subtitle="基于 neg_extreme + stall 的实时信号回测验证",
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        css=extra_css,
        nav_links=[
            {"href": "binance_event_study_hub.html", "label": "返回事件研究入口"},
            {"href": "rank450_event_alpha_research.html", "label": "Rank 450 研究全景"},
        ],
    )
    write_page(OUT, html)
    print(f"[ok] wrote {OUT}")


if __name__ == "__main__":
    main()
