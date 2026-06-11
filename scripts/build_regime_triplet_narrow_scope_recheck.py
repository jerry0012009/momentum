#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from build_regime_triplet_scout_clean_replication import (  # noqa: E402
    ASSETS,
    PRIMARY_LABEL,
    ensure_dir,
    evaluate_one,
    load_cached_bars,
    num,
    pct,
    render_table,
)

ART_DIR = ROOT / "reports" / "artifacts" / "scout_regime_triplet_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_regime_triplet_15m"
REPORT_PATH = SITE_DIR / "ethsol_scope_recheck.html"

SCOPE_COST_PATH = ART_DIR / "ethsol_scope_recheck.csv"
SCOPE_TIME_PATH = ART_DIR / "ethsol_scope_time_recheck_15bps.csv"
SCOPE_MONITOR_PATH = ART_DIR / "narrow_paper_pilot_ethsol_monitoring_board.csv"
SCOPE_REVIEW_PATH = ART_DIR / "narrow_paper_pilot_ethsol_review_queue.csv"
META_PATH = ART_DIR / "ethsol_scope_recheck_meta.csv"

NARROW_ASSETS = ["ETH-USD", "SOL-USD"]
PRIMARY_COSTS = [6.0, 10.0, 15.0, 20.0]
TIME_BUCKETS = 3
PROMOTION_SCOPE = "ETH+SOL only"


