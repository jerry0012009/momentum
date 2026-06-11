#!/usr/bin/env python3
"""Build Rank 154 / Crypto-Stat-Arb strategy overview page.

Reads paper runner artifacts + strategy source to generate a comprehensive
overview page: strategy logic, paper performance, current positions,
and research history.

Usage:
    python scripts/build_rank154_overview.py
    python scripts/build_rank154_overview.py --open  # open in browser after build
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.html_render import (
    PAGE_CSS_DARK,
    fmt_int,
    fmt_num,
    fmt_pct,
    fmt_usd,
    fmt_x,
    read_artifact_csv,
    read_artifact_json,
    render_metric_cards,
    render_note,
    render_page,
    render_section,
    render_table,
    write_page,
)

# --- Paths ---
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank154_crypto_stat_arb_runner"
SITE_PATH = ROOT / "reports" / "site" / "paper" / "rank154_overview.html"

EQUITY_PATH = ART_DIR / "rank154_paper_equity_curve.csv"
STATE_PATH = ART_DIR / "rank154_paper_state.json"
STATUS_PATH = ART_DIR / "rank154_paper_status.csv"
POSITIONS_PATH = ART_DIR / "rank154_paper_open_positions.csv"
TRADES_PATH = ART_DIR / "rank154_paper_rebalance_trades.csv"


def compute_equity_stats(eq: pd.DataFrame) -> dict:
    """Compute summary statistics from equity curve."""
    if eq.empty:
        return {}

    eq = eq.sort_values("signal_date_utc").reset_index(drop=True)
    n = len(eq)
    first_eq = eq["equity_after_rebalance_usd"].iloc[0]
    last_eq = eq["equity_after_rebalance_usd"].iloc[-1]
    peak = eq["running_max_equity_usd"].max()
    max_dd = eq["drawdown"].min()

    # Daily returns
    eq["daily_return"] = eq["equity_after_rebalance_usd"].pct_change()
    daily_rets = eq["daily_return"].dropna()
    win_rate = (daily_rets > 0).mean()
    avg_daily = daily_rets.mean()
    std_daily = daily_rets.std()
    sharpe = (avg_daily / std_daily * np.sqrt(365)) if std_daily > 0 else 0

    best_day_idx = daily_rets.idxmax()
    worst_day_idx = daily_rets.idxmin()

    total_funding = eq["funding_pnl_usd"].sum()
    total_commission = eq["commission_usd"].sum()
    total_price_pnl = eq["price_pnl_usd"].sum()
    avg_turnover = eq["turnover"].mean()

    return {
        "n_days": n,
        "first_equity": first_eq,
        "last_equity": last_eq,
        "total_return": (last_eq / first_eq) - 1,
        "peak_equity": peak,
        "max_drawdown": max_dd,
        "sharpe": sharpe,
        "win_rate": win_rate,
        "avg_daily_return": avg_daily,
        "best_day_return": daily_rets.iloc[best_day_idx - daily_rets.index[0]] if best_day_idx in daily_rets.index else daily_rets.max(),
        "best_day_date": eq.loc[best_day_idx, "signal_date_utc"] if best_day_idx in eq.index else "—",
        "worst_day_return": daily_rets.iloc[worst_day_idx - daily_rets.index[0]] if worst_day_idx in daily_rets.index else daily_rets.min(),
        "worst_day_date": eq.loc[worst_day_idx, "signal_date_utc"] if worst_day_idx in eq.index else "—",
        "total_funding": total_funding,
        "total_commission": total_commission,
        "total_price_pnl": total_price_pnl,
        "avg_turnover": avg_turnover,
        "start_date": eq["signal_date_utc"].iloc[0],
        "end_date": eq["signal_date_utc"].iloc[-1],
    }


def build_hero_section(stats: dict) -> str:
    """Build the top metric cards."""
    dd_kind = "good" if stats["max_drawdown"] > -0.10 else ("warn" if stats["max_drawdown"] > -0.20 else "bad")
    ret_kind = "good" if stats["total_return"] > 0 else "bad"

    cards = [
        {"label": "Paper Return", "value": fmt_pct(stats["total_return"]), "subtitle": f'{stats["start_date"][:10]} → {stats["end_date"][:10]} ({stats["n_days"]}d)', "kind": ret_kind},
        {"label": "Current Equity", "value": fmt_usd(stats["last_equity"]), "subtitle": f'Peak: {fmt_usd(stats["peak_equity"])}'},
        {"label": "Max Drawdown", "value": fmt_pct(stats["max_drawdown"]), "subtitle": "from peak equity", "kind": dd_kind},
        {"label": "Daily Sharpe (ann.)", "value": fmt_num(stats["sharpe"]), "subtitle": f'Avg daily: {fmt_pct(stats["avg_daily_return"])}'},
        {"label": "Win Rate", "value": fmt_pct(stats["win_rate"]), "subtitle": f'{int(stats["win_rate"] * stats["n_days"])}W / {stats["n_days"] - int(stats["win_rate"] * stats["n_days"])}L'},
        {"label": "Avg Turnover", "value": fmt_x(stats["avg_turnover"]), "subtitle": f'Funding: {fmt_usd(stats["total_funding"])} total'},
    ]
    return render_metric_cards(cards)


def build_architecture_section() -> str:
    """Build the strategy architecture explanation with full audit."""
    html = """
