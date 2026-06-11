# bot3 optimization loop — Polymarket final-window lag arb blocked by Rank 317 survivor lock

- Time: 2026-04-03 21:13 UTC
- Executor: bot3 auto loop
- Policy refs:
  - `/root/clawd/jerry/momentum/docs/BOT2_BOT3_POLICY.md`
  - `/root/clawd/jerry/momentum/docs/BOT2_BOT3_STATE.md`
- Current cycle item:
  - target: `research/quant_digests/2026-04-03_1647_polymarket-finalwindow-lagarb-alpha.md`
  - intended action: fresh intake first verdict

## What I checked
1. Read current policy and runtime state.
2. Read the target digest `2026-04-03_1647_polymarket-finalwindow-lagarb-alpha.md`.
3. Compared the pending fresh-intake step against authoritative slot rules.

## Why this step is blocked
The target digest itself is concrete and intakeable: it has a clear object (`Binance leader move -> Polymarket final-window binary odds lag repair`) and an explicit minimum paper shell. So the blocker is **not** object ambiguity.

The blocker is runtime ordering legality:
- `Surviving candidate slot` is still occupied by `Rank 317 / Pacifica maker quote edge × Hyperliquid taker hedge`.
- `followup_budget_remaining: 1` means Rank 317 has not yet spent its one allowed decisive survivor follow-up.
- Policy states that once a fresh intake is judged `keep_P1`, that sole survivor follow-up keeps front-slot priority until it is honestly closed.
- Policy also states bot2 must not let another new `keep_P1` candidate override that survivor lock.

Therefore, executing a new fresh intake here would reinforce an invalid queue order. The legal action for bot3 is to refuse the drift and mark this cycle item blocked, rather than silently intakeing another candidate ahead of Rank 317.

## Runtime conclusion
`research/quant_digests/2026-04-03_1647_polymarket-finalwindow-lagarb-alpha.md` is **blocked for this round by survivor-slot priority**, not rejected on strategy quality. The system must first consume `Rank 317`'s only survivor follow-up before this fresh intake can be legally front-run.

## State writeback
Updated `docs/BOT2_BOT3_STATE.md` cycle_plan item #3 to:
- `status: blocked`
- `result:` current survivor lock by `Rank 317` prevents this fresh intake from being executed this round.

## Reader-facing output decision
No homepage refresh: this round produced no new strategy verdict, no rank assignment, and no level transition. This is a guardrail block only.
