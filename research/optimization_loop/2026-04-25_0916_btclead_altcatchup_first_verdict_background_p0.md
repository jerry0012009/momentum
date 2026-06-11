# Rankless fresh intake — BTC downside shock × alt catch-up continuation first verdict

- Time: 2026-04-25 09:16 UTC
- Target: `research/quant_digests/2026-04-24_2152_btclead-altcatchup-intraday-tsmom-alpha.md`
- Action: fresh intake first verdict with one minimal decisive blocker check
- Verdict: `background/P0`

## What I checked
I used the intake's existing public-data artifacts and added one minimal honesty/cost check on the only visible pocket:

- Summary artifact: `reports/artifacts/quant_digests/2026-04-24_btclead_altfollow_summary.csv`
- Asset-tail artifact: `reports/artifacts/quant_digests/2026-04-24_btclead_altfollow_asset_tail.csv`
- Pocket under review: `BTC neg q90/q95 -> next 15m alt-basket same-sign continuation`
- Minimal blocker: whether the tail pocket still looks like a tradable after-cost lead-lag alpha under a unified friction ladder, rather than a thin metadata-style clue.

## Key evidence
From the artifact:

- `btc_neg_q90`: `n=65`, gross `+2.757 bps/trade`
- `btc_neg_q95`: `n=31`, gross `+5.709 bps/trade`

Unified friction ladder:

- `btc_neg_q90` net after `2/4/6/8 bps` = `+0.757 / -1.243 / -3.243 / -5.243`
- `btc_neg_q95` net after `2/4/6/8 bps` = `+3.709 / +1.709 / -0.291 / -2.291`

Follower split is not purely one-symbol luck, but the edge is still concentrated in the thinnest tail:

- `btc_neg_q95 -> DOGE`: `+9.42 bps`
- `btc_neg_q95 -> ADA`: `+9.11 bps`
- `btc_neg_q95 -> SOL`: `+7.86 bps`
- `btc_neg_q95 -> XRP`: `+4.34 bps`
- `btc_neg_q95 -> LINK`: `+4.00 bps`
- `btc_neg_q95 -> BNB`: `-0.47 bps`

## Decision
This intake does **not** clear the first-verdict bar for `keep_P1`.

Reason:
1. The normal `BTC -> alt` lead-lag is too thin.
2. The only visible positive pocket is the extreme downside tail.
3. That pocket is **not clearly robust under a unified realistic cost range**: q90 already turns negative by `4 bps`, and q95 is only `+1.709 bps` at `4 bps` before any additional execution degradation.
4. The current evidence is still basically one parent/child window (`15m -> next 15m`) with only `31` q95 events, so it is not yet strong enough to say there is a durable, independently tradable after-cost tail-pocket alpha.

## Runtime-changing conclusion
`BTC downside shock × alt catch-up continuation` should be honestly closed as `background/P0`: current public-data evidence only supports a thin extreme-tail clue, not a clearly tradable after-cost lead-lag alpha for short-cycle crypto perp execution.
