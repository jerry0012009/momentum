# Strategy Review — 2026-04-02 20:28 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short --branch`）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-02_1955_rank296_cidr_nextday_curve_timing_keep_p1.md`
  - `research/optimization_loop/2026-04-02_2008_liquidity_provision_shortterm_reversal_blocked_by_rank296_survivor.md`
  - `research/optimization_loop/2026-04-02_2026_blocked_percentile_pairs_fresh_intake_behind_rank296_survivor.md`
  - `research/optimization_loop/2026-04-02_1823_rank295_public_inflow_proxy_blocked.md`
  - `research/optimization_loop/2026-04-02_0159_rank285_p2_exit_rescope_to_p1.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-02_1932_strategy-review.md`

## 只回答 4 个问题

1) `Paper launch queue` 是否非空？
- 否。
- 当前 `Paper launch queue.current_target = none`。
- 已完成接线并处于运行态的仍是 `Rank 200 / 201 / 213 / 229`；本轮没有新的 queue head，也没有需要 bot2 兜底直接推进到 `P3 / Paper launch queue` 的对象。

2) 本轮 `fresh intake` 是什么？
- 当前运行态最近一条已完成首判的 fresh intake 是 `research/quant_digests/2026-04-02_1929_cidr-intraday-curve-timing-alpha.md`。
- 它已被正式写成 `Rank 296 / BTC next-day CIDR curve timing`，fresh intake first verdict = `keep_P1`。
- 因此本轮前排 fresh intake 主语不是旧 `Rank 295`，而是已经切换成 `Rank 296` 这条新对象。

3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得。
- `Rank 296` 的首判并不是泛泛保留，而是已经明确回答了：这条线和旧 `fixed UTC clock` / `same-day path-shape` 家族不同，主语是“在日初前预测次日整条 BTC 日内路径，再在预测低点买入、预测后续高点退出的 gated timing trade”。
- 同时它也还没强到直接升 `P2`：当前公开证据仍主要集中在 `BTC` 单币、recent sample、低频 gated 交易日偏少，且 `8 bps` 成本下已接近失真。
- 所以按 policy，`Rank 296` 正好处在最该使用那唯一一次 survivor follow-up 的位置：要么借这次机会升 `P2`，要么诚实收口回 `background/P0`，不能继续拖。

4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`（`current_target = none`）。
- 最近一次 active P2 出口仍是 `Rank 285` 的 `one-time P2->P1 re-scope`，并未留下需要 bot2 本轮继续裁决的 active admission 对象。
- 因此本轮最近的前排出口，不是 `P2 -> P3`，而是 `Rank 296` 的 `P1 survivor -> P2 / P0` 二选一收口。

## Rank 完整性检查
- 当前前排对象中：
  - `Surviving candidate slot = Rank 296`
  - `Paper launch queue` 无新增 queue head
  - `Active P2 = none`
- 不存在无 rank 的前排对象。
- 因此本轮无需补新的整数 `Rank`。

## P2 -> P3 兜底裁判检查
- 当前没有 `Active P2`。
- 最近 desk evidence 里也没有出现“bot3 没升，但已经明显足够 paper launch”的漏升对象。
- 因此本轮不触发强制写入 `P3 / Paper launch queue`。

## 本轮状态重写
本轮只需要重写 `cycle_plan`，并且必须遵循默认顺序：
`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0 archive`

由于当前：
- `Paper launch queue` 无 queue head
- `Active P2 = none`
- 但 `Surviving candidate = Rank 296` 且 follow-up 预算剩余 `1`

所以本轮合法且最高优先级的动作只能是：
1. 先把 `Rank 296` 排成 survivor 唯一一次 follow-up，直接回答它是 `promote_P2` 还是 `background/P0`
2. 只有在这条前排链条已诚实收口之后，才用剩余预算补新的具体 fresh intake

按最近新 alpha 报告优先级，本轮 fresh intake 后备顺序重写为：
1. `research/quant_digests/2026-04-02_2018_multiquote-bucket-rv-alpha.md`
2. `research/quant_digests/2026-04-02_1946_dynamic-scaling-pairs-alpha.md`
3. `research/quant_digests/2026-04-02_1845_liquidity-provision-shortterm-reversal-cost-cliff.md`

并统一写成：
- 只含 `target / action / success_criterion / result / status`
- 新项 `result = none`
- 新项 `status = pending`

## State 写回说明
本轮只更新：
- `docs/BOT2_BOT3_STATE.md`

未改动：
- policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排
- 未依据最近日志反向改 policy

## 本轮改变系统认知的一句话
当前前排最值得做的事已经不是继续堆新的 intake，而是把 `Rank 296` 用掉那唯一一次 survivor follow-up，直接回答它能不能升 `P2`；新的 intake 只能老老实实排在它后面。