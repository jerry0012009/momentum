#!/usr/bin/env python3
"""Build Rank154 postmortem Chinese report page."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from momentum.html_render import (  # noqa: E402
    fmt_num,
    fmt_pct,
    render_metric_cards,
    render_note,
    render_page,
    render_section,
    render_table,
    write_page,
)

ART_DIR = ROOT / "reports" / "artifacts" / "rank154_postmortem"
LONG_ART_DIR = ROOT / "reports" / "artifacts" / "rank154_long_history"
SITE_PATH = ROOT / "reports" / "site" / "paper" / "rank154_postmortem.html"


def read_csv(name: str) -> pd.DataFrame:
    p = ART_DIR / name
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p)


def bps(x):
    try:
        return f"{float(x) * 10000:+.2f} bps"
    except Exception:
        return "—"


def pct(x):
    return fmt_pct(x)


def num(x):
    return fmt_num(x)


def compact_table(df: pd.DataFrame, cols: list[str], labels: dict[str, str] | None = None, n: int | None = None) -> str:
    if df.empty:
        return render_note("没有可展示的数据。", kind="warn")
    if n is not None:
        df = df.head(n)
    return render_table(
        df,
        columns=cols,
        col_labels=labels or {},
        col_formats={
            "mean_ic": num,
            "median_ic": num,
            "ic_std": num,
            "icir_daily": num,
            "positive_ic_rate": pct,
            "avg_cross_section_n": num,
            "top_ret_mean": bps,
            "bottom_ret_mean": bps,
            "spread_mean": bps,
            "spread_median": bps,
            "spread_positive_rate": pct,
            "portfolio_ret_mean": bps,
            "long_contribution_mean": bps,
            "short_contribution_mean": bps,
            "portfolio_positive_rate": pct,
            "long_equal_ret_mean": bps,
            "short_underlying_ret_mean": bps,
            "avg_long_n": num,
            "avg_short_n": num,
            "avg_gross_weight": num,
            "mean_fwd_ret": bps,
            "mean_ic_pooled": num,
        },
        col_positive_good=[
            "mean_ic", "icir_daily", "spread_mean", "portfolio_ret_mean",
            "long_contribution_mean", "short_contribution_mean", "positive_ic_rate",
        ],
    )


def factor_definition_html() -> str:
    rows = [
        ["carry", "`carry_raw = funding_rate_last`", "资金费率最后一笔；当前策略是值越高越偏多", "注意：这不是传统 carry short-high-funding，而更像 crowding/sentiment 暴露"],
        ["momo", "`momo_10d = close.pct_change(10)`", "10 日价格动量；越高越偏多", "经典截面趋势/动量"],
        ["breakout", "`breakout_raw = 19 - days_since_20d_high`", "越接近 20 日新高越偏多", "breakout/trend-following 暴露"],
        ["combined", "`0.5*carry_decile + 0.2*momo_decile + 0.3*breakout_decile` centered", "综合分数高做多、低做空", "rank154 当前实际交易信号"],
    ]
    html = ["<table><thead><tr><th>因子</th><th>公式</th><th>排名方向</th><th>我的解释</th></tr></thead><tbody>"]
    for r in rows:
        html.append("<tr>" + "".join(f"<td>{escape(x).replace('`', '<code>', 1).replace('`', '</code>', 1)}</td>" for x in r) + "</tr>")
    html.append("</tbody></table>")
    return "".join(html)


def main() -> None:
    manifest = json.loads((ART_DIR / "postmortem_manifest.json").read_text(encoding="utf-8"))
    ic = read_csv("factor_ic_summary.csv")
    yearly_ic = read_csv("yearly_factor_ic.csv")
    dec = read_csv("decile_spread_summary.csv")
    legs = read_csv("long_short_leg_summary.csv")
    age_ic = read_csv("age_bucket_ic_summary.csv")

    long_stats = {}
    p = LONG_ART_DIR / "long_history_results.json"
    if p.exists():
        long_stats = json.loads(p.read_text(encoding="utf-8")).get("baseline", {})

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    all_ic = ic.copy()
    combined_1 = all_ic[(all_ic.factor == "combined") & (all_ic.horizon == 1)].iloc[0]
    combined_5 = all_ic[(all_ic.factor == "combined") & (all_ic.horizon == 5)].iloc[0]
    carry_10 = all_ic[(all_ic.factor == "carry") & (all_ic.horizon == 10)].iloc[0]
    all_leg_5 = legs[(legs.year.astype(str) == "ALL") & (legs.horizon == 5)].iloc[0]
    all_dec_10 = dec[(dec.year.astype(str) == "ALL") & (dec.factor == "combined") & (dec.horizon == 10)].iloc[0]

    cards = [
        {"label": "长历史 baseline", "value": fmt_pct(long_stats.get("return")), "subtitle": "原 release gate: 5 bps/side", "kind": "bad"},
        {"label": "Baseline Max DD", "value": fmt_pct(long_stats.get("max_dd")), "subtitle": "长历史主验证", "kind": "bad"},
        {"label": "Combined IC 1d", "value": fmt_num(combined_1["mean_ic"]), "subtitle": f"ICIR {fmt_num(combined_1['icir_daily'])}", "kind": "bad"},
        {"label": "Combined IC 5d", "value": fmt_num(combined_5["mean_ic"]), "subtitle": f"正 IC 日 {fmt_pct(combined_5['positive_ic_rate'])}", "kind": "bad"},
        {"label": "Carry IC 10d", "value": fmt_num(carry_10["mean_ic"]), "subtitle": "唯一相对能看的组件", "kind": "warn"},
        {"label": "5d weighted edge", "value": bps(all_leg_5["portfolio_ret_mean"]), "subtitle": "未扣成本；很薄", "kind": "warn"},
    ]

    verdict = render_note(
        "<b>最终结论：rank154 应正式归档为 failed release candidate，而不是继续做参数优化。</b> "
        "长历史 baseline 已经失败；这次 postmortem 进一步说明失败不是单纯成本问题，而是 combined 信号本身长期 IC 接近 0 且在 2022/2024 明显反向。"
        "carry 子因子有一点 5-10d 正 IC，但不足以支撑原组合；momo/breakout 更像 regime 暴露，不是稳定 alpha。",
        kind="bad",
    )

    data_note = render_note(
        f"数据口径：读取 <code>{escape(manifest['panel_path'])}</code>，panel {manifest['panel_rows']:,} 行、"
        f"{manifest['panel_symbols']} 个 symbols，日期 {escape(manifest['panel_date_min'][:10])} → {escape(manifest['panel_date_max'][:10])}。"
        f"每天只用当时 eligible symbol 的 30d trailing quote volume 取 Top{manifest['universe_size']}，得到 {manifest['universe_rows']:,} 条 daily universe rows / "
        f"{manifest['universe_days']:,} 个交易日。forward return 是按 symbol 向未来 shift，避免未来数据选 universe。",
        kind="good",
    )

    ic_tbl = compact_table(
        ic.sort_values(["factor", "horizon"]),
        ["factor", "horizon", "days", "mean_ic", "median_ic", "icir_daily", "positive_ic_rate"],
        {"factor": "因子", "horizon": "持有天数", "days": "天数", "mean_ic": "Mean IC", "median_ic": "Median IC", "icir_daily": "Daily ICIR", "positive_ic_rate": "正IC比例"},
    )

    y_combined = yearly_ic[yearly_ic.factor == "combined"].sort_values(["year", "horizon"])
    yearly_tbl = compact_table(
        y_combined,
        ["year", "horizon", "days", "mean_ic", "icir_daily", "positive_ic_rate"],
        {"year": "年份", "horizon": "持有天数", "days": "天数", "mean_ic": "Mean IC", "icir_daily": "ICIR", "positive_ic_rate": "正IC比例"},
    )

    dec_all = dec[dec.year.astype(str) == "ALL"].sort_values(["factor", "horizon"])
    dec_tbl = compact_table(
        dec_all,
        ["factor", "horizon", "top_ret_mean", "bottom_ret_mean", "spread_mean", "spread_median", "spread_positive_rate"],
        {"factor": "因子", "horizon": "持有天数", "top_ret_mean": "Top均值", "bottom_ret_mean": "Bottom均值", "spread_mean": "Top-Bottom", "spread_median": "中位spread", "spread_positive_rate": "spread>0"},
    )

    leg_all = legs[legs.year.astype(str) == "ALL"].sort_values("horizon")
    leg_tbl = compact_table(
        leg_all,
        ["horizon", "portfolio_ret_mean", "long_contribution_mean", "short_contribution_mean", "portfolio_positive_rate", "long_equal_ret_mean", "short_underlying_ret_mean", "avg_gross_weight"],
        {"horizon": "持有天数", "portfolio_ret_mean": "组合均值", "long_contribution_mean": "Long贡献", "short_contribution_mean": "Short贡献", "portfolio_positive_rate": "正收益日", "long_equal_ret_mean": "Long标的均值", "short_underlying_ret_mean": "Short标的涨跌", "avg_gross_weight": "平均gross"},
    )

    age_focus = age_ic[(age_ic.factor.isin(["combined", "carry"])) & (age_ic.horizon.isin([1, 5, 10]))].sort_values(["age_bucket", "factor", "horizon"])
    age_tbl = compact_table(
        age_focus,
        ["age_bucket", "factor", "horizon", "days", "mean_ic", "icir_daily", "positive_ic_rate", "avg_cross_section_n"],
        {"age_bucket": "上市年龄", "factor": "因子", "horizon": "持有天数", "days": "天数", "mean_ic": "Mean IC", "icir_daily": "ICIR", "positive_ic_rate": "正IC比例", "avg_cross_section_n": "日均样本"},
    )

    why_failed = """
