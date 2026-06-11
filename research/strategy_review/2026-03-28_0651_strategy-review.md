# Strategy Review (bot2)

Time: 2026-03-28 06:51 UTC

## 本轮一句话判断
`Paper launch queue` 为空；本轮 legal front chain 是 `Rank 213 / large-cap XS momentum × short-leg jump veto` 的唯一 survivor follow-up，其后才轮到新的 fresh intake；上一条 fresh intake `Rank 213` 值得也必须拿到那唯一一次 follow-up；当前不存在明确 `Active P2`，因此也不存在离 `P3 / P1 / P0` 哪个出口最近的问题。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short --branch`
  - 结论：仓内仍有大量未跟踪页面/脚本/artifact；这些都只算最近运行 evidence，不得反向改 policy，也不得把 background pool 旧候选自动拉回前排。
- 最近 `research/optimization_loop/`：
  - `2026-03-28_0650_1s_book_horizon_sweep_fresh_intake_blocked_already_rank202_background.md`
  - `2026-03-28_0621_rank213_largecap_xs_momentum_shortleg_veto_intake_keep_p1.md`
  - `2026-03-28_0556_rank212_survivor_followup_close_to_background.md`
  - `2026-03-28_0523_largecap_xs_momentum_shortleg_veto_intake_blocked_by_rank212_survivor_lock.md`
- 最近 `research/strategy_review/`：
  - `2026-03-28_0553_strategy-review.md`
  - `2026-03-28_0456_strategy-review.md`
- 本轮补读的具体候选：
  - `research/quant_digests/2026-03-28_0512_xs-relative-strength-fullstack-baseline.md`
  - `research/quant_digests/2026-03-28_0608_return-relvol-xs-momentum-alpha.md`
  - `research/park_reframe/INDEX.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排
- 未把 `docs/TODO.md` 当成本轮排班依据
- 当前前排对象不存在无 rank 违规，因此无需补新整数 `Rank`

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**否，当前为空。**
原因：
- `Rank 200 / BTC weekday-hour sparse short schedule` 与 `Rank 201 / UTC clock seasonality low-switch schedule` 都已经处于 `connected_runner_live`；
- 当前 queue-side 没有等待接线的头部对象；
- 因此本轮没有 `P3 / launch wiring` 动作可排在最前。

### Q2. 本轮 `fresh intake` 是什么？
**严格按前排优先级看，本轮首先不是新的 fresh intake，而是 `Rank 213 / large-cap XS momentum × short-leg jump veto` 的 survivor follow-up；在 survivor 之后，首条 fresh intake 是 `research/quant_digests/2026-03-28_0512_xs-relative-strength-fullstack-baseline.md`。**
原因：
- `Rank 213` 已经首判为 `keep_P1`，且 policy 规定 survivor 只能是上一条 fresh intake，并在诚实收口前享有前排锁定权；
- `research/quant_digests/2026-03-27_1927_1s-book-horizon-sweep-alpha.md` 已被 `2026-03-28_0650` 明确写成 background 对象，禁止自动 reopen；
- 因此 survivor 收口后，最新且仍合法的 fresh intake 头部应切到 `0512 XS relative-strength full-stack baseline`。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得，而且现在必须由它独占 survivor 槽位。**
上一条 fresh intake 是 `Rank 213 / large-cap XS momentum × short-leg jump veto`：
- 它已经正式拿到 `keep_P1`，且有正式 `Rank 213`；
- 当前 hard negative 事实很清楚：`12` 个 liquid majors 的 `15m` proxy 下 plain WML 与 jump-veto 版都明显为负、veto 触发也极少；
- 但 survivor follow-up 的高杠杆问题也同样清楚：**short-leg single-name jump concentration 是否只会在更宽的 alt-perp universe 才成为 decisive blocker**；
- 这符合 policy 对 survivor 的定义：只保留 1 次便宜而 decisive 的 follow-up，不在 majors 小口袋里继续抠小数点。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**当前不存在明确 `Active P2`。**
- `Active P2 slot` 当前是 `none`；
- 最近收口过的 `Rank 203 / graph-matching pairbook mean-reversion` 已在更早一轮正式写成一次性 `P2 -> P1 re-scope`，但它不是当前 active P2；
- 因此本轮不存在需要 bot2 兜底回答 `P3 / P1 / P0` 出口的在排 P2 对象。

