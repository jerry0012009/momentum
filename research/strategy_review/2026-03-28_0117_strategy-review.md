# Strategy Review (bot2)

Time: 2026-03-28 01:17 UTC

## 本轮一句话判断
`Paper launch queue` 为空；本轮应把 `research/quant_digests/2026-03-28_0057_us-close-crypto-synthetic-open-spillover-alpha.md` 作为 fresh intake；上一条 fresh intake `Rank 208 / extreme-return shock percentile` 值得那唯一一次 follow-up，且必须占住 survivor 槽位；当前不存在明确 `Active P2`，最近的已收口前排出口是 `Rank 203` 已从 `P2` 一次性退回 `P1 re-scope`，因此本轮默认顺序应是 `Rank 208 survivor > 0057 intake > 0020 intake > Rank 203 re-scope framing`。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git status --short`
  - 结论：仓内仍有大量未跟踪页面/脚本/artifact；这些只算最近运行 evidence，不得反向改 policy，也不得把 background pool 旧候选自动拉回前排。
- 最近 `research/optimization_loop/`：
  - `2026-03-28_0102_rank208_extreme_return_shock_percentile_intake_keep_p1.md`
  - `2026-03-28_0039_rank207_btc_si_lagged_tech_intake_keep_p1.md`
  - `2026-03-28_0032_rank205_survivor_followup_drop_to_background.md`
  - `2026-03-28_0005_rank203_p2_exit_rescope_to_p1.md`
- 最近 `research/strategy_review/`：
  - `2026-03-28_0001_strategy-review.md`
  - `2026-03-27_2303_strategy-review.md`
  - `2026-03-27_2206_strategy-review.md`
- 最近新 digest：
  - `research/quant_digests/2026-03-28_0020_predicted-funding-sign-carry-switch-alpha.md`
  - `research/quant_digests/2026-03-28_0057_us-close-crypto-synthetic-open-spillover-alpha.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排
- 未把 `docs/TODO.md` 当成本轮排班依据
- 前排对象 rank 合规：`Rank 200 / 201 / 203 / 208` 均已有正式整数 rank；本轮无需补号

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**否，当前为空。**
原因：
- `Rank 200` 与 `Rank 201` 都已是 `connected_runner_live`；
- 当前 queue-side 没有等待接线的头部对象；
- 因此本轮没有 `P3 / launch wiring` 动作可排在最前。

### Q2. 本轮 `fresh intake` 是什么？
**本轮 fresh intake 应改为 `research/quant_digests/2026-03-28_0057_us-close-crypto-synthetic-open-spillover-alpha.md`。**
原因：
- `Rank 208` 的首轮 intake 已在 `2026-03-28_0102_rank208_extreme_return_shock_percentile_intake_keep_p1.md` 完成，不能继续占 fresh intake 名额；
- 最新两个候选里，`0057` 的 `US close impulse -> crypto synthetic open catch-up` 是更明确的跨时段 raw-alpha 母线，且与当前 front chain 正交；
- `0020` 也具体，但按默认顺序应排在 `0057` 之后作为补位 intake。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得，而且现在必须由它占住 survivor 槽位。**
上一条 fresh intake 是 `Rank 208 / extreme-return shock percentile`：
- 它已正式拿到 `keep_P1`；
- 唯一高杠杆 follow-up 问题非常明确：在 BTC/ETH（必要时再加 SOL）的 `3m/5m` majors 上，把 `continuation` 与 `fade` 两支拆开，在统一 friction ladder 下回答成本后到底剩哪一支 pocket；
- 这正符合 policy 的“上一条 fresh intake 只配一次便宜而 decisive 的 survivor follow-up”。

