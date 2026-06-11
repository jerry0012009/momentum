# Strategy Review (bot2)

Time: 2026-03-28 14:27 UTC

## 本轮一句话判断
`Paper launch queue` 仍然非空；当前没有 `Active P2`；最新 fresh intake 是 `Rank 224`，所以唯一合法的 survivor 也必须切到 `Rank 224`。`Rank 223` 虽然本身仍是 `keep_P1`，但已不再合法占用 survivor 槽位，本轮已把它退回 background 以恢复 runtime 与 policy 一致性。当前队首动作是先把 `Rank 224` 的唯一 follow-up 诚实收口，再切到新的 fresh intake：`2026-03-28_1403_deribit-option-volume-shock-otm-flow-gate.md`。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short --branch`
- 最近 `research/optimization_loop/`：
  - `2026-03-28_1424_rank224_btc_reference_copula_spread_intake_keep_p1.md`
  - `2026-03-28_1400_rank223_session_anchor_itsm_intake_keep_p1.md`
  - `2026-03-28_1332_rank222_survivor_followup_close_to_background.md`
  - `2026-03-28_1120_rank213_p3_launch_wiring_connected_runner_live.md`
- 最近 `research/strategy_review/`：
  - `2026-03-28_1326_strategy-review.md`
  - `2026-03-28_1246_strategy-review.md`
  - `2026-03-28_1154_strategy-review.md`
- 本轮补读：
  - `research/quant_digests/2026-03-28_1403_deribit-option-volume-shock-otm-flow-gate.md`
  - `research/park_reframe/INDEX.md`

硬约束遵守：
- 只更新了 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排
- 未把 `docs/TODO.md` 当成本轮排班依据
- 当前前排对象均已有正式 `Rank`，无需补号

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**是，非空。**
当前 state 里：
- `current_target = none`
- `connected_runner_live` 包含 `Rank 200 / 201 / 213`

这表示：
- 队列并不空；
- 但当前没有新的 queue-head wiring 动作要先于前排 survivor / intake 执行。

### Q2. 本轮 `fresh intake` 是什么？
**本轮 fresh intake 头部应切到 `research/quant_digests/2026-03-28_1403_deribit-option-volume-shock-otm-flow-gate.md`。**
原因：
- `Paper launch queue` 没有新的 `current_target`
- `Active P2 = none`
- 最新 fresh intake `Rank 224` 已完成首判并应接管 survivor 槽
- 因此 survivor 之后，fresh intake 应优先回到最近新的 repo/paper/alpha report；当前最近且未首判的就是 `14:03` 这条 Deribit options flow 线。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**
上一条 fresh intake 是 `Rank 224 / BTC reference + dual-spread copula conditional mispricing`。
它不是旧 pairs/z-score 家族的简单换皮，而是一个确实不同的 `signal-layer upgrade`：交易的是 `BTC` 参考腿下两条 spread 的相对误价，而不是单 spread 的经典回归。

但它仍只到 `keep_P1`，因为还缺最关键的一刀：
- 在同一 formation/trading split、同一成本口径下，
- 正面对照 `single-spread z-score` / `dual-spread plain threshold or z-score` / `dual-spread copula conditional mispricing`
- 直接回答 copula 条件误价这层是否真的带来独立净增益。

这正是 cheap 且 decisive 的唯一 follow-up，值得给它那一次前排机会。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在，当前 `Active P2 = none`。**
- `Rank 213` 已经从 `Active P2` 升到 `P3` 并完成 wiring
- 当前没有需要 bot2 兜底裁成 `P3 / P1 / P0` 的在位 `P2`

## 3) rank 合规检查
- `Paper launch queue`：均已有正式 rank
- `Fresh intake slot`：`Rank 224`，已有 rank
- `Surviving candidate slot`：本轮改正为 `Rank 224`，已有 rank
- `Active P2 slot`：none

结论：
- 当前不存在达到 `keep_P1 / P2 / P3` 但仍无正式 rank 的前排对象
- 本轮无需补新的整数 `Rank`

## 4) 本轮 runtime 纠偏
上一轮 runtime 出现了一处和 policy 不一致的地方：
- `Fresh intake slot` 已经是 `Rank 224`
- 但 `Surviving candidate slot` 仍停在 `Rank 223`

这违反了 policy 的硬定义：
> `Surviving candidate` 只能是上一条 fresh intake。

因此本轮做了纠偏：
1. 把 survivor 槽位改写为 `Rank 224`
2. 把 `Rank 223` 从前排退出，写回 background
3. 明确 `Rank 223` 未来只可在 human 明确 reopen 时再继续那条 anchor-only A/B，不再以 runtime 漂移方式滞留前排

这一步不是否定 `Rank 223` 的 `keep_P1` 结论，而是恢复前排身份的一致性，避免 survivor 槽位被覆盖后继续“假装没发生”。

## 5) 本轮排班结论
按 policy 默认顺序扫描：
1. `P3 / Paper launch queue`：非空，但无新的 `current_target`，无 queue-head 动作
2. `P2 / Active P2`：无
3. `P1 / Surviving candidate`：有，且必须排第一 —— `Rank 224` 的唯一 follow-up
4. `fresh intake`：回到最近新 repo/paper/alpha report，头部为 `14:03` Deribit options flow
5. 若预算仍有余，再补 park-reframe 中更具体的 candidate，优先 `Rank 86`，其后 `Rank 96`

因此本轮 `cycle_plan` 重写为：
1. `Rank 224 / BTC reference + dual-spread copula conditional mispricing`
   - survivor 唯一 follow-up：同口径对照 copula vs plain baselines
2. `research/quant_digests/2026-03-28_1403_deribit-option-volume-shock-otm-flow-gate.md`
   - 当前 fresh intake 头部
3. `research/park_reframe/2026-03-28_1128_rank86-park-reframe.md`
   - `derived_hypothesis_drafted` 条目；但只在前两项已诚实排入后才做
4. `research/park_reframe/2026-03-26_0218_rank96-park-reframe.md`
   - `soft_reframe_candidate` 条目；预算仍有余时再做

所有新计划项均满足：
- 只包含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 6) 是否需要 bot2 直接兜底推进到 P3？
**本轮不需要。**
- 当前没有 `Active P2`
- 最近唯一相关对象 `Rank 213` 已经升到 `P3` 且完成最小 wiring
- 因此本轮 bot2 的正确动作不是再补一刀 P3 裁决，而是修正 survivor 槽位、重写本轮排班

## 7) 对 state 的实际写回
本轮已更新 `docs/BOT2_BOT3_STATE.md`：
- `Surviving candidate slot`：从 `Rank 223` 改为 `Rank 224`
- `Background pool.latest_parked`：改写为 `Rank 223` 的 runtime 退场说明
- `cycle_plan`：重写为 `Rank 224 survivor > Deribit options flow fresh intake > Rank 86 conditional intake > Rank 96 conditional intake`

## 8) 一句话结论
这轮真正要先做的不是再往前塞新对象，而是把前排身份纠正过来：`Rank 224` 既然是最新 fresh intake 的 `keep_P1`，它就必须拿到唯一 survivor 槽；修正完以后，再把新的 desk 视线切到 `14:03` 那条 Deribit BTC options volume shock raw alpha。