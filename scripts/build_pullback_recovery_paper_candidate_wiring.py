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
PARAM_PATH = ART_DIR / "parameter_stability.csv"
COST_PATH = ART_DIR / "cost_trade_stability.csv"
ADMISSION_PATH = ART_DIR / "paper_candidate_admission_memo.csv"
META_PATH = ART_DIR / "clean_replication_meta.csv"

MONITOR_PATH = ART_DIR / "paper_candidate_monitoring_board.csv"
SEED_PATH = ART_DIR / "paper_candidate_refresh_seed_rows.csv"
HISTORY_PATH = ART_DIR / "paper_candidate_refresh_history.csv"
REPORT_PATH = SITE_DIR / "report.html"

CANDIDATE_ID = "rank17_pullback2_vol1.0_break1"
SCOPE_TAG = "paper_candidate_only"
TIMEFRAME = "15m"
VENUE_MODE = "paper_binance_spot"
SIGNAL_FAMILY = "pullback_recovery_confirmation"


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


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    summary = pd.read_csv(SUMMARY_PATH)
    asset = pd.read_csv(ASSET_PATH)
    trades = pd.read_csv(TRADES_PATH)
    time_df = pd.read_csv(TIME_PATH)
    param = pd.read_csv(PARAM_PATH)
    cost = pd.read_csv(COST_PATH)
    admission = pd.read_csv(ADMISSION_PATH)
    meta = pd.read_csv(META_PATH)

    trades["signal_ts"] = pd.to_datetime(trades["signal_ts"], utc=True)
    trades["entry_ts"] = pd.to_datetime(trades["entry_ts"], utc=True)
    trades["exit_ts"] = pd.to_datetime(trades["exit_ts"], utc=True)

    primary_variant = str(admission.iloc[0]["primary_variant"])
    sample_end = trades["exit_ts"].max()
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    primary_asset = asset[asset["variant"] == primary_variant].copy()
    primary_cost = cost[cost["variant"] == primary_variant].copy().sort_values("cost_bps_per_side")
    primary_time = time_df[time_df["variant"] == primary_variant].copy()
    primary_trades = trades[trades["variant"] == primary_variant].copy()

    ret_6 = float(primary_cost.loc[primary_cost["cost_bps_per_side"] == 6.0, "total_return"].iloc[0])
    ret_10 = float(primary_cost.loc[primary_cost["cost_bps_per_side"] == 10.0, "total_return"].iloc[0])
    ret_15 = float(primary_cost.loc[primary_cost["cost_bps_per_side"] == 15.0, "total_return"].iloc[0])
    ret_20 = float(primary_cost.loc[primary_cost["cost_bps_per_side"] == 20.0, "total_return"].iloc[0])

    monitoring_rows = [
        {
            "component": "scope_lock",
            "status": "pass",
            "minimum_rule": "只允许 rank17 / pullback2_vol1.0_break1 / 15m / BTC+ETH+SOL / paper_candidate_pool；不得越级写成 narrow paper pilot / tiny-live。",
            "default_fields": "candidate_id, scope_tag, asset_universe, timeframe, verdict_tag",
            "why_it_matters": "先把当前准入范围锁死，避免一条还在 friction/time pocket 里摇摆的候选被文档偷升格。",
        },
        {
            "component": "signal_ledger",
            "status": "pass",
            "minimum_rule": "每条记录都必须能追溯 signal_ts -> next-bar entry -> exit_ts，并保留 side / entry_price / exit_price / hold_bars / cost_bps_roundtrip。",
            "default_fields": "signal_ts_utc, asset, side, entry_ts_utc, exit_ts_utc, entry_price, exit_price, hold_bars, cost_bps_roundtrip, net_ret",
            "why_it_matters": "paper candidate 至少要能落成可审计账本，而不是只剩 headline 收益。",
        },
        {
            "component": "btc_weak_leg_watch",
            "status": "watch",
            "minimum_rule": "BTC 腿保持单独红灯；若 BTC 继续为负或 drawdown 扩大，不得偷升 narrow paper。",
            "default_fields": "asset, lifetime_total_return_6bps, lifetime_max_drawdown_6bps, watch_status, operator_note",
            "why_it_matters": "当前 2/3 资产为正，但 BTC-USD 仍约 -17.63%，不能被总均值掩盖。",
        },
        {
            "component": "friction_guard",
            "status": "watch",
            "minimum_rule": "保留 6/10/15/20bps 梯度；当前 15bps≈-3.13%、20bps≈-9.81%，因此继续维持 paper_candidate_only。",
            "default_fields": "cost_bps_per_side, aggregate_total_return, positive_asset_ratio, friction_status",
            "why_it_matters": "这轮最关键的诚实事实是：它不是只在 20bps 才塌，15bps 已经转负。",
        },
        {
            "component": "time_pocket_review",
            "status": "watch",
            "minimum_rule": "固定回看 bucket_1/bucket_2/bucket_3；若再次出现类似 bucket_1/2 的同步负 pocket，则不得提升。",
            "default_fields": "time_bucket, asset, total_return, trades, bucket_status",
            "why_it_matters": "当前时间稳定性只有 4/9 bucket 为正，说明并非平滑稳态。",
        },
        {
            "component": "promotion_boundary",
            "status": "pass",
            "minimum_rule": "这套 board 只服务 paper candidate；若要进 narrow paper pilot，必须先拿到新的最小诚实证据，而不是沿本板直接越级。",
            "default_fields": "eligible_next_stage, blocker_summary, reopen_condition",
            "why_it_matters": "把下一步边界写死，防止后续又回到 admission wording 打磨。",
        },
    ]
    monitoring_df = pd.DataFrame(monitoring_rows)
    monitoring_df.to_csv(MONITOR_PATH, index=False)

    seed_rows = []
    history_rows = []
    for _, asset_row in primary_asset.sort_values("asset").iterrows():
        asset_name = str(asset_row["asset"])
        last_trade = primary_trades[primary_trades["asset"] == asset_name].sort_values("exit_ts").iloc[-1]
        days_since = (sample_end - last_trade["exit_ts"]).total_seconds() / 86400.0
        time_slice = primary_time[primary_time["asset"] == asset_name].copy().sort_values("time_bucket")
        weak_buckets = ", ".join(time_slice.loc[time_slice["total_return"] <= 0, "time_bucket"].astype(str).tolist()) or "none"
        review_status = "red" if float(asset_row["total_return"]) <= 0 else "green"
        friction_status = "yellow_global_friction_watch" if ret_15 < 0 else "green"
        operator_action = (
            "carry_btc_red_watch_and_block_promotion"
            if review_status == "red"
            else "log_refresh_row_and_keep_friction_watch"
        )
        row = {
            "candidate_id": CANDIDATE_ID,
            "scope_tag": SCOPE_TAG,
            "asset": asset_name,
            "timeframe": TIMEFRAME,
            "venue_mode": VENUE_MODE,
            "signal_family": SIGNAL_FAMILY,
            "sample_end_utc": sample_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "last_signal_ts_utc": last_trade["signal_ts"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "last_entry_ts_utc": last_trade["entry_ts"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "last_exit_ts_utc": last_trade["exit_ts"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "last_side": last_trade["side"],
            "last_net_ret": round(float(last_trade["net_ret"]), 6),
            "lifetime_total_return_6bps": round(float(asset_row["total_return"]), 6),
            "lifetime_max_drawdown_6bps": round(float(asset_row["max_drawdown"]), 6),
            "days_since_last_trade": round(days_since, 1),
            "weak_time_buckets": weak_buckets,
            "friction_status": friction_status,
            "weekly_review_status": review_status,
            "operator_action": operator_action,
            "promotion_boundary": "paper_only_until_new_honest_evidence",
        }
        seed_rows.append(row)
        history_rows.append(
            {
                **row,
                "refresh_round": "seed_1",
                "continuity_status": "append_ready_with_red_watch" if review_status == "red" else "append_ready_green_with_global_watch",
                "writeback_note": "historical seed row only; no new bar fetched",
            }
        )

    seed_df = pd.DataFrame(seed_rows)
    history_df = pd.DataFrame(history_rows)
    seed_df.to_csv(SEED_PATH, index=False)
    history_df.to_csv(HISTORY_PATH, index=False)

    summary_view = summary.copy()
    summary_view["win_rate"] = summary_view["win_rate"].map(pct)
    summary_view["avg_ret"] = summary_view["avg_ret"].map(pct)
    summary_view["median_ret"] = summary_view["median_ret"].map(pct)
    summary_view["total_return"] = summary_view["total_return"].map(pct)
    summary_view["max_drawdown"] = summary_view["max_drawdown"].map(pct)
    summary_view["positive_asset_ratio"] = summary_view["positive_asset_ratio"].map(pct)

    asset_view = primary_asset[["asset", "trades", "win_rate", "total_return", "max_drawdown"]].copy()
    asset_view["win_rate"] = asset_view["win_rate"].map(pct)
    asset_view["total_return"] = asset_view["total_return"].map(pct)
    asset_view["max_drawdown"] = asset_view["max_drawdown"].map(pct)

    cost_view = primary_cost[["cost_bps_per_side", "total_return", "positive_asset_ratio", "trades"]].copy()
    cost_view["total_return"] = cost_view["total_return"].map(pct)
    cost_view["positive_asset_ratio"] = cost_view["positive_asset_ratio"].map(pct)
    cost_view["cost_bps_per_side"] = cost_view["cost_bps_per_side"].map(lambda x: f"{float(x):.0f}")

    time_view = primary_time[["asset", "time_bucket", "trades", "total_return", "max_drawdown"]].copy()
    time_view["total_return"] = time_view["total_return"].map(pct)
    time_view["max_drawdown"] = time_view["max_drawdown"].map(pct)

    seed_view = seed_df[[
        "asset",
        "last_exit_ts_utc",
        "days_since_last_trade",
        "lifetime_total_return_6bps",
        "weak_time_buckets",
        "weekly_review_status",
        "operator_action",
    ]].copy()
    seed_view["lifetime_total_return_6bps"] = seed_view["lifetime_total_return_6bps"].map(pct)
    seed_view["days_since_last_trade"] = seed_view["days_since_last_trade"].map(lambda x: num(x, 1))

    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Scout Seat · Rank 17 pullback recovery confirmation · paper-candidate wiring</title>
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
  <h1>Scout Seat · Rank 17 pullback recovery confirmation · paper-candidate wiring</h1>
  <p class="muted">生成时间：{generated_at} ｜ 基于现有历史样本，把 Rank 17 从“已入 paper candidate pool”继续压成最小 monitoring / refresh seed；不追新 bar，不扩新研究。</p>

  <div class="card">
    <h2>hard verdict</h2>
    <p><b>Rank 17 继续保留在 <code>paper candidate pool</code>，本轮不升 <code>narrow paper pilot</code>。</b></p>
    <ul>
      <li>当前最重要的诚实 blocker 不是“还没写 enough docs”，而是 <b>friction 已在 15bps 转负</b>：6bps {pct(ret_6)} → 10bps {pct(ret_10)} → 15bps {pct(ret_15)} → 20bps {pct(ret_20)}。</li>
      <li>跨资产仍是 2/3 为正，但 BTC 腿 6bps lifetime total_return 仍约 {pct(float(primary_asset.loc[primary_asset['asset'] == 'BTC-USD', 'total_return'].iloc[0]))}，不能被均值 headline 淹掉。</li>
      <li>因此这轮最有边际价值的动作不是继续扩研究，而是把它压成可复用的 <code>paper candidate monitoring + seed rows</code>，并把 promotion 边界写死。</li>
    </ul>
  </div>

  <div class="card">
    <h2>aggregate clean replication（existing sample）</h2>
    {render_table(summary_view, ["variant", "win_rate", "avg_ret", "median_ret", "total_return", "max_drawdown", "trades", "positive_asset_ratio"])}
  </div>

  <div class="card">
    <h2>6bps per-asset snapshot</h2>
    {render_table(asset_view, ["asset", "trades", "win_rate", "total_return", "max_drawdown"])}
  </div>

  <div class="card">
    <h2>friction ladder（决定本轮不升 narrow paper 的关键证据）</h2>
    <p><b>诚实读法：</b>这条线不是只在 20bps 才变差；现有样本里 <code>15bps</code> 已经转负，所以当前更像“可继续留在 paper candidate pool 并接监控”，而不是直接升窄范围 paper pilot。</p>
    {render_table(cost_view, ["cost_bps_per_side", "total_return", "positive_asset_ratio", "trades"])}
    <p class="muted">artifact：<code>{COST_PATH.relative_to(ROOT)}</code></p>
  </div>

  <div class="card">
    <h2>time pocket snapshot</h2>
    <p>时间稳定性仍偏混合，因此 monitoring board 默认要求固定回看弱 pocket，而不是只盯 aggregate headline。</p>
    {render_table(time_view, ["asset", "time_bucket", "trades", "total_return", "max_drawdown"])}
    <p class="muted">artifact：<code>{TIME_PATH.relative_to(ROOT)}</code></p>
  </div>

  <div class="card">
    <h2>paper candidate monitoring board（本轮新增）</h2>
    <p><b>这不是新 alpha 证据，而是最小可部署接线：</b>把 Rank 17 当前必须长期盯住的 scope / friction / BTC 弱腿 / 时间 pocket / promotion boundary 压成单独 board。</p>
    {render_table(monitoring_df, ["component", "status", "minimum_rule", "why_it_matters"])}
    <p class="muted">artifact：<code>{MONITOR_PATH.relative_to(ROOT)}</code></p>
  </div>

  <div class="card">
    <h2>paper candidate refresh seed rows（本轮新增）</h2>
    <p>已从现有历史样本抽出每个资产最新一条可回放 seed row；后续若继续认领 Rank 17，默认应沿这组 row 做 append / review，而不是回到 admission wording 打磨。</p>
    {render_table(seed_view, ["asset", "last_exit_ts_utc", "days_since_last_trade", "lifetime_total_return_6bps", "weak_time_buckets", "weekly_review_status", "operator_action"])}
    <p class="muted">artifact：<code>{SEED_PATH.relative_to(ROOT)}</code> ｜ history seed：<code>{HISTORY_PATH.relative_to(ROOT)}</code></p>
  </div>

  <div class="card">
    <h2>怎么读这页</h2>
    <ul>
      <li>这页回答的是：<b>Rank 17 既然已经进了 paper candidate pool，下一步最小可接线物是什么？</b></li>
      <li>它没有新增 future bar，也没有把 paper candidate 偷写成 narrow paper pilot。</li>
      <li>如果后续 1~2 轮能拿到新的诚实证据、并把 friction / weak-leg 读法进一步稳定，再讨论 promotion；否则就应继续维持 paper-candidate only 或直接切去更高边际值的新 Scout 候选。</li>
    </ul>
  </div>
</body>
</html>
'''
    REPORT_PATH.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
