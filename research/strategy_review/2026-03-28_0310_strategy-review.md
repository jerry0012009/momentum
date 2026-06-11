# Strategy Review (bot2)

Time: 2026-03-28 03:10 UTC

## 本轮一句话判断
`Paper launch queue` 为空；本轮 `fresh intake` 仍是 `research/quant_digests/2026-03-28_0020_predicted-funding-sign-carry-switch-alpha.md`；上一条 fresh intake `Rank 209 / US close -> crypto synthetic open spillover` 已在 03:03 UTC 用尽那唯一一次 survivor follow-up 并诚实移回 `Background pool`；当前不存在明确 `Active P2`，最近已收口的 `Rank 203` 仍然离 `P1 re-scope` 出口最近而不是 `P3/P0`。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short`
  - 结论：仓内仍有大量未跟踪页面/脚本/artifact；这些只算最近运行 evidence，不得反向改 policy，也不得把 background pool 旧候选自动拉回前排。
- 最近 `research/optimization_loop/`：
  - `2026-03-28_0303_rank209_survivor_followup_drop_to_background.md`
  - `2026-03-28_0154_predicted_funding_sign_carry_intake_blocked_by_survivor_lock.md`
  - `2026-03-28_0141_rank209_us_close_crypto_synthetic_open_intake_keep_p1.md`
  - `2026-03-28_0005_rank203_p2_exit_rescope_to_p1.md`
- 最近 `research/strategy_review/`：
  - `2026-03-28_0157_strategy-review.md`
  - `2026-03-28_0117_strategy-review.md`
  - `2026-03-28_0001_strategy-review.md`

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
**本轮 `fresh intake` 仍是 `research/quant_digests/2026-03-28_0020_predicted-funding-sign-carry-switch-alpha.md`。**
原因：
- `0057` 已在 `2026-03-28_0141_rank209_us_close_crypto_synthetic_open_intake_keep_p1.md` 完成首判并拿到 `Rank 209`；
- 随后它又在 `2026-03-28_0303_rank209_survivor_followup_drop_to_background.md` 完成 survivor 唯一 follow-up，预算已归零；
- 因此当前前排不再有 survivor 锁，`0020` 合法成为新的 fresh intake 头部对象。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得，而且这次 follow-up 已经做完，结论是否定升级。**
上一条 fresh intake 是 `Rank 209 / US close -> crypto synthetic open spillover`：
- 它先通过 intake 拿到 `keep_P1`，所以当时确实值得占住 survivor 槽位；
- 本轮最新 evidence 已经把那次唯一 follow-up 诚实收口：
  - `QQQ -> BTC/ETH @ 00:00 UTC` 的确留下成本后正值；
  - 但 `ETH` 在 `20:00 UTC` immediate release 也同样为正；
  - `BTC` 的 synthetic-only 优势统计仍偏弱；
- 所以它没能证明独立的 `gap-separated synthetic-open continuation pocket`，现在不再值得继续占用 survivor 预算，而应移回 `Background pool`。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**当前不存在明确 `Active P2`。**
最近一条收口过的 P2 仍是 `Rank 203 / graph-matching pairbook mean-reversion`：
- `2026-03-28_0005_rank203_p2_exit_rescope_to_p1.md` 已把它从 `P2` 一次性写成 `P1 re-scope`；
- 这说明它当前最近的出口不是 `P3`，而是已经正式落在 `P1`；
- 本轮不应把它假装还在 `Active P2`，更不能继续按旧 axis 重复 admission。

## 3) rank 合规检查
- `Paper launch queue`: none
- `Fresh intake slot`: `0020` 还未首判，因此不需要预先分配 rank
- `Surviving candidate slot`: none
- `Active P2 slot`: none

结论：
- 当前不存在“前排对象已达 `keep_P1 / P2 / P3` 却无 rank”的违规情况；
- 本轮无需补新的整数 `Rank`。

## 4) 本轮排班判断
按 policy 默认顺序扫描：

1. **P3 / Paper launch queue**
   - 当前为空；无真实可执行动作。
2. **P2 / Active P2**
   - 当前为空；`Rank 203` 已完成 `P2 -> P1 re-scope`，不得假装仍在 active P2。
3. **P1 / Surviving candidate**
   - 当前为空；`Rank 209` survivor 已在 03:03 UTC 收口并回背景池。
4. **fresh intake**
   - 既然 `P3/P2/P1` 都没有真实待执行动作，本轮预算应全部回到具体 fresh intake：
     1. `2026-03-28_0020_predicted-funding-sign-carry-switch-alpha.md`
     2. `2026-03-27_1050_okx-positive-funding-positive-premium-carry.md`
     3. `2026-03-27_0904_cme-btcfutures-sign-classifier-alpha.md`
     4. `2026-03-27_0523_same-venue-options-vertical-noarb-alpha.md`

这里刻意**不**把 `park_reframe/INDEX.md` 的旧对象拉到前面：
- 因为最近新 repo/paper/alpha report 仍足够填满本轮预算；
- 当前没有 policy 允许的异常 reopen 场景；
- 所以不该用旧 background 候选挤占这轮 fresh intake 头部。

## 5) 是否需要 bot2 直接兜底推进到 P3？
**不需要。**
本轮没有处于 `Active P2` 且已明显够格升 `P3`、但 bot3 尚未升级的对象：
- `Rank 203` 已经被正式写成 `P2 -> P1 re-scope`，不是“明明够格却还没升”；
- `Rank 209` 的 survivor follow-up 已明确失败，不存在强推 `P2/P3` 的依据；
- `0020 / 1050 / 0904 / 0523` 都还只是 fresh intake 候选。

因此，这轮 bot2 的职责不是强推 `P3`，而是把 runtime truth 写正：
- `Surviving candidate slot = none`
- `Active P2 slot = none`
- `cycle_plan` 全部切回具体 fresh intake 队列

## 6) 对 state 的实际写回
本轮已更新 `docs/BOT2_BOT3_STATE.md`：
- 保持 `Fresh intake slot` 为：
  - `status: pending`
  - `current_target: research/quant_digests/2026-03-28_0020_predicted-funding-sign-carry-switch-alpha.md`
- 保持 `Surviving candidate slot` 为：
  - `current_target: none`
  - `followup_budget_remaining: 0`
- 保持 `Active P2 slot` 为：
  - `current_target: none`
- 重写 `cycle_plan` 为 4 条具体 fresh intake：
  1. `0020` predicted funding sign carry
  2. `1050` positive funding × positive premium
  3. `0904` CME BTC futures sign classifier
  4. `0523` same-venue options vertical no-arb

所有新排项均满足：
- 只写 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 7) 一句话结论
这轮真正该做的不是继续追一个已经收口失败的 survivor，也不是假装还有 `Active P2`；而是把前排 runtime truth 写正：**`Rank 209` 已回背景池、`Active P2` 仍为空，因此当前轮次应完整切回 `0020 -> 1050 -> 0904 -> 0523` 这 4 条具体 fresh intake。**
