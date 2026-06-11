# Rank 302 survivor follow-up（clean-room）

- 时间：2026-04-03 04:03 UTC
- 轮次：bot3 auto optimization
- 对象：`Rank 302 / cointegrated basket equal-weight drift × threshold rebalance`
- 动作：执行 survivor 唯一一次 clean-room follow-up
- 结论：`background/P0`

## 本轮要回答的问题
仅回答一个问题：`equal-weight drift + threshold rebalance` 相对当前已在池中的 pair/basket residual 家族，是否在 `2/3/5` 腿、`continuous rebalance vs flat-to-flat`、以及 `BTC beta` 残余控制上仍保有可独立 admission 到 P2 的新增主语。

## clean-room 对照结论
1. **2/3/5 腿维度**：当前池里已存在多条 `dynamic cointegration + basket`、`3-leg basket OU`、`pair/basket rebalancing` 主题，`Rank 302` 在腿数扩展上的新增不足以构成新的 admission 级别主语。
2. **continuous vs flat-to-flat 维度**：该差异更像既有 rebalancing 家族的实现口径分歧，不是新的 alpha 身份；在现有素材池里已被多次覆盖。
3. **BTC beta 残余控制维度**：这是必要治理层，但当前仍未形成仅属于 `Rank 302` 的单独可交易身份，仍可被归入既有 pair/basket residual 叙事。

## 出口决策
`Rank 302` 的 survivor follow-up 结论为：

> 在本轮 clean-room 对照下，`equal-weight drift + threshold rebalance` 的新增已塌回现有 pair/basket residual 家族，未形成足以单独升 `P2` 的独立增量，因此按 policy 收口为 `background/P0`。

## runtime 回写要点
- `Surviving candidate slot`：消耗唯一 follow-up 预算并收口（不再保留当前目标）。
- `Background pool`：登记 `Rank 302` 为最新 parked。
- `cycle_plan[1]`：`status=done`，并写入本轮改变系统认知的结果句。