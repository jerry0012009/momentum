# Rank 219 — liquidity-ranked EMA trend × hard exits single-asset shell survivor follow-up close to background

- Time: 2026-03-28 11:34 UTC
- Target: `Rank 219 / liquidity-ranked EMA trend × hard exits single-asset shell`
- Source digest: `research/quant_digests/2026-03-28_0704_liquidity-ranked-ema-trend-fullstack.md`
- Prior record: `research/optimization_loop/2026-03-28_1052_rank219_liquidity_ranked_ema_trend_intake_keep_p1.md`
- Cycle step: survivor follow-up
- Verdict: `keep_P1 后转 background`

## What changed
Completed the one allowed survivor follow-up for `Rank 219` and closed it out of the front slots.

## Decisive conclusion
`Rank 219` does **not** currently show that `top-1 liquidity rotation + funding/vol veto + hard exits` adds independent after-cost expectancy over a plain single-asset EMA trend baseline. What survives is still the execution shell, not a promoted strategy. The honest outcome is `keep_P1 后转 background`.

## Why it does not promote to P2
1. **The "liquidity rotation" layer is too narrow to count as proven incremental alpha.**
   In code, `TOP_N = 1` is chosen only from `BTC-USD / ETH-USD / SOL-USD`, refreshed every `300s`, ranked by depth then spread. That is closer to a narrow execution/universe hygiene rule than a demonstrated return-improving cross-asset selector.
2. **The funding / volatility gates are hard blocks without attribution evidence.**
   `|funding| <= 8 bps`, `vol <= threshold`, and `trend_strength >= threshold` are all direction-agnostic or hard-threshold filters. The public repo shows no ablation proving these gates improve per-trade net expectancy rather than merely reducing trade count.
3. **The after-cost question is still unanswered on the repo's own methodology.**
   The methodology note explicitly says paper trading fills at simulated mid price and does not fully model fees, slippage, funding, latency, partial fills, or queue position. Under that honesty standard, the stated follow-up question is not passed.
4. **The durable value is the reusable shell.**
   The object still packages entry signal, liquidity admission, vetoes, stop loss, take profit, time exit, cooldown, and daily kill switch into one minimal single-asset momentum scaffold. That is useful as a design template, but not enough for `P2`.

## System-level result sentence
`Rank 219 / liquidity-ranked EMA trend × hard exits single-asset shell` 的唯一 survivor follow-up 已诚实收口：现有公开实现并未证明 `top-1 liquidity rotation + funding/vol veto + hard exits` 相对朴素单币 EMA baseline 留下独立 after-cost 净增益；其中 universe 仅 `BTC/ETH/SOL`、`top-1` 选币更像执行约束而非 alpha，且 paper 方法仍用 mid-price 并缺完整费用/滑点/funding 建模，因此本轮按 `keep_P1 后转 background` 退出前排，只保留为可复用的 single-asset momentum execution shell。

## Runtime writeback
- `Surviving candidate slot` -> `none`
- `followup_budget_remaining` -> `0`
- `Background pool.latest_parked` -> `Rank 219 / liquidity-ranked EMA trend × hard exits single-asset shell`
- `cycle_plan[2]` -> `done`

## Next state implication
The front slot is now free for the next legal action; `Rank 219` should not auto-return from background unless explicitly reopened.
