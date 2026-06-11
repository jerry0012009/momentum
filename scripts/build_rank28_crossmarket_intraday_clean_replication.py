#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank28_crossmarket_intraday_tsmom_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank28_crossmarket_intraday_tsmom_15m"
REPORT_PATH = SITE_DIR / "report.html"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
SESSION_MODES = ["utc_day", "funding_8h"]
THRESHOLDS = [0.50, 0.60, 0.70]
COSTS = [6.0, 10.0, 15.0, 20.0]
PRIMARY_VARIANT = "funding_8h_q60"
PRIMARY_COST = 6.0
LEAD_BARS = 2
TAIL_BARS = 2
TIME_BUCKETS = 3


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


def render_table(df: pd.DataFrame, *, percent_cols: set[str], digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    digits_cols = digits_cols or {}
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value)
            elif isinstance(value, (float, np.floating, int, np.integer)) and not isinstance(value, bool):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = str(value)
            cells.append(f"<td>{escape(text)}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def load_cached_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def attach_sessions(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    ts = out["timestamp"]
    out["utc_day_session"] = ts.dt.floor("1D")
    funding_hour = (ts.dt.hour // 8) * 8
    out["funding_8h_session"] = ts.dt.floor("1D") + pd.to_timedelta(funding_hour, unit="h")
    return out


def build_session_rows(asset: str, bars: pd.DataFrame, session_mode: str) -> pd.DataFrame:
    session_col = "utc_day_session" if session_mode == "utc_day" else "funding_8h_session"
    rows: list[dict] = []
    for session_start, g in bars.groupby(session_col, sort=True):
        g = g.sort_values("timestamp").reset_index(drop=True)
        if len(g) < LEAD_BARS + TAIL_BARS:
            continue
        lead = g.iloc[:LEAD_BARS]
        tail = g.iloc[-TAIL_BARS:]
        lead_ret = float(lead.iloc[-1]["close"] / lead.iloc[0]["open"] - 1.0)
        tail_ret_long = float(tail.iloc[-1]["close"] / tail.iloc[0]["open"] - 1.0)
        rows.append(
            {
                "asset": asset,
                "session_mode": session_mode,
                "session_start": session_start,
                "bars_in_session": int(len(g)),
                "lead_ret": lead_ret,
                "abs_lead_ret": abs(lead_ret),
                "lead_sign": 1 if lead_ret > 0 else -1 if lead_ret < 0 else 0,
                "lead_start_ts": lead.iloc[0]["timestamp"],
                "lead_end_ts": lead.iloc[-1]["timestamp"],
                "tail_entry_ts": tail.iloc[0]["timestamp"],
                "tail_exit_ts": tail.iloc[-1]["timestamp"],
                "tail_ret_long": tail_ret_long,
                "tail_ret_short": float(-tail_ret_long),
            }
        )
    return pd.DataFrame(rows)


def summarize_trades(trades: pd.DataFrame, *, asset: str, variant: str, cost: float) -> dict:
    if trades.empty:
        return {
            "asset": asset,
            "variant": variant,
            "cost_bps_per_side": float(cost),
            "trades": 0,
            "win_rate": np.nan,
            "avg_net_ret": np.nan,
            "median_net_ret": np.nan,
            "total_return": 0.0,
            "false_follow_ratio": np.nan,
            "mean_abs_lead_ret": np.nan,
        }
    return {
        "asset": asset,
        "variant": variant,
        "cost_bps_per_side": float(cost),
        "trades": int(len(trades)),
        "win_rate": float((trades["net_ret"] > 0).mean()),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "median_net_ret": float(trades["net_ret"].median()),
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "false_follow_ratio": float((trades["net_ret"] <= 0).mean()),
        "mean_abs_lead_ret": float(trades["leader_abs_lead_ret"].mean()),
    }


def build_variant_events(session_rows: pd.DataFrame, session_mode: str, quantile: float, variant: str) -> pd.DataFrame:
    mode_rows = session_rows[session_rows["session_mode"] == session_mode].copy()
    if mode_rows.empty:
        return pd.DataFrame()
    threshold_by_asset = mode_rows.groupby("asset")["abs_lead_ret"].quantile(quantile).to_dict()
    events: list[dict] = []
    for session_start, g in mode_rows.groupby("session_start", sort=True):
        g = g.copy()
        g["asset_threshold"] = g["asset"].map(threshold_by_asset)
        eligible = g[(g["lead_sign"] != 0) & (g["abs_lead_ret"] >= g["asset_threshold"])].copy()
        if eligible.empty:
            continue
        leader = eligible.sort_values(["abs_lead_ret", "asset"], ascending=[False, True]).iloc[0]
        followers = g[(g["asset"] != leader["asset"]) & (g["lead_sign"] == leader["lead_sign"]) & (g["abs_lead_ret"] < leader["abs_lead_ret"])].copy()
        if followers.empty:
            continue
        for _, row in followers.iterrows():
            gross_ret = float(row["tail_ret_long"] if leader["lead_sign"] > 0 else row["tail_ret_short"])
            events.append(
                {
                    "variant": variant,
                    "session_mode": session_mode,
                    "quantile": quantile,
                    "session_start": session_start,
                    "leader_asset": leader["asset"],
                    "leader_lead_ret": float(leader["lead_ret"]),
                    "leader_abs_lead_ret": float(leader["abs_lead_ret"]),
                    "leader_threshold": float(leader["asset_threshold"]),
                    "asset": row["asset"],
                    "follower_lead_ret": float(row["lead_ret"]),
                    "follower_abs_lead_ret": float(row["abs_lead_ret"]),
                    "signal_side": "long" if leader["lead_sign"] > 0 else "short",
                    "tail_entry_ts": row["tail_entry_ts"],
                    "tail_exit_ts": row["tail_exit_ts"],
                    "gross_ret": gross_ret,
                }
            )
    return pd.DataFrame(events)


def apply_costs(events: pd.DataFrame, cost: float) -> pd.DataFrame:
    if events.empty:
        return events.copy()
    out = events.copy()
    cost_rate = float(cost) / 10000.0
    out["cost_bps_per_side"] = float(cost)
    out["net_ret"] = (1.0 + out["gross_ret"]) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
    out["false_follow"] = (out["net_ret"] <= 0).astype(int)
    return out


def build_aggregate(asset_summary: pd.DataFrame) -> pd.DataFrame:
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
            mean_false_follow_ratio=("false_follow_ratio", "mean"),
            mean_trades=("trades", "mean"),
            min_trades=("trades", "min"),
        )
        .sort_values(["cost_bps_per_side", "mean_total_return"], ascending=[True, False])
        .reset_index(drop=True)
    )
    out["positive_asset_ratio"] = out["positive_assets"] / out["assets_tested"].replace(0, np.nan)
    return out


