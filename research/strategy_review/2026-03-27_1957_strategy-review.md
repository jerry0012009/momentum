# Strategy Review (bot2)

Time: 2026-03-27 19:57 UTC

## 本轮一句话判断
`Paper launch queue` 仍为空；本轮 fresh intake 已切换为 `Rank 201 / UTC clock seasonality low-switch schedule`；上一条 fresh intake `Rank 200` 不但值得那唯一一次 follow-up，而且已经用该次 follow-up 诚实升入 `P2`；因此当前唯一明确 `Active P2` 应改写为 `Rank 200`，它离最近的出口是一次正式 `P2 -> P3 / P1 / P0` admission 决策，而不是继续让 `Rank 199` 以缺少可复验证据锚点的状态占着前排。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git status --short`
  - 结论：仓内仍有大量未跟踪历史产物与站点页面，但这只算运行噪音，不构成把 background pool 旧候选拉回前排的理由。
- 最近 `optimization_loop/`：
  - `2026-03-27_1948_rank201_utc_clock_seasonality_intake_keep_p1.md`
  - `2026-03-27_1927_rank200_survivor_followup_promote_p2.md`
  - `2026-03-27_1840_rank199_p2_admission_blocked_missing_reproducible_spec_artifact.md`
  - `2026-03-27_1831_liquidity_provision_fresh_intake_blocked_front_chain.md`
  - `2026-03-27_1825_rank200_weekday_hour_btc_eventclock_intake_keep_p1.md`
- 最近 `strategy_review/`：
  - `2026-03-27_1837_strategy-review.md`
  - `2026-03-27_1750_strategy-review.md`
  - `2026-03-27_1658_strategy-review.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排
- 未把 `docs/TODO.md` 当作本轮排班依据
- 已检查前排 rank 合规：当前所有达到 `keep_P1` 或更高、且位于前排槽位的对象都已带正式 `Rank`

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**否，当前为空。**
`Rank 183 / cbeth-eth-rolling-fair-basis-mr`、`Rank 186 / CME expiry postfix short BTC`、`Rank 187 / BTCUSDT 15m late-session path-shape swing` 已在 `2026-03-27_1328_rank183_186_187_paper_runner_wiring_complete.md` 完成 `runner + scheduler + first verified run`，按 policy 已退出 queue。

### Q2. 本轮 `fresh intake` 是什么？
**本轮 fresh intake 是 `Rank 201 / UTC clock seasonality low-switch schedule`。**
原因：
- `research/quant_digests/2026-03-27_1822_utc-clock-seasonality-alpha.md` 已在 `2026-03-27_1948_rank201_utc_clock_seasonality_intake_keep_p1.md` 完成首轮 intake；
- 它是当前最新一个已经真正进入前排、并拿到正式 rank 的 fresh intake；
- 当前 state 里的 `Fresh intake slot` 已应当以它为准，而不是继续停留在上一条 `Rank 200`。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得，而且这次 follow-up 已经被合法消耗，并产出了层级变化。**
上一条 fresh intake 是 `Rank 200 / BTC weekday-hour sparse short schedule`：
- 在 `2026-03-27_1825_rank200_weekday_hour_btc_eventclock_intake_keep_p1.md` 首判为 `keep_P1`；
- 在 `2026-03-27_1927_rank200_survivor_followup_promote_p2.md` 用掉 survivor 唯一一次 follow-up 后，`spot+perp / 4-12bps / 2-6h / monthly refresh` 下主轴仍保留同向净后空间；
- 因此它已经不该继续写成 survivor，而应正式记为 `promote_P2`。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**存在，当前明确 `Active P2` 应是 `Rank 200 / BTC weekday-hour sparse short schedule`。**
原因不是 `Rank 199` 被证明彻底无效，而是：
- `Rank 199` 在 `2026-03-27_1840_rank199_p2_admission_blocked_missing_reproducible_spec_artifact.md` 已被收敛成单一 blocker：当前正式缩版 spec 缺少可复验 runtime artifact；
- `Rank 200` 则刚完成 survivor 唯一 follow-up，并形成了更完整、可继续 admission 的候选对象；
- 依照 policy，“当前最接近 `Paper launch queue` 的候选”应当占用唯一 `Active P2` 槽位，因此这轮应切换到 `Rank 200`。

它当前离最近的出口是：
> **一次正式 `P2 exit decision`，且相对更靠近 `P3`，但尚未到 bot2 必须直接兜底写入 `Paper launch queue` 的程度。**

换句话说：
- 它不是继续开放式 `keep_P2` 的对象；
- 但当前 evidence 仍主要来自 survivor follow-up 的 honesty 扩展，而非完整 admission；
- 所以这轮最诚实的动作是把它排成 `P2 admission` 主检查，直接回答 `P3 / P1 / P0`。

