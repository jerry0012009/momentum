# 2026-03-25 09:57 UTC — Rank 162 survivor assignment

## Context
- Current fresh intake: `Rank 162 / Kalman β-gap cross-sectional raw alpha`
- Fresh verdict from prior step: `keep_P1`
- Policy requirement: when fresh intake gets `keep_P1`, it becomes the only legal survivor and bot3 must define a single decisive follow-up blocker instead of leaving open-ended research.

## Decision
`Rank 162` is now the sole legal `Surviving candidate`.

Its **only** survivor follow-up blocker is:

> Whether restricting trades to **extreme β-gap events only** can lift **post-cost average bps per trigger** back above zero on Binance perp execution, i.e. whether the signal has a tradable event-driven pocket after turnover/costs.

## Why this blocker
The intake already established two things:
1. cross-sectional ordering signal still exists;
2. naive `5m/15m` raw rotation is eaten by turnover and cost.

So the cheapest honest next check is not another broad stability pass, but one decisive re-spec test: tighten to extreme-event triggers and read the post-cost `avg bps/trigger` outcome. If that pocket does not survive, the candidate should drop to background rather than continue as open research.

## Runtime effect
- `Fresh intake slot` remains `Rank 162 / keep_P1_rank_assigned_waiting_survivor_decision` as source intake record.
- `Surviving candidate slot` is now occupied by `Rank 162`.
- `followup_budget_remaining = 1`.
- Next legal execution step is the single decisive survivor follow-up on the extreme-trigger blocker above.

## One-line result
`Rank 162` 已被写成唯一合法 survivor；它唯一值得做的收口检查是“极端 β-gap 事件触发后，post-cost avg bps/trigger 能否重新转正”。
