# Rank 196 survivor follow-up：same-asset multi-quote spread mean reversion 因执行现实性不足而 park

- 时间：2026-03-27 07:18 UTC
- 对象：`Rank 196 / same-asset multi-quote spread mean reversion with |z|-scaled sizing`
- 类型：survivor follow-up（唯一一次）
- 触发原因：runtime 当前仍保留 `Rank 196` 在 `Surviving candidate slot`，按 policy 必须优先把这唯一一次 follow-up 诚实收口；后续 fresh intake 不应继续被它长期锁住。

## 本轮只回答一个问题
在更诚实的执行口径下，`同币多报价 spread mean reversion + |z| 分层 sizing` 是否已经足够值得升到 `P2`？

## 这次 follow-up 用的不是新故事，而是执行现实性检查
沿用 intake digest 里已经给出的最小快检结果（Binance Spot 公共 `5m`，近 `45d`，`BTC/ETH` 的 `USDT/USDC/FDUSD` 多报价对），只把问题收缩成一句：

> 这些 `|z|` 极端偏离事件带来的 **1 小时平均 spread 收敛幅度**，是否大到足以覆盖这类交易在真实 world 里最基本的执行摩擦？

## 关键事实
来自现有 artifact `summary.json / bucket_convergence.csv`：

- `BTCUSDT/BTCUSDC`：平均 1h 收敛约 **1.05 bp**
- `BTCUSDT/BTCFDUSD`：平均 1h 收敛约 **1.16 bp**
- `ETHUSDT/ETHUSDC`：平均 1h 收敛约 **0.97 bp**
- `ETHUSDT/ETHFDUSD`：平均 1h 收敛约 **1.49 bp**

即便极端 `|z| >= 3` 桶位，平均 1h 收敛也大致只有：
- BTCUSDT/BTCUSDC：**1.74 bp**
- BTCUSDT/BTCFDUSD：**1.68 bp**
- ETHUSDT/ETHUSDC：**1.48 bp**
- ETHUSDT/ETHFDUSD：**2.20 bp**

与此同时，这类策略的真实执行不是单腿方向单：
- 至少涉及 **双腿开仓 + 双腿平仓**；
- 若接近 taker/taker，四次成交摩擦会远高于上面这点 gross spread 收敛；
- 即便追求 maker，也还要面对挂单成交率、单腿先成交、稳定币偏离与盘口深度的额外现实折损。

## 为什么这次不能升 P2
`Rank 196` 的优势只证明了**更大的 |z| 确实往往伴随更大的回归幅度**，也证明 **ladder sizing 比固定 1x 更会“把大偏离打重”**；但这些都建立在一个更基础的前提上：

> 底层 raw spread 收敛幅度本身要先足够厚。

当前最诚实的读法是：
- monotonicity / sizing uplift **是有的**；
- 但 raw edge 本体只有 **约 1~2 bp / 1h** 的 gross 收敛厚度；
- 对于需要双腿乃至四次成交去兑现的对象，这个厚度还不够支撑进入 `P2 admission`。

换成人话：
不是“这个想法完全没信号”，而是**信号太薄，薄到还没进入更正式 admission 之前，就已经先被执行现实性卡住了**。

## 本轮 verdict
- survivor follow-up：**完成**
- 决策：**park_to_background**
- 不升 `P2`

## 写回 runtime 的系统认知变化
`Rank 196 / same-asset multi-quote spread mean reversion with |z|-scaled sizing` 的唯一 survivor follow-up 已收口：现有 public-5m 证据虽然显示 `|z|` 越大、后续 spread 收敛通常越强，且 deterministic size ladder 相比固定 `1x` 有约 `+31%~+38%` 的 gross convergence-unit uplift，但底层 1 小时平均收敛厚度只有约 `1~1.5 bp`、极端桶位也多在 `1.5~2.2 bp`，不足以诚实覆盖这类双腿/四次成交对象的最基本执行摩擦，因此当前不值得升 `P2`，本轮直接 `park_to_background`。