def pick_primary(aggregate: pd.DataFrame) -> pd.Series | None:
    hit = aggregate[(aggregate["variant"] == PRIMARY_VARIANT) & (aggregate["cost_bps_per_side"] == PRIMARY_COST)]
    if hit.empty:
        return None
    return hit.iloc[0]


def build_time_stability(primary_trades: pd.DataFrame) -> pd.DataFrame:
    cols = ["gate", "status", "actual", "threshold", "why_it_matters"]
    if primary_trades.empty or len(primary_trades) < 9:
        return pd.DataFrame(columns=cols)
    df = primary_trades.sort_values("session_start").reset_index(drop=True).copy()
    df["bucket"] = pd.qcut(np.arange(len(df)), TIME_BUCKETS, labels=["bucket_1", "bucket_2", "bucket_3"])
    stats = []
    for bucket, g in df.groupby("bucket", observed=False):
        if g.empty:
            continue
        asset_totals = g.groupby("asset")["net_ret"].apply(lambda s: float((1.0 + s).prod() - 1.0))
        stats.append({"bucket": str(bucket), "trades": int(len(g)), "mean_asset_return": float(asset_totals.mean())})
    bdf = pd.DataFrame(stats)
    if bdf.empty:
        return pd.DataFrame(columns=cols)
    positive_buckets = int((bdf["mean_asset_return"] > 0).sum())
    return pd.DataFrame([
        {
            "gate": "positive_bucket_floor",
            "status": "pass" if positive_buckets >= 2 else "fail",
            "actual": f"{positive_buckets}/3 positive buckets",
            "threshold": ">= 2 positive buckets",
            "why_it_matters": "不能只靠一个时间 pocket 存活。",
        },
        {
            "gate": "bucket_trade_floor",
            "status": "pass" if int(bdf["trades"].min()) >= 4 else "fail",
            "actual": f"min bucket trades = {int(bdf['trades'].min())}",
            "threshold": ">= 4 trades per bucket",
            "why_it_matters": "时间切片至少要有最小样本。",
        },
        {
            "gate": "worst_bucket_watch",
            "status": "watch" if float(bdf["mean_asset_return"].min()) <= -0.01 else "pass",
            "actual": f"worst bucket = {pct(bdf['mean_asset_return'].min())}",
            "threshold": "ideally > -1.00%",
            "why_it_matters": "最差时间 pocket 明显翻负时，不应写成稳定 alpha。",
        },
    ], columns=cols)


