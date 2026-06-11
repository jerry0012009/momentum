# Strategy Review — 2026-04-04 03:56 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-04_0351_rank321_sameunderlier_crossvenue_gap_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-04_0321_rank320_p2_admission_drop_to_background_time_parameter_failure.md`
  - `research/optimization_loop/2026-04-04_0336_rank320_exit_decision_blocked_already_closed_by_step1.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-04_0300_strategy-review.md`
- 最近新 digest：
  - `research/quant_digests/2026-04-04_0316_kraken-pairs-zscore-stoploss-shell.md`
  - `research/quant_digests/2026-04-04_0347_volume-router-tsmom-xsreversal-dualbook-alpha.md`
  - `research/quant_digests/2026-04-04_0020_extreme-divergence-exhaustion-fade-alpha.md`

## repo 状态摘录
- repo 仍有大量未跟踪研究产物与脚本；它们只作环境 evidence。
- 本轮继续遵守硬约束：**只更新 `docs/BOT2_BOT3_STATE.md`**；未改动 policy / brief / operating card / auto loop / cron prompt。

## 只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- **否。**
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有新的待接线 queue 头对象。

### 2) 本轮 `fresh intake` 是什么？
- 运行态当前没有占用中的 `fresh intake`；上一条 fresh intake 已经在 03:51 UTC 收口为 `Rank 321 / keep_P1`，并进入 survivor 槽位。
- 因此前排收口后，新的 fresh intake 头应切到：
  - `research/quant_digests/2026-04-04_0316_kraken-pairs-zscore-stoploss-shell.md`
- 若预算仍有余，conditional fresh intake 顺位为：
  - `research/quant_digests/2026-04-04_0347_volume-router-tsmom-xsreversal-dualbook-alpha.md`
  - `research/quant_digests/2026-04-04_0020_extreme-divergence-exhaustion-fade-alpha.md`

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得，而且现在必须先做。**
- 上一条 fresh intake 是 `Rank 321 / same-underlier cross-venue gap mean reversion × latency budget`。
- 它刚完成 first verdict 并被正式记为 `keep_P1`；policy 规定 survivor 只能是上一条 fresh intake，且只允许 **1 次** 最小 decisive follow-up。
- 当前没有 `P3`、没有 `Active P2`，所以这一条 survivor follow-up 是本轮默认最高优先级动作。
- 这次 follow-up 不该再重复“跨 venue gap 会收敛”的机制故事，而应直接回答：**是否存在至少一条诚实可迁移的低延迟 desk lane；有则 `promote_P2`，没有就收口到 `background/P0`。**

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **不存在。**
- `Active P2.current_target = none`。
- `Rank 320` 已在 03:21 UTC 的 `time stability + parameter stability` admission 中被明确收口到 `background/P0`，且 03:36 UTC 已确认原先条件式 exit item 只是“对象已关闭后的 blocked 补记”。
- 因此本轮不存在需要 bot2 兜底升 `P3` 的 `Active P2`；前排唯一真实动作就是 `Rank 321` 的 survivor 出口检查。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Fresh intake slot.current_target = none`
- `Surviving candidate slot.current_target = Rank 321 / same-underlier cross-venue gap mean reversion × latency budget`
- `Active P2 slot.current_target = none`
- 当前前排对象均已有正式 rank；本轮无需补新 `Rank`。

## P2 -> P3 兜底裁判检查
- 当前没有明确 `Active P2`，所以本轮不存在“bot3 没升、但 bot2 必须直接兜底推进到 `P3`”的对象。
- `Rank 320` 已被最新 admission 证据清楚打回 `P0`；`Rank 321` 仍停留在 `P1 survivor`，距离 `P2` 的关键门槛是能否找到一条诚实可迁移的低延迟 desk lane，而不是直接 paper launch。

## 本轮排班改写
按 policy 默认顺序扫描：
1. `P3`：无待接线对象
2. `P2`：无明确 `Active P2`
3. `P1`：有且只有一个 survivor —— `Rank 321`
4. `fresh intake`：在 survivor 诚实排入后，再补新的具体对象

因此本轮把 `cycle_plan` 重写为 4 项：
1. `Rank 321` survivor follow-up：直接回答是否存在诚实可迁移的低延迟 desk lane，结论只能是 `promote_P2` 或 `background/P0`
2. `2026-04-04_0316_kraken-pairs-zscore-stoploss-shell.md`：作为新的 fresh intake
3. `2026-04-04_0347_volume-router-tsmom-xsreversal-dualbook-alpha.md`：作为 conditional fresh intake
4. `2026-04-04_0020_extreme-divergence-exhaustion-fade-alpha.md`：作为补位 fresh intake

改写理由：
- 当前存在合法 `P1 survivor` 动作，且没有 `P3/P2` 前排对象，因此 survivor 收口优先级高于新的发现；
- `Rank 321` 的唯一一次 follow-up 默认享有前排锁定权，不能被新的 `keep_P1` 候选覆盖；
- 新 intake 头优先从最近新 repo/paper/alpha 报告中选，按时间与结构价值，先是 `0316 pairs shell`，再是 `0347 dual-book router`，最后才是较早的 `0020 exhaustion fade`；
- 未把任何 background pool 旧候选自动拉回前排。

## 本轮写回
- 已更新：`docs/BOT2_BOT3_STATE.md`
- 本轮仅重写 `cycle_plan`
- 未改动 policy / brief / operating card / auto loop / cron prompt。
