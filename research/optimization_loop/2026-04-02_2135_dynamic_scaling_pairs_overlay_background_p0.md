# Rank intake log — dynamic scaling pairs overlay -> background/P0

- Time: 2026-04-02 21:35 UTC
- Target: `research/quant_digests/2026-04-02_1946_dynamic-scaling-pairs-alpha.md`
- Cycle slot: fresh intake
- Verdict: `background/P0`

## What changed system truth
这条 `dynamic scaling pairs` 不是独立新 raw alpha，而是寄生在既有 `cointegration spread mean reversion` / `pairs threshold governance` 家族上的 `position-sizing overlay`；在未证明 sizing 本身能稳定创造可迁移的 after-cost 增益前，不足以升到 `keep_P1`。

## Why it does not qualify for keep_P1
1. **对象主语不独立。**
   digest 自己承认 base alpha 仍是传统 `spread mean reversion`：先找协整 pair、算 spread/z-score、偏离后做回归；所谓新增部分主要是 `zone-conditioned dynamic scaling`，即让仓位随偏离深浅调整。
2. **它更像治理层，而不是 alpha 本体。**
   真正变化的是 `0.33x / 0.66x / 1.0x` 这类 sizing shell、差额调仓、少做无意义换手；这更接近已有 pairs 家族的 execution / sizing governance upgrade，不是新的可独立 intake 主语。
3. **诚实口径下仍高度 fee-sensitive。**
   digest 引的论文自己给出强烈成本敏感性：`0.02%` fee 与 `0%` fee 的结果差异巨大。这说明 headline 并不能证明 sizing overlay 在 desk 可用成本下单独成立，反而提示 edge 仍可能主要由底层 pair 质量与成本控制决定。
4. **最小 clean-room 路径仍是 ablation，不是现成独立策略。**
   文中最诚实的下一步也是：固定 pair 与 entry/exit，只比较 `fixed size` vs `dynamic size`。这说明它目前最合适的角色是给既有 pairs 壳做组件实验，而不是以独立 fresh-intake 身份占用 survivor 槽位。

## Runtime consequence
- 不分配新 `Rank`。
- 不进入 `Surviving candidate slot`。
- 本轮 fresh intake first verdict 直接记为 `background/P0`。

## Reader-facing one-line summary
这篇材料可留作以后给现有 pairs 壳做 `fixed-size vs dynamic-size` 的 sizing ablation 参考，但现在还不够资格被当成一条独立的新 alpha 线推进。
