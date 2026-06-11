# bot3 optimization loop — lowest-price-anchor intake blocked by survivor lock

- Time: 2026-03-27 01:09 UTC
- Target: `research/quant_digests/2026-03-27_0018_lowest-price-anchor-xs-reversal.md`
- Cycle step: `4`
- Verdict: `blocked`

## Why this step was not legally executable
According to `docs/BOT2_BOT3_POLICY.md`, a `Surviving candidate` can only be the immediately previous `fresh intake`, and that survivor keeps front-slot priority until its one cheap decisive follow-up is honestly closed.

In the same cycle, step 3 already converted the prior fresh intake into:
- `Rank 190 / BTC-shock ADA-underreaction 1m beta-hedged catch-up spread`
- verdict: `keep_P1`
- slot: `Surviving candidate`
- `followup_budget_remaining: 1`

That means step 4's own gating clause — `仅在前 3 项已诚实排入且前排链条未再扩张时` — is no longer true, because the front chain *did* expand at step 3 when `Rank 190` entered the survivor slot.

## System-impacting conclusion
`lowest-price-anchor` 这条补位 fresh intake 本轮不能被合法推进到首判；不是它已被判负，而是因为 `Rank 190` 刚占用 survivor front-slot，导致该补位 intake 的前置条件失效，因此本轮必须记为 `blocked` 而不是继续硬做第二个会挤占 survivor 的 `keep_P1` 候选。

## Runtime writeback needed
- only update current cycle item status/result to `blocked`
- do not alter policy / queue head / active survivor identity
- do not assign a new Rank this round, because no legal `keep_P1` verdict was executed
