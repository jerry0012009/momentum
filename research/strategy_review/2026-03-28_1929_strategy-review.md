# Strategy Review (bot2)

Time: 2026-03-28 19:29 UTC

## 本轮一句话判断
`Paper launch queue` 仍然非空，但没有新的接线缺口；当前唯一明确前排对象是 `Rank 228` survivor，所以本轮必须先把它的唯一一次 follow-up 诚实收口。收口前，`Rank 86` 的 park-reframe 派生假设只能作为下一条 pending fresh intake 头部，不能插队。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short --branch`
- 最近 `research/optimization_loop/`：
  - `2026-03-28_1923_rank86b_conditional_intake_blocked_survivor_slot_occupied.md`
  - `2026-03-28_1900_rank228_directional_change_overshoot_intake_keep_p1.md`
  - `2026-03-28_1844_rank227_survivor_followup_keep_p1_background.md`
  - `2026-03-28_1823_rank227_stablecoin_orderflow_shock_path_intake_keep_p1.md`
- 最近 `research/strategy_review/`：
  - `2026-03-28_1831_strategy-review.md`
  - `2026-03-28_1717_strategy-review.md`
- 新 intake 补充来源：
  - `research/park_reframe/INDEX.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改写 policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排
- 未把 `docs/TODO.md` 当成本轮排班依据
- 前排对象均已有正式 rank，本轮无需补号

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**是，非空。**

当前 state 仍记录：
- `current_target = none`
- `connected_runner_live` 包含 `Rank 200 / 201 / 213`

说明 queue 里仍有已接线完成对象，但最近证据没有出现新的 `runner / scheduler / first verified run` 缺口，所以本轮没有需要抢到 survivor 前面的 `P3` 动作。

### Q2. 本轮 `fresh intake` 是什么？
**当前顺位上的 fresh intake 头部是 `research/park_reframe/2026-03-28_1128_rank86-park-reframe.md`。**

原因：
- `Rank 228` 已在 19:00 完成 fresh intake 首判，并转入 `Surviving candidate slot`
- 19:23 的 bot3 日志也确认：`Rank 86` conditional intake 因 survivor 槽仍被 `Rank 228` 占用而被 guard 拦下
- 因此，当前 front-chain 上“下一条合法 fresh intake”已经顺延到 `Rank 86` 的 park-reframe 派生假设

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**

上一条 fresh intake 是 `Rank 228 / directional-change overshoot + abnormal-regime veto`。

它值得那唯一一次 follow-up，因为：
1. 它保留的是独立的 **event-driven raw alpha 骨架**：`DC 确认 -> 吃 overshoot continuation -> 反向 DC / abnormal regime 退出`；
2. 目前没过关的核心不是逻辑塌掉，而是证据还停在 **FX / long-only / 无成本**；
3. 仍有一条便宜、具体、decisive 的下一步：直接在 `BTCUSDT / ETHUSDT 1m` public bar-proxy DC 事件流上回答，扣掉 `4~6 bps` 后是否还有 pocket，以及 abnormal veto 是否真能压 tail loss。

所以答案是：
- **值得那唯一一次 follow-up**；
- 而且这次 follow-up 就是当前第一优先级；
- 在它收口前，不该让 `Rank 86` 或其他新 intake 插队。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在，当前 `Active P2 = none`。**

最近的 `Active P2` 是 `Rank 213`，但它已经：
- 在 08:52 完成 `P2 -> P3` 升级；
- 在 11:20 完成最小 `P3 launch wiring`；
- 当前已写成 `connected_runner_live`。

因此，本轮不存在需要我直接裁成 `P3 / P1 / P0` 的在位 `Active P2`。

## 3) rank 合规检查
- `Paper launch queue`：`Rank 200 / 201 / 213`，都有正式 rank
- `Surviving candidate slot`：`Rank 228`，已有正式 rank
- `Active P2 slot`：`none`
- 当前 fresh intake 头部 `Rank 86` 仍只是 park-reframe 来源对象，不是新的未编号 survivor / P2 / P3 前排实体；因此本轮无需补新整数 rank

结论：
- 当前前排对象不存在缺 rank 违规项
- 本轮无需补号

## 4) 当前前排判断
按 policy 默认顺序扫描：
1. `P3 / Paper launch queue`：非空，但无新接线动作
2. `P2 / Active P2`：无
3. `P1 / Surviving candidate`：**有，而且就是 `Rank 228` 这一条合法前排动作**
4. `fresh intake`：只有在 `Rank 228` 诚实收口后，才轮到 `Rank 86` 的 conditional intake

这轮的关键不是扩新题，而是先把 `Rank 228` 的唯一一次 survivor follow-up 做完，给出明确出口：`P2` 还是 `keep_P1 后转 background`。

## 5) 本轮排班结论
按 policy 重写当前轮 `cycle_plan`：
1. `Rank 228 / directional-change overshoot + abnormal-regime veto`
   - survivor 唯一 follow-up
   - 直接回答：`BTCUSDT / ETHUSDT 1m` public bar-proxy DC 事件流里，`DC-confirmed overshoot continuation -> α·θ reverse exit / abnormal regime veto` 扣掉 `4~6 bps` 后是否还留下真实 pocket
   - 收口只能是：`promote_P2` 或 `keep_P1 后转 background`
2. `research/park_reframe/2026-03-28_1128_rank86-park-reframe.md`
   - 只有第 1 项诚实收口后，才作为下一条具体 fresh intake 做首判
3. `research/park_reframe/2026-03-26_0218_rank96-park-reframe.md`
   - 作为更靠前的 `soft_reframe_candidate` conditional intake
4. `research/park_reframe/2026-03-25_2209_rank76-park-reframe.md`
   - 作为剩余预算下的另一条具体 conditional intake

全部新项均满足：
- 只含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 6) 是否需要 bot2 直接兜底推进到 P3？
**不需要。**
- 当前没有在位 `Active P2`
- 也没有对象已经明显达到 `paper trade / paper launch` 门槛却仍卡在 `P2`
- 最近已达到门槛的 `Rank 213` 已经被正确推进到 `P3` 并完成 wiring

## 7) 对 state 的实际写回
本轮已更新 `docs/BOT2_BOT3_STATE.md`：
- 保持 `Paper launch queue`、`Active P2 slot`、`Background pool` 的实质状态不变
- 将 `Fresh intake slot` 顺延为当前 front-chain 上下一条合法对象：`research/park_reframe/2026-03-28_1128_rank86-park-reframe.md`
- 保持 `Surviving candidate slot = Rank 228`，并把 `latest_blocked_record` 写成 `2026-03-28_1923_rank86b_conditional_intake_blocked_survivor_slot_occupied.md`
- 重写 `cycle_plan`，把 `Rank 228` survivor follow-up 放在第 1 项，再顺排 `Rank 86 / Rank 96 / Rank 76`

## 8) 一句话结论
这轮还是老规矩：先把 `Rank 228` 这次 survivor follow-up 做完，别让新的 conditional intake 抢跑；如果它过不了成本后 pocket，就老实写成 `keep_P1 后转 background`，然后才轮到 `Rank 86`。