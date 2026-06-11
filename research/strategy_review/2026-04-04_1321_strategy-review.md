# Strategy Review — 2026-04-04 13:21 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-04_1212_rank328_survivor_followup_promote_p2_overlay_replay_protocol.md`
  - `research/optimization_loop/2026-04-04_1234_rank329_bybit_laddered_inventory_skew_maker_alpha_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-04_1317_rank330_dual_supertrend_nonfiring_first_verdict_keep_p1.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-04_1208_strategy-review.md`
  - `research/strategy_review/2026-04-04_1101_strategy-review.md`

## repo 状态摘录
- repo 仍有大量未跟踪研究产物与临时文件；这些只作环境 evidence，不改变本轮 policy 判定。
- 本轮继续遵守硬约束：**只更新 `docs/BOT2_BOT3_STATE.md`**；未改动 policy / brief / operating card / auto loop / cron prompt。

## 只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- **否。**
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有新的待接线 queue 头对象。

### 2) 本轮 `fresh intake` 是什么？
- **若严格按当前前排顺序，本轮 fresh intake 头是**：`research/quant_digests/2026-04-04_1226_azalyst-betaneutral-1h-xs-ranker-alpha.md`。
- 原因：当前前排已有 `Active P2 = Rank 328` 与 `Surviving candidate = Rank 330`，它们按 policy 优先级都必须排在 fresh intake 之前；而上一批新 intake 里 `Rank 329` 与 `Rank 330` 已经完成 first verdict，所以轮到新的具体 intake 时，最新未处理头对象就是 `2026-04-04_1226_azalyst-betaneutral-1h-xs-ranker-alpha.md`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得。**
- 上一条 fresh intake 已在 `research/optimization_loop/2026-04-04_1317_rank330_dual_supertrend_nonfiring_first_verdict_keep_p1.md` 被正式写成 `Rank 330`，并进入 `Surviving candidate slot`，`followup_budget_remaining = 1`。
- 这条对象虽然当前 repo 实现几乎不触发，但 raw alpha、entry/exit/sizing/cost 壳已经明确，而且 blocker 已经收敛到单一可执行问题：`canonical SuperTrend / firing density` 对账。
- 因此它合法占有那唯一一次 follow-up；但这次 follow-up 必须直接回答出口：**升 `P2` 还是用尽预算后收口回 `background/P0`**，不能继续拖成第二次 survivor。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **存在。**
- 当前明确 `Active P2 = Rank 328 / water-filling leverage equalization × factor-adjusted deleveraging shared risk overlay`。
- 依据 `research/optimization_loop/2026-04-04_1212_rank328_survivor_followup_promote_p2_overlay_replay_protocol.md`，它已经具备可挂接的 multi-sleeve state/ledger 壳、清楚的对照实验框架，以及最小 admission 指标；因此在三种出口里，它当前**更接近 `P3`**，而不是 `P1` 或 `P0`。
- 但它还没有 desk replay 结果与通过阈值，所以本轮仍应先做 `P2 admission`，不能提前越级写成 `P3`。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Surviving candidate slot.current_target = Rank 330`
- `Active P2 slot.current_target = Rank 328`
- 当前前排对象均已有正式 rank；本轮无需补新 rank。

## P2 -> P3 兜底裁判检查
- 当前唯一 `Active P2` 是 `Rank 328`。
- 现有证据说明它已经明显超过纯概念叙事阶段，且出口方向更偏 `P3`；但 desk review 还**没有**显示它已经完成足以直接进入 paper trade 的 replay honesty / metric passability 证据。
- 因此本轮**不触发** bot2 的强制 `P2 -> P3` 兜底升级；正确动作是把它排成 `P2 admission` 第一优先，而不是继续泛泛研究，也不是提前改写成 `Paper launch queue`。

## 本轮写回
已重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`，按 policy 默认顺序改为：
1. `Rank 328 / water-filling leverage equalization × factor-adjusted deleveraging shared risk overlay`
2. `Rank 330 / dual SuperTrend flip × EMA50 × volume gate`
3. `research/quant_digests/2026-04-04_1226_azalyst-betaneutral-1h-xs-ranker-alpha.md`
4. `research/quant_digests/2026-04-04_1314_dynamic-mst-cluster-relative-value-alpha.md`

写回理由：
- `P3` 为空，所以不能凭空制造 launch wiring；
- `Rank 328` 是当前唯一明确 `Active P2`，必须先做 admission；
- `Rank 330` 是上一条 fresh intake 的唯一 survivor，按 policy 享有前排锁定权；
- 只有在 `P2/P1` 都已诚实排入当前轮前部后，才用剩余预算补新的具体 fresh intake；
- 新 intake 直接指定到两条最新具体对象，避免抽象占位。

## 本轮结论一句话
当前前排主线很清楚：**先把 `Rank 328` 做成真正会改变层级判断的 `P2 admission`，同时用掉 `Rank 330` 那唯一一次 survivor follow-up；只有这两条前排动作已诚实排入后，才切回新的 fresh intake。**
