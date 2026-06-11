# 2026-03-19 23:15 UTC — Rank 102 retest 后重破 impulse extreme continuation gate minimal clean replication

## Run 1 -> Run 2 执行
- Run 1：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：`EMA = waiting_not_due`
  - 当前没有 `due-now / overdue` lane
  - 最靠前 lane 仍是 `Crypto 1d+1wk -> due_soon / 约 49 分钟后到点`
- 因此按 `TRADING DESK BOARD` 当前 authoritative `Next 3`，本轮合法主动作只能落在：
  - `Scout Seat / Rank 102 / retest 后重破 impulse extreme continuation gate` 的 **1 次最小 clean replication**

## 开轮检查
- branch：`master`
- repo 工作区仍有大量与本轮无关的既有脏文件；本轮不混提、不清理。
- 最近 optimization logs：
  - `2026-03-19_2258_rank102-impulse-rebreak-intake.md`
  - `2026-03-19_2233_rank101-volume-drydown-clean-replication.md`
  - `2026-03-19_2212_rank101-volume-drydown-intake.md`
- `manual_narrow_paper_last_run_summary.json` 仍未出现新的 `P3 status-changing event`，因此本轮不回头挤占 `P3 continuity` 预算。

## Active Scout 候选边际比较（先比较后认领）
1. **`Rank 102 / retest 后重破 impulse extreme continuation gate`**
   - 顶板已明确要求：若 `EMA` 仍 `waiting_not_due`，本轮就先给它那 `1` 次最小 clean replication。
   - 它直接回答当前三条主线共用的问题：**回踩后能不能快速重破回踩前 impulse extreme，还是只是摸线后继续假延续。**
2. **`Rank 103 / confirmed extremum honest fib anchor`**
   - 继续保留为 `P0 / fresh repo reserve`；只有当 `Rank 102` 本轮直接 hard-fail / exhausted，才轮到它。
3. **`post-break sign-flip density` / `tiny-live plumbing`**
   - 当前都不该抢本轮主资源。

结论：本轮只认领 `Rank 102` 的最小 clean replication，不并开第二条候选。

## 本轮认领
- 主点：`Rank 102 / retest 后重破 impulse extreme continuation gate`
- 紧邻子点：把 hard verdict、reader-facing 页面、`TODO` 顶板一次写齐

## 最小 clean replication 口径
- 新脚本：`scripts/build_rank102_impulse_rebreak_clean_replication.py`
- 复用 cache：`reports/artifacts/scout_tau_band_breakout_15m/cache/`
- 数据口径：`BTC / ETH / SOL | 120d | 15m | next-bar open | no-overlap | 6bps/side`
- 只比较：
  - `baseline`
  - `baseline + impulse_rebreak_gate`
- 统一 shared gate 定义：
  - **long**：近 20-bar breakout 上破后，`5` 根内出现 retest；若 retest 后 `6` 根确认窗内，收盘价重破 retest 前 `impulse high`，才放行
  - **short**：近 20-bar breakout 下破后，`5` 根内出现 retest；若 retest 后 `6` 根确认窗内，收盘价重破 retest 前 `impulse low`，才放行
- 统一冻结到：`signal 当根及之前数据 + next-bar open + no-overlap`

## 最小结果
### 1) setup 级总表
- `ema_psar_long / baseline`
  - `trades = 111`
  - `avg_net_ret ≈ -3.33bps`
  - `false_follow_4bars ≈ 45.05%`
- `fib_retest_long / baseline`
  - `trades = 166`
  - `avg_net_ret ≈ -11.12bps`
  - `false_follow_4bars ≈ 46.39%`
- `breakout_short / baseline`
  - `trades = 596`
  - `avg_net_ret ≈ -8.19bps`
  - `false_follow_4bars ≈ 55.03%`
- `breakout_short / impulse_rebreak_gate`
  - `trades = 237`
  - `avg_net_ret ≈ +6.77bps`
  - `median_net_ret ≈ -18.14bps`
  - `win_rate ≈ 41.35%`
  - `false_follow_4bars ≈ 50.63%`
  - `trade_count_retention ≈ 39.77%`
  - `positive_asset_ratio = 1/3`

