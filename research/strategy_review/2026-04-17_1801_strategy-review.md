# 2026-04-17 18:01 UTC bot2 strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git status --short`（仍主要是历史遗留未跟踪临时文件；本轮不把这些噪音当排班依据）
- Recent optimization loop:
  - `2026-04-17_1756_rank27_conditional_freshintake_blocked_stale_replay.md`
  - `2026-04-17_1744_rank60_freshintake_blocked_stale_absorbed_by_rank378.md`
  - `2026-04-17_1713_cycle_plan_no_pending_guard.md`
  - `2026-04-17_1700_rank74_fallback_freshintake_background_p0.md`
  - `2026-04-17_1443_rank419_survivor_followup_rescope_longonly_background.md`
  - `2026-04-17_1038_rank57_conditional_freshintake_stale_blocked.md`
- Recent strategy review:
  - `2026-04-17_1721_strategy-review.md`
  - `2026-04-17_1455_strategy-review.md`
  - `2026-04-17_1351_strategy-review.md`
- Recent park-reframe / intake sources actually consulted for rewrite:
  - `research/park_reframe/2026-04-10_0611_rank89-park-reframe.md`
  - `research/park_reframe/2026-04-09_0244_rank71-park-reframe.md`
  - `research/park_reframe/2026-04-10_1516_rank74-park-reframe.md`
  - `research/park_reframe/2026-04-03_0656_rank57-park-reframe.md`
  - `research/park_reframe/2026-04-11_1550_rank57-park-reframe.md`
  - `research/park_reframe/INDEX.md`

## 四个问题（本轮结论）
1. `Paper launch queue` 是否非空？
   - 结论：**否**。
   - `current_target = none`；`connected_runner_live` 虽然非空，但这些对象都已完成 runner + scheduler + first verified run，不属于待接线 queue。

2. 本轮 `fresh intake` 是什么？
   - 结论：**应切换为 `Rank 89 / outside-close -> back-inside-close anchored failure-followthrough setup`。**
   - 原因：上一轮被排到前排的 `Rank 60 / Rank 27 / Rank 57 / Rank 74` 已被最近 runtime 逐条证明为 stale residue 或已收口对象，继续把它们挂在前排不诚实；当前必须切回仍未消费的新具体 intake。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
   - 结论：**值得，但那唯一一次 follow-up 已经用完并收口。**
   - 对象：`Rank 419`。
   - authoritative 结论仍是 `2026-04-17_1443_rank419_survivor_followup_rescope_longonly_background.md`：旧 spec 不升 `P2`，只保留 `long-only top quintile + BTC realized vol gate` 这一条 one-time `P1 re-scope` 方向，并已退出 survivor/front slot。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
   - 结论：**不存在。**
   - `Active P2 = none`；最近一次 P2 出口仍是 `Rank 417` 的 one-time `P2->P1 re-scope`，但它已退出 active 槽位，不构成本轮待判对象。

## Rank 合规检查
- 本轮前排槽位中不存在“已到 `keep_P1 / P2 / P3` 但无正式 Rank”的违规。
- 无需补发新 Rank。

## 关键判断
- 本轮没有待接线 `P3`。
- 没有 `Active P2`。
- `Rank 419` survivor 已诚实收口。
- 但当前 state 中留着的 `Rank 60 / 27 / 57 / 74` 前排链条已经被最新 runtime 逐条打成 stale/consumed，不应继续作为 bot3 默认 pending 主线。
- 因此本轮不是继续复读这些旧对象，而是必须把 `cycle_plan` 切回一组真正还能执行的新具体 intake。

## cycle_plan rewrite（本轮执行）
已按 policy 重写 `docs/BOT2_BOT3_STATE.md`：

### Fresh intake slot
- `status = open_pending_first_verdict`
- `current_target = research/park_reframe/2026-04-10_0611_rank89-park-reframe.md`
- `source_record` 同步切到 `Rank 89`
- `latest_result` 明确写回：`Rank 60 / 27 / 57 / 74` 属于 stale residue / 已收口对象，不再占用 fresh intake

### Surviving candidate slot
- 保持 `none`

### Active P2 slot
- 保持 `none`

### cycle_plan
1. `Rank 89` fresh intake first-verdict
2. `Rank 71` conditional fresh intake
3. `Rank 74` conditional cheap fallback fresh intake
4. `Rank 89` conditional survivor guardrail（仅当 item1=`keep_P1` 时才触发）

## 为什么本轮这样排
- policy 明确要求：只有在 `P3 / P2 / P1` 前排链条诚实收口后，才切回 `fresh intake`。
- 这一步已经满足，因为当前 `P3/P2/P1` 都为空。
- 但切回 intake 时，不能继续拿已消费对象伪装成 pending；所以 `Rank 60 / 27 / 57` 必须退出本轮排班。
- 在当前 `research/park_reframe/INDEX.md` 里，仍未消费、且相对具体的候选以 `soft_reframe_candidate` 为主；其中 `Rank 89` 的事件化 failure-followthrough 改写最具体，也最像真正还能做一次诚实 first verdict 的对象，因此放到第 1 位。
- `Rank 71` 仍保留一条足够明确的唯一修改轴（extreme-only binary gate / veto），放到第 2 位做 conditional intake。
- `Rank 74` 作为 cheap fallback 保留在第 3 位；虽然它刚被判过 `background/P0`，但它在 index 中仍是 `soft_reframe_candidate` 且修改轴明确，因此只适合作为预算尾部 fallback，不再占前排。
- 第 4 项不新开对象，只把 `Rank 89` 若首判 `keep_P1` 时的唯一 survivor 检查范围预先钉死，避免下一轮又把它拖成开放式 follow-up。

## P2 -> P3 兜底裁判检查
- 本轮无 `Active P2`。
- 因此不存在“desk review 已清楚表明足够值得 paper trade / paper launch，但 bot3 尚未升级”的兜底升 `P3` 场景。
- 本轮无需把任何对象直接写入 `P3 / Paper launch queue` 或 handoff 路径。

## Tail steps
- homepage 刷新：按要求作为独立命令 best-effort 执行；失败视为非阻断尾部失败。
- 邮件通知：无论 publish 是否成功，均继续单独执行中文邮件摘要发送。
