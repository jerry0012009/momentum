# Rank 221 / base imbalance × next-event clock alpha — fresh intake 首轮判分：keep_P1

- 时间：2026-03-28 12:14 UTC
- 对象：`research/quant_digests/2026-03-28_1115_base-imbalance-hawkes-eventtime-alpha.md`
- 结论：`keep_P1`
- 新分配 Rank：`221`
- 本轮角色：fresh intake 首判

## 一句话结论
这篇 Hawkes LOB 论文真正留下的不是一篇泛 event-time ML 素材，而是一条值得保留到前排做唯一一次 follow-up 的 **`base imbalance × next-event clock` 微结构 raw alpha**；但当前公开证据仍主要停在单所单样本、next-event/秒级、且未计成本的 proof-of-concept，尚不足以直接升到 `P2`。

## 为什么不是直接 drop
1. **base alpha 清楚**：核心不是“用 Hawkes 很高级”，而是盘口前几档形状不对称（base imbalance）本身就带下一次有效价格变动方向信息。
2. **clock layer 有明确增益假说**：论文最有价值的地方是把“方向信号”和“兑现时钟”拆开，留下了 `BI only` 与 `BI × high-intensity gate` 可直接比较的最小实验框架。
3. **公开可复现门槛不算离谱**：第一版不必完整复刻 Hawkes MLE，只要有公开 websocket 的 top-10 depth + trade/update burst，就能先检验 clock gate 是否真的让极短 markout 更可交易。
4. **与现有前排素材互补**：它补的是微结构 execution-trigger 家族，而不是又一条慢变量/链上/横截面叙事。

## 为什么还不能直接升 P2
1. **样本窄且单所单资产**：原文主要是 Bitfinex `USDT/USD`、2019 年短样本，不能默认外推到 BTC/ETH/SOL perp。
2. **兑现窗口过短**：论文原生更接近 next-event / next-few-second；还没证明 edge 能诚实外溢到 desk 真正关心的 `1m/3m/5m` after-cost markout。
3. **成本 realism 缺失**：原文 toy trading 不计手续费与滑点；若 edge 只够覆盖 paper world，就不能进 admission。
4. **实现复杂度仍需节制**：若没有先证明 `BI × 简化 intensity proxy` 已明显优于 `BI only`，直接上完整 Hawkes/COE 会先滑成模型工程，而不是 cheap-but-decisive validation。

## 本轮正式 verdict
- `Rank 221 / base imbalance × next-event clock alpha`：**keep_P1**
- 保留原因：它留下了一条可独立建模、可独立回测、可独立关停的微结构 raw alpha 原子，不只是方法论注记。
- 不升 `P2` 原因：当前还缺唯一关键 admission bridge——**公开盘口数据下，`BI × high-intensity gate` 是否能在现实成本口径下稳定外溢到 `1m/3m/5m` 标记收益**。

## 唯一 survivor follow-up 应该回答什么
只做一次最小诚实检查：

> 用公开 websocket 的 BTC/ETH/SOL perp top-10 depth + event-burst proxy，直接比较 `BI only` 与 `BI × high-intensity gate` 在 `1m/3m/5m` after-cost markout 上是否留下稳定增益；若没有，就按 `keep_P1 后转 background` 收口。

## 对 runtime 的影响
- fresh intake 已正式判分并获得 `Rank 221`
- survivor 槽位应切换到 `Rank 221`
- `followup_budget_remaining = 1`
