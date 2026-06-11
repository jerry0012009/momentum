# Strategy Review (bot2)

Time: 2026-03-30 00:56 UTC

## 本轮一句话判断
`Paper launch queue` 为空；本轮已无 `survivor`、无 `Active P2`；最新 fresh intake `Rank 244` 的唯一 follow-up 已诚实收口并回 `background/P0`，所以本轮应按 policy 切回具体 `fresh intake`，但不能再重复消费已被明确 blocked 的 `Rank 96 / Rank 76`，而应把预算转到仍未正式 intake 的 `Rank 101 / Rank 28 / Rank 5 / Rank 4`。

## 1) 本轮读取与边界
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git status --short`
- 最近 `research/optimization_loop/`：
  - `2026-03-30_0055_rank76_fixed_utc_bucket_mode_switch_blocked_absorbed_by_rank201.md`
  - `2026-03-30_0042_rank96_conditional_intake_blocked_duplicate_non_distinct.md`
  - `2026-03-30_0029_rank244_survivor_followup_background.md`
  - `2026-03-30_0012_rank64_conditional_intake_keep_park_reframe.md`
  - `2026-03-30_0000_rank244_gmadl_directional_threshold_btc_keep_p1.md`
- 最近 `research/strategy_review/`：
  - `2026-03-30_0015_strategy-review.md`
  - `2026-03-29_2335_strategy-review.md`
- 为重排本轮 `cycle_plan` 额外补读：
  - `research/park_reframe/INDEX.md`
  - `research/park_reframe/2026-03-25_0457_rank101-park-reframe.md`
  - `research/park_reframe/2026-03-23_2358_rank28-park-reframe.md`
  - `research/park_reframe/2026-03-23_1941_rank5-park-reframe.md`
  - `research/park_reframe/2026-03-24_1430_rank4-park-reframe.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排；只从 `research/park_reframe/INDEX.md` 的合法 `soft_reframe_candidate` / 残余候选中选新的 intake 检查
- 未把 `docs/TODO.md` 当作排班依据
- 当前前排对象不存在无 rank 情况，因此无需补 rank

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**否。**

当前 runtime truth：
- `Paper launch queue.current_target = none`
- `connected_runner_live = Rank 200 / 201 / 213 / 229`

因此本轮没有等待 `runner + scheduler + 首跑验证` 的新 `P3` 接线动作。

### Q2. 本轮 `fresh intake` 是什么？
**严格按 runtime 里“上一条正式 fresh intake”来看，本轮 fresh intake 来源刚刚结束于 `Rank 244 / direction-aware loss × thresholded BTC directional state machine`。**

它在 `2026-03-30_0000_rank244_gmadl_directional_threshold_btc_keep_p1.md` 被正式记为 `keep_P1`，随后在 `2026-03-30_0029_rank244_survivor_followup_background.md` 完成唯一 follow-up 并回到 `background/P0`。

换句话说：
- 最新已消费完成的 fresh intake 是 `Rank 244`
- 但它已经收口，不再占前排
- 因此本轮需要**重新指定新的 fresh intake 对象**，而不是继续把 `Rank 244` 留在前排

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得，而且已经做完，结论是否定升级。**

理由：
- `Rank 244` 的 blocker 单一且 decisive：`direction-aware loss` 的增量到底是不是独立于 `threshold abstain` 的真增量
- 这正符合 survivor 唯一一次便宜诚实检查的定义
- follow-up 已经直接给出出口答案：在同一 BTC 15m walk-forward、同一特征、同一状态机、保守 friction 下，`direction-aware loss` 只是把预测幅度放大并显著增加交易，没有留下独立成本后增量，因此 survivor 用尽后回 `background/P0`

所以本题答案是：
- **值得做**
- **且已做完**
- **做完后的结论是不升 `P2`**

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**当前不存在明确 `Active P2`。**

原因：
- `Active P2 slot.current_target = none`
- 最近一次明确 P2 出口仍是 `Rank 235`，并已在 `2026-03-29_1230_rank235_p2_exit_rescope_p1_honesty_gap.md` 完成 `one-time P2 -> P1 re-scope`
- 之后没有新的对象进入 `Active P2 slot`

