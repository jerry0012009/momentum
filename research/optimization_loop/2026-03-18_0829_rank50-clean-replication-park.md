# 2026-03-18 08:29 UTC — Rank 50 clean replication 完成并压回 park

## 1）本轮先做的状态检查（按 desk 规则）
- 读取并遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD` 与 `Next 3 bot3 runs`。
- 当前 `EMA / Paper Seat` 真实状态：`running paper / waiting_not_due`（due guardrail 未出现 `due-now / overdue` lane）。
- 当前 `Next 3` 在本轮执行前是：
  - `Run 1 = EMA due-check only`
  - `Run 2 = Rank 50 minimal clean replication（仅当 EMA 仍 waiting_not_due）`
  - `Run 3 = Rank 51 source intake；再回退 Rank 35b / tiny-live plumbing`
- 工作区存在大量与本轮无关脏文件；本轮仅做 selective 变更，不混提其它条目。

## 2）本轮认领（1 主点 + 1 紧邻子点）
### 主点
- 完成 `Run 2`：`Rank 50 / chanlun-pro structural reclaim gate` 的 **最小 clean replication**。

### 紧邻子点
- 将 hard verdict 写回 `TODO` 顶板权威区，并更新 `Next 3` 顺序到下一条 active Scout。

## 3）执行内容（最小复现口径）
- 新增脚本：
  - `scripts/build_rank50_chanlun_structural_reclaim_clean_replication.py`
- 固定样本与执行：
  - `BTC / ETH / SOL`，`120d`，`15m`，复用本地 cache
  - `signal bar close -> next-bar open -> no-overlap -> hold 8 bars`
  - 成本：`6 / 10 / 15 / 20 bps per side`
- 三臂对照：
  1. `raw_breakout_retest`
  2. `structural_reclaim`
  3. `structural_reclaim_plus_htf`
- 先看四个快筛指标：`post_cost_return / false_reclaim_ratio / trade_count / no_trade_ratio`

## 4）关键产物（deployable artifacts）
- 数据产物：
  - `reports/artifacts/scout_rank50_chanlun_structural_reclaim_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank50_chanlun_structural_reclaim_15m/asset_summary.csv`
  - `reports/artifacts/scout_rank50_chanlun_structural_reclaim_15m/trades_primary_6bps.csv`
  - `reports/artifacts/scout_rank50_chanlun_structural_reclaim_15m/meta.csv`
- 网页落点（reader-facing）：
  - `reports/site/factors/scout_rank50_chanlun_structural_reclaim_15m/report.html`
  - `reports/site/reading/repo_scout/rank50_chanlun_structural_reclaim_clean_replication.html`

## 5）硬结论（hard verdict）
- 脚本输出主 verdict：`park / evidence pool`
- 主变体（`structural_reclaim_plus_htf @ 6bps/side`）跨资产结果：
  - `mean_total_return ≈ -4.63%`
  - `positive_asset_ratio = 0/3`
  - `mean_trades ≈ 12.0`
  - `mean_false_reclaim_ratio ≈ 72.78%`
  - `mean_no_trade_ratio ≈ 87.14%`
- 对照臂：
  - `raw_breakout_retest @ 6bps`：`mean_total_return ≈ -9.34%`，但 `mean_trades ≈ 82.3`
  - `structural_reclaim @ 6bps`：`mean_total_return ≈ -4.85%`，`mean_trades ≈ 12.7`
- 结论解释：
  - `structural_reclaim` 系列确实“少亏”，但主要以大幅砍交易换来；
  - 成本后仍未过正，且 `false_reclaim` 偏高；
  - 不满足推进到 `P1/P2` 的最小诚实门槛，故压回 `park / evidence pool`。

## 6）对 desk 排班的直接影响
- `Rank 50` 已用掉其允许预算，不再占默认 `Run 2`。
- `TODO` 顶板已更新为：
  - `Run 1 = EMA due-check only`
  - `Run 2 = Rank 51 / vwap-trend-defense source intake（仅当 EMA 仍 waiting_not_due）`
  - `Run 3 = Rank 35b / tiny-live plumbing（若 Rank 51 也不合格）`

## 7）本轮验证与执行备注
- 首次运行因脚本复杂度触发超时终止（SIGTERM）；随后将重复信号扫描改为“先预计算信号再复用到不同 cost”，复跑成功并产出完整 artifact。
- 未做 git commit（存在大量与本轮无关脏文件，不满足安全 selective commit 条件）。
