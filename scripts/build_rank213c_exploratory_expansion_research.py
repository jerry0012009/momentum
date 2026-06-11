#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import dataclass
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
SITE_PATH = ROOT / "reports" / "site" / "paper" / "rank213c_exploratory_expansion_research.html"
FIFTH_SCRIPT_PATH = ROOT / "scripts" / "build_rank213_age90_14d_fifth_round_profit_thickness.py"

SUMMARY_PATH = ART_DIR / "rank213c_exploratory_expansion_summary.json"
RESULTS_PATH = ART_DIR / "rank213c_exploratory_expansion_results.csv"
DAILY_PATH = ART_DIR / "rank213c_exploratory_expansion_daily.csv"
SHORTLIST_PATH = ART_DIR / "rank213c_exploratory_expansion_shortlist.csv"

COST_GRID_BPS = [4.0, 8.0, 12.0, 16.0]
SAMPLE_START = pd.Timestamp("2020-02-01T00:00:00Z")


def load_fifth_module():
    spec = importlib.util.spec_from_file_location("rank213_fifth_mod", FIFTH_SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {FIFTH_SCRIPT_PATH}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["rank213_fifth_mod"] = mod
    spec.loader.exec_module(mod)
    return mod


fifth = load_fifth_module()


@dataclass(frozen=True)
class VariantSpec:
    group: str
    variant: str
    long_capital: float = 0.5
    short_capital: float = 0.5
    leg_count: int = 4
    long_count: int | None = None
    short_count: int | None = None
    universe_size: int = 50
    signal_name: str = "retvol_14d_skip1d"
    short_gate: str = "always"
    rebalance_every_days: int = 1
    rank_buffer_extra: int = 0
    market_guard: str = "none"


def fmt_pct(x: object, digits: int = 2) -> str:
    try:
        if pd.isna(x):
            return ""
        return f"{float(x):.{digits}f}%"
    except (TypeError, ValueError):
        return ""


def fmt_bps(x: object, digits: int = 2) -> str:
    try:
        if pd.isna(x):
            return ""
        return f"{float(x):.{digits}f} bps"
    except (TypeError, ValueError):
        return ""


def fmt_num(x: object, digits: int = 3) -> str:
    try:
        if pd.isna(x):
            return ""
        return f"{float(x):.{digits}f}"
    except (TypeError, ValueError):
        return escape(str(x))


def gate_series(ctx: pd.DataFrame, name: str) -> pd.Series:
    gates = fifth.gate_masks(ctx)
    if name == "always":
        return pd.Series(True, index=ctx.index)
    if name == "never":
        return pd.Series(False, index=ctx.index)
    if name in gates:
        return gates[name].fillna(False).astype(bool)
    raise KeyError(f"unknown gate {name}")


def market_guard_series(ctx: pd.DataFrame, name: str) -> pd.Series:
    if name == "none":
        return pd.Series(True, index=ctx.index)
    if name == "avoid_eligible_prior7_crash":
        return (pd.to_numeric(ctx["prior7_eligible_ew_ret"], errors="coerce") > -0.10).fillna(True)
    if name == "avoid_eligible_prior30_crash":
        return (pd.to_numeric(ctx["prior30_eligible_ew_ret"], errors="coerce") > -0.25).fillna(True)
    if name == "avoid_btc_prior7_crash":
        return (pd.to_numeric(ctx["prior7_btc_ret"], errors="coerce") > -0.08).fillna(True)
    raise KeyError(f"unknown market guard {name}")


def score_panel_for(spec: VariantSpec, score_panels: dict[str, pd.DataFrame]) -> pd.DataFrame:
    if spec.signal_name in score_panels:
        return score_panels[spec.signal_name]
    raise KeyError(f"missing score panel {spec.signal_name}")


def choose_legs(scores: pd.Series, spec: VariantSpec) -> tuple[list[str], list[str]]:
    scores = scores.dropna().sort_values()
    long_count = spec.long_count if spec.long_count is not None else spec.leg_count
    short_count = spec.short_count if spec.short_count is not None else spec.leg_count
    if len(scores) < max(long_count, short_count, long_count + short_count):
        return [], []
    longs = scores.index[-long_count:].astype(str).tolist()[::-1] if long_count > 0 and spec.long_capital > 0 else []
    shorts = scores.index[:short_count].astype(str).tolist() if short_count > 0 and spec.short_capital > 0 else []
    return longs, shorts


def apply_buffer(prev: list[str], desired: list[str], rank_order: list[str], count: int, extra: int) -> list[str]:
    if extra <= 0 or not prev:
        return desired[:count]
    zone = set(rank_order[: count + extra])
    out = [sym for sym in prev if sym in zone]
    for sym in desired:
        if sym not in out:
            out.append(sym)
        if len(out) >= count:
            break
    return out[:count]


def simulate_variant(
    spec: VariantSpec,
    *,
    close: pd.DataFrame,
    next_ret: pd.DataFrame,
    score_panels: dict[str, pd.DataFrame],
    ranked_by_month: dict[str, list[str]],
    onboard_map: dict[str, pd.Timestamp],
    ctx: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict] = []
    prev_weights: dict[str, float] = {}
    prev_longs: list[str] = []
    prev_shorts: list[str] = []
    last_rebalance_i = -10**9
    short_gate = gate_series(ctx, spec.short_gate)
    active_guard = market_guard_series(ctx, spec.market_guard)
    score_panel = score_panel_for(spec, score_panels)
    long_count = spec.long_count if spec.long_count is not None else spec.leg_count
    short_count = spec.short_count if spec.short_count is not None else spec.leg_count

    for i, row in ctx.iterrows():
        ts = row["timestamp_ts"]
        month = str(row["month"])
        do_rebalance = (i - last_rebalance_i) >= spec.rebalance_every_days or not prev_weights
        if do_rebalance:
            universe = ranked_by_month.get(month, [])[: spec.universe_size]
            eligible = fifth.eligible_for_day(universe, onboard_map, ts)
            cols = [sym for sym in eligible if sym in score_panel.columns]
            scores = pd.Series(dtype=float)
            if cols and ts in score_panel.index:
                scores = pd.to_numeric(score_panel.loc[ts, cols], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
            desired_longs, desired_shorts = choose_legs(scores, spec)
            if desired_longs or desired_shorts:
                desc = scores.sort_values(ascending=False).index.astype(str).tolist()
                asc = scores.sort_values(ascending=True).index.astype(str).tolist()
                prev_longs = apply_buffer(prev_longs, desired_longs, desc, long_count, spec.rank_buffer_extra)
                prev_shorts = apply_buffer(prev_shorts, desired_shorts, asc, short_count, spec.rank_buffer_extra)
                last_rebalance_i = i

        use_short = bool(short_gate.iloc[i]) and bool(active_guard.iloc[i])
        use_long = bool(active_guard.iloc[i])
        weights = fifth.weights_from_longs_shorts(
            prev_longs if use_long else [],
            prev_shorts if use_short else [],
            long_capital=spec.long_capital,
            short_capital=spec.short_capital,
        )
        gross, long_contrib, short_contrib, lc, sc = fifth.returns_for_weights(next_ret, weights, ts)
        turn = fifth.turnover(prev_weights, weights)
        rows.append({
            "experiment_group": spec.group,
            "variant": spec.variant,
            "timestamp_ts": ts,
            "month": month,
            "active": bool(weights),
            "active_short": any(w < 0 for w in weights.values()),
            "gross_ret": gross,
            "long_contribution": long_contrib,
            "short_contribution": short_contrib,
            "target_turnover_x": turn,
            "long_count": lc,
            "short_count": sc,
            "long_capital": spec.long_capital,
            "short_capital": spec.short_capital,
            "universe_size": spec.universe_size,
            "rebalance_every_days": spec.rebalance_every_days,
            "rank_buffer_extra": spec.rank_buffer_extra,
            "short_gate": spec.short_gate,
            "market_guard": spec.market_guard,
        })
        prev_weights = weights
    return pd.DataFrame(rows)


def summarize(sub: pd.DataFrame, cost_bps: float) -> dict:
    gross = pd.to_numeric(sub["gross_ret"], errors="coerce").fillna(0.0)
    turnover = pd.to_numeric(sub["target_turnover_x"], errors="coerce").fillna(0.0)
    net = gross - cost_bps / 10000.0 * turnover
    active = sub["active"].fillna(False).astype(bool)
    active_short = sub["active_short"].fillna(False).astype(bool)
    return {
        "experiment_group": sub["experiment_group"].iloc[0],
        "variant": sub["variant"].iloc[0],
        "cost_bps_per_1x_turnover": cost_bps,
        "days": int(len(sub)),
        "active_days": int(active.sum()),
        "active_short_days": int(active_short.sum()),
        "gross_mean_bps": float(gross.mean() * 10000.0),
        "net_mean_bps": float(net.mean() * 10000.0),
        "net_cum_pct": float(fifth.compound(net) * 100.0),
        "max_drawdown_pct": float(fifth.max_drawdown(net) * 100.0),
        "sharpe": fifth.sharpe(net),
        "win_rate_pct": float((net > 0).mean() * 100.0),
        "avg_turnover_x": float(turnover.mean()),
        "turnover_p95_x": float(turnover.quantile(0.95)),
        "long_mean_bps": float(pd.to_numeric(sub["long_contribution"], errors="coerce").fillna(0.0).mean() * 10000.0),
        "short_mean_bps": float(pd.to_numeric(sub["short_contribution"], errors="coerce").fillna(0.0).mean() * 10000.0),
        "long_capital": float(sub["long_capital"].iloc[0]),
        "short_capital": float(sub["short_capital"].iloc[0]),
        "rebalance_every_days": int(sub["rebalance_every_days"].iloc[0]),
        "rank_buffer_extra": int(sub["rank_buffer_extra"].iloc[0]),
        "short_gate": sub["short_gate"].iloc[0],
        "market_guard": sub["market_guard"].iloc[0],
    }


def classify(row: pd.Series) -> tuple[str, str]:
    if row["net_mean_bps"] > 3.0 and row["net_cum_pct"] > 0 and row["max_drawdown_pct"] > -55 and row["avg_turnover_x"] < 0.45:
        return "Promising", "positive 12bps net with lower turnover; needs robustness follow-up"
    if row["net_mean_bps"] > 0 and row["net_cum_pct"] > 0:
        return "Watch", "positive 12bps net but drawdown/turnover still not clean"
    return "Fail", "does not preserve positive 12bps net"


def table_html(df: pd.DataFrame, cols: list[str], max_rows: int | None = None) -> str:
    view = df[cols].copy()
    if max_rows is not None:
        view = view.head(max_rows)
    head = "".join(f"<th>{escape(c)}</th>" for c in cols)
    body = []
    for _, row in view.iterrows():
        cells = []
        for c in cols:
            v = row.get(c, "")
            if c.endswith("_pct") or c in {"net_cum_pct", "max_drawdown_pct", "win_rate_pct"}:
                txt = fmt_pct(v)
            elif c.endswith("_bps") or c in {"gross_mean_bps", "net_mean_bps", "long_mean_bps", "short_mean_bps"}:
                txt = fmt_bps(v)
            elif isinstance(v, float):
                txt = fmt_num(v, 3)
            else:
                txt = escape(str(v))
            cells.append(f"<td>{txt}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def build_report(results: pd.DataFrame, shortlist: pd.DataFrame, summary: dict) -> str:
    cost12 = results[results["cost_bps_per_1x_turnover"] == 12.0].copy()
    base = cost12[cost12["variant"] == "base_50_50_daily"].iloc[0]
    best = shortlist.iloc[0]
    best_by_group = cost12.sort_values("net_mean_bps", ascending=False).groupby("experiment_group").head(4)
    generated = summary["generated_at_utc"].replace("T", " ").replace("Z", " UTC")
    cols = [
        "verdict", "experiment_group", "variant", "net_mean_bps", "net_cum_pct", "max_drawdown_pct", "sharpe",
        "avg_turnover_x", "gross_mean_bps", "long_mean_bps", "short_mean_bps", "active_short_days", "reason",
    ]
    compact_cols = [
        "experiment_group", "variant", "net_mean_bps", "net_cum_pct", "max_drawdown_pct", "avg_turnover_x",
        "long_capital", "short_capital", "short_gate", "market_guard",
    ]
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank213c 试探性拓展研究</title>
  <style>
    body {{ margin:0; background:#f6f3ec; color:#172033; font-family:"Noto Sans SC","Source Han Sans SC","PingFang SC","Microsoft YaHei",sans-serif; line-height:1.62; }}
    main {{ max-width:1220px; margin:0 auto; padding:28px 16px 56px; }}
    .card {{ background:white; border:1px solid #e6dccb; border-radius:14px; padding:18px 20px; margin:14px 0; }}
    .hero {{ border-color:#2563eb; background:#eff6ff; }}
    .warn {{ background:#fff7ed; border-color:#fdba74; }}
    .grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; }}
    .metric {{ background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:12px; }}
    .metric b {{ display:block; font-size:22px; line-height:1.2; }}
    .muted {{ color:#64748b; }}
    .table-wrap {{ overflow-x:auto; }}
    table {{ border-collapse:collapse; min-width:1120px; width:100%; }}
    th,td {{ border-bottom:1px solid #e2e8f0; padding:8px 10px; text-align:right; vertical-align:top; font-size:13px; }}
    th {{ background:#f8fafc; color:#475569; }}
    td:first-child,th:first-child,td:nth-child(2),th:nth-child(2),td:nth-child(3),th:nth-child(3) {{ text-align:left; }}
    code {{ background:#f1f5f9; border-radius:6px; padding:2px 6px; }}
    a {{ color:#2563eb; text-decoration:none; }}
    @media (max-width:760px) {{ .grid {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
<main>
  <section class="card hero">
    <h1>Rank213c 试探性拓展研究</h1>
    <p>目标：基于 213c 的 causal monthly-volume Top50 / age90 / ret-vol 选币框架，尝试寻找下一步可能优化收益的方向。这里是探索性研究，不是上线参数选择。</p>
    <p class="muted">生成时间：{escape(generated)}。成本统一用 <code>cost_bps_per_1x_turnover</code>，主读法看 12bps。</p>
    <p><a href="/momentum/paper/rank213_age90_14d_fifth_round_profit_thickness.html">第五轮利润厚度</a> · <a href="/momentum/paper/rank213_version_overview.html">Rank213 版本总览</a></p>
  </section>

  <section class="card warn">
    <h2>一句话结论</h2>
    <p><b>试探性拓展里最值得继续的是“低换手 + 降低 short capital”，而不是继续扩大 universe 或换信号。</b> 基准 <code>base_50_50_daily</code> 在 12bps 后为 {fmt_bps(base['net_mean_bps'])}、累计 {fmt_pct(base['net_cum_pct'])}；最好候选 <code>{escape(str(best['variant']))}</code> 为 {fmt_bps(best['net_mean_bps'])}、累计 {fmt_pct(best['net_cum_pct'])}、换手 {fmt_num(best['avg_turnover_x'])}x/day。</p>
    <p>推论：213c 的 long 排序仍有价值，但 short leg 更像需要降权/条件化的风险模块。若继续推进，应把 213c2/213d 的研究收窄到“低换手持仓惯性 + 0.25 short capital + 明确风险开关”。</p>
  </section>

  <section class="card">
    <h2>给新研究者的读法</h2>
    <ul>
      <li><b>本页是方向筛选，不是上线报告。</b> Promising 表示值得进入下一轮验证，不表示可以直接替换 213c 实盘参数。</li>
      <li><b>主读法看 12bps。</b> 这个口径比 flat 4bps 更接近实盘摩擦，因此比漂亮的低成本曲线更重要。</li>
      <li><b>先比较基准和最好候选。</b> 如果候选只是牺牲回撤或减少交易天数换来均值，不能简单视为改进。</li>
      <li><b>本页最重要的推论：</b>213c 的 alpha 主要还在 long 排序，short half 应该更像风险模块，下一轮应围绕低换手、short 降权和明确风控开关做小样本深挖。</li>
    </ul>
  </section>

  <section class="card">
    <h2>核心读数</h2>
    <div class="grid">
      <div class="metric"><b>{fmt_bps(base['net_mean_bps'])}</b><span>基准 12bps 日均</span></div>
      <div class="metric"><b>{fmt_bps(best['net_mean_bps'])}</b><span>最好候选 12bps 日均</span></div>
      <div class="metric"><b>{fmt_num(best['avg_turnover_x'])}x</b><span>最好候选换手</span></div>
      <div class="metric"><b>{int(summary['promising_count_12bps'])} / {int(summary['watch_count_12bps'])}</b><span>Promising / Watch</span></div>
    </div>
  </section>

  <section class="card">
    <h2>12bps Shortlist</h2>
    <div class="table-wrap">{table_html(shortlist, cols)}</div>
  </section>

  <section class="card">
    <h2>分组最好结果</h2>
    <div class="table-wrap">{table_html(best_by_group.sort_values(["experiment_group", "net_mean_bps"], ascending=[True, False]), compact_cols)}</div>
  </section>

  <section class="card">
    <h2>推论讨论</h2>
    <ul>
      <li><b>资本配比是第一优先级。</b> long-only 或 0.25 short capital 往往比 0.5/0.5 market-neutral 更接近保留 alpha，同时减少 short 噪声。</li>
      <li><b>低换手是第二优先级。</b> rank buffer 和 weekly rebalance 不是单纯省成本，也在减少每日 rank 抖动带来的误换仓。</li>
      <li><b>风险开关只能做 guard。</b> eligible/BTC crash guard 对回撤有帮助，但容易牺牲复利路径，不能独立构成收益来源。</li>
      <li><b>下一轮不要做大参数网格。</b> 更合理的是选 2-3 个候选做 walk-forward、年度稳定性、live-vs-shadow 成本复核。</li>
    </ul>
  </section>

  <section class="card">
    <h2>产物</h2>
    <ul>
      <li><code>{escape(str(RESULTS_PATH.relative_to(ROOT)))}</code></li>
      <li><code>{escape(str(DAILY_PATH.relative_to(ROOT)))}</code></li>
      <li><code>{escape(str(SHORTLIST_PATH.relative_to(ROOT)))}</code></li>
      <li><code>{escape(str(SUMMARY_PATH.relative_to(ROOT)))}</code></li>
    </ul>
  </section>
</main>
</body>
</html>
"""


def main() -> int:
    close, quote_volume = fifth.fourth.load_close_quote_panels()
    close = close[close.index >= SAMPLE_START - pd.Timedelta(days=45)].copy()
    next_ret = (close.shift(-1) / close - 1.0).replace([np.inf, -np.inf], np.nan)
    score_panels = fifth.build_score_panels(close)
    onboard_map = fifth.fourth.read_onboard_map()
    months = sorted({ts.strftime("%Y-%m") for ts in close.index[close.index >= SAMPLE_START]})
    ranked_by_month = fifth.fourth.build_monthly_ranked_universes(months, quote_volume, onboard_map, 100)
    dates = pd.DataFrame({"timestamp_ts": [ts for ts in close.index if ts >= SAMPLE_START and ts + pd.Timedelta(days=1) in close.index]})
    dates["exit_ts"] = dates["timestamp_ts"] + pd.Timedelta(days=1)
    dates["month"] = dates["timestamp_ts"].dt.strftime("%Y-%m")
    ctx = fifth.add_reference_gate_context(fifth.build_market_context(close, ranked_by_month, onboard_map, dates))

    specs = [
        VariantSpec("capital_mix", "base_50_50_daily"),
        VariantSpec("capital_mix", "long75_short25_daily", long_capital=0.75, short_capital=0.25),
        VariantSpec("capital_mix", "long100_no_short", long_capital=1.0, short_capital=0.0, short_count=0, short_gate="never"),
        VariantSpec("capital_mix", "long50_short25", long_capital=0.5, short_capital=0.25),
        VariantSpec("short_optional", "long75_short25_btc_prior7_positive", long_capital=0.75, short_capital=0.25, short_gate="btc_prior7_positive"),
        VariantSpec("short_optional", "long75_short25_btc_ma20", long_capital=0.75, short_capital=0.25, short_gate="btc_above_ma20"),
        VariantSpec("short_optional", "long50_short25_dispersion_high", long_capital=0.5, short_capital=0.25, short_gate="prior30_dispersion_high"),
        VariantSpec("low_turnover", "weekly_50_50", rebalance_every_days=7),
        VariantSpec("low_turnover", "weekly_long75_short25", long_capital=0.75, short_capital=0.25, rebalance_every_days=7),
        VariantSpec("low_turnover", "rank_buffer8_50_50", rank_buffer_extra=8),
        VariantSpec("low_turnover", "rank_buffer8_long75_short25", long_capital=0.75, short_capital=0.25, rank_buffer_extra=8),
        VariantSpec("low_turnover", "weekly_buffer8_long75_short25", long_capital=0.75, short_capital=0.25, rebalance_every_days=7, rank_buffer_extra=8),
        VariantSpec("risk_guard", "base_avoid_eligible_prior7_crash", market_guard="avoid_eligible_prior7_crash"),
        VariantSpec("risk_guard", "long75_short25_avoid_prior7_crash", long_capital=0.75, short_capital=0.25, market_guard="avoid_eligible_prior7_crash"),
        VariantSpec("risk_guard", "weekly_long75_short25_avoid_prior7_crash", long_capital=0.75, short_capital=0.25, rebalance_every_days=7, market_guard="avoid_eligible_prior7_crash"),
        VariantSpec("leg_shape", "top6_long_only", long_capital=1.0, short_capital=0.0, long_count=6, short_count=0, short_gate="never"),
        VariantSpec("leg_shape", "top6_long_short2_75_25", long_capital=0.75, short_capital=0.25, long_count=6, short_count=2),
        VariantSpec("leg_shape", "top3_long_short3_75_25", long_capital=0.75, short_capital=0.25, long_count=3, short_count=3),
    ]

    daily = pd.concat([
        simulate_variant(spec, close=close, next_ret=next_ret, score_panels=score_panels, ranked_by_month=ranked_by_month, onboard_map=onboard_map, ctx=ctx)
        for spec in specs
    ], ignore_index=True)
    daily.to_csv(DAILY_PATH, index=False)

    rows = []
    for (_, variant), sub in daily.groupby(["experiment_group", "variant"], sort=False):
        for cost in COST_GRID_BPS:
            rows.append(summarize(sub, cost))
    results = pd.DataFrame(rows)
    results["verdict"] = ""
    results["reason"] = ""
    cost12 = results["cost_bps_per_1x_turnover"] == 12.0
    for idx, row in results[cost12].iterrows():
        verdict, reason = classify(row)
        results.loc[idx, "verdict"] = verdict
        results.loc[idx, "reason"] = reason
    rank = {"Promising": 0, "Watch": 1, "Fail": 2, "": 3}
    results["verdict_rank"] = results["verdict"].map(rank).fillna(3).astype(int)
    results.to_csv(RESULTS_PATH, index=False)

    shortlist = results[cost12].sort_values(["verdict_rank", "net_mean_bps"], ascending=[True, False]).copy()
    shortlist.to_csv(SHORTLIST_PATH, index=False)

    summary = {
        "generated_at_utc": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ"),
        "objective": "rank213c exploratory expansion research",
        "sample_start": dates["timestamp_ts"].min().strftime("%Y-%m-%d"),
        "sample_end": dates["exit_ts"].max().strftime("%Y-%m-%d"),
        "variant_count": len(specs),
        "cost_grid_bps": COST_GRID_BPS,
        "promising_count_12bps": int((shortlist["verdict"] == "Promising").sum()),
        "watch_count_12bps": int((shortlist["verdict"] == "Watch").sum()),
        "fail_count_12bps": int((shortlist["verdict"] == "Fail").sum()),
        "artifacts": {
            "daily": str(DAILY_PATH.relative_to(ROOT)),
            "results": str(RESULTS_PATH.relative_to(ROOT)),
            "shortlist": str(SHORTLIST_PATH.relative_to(ROOT)),
            "site": str(SITE_PATH.relative_to(ROOT)),
        },
    }
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    SITE_PATH.write_text(build_report(results, shortlist, summary), encoding="utf-8")
    print(f"wrote {RESULTS_PATH.relative_to(ROOT)}")
    print(f"wrote {SHORTLIST_PATH.relative_to(ROOT)}")
    print(f"wrote {SUMMARY_PATH.relative_to(ROOT)}")
    print(f"wrote {SITE_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
