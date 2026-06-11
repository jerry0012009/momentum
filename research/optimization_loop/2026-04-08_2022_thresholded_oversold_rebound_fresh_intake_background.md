# Rankless fresh intake verdict — thresholded oversold rebound

- Time: 2026-04-08 20:22 UTC
- Target: `research/quant_digests/2026-04-08_1900_thresholded-oversold-rebound-alpha.md`
- Action: fresh intake first verdict
- Outcome: `background / P0`

## Why this changes runtime truth
`thresholded oversold crash × symmetric rebound exit` does show a real extreme-event bounce pattern, but the current evidence still fails to establish a queue-facing **independent** raw alpha distinct from the existing single-asset oversold / mean-reversion family.

More specifically:
1. The strongest positive evidence is still the familiar statement that **only very extreme selloffs bounce enough after costs**; once the threshold is relaxed, expectancy dies. That is useful admission discipline, but it does not by itself define a new standalone subject.
2. Cross-asset portability is weak in the exact way a generic oversold-bounce shell often is: `5m` looks better on `ETH/SOL`, while `15m` currently looks `BTC-first`; that supports a scoped event shell, not a broadly portable new family.
3. The proposed novelty is mostly **parameter severity** (`hard threshold`, `major-only`, `symmetric rebound exit`) rather than a new mechanism with clear independence from prior oversold-bounce / mean-reversion ideas.
4. No single extra honesty check available inside this cycle would plausibly flip the identity question from “generic oversold event shell” to “new queue-facing raw alpha”. The blocker is not missing one cheap metric; it is missing evidence of unique subject identity.

## Runtime verdict
This intake is informative as a **design lesson** for future event-driven mean reversion (`major-only`, sparse, hard-threshold, long-only first), but it should not take survivor/P2 resources as a new independent candidate.

**Verdict:** park to `background / P0`.

## One-line result for state
`thresholded oversold crash × symmetric rebound exit` 说明“极端 oversold 事件才有 bounce、阈值一放松就失效”，但当前新增信息主要是单资产均值回归 family 的 admission discipline，而不是新的独立 queue-facing raw alpha，因此本轮 fresh intake 收口为 `background / P0`.
