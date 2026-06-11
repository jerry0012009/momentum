# Strategy Review — 2026-04-04 03:00 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short --branch`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-04_0226_rank320_p2_admission_keep_p2_honesty_postcost.md`
  - `research/optimization_loop/2026-04-04_0120_rank320_survivor_followup_promote_p2.md`
  - `research/optimization_loop/2026-04-04_0101_rank320_wilder_rsi_fast_exit_first_verdict_keep_p1.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-04_0221_strategy-review.md`
  - `research/strategy_review/2026-04-04_0111_strategy-review.md`
- 最近新 digest：
  - `research/quant_digests/2026-04-04_0146_sameunderlier-crossvenue-gap-latency-budget-alpha.md`
  - `research/quant_digests/2026-04-04_0020_extreme-divergence-exhaustion-fade-alpha.md`

## repo 状态摘录
- 当前 repo 仍有大量未跟踪文件与临时产物；它们只作为环境 evidence，不改变本轮 policy / state 解释。
- 本轮继续遵守硬约束：只更新 `docs/BOT2_BOT3_STATE.md`；未改动 policy / brief / operating card / auto loop / cron prompt。

## 只回答 4 个问题

1) `Paper launch queue` 是否非空？
- 否。
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`，没有新的待接线 queue 头对象。

2) 本轮 `fresh intake` 是什么？
- 当前运行态里没有正在占用的 `fresh intake`。
- `Fresh intake slot.current_target = none`，上一条 fresh intake `Rank 320` 已在 survivor follow-up 后升入 `Active P2`。
- 因此前排动作诚实排入后，本轮新的 fresh intake 头应更新为最新未占槽对象：
  - `research/quant_digests/2026-04-04_0146_sameunderlier-crossvenue-gap-latency-budget-alpha.md`
- conditional fresh intake 则顺延为：
  - `research/quant_digests/2026-04-04_0020_extreme-divergence-exhaustion-fade-alpha.md`

3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 不存在可再分配的 survivor follow-up。
- 上一条 fresh intake 是 `Rank 320 / Wilder RSI breakout × EMA200/ADX/volume allow × fast RSI-45 exit`；它那唯一一次 follow-up 已在 `2026-04-04_0120_rank320_survivor_followup_promote_p2.md` 用掉，并且答案已经是 `promote_P2`。
- 因而本轮不能再把它按 survivor 续写；后续只能按 `Active P2 admission` 逻辑收口。

4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 存在。
- 当前明确 `Active P2 = Rank 320 / Wilder RSI breakout × EMA200/ADX/volume allow × fast RSI-45 exit`。
- 基于最近 desk evidence，它当前离 **`P3` 出口最近**：
  - 已完成 `P1 survivor -> P2` 的层级变化；
  - 已证明 `BTC/ETH/SOL × 5m/15m` 上存在诚实、可复现、post-cost 为正的 admission 路径；
  - `2026-04-04_0226` 已把 `honesty / execution realism + post-cost effectiveness` 这一轴收口为 `keep_P2`，说明它不是主要依赖理想 fills 的摩擦幻觉。
- 但按当前证据，bot2 还不能直接兜底把它推入 `P3`：`time stability + parameter stability` 仍未完成正式收口；因此最诚实动作是先把下一轮前两项锁给 `Rank 320` 的出口判断。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Fresh intake slot.current_target = none`
- `Surviving candidate slot.current_target = none`
- `Active P2 slot.current_target = Rank 320 / Wilder RSI breakout × EMA200/ADX/volume allow × fast RSI-45 exit`
- 当前前排对象不存在已达 `keep_P1 / P2 / P3` 但无正式 rank 的情况；本轮无需补新 `Rank`。

## P2 -> P3 兜底裁判检查
- 当前只有一个明确 `Active P2`：`Rank 320`。
- 最近 evidence 已把它推到明显高于 `P1`、且更靠近 `P3` 的位置；但 desk review 仍未清楚证明它已经“足够值得直接进入 paper trade / paper launch”。
- 因此本轮 **不**直接把它改写到 `P3 / Paper launch queue`；而是把 `cycle_plan` 前两项改成：
  1. 直接做 `time stability + parameter stability`
  2. 若仍未自然给出出口，则立即做 `P3 / P1 / P0` 三选一出口收口
- 这样既避免重复 `honesty` 轴，也避免放任它继续开放式 `keep_P2`。

## 本轮排班改写
按 policy 默认顺序扫描后：
- `P3`：无待接线对象
- `P2`：有且只有一个明确对象 —— `Rank 320`
- `P1`：无 survivor
- 因此前两项必须先给 `Rank 320`，且不能重复上一轮已完成的 `honesty/post-cost` 轴

因此本轮将 `cycle_plan` 重写为 4 项：
1. `Rank 320`：先做 `time stability + parameter stability`，回答这条 fast-exit 壳在更长时间窗与邻近参数扰动下是否仍保留非单点优势
2. `Rank 320`：若第 1 项未直接给出口，则立即做更接近出口的三选一收口：`promote_P3 / drop_to_background/P0 / one-time P2->P1 re-scope`
3. `research/quant_digests/2026-04-04_0146_sameunderlier-crossvenue-gap-latency-budget-alpha.md`：作为新的 fresh intake
4. `research/quant_digests/2026-04-04_0020_extreme-divergence-exhaustion-fade-alpha.md`：作为 conditional fresh intake

改写理由：
- 当前存在合法 `Active P2`，已有前排对象的收口优先级高于新的发现；
- `Rank 320` 当前离 `P3` 最近，所以要先做最会改变层级的剩余 admission 轴；
- `p2_last_evidence_axis = honesty_execution_realism_post_cost_effectiveness`，因此本轮不能继续沿同一 axis 续写；
- 在前两项诚实锁给 `Rank 320` 后，fresh intake 头应按“最近新 repo/paper/alpha 报告”切换到更新的 `2026-04-04_0146`，而不是继续把较旧的 `2026-04-04_0020` 放在更前面；
- 未把任何 background pool 旧候选自动拉回前排。

## 本轮写回
- 已更新：`docs/BOT2_BOT3_STATE.md`
- 本轮仅重写 `cycle_plan`
- 未改动 policy / brief / operating card / auto loop / cron prompt。
