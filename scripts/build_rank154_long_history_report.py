#!/usr/bin/env python3
"""Build Rank154 long-history validation report."""
from __future__ import annotations

import json
import sys
from html import escape
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from momentum.html_render import fmt_pct, fmt_num, fmt_usd, render_metric_cards, render_note, render_page, render_section, render_table, write_page

ART_DIR = ROOT / "reports" / "artifacts" / "rank154_long_history"
SITE_PATH = ROOT / "reports" / "site" / "paper" / "rank154_long_history.html"


def line_svg(eq: pd.DataFrame, width=1100, height=280) -> str:
    if eq.empty:
        return ""
    vals = eq["equity"].astype(float).to_numpy()
    dds = eq["drawdown"].astype(float).to_numpy()
    n = len(vals)
    def pts(arr, lo=None, hi=None):
        lo = float(arr.min()) if lo is None else lo
        hi = float(arr.max()) if hi is None else hi
        if hi == lo: hi = lo + 1
        out=[]
        for i,v in enumerate(arr):
            x = i/(n-1)*(width-40)+20
            y = height-30 - (float(v)-lo)/(hi-lo)*(height-55)
            out.append(f"{x:.1f},{y:.1f}")
        return " ".join(out)
    eq_pts = pts(vals)
    # drawdown scaled from min to 0 and placed behind
    dd_pts = pts(dds, lo=float(dds.min()), hi=0.0)
    return f"""
<div class="card">
<svg viewBox="0 0 {width} {height}" style="width:100%;height:auto" role="img" aria-label="equity curve">
  <rect x="0" y="0" width="{width}" height="{height}" fill="#111827"/>
  <line x1="20" y1="{height-30}" x2="{width-20}" y2="{height-30}" stroke="#334155"/>
  <polyline points="{dd_pts}" fill="none" stroke="#ef4444" stroke-width="1.2" opacity="0.55"/>
  <polyline points="{eq_pts}" fill="none" stroke="#38bdf8" stroke-width="2"/>
  <text x="24" y="24" fill="#94a3b8" font-size="13">Equity 蓝线；Drawdown 红线（独立缩放）</text>
  <text x="24" y="{height-8}" fill="#64748b" font-size="12">{escape(str(eq['date'].iloc[0]))}</text>
  <text x="{width-110}" y="{height-8}" fill="#64748b" font-size="12">{escape(str(eq['date'].iloc[-1]))}</text>
</svg>
</div>
"""


def subset_table(df, cols, labels=None, n=None):
    if n:
        df = df.head(n)
    return render_table(df, columns=cols, col_labels=labels or {}, col_formats={
        "return": fmt_pct, "ann_return": fmt_pct, "max_dd": fmt_pct, "win_rate": fmt_pct,
        "positive_rate": fmt_pct, "avg_turnover": fmt_num, "sharpe": fmt_num,
    }, col_positive_good=["return", "ann_return", "sharpe"])