def build_parameter_stability(aggregate: pd.DataFrame) -> pd.DataFrame:
    cols = ["gate", "status", "actual", "threshold", "why_it_matters"]
    neighbors = aggregate[(aggregate["cost_bps_per_side"] == PRIMARY_COST) & (aggregate["variant"].isin(["funding_8h_q50", "funding_8h_q60", "funding_8h_q70"]))]
    if neighbors.empty:
        return pd.DataFrame(columns=cols)
    positive = int((neighbors["mean_total_return"] > 0).sum())
    return pd.DataFrame([
        {
            "gate": "neighbor_positive_floor",
            "status": "pass" if positive >= 2 else "fail",
            "actual": f"{positive}/3 funding-threshold neighbors positive",
            "threshold": ">= 2 positive neighbors",
            "why_it_matters": "小参数邻域别一碰就碎。",
        },
        {
            "gate": "neighbor_trade_floor",
            "status": "pass" if int(neighbors["min_trades"].min()) >= 4 else "fail",
            "actual": f"min trades across neighbors = {int(neighbors['min_trades'].min())}",
            "threshold": ">= 4 per asset",
            "why_it_matters": "参数口袋太薄时，正收益也不可靠。",
        },
        {
            "gate": "worst_neighbor_watch",
            "status": "watch" if float(neighbors["mean_total_return"].min()) <= -0.01 else "pass",
            "actual": f"worst neighbor = {pct(neighbors['mean_total_return'].min())}",
            "threshold": "ideally > -1.00%",
            "why_it_matters": "最差邻域若明显翻负，说明样本绑定很重。",
        },
    ], columns=cols)


def build_cross_asset_stability(asset_summary: pd.DataFrame) -> pd.DataFrame:
    cols = ["gate", "status", "actual", "threshold", "why_it_matters"]
    hit = asset_summary[(asset_summary["variant"] == PRIMARY_VARIANT) & (asset_summary["cost_bps_per_side"] == PRIMARY_COST)]
    if hit.empty:
        return pd.DataFrame(columns=cols)
    positive_assets = int((hit["total_return"] > 0).sum())
    worst = hit.sort_values("total_return").iloc[0]
    return pd.DataFrame([
        {
            "gate": "positive_asset_floor",
            "status": "pass" if positive_assets >= 2 else "fail",
            "actual": f"{positive_assets}/{len(hit)} assets positive",
            "threshold": ">= 2 positive assets",
            "why_it_matters": "不能只靠单腿运气。",
        },
        {
            "gate": "min_trade_floor",
            "status": "pass" if int(hit["trades"].min()) >= 4 else "fail",
            "actual": f"min trades = {int(hit['trades'].min())}",
            "threshold": ">= 4 per asset",
            "why_it_matters": "跨标的判断也要最小样本。",
        },
        {
            "gate": "worst_asset_watch",
            "status": "watch" if float(worst["total_return"]) <= -0.01 else "pass",
            "actual": f"{worst['asset']} total_return={pct(worst['total_return'])}",
            "threshold": "ideally > -1.00%",
            "why_it_matters": "把最弱腿单独写明，避免均值掩盖。",
        },
    ], columns=cols)


