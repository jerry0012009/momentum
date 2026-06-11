# 2026-04-08 06:09 UTC strategy review

## Scope
按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 执行本轮 40 分钟 desk review；本轮只更新 runtime state，不改 policy / brief / operating card / auto loop / cron prompt。

## 先回答 4 个问题

### 1) `Paper launch queue` 是否非空？
**否。**

- `Paper launch queue.current_target = none`
- `Rank 200 / 201 / 213 / 229 / 342` 都已在 `connected_runner_live`
- 最近 queue / wiring 完成记录仍是 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md`

因此当前没有待接线的 `P3 / Paper launch queue` 头对象。

### 2) 本轮 `fresh intake` 是什么？
**本轮 fresh intake 队头改为 `research/park_reframe/2026-04-06_1034_rank60-park-reframe.md`。**

原因：
- 最近新的 digest intake 已一路推进到 `Rank 365`，其中 `Rank 364` 已合法占据 survivor 槽，`Rank 365` 则刚完成 first verdict 并已获得正式 rank；
- 在不允许自动拉回 background pool 旧候选的前提下，当前剩余可诚实补位的新对象，优先来自 policy 允许的 `research/park_reframe/INDEX.md` 中 `derived_hypothesis_drafted / soft_reframe_candidate`；
- 其中 `Rank 60` reframe 是更硬的 `derived_hypothesis_drafted`，比继续重复已做完 first verdict 的 recent digests 更适合作为当前 fresh intake 队头。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**

这里的上一条 fresh intake 是 `Rank 365 / benchmark-beta return differential × thresholded pair fade`。

理由：
- 它已把主语压清为 `benchmark-beta adjusted residual -> thresholded pair fade`，不是泛 pairs-trading 教科书重述；
- 最小 clean-room 实验壳、宿主（majors perp）、时间框架、成本口径与 entry/exit 壳都已写出；
- 当前缺的不是对象主语，而是一次决定性的 survivor follow-up：
  1. benchmark 定义敏感度；
  2. 相对简单 raw-spread z-score 基线的 post-cost 增益；
  3. 净边是否真的来自 beta-adjusted residual，而不是旧式 pairs MR 在特定子样本上的偶然存活。

因此它值得那唯一一次 follow-up；但当前 `Rank 364` 仍合法占据 survivor 槽，所以 `Rank 365` 的 follow-up 只能作为 **收口后的下一优先动作** 排入 `cycle_plan`，不能越权直接覆盖当前 survivor。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。**

- `Active P2 slot.current_target = none`
- 最近一次 `P2` 出口决策仍是 `Rank 342`，但它已经完成 `P2 -> P3 -> connected_runner_live`
- 当前没有需要 bot2 兜底直升 `P3` 的漏升 `Active P2`

因此本轮不存在必须由 bot2 直接改写进 `P3 / Paper launch queue` 的在场 P2 对象。

## 最近读取与证据核对
1. `docs/BOT2_BOT3_POLICY.md`
2. `docs/BOT2_BOT3_STATE.md`
3. repo 工作树：`git status --short`
4. 最近 optimization 记录：
   - `2026-04-08_0555_rank365_benchmark_beta_pairs_fresh_intake_keep_p1.md`
   - `2026-04-08_0530_rank364_polymarket_kalshi_samehour_strike_arb_intake_keep_p1.md`
   - `2026-04-08_0516_rank363_survivor_followup_exhausted_background.md`
5. 最近 strategy review：
   - `2026-04-08_0436_strategy-review.md`
6. 最近 digest / park-reframe 队头：
   - `research/quant_digests/INDEX.md` 时间序列确认最近 digest 已一路推进到 `Rank 365`
   - `research/park_reframe/INDEX.md` 显示当前最适合补位的 fresh intake 来源是 `derived_hypothesis_drafted / soft_reframe_candidate`

## Rank / 前排合法性检查
- `Paper launch queue.current_target = none`，合法
- `Surviving candidate slot.current_target = Rank 364`，且已有正式 rank，合法
- `Active P2 slot.current_target = none`，合法
- `Rank 365` 已获得正式 `Rank`，不存在前排对象达到 `keep_P1 / P2 / P3` 却无正式 rank 的情况

因此本轮无需补 rank，只需重写 runtime state 与当前轮 `cycle_plan`。

## 排班判断
按 policy 默认顺序：
`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0`

本轮扫描结果：
- `P3`：无待接线对象
- `P2`：无在场 `Active P2`
- `P1`：存在明确 survivor `Rank 364`，必须排在最前并收口
- survivor 收口后，下一优先不是新的陌生对象，而是 **上一条 fresh intake `Rank 365` 的唯一一次合法 follow-up**
- 只有把这条前排链条诚实放在前面后，剩余预算才给新的 fresh intake
- 在当前没有新的未判 recent digest 可优先覆盖时，fresh intake 来源转向 `park_reframe/INDEX.md` 中的 `derived_hypothesis_drafted / soft_reframe_candidate`

## Runtime writeback
本轮已重写 `docs/BOT2_BOT3_STATE.md`：

### Fresh intake slot
- `current_target` 改为 `research/park_reframe/2026-04-06_1034_rank60-park-reframe.md`
- `latest_result` 明确写成：`Rank 365` 值得那唯一一次 survivor follow-up，但在 `Rank 364` 的 survivor 锁尚未收口前不能越权覆盖

### Surviving candidate slot
- 保持 `Rank 364 / Polymarket × Kalshi same-hour strike mismatch binary lock-in arb`
- `followup_budget_remaining = 1`
- 本轮必须优先回答它是 `promote_P2` 还是 `keep_P1 exhausted -> background`

### Active P2 slot
- 保持 `none`
- 本轮不存在需要 bot2 兜底直升 `P3` 的在场对象

### cycle_plan
1. `Rank 364 / Polymarket × Kalshi same-hour strike mismatch binary lock-in arb`
   - 做 survivor 的唯一决定性 follow-up，直接回答是否 `promote_P2`
2. `Rank 365 / benchmark-beta return differential × thresholded pair fade`
   - 若 `Rank 364` 收口释放 survivor 槽，立即承接为唯一合法下一条 survivor follow-up
3. `research/park_reframe/2026-04-06_1034_rank60-park-reframe.md`
   - 作为 survivor 链条已诚实排入后的首条 fresh intake
4. `research/park_reframe/2026-04-07_0302_rank56-park-reframe.md`
   - 作为剩余预算里的 conditional fresh intake

新生成项均保持：
- `result = none`
- `status = pending`

## 为什么本轮不需要 bot2 兜底升 P3
policy 要求 bot2 在 desk review 已明确看到某个**在场 `Active P2`** 已足够值得进入 paper trade，而 bot3 尚未升级时，直接改写到 `P3 / handoff`。

本轮不满足该条件：
- `Active P2 = none`
- 当前最前排的真实收口对象是 `Rank 364` survivor，而不是 `P2`
- 最近完成的 `Rank 342` 已经在 `connected_runner_live`

因此本轮不存在需要 bot2 强制推进到 `P3 / Paper launch queue` 的漏升对象。

## 一句话总结
本轮没有待接线的 `P3`，也没有漏升的 `Active P2`；当前必须先收口 `Rank 364` survivor，再把 `Rank 365` 作为唯一合法下一条 survivor follow-up 接上，之后 fresh intake 队头切到 `Rank 60` derived hypothesis，剩余预算再给 `Rank 56` soft reframe。