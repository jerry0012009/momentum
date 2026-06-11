# Strategy Review (bot2)

Time: 2026-03-27 20:46 UTC

## 本轮一句话判断
`Paper launch queue` 非空，头部是 `Rank 200`；本轮 fresh intake 是 `Rank 202`；上一条 fresh intake `Rank 201` 值得且已经拿到了那唯一一次 follow-up，并已合法升入 `Active P2`；因此当前最需要 bot3 先做的不是再开新研究，而是先把 `Rank 200` 推进 `P3 handoff / launch wiring`，再对 `Rank 201` 做出口决策，再收口 `Rank 202` 的 survivor follow-up。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git status --short`
  - 结论：仓内仍有大量未跟踪 artifact / site 页面 / 历史文件，但这些只是运行噪音，不构成自动 reopen background pool 的理由。
- 最近 `optimization_loop/`：
  - `2026-03-27_2033_graph_matching_intake_blocked_by_rank202_survivor_lock.md`
  - `2026-03-27_2028_rank202_1s_book_horizon_sweep_intake_keep_p1.md`
  - `2026-03-27_2015_rank201_survivor_followup_promote_p2.md`
  - `2026-03-27_2002_rank200_p2_admission_promote_p3.md`
  - `2026-03-27_1948_rank201_utc_clock_seasonality_intake_keep_p1.md`
- 最近 `strategy_review/`：
  - `2026-03-27_1957_strategy-review.md`
  - `2026-03-27_1837_strategy-review.md`
  - `2026-03-27_1750_strategy-review.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排
- 未把 `docs/TODO.md` 当作本轮排班依据
- 已检查前排 rank：当前 `Rank 200 / 201 / 202` 均已有正式整数 rank，无需补号

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**是，非空。**
当前 queue 头部就是 `Rank 200 / BTC weekday-hour sparse short schedule`。
而且它不是“可有可无的 queued 文档态”，而是已经被明确判定为足够值得进入 paper trade 的对象；按 policy，这轮默认动作应切到 `P3 handoff / launch wiring`，直到补齐 `runner + scheduler + first verified run`。

### Q2. 本轮 `fresh intake` 是什么？
**本轮 fresh intake 是 `Rank 202 / 1s book horizon sweep microstructure drift`。**
依据：
- `2026-03-27_2028_rank202_1s_book_horizon_sweep_intake_keep_p1.md` 已完成首轮 intake；
- 它是当前最新一条真正进入前排、并拿到正式 rank 的 fresh intake；
- 因为首判为 `keep_P1`，所以现在 survivor 槽位也应由它锁定。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得，而且已经被合法消耗并形成层级变化。**
上一条 fresh intake 是 `Rank 201 / UTC clock seasonality low-switch schedule`：
- 在 `2026-03-27_1948_rank201_utc_clock_seasonality_intake_keep_p1.md` 首判为 `keep_P1`；
- 在 `2026-03-27_2015_rank201_survivor_followup_promote_p2.md` 用掉 survivor 唯一一次 follow-up 后，`20~21 UTC long / 22~23 UTC short` 在 8 币 perp `15m` 真执行口径下成本后仍为正；
- 同时它相对 `Rank 200` 不是同一 pocket 的换壳，而是同属时钟家族的另一条独立母线；
- 因此它已经不该继续停在 survivor，而应正式进入 `Active P2`。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**存在，当前明确 `Active P2` 是 `Rank 201 / UTC clock seasonality low-switch schedule`。**
它当前离最近的出口是：
> **`P3 / P1 / P0` 三选一的 admission 出口决策，其中相对更靠近 `P3`，但还没到 bot2 必须直接兜底升 queue 的程度。**

原因：
- `Rank 201` 的 survivor follow-up 已经证明最关键的一层：`15m` 可执行 transfer 仍存活；
- 但它还没有像 `Rank 200` 那样完成更完整的 admission 收口；
- 所以这轮最诚实的动作，是围绕 `effectiveness / cross-asset / time / parameter / honesty` 给它一次正式 `P2 exit decision`，而不是继续拖成开放式 `keep_P2`。

## 3) 前排 rank 合规检查
- `Paper launch queue`: `Rank 200`，已有正式 rank
- `Fresh intake slot`: `Rank 202`，已有正式 rank
- `Surviving candidate slot`: `Rank 202`，已有正式 rank
- `Active P2 slot`: `Rank 201`，已有正式 rank

结论：本轮不存在“前排对象已达 `keep_P1 / P2 / P3` 但仍无正式 rank”的违规情况；无需补下一个整数 `Rank`。

## 4) bot2 兜底裁判判断
这轮不需要 bot2 再去兜底强推新的 `P2 -> P3`：
- `Rank 200` 已经在上一轮被明确升入 `P3 / Paper launch queue`；
- 现在 bot2 的责任是承认 queue 非空，并把默认动作改成 `P3 handoff / launch wiring`；
- `Rank 201` 虽然看起来更靠近 `P3`，但 desk review 还没有清楚到必须由 bot2 越过 bot3 直接把它也塞进 queue 的程度。

## 5) 本轮 cycle_plan 为什么要这样重写
按 authoritative priority ladder 扫描：
1. **`P3 handoff`：有，而且必须放第一。**
   `Rank 200` 已在 queue 中，但还停在 `queued_handoff_ready` 语义，没有看到 `runner + scheduler + first run` 完成记录，因此当前最优先动作就是接线，而不是继续研究。
2. **`P2 / Active P2`：有。**
   `Rank 201` 是当前唯一明确 active P2，应直接安排 admission 出口决策。
3. **`P1 / Surviving candidate`：有。**
   `Rank 202` 作为上一条 fresh intake 的唯一 survivor follow-up，默认享有前排锁定权；它必须在新的 intake 之前收口。
4. **`fresh intake`：只能排在前三者之后。**
   当前最具体、合法的 intake 目标仍是 `research/quant_digests/2026-03-27_1748_graph-matching-pairbook-meanreversion.md`，但只能作为第 4 项补位，不能越过前排对象。

## 6) 对 state 的实际写回
本轮已更新 `docs/BOT2_BOT3_STATE.md`：
- 保持 `Paper launch queue.current_target = Rank 200`
- 明确 queue 非空，且 `Rank 200` 当前应继续做 `P3 handoff / launch wiring`
- 保持 `Fresh intake slot = Rank 202`
- 保持 `Surviving candidate slot = Rank 202`
- 保持 `Active P2 slot = Rank 201`
- 重写 `cycle_plan` 为：
  1. `Rank 200`：P3 launch wiring
  2. `Rank 201`：P2 admission 出口决策
  3. `Rank 202`：survivor 唯一 follow-up
  4. `graph-matching pairbook meanreversion`：conditional fresh intake

所有新排项均满足：
- 只写 `target / action / success_criterion / result / status`
- 新生成项 `result = none`
- 新生成项 `status = pending`

## 7) 一句话结论
这轮真正需要 bot3 做的顺序已经很清楚：**先把 `Rank 200` 从 queue 文档态推到真实 paper wiring，再让 `Rank 201` 做 admission 出口决策，然后用掉 `Rank 202` 的 survivor 唯一 follow-up；只有这些都诚实排在前面后，才轮到新的 graph-matching intake。**