因此本轮不存在需要 bot2 触发 `P3 / P1 / P0` 出口裁决的 active P2。

## 3) P3 兜底判断
本轮不触发 bot2 的 `P2 -> P3` 兜底裁判。

原因：
- `Paper launch queue = none`
- `Active P2 = none`
- 最近结果里没有出现“对象已经明显够 `paper trade / paper launch`，但 bot3 还没升”的前排对象

因此 bot2 这轮不能假装有 P3 或 P2 主线；诚实排班只能切回新的 intake。

## 4) rank 合规检查
- `Paper launch queue / connected_runner_live`：均有正式 rank
- `Fresh intake slot.current_target = none`
- `Surviving candidate slot.current_target = none`
- `Active P2 slot.current_target = none`

结论：**本轮无需补新的正式 Rank。**

## 5) 本轮 `cycle_plan` 重写逻辑
按 policy 默认顺序扫描：
1. `P3 handoff`：无 queue 头，跳过
2. `P2 admission/promote/park`：无 active P2，跳过
3. `P1 survivor`：无 surviving candidate，跳过
4. `fresh intake`：成为当前轮主任务，必须直接给具体对象
5. `P0 / background pool`：只保留证据，不单独占位

关键约束下的诚实处理：
- `Rank 244` 已完成唯一 follow-up，不能继续占 survivor 槽位
- `Rank 96` 已在 `2026-03-30_0042` 被明确写成重复检查 blocked
- `Rank 76` 已在 `2026-03-30_0055` 被明确写成已被 `Rank 201` 吸收、不得再次当新 intake
- `Rank 64` 已在 `2026-03-30_0012` 再次收口为 `继续留在 park/reframe`

所以这轮不能把旧的 blocked 项继续挂在 `cycle_plan` 里占位，必须把预算转给仍有合法空间、但尚未正式 intake 的具体对象。

## 6) 为什么是这 4 项
### 6.1 Rank 101 放第 1 项
它是当前最自然、最近且尚未正式消费的 `soft_reframe_candidate`：
- 主语够窄：`long-side hold-quality residual note`
- 最近还被 `trend-pullback-correlation-shell` 类证据间接触发过边界重审
- 但至今没有正式 fresh intake 结论

所以它应作为本轮第一个 fresh intake 检查。

### 6.2 Rank 28 放第 2 项
原因：
- 它不是在重开原 `leader-laggard` 旧题，而是检查最近 same-clock 横截面证据是否已让其残余收敛成独立对象
- 相比已被判重复的 `Rank 96 / Rank 76`，这里还有真实的新边界问题可答
- 但又必须严防偷换成“另开新 family 却挂旧名”

### 6.3 Rank 5 放第 3 项
原因：
- double-clock 新证据确实提供了新的 residual 方向
- 但它目前更像 `open-impulse + pre-close reversal` 的更大 raw-alpha family 提示
- 因此值得做一次正式 intake 检查，确认它能否诚实从旧 `Rank 5` 残余里长成独立对象

### 6.4 Rank 4 放第 4 项
原因：
- pairs 主题最近新增 `threshold governance / basket governance / dynamic sizing` 的旁证
- 但这些旁证很可能已经超出原 `Rank 4` 的窄 reframe边界
- 仍值得用一轮 fresh intake 检查把这件事说死：到底能否形成新对象，还是应明确留在 park_reframe

## 7) 已写回 runtime truth
本轮已重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan` 为 4 个具体 `fresh intake`：
1. `Rank 101 park residual -> long-side hold-quality residual note`
2. `Rank 28 park residual -> same-clock cross-sectional market-neutral residual`
3. `Rank 5 park residual -> double-clock open-impulse plus pre-close reversal residual`
4. `Rank 4 park residual -> threshold-governed pairs family residual`

所有新生成项都满足：
- `result = none`
- `status = pending`

## 8) 一句话结论
这轮已经没有 `P3 / P2 / survivor` 前排主线可收口；最诚实的 bot2 动作不是继续重复 `Rank 244 / 96 / 76 / 64`，而是把预算完整切回尚未正式 intake 的 4 条具体残余：**先看 `Rank 101`，再看 `Rank 28 / Rank 5 / Rank 4`，逐条回答它们能否真正长成新的 queue-facing 对象。**
