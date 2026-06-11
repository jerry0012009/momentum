# Strategy Review (bot2)

Time: 2026-03-28 17:17 UTC

## 本轮一句话判断
`Paper launch queue` 仍然非空，但没有新的 `P3` 接线缺口；当前唯一明确前排对象是 `Rank 226` survivor，所以它的唯一一次 follow-up 必须排在最前。`stablecoin signed order-flow shock path` 现在只能作为 survivor 收口之后的下一条具体 fresh intake，不能越过 `Rank 226` 插队。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short --branch`
- 最近 `research/optimization_loop/`：
  - `2026-03-28_1700_stablecoin_orderflow_shock_path_alpha_blocked_front_slot_priority.md`
  - `2026-03-28_1648_rank226_iv_quantile_confirmation_gate_intake_keep_p1.md`
  - `2026-03-28_1626_rank225_survivor_followup_keep_p1_background.md`
  - `2026-03-28_1518_rank225_deribit_option_volume_shock_intake_keep_p1.md`
  - `2026-03-28_1120_rank213_p3_launch_wiring_connected_runner_live.md`
- 最近 `research/strategy_review/`：
  - `2026-03-28_1637_strategy-review.md`
  - `2026-03-28_1554_strategy-review.md`
  - `2026-03-28_1514_strategy-review.md`
  - `2026-03-28_1427_strategy-review.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改写 policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选拉回前排
- 未把 `docs/TODO.md` 当成本轮排班依据
- 当前前排对象不存在“达到 `keep_P1 / P2 / P3` 但无正式 rank”的违规项，因此本轮无需补号

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**是，非空。**
当前 state 仍记录：
- `current_target = none`
- `connected_runner_live` 包含 `Rank 200 / 201 / 213`

这说明 queue 不空，但最近证据没有出现新的 queue-head wiring 缺口，因此本轮没有需要抢到 `survivor` 之前的 `P3` 动作。

### Q2. 本轮 `fresh intake` 是什么？
**本轮应切到的下一条 fresh intake 是 `research/quant_digests/2026-03-28_1613_stablecoin-orderflow-shock-path-alpha.md`。**
但要注意：它**还不能立刻执行**，因为当前前排仍有 `Rank 226` 的 survivor follow-up。

理由：
- `research/quant_digests/2026-03-28_1433_iv-quantile-confirmation-gate.md` 已在 16:48 完成首判并拿到 `Rank 226`
- 它因此不再是待首判 fresh intake，而是当前合法 `Surviving candidate`
- 所以当前“下一条具体 fresh intake 头部”已经顺延到 `2026-03-28_1613_stablecoin-orderflow-shock-path-alpha.md`
- 17:00 的 blocked 日志也已经确认：它这轮没首判，不是对象失效，而是被前排 survivor 锁住

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**
上一条 fresh intake 是 `Rank 226 / IV quantile confirmation / veto`。

它值得那唯一一次 follow-up，因为：
1. 这条线已经被诚实界定为 **shared admission-veto gate**，不是冒充独立 raw alpha 的 filter 包装；
2. 它具备明确、便宜、可 decisive 的最小下一步：对现成 `5m/15m` continuation / fade baseline 做 BTC/ETH 同口径 after-cost A/B；
3. 当前缺口不是更多论文解读，而正是这一步实证：`iv_q × ivchg` 是否相对 baseline 留下独立净增益。

所以答案是：
- **值得那唯一一次 follow-up**；
- 而且这次 follow-up 现在就是当前前排第一优先级；
- 在它收口前，不该让 `stablecoin orderflow` 或其他 intake 插队。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在，当前 `Active P2 = none`。**
最近一个明确 `Active P2` 是 `Rank 213`，但它已经：
- 在 08:52 完成 `P2 -> P3` 升级
- 在 11:20 完成最小 `P3 launch wiring`
- 当前已写成 `connected_runner_live`

因此，本轮没有需要 bot2 兜底裁成 `P3 / P1 / P0` 的在位 `Active P2` 对象。

## 3) rank 合规检查
- `Paper launch queue`：`Rank 200 / 201 / 213`，都有正式 rank
- `Surviving candidate slot`：`Rank 226`，已有正式 rank
- `Active P2 slot`：`none`
- 下一条 fresh intake `stablecoin-orderflow-shock-path-alpha` 尚未首判，因此不应预先分配 rank

结论：
- 当前前排对象不存在缺 rank 的违规情况
- 本轮无需补新的整数 `Rank`

## 4) 当前前排判断
按 policy 里的默认优先顺序扫描：
1. `P3 / Paper launch queue`：非空，但无新的 queue-head 接线动作
2. `P2 / Active P2`：无
3. `P1 / Surviving candidate`：**有，而且就是 `Rank 226` 这一条合法前排动作**
4. `fresh intake`：只有在 `Rank 226` 诚实收口后，才轮到 `stablecoin signed order-flow shock path`

这意味着：
- 当前最该修的不是继续解释 `stablecoin orderflow` 有没有意思；
- 而是先把 `Rank 226` 的唯一 survivor follow-up 做完，给出明确出口：`P2` 还是 `keep_P1 后转 background`。

## 5) 本轮排班结论
按 policy 重写当前轮 `cycle_plan`：
1. `Rank 226 / IV quantile confirmation / veto`
   - survivor 唯一 follow-up
   - 直接回答：对现成 `5m/15m` continuation / fade baseline 的 BTC/ETH 同口径 after-cost A/B 中，`iv_q × ivchg` 是否留下独立净增益
   - 收口只能是：`promote_P2` 或 `keep_P1 后转 background`
2. `research/quant_digests/2026-03-28_1613_stablecoin-orderflow-shock-path-alpha.md`
   - 只有第 1 项诚实收口后，才作为下一条具体 fresh intake 做首判
3. `research/park_reframe/2026-03-28_1128_rank86-park-reframe.md`
   - 作为 `derived_hypothesis_drafted` conditional intake，排在 survivor 与更近 fresh intake 之后
4. `research/park_reframe/2026-03-26_0218_rank96-park-reframe.md`
   - 作为 `soft_reframe_candidate` conditional intake，继续放在本轮尾部补预算

全部新项均满足：
- 只含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 6) 是否需要 bot2 直接兜底推进到 P3？
**不需要。**
- 当前没有在位 `Active P2`
- 也没有对象已经清楚达到 `paper trade / paper launch` 门槛却仍卡在 `P2`
- 最近已达到该门槛的 `Rank 213` 已经被正确推进到 `P3` 并完成 wiring

## 7) 对 state 的实际写回
本轮已更新 `docs/BOT2_BOT3_STATE.md`：
- 保持 `Paper launch queue`、`Fresh intake slot`、`Surviving candidate slot`、`Active P2 slot` 的实质状态不变
- 只重写 `cycle_plan`，把 `Rank 226` survivor follow-up 提到第 1 项
- 把 `stablecoin-orderflow-shock-path-alpha` 下移为 survivor 收口后的下一条具体 fresh intake

## 8) 一句话结论
这轮别再让新题抢跑了：`Rank 226` 既然已经拿到 `keep_P1` 并占住 survivor 槽，就该先用那唯一一次 A/B follow-up 诚实收口；收口完，才轮到 `stablecoin signed order-flow shock path` 做 fresh intake 首判。
