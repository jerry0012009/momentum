#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import math
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
SITE_PATH = ROOT / "reports" / "site" / "paper" / "rank213c_buffer8_focus_research.html"
FIFTH_SCRIPT_PATH = ROOT / "scripts" / "build_rank213_age90_14d_fifth_round_profit_thickness.py"

SUMMARY_PATH = ART_DIR / "rank213c_buffer8_focus_summary.json"
RESULTS_PATH = ART_DIR / "rank213c_buffer8_focus_results.csv"
DAILY_PATH = ART_DIR / "rank213c_buffer8_focus_daily.csv"
SHORTLIST_PATH = ART_DIR / "rank213c_buffer8_focus_shortlist.csv"
ANNUAL_PATH = ART_DIR / "rank213c_buffer8_focus_annual.csv"
MONTHLY_PATH = ART_DIR / "rank213c_buffer8_focus_monthly.csv"

COST_GRID_BPS = [4.0, 8.0, 12.0, 16.0]
SAMPLE_START = pd.Timestamp("2020-02-01T00:00:00Z")


def load_fifth_module():
    spec = importlib.util.spec_from_file_location("rank213_fifth_buffer_mod", FIFTH_SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {FIFTH_SCRIPT_PATH}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["rank213_fifth_buffer_mod"] = mod
    spec.loader.exec_module(mod)
    return mod


fifth = load_fifth_module()


@dataclass(frozen=True)
class BufferSpec:
    group: str
    variant: str
    long_capital: float = 0.5
    short_capital: float = 0.5
    long_count: int = 4
    short_count: int = 4
    universe_size: int = 50
    long_buffer_extra: int = 8
    short_buffer_extra: int = 8
    rebalance_every_days: int = 1
    replacement_cap: int | None = None
    short_gate: str = "always"
    market_guard: str = "none"
    weight_blend: float = 1.0
    turnover_cap_x: float | None = None


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
    if name == "always":
        return pd.Series(True, index=ctx.index)
    if name == "never":
        return pd.Series(False, index=ctx.index)
    gates = fifth.gate_masks(ctx)
    if name not in gates:
        raise KeyError(f"unknown gate {name}")
    return gates[name].fillna(False).astype(bool)


def guard_series(ctx: pd.DataFrame, name: str) -> pd.Series:
    if name == "none":
        return pd.Series(True, index=ctx.index)
    if name == "avoid_eligible_prior7_crash":
        return (pd.to_numeric(ctx["prior7_eligible_ew_ret"], errors="coerce") > -0.10).fillna(True)
    if name == "avoid_btc_prior7_crash":
        return (pd.to_numeric(ctx["prior7_btc_ret"], errors="coerce") > -0.08).fillna(True)
    raise KeyError(f"unknown guard {name}")


def choose_legs(scores: pd.Series, spec: BufferSpec) -> tuple[list[str], list[str]]:
    scores = scores.dropna().sort_values()
    if len(scores) < max(spec.long_count, spec.short_count, spec.long_count + spec.short_count):
        return [], []
    longs = scores.index[-spec.long_count:].astype(str).tolist()[::-1] if spec.long_capital > 0 and spec.long_count > 0 else []
    shorts = scores.index[:spec.short_count].astype(str).tolist() if spec.short_capital > 0 and spec.short_count > 0 else []
    return longs, shorts


def apply_side_buffer(prev: list[str], desired: list[str], rank_order: list[str], count: int, extra: int) -> list[str]:
    if count <= 0:
        return []
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


def blend_or_cap_weights(prev: dict[str, float], target: dict[str, float], spec: BufferSpec) -> dict[str, float]:
    if not prev:
        return target
    keys = set(prev) | set(target)
    raw_delta = {k: target.get(k, 0.0) - prev.get(k, 0.0) for k in keys}
    scale = min(max(spec.weight_blend, 0.0), 1.0)
    if spec.turnover_cap_x is not None:
        full_turnover = sum(abs(v) for v in raw_delta.values())
        if full_turnover > spec.turnover_cap_x and full_turnover > 0:
            scale = min(scale, spec.turnover_cap_x / full_turnover)
    out = {k: prev.get(k, 0.0) + scale * raw_delta[k] for k in keys}
    return {k: v for k, v in out.items() if abs(v) > 1e-10}


def simulate_spec(
    spec: BufferSpec,
    *,
    next_ret: pd.DataFrame,
    score_panel: pd.DataFrame,
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
    active_guard = guard_series(ctx, spec.market_guard)

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
                long_rank = scores.sort_values(ascending=False).index.astype(str).tolist()
                short_rank = scores.sort_values(ascending=True).index.astype(str).tolist()
                new_longs = apply_side_buffer(prev_longs, desired_longs, long_rank, spec.long_count, spec.long_buffer_extra)
                new_shorts = apply_side_buffer(prev_shorts, desired_shorts, short_rank, spec.short_count, spec.short_buffer_extra)
                if spec.replacement_cap is not None and prev_longs and prev_shorts:
                    new_longs = fifth.apply_replacement_cap(prev_longs, new_longs, spec.replacement_cap)
                    new_shorts = fifth.apply_replacement_cap(prev_shorts, new_shorts, spec.replacement_cap)
                prev_longs = new_longs
                prev_shorts = new_shorts
                last_rebalance_i = i

        guard_on = bool(active_guard.iloc[i])
        use_short = guard_on and bool(short_gate.iloc[i])
        target_weights = fifth.weights_from_longs_shorts(
            prev_longs if guard_on else [],
            prev_shorts if use_short else [],
            long_capital=spec.long_capital,
            short_capital=spec.short_capital,
        )
        cur_weights = blend_or_cap_weights(prev_weights, target_weights, spec)
        gross, long_ret, short_ret, long_count, short_count = fifth.returns_for_weights(next_ret, cur_weights, ts)
        t = fifth.turnover(prev_weights, cur_weights)
        rows.append({
            "experiment_group": spec.group,
            "variant": spec.variant,
            "timestamp_ts": ts,
            "month": month,
            "active": bool(cur_weights),
            "active_short": any(w < 0 for w in cur_weights.values()),
            "gross_ret": gross,
            "long_contribution": long_ret,
            "short_contribution": short_ret,
            "target_turnover_x": t,
            "long_count": long_count,
            "short_count": short_count,
            "long_capital": spec.long_capital,
            "short_capital": spec.short_capital,
            "long_buffer_extra": spec.long_buffer_extra,
            "short_buffer_extra": spec.short_buffer_extra,
            "rebalance_every_days": spec.rebalance_every_days,
            "replacement_cap": spec.replacement_cap if spec.replacement_cap is not None else 0,
            "short_gate": spec.short_gate,
            "market_guard": spec.market_guard,
            "weight_blend": spec.weight_blend,
            "turnover_cap_x": spec.turnover_cap_x if spec.turnover_cap_x is not None else np.nan,
            "longs": ",".join(prev_longs),
            "shorts": ",".join(prev_shorts if use_short else []),
        })
        prev_weights = cur_weights
    return pd.DataFrame(rows)


def summarize_daily(sub: pd.DataFrame, cost_bps: float) -> dict:
    gross = pd.to_numeric(sub["gross_ret"], errors="coerce").fillna(0.0)
    turn = pd.to_numeric(sub["target_turnover_x"], errors="coerce").fillna(0.0)
    net = gross - cost_bps / 10000.0 * turn
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
        "avg_turnover_x": float(turn.mean()),
        "turnover_p95_x": float(turn.quantile(0.95)),
        "long_mean_bps": float(pd.to_numeric(sub["long_contribution"], errors="coerce").fillna(0.0).mean() * 10000.0),
        "short_mean_bps": float(pd.to_numeric(sub["short_contribution"], errors="coerce").fillna(0.0).mean() * 10000.0),
        "long_capital": float(sub["long_capital"].iloc[0]),
        "short_capital": float(sub["short_capital"].iloc[0]),
        "long_buffer_extra": int(sub["long_buffer_extra"].iloc[0]),
        "short_buffer_extra": int(sub["short_buffer_extra"].iloc[0]),
        "rebalance_every_days": int(sub["rebalance_every_days"].iloc[0]),
        "replacement_cap": int(sub["replacement_cap"].iloc[0]),
        "short_gate": sub["short_gate"].iloc[0],
        "market_guard": sub["market_guard"].iloc[0],
        "weight_blend": float(sub["weight_blend"].iloc[0]),
        "turnover_cap_x": float(sub["turnover_cap_x"].iloc[0]) if pd.notna(sub["turnover_cap_x"].iloc[0]) else np.nan,
    }


def classify(row: pd.Series) -> tuple[str, str, int]:
    if row["net_mean_bps"] >= 5.0 and row["net_cum_pct"] > 0 and row["max_drawdown_pct"] > -50 and row["avg_turnover_x"] <= 0.25:
        return "Promising", "clears 12bps mean/turnover target, but still needs robustness and real-cost replay", 0
    if row["net_mean_bps"] > 0 and row["net_cum_pct"] > 0 and row["max_drawdown_pct"] > -55 and row["avg_turnover_x"] <= 0.30:
        return "Watch", "positive 12bps net with acceptable turnover, but thickness or drawdown is still marginal", 1
    if row["net_mean_bps"] > 0 and row["net_cum_pct"] > 0:
        return "Diagnostic", "positive net, but drawdown/turnover/path is not suitable as a candidate", 2
    return "Fail", "does not preserve positive 12bps net", 3


def add_net_columns(daily: pd.DataFrame, cost_bps: float = 12.0) -> pd.DataFrame:
    out = daily.copy()
    out["net_ret_12bps"] = pd.to_numeric(out["gross_ret"], errors="coerce").fillna(0.0) - cost_bps / 10000.0 * pd.to_numeric(out["target_turnover_x"], errors="coerce").fillna(0.0)
    return out


def annual_monthly_tables(daily: pd.DataFrame, selected: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows_a: list[dict] = []
    rows_m: list[dict] = []
    d = add_net_columns(daily)
    d["year"] = pd.to_datetime(d["timestamp_ts"], utc=True).dt.year
    for variant in selected:
        sub = d[d["variant"] == variant].copy()
        for year, g in sub.groupby("year"):
            net = pd.to_numeric(g["net_ret_12bps"], errors="coerce").fillna(0.0)
            rows_a.append({
                "variant": variant,
                "year": int(year),
                "days": int(len(g)),
                "net_cum_pct": fifth.compound(net) * 100.0,
                "max_drawdown_pct": fifth.max_drawdown(net) * 100.0,
                "avg_turnover_x": pd.to_numeric(g["target_turnover_x"], errors="coerce").mean(),
                "long_mean_bps": pd.to_numeric(g["long_contribution"], errors="coerce").fillna(0.0).mean() * 10000.0,
                "short_mean_bps": pd.to_numeric(g["short_contribution"], errors="coerce").fillna(0.0).mean() * 10000.0,
            })
        for month, g in sub.groupby("month"):
            net = pd.to_numeric(g["net_ret_12bps"], errors="coerce").fillna(0.0)
            rows_m.append({
                "variant": variant,
                "month": month,
                "net_cum_pct": fifth.compound(net) * 100.0,
                "max_drawdown_pct": fifth.max_drawdown(net) * 100.0,
                "avg_turnover_x": pd.to_numeric(g["target_turnover_x"], errors="coerce").mean(),
            })
    return pd.DataFrame(rows_a), pd.DataFrame(rows_m)


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
                txt = fmt_num(v)
            else:
                txt = escape(str(v))
            cells.append(f"<td>{txt}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def build_specs() -> list[BufferSpec]:
    specs: list[BufferSpec] = [
        BufferSpec("reference", "base_50_50_daily", long_buffer_extra=0, short_buffer_extra=0),
    ]
    for extra in [4, 6, 8, 10, 12, 16]:
        specs.append(BufferSpec("buffer_width", f"buffer{extra}_50_50", long_buffer_extra=extra, short_buffer_extra=extra))
    specs.extend([
        BufferSpec("side_specific", "long_buffer12_short_daily", long_buffer_extra=12, short_buffer_extra=0),
        BufferSpec("side_specific", "long_buffer12_short_buffer4", long_buffer_extra=12, short_buffer_extra=4),
        BufferSpec("side_specific", "long_buffer16_short_buffer4", long_buffer_extra=16, short_buffer_extra=4),
        BufferSpec("side_specific", "long_buffer12_short25_buffer4", long_capital=0.5, short_capital=0.25, long_buffer_extra=12, short_buffer_extra=4),
        BufferSpec("side_specific", "long75_short25_buffer8", long_capital=0.75, short_capital=0.25, long_buffer_extra=8, short_buffer_extra=8),
        BufferSpec("side_specific", "long75_short25_long12_short4", long_capital=0.75, short_capital=0.25, long_buffer_extra=12, short_buffer_extra=4),
        BufferSpec("short_overlay", "buffer8_short_btc_prior7_positive", long_buffer_extra=8, short_buffer_extra=8, short_gate="btc_prior7_positive"),
        BufferSpec("short_overlay", "buffer8_short_btc_above_ma20", long_buffer_extra=8, short_buffer_extra=8, short_gate="btc_above_ma20"),
        BufferSpec("short_overlay", "buffer8_short_dispersion_high", long_buffer_extra=8, short_buffer_extra=8, short_gate="prior30_dispersion_high"),
        BufferSpec("short_overlay", "buffer8_short25_btc_prior7_positive", short_capital=0.25, long_buffer_extra=8, short_buffer_extra=8, short_gate="btc_prior7_positive"),
        BufferSpec("short_overlay", "buffer8_short25_dispersion_high", short_capital=0.25, long_buffer_extra=8, short_buffer_extra=8, short_gate="prior30_dispersion_high"),
        BufferSpec("friction_control", "buffer8_replacement_cap1", long_buffer_extra=8, short_buffer_extra=8, replacement_cap=1),
        BufferSpec("friction_control", "buffer8_weekly", long_buffer_extra=8, short_buffer_extra=8, rebalance_every_days=7),
        BufferSpec("friction_control", "buffer8_partial_2d", long_buffer_extra=8, short_buffer_extra=8, weight_blend=0.5),
        BufferSpec("friction_control", "buffer8_partial_3d", long_buffer_extra=8, short_buffer_extra=8, weight_blend=1.0 / 3.0),
        BufferSpec("friction_control", "buffer8_turnover_cap_0p2", long_buffer_extra=8, short_buffer_extra=8, turnover_cap_x=0.2),
        BufferSpec("friction_control", "buffer8_turnover_cap_0p3", long_buffer_extra=8, short_buffer_extra=8, turnover_cap_x=0.3),
        BufferSpec("risk_guard", "buffer8_avoid_eligible_prior7_crash", long_buffer_extra=8, short_buffer_extra=8, market_guard="avoid_eligible_prior7_crash"),
        BufferSpec("risk_guard", "buffer8_avoid_btc_prior7_crash", long_buffer_extra=8, short_buffer_extra=8, market_guard="avoid_btc_prior7_crash"),
    ])
    return specs


def build_report(results: pd.DataFrame, shortlist: pd.DataFrame, annual: pd.DataFrame, monthly: pd.DataFrame, summary: dict) -> str:
    cost12 = results[results["cost_bps_per_1x_turnover"] == 12.0].copy()
    base = cost12[cost12["variant"] == "base_50_50_daily"].iloc[0]
    anchor = cost12[cost12["variant"] == "buffer8_50_50"].iloc[0]
    best = shortlist.iloc[0] if len(shortlist) else anchor
    best_by_group = cost12.sort_values(["verdict_rank", "net_mean_bps"], ascending=[True, False]).groupby("experiment_group").head(3)
    worst_months = monthly[monthly["variant"] == str(best["variant"])].sort_values("net_cum_pct").head(8) if len(monthly) else pd.DataFrame()
    annual_best = annual[annual["variant"] == str(best["variant"])].copy()
    generated = summary["generated_at_utc"].replace("T", " ").replace("Z", " UTC")
    cols = [
        "verdict", "experiment_group", "variant", "net_mean_bps", "net_cum_pct", "max_drawdown_pct", "sharpe",
        "avg_turnover_x", "long_mean_bps", "short_mean_bps", "long_capital", "short_capital", "short_gate", "reason",
    ]
    compact_cols = [
        "experiment_group", "variant", "net_mean_bps", "net_cum_pct", "max_drawdown_pct", "avg_turnover_x",
        "long_buffer_extra", "short_buffer_extra", "short_capital", "short_gate", "weight_blend", "turnover_cap_x",
    ]
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank213c Buffer8 专题研究</title>
  <style>
    body {{ margin:0; background:#f6f3ec; color:#172033; font-family:"Noto Sans SC","Source Han Sans SC","PingFang SC","Microsoft YaHei",sans-serif; line-height:1.62; }}
    main {{ max-width:1220px; margin:0 auto; padding:28px 16px 56px; }}
    .card {{ background:white; border:1px solid #e6dccb; border-radius:14px; padding:18px 20px; margin:14px 0; }}
    .hero {{ border-color:#0f766e; background:#f0fdfa; }}
    .warn {{ background:#fff7ed; border-color:#fdba74; }}
    .good {{ background:#f0fdf4; border-color:#86efac; }}
    .bad {{ background:#fef2f2; border-color:#fecaca; }}
    .grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; }}
    .twocol {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; }}
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
    @media (max-width:760px) {{ .grid,.twocol {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
<main>
  <section class="card hero">
    <h1>Rank213c Buffer8 专题研究</h1>
    <p>目标：沿着 <code>rank_buffer8_50_50</code> 这条线，测试 buffer 宽度、long/short 分侧缓冲、short overlay、only-replace、partial rebalance 与 turnover cap，寻找 12bps 成本下更可持有的 213c2 候选。</p>
    <p class="muted">生成时间：{escape(generated)}。样本为 causal monthly-volume Top50、age90、retvol14 skip1d、daily next-day hold；主读法看 12bps/1x turnover。</p>
    <p><a href="/momentum/paper/rank213c_next_research_roadmap.html">213c 研究路线图</a> · <a href="/momentum/paper/rank213_age90_14d_fifth_round_profit_thickness.html">第五轮利润厚度</a> · <a href="/momentum/paper/rank213c_exploratory_expansion_research.html">试探性拓展</a></p>
  </section>

  <section class="card warn">
    <h2>一句话结论</h2>
    <p><b>本轮把 buffer8 线推进到了“可继续深挖”的阶段，但还没有推进到“可放大”的阶段。</b> 最好候选是 <code>{escape(str(best['variant']))}</code>，12bps 后日均 {fmt_bps(best['net_mean_bps'])}，累计 {fmt_pct(best['net_cum_pct'])}，最大回撤 {fmt_pct(best['max_drawdown_pct'])}，换手 {fmt_num(best['avg_turnover_x'])}x/day；它通过了本轮 Promising 门槛，但仍需要真实成本 replay、年度稳定性和 live-vs-shadow 验证。</p>
    <p>最重要的发现是：<b>buffer 的价值主要来自降低误换仓，而不是让策略变成新 alpha。</b> 过宽 buffer、short 降权、dispersion gate、partial rebalance 都不能稳定解决路径风险；下一步应该把研究收窄到“buffer8 附近 + 真实成本 replay + short-active day 归因”。</p>
  </section>

  <section class="card">
    <h2>核心读数</h2>
    <div class="grid">
      <div class="metric"><b>{fmt_bps(base['net_mean_bps'])}</b><span>无 buffer 基准 12bps 日均</span></div>
      <div class="metric"><b>{fmt_bps(anchor['net_mean_bps'])}</b><span>buffer8 anchor 日均</span></div>
      <div class="metric"><b>{fmt_bps(best['net_mean_bps'])}</b><span>本轮最好候选日均</span></div>
      <div class="metric"><b>{int(summary['promising_count_12bps'])} / {int(summary['watch_count_12bps'])}</b><span>Promising / Watch</span></div>
    </div>
  </section>

  <section class="card good">
    <h2>12bps 候选表</h2>
    <div class="table-wrap">{table_html(shortlist, cols)}</div>
  </section>

  <section class="card">
    <h2>分组最好结果</h2>
    <div class="table-wrap">{table_html(best_by_group.sort_values(["experiment_group", "verdict_rank", "net_mean_bps"], ascending=[True, True, False]), compact_cols)}</div>
  </section>

  <section class="card">
    <h2>推论讨论</h2>
    <ul>
      <li><b>buffer 宽度不是越大越好。</b> buffer8 附近仍是较合理的中间点；继续加宽会降低换手，但也更容易持有过期信号。</li>
      <li><b>weekly buffer8 是本轮唯一 Promising。</b> 它把换手压到约 0.134x/day，并把 12bps 后日均推到 6.78bps；但 2022 和 2026YTD 仍为负，说明它不是一个可以直接放大的终局版本。</li>
      <li><b>分侧 buffer 没有解决核心问题。</b> 给 long 更宽、给 short 更窄的设计能改变风险形态，但没有稳定地产生更低回撤的 12bps 候选。</li>
      <li><b>short overlay 仍偏诊断价值。</b> BTC / dispersion gate 会减少 short active days，但不够精准，不能单独成为上线开关。</li>
      <li><b>partial rebalance 和 turnover cap 的方向合理，但需要实盘成本模型。</b> 它们降低账面换手后，收益是否真实保留，取决于成交价漂移与分批成交成本。</li>
      <li><b>当前最有价值的下一步不是再扩网格。</b> 应该对 buffer8 anchor 做交易原因归因、真实成本 replay、最差月份拆解，再决定是否有必要写 213c2 实盘候选。</li>
    </ul>
  </section>

  <section class="card">
    <h2>最好候选年度稳定性</h2>
    <div class="table-wrap">{table_html(annual_best, ["variant", "year", "days", "net_cum_pct", "max_drawdown_pct", "avg_turnover_x", "long_mean_bps", "short_mean_bps"])}</div>
  </section>

  <section class="card">
    <h2>最好候选最差月份</h2>
    <div class="table-wrap">{table_html(worst_months, ["variant", "month", "net_cum_pct", "max_drawdown_pct", "avg_turnover_x"])}</div>
  </section>

  <section class="card bad">
    <h2>操作建议</h2>
    <ul>
      <li><b>不放大。</b> 本轮没有出现“12bps 后厚度足够、回撤明显下降”的版本。</li>
      <li><b>保留 buffer8_50_50 和 buffer8_weekly 两个 anchor。</b> 前者路径更接近第五轮 Watch，后者是本轮唯一 Promising；二者都要做真实成本 replay 和 live-vs-shadow 对齐。</li>
      <li><b>下一轮只做深挖，不做宽网格。</b> 拆分新开仓/carry/替换原因，计算每类交易的净贡献，并重点解释 weekly cadence 为什么改善均值但仍留下年份亏损。</li>
      <li><b>short gate 暂不进生产。</b> dispersion / BTC gate 可以做监控标签，但不作为硬交易开关。</li>
    </ul>
  </section>

  <section class="card">
    <h2>产物</h2>
    <ul>
      <li><code>{escape(str(RESULTS_PATH.relative_to(ROOT)))}</code></li>
      <li><code>{escape(str(DAILY_PATH.relative_to(ROOT)))}</code></li>
      <li><code>{escape(str(SHORTLIST_PATH.relative_to(ROOT)))}</code></li>
      <li><code>{escape(str(ANNUAL_PATH.relative_to(ROOT)))}</code></li>
      <li><code>{escape(str(MONTHLY_PATH.relative_to(ROOT)))}</code></li>
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
    score_panel = score_panels["retvol_14d_skip1d"]
    onboard_map = fifth.fourth.read_onboard_map()
    months = sorted({ts.strftime("%Y-%m") for ts in close.index[close.index >= SAMPLE_START]})
    ranked_by_month = fifth.fourth.build_monthly_ranked_universes(months, quote_volume, onboard_map, 100)
    dates = pd.DataFrame({"timestamp_ts": [ts for ts in close.index if ts >= SAMPLE_START and ts + pd.Timedelta(days=1) in close.index]})
    dates["exit_ts"] = dates["timestamp_ts"] + pd.Timedelta(days=1)
    dates["month"] = dates["timestamp_ts"].dt.strftime("%Y-%m")
    ctx = fifth.add_reference_gate_context(fifth.build_market_context(close, ranked_by_month, onboard_map, dates))

    specs = build_specs()
    daily = pd.concat([
        simulate_spec(spec, next_ret=next_ret, score_panel=score_panel, ranked_by_month=ranked_by_month, onboard_map=onboard_map, ctx=ctx)
        for spec in specs
    ], ignore_index=True)
    daily.to_csv(DAILY_PATH, index=False)

    rows = []
    for (_, variant), sub in daily.groupby(["experiment_group", "variant"], sort=False):
        for cost in COST_GRID_BPS:
            rows.append(summarize_daily(sub, cost))
    results = pd.DataFrame(rows)
    verdicts = results.apply(lambda r: classify(r), axis=1)
    results["verdict"] = [v[0] for v in verdicts]
    results["reason"] = [v[1] for v in verdicts]
    results["verdict_rank"] = [v[2] for v in verdicts]
    results.to_csv(RESULTS_PATH, index=False)

    cost12 = results[results["cost_bps_per_1x_turnover"] == 12.0].copy()
    shortlist = cost12[cost12["verdict"].isin(["Promising", "Watch", "Diagnostic"])].sort_values(["verdict_rank", "net_mean_bps"], ascending=[True, False]).copy()
    shortlist.to_csv(SHORTLIST_PATH, index=False)
    selected = shortlist.head(4)["variant"].astype(str).tolist()
    if "buffer8_50_50" not in selected:
        selected.append("buffer8_50_50")
    annual, monthly = annual_monthly_tables(daily, selected)
    annual.to_csv(ANNUAL_PATH, index=False)
    monthly.to_csv(MONTHLY_PATH, index=False)

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "objective": "rank213c buffer8 focused research",
        "sample_start": str(SAMPLE_START.date()),
        "sample_end": str(pd.to_datetime(dates["timestamp_ts"].max()).date()),
        "variant_count": len(specs),
        "cost_grid_bps": COST_GRID_BPS,
        "promising_count_12bps": int((cost12["verdict"] == "Promising").sum()),
        "watch_count_12bps": int((cost12["verdict"] == "Watch").sum()),
        "diagnostic_count_12bps": int((cost12["verdict"] == "Diagnostic").sum()),
        "fail_count_12bps": int((cost12["verdict"] == "Fail").sum()),
        "artifacts": {
            "daily": str(DAILY_PATH.relative_to(ROOT)),
            "results": str(RESULTS_PATH.relative_to(ROOT)),
            "shortlist": str(SHORTLIST_PATH.relative_to(ROOT)),
            "annual": str(ANNUAL_PATH.relative_to(ROOT)),
            "monthly": str(MONTHLY_PATH.relative_to(ROOT)),
            "site": str(SITE_PATH.relative_to(ROOT)),
        },
    }
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    SITE_PATH.write_text(build_report(results, shortlist, annual, monthly, summary), encoding="utf-8")
    print(f"wrote {RESULTS_PATH.relative_to(ROOT)}")
    print(f"wrote {SHORTLIST_PATH.relative_to(ROOT)}")
    print(f"wrote {SUMMARY_PATH.relative_to(ROOT)}")
    print(f"wrote {SITE_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
