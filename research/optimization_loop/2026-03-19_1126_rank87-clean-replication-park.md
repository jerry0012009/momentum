# 2026-03-19 11:26 UTC — Rank 87 最小 clean replication 后压回 park

## 本轮先做的 desk 检查（Run 1）
- 先执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：`Paper Seat / EMA` 仍是 `waiting_not_due`，无 `due-now / overdue`。
  - 最近 due：美股约 `8.6h`、Crypto 约 `12.6h`、A股约 `19.6h`。
- 结论：本轮不能空转，也不能伪造 paper refresh；主资源应落在 `Scout Seat`。

## 本轮主点 + 紧邻子点
- **主点**：`Run 2 / Rank 87` 最小 clean replication（只做这一条，不并开其他候选）
- **紧邻子点**：同步改写 `TRADING DESK BOARD / Next 3` 与分级，把 `Rank 87` 从 `P1` 收口到 `P0`。

## 先比较 active Scout 候选边际价值（3.5）
本轮执行前按当前板面与 active 队列做了边际价值比较：
1. `Rank 87 / volume-clock + CS spread interaction gate`（唯一 guard-passed 且未跑 clean replication）
2. 两条 breakout-centric backlog（outside-close/back-inside-close；close-range compression）
3. `Rank 82 / 80 / 81`（均为 evidence_pool，不应默认续命）
4. `P3 continuity`
5. `tiny-live plumbing`

因此本轮应先给 `Rank 87` 唯一那次最小复现实验预算。

## 本轮产物（deployable artifacts）
### 新脚本
- `scripts/build_rank87_volume_clock_clean_replication.py`

### 新 artifact
- `reports/artifacts/scout_rank87_volume_clock_cs_spread_15m/overall_summary.csv`
- `reports/artifacts/scout_rank87_volume_clock_cs_spread_15m/setup_summary.csv`
- `reports/artifacts/scout_rank87_volume_clock_cs_spread_15m/asset_summary.csv`
- `reports/artifacts/scout_rank87_volume_clock_cs_spread_15m/trade_samples.csv`
- `reports/artifacts/scout_rank87_volume_clock_cs_spread_15m/meta.csv`

### reader-facing 网页
- `reports/site/factors/scout_rank87_volume_clock_cs_spread_15m/report.html`
- `reports/site/reading/repo_scout/rank87_volume_clock_cs_spread_clean_replication.html`

## clean replication 冻结口径
- 资产：`BTC/ETH/SOL`
- 数据：本地 `120d 15m cache`
- 执行：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- 三条 base setup：`ema_psar_long / fib_retest_long / breakout_short`
- 三臂对照：`baseline / fixed_clock_gate / volume_clock_gate`
- gate 构造：
  - fixed clock：`00/08/16 UTC` 最近 anchor
  - volume clock：最近 24h 成交量最大的 30m anchor
  - 二者都要求：anchor 邻近窗口 + 同向 impulse + spread z-score 支持

## 本轮 hard verdict
- **`Rank 87 / volume-clock + CS spread interaction gate = park / evidence_pool`**

关键证据（6bps/side）：
- `baseline`：`mean_total_return ≈ -28.85%`，`positive_asset_ratio=1/3`，`retention≈86.96%`
- `fixed_clock_gate`：`mean_total_return ≈ -5.73%`，`positive_asset_ratio=1/3`，`retention≈8.22%`
- `volume_clock_gate`：`mean_total_return ≈ -0.67%`，`positive_asset_ratio=1/3`，`retention≈3.42%`

读法：`volume_clock` 确实“少亏”，但主要靠极低 retention（样本过度收缩）换来，不满足升 `P2` 的诚实门槛。

## 对 desk board 的写回
已更新 `docs/TODO.md`：
- 新增 `11:25 UTC` 补充；
- 将 `Rank 87` 收口为 `P0 / park`；
- 改写 `Next 3` 为：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = fresh paper/repo intake（按 7.10，只认领 1 条 5m/15m crypto source，默认优先非 breakout-centric）`
  3. `Run 3 = 新 source guard-passed 后给 1 次最小 clean replication；fresh intake exhausted 才回退 backlog/plumbing`

## 实施中的最小修复记录（8.1）
- 首版脚本运行时出现两处问题并已就地修复：
  1. 列对齐时带入重复 `open/close` 字段导致 `float()` 转换报错；改为仅对齐 gate 必要列。
  2. 初版循环过慢（按 cost 重复回测）；改为先算 `gross_return`，再在汇总阶段按 `cost` 批量换算 `net_return`。
- 以上均已落到最终脚本并成功跑完。

## 脏文件与提交
- 当前 repo 脏文件很多（`git status --short | wc -l = 1390`），且大量改动与本轮无关。
- 本轮未提交，避免混提。

## 下一轮建议
- 若 `EMA` 仍 `waiting_not_due`，按新 `Next 3` 直接做 1 条 fresh intake（优先非 breakout-centric shared gate）。
- 不再继续给 `Rank 87` 默认 Scout 预算，除非有新证据能改变 `park` verdict。
