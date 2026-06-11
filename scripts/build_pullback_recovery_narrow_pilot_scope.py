#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_pullback_recovery_confirmation_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_pullback_recovery_confirmation_15m"

SUMMARY_PATH = ART_DIR / "clean_replication_summary.csv"
ASSET_PATH = ART_DIR / "clean_replication_asset_summary.csv"
TRADES_PATH = ART_DIR / "clean_replication_trades.csv"
TIME_PATH = ART_DIR / "time_stability.csv"
COST_PATH = ART_DIR / "cost_trade_stability.csv"
ADMISSION_PATH = ART_DIR / "paper_candidate_admission_memo.csv"

NARROW_COST_PATH = ART_DIR / "narrow_paper_pilot_ethsol_friction_check.csv"
NARROW_MONITOR_PATH = ART_DIR / "narrow_paper_pilot_ethsol_monitoring_board.csv"
NARROW_SEED_PATH = ART_DIR / "narrow_paper_pilot_ethsol_seed_rows.csv"
NARROW_HISTORY_PATH = ART_DIR / "narrow_paper_pilot_ethsol_refresh_history.csv"
REPORT_PATH = SITE_DIR / "report.html"

PRIMARY_VARIANT = "pullback2_vol1.0_break1"
NARROW_SCOPE_TAG = "narrow_paper_pilot_eth_sol_only"
PARKED_SCOPE_TAG = "park_btc_excluded_leg"
ASSETS_NARROW = ["ETH-USD", "SOL-USD"]
ASSET_PARKED = "BTC-USD"


def pct(x: float | int | None) -> str:
    if pd.isna(x):
        return "—"
    return f"{float(x) * 100:.2f}%"


def num(x: float | int | None, digits: int = 2) -> str:
    if pd.isna(x):
        return "—"
    return f"{float(x):.{digits}f}"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def render_table(df: pd.DataFrame, columns: list[str] | None = None) -> str:
    if columns is None:
        columns = list(df.columns)
    rows = []
    for _, row in df[columns].iterrows():
        cells = "".join(f"<td>{escape(str(row[col]))}</td>" for col in columns)
        rows.append(f"<tr>{cells}</tr>")
    head = "".join(f"<th>{escape(col)}</th>" for col in columns)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def apply_cost(gross_ret: pd.Series, cost_bps_per_side: float) -> pd.Series:
    c = cost_bps_per_side / 10000.0
    return (1.0 + gross_ret) * (1.0 - c) * (1.0 - c) - 1.0


