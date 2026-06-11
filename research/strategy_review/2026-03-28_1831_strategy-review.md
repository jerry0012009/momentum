# Strategy Review (bot2)

Time: 2026-03-28 18:31 UTC

## 本轮一句话判断
`Paper launch queue` 仍然非空，但没有新的 `P3` 接线缺口；当前唯一明确前排对象是 `Rank 227` survivor，所以它的唯一一次 follow-up 必须排在最前。`directional-change overshoot + abnormal-regime veto` 现在只能作为 `Rank 227` 诚实收口之后的下一条具体 fresh intake，不能插队到 survivor 前面。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short`
- 最近 `research/optimization_loop/`：
  - `2026-03-28_1823_rank227_stablecoin_orderflow_shock_path_intake_keep_p1.md`
  - `2026-03-28_1747_rank226_survivor_followup_keep_p1_background.md`
  - `2026-03-28_1700_stablecoin_orderflow_shock_path_alpha_blocked_front_slot_priority.md`
  - `2026-03-28_1648_rank226_iv_quantile_confirmation_gate_intake_keep_p1.md`
- 最近 `research/strategy_review/`：
  - `2026-03-28_1717_strategy-review.md`
  - `2026-03-28_1637_strategy-review.md`
- 新 intake 候选证据：
  - `research/quant_digests/2026-03-28_1755_directional-change-overshoot-abnormal-regime-alpha.md`
  - `research/park_reframe/INDEX.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改写 policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排
- 未把 `docs/TODO.md` 当成本轮排班依据
- 当前前排对象不存在“达到 `keep_P1 / P2 / P3` 却无正式 rank”的违规项，因此本轮无需补号

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**是，非空。**
当前 state 仍记录：
- `current_target = none`
- `connected_runner_live` 包含 `Rank 200 / 201 / 213`

这说明 queue 不空，但最近证据没有出现新的 queue-head wiring 缺口，因此本轮没有需要抢到 survivor 之前的 `P3` 动作。

### Q2. 本轮 `fresh intake` 是什么？
**本轮 fresh intake 头部是 `research/quant_digests/2026-03-28_1755_directional-change-overshoot-abnormal-regime-alpha.md`。**

原因：
- `research/quant_digests/2026-03-28_1613_stablecoin-orderflow-shock-path-alpha.md` 已在 18:23 完成首判并拿到 `Rank 227`
- 它因此不再是待首判 fresh intake，而是当前合法 `Surviving candidate`
- 所以当前“下一条具体 fresh intake 头部”已经顺延到 17:55 的 directional-change digest
- 这条线是新的 raw-alpha/object 级候选，不是 background pool reopen

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**
上一条 fresh intake 是 `Rank 227 / stablecoin signed-flow shock path alpha`。

它值得那唯一一次 follow-up，因为：
1. 这条线保留下来的不是 generic stablecoin 叙事，而是明确的 **event-level signed-flow shock -> continuation / decay fade** 微结构路径；
2. 当前失败主要来自把它压成 `1m` kline proxy 后，BTC/ETH 两条腿都过不了 `4~6 bps` 成本门槛，而不是逻辑自相矛盾；
3. 它仍有一条便宜、具体、decisive 的最小下一步：用 public `aggTrades` / taker buy-sell volume 重建 event-time shock，看更细事件定义下是否留下稳定 pocket。

所以答案是：
- **值得那唯一一次 follow-up**；
- 而且这次 follow-up 现在就是当前前排第一优先级；
- 在它收口前，不该让 `directional-change` 或其他 intake 插队。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在，当前 `Active P2 = none`。**
最近一个明确 `Active P2` 是 `Rank 213`，但它已经：
- 在 08:52 完成 `P2 -> P3` 升级；
- 在 11:20 完成最小 `P3 launch wiring`；
- 当前已写成 `connected_runner_live`。

因此，本轮没有需要 bot2 兜底裁成 `P3 / P1 / P0` 的在位 `Active P2` 对象。

## 3) rank 合规检查
- `Paper launch queue`：`Rank 200 / 201 / 213`，都有正式 rank
- `Surviving candidate slot`：`Rank 227`，已有正式 rank
- `Active P2 slot`：`none`
- 下一条 fresh intake `directional-change-overshoot-abnormal-regime-alpha` 尚未首判，因此不应预先分配 rank

结论：
- 当前前排对象不存在缺 rank 的违规情况
- 本轮无需补新的整数 `Rank`

## 4) 当前前排判断
按 policy 里的默认优先顺序扫描：
1. `P3 / Paper launch queue`：非空，但无新的 queue-head 接线动作
2. `P2 / Active P2`：无
3. `P1 / Surviving candidate`：**有，而且就是 `Rank 227` 这一条合法前排动作**
4. `fresh intake`：只有在 `Rank 227` 诚实收口后，才轮到 `directional-change overshoot + abnormal-regime veto`

这意味着：
- 当前最该修的不是继续扩新题；
- 而是先把 `Rank 227` 的唯一 survivor follow-up 做完，给出明确出口：`P2` 还是 `keep_P1 后转 background`。

## 5) 本轮排班结论
按 policy 重写当前轮 `cycle_plan`：
1. `Rank 227 / stablecoin signed-flow shock path alpha`
   - survivor 唯一 follow-up
   - 直接回答：用 public `aggTrades` / taker buy-sell volume 重建 event-level shock 后，`shock continuation` 与 `shock-decay fade` 两条腿在 `BTCUSDT / ETHUSDT` 的 `1m/3m/5m/15m` markout 中，是否有任一腿能穿过 `4~6 bps`
   - 收口只能是：`promote_P2` 或 `keep_P1 后转 background`
2. `research/quant_digests/2026-03-28_1755_directional-change-overshoot-abnormal-regime-alpha.md`
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
- 保持 `Paper launch queue`、`Active P2 slot`、`Background pool` 的实质状态不变
- 把 `Fresh intake slot` 头部改写为下一条具体对象：`2026-03-28_1755_directional-change-overshoot-abnormal-regime-alpha.md`
- 保持 `Surviving candidate slot = Rank 227`，并把 survivor 描述改成“值得唯一一次 follow-up，但还不够升 `P2`”
- 重写 `cycle_plan`，把 `Rank 227` survivor follow-up 提到第 1 项，并把 directional-change digest 写成 survivor 收口后的下一条具体 fresh intake

## 8) 一句话结论
这轮别让新题抢跑：`Rank 227` 既然已经拿到 `keep_P1` 并占住 survivor 槽，就该先用那唯一一次 event-time follow-up 诚实收口；收口完，才轮到 directional-change overshoot 这条新的 raw alpha 做 fresh intake 首判。
