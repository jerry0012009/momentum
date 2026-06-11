# Rank 209 / US close -> crypto synthetic open spillover intake keep_P1

- Time: 2026-03-28 01:41 UTC
- Target: `research/quant_digests/2026-03-28_0057_us-close-crypto-synthetic-open-spillover-alpha.md`
- Action type: fresh intake
- Verdict: `keep_P1`
- Assigned Rank: `209`

## Why this survives intake
1. **Base alpha is concrete, not narrative.** The object is a clean event-driven raw alpha: `US cash close last-15m/30m shock -> crypto synthetic next-open catch-up`. That is directly translatable into entry / exit / sizing / cost tests rather than a vague macro filter.
2. **It is orthogonal enough to the current front chain.** The important object here is not generic US-overlap follow-through, but a **gap-separated continuation** after an external session boundary. That gives it a different clock and failure mode from existing same-session overlap logic.
3. **The first test can be run cheaply and honestly.** Public data is enough for a first pass on `QQQ/NVDA -> BTC/ETH`, with explicit boundary sweep (`20:00/00:00/08:00/13:30 UTC`) and friction ladder. So it is cheap enough to preserve for one decisive survivor follow-up.

## Why it does not jump straight to P2
- The current evidence is still transferred-from-equities thesis evidence, not crypto-native verification.
- The key uncertainty is whether the edge exists specifically at a **crypto synthetic open** after the waiting gap, or whether it collapses into already-known overlap beta once tested on BTC/ETH.
- Therefore the honest intake verdict is to keep it alive as one `P1` survivor, not to over-promote it before the first transfer test.

## Required survivor question
Run exactly one cheap decisive follow-up around:
- leader: `QQQ` / `NVDA` US close last `15m/30m`
- follower: `BTCUSDT` / `ETHUSDT`
- boundaries: at minimum compare `20:00 UTC` immediate release vs `00:00 UTC` synthetic-open catch-up
- holding windows: first `15m/30m/60m`
- friction: at least `4/6/8/10 bps` round-trip

The survivor question is simple: **does a cost-aware, gap-separated continuation pocket survive on crypto at a synthetic open, or is this just delayed repackaging of existing US-overlap momentum?**

## Result sentence
`Rank 209 / US close -> crypto synthetic open spillover` intake passed as `keep_P1`: it contributes a distinct gap-separated external-session continuation hypothesis worth one cheap survivor test, but not enough crypto-native evidence yet for `P2`.
