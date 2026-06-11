# Strategy Review — 2026-04-03 03:41 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short --branch`；仅作状态参考，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-03_0328_realized_skewness_fresh_intake_blocked_by_rank302_survivor_lock.md`
  - `research/optimization_loop/2026-04-03_0310_rank302_basket_rebalance_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-03_0234_rank301_survivor_followup_background_p0.md`
  - `research/optimization_loop/2026-04-03_0145_btc_volclock_first30_impulse_first_verdict_p0.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-03_0302_strategy-review.md`
  - `research/strategy_review/2026-04-03_0149_strategy-review.md`
  - `research/strategy_review/2026-04-03_0055_strategy-review.md`
- 最近新 repo/paper/alpha 报告：
  - `research/quant_digests/2026-04-03_0254_realized-skewness-xs-reversal-alpha.md`
  - `research/quant_digests/2026-04-03_0228_kalshi-macro-vol-regime-gate.md`
  - `research/quant_digests/2026-04-03_0136_coint-basket-hfra-rebalance-alpha.md`
  - `research/quant_digests/2026-04-02_2257_rf-threshold-hfpt-pairs-alpha.md`

## Repo 状态摘要
- `## master...origin/master`
- 工作区存在若干仓库外层临时文件/目录未跟踪（`../../tmp_*` 等）；本轮未改动它们。
- `jerry/momentum` 本轮实际只更新 `docs/BOT2_BOT3_STATE.md` 并新增本条 strategy review 日志，符合 bot2 权限边界。

## 只回答 4 个问题

1) `Paper launch queue` 是否非空？
- 否。
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有待 bot2 兜底推进的 queue 头对象。

2) 本轮 `fresh intake` 是什么？
- 本轮唯一应被保留为下一条 fresh intake 的对象是 `research/quant_digests/2026-04-03_0254_realized-skewness-xs-reversal-alpha.md`。
- 但它只能排在 `Rank 302` survivor follow-up 之后，不能越过当前前排锁。
- `0136` 已不再是 fresh intake：它已经拿到正式编号 `Rank 302` 并进入 `Surviving candidate slot`。

3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得。
- 上一条 fresh intake 就是 `0136`，现已成为 `Rank 302 / cointegrated basket equal-weight drift × threshold rebalance`。
- `2026-04-03_0310_rank302_basket_rebalance_first_verdict_keep_p1.md` 已明确给出 `keep_P1`，而且 follow-up 目标也已经被定义得足够具体：只做一次 clean-room 独立性检查，回答它是不是独立于既有 pair/basket residual 壳的真实增量，而不是继续泛泛补文献。
- 因此这次唯一 follow-up 仍属高杠杆前排动作，不能被新的 intake 抢位。

4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`（`current_target = none`）。
- 最近一次 P2 出口仍是 `Rank 285` 的 `one-time P2->P1 re-scope`；此后没有新对象进入 `Active P2`。
- 因而当前不触发 bot2 作为 `P2 -> P3` 兜底裁判的强制升级动作。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Surviving candidate slot.current_target = Rank 302`
- `Active P2 slot.current_target = none`
- 当前前排对象都有正式 `Rank`；本轮无需补发新的整数编号。

## P2 -> P3 兜底裁判检查
- 当前没有 `Active P2`，因此不触发 bot2 直接把对象改写进 `P3 / Paper launch queue` 或 handoff 路径。
- 最近证据中也没有出现“desk review 已清楚表明足够进入 paper trade，但 bot3 尚未升级”的漏升案例。

## 本轮排班改写
按 policy 默认顺序，当前真实可执行动作应为：
1. `P1 / Surviving candidate`：先执行 `Rank 302` 的唯一一次 decisive follow-up。
2. `fresh intake`：只有在 `Rank 302` 已诚实收口后，才允许继续推进新的 intake。

据此，已将 `cycle_plan` 重写为：
1. `Rank 302 / cointegrated basket equal-weight drift × threshold rebalance`
2. `2026-04-03_0254_realized-skewness-xs-reversal-alpha.md`
3. `2026-04-03_0228_kalshi-macro-vol-regime-gate.md`
4. `2026-04-02_2257_rf-threshold-hfpt-pairs-alpha.md`

重写理由：
- `0328` 的 blocked 记录说明上一版把新 intake 写到 survivor 前面，已与 policy 前排锁冲突；本轮必须纠正。
- `Rank 302` 是当前唯一合法且高优先级的前排动作。
- 在把 survivor follow-up 诚实排回第 1 位后，才允许用剩余预算补具体 fresh intake。
- 未把任何 background pool 旧候选自动拉回前排。

## 本轮写回内容
- 已更新：`docs/BOT2_BOT3_STATE.md`
- 已新增：`research/strategy_review/2026-04-03_0341_strategy-review.md`
- 未改动：policy / brief / operating card / auto loop / cron prompt

## 本轮改变系统认知的一句话
当前前排唯一真实动作不是新的发现，而是 `Rank 302` 的那一次 survivor exit follow-up；只有把它诚实收口后，`0254 realized-skewness` 才能成为下一条 fresh intake。
