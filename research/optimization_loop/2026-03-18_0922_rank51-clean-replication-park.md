# 2026-03-18 09:22 UTC — Rank 51 clean replication 完成并压回 park

## 1）本轮先做的状态检查（按 desk 规则）
- 读取并遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD` 与 `Next 3 bot3 runs`。
- 当前 `EMA / Paper Seat` 真实状态：`running paper / waiting_not_due`。
- 最新 `ema_paper_trading_due_guardrail_snapshot.csv` 显示：
  - `美股 1d+1wk -> 2026-03-18 20:00 UTC`
  - `Crypto 1d+1wk -> 2026-03-19 00:00 UTC`
  - `A 股三条 lane -> 2026-03-19 07:00 UTC`
- 因此这轮 `Run 1` 只能是 `EMA due-check only`，不应伪造 refresh；按当前权威板，默认主资源应落到 `Run 2 / Rank 51 minimal clean replication`。
- 先比较 active Scout 候选边际价值：当前只有 `Rank 51 / vwap-trend-defense` 仍是 active fresh repo source，而 `Rank 35b` 仍只是 queue-only fallback，因此本轮继续认领 `Rank 51 > Rank 35b`。
- 工作区存在大量与本轮无关脏文件；本轮仅做 selective 变更，不混提其它条目。

## 2）本轮认领（1 主点 + 1 紧邻子点）
### 主点
- 完成 `Run 2`：`Rank 51 / vwap-trend-defense / session VWAP reclaim + breadth gate` 的 **唯一那手最小 clean replication**。

### 紧邻子点
- 将 hard verdict 写回 `TODO` 顶板权威区，并把 `Run 2` 回退顺序重置到下一条 fresh intake，而不是继续停在 `Rank 51` 的 intake wording。

## 3）执行内容（最小复现口径）
- 执行脚本：
  - `python3 scripts/build_rank51_vwap_trend_defense_clean_replication.py`
- 固定样本与执行：
  - `BTC / ETH / SOL`，`120d`，`15m`，复用本地 cache
  - `UTC session VWAP reset -> signal bar close -> next-bar open -> no-overlap -> hold 8 bars`
  - 成本：`6 / 10 / 15 / 20 bps per side`
- 三臂对照：
  1. `touch_only`
  2. `touch_plus_reclaim`
  3. `touch_reclaim_plus_breadth`
- 本轮只回答四个快筛问题：`post_cost_return / false_retest_4bars_rate / trade_count_retention / positive_asset_ratio`

## 4）关键产物（deployable artifacts）
- 数据产物：
  - `reports/artifacts/scout_rank51_vwap_trend_defense_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank51_vwap_trend_defense_15m/asset_summary.csv`
  - `reports/artifacts/scout_rank51_vwap_trend_defense_15m/time_pocket_summary.csv`
  - `reports/artifacts/scout_rank51_vwap_trend_defense_15m/trades_primary_6bps.csv`
  - `reports/artifacts/scout_rank51_vwap_trend_defense_15m/meta.csv`
- 网页落点（reader-facing）：
  - `reports/site/factors/scout_rank51_vwap_trend_defense_15m/report.html`
  - `reports/site/reading/repo_scout/rank51_vwap_trend_defense_clean_replication.html`

## 5）硬结论（hard verdict）
- 脚本输出主 verdict：`park / evidence pool`
- 主变体（`touch_reclaim_plus_breadth @ 6bps/side`）跨资产结果：
  - `mean_total_return ≈ -43.79%`
  - `positive_asset_ratio = 0/3`
  - `mean_trades ≈ 423.3`
  - `mean_trade_count_retention ≈ 39.10%`
  - `mean_false_retest_4bars_rate ≈ 39.20%`
  - `mean_win_rate ≈ 38.42%`
- 对照臂：
  - `touch_only @ 6bps`：`mean_total_return ≈ -79.13%`，`mean_trades ≈ 1081.7`，`false_retest_4bars_rate ≈ 75.57%`
  - `touch_plus_reclaim @ 6bps`：`mean_total_return ≈ -49.69%`，`mean_trades ≈ 580.0`，`false_retest_4bars_rate ≈ 47.70%`
- 结论解释：
  - `breadth` 确实把 `false_retest` 从约 `75.57% -> 39.20%` 压下来，也没有把样本砍到几乎归零；
  - 但成本后仍是深负，且 `positive_asset_ratio=0/3`，说明它更像一个能“少犯错、但仍不赚钱”的确认层；
  - 在当前 desk 口径下，这还不足以进 `paper candidate pool`，因此最诚实的 hard verdict 仍是 `park / evidence pool`。

## 6）time-pocket honesty
- `touch_reclaim_plus_breadth` 三段时间 pocket 全部仍为负：
  - `bucket_1 ≈ -76.60% / positive_asset_ratio=0/3 / mean_trades≈586.7`
  - `bucket_2 ≈ -79.39% / positive_asset_ratio=0/3 / mean_trades≈588.0`
  - `bucket_3 ≈ -78.34% / positive_asset_ratio=0/3 / mean_trades≈518.7`
- 这说明它不是“只有某一段坏”；更诚实的读法是：当前这条线的 24/7 crypto 迁移版本整体仍不成立。

## 7）对 desk 排班的直接影响
- `Rank 51` 已用掉允许预算，不再占默认 `Run 2`。
- 当前更诚实的回退顺序应是：
  - `Run 1 = EMA due-check only`
  - `Run 2 = fresh paper/repo intake（先从 RECENT_PAPER_SEEDS / quant_digests / validated shortlist 里认领 1 条新的 15m crypto source）`
  - `Run 3 = Rank 35b / tiny-live plumbing（仅当 fresh intake 也真实 exhausted）`
- 也就是说：这轮之后，不该继续围着 `Rank 51` 补 intake / admission 近义文案，而应回到新的 fresh intake。

## 8）本轮验证与执行备注
- 已确认网页落点存在：
  - `reports/site/factors/scout_rank51_vwap_trend_defense_15m/report.html`
  - `reports/site/reading/repo_scout/rank51_vwap_trend_defense_clean_replication.html`
- 未做 git commit：当前工作区存在大量与本轮无关的脏文件与未跟踪产物，不满足安全 selective commit 条件。