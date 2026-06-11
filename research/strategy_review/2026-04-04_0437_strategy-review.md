# Strategy Review — 2026-04-04 04:37 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-04_0424_rank322_kraken_pairs_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-04_0435_rank323_candidate_blocked_by_rank322_survivor_lock.md`
  - `research/optimization_loop/2026-04-04_0321_rank320_p2_admission_drop_to_background_time_parameter_failure.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-04_0356_strategy-review.md`

## repo 状态摘录
- repo 仍有大量未跟踪研究产物与脚本；它们只作环境 evidence。
- 本轮继续遵守硬约束：**只更新 `docs/BOT2_BOT3_STATE.md`**；未改动 policy / brief / operating card / auto loop / cron prompt。

## 只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- **否。**
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有新的待接线 queue 头对象。

### 2) 本轮 `fresh intake` 是什么？
- 当前运行态里的最新 fresh intake 已在 04:24 UTC 收口为 `Rank 322 / keep_P1`，并进入 `Surviving candidate slot`。
- 因此在 survivor 收口之前，前排新 intake 不能越过它；**下一条合法的 fresh intake 头**应是：
  - `research/quant_digests/2026-04-04_0347_volume-router-tsmom-xsreversal-dualbook-alpha.md`
- 若预算仍有余，补位 fresh intake 顺位为：
  - `research/quant_digests/2026-04-04_0416_obi-microprice-pairs-shell-alpha.md`
  - `research/quant_digests/2026-04-04_0020_extreme-divergence-exhaustion-fade-alpha.md`

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得，而且现在必须先做。**
- 上一条 fresh intake 是 `Rank 322 / cointegrated spread z-score × stop-loss/time-exit`。
- 04:24 UTC 的 first verdict 已明确把它写成 `keep_P1`：对象不是空泛的 pairs 教材叙事，而是带有 `entry/exit/stop/cost/portfolio` 完整壳、并至少保留一条 `15m / near-short-cycle` 诚实可迁移路径的 pairs/stat-arb raw alpha。
- 按 policy，survivor 只能是上一条 fresh intake，且只允许 **1 次** decisive follow-up；04:35 UTC 的 `Rank 323` 候选已被明确记录为 **因 `Rank 322` survivor lock 而 blocked**。
- 因此本轮第 1 优先动作必须是：直接回答 `Rank 322` 是否存在至少一条在更严格 `pair admission / half-life / correlation / cost ladder / horizon narrowing` 口径下仍保留正净边的唯一可迁移 lane；有则 `promote_P2`，没有则收口到 `background/P0`。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **不存在。**
- `Active P2.current_target = none`。
- `Rank 320` 已在 03:21 UTC 的 `time stability + parameter stability` admission 中被明确收口到 `background/P0`：把样本拉长到 `2025-01-01 ~ 2026-04-04` 后，原先 `BTC/ETH/SOL × 5m/15m` 六条主路径全部转负，且邻近参数也没有出现唯一清楚的 re-scope lane。
- 因此本轮不存在需要 bot2 兜底直接升 `P3` 的 `Active P2` 对象。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Fresh intake slot.current_target = none`
- `Surviving candidate slot.current_target = Rank 322 / cointegrated spread z-score × stop-loss/time-exit`
- `Active P2 slot.current_target = none`
- 当前所有前排对象均已有正式 `Rank`；本轮无需补新 rank。

## P2 -> P3 兜底裁判检查
- 当前没有明确 `Active P2`，因此本轮不存在“desk review 已清楚表明足够 paper trade、但 bot3 尚未升级，需 bot2 直接兜底推进到 `P3`”的对象。
- `Rank 320` 已被最新 admission 证据明确打回 `P0`；`Rank 322` 仍处于 `P1 survivor`，下一步门槛是先回答它能否通过唯一一次更严格的 survivor follow-up，而不是直接进入 paper launch。

## 本轮排班改写
按 policy 默认顺序扫描：
1. `P3`：无待接线对象
2. `P2`：无明确 `Active P2`
3. `P1`：有且只有一个 survivor —— `Rank 322`
4. `fresh intake`：只有在第 1 项已诚实排入后，才能补新的具体对象

因此本轮把 `cycle_plan` 重写为 4 项：
1. `Rank 322` survivor follow-up：直接回答是否存在唯一、诚实、可迁移的 pairs lane，结论只能是 `promote_P2` 或 `background/P0`
2. `2026-04-04_0347_volume-router-tsmom-xsreversal-dualbook-alpha.md`：作为 survivor 收口后的 fresh intake 头
3. `2026-04-04_0416_obi-microprice-pairs-shell-alpha.md`：作为补位 fresh intake
4. `2026-04-04_0020_extreme-divergence-exhaustion-fade-alpha.md`：作为第二补位 fresh intake

改写理由：
- 当前存在合法 `P1 survivor` 动作，且没有 `P3/P2` 前排对象，因此 survivor 收口优先级高于新的发现；
- `Rank 322` 的唯一一次 follow-up 仍享有前排锁定权，不能让新的 `keep_P1` 候选覆盖；
- `Rank 323` 已被最近 optimization log 明确记录为 blocked，因此不应继续把它写成当前合法 front action；
- 新 intake 头优先从最近新 repo/paper/alpha 报告中选，且不自动从 background pool 拉回旧候选。

## 本轮写回
- 已更新：`docs/BOT2_BOT3_STATE.md`
- 本轮只重写 runtime state 中的 `cycle_plan`
- 未改动 policy / brief / operating card / auto loop / cron prompt。
