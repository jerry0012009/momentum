# Strategy Review (bot2)

Time: 2026-03-27 21:27 UTC

## 本轮一句话判断
`Paper launch queue` 仍然非空，头部仍是 `Rank 200`；本轮 fresh intake 仍是 `Rank 202`；上一条 fresh intake `Rank 201` 的唯一 follow-up 已经证明它值得进入 `Active P2`；当前明确存在 `Active P2 = Rank 201`，而它离最近出口更偏向 `P3`，但这轮还没到需要 bot2 直接越权把它塞进 queue 的程度，所以本轮排班仍应先做 `Rank 200` 的 `P3 wiring`，再做 `Rank 201` 的出口决策，再收口 `Rank 202`，最后才保留 conditional fresh intake。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git status --short`
  - 结论：仓内仍有大量未跟踪 artifact / site 页面 / 临时文件，但这些只能算运行噪音和证据池，不能据此把 background pool 老对象重新拉回前排。
- 最近 `research/optimization_loop/`：
  - `2026-03-27_2033_graph_matching_intake_blocked_by_rank202_survivor_lock.md`
  - `2026-03-27_2028_rank202_1s_book_horizon_sweep_intake_keep_p1.md`
  - `2026-03-27_2015_rank201_survivor_followup_promote_p2.md`
  - `2026-03-27_2002_rank200_p2_admission_promote_p3.md`
  - `2026-03-27_1948_rank201_utc_clock_seasonality_intake_keep_p1.md`
- 最近 `research/strategy_review/`：
  - `2026-03-27_2046_strategy-review.md`
  - `2026-03-27_1957_strategy-review.md`
  - `2026-03-27_1837_strategy-review.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排
- 未把 `docs/TODO.md` 当成本轮排班依据
- 已检查前排对象 rank：`Rank 200 / 201 / 202` 均已有正式整数 rank，无需补号

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**是，非空。**
当前 queue 头部仍是 `Rank 200 / BTC weekday-hour sparse short schedule`。
而且它不是“还要再研究一下”的 `P2`，而是已经在 `2026-03-27_2002_rank200_p2_admission_promote_p3.md` 中被正式判定为足够值得进入 paper trade 的对象；按 policy，这轮默认动作仍应是 `P3 handoff / launch wiring`，直到补齐 dedicated runner、scheduler 与首跑验证。

### Q2. 本轮 `fresh intake` 是什么？
**本轮 fresh intake 仍是 `Rank 202 / 1s book horizon sweep microstructure drift`。**
依据：
- `2026-03-27_2028_rank202_1s_book_horizon_sweep_intake_keep_p1.md` 是当前最新一条真正完成首轮 intake 并获得正式 rank 的前排新对象；
- 它首判为 `keep_P1`，因此当前 survivor 槽位也必须继续由它锁定。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得，而且那唯一一次 follow-up 已经被合法消耗，并形成了层级变化。**
上一条 fresh intake 是 `Rank 201 / UTC clock seasonality low-switch schedule`：
- 在 `2026-03-27_1948_rank201_utc_clock_seasonality_intake_keep_p1.md` 首判为 `keep_P1`；
- 在 `2026-03-27_2015_rank201_survivor_followup_promote_p2.md` 中，唯一一次 follow-up 已证明 `20~21 UTC long / 22~23 UTC short` 在 8 币 perp `15m` 真执行口径下成本后仍为正；
- 因此它已经不该继续停在 survivor，而应正式作为当前唯一 `Active P2`。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**存在，当前明确 `Active P2` 是 `Rank 201 / UTC clock seasonality low-switch schedule`。**
它当前最近的出口判断是：
> **更偏向 `P3`，但还需要 bot3 按 admission 五项把这轮正式收口成 `promote_P3 / one-time P2->P1 re-scope / drop_to_background` 三选一。**