<div class="card">
<h3>Signal Formula — 三因子复合评分</h3>
<p>策略在 Top30 universe 内对三个因子分别做 centered decile 排名，加权合成后归一化为持仓权重。</p>

<h3 style="color:#7dd3fc; margin-top:24px;">Factor 1: Carry（权重 50%）</h3>
<table>
<tr><th>项目</th><th>定义</th></tr>
<tr><td><b>原始值</b></td><td><code>carry_raw = funding_rate_last (最后一笔结算率)</code></td></tr>
<tr><td><b>数据来源</b></td><td>Binance <code>fapi/v1/fundingRate</code> API</td></tr>
<tr><td><b>聚合方式</b></td><td>日频取最后一笔结算率（非求和，避免 4h/8h interval 偏差）</td></tr>
<tr><td><b>符号约定</b></td><td>正值 = 多头付空头（longs pay shorts）；负值 = 空头付多头（shorts pay longs）</td></tr>
<tr><td><b>排名方向</b></td><td>值越大 → decile 越高 → <b>做多</b></td></tr>
<tr><td><b>实际效果</b></td><td>carry D10（最高正 funding）→ 做多；carry D1（最低/负 funding）→ 做空</td></tr>
</table>
""" + render_note(
    "<b>⚠️ 审计发现：这不是传统 carry trade。</b> 传统 carry 是「做空高 funding 收钱、做多低 funding 收钱」。这个策略是<b>反过来的</b>——它把高 funding 当作「市场看多情绪拥挤」的信号，做多高 funding 币、做空低 funding 币。本质上是<b>情绪/拥挤度因子</b>，不是收益因子。实际 PnL 中，funding 部分长期为负（做多的币在付 funding），说明 carry 因子的贡献主要来自价格方向而非 funding 收入。",
    kind="warn",
) + """

<h3 style="color:#7dd3fc; margin-top:24px;">Factor 2: Momentum（权重 20%）</h3>
<table>
<tr><th>项目</th><th>定义</th></tr>
<tr><td><b>原始值</b></td><td><code>momo_10d = close.pct_change(10)</code></td></tr>
<tr><td><b>计算时刻</b></td><td>用<b>已完成的日线 close 价</b>（decision_ts 时刻的 t-1 日收盘价）</td></tr>
<tr><td><b>含义</b></td><td>过去 10 个交易日的累计收益率</td></tr>
<tr><td><b>排名方向</b></td><td>值越大 → decile 越高 → <b>做多</b></td></tr>
<tr><td><b>实际效果</b></td><td>momo D10（过去 10 天涨最多）→ 做多；momo D1（过去 10 天跌最多）→ 做空</td></tr>
</table>
""" + render_note(
    "经典横截面动量因子。逻辑：强者恒强、弱者恒弱。在 crypto 中，短期动量效应比传统市场更强（散户追涨杀跌）。",
    kind="good",
) + """

