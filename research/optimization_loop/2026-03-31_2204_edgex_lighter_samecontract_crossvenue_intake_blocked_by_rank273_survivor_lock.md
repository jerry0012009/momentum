# bot3 optimization loop — EdgeX/Lighter same-contract cross-venue intake blocked by Rank 273 survivor lock

- Time: 2026-03-31 22:04 UTC
- Executor: bot3
- Cycle step target: `research/quant_digests/2026-03-31_1929_edgex-lighter-samecontract-crossvenue-arb-alpha.md`
- Cycle step type: conditional fresh intake

## What I checked

1. Re-read `docs/BOT2_BOT3_POLICY.md` and `docs/BOT2_BOT3_STATE.md`.
2. Confirmed current front-of-queue runtime truth:
   - `Surviving candidate slot = Rank 273 / whitelist peer-divergence × half-life-gated spread fade`
   - `followup_budget_remaining = 1`
   - latest survivor result explicitly says the **unique** follow-up still has to answer the `96 vs 672` lookback / pair-search / after-cost pocket question before this object can be honestly closed.
3. Re-read the EdgeX/Lighter digest and did a light source sanity check:
   - GitHub repo page is public, but the fetched landing-page text is noisy / partially spammy and does not add decisive new admission evidence.
   - Lighter public `orderBooks` endpoint is reachable and still exposes active markets plus `maker_fee` / `taker_fee` metadata, but this remains only venue metadata, not a completed executable-gap event study.

## Policy application

This cycle item is a **new fresh intake**. Under policy section 6:

- existing front-chain closure always outranks new discovery;
- once a fresh intake is kept as `P1`, its sole survivor follow-up keeps front-slot priority until honestly closed;
- bot3 must refuse a warped path when current state / step ordering would bypass the legal front action.

Because `Rank 273` survivor follow-up is still live and unresolved, this EdgeX/Lighter intake cannot legally consume the current execution turn.

## Result

`same-contract perp cross-venue executable quote-gap reversion` has a readable raw-alpha shell, but in the current runtime it cannot be promoted into active fresh-intake execution yet, because `Rank 273` still holds the sole legal survivor front-slot and has not spent its one follow-up.

## Step verdict

- status: `blocked`
- blocker: `Rank 273 survivor lock still active; legal front action remains the survivor follow-up, so this conditional new intake cannot start this turn.`

## Runtime write-back intent

Only the current cycle item should be updated:
- item 3 status -> `blocked`
- item 3 result -> explain that the EdgeX/Lighter line stays as background-readable candidate only until Rank 273 survivor follow-up is honestly closed

No slot/rank/handoff mutation was legal in this turn, so no other runtime fields should change.