<ul>
  <li><b>组合方向长期不稳：</b>combined IC 全样本 1d/3d/5d/10d 约 -0.020/-0.014/-0.010/-0.001；这不是能靠实盘执行救回来的信号。</li>
  <li><b>2022/2024 是强反证：</b>combined 在 2022、2024 的多数 horizon 为负，说明它不是跨 regime 的结构性套利。</li>
  <li><b>Top-Bottom spread 很薄：</b>combined 10d 全样本 Top-Bottom 约 <b>%s</b>，且 1d/3d 的中位 spread 为负；这还没扣真实成本。</li>
  <li><b>收益主要来自 short leg 的阶段性暴露：</b>5d weighted edge 约 <b>%s</b>，long 贡献为 <b>%s</b>、short 贡献为 <b>%s</b>；这不像一个双边稳定截面 alpha。</li>
  <li><b>因子语义有偏差：</b>carry 当前是“高 funding 更偏多”，不是传统意义上的 short-high-funding carry trade。它可能捕捉的是拥挤趋势，而不是资金费套利。</li>
</ul>
""" % (bps(all_dec_10["spread_mean"]), bps(all_leg_5["portfolio_ret_mean"]), bps(all_leg_5["long_contribution_mean"]), bps(all_leg_5["short_contribution_mean"]))

    archive_decision = render_note(
        "<b>Archive decision:</b> 停止把 rank154 当作 release 候选推进；保留代码、paper runner 和 artifacts 作为 research archive。"
        "下一步如果继续利用它，应该拆成 factor leads，而不是继续优化原始 0.5/0.2/0.3 权重。",
        kind="warn",
    )

    followups = """