<h3 style="color:#7dd3fc; margin-top:24px;">Factor 3: Breakout（权重 30%）</h3>
<table>
<tr><th>项目</th><th>定义</th></tr>
<tr><td><b>原始值</b></td><td><code>breakout_raw = 19.0 - days_since_20d_high</code></td></tr>
<tr><td><b>days_since_20d_high</b></td><td>当前 close 在过去 20 根日线中，距离最高价的天数（0 = 今天就是最高价）</td></tr>
<tr><td><b>值域</b></td><td>0 到 19（19 = 刚创新高，0 = 20 天前是最高价）</td></tr>
<tr><td><b>排名方向</b></td><td>值越大 → decile 越高 → <b>做多</b></td></tr>
<tr><td><b>实际效果</b></td><td>breakout D10（刚创新高）→ 做多；breakout D1（远离高点）→ 做空</td></tr>
</table>
""" + render_note(
    "突破接近度因子。逻辑：刚创新高的币更可能继续上涨（趋势延续），远离高点的币更可能继续下跌。与 momentum 高度相关但不完全相同——breakout 关注的是「离高点有多近」，momentum 关注的是「涨了多少」。",
    kind="good",
) + """

<h3 style="margin-top:24px;">合成公式</h3>
<div style="background:#0f172a; padding:16px; border-radius:10px; margin:12px 0; font-family:monospace; font-size:14px; line-height:2;">
  <div><span style="color:#94a3b8">// Step 1: 每个因子在 universe 内做 centered decile 排名</span></div>
  <div><span style="color:#7dd3fc">carry_centered</span> = decile_rank(carry_raw) - mean(deciles)</div>
  <div><span style="color:#7dd3fc">momo_centered</span> = decile_rank(momo_10d) - mean(deciles)</div>
  <div><span style="color:#7dd3fc">breakout_centered</span> = decile_rank(breakout_raw) - mean(deciles)</div>
  <div style="margin-top:8px"><span style="color:#94a3b8">// Step 2: 加权合成</span></div>
  <div><span style="color:#fbbf24">score</span> = 0.5 × carry_centered + 0.2 × momo_centered + 0.3 × breakout_centered</div>
  <div style="margin-top:8px"><span style="color:#94a3b8">// Step 3: 归一化为权重</span></div>
  <div>weight = score / Σ|score|</div>
  <div>weight = clip(weight, -10%, +10%)</div>
  <div>if |weight| < 0.5%: weight = 0</div>
</div>

<h3 style="margin-top:24px;">Decile 含义速查</h3>
<table>
<tr><th>Decile</th><th>Carry 含义</th><th>Momo 含义</th><th>Breakout 含义</th><th>→ 方向</th></tr>
<tr><td><b>D10</b></td><td>最高正 funding（多头拥挤）</td><td>过去 10 天涨幅最大</td><td>今天就是 20 日新高</td><td style="color:#4ade80"><b>做多</b></td></tr>
<tr><td><b>D9</b></td><td>次高 funding</td><td>次高涨幅</td><td>昨天是新高</td><td style="color:#4ade80"><b>做多</b></td></tr>
<tr><td>...</td><td>...</td><td>...</td><td>...</td><td>...</td></tr>
<tr><td><b>D2</b></td><td>次低 funding</td><td>次低涨幅</td><td>远离高点</td><td style="color:#f87171"><b>做空</b></td></tr>
<tr><td><b>D1</b></td><td>最低/负 funding（空头拥挤）</td><td>过去 10 天跌幅最大</td><td>最远离高点</td><td style="color:#f87171"><b>做空</b></td></tr>
</table>

<h3 style="margin-top:24px;">实战举例（2026-05-08 信号）</h3>
<table>
<tr><th>币</th><th>Carry</th><th>Momo</th><th>Breakout</th><th>主因</th><th>权重</th></tr>
<tr><td>LABUSDT</td><td>D10（最高 funding）</td><td>D10（涨最多）</td><td>D6</td><td>carry</td><td style="color:#4ade80">+5.77%</td></tr>
<tr><td>ETHUSDT</td><td>D2（低 funding）</td><td>D2（跌很多）</td><td>D1（远离高点）</td><td>carry</td><td style="color:#f87171">-6.64%</td></tr>
<tr><td>ORCAUSDT</td><td>D1（最低 funding）</td><td>D2</td><td>D3</td><td>carry</td><td style="color:#f87171">-6.47%</td></tr>
</table>
""" + render_note(
    "<b>读法</b>：三个因子方向一致时权重最大（如 LABUSDT 三个都高 → +5.77%）。方向矛盾时互相抵消。Carry 权重 50% 所以「主因=carry」最常见。",
) + """
</div>

