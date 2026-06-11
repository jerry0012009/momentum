# 2026-03-20 17:18 UTC — Rank 126 / deepest retracement hold-quality gate / minimal clean replication

## 本轮先核对的东西
- repo：`master`；`git status --short | wc -l = 1919`，存在大量与本轮无关的脏文件，**不混提**。
- 最近 optimization loop：仍以 `16:36 UTC / Rank 125 cost-trade stability -> keep_P1 / budget used` 为最近已留痕 run；与此同时，`Rank 126` 的 source intake card 已存在，且 `generated_at_utc=2026-03-20 17:01 UTC`，可视为 **guard-passed / admit_to_clean_replication_queue**。
- `Paper Seat`：再次实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`，结果仍是 **`EMA = waiting_not_due`**；当前无 `due-now / overdue` lane，最近 due 约为：美股 `~2.8h`、Crypto `~6.8h`、创业板ETF `~61.8h`。

## 为什么本轮合法主动作是 Rank 126
按 `docs/TODO.md` 顶板 `2026-03-20 16:43 UTC` 最新补充：
1. `Run 1 = EMA due-check first`
2. 若 EMA 仍 `waiting_not_due`，`Run 2 = Rank 126 source intake + 两条轻量诚实守门`
3. 若 `Rank 126 guard-pass` 且 EMA 仍 `waiting_not_due`，`Run 3 = Rank 126 1 次最小 clean replication`

本轮满足上述第 3 条，因此只认领 **`Rank 126 / deepest retracement hold-quality gate`** 这 1 个主点，不并开其他候选。

## 本轮实际执行
新建并运行：
- `scripts/build_rank126_deepest_retracement_clean_replication.py`

冻结口径：
- 数据：`BTC/ETH/SOL 120d 15m` 本地 cache
- archetype：只挂 **`fib_retest_long`**（当前最直接、最诚实的最小验证口）
- 执行：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- 训练段冻结参数后去测试段验证
- 比较三臂：
  - `baseline`
  - `current_only`：只看信号当根 low 的 `current_retracement_pct`
  - `current_plus_deepest`：再加最近若干根 trailing-only 的 `deepest_retracement_pct`

训练段选出的最优冻结参数：
- `lookback_bars = 4`
- `current_threshold = 0.79`
- `deepest_threshold = 0.79`

## 硬结论
**`Rank 126 / deepest retracement hold-quality gate = park / evidence pool`**。

翻成人话：
- 只看 `current` 这层还有一点 honest value；
- 但把 `deepest` 一起加进去后，测试段并没有同步改善收益与 hold-quality，反而更像靠缩样本；
- 所以这条线当前**不该升到 P2 / paper candidate**，也不该继续默认占用 Scout 主资源位。

## 关键结果（测试段，6 bps/side）
### 总表
- `baseline`：`14` 笔，`mean_total_return ≈ +0.05%`，`failure_before_target ≈ 42.86%`
- `current_only`：`12` 笔，`trade_count_retention ≈ 85.71%`，`mean_total_return ≈ +0.21%`，`failure_before_target ≈ 41.67%`，`false_hold ≈ 16.67%`
- `current_plus_deepest`：`8` 笔，`trade_count_retention ≈ 57.14%`，`mean_total_return ≈ -0.06%`，`failure_before_target ≈ 50.00%`，`false_hold ≈ 12.50%`

### 直接 verdict-changing 读法
- `current_only` 相对 baseline：
  - `return_delta ≈ +0.16%`
  - `failure_delta ≈ -1.19pct`
  - `false_hold_delta ≈ -4.76pct`
- `current_plus_deepest` 相对 baseline：
  - `return_delta ≈ -0.12%`
  - `failure_delta ≈ +7.14pct`
  - `false_hold_delta ≈ -8.93pct`

也就是说：
- `deepest` 确实能再砍掉一部分“表面守住、路径不干净”的假 hold；
- 但在这次 clean-room 里，它把样本压得更薄以后，**收益和 failure-before-target 没一起变好**，不够诚实支撑升格。

### 分资产测试段
- `BTC`：`current_only` 有改善；`current+deepest` 退化
- `ETH`：`current_only` 基本持平；`current+deepest` 明显转差
- `SOL`：`current+deepest` 与 `current_only` 一样只保留局部改善，但未形成跨资产一致 verdict

## 本轮产物
### artifacts
- `reports/artifacts/scout_rank126_deepest_retracement_hold_quality_15m/signal_catalog.csv`
- `reports/artifacts/scout_rank126_deepest_retracement_hold_quality_15m/trade_log.csv`
- `reports/artifacts/scout_rank126_deepest_retracement_hold_quality_15m/overall_summary.csv`
- `reports/artifacts/scout_rank126_deepest_retracement_hold_quality_15m/asset_summary.csv`
- `reports/artifacts/scout_rank126_deepest_retracement_hold_quality_15m/cost_summary.csv`
- `reports/artifacts/scout_rank126_deepest_retracement_hold_quality_15m/summary.json`

### reader-facing
- `reports/site/factors/scout_rank126_deepest_retracement_hold_quality_15m/report.html`
- `reports/site/reading/repo_scout/rank126_deepest_retracement_hold_quality_clean_replication.html`

## 对 desk 的含义
- `Paper Seat`：仍是 `EMA / running paper / waiting_not_due`
- `Live Seat`：继续暂空
- `Scout Seat`：`Rank 126` 本轮跑完后，当前最诚实位置应改成 **`P0 / park / evidence pool`**，不再默认续命

更直白地说：
- 这轮没有把 `deepest retracement` 证明成可直接晋升的 hold-quality shared gate；
- 若后续还想保留它，最诚实的写法也应降成 **fib retest 的补充诊断读数 / false-hold note**，而不是继续包装成要升 P2 的新 admission layer。

## 下一手建议
若下一轮 `EMA` 仍 `waiting_not_due`，应按顶板回到 **fresh intake reserve / 下一个高边际 Scout 候选**，而不是继续磨 Rank 126 的 wording 或近义 stability。