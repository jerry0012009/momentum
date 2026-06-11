# Strategy Review — 2026-04-04 14:30 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-04_1428_rank330_survivor_followup_canonical_supertrend_promote_p2.md`
  - `research/optimization_loop/2026-04-04_1347_rank328_p2_rescope_to_p1_missing_unified_overlay_replay_board.md`
  - `research/optimization_loop/2026-04-04_1317_rank330_dual_supertrend_nonfiring_first_verdict_keep_p1.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-04_1321_strategy-review.md`

## repo 状态摘录
- repo 仍有大量未跟踪研究产物与临时文件；这些只作环境 evidence，不改变本轮 policy 判定。
- 本轮继续遵守硬约束：**只更新 `docs/BOT2_BOT3_STATE.md`**；未改动 policy / brief / operating card / auto loop / cron prompt。

## 只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- **否。**
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有新的待接线 queue 头对象。

### 2) 本轮 `fresh intake` 是什么？
- **本轮 fresh intake 头是**：`research/quant_digests/2026-04-04_1226_azalyst-betaneutral-1h-xs-ranker-alpha.md`。
- 原因：当前前排只剩一个明确 `Active P2 = Rank 330`；`Rank 328` 已在 13:47 UTC 明确做成一次性 `P2 -> P1 re-scope` 并退出前排，`Rank 330` 的 fresh intake 与 survivor follow-up 都已完成，所以新的 fresh intake 头自然切到 `2026-04-04_1226_azalyst-betaneutral-1h-xs-ranker-alpha.md`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得，而且这次 follow-up 已经用完并成功改变层级。**
- 上一条 fresh intake 是 `research/quant_digests/2026-04-04_1050_dual-supertrend-nonfiring-alpha.md`，已被分配为 `Rank 330`。
- 在 `research/optimization_loop/2026-04-04_1428_rank330_survivor_followup_canonical_supertrend_promote_p2.md` 中，唯一 follow-up 已直接回答了关键 blocker：repo 当前口径在 `BTCUSDT 15m recent 90d` 上只有 `bull_flip=2 / bear_flip=3`，但 canonical SuperTrend 口径恢复到 `146 / 146` 次 flip，并重新产生 `69` 个 long 与 `87` 个 short 壳信号。
- 所以结论不是“还值不值得继续跟”，而是：**这次 follow-up 已被证明值得，并且它已经把 `Rank 330` 从 `P1` 推进到 `Active P2`；survivor 预算已用完，不再允许第二次 P1 follow-up。**

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **存在。**
- 当前明确 `Active P2 = Rank 330 / dual SuperTrend flip × EMA50 × volume gate`。
- 结合最新证据，这条对象当前**离 `P3` 最近**，不是 `P1` 也不是 `P0`：
  - 它的核心 blocker 已从“raw alpha 不 firing”转成“repo 实现偏离 canonical”；
  - canonical 化后已经恢复出足够继续做 admission 的信号密度；
  - 目前缺的是 `effectiveness / cross-asset / time / parameter / honesty` 的 admission 收口，而不是概念重写或 survivor 复查。
- 但 desk review 还没有清楚证明它已经足够进入 paper trade，所以本轮**不触发 bot2 的强制 `P2 -> P3` 兜底升级**；正确动作是直接把 `Rank 330` 排成 admission + 出口决策前排，而不是继续开放式研究。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Fresh intake slot.current_target = research/quant_digests/2026-04-04_1050_dual-supertrend-nonfiring-alpha.md`（done，已具正式 `Rank 330`）
- `Surviving candidate slot.current_target = none`
- `Active P2 slot.current_target = Rank 330`
- 当前前排对象均已有正式 rank；本轮无需补新 rank。

## P2 -> P3 兜底裁判检查
- 当前唯一 `Active P2` 是 `Rank 330`。
- 现有 desk review 证据已经说明它更接近 `P3` 而不是 `P1/P0`，但还**没有**完成足以直接 paper launch 的 admission 五维收口。
- 因此本轮 bot2 的正确兜底动作不是提前强升 `P3`，而是把 `cycle_plan` 改写成：
  1. 先做 `Rank 330` 的 `effectiveness / cross-asset` admission；
  2. 若无致命 flaw，立刻把同一对象排成 `time / parameter / honesty / execution realism` 出口决策轮，并明确要求若证据已足够 paper trade 就直接 `promote_P3`；
  3. 然后才补 fresh intake `2026-04-04_1226_azalyst-betaneutral-1h-xs-ranker-alpha.md`；
  4. 再补 `2026-04-04_1314_dynamic-mst-cluster-relative-value-alpha.md`。

## 本轮写回
已重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`，按 policy 默认顺序改为：
1. `Rank 330 / dual SuperTrend flip × EMA50 × volume gate` — `effectiveness / cross-asset` admission
2. `Rank 330 / dual SuperTrend flip × EMA50 × volume gate` — `time / parameter / honesty / execution realism` 出口决策
3. `research/quant_digests/2026-04-04_1226_azalyst-betaneutral-1h-xs-ranker-alpha.md`
4. `research/quant_digests/2026-04-04_1314_dynamic-mst-cluster-relative-value-alpha.md`

写回理由：
- `P3` 为空，所以不能凭空制造 launch wiring；
- 当前只有一个明确前排对象 `Rank 330`，必须优先收口；
- `Rank 330` 已完成 P1 路径，不能再伪装成新的 survivor follow-up，下一步必须是 P2 admission 与出口决策；
- 只有当前前排链条已被诚实排到前两项后，才合法切回新的具体 fresh intake。

## 本轮结论一句话
当前前排主线已经收缩成一件事：**先把 `Rank 330` 做成真正会改变层级的 P2 admission + 出口决策轮；如果它经收口后已足够 paper trade，就必须直接升 `P3`，不能继续拖在开放式研究里。**
