# Rank 409 P2 admission（出口决策轮-2）— drop_to_background（P0）

- 时间：2026-04-15 06:46 UTC
- 执行者：bot3
- 对应 cycle_plan 小点：#1 `Rank 409 / BTC-beta-neutral residual momentum ranking shell（re-scoped to residual sign-fade @1h->24h hold）`

## 本轮执行
按上轮唯一剩余 blocker（time-stability）做最小收口：
1. 固定同一策略骨架（`1h residual sign-fade @24h hold`）与执行现实口径（`t+2` delay）；
2. 在统一成本 `6/8 bps` 下，做同场对照：
   - 原版 baseline（全时段）；
   - 单一可执行 re-scope：`UTC 07:00–20:59` session gate（Europe+US 流动性窗口）。

## 关键工件
- `research/optimization_loop/artifact_rank409_p2_exit_round2_session_gate_compare_20260415.csv`
- `research/optimization_loop/artifact_rank409_p2_exit_round2_session_gate_compare_20260415.json`

## 关键结果（统一 6/8 bps + t+2）
样本：`2026-03-21 13:00 UTC ~ 2026-04-15 06:00 UTC`，test bars=`594`。

- `BTC proxy` baseline：
  - `6bps: -0.225 bps/bar`，`8bps: -0.308 bps/bar`；前后半段均为负。
- `BTC proxy` + session gate（07–20 UTC）：
  - `6bps: -0.252`，`8bps: -0.324 bps/bar`；较 baseline 未改善。
- `BTC+ETH proxy` baseline：
  - `6bps: -0.260`，`8bps: -0.342 bps/bar`；前后半段均为负。
- `BTC+ETH proxy` + session gate：
  - `6bps: -0.245`，`8bps: -0.317 bps/bar`；虽略减亏，但仍稳定为负。

## 出口决策
- 本轮已按要求完成“单一 re-scope 方向 vs 原版”的同场比较；
- 结论是：在 admission 指定的现实口径（`t+2` + `6/8bps`）下，**alpha 不成立**，且唯一 blocker（time-stability）并未被 session gating 修复；
- 不存在可支撑 `promote_P3` 的费后稳定 pocket，也没有剩余“单一可修复 blocker”。

## 结论（改变系统认知）
`Rank 409` 完成 P2 出口决策：在统一 `t+2` 与 `6/8bps` 口径下，baseline 与单一 session re-scope 同时失效，故从 `Active P2` **收口为 `drop_to_background (P0)`**，不再占用前排槽位。