<div class="card">
<h3>Universe 构造</h3>
<ul>
  <li><b>池子</b>：Binance USDT-M 永续合约，按 30 日滚动成交额排名取 Top 30</li>
  <li><b>Guard</b>：过滤稳定币 base（USDT/USDC/BUSD 等）、上市不足 180 天的币</li>
  <li><b>更新频率</b>：每天 UTC 00:20 用已完成的日线数据重建</li>
  <li><b>信号数据</b>：全部使用已完成的日线（无 look-ahead），funding 取当日已发生的结算</li>
</ul>
</div>

<div class="card">
<h3>执行规则</h3>
<ul>
  <li><b>频率</b>：日频 rebalance（每天 UTC 00:20）</li>
  <li><b>信号 → 执行</b>：t 日 UTC 00:00 的已完成数据 → t 日 UTC 00:20 生成信号 → 按 close 价执行（next-bar）</li>
  <li><b>权重 buffer</b>：1% deadzone — 如果新权重与旧权重差 < 1%，不换仓</li>
  <li><b>单币上限</b>：±10% 权重</li>
  <li><b>成本假设</b>：5 bps/side（paper runner 中的估算）</li>
  <li><b>组合特征</b>：dollar-neutral（净暴露 ~0%，多空各约 50%）</li>
</ul>
</div>
"""
    return html


def build_backtest_section() -> str:
    """Build the backtest / honesty audit section."""
    html = """
<div class="card">
<h3>回测诚实性审计（2026-03-24）</h3>
<p>基于公开 repo <code>ryanczm/Crypto-Stat-Arb</code> 的回测数据，在不同执行假设下的表现：</p>
""" + render_table(
        pd.DataFrame({
            "scenario": [
                "Same-day execution（乐观）",
                "+1 day lag（诚实）",
                "+1 day lag + lagged funding",
                "No funding（纯价格）",
                "20bps cost（高摩擦）",
                "Buffer=0%（无 deadzone）",
                "Buffer=10%（过窄）",
            ],
            "cagr": [0.455, 0.422, 0.428, 0.342, 0.391, 0.257, 0.044],
            "sharpe": [1.32, 1.26, 1.27, 1.08, 1.19, 0.73, 0.35],
            "mdd": [-0.33, -0.285, -0.285, None, None, None, None],
        }),
        columns=["scenario", "cagr", "sharpe", "mdd"],
        col_labels={"scenario": "场景", "cagr": "CAGR", "sharpe": "Sharpe", "mdd": "Max DD"},
        col_formats={"cagr": fmt_pct, "sharpe": lambda v: f"{v:.2f}", "mdd": fmt_pct},
        col_positive_good=["cagr", "sharpe"],
    ) + render_note(
        "核心结论：把同日 close 执行修正为 1 日滞后后，CAGR 从 45.5% 降到 42.2%，Sharpe 从 1.32 降到 1.26。<b>策略 survive 不是靠同 bar fill 幻觉</b>。但对 trade buffer 敏感（0% → 61.9% 换手 → Sharpe 0.73）。",
        kind="good",
    ) + """