def build_cost_trade_stability(aggregate: pd.DataFrame) -> pd.DataFrame:
    cols = ["gate", "status", "actual", "threshold", "why_it_matters"]
    hit = aggregate[aggregate["variant"] == PRIMARY_VARIANT]
    if hit.empty:
        return pd.DataFrame(columns=cols)
    positive_costs = int((hit["mean_total_return"] > 0).sum())
    at20 = hit.loc[hit["cost_bps_per_side"] == 20.0, "mean_total_return"]
    at20_val = float(at20.iloc[0]) if not at20.empty else np.nan
    return pd.DataFrame([
        {
            "gate": "cost_survival_floor",
            "status": "pass" if positive_costs >= 2 else "fail",
            "actual": f"{positive_costs}/{len(hit)} cost levels positive",
            "threshold": ">= 2 positive cost levels",
            "why_it_matters": "轻量 friction 后不该立刻归零。",
        },
        {
            "gate": "trade_count_floor",
            "status": "pass" if int(hit["min_trades"].min()) >= 4 else "fail",
            "actual": f"min trades across cost ladder = {int(hit['min_trades'].min())}",
            "threshold": ">= 4 per asset",
            "why_it_matters": "交易数太薄时没法拿来晋级。",
        },
        {
            "gate": "20bps_watch",
            "status": "watch" if pd.notna(at20_val) and at20_val <= 0 else "pass",
            "actual": pct(at20_val),
            "threshold": "ideally > 0% @ 20bps",
            "why_it_matters": "20bps 不是硬门槛，但能看出是否只在极轻摩擦下存活。",
        },
    ], columns=cols)


def derive_verdict(primary: pd.Series | None, time_df: pd.DataFrame, param_df: pd.DataFrame, cross_df: pd.DataFrame, cost_df: pd.DataFrame) -> tuple[str, list[str], str]:
    if primary is None:
        return (
            "当前 Rank 28 clean replication 没有形成可读 primary variant，先压回 park / evidence pool。",
            ["缺少 primary variant 结果，说明当前 spec 还不足以支撑晋级讨论。"],
            "park / evidence pool",
        )
    fail_sets = []
    for name, df in [("时间稳定性", time_df), ("参数稳定性", param_df), ("跨标的稳定性", cross_df), ("成本/交易数稳定性", cost_df)]:
        if not df.empty and (df["status"] == "fail").any():
            fail_sets.append(name)
    headline = "当前 Rank 28 更诚实的 hard verdict 是 park / evidence pool，不进入 paper candidate pool。"
    final_verdict = "park / evidence pool"
    if float(primary["mean_total_return"]) > 0 and float(primary["positive_asset_ratio"]) >= 2/3 and not fail_sets:
        headline = "当前 Rank 28 clean replication 拿到了最小正向 first verdict，可暂列 P1 weak candidate，但还不到 paper candidate。"
        final_verdict = "P1 weak candidate / one cheap check at most"
    bullets = [
        f"primary variant={PRIMARY_VARIANT} @ 6bps/side：mean_total_return {pct(primary['mean_total_return'])}，positive_asset_ratio {pct(primary['positive_asset_ratio'])}，mean_trades {num(primary['mean_trades'], 1)}，mean_false_follow_ratio {pct(primary['mean_false_follow_ratio'])}。",
        "trade on / trade off 仍是因果的：只用 session 前 2 根已完成 bar 选出跨市场 leader，再去交易同 session 尾段的 laggard follow-through，不用未来标签。",
    ]
    if fail_sets:
        bullets.append(f"Light Stability Pack 的硬 fail 位：{' / '.join(fail_sets)}。")
    else:
        bullets.append("Light Stability Pack 当前没有硬 fail，但仍需警惕样本很薄或 pocket 偏窄。")
    if final_verdict.startswith("park"):
        bullets.append("因此这条线当前更适合作为 cross-market intraday lead-lag 的证据池，而不是继续占 Scout 主资源做 paper wiring。")
    else:
        bullets.append("如果下一轮继续认领，默认也只允许做 1 次便宜诚实检查；不要直接扩成大框架。")
    return headline, bullets, final_verdict


