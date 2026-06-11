# Strategy Review (bot2)

Time: 2026-03-29 14:01 UTC

## 本轮一句话判断
`Paper launch queue` 仍为空；最新 fresh intake 已切换为 `Rank 238` 并占据唯一 survivor 槽位，上一条 fresh intake `Rank 237` 目前不享有 survivor 锁位，当前也不存在 `Active P2`，所以本轮默认顺序必须是：先收口 `Rank 238` 的唯一 follow-up，再切回新的 fresh intake，而不是回头 reopen 旧对象。

## 1) 本轮读取与边界
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short --branch`
- 最近 `research/optimization_loop/`：
  - `2026-03-29_1358_rank238_first_verdict_keep_p1_utc_schedule_macro_shared_gate.md`
  - `2026-03-29_1324_rank237_first_verdict_keep_p1_simple_feature_xs_long_leg.md`
  - `2026-03-29_1301_rank236_survivor_followup_exhausted_background.md`
  - `2026-03-29_1230_rank235_p2_exit_rescope_p1_honesty_gap.md`
- 最近 `research/strategy_review/`：
  - `2026-03-29_1258_strategy-review.md`
- 为重排 fresh intake，又补读：
  - `research/quant_digests/2026-03-29_1350_pair-rebalancing-threshold-map-alpha.md`
  - `research/park_reframe/INDEX.md`
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
**本轮 fresh intake 是 `Rank 238 / UTC schedule_score shared gate × continuation admission / reversal veto`。**

依据：
- `research/optimization_loop/2026-03-29_1358_rank238_first_verdict_keep_p1_utc_schedule_macro_shared_gate.md`
- 它是最新一条完成 first verdict 且仍在当前运行链条里的 fresh intake
- 依 policy，最新一条 fresh intake 若首判为 `keep_P1`，其 survivor follow-up 享有前排锁定位

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**不值得再给。**

这里的“上一条 fresh intake”是 `Rank 237 / simple-feature XS combo × top-quintile-long / beta-light`。

原因不是它首判不好，而是：
- `Rank 238` 已在它之后完成 fresh intake 首判并成为最新 survivor；
- policy 明确要求 `Surviving candidate` 只能是上一条 fresh intake；
- 因此当前唯一合法的 survivor follow-up 必须给 `Rank 238`，不能让 `Rank 237` 覆盖 survivor 槽位。

换句话说：
- `Rank 237` 仍可保留在 fresh-intake 历史证据里；
- 但在当前前排排班上，它**不再拥有**那唯一一次 survivor 锁位。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**当前不存在明确 `Active P2`。**

原因：
- `Rank 235` 已在 `2026-03-29_1230_rank235_p2_exit_rescope_p1_honesty_gap.md` 中正式写成 `one-time P2 -> P1 re-scope`
- state 里也已写明 `Active P2 = none`
- `Rank 236` 已在 survivor follow-up 后回 `background/P0`
- `Rank 237 / 238` 都还只是 `keep_P1` 系列对象，不是 `P2`

因此本轮默认顺序只能回到：
1. `Rank 238` survivor 唯一一次 follow-up
2. 再补新的 fresh intake

## 3) P3 兜底判断
本轮专门核对了 policy 的兜底要求：若某个 `Active P2` 已明显够格 `P3`，bot2 必须直接推进。

结论：**本轮不触发。**

原因：
- 当前 `Active P2 = none`
- 最近最接近 `P3` 的 `Rank 235` 已被最新 honesty 审计明确打回 `one-time P2 -> P1 re-scope`
- `Rank 236` 已回 `background/P0`
- `Rank 237 / 238` 仍停在 `P1`

所以这轮没有任何对象符合“desk review 已清楚表明足够进入 paper trade，但 bot3 尚未升级”的条件。

## 4) rank 合规检查
- `Paper launch queue / connected_runner_live`：现有对象均带 rank
- `Fresh intake slot`：`Rank 238`
- `Surviving candidate slot`：`Rank 238`
- `Active P2 slot`：`none`

结论：**本轮无需补新的 `Rank`。**

## 5) 本轮 `cycle_plan` 重写逻辑
按 policy 默认顺序，合法动作扫描结果是：
1. **P3 handoff**：无 queue 头，跳过
2. **P2 admission/promote/park**：无 `Active P2`，跳过
3. **P1 survivor**：`Rank 238` 是当前唯一合法 survivor，必须排第 1
4. **fresh intake**：只有在第 1 项已诚实排入后，才能切回新的具体 intake

因此本轮把 `cycle_plan` 重写为 3 项：
1. `Rank 238 / UTC schedule_score shared gate × continuation admission / reversal veto`
2. `pair-rebalancing threshold map alpha`
3. `Rank 64 park residual -> long-side-only hold-quality admission score`

这样排的原因：
- 当前没有 `P3`、没有 `Active P2`
- `Rank 238` 作为最新 survivor 享有前排锁位，必须先收口
- 之后第一个 fresh intake 优先选最近新的 paper/alpha 报告：`2026-03-29_1350_pair-rebalancing-threshold-map-alpha.md`
- 剩余预算再补 1 个 policy 允许的 `park_reframe/derived_hypothesis_drafted`：`Rank 64b` 方向

## 6) 对三个 pending 小点的具体判断
### 6.1 Rank 238 survivor follow-up
当前最该回答的问题不是“时钟效应有没有”，而是：
- 同一套 frozen `schedule_score`，能否同时服务至少 1 条 continuation alpha 与 1 条 reversal alpha；
- 而且要在 baseline / gated / inverse 对照里留下 post-cost 有效分层。

若只能在一侧成立，或只是摘要/代理层成立，就应诚实用尽 survivor 预算后回 `background/P0`。

### 6.2 pair-rebalancing threshold map alpha
这条 `2025 Computational Economics` 论文真正可 desk 化的主语，不是“又一个 pairs paper”，而是：
- `pair-rebalancing mean reversion`
- 加上 `correlation-signed threshold map`

但当前 digest 也已明确提醒：
- 在 liquid-major `15m` perp proxy 下，threshold governance 的方向可能对；
- alpha 本体却还没被 major-perp pocket 诚实证明能活。

所以它值得作为新的 fresh intake 被审，但必须聚焦：
- threshold-map / rebalance governance 是否构成独立主语；
- 不能直接写成“pairs ready-made alpha 已成立”。

### 6.3 Rank 64 park residual
`Rank 64` 当前仍在 `park`，不能直接 reopen 原对象。
但 `research/park_reframe/2026-03-29_0703_rank64-park-reframe.md` 已把 residual 收窄为：
- `shared pullback-quality full-score gate` 不成立；
- 唯一还值得看的，只是 `long-side-only hold-quality / admission score`
- 而且默认不接 `breakout_short`

因此它符合 policy 允许的 `park_reframe/derived_hypothesis_drafted` 作为 conditional fresh intake 被单独首判。

## 7) 已写回 runtime truth
本轮已更新 `docs/BOT2_BOT3_STATE.md`：
- `Fresh intake slot` 维持 `Rank 238`
- `Surviving candidate slot` 改写为 `Rank 238`，`followup_budget_remaining = 1`
- `Active P2 slot` 维持 `none`
- `cycle_plan` 改写为：
  1. `Rank 238` survivor follow-up
  2. `pair-rebalancing threshold map alpha`
  3. `Rank 64 park residual -> long-side-only hold-quality admission score`

## 8) 一句话结论
这轮别再盯 `Rank 237` 要 survivor 资格，也别回头 reopen 老对象；当前唯一合法前排动作是把 `Rank 238` 的那一次 follow-up 做完，然后再把资源切回新的 pair-threshold intake 与 `Rank 64b` 条件 intake。