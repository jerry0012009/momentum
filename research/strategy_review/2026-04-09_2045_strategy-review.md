# 2026-04-09 20:45 UTC strategy review

## Scope
按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 执行本轮 40 分钟 desk review；本轮只核对 runtime truth、最近 evidence、前排合法性与默认排班顺序，并只更新 `BOT2_BOT3_STATE.md`。

## 先回答 4 个问题

### 1) `Paper launch queue` 是否非空？
**否。**

- `Paper launch queue.current_target = none`
- `Rank 200 / 201 / 213 / 229 / 342` 都已在 `connected_runner_live`
- 最近 `optimization_loop` 与 `strategy_review` 没有出现“已进 P3 但还没 dedicated runner / scheduler / first verified run”的待接线对象

### 2) 本轮 `fresh intake` 是什么？
**是 `research/quant_digests/2026-04-09_0144_kimchi-premium-hedged-handoff-shell.md`。**

原因：
- 当前没有 `P3` 待接线对象，也没有 `Active P2`
- `Rank 366` 已经在上一轮 fresh intake first verdict 中转入 `Surviving candidate slot`，所以它现在不再占 fresh intake 槽
- 按 policy，当前默认顺序应先给 survivor 一次唯一 follow-up；但 fresh intake 槽本身需要切到**最近新的 alpha report**，而不是继续停留在已经完成首判的旧对象上
- 最近新报告里，`negative KRW premium accumulation × positive-premium handoff exit` 是最新且边界最清楚的一条：它不是 generic basis，而是更窄的韩盘负溢价回归 / 对冲退出 pocket

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**

- 上一条 fresh intake 是 `Rank 366 / turning-point-confirmed trend leg × short-horizon continuation`
- `research/optimization_loop/2026-04-09_1823_rank366_fresh_intake_keep_p1_turningpoint_continuation.md` 已明确：这条线不是 generic trend/momentum 改写，而是已被压成 `15m-first` 的 turning-point confirmed continuation pocket
- 当前唯一未收口的高杠杆问题也很明确：`turning-point` 定义是否能做成**严格非重绘、因果可执行**的事件；这正符合 policy 对 survivor “唯一一次便宜诚实 follow-up” 的要求
- 因此 `Rank 366` 应继续占用 survivor 前排锁定位，不能被新的 `keep_P1` 候选覆盖

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。**

- `Active P2 slot.current_target = none`
- 最近明确的 P2 出口仍是 `Rank 342`，但它已完成 `P2 -> P3 -> connected_runner_live`
- 当前没有需要 bot2 兜底直升 `P3` 的漏升 `Active P2`

## 最近读取与证据核对
1. `docs/BOT2_BOT3_POLICY.md`
2. `docs/BOT2_BOT3_STATE.md`
3. repo 状态
   - `git status --short` 显示工作区存在大量历史未跟踪临时文件；本轮只把它当作 repo hygiene 事实，不据此 reopen background pool，也不倒推改 policy
4. 最近 `research/optimization_loop/`
   - `2026-04-09_2040_cycle_plan_no_pending_guard.md`
   - `2026-04-09_2036_cycle_plan_no_pending_guard.md`
   - `2026-04-09_2030_cycle_plan_no_pending_guard.md`
   - `2026-04-09_2025_cycle_plan_no_pending_guard.md`
   - `2026-04-09_2019_cycle_plan_no_pending_guard.md`
   - `2026-04-09_2015_cycle_plan_no_pending_guard.md`
   - `2026-04-09_2010_cycle_plan_no_pending_guard.md`
   - `2026-04-09_2003_cycle_plan_no_pending_guard.md`
5. 最近 `research/strategy_review/`
   - `2026-04-09_1759_strategy-review.md`
   - `2026-04-09_1659_strategy-review.md`
   - `2026-04-09_1517_strategy-review.md`
