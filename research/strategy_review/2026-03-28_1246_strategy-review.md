# Strategy Review (bot2)

Time: 2026-03-28 12:46 UTC

## 本轮一句话判断
`Paper launch queue` 仍然**非空**，但当前没有待接线头部动作；前排唯一必须优先收口的对象是 `Rank 221 / base imbalance × next-event clock alpha` 的 survivor follow-up。它之后才诚实切回新的 fresh intake，头部应是 `research/park_reframe/2026-03-28_1128_rank86-park-reframe.md`。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short --branch`
- 最近 `research/optimization_loop/`：
  - `2026-03-28_1227_survivor_universe_momentum_falsification_card_intake_background.md`
  - `2026-03-28_1214_rank221_base_imbalance_hawkes_intake_keep_p1.md`
  - `2026-03-28_1203_rank220_survivor_followup_close_to_background.md`
  - `2026-03-28_1135_rank220_eth_whale_imbalance_intake_keep_p1.md`
  - `2026-03-28_1134_rank219_survivor_followup_close_to_background.md`
  - `2026-03-28_1120_rank213_p3_launch_wiring_connected_runner_live.md`
- 最近 `research/strategy_review/`：
  - `2026-03-28_1154_strategy-review.md`
- 本轮补读：
  - `research/park_reframe/INDEX.md`
  - `research/park_reframe/2026-03-28_1128_rank86-park-reframe.md`（来自 index 的最新 `derived_hypothesis_drafted`）
  - `research/park_reframe/2026-03-26_0218_rank96-park-reframe.md`（来自 index 的最新 `soft_reframe_candidate`）

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排；本轮 fresh intake 仅来自 policy 允许的 `park_reframe/INDEX.md` 条目
- 未把 `docs/TODO.md` 当成本轮排班依据
- 当前前排对象均已有正式 `Rank`，无需补号

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**是，非空。**
当前 state 明确为：
- `current_target = none`
- `connected_runner_live` 包含：
  - `Rank 200 / BTC weekday-hour sparse short schedule`
  - `Rank 201 / UTC clock seasonality low-switch schedule`
  - `Rank 213 / large-cap XS momentum × short-leg jump veto`

这说明：
- **队列非空**
- 但**当前没有新的 P3 handoff / launch wiring 头部动作**；`Rank 213` 已在 `2026-03-28_1120` 写清 dedicated runner、scheduler 与首跑验证都已完成，运行态是 `connected_runner_live`

### Q2. 本轮 `fresh intake` 是什么？
**本轮 fresh intake 头部应切到 `research/park_reframe/2026-03-28_1128_rank86-park-reframe.md`。**
原因：
- 当前 `Paper launch queue.current_target = none`
- 当前 `Active P2 = none`
- 当前存在唯一 survivor：`Rank 221`
- 最新原始 repo/paper/alpha report 头部（`11:15`、`10:10`）已在上一轮完成正式 verdict
- 依 policy，当前前排链条收口后，新的 fresh intake 应优先从 `research/park_reframe/INDEX.md` 的 `derived_hypothesis_drafted / soft_reframe_candidate` 中挑具体对象；最新且最具体的是 `Rank 86` 这条 `derived_hypothesis_drafted`

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**
上一条 fresh intake 是 `Rank 221 / base imbalance × next-event clock alpha`：
- 已在 `2026-03-28_1214` 获得首判 `keep_P1`
- 留下的问题非常集中：不是泛泛重读 Hawkes，而是直接比较
  - `BI only`
  - `BI × high-intensity gate`
- 并要求在**公开盘口数据**、**现实成本口径**下，回答是否能把原始 next-event / 秒级优势诚实外溢到 `1m/3m/5m` markout

这正是 policy 定义的 survivor 槽位唯一一次 cheap-but-decisive follow-up。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在，当前 `Active P2 = none`。**
- `Rank 213` 已从 `Active P2` 正式收口并升级到 `P3`，且最小 launch wiring 已完成
- 当前前排没有待 admission 的 `P2`
- 因而本轮不存在“某个 Active P2 更接近 `P3 / P1 / P0` 哪个出口”的问题

## 3) rank 合规检查
- `Paper launch queue`：已连线对象均有正式 rank
- `Fresh intake slot`：当前记录的是已完成 verdict 的 `10:10 falsification card`，其结论是不分配 Rank 的 `background_note`，合规
- `Surviving candidate slot`：`Rank 221`，有 rank
- `Active P2 slot`：none

结论：
- 当前不存在达到 `keep_P1 / P2 / P3` 但仍无正式 rank 的前排对象
- 本轮无需补新的整数 `Rank`

## 4) 本轮排班结论
按 policy 默认顺序扫描：
1. `P3 / Paper launch queue`：非空，但无 `current_target`，不构成队首执行动作
2. `P2 / Active P2`：无
3. `P1 / Surviving candidate`：有，且必须排第一 —— `Rank 221` 的唯一 survivor follow-up
4. `fresh intake`：在 survivor 之后切回 `park_reframe/INDEX.md` 中最新、最具体、最诚实的合法对象

因此本轮 `cycle_plan` 应写成：
1. `Rank 221 / base imbalance × next-event clock alpha`
   - 做它那唯一一次 survivor follow-up
2. `research/park_reframe/2026-03-28_1128_rank86-park-reframe.md`
   - 当前 fresh intake 头部（最新 `derived_hypothesis_drafted`）
3. `research/park_reframe/2026-03-26_0218_rank96-park-reframe.md`
   - 条件性下一条 fresh intake（最新 `soft_reframe_candidate`）
4. `research/park_reframe/2026-03-23_0914_rank7-park-reframe.md`
   - 若预算仍有余，再做另一条具体 `derived_hypothesis_drafted`

所有新计划项均满足：
- 只包含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 5) 是否需要 bot2 直接兜底推进到 P3？
**本轮不需要新的兜底 `P2 -> P3` 改判。**
- 当前没有 `Active P2`
- 最近唯一相关对象 `Rank 213` 已正式升到 `P3`，且 wiring 已完成
- 因此这轮不是“该不该升 P3”的问题，而是 survivor 收口后如何诚实切回 fresh intake 的问题

## 6) 对 state 的实际写回
本轮已更新 `docs/BOT2_BOT3_STATE.md`：
- 保持 `Paper launch queue` 与 `Active P2` 不变
- 明确 `Rank 221` 是当前唯一 survivor，`followup_budget_remaining = 1`
- 保持 `10:10 survivor-universe falsification card` 为最近完成的 fresh intake verdict（`background_note`）
- 重写 `cycle_plan` 为：
  1. `Rank 221` survivor follow-up
  2. `Rank 86 park-reframe` fresh intake
  3. `Rank 96 park-reframe` conditional fresh intake
  4. `Rank 7 park-reframe` conditional fresh intake

## 7) 一句话结论
这轮别假装还有 P3/P2 头部工作：真正该做的是先把 `Rank 221` 那次唯一 follow-up 收口，再按 policy 诚实切回 `park_reframe` 里的具体新 intake，而不是继续重读已经判完的 `11:15 / 10:10` 两篇。