<ol>
  <li><b>Carry-only reversal / trend sleeve：</b>单独重测 carry，不要沿用 rank154 的命名假设；先确认高 funding 到底应该顺势做多，还是反向做空收拥挤 unwind。</li>
  <li><b>Young-coin trend rotation：</b>age bucket 里 3y+ 明显更差，young buckets 没有完全死；可以单独研究 180d-2y 的新币趋势，但必须加流动性和成本约束。</li>
  <li><b>Market-regime gate：</b>如果宏观观点是“某些阶段趋势拥挤能延续”，应该显式定义 regime（BTC trend、全市场 funding、dispersion），而不是在原 rank154 里暗含。</li>
  <li><b>多因子不是简单叠加：</b>先做 factor zoo 的独立 IC、相关性、换手、cost haircut；只有能跨 regime 留下净 edge 的因子才进入组合。</li>
</ol>
"""

    artifacts = pd.DataFrame([
        {"file": "research/optimization_loop/2026-05-09_rank154_postmortem_plan.md", "purpose": "可落地执行方案"},
        {"file": "scripts/analyze_rank154_postmortem.py", "purpose": "归因计算脚本"},
        {"file": "reports/artifacts/rank154_postmortem/factor_ic_summary.csv", "purpose": "全样本 IC/ICIR"},
        {"file": "reports/artifacts/rank154_postmortem/yearly_factor_ic.csv", "purpose": "年度 IC 分解"},
        {"file": "reports/artifacts/rank154_postmortem/decile_spread_summary.csv", "purpose": "分位 Top-Bottom spread"},
        {"file": "reports/artifacts/rank154_postmortem/long_short_leg_summary.csv", "purpose": "long/short leg 贡献"},
        {"file": "reports/artifacts/rank154_postmortem/age_bucket_ic_summary.csv", "purpose": "上市年龄分桶 IC"},
    ])
    artifact_tbl = render_table(artifacts, columns=["file", "purpose"], col_labels={"file": "文件", "purpose": "用途"})

    body = ""
    body += render_metric_cards(cards)
    body += verdict
    body += data_note
    body += render_section("1. 因子定义审计", factor_definition_html())
    body += render_section("2. IC/ICIR：combined 信号长期接近没预测力", ic_tbl)
    body += render_note("IC 是“今天的因子排名”和“未来收益排名”的相关性。>0 代表因子越高，未来收益越高；<0 代表反向。这里 combined 在短 horizon 为负，说明原组合方向本身不稳。", kind="warn")
    body += render_section("3. 年度分解：2022/2024 是核心反证", yearly_tbl)
    body += render_section("4. 分位收益：Top-Bottom spread 不够厚", dec_tbl)
    body += render_section("5. Long / Short leg：不是漂亮的双边 alpha", leg_tbl)
    body += render_section("6. Age bucket：老币暴露更差，新币线索只能当后续 lead", age_tbl)
    body += render_section("7. 为什么失败", why_failed)
    body += render_section("8. 归档决定与后续分支", archive_decision + followups)
    body += render_section("9. 产物清单", artifact_tbl)

    html = render_page(
        title="Rank154 Postmortem · 失败归因与归档报告",
        subtitle="IC/ICIR · 分位 spread · long/short leg · age bucket · release gate archive",
        body_html=body,
        generated_at=generated,
        nav_links=[
            {"href": "/momentum/paper/rank154_hub.html", "label": "Rank154 Hub"},
            {"href": "/momentum/paper/rank154_long_history.html", "label": "长历史验证"},
            {"href": "/momentum/paper/rank154_validation.html", "label": "120天验证"},
        ],
    )
    out = write_page(SITE_PATH, html)
    print(f"[ok] {out} ({out.stat().st_size:,} bytes)")
    print("[url] https://jp.jerrypsy.top/momentum/paper/rank154_postmortem.html")


if __name__ == "__main__":
    main()
