# Rank 345 — GHE pair selection × spread mean reversion fresh intake first verdict：keep_P1

- Time: 2026-04-06 02:24 UTC
- Target: `research/quant_digests/2026-04-06_0115_ghe-pair-selection-spread-meanreversion-alpha.md`
- Verdict: `keep_P1`
- Assigned Rank: `345`
- Layer change: `fresh intake -> Surviving candidate slot`

## Why this changes system belief
`GHE/Hurst` 在这条线里不是事后 regime veto，而是前移到 `pair formation / pair ranking / admission` 的 raw-alpha shell：先筛出更像会回归的 spread，再做 beta-hedged z-score mean reversion。和普通 `cointegration / correlation + threshold` pairs baseline 相比，新增信息不只是包装叙事，而是 pairbook construction 这一层的 distinct source。

## Decision basis
1. 主论文给的是明确的 pair-selection superiority claim：相对 `Distance / Correlation / Cointegration` baseline，`GHE` 选对方法在 crypto pairs 上更优，而且摘要明确写到有 out-of-sample 支撑。
2. digest 已把 companion papers 压清：`optimal threshold` 与 `optimal rebalancing frequency` 是后续治理层，不是对 raw alpha 本体的替代。这反而说明主线骨架清楚：`GHE ranking -> spread MR`。
3. 本地 portability probe 给出了 desk 可迁移的最小 pocket：`5m` 的若干大币 pair 在 low-H bucket 下明显比 persistent bucket 更快、更高命中地回到中线；这足以支持先进入 `P1` 做一次 survivor follow-up。
4. 但同一份 digest 也明确写出 `15m` 结果 mixed，因此现在还不能直接升 `P2`；当前更诚实的写法是：保留为 `5m-first / 15m-admission-feature` 的 surviving candidate，而不是夸大成已完成跨周期迁移。

## First-verdict statement
`Rank 345`：`GHE/Hurst pair selection × spread mean reversion` 已通过 fresh intake first verdict；对象的 distinctness 落在 `先用 low-H / roughness 构建 top-K pairbook，再做 beta-hedged z-score MR` 这一前移的 pair formation shell，而不是普通 pairs baseline 的 ranking embellishment。现有证据足够支持进入 `keep_P1`，但 desk 可迁移主体目前更明确落在 `5m-first`，`15m` 仍只适合作为 admission/veto feature，故本轮不直升 `P2`。

## Next honest follow-up boundary
唯一值得保留的 survivor follow-up 应围绕：`在 high-liquidity perp / after-cost / walk-forward 口径下，GHE-ranked top-K pairbook 是否相对 plain corr/cointegration baseline 仍保留独立净收益与更好的 pairbook quality`。若这一步不能成立，就应按 policy 收口回 background，而不是继续把 Hurst 当通用 embellishment。
