#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
SITE_PATH = ROOT / "reports" / "site" / "paper" / "rank213_age90_top50_4x4_execution_stability.html"
FOURTH_PAGE = ROOT / "reports" / "site" / "paper" / "rank213_age90_14d_fourth_round_benchmark_attribution.html"
FOURTH_SCRIPT_PATH = ROOT / "scripts" / "build_rank213_age90_14d_fourth_round_benchmark_attribution.py"

PARAM_DAILY_PATH = ART_DIR / "rank213_age90_14d_fourth_round_param_stability_daily.csv"

SUMMARY_PATH = ART_DIR / "rank213_age90_top50_4x4_execution_stability_summary.json"
DAILY_OUT = ART_DIR / "rank213_age90_top50_4x4_execution_stability_daily.csv"
FLAT_COST_OUT = ART_DIR / "rank213_age90_top50_4x4_execution_stability_flat_cost.csv"
TURNOVER_COST_OUT = ART_DIR / "rank213_age90_top50_4x4_execution_stability_turnover_cost.csv"
ANNUAL_OUT = ART_DIR / "rank213_age90_top50_4x4_execution_stability_annual.csv"
MONTHLY_OUT = ART_DIR / "rank213_age90_top50_4x4_execution_stability_monthly.csv"
ROLLING_OUT = ART_DIR / "rank213_age90_top50_4x4_execution_stability_rolling.csv"
STATE_OUT = ART_DIR / "rank213_age90_top50_4x4_execution_stability_state_slices.csv"
DISPERSION_OUT = ART_DIR / "rank213_age90_top50_4x4_execution_stability_dispersion_slices.csv"
SIDE_OUT = ART_DIR / "rank213_age90_top50_4x4_execution_stability_side.csv"

FLAT_COST_GRID_BPS = [0, 4, 8, 12, 16, 20, 30, 40]
TURNOVER_COST_GRID_BPS = [1, 2, 3, 4, 5, 6, 8, 10, 12]
UNIVERSE_SIZE = 50
LEG_COUNT = 4
BASE_FLAT_COST_BPS = 4.0


