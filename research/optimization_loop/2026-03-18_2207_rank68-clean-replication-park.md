# Rank 68 / block-mitigation retest score minimal clean replication

## 轮次定位
- 时间：2026-03-18 22:07 UTC
- 席位：`Scout Seat`
- 本轮主点：`Run 2 / Rank 68 minimal clean replication`
- 紧邻子点：`queue-facing 更新（TODO 顶板）`

## 开始前检查
- `Run 1 / EMA due-check`：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍无 `due-now / overdue`；最早仍是 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC / due_soon`。
- `P3 continuity`：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 最新一次仍是 `new_closed_trades_appended=0`，没有新的 status-changing event。
- `TRADING DESK BOARD` 最新授权顺序：`Run 1 = EMA due-check only`，`Run 2 = Rank 68 minimal clean replication`，`Run 3 = 若 Rank 68 不升层则先回 fresh source intake`。
- git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件；本轮只新增 `Rank 68` 对应脚本、artifact、reader-facing 页面、TODO 顶板与本轮日志，不做混提。

## 本轮最小实验口径
- 数据：固定复用 `BTC/ETH/SOL 120d 15m` 本地 cache，不追新 bar、不做重型下载。
- base archetype：`ema_psar_long`、`fib_retest_long`、`breakout_short`。
- 四臂固定为：
  1. `base`
  2. `plus_block_length`
  3. `plus_block_length_and_range`
  4. `plus_full_block_score`
- 最小 block 定义：在信号前回看最近 `3~10` 根 closed bars，要求 `zone_range / ATR <= 2.8`、`median_body_pct <= 0.6`、`drift_share <= 0.45`。
- `full` gate 只再加最便宜四项：`L >= 4`、`range_pct >= 0.15%`、`vol_ratio >= 1.0`、`retest_depth <= 0.6`。
- 执行统一冻结到：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`。
- 首轮只看：`post-cost return`、`trade count retention`、`failure-before-target`、`target-hit within 8/12 bars`。

## 本轮新增产物
1. 脚本：
   - `scripts/build_rank68_block_mitigation_clean_replication.py`
2. Artifact：
   - `reports/artifacts/scout_rank68_block_mitigation_retest_score_15m/signal_windows.csv`
   - `reports/artifacts/scout_rank68_block_mitigation_retest_score_15m/trade_log.csv`
   - `reports/artifacts/scout_rank68_block_mitigation_retest_score_15m/asset_summary.csv`
   - `reports/artifacts/scout_rank68_block_mitigation_retest_score_15m/overall_summary.csv`
   - `reports/artifacts/scout_rank68_block_mitigation_retest_score_15m/feature_board.csv`
   - `reports/artifacts/scout_rank68_block_mitigation_retest_score_15m/time_pockets.csv`
   - `reports/artifacts/scout_rank68_block_mitigation_retest_score_15m/setup_compare.csv`
3. Reader-facing 页面：
   - `reports/site/factors/scout_rank68_block_mitigation_retest_score_15m/report.html`
   - `reports/site/reading/repo_scout/rank68_block_mitigation_retest_score_clean_replication.html`
4. Queue-facing 更新：
   - `docs/TODO.md` 顶部 `Next 3 bot3 runs` 已补 `2026-03-18 22:07 UTC` 最新块。

## 关键信号覆盖
- `breakout_short`：`has_block_ratio≈61.90%`，`mean_block_length≈7.36`，`mean_retest_depth≈0.12`。
- `ema_psar_long`：`has_block_ratio≈92.73%`，`mean_block_length≈8.83`，但 `mean_retest_depth≈0.69`，说明很多信号其实已经回踩得很深。
- `fib_retest_long`：`has_block_ratio≈88.24%`，`mean_block_length≈8.57`，`mean_retest_depth≈0.57`。
- 直观读法：**样本里不缺“能识别出 block”的事件，真正的问题是 `full` gate 一加上回踩深度和量能后，覆盖掉得太快。**

## 关键结果（6bps / side）
- `ema_psar_long`：
  - `base≈-3.79%`
  - `L≈-3.31%`（retention≈91.43%）
  - `L+R≈-3.31%`（retention≈91.43%）
  - `full≈-1.46%`（retention≈8.57%，failure-before-target≈16.67%，target-hit-12≈50.00%）
- `fib_retest_long`：
  - `base≈1.20%`
  - `L≈0.65%`（retention≈87.88%）
  - `L+R≈0.65%`（retention≈87.88%）
  - `full≈-0.02%`（retention≈9.09%，target-hit-12≈66.67%）
- `breakout_short`：
  - `base≈-3.54%`
  - `L≈-3.89%`（retention≈56.28%，failure-before-target≈6.94%）
  - `L+R≈-3.85%`（retention≈54.83%）
  - `full≈-0.98%`（retention≈21.45%，failure-before-target≈4.76%，positive_asset_ratio≈33.33%）

## Hard verdict
**`Rank 68 / block-mitigation retest score = park / evidence pool`**

## 为什么是这个 verdict
- `full` gate 的确让 `ema_psar_long` 与 `breakout_short` 少亏，也明显压低了 `failure-before-target`；但这主要建立在**极重砍样本**之上：
  - `ema_psar_long` retention 只剩 `≈8.57%`
  - `fib_retest_long` retention 只剩 `≈9.09%`
  - `breakout_short` retention 只剩 `≈21.45%`
- `fib_retest_long` 甚至从 `base≈+1.20%` 被压到 `full≈-0.02%`，说明这条 gate 目前并没有形成三条主线共用的 shared retest-quality 语言，反而把原本还能赚钱的一条线筛坏了。
- `plus_block_length` / `plus_block_length_and_range` 几乎没带来结构性改善：`ema_psar_long` 只是少亏一点，`fib_retest_long` 与 `breakout_short` 都没有得到更诚实的统一提升。
- 更直白地说：**这条线现在更像“把一小撮看起来更干净的样本挑出来”，而不是一个对 desk 有普适增量的低成本 gate。**

## 对交易台顺序的影响
- `Rank 68` 已消耗完当前允许的 `1 次 minimal clean replication` 预算，不应继续在 fast-lane 队首反复打磨。
- 当前更诚实的 active Scout 顺序更新为：
  - `fresh source intake（先从 RECENT_PAPER_SEEDS / quant_digests / validated shortlist 再认领 1 条新的 5m / 15m crypto source）`
  - `Rank 35b`
  - `Rank 16b`
  - `tiny-live plumbing`
- 更新后的 `Next 3`：
  - `Run 1 = EMA due-check only`
  - `Run 2 = 若 Rank 68 verdict 不足以升到下一层，则继续按 7.10 先从 RECENT_PAPER_SEEDS / quant_digests / validated shortlist 再认领 1 条新的 5m / 15m crypto source`
  - `Run 3 = 若新的 fresh source 已 guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication；只有 fresh source 这一层也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`

## 最小验证
- 成功执行：`python3 scripts/build_rank68_block_mitigation_clean_replication.py`
- 结果：脚本完成并输出 `verdict=park / evidence pool`
- 备注：运行中仅出现 pandas `FutureWarning(observed=False)`，不影响本轮 artifact 与 verdict。

## 提交
- 未提交（工作区有大量与本轮无关的脏文件，避免混提）。