### 2) 按资产拆开后的最诚实读法（gate 只在 breakout-short 留下有效样本）
- `BTC / breakout_short + gate`
  - `trades = 81`
  - `avg_net_ret ≈ -2.87bps`
  - `false_follow_4bars ≈ 53.09%`
- `ETH / breakout_short + gate`
  - `trades = 68`
  - `avg_net_ret ≈ +34.03bps`
  - `false_follow_4bars ≈ 38.24%`
- `SOL / breakout_short + gate`
  - `trades = 88`
  - `avg_net_ret ≈ -5.42bps`
  - `false_follow_4bars ≈ 57.95%`

### 3) 这轮最诚实的解释
- 这层 `impulse re-break` gate **确实让 shared continuation 读法更像回事**：至少在 `breakout_short` 这条 lane 里，收益从负值翻到正值，而且保留率还不算极端稀薄。
- 但它的改善目前**不够广**：
  - 最小 clean replication 下，真正留下有效 gate 样本的主要还是 `breakout_short`
  - 跨资产只有 `ETH` 明显转正，`BTC / SOL` 仍没过门
  - `4-bar false-follow-through` 并没有同步明显下降到足够硬的程度
- 所以它还不够诚实到直接升 `P2 / paper candidate`。

## 本轮 hard verdict
- **`Rank 102 = keep_P1 / evidence pool`**

### 为什么不是 `promote_to_P2`
1. 当前正向 pocket 主要集中在 `ETH breakout_short`，不是三资产一致的 shared gate。
2. `positive_asset_ratio` 只有 `1/3`，还不足以支撑 paper candidate。
3. 这轮最想要的副效应——明显压低 `false_follow_through_4bars`——并没有强到足以盖过样本切窄的问题。

### 为什么也不是直接 `park`
1. 它不是纯文案改善；在 `breakout_short` 这条线上，`avg_net_ret` 的确从负值翻到正值。
2. `trade_count_retention ≈ 39.77%`，说明这不是只剩极少数残样本的“漂亮幸存者”。
3. 因此更诚实的分级是：**`P1 evidence_pool / one cheap honesty check left`**。

## 本轮交付（deployable artifact）
- script:
  - `scripts/build_rank102_impulse_rebreak_clean_replication.py`
- artifacts:
  - `reports/artifacts/scout_rank102_impulse_rebreak_continuation_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank102_impulse_rebreak_continuation_15m/asset_summary.csv`
  - `reports/artifacts/scout_rank102_impulse_rebreak_continuation_15m/trade_log.csv`
  - `reports/artifacts/scout_rank102_impulse_rebreak_continuation_15m/verdict_summary.csv`
- reader-facing:
  - `reports/site/factors/scout_rank102_impulse_rebreak_continuation_15m/report.html`
  - `reports/site/reading/repo_scout/rank102_impulse_rebreak_continuation_clean_replication.html`

## 对顶板的直接影响
- `Paper Seat = EMA / running paper / waiting_not_due`
- `Live Seat = 暂空`
- `Rank 102 = P1 evidence_pool / one cheap honesty check left`
- `Rank 103 = P0 fresh repo reserve`
- 当前最新 `Next 3`：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则只给 Rank 102 1 次 truly verdict-changing 的便宜诚实检查（默认优先时间稳定性：最近/较早两半窗拆分）`
  3. `Run 3 = 若 Rank 102 这次 cheap check 后仍不能升格，则直接做 promote_to_P2 / park 二选一；若已直接 park，则切 Rank 103 / confirmed extremum honest fib anchor 的 source intake`

## 最小验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 如实确认当前还是 `waiting_not_due`
- `python3 scripts/build_rank102_impulse_rebreak_clean_replication.py`
  - 已成功写出 artifact 与 reader-facing 页面
- 回读：
  - `reports/artifacts/scout_rank102_impulse_rebreak_continuation_15m/verdict_summary.csv`
  - `docs/TODO.md`
  - 已确认 hard verdict 与更新后的 `Next 3` 写入成功

## 备注
- 本轮没有并开 `Rank 103`
- 本轮没有触发 `P3 continuity` 或 `tiny-live plumbing`
- 工作区仍有大量历史脏文件；本轮未尝试整理、提交或覆盖这些无关改动
