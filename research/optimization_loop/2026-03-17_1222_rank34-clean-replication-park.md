# 2026-03-17 12:22 UTC · Rank 34 chip-distribution clean replication（assumption gate）

## 本轮归属
- Desk lane：`Run 2 / Scout Fast Lane`
- 触发原因：`Paper Seat / EMA` 继续 `waiting_not_due`，due snapshot 显示全 desk 当前无 `due-now / overdue` lane，因此按板上顺序从 Run 1 切到 Run 2。

## 开始前检查
- `TRADING DESK BOARD` 已读，且仅从 `Next 3 bot3 runs` 认领。
- 当前席位状态：
  - `Paper Seat = EMA waiting_not_due`
  - `Live Seat = 空`
  - `Scout Seat = Rank 34`（上轮 intake 后，允许的下一步是 1 次最小 clean replication）
- repo 有大量与本轮无关脏文件，按 selective 改动执行，不混提。

## active Scout 边际价值比较（本轮）
- `Rank 17 / Rank 2 / Rank 29`：当前无真实 append/review need，继续补近义 wiring 边际低。
- `Rank 30~33`：已完成当前允许动作并 park，不应立刻重开。
- `Rank 34`：正好处于上轮限定的下一步（1 次最小 clean replication，先回答 assumption sensitivity）。
- 结论：本轮主资源给 `Rank 34`。

## 本轮主点 + 紧邻子点
- **主点**：执行 `Rank 34` 最小 clean replication（固定历史样本，回答 hard verdict）。
- **紧邻子点**：同步更新 `TODO` 与 reader-facing 页面，把它从 intake 状态推进到 clean-replication verdict。

## 执行动作
1. 新建并运行脚本：
   - `scripts/build_rank34_chip_distribution_clean_replication.py`
   - 固定复用：`BTC/ETH/SOL 120d 15m cache`
   - 三档 synthetic shares anchors：`conservative / neutral / aggressive`
   - 三档规则：`raw_baseline / chip_cost_reclaim / chip_cost_reclaim_plus_winner_ratio`
   - 成本梯度：`6/10/15/20 bps`

2. 生成产物：
   - `reports/artifacts/scout_rank34_chip_distribution_15m/overall_summary.csv`
   - `reports/artifacts/scout_rank34_chip_distribution_15m/asset_summary.csv`
   - `reports/artifacts/scout_rank34_chip_distribution_15m/assumption_sensitivity_summary.csv`
   - `reports/artifacts/scout_rank34_chip_distribution_15m/primary_trades_6bps.csv`
   - `reports/site/factors/scout_rank34_chip_distribution_15m/report.html`
   - `reports/site/reading/trendline_alpha_scout/rank34_chip_distribution_clean_replication.html`

3. 同步更新：
   - `docs/TODO.md`（Rank 34 与 Next 3 调度口径）
   - `reports/site/reading/trendline_alpha_scout/report.html`（Rank 34 卡片由 intake 切到 clean replication）

## 本轮 hard verdict
- **`Rank 34 -> park / evidence pool`**
- 核心证据（主变体 `chip_cost_reclaim`, 6bps/side）：
  - conservative：`mean_total_return≈+18.14%`, `positive_asset_ratio=3/3`
  - neutral：`mean_total_return≈+13.72%`, `positive_asset_ratio=1/3`
  - aggressive：`mean_total_return≈-18.62%`, `positive_asset_ratio=1/3`
- 结论：edge 对 `shares / turnover` 假设过于敏感；假设收紧后跨标的存活与收益明显退化，不够诚实进入 `paper candidate`。

## 最小验证
- 脚本输出：`verdict=park / evidence pool`
- 关键统计已在 stdout 打印并落入 artifact csv。
- reader-facing 页面已落地（factor 页 + reading 页）。

## fallback / 风险记录
- 本轮未触发 `edit exact-text mismatch`；采用脚本更新，避免大文件手工替换失败。

## 提交与后续
- 未提交（存在大量与本轮无关脏文件）。
- 下轮默认：若 `EMA` 仍 `waiting_not_due` 且 `Rank 17/2/29` 无真实 append/review need，则应切到下一条新的 `paper/repo based 5m/15m crypto` fresh intake，而不是继续磨 Rank 34。
