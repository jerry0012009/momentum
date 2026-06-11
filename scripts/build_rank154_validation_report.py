#!/usr/bin/env python3
"""Build Rank 154 comprehensive validation report."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from momentum.html_render import (
    fmt_pct, fmt_usd, fmt_num, render_metric_cards, render_note,
    render_page, render_section, render_table, write_page,
)

ART_DIR = ROOT / "reports" / "artifacts" / "rank154_validation"
SITE_PATH = ROOT / "reports" / "site" / "paper" / "rank154_validation.html"


def main():
    v = json.loads((ART_DIR / "validation_results.json").read_text())
    b = v["baseline"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # === Hero ===
    hero = render_metric_cards([
        {"label": "120-Day Return", "value": fmt_pct(b["return"]), "subtitle": f'{b["days"]} days', "kind": "good" if b["return"] > 0 else "bad"},
        {"label": "Max Drawdown", "value": fmt_pct(b["max_dd"]), "subtitle": "120 days", "kind": "warn"},
        {"label": "Sharpe (ann.)", "value": fmt_num(b["sharpe"]), "subtitle": f'Win rate {fmt_pct(b["win_rate"])}', "kind": "good" if b["sharpe"] > 1.5 else "warn"},
        {"label": "Monthly Win", "value": "3/5", "subtitle": "Jan -0.6%, Feb -5.9%, Mar +27.9%, Apr -10.5%, May +24.1%"},
        {"label": "Rolling Win", "value": f'{v["rolling_stability"]["positive_windows"]}/{v["rolling_stability"]["total_windows"]}', "subtitle": f'{fmt_pct(v["rolling_stability"]["positive_rate"])} 30-day windows positive'},
        {"label": "Avg Recovery", "value": "10 days", "subtitle": "from drawdown to new high"},
    ])

    # === Parameter: Universe Size ===
    us_data = [r for r in v["param_sensitivity"] if r["param"] == "universe_size"]
    us_table = render_table(pd.DataFrame(us_data), columns=["value", "return", "max_dd", "sharpe", "win_rate"],
        col_labels={"value": "Universe", "return": "收益", "max_dd": "回撤", "sharpe": "Sharpe", "win_rate": "胜率"},
        col_formats={"return": fmt_pct, "max_dd": fmt_pct, "win_rate": fmt_pct},
        col_positive_good=["return"])

    # === Parameter: Carry Weight ===
    cw_data = [r for r in v["param_sensitivity"] if r["param"] == "carry_weight"]
    cw_table = render_table(pd.DataFrame(cw_data), columns=["value", "return", "max_dd", "sharpe", "win_rate"],
        col_labels={"value": "Carry 权重", "return": "收益", "max_dd": "回撤", "sharpe": "Sharpe", "win_rate": "胜率"},
        col_formats={"return": fmt_pct, "max_dd": fmt_pct, "win_rate": fmt_pct},
        col_positive_good=["return"])

    # === Monthly ===
    monthly_data = [{"month": k, "return": v} for k, v in v["monthly"].items()]
    monthly_table = render_table(pd.DataFrame(monthly_data), columns=["month", "return"],
        col_labels={"month": "月份", "return": "收益"}, col_formats={"return": fmt_pct}, col_positive_good=["return"])

    # === Rolling Windows ===
    rolling = v["rolling_stability"]
    roll_details = rolling["details"]
    roll_table = render_table(pd.DataFrame(roll_details), columns=["start", "end", "return", "max_dd", "sharpe"],
        col_labels={"start": "开始", "end": "结束", "return": "收益", "max_dd": "回撤", "sharpe": "Sharpe"},
        col_formats={"return": fmt_pct, "max_dd": fmt_pct},
        col_positive_good=["return"])

    # === Drawdown Recovery ===
    dd_data = v["drawdown_recovery"]
    dd_table = render_table(pd.DataFrame(dd_data), columns=["start", "end", "trough", "days"],
        col_labels={"start": "开始", "end": "恢复", "trough": "最深回撤", "days": "恢复天数"},
        col_formats={"trough": fmt_pct})

    # === Stability Verdict ===
    positive_windows = rolling["positive_windows"]
    total_windows = rolling["total_windows"]
    median_ret = rolling["median_return"]
    worst_window = rolling["min_return"]
    best_window = rolling["max_return"]

    # Count months with different outcomes
    monthly_rets = list(v["monthly"].values())
    pos_months = sum(1 for r in monthly_rets if r > 0)
    neg_months = sum(1 for r in monthly_rets if r <= 0)

    # Carry weight sensitivity
    best_cw = max(cw_data, key=lambda x: x["sharpe"])
    worst_cw = min(cw_data, key=lambda x: x["sharpe"])

    # Universe sensitivity
    best_us = max(us_data, key=lambda x: x["sharpe"])
    worst_us = min(us_data, key=lambda x: x["sharpe"])

    verdict_body = f"""
