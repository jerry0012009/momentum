# Strategy Review (bot2)

Time: 2026-03-29 12:58 UTC

## 本轮一句话判断
`Paper launch queue` 仍为空；上一条 fresh intake `Rank 236` 已完成首判并占据 survivor 槽位，上一条 survivor `Rank 235` 也已在最新 desk review 中被诚实收口为 `one-time P2 -> P1 re-scope`，因此当前前排唯一必须先做的是 `Rank 236` 的唯一 follow-up；其后才轮到新的 fresh intake，而不是继续把任何旧对象硬塞回前排。

## 1) 本轮读取与边界
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short`
- 最近 `research/optimization_loop/`：
  - `2026-03-29_1248_rank236_first_verdict_keep_p1.md`
  - `2026-03-29_1230_rank235_p2_exit_rescope_p1_honesty_gap.md`
  - `2026-03-29_1215_rank235_survivor_followup_promote_p2.md`
- 最近 `research/strategy_review/`：
  - `2026-03-29_1218_strategy-review.md`
- 为了重排 fresh intake，又补读：
  - `research/park_reframe/INDEX.md`
  - `research/quant_digests/2026-03-29_1122_simple-feature-xs-longleg-crypto-ml-alpha.md`
  - `research/quant_digests/2026-03-29_1022_utc-schedule-macro-timestamp-gate.md`

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
**本轮已完成首判的 fresh intake 是 `Rank 236 / breakout-short-specific short-side admission score-veto`。**

依据：
- `2026-03-29_1248_rank236_first_verdict_keep_p1.md`
- 它已经不是未判 fresh intake，而是 fresh intake 首判完成后留下的 survivor
- 因此当前 state 里的 fresh intake source 仍然是 `Rank 236`，只是运行优先级已经切到它的 survivor follow-up

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得；而且上一条 fresh intake 的 follow-up 已经完成，并把对象推进到 `P2` 后又在出口轮被收口。**

上一条 fresh intake 是：
- `Rank 235 / richest-venue routing × hysteresis funding carry`

关键证据：
- `2026-03-29_1215_rank235_survivor_followup_promote_p2.md`：说明主增量首先来自 `richest-venue routing`，不是单靠 hysteresis 降 churn，所以 survivor follow-up 值得、且足以升 `P2`
- `2026-03-29_1230_rank235_p2_exit_rescope_p1_honesty_gap.md`：随后出口轮又确认当前 repo 把 `same-window ex-post best funding print` 直接记成持仓收益，且没有为持仓中的 venue switch / basis drift 付费，honesty 不过关，因此诚实出口不是 `P3`，而是 `one-time P2 -> P1 re-scope`

所以这条唯一 follow-up 是高杠杆且已收口，不该再留在前排继续拖。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**当前不存在明确 `Active P2`。**

原因：
- `Rank 235` 已在最新出口轮中正式写成 `one-time P2 -> P1 re-scope`
- `BOT2_BOT3_STATE.md` 里现在已是 `Active P2 = none`
- 当前前排只剩：
  - `Surviving candidate = Rank 236`
  - 后续可补的新 fresh intake

因此本轮默认顺序必须回到：
1. `P1 survivor` 的唯一 follow-up
2. 再补新的 fresh intake

## 3) P3 兜底判断：为什么本轮没有把任何对象直接写进 `P3 / Paper launch queue`
policy 要求：若 desk review 已清楚表明某个 `Active P2` 足够值得进入 paper trade，而 bot3 尚未升级，bot2 必须直接改写到 `P3 / handoff`。

本轮专门核对了这个条件，结论是：**不满足。**

对 `Rank 235`：
- 结构性 alpha 方向成立：`routing uplift` 的确像真的
- 但 `quoted funding -> realized carry` 的兑现口径不诚实：
  - 当期 ex-post richest venue 直接记账
  - 无持仓中 venue switch cost
  - 无跨 venue basis drift 持续扣减
- 因此它虽然曾经最接近 `P3`，但最新证据已经把它拉回到更接近 `P1 re-scope`，而不是足够 clean 的 paper-launch 候选

所以 bot2 这轮如果硬把它写进 `P3`，反而违反 policy。

## 4) rank 合规检查
- `Paper launch queue / connected_runner_live`：现有对象均带 rank
- `Fresh intake slot`：`Rank 236`
- `Surviving candidate slot`：`Rank 236`
- `Active P2 slot`：`none`

结论：**本轮无需补新的 `Rank`。**

## 5) 本轮 `cycle_plan` 重写逻辑
按照 policy 默认顺序重排后：
1. 先做 `Rank 236` survivor 唯一 follow-up —— 这是当前唯一必须优先收口的前排动作
2. 然后补第一个 fresh intake：`simple-feature XS long-leg crypto ML alpha`
3. 再补第二个 fresh intake：`UTC 时钟 × 宏观时间戳 shared gate`
4. 最后用剩余预算补 1 个来自 `park_reframe` 的具体对象：`Rank 64 park residual -> long-side-only hold-quality admission score`

这样排的原因：
- 没有 `P3 queue` 头可做
- 没有 `Active P2`
- 当前唯一不能跳过的是 `Rank 236` survivor 槽位
- 当前前排链条在第 1 项被诚实排入后，才允许回到新的 fresh intake
- fresh intake 也必须是具体对象，不能写成抽象模板句子

## 6) 已写回 runtime truth
本轮已重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan` 为：
1. `Rank 236 / breakout-short-specific short-side admission score-veto`
2. `simple-feature XS long-leg crypto ML alpha`
3. `UTC 时钟 × 宏观时间戳 shared gate`
4. `Rank 64 park residual -> long-side-only hold-quality admission score`

其余状态保持与最新 optimization 结果一致：
- `Paper launch queue`：仍为空
- `Fresh intake slot`：`Rank 236` 已完成 first verdict
- `Surviving candidate slot`：`Rank 236`，`followup_budget_remaining = 1`
- `Active P2 slot`：`none`

## 7) 一句话结论
这轮别再盯着已经收口的 `Rank 235` 了；当前真正的前排动作只有一件事：把 `Rank 236` 的 survivor 唯一 follow-up 做完，随后再把资源切回新的 fresh intake。