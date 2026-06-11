# Rank 338 — extreme funding tail carry — fresh intake first verdict = keep_P1

- Time: 2026-04-05 15:07 UTC
- Target: `research/quant_digests/2026-04-04_2203_extreme-funding-tail-carry-alpha.md`
- Slot: `Fresh intake -> Surviving candidate`
- Verdict: `keep_P1`
- Assigned Rank: `338`

## What changed
`extreme funding tail carry` should be kept as a distinct `P1` object rather than dropped as a generic funding/carry rename. Its distinct edge is not "positive funding exists" but the narrower shell: `extreme-positive-funding-only × funding-boundary entry × fee-churn veto`, with an explicit net-cost framing and a concrete BTC/ETH perp transfer path.

## Why this passes first verdict
1. **Tail-event definition is concrete enough.**
   The digest does not stop at "APR > 5%". It explicitly shows that default `5%/3%` and even `10%/5%` threshold carry are fee-dominated, while the edge only begins to survive in the extreme positive funding tail (`15%/8%` style sparse windows).
2. **Boundary-time execution shell is concrete.**
   The proposed branch is not continuous carry; it is event-driven carry centered on the funding boundary, with explicit suggestion to enter only in the pre-settlement window and hold through one funding event unless basis/APR degrades.
3. **Fee-churn veto is the actual distinct insight.**
   The object is not just a funding-threshold rename because it identifies the main failure mode as turnover-induced fee drag and proposes a specific execution veto: avoid entry while spot-perp basis is still expanding into the funding boundary.
4. **Transfer path is already narrow and testable.**
   The next honest test is already scoped to `BTC/ETH`, high-liquidity perp pairs, comparing repo baseline vs `extreme-only` vs `boundary-timed extreme-only`, with `funding/fees` as the first report metric.

## Why this is not yet P2
It still lacks the minimum clean-room admission artifact proving that the `boundary-time + fee-churn veto` shell, rather than just a higher static threshold, is what preserves net edge on a liquid-major executable path. So it is not ready for `P2` yet.

## Next legal follow-up
Single survivor follow-up should compress this into one clean-room `BTC/ETH` event study:
- compare `continuous threshold carry` vs `extreme-only` vs `boundary-timed extreme-only`
- keep the report centered on `funding income / fees / event count / net per funding window`
- test whether the `basis-expansion veto` is the single decisive blocker-remover or not

## Result sentence for runtime
`Rank 338`：`extreme-positive-funding-only × funding-boundary entry / fee-churn veto` 已构成 distinct 的事件型 carry raw alpha，fresh intake first verdict 通过并进入 `P1 / Surviving candidate`。
