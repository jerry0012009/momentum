# Rank 79 park reframe review
- Time: 2026-04-01 05:11 UTC
- Source rank: `Rank 79`
- Verdict: `keep_park`
- Original verdict kept: `park`

## Why this rank
- Followed the default band priority: `50~79` first.
- `Rank 79` has not been revisited by `bot6` in the last 7 days.
- It is a clean candidate for one low-frequency review because the theme is specific (`one-regime-per-session`) and already has both source-intake and clean-replication audit trails.

## 1) Why was the original rank parked?
From `research/optimization_loop/2026-03-19_0513_rank79-clean-replication-park.md`, the original `park` came from a very simple problem:
- `one_regime_per_session` did reduce same-session conflict rate and reduced total loss versus baseline;
- but it did so by cutting trade retention down to about `31.64%`;
- and the improvement was not cross-asset clean: only `SOL` stayed positive, while `BTC` and `ETH` were still negative;
- so the result read more like “sample-thinning / budget throttling evidence” than a durable queue-facing edge.

In plain language: the idea did identify that continuation lanes and retest lanes can fight each other inside the same session, but the tested implementation mostly improved things by doing much less.

## 2) Hard park or soft park?
`Rank 79` still reads as **soft park, but leaning harder now**.

Why not full hard park:
- there *is* a real signal fragment here: same-session lane conflict appears costly;
- the original clean replication did improve conflict rate and headline loss.

Why it leans harder than a normal soft park:
- the only credible rescue axis is already very narrow and already consumed;
- the tested implementation did not survive the honesty test on retention;
- the residual value has already been rewritten more cleanly elsewhere.

## 3) Is there any salvage signal?
Yes, but it is **not enough for a new rank-level reopening**.

The salvage signal is:
- session-level lane conflict is likely real;
- continuation-style lanes and retest-style lanes probably should not always be allowed to fire together.

The problem is that this salvage signal has already been harvested into a cleaner, more general formulation:
- `research/quant_digests/2026-03-18_2354_one-regime-per-session-overlay.md` already reframed the theme as a shared allocation overlay;
- `docs/PARK_REFRAME_QUEUE.md` already contains that same residual idea in a more desk-usable form as **`Rank 7b`**.

So the answer is not “no salvage signal”; it is “the salvage signal is already absorbed.”

## 4) The single best cut
If forced to name the one best modification axis, it is still:
- **demote direct mixed-lane session trading into a one-regime-per-session shared allocation overlay**.

But that is exactly why this review stops at `keep_park`:
- this axis is no longer unique to `Rank 79`;
- it has already been captured more honestly by `Rank 7b`;
- drafting a new `Rank 79b` would mostly duplicate an existing queue item rather than add a fresh, narrower hypothesis.

## 5) Is a new derived hypothesis worth drafting?
**No.**

Reason:
- original `Rank 79` verdict should stay parked for audit honesty;
- the only meaningful residual idea has already been converted into an existing derived candidate (`Rank 7b`);
- drafting `Rank 79b` now would create queue clutter, not new decision value.

## 6) Trade on / trade off of the residual idea
This section is recorded only to explain why no new draft is needed.

- Trade on:
  - lower same-session lane conflict;
  - cleaner budget allocation between continuation and retest regimes;
  - more honest framing as an overlay rather than a standalone alpha.
- Trade off:
  - very high risk of “improvement” coming mostly from heavy trade suppression;
  - unstable cross-asset behavior;
  - concept already absorbed by an existing reframe candidate, so reopening it here would be duplicative.

## Final conclusion
- `Rank 79` remains `keep_park`.
- Original `park` verdict stays intact.
- Current classification: **soft park leaning hard**.
- There is a salvage signal, but it has already been more cleanly consumed by existing queue item `Rank 7b`.
- Therefore this round does **not** draft `Rank 79b` and does **not** update `docs/TODO.md`.

## File-change / commit note
- This round only updates the park-reframe log, index, and queue.
- No selective commit was made because the task only required minimal documentation updates and the shared workspace may contain unrelated dirty files.
