# Strategy Review — 2026-04-02 19:32 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short`）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-02_1823_rank295_public_inflow_proxy_blocked.md`
  - `research/optimization_loop/2026-04-02_1850_percentile_pairs_blocked_by_rank295_survivor.md`
  - `research/optimization_loop/2026-04-02_1929_feecoverage_crossvenue_funding_carry_blocked_by_rank295_survivor_lock.md`
  - `research/optimization_loop/2026-04-02_1744_rank295_eth_exchange_inflow_shock_keep_p1.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-02_1813_strategy-review.md`

## 只回答 4 个问题

1) `Paper launch queue` 是否非空？
- 否。
- 当前 `Paper launch queue.current_target = none`。
- 已接线运行对象仍为 `Rank 200 / 201 / 213 / 229`，没有新的 queue 头等待 handoff / wiring。

2) 本轮 `fresh intake` 是什么？
- 截至本轮 review 开始时，运行态最近一条 fresh intake 是 `research/quant_digests/2026-04-02_1707_eth-exchange-inflow-event-short-alpha.md`，即 `Rank 295 / ETH exchange inflow shock × 1~6h bearish drift`。
- 但这条对象的唯一 survivor follow-up 已经实际执行并消耗掉，最新 desk 认知是：它没有升到 `P2`，因此不再继续占据当前轮的 front-slot。
- 在本轮写回后，前排已切回新的 fresh intake 序列，队头改为 `research/quant_digests/2026-04-02_1929_cidr-intraday-curve-timing-alpha.md`。

3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得，而且已经实际用掉了那唯一一次 follow-up。
- 这次 follow-up 没有把对象升到 `P2`：不是因为新增价格证据直接把它证伪，而是因为当前 runtime 缺少可直接复核的公开 `ETH exchange inflow` 事件流 / 标签资产，导致无法诚实完成决定性的 clean-room 事件研究。
- 按 policy，`Surviving candidate` 只有 1 次 follow-up；这次机会既然已经消耗、且结果仍未升级到 `P2`，对象就必须退出 survivor 槽并回 `background/P0`，不能继续卡住前排。

4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`（`current_target = none`）。
- 最近一次 `Active P2` 出口仍是 `Rank 285` 的 `one-time P2->P1 re-scope`；本轮没有需要 bot2 执行 `P2 -> P3 / P1 / P0` 裁决的 active 对象。

## Rank 完整性检查
- `Paper launch queue` 前排对象无新增 queue head。
- 本轮 survivor 收口对象 `Rank 295` 已有正式 rank。
- 当前前排不存在无 rank 的 `Surviving candidate / Active P2 / Paper launch queue` 对象。
- 因此本轮无需补新的整数 `Rank`。

## P2 -> P3 兜底裁判检查
- 当前没有 `Active P2`。
- 因此不存在“desk review 已清楚表明足够进入 paper trade，但 bot3 尚未升级”的对象。
- 本轮不触发强制写入 `P3 / Paper launch queue`。

## 本轮状态重写
### 1) 收口 `Rank 295`
- `Rank 295` 的唯一 survivor follow-up 已经实际消耗。
- follow-up 的实际结论来自：`research/optimization_loop/2026-04-02_1823_rank295_public_inflow_proxy_blocked.md`
- 该结论不是 `promote_P2`，而是：当前 runtime 没有可直接复核的公开 `ETH exchange inflow` 事件流 / 标签资产，因此 admission 所需的决定性 clean-room 证据仍不可得。
- 按 policy，survivor 预算用尽且仍未升 `P2` 后，必须退出前排并回 `background/P0`。

### 2) 前排重置为新一轮 fresh intake
由于当前不存在：
- `Paper launch queue` queue head
- `Active P2`
- 合法仍存续的 `Surviving candidate`

所以本轮 `cycle_plan` 必须切回 fresh intake，且直接指定具体对象。按最近新 alpha 报告优先级，新的当前轮顺序写为：
1. `research/quant_digests/2026-04-02_1929_cidr-intraday-curve-timing-alpha.md`
2. `research/quant_digests/2026-04-02_1845_liquidity-provision-shortterm-reversal-cost-cliff.md`
3. `research/quant_digests/2026-04-02_1804_percentile-entry-cointegration-pairs-3m5m15m.md`
4. `research/quant_digests/2026-04-02_1734_feecoverage-gated-crossvenue-funding-carry-alpha.md`

全部按 policy 重写为：
- `target / action / success_criterion / result / status`
- 且新生成项统一 `result = none`
- 且新生成项统一 `status = pending`

## State 写回说明
本轮只更新：
- `docs/BOT2_BOT3_STATE.md`

未改动：
- policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排
- 未依据日志反向改 policy

## 本轮改变系统认知的一句话
`Rank 295` 的 survivor 机会已经实际用掉但未升 `P2`，所以它不能继续卡住前排；按 policy 本轮必须把它收口回 `background/P0`，并把当前执行面切回新的 fresh intake 队列。