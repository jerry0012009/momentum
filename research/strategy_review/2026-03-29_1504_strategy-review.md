# Strategy Review (bot2)

Time: 2026-03-29 15:04 UTC

## 本轮一句话判断
`Paper launch queue` 仍为空；最新 fresh intake 已切换为 `Rank 239` 并锁定唯一 survivor 槽位，上一条 fresh intake `Rank 238` 的唯一 follow-up 已经用尽且已回 `background/P0`，当前也不存在 `Active P2`，所以本轮默认顺序必须是：先收口 `Rank 239` 的唯一 follow-up，再切回新的 fresh intake，而不是 reopen 更早对象。

## 1) 本轮读取与边界
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short --branch`
- 最近 `research/optimization_loop/`：
  - `2026-03-29_1424_rank239_first_verdict_keep_p1_pair_rebalancing_threshold_map.md`
  - `2026-03-29_1411_rank238_survivor_followup_exhausted_background.md`
  - `2026-03-29_1358_rank238_first_verdict_keep_p1_utc_schedule_macro_shared_gate.md`
  - `2026-03-29_1230_rank235_p2_exit_rescope_p1_honesty_gap.md`
- 最近 `research/strategy_review/`：
  - `2026-03-29_1401_strategy-review.md`
- 为重排 fresh intake，又补读：
  - `research/quant_digests/2026-03-29_1458_usdt-depeg-jump-risk-shared-overlay.md`
  - `research/park_reframe/INDEX.md`
  - `research/park_reframe/2026-03-29_0703_rank64-park-reframe.md`
  - `research/park_reframe/2026-03-28_1128_rank86-park-reframe.md`

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
**本轮 fresh intake 是 `Rank 239 / pair-rebalancing MR × correlation-signed threshold map`。**

依据：
- `research/optimization_loop/2026-03-29_1424_rank239_first_verdict_keep_p1_pair_rebalancing_threshold_map.md`
- 它是最新一条完成 first verdict 且仍在当前运行链条里的 fresh intake
- 依 policy，最新一条 fresh intake 若首判为 `keep_P1`，其 survivor follow-up 享有前排锁定位

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**不值得再给。**

这里的“上一条 fresh intake”是 `Rank 238 / UTC schedule_score shared gate × continuation admission / reversal veto`。

原因不是它没有被检查，而是：
- 它的唯一 survivor follow-up 已在 `2026-03-29_1411_rank238_survivor_followup_exhausted_background.md` 完成；
- frozen `schedule_score` 在 `5m BTC` continuation admission 与 reversal veto 两侧都未留下 gated 优于 baseline、且 inverse 可反证的 post-cost 分层；
- 因此它已经诚实用尽唯一 follow-up 预算，并回 `background/P0`。

换句话说：
- `Rank 238` 这条线已经收口；
- 当前唯一合法 survivor 锁位必须给最新的 `Rank 239`，不能再回头给 `Rank 238` 第二次机会。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**当前不存在明确 `Active P2`。**

原因：
- `Rank 235` 已在 `2026-03-29_1230_rank235_p2_exit_rescope_p1_honesty_gap.md` 中正式写成 `one-time P2 -> P1 re-scope`
- state 里也已写明 `Active P2 = none`
- `Rank 238` 已回 `background/P0`
- `Rank 239` 目前只是 `keep_P1` survivor，不是 `P2`

因此本轮默认顺序只能回到：
1. `Rank 239` survivor 唯一一次 follow-up
2. 再补新的 fresh intake

## 3) P3 兜底判断
本轮专门核对了 policy 的兜底要求：若某个 `Active P2` 已明显够格 `P3`，bot2 必须直接推进。

结论：**本轮不触发。**

原因：
- 当前 `Active P2 = none`
- 最近最接近 `P3` 的 `Rank 235` 已被最新 honesty 审计明确打回 `one-time P2 -> P1 re-scope`
- `Rank 238` 已回 `background/P0`
- `Rank 239` 仍停在 `P1`

所以这轮没有任何对象符合“desk review 已清楚表明足够进入 paper trade，但 bot3 尚未升级”的条件。

## 4) rank 合规检查
- `Paper launch queue / connected_runner_live`：现有对象均带 rank
- `Fresh intake slot`：`Rank 239`
- `Surviving candidate slot`：`Rank 239`
- `Active P2 slot`：`none`

结论：**本轮无需补新的 `Rank`。**

## 5) 本轮 `cycle_plan` 重写逻辑
按 policy 默认顺序，合法动作扫描结果是：
1. **P3 handoff**：无 queue 头，跳过
2. **P2 admission/promote/park**：无 `Active P2`，跳过
3. **P1 survivor**：`Rank 239` 是当前唯一合法 survivor，必须排第 1
4. **fresh intake**：只有在第 1 项已诚实排入后，才能切回新的具体 intake

因此本轮把 `cycle_plan` 重写为 4 项：
1. `Rank 239` survivor follow-up
2. `stablecoin depeg jump-risk shared overlay`
3. `Rank 64 park residual -> long-side-only hold-quality admission score`
4. `Rank 86 park residual -> breakout-short-specific short-side admission score / veto`

这样排的原因：
- 当前没有 `P3`、没有 `Active P2`
- `Rank 239` 作为最新 survivor 享有前排锁位，必须先收口
- 之后第一个 fresh intake 优先选最近新的 paper/alpha 报告：`2026-03-29_1458_usdt-depeg-jump-risk-shared-overlay.md`
- 剩余预算再补 policy 允许的 `park_reframe/derived_hypothesis_drafted`：`Rank 64b` 与 `Rank 86b` 方向

## 6) 对四个 pending 小点的具体判断
### 6.1 Rank 239 survivor follow-up
当前最该回答的问题不是“pairs threshold 方向看起来合理”，而是：
- 同一批可交易 pair 上，`corr-bucket threshold map` 是否真的优于 `fixed-threshold baseline`；
- 而且要在 trade retention、post-cost PnL、尾部回撤、负对照/反向 bucket 对照里留下真实增量。

若改善只来自砍样本，或负对照也同样成立，就应诚实用尽 survivor 预算后回 `background/P0`；若留下清楚增量，才值得升 `P2`。

### 6.2 stablecoin depeg jump-risk shared overlay
这条 `2025 JIMF` 真正可 desk 化的主语，不是“stablecoin 风险很重要”，而是：
- `downward USDT depeg`
- 导致未来 `30m/60m` 的 `jump-risk / cojump-risk` 明显上升
- 因而形成一个服务多类 raw alpha 的 shared `size-down + veto` risk layer

所以它值得作为新的 fresh intake 被审，但必须聚焦：
- 事件定义是否清楚（threshold / hold window / direction split）
- 它是否真是一个 queue-facing shared overlay 对象
- 不能直接写成宏观解释文

### 6.3 Rank 64 park residual
`Rank 64` 当前仍在 `park`，不能直接 reopen 原对象。
但 `research/park_reframe/2026-03-29_0703_rank64-park-reframe.md` 已把 residual 收窄为：
- `shared pullback-quality full-score gate` 不成立；
- 唯一还值得看的，只是 `long-side-only hold-quality / admission score`
- 且默认不接 `breakout_short`

因此它符合 policy 允许的 `park_reframe/derived_hypothesis_drafted` 作为 conditional fresh intake 被单独首判。

### 6.4 Rank 86 park residual
`Rank 86` 也仍在 `park`，不能 reopen 原对象。
但 index 显示其 residual 已被收窄为：
- 将 `penetration×ATR` 从 shared admission gate 降级为 `breakout-short-specific short-side admission score / veto`

这条线之所以还能占一个 conditional intake 位，是因为它问的是：
- 该残余是否与既有 `Rank 222` 家族真正不同；
- 还是只是旧 breakout-short honesty / admission family 的换壳重打包。

## 7) 已写回 runtime truth
本轮已更新 `docs/BOT2_BOT3_STATE.md`：
- `Fresh intake slot` 维持 `Rank 239`
- `Surviving candidate slot` 改写为 `Rank 239`，`followup_budget_remaining = 1`
- `Active P2 slot` 维持 `none`
- `cycle_plan` 改写为上述 4 项 pending 小点

## 8) 一句话结论
这轮别再回头 reopen `Rank 238` 或更早对象；当前唯一合法前排动作是把 `Rank 239` 的那一次 follow-up 做完，然后再把资源切回 `USDT depeg jump-risk overlay` 与两个 park residual intake。