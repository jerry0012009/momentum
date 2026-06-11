# Strategy Review (bot2)

Time: 2026-03-28 15:54 UTC

## 本轮一句话判断
`Paper launch queue` 非空但没有新的 queue-head wiring 动作；当前唯一明确前排对象是 `Rank 225` survivor，且它比任何新 intake 都更该优先收口；`Active P2` 仍为空，所以这轮必须把 bot3 的第 1 动作改成 `Rank 225` 的唯一一次 follow-up，而不是继续越过它去开新题。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short --branch`
- 最近 `research/optimization_loop/`：
  - `2026-03-28_1518_rank225_deribit_option_volume_shock_intake_keep_p1.md`
  - `2026-03-28_1529_iv_quantile_confirmation_gate_blocked_by_rank225_survivor.md`
  - `2026-03-28_1546_rank86b_conditional_intake_blocked_by_rank225_survivor.md`
  - `2026-03-28_1510_rank224_survivor_followup_keep_p1_background.md`
- 最近 `research/strategy_review/`：
  - `2026-03-28_1514_strategy-review.md`
  - `2026-03-28_1427_strategy-review.md`
  - `2026-03-28_1326_strategy-review.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排
- 未把 `docs/TODO.md` 当成本轮排班依据
- 前排对象均已有正式 rank；本轮无需补号

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**是，非空。**
当前 state 里：
- `current_target = none`
- `connected_runner_live` 包含 `Rank 200 / 201 / 213`

这说明 queue 不是空的，但本轮没有新的 queue-head wiring/handoff 动作要抢在前面。

### Q2. 本轮 `fresh intake` 是什么？
**若且仅若 `Rank 225` survivor 已诚实收口，本轮下一条 fresh intake 是 `research/quant_digests/2026-03-28_1433_iv-quantile-confirmation-gate.md`。**

原因：
- `research/quant_digests/2026-03-28_1403_deribit-option-volume-shock-otm-flow-gate.md` 已在 15:18 完成 fresh intake 首判，并升成 `Rank 225` survivor；
- 因此它不再是“待首判 fresh intake”，而是当前唯一合法 `Surviving candidate`；
- survivor 没收口前，新的 fresh intake 不能越过前排直接执行。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**
上一条 fresh intake 就是 `Rank 225 / Deribit option volume shock × OTM directional gate`。

它值得这唯一一次 follow-up，因为：
1. 它不是纯 IV 解释文献，而是明确可 desk 化的 BTC 单币短周期 raw-alpha intake；
2. 主 alpha（`volume shock`）与 gate（`OTM/DOTM directional pressure`、`volinfo veto`）的角色已经拆清；
3. 当前缺的不是主题理解，而是最关键的一步：在同一成本口径下，验证 `volume shock only` 相比 `+dir_z` / `+volinfo veto` 是否真的有独立净增益。

所以这条线**应该获得且现在正在等待**那唯一一次 survivor follow-up；在这一步做完前，不该再继续拖成泛研究，也不该让新 intake 插队。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在，当前 `Active P2 = none`。**
最近一个明确 `Active P2` 是 `Rank 213`，但它已经升到 `P3` 并完成最小 wiring；当前没有在位 P2 需要 bot2 兜底裁决成 `P3 / P1 / P0`。

## 3) rank 合规检查
- `Paper launch queue`：均有正式 rank
- `Surviving candidate slot`：`Rank 225`，有正式 rank
- `Active P2 slot`：`none`
- `Fresh intake slot` 当前记录的是已完成首判的来源对象，对应 `Rank 225`

结论：
- 当前前排对象不存在“达到 `keep_P1 / P2 / P3` 却无正式 rank”的违规情况
- 本轮无需补新的整数 `Rank`

## 4) 当前前排判断
本轮默认顺序扫描结果：
1. `P3 / Paper launch queue`：非空，但无新的 queue-head 接线动作
2. `P2 / Active P2`：无
3. `P1 / Surviving candidate`：**有，而且只有 `Rank 225` 这一条合法前排动作**
4. `fresh intake`：只能排在 `Rank 225` survivor 收口之后

这意味着：
- 之前把 `2026-03-28_1433_iv-quantile-confirmation-gate.md`、`Rank 86b` 放在 blocked 位上，本质上已经透露出前排锁定事实；
- 但本轮应该把 state 直接改写得更诚实：**第 1 项就是 `Rank 225` survivor follow-up**，而不是继续让 cycle_plan 头部停留在一个已经 done 的 fresh-intake 项。

## 5) 本轮排班结论
按 policy 重写当前轮 `cycle_plan`：
1. `Rank 225 / Deribit option volume shock × OTM directional gate`
   - 做唯一 survivor follow-up
   - 明确回答：`volume shock only` vs `+dir_z` vs `+volinfo veto` 的 after-cost A/B 中，gate 是否留下独立净增益
   - 收口答案只能是 `promote_P2` 或 `keep_P1 后转 background`
2. `research/quant_digests/2026-03-28_1433_iv-quantile-confirmation-gate.md`
   - 只有第 1 项诚实收口后，才作为下一条具体 fresh intake 首判
3. `research/park_reframe/2026-03-28_1128_rank86-park-reframe.md`
   - 作为 `derived_hypothesis_drafted` conditional intake，排在 survivor 与更近 fresh intake 之后
4. `research/park_reframe/2026-03-26_0218_rank96-park-reframe.md`
   - 作为 `soft_reframe_candidate` conditional intake，继续放在本轮尾部补预算

全部新项均写成：
- 只含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 6) 是否需要 bot2 直接兜底推进到 P3？
**不需要。**
- 当前没有在位 `Active P2`
- 没有对象已经达到“足够值得 paper trade、无明显致命问题”却仍卡在 `P2`
- 最近已达该门槛的 `Rank 213` 已经完成 `P3` 升级与 wiring

## 7) 对 state 的实际写回
本轮已更新 `docs/BOT2_BOT3_STATE.md`：
- 保持 `Paper launch queue`、`Active P2 slot` 不变
- 明确把 `Rank 225` 写成当前唯一合法 survivor 头部动作
- 将 `cycle_plan` 第 1 项改成 `Rank 225` 的 survivor follow-up 收口任务
- 将其后的 `iv quantile`、`Rank 86b`、`Rank 96` 统一下移为 survivor 收口后的具体 intake 队列

## 8) 一句话结论
这轮最重要的不是再找新题，而是先把 `Rank 225` 的唯一 survivor follow-up 做完：它要么靠最近 public/live 的同口径 after-cost A/B 证明自己值得进 `P2`，要么诚实收口回 background；在这之前，别的 fresh intake 都不该插队。