</div>
"""
    return html


def build_performance_section(eq: pd.DataFrame, stats: dict) -> str:
    """Build the paper performance section with equity curve table."""
    if eq.empty:
        return '<div class="card"><p class="muted">No equity data available.</p></div>'

    # Monthly aggregation
    eq_copy = eq.copy()
    eq_copy["month"] = eq_copy["signal_date_utc"].str[:7]
    monthly = eq_copy.groupby("month").agg(
        start_eq=("equity_after_rebalance_usd", "first"),
        end_eq=("equity_after_rebalance_usd", "last"),
        total_pnl=("price_pnl_usd", "sum"),
        total_funding=("funding_pnl_usd", "sum"),
        total_commission=("commission_usd", "sum"),
        max_dd=("drawdown", "min"),
        days=("signal_date_utc", "count"),
    ).reset_index()
    monthly["return"] = (monthly["end_eq"] / monthly["start_eq"]) - 1

    monthly_table = render_table(
        monthly,
        columns=["month", "return", "total_pnl", "total_funding", "total_commission", "max_dd", "days"],
        col_labels={
            "month": "月份", "return": "月收益", "total_pnl": "价格 PnL",
            "total_funding": "Funding PnL", "total_commission": "手续费",
            "max_dd": "月内回撤", "days": "天数",
        },
        col_formats={
            "return": fmt_pct, "total_pnl": fmt_usd, "total_funding": fmt_usd,
            "total_commission": fmt_usd, "max_dd": fmt_pct,
        },
        col_positive_good=["return", "total_pnl"],
    )

    # Recent daily equity (last 15 days)
    recent = eq.tail(15).copy()
    recent_table = render_table(
        recent,
        columns=["signal_date_utc", "equity_after_rebalance_usd", "price_pnl_usd", "funding_pnl_usd", "turnover", "drawdown", "top_long", "top_short"],
        col_labels={
            "signal_date_utc": "日期", "equity_after_rebalance_usd": "权益",
            "price_pnl_usd": "价格 PnL", "funding_pnl_usd": "Funding",
            "turnover": "换手", "drawdown": "回撤", "top_long": "Top Long", "top_short": "Top Short",
        },
        col_formats={
            "equity_after_rebalance_usd": fmt_usd, "price_pnl_usd": fmt_usd,
            "funding_pnl_usd": fmt_usd, "turnover": fmt_pct, "drawdown": fmt_pct,
        },
        col_positive_good=["price_pnl_usd"],
    )

    return f"""
<div class="card">
<h3>月度表现</h3>
{monthly_table}
</div>

<div class="card">
<h3>近期每日权益</h3>
{recent_table}
</div>
"""


def build_positions_section(state: dict) -> str:
    """Build the current positions section."""
    positions = state.get("positions", {})
    if not positions:
        return ""

    rows = []
    for sym, pos in sorted(positions.items(), key=lambda x: abs(x[1].get("weight", 0)), reverse=True):
        rows.append({
            "symbol": sym,
            "side": "long" if pos.get("weight", 0) > 0 else "short",
            "weight": pos.get("weight", 0),
            "entry_price": pos.get("entry_price", 0),
            "reason": pos.get("decision_reason", ""),
        })

    df = pd.DataFrame(rows)

    def side_tag(s):
        if s == "long":
            return '<span class="tag tag-long">LONG</span>'
        return '<span class="tag tag-short">SHORT</span>'

    # Build table manually for side tags
    header = "<tr><th>Symbol</th><th>Side</th><th>Weight</th><th>Entry</th><th>Reason</th></tr>"
    body_rows = []
    for _, r in df.iterrows():
        body_rows.append(
            f'<tr><td>{r["symbol"]}</td>'
            f'<td>{side_tag(r["side"])}</td>'
            f'<td class="num">{fmt_pct(r["weight"])}</td>'
            f'<td class="num">{fmt_usd(r["entry_price"])}</td>'
            f'<td style="font-size:12px">{r["reason"]}</td></tr>'
        )

    long_count = sum(1 for r in rows if r["side"] == "long")
    short_count = sum(1 for r in rows if r["side"] == "short")

    summary_cards = render_metric_cards([
        {"label": "Total Positions", "value": str(len(rows))},
        {"label": "Long / Short", "value": f"{long_count} / {short_count}"},
        {"label": "Gross Exposure", "value": fmt_pct(sum(abs(r["weight"]) for r in rows))},
        {"label": "Net Exposure", "value": fmt_pct(sum(r["weight"] for r in rows))},
    ])

    return f"""
<div class="card">
<h3>当前持仓</h3>
{summary_cards}
<table><thead>{header}</thead><tbody>{"".join(body_rows)}</tbody></table>
</div>
"""


def build_research_section() -> str:
    """Build the research history / links section."""
    html = """
<div class="card">
<h3>研发历程</h3>
<table>
<thead><tr><th>阶段</th><th>时间</th><th>结论</th><th>链接</th></tr></thead>
<tbody>
<tr>
  <td>Fresh Intake</td><td>2026-03-24</td>
  <td>从 <code>ryanczm/Crypto-Stat-Arb</code> repo intake，carry+momo+breakout 三因子骨架可复现</td>
  <td><a href="/momentum/reading/quant_digests/2026-03-24_0922_crypto-stat-arb-carry-momo-breakout-intake.html">Digest</a></td>
