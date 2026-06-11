# Rank 184 / cross-venue cheapest-spot-richest-perp contango carry — intake keep_P1

- Time: 2026-03-26 13:22 UTC
- Executor: bot3 auto 13m loop
- Source digest: `research/quant_digests/2026-03-26_1122_cross-exchange-cheapest-spot-richest-perp-contango.md`
- Object: `cross-venue cheapest-spot / richest-perp fee-adjusted contango carry`
- Verdict: `keep_P1`
- Assigned rank: `Rank 184`

## What changed this round
这轮不是继续把韩国出金叙事当主线，而是把可 desk 化的 raw alpha 本体定死为：

- 在多交易所里扫描 **最便宜现货 ask** 与 **最贵永续 bid**；
- 用双边 taker fee 先折成真实净价差；
- 只有当 `fee-adjusted net spread` 超过阈值时才做 `long cheapest spot / short richest perp`；
- 核心收益来源是 **跨 venue spot-perp contango 的收敛**，不是单腿方向。

## Why it is not a park
当前 digest 已经给出足够明确的正反两面：

1. **正面**：raw alpha 形态完整，entry/exit/cost/risk 都能直接写成策略，不是空泛“跨境套利故事”。
2. **反面**：在 `BTC/ETH/SOL/XRP/ADA/DOGE` 这些 majors 的 taker/taker 口径下，live quick check 基本全部为负，说明它**不是 majors 上的常开型主策略**。
3. **关键判断**：这不是 fatal flaw，而是一次很清晰的 re-scope 指向——
   - 主研究对象应保留为 **cross-venue cheapest-spot / richest-perp contango carry** 这条 raw alpha；
   - 下一步唯一便宜且会改变结论的 follow-up，应转去回答它是否只在 **altcoin dislocation / 更优 fee tier / maker 化** 这些 pocket 里才成立。

因此本轮最诚实的首判不是 `park`，而是：

> `Rank 184` 保留进入 survivor，但保留的是 **cross-venue cheapest-spot / richest-perp fee-adjusted contango carry** 这条 exact raw alpha，本体不包含“韩国退出腿必须成立”这个附加条件。

## Reader-facing conclusion
`Rank 184 / cross-venue cheapest-spot-richest-perp contango carry` 首判为 `keep_P1`：当前公开证据已足够证明它是一条结构清楚、可完整 desk 化的 raw alpha，但它在 majors 的 taker/taker 口径下并不常开；后续 survivor 唯一值得做的便宜 follow-up，不是再讲韩国叙事，而是验证这条边是否只在 `altcoin dislocation / maker-fee pocket / 更低费率层级` 下才真正可活。
