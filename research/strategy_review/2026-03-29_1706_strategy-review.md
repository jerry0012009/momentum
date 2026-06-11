# Strategy Review (bot2)

Time: 2026-03-29 17:06 UTC

## 本轮一句话判断
`Paper launch queue` 为空；当前最新 fresh intake 仍是 `Rank 240`，且它已锁定唯一 survivor 槽位；上一条 fresh intake `Rank 239` 的唯一 follow-up 已经用尽并回 `background/P0`；当前不存在 `Active P2`，因此本轮默认顺序只能是：先把 `Rank 240` 的 survivor 收口，再切回新的具体 fresh intake，而不是 reopen 更早对象。

## 1) 本轮读取与边界
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short`
- 最近 `research/optimization_loop/`：
  - `2026-03-29_1630_rank240_stablecoin_depeg_jump_risk_overlay_keep_p1.md`
  - `2026-03-29_1605_rank239_survivor_followup_background.md`
  - `2026-03-29_1424_rank239_first_verdict_keep_p1_pair_rebalancing_threshold_map.md`
  - `2026-03-29_1230_rank235_p2_exit_rescope_p1_honesty_gap.md`
- 最近 `research/strategy_review/`：
  - `2026-03-29_1504_strategy-review.md`
- 为 fresh intake 重排，又补读：
  - `research/quant_digests/2026-03-29_1619_amm-book-slippage-veto-sameasset-leadlag.md`
  - `research/park_reframe/INDEX.md`
  - `research/park_reframe/2026-03-28_1128_rank86-park-reframe.md`
  - `research/park_reframe/2026-03-29_0703_rank64-park-reframe.md`

硬约束遵守：
- 本轮只更新 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排
- 未把 `docs/TODO.md` 当排班依据
- 当前前排对象都有正式 `Rank`，无需补新的整数 `Rank`

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**否。**

当前 state：
- `Paper launch queue.current_target = none`
- `connected_runner_live` 仍是 `Rank 200 / 201 / 213 / 229`
- 最近没有新的 queue 头对象等待接线

所以本轮没有合法的 `P3 launch wiring` 默认优先项。

### Q2. 本轮 `fresh intake` 是什么？
**本轮 fresh intake 是 `Rank 240 / stablecoin depeg jump-risk shared overlay`。**

依据：
- `research/optimization_loop/2026-03-29_1630_rank240_stablecoin_depeg_jump_risk_overlay_keep_p1.md`
- 它是最新一条完成 first verdict 且仍在当前运行链条里的 fresh intake
- 依 policy，最新一条 fresh intake 若首判为 `keep_P1`，其 survivor follow-up 享有前排锁定位

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**不值得再给。**

这里的“上一条 fresh intake”是 `Rank 239 / pair-rebalancing MR × correlation-signed threshold map`。

原因不是它没被检查，而是：
- 它的唯一 survivor follow-up 已在 `2026-03-29_1605_rank239_survivor_followup_background.md` 完成；
- `corr-bucket threshold map` 实际退化成“高相关 pair 用更低固定阈值”的弱结论，没有相对最佳固定低阈值 baseline 留下 post-cost 增量；
- 因此它已经诚实用尽唯一 follow-up 预算，并回 `background/P0`。

换句话说：
- `Rank 239` 这条线已经收口；
- 当前唯一合法 survivor 锁位必须给最新的 `Rank 240`，不能再回头给 `Rank 239` 第二次机会。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**当前不存在明确 `Active P2`。**

原因：
- `Rank 235` 已在 `2026-03-29_1230_rank235_p2_exit_rescope_p1_honesty_gap.md` 中正式写成 `one-time P2 -> P1 re-scope`
- state 里也已写明 `Active P2 = none`
- `Rank 239` 已回 `background/P0`
- `Rank 240` 目前只是 `keep_P1` survivor，不是 `P2`

因此本轮默认顺序只能回到：
1. `Rank 240` survivor 唯一一次 follow-up
2. 再补新的 fresh intake

## 3) P3 兜底判断
本轮专门核对了 policy 的兜底要求：若某个 `Active P2` 已明显够格 `P3`，bot2 必须直接推进。

结论：**本轮不触发。**

原因：
- 当前 `Active P2 = none`
- 最近最接近 `P3` 的 `Rank 235` 已被最新 honesty 审计明确打回 `one-time P2 -> P1 re-scope`
- `Rank 239` 已回 `background/P0`
- `Rank 240` 仍停在 `P1`

所以这轮没有任何对象符合“desk review 已清楚表明足够进入 paper trade，但 bot3 尚未升级”的条件。

## 4) rank 合规检查
- `Paper launch queue / connected_runner_live`：现有对象均带 rank
- `Fresh intake slot`：`Rank 240`
- `Surviving candidate slot`：`Rank 240`
- `Active P2 slot`：`none`

结论：**本轮无需补新的 `Rank`。**

## 5) 本轮 `cycle_plan` 重写逻辑
按 policy 默认顺序，合法动作扫描结果是：
1. **P3 handoff**：无 queue 头，跳过
2. **P2 admission/promote/park**：无 `Active P2`，跳过
3. **P1 survivor**：`Rank 240` 是当前唯一合法 survivor，必须排第 1
4. **fresh intake**：只有在第 1 项已诚实排入后，才能切回新的具体 intake

因此本轮把 `cycle_plan` 重写为 4 项：
1. `Rank 240` survivor follow-up
2. `AMM executable-price reconstruction × slippage/gas veto for same-asset lead-lag`
3. `Rank 86 park residual -> breakout-short-specific short-side admission score / veto`
4. `Rank 64 park residual -> long-side-only hold-quality admission score`

这样排的原因：
- 当前没有 `P3`、没有 `Active P2`
- `Rank 240` 作为最新 survivor 享有前排锁位，必须先收口
- 之后第一个 fresh intake 优先选最近新的 alpha 报告：`2026-03-29_1619_amm-book-slippage-veto-sameasset-leadlag.md`
- 剩余预算再补 policy 允许的 `park_reframe/derived_hypothesis_drafted`：`Rank 86b` 与 `Rank 64b` 方向
- `Rank 86` 放在 `Rank 64` 前面，是因为它更贴近当前 desk 的 breakout-short / admission family，且 distinctness 问题比 `Rank 64` 更值得先回答

## 6) 对四个 pending 小点的具体判断
### 6.1 Rank 240 survivor follow-up
当前最该回答的问题不是“stablecoin depeg 很危险”，而是：
- 用 frozen `downward-only` threshold 与 `30m/60m` 窗口后，接到至少一类现有短周期策略时，是否留下了真正的 `with overlay vs without overlay` 净改进；
- 而且要显式区分“少做亏损单”和“只是把交易全部砍掉”。

若它能不靠极端砍单就改善 `tail loss / drawdown / adverse excursion / post-cost pnl` 之一，才值得升 `P2`；否则就应诚实用尽 survivor 预算后回 `background/P0`。

### 6.2 AMM executable-price reconstruction × slippage/gas veto
这条 `2025 arXiv` 真正可 desk 化的主语，不是“CEX 领先 DEX”，而是：
- 对 same-asset lead-lag / basis / cross-venue relative-value 家族，
- 用 `executable spread after fee/gas/slippage` 代替 mid-price spread，
- 形成一个 shared execution veto / admission filter。

所以它值得作为新的 fresh intake 被审，但必须聚焦：
- 是否真能收敛成一个独立 queue-facing shared filter；
- 是否具备清楚的 A/B 边界（`naive mid-gap` vs `executable-gap veto`）；
- 不能直接写成又一篇 price discovery 摘要。

### 6.3 Rank 86 park residual
`Rank 86` 当前仍在 `park`，不能直接 reopen 原对象。
但 `research/park_reframe/2026-03-28_1128_rank86-park-reframe.md` 已把 residual 收窄为：
- `penetration×ATR shared admission gate` 已死；
- 唯一还值得看的，只是 `breakout-short` 专用的 short-side admission score / veto。

因此它符合 policy 允许的 `park_reframe/derived_hypothesis_drafted` 作为 conditional fresh intake 被单独首判。

### 6.4 Rank 64 park residual
`Rank 64` 也仍在 `park`，不能 reopen 原对象。
但 index 显示其 residual 已被收窄为：
- `shared pullback-quality full-score gate` 不成立；
- 唯一还值得看的，只是 `long-side-only hold-quality / admission score`。

它能占一个 conditional intake 位，但优先级在 `Rank 86` 后，因为当前更前排、更独立的 recent paper intake 已经存在，而且 `Rank 64` 与既有 long-side hold-quality family 的重叠风险也更高。

## 7) 已写回 runtime truth
本轮已更新 `docs/BOT2_BOT3_STATE.md`：
- `Fresh intake slot` 维持 `Rank 240`
- `Surviving candidate slot` 维持 `Rank 240`，`followup_budget_remaining = 1`
- `Active P2 slot` 维持 `none`
- `cycle_plan` 改写为上述 4 项 pending 小点

## 8) 一句话结论
这轮别回头 reopen `Rank 239` 或更早对象；当前唯一合法前排动作是把 `Rank 240` 的那一次 follow-up 做完，然后再把资源切回 `AMM executable-spread veto` 与两个 park residual intake。