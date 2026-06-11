# 2026-03-25 08:18 UTC — ETH exchange netflow short alpha fresh intake：先 `park`，不进 P1

## 本轮执行对象
- slot: Fresh intake slot
- candidate: 2026-03-25 quant digest《ETH exchange netflow intraday short alpha》
- source: `research/quant_digests/2026-03-25_0805_eth-exchange-netflow-intraday-short-alpha.md`
- policy动作: 只回答 `park / keep_P1`，不额外扩展排班

## 最小公开证据
- 论文主张本身清楚：`ETH 交易所净流入上升 -> 后续 1~6h ETH 回报偏负`，且同文把 `USDT inflow` 定义成更偏 bullish 的 companion flow。
- 从 raw alpha 语义上看，这更像“链上卖压上所”的事件驱动 short 线索，而不是泛泛情绪因子。

## 本地快检（诚实可执行性）
本轮没有把重点放在复读论文显著性，而是检查它是否满足当前 auto loop 对 fresh intake 的“便宜、可快速独立验证”门槛：

1. workspace 内未发现现成可复用的 `ETH exchange netflow` 小时级序列，也没有现成的交易所地址标签治理产物可直接接到 `ETHUSDT` 事件回测；
2. 这条 alpha 的最小真实实现并不是普通行情快检，而是先要解决 **交易所地址标签 + 多地址归集 + 小时聚合口径**；
3. 若没有这层数据治理，只能停留在论文 sign 复述，无法完成当前轮要求的“最小本地 honesty check”；
4. 现阶段 front slot 更适合留给能用公开行情/成交/仓位等现成数据在 1 轮内完成 honest quick check 的候选，而不是先吞一个外部数据工程项目。

## 收口判断
**结论：先 `park`，不进 `keep_P1`。**

改变系统认知的一句话：
> 这条 ETH exchange netflow short idea 的问题不是论文方向不清，而是它当前首先是“外部链上标签与聚合工程项目”，还不满足本轮 auto loop 对 fresh intake 的低摩擦诚实验证门槛，因此先停在 background research，不占用 front/survivor 资源。

## 对 runtime 的直接影响
- Fresh intake slot: 继续 `vacant`
- Surviving candidate slot: 不生成新 survivor
- Active P2 slot: 保持 `none`
- cycle_plan 第 3 项: `done`
- cycle_plan 第 4 项: 因第 3 项未产出 `keep_P1`，应转为 `blocked`

## 为什么这不是否定论文
这不是说论文没价值，而是说它**不适合当前这一轮 bot3 自动执行节奏**：
- 若未来专门开一个“外部链上数据接入/地址标签治理”轨道，它可以重新作为 on-chain flow 分支候选；
- 但在当前 bot2/bot3 机制下，它还不够“便宜可诚实验证”，因此最优动作是尽快 `park`，把前排让给更容易完成 honest transfer 的 raw alpha。