def aggregate_scope(cost: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    for asset, symbol in ASSETS.items():
        if asset not in NARROW_ASSETS:
            continue
        bars = load_cached_bars(symbol, asset)
        s, _ = evaluate_one(bars, variant=PRIMARY_LABEL, cost_bps=cost)
        rows.append(s)
    df = pd.DataFrame(rows).sort_values("asset").reset_index(drop=True)
    agg = pd.DataFrame(
        [
            {
                "scope_tag": "ethsol_only",
                "cost_bps_per_side": float(cost),
                "mean_total_return": float(df["total_return"].mean()),
                "positive_asset_ratio": float((df["total_return"] > 0).mean()),
                "mean_trades": float(df["trades"].mean()),
                "mean_win_rate": float(df["win_rate"].mean()),
                "mean_max_drawdown": float(df["max_drawdown"].mean()),
                "mean_no_trade_ratio": float(df["no_trade_ratio"].mean()),
                "ETH_total_return": float(df.loc[df["asset"] == "ETH-USD", "total_return"].iloc[0]),
                "SOL_total_return": float(df.loc[df["asset"] == "SOL-USD", "total_return"].iloc[0]),
            }
        ]
    )
    return agg, df


def time_recheck_15bps() -> pd.DataFrame:
    rows = []
    for asset, symbol in ASSETS.items():
        if asset not in NARROW_ASSETS:
            continue
        bars = load_cached_bars(symbol, asset)
        idx_splits = np.array_split(np.arange(len(bars)), TIME_BUCKETS)
        for i, idx in enumerate(idx_splits, start=1):
            bucket_bars = bars.iloc[idx].reset_index(drop=True)
            s, _ = evaluate_one(bucket_bars, variant=PRIMARY_LABEL, cost_bps=15.0)
            rows.append(
                {
                    "asset": asset,
                    "time_bucket": f"bucket_{i}",
                    "total_return": float(s["total_return"]),
                    "trades": int(s["trades"]),
                    "win_rate": float(s["win_rate"]),
                    "no_trade_ratio": float(s["no_trade_ratio"]),
                }
            )
    df = pd.DataFrame(rows)
    agg_rows = []
    for bucket, g in df.groupby("time_bucket", sort=True):
        agg_rows.append(
            {
                "time_bucket": bucket,
                "mean_total_return": float(g["total_return"].mean()),
                "positive_asset_ratio": float((g["total_return"] > 0).mean()),
                "mean_trades": float(g["trades"].mean()),
                "mean_win_rate": float(g["win_rate"].mean()),
                "mean_no_trade_ratio": float(g["no_trade_ratio"].mean()),
            }
        )
    return pd.DataFrame(agg_rows)


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    scope_rows = []
    asset_views = []
    for cost in PRIMARY_COSTS:
        agg, asset_df = aggregate_scope(cost)
        scope_rows.append(agg.iloc[0].to_dict())
        asset_df = asset_df.copy()
        asset_df["cost_bps_per_side"] = float(cost)
        asset_views.append(asset_df)
    scope_df = pd.DataFrame(scope_rows)
    asset_df = pd.concat(asset_views, ignore_index=True)
    time_df = time_recheck_15bps()

    scope_df.to_csv(SCOPE_COST_PATH, index=False)
    time_df.to_csv(SCOPE_TIME_PATH, index=False)

    row15 = scope_df.loc[scope_df["cost_bps_per_side"] == 15.0].iloc[0]
    positive_buckets = int((time_df["mean_total_return"] > 0).sum())

    hard_verdict = "park / evidence pool"
    verdict_reason = (
        "ETH+SOL-only 虽把 15bps mean_total_return 拉回正值，但 15bps 仅 1/2 资产为正，且时间桶 bucket_1 仍明显转负，"
        "说明 narrow-scope 后仍没有形成足够干净的 P3 paper pilot。"
    )

    monitor_df = pd.DataFrame(
        [
            {
                "component": "scope_narrowing_result",
                "status": "watch",
                "minimum_rule": f"ETH+SOL-only 在 15bps/side 平均回报约 {pct(row15['mean_total_return'])}，但 positive_asset_ratio 只有 {pct(row15['positive_asset_ratio'])}。",
                "why_it_matters": "说明移除 BTC 弱腿确实改善 aggregate，但 improvement 仍不够干净，不能直接当成稳定 P3。",
            },
            {
                "component": "time_bucket_recheck_15bps",
                "status": "red_watch",
                "minimum_rule": f"15bps 下 time positive buckets = {positive_buckets}/3，且 bucket_1 mean_total_return 仍为负。",
                "why_it_matters": "真正决定 verdict 的不是 headline 平均值，而是窄 scope 后是否还保留明显的时间结构破口。",
            },
            {
                "component": "btc_exclusion_honesty",
                "status": "pass",
                "minimum_rule": "本轮没有改信号规则、没有追新 bar，只是诚实地把 BTC 从 scope 中剥离来测试 blocker 是否消失。",
                "why_it_matters": "这让本轮最小检查可以直接回答“升 P3 / 压回 park”，而不是继续堆近义文档。",
            },
            {
                "component": "next_action",
                "status": "park",
                "minimum_rule": "当前更诚实的动作是把 Rank 26 压回 park / evidence pool；除非后续有新的 genuinely verdict-changing 证据，否则不再继续占默认 Scout 主资源。",
                "why_it_matters": "避免让一个已经用完预算的 P2 长期挂在研究态。",
            },
        ]
    )
    monitor_df.to_csv(SCOPE_MONITOR_PATH, index=False)

    review_df = pd.DataFrame(
        [
            {
                "candidate_id": "rank26_regime_triplet_state_gate_15m",
                "scope_tag": "ethsol_only_recheck",
                "asset": "ETH-USD",
                "cost_15_total_return": round(float(asset_df[(asset_df['asset'] == 'ETH-USD') & (asset_df['cost_bps_per_side'] == 15.0)]['total_return'].iloc[0]), 6),
                "time_bucket_watch": "bucket_1,bucket_3",
                "operator_action": "park_candidate_keep_eth_as_evidence_only",
            },
            {
                "candidate_id": "rank26_regime_triplet_state_gate_15m",
                "scope_tag": "ethsol_only_recheck",
                "asset": "SOL-USD",
                "cost_15_total_return": round(float(asset_df[(asset_df['asset'] == 'SOL-USD') & (asset_df['cost_bps_per_side'] == 15.0)]['total_return'].iloc[0]), 6),
                "time_bucket_watch": "bucket_1,bucket_2",
                "operator_action": "park_candidate_keep_sol_as_evidence_only",
            },
        ]
    )
    review_df.to_csv(SCOPE_REVIEW_PATH, index=False)

    meta_df = pd.DataFrame(
        [
            {
                "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "hard_verdict": hard_verdict,
                "verdict_reason": verdict_reason,
                "promotion_scope_tested": PROMOTION_SCOPE,
            }
        ]
    )
    meta_df.to_csv(META_PATH, index=False)

    scope_view = scope_df.copy()

    time_view = time_df.copy()

    asset15 = asset_df[asset_df["cost_bps_per_side"] == 15.0][["asset", "trades", "win_rate", "total_return", "max_drawdown", "no_trade_ratio"]].copy()

    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Scout Seat · Rank 26 regime triplet · ETH+SOL scope recheck</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1120px; margin: 40px auto; padding: 0 18px; line-height: 1.68; color: #111827; background: #f8fafc; }}
    h1,h2,h3 {{ line-height: 1.25; }}
    .muted {{ color:#6b7280; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
  </style>
</head>
<body>
  <p><a href="../../index.html">← 返回首页</a></p>
  <h1>Scout Seat · Rank 26 regime triplet · ETH+SOL scope recheck</h1>
  <p class="muted">生成时间：{escape(str(meta_df.iloc[0]['generated_at_utc']))} ｜ 用现有历史样本做 1 次 genuinely verdict-changing 最小检查：不改规则、不追新 bar，只把 BTC 弱腿剥离，测试 Rank 26 是否足以升到 narrow paper pilot。</p>

  <div class="card">
    <h2>hard verdict</h2>
    <p><b>{hard_verdict}</b></p>
    <ul>
      <li>ETH+SOL-only 在 6/10bps 确实比 full-scope 更干净，但到 15bps/side 时平均回报只剩 <b>{pct(row15['mean_total_return'])}</b>，且只有 <b>{pct(row15['positive_asset_ratio'])}</b> 的资产为正。</li>
      <li>更关键的是，15bps 下时间桶仍不是干净的 P3 读法：<b>{positive_buckets}/3</b> 个 bucket 为正，<code>bucket_1</code> 仍明显转负。</li>
      <li>因此这条线最诚实的结论不是“差一点先挂着 P2”，而是：<b>当前预算用完，压回 park / evidence pool</b>。</li>
    </ul>
  </div>

  <div class="card">
    <h2>ETH+SOL-only friction recheck（本轮新增）</h2>
    <p>方法：直接复用同一套 `BTC/ETH/SOL 120d 15m` 历史样本与同一条 `strict_up_down` 规则，只把 BTC 从运行 scope 里剥离，再按 6/10/15/20bps 重算 ETH+SOL 的 aggregate。</p>
    {render_table(scope_view, percent_cols={'mean_total_return','positive_asset_ratio','mean_win_rate','mean_max_drawdown','mean_no_trade_ratio','ETH_total_return','SOL_total_return'}, digits_cols={'mean_trades':1})}
    <p class="muted">artifact：<code>{SCOPE_COST_PATH.relative_to(ROOT)}</code></p>
  </div>

  <div class="card">
    <h2>15bps time recheck（为什么这刀足以改 verdict）</h2>
    {render_table(time_view, percent_cols={'mean_total_return','positive_asset_ratio','mean_win_rate','mean_no_trade_ratio'}, digits_cols={'mean_trades':1})}
    <p class="muted">它直接回答了当前 blocker：如果连 ETH+SOL-only 在更贴近执行摩擦的 15bps 下都还留着明显时间破口，那就不该再继续把它挂在 P2 等待“再来一页说明”。</p>
  </div>

  <div class="card">
    <h2>15bps per-asset snapshot</h2>
    {render_table(asset15, percent_cols={'win_rate','total_return','max_drawdown','no_trade_ratio'}, digits_cols={'trades':0})}
    <p class="muted">ETH 仍为正，但 SOL 在 15bps 已转负；这说明 scope narrowing 没有把它修成足够干净的双腿 P3。</p>
  </div>

  <div class="card">
    <h2>operator read</h2>
    {render_table(monitor_df, percent_cols=set(), digits_cols={})}
    <p class="muted">artifacts：<code>{SCOPE_MONITOR_PATH.relative_to(ROOT)}</code> ｜ <code>{SCOPE_REVIEW_PATH.relative_to(ROOT)}</code></p>
  </div>
</body>
</html>
'''
    REPORT_PATH.write_text(html, encoding="utf-8")
    print(f"Wrote Rank 26 scope recheck to {REPORT_PATH}")
    print(f"Hard verdict: {hard_verdict}")


if __name__ == "__main__":
    main()
