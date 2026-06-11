# 2026-03-18 11:35 UTC — Rank 54 最小 clean replication 后压回 park

## 为什么这次选这个
- 先按 `TRADING DESK BOARD` 执行 `Run 1`：`ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 没有新的 `due-now / overdue` lane，`EMA` 继续处于 `running paper / waiting_not_due`。
- 因此按当前权威 `Next 3`，本轮应执行 `Run 2 = Rank 54 / LVN rejection + POC acceptance gate minimal clean replication`。
- 本轮只认领 1 个主点，不并行打开新候选，也不回头挤占 `P3 continuity`。

## 做了什么改动
### 主点：Rank 54 最小 clean replication
- 新增脚本：
  - `scripts/build_rank54_lvn_poc_acceptance_clean_replication.py`
- 新增 artifact：
  - `reports/artifacts/scout_rank54_lvn_poc_acceptance_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank54_lvn_poc_acceptance_15m/asset_summary.csv`
  - `reports/artifacts/scout_rank54_lvn_poc_acceptance_15m/time_pocket_summary.csv`
  - `reports/artifacts/scout_rank54_lvn_poc_acceptance_15m/trades_primary_6bps.csv`
  - `reports/artifacts/scout_rank54_lvn_poc_acceptance_15m/meta.csv`
- 新增 reader-facing 页面：
  - `reports/site/factors/scout_rank54_lvn_poc_acceptance_15m/report.html`
  - `reports/site/reading/repo_scout/rank54_lvn_poc_acceptance_clean_replication.html`

### 紧邻子点：authoritative board 最小写回
- 在 `docs/TODO.md` 顶部权威区追加 `2026-03-18 11:35 UTC` 补充：
  - 写回 `Rank 54` 最小 clean replication 的 hard verdict；
  - 把 `Next 3` 收紧回 `EMA due-check only -> fresh paper/repo intake -> Rank 35b > Rank 16b > tiny-live plumbing` 的读法。

## 验证 / 证据
### 1）Paper Seat 仍是 waiting_not_due
`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 当前显示：
- `美股 1d+1wk -> 2026-03-18 20:00 UTC`
- `Crypto 1d+1wk -> 2026-03-19 00:00 UTC`
- `A股三条 lane -> 2026-03-19 07:00 UTC`
- `due_bucket` 全部仍为 `waiting_not_due`

因此本轮不应伪造 `EMA` continuation，而应落回 `Scout Seat`。

### 2）最小 clean replication 口径
- 固定复用 `BTC/ETH/SOL 120d 15m` cache，不追新 bar；
- 两条 base archetype：
  - `ema_pullback_long`
  - `breakdown_reclaim_short`
- 三臂比较：
  - `base`
  - `lvn_rejection`
  - `lvn_rejection_plus_poc_acceptance`
- 执行冻结为：`signal bar close -> next-bar open -> no-overlap -> hold 8 bars`
- volume-profile 只用过去 `48` 根 15m bar 的 rolling histogram 近似 `POC/LVN`，不允许未来 bar 回填。

### 3）主读法结果
`overall_summary.csv` 显示主读法 `breakdown_reclaim_short + lvn_rejection_plus_poc_acceptance` 在 `6bps/side` 下：
- `mean_total_return ≈ 0.00%`
- `positive_asset_ratio = 0/3`
- `mean_trades = 0.0`
- `mean_trade_count_retention = 0.00%`
- `time-pocket` 无可用样本

直白读法：`POC acceptance` 这一层一加上去，样本直接被砍到没有可交易事件，已经足够给出 hard verdict，不需要再继续磨 wording。

### 4）相邻变体的诚实读法
- `ema_pullback_long + lvn_rejection` 确实把跨资产 `mean_total_return` 拉到约 `+1.40%`，且 `false_hold_4bars_rate≈4.76%`；
- 但它的 `mean_trade_count_retention≈22.45%`，只剩很薄的样本，而且跨资产仍只有 `1/3` 为正；
- short 主读法更直接：`breakdown_reclaim_short + lvn_rejection` 只剩 `mean_trades≈0.33`，仍无法支撑继续 admission。

因此当前更诚实的结论不是“还差一个漂亮解释页”，而是：**acceptance gate 在 desk 语义下更像极窄 sample veto，而不是足够稳的 shared confirmation layer。**

## 当前硬结论
- **`Rank 54 / LVN rejection + POC acceptance gate = park / evidence pool`**。
- 更直白地说：这条线已经不该继续停在 active clean-replication 队列；若后续继续认领，默认只能按 `park` 证据池读法处理。

## Reader-facing 落点
- `reports/site/factors/scout_rank54_lvn_poc_acceptance_15m/report.html`
- `reports/site/reading/repo_scout/rank54_lvn_poc_acceptance_clean_replication.html`
- `docs/TODO.md` 顶部权威板已同步写回

## 风险 / 边界
- 这次是 desk clean-room 迁移，不是对原 repo NQ futures volume-profile 执行层的全量复刻；
- `POC/LVN` 目前是用 `15m OHLCV + rolling histogram` 做近似，结论只说明它在当前 desk 约束下不够诚实，不代表原作者在原市场语境下一定无效；
- 当前仓库存在大量与本轮无关的脏文件，未做 commit，避免混提。

## 下一步建议
1. 下一轮先继续 `EMA due-check only`；
2. 若仍 `waiting_not_due`，按 `7.10` 回到 fresh paper/repo intake，从：
   - `docs/RECENT_PAPER_SEEDS.md`
   - `research/quant_digests/INDEX.md`
   - `reports/artifacts/literature/validated_alpha_shortlist_2026-03-10.md`
   再认领 1 条新的 `5m / 15m crypto` source；
3. 只有 fresh intake 也真实 exhausted，才回退比较 `Rank 35b > Rank 16b > tiny-live plumbing`。

## Commit hash
- 未提交。
- 原因：当前 git 工作区有大量与本轮无关的脏文件与未跟踪产物，不安全 selective commit。
