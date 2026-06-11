# Rankless fresh intake first verdict：OFI-EWMA reservation-price maker skew → background / P0

- Time: 2026-04-07 09:38 UTC
- Target: `research/quant_digests/2026-04-07_0852_ofi-ewma-reservation-maker-alpha.md`
- Slot acted on: `Fresh intake slot`
- Verdict: `background / P0`
- Rank assigned: none

## Why this step was executed
`cycle_plan` 当前排在最前的 pending 小点就是这条 fresh intake first verdict，因此本轮只执行它，不重排其他项。

## What changed system belief
这条对象**不是一个足够独立的新 raw alpha 主语**；它更像把已知的 `LOB imbalance / OFI short-horizon drift / reservation-price skew / inventory-bounded market making` 家族，用 2026 repo 的工程壳重新讲清楚。

## Decisive reasoning
1. **alpha 主语并不新**
   digest 自己承认核心是 `OFI -> next short-horizon drift`，再把该漂移写进 reservation price。这是成熟 microstructure / market-making 文献与实践家族里的经典结构，不是当前项目语义上新的独立 alpha 物种。

2. **可迁移性更偏 execution shell，不是新候选主策略**
   文中最强可取点是“有 flow 偏置时别围着静态 mid 报价”，即 maker quote-skew / child execution 价值；但这更像 execution overlay 或 implementation improvement，而不是值得占用 survivor 槽位的全新前排候选。

3. **公开证据仍停留在 repo/README 自报，不足以支撑前排 first verdict 升级**
   digest 明确写了：证据主要来自 README 自报结果，fill model 仍是研究级近似，不是 queue-level 真回放；秒级 half-life 只有 0.35s，真实网络延迟、排队位置与 adverse selection 足以吃掉纸面 edge。也就是说，它虽然“像回事”，但公开材料并未把一个可独立迁移、after-cost 仍稳的 pocket 压成当前项目需要的可审计前排证据。

4. **更像旧家族的强化版，而不是需要正式 Rank 的新对象**
   该对象的价值主要在于：把旧 maker 家族的诚实成本分解（commission / slippage / adverse selection）写得更直白。这个增量值得保留在 background/reference，但不足以让它从 fresh intake 进入 `keep_P1`。

## Result sentence for runtime
`OFI × EWMA reservation-price maker skew` 更像已知 `LOB imbalance / maker inventory skew` 家族的工程化重述；公开证据仍主要停留在 README 自报与研究级 fill 近似，尚未把可独立迁移的 after-cost maker pocket 压成前排所需的新 alpha 证据，因此 fresh intake first verdict 直接收口为 `background / P0`，不分配新 Rank。

## Reader-facing takeaway
可以把这条线当成以后做 directional/RV 策略时的 **maker execution overlay 参考**，但不该把它当成一个需要进入当前前排流程的新独立候选。
