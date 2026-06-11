#!/usr/bin/env python3
from __future__ import annotations

import math
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_intraday_tsmom_session_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_intraday_tsmom_session_15m"
REPORT_PATH = SITE_DIR / "report.html"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}

COSTS = [6.0, 10.0, 15.0, 20.0]
PRIMARY_COST = 6.0
PRIMARY_THRESHOLD = 0.60
PRIMARY_SESSION = "funding_8h"
LEAD_BARS = 2
TAIL_BARS = 2
TIME_STABILITY_BUCKETS = 3

VARIANTS = [
    {"variant": "utc_day_q50", "session_mode": "utc_day", "abs_quantile": 0.50},
    {"variant": "utc_day_q60", "session_mode": "utc_day", "abs_quantile": 0.60},
    {"variant": "utc_day_q70", "session_mode": "utc_day", "abs_quantile": 0.70},
    {"variant": "funding_8h_q50", "session_mode": "funding_8h", "abs_quantile": 0.50},
    {"variant": "funding_8h_q60", "session_mode": "funding_8h", "abs_quantile": 0.60},
    {"variant": "funding_8h_q70", "session_mode": "funding_8h", "abs_quantile": 0.70},
]


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def pct(value: float | int | None, digits: int = 2) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value) * 100:.{digits}f}%"


def num(value: float | int | None, digits: int = 2) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value):.{digits}f}"


def fmt_ts(ts) -> str:
    if ts is None or pd.isna(ts):
        return "-"
    return pd.to_datetime(ts, utc=True).strftime("%Y-%m-%d %H:%M UTC")


