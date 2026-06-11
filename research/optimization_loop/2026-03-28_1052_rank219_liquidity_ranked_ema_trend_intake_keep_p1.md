# Rank 219 — liquidity-ranked EMA trend × hard exits single-asset shell intake keep_P1

- Time: 2026-03-28 10:52 UTC
- Target: `Rank 219 / liquidity-ranked EMA trend × hard exits single-asset shell`
- Source digest: `research/quant_digests/2026-03-28_0704_liquidity-ranked-ema-trend-fullstack.md`
- Cycle step: fresh intake verdict
- Verdict: `keep_P1`

## What changed
Assigned formal `Rank 219` and completed first verdict for the Hyperliquid `top-1` liquidity rotation × EMA trend × hard exits repo.

## Key conclusion
This object is not yet an admission-ready single-asset momentum strategy. What it honestly leaves behind is a reproducible `raw alpha + risk shell`: the repo already hard-codes asset selection, EMA direction, hard exits, cooldown, and a daily kill switch into one minimal strategy package, which makes it useful as a deskable baseline. But the public evidence is still too narrow and too synthetic to justify `P2`.

## Why it stays P1
1. **Alpha is real enough to keep, but still baseline-grade.**
   The core idea is plain short-horizon single-asset trend following via fast/slow EMA crossover, with a `top-1` liquidity rotation overlay. That is specific enough to test and not just an execution story.
2. **The engineering shell is the main surviving value.**
   Entry vetoes, `0.5%` SL, `0.8%` TP, `30m` timeout, `180s` cooldown, and daily loss kill switch are already present, so this is more than a naked signal.
3. **Public evidence is not yet honest enough for P2 admission.**
   The digest itself says backtests omit realistic slippage/fees/funding modeling, use narrow universe exposure, and currently behave more like an engineering prototype than a demonstrated after-cost edge.
4. **The unresolved decisive question is incremental value, not existence.**
   The only worthwhile survivor follow-up is to test whether `top-1 liquidity rotation + funding/vol veto + hard exits` actually improves after-cost expectancy versus a plain single-asset trend baseline. If not, this object is mostly a reusable shell, not a promotable strategy.

## Runtime writeback
- `Fresh intake slot` -> `Rank 219 / liquidity-ranked EMA trend × hard exits single-asset shell`
- `Surviving candidate slot` -> `Rank 219 / liquidity-ranked EMA trend × hard exits single-asset shell`
- `followup_budget_remaining` -> `1`
- `cycle_plan[4]` -> `done`

## Next allowed action
One and only one survivor follow-up is justified: measure whether the liquidity-ranking / veto / hard-exit stack adds independent after-cost value relative to a plain single-asset EMA trend baseline under realistic cost assumptions.
