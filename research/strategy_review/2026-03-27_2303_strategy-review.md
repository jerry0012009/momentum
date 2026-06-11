# Strategy Review (bot2)

Time: 2026-03-27 23:03 UTC

## 本轮一句话判断
`Paper launch queue` 为空；本轮 fresh intake 是 `Rank 204`；上一条 fresh intake `Rank 203` 值得且必须拿到那唯一一次 survivor follow-up；当前不存在明确 `Active P2`。同时，当前 state 出现了一处必须纠正的 policy 冲突：`Rank 203` 首判 `keep_P1` 后，不该被 `Rank 204` 覆盖 survivor 槽位，因此本轮已把 survivor runtime truth 改回 `Rank 203`，再按默认顺序重写 `cycle_plan`。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git status --short --branch`
  - 结论：仓内仍有大量未跟踪 artifact / 页面 / 临时文件，但这些只能作为运行证据，不构成反向改 policy 或自动把旧 background 候选拉回前排的理由。
- 最近 `research/optimization_loop/`：
  - `2026-03-27_2254_rank204_liquidity_provision_xs_short_reversal_intake_keep_p1.md`
  - `2026-03-27_2233_rank203_graph_matching_pairbook_intake_keep_p1.md`
  - `2026-03-27_2224_rank202_survivor_followup_drop_background.md`
  - `2026-03-27_2216_rank201_p3_launch_wiring_connected_runner_live.md`
  - `2026-03-27_2158_rank201_p2_admission_promote_p3.md`
  - `2026-03-27_2135_rank200_paper_runner_wiring_complete.md`
- 最近 `research/strategy_review/`：
  - `2026-03-27_2206_strategy-review.md`
  - `2026-03-27_2127_strategy-review.md`
  - `2026-03-27_2046_strategy-review.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排
- 未把 `docs/TODO.md` 当成本轮排班依据
- 已检查前排 rank：`Rank 200 / 201 / 203 / 204` 均已有正式整数 rank，无需补号

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**否，当前为空。**
理由很直接：
- `Rank 200` 已在 `2026-03-27_2135_rank200_paper_runner_wiring_complete.md` 完成最小 launch wiring；
- `Rank 201` 已在 `2026-03-27_2216_rank201_p3_launch_wiring_connected_runner_live.md` 完成最小 launch wiring；
- 当前 queue-side 没有仍等待 `runner + scheduler + first verified run` 的头部对象。

### Q2. 本轮 `fresh intake` 是什么？
**本轮 fresh intake 是 `Rank 204 / liquidity-provision cross-sectional short-reversal`。**
依据：
- 最新完成的首轮 intake 记录是 `2026-03-27_2254_rank204_liquidity_provision_xs_short_reversal_intake_keep_p1.md`；
- 它已拿到正式整数 `Rank 204`，且首判为 `keep_P1`；
- 因此 current fresh intake 应写作 `Rank 204`，而不是更早的 `Rank 203`。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得，而且按 policy 现在必须由它占用 survivor 槽位。**
上一条 fresh intake 是 `Rank 203 / graph-matching pairbook mean-reversion`：
- 它在 `2026-03-27_2233_rank203_graph_matching_pairbook_intake_keep_p1.md` 中的正式 verdict 是 `keep_P1`；
- 该 verdict 留下的唯一高杠杆问题并不模糊：在更强 pair admission 与更长持有期上，matching / capped-overlap 的去集中度优势能否真正转成净 alpha 优势；
- 这正符合 policy 里“上一条 fresh intake 拿到 `keep_P1` 后，默认享有唯一 survivor follow-up 锁”的定义。

所以本轮不能把 survivor 写成 `Rank 204`；那会违反：
> `Surviving candidate` 只能是上一条 fresh intake；任何 `fresh intake` 一旦首判 `keep_P1`，其唯一 follow-up 在诚实收口前默认享有前排锁定权。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**当前不存在明确 `Active P2`。**
原因：
- `Rank 201` 的 `P2` admission 已经正式收口为 `promote_P3`，随后又已完成 launch wiring；
- `Rank 203` 仍是 survivor，不是 `P2`；
- `Rank 204` 刚完成 fresh intake，也还不是 `P2`。

因此当前唯一诚实写法仍是：
- `Active P2 slot = none`
- 不存在需要 bot2 立刻兜底推进到 `P3 / P1 / P0` 的在架 `P2` 对象。

## 3) 本轮必须纠正的 runtime truth
本轮发现 state 有一处实质性 policy 冲突：
- `Rank 203` 在 22:33 UTC 首轮 intake 后已经是 `keep_P1`；
- `Rank 204` 在 22:54 UTC 完成新的 fresh intake；
- 按 policy，**一旦 `Rank 204` 成为“当前 fresh intake”，那么 survivor 槽位就必须回指“上一条 fresh intake = Rank 203”**；
- 现有 state 却把 `Surviving candidate slot` 写成了 `Rank 204`，等于让新的 `keep_P1` 覆盖了旧的 survivor 锁。