def render_table(df: pd.DataFrame, *, percent_cols: set[str], digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    digits_cols = digits_cols or {}
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    body = []
    for _, row in df.iterrows():
        tds = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value)
            elif isinstance(value, (float, np.floating, int, np.integer)) and not isinstance(value, bool):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = str(value)
            tds.append(f"<td>{escape(text)}</td>")
        body.append(f"<tr>{''.join(tds)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def load_cached_bars(symbol: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df.sort_values("timestamp").reset_index(drop=True)


def attach_sessions(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    ts = out["timestamp"]
    out["utc_day_session"] = ts.dt.floor("1D")
    funding_hour = (ts.dt.hour // 8) * 8
    out["funding_8h_session"] = ts.dt.floor("1D") + pd.to_timedelta(funding_hour, unit="h")
    out["bar_idx_in_day"] = ((ts - out["utc_day_session"]).dt.total_seconds() // 900).astype(int)
    out["bar_idx_in_8h"] = ((ts - out["funding_8h_session"]).dt.total_seconds() // 900).astype(int)
    return out


def build_session_rows(asset: str, symbol: str, bars: pd.DataFrame, session_mode: str) -> pd.DataFrame:
    session_col = "utc_day_session" if session_mode == "utc_day" else "funding_8h_session"
    rows: list[dict] = []
    grouped = bars.groupby(session_col, sort=True)
    for session_start, g in grouped:
        g = g.sort_values("timestamp").reset_index(drop=True)
        if len(g) < LEAD_BARS + TAIL_BARS:
            continue
        lead = g.iloc[:LEAD_BARS]
        tail = g.iloc[-TAIL_BARS:]
        lead_ret = float(lead.iloc[-1]["close"] / lead.iloc[0]["open"] - 1.0)
        tail_entry_price = float(tail.iloc[0]["open"])
        tail_exit_price = float(tail.iloc[-1]["close"])
        tail_ret_long = float(tail_exit_price / tail_entry_price - 1.0)
        rows.append(
            {
                "asset": asset,
                "symbol": symbol,
                "session_mode": session_mode,
                "session_start": session_start,
                "session_end": g.iloc[-1]["timestamp"],
                "bars_in_session": int(len(g)),
                "lead_ret": lead_ret,
                "abs_lead_ret": abs(lead_ret),
                "signal_side": "long" if lead_ret > 0 else "short" if lead_ret < 0 else "flat",
                "lead_start_ts": lead.iloc[0]["timestamp"],
                "lead_end_ts": lead.iloc[-1]["timestamp"],
                "tail_entry_ts": tail.iloc[0]["timestamp"],
                "tail_exit_ts": tail.iloc[-1]["timestamp"],
                "tail_entry_price": tail_entry_price,
                "tail_exit_price": tail_exit_price,
                "tail_ret_long": tail_ret_long,
                "tail_ret_short": float(-tail_ret_long),
                "full_session_ret": float(g.iloc[-1]["close"] / g.iloc[0]["open"] - 1.0),
            }
        )
    return pd.DataFrame(rows)


def filter_variant_events(session_df: pd.DataFrame, *, abs_quantile: float, variant: str) -> pd.DataFrame:
    if session_df.empty:
        return session_df.copy()
    out = session_df.copy().sort_values("session_start").reset_index(drop=True)
    threshold = float(out["abs_lead_ret"].quantile(abs_quantile))
    out["abs_lead_threshold"] = threshold
    out = out[(out["signal_side"] != "flat") & (out["abs_lead_ret"] >= threshold)].copy()
    out["variant"] = variant
    return out.reset_index(drop=True)


def simulate_variant(events: pd.DataFrame, *, cost_bps_per_side: float) -> pd.DataFrame:
    if events.empty:
        return events.copy()
    out = events.copy()
    out["gross_ret"] = np.where(out["signal_side"] == "long", out["tail_ret_long"], out["tail_ret_short"])
    cost_rate = float(cost_bps_per_side) / 10000.0
    out["net_ret"] = (1.0 + out["gross_ret"]) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
    out["win"] = (out["net_ret"] > 0).astype(int)
    out["cost_bps_per_side"] = float(cost_bps_per_side)
    out["holding_bars"] = TAIL_BARS
    out["correct_direction"] = (
        ((out["signal_side"] == "long") & (out["tail_ret_long"] > 0))
        | ((out["signal_side"] == "short") & (out["tail_ret_long"] < 0))
    ).astype(int)
    return out


def summarize_asset_variant(trades: pd.DataFrame, asset: str, variant: str, cost: float) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame([
            {
                "asset": asset,
                "variant": variant,
                "cost_bps_per_side": cost,
                "trades": 0,
                "win_rate": np.nan,
                "direction_hit_rate": np.nan,
                "avg_net_ret": np.nan,
                "median_net_ret": np.nan,
                "total_return": 0.0,
                "positive_session_ratio": np.nan,
                "mean_abs_lead_ret": np.nan,
            }
        ])
    return pd.DataFrame([
        {
            "asset": asset,
            "variant": variant,
            "cost_bps_per_side": cost,
            "trades": int(len(trades)),
            "win_rate": float(trades["win"].mean()),
            "direction_hit_rate": float(trades["correct_direction"].mean()),
            "avg_net_ret": float(trades["net_ret"].mean()),
            "median_net_ret": float(trades["net_ret"].median()),
            "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
            "positive_session_ratio": float((trades["net_ret"] > 0).mean()),
            "mean_abs_lead_ret": float(trades["abs_lead_ret"].mean()),
        }
    ])


def build_variant_aggregate(asset_summary: pd.DataFrame) -> pd.DataFrame:
    if asset_summary.empty:
        return pd.DataFrame()
    out = (
        asset_summary.groupby(["variant", "cost_bps_per_side"], as_index=False)
        .agg(
            assets_tested=("asset", "nunique"),
            positive_assets=("total_return", lambda s: int((s > 0).sum())),
            mean_total_return=("total_return", "mean"),
            median_total_return=("total_return", "median"),
            mean_win_rate=("win_rate", "mean"),
            mean_direction_hit_rate=("direction_hit_rate", "mean"),
            mean_trades=("trades", "mean"),
            min_trades=("trades", "min"),
        )
        .sort_values(["cost_bps_per_side", "mean_total_return"], ascending=[True, False])
        .reset_index(drop=True)
    )
    out["positive_asset_ratio"] = out["positive_assets"] / out["assets_tested"].replace(0, np.nan)
    return out


def pick_primary(variant_aggregate: pd.DataFrame) -> pd.Series | None:
    hit = variant_aggregate[
        (variant_aggregate["variant"] == f"{PRIMARY_SESSION}_q{int(PRIMARY_THRESHOLD * 100)}")
        & (variant_aggregate["cost_bps_per_side"] == PRIMARY_COST)
    ]
    if hit.empty:
        return None
    return hit.iloc[0]


def build_time_stability(primary_trades: pd.DataFrame) -> pd.DataFrame:
    cols = ["gate", "status", "actual", "threshold", "why_it_matters"]
    if primary_trades.empty or len(primary_trades) < 9:
        return pd.DataFrame(columns=cols)
    df = primary_trades.copy().sort_values("session_start").reset_index(drop=True)
    df["bucket"] = pd.qcut(np.arange(len(df)), TIME_STABILITY_BUCKETS, labels=["early", "mid", "late"])
    bucket_stats = []
    for bucket, g in df.groupby("bucket", observed=False):
        if g.empty:
            continue
        asset_totals = g.groupby("asset")["net_ret"].apply(lambda s: float((1.0 + s).prod() - 1.0))
        bucket_stats.append(
            {
                "bucket": str(bucket),
                "trades": int(len(g)),
                "positive_assets": int((asset_totals > 0).sum()),
                "assets": int(asset_totals.size),
                "mean_asset_return": float(asset_totals.mean()),
            }
        )
    bdf = pd.DataFrame(bucket_stats)
    if bdf.empty:
        return pd.DataFrame(columns=cols)
    positive_buckets = int((bdf["mean_asset_return"] > 0).sum())
    rows = [
        {
            "gate": "positive_bucket_floor",
            "status": "pass" if positive_buckets >= 2 else "fail",
            "actual": f"{positive_buckets}/3 positive buckets",
            "threshold": ">= 2 positive buckets",
            "why_it_matters": "至少要避免只在单一时间 pocket 才成立。",
        },
        {
            "gate": "bucket_trade_floor",
            "status": "pass" if int(bdf["trades"].min()) >= 5 else "fail",
            "actual": f"min bucket trades = {int(bdf['trades'].min())}",
            "threshold": ">= 5 trades per bucket",
            "why_it_matters": "时间稳定性不能建立在极少数 session 上。",
        },
        {
            "gate": "worst_bucket_watch",
            "status": "watch" if float(bdf["mean_asset_return"].min()) <= -0.01 else "pass",
            "actual": f"worst mean_asset_return = {pct(bdf['mean_asset_return'].min())}",
            "threshold": "ideally > -1.00%",
            "why_it_matters": "若最差 pocket 明显翻负，就不该写成稳定可推广候选。",
        },
    ]
    return pd.DataFrame(rows, columns=cols)


def build_parameter_stability(variant_aggregate: pd.DataFrame) -> pd.DataFrame:
    cols = ["gate", "status", "actual", "threshold", "why_it_matters"]
    q_hits = variant_aggregate[
        (variant_aggregate["variant"].isin(["funding_8h_q50", "funding_8h_q60", "funding_8h_q70"]))
        & (variant_aggregate["cost_bps_per_side"] == PRIMARY_COST)
    ].copy()
    if q_hits.empty:
        return pd.DataFrame(columns=cols)
    positive_configs = int((q_hits["mean_total_return"] > 0).sum())
    rows = [
        {
            "gate": "neighbor_positive_floor",
            "status": "pass" if positive_configs >= 2 else "fail",
            "actual": f"{positive_configs}/3 funding-threshold neighbors positive",
            "threshold": ">= 2 positive neighbors",
            "why_it_matters": "小参数邻域别一碰就碎。",
        },
        {
            "gate": "neighbor_trade_floor",
            "status": "pass" if int(q_hits["min_trades"].min()) >= 10 else "fail",
            "actual": f"min trades across neighbors = {int(q_hits['min_trades'].min())}",
            "threshold": ">= 10 per asset",
            "why_it_matters": "参数稳定性也需要最小 trade count 支撑。",
        },
        {
            "gate": "worst_neighbor_watch",
            "status": "watch" if float(q_hits["mean_total_return"].min()) <= -0.01 else "pass",
            "actual": f"worst neighbor mean_total_return = {pct(q_hits['mean_total_return'].min())}",
            "threshold": "ideally > -1.00%",
            "why_it_matters": "最差邻域若明显翻负，说明这条线偏 sample-bound。",
        },
    ]
    return pd.DataFrame(rows, columns=cols)


def build_cross_asset_stability(asset_summary: pd.DataFrame) -> pd.DataFrame:
    cols = ["gate", "status", "actual", "threshold", "why_it_matters"]
    hit = asset_summary[
        (asset_summary["variant"] == f"{PRIMARY_SESSION}_q{int(PRIMARY_THRESHOLD * 100)}")
        & (asset_summary["cost_bps_per_side"] == PRIMARY_COST)
    ].copy()
    if hit.empty:
        return pd.DataFrame(columns=cols)
    positive_assets = int((hit["total_return"] > 0).sum())
    worst = hit.sort_values("total_return").iloc[0]
    rows = [
        {
            "gate": "positive_asset_floor",
            "status": "pass" if positive_assets >= 2 else "fail",
            "actual": f"{positive_assets}/{len(hit)} assets positive",
            "threshold": ">= 2 positive assets",
            "why_it_matters": "不能只靠单一币种 lucky pocket。",
        },
        {
            "gate": "min_trade_floor",
            "status": "pass" if int(hit["trades"].min()) >= 10 else "fail",
            "actual": f"min trades = {int(hit['trades'].min())}",
            "threshold": ">= 10 per asset",
            "why_it_matters": "跨标的判断也要有最小样本。",
        },
        {
            "gate": "worst_asset_watch",
            "status": "watch" if float(worst["total_return"]) <= -0.01 else "pass",
            "actual": f"{worst['asset']} total_return={pct(worst['total_return'])}",
            "threshold": "ideally > -1.00%",
            "why_it_matters": "把最弱腿直接写明，避免均值掩盖。",
        },
    ]
    return pd.DataFrame(rows, columns=cols)


def build_cost_trade_stability(variant_aggregate: pd.DataFrame) -> pd.DataFrame:
    cols = ["gate", "status", "actual", "threshold", "why_it_matters"]
    hit = variant_aggregate[variant_aggregate["variant"] == f"{PRIMARY_SESSION}_q{int(PRIMARY_THRESHOLD * 100)}"].copy()
    if hit.empty:
        return pd.DataFrame(columns=cols)
    cost_positive = int((hit["mean_total_return"] > 0).sum())
    rows = [
        {
            "gate": "cost_survival_floor",
            "status": "pass" if cost_positive >= 2 else "fail",
            "actual": f"{cost_positive}/{len(hit)} cost levels positive",
            "threshold": ">= 2 positive cost levels",
            "why_it_matters": "轻量 friction 后不能立刻归零。",
        },
        {
            "gate": "trade_count_floor",
            "status": "pass" if int(hit["min_trades"].min()) >= 10 else "fail",
            "actual": f"min trades across cost ladder = {int(hit['min_trades'].min())}",
            "threshold": ">= 10 per asset",
            "why_it_matters": "trade count 过薄就不配继续推广。",
        },
        {
            "gate": "20bps_watch",
            "status": "watch" if float(hit.loc[hit['cost_bps_per_side'] == 20.0, 'mean_total_return'].iloc[0]) <= 0 else "pass",
            "actual": pct(hit.loc[hit['cost_bps_per_side'] == 20.0, 'mean_total_return'].iloc[0]) if not hit.loc[hit['cost_bps_per_side'] == 20.0].empty else "-",
            "threshold": "ideally > 0% @ 20bps",
            "why_it_matters": "20bps 不是硬门槛，但能看出是否只在轻摩擦下存活。",
        },
    ]
    return pd.DataFrame(rows, columns=cols)


def derive_verdict(primary_row: pd.Series | None, time_stability: pd.DataFrame, parameter_stability: pd.DataFrame, cross_asset_stability: pd.DataFrame, cost_trade_stability: pd.DataFrame) -> tuple[str, list[str]]:
    if primary_row is None:
        return "hard verdict：本轮没有拿到可读 primary variant。", ["缺少 funding_8h_q60 主变体结果。"]
    headline = (
        "hard verdict：session-aware intraday TSMOM（funding_8h_q60）在现有 120d / 15m crypto cache 上仍更像 `park / evidence pool`，"
        "不进入 paper candidate pool。"
    )
    if float(primary_row["mean_total_return"]) > 0 and float(primary_row["positive_asset_ratio"]) >= 2 / 3:
        headline = (
            "hard verdict：session-aware intraday TSMOM（funding_8h_q60）在当前 cache 上已拿到最小正向 first verdict，"
            "可进入更窄的后续复核，但仍未到 paper candidate。"
        )
    bullets = [
        f"primary variant：mean_total_return {pct(primary_row['mean_total_return'])}，positive_asset_ratio {pct(primary_row['positive_asset_ratio'])}，mean_trades {num(primary_row['mean_trades'], 1)}，mean_direction_hit_rate {pct(primary_row['mean_direction_hit_rate'])}。",
        "trade on / trade off 很清楚：只在 session 前 2 根方向明确、且绝对幅度超过本地分位阈值时，去交易同一 session 最后 2 根的方向；否则 no-trade。",
        "当前 clean replication 没有明显 lookahead：signal 只用 session 前段收益，执行段严格落在同一 session 的尾段。",
    ]
    fail_sets = []
    for name, df in [
        ("time", time_stability),
        ("parameter", parameter_stability),
        ("cross_asset", cross_asset_stability),
        ("cost_trade", cost_trade_stability),
    ]:
        if not df.empty and (df["status"] == "fail").any():
            fail_sets.append(name)
    bullets.append(f"Light Stability Pack 当前 fail 位：{', '.join(fail_sets) if fail_sets else '无硬 fail'}。")
    if float(primary_row["mean_total_return"]) <= 0 or float(primary_row["positive_asset_ratio"]) < 2 / 3 or fail_sets:
        bullets.append("因此这条线当前更适合作为 session-aware momentum 的 evidence pool，而不是继续占 Scout 主资源去做 paper wiring。")
    else:
        bullets.append("虽然 first verdict 转正，但当前更诚实的读法仍是 one-more-light-check，而不是直接 admission。")
    return headline, bullets


def write_report(variant_aggregate: pd.DataFrame, asset_summary: pd.DataFrame, time_stability: pd.DataFrame, parameter_stability: pd.DataFrame, cross_asset_stability: pd.DataFrame, cost_trade_stability: pd.DataFrame, trial_meta: pd.DataFrame) -> None:
    ensure_dir(SITE_DIR)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    primary = pick_primary(variant_aggregate)
    verdict_headline, verdict_bullets = derive_verdict(primary, time_stability, parameter_stability, cross_asset_stability, cost_trade_stability)
    meta = trial_meta.iloc[0].to_dict() if not trial_meta.empty else {}
    summary_table = render_table(
        variant_aggregate[variant_aggregate["cost_bps_per_side"] == PRIMARY_COST][[
            "variant", "assets_tested", "positive_assets", "positive_asset_ratio", "mean_total_return", "median_total_return", "mean_direction_hit_rate", "mean_trades", "min_trades"
        ]],
        percent_cols={"positive_asset_ratio", "mean_total_return", "median_total_return", "mean_direction_hit_rate"},
        digits_cols={"mean_trades": 1, "min_trades": 0},
    )
    asset_table = render_table(
        asset_summary[(asset_summary["variant"] == f"{PRIMARY_SESSION}_q{int(PRIMARY_THRESHOLD * 100)}") & (asset_summary["cost_bps_per_side"] == PRIMARY_COST)][[
            "asset", "trades", "win_rate", "direction_hit_rate", "total_return", "avg_net_ret"
        ]],
        percent_cols={"win_rate", "direction_hit_rate", "total_return", "avg_net_ret"},
        digits_cols={"trades": 0},
    )
    cost_table = render_table(
        variant_aggregate[variant_aggregate["variant"] == f"{PRIMARY_SESSION}_q{int(PRIMARY_THRESHOLD * 100)}"][[
            "cost_bps_per_side", "mean_total_return", "positive_asset_ratio", "mean_trades", "min_trades"
        ]],
        percent_cols={"mean_total_return", "positive_asset_ratio"},
        digits_cols={"cost_bps_per_side": 0, "mean_trades": 1, "min_trades": 0},
    )
    time_table = render_table(time_stability, percent_cols=set())
    param_table = render_table(parameter_stability, percent_cols=set())
    cross_table = render_table(cross_asset_stability, percent_cols=set())
    cost_stability_table = render_table(cost_trade_stability, percent_cols=set())
    bullets_html = "".join(f"<li>{escape(x)}</li>" for x in verdict_bullets)
    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Scout intraday TSMOM session · 15m crypto</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1120px; margin: 40px auto; padding: 0 18px; line-height: 1.68; color: #111827; background: #f8fafc; }}
    h1,h2,h3 {{ line-height: 1.25; }}
    .muted {{ color:#6b7280; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    ul {{ padding-left:20px; }}
    a {{ color:#2563eb; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
  </style>
</head>
<body>
  <p><a href=\"../../index.html\">← 返回首页</a></p>
  <h1>Scout Seat · session-aware intraday TSMOM · 15m crypto first verdict</h1>
  <p class=\"muted\">生成时间：{generated_at} ｜ 本页对应新的 paper-based scout intake：Li, Sakkas, Urquhart (2022) 的 intraday time-series momentum，被 clean-room 改写成 15m crypto 的 session lead → tail 实验。</p>

  <div class=\"card\">
    <h2>hard verdict</h2>
    <p><b>{escape(verdict_headline)}</b></p>
    <ul>{bullets_html}</ul>
  </div>

  <div class=\"card\">
    <h2>本轮 clean-room 口径</h2>
    <ul>
      <li>样本：<code>{escape(str(meta.get('sample_window', 'Binance 120d 15m cache')))}</code></li>
      <li>资产：<code>{escape(str(meta.get('assets', 'BTC-USD, ETH-USD, SOL-USD')))}</code></li>
      <li>session 候选：<code>utc_day</code>（00:00 UTC 日切）与 <code>funding_8h</code>（00/08/16 UTC）</li>
      <li>signal：同一 session 前 <code>2</code> 根 15m bar 的收益方向与绝对幅度</li>
      <li>trade on：<code>sign(lead_ret)</code> 明确，且 <code>|lead_ret|</code> 超过该 variant 分位阈值（q50/q60/q70）</li>
      <li>trade off：方向为 flat 或绝对幅度低于阈值，则 <code>no-trade</code></li>
      <li>执行：交易同一 session 最后 <code>2</code> 根 15m bar 的方向；成本默认 <code>{PRIMARY_COST:.0f}bps/side</code></li>
      <li>诚实边界：不等下一 session，不追新 bar；只复用现有 120d cache 做最小 replication + Light Stability Pack</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>variant aggregate（6bps/side）</h2>
    {summary_table}
    <p class=\"muted\">artifact：<code>reports/artifacts/scout_intraday_tsmom_session_15m/variant_aggregate.csv</code></p>
  </div>

  <div class=\"card\">
    <h2>primary variant per-asset（funding_8h_q60）</h2>
    {asset_table}
    <p class=\"muted\">当前默认只把 <code>funding_8h_q60</code> 当 reader-facing primary，因为它在 funding 风格 session 上比 UTC 日切更贴近 crypto 执行语境。</p>
  </div>

  <div class=\"card\">
    <h2>cost / trade-count stability（funding_8h_q60）</h2>
    {cost_table}
    {cost_stability_table}
  </div>

  <div class=\"card\">
    <h2>Light Stability Pack</h2>
    <h3>1) 时间稳定性</h3>
    {time_table}
    <h3>2) 参数稳定性（q50 / q60 / q70 邻域）</h3>
    {param_table}
    <h3>3) 跨标的稳定性</h3>
    {cross_table}
    <h3>4) 成本 / 交易数稳定性</h3>
    {cost_stability_table}
  </div>

  <div class=\"card\">
    <h2>怎么读这页</h2>
    <ul>
      <li>这条线不是 EMA / breakout 的延伸 wiring，而是新的 paper-based scout intake：测试“session 前段走势能否预测同一 session 尾段方向”。</li>
      <li>若 funding_8h 比 utc_day 更不差，说明 crypto 里更像有“资金费率/会话批次”风格的 session momentum，而不是简单照搬股票日切。</li>
      <li>若 Light Stability Pack 里出现硬 fail，就默认先 <code>park</code>；不要因为它是新 intake 就继续给 paper candidate 文书。</li>
    </ul>
  </div>
</body>
</html>
"""
    REPORT_PATH.write_text(html, encoding="utf-8")


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    session_rows = []
    all_trades = []
    all_summaries = []
    cache_meta = []

    for asset, symbol in ASSETS.items():
        bars = attach_sessions(load_cached_bars(symbol))
        cache_meta.append(
            {
                "asset": asset,
                "symbol": symbol,
                "source_cache": str((CACHE_DIR / f"{symbol}__120d__15m.csv").relative_to(ROOT)),
                "bars": int(len(bars)),
                "first_bar_utc": fmt_ts(bars["timestamp"].min()),
                "last_bar_utc": fmt_ts(bars["timestamp"].max()),
            }
        )
        for session_mode in ["utc_day", "funding_8h"]:
            base_sessions = build_session_rows(asset, symbol, bars, session_mode)
            if not base_sessions.empty:
                session_rows.append(base_sessions)
            for cfg in [x for x in VARIANTS if x["session_mode"] == session_mode]:
                filtered = filter_variant_events(base_sessions, abs_quantile=float(cfg["abs_quantile"]), variant=str(cfg["variant"]))
                for cost in COSTS:
                    trades = simulate_variant(filtered, cost_bps_per_side=cost)
                    all_trades.append(trades)
                    all_summaries.append(summarize_asset_variant(trades, asset, str(cfg["variant"]), float(cost)))

    session_df = pd.concat(session_rows, ignore_index=True) if session_rows else pd.DataFrame()
    trades_df = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    asset_summary = pd.concat(all_summaries, ignore_index=True) if all_summaries else pd.DataFrame()
    variant_aggregate = build_variant_aggregate(asset_summary)

    primary_trades = trades_df[
        (trades_df["variant"] == f"{PRIMARY_SESSION}_q{int(PRIMARY_THRESHOLD * 100)}")
        & (trades_df["cost_bps_per_side"] == PRIMARY_COST)
    ].copy() if not trades_df.empty else pd.DataFrame()

    time_stability = build_time_stability(primary_trades)
    parameter_stability = build_parameter_stability(variant_aggregate)
    cross_asset_stability = build_cross_asset_stability(asset_summary)
    cost_trade_stability = build_cost_trade_stability(variant_aggregate)
    primary = pick_primary(variant_aggregate)
    verdict_headline, _ = derive_verdict(primary, time_stability, parameter_stability, cross_asset_stability, cost_trade_stability)

    trial_meta = pd.DataFrame([
        {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "assets": ", ".join(ASSETS.keys()),
            "sample_window": "Binance 120d 15m（沿用现有 Rank 1 cache）",
            "lead_bars": LEAD_BARS,
            "tail_bars": TAIL_BARS,
            "primary_variant": f"{PRIMARY_SESSION}_q{int(PRIMARY_THRESHOLD * 100)}",
            "primary_cost_bps_per_side": PRIMARY_COST,
            "verdict": verdict_headline,
            "source_paper": "Li, Sakkas, Urquhart (2022) · Intraday time series momentum: Global evidence and links to market characteristics",
        }
    ])

    if not session_df.empty:
        session_df.to_csv(ART_DIR / "session_rows.csv", index=False)
    if not trades_df.empty:
        trades_df.to_csv(ART_DIR / "trades.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    variant_aggregate.to_csv(ART_DIR / "variant_aggregate.csv", index=False)
    pd.DataFrame(cache_meta).to_csv(ART_DIR / "cache_meta.csv", index=False)
    if not time_stability.empty:
        time_stability.to_csv(ART_DIR / "time_stability_drycheck.csv", index=False)
    if not parameter_stability.empty:
        parameter_stability.to_csv(ART_DIR / "parameter_stability_drycheck.csv", index=False)
    if not cross_asset_stability.empty:
        cross_asset_stability.to_csv(ART_DIR / "cross_asset_stability_drycheck.csv", index=False)
    if not cost_trade_stability.empty:
        cost_trade_stability.to_csv(ART_DIR / "cost_trade_stability_drycheck.csv", index=False)
    trial_meta.to_csv(ART_DIR / "trial_meta.csv", index=False)

    write_report(variant_aggregate, asset_summary, time_stability, parameter_stability, cross_asset_stability, cost_trade_stability, trial_meta)
    print("[ok] intraday tsmom session first verdict generated")
    print("[artifact]", ART_DIR / "variant_aggregate.csv")
    print("[site]", REPORT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
