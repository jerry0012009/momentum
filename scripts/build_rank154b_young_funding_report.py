#!/usr/bin/env python3
"""Build HTML report for rank154b young funding strict backtest."""
from __future__ import annotations

import html
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from momentum.html_render import (  # noqa: E402
    render_page, render_metric_cards, render_table, render_note, render_section,
    fmt_pct, fmt_num, fmt_usd, write_page,
)

ART = ROOT / "reports" / "artifacts" / "rank154b_young_funding_backtest"
OUT = ROOT / "reports" / "site" / "paper" / "rank154b_young_funding_backtest.html"
CORE = "154b_long_short_staggered_h5_cost20"

def pct(v, d=1):
    if pd.isna(v): return "—"
    return f"{float(v)*100:.{d}f}%"

def fnum(v, d=2):
    if pd.isna(v): return "—"
    return f"{float(v):,.{d}f}"

def money(v):
    if pd.isna(v): return "—"
    return f"${float(v):,.0f}"

def mini_svg(eq: pd.DataFrame, width=1120, height=260) -> str:
    if eq.empty:
        return '<p class="muted">No equity data.</p>'
    y = eq["equity"].astype(float).to_numpy()
    n = len(y)
    if n < 2:
        return '<p class="muted">Too few points.</p>'
    ymin, ymax = float(np.nanmin(y)), float(np.nanmax(y))
    pad = (ymax - ymin) * 0.08 if ymax > ymin else 1
    ymin -= pad; ymax += pad
    xs = np.linspace(0, width, n)
    ys = height - (y - ymin) / (ymax - ymin) * height
    # Downsample for compact HTML.
    step = max(1, n // 500)
    pts = " ".join(f"{xs[i]:.1f},{ys[i]:.1f}" for i in range(0, n, step))
    grid = "".join(f'<line x1="0" y1="{height*i/4:.1f}" x2="{width}" y2="{height*i/4:.1f}" stroke="#1f2937" />' for i in range(5))
    labels = f'<text x="8" y="18" fill="#94a3b8" font-size="12">max {ymax-pad:,.0f}</text><text x="8" y="{height-8}" fill="#94a3b8" font-size="12">min {ymin+pad:,.0f}</text>'
    return f'<svg viewBox="0 0 {width} {height}" style="width:100%;height:auto;background:#111827;border:1px solid #1f2937;border-radius:14px;padding:8px">{grid}{labels}<polyline points="{pts}" fill="none" stroke="#38bdf8" stroke-width="2" /></svg>'

def prep_stats(st: pd.DataFrame) -> pd.DataFrame:
    x = st.copy()
    x["variant"] = x["config"].str.replace("154b_", "", regex=False).str.replace("_", " ")
    return x

def main() -> None:
    st = pd.read_csv(ART / "rank154b_backtest_stats.csv")
    y = pd.read_csv(ART / "rank154b_backtest_yearly.csv")
    m = pd.read_csv(ART / "rank154b_backtest_monthly.csv")
    roll = pd.read_csv(ART / "rank154b_backtest_rolling365.csv")
    ic_sum_path = ART / "rank154b_funding_ic_summary.csv"
    sp_sum_path = ART / "rank154b_funding_spread_summary.csv"
    ic_year_path = ART / "rank154b_funding_ic_yearly.csv"
    ic_sum = pd.read_csv(ic_sum_path) if ic_sum_path.exists() else pd.DataFrame()
    sp_sum = pd.read_csv(sp_sum_path) if sp_sum_path.exists() else pd.DataFrame()
    ic_year = pd.read_csv(ic_year_path) if ic_year_path.exists() else pd.DataFrame()
    core_eq = pd.read_csv(ART / f"{CORE}_equity.csv")
    core = st[st["config"] == CORE].iloc[0]

    cards = [
        {"label": "Verdict", "value": "ARCHIVED", "subtitle": "NO-GO · no paper lane", "kind": "bad"},
        {"label": "Core total return", "value": pct(core["return"]), "subtitle": "20bps, 5d staggered", "kind": "bad"},
        {"label": "Annualized", "value": pct(core["ann_return"]), "subtitle": "2021-05-03 → 2026-04-30", "kind": "bad"},
        {"label": "Max drawdown", "value": pct(core["max_dd"]), "subtitle": "回撤过深", "kind": "bad"},
        {"label": "Sharpe", "value": fnum(core["sharpe"]), "subtitle": "统计质量不足", "kind": "warn"},
        {"label": "Avg turnover", "value": pct(core["avg_turnover"]), "subtitle": "日均换手，5d staggered 后", "kind": "warn"},
        {"label": "0 cost edge", "value": "+85.7%", "subtitle": "有 gross edge，但不够厚", "kind": "warn"},
        {"label": "20bps cost drag", "value": "-66.3%", "subtitle": "累计 turnover × cost", "kind": "bad"},
    ]

    cost = st[(st["mode"] == "long_short") & (st["rebalance"] == "staggered") & (st["age_min"] == 180) & (st["age_max"] == 365) & (st["universe_size"] == 30)].copy()
    cost = cost[["cost_bps", "return", "ann_return", "max_dd", "sharpe", "avg_turnover", "commission_return_sum"]]

    yearly = y[y["config"] == CORE][["period", "return", "max_dd", "avg_turnover", "price_return_sum", "funding_return_sum", "commission_return_sum"]].copy()
    yearly["regime_note"] = yearly["period"].astype(str).map({
        "2021": "早期正收益",
        "2022": "熊市/高换手，亏",
        "2023": "小正",
        "2024": "OOS 亏",
        "2025": "价格腿强但 funding+cost 抹平",
        "2026": "前 4 个月暴拉，结果被它救回来",
    }).fillna("")

    variant = prep_stats(st).sort_values("sharpe", ascending=False).head(12)[[
        "variant", "return", "ann_return", "max_dd", "sharpe", "avg_turnover", "price_return_sum", "funding_return_sum", "commission_return_sum"
    ]]

    rcore = roll[roll["config"] == CORE]
    rolling_summary = pd.DataFrame([{
        "windows": len(rcore),
        "positive_windows": int((rcore["return"] > 0).sum()),
        "positive_rate": (rcore["return"] > 0).mean(),
        "median_return": rcore["return"].median(),
        "min_return": rcore["return"].min(),
        "max_return": rcore["return"].max(),
        "median_sharpe": rcore["sharpe"].median(),
    }])

    train = yearly[yearly["period"].astype(str).isin(["2021", "2022", "2023"])]
    oos = yearly[yearly["period"].astype(str).isin(["2024", "2025", "2026"])]
    split = pd.DataFrame([
        {"split": "Train-ish 2021-2023", "return": np.prod(1 + train["return"]) - 1, "positive_years": f"{int((train['return']>0).sum())}/{len(train)}", "note": "基本持平，不是强训练样本"},
        {"split": "OOS-ish 2024-2026", "return": np.prod(1 + oos["return"]) - 1, "positive_years": f"{int((oos['return']>0).sum())}/{len(oos)}", "note": "2024/2025 连续亏，2026 单段救场"},
    ])

    audit = pd.DataFrame([
        {"item": "Universe", "status": "PASS", "detail": "每个交易日用 archive panel，listing_days 180-365，按当日 trailing 30d quote volume 取 Top30。"},
        {"item": "Listing age", "status": "PASS_WITH_LIMITATION", "detail": "用首次 archive daily kline 近似上市日；因果但不是官方 onboardDate。"},
        {"item": "Signal", "status": "PASS", "detail": "signal date 已结算 funding_rate_last；高 funding 做多，低 funding 做空。"},
        {"item": "Execution", "status": "PASS", "detail": "D 日 close 后调仓，吃 D→D+1 close-to-close price return 和 D+1 realized funding。"},
        {"item": "Cost", "status": "ROUGH", "detail": "按 turnover × bps 粗扣；尚未做订单簿/冲击成本模拟。"},
        {"item": "Robustness", "status": "FAIL", "detail": "20bps 核心版净收益为负；rolling 365d 仅 10/25 个窗口为正。"},
    ])

    fmt = {
        "return": lambda v: pct(v, 1), "ann_return": lambda v: pct(v, 1), "max_dd": lambda v: pct(v, 1),
        "sharpe": lambda v: fnum(v, 2), "avg_turnover": lambda v: pct(v, 1), "commission_return_sum": lambda v: pct(v, 1),
        "price_return_sum": lambda v: pct(v, 1), "funding_return_sum": lambda v: pct(v, 1), "positive_rate": lambda v: pct(v, 1),
        "median_return": lambda v: pct(v, 1), "min_return": lambda v: pct(v, 1), "max_return": lambda v: pct(v, 1), "median_sharpe": lambda v: fnum(v, 2),
        "cost_bps": lambda v: f"{float(v):.0f} bps",
        "ic_mean": lambda v: fnum(v, 4), "ic_median": lambda v: fnum(v, 4), "ic_std": lambda v: fnum(v, 4),
        "icir_daily": lambda v: fnum(v, 3), "icir_ann_sqrt365": lambda v: fnum(v, 2), "t_stat": lambda v: fnum(v, 2),
        "spread_mean": lambda v: pct(v, 2), "spread_median": lambda v: pct(v, 2), "spread_t_stat": lambda v: fnum(v, 2),
        "top_ret_mean": lambda v: pct(v, 2), "bottom_ret_mean": lambda v: pct(v, 2),
    }

    ic_core = pd.DataFrame()
    spread_core = pd.DataFrame()
    ic_year_core_5d = pd.DataFrame()
    if not ic_sum.empty:
        ic_core = ic_sum[(ic_sum["sample"] == "young_180_365_top30_core") & (ic_sum["horizon"].isin([1, 5, 10]))][[
            "horizon", "target", "days", "ic_mean", "ic_median", "icir_daily", "icir_ann_sqrt365", "t_stat", "positive_rate"
        ]].copy()
    if not sp_sum.empty:
        spread_core = sp_sum[(sp_sum["sample"] == "young_180_365_top30_core") & (sp_sum["horizon"].isin([1, 5, 10]))][[
            "horizon", "target", "spread_mean", "spread_median", "spread_t_stat", "positive_rate", "top_ret_mean", "bottom_ret_mean"
        ]].copy()
    if not ic_year.empty:
        ic_year_core_5d = ic_year[(ic_year["sample"] == "young_180_365_top30_core") & (ic_year["horizon"] == 5)][[
            "year", "target", "days", "ic_mean", "icir_daily", "positive_rate"
        ]].copy()

    body = ""
    body += render_metric_cards(cards)
    body += render_note("<b>最终收口：</b>154b 已归档为 research lead only，不进入 paper lane。它的经济故事（young coin 的 funding crowding/attention continuation）有一点 gross price edge，但在 funding 支付和 20bps turnover 成本下已经变成负净 alpha；2024/2025 OOS 连亏，2026 前四个月的暴拉把总曲线救回接近零。这不是可以继续调参推进的 release candidate。", kind="bad")
    body += render_section("1. 策略定义", """
<ul>
<li><b>Universe：</b>Binance USDT perp archive panel，按每个日期过滤上市年龄 <code>180-365d</code>，再取当日 30d trailing quote volume Top30。</li>
<li><b>Alpha 因子：</b><code>carry_raw = funding_rate_last</code>。154b 当前只关注这一个核心 alpha 因子；没有 momentum、breakout、volume quality 等第二因子参与打分。</li>
<li><b>Signal：</b>高 funding 做多、低 funding 做空。这个方向测试的是 young coin 的注意力/拥挤延续，而不是收 funding carry。</li>
<li><b>Portfolio：</b>高 funding 前 20% 做多，低 funding 后 20% 做空；核心版 5-day staggered，每天开 1/5 sleeve，目标 gross 约 65%。</li>
<li><b>PnL：</b>close-to-close price return + realized next-day funding；正 funding 下，long 付费、short 收费。</li>
<li><b>Cost：</b>核心版按 20bps × turnover 粗扣，另跑 0/10/20/30/50bps 敏感性。</li>
</ul>
""")
    if not ic_core.empty:
        body += render_section("1b. Funding 单因子 IC / ICIR", render_table(ic_core, columns=list(ic_core.columns), col_formats=fmt, col_positive_good=["ic_mean", "icir_daily", "icir_ann_sqrt365", "t_stat", "positive_rate"]))
        body += render_note("<b>解释：</b><code>price</code> target 只看未来价格；<code>long_total</code> target = 未来价格收益 - 未来 funding 成本，代表高 funding 做多后真正拿到的方向收益。154b 的 price IC 为正，但 long_total IC 转负，说明价格延续信号被 funding 成本抵消。", kind="warn")
    if not spread_core.empty:
        body += render_section("1c. Top 20% vs Bottom 20% spread", render_table(spread_core, columns=list(spread_core.columns), col_formats=fmt, col_positive_good=["spread_mean", "spread_median", "spread_t_stat", "positive_rate", "top_ret_mean", "bottom_ret_mean"]))
    if not ic_year_core_5d.empty:
        body += render_section("1d. 5d IC 年度稳定性", render_table(ic_year_core_5d, columns=list(ic_year_core_5d.columns), col_formats=fmt, col_positive_good=["ic_mean", "icir_daily", "positive_rate"]))
        body += render_note("5d price IC 的主要强度来自 2026：2024/2025 的 price IC 分别只有约 0.0046 / 0.0010；long_total 在 2024/2025 为负。这进一步支持“regime burst，不是稳定可交易 alpha”的收口。", kind="bad")
    body += render_section("2. Core equity curve", mini_svg(core_eq))
    body += render_section("3. 成本敏感性：edge 不够厚", render_table(cost, columns=list(cost.columns), col_formats=fmt, col_positive_good=["return", "ann_return", "sharpe", "commission_return_sum"]))
    body += render_note("0 cost 下总收益 +85.7%，10bps 下 +33.3%，20bps 下变成 -4.3%。这说明问题不是完全没有信号，而是 gross edge 太薄，无法覆盖真实执行成本。", kind="warn")
    body += render_section("4. 年度拆解：OOS 不稳，2026 单段救场", render_table(yearly, columns=list(yearly.columns), col_formats=fmt, col_positive_good=["return", "price_return_sum", "funding_return_sum", "commission_return_sum"]))
    body += render_section("5. Train / OOS 粗拆", render_table(split, columns=list(split.columns), col_formats=fmt, col_positive_good=["return"]))
    body += render_section("6. Rolling 365d 稳定性", render_table(rolling_summary, columns=list(rolling_summary.columns), col_formats=fmt, col_positive_good=["positive_rate", "median_return", "min_return", "max_return", "median_sharpe"]))
    body += render_note("Rolling 365d 只有 10/25 个窗口为正，中位窗口收益 -11.0%，最差窗口 -49.7%。这不是“稳定小 edge”，更像 regime-dependent burst。", kind="bad")
    body += render_section("7. 变体对照", render_table(variant, columns=list(variant.columns), col_formats=fmt, col_positive_good=["return", "ann_return", "sharpe", "price_return_sum", "funding_return_sum", "commission_return_sum"]))
    body += render_note("Top50 版本在 20bps 下为正（+23.6%），但这更像降低波动/特定样本改善，不足以改变结论；需要单独做 IC、事件归因和近期 paper shadow 才能考虑作为下一条线索。", kind="warn")
    body += render_section("8. Causality / honesty audit", render_table(audit, columns=list(audit.columns)))
    body += render_section("9. Archive rule / 产物", f"""
<p><b>Archive rule:</b> 不要用 TopN / holding period / sleeve fraction 继续救 154b。任何 future funding-age work 必须新建 rank/name，并先声明 regime、after-funding target 与真实成本口径。</p>
<ul>
<li><code>scripts/backtest_rank154b_young_funding.py</code></li>
<li><code>reports/artifacts/rank154b_young_funding_backtest/rank154b_backtest_stats.csv</code></li>
<li><code>reports/artifacts/rank154b_young_funding_backtest/rank154b_backtest_yearly.csv</code></li>
<li><code>reports/artifacts/rank154b_young_funding_backtest/rank154b_backtest_rolling365.csv</code></li>
<li><code>reports/artifacts/rank154b_young_funding_backtest/{html.escape(CORE)}_equity.csv</code></li>
</ul>
""")

    html_out = render_page(
        "Rank154b young funding 归档审计",
        body,
        subtitle="180-365d young coin · funding crowding continuation · daily vs 5d staggered · cost sensitivity",
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        nav_links=[{"label": "Rank154 Hub", "href": "rank154_hub.html"}],
    )
    write_page(OUT, html_out)
    print(OUT)

if __name__ == "__main__":
    main()