def load_fourth_module():
    spec = importlib.util.spec_from_file_location("rank213_fourth_mod", FOURTH_SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {FOURTH_SCRIPT_PATH}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["rank213_fourth_mod"] = mod
    spec.loader.exec_module(mod)
    return mod


fourth = load_fourth_module()


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


def compound(ret: pd.Series) -> float:
    return fourth.compound(ret)


def max_drawdown(ret: pd.Series) -> float:
    return fourth.max_drawdown(ret)


def stats(name: str, ret: pd.Series, active: pd.Series | None = None) -> dict:
    ret = pd.to_numeric(ret, errors="coerce").fillna(0.0)
    if active is None:
        active = pd.Series(True, index=ret.index)
    active = active.fillna(False).astype(bool)
    out = fourth.stats(name, ret)
    out["active_days"] = int(active.sum())
    out["active_rate_pct"] = float(active.mean() * 100.0) if len(active) else np.nan
    out["active_mean_bps"] = float(ret[active].mean() * 10000.0) if active.sum() else np.nan
    return out


def parse_symbols(text: object) -> list[str]:
    if pd.isna(text):
        return []
    return [x.strip().upper() for x in str(text).split(",") if x.strip()]


def target_weights(row: pd.Series) -> dict[str, float]:
    if not bool(row["active"]):
        return {}
    out = {}
    for sym in parse_symbols(row["longs"]):
        out[sym] = out.get(sym, 0.0) + 0.5 / LEG_COUNT
    for sym in parse_symbols(row["shorts"]):
        out[sym] = out.get(sym, 0.0) - 0.5 / LEG_COUNT
    return out


def turnover(prev: dict[str, float], cur: dict[str, float]) -> float:
    keys = set(prev) | set(cur)
    return float(sum(abs(cur.get(k, 0.0) - prev.get(k, 0.0)) for k in keys))


def read_top50_daily() -> pd.DataFrame:
    df = pd.read_csv(PARAM_DAILY_PATH)
    df = df[(df["universe_size"] == UNIVERSE_SIZE) & (df["leg_count"] == LEG_COUNT)].copy()
    df["timestamp_ts"] = pd.to_datetime(df["timestamp_ts"], utc=True, format="mixed")
    df["exit_ts"] = pd.to_datetime(df["exit_ts"], utc=True, format="mixed")
    for col in ["gross_ret", "net_ret_4bps", "long_avg_ret", "short_pnl_avg_ret", "short_raw_avg_ret", "btc_ret"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
    df["active"] = df["active"].astype(str).str.lower().isin(["true", "1", "yes"])
    df = df.sort_values("timestamp_ts").reset_index(drop=True)

    prev: dict[str, float] = {}
    turns = []
    gross_changed = []
    for _, row in df.iterrows():
        cur = target_weights(row)
        t = turnover(prev, cur)
        turns.append(t)
        gross_changed.append(bool(t > 1e-12))
        prev = cur
    df["target_turnover_x"] = turns
    df["target_changed"] = gross_changed
    df["long_half_contribution"] = 0.5 * df["long_avg_ret"]
    df["short_half_contribution"] = 0.5 * df["short_pnl_avg_ret"]
    df["net_flat_4bps"] = df["gross_ret"].where(df["active"], 0.0) - BASE_FLAT_COST_BPS / 10000.0 * df["active"].astype(float)
    return df


def add_market_diagnostics(daily: pd.DataFrame) -> pd.DataFrame:
    _, quote_volume = fourth.load_close_quote_panels()
    onboard = fourth.read_onboard_map()
    ranked = fourth.build_monthly_ranked_universes(daily["month"].astype(str).tolist(), quote_volume, onboard, UNIVERSE_SIZE)
    price_cache: dict[str, pd.Series | None] = {}
    rows = []
    for _, row in daily.iterrows():
        ts = row["timestamp_ts"]
        exit_ts = row["exit_ts"]
        month = str(row["month"])
        universe = ranked.get(month, [])[:UNIVERSE_SIZE]
        eligible = [
            sym for sym in universe
            if sym in onboard and ts - onboard[sym] >= pd.Timedelta(days=fourth.AGE_DAYS)
        ]
        estats = fourth.symbol_return_stats(eligible, ts, exit_ts, price_cache)
        rows.append({
            "timestamp_ts": ts,
            "top50_eligible_ew_ret": estats["mean"],
            "top50_eligible_dispersion_p90_p10": estats["p90_p10"],
            "top50_eligible_dispersion_std": estats["std"],
            "top50_eligible_count_rebuilt": len(eligible),
            "top50_eligible_price_coverage_pct": estats["ok"] / estats["total"] * 100.0 if estats["total"] else np.nan,
        })
    diag = pd.DataFrame(rows)
    out = daily.merge(diag, on="timestamp_ts", how="left")
    out["top50_eligible_abs_ret"] = out["top50_eligible_ew_ret"].abs()
    out["btc_abs_ret"] = out["btc_ret"].abs()
    out["prior30_btc_vol"] = out["btc_ret"].shift(1).rolling(30, min_periods=20).std()
    out["prior30_top50_eligible_vol"] = out["top50_eligible_ew_ret"].shift(1).rolling(30, min_periods=20).std()
    out["prior30_top50_dispersion"] = out["top50_eligible_dispersion_p90_p10"].shift(1).rolling(30, min_periods=20).mean()
    return out


def build_flat_cost(daily: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cost in FLAT_COST_GRID_BPS:
        ret = daily["gross_ret"].where(daily["active"], 0.0) - cost / 10000.0 * daily["active"].astype(float)
        row = stats(f"flat_cost_{cost}bps_per_day", ret, daily["active"])
        row["cost_bps_per_active_day"] = cost
        rows.append(row)
    return pd.DataFrame(rows)


def build_turnover_cost(daily: pd.DataFrame) -> pd.DataFrame:
    rows = []
    active = daily["active"]
    for cost in TURNOVER_COST_GRID_BPS:
        ret = daily["gross_ret"].where(active, 0.0) - cost / 10000.0 * daily["target_turnover_x"]
        row = stats(f"turnover_cost_{cost}bps_per_1x_turnover", ret, active)
        row["cost_bps_per_1x_turnover"] = cost
        row["avg_turnover_x"] = float(daily["target_turnover_x"].mean())
        row["active_avg_turnover_x"] = float(daily.loc[active, "target_turnover_x"].mean())
        row["implied_avg_daily_cost_bps"] = float(cost * daily["target_turnover_x"].mean())
        rows.append(row)
    return pd.DataFrame(rows)


def build_annual(daily: pd.DataFrame) -> pd.DataFrame:
    rows = []
    work = daily.copy()
    work["year"] = work["timestamp_ts"].dt.year
    for year, sub in work.groupby("year"):
        rows.append({
            "year": int(year),
            "days": int(len(sub)),
            "active_days": int(sub["active"].sum()),
            "net_flat_4bps_pct": compound(sub["net_flat_4bps"]) * 100.0,
            "gross_pct": compound(sub["gross_ret"]) * 100.0,
            "long_half_pct": compound(sub["long_half_contribution"]) * 100.0,
            "short_half_pct": compound(sub["short_half_contribution"]) * 100.0,
            "long_half_mean_bps": float(sub["long_half_contribution"].mean() * 10000.0),
            "short_half_mean_bps": float(sub["short_half_contribution"].mean() * 10000.0),
            "avg_turnover_x": float(sub["target_turnover_x"].mean()),
            "btc_pct": compound(sub["btc_ret"]) * 100.0,
            "top50_eligible_ew_pct": compound(sub["top50_eligible_ew_ret"]) * 100.0,
        })
    return pd.DataFrame(rows)


def build_monthly(daily: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for month, sub in daily.groupby("month"):
        rows.append({
            "month": str(month),
            "days": int(len(sub)),
            "active_days": int(sub["active"].sum()),
            "net_flat_4bps_pct": compound(sub["net_flat_4bps"]) * 100.0,
            "gross_pct": compound(sub["gross_ret"]) * 100.0,
            "max_drawdown_pct": max_drawdown(sub["net_flat_4bps"]) * 100.0,
            "win_rate_pct": float((sub["net_flat_4bps"] > 0).mean() * 100.0),
            "long_half_mean_bps": float(sub["long_half_contribution"].mean() * 10000.0),
            "short_half_mean_bps": float(sub["short_half_contribution"].mean() * 10000.0),
            "avg_turnover_x": float(sub["target_turnover_x"].mean()),
        })
    return pd.DataFrame(rows).sort_values("month")


def build_rolling(monthly: pd.DataFrame) -> pd.DataFrame:
    rows = []
    work = monthly.copy()
    work["month_ret"] = work["net_flat_4bps_pct"] / 100.0
    for window in [6, 12, 24]:
        for i in range(window - 1, len(work)):
            sub = work.iloc[i - window + 1:i + 1]
            rows.append({
                "window_months": window,
                "end_month": sub.iloc[-1]["month"],
                "net_cum_pct": compound(sub["month_ret"]) * 100.0,
                "positive_month_rate_pct": float((sub["month_ret"] > 0).mean() * 100.0),
                "worst_month_pct": float(sub["net_flat_4bps_pct"].min()),
                "avg_monthly_pct": float(sub["net_flat_4bps_pct"].mean()),
            })
    return pd.DataFrame(rows)


def slice_row(group: str, name: str, sub: pd.DataFrame, total: int) -> dict:
    row = stats(name, sub["net_flat_4bps"], sub["active"])
    row["slice_group"] = group
    row["slice"] = name
    row["days"] = int(len(sub))
    row["active_rate_pct"] = float(len(sub) / total * 100.0) if total else np.nan
    row["long_half_mean_bps"] = float(sub["long_half_contribution"].mean() * 10000.0) if len(sub) else np.nan
    row["short_half_mean_bps"] = float(sub["short_half_contribution"].mean() * 10000.0) if len(sub) else np.nan
    row["avg_turnover_x"] = float(sub["target_turnover_x"].mean()) if len(sub) else np.nan
    row["btc_mean_bps"] = float(sub["btc_ret"].mean() * 10000.0) if len(sub) else np.nan
    row["top50_eligible_ew_mean_bps"] = float(sub["top50_eligible_ew_ret"].mean() * 10000.0) if len(sub) else np.nan
    row["dispersion_mean_bps"] = float(sub["top50_eligible_dispersion_p90_p10"].mean() * 10000.0) if len(sub) else np.nan
    row["prior30_dispersion_mean_bps"] = float(sub["prior30_top50_dispersion"].mean() * 10000.0) if len(sub) else np.nan
    return row


def tercile_masks(s: pd.Series) -> list[tuple[str, pd.Series]]:
    valid = pd.to_numeric(s, errors="coerce").dropna()
    q1, q2 = valid.quantile([1 / 3, 2 / 3])
    return [
        ("low", s <= q1),
        ("mid", (s > q1) & (s <= q2)),
        ("high", s > q2),
    ]


def build_state_slices(daily: pd.DataFrame) -> pd.DataFrame:
    rows = []
    total = len(daily)
    masks = [
        ("top50_eligible_EW_state", "big_up_>3pct", daily["top50_eligible_ew_ret"] > 0.03),
        ("top50_eligible_EW_state", "flat_abs_<=1pct", daily["top50_eligible_ew_ret"].abs() <= 0.01),
        ("top50_eligible_EW_state", "big_down_<-3pct", daily["top50_eligible_ew_ret"] < -0.03),
        ("BTC_realized_move", "abs_<=1pct", daily["btc_abs_ret"] <= 0.01),
        ("BTC_realized_move", "abs_1pct_to_3pct", (daily["btc_abs_ret"] > 0.01) & (daily["btc_abs_ret"] <= 0.03)),
        ("BTC_realized_move", "abs_>3pct", daily["btc_abs_ret"] > 0.03),
    ]
    for group, name, mask in masks:
        rows.append(slice_row(group, name, daily[mask.fillna(False)], total))
    for name, mask in tercile_masks(daily["prior30_btc_vol"]):
        rows.append(slice_row("BTC_prior30_vol_causal_tercile", name, daily[mask.fillna(False)], total))
    for name, mask in tercile_masks(daily["prior30_top50_dispersion"]):
        rows.append(slice_row("top50_prior30_dispersion_causal_tercile", name, daily[mask.fillna(False)], total))
    return pd.DataFrame(rows)


def build_dispersion_slices(daily: pd.DataFrame) -> pd.DataFrame:
    rows = []
    total = len(daily)
    for name, mask in tercile_masks(daily["top50_eligible_dispersion_p90_p10"]):
        rows.append(slice_row("same_day_top50_dispersion_diagnostic", name, daily[mask.fillna(False)], total))
    for name, mask in tercile_masks(daily["prior30_top50_dispersion"]):
        rows.append(slice_row("prior30_top50_dispersion_causal_proxy", name, daily[mask.fillna(False)], total))
    return pd.DataFrame(rows)


def build_side(daily: pd.DataFrame) -> pd.DataFrame:
    rows = [
        stats("dollar_neutral_top50_4x4_flat4bps", daily["net_flat_4bps"], daily["active"]),
        stats("gross_no_cost", daily["gross_ret"], daily["active"]),
        stats("half_cap_long_contribution", daily["long_half_contribution"], daily["active"]),
        stats("half_cap_short_contribution", daily["short_half_contribution"], daily["active"]),
        stats("full_cap_long_only_minus_4bps", daily["long_avg_ret"] - BASE_FLAT_COST_BPS / 10000.0, daily["active"]),
        stats("full_cap_short_only_minus_4bps", daily["short_pnl_avg_ret"] - BASE_FLAT_COST_BPS / 10000.0, daily["active"]),
    ]
    return pd.DataFrame(rows)


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
            if c.endswith("_pct") or c in {"cum_pct", "max_drawdown_pct", "win_rate_pct", "active_rate_pct", "daily_vol_pct", "net_cum_pct"}:
                txt = fmt_pct(v)
            elif c.endswith("_bps") or c in {"mean_bps", "active_mean_bps", "implied_avg_daily_cost_bps"}:
                txt = fmt_bps(v)
            elif isinstance(v, float):
                txt = fmt_num(v, 3)
            else:
                txt = escape(str(v))
            cells.append(f"<td>{txt}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def equity_svg(daily: pd.DataFrame) -> str:
    width, height = 1100, 360
    left, right, top, bottom = 70, 25, 28, 54
    plot_w = width - left - right
    plot_h = height - top - bottom
    work = daily.sort_values("timestamp_ts").copy()
    work["equity"] = (1.0 + work["net_flat_4bps"]).cumprod()
    ts_min, ts_max = work["timestamp_ts"].min(), work["timestamp_ts"].max()
    x_span = max((ts_max - ts_min).total_seconds(), 1.0)
    y = np.log(work["equity"].clip(lower=1e-6))
    y_min, y_max = float(y.min()), float(y.max())

    def xy(ts: pd.Timestamp, eq: float) -> tuple[float, float]:
        x = left + ((ts - ts_min).total_seconds() / x_span) * plot_w
        yy = top + (1.0 - ((np.log(max(eq, 1e-6)) - y_min) / (y_max - y_min))) * plot_h
        return x, yy

    pts = [xy(r["timestamp_ts"], float(r["equity"])) for _, r in work.iterrows()]
    path = " ".join(("M" if i == 0 else "L") + f"{x:.2f},{yy:.2f}" for i, (x, yy) in enumerate(pts))
    years = []
    for year in range(ts_min.year, ts_max.year + 1):
        ts = pd.Timestamp(f"{year}-01-01T00:00:00Z")
        if ts_min <= ts <= ts_max:
            x = left + ((ts - ts_min).total_seconds() / x_span) * plot_w
            years.append(f"<line x1='{x:.1f}' y1='{top}' x2='{x:.1f}' y2='{top+plot_h}' stroke='#f1f5f9'/><text x='{x:.1f}' y='{height-28}' text-anchor='middle'>{year}</text>")
    return f"""
<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="top50 4x4 equity">
  <rect x="0" y="0" width="{width}" height="{height}" rx="18" fill="#fff"/>
  <g font-family="Noto Sans SC, Microsoft YaHei, sans-serif" font-size="13" fill="#475569">
    {''.join(years)}
    <line x1="{left}" y1="{top+plot_h}" x2="{width-right}" y2="{top+plot_h}" stroke="#cbd5e1"/>
    <line x1="{left}" y1="{top}" x2="{left}" y2="{top+plot_h}" stroke="#cbd5e1"/>
    <path d="{path}" fill="none" stroke="#0f766e" stroke-width="2.6"/>
    <text x="{left}" y="20" font-size="15" font-weight="700" fill="#172033">Top50 4L4S net equity, flat 4bps（log scale）</text>
  </g>
</svg>
"""


def build_report(
    daily: pd.DataFrame,
    flat_cost: pd.DataFrame,
    turnover_cost: pd.DataFrame,
    annual: pd.DataFrame,
    monthly: pd.DataFrame,
    rolling: pd.DataFrame,
    state: pd.DataFrame,
    dispersion: pd.DataFrame,
    side: pd.DataFrame,
    summary: dict,
) -> str:
    base = flat_cost[flat_cost["cost_bps_per_active_day"] == 4].iloc[0]
    flat12 = flat_cost[flat_cost["cost_bps_per_active_day"] == 12].iloc[0]
    turn4 = turnover_cost[turnover_cost["cost_bps_per_1x_turnover"] == 4].iloc[0]
    turn8 = turnover_cost[turnover_cost["cost_bps_per_1x_turnover"] == 8].iloc[0]
    positive_month_rate = float((monthly["net_flat_4bps_pct"] > 0).mean() * 100.0)
    worst_months = monthly.sort_values("net_flat_4bps_pct").head(8)
    best_months = monthly.sort_values("net_flat_4bps_pct", ascending=False).head(8)
    generated = pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank213 age90 Top50 4x4 执行成本与稳定性</title>
  <style>
    body {{ margin:0; background:#f3efe6; color:#172033; font-family:"Noto Sans SC","Source Han Sans SC","PingFang SC","Microsoft YaHei",sans-serif; line-height:1.65; }}
    main {{ max-width:1180px; margin:0 auto; padding:28px 16px 56px; }}
    .card {{ background:#fff; border:1px solid #e6dccb; border-radius:16px; padding:18px 20px; margin:14px 0; box-shadow:0 1px 2px rgba(20,24,31,.04); }}
    .hero {{ background:linear-gradient(135deg,#ecfdf5,#fff 55%,#fff7ed); border-color:#6ee7b7; }}
    .warn {{ background:#fff7ed; border-color:#fdba74; }}
    .good {{ background:#f0fdf4; border-color:#bbf7d0; }}
    .grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; }}
    .metric {{ background:#f8fafc; border:1px solid #e2e8f0; border-radius:14px; padding:12px; }}
    .metric b {{ display:block; font-size:22px; line-height:1.2; }}
    .muted {{ color:#64748b; }}
    .table-wrap {{ overflow-x:auto; }}
    table {{ border-collapse:collapse; min-width:940px; width:100%; }}
    th,td {{ border-bottom:1px solid #e2e8f0; padding:8px 10px; text-align:right; vertical-align:top; font-size:14px; }}
    th {{ background:#f8fafc; color:#475569; }}
    td:first-child,th:first-child,td:nth-child(2),th:nth-child(2) {{ text-align:left; }}
    .chart {{ width:100%; height:auto; border:1px solid #e2e8f0; border-radius:18px; background:#fff; margin:8px 0; }}
    code {{ background:#f1f5f9; border-radius:6px; padding:2px 6px; }}
    a {{ color:#2563eb; text-decoration:none; }}
    @media (max-width:760px) {{ .grid {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
<main>
  <section class="card hero">
    <h1>Top50 + 4L4S 执行成本与稳定性验证</h1>
    <p>对象：<code>rank213_age90_14d_skip1d_voladj</code>，每月用上一完整月 quote volume 选 Top50，age ≥ 90d，日频 4 long + 4 short。</p>
    <p class="muted">生成时间：{escape(generated)}。本页是第四轮扩展，不改变信号公式，只检查 Top50 4x4 是否能承受成本和时间稳定性。</p>
    <p><a href="/momentum/paper/rank213_age90_14d_fifth_round_profit_thickness.html">第五轮：真实成本利润厚度</a> · <a href="/momentum/paper/rank213_age90_14d_fourth_round_benchmark_attribution.html">返回第四轮主报告</a> · <a href="/momentum/paper/rank213_age90_14d_phase3_validation.html">Phase 3</a></p>
  </section>

  <section class="card warn">
    <h2>结论</h2>
    <p><b>Top50 4x4 目前是最值得继续研究的版本，但不是“已可放大上线”。</b> flat 4bps 下累计 {fmt_pct(base['cum_pct'])}、最大回撤 {fmt_pct(base['max_drawdown_pct'])}、均值 {fmt_bps(base['mean_bps'])}；flat 12bps 后仍有 {fmt_pct(flat12['cum_pct'])}，说明它比 Top30 3x3 更能承受成本。</p>
    <p>更现实的 turnover cost 下，平均目标换手约 {fmt_num(summary['avg_turnover_x'], 3)}x/day。若按每 1x turnover 4bps 计，累计 {fmt_pct(turn4['cum_pct'])}；8bps 计仍为 {fmt_pct(turn8['cum_pct'])}。这说明它不是只靠 4bps 乐观假设活着，但真实 maker/taker、滑点和 funding 仍必须实盘验证。</p>
  </section>

  <section class="card">
    <h2>给新研究者的读法</h2>
    <ul>
      <li><b>本页回答的问题：</b>为什么 213c 采用 Top50 4L4S，以及它在成本、年份和市场状态维度是否稳定。</li>
      <li><b>先看成本阶梯。</b> flat cost 适合快速比较版本，turnover cost 更接近实盘。二者结论一致时，证据更强。</li>
      <li><b>再看年度稳定性。</b> 如果收益只集中在某一年，策略更像行情偶然。本页重点确认 213c 没有明显只靠单一年份。</li>
      <li><b>最后看 Long / Short 贡献。</b> 213c 的 long half 是主要收益来源；short half 为正但很薄，因此后续研究不能只追求更多做空。</li>
      <li><b>本页边界：</b>它证明 Top50 4x4 是当前最强结构，但还没有证明真实成交成本下可以放大。</li>
    </ul>
  </section>

  <section class="card">
    <h2>核心指标</h2>
    <div class="grid">
      <div class="metric"><b>{fmt_pct(base['cum_pct'])}</b><span>flat 4bps 累计净收益</span></div>
      <div class="metric"><b>{fmt_pct(base['max_drawdown_pct'])}</b><span>flat 4bps 最大回撤</span></div>
      <div class="metric"><b>{fmt_bps(base['mean_bps'])}</b><span>flat 4bps 日均</span></div>
      <div class="metric"><b>{fmt_pct(positive_month_rate)}</b><span>正收益月占比</span></div>
    </div>
    {equity_svg(daily)}
  </section>

  <section class="card">
    <h2>Flat 成本阶梯</h2>
    <p class="muted">直接从 daily gross 扣固定 bps/active day。它方便比较，但没有反映换手差异。</p>
    <div class="table-wrap">{table_html(flat_cost, ["cost_bps_per_active_day", "active_days", "mean_bps", "cum_pct", "max_drawdown_pct", "win_rate_pct", "daily_vol_pct"])}</div>
  </section>

  <section class="card">
    <h2>换手成本阶梯</h2>
    <p>每日根据 8 条腿目标权重计算 turnover：<code>sum(abs(w_t - w_{{t-1}}))</code>。全换仓接近 2x，部分持仓延续则低于 2x。</p>
    <div class="table-wrap">{table_html(turnover_cost, ["cost_bps_per_1x_turnover", "avg_turnover_x", "implied_avg_daily_cost_bps", "mean_bps", "cum_pct", "max_drawdown_pct", "win_rate_pct"])}</div>
  </section>

  <section class="card">
    <h2>Long / Short 贡献</h2>
    <p class="muted">Top50 4x4 的收益仍主要来自 long half；short half 平均为正，但贡献较薄。</p>
    <div class="table-wrap">{table_html(side, ["series", "mean_bps", "cum_pct", "max_drawdown_pct", "win_rate_pct", "active_days"])}</div>
  </section>

  <section class="card">
    <h2>年度稳定性</h2>
    <div class="table-wrap">{table_html(annual, ["year", "days", "net_flat_4bps_pct", "gross_pct", "long_half_pct", "short_half_pct", "long_half_mean_bps", "short_half_mean_bps", "avg_turnover_x", "btc_pct", "top50_eligible_ew_pct"])}</div>
  </section>

  <section class="card">
    <h2>月度与滚动窗口</h2>
    <p class="muted">重点看收益是否集中在少数月份，以及 6/12/24 个月窗口是否反复失效。</p>
    <h3>最佳月份</h3>
    <div class="table-wrap">{table_html(best_months, ["month", "net_flat_4bps_pct", "max_drawdown_pct", "win_rate_pct", "long_half_mean_bps", "short_half_mean_bps", "avg_turnover_x"])}</div>
    <h3>最差月份</h3>
    <div class="table-wrap">{table_html(worst_months, ["month", "net_flat_4bps_pct", "max_drawdown_pct", "win_rate_pct", "long_half_mean_bps", "short_half_mean_bps", "avg_turnover_x"])}</div>
    <h3>最近滚动窗口</h3>
    <div class="table-wrap">{table_html(rolling.tail(36), ["window_months", "end_month", "net_cum_pct", "positive_month_rate_pct", "worst_month_pct", "avg_monthly_pct"])}</div>
  </section>

  <section class="card">
    <h2>市场状态 / 离散度</h2>
    <p class="muted">same-day dispersion 是事后诊断，prior30 dispersion 才是可交易 proxy。</p>
    <h3>市场状态</h3>
    <div class="table-wrap">{table_html(state, ["slice_group", "slice", "days", "mean_bps", "cum_pct", "max_drawdown_pct", "long_half_mean_bps", "short_half_mean_bps", "avg_turnover_x", "dispersion_mean_bps", "prior30_dispersion_mean_bps"])}</div>
    <h3>横截面离散度</h3>
    <div class="table-wrap">{table_html(dispersion, ["slice_group", "slice", "days", "mean_bps", "cum_pct", "max_drawdown_pct", "long_half_mean_bps", "short_half_mean_bps", "avg_turnover_x", "dispersion_mean_bps", "prior30_dispersion_mean_bps"])}</div>
  </section>

  <section class="card good">
    <h2>下一步应用建议</h2>
    <ul>
      <li>Top50 4x4 可以进入更严格的 paper/live parity 研究，但真钱规模不要放大，先用 tiny-live 验证真实成交成本。</li>
      <li>优先补 maker/taker fill、fallback market、exit slippage、funding 后的真实净收益；如果 turnover cost 接近 8-12bps/1x turnover，它仍可能活，但空间会明显收窄。</li>
      <li>保留 Top20/30 3x3 作为保守备选；Top50 4x4 是当前研究最强版本，不应直接替换成 long-only 或 Top100。</li>
    </ul>
  </section>
</main>
</body>
</html>
"""


def patch_fourth_entry() -> None:
    if not FOURTH_PAGE.exists():
        return
    text = FOURTH_PAGE.read_text(encoding="utf-8")
    href = "/momentum/paper/rank213_age90_top50_4x4_execution_stability.html"
    if href in text:
        return
    marker = '<p><a href="/momentum/paper/rank213_age90_14d_phase3_validation.html">Phase 3</a>'
    insert = f'<p><a href="{href}">Top50 4x4 执行成本与稳定性验证</a></p>\n    '
    text = text.replace(marker, insert + marker, 1)
    FOURTH_PAGE.write_text(text, encoding="utf-8")


def main() -> int:
    daily = add_market_diagnostics(read_top50_daily())
    flat_cost = build_flat_cost(daily)
    turnover_cost = build_turnover_cost(daily)
    annual = build_annual(daily)
    monthly = build_monthly(daily)
    rolling = build_rolling(monthly)
    state = build_state_slices(daily)
    dispersion = build_dispersion_slices(daily)
    side = build_side(daily)
    summary = {
        "generated_at_utc": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ"),
        "strategy": "rank213_age90_14d_skip1d_voladj_top50_4x4",
        "rows": int(len(daily)),
        "active_days": int(daily["active"].sum()),
        "avg_turnover_x": float(daily["target_turnover_x"].mean()),
        "active_avg_turnover_x": float(daily.loc[daily["active"], "target_turnover_x"].mean()),
        "avg_top50_eligible_count": float(daily["top50_eligible_count_rebuilt"].mean()),
        "flat4_cum_pct": float(flat_cost[flat_cost["cost_bps_per_active_day"] == 4]["cum_pct"].iloc[0]),
        "flat4_max_drawdown_pct": float(flat_cost[flat_cost["cost_bps_per_active_day"] == 4]["max_drawdown_pct"].iloc[0]),
        "turnover4_cum_pct": float(turnover_cost[turnover_cost["cost_bps_per_1x_turnover"] == 4]["cum_pct"].iloc[0]),
        "artifacts": {
            "daily": str(DAILY_OUT.relative_to(ROOT)),
            "flat_cost": str(FLAT_COST_OUT.relative_to(ROOT)),
            "turnover_cost": str(TURNOVER_COST_OUT.relative_to(ROOT)),
            "annual": str(ANNUAL_OUT.relative_to(ROOT)),
            "monthly": str(MONTHLY_OUT.relative_to(ROOT)),
            "rolling": str(ROLLING_OUT.relative_to(ROOT)),
            "state": str(STATE_OUT.relative_to(ROOT)),
            "dispersion": str(DISPERSION_OUT.relative_to(ROOT)),
            "side": str(SIDE_OUT.relative_to(ROOT)),
            "site": str(SITE_PATH.relative_to(ROOT)),
        },
    }

    daily.to_csv(DAILY_OUT, index=False)
    flat_cost.to_csv(FLAT_COST_OUT, index=False)
    turnover_cost.to_csv(TURNOVER_COST_OUT, index=False)
    annual.to_csv(ANNUAL_OUT, index=False)
    monthly.to_csv(MONTHLY_OUT, index=False)
    rolling.to_csv(ROLLING_OUT, index=False)
    state.to_csv(STATE_OUT, index=False)
    dispersion.to_csv(DISPERSION_OUT, index=False)
    side.to_csv(SIDE_OUT, index=False)
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    SITE_PATH.write_text(build_report(daily, flat_cost, turnover_cost, annual, monthly, rolling, state, dispersion, side, summary), encoding="utf-8")
    patch_fourth_entry()
    print(f"wrote {SUMMARY_PATH.relative_to(ROOT)}")
    print(f"wrote {SITE_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
