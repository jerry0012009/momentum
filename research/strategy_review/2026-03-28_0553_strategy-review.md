# Strategy Review (bot2)

Time: 2026-03-28 05:53 UTC

## 本轮一句话判断
`Paper launch queue` 仍为空；本轮 legal front chain 先是 `Rank 212 / XS momentum × inverse-vol × low-sentiment gate` 的唯一 survivor follow-up，随后才是 `research/quant_digests/2026-03-28_0447_largecap-xs-momentum-shortleg-veto-alpha.md` 这条 fresh intake；上一条 fresh intake `Rank 212` 值得那唯一一次 follow-up；当前不存在明确 `Active P2`，因此不存在离 `P3 / P1 / P0` 哪个出口最近的问题。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short`
  - 结论：仓内仍有大量未跟踪页面/脚本/artifact；这些都只算最近运行 evidence，不得反向改 policy，也不得把 background pool 旧候选自动拉回前排。
- 最近 `research/optimization_loop/`：
  - `2026-03-28_0531_1s_book_horizon_sweep_intake_blocked_by_rank212_survivor_lock.md`
  - `2026-03-28_0523_largecap_xs_momentum_shortleg_veto_intake_blocked_by_rank212_survivor_lock.md`
  - `2026-03-28_0518_rank212_xs_momentum_inversevol_lowsentiment_intake_keep_p1.md`
  - `2026-03-28_0453_crossvenue_funding_rotation_refresh_intake_drop_to_background.md`
- 最近 `research/strategy_review/`：
  - `2026-03-28_0456_strategy-review.md`
  - `2026-03-28_0358_strategy-review.md`
- 本轮补读的具体 fresh-intake 候选：
  - `research/quant_digests/2026-03-28_0512_xs-relative-strength-fullstack-baseline.md`

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
- `Rank 200 / BTC weekday-hour sparse short schedule` 与 `Rank 201 / UTC clock seasonality low-switch schedule` 都已经是 `connected_runner_live`；
- 当前 queue-side 没有等待接线的头部对象；
- 因此本轮没有 `P3 / launch wiring` 动作可排在最前。

### Q2. 本轮 `fresh intake` 是什么？
**本轮 `fresh intake` 仍是 `research/quant_digests/2026-03-28_0447_largecap-xs-momentum-shortleg-veto-alpha.md`。**
原因：
- 当前前排还有 `Rank 212` survivor 要先收口，所以 fresh intake 不能越位；
- 但在 survivor 之后排队的首条 fresh intake 仍是 `0447 large-cap XS momentum × short-leg jump veto`；
- `0523` 与 `0531` 两条最新 optimization loop 只是证明它目前被 survivor lock 挡住，不是把 fresh intake 头部改成别的对象。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得，而且现在必须由它独占 survivor 槽位。**
上一条 fresh intake 是 `Rank 212 / XS momentum × inverse-vol × low-sentiment gate`：
- 它已经正式拿到 `keep_P1`，且有正式 `Rank 212`；
- 唯一高杠杆问题也很明确：不是继续追慢变量 sentiment 叙事，而是直接回答 `inverse-vol` sizing 放到更长窗口、更多 friction ladder、liquid majors 的真实 turnover 后，净边际还能不能活；
- 这正符合 policy 对 survivor 的定义：**只保留 1 次便宜而 decisive 的 follow-up**。

所以答案不是“可以考虑”，而是：**值得，而且在诚实收口前不能让别的 fresh intake 抢走 survivor 前排锁。**

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**当前不存在明确 `Active P2`。**
- `Active P2 slot` 当前仍是 `none`；
- 最近已收口过的 `Rank 203 / graph-matching pairbook mean-reversion` 已在更早一轮正式写成 `P1 re-scope`，但它不是当前 active P2；
- 既然当前 active P2 不存在，就不存在“离 `P3 / P1 / P0` 哪个出口最近”的当前对象。

## 3) rank 合规检查
- `Paper launch queue`: none
- `Fresh intake slot`: `0447` 还未首判，因此不需要预先分配 rank
- `Surviving candidate slot`: `Rank 212`，已有正式 rank
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
   - 有，而且必须排第一：`Rank 212` 的唯一一次 survivor follow-up 需要这轮先收口。
4. **fresh intake**
   - 只有在 survivor 已被诚实排进首位后，剩余预算才回到新的具体 intake；
   - 当前最诚实的顺序应是：
     1. `2026-03-28_0447_largecap-xs-momentum-shortleg-veto-alpha.md`
     2. `2026-03-27_1927_1s-book-horizon-sweep-alpha.md`
     3. `2026-03-28_0512_xs-relative-strength-fullstack-baseline.md`

这里刻意**不**把任何 background pool 旧候选重新拉回前排，也不把 `Rank 212` 的 follow-up 再写成第二次开放式延长。

## 5) 是否需要 bot2 直接兜底推进到 P3？
**不需要。**
本轮没有处于 `Active P2` 且已明显够格升 `P3`、但 bot3 尚未升级的对象：
- `Active P2 slot = none`
- `Rank 212` 还只是 survivor follow-up 阶段，不是 P2 出口决策轮
- 当前后续动作都还是 fresh intake

因此这轮 bot2 的职责不是强推 `P3`，而是把 runtime truth 写正到：**`Rank 212 survivor > 0447 intake > 1927 intake > 0512 intake`**。

## 6) 对 state 的实际写回
本轮已更新 `docs/BOT2_BOT3_STATE.md`：
- `Fresh intake slot` 维持 `blocked`，但最新说明改成：`0447` 仍是 survivor 链之后的首条 fresh intake，而不是被新的对象替换；
- `Surviving candidate slot` 维持：
  - `current_target: Rank 212 / XS momentum × inverse-vol × low-sentiment gate`
  - `followup_budget_remaining: 1`
- `Active P2 slot` 保持 `none`
- `cycle_plan` 重写为 4 条具体任务：
  1. `Rank 212` survivor 唯一 follow-up
  2. `0447` fresh intake
  3. `1927` fresh intake
  4. `0512` fresh intake

所有新排项都满足：
- 只写 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 7) 一句话结论
这轮没必要装复杂：**先把 `Rank 212` 那唯一一次 survivor follow-up 做完，后面 fresh intake 头部仍是 `0447 large-cap XS momentum × short-leg jump veto`，再往后才轮到 `1927 1s book horizon sweep` 和 `0512 XS relative-strength baseline`。**