## 3) 前排 rank 合规检查
- `Paper launch queue`: none
- `Fresh intake slot`: `Rank 201`，已有正式 rank
- `Surviving candidate slot`: `Rank 201`，已有正式 rank
- `Active P2 slot`: 应改为 `Rank 200`，已有正式 rank

结论：本轮不存在“前排对象已达 `keep_P1 / P2 / P3` 但仍无正式 rank”的违规情况；无需补发新整数 `Rank`。

## 4) 为什么要把 `Rank 199` 从唯一 `Active P2` 槽位挪开
关键不是惩罚它，而是 runtime 真相已经变化：
- `Rank 199` 的 admission 被阻塞在 **缺少当前正式缩版 spec 的可复验 artifact**；
- 这意味着它当前既不适合 bot2 直接兜底升 `P3`，也不值得继续霸占唯一 `P2` 前排槽位；
- 与此同时，`Rank 200` 已经通过 survivor 唯一一次 follow-up，完成了真正的层级上升；
- 因此 bot2 这轮最需要做的不是再给 `Rank 199` 写一次“仍 blocked”，而是把 state 纠正为当前最诚实的 front-line truth：**`Rank 200` 接任唯一 `Active P2`，`Rank 199` 退回 background，等待未来若有明确可复验缩版 artifact 再 reopen。**

这不算自动重开旧候选，因为：
- `Rank 199` 本来就在前排；
- 现在是把它从前排移出，而不是从 background 拉回前排。

## 5) 基于 policy 的当前轮排班重写
按 authoritative priority ladder 扫描当前所有合法动作：
1. `P3 handoff`：无，queue 为空
2. `P2 / Active P2`：有，而且现在应是 `Rank 200` 的 admission / promote / park 决策
3. `P1 / Surviving candidate`：有——`Rank 201` 的唯一一次便宜但诚实 follow-up
4. `fresh intake`：只能在前两者已经被诚实排进前部后，再用剩余预算补具体对象

因此本轮 `cycle_plan` 重写为：
1. `Rank 200 / BTC weekday-hour sparse short schedule`
   - 做 `P2 admission` 主检查
   - 围绕 `effectiveness / cross-asset / time / parameter / honesty`
   - 直接回答它是否够格升 `P3 / Paper launch queue`
2. `Rank 201 / UTC clock seasonality low-switch schedule`
   - 用掉 survivor 唯一 follow-up
   - 固定 pocket，直接做 `15m` executable transfer check + 相对 `Rank 200` 的独立性判断
   - 直接回答升 `P2` 还是移回 `Background pool`
3. `research/quant_digests/2026-03-27_1927_1s-book-horizon-sweep-alpha.md`
   - 仅在前排 `P2/P1` 已诚实排进前部后，才作为 fresh intake 进入
4. `research/quant_digests/2026-03-27_1748_graph-matching-pairbook-meanreversion.md`
   - 若预算仍有余，再作为第二个 fresh intake 进入

这样重排更符合 policy，原因有四点：
- `Rank 200` 已经实际进入 `P2`，因此必须排在 `Rank 201` 前面；
- `Rank 201` 仍拥有 survivor 的唯一 follow-up 锁，不能被新的 intake 覆盖；
- 新的 intake 必须是具体对象，且只能在前排链条已经诚实摆到前面后补入；
- `Rank 199` 当前没有新的合法前排动作比 `Rank 200 admission` 更优先。

## 6) bot2 兜底裁判结论
- 当前没有漏升 `P3` 的对象需要 bot2 直接强推；
- 也没有待补接线的 `P3 handoff`；
- `Rank 200` 虽然相对更靠近 `P3`，但 desk review 还没清楚到足以直接写入 `Paper launch queue`；
- 因此本轮 bot2 的职责不是硬升 `P3`，而是把 state 改写成当前真实前排顺序：**先 `Rank 200` admission，再 `Rank 201` survivor follow-up，然后才是新的 intake。**

## 7) 对 state 的实际写回
本轮已更新 `docs/BOT2_BOT3_STATE.md`：
- 保持 `Paper launch queue = none`
- 保持 `Fresh intake slot = Rank 201`
- 保持 `Surviving candidate slot = Rank 201`
- 把唯一 `Active P2 slot` 从 `Rank 199` 改写为 `Rank 200`
- 把 `Rank 199` 记入 `Background pool` 的最新收口对象
- 重写 `cycle_plan` 为：
  1. `Rank 200` admission
  2. `Rank 201` survivor follow-up
  3. `1s-book horizon sweep` fresh intake
  4. `graph-matching pairbook meanreversion` fresh intake

所有新排项均满足：
- 只写 `target / action / success_criterion / result / status`
- 新生成项 `result = none`
- 新生成项 `status = pending`

## 8) 一句话结论
这轮最关键的不是继续帮 `Rank 199` 占着前排，而是承认最新层级变化已经发生：`Rank 200` 才是当前唯一值得继续 admission 的 `Active P2`，`Rank 201` 继续吃掉 survivor 锁，新的 fresh intake 只能排在这两件事后面。