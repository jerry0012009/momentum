# BTC 单 venue spot-perp carry × 负 funding 成本阈值 veto / re-entry — fresh intake 首判（background/P0）

- 时间：2026-04-04 08:55 UTC
- 执行者：bot3 auto 13m loop
- Source digest: `research/quant_digests/2026-04-04_0720_btc-spotperp-funding-threshold-carry-alpha.md`
- Object: `BTC 单 venue spot-perp carry × 负 funding 成本阈值 veto / re-entry`
- Verdict: `background/P0`

## 本轮回答的唯一问题
这条对象是否已经足够构成一条值得单列前排推进的 **fresh intake raw alpha**：也就是，不只是“same-venue delta-neutral carry”家族里的又一个更诚实 gate / veto 写法，而是真的给出了一个足够独立、值得占用 survivor 预算的新对象？

本轮结论：**不进入前排，直接记为 `background/P0`。**

## 为什么这次不该再给新的前排名额
1. **收益来源没有换，换的是 same-venue carry 的离场条件。**  
   digest 的主收益来源仍然是最经典的 `long spot + short perp` funding carry；新增值在于把“正 funding 就一直拿着”改成“遇到负 funding 且足以覆盖 round-trip 成本时先退出，恢复后再开回”。这会让对象更诚实，但它改变的是 **admission / veto / re-entry**，不是新的 raw alpha 主体。

2. **它与前排已收过的 same-venue carry 家族重叠过深。**  
   - `Rank 265` 已把对象收口成 `same-venue delta-neutral carry × premium-z admission × current+next funding > close-cost`；
   - `Rank 310` 又把同一家族保留为 `delta-neutral funding carry gate`。  
   当前这条 BTC 单币版本虽然把 gate 写得更 desk-friendly，但本质上仍是 **same-venue delta-neutral carry family 的阈值化离场分支**，不足以再单开一个新的 front-slot 身份。

3. **digest 的真正增量，更像 family-level honesty baseline，而不是独立 survivor。**  
   这篇材料最有价值的地方，是把一个大家都知道的 carry 常识，压成可执行的最小实验壳：`8h funding clock -> negative funding budget veto -> 5m/15m re-entry execution`。这值得保留为后续 carry 家族的 baseline / cost-model 参考；但它更像“把旧 carry 题写对”，而不是“发现一条新的 carry 母板”。

4. **当前对象也没有提供足够强的新独特性去覆盖家族重复。**  
   它没有把 alpha 扩成新的跨资产、跨 venue、或新的价格失衡来源；仍然主要依赖单币 BTC、单 venue、已知 funding carry 经济学。即便 digest 里给了阈值 sweep、再入场与最小成本壳，这些也更像对既有对象的参数化实现，而不是新的系统认知层级。

## 为什么不是 keep_P1
如果给 `keep_P1`，等于默认承认这是一条值得继续占用 survivor 预算的**新候选**。但当前最诚实的系统读法应是：

> `BTC 单 venue spot-perp carry × 负 funding 成本阈值 veto / re-entry` 不是独立于 `Rank 265 / Rank 310` 的新前排 raw alpha；它更像 same-venue delta-neutral carry 家族的一条更清楚、更可执行的退出/重开规则，应并回该家族的 evidence pool。

也就是说，这篇 digest 有用，但用途主要是**修正与加厚 carry 家族的最小实验壳**，不是重新打开一条前排 rank。

## 改变系统认知的一句话
**`BTC 单 venue spot-perp carry × 负 funding 成本阈值 veto / re-entry` 没有形成独立于 `Rank 265 / Rank 310` 的新 front-slot alpha；它更像 same-venue delta-neutral carry 家族的阈值化离场 / re-entry baseline，因此本轮 fresh intake 首判直接记为 `background/P0`。**

## 最终 verdict
- 不分配新 Rank
- 不进入 survivor slot
- `Fresh intake` 首判：`background/P0`
- 后续若再引用这条材料，应作为 same-venue funding carry 家族的 `negative-funding veto / re-entry / cost-budget` 参考，而不是自动 reopen 成新的前排对象
