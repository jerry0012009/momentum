# Strategy Review (bot2)

Time: 2026-03-28 11:54 UTC

## 本轮一句话判断
`Paper launch queue` 仍然**非空但已无待接线头部动作**；当前前排唯一真实可执行动作是 `Rank 220` 的 survivor follow-up，因此这轮必须先把它诚实收口，再切回新的 fresh intake，头部是 `2026-03-28_1115_base-imbalance-hawkes-eventtime-alpha.md`。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short --branch`
- 最近 `research/optimization_loop/`：
  - `2026-03-28_1135_rank220_eth_whale_imbalance_intake_keep_p1.md`
  - `2026-03-28_1134_rank219_survivor_followup_close_to_background.md`
  - `2026-03-28_1120_rank213_p3_launch_wiring_connected_runner_live.md`
  - `2026-03-28_1052_rank219_liquidity_ranked_ema_trend_intake_keep_p1.md`
  - `2026-03-28_1031_rank218_drift_hyperliquid_basis_intake_keep_p1.md`
- 最近 `research/strategy_review/`：
  - `2026-03-28_1054_strategy-review.md`
- 本轮补读：
  - `research/quant_digests/2026-03-28_1115_base-imbalance-hawkes-eventtime-alpha.md`
  - `research/quant_digests/2026-03-28_1010_survivor-universe-momentum-falsification-card.md`
  - `research/park_reframe/INDEX.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排
- 未把 `docs/TODO.md` 当成本轮排班依据
- 本轮前排对象已有正式 `Rank`，无需补号

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**是，非空。**
但当前语义不是“有待接线头部对象”，而是：
- `current_target = none`
- `connected_runner_live` 已包含：
  - `Rank 200 / BTC weekday-hour sparse short schedule`
  - `Rank 201 / UTC clock seasonality low-switch schedule`
  - `Rank 213 / large-cap XS momentum × short-leg jump veto`
- 最近结果明确写着 `Rank 213` 已完成 dedicated runner、scheduler 与首跑验证，运行态已是 `connected_runner_live`

所以：
- **队列非空**
- **但本轮没有新的 P3 wiring 动作排在最前**

### Q2. 本轮 `fresh intake` 是什么？
**本轮 fresh intake 头部应切到 `research/quant_digests/2026-03-28_1115_base-imbalance-hawkes-eventtime-alpha.md`。**
原因：
- 当前不存在 `Active P2`
- 当前没有待接线的 `Paper launch queue.current_target`
- 当前存在明确 survivor：`Rank 220`
- 在 survivor 之后，最近新的 repo / paper / alpha report 里，`11:15` 这篇 Hawkes LOB digest 是最新且尚未首判的合法具体 intake 对象

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**
上一条 fresh intake 是 `Rank 220 / ETH whale balance imbalance alpha`：
- 已在 `2026-03-28_1135` 获得首判 `keep_P1`
- 留下的问题足够集中，不是泛泛“whale story 还行不行”，而是：
  - 能否用**公开可重建**的 `large-vs-small cohort proxy`
  - 把 `imbalance = z(Δlarge) - z(Δsmall)`
  - 诚实地落到 ETH 上 `15m/30m/60m/240m`、现实成本口径下的事件漂移
- 这正符合 policy 对 survivor 槽位的唯一一次 cheap-but-decisive follow-up 定义

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在，当前 `Active P2 = none`。**
- `Rank 213` 已从 `Active P2` 收口并升级到 `P3`，且接线也已完成
- 当前前排没有待 admission 的 `P2`
- 因此本轮不存在 “某个 Active P2 更靠近 `P3 / P1 / P0` 哪个出口” 的问题

## 3) rank 合规检查
- `Paper launch queue`：虽非空，但当前都是已连线对象；无未编号前排对象
- `Fresh intake slot`：`Rank 220`，有 rank
- `Surviving candidate slot`：`Rank 220`，有 rank
- `Active P2 slot`：none

结论：
- 当前不存在达到 `keep_P1 / P2 / P3` 但仍无正式 rank 的前排对象
- 本轮无需补新的整数 `Rank`

## 4) 本轮排班结论
按 policy 默认顺序扫描：
1. `P3 / Paper launch queue`：非空，但当前没有待接线的 `current_target`，不构成新的队首执行动作
2. `P2 / Active P2`：无
3. `P1 / Surviving candidate`：有，且必须排第一 —— `Rank 220` 的唯一 survivor follow-up
4. `fresh intake`：在 survivor 之后，切回最近未处理的具体对象
5. 若仍有预算，再补 1 条合规 conditional intake

因此本轮 `cycle_plan` 应写成：
1. `Rank 220 / ETH whale balance imbalance alpha`
   - 做唯一一次 survivor follow-up
2. `research/quant_digests/2026-03-28_1115_base-imbalance-hawkes-eventtime-alpha.md`
   - 当前 fresh intake 头部
3. `research/quant_digests/2026-03-28_1010_survivor-universe-momentum-falsification-card.md`
   - 条件性下一条 fresh intake
4. `research/park_reframe/2026-03-28_1128_rank86-park-reframe.md`
   - 若前排链条已诚实收口且仍有预算，再做来自 `derived_hypothesis_drafted` 的 conditional fresh intake

所有新计划项均满足：
- 只包含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 5) 是否需要 bot2 直接兜底推进到 P3？
**本轮不需要新的兜底 P2->P3 改判。**
- 最近唯一相关对象 `Rank 213` 已在 state 中完成 `P2 -> P3`
- 且 `2026-03-28_1120` 已完成最小 launch wiring，当前不是“该不该升 P3”的问题，而是已正式连线完成后的前排收口

## 6) 对 state 的实际写回
本轮已更新 `docs/BOT2_BOT3_STATE.md`，重写 `cycle_plan` 为：
1. `Rank 220` survivor follow-up
2. `11:15 base-imbalance Hawkes event-time alpha` fresh intake
3. `10:10 survivor-universe falsification card` fresh intake
4. `11:28 Rank 86 park-reframe` conditional fresh intake

## 7) 一句话结论
这轮前排已经没有可继续拖的 P3/P2；真正该做的是先把 `Rank 220` 那次唯一 follow-up 做完，再把 freshest 的 Hawkes LOB 微结构 raw alpha 接进 fresh intake。