# Strategy Review (bot2)

Time: 2026-03-28 03:58 UTC

## 本轮一句话判断
`Paper launch queue` 为空；本轮新的 `fresh intake` 应切到 `research/quant_digests/2026-03-27_0523_same-venue-options-vertical-noarb-alpha.md`；上一条 fresh intake `Rank 211 / CME BTC futures sign classifier` 值得且必须占住那唯一一次 survivor follow-up；当前不存在明确 `Active P2`，因此它离 `P3 / P1 / P0` 都不适用，最近已收口的前排出口仍是 `Rank 203` 已正式落在 `P1 re-scope`。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short`
  - 结论：仓内仍有大量未跟踪页面/脚本/artifact；这些只算最近运行 evidence，不得反向改 policy，也不得把 background pool 旧候选自动拉回前排。
- 最近 `research/optimization_loop/`：
  - `2026-03-28_0356_rank211_cme_btcfutures_sign_classifier_intake_keep_p1.md`
  - `2026-03-28_0321_okx_positive_funding_positive_premium_intake_drop_to_background.md`
  - `2026-03-28_0319_rank210_predicted_funding_sign_carry_intake_keep_p1.md`
  - `2026-03-28_0303_rank209_survivor_followup_drop_to_background.md`
- 最近 `research/strategy_review/`：
  - `2026-03-28_0310_strategy-review.md`
  - `2026-03-28_0157_strategy-review.md`
  - `2026-03-28_0117_strategy-review.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排
- 未把 `docs/TODO.md` 当成本轮排班依据
- 当前前排对象 rank 合规；本轮无需补新的整数 `Rank`

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**否，当前为空。**
原因：
- `Rank 200 / BTC weekday-hour sparse short schedule` 与 `Rank 201 / UTC clock seasonality low-switch schedule` 都已是 `connected_runner_live`；
- 当前 queue-side 没有等待接线的头部对象；
- 因此本轮没有 `P3 / launch wiring` 动作可排在最前。

### Q2. 本轮 `fresh intake` 是什么？
**本轮 `fresh intake` 应切到 `research/quant_digests/2026-03-27_0523_same-venue-options-vertical-noarb-alpha.md`。**
原因：
- `research/quant_digests/2026-03-27_0904_cme-btcfutures-sign-classifier-alpha.md` 已在 `2026-03-28_0356_rank211_cme_btcfutures_sign_classifier_intake_keep_p1.md` 完成首判并拿到 `Rank 211`；
- 按 fixed policy，最新一条 fresh intake 一旦首判为 `keep_P1`，其唯一 survivor follow-up 默认享有前排锁定权；
- 因此 fresh intake 槽位必须往下切到下一条尚未首判、且最近仍具体可做的新对象，首选就是前一轮未执行的 `0523 same-venue options vertical no-arb`。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得，而且现在必须由它占住 survivor 槽位。**
上一条 fresh intake 是 `Rank 211 / CME BTC futures sign classifier`：
- 它已正式拿到 `keep_P1`；
- 唯一高杠杆 follow-up 问题也很明确：不是继续看论文 headline accuracy，而是直接回答加入更细 `aggTrades/bookTicker` 风格 microstructure 特征后，高置信度 abstain classifier 能否把 net edge 拉过 realistic cost gate；
- 这正符合 policy 里 survivor 只能做一次便宜而 decisive 的 follow-up 的定义。

所以答案不是“可以做”，而是：**值得，而且在诚实收口前不能被另一条新的 `keep_P1` 候选覆盖。**

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**当前不存在明确 `Active P2`。**
- `Active P2 slot` 当前应保持 `none`；
- 最近已收口的 `Rank 203 / graph-matching pairbook mean-reversion` 已在 `2026-03-28_0005_rank203_p2_exit_rescope_to_p1.md` 正式写成 `P1 re-scope`，因此它不应再被当作当前 active P2；
- 既然当前 active P2 不存在，就不存在“更接近 `P3 / P1 / P0` 哪个出口”的当前对象；若只看最近一次出口判断，`Rank 203` 最近的是 `P1` 而非 `P3/P0`。

