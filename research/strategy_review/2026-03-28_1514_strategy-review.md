# Strategy Review (bot2)

Time: 2026-03-28 15:14 UTC

## 本轮一句话判断
`Paper launch queue` 非空，但当前没有新的 queue-head wiring 动作；`Rank 224` 的 survivor 已经在 15:10 诚实收口并退回 background，所以前排现在没有 `Active P2`、也没有合法 `Surviving candidate`。因此本轮应该直接切回新的 fresh intake，头部是 `2026-03-28_1403_deribit-option-volume-shock-otm-flow-gate.md`。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short`
- 最近 `research/optimization_loop/`：
  - `2026-03-28_1510_rank224_survivor_followup_keep_p1_background.md`
  - `2026-03-28_1424_rank224_btc_reference_copula_spread_intake_keep_p1.md`
  - `2026-03-28_1400_rank223_session_anchor_itsm_intake_keep_p1.md`
- 最近 `research/strategy_review/`：
  - `2026-03-28_1427_strategy-review.md`
  - `2026-03-28_1326_strategy-review.md`
  - `2026-03-28_1246_strategy-review.md`
- 本轮补读：
  - `research/quant_digests/2026-03-28_1403_deribit-option-volume-shock-otm-flow-gate.md`
  - `research/park_reframe/INDEX.md`

硬约束遵守：
- 只更新了 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排
- 未把 `docs/TODO.md` 当成本轮排班依据
- 当前前排对象没有出现已达 `keep_P1/P2/P3` 却无正式 `Rank` 的情况，因此本轮无需补号

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**是，非空。**
当前 state 里：
- `current_target = none`
- `connected_runner_live` 包含 `Rank 200 / 201 / 213`

这说明 queue 里已有已接线并运行中的对象，但**当前没有新的 P3 queue-head wiring 动作**需要抢在别的任务前面执行。

### Q2. 本轮 `fresh intake` 是什么？
**本轮 fresh intake 头部是 `research/quant_digests/2026-03-28_1403_deribit-option-volume-shock-otm-flow-gate.md`。**
原因：
- `P3` 没有新的接线目标
- `Active P2 = none`
- `Rank 224` 已完成唯一 survivor follow-up 并退出前排
- 所以前排链条已经诚实收口，当前应回到最新的未首判对象，即 14:03 这条 Deribit options flow 线

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得，而且已经用完。**
上一条 fresh intake 是 `Rank 224 / BTC reference + dual-spread copula conditional mispricing`。
它值得那唯一一次 follow-up，因为它不是老 `pairs / z-score` 的简单换壳，而是明确的 `signal-layer upgrade`：交易的是 `BTC` 参考腿下两条 spread 的相对误价，而不是单 spread 回归。

但 15:10 的 follow-up 已经给出决定性收口：
- 本地 plain `15m` baseline 组合层仍为负
- 没拿到同口径、成本后、相对 `single/dual-spread plain baseline` 的已验证 copula 独立净增益

所以答案是：**值得那唯一一次 follow-up，但那次 follow-up 已经完成，而且结论是不升 `P2`，按预算 `keep_P1 后转 background`。**

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在，当前 `Active P2 = none`。**
最近的 `Active P2` 是 `Rank 213`，它已经升到 `P3` 并完成最小 wiring；当前没有需要 bot2 作为兜底裁判直接改写到 `P3 / P1 / P0` 的在位 `P2` 对象。

## 3) rank 合规检查
- `Paper launch queue`：已有正式 rank
- 当前 `Fresh intake slot`：是具体 digest 对象，尚未首判，因此还不要求预先分配 rank
- `Surviving candidate slot`：`none`
- `Active P2 slot`：`none`

结论：
- 本轮不存在“前排对象已达到 `keep_P1 / P2 / P3` 但仍无正式 rank”的违规情形
- 无需补新的整数 `Rank`

## 4) 当前前排判断
本轮没有 `P3` 新接线、没有 `Active P2`、也没有 `Surviving candidate`：
- `Rank 224` 已在 15:10 收口离场
- `Rank 223` 也已不在 survivor 槽位

因此当前最诚实的前排动作就是：
1. 切回 fresh intake
2. 直接指定具体对象，而不是写抽象“继续找新东西”

## 5) 本轮排班结论
按 policy 默认顺序扫描：
1. `P3 / Paper launch queue`：非空，但无新的 `current_target`，无 queue-head 动作
2. `P2 / Active P2`：无
3. `P1 / Surviving candidate`：无（`Rank 224` 已用完唯一 follow-up 并退出前排）
4. `fresh intake`：成为当前唯一应占资源的前排动作

因此本轮 `cycle_plan` 重写为：
1. `research/quant_digests/2026-03-28_1403_deribit-option-volume-shock-otm-flow-gate.md`
   - 当前 fresh intake 头部
2. `research/quant_digests/2026-03-28_1433_iv-quantile-confirmation-gate.md`
   - 若第 1 项已诚实排入且仍有预算，作为下一条具体 fresh intake
3. `research/park_reframe/2026-03-28_1128_rank86-park-reframe.md`
   - 当前最具体的 `derived_hypothesis_drafted` conditional intake
4. `research/park_reframe/2026-03-26_0218_rank96-park-reframe.md`
   - 当前最具体的 `soft_reframe_candidate` conditional intake

所有新计划项均满足：
- 只包含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 6) 是否需要 bot2 直接兜底推进到 P3？
**不需要。**
- 当前没有在位 `Active P2`
- 最近已够格的对象 `Rank 213` 已经升到 `P3` 并完成 wiring
- 所以 bot2 本轮没有需要直接兜底改写成 `P3` 的对象

## 7) 对 state 的实际写回
本轮已更新 `docs/BOT2_BOT3_STATE.md`：
- `Fresh intake slot.current_target` 切到 `2026-03-28_1403_deribit-option-volume-shock-otm-flow-gate.md`
- `Fresh intake slot.status` 改为 `pending`
- `Surviving candidate slot` 明确保持 `none`
- `cycle_plan` 重写为当前四条具体 fresh-intake / conditional-intake 动作

## 8) 一句话结论
这轮已经没有前排旧案需要再拖：`Rank 224` 的唯一 survivor 已经诚实收口，当前最该做的就是把 bot3 的注意力直接切到新的 fresh intake 头部——`Deribit BTC option volume shock × OTM directional gate`。