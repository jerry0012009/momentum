# Rank 239 / pair-rebalancing MR × correlation-signed threshold map — first verdict keep_P1

- 时间：2026-03-29 14:24 UTC
- 轮次角色：bot3 auto executor
- 对应 cycle_plan 小点：`pair-rebalancing threshold map alpha`
- 来源 digest：`research/quant_digests/2026-03-29_1350_pair-rebalancing-threshold-map-alpha.md`
- 结论：`keep_P1`
- 正式 Rank：`239`

## 这一步回答的问题
这条 digest 里讲的东西，是否已经足够收窄成一个**边界清楚、可单轮证伪**的新对象，而不是继续停留在“pairs 调仓阈值可能重要”的泛叙事。

## 结论
可以，且应该收窄成：

> **Rank 239 / pair-rebalancing mean reversion × correlation-signed threshold map**

这里的主语不是宽泛的 pairs / stat-arb，也不是“也许该调阈值”这种参数感想，而是一个很具体的 raw-alpha / governance 组合对象：
- **alpha 本体**：两资产等权组合偏离后的 pair-rebalancing mean reversion；
- **核心新增轴**：threshold 不再全局固定，而是按 pair 的相关性签名分 bucket；
- **最小可证伪问题**：`corr-bucket threshold map` 是否能稳定优于 `fixed-threshold baseline`，而不是只证明“高相关 pair 倾向低阈值”这句摘要。

## 为什么这次给 keep_P1，而不是直接升 P2
虽然 digest 已经把对象说清了，但当前证据还停在：
1. 论文全文 + 本地表格抽取；
2. 一个方向正确但收益没活的 `liquid-major 15m perp proxy`；
3. 还没有把同一批可交易 pair 上的 `fixed threshold`、`corr-bucket map`、更复杂 classifier 做并排、诚实、成本后一致对照。

所以它已经**足够独立到值得进入前排**，但还没到 `promote_P2`。

## 为什么不是 background only
因为这条对象已经具备了一个明确且和旧 pairs 家族不同的独立主语：
- 旧 pairs 研究大多在回答 **pair 怎么选 / spread 怎么定义 / signal 怎么算**；
- 这条对象在回答 **同一条 pair-rebalancing alpha 应该用什么 threshold governance**；
- digest 还给出了清楚先验：`高相关 -> 低阈值`，`低/负相关 -> 更高阈值`，这足够形成单轮 follow-up 的具体实验设计。

换句话说，它不是“pairs 也许还能再调一个参数”，而是**threshold governance 本身是否能把 pair-rebalancing 从拍脑袋推进成可治理对象**。

## runtime 改写要点
- 新 fresh intake 获得正式 Rank：`239`
- fresh intake first verdict：`keep_P1`
- 当前 survivor 仍为 `none`；是否进入 survivor follow-up 留给后续合法排班决定

## 一句话结果（用于 state/result）
`pair-rebalancing threshold map alpha` 已足够收窄成 `Rank 239 / pair-rebalancing MR × correlation-signed threshold map`：它的独立主语是 `corr-bucket threshold governance` 是否优于 fixed-threshold baseline，因此本轮 first verdict 诚实记为 `keep_P1`，进入前排但暂不升 `P2`。