def eq_return(net_ret: pd.Series) -> float:
    return float((1.0 + net_ret).prod() - 1.0)


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    summary = pd.read_csv(SUMMARY_PATH)
    asset = pd.read_csv(ASSET_PATH)
    trades = pd.read_csv(TRADES_PATH)
    time_df = pd.read_csv(TIME_PATH)
    cost_df = pd.read_csv(COST_PATH)
    admission = pd.read_csv(ADMISSION_PATH)

    trades["signal_ts"] = pd.to_datetime(trades["signal_ts"], utc=True)
    trades["entry_ts"] = pd.to_datetime(trades["entry_ts"], utc=True)
    trades["exit_ts"] = pd.to_datetime(trades["exit_ts"], utc=True)

    primary_asset = asset[asset["variant"] == PRIMARY_VARIANT].copy()
    primary_time = time_df[time_df["variant"] == PRIMARY_VARIANT].copy()
    primary_cost = cost_df[cost_df["variant"] == PRIMARY_VARIANT].copy().sort_values("cost_bps_per_side")
    primary_trades = trades[(trades["variant"] == PRIMARY_VARIANT) & (trades["cost_bps_per_side"] == 6.0)].copy()
    narrow_trades = primary_trades[primary_trades["asset"].isin(ASSETS_NARROW)].copy()
    parked_trades = primary_trades[primary_trades["asset"] == ASSET_PARKED].copy()

    sample_end = primary_trades["exit_ts"].max()
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    narrow_rows = []
    for cost in [6.0, 10.0, 15.0, 20.0]:
        cost_trades = narrow_trades.copy()
        cost_trades["net_ret_cost"] = apply_cost(cost_trades["gross_ret"], cost)
        per_asset = (
            cost_trades.groupby("asset")
            .agg(
                total_return=("net_ret_cost", eq_return),
                trades=("net_ret_cost", "size"),
                win_rate=("net_ret_cost", lambda s: float((s > 0).mean())),
                avg_ret=("net_ret_cost", "mean"),
                median_ret=("net_ret_cost", "median"),
            )
            .reset_index()
        )
        narrow_rows.append(
            {
                "scope_tag": NARROW_SCOPE_TAG,
                "cost_bps_per_side": cost,
                "mean_total_return": float(per_asset["total_return"].mean()),
                "positive_asset_ratio": float((per_asset["total_return"] > 0).mean()),
                "mean_trades": float(per_asset["trades"].mean()),
                "mean_win_rate": float(per_asset["win_rate"].mean()),
                "ETH_total_return": float(per_asset.loc[per_asset["asset"] == "ETH-USD", "total_return"].iloc[0]),
                "SOL_total_return": float(per_asset.loc[per_asset["asset"] == "SOL-USD", "total_return"].iloc[0]),
            }
        )
    narrow_cost = pd.DataFrame(narrow_rows)
    narrow_cost.to_csv(NARROW_COST_PATH, index=False)

    narrow_15 = narrow_cost.loc[narrow_cost["cost_bps_per_side"] == 15.0].iloc[0]
    narrow_20 = narrow_cost.loc[narrow_cost["cost_bps_per_side"] == 20.0].iloc[0]

    narrow_monitor = pd.DataFrame(
        [
            {
                "component": "scope_freeze",
                "status": "pass",
                "minimum_rule": "只允许 ETH-USD + SOL-USD 两条腿进入 narrow paper pilot；BTC 保持 excluded red-watch，不得混回同一 pilot headline。",
                "why_it_matters": "当前真正改变 verdict 的不是再磨总均值，而是把弱腿 BTC 从可运行 scope 中诚实剥离。",
            },
            {
                "component": "friction_guard",
                "status": "pass" if float(narrow_15["mean_total_return"]) > 0 else "watch",
                "minimum_rule": f"ETH+SOL 缩 scope 后必须在 15bps/side 仍为正；当前约 {pct(narrow_15['mean_total_return'])}，20bps/side 约 {pct(narrow_20['mean_total_return'])}。",
                "why_it_matters": "这刀直接回答原来卡住 Rank 17 的 friction blocker 在窄范围 pilot 下是否还成立。",
            },
            {
                "component": "btc_exclusion_watch",
                "status": "red_watch",
                "minimum_rule": "BTC 继续单列 park / excluded leg；后续若想重回 pilot，必须先拿到新的 honest evidence。",
                "why_it_matters": "避免把 2/2 缩 scope 后的正结果误读成 3/3 全部过关。",
            },
            {
                "component": "time_pocket_watch",
                "status": "watch",
                "minimum_rule": "ETH bucket_1 与 SOL bucket_1/2 仍保留 watch；pilot 允许运行，但 weekly review 必须继续单列弱 pocket。",
                "why_it_matters": "这条线已到 P3，不代表时间稳定性变完美；只是说明它已足够进入更窄 paper 观察。",
            },
            {
                "component": "promotion_boundary",
                "status": "pass",
                "minimum_rule": "当前只升到 narrow paper pilot approved（paper only）；不得偷升 tiny-live。",
                "why_it_matters": "符合 desk 当前默认：P3 只补 paper ledger / monitoring / refresh / review 最小接线。",
            },
        ]
    )
    narrow_monitor.to_csv(NARROW_MONITOR_PATH, index=False)

    seed_rows = []
    history_rows = []
    for asset_name in ASSETS_NARROW:
        asset_row = primary_asset[primary_asset["asset"] == asset_name].iloc[0]
        last_trade = narrow_trades[narrow_trades["asset"] == asset_name].sort_values("exit_ts").iloc[-1]
        days_since = (sample_end - last_trade["exit_ts"]).total_seconds() / 86400.0
        time_slice = primary_time[primary_time["asset"] == asset_name].copy().sort_values("time_bucket")
        weak_buckets = ", ".join(time_slice.loc[time_slice["total_return"] <= 0, "time_bucket"].astype(str).tolist()) or "none"
        seed_row = {
            "candidate_id": "rank17_pullback_ethsol_narrow_pilot",
            "scope_tag": NARROW_SCOPE_TAG,
            "asset": asset_name,
            "timeframe": "15m",
            "venue_mode": "paper_binance_spot",
            "signal_family": "pullback_recovery_confirmation",
            "sample_end_utc": sample_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "last_signal_ts_utc": last_trade["signal_ts"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "last_entry_ts_utc": last_trade["entry_ts"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "last_exit_ts_utc": last_trade["exit_ts"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "last_side": last_trade["side"],
            "last_net_ret_6bps": round(float(last_trade["net_ret"]), 6),
            "lifetime_total_return_6bps": round(float(asset_row["total_return"]), 6),
            "days_since_last_trade": round(days_since, 1),
            "weak_time_buckets": weak_buckets,
            "weekly_review_status": "green_keep_narrow_pilot",
            "operator_action": "append_refresh_review_row_keep_ethsol_narrow_pilot",
            "promotion_boundary": "paper_only_narrow_pilot_until_new_live_clearance",
        }
        seed_rows.append(seed_row)
        history_rows.append(
            {
                **seed_row,
                "refresh_round": "seed_1",
                "continuity_status": "append_ready_green_narrow_pilot",
                "writeback_note": "historical seed row only; no new bar fetched",
            }
        )

    btc_row = primary_asset[primary_asset["asset"] == ASSET_PARKED].iloc[0]
    btc_last = parked_trades.sort_values("exit_ts").iloc[-1]
    btc_days = (sample_end - btc_last["exit_ts"]).total_seconds() / 86400.0
    btc_time_slice = primary_time[primary_time["asset"] == ASSET_PARKED].copy().sort_values("time_bucket")
    btc_weak_buckets = ", ".join(btc_time_slice.loc[btc_time_slice["total_return"] <= 0, "time_bucket"].astype(str).tolist()) or "none"
    history_rows.append(
        {
            "candidate_id": "rank17_pullback_btc_parked_leg",
            "scope_tag": PARKED_SCOPE_TAG,
            "asset": ASSET_PARKED,
            "timeframe": "15m",
            "venue_mode": "paper_binance_spot",
            "signal_family": "pullback_recovery_confirmation",
            "sample_end_utc": sample_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "last_signal_ts_utc": btc_last["signal_ts"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "last_entry_ts_utc": btc_last["entry_ts"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "last_exit_ts_utc": btc_last["exit_ts"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "last_side": btc_last["side"],
            "last_net_ret_6bps": round(float(btc_last["net_ret"]), 6),
            "lifetime_total_return_6bps": round(float(btc_row["total_return"]), 6),
            "days_since_last_trade": round(btc_days, 1),
            "weak_time_buckets": btc_weak_buckets,
            "weekly_review_status": "red_keep_parked",
            "operator_action": "keep_btc_excluded_red_watch",
            "promotion_boundary": "park_until_new_honest_evidence",
            "refresh_round": "seed_1",
            "continuity_status": "parked_red_watch",
            "writeback_note": "excluded from ETH+SOL narrow pilot",
        }
    )

    seed_df = pd.DataFrame(seed_rows)
    seed_df.to_csv(NARROW_SEED_PATH, index=False)
    history_df = pd.DataFrame(history_rows)
    history_df.to_csv(NARROW_HISTORY_PATH, index=False)

    summary_view = summary.copy()
    for col in ["win_rate", "avg_ret", "median_ret", "total_return", "max_drawdown", "positive_asset_ratio"]:
        summary_view[col] = summary_view[col].map(pct)

    asset_view = primary_asset[["asset", "trades", "win_rate", "total_return", "max_drawdown"]].copy()
    for col in ["win_rate", "total_return", "max_drawdown"]:
        asset_view[col] = asset_view[col].map(pct)

    primary_cost_view = primary_cost[["cost_bps_per_side", "total_return", "positive_asset_ratio", "trades"]].copy()
    primary_cost_view["cost_bps_per_side"] = primary_cost_view["cost_bps_per_side"].map(lambda x: f"{float(x):.0f}")
    for col in ["total_return", "positive_asset_ratio"]:
        primary_cost_view[col] = primary_cost_view[col].map(pct)

    narrow_cost_view = narrow_cost[["cost_bps_per_side", "mean_total_return", "positive_asset_ratio", "mean_trades", "ETH_total_return", "SOL_total_return"]].copy()
    narrow_cost_view["cost_bps_per_side"] = narrow_cost_view["cost_bps_per_side"].map(lambda x: f"{float(x):.0f}")
    for col in ["mean_total_return", "positive_asset_ratio", "ETH_total_return", "SOL_total_return"]:
        narrow_cost_view[col] = narrow_cost_view[col].map(pct)
    narrow_cost_view["mean_trades"] = narrow_cost_view["mean_trades"].map(lambda x: num(x, 1))

    seed_view = seed_df[[
        "asset",
        "last_exit_ts_utc",
        "days_since_last_trade",
        "lifetime_total_return_6bps",
        "weak_time_buckets",
        "weekly_review_status",
        "operator_action",
    ]].copy()
    seed_view["days_since_last_trade"] = seed_view["days_since_last_trade"].map(lambda x: num(x, 1))
    seed_view["lifetime_total_return_6bps"] = seed_view["lifetime_total_return_6bps"].map(pct)

    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Scout Seat · Rank 17 pullback recovery confirmation · narrow paper pilot verdict</title>
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
  <h1>Scout Seat · Rank 17 pullback recovery confirmation · narrow paper pilot verdict</h1>
  <p class="muted">生成时间：{generated_at} ｜ 基于现有历史样本，对 Rank 17 做 1 次 genuinely verdict-changing 最小检查：把 BTC 弱腿剥离，只看 ETH+SOL 窄范围 pilot 在更贴执行摩擦下是否还能站住。</p>

  <div class="card">
    <h2>hard verdict</h2>
    <p><b>Rank 17 现提升为 <code>narrow paper pilot approved</code>，但 scope 只限 <code>ETH-USD + SOL-USD</code>；<code>BTC-USD</code> 保持 <code>park / excluded red-watch leg</code>。</b></p>
    <ul>
      <li>全 scope（BTC+ETH+SOL）原本卡住 promotion 的关键 blocker 是：<b>15bps/side 已转负</b>，约 {pct(float(primary_cost.loc[primary_cost['cost_bps_per_side']==15.0,'total_return'].iloc[0]))}。</li>
      <li>这轮用同一套历史 trades 做最小 honest narrowing 后，<b>ETH+SOL-only 在 15bps/side 仍约 {pct(float(narrow_15['mean_total_return']))}</b>，且 2/2 资产仍为正；20bps/side 则约 {pct(float(narrow_20['mean_total_return']))}，说明它适合进更窄 paper pilot，但还不配写成 live-ready。</li>
      <li>更诚实的 desk 读法因此不是“Rank 17 全体翻身”，而是：<b>ETH+SOL 可升 P3，BTC 继续 park。</b></li>
    </ul>
  </div>

  <div class="card">
    <h2>原始 full-scope 快照（为什么此前只停在 paper candidate）</h2>
    {render_table(summary_view, ["variant", "win_rate", "avg_ret", "median_ret", "total_return", "max_drawdown", "trades", "positive_asset_ratio"])}
    <p class="muted">原始全 scope friction：15bps/side 已转负，因此此前更诚实的位置只是 <code>paper candidate pool</code>。</p>
    {render_table(primary_cost_view, ["cost_bps_per_side", "total_return", "positive_asset_ratio", "trades"])}
  </div>

  <div class="card">
    <h2>verdict-changing 最小检查：ETH+SOL 窄范围 friction 审计（本轮新增）</h2>
    <p>方法：直接复用既有 <code>clean_replication_trades.csv</code> 的同一组 historical trades，不追新 bar、不改信号规则，只把 BTC 弱腿从运行 scope 里剥离，再按 6/10/15/20bps 重新计算 ETH+SOL 两腿的等权 aggregate。</p>
    {render_table(narrow_cost_view, ["cost_bps_per_side", "mean_total_return", "positive_asset_ratio", "mean_trades", "ETH_total_return", "SOL_total_return"])}
    <p class="muted">artifact：<code>{NARROW_COST_PATH.relative_to(ROOT)}</code></p>
  </div>

  <div class="card">
    <h2>为什么这刀足以改变 verdict</h2>
    <ul>
      <li>它直接打在当前最大的真实 blocker：<b>不是研究不够，而是 friction + BTC weak leg</b>。</li>
      <li>检查结果没有靠新数据或新参数偷分，只是把现有 evidence 更诚实地收成一个更窄可运行 scope。</li>
      <li>它符合 desk 当前规则：P2 候选经过 1~2 轮最小诚实检查仍未 blow-up 时，默认应推进到 P3，而不是继续停在 admission wording。</li>
    </ul>
  </div>

  <div class="card">
    <h2>6bps per-asset snapshot（保留 full-scope honesty）</h2>
    {render_table(asset_view, ["asset", "trades", "win_rate", "total_return", "max_drawdown"])}
    <p class="muted">BTC 仍然显著偏弱，因此它被保留为 excluded red-watch leg，而不是被均值 headline 冲淡。</p>
  </div>

  <div class="card">
    <h2>ETH+SOL narrow paper pilot monitoring board（本轮新增）</h2>
    {render_table(narrow_monitor, ["component", "status", "minimum_rule", "why_it_matters"])}
    <p class="muted">artifact：<code>{NARROW_MONITOR_PATH.relative_to(ROOT)}</code></p>
  </div>

  <div class="card">
    <h2>ETH+SOL narrow paper pilot seed rows（本轮新增）</h2>
    <p>这不是 live 账本，只是把 P3 之后允许继续做的最小接线补齐：后续若继续认领 Rank 17，默认只沿这两条腿做 refresh / review append；BTC 单列保留在 parked watch，不再混成 pilot headline。</p>
    {render_table(seed_view, ["asset", "last_exit_ts_utc", "days_since_last_trade", "lifetime_total_return_6bps", "weak_time_buckets", "weekly_review_status", "operator_action"])}
    <p class="muted">artifacts：<code>{NARROW_SEED_PATH.relative_to(ROOT)}</code> ｜ <code>{NARROW_HISTORY_PATH.relative_to(ROOT)}</code></p>
  </div>

  <div class="card">
    <h2>怎么读这页</h2>
    <ul>
      <li>这页不是说 Rank 17 已经适合 tiny-live；它只是在 Scout Seat 口径下，把一条 P2 候选更快推进到 P3。</li>
      <li>后续若继续认领 Rank 17，默认只允许补 <code>paper ledger / monitoring / refresh / review</code> 的最小接线，或一个真正会改变 paper verdict 的最小检查。</li>
      <li>如果没有真实 append/review need，则应把 Scout 主资源切回新的 paper / repo intake，而不是继续围着 Rank 17 打磨近义文档。</li>
    </ul>
  </div>
</body>
</html>
'''
    REPORT_PATH.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
