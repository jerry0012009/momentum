# 2026-03-19 08:05 UTC · Rank 83 fib trend-strength clean replication

## Context
- 先按 `Run 1 / EMA due-check only` 复核当前 desk：`EMA = waiting_not_due`，没有新的 `due-now / overdue` lane。
- 按顶板顺序，本轮合法主动作落在 `Run 2 / Rank 83 minimal clean replication`。
- 当前 repo 工作区存在大量与本轮无关的既有脏文件 / 未跟踪文件，因此本轮只做最小增量，不混提其他线。

## Claimed scope
- 主点：`Rank 83 / Fib trend-strength admission layer` 最小 clean replication
- 紧邻子点：把 hard verdict 回写到 `docs/TODO.md`，并补 reader-facing 页面

## What I ran
- 新增脚本：`scripts/build_rank83_fib_trend_strength_clean_replication.py`
- 执行：`python3 scripts/build_rank83_fib_trend_strength_clean_replication.py`

## Frozen test design
- 样本：`BTC / ETH / SOL`，复用本地 `120d 15m` cache
- 单 lane：只接 `Fib retest`，不扩成 shared 三 archetype 大框架
- 执行冻结：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- 三臂：
  - `base_binary`：所有 `weak / medium / strong` 都放行
  - `strength_filter`：只放行 `medium + strong`
  - `strength_sizing`：`weak=0 / medium=0.5x / strong=1.0x`
- strength bucket：
  - `weak`：站回 `Fib 0.618`，但收盘仍未回到 `Fib 0.5`
  - `medium`：收回 `Fib 0.5`
  - `strong`：在 `medium` 基础上，再收回 `Fib 0.382` 或站上前一根高点

## Hard verdict
- `Rank 83 / Fib trend-strength admission layer = keep_P1 / evidence_pool`
- 结论理由：`medium + strong` 过滤确实降低了早期失效，但改善还不够统一；当前更诚实的位置是保留为 `P1 evidence`，而不是直接升格。

## Key numbers @ 6bps/side
- `base_binary`
  - `mean_total_return ≈ -1.83%`
  - `positive_asset_ratio = 0/3`
  - `mean_trades ≈ 16.0`
  - `4-bar fail ≈ 63.96%`
- `strength_filter`
  - `mean_total_return ≈ +1.18%`
  - `positive_asset_ratio ≈ 66.67%`
  - `retention ≈ 66.38%`
  - `mean_avg_net_ret ≈ +0.110%`
  - `4-bar fail ≈ 51.52%`
- `strength_sizing`
  - `mean_total_return ≈ +1.16%`
  - `positive_asset_ratio = 3/3`
  - `retention ≈ 66.38%`
  - `mean_avg_net_ret ≈ +0.108%`
  - `4-bar fail ≈ 51.52%`

## Bucket read @ primary (6bps)
- `medium`：`trades=5`，`mean_net_ret≈-0.106%`，`fail_4bars=100%`
- `strong`：`trades=28`，`mean_net_ret≈+0.146%`，`fail_4bars≈42.86%`
- 读法：真实 edge 主要集中在 `strong` 桶；`medium` 还不够干净，所以这轮不应直接升到 `P2`。

## Artifacts
- `reports/artifacts/scout_rank83_fib_trend_strength_15m/overall_summary.csv`
- `reports/artifacts/scout_rank83_fib_trend_strength_15m/bucket_summary_primary_6bps.csv`
- `reports/artifacts/scout_rank83_fib_trend_strength_15m/asset_summary.csv`
- `reports/artifacts/scout_rank83_fib_trend_strength_15m/trades_primary_6bps.csv`

## Reader-facing pages
- `reports/site/factors/scout_rank83_fib_trend_strength_15m/report.html`
- `reports/site/reading/repo_scout/rank83_fib_trend_strength_clean_replication.html`

## TODO writeback
- 已把本轮 verdict 写回 `docs/TODO.md`
- 最新 `Next 3` 已收紧为：
  - `Run 1 = EMA due-check only`
  - `Run 2 = 若 Rank 83 仍不足以升格但未硬 fail，则只允许给它 1 个 truly verdict-changing 的最小检查`
  - `Run 3 = 若不继续 Rank 83，则切 Rank 85 / fresh pullback → reclaim re-arm gate source intake`

## Notes
- 本轮没有动 `P3 continuity`，也没有去碰 `tiny-live plumbing`。
- 当前工作区里有大量与本轮无关的脏文件；本轮仅新增 Rank 83 相关脚本 / artifact / 页面 / TODO 写回 / 本日志。