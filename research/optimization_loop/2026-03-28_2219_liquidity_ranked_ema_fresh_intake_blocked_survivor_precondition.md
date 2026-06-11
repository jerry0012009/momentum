# bot3 optimization loop — conditional fresh intake blocked by active survivor precondition

- Time: 2026-03-28 22:19 UTC
- Executor: bot3
- Policy refs:
  - `docs/BOT2_BOT3_POLICY.md`
  - `docs/BOT2_BOT3_STATE.md`
- Cycle item executed: `cycle_plan` item 2 only
- Target: `research/quant_digests/2026-03-28_0704_liquidity-ranked-ema-trend-fullstack.md`
- Outcome: `blocked`

## Why this item was blocked
`cycle_plan` item 2 is explicitly conditional: it is only legal when item 1 has already been honestly queued **and** there is still no actionable `P3 / Active P2 / Surviving candidate` object at the front of the chain.

Current runtime truth still has:
- `Surviving candidate slot = Rank 229 / abnormal-day continuation to close`
- `followup_budget_remaining = 1`
- latest runtime instruction: only one cheap decisive `ETH-led` re-scope / session-robustness follow-up is still allowed

Under policy:
- existing front-chain closure always outranks a new fresh intake;
- a survivor keeps front-of-queue lock until its one allowed follow-up is honestly closed;
- bot3 must reject state/cycle drift and fall back to legal actions instead of silently letting a new intake preempt the survivor.

## Result written back to runtime
- `cycle_plan` item 2 marked `blocked`
- result written as: current survivor precondition remains active, so the conditional fresh intake cannot be executed this round

## Notes
I also sanity-checked the repo-digest thesis with a quick public-data proxy (`BTC/ETH/SOL` 1m Binance perp, top-1 quote-volume rotation, EMA(10/22), `-50bps/+80bps/30m/flip`, roundtrip cost proxy `8bps`). The proxy came out clearly negative (`top1 avg ≈ -8.77 bps/trade net`, `n=982`, last 14d), which is directionally consistent with the digest reading that this object looks more like an engineering shell than a proven standalone raw alpha. But because the cycle item's own prerequisite is currently false, no formal intake verdict or rank assignment was made in this round.
