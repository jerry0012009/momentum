# Rank 412 survivor 唯一 follow-up：timestamp-faithful event replay（结论：drop_to_background/P0）

- 时间：2026-04-15 09:28 UTC
- 执行器：bot3
- 对象：`Rank 412 / Binance listing announcement × cross-venue catch-up shell`
- 对应 cycle_plan：#1（survivor 唯一 follow-up）

## 本轮执行（最小且决定性）
按 state 要求仅做一个最小 honesty/realism 决定性检查：
- 事件源：Binance 公告 API（`/bapi/apex/v1/public/apex/cms/article/list/query`）中标题含 `will list` 的历史事件；
- `t0`：公告 `releaseDate`；
- 入场：最早 `t0+2m`（按分钟对齐）；
- 可交易腿：Bybit linear `SYMBOLUSDT` 1m K 线（作为跨 venue 可交易代理）；
- 出场窗口：`+1m / +3m / +5m`（对应从 `t0+2m` 到 `t0+3/5/7m`）；
- 成本阶梯：统一扣减 `4/6/8 bps`（round-trip）；
- 最小流动性过滤：入场分钟成交额 `>= 50,000 USDT`。

样本覆盖：
- 原始 `will list` 事件：120
- 通过可交易与数据完整性过滤后的有效事件：26

## 结果（改变系统认知）
`Rank 412` 在统一 `t0+2m + 4/6/8bps` 口径下**只在 3m 持有窗呈现净正均值**，`1m` 明显为负、`5m` 在 8bps 下转负，无法满足“跨 1m/3m/5m 稳健净 alpha”门槛；因此 survivor 唯一 follow-up 结论为 **`drop_to_background(P0)`**，不升 `P2`。

关键统计（bps）：
- 1m：gross mean `-24.21`；net@4/6/8 = `-28.21 / -30.21 / -32.21`
- 3m：gross mean `+36.58`；net@4/6/8 = `+32.58 / +30.58 / +28.58`
- 5m：gross mean `+6.56`；net@4/6/8 = `+2.56 / +0.56 / -1.44`

## honesty / execution realism 口径说明
- 使用 `t0+2m` 规避“公告即刻可成交”的重放乐观偏差；
- 采用统一成本阶梯与最小流动性门槛；
- 结果显示 edge 强依赖单一窗口（3m）且跨窗口不稳，按 policy 不进入 P2 admission。

## runtime 回写要点
- `Surviving candidate slot`：`followup_budget_remaining -> 0`，当前对象完成唯一 follow-up 并退出前排；
- `Background pool`：新增 `Rank 412` 停放记录；
- `cycle_plan #1`：`status -> done`，写入本轮出口结论。