<div class="card">
<h3>稳定性综合评估</h3>

<h4>✓ 优势</h4>
<ul>
<li><b>120 天累计 +28.1%</b>，Sharpe 1.99，说明修正后的 carry 信号确实有 alpha</li>
<li><b>5 个月中 3 个月正收益</b>（Mar +27.9%, May +24.1%），正月份贡献远大于负月份</li>
<li><b>30 天滚动窗口 {positive_windows}/{total_windows} 正收益</b>，中位数 +2.3%</li>
<li><b>参数敏感性合理</b>：universe 15-50、carry 权重 0.2-0.8 范围内全部正收益</li>
<li><b>回撤恢复快</b>：平均 10 天恢复，最长 38 天（Apr 大回撤）</li>
</ul>

<h4>⚠️ 风险</h4>
<ul>
<li><b>1 月和 2 月连续亏损</b>（-0.6%, -5.9%），策略在低波动/震荡市表现差</li>
<li><b>4 月回撤 -10.5%</b>，最大回撤 -17.2%，持续 38 天——需要足够信念持有</li>
<li><b>最差 30 天窗口 -16.0%</b>（3 月底 → 4 月底），与最大回撤期重合</li>
<li><b>Carry 权重越高表现越差</b>：权重 0.2 时 Sharpe 3.35，权重 0.8 时 Sharpe 0.62</li>
<li><b>Universe 过小（15）或过大（50）都会降低 Sharpe</b>：最优是 30</li>
</ul>

<h4>💡 关键发现</h4>
<ul>
<li><b>Carry 权重应降低到 0.2-0.35</b>：当前 0.5 过高。低 carry 权重时 Sharpe 更高（3.35 vs 1.99），说明 carry 因子的 alpha 不如 momo/breakout</li>
<li><b>Universe 30 是最优</b>：15 太集中（Sharpe 0.54），50 太分散（Sharpe 1.70），30 最佳（1.99）</li>
<li><b>策略是趋势型</b>：3 月和 5 月大涨，1/2/4 月震荡或下跌——适合有趋势的市场</li>
<li><b>Funding PnL 占比较小</b>（-437 / 总收益 2813 = 16%），主要收益来自价格方向</li>
</ul>
</div>
"""

    # === Assemble ===
    body = hero
    body += render_section("120 天基线回测", render_note(
        f'<b>{b["days"]} 天回测</b>（2026-01-05 → 2026-05-08），修正后的 carry 信号（last settled rate）。'
        f'累计 {fmt_pct(b["return"])}，Sharpe {b["sharpe"]:.2f}，最大回撤 {fmt_pct(b["max_dd"])}。'
        f'Funding PnL {fmt_usd(b["funding_pnl"])}，Commission {fmt_usd(b["commission"])}。',
    ))

    body += render_section("参数敏感性：Universe 大小", us_table)
    body += render_note(
        f'Universe 30 最优（Sharpe {best_us["sharpe"]:.2f}）。'
        f'15 太集中导致 Sharpe 降到 {worst_us["sharpe"]:.2f}。50 太分散降到 1.70。'
        f'建议保持 30 不变。',
    )

    body += render_section("参数敏感性：Carry 权重", cw_table)
    body += render_note(
        f'<b>⚠️ 重要发现：Carry 权重越低越好。</b> 当前 0.5 对应 Sharpe 1.99，'
        f'但降到 0.2 后 Sharpe 提高到 {best_cw["sharpe"]:.2f}，收益 {fmt_pct(best_cw["return"])}。'
        f'这说明 carry 因子的独立 alpha 不如 momo/breakout，'
        f'降低 carry 权重可以减少 funding drag 而保留价格趋势 alpha。'
        f'<b>建议将 carry 权重从 0.5 降到 0.2-0.35。</b>',
        kind="warn",
    )

    body += render_section("月度表现", monthly_table)
    body += render_section("30 天滚动窗口", roll_table)
    body += render_section("回撤恢复", dd_table)

    body += render_section("稳定性综合评估", verdict_body)

    html = render_page(
        title="Rank 154 · 综合验证报告",
        subtitle="120 天回测 · 参数敏感性 · 滚动稳定性 · 回撤恢复",
        body_html=body,
        generated_at=now,
        nav_links=[
            {"href": "/momentum/paper/rank154_carry_fix_backtest.html", "label": "Carry 修正回测"},
            {"href": "/momentum/paper/rank154_overview.html", "label": "策略总览"},
            {"href": "/momentum/paper/rank154_hub.html", "label": "研究目录"},
        ],
    )
    out = write_page(SITE_PATH, html)
    print(f"[ok] {out} ({out.stat().st_size:,} bytes)")
    print(f"[url] https://jp.jerrypsy.top/momentum/paper/rank154_validation.html")


if __name__ == "__main__":
    main()