## 3) rank 合规检查
- `Paper launch queue`: none
- `Fresh intake slot`: `0523` 还未首判，因此不需要预先分配 rank
- `Surviving candidate slot`: `Rank 211`，已有正式 rank
- `Active P2 slot`: none

结论：
- 当前不存在“前排对象已达 `keep_P1 / P2 / P3` 却无 rank”的违规情况；
- 本轮无需补新的整数 `Rank`；
- 真正需要修正的是 survivor runtime truth：`Rank 210` 不能继续与 `Rank 211` 并存于前排。

## 4) 本轮排班判断
按 policy 默认顺序扫描：

1. **P3 / Paper launch queue**
   - 当前为空；无真实可执行动作。
2. **P2 / Active P2**
   - 当前为空；无 admission / promote / park 动作可排。
3. **P1 / Surviving candidate**
   - 有，而且必须排第一：`Rank 211` 的 survivor 唯一 follow-up 不应被新的 intake 覆盖。
4. **fresh intake**
   - 只有在 survivor 已被诚实排入首位后，剩余预算才回到具体新 intake：
     1. `2026-03-27_0523_same-venue-options-vertical-noarb-alpha.md`
     2. `2026-03-28_0334_crossvenue-funding-rotation-refresh-alpha.md`
     3. `2026-03-27_1927_1s-book-horizon-sweep-alpha.md`

这里刻意**不**把 `Rank 210` 继续保留在 survivor / active P2 / fresh intake 任一前排槽位：
- 因为 fixed policy 只允许一个 survivor，且它只能是上一条 fresh intake；
- `Rank 210` 不是最新一条 fresh intake；
- 在没有 human reopen 的情况下，它不能自动挤占 `Rank 211` 的 survivor 锁。

## 5) 是否需要 bot2 直接兜底推进到 P3？
**不需要。**
本轮没有处于 `Active P2` 且已明显够格升 `P3`、但 bot3 尚未升级的对象：
- `Active P2 slot` 为空；
- `Rank 211` 只是 survivor follow-up 阶段，离 `P3` 还远；
- `0523 / 0334 / 1927` 都还只是 fresh intake 候选。

因此，这轮 bot2 的职责不是强推 `P3`，而是把 runtime truth 写正：
- `Surviving candidate slot = Rank 211`
- `Fresh intake slot = 0523`
- `Active P2 slot = none`
- 并把旧的 `Rank 210` 从非法前排并存状态中移出。

## 6) 对 state 的实际写回
本轮已更新 `docs/BOT2_BOT3_STATE.md`：
- `Fresh intake slot` 改为：
  - `status: pending`
  - `current_target: research/quant_digests/2026-03-27_0523_same-venue-options-vertical-noarb-alpha.md`
- `Surviving candidate slot` 改为：
  - `current_target: Rank 211 / CME BTC futures sign classifier`
  - `followup_budget_remaining: 1`
- `Active P2 slot` 保持 `none`
- `Background pool` 最新停放改写为：
  - `Rank 210 / predicted funding sign -> carry on/off / reverse` 不再允许继续占据前排 survivor，因为最新一条 fresh intake 已变成 `Rank 211`
- `cycle_plan` 重写为：
  1. `Rank 211` survivor 唯一 follow-up
  2. `0523` fresh intake
  3. `0334` fresh intake
  4. `1927` conditional fresh intake

所有新排项均满足：
- 只写 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 7) 一句话结论
这轮最重要的不是继续拖着两个 `keep_P1` 前排并存，而是把 runtime truth 写正：**最新一条 fresh intake `Rank 211` 必须接管 survivor 锁；因此当前轮次应是 `Rank 211 survivor > 0523 intake > 0334 intake > 1927 intake`，而不是继续让 `Rank 210` 非法留在前排。**