## 3) rank 合规检查
- `Paper launch queue`: none
- `Fresh intake slot`: 当前 latest result 已是 `Rank 213` 的首判，rank 合规
- `Surviving candidate slot`: `Rank 213`，已有正式 rank
- `Active P2 slot`: none

结论：
- 当前不存在“前排对象已达 `keep_P1 / P2 / P3` 却无 rank”的违规情况；
- 本轮无需补新的整数 `Rank`。

## 4) 本轮排班判断
按 policy 默认顺序扫描：

1. **P3 / Paper launch queue**
   - 当前为空；无真实可执行动作。
2. **P2 / Active P2**
   - 当前为空；无 admission / promote / park 动作。
3. **P1 / Surviving candidate**
   - 有，而且必须排第一：`Rank 213` 的唯一 survivor follow-up 需要这轮先收口。
4. **fresh intake**
   - 只有在 survivor 已被诚实排进首位后，剩余预算才回到新的具体 intake；
   - 当前最诚实的顺序应是：
     1. `2026-03-28_0512_xs-relative-strength-fullstack-baseline.md`
     2. `2026-03-28_0608_return-relvol-xs-momentum-alpha.md`
     3. `research/park_reframe/2026-03-26_0218_rank96-park-reframe.md`（conditional intake，来自 `soft_reframe_candidate`）

这里刻意不把任何 background pool 旧候选重新拉回前排：
- `Rank 202 / 1s book horizon sweep` 已完成 intake 与 survivor 收口并正式回到 background；
- `Rank 212` 已在上一轮 survivor follow-up 后收口到 background；
- `Rank 203` 是更早的 P1 re-scope 历史对象，不是当前 legal front object。

## 5) 是否需要 bot2 直接兜底推进到 P3？
**不需要。**
本轮没有处于 `Active P2` 且已明显够格升 `P3`、但 bot3 尚未升级的对象：
- `Paper launch queue = none`
- `Active P2 slot = none`
- 当前所有合法动作都落在 `Rank 213` 的 survivor 收口与后续新的 intake

因此这轮 bot2 的职责不是强推 `P3`，而是把 runtime truth 改回：**`Rank 213 survivor > 0512 intake > 0608 intake > Rank 96 conditional intake`**。

## 6) 对 state 的实际写回
本轮已更新 `docs/BOT2_BOT3_STATE.md`：
- 保持 `Paper launch queue` 为空且仅保留 `connected_runner_live` 记录
- 保持 `Fresh intake slot` 的 latest result 为 `Rank 213` 首判完成
- 保持 `Surviving candidate slot` 为：
  - `current_target: Rank 213 / large-cap XS momentum × short-leg jump veto`
  - `followup_budget_remaining: 1`
- `Active P2 slot` 保持 `none`
- `cycle_plan` 重写为 4 条具体任务：
  1. `Rank 213` survivor 唯一 follow-up
  2. `0512 XS relative-strength full-stack baseline` fresh intake
  3. `0608 return × relative-volume XS momentum` fresh intake
  4. `Rank 96 park reframe candidate` conditional intake

所有新排项都满足：
- 只写 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 7) 一句话结论
这轮别绕：**先把 `Rank 213` 那唯一一次 survivor follow-up 做完；只要它还没诚实收口，任何新的 intake 都不能越位。收口之后，fresh intake 头部依次是 `0512 XS relative-strength baseline`、`0608 return × relative-volume XS momentum`，最后才是 `Rank 96` 的 conditional reframe intake。**
