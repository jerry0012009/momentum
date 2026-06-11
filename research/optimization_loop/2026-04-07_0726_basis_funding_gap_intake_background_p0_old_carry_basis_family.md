# 2026-04-07 07:26 UTC — basis-funding gap fresh intake first verdict：background / P0

## 本轮执行对象
- target: `research/quant_digests/2026-04-07_0551_basis-funding-gap-convergence-alpha.md`
- action: fresh intake first verdict

## 结论
`annualized basis - implied funding` 这条线本轮不进 `P1`。结论是 **`background / P0`**。

一句话原因：**它的收益主语仍是熟悉的 `delivery/perp carry gap mean reversion`，只是把季度年化 basis 与 funding 年化放进同一个 spread 里重写；repo 没有证明这层重写解决了旧 carry / basis family 的决定性 blocker。**

## 为什么不升 `keep_P1`
1. **alpha 主语不独立。**
   - 核心定义就是 `gap_t = basis_ann_t - funding_ann_t`。
   - 其中 `basis_ann` 仍是交割合约 vs 现货/近现货的 carry 定价，`funding_ann` 只是 perp carry 的慢变量锚。
   - 所以本质上还是：**当 delivery carry 相对 perp implied carry 偏贵/偏便宜时，赌 curve/carry 回归。** 这仍属于旧 `basis / funding carry / calendar basis convergence` 家族，不是新 raw alpha 主语。

2. **新增成分主要是 admission / packaging，不是新 edge。**
   - repo 里更有价值的 `half-life / Hurst / z-score`，本质上是判断什么时候值得做，而不是创造了新的收益来源。
   - 这更像旧 carry 壳上的 `admission layer`，不是能单独把对象抬进前排的新 alpha 本体。

3. **证据强度不够支撑“旧家族里值得单列 survivor”。**
   - 摘要里主回测样本只有 `2024-06-28 ~ 2024-12-01`，仅 `7` 笔 round-trip。
   - 这足以说明“有过看起来不错的结构性 episode”，但不足以证明它相对现有 funding/basis 候选解决了稳定性与执行诚实性的核心问题。

4. **执行改写仍停留在 desk packaging。**
   - digest 自己也承认真正 desk-fit 的实现要改成 `perp-vs-quarterly / perp-vs-synthetic-spot`。
   - 这说明当前最像“可复用”的部分是一个研究重述框架，而不是已经压清的新 pocket。

## 改变系统认知的话
**这条 `basis-funding gap` intake 没有带来独立于既有 funding/basis 家族的新 alpha 主语；`half-life / Hurst` 更像 admission overlay，因此本轮直接记为 `background / P0`，不分配新 Rank。**

## Runtime 写回要点
- `Fresh intake slot` 更新为本对象与上述 verdict
- `Background pool.latest_parked` 更新为该对象
- `cycle_plan[1]` 写回 `done`

## 后续影响
- 该对象不进入 survivor，不占用前排槽位
- 下一轮应继续执行 `cycle_plan` 中下一条 pending 小点