def write_report(aggregate: pd.DataFrame, asset_summary: pd.DataFrame, time_df: pd.DataFrame, param_df: pd.DataFrame, cost_df: pd.DataFrame, trial_meta: pd.DataFrame) -> None:
    ensure_dir(SITE_DIR)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    primary = pick_primary(aggregate)
    headline, bullets, _ = derive_verdict(primary, time_df, param_df, cross_df=time_df if False else build_cross_asset_stability(asset_summary), cost_df=cost_df)
    bullets_html = "".join(f"<li>{escape(x)}</li>" for x in bullets)
    summary_table = render_table(
        aggregate[aggregate["cost_bps_per_side"] == PRIMARY_COST][[
            "variant", "assets_tested", "positive_assets", "positive_asset_ratio", "mean_total_return", "median_total_return", "mean_false_follow_ratio", "mean_trades", "min_trades"
        ]],
        percent_cols={"positive_asset_ratio", "mean_total_return", "median_total_return", "mean_false_follow_ratio"},
        digits_cols={"mean_trades": 1, "min_trades": 0},
    )
    asset_table = render_table(
        asset_summary[(asset_summary["variant"] == PRIMARY_VARIANT) & (asset_summary["cost_bps_per_side"] == PRIMARY_COST)][[
            "asset", "trades", "total_return", "win_rate", "false_follow_ratio", "avg_net_ret"
        ]],
        percent_cols={"total_return", "win_rate", "false_follow_ratio", "avg_net_ret"},
        digits_cols={"trades": 0},
    )
    cost_table = render_table(
        aggregate[aggregate["variant"] == PRIMARY_VARIANT][[
            "cost_bps_per_side", "mean_total_return", "positive_asset_ratio", "mean_false_follow_ratio", "mean_trades", "min_trades"
        ]],
        percent_cols={"mean_total_return", "positive_asset_ratio", "mean_false_follow_ratio"},
        digits_cols={"cost_bps_per_side": 0, "mean_trades": 1, "min_trades": 0},
    )
    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank 28 · cross-market intraday leader-laggard TSMOM</title>
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
  <p><a href="../../index.html">← 返回首页</a></p>
  <h1>Rank 28 · cross-market intraday leader-laggard TSMOM</h1>
  <p class="muted">生成时间：{generated_at} ｜ 当前只做 1 个最小 clean replication：固定复用 BTC/ETH/SOL 120d 15m cache，对比 funding_8h / UTC session 的跨市场 leader-laggard follow-through。</p>

  <div class="card">
    <h2>hard verdict</h2>
    <p><b>{escape(headline)}</b></p>
    <ul>{bullets_html}</ul>
  </div>

  <div class="card">
    <h2>clean-room 口径</h2>
    <ul>
      <li>样本：<code>BTC / ETH / SOL | Binance 120d | 15m</code></li>
      <li>session：<code>utc_day</code> 与 <code>funding_8h</code></li>
      <li>leader 定义：同一 session 前 <code>2</code> 根 15m bar 内，绝对 lead move 超过各自分位阈值且幅度最大的那条腿</li>
      <li>follower 定义：同 session 内其余同方向、但前段幅度更弱的 laggard 腿</li>
      <li>trade on：leader 已出现，且 follower 在前段并未反向；于同一 session 最后 <code>2</code> 根 15m bar 跟随 leader 方向</li>
      <li>trade off：没有合格 leader / follower，或方向不一致，则 no-trade</li>
      <li>诚实边界：不接 prediction-market / equity proxy 外部 feed，不追新 bar，不扩成重型 stability 包</li>
    </ul>
  </div>

  <div class="card">
    <h2>variant aggregate（6bps/side）</h2>
    {summary_table}
    <p class="muted">artifact：<code>reports/artifacts/scout_rank28_crossmarket_intraday_tsmom_15m/variant_aggregate.csv</code></p>
  </div>

  <div class="card">
    <h2>primary variant per-asset（{escape(PRIMARY_VARIANT)}）</h2>
    {asset_table}
  </div>

  <div class="card">
    <h2>成本 / 交易数稳定性（{escape(PRIMARY_VARIANT)}）</h2>
    {cost_table}
  </div>

  <div class="card">
    <h2>Light Stability Pack</h2>
    <h3>1) 时间稳定性</h3>
    {render_table(time_df, percent_cols=set())}
    <h3>2) 参数稳定性</h3>
    {render_table(param_df, percent_cols=set())}
    <h3>3) 跨标的稳定性</h3>
    {render_table(build_cross_asset_stability(asset_summary), percent_cols=set())}
    <h3>4) 成本 / 交易数稳定性</h3>
    {render_table(cost_df, percent_cols=set())}
  </div>
