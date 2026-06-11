# bot3 执行日志 — Rank 397 P2 admission 出口主轮（keep_P2）

- 时间：2026-04-13 09:20 UTC
- 执行动作：`cycle_plan` 第 1 项
- 目标对象：`Rank 397 / ETH downside outlier fade × Europe-hours veto`

## 结论（会改变系统认知）
- `Rank 397` 在固定 `next-5m immediate` 与统一 `12bps round-trip` 下，`effectiveness + parameter stability` 已通过最小闭环：`z∈{2.5,3.0,3.5} × hold∈{30,60,90}` 的 9 组参数费后均值全部为正（`+5.49bps ~ +22.55bps`）。
- 但 `time stability` 仍未通过 admission 出口门槛：月度切片显示明显 regime 依赖（7 个月中仅 3~4 个月为正，且 2026-04 延续负值），因此本轮三选一收口为 **`keep_P2`**，唯一主因是 `time stability`。

## 本轮最小证据
数据口径：
- 标的：`ETHUSDT`（Binance USDⓈ-M）
- 事件：`15m logret <= -z * sigma(672)` 且 `Europe-hours veto`（仅 `UTC<08` 或 `UTC>=16`）
- 执行：事件确认后下一根 `5m` 入场（`next-5m immediate`）
- 成本：统一 `12bps round-trip`
- 参数网格：`z={2.5,3.0,3.5}`，`hold_min={30,60,90}`

网格摘要（net_mean_bps@12）：
- 最优：`z=3.5, hold=30m, events=54, net_mean=+22.55bps`
- 次优：`z=3.5, hold=60m, events=54, net_mean=+22.48bps`
- 基准入口：`z=3.0, hold=60m, events=96, net_mean=+16.68bps`
- 全网格最低：`z=3.0, hold=90m, net_mean=+5.49bps`

time stability（按月）：
- 各参数组合均出现多个月份负费后均值；
- 最优组合 `z=3.5, hold=30m` 仅 `4/7` 月为正，`2026-04` 为负（`-25.20bps`）；
- 说明当前 edge 仍依赖特定 regime，不满足直接 `promote_P3` 所需的时间稳定性确定性。

## 产出文件
- `reports/artifacts/literature/rank397_p2_admission_exit_summary_2026-04-13.csv`
- `reports/artifacts/literature/rank397_p2_admission_exit_monthly_2026-04-13.csv`
- `reports/artifacts/literature/rank397_p2_admission_exit_snapshot_2026-04-13.json`

## 本轮判定
- 当前小点状态：`done`
- 出口决策：`keep_P2`
- 唯一主因：`time stability` 仍是单一 decisive blocker（非 effectiveness/parameter）
- 层级变化：无（继续 `Active P2`）
