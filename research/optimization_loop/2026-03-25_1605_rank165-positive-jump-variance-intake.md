# Rank 165 intake — positive-jump variance lottery fade

- Time: 2026-03-25 16:05 UTC
- Target: Fresh intake slot
- Source digest: `research/quant_digests/2026-03-25_1600_xs-positive-jump-variance-lottery-fade.md`
- Assigned rank: `Rank 165`
- Verdict: `keep_P1`
- Scope: `cross-sectional positive-jump variance lottery fade`

## Why this intake survives the first cut
1. **Base alpha is clean and independent.** This is not a filter pretending to be alpha; the paper’s core claim is directly tradable as `long low positive-jump variance / short high positive-jump variance`.
2. **The evidence is stronger than a loose narrative.** The digest already points to a top-journal paper with explicit portfolio results (`Low-High` positive-jump variance spread, Fama-MacBeth slope, regime split), so the first-cut honesty bar is passed.
3. **It expands the raw-alpha family instead of duplicating an existing line.** The mechanism is “lottery-like upside jump crowding fades later,” which is not the same as the current loser-reversal or beta-gap families.

## Why it does not jump straight to P2
- The paper evidence is strong, but **desk transfer is still missing**: we do not yet know whether a Binance perp tradable universe, realistic long/short basket construction, and post-cost holding windows can keep any net edge after friction.
- The most likely decisive blocker is **tradeability concentration**: the effect may live mainly in smaller, uglier short-leg names and weaken sharply in large-cap perp subsets.

## Result sentence
`Rank 165 / positive-jump variance lottery fade` passes first-cut intake honesty as a distinct cross-sectional raw alpha and stays `keep_P1`, but it is not yet `P2` because the key unresolved blocker is whether the edge survives a large-cap-perp, post-cost transfer instead of living only in small-cap lottery tails.
