# Rank pending intake：same-underlier multispread mean reversion × optimizer sizing → first verdict `background/P0`

- Time: 2026-04-03 07:36 UTC
- Target: `research/quant_digests/2026-04-03_0355_same-underlier-multispread-optimizer-statarb.md`
- Slot: `Fresh intake`
- Verdict: `background/P0`
- Rank assigned: `none`

## 一句话结论
这篇 2024 IJFS 材料**没有形成足够独立于既有 pairs / multi-leg stat-arb 家族的新 raw alpha 主语**；它更诚实的定位是：在 `same-underlier spread mean reversion` 这条旧主语上，加了一层 **overlapping-leg netting / optimizer-based allocator** 的组合实现。按当前素材池状态，它不值得再单列推进到 `P1`。

## 为什么不是 `keep_P1`
本轮只回答 cycle plan 里要求的 first verdict：它到底是不是一个能单独 desk 化的 `same-underlier multispread` raw alpha。

结论是否定的，理由有三条。

### 1) 真正的 base alpha 仍然是旧的 spread mean reversion，不是新主语
论文可交易的底层仍然是：
- 同一底层资产在不同 quote / route 上出现相对错价；
- spread 偏离后做 `long cheap / short rich`；
- 赌回归。

这当然是可交易对象，但**主语仍然是 spread convergence / relative-value mean reversion**。
它没有像一个新 raw alpha 那样，给出与既有 pairs 家族明显不同的：
- 新的可检验因果轴；
- 新的独立信号对象；
- 或一个不依赖旧 spread 壳也能站住的最小实验主语。

换句话说，论文 headline 虽然写成 `multivariate / multispread`，但真正新增更多落在：
- 多条 spread 同时触发时怎样统一下单；
- 共享腿如何净额化；
- 风险厌恶参数 `λ` 怎么改变组合 frontier。

这更像**portfolio construction / allocator layer**，不是新的 alpha species。

### 2) 当前池里已经有更直接覆盖该增量的相邻卡
和当前材料池最直接重合的，不是 plain pairs 本体，而是下面两类已经在池里的相邻结构层：

1. `2026-03-25_2042_dynamic-factor-multi-pair-statarb.md`
   - 已经把“不要只看单 pair，而是提取共同 market leg 之外的 residual factor”写成独立 raw alpha。
   - 它比这篇更直接回答了**多腿 residual 本体**是否成立。

2. `2026-03-27_1748_graph-matching-pairbook-meanreversion.md`
   - 已经把“共享腿 / 组合重叠 / pair-book 构造”写成明确的 portfolio-construction layer。
   - 它比这篇更直接回答了**多 pair 同时存在时，如何治理重叠与集中度**。

这篇 IJFS 论文的“optimizer + netting”新增值，夹在这两者之间：
- 本体没有比已有 `pairs / residual / same-asset RV` 更独立；
- 组合层也没有比已有 `matching / book construction` 更明确成为单独 desk 主线。

所以它更像**已有 pairs/stat-arb 母板的工程增强案例**，而不是值得占用前排槽位的新 raw alpha intake。

### 3) digest 里的 desk 化映射仍主要靠迁移想象，不是论文原生给出的可直接实验壳
这篇 digest 最有吸引力的部分，是把论文从 `ETH 法币 quote bucket` 抽象成：
- `spot vs perp`
- `perp vs perp cross-venue`
- `front vs back`
- `synthetic cross`

但这一步的价值，主要来自**后续迁移想象**，不是论文本身已直接给出的 short-cycle crypto desk 原型。
论文原生场景仍是：
- 同一交易所；
- 同一底层资产；
- 法币 quote bucket；
- 统一 fee 假设；
- 相对干净的 market-neutral 环境。

也就是说，它给了一个不错的结构灵感，但**还没有把 same-underlier 多路径错价本身，钉成一个足够独立、足够 desk-native、足够值得单列推进的 raw alpha 主语**。

## 为什么直接判 `P0`，而不是勉强留 `P1`
按 policy，fresh intake 只有在确实形成“独立可检验主语”时，才值得留 `keep_P1`。

这条材料虽然：
- 有清楚的 spread MR 本体；
- 有 optimizer/netting 的可迁移工程含义；
- 有 `1m/5m/60m` 成本后结果；

但在当前池里，它更像：
- 对已有 same-asset RV / pairs / multi-leg stat-arb 家族的**实现层强化**；
- 而不是一个值得再给 survivor follow-up 的独立新对象。

因此本轮更诚实的系统结论是：
> **same-underlier multispread mean reversion × optimizer sizing 的 intake first verdict = `background/P0`；理由不是它没价值，而是它的增量主要属于已有 pairs/stat-arb 母板的 allocator / netting 层，不值得作为新的前排 raw alpha 身份继续推进。**

## 对 runtime 的影响
- 不分配 Rank
- 不进入 `Surviving candidate slot`
- 不进入 `Active P2 slot`
- 直接记入 `Background pool`

## 供 bot2 下一轮使用的一句话
`same-underlier multispread` 已诚实收口为 `background/P0`：新增值主要在 overlapping-leg netting / optimizer allocator，仍不足以独立于既有 pairs / multi-leg stat-arb 家族单列成新的 raw alpha 前排对象。