def main():
    r = json.loads((ART_DIR / "long_history_results.json").read_text())
    eq = pd.read_csv(ART_DIR / "baseline_equity.csv")
    params = pd.read_csv(ART_DIR / "param_sweep.csv")
    yearly = pd.read_csv(ART_DIR / "yearly_isolated.csv")
    roll180 = pd.read_csv(ART_DIR / "rolling_180d.csv")
    roll365 = pd.read_csv(ART_DIR / "rolling_365d.csv")
    b = r["baseline"]
    m = r["data_manifest"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    month_vals = list(r["monthly"].values())
    pos_months = sum(x > 0 for x in month_vals)
    total_months = len(month_vals)
    roll180_pos = (roll180["return"] > 0).mean()
    roll365_pos = (roll365["return"] > 0).mean()

    hero = render_metric_cards([
        {"label":"Long-history return", "value":fmt_pct(b["return"]), "subtitle":f"{b['start']} → {b['end']} / {b['days']} days", "kind":"bad"},
        {"label":"Annualized", "value":fmt_pct(b["ann_return"]), "subtitle":"5 bps per-side cost", "kind":"bad"},
        {"label":"Max drawdown", "value":fmt_pct(b["max_dd"]), "subtitle":"deep enough to reject", "kind":"bad"},
        {"label":"Sharpe", "value":fmt_num(b["sharpe"]), "subtitle":f"win rate {fmt_pct(b['win_rate'])}", "kind":"bad"},
        {"label":"Monthly positive", "value":f"{pos_months}/{total_months}", "subtitle":fmt_pct(pos_months/total_months), "kind":"warn"},
        {"label":"365d rolling positive", "value":f"{(roll365['return']>0).sum()}/{len(roll365)}", "subtitle":fmt_pct(roll365_pos), "kind":"bad"},
    ])

    data_note = render_note(
        f"数据源是 Binance public data archive：{m['symbols']} 个 USDT plain symbols，"
        f"{m['kline_files']:,} 个月度 kline 文件、{m['funding_files']:,} 个 funding 文件，"
        f"共 {m['rows']:,} 行日频 panel。Universe 每天用当时的 30d trailing quote_volume 排 TopN，"
        f"没有用今天的 24h ticker 排名去筛过去。月度归档当前覆盖到 {m['date_max']}，所以本轮长历史主报告截至 2026-04-30。",
        kind="good",
    )

    verdict = render_note(
        "<b>结论：严格长历史下，rank154 当前形态不能进入 release。</b> "
        "它在 2025-2026 局部窗口确实能赚钱，但拉到 2021-2026 后，0 成本仍为负，"
        "5 bps per-side 后累计 -50.45%，最大回撤 -66.55%。这不是“参数微调一下”的问题，"
        "而是 alpha 来源没有跨 regime 稳定成立。",
        kind="bad",
    )

    cost_tbl = subset_table(params[params.param=="cost_bps"], ["value","return","ann_return","max_dd","sharpe","avg_turnover"], {"value":"Cost bps/side", "return":"累计", "ann_return":"年化", "max_dd":"最大回撤", "sharpe":"Sharpe", "avg_turnover":"日均换手"})
    uni_tbl = subset_table(params[params.param=="universe_size"], ["value","return","ann_return","max_dd","sharpe","median_positions"], {"value":"Universe", "return":"累计", "ann_return":"年化", "max_dd":"最大回撤", "sharpe":"Sharpe", "median_positions":"中位持仓数"})
    cw_tbl = subset_table(params[params.param=="carry_weight"], ["value","breakout_weight","return","ann_return","max_dd","sharpe","avg_turnover"], {"value":"Carry", "breakout_weight":"Breakout", "return":"累计", "ann_return":"年化", "max_dd":"最大回撤", "sharpe":"Sharpe", "avg_turnover":"日均换手"})
    yearly_tbl = subset_table(yearly, ["year","return","ann_return","max_dd","sharpe","commission","avg_turnover"], {"year":"年份", "return":"累计", "ann_return":"年化", "max_dd":"最大回撤", "sharpe":"Sharpe", "commission":"手续费$", "avg_turnover":"日均换手"})

    roll180_summary = pd.DataFrame([{
        "window":"180d", "count":len(roll180), "positive_rate":roll180_pos, "median_return":roll180["return"].median(), "min_return":roll180["return"].min(), "max_return":roll180["return"].max()
    }, {"window":"365d", "count":len(roll365), "positive_rate":roll365_pos, "median_return":roll365["return"].median(), "min_return":roll365["return"].min(), "max_return":roll365["return"].max()}])
    roll_sum_tbl = render_table(roll180_summary, columns=["window","count","positive_rate","median_return","min_return","max_return"], col_labels={"window":"窗口", "count":"样本数", "positive_rate":"正收益比例", "median_return":"中位收益", "min_return":"最差", "max_return":"最好"}, col_formats={"positive_rate":fmt_pct,"median_return":fmt_pct,"min_return":fmt_pct,"max_return":fmt_pct}, col_positive_good=["positive_rate","median_return"])
    worst365 = roll365.sort_values("return").head(8)
    best365 = roll365.sort_values("return", ascending=False).head(8)
    worst_tbl = subset_table(worst365, ["start","end","return","max_dd","sharpe"], {"start":"开始","end":"结束","return":"收益","max_dd":"回撤","sharpe":"Sharpe"})
    best_tbl = subset_table(best365, ["start","end","return","max_dd","sharpe"], {"start":"开始","end":"结束","return":"收益","max_dd":"回撤","sharpe":"Sharpe"})

    audit_df = pd.DataFrame(r["causality_audit"])
    audit_tbl = render_table(audit_df, columns=["item","status","detail"], col_labels={"item":"检查项","status":"结论","detail":"说明"})

    body = hero + verdict + data_note + line_svg(eq)
    body += render_section("因果性与数据口径审计", audit_tbl)
    body += render_section("年度表现：regime 稳定性不够", yearly_tbl)
    body += render_note("2022 和 2024 是核心反证：两个完整年份分别约 -36.5% 和 -32.3%。2025/2026 的正收益不足以抵消历史大回撤。", kind="warn")
    body += render_section("成本敏感性：0 成本也不够强", cost_tbl)
    body += render_note("最关键的是 0 bps 仍然 -10.4%。如果裸 alpha 都不是明显正的，那么真实成本只会把问题放大。", kind="bad")
    body += render_section("参数范围：不是一个窄参数最优的问题", uni_tbl + cw_tbl)
    body += render_note("Universe=15 在长历史里勉强为正，但回撤仍 -54.1%，且这属于另一个更集中、更高风险的策略形态；carry 权重降低能改善，但没有把策略变成稳健 alpha。", kind="warn")
    body += render_section("滚动窗口稳定性", roll_sum_tbl + "<h3>最差 365d 窗口</h3>" + worst_tbl + "<h3>最好 365d 窗口</h3>" + best_tbl)
    body += render_section("我的判断", render_note(
        "这个验证基本推翻了“rank154 是强候选”的短样本结论。它更像一个在近期市场阶段有效的 trend/carry 混合暴露，"
        "而不是跨 3-5 年稳定存在的结构性套利。下一步如果继续做，不建议直接优化原参数；更合理的是拆开做因子归因："
        "单独测 carry、momo、breakout 的 long/short leg、按牛熊/高低 funding regime 分桶，再决定是否保留某个 sleeve。",
        kind="bad"))

    html = render_page(
        title="Rank154 · 3-5 年长历史验证报告",
        subtitle="历史 universe · Binance archive · 参数/成本/滚动窗口稳定性审计",
        body_html=body,
        generated_at=now,
        nav_links=[
            {"href":"/momentum/paper/rank154_validation.html", "label":"120天验证"},
            {"href":"/momentum/paper/rank154_carry_fix_backtest.html", "label":"Carry修正"},
            {"href":"/momentum/paper/rank154_hub.html", "label":"Rank154 Hub"},
        ],
    )
    out = write_page(SITE_PATH, html)
    print(f"[ok] {out} ({out.stat().st_size:,} bytes)")
    print("[url] https://jp.jerrypsy.top/momentum/paper/rank154_long_history.html")

if __name__ == "__main__":
    main()