</body>
</html>'''
    REPORT_PATH.write_text(html, encoding="utf-8")


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    session_rows = []
    for asset, symbol in ASSETS.items():
        bars = attach_sessions(load_cached_bars(symbol, asset))
        for session_mode in SESSION_MODES:
            session_rows.append(build_session_rows(asset, bars, session_mode))
    session_df = pd.concat(session_rows, ignore_index=True)

    event_frames = []
    trade_frames = []
    summary_rows = []
    for session_mode in SESSION_MODES:
        for threshold in THRESHOLDS:
            variant = f"{session_mode}_q{int(threshold * 100)}"
            events = build_variant_events(session_df, session_mode, threshold, variant)
            if not events.empty:
                event_frames.append(events)
            for cost in COSTS:
                trades = apply_costs(events, cost)
                if not trades.empty:
                    trade_frames.append(trades)
                for asset in ASSETS:
                    asset_trades = trades[trades["asset"] == asset].copy() if not trades.empty else pd.DataFrame()
                    summary_rows.append(summarize_trades(asset_trades, asset=asset, variant=variant, cost=cost))

    event_df = pd.concat(event_frames, ignore_index=True) if event_frames else pd.DataFrame()
    trades_df = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()
    asset_summary = pd.DataFrame(summary_rows)
    aggregate = build_aggregate(asset_summary)

    primary_trades = trades_df[(trades_df["variant"] == PRIMARY_VARIANT) & (trades_df["cost_bps_per_side"] == PRIMARY_COST)].copy() if not trades_df.empty else pd.DataFrame()
    time_df = build_time_stability(primary_trades)
    param_df = build_parameter_stability(aggregate)
    cross_df = build_cross_asset_stability(asset_summary)
    cost_df = build_cost_trade_stability(aggregate)
    headline, bullets, final_verdict = derive_verdict(pick_primary(aggregate), time_df, param_df, cross_df, cost_df)

    trial_meta = pd.DataFrame([
        {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "candidate_id": "rank28_crossmarket_intraday_leader_laggard_tsmom",
            "sample_window": "BTC/ETH/SOL Binance 120d 15m cache",
            "lead_bars": LEAD_BARS,
            "tail_bars": TAIL_BARS,
            "primary_variant": PRIMARY_VARIANT,
            "primary_cost_bps_per_side": PRIMARY_COST,
            "hard_verdict": final_verdict,
            "headline": headline,
            "evidence_1": bullets[0] if bullets else "",
            "evidence_2": bullets[1] if len(bullets) > 1 else "",
        }
    ])

    session_df.to_csv(ART_DIR / "session_rows.csv", index=False)
    event_df.to_csv(ART_DIR / "leader_laggard_events.csv", index=False)
    trades_df.to_csv(ART_DIR / "leader_laggard_trades.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    aggregate.to_csv(ART_DIR / "variant_aggregate.csv", index=False)
    time_df.to_csv(ART_DIR / "time_stability_drycheck.csv", index=False)
    param_df.to_csv(ART_DIR / "parameter_stability_drycheck.csv", index=False)
    cross_df.to_csv(ART_DIR / "cross_asset_stability_drycheck.csv", index=False)
    cost_df.to_csv(ART_DIR / "cost_trade_stability_drycheck.csv", index=False)
    trial_meta.to_csv(ART_DIR / "trial_meta.csv", index=False)

    write_report(aggregate, asset_summary, time_df, param_df, cost_df, trial_meta)
    print("[ok] rank28 clean replication generated")
    print("[artifact]", ART_DIR / "variant_aggregate.csv")
    print("[site]", REPORT_PATH)
    print("[verdict]", final_verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
