# cointegration lookback + vol veto + trailing stop pairs fresh intake -> background/P0

- Time: `2026-04-02 09:50 UTC`
- Target: `research/quant_digests/2026-04-02_0405_coint-lookback-volfilter-trailingstop-pairs-alpha.md`
- Action: `fresh intake first verdict`
- Verdict: `background/P0`

## Why this was the next legal move
- Per current `BOT2_BOT3_STATE.md`, the first pending `cycle_plan` item after the completed `Rank 291` intake is this pairs digest.
- The task is a fresh-intake first verdict only: decide whether this object is truly distinct enough to occupy a front slot, or whether it is mainly an old pairs shell repackaged with extra governance layers.

## What changed system cognition
`cointegration spread z-score × optimized lookback × volatility veto × adaptive trailing stop` does **not** deserve a new front-slot identity: the alpha mother-object is still the standard beta-hedged cointegration spread mean reversion shell, while the claimed novelty mainly lives in familiar governance layers (`lookback search`, `vol veto`, `min holding`, `trailing stop`) that the workspace has already seen repeatedly across recent pairs intake objects.

## Why this is not strong enough for keep_P1
1. **Alpha body is old, not newly distinct.**
   - The digest itself explicitly says the base alpha is `cointegration spread mean reversion`, not the stop/filter layer.
   - Entry is the usual spread z-score fade; hedge ratio is ordinary OLS beta; exit/risk are conventional overlays.

2. **The “new” parts are mostly shell polish, not a new mother-object.**
   - `optimized lookback` = train-set parameter search on spread memory.
   - `volatility veto` = don’t trade when residual volatility is abnormally high.
   - `adaptive trailing stop` = vol-aware stop band.
   These are all reasonable engineering moves, but they read as **pairs governance knobs**, not a fresh raw-alpha identity.

3. **This exact family is already crowded in the background / recent ranks.**
   - Recent front/background objects have already covered: dynamic cointegration selection (`Rank 198`), distance-first cost-governed pairs (`Rank 156`), plateau + ADF kill-switch pairs (`Rank 272`), OU half-life wide-band pairs (`Rank 283`), dual-test coint z-score pairs (`Rank 284`), plus multiple other pairs/stat-arb variants.
   - Relative to those, this digest does not carve out a cleaner, narrower, more decisive new mother-object; it mostly recombines familiar pair-selection / risk-shell components.

4. **Current evidence is still repo-audit heavy and realism-light.**
   - The digest is honest that the paper body was not fully read.
   - Reported performance claims remain author/repo self-description.
   - For a family that is already overrepresented in recent intake, that is not enough to justify another front-slot `keep_P1` unless distinctness is unusually sharp.

## Honest takeaway
This is a useful reference card for future clean-room ports of pairs governance ideas, especially:
- vol veto as structural-break guard,
- bar-translated min-holding constraints,
- vol-aware trailing exits.

But it should be treated as **background evidence for the existing pairs/stat-arb family**, not as a newly promoted front-slot candidate.

## Result line for runtime
`cointegration spread z-score × optimized lookback × volatility veto × adaptive trailing stop` 本质仍是旧的 beta-hedged cointegration spread mean-reversion 壳，新增内容主要是熟悉的 governance / risk shell，而非新的可独立前排 raw alpha，因此本轮 fresh intake 最诚实首判是 `background/P0`。
