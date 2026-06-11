# 2026-04-09 05:00 UTC · Rank 4 fresh intake first verdict

## 本轮执行对象
- cycle step: `2`
- target: `research/park_reframe/2026-03-24_1430_rank4-park-reframe.md`
- action: 判断 `Rank 4` 的 `BTC-ETH spread z-score direct pairs entry -> shared risk overlay / position-sizing gate` 是否已足够从 parked pairs 主题里升成一个独立、queue-facing 的 fresh intake pocket。

## 读取与约束
本轮只做这一个 fresh intake 小点，不重排 `cycle_plan`，也不回头改 policy / brief。

主读证据：
- `research/optimization_loop/2026-03-16_1508_rank4-pairs-clean-replication-park.md`
- `research/park_reframe/2026-03-22_2241_rank4-park-reframe.md`
- `research/park_reframe/2026-03-24_1430_rank4-park-reframe.md`
- `research/quant_digests/2026-03-24_0153_hf-pairs-threshold-governance-not-dogma.md`
- `research/quant_digests/2026-03-24_1424_rl2-pairs-dynamic-scaling-fullstack.md`

## 这一步真正要回答的问题
翻成人话：
不是问“pairs 主题有没有研究价值”，而是问——`shared risk overlay / position-sizing gate` 这一刀，是否已经独立到值得从旧 `Rank 4` park 残余里剥离出来，作为一个新的前排对象继续推进。

## 最小审计结论
答案是否定的。

### 1. 原 Rank 4 的失败主语没有变
`Rank 4` 作为 direct pairs / stat-arb alpha 的最小 clean replication 已经明确失败：三组主 pair 在 frozen-beta z-score first pass 上一起为负。
这意味着后续任何 salvage，如果还想挂在 `Rank 4` 名下，就必须证明自己不是“原策略失败后的备注层”。

### 2. 现在留下来的只是角色降级，不是独立 pocket
`2026-03-22` 与 `2026-03-24` 两次 park reframe 都在收敛到同一个意思：
- `spread z-score` 还有残余信息；
- 但它更像 shared risk overlay / position-sizing gate；
- 它不再诚实地支撑“直接 pairs entry alpha”。

这类读法本质上是把原始 alpha 降级为二阶治理层，而不是长出一个新的 raw-alpha pocket。

### 3. 新增证据反而继续把它吸收到更大的 pairs full-stack family
两条新增 pairs 证据都不是在证明“Rank 4 这一刀单独成立”：
- `2026-03-24_0153` 强调的是 `threshold × pair basket × cost` 的治理框架；
- `2026-03-24_1424` 强调的是 `cointegration spread raw alpha + dynamic sizing` 的完整骨架。

它们共同支持的是：如果 pairs 主题要重开，更像新的 full-stack family intake；
而不是“旧 Rank 4 再拆出一个 shared sizing gate，就能独立排进前排”。

### 4. honesty / execution realism 也不支持升格
如果一个候选的主要价值来自“给已有 pairs 主题做风险预算 / 仓位调节”，那它天然依赖宿主策略上下文：
- 没有独立 entry 主语；
- 没有独立 after-cost 兑现路径；
- 也没有证明相对 generic pairs risk / volatility sizing / spread governance family 存在单轴不可替代增量。

所以它不是一个可独立 queue-facing 的 fresh intake pocket，而更像旧 pairs family 的辅助说明。

## First verdict
- verdict: `background / P0`
- reason: `Rank 4` 的 `shared risk overlay / position-sizing gate` 仍只是旧 pairs 失败后保留下来的 overlay 级残余解释；新增证据继续把价值指向更大的 threshold-governed / dynamically-sized pairs full-stack family，而没有证明这条 overlay 已成长为独立 pocket。

## 会改变系统认知的一句话
`Rank 4` 的 `BTC-ETH spread z-score direct pairs entry -> shared risk overlay / position-sizing gate` 仍只是旧 pairs/stat-arb park 后的辅助治理层，不构成一个可独立进入前排的 fresh intake pocket，因此 first verdict 收口为 `background / P0`。

## 写回边界
- 允许写回：本轮日志、`BOT2_BOT3_STATE.md` 中与当前 fresh intake 小点直接相关的字段
- 不写：policy / brief / cron prompt / 其他未执行小点