原因：
- `Rank 201` 已经跨过 survivor 阶段最关键的一步：`15m` executable transfer 仍存活；
- 但 desk review 目前还没清楚到必须由 bot2 直接兜底把它越过 bot3 塞进 queue；
- 所以本轮最诚实动作仍是：让它进入一次真正的 `P2 exit decision`，而不是继续开放式 `keep_P2`。

## 3) 前排 rank 合规检查
- `Paper launch queue`: `Rank 200`，已有正式 rank
- `Fresh intake slot`: `Rank 202`，已有正式 rank
- `Surviving candidate slot`: `Rank 202`，已有正式 rank
- `Active P2 slot`: `Rank 201`，已有正式 rank

结论：本轮不存在“前排对象已达 `keep_P1 / P2 / P3` 但仍无正式 rank”的违规情况；无需补下一个未使用整数 `Rank`。

## 4) bot2 兜底裁判判断
这轮 **不需要** bot2 再额外兜底强推新的 `P2 -> P3`：
- `Rank 200` 已经在上一轮被正式升入 `P3 / Paper launch queue`，所以这轮 bot2 的责任是承认 queue 非空，并继续把默认动作锁到 `P3 wiring`；
- `Rank 201` 虽然离 `P3` 更近，但 desk review 目前仍更适合把它排成一次 admission 出口决策，而不是由 bot2 直接越过 bot3 写进 queue。

## 5) 对最新 bot3 结果的解释
`2026-03-27_2033_graph_matching_intake_blocked_by_rank202_survivor_lock.md` 的含义很清楚：
- 这不是新鲜发现推翻了当前排班；
- 恰恰相反，它证明 policy 正在正常工作：`Rank 202` 作为当前唯一 survivor 还没用掉那次 follow-up 之前，新的 graph-matching intake 不能越过前排链条。

因此，本轮 `cycle_plan` 不该改成新的 intake 优先，而应把第 4 项明确保持为 **conditional fresh intake**：
只有当前三个前排动作都已诚实排入并等待 bot3 依次执行后，graph-matching 才有资格再被 intake。

## 6) 本轮 cycle_plan 重写原则
按 authoritative priority ladder 扫描后，当前所有合法且值得做的动作顺序仍是：
1. **`Rank 200`：P3 / Paper launch queue` 头部对象，先做最小 `launch wiring`**
2. **`Rank 201`：当前唯一 `Active P2`，做 admission 出口决策**
3. **`Rank 202`：当前 survivor，必须用掉那唯一一次 follow-up 并正式收口**
4. **graph-matching pairbook meanreversion：只保留 conditional fresh intake，不得越过前三项**

这满足 policy 的关键要求：
- 现有前排对象的收口优先级永远高于新的发现；
- survivor 锁定未解除前，不得让新的 `keep_P1` 候选覆盖 survivor 槽位；
- fresh intake 只能在前排链条已诚实排入后，作为剩余预算补位。

## 7) 对 state 的实际写回
本轮已更新 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan` 第 4 项，使其更明确地写成 conditional intake：
- 只有当 `Rank 200`、`Rank 201`、`Rank 202` 三条前排动作已按顺序诚实排入并等待 bot3 依次执行后，才允许对 graph-matching 开 fresh intake；
- 若再次被 `Rank 202` survivor 锁定拦下，则维持 conditional intake，而不是越权开新 fresh slot；
- 所有新排项继续保持 `result = none`、`status = pending`。

除这处写回外，本轮未改变任何 front-line 槽位归属：
- `Paper launch queue = Rank 200`
- `Active P2 = Rank 201`
- `Surviving candidate = Rank 202`
- `Fresh intake = Rank 202`

## 8) 一句话结论
这轮真正需要 bot3 做的事情没有变：**先把 `Rank 200` 从 queue 文档态推进到真实 `paper launch wiring`，再让 `Rank 201` 做 `P2` 出口决策，再用掉 `Rank 202` 的 survivor 唯一 follow-up；graph-matching 只能作为诚实补位的 conditional fresh intake，不能越过当前前排链条。**
