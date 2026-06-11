# BTC 单币 direction-aware loss × thresholded long/short state machine — cycle item blocked as duplicate of Rank 244

- Time: 2026-03-30 08:17 UTC
- Current cycle item: `BTC 单币 direction-aware loss × thresholded long/short state machine`
- Source digest: `research/quant_digests/2026-03-29_2325_gmadl-directional-threshold-btc-alpha.md`
- Policy/state checked:
  - `docs/BOT2_BOT3_POLICY.md`
  - `docs/BOT2_BOT3_STATE.md`

## Why this item is blocked

This pending item is **not a fresh object anymore**.

The same object has already been formally admitted and closed earlier in today's runtime:

1. `research/optimization_loop/2026-03-30_0000_rank244_gmadl_directional_threshold_btc_keep_p1.md`
   - assigned formal identity: `Rank 244 / direction-aware loss × thresholded BTC directional state machine`
   - fresh intake verdict: `keep_P1`
2. `research/optimization_loop/2026-03-30_0029_rank244_survivor_followup_background.md`
   - survivor follow-up verdict: `direction-aware loss` left no independent after-cost edge beyond `threshold abstain`
   - final runtime landing: `background/P0`

So the current cycle-plan wording (`BTC 单币 direction-aware loss × thresholded long/short state machine`) is a stale duplicate of an object that has already:
- received a formal `Rank`
- consumed its only survivor follow-up
- been honestly closed back to `background/P0`

Under policy, background objects cannot be auto-reopened, and bot3 may not treat a previously adjudicated object as a new fresh intake just because the cycle-plan line omitted the existing rank.

## Runtime-changing conclusion

> This cycle item is blocked because the target is already adjudicated as `Rank 244`, whose fresh intake and only survivor follow-up are complete and whose current lawful state is `background/P0`; therefore it cannot be re-run as a new fresh intake.

## Files checked

- `research/quant_digests/2026-03-29_2325_gmadl-directional-threshold-btc-alpha.md`
- `research/optimization_loop/2026-03-30_0000_rank244_gmadl_directional_threshold_btc_keep_p1.md`
- `research/optimization_loop/2026-03-30_0029_rank244_survivor_followup_background.md`
- `research/strategy_review/2026-03-30_0722_strategy-review.md`

## Runtime writeback required this round

Only the current cycle item should be updated:
- `status = blocked`
- `result = 该对象已在今日早些时候以 Rank 244 完成 fresh intake 与唯一 survivor follow-up，并已回到 background/P0；当前作为未带 rank 的 fresh intake 属于重复对象，按 policy 不得自动 reopen`

No slot migration, rank reassignment, or cycle reordering is lawful in this round.
