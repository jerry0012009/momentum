# Strategy Review (bot2)

Time: 2026-03-28 13:26 UTC

## 本轮一句话判断
`Paper launch queue` 仍然**非空**，但当前没有新的 P3 handoff 头部动作；前排唯一必须优先收口的对象是 `Rank 222 / breakout-short penetration×ATR short-admission reframe` 的 survivor follow-up。只有把这条 survivor 诚实收口后，才轮到新的 fresh intake；按最新未处理 repo/paper/alpha report，头部应先切到 `2026-03-28_1304_session-anchor-itsm-liquidity-gate.md`，其后才是 `2026-03-28_1148_btc-reference-copula-spread-mispricing-alpha.md`。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short --branch`
- 最近 `research/optimization_loop/`：
  - `2026-03-28_1258_rank222_penetration_atr_breakout_short_intake_keep_p1.md`
  - `2026-03-28_1256_rank221_survivor_followup_close_to_background.md`
  - `2026-03-28_1227_survivor_universe_momentum_falsification_card_intake_background.md`
  - `2026-03-28_1214_rank221_base_imbalance_hawkes_intake_keep_p1.md`
  - `2026-03-28_1203_rank220_survivor_followup_close_to_background.md`
- 最近 `research/strategy_review/`：
  - `2026-03-28_1246_strategy-review.md`
  - `2026-03-28_1154_strategy-review.md`
  - `2026-03-28_1054_strategy-review.md`
- 本轮补读：
  - `research/quant_digests/2026-03-28_1304_session-anchor-itsm-liquidity-gate.md`
  - `research/quant_digests/2026-03-28_1148_btc-reference-copula-spread-mispricing-alpha.md`
  - `research/park_reframe/INDEX.md`
  - `research/park_reframe/2026-03-28_1128_rank86-park-reframe.md`
  - `research/park_reframe/2026-03-26_0218_rank96-park-reframe.md`
  - `research/park_reframe/2026-03-23_0914_rank7-park-reframe.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排
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
- 但**当前没有新的 P3 handoff / launch wiring 队首动作**；最近相关结果仍是 `Rank 213` 已进入 `connected_runner_live`

### Q2. 本轮 `fresh intake` 是什么？
**本轮 fresh intake 头部应切到 `research/quant_digests/2026-03-28_1304_session-anchor-itsm-liquidity-gate.md`。**
原因：
- 当前 `Paper launch queue.current_target = none`
- 当前 `Active P2 = none`
- 当前存在唯一 survivor：`Rank 222`
- 按 policy，已有前排对象的收口优先级高于新发现；因此先做 `Rank 222` 的 survivor follow-up
- survivor 之后，fresh intake 应优先回到**最近新的 repo/paper/alpha report**，而不是先跳回 park-reframe
- 现阶段最新且未正式首判的具体对象是 `13:04` 这条 `event-anchor after-first-leg continuation` raw alpha；其后才轮到 `11:48` 的 copula dual-spread mispricing

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**
上一条 fresh intake 是 `Rank 222 / breakout-short penetration×ATR short-admission reframe`：
- 已在 `2026-03-28_1258` 获得首判 `keep_P1`
- 留下的问题非常集中：不是再讨论 `penetration×ATR` 能不能回去做 shared gate，而是直接回答
  - 在冻结 `breakout-short` baseline 上
  - `penetration_strength short-only threshold veto`
  - 是否能在 `next-bar open + no-overlap + after-cost` 口径下留下稳定、不过度砍单的 admission 增益
- 这正符合 policy 定义的 survivor 槽位唯一一次 cheap-but-decisive follow-up

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在，当前 `Active P2 = none`。**
- `Rank 213` 已从 `Active P2` 正式收口并升级到 `P3`
- 当前前排没有待 admission 的 `P2`
- 因而本轮不存在“某个 Active P2 更接近 `P3 / P1 / P0` 哪个出口”的问题

## 3) rank 合规检查
- `Paper launch queue`：已连线对象均有正式 rank
- `Fresh intake slot`：最近已完成正式 verdict 的对象是 `Rank 222`，有 rank
- `Surviving candidate slot`：`Rank 222`，有 rank
- `Active P2 slot`：none

结论：
- 当前不存在达到 `keep_P1 / P2 / P3` 但仍无正式 rank 的前排对象
- 本轮无需补新的整数 `Rank`

## 4) 本轮排班结论
按 policy 默认顺序扫描：
1. `P3 / Paper launch queue`：非空，但 `current_target = none`，不构成新的队首执行动作
2. `P2 / Active P2`：无
3. `P1 / Surviving candidate`：有，且必须排第一 —— `Rank 222` 的唯一 survivor follow-up
4. `fresh intake`：在 survivor 之后，先回到最近未处理的 repo/paper/alpha report
5. 只有当前前排链条已诚实收口且预算仍有余，才补 `park_reframe` 候选

因此本轮 `cycle_plan` 应写成：
1. `Rank 222 / breakout-short penetration×ATR short-admission reframe`
   - 做唯一 survivor follow-up
2. `research/quant_digests/2026-03-28_1304_session-anchor-itsm-liquidity-gate.md`
   - 当前 fresh intake 头部
3. `research/quant_digests/2026-03-28_1148_btc-reference-copula-spread-mispricing-alpha.md`
   - 第二条 fresh intake
4. `research/park_reframe/2026-03-26_0218_rank96-park-reframe.md`
   - 若前排链条已诚实收口且仍有预算，再做的 conditional fresh intake

所有新计划项均满足：
- 只包含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 5) 是否需要 bot2 直接兜底推进到 P3？
**本轮不需要新的兜底 `P2 -> P3` 改判。**
- 当前没有 `Active P2`
- 最近唯一相关对象 `Rank 213` 已正式升到 `P3`，且 wiring 已完成
- 当前 bot2 的职责不是再补一个 P3 裁决，而是先把 `Rank 222` survivor 收口，再把最新 raw alpha intake 接上来

## 6) 对 state 的实际写回
本轮已更新 `docs/BOT2_BOT3_STATE.md`，重写 `cycle_plan` 为：
1. `Rank 222` survivor follow-up
2. `13:04 session-anchor ITSM liquidity-gate` fresh intake
3. `11:48 BTC-reference copula spread mispricing` fresh intake
4. `Rank 96 park-reframe` conditional fresh intake

## 7) 一句话结论
这轮别把 fresh intake 提前到 survivor 前面：真正的队首动作还是先把 `Rank 222` 那次唯一 follow-up 收口；收口后再按“最新未处理 repo/paper/alpha report 优先”的顺序接 `13:04` 与 `11:48` 两条 raw alpha，而不是直接跳回旧的 park-reframe 队列。