所以答案不是“可做可不做”，而是：**值得，而且在诚实收口前不能被另一条新的 keep_P1 覆盖。**

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**当前不存在明确 `Active P2`。**
最近的前排 P2 出口已经在 `Rank 203 / graph-matching pairbook mean-reversion` 上收口完成：
- `2026-03-28_0005_rank203_p2_exit_rescope_to_p1.md` 已把它从 `P2` 一次性写成 `P1 re-scope`；
- 这说明它当前最近的出口不是 `P3`，而是已经正式落在 `P1`；
- 本轮不应把它假装还在 `Active P2`，更不能继续按旧 axis 重复 admission。

## 3) rank 合规检查
- `Paper launch queue`: none
- `Fresh intake slot`: 待执行对象 `0057` 还未首判，因此不需要预先分配 rank
- `Surviving candidate slot`: `Rank 208`，已有正式 rank
- `Active P2 slot`: none

结论：
- 当前不存在“前排对象已达 `keep_P1 / P2 / P3` 却无 rank”的违规情况；
- 本轮无需补新的整数 `Rank`；
- 真正需要修正的是 runtime 槽位与 `cycle_plan` 的默认顺序。

## 4) 本轮排班判断
按 policy 默认顺序扫描：

1. **P3 / Paper launch queue**
   - 当前为空；无真实可执行动作。
2. **P2 / Active P2**
   - 当前为空；`Rank 203` 已完成 `P2 -> P1 re-scope`，不得假装仍在 active P2。
3. **P1 / Surviving candidate**
   - 有，而且必须排第一：`Rank 208` 的 survivor 唯一 follow-up 不应被新的 intake 覆盖。
4. **fresh intake**
   - 当前前排真实可执行动作是 survivor；在它被诚实排入首位后，剩余预算再补最新两个具体 intake：
     - `2026-03-28_0057_us-close-crypto-synthetic-open-spillover-alpha.md`
     - `2026-03-28_0020_predicted-funding-sign-carry-switch-alpha.md`
5. **已收口前排对象的 re-scope framing**
   - 若预算仍有余，再把 `Rank 203` 仅作为 `P1 re-spec` 问题定义来处理；
   - 明确禁止 reopen 成 `Active P2`，也禁止重复上一轮 `execution realism / live-book availability` axis。

## 5) 是否需要 bot2 直接兜底推进到 P3？
**不需要。**
本轮没有处于 `Active P2` 且已明显够格升 `P3`、但 bot3 尚未升级的对象：
- `Rank 203` 已经被正式写成 `P2 -> P1 re-scope`，而不是“明明够格却还没升”；
- `Rank 208` 只是 survivor follow-up 阶段，离 `P3` 还很远；
- `0057 / 0020` 都还只是新 intake 候选。

因此，这轮 bot2 的兜底动作不是强推 `P3`，而是：
- 把 `Rank 208` 正式写回 survivor 槽位；
- 把 `0057` 指定为 fresh intake；
- 把 `0020` 放到其后；
- 明确 `Active P2 = none`。

## 6) 对 state 的实际写回
本轮已更新 `docs/BOT2_BOT3_STATE.md`：
- `Fresh intake slot` 改为：
  - `status: pending`
  - `current_target: research/quant_digests/2026-03-28_0057_us-close-crypto-synthetic-open-spillover-alpha.md`
- `Surviving candidate slot` 改为：
  - `current_target: Rank 208 / extreme-return shock percentile`
  - `followup_budget_remaining: 1`
- `Active P2 slot` 保持 `none`
- `cycle_plan` 重写为：
  1. `Rank 208` survivor 唯一 follow-up
  2. `0057` fresh intake
  3. `0020` fresh intake
  4. `Rank 203` 仅限 re-scope framing，不做 reopen

所有新排项均满足：
- 只写 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 7) 一句话结论
这轮真正该做的不是继续假装有 `Active P2`，而是把前排 runtime truth 写正：**`Rank 208` 必须锁住 survivor 槽位，然后才轮到 `0057` 与 `0020` 两条最新、最具体的新 intake；`Rank 203` 已经收口成 `P1 re-scope`，不该再被当作当前 P2。**
