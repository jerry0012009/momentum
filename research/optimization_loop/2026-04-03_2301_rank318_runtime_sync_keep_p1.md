# Rank 318 — runtime sync: keep_P1 truth written back to state

- Time: 2026-04-03 23:01 UTC
- Target: `research/quant_digests/2026-04-03_1647_polymarket-finalwindow-lagarb-alpha.md`
- Action: sync completed fresh-intake verdict back into `BOT2_BOT3_STATE.md`
- Verdict: `done`

## Why this log exists
本轮发现 runtime state 仍把 `Polymarket final-window lag arb` 写成 fresh-intake pending，但对应 first-verdict 研究结论其实已经在 `research/optimization_loop/2026-04-03_2230_rank318_polymarket_finalwindow_lagarb_first_verdict_keep_p1.md` 中形成并分配了正式 `Rank 318`。

按 policy，bot3 本轮不得假装该对象仍未判定；因此这一步的合法动作不是重做 intake，而是把已经成立的前排真相补写回 runtime。

## Runtime truth written back
1. `Rank 318` 已被确认是正式 rank，不能重复占用 fresh-intake 无 rank 状态。
2. 该对象 first verdict 已是 `keep_P1`，因此必须进入 `Surviving candidate slot`，并保留唯一一次 one-shot follow-up 预算。
3. `Fresh intake slot` 头部因此顺延到下一条具体对象：`research/quant_digests/2026-04-03_1425_hyperliquid-public-trigger-cluster-alpha.md`。
4. `cycle_plan` 第 1 小点已补写结果并标记为 `done`，其余顺位不重排。

## Result sentence
`Rank 318`：`Binance 领涨/领跌 -> Polymarket final-window binary odds lag repair` 已证明是可独立复现的 hard-expiry raw alpha，正式首判 `keep_P1` 并进入 `Surviving candidate slot`；runtime 不再把它错误保留在 fresh-intake pending。

## Files touched
- `docs/BOT2_BOT3_STATE.md`
- `research/optimization_loop/2026-04-03_2301_rank318_runtime_sync_keep_p1.md`

## Source of truth referenced
- `research/optimization_loop/2026-04-03_2230_rank318_polymarket_finalwindow_lagarb_first_verdict_keep_p1.md`