</tr>
<tr>
  <td>P2 Admission</td><td>2026-03-24</td>
  <td>1 日滞后执行后 CAGR 42.2% / Sharpe 1.26，survive 同 bar 幻觉；依赖 ~5% trade buffer</td>
  <td><a href="/momentum/reading/quant_digests/2026-03-24_0922_crypto-stat-arb-carry-momo-breakout-intake.html">Admission</a></td>
</tr>
<tr>
  <td>P3 Handoff</td><td>2026-03-24</td>
  <td>refresh-only paper queue 实现完成，scheduler 接线</td>
  <td>—</td>
</tr>
<tr>
  <td>Paper Runner</td><td>2026-03-25 → now</td>
  <td>日频 forward paper 自动运行，45 天 +17.18%，最大回撤 -17.07%</td>
  <td><a href="/momentum/factors/paper_rank154_crypto_stat_arb_runner/report.html">Live Report</a></td>
</tr>
</tbody>
</table>
</div>

<div class="card">
<h3>Release Gate 状态</h3>
""" + render_note(
        "<b>当前状态：尚未通过 formal release gate。</b> 主要 blocker：(1) forward paper 历史不足 60 天；(2) 缺少 tiny-live runner 实现；(3) 缺少 exchange precision 检查和 live-vs-shadow 对账。Config 中 mode=<code>reject_before_live</code>。",
        kind="warn",
    ) + """
</div>
"""
    return html


def build_artifacts_section() -> str:
    """Build the artifacts reference section."""
    return """
<div class="card">
<h3>相关产物</h3>
<table>
<thead><tr><th>产物</th><th>路径</th></tr></thead>
<tbody>
<tr><td>策略源码</td><td><code>src/momentum/strategies/rank154_crypto_stat_arb.py</code></td></tr>
<tr><td>Paper Runner</td><td><code>scripts/run_rank154_crypto_stat_arb_paper_runner.py</code></td></tr>
<tr><td>Live Config</td><td><code>config/strategies/rank154_crypto_stat_arb_tiny_live.yaml</code></td></tr>
<tr><td>Release Gate</td><td><code>scripts/build_rank154_final_release_gate.py</code></td></tr>
<tr><td>Equity Curve</td><td><code>reports/artifacts/paper_rank154_crypto_stat_arb_runner/rank154_paper_equity_curve.csv</code></td></tr>
<tr><td>Paper State</td><td><code>reports/artifacts/paper_rank154_crypto_stat_arb_runner/rank154_paper_state.json</code></td></tr>
</tbody>
</table>
</div>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Rank 154 overview page")
    parser.add_argument("--open", action="store_true", help="Open in browser after build")
    args = parser.parse_args()

    # Load data
    eq = read_artifact_csv(EQUITY_PATH)
    state = read_artifact_json(STATE_PATH)

    # Compute stats
    stats = compute_equity_stats(eq)

    # Build sections
    sections = []
    sections.append(build_hero_section(stats))
    sections.append(render_section("策略架构", build_architecture_section()))
    sections.append(render_section("回测与诚实性审计", build_backtest_section()))
    if stats:
        sections.append(render_section("Paper Trade 表现", build_performance_section(eq, stats)))
    if state.get("positions"):
        sections.append(render_section("当前持仓", build_positions_section(state)))
    sections.append(render_section("研发历史与 Release Gate", build_research_section()))
    sections.append(render_section("相关产物", build_artifacts_section()))

    body = "\n\n".join(sections)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    html = render_page(
        title="Rank 154 · Crypto-Stat-Arb · 策略总览",
        subtitle="日频横截面 carry+momo+breakout 多空组合 · Binance USDT-M Perpetuals",
        body_html=body,
        generated_at=now,
        nav_links=[
            {"href": "/momentum/factors/paper_rank154_crypto_stat_arb_runner/report.html", "label": "Live Paper Report"},
            {"href": "/momentum/reading/quant_digests/2026-03-24_0922_crypto-stat-arb-carry-momo-breakout-intake.html", "label": "Intake Digest"},
            {"href": "/momentum/paper/rank213c_architecture.html", "label": "Rank 213c 对比"},
        ],
    )

    out = write_page(SITE_PATH, html)
    print(f"[ok] wrote {out} ({out.stat().st_size:,} bytes)")
    print(f"[url] https://jp.jerrypsy.top/momentum/paper/rank154_overview.html")

    if args.open:
        import webbrowser
        webbrowser.open(str(out))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