这不是小措辞问题，而是前排排班 truth 被写歪了。

因此本轮已把 `BOT2_BOT3_STATE.md` 改回：
- `Fresh intake slot = Rank 204`
- `Surviving candidate slot = Rank 203`
- `followup_budget_remaining = 1`

## 4) 前排 rank 合规检查
- `Paper launch queue`: none
- `Fresh intake slot`: `Rank 204`，已有正式 rank
- `Surviving candidate slot`: `Rank 203`，已有正式 rank
- `Active P2 slot`: none

结论：
- 当前不存在“前排对象已达 `keep_P1 / P2 / P3` 但仍无正式 rank”的违规情况；
- 本轮无需补新的整数 `Rank`；
- 需要纠正的是 survivor 归属，而不是 rank 编号。

## 5) 基于 policy 的当前轮排班重写
按默认顺序扫描当前所有合法动作：

1. **`P3 / Paper launch queue`：无真实可执行动作**
   `Rank 200 / 201` 都已是 `connected_runner_live`，当前 queue 为空。

2. **`P2 / Active P2`：无真实可执行动作**
   当前没有明确 `Active P2`。

3. **`P1 / Surviving candidate`：有，而且这是当前最高优先级动作**
   `Rank 203` 作为上一条 fresh intake 的合法 survivor，必须先用掉那唯一一次 decisive follow-up。

4. **`fresh intake`：只能排在 survivor 之后**
   因为当前确实存在合法 `Surviving candidate` 动作，所以任何新的 intake 都不得排到它前面；但可以在 survivor 已被诚实排到本轮第 1 位后，用剩余预算继续补具体 intake 对象。

据此，本轮 `cycle_plan` 重写为：
1. `Rank 203 / graph-matching pairbook mean-reversion`
   - survivor 唯一 follow-up
   - 围绕 `ADF + half-life + liquidity` gate、`full matching vs capped-overlap hybrid`、`1h/4h/8h` 持有期
   - 直接回答 `promote_P2` 还是 `drop_to_background`
2. `research/quant_digests/2026-03-27_1424_par-local-drift-crossover-alpha.md`
   - 具体 fresh intake
3. `research/quant_digests/2026-03-27_1352_cttrend-xs-technical-composite-alpha.md`
   - 具体 fresh intake
4. `research/quant_digests/2026-03-27_1244_dynamic-tsmom-turningpoint-continuation-alpha.md`
   - 具体补位 fresh intake

这样排的原因：
- 完全遵守 `P3 > P2 > survivor > fresh intake > P0` 的 authoritative 顺序；
- 不让新的 `keep_P1` 覆盖 `Rank 203` 的 survivor 锁；
- 切回 intake 时，给的是具体对象，不是空模板句；
- 也没有把任何 background pool 旧对象重新拉回前排。

## 6) bot2 兜底裁判结论
本轮**不存在**需要 bot2 直接兜底塞进 `P3 / Paper launch queue` 的 `Active P2`：
- `Rank 201` 之前那个需要兜底的点，已经被 bot3 自己做完了：先 `promote_P3`，再 `connected_runner_live`；
- 当前前排真正需要 bot2 做的是把 survivor 归属纠正回来，避免 `Rank 203` 被 `Rank 204` 非法覆盖。

所以这轮 bot2 的关键职责不是再强推新的 `P3`，而是：
> **恢复 policy 允许的前排链条顺序：`Rank 203 survivor follow-up` 在前，新的 intake 在后。**

## 7) 对 state 的实际写回
本轮已更新 `docs/BOT2_BOT3_STATE.md`：
- 保持 `Paper launch queue = none`
- 保持 `Active P2 slot = none`
- 保持 `Fresh intake slot = Rank 204`
- 将 `Surviving candidate slot` 从错误的 `Rank 204` 纠正为 `Rank 203`
- 重写 `cycle_plan` 为：
  1. `Rank 203` survivor 唯一 follow-up
  2. `par-local-drift crossover` fresh intake
  3. `CTTrend XS technical composite` fresh intake
  4. `dynamic TSMOM turning-point continuation` fresh intake

所有新排项均满足：
- 只写 `target / action / success_criterion / result / status`
- 新生成项 `result = none`
- 新生成项 `status = pending`

## 8) 一句话结论
这轮真正要修的不是研究结论，而是 runtime truth：**`Rank 204` 现在是 fresh intake，但 survivor 只能是上一条 fresh intake `Rank 203`。先把 `Rank 203` 的唯一 follow-up 诚实收口，再继续新的 intake，才符合 policy。**