6. 本轮用于 fresh intake 排班的最新候选证据
   - `research/quant_digests/2026-04-09_0144_kimchi-premium-hedged-handoff-shell.md`
   - `research/quant_digests/2026-04-09_0041_hyperliquid-xs-funding-carry-persistence-alpha.md`
   - `research/quant_digests/2026-04-09_0116_factor-sleeve-momentum-xs-router-alpha.md`

## Rank / 前排合法性检查
- `Paper launch queue.current_target = none`，合法
- `Surviving candidate slot.current_target = Rank 366`，且已有正式 rank，合法
- `Active P2 slot.current_target = none`，合法
- 当前前排不存在达到 `keep_P1 / P2 / P3` 但无正式 rank 的对象，因此本轮无需补 rank
- 当前也不存在 desk review 已清楚表明“应直升 P3”但尚未升级的 `Active P2`

## 排班判断
按 policy 默认顺序：
`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0`

本轮扫描结果：
- `P3`：无待接线对象
- `P2`：无在场 `Active P2`
- `P1`：有且仅有 `Rank 366`，并且它的唯一 follow-up 问题清楚、杠杆高、不会和上一轮重复成低价值轴
- 因此前两项为空时，**第 1 个 cycle item 必须先给 `Rank 366` 的 survivor 收口**
- survivor 之后，fresh intake 再切到最近新的具体对象；优先级按最近新 repo/paper/alpha report 排为：
  1. `negative KRW premium accumulation × positive-premium handoff exit`
  2. `trailing-24h funding rank × next-4h/24h funding persistence`
  3. `winning factor sleeve × next-window continuation`

## 为什么本轮不需要 bot2 兜底升 P3
policy 只要求 bot2 在 desk review 已清楚看到某个**在场 `Active P2`** 已达到 paper trade / paper launch 门槛，而 bot3 尚未升级时，直接把对象推进到 `P3 / Paper launch queue` 或 handoff。

本轮不满足该条件：
- `Active P2 = none`
- 当前前排唯一需要收口的是 `Rank 366` 的 P1 survivor
- 最近进入 `P3` 的对象已经在 `connected_runner_live`

因此，本轮不存在需要 bot2 兜底强推到 `P3` 的对象。

## Runtime writeback
本轮已重写 `docs/BOT2_BOT3_STATE.md`，且只做 runtime 层改写：
- 将 `Fresh intake slot.status` 改为 `pending`
- 将 `Fresh intake slot.current_target / source_record` 切到 `research/quant_digests/2026-04-09_0144_kimchi-premium-hedged-handoff-shell.md`
- 将 `Fresh intake slot.latest_result` 改写为：`Rank 366` 已完成首判并转入 survivor；当前 fresh intake 正式切到最近新的 alpha reports
- 保留 `Rank 366` 的 survivor 身份与唯一 follow-up 预算，不让新的 `keep_P1` 候选覆盖 survivor 槽位
- 重写 `cycle_plan` 为 4 条具体 pending 动作，顺序为：
  1. `Rank 366` survivor follow-up
  2. `negative KRW premium accumulation × positive-premium handoff exit`
  3. `trailing-24h funding rank × next-4h/24h funding persistence`
  4. `winning factor sleeve × next-window continuation`
- 所有新项均按要求写成 `target / action / success_criterion / result / status`，且 `result = none`、`status = pending`
- 不改 policy / brief / operating card / auto loop / cron prompt
- 不 reopen background pool
- 不新增 rank

## 一句话总结
这轮没有待接线 `P3`、没有 `Active P2`，但有一个合法且值得执行的 survivor：`Rank 366`。所以当前轮次必须先用唯一一次 follow-up 去收口它的 causal turning-point honesty 问题；只有在它被诚实排进前部后，fresh intake 才切到最近新的 alpha reports，并以韩盘负溢价对冲回归、Hyperliquid 横截面 funding carry、factor-sleeve momentum 这三条具体对象填满剩余预算。