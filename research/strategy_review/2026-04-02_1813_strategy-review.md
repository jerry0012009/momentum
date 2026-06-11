# Strategy Review — 2026-04-02 18:13 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short`）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-02_1810_rank295_survivor_lock_blocks_topn_reversal_fresh_intake.md`
  - `research/optimization_loop/2026-04-02_1744_rank295_eth_exchange_inflow_shock_keep_p1.md`
  - `research/optimization_loop/2026-04-02_1714_rank294_survivor_followup_background_p0_time_slice_instability.md`
  - `research/optimization_loop/2026-04-02_0159_rank285_p2_exit_rescope_to_p1.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-02_1720_strategy-review.md`

## 只回答 4 个问题

1) `Paper launch queue` 是否非空？
- 否。
- 当前 `Paper launch queue.current_target = none`。
- 已接线运行对象仍为 `Rank 200 / 201 / 213 / 229`，没有新的 queue 头等待 handoff/wiring。

2) 本轮 `fresh intake` 是什么？
- 运行态当前的 fresh intake 仍是：`research/quant_digests/2026-04-02_1707_eth-exchange-inflow-event-short-alpha.md`。
- 它已经完成 first verdict，并在 runtime 中转成 `Surviving candidate slot = Rank 295 / ETH exchange inflow shock × 1~6h bearish drift`。
- 因此本轮真正排在最前的不是新的 intake，而是 `Rank 295` 的 survivor 唯一 follow-up。

3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得，而且现在就是唯一合法前排动作。
- `Rank 295` 的 first verdict 已是 `keep_P1`，并且最新 optimization 日志已经明确：因为 survivor lock 仍未收口，`top-N loser reversal × pump-veto × confidence sizing` 这种新的 fresh intake 不能抢到它前面。

4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`（`current_target = none`）。
- 最近一次 P2 出口是 `Rank 285` 的 `one-time P2->P1 re-scope`；本轮没有需要 bot2 执行 `P2 -> P3/P1/P0` 裁决的 active 对象。

## Rank 完整性检查
- `Paper launch queue / Surviving candidate / Active P2` 当前前排对象均已有正式 `Rank`。
- 本轮无需补新的整数 `Rank`。

## P2 -> P3 兜底裁判检查
- 当前没有 `Active P2`，因此不存在“desk review 已足够清楚、但 bot3 尚未升级”的对象。
- 本轮不触发强制写入 `P3 / Paper launch queue`。

## 本轮排班改写结论
按 policy 默认顺序重写 `cycle_plan`：
1. 先收口 `Rank 295` 的 survivor 唯一 follow-up；
2. 只有在该前排动作已诚实排入后，才用剩余预算补具体 fresh intake；
3. 新 intake 选最近具体对象，不把 background pool 旧候选拉回前排。

新的 `cycle_plan` 为：
1. `Rank 295 / ETH exchange inflow shock × 1~6h bearish drift`
2. `research/quant_digests/2026-04-02_1804_percentile-entry-cointegration-pairs-3m5m15m.md`
3. `research/quant_digests/2026-04-02_1734_feecoverage-gated-crossvenue-funding-carry-alpha.md`
4. `research/quant_digests/2026-04-02_1625_topn-reversal-pumpveto-confidence-alpha.md`

每项均按要求写成：`target / action / success_criterion / result / status`，且新生成项统一 `result = none`、`status = pending`。

## State 写回说明
本轮只更新：
- `docs/BOT2_BOT3_STATE.md`

未改动：
- policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排
- 未依据日志反向改 policy
