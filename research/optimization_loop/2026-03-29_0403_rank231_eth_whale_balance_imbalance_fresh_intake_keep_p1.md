# Rank 231 / ETH whale balance imbalance fresh intake → keep_P1

- Time: 2026-03-29 04:03 UTC
- Target: `research/quant_digests/2026-03-28_1033_eth-whale-balance-imbalance-alpha.md`
- Verdict: `keep_P1`
- Rank assigned: `231`
- Layer move: `fresh intake -> surviving candidate`

## Why this changes system belief

`large-holder accumulation minus small-holder distribution` 已经足够像一条**独立的 ETH 事件型 raw alpha**，不该只当链上叙事；但按当前 desk 口径，它还**没有强到可以直接升 P2**，因为现有主证据仍是日频论文结果，短周期可交易性高度依赖 cohort 构造、地址标签洁净度与实际数据延迟，尚未经过一次诚实的最小分钟化 admission。

## First verdict

结论写成一句话：

> `Rank 231 / ETH whale balance imbalance` 首判完成：保留为 **standalone event alpha first, potentially ETH overlay second** 的 `keep_P1`，不直接升 `P2`。

## Why not P2 yet

1. **原始 alpha 结构真实存在**
   - 论文不是泛泛“whales matters”，而是明确的分层方向差：
     - 大钱包增持 → 后续 ETH 更偏强
     - 小钱包增持 → 后续 ETH 更偏弱
   - 因此真正 alpha 本体是 `Δlarge - Δsmall` 的 holder-imbalance spread，而不是普通 sentiment gate。

2. **但当前证据主频率仍然偏日度**
   - digest 已经诚实写清：论文核心回归是 `t -> t+1 day`。
   - 这足以证明“结构值得保留”，但不足以直接证明它在当前 desk 要的 `1m/3m/5m/15m` 上已经能稳定留下净边。

3. **实盘门槛主要卡在数据工程，不是想法本身**
   - large/small cohort 如何构造、如何剔除交易所/桥/合约地址，会直接决定信号是否被污染。
   - 如果只能拿到慢更新或滞后聚合，这条线就容易在被观测时已被价格消化。

4. **因此最诚实定位是：值得保留，但还没通过 admission**
   - 它不像纯 overlay 文案，因为 base alpha 已经清楚。
   - 但也还不是可直接前排的 `P2`，因为“分钟化后的漂移是否能穿过成本/延迟/标签误差”还没被检验。

## What it is inside the desk

更准确的 desk 归类：

- **Primary identity**: standalone ETH event-driven raw alpha candidate
- **Secondary use**: ETH overlay / participation-aware regime gate
- **Not yet**: admitted intraday production candidate

## Decisive survivor follow-up to spend next

这条 survivor 的唯一 follow-up 应该只问一个问题：

> 用最简代理 cohort / 公共或现成可得链上聚合口径，`Δlarge - Δsmall` 的事件阈值在 `15m/30m/60m/240m` 是否留下方向一致、成本前后仍有意义的 ETH 漂移？

如果答案是否定，说明它更适合长期/overlay 语境，收回 background；如果答案肯定，再考虑升 `P2`。

## Runtime sentence

> `Rank 231 / ETH whale balance imbalance` fresh intake 首判完成：这不是只会讲故事的链上叙事，而是一条值得保留的 ETH 事件型 raw alpha 结构；但在分钟级可交易性、cohort 代理与数据延迟尚未过最小诚实检验前，先按 `keep_P1` 收口并占用唯一 survivor follow-up，不直接升 `P2`。
