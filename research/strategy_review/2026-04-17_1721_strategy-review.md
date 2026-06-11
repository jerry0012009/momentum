# 2026-04-17 17:21 UTC bot2 strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git status --short`（主要仍是历史未跟踪临时文件；本轮不把这些噪音当作排班依据）
- Recent optimization loop:
  - `2026-04-17_1713_cycle_plan_no_pending_guard.md`
  - `2026-04-17_1700_rank74_fallback_freshintake_background_p0.md`
  - `2026-04-17_1657_crossmarket_leaderlag_freshintake_background_p0.md`
  - `2026-04-17_1632_oivolume_freshintake_background_p0.md`
  - `2026-04-17_1619_clusterdeviation_freshintake_background_p0.md`
  - `2026-04-17_1551_rank27_conditional_freshintake_blocked_stale_replay.md`
  - `2026-04-17_1516_rank60_freshintake_blocked_stale_already_absorbed.md`
  - `2026-04-17_1443_rank419_survivor_followup_rescope_longonly_background.md`
- Recent strategy review:
  - `2026-04-17_1455_strategy-review.md`
  - `2026-04-17_1351_strategy-review.md`
  - `2026-04-17_1248_strategy-review.md`
- Recent park-reframe / intake sources:
  - `research/park_reframe/2026-04-06_1034_rank60-park-reframe.md`
  - `research/park_reframe/2026-04-06_0606_rank27-park-reframe.md`
  - `research/park_reframe/2026-04-03_0656_rank57-park-reframe.md`
  - `research/park_reframe/2026-04-10_1516_rank74-park-reframe.md`

## 四个问题（本轮结论）
1. `Paper launch queue` 是否非空？
   - 结论：**否**。
   - `current_target = none`；`connected_runner_live` 虽然非空，但这些对象都已完成 runner + scheduler + first verified run，不属于待接线 queue。

2. 本轮 `fresh intake` 是什么？
   - 结论：**`Rank 60 / retest-window impulse re-break confirmation`。**
   - 理由：上一轮四个 intake 小点都已完成并写成 `done`，随后 bot3 又写出 `2026-04-17_1713_cycle_plan_no_pending_guard.md`，说明运行态已经卡在“无合法 pending 小点”。按 policy，bot2 必须重排而不是继续放着 stale done 列表。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
   - 结论：**值得，但那唯一一次 follow-up 已经用完并收口。**
   - 对象：`Rank 419`。
   - 结论已在 `2026-04-17_1443_rank419_survivor_followup_rescope_longonly_background.md` 落定：旧 spec 不升 `P2`，只保留 `long-only top quintile + BTC realized vol gate` 这一条 one-time re-scope 方向，并移入 background 等待未来按新 spec 重新 fresh intake。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
   - 结论：**不存在。**
   - `Active P2 = none`；最近一次 P2 出口仍是 `Rank 417` 的 one-time `P2->P1 re-scope`，但它已退出 active 槽位，不构成本轮待判对象。

## Rank 合规检查
- `Paper launch queue / Surviving candidate / Active P2` 当前不存在“已到 `keep_P1 / P2 / P3` 却没有正式 Rank”的违规。
- 本轮无需补发新 Rank。

## 排班判断
- 当前没有待接线 `P3`，没有 `Active P2`，上一条 survivor（`Rank 419`）也已诚实收口。
- 但运行态当前仍残留一组 `status: done` 的旧 cycle_plan，已被 bot3 的 no-pending guard 明确证明不能继续执行。
- 因此前排链条虽已清空，但 bot2 的本轮职责不是再做抽象说明，而是**把 state 重排回新的具体 pending fresh intake**。
- 新 intake 来源按 policy 继续优先吃 `research/park_reframe/INDEX.md` 中仍可诚实认领的 `derived_hypothesis_drafted`，cheap fallback 才留给 `soft_reframe_candidate`。

## cycle_plan rewrite（本轮执行）
已按 policy 重写 `docs/BOT2_BOT3_STATE.md`：
- `Fresh intake slot`
  - `status = open_pending_first_verdict`
  - `current_target = research/park_reframe/2026-04-06_1034_rank60-park-reframe.md`
  - `source_record` 同步切回 `Rank 60`
- `Surviving candidate slot`：保持 `none`
- `Active P2 slot`：保持 `none`
- `cycle_plan` 重写为 4 个具体 pending 小点：
  1. `Rank 60` first-verdict
  2. `Rank 27` conditional fresh intake
  3. `Rank 57` conditional fresh intake
  4. `Rank 74` conditional cheap fallback fresh intake

## P2 -> P3 兜底裁判检查
- 本轮无 `Active P2`，因此不存在“desk review 已清楚表明足够值得 paper trade，但 bot3 尚未升级”的兜底升 `P3` 场景。
- 本轮无需把任何对象直接写入 `P3 / Paper launch queue` 或 handoff 路径。

## Tail steps
- homepage 刷新：按要求作为独立命令 best-effort 执行；若因 `/var/www` 权限或 preflight 失败，则记为非阻断尾部失败，不回滚 state / log。
- 邮件通知：无论 publish 是否成功，均继续单独执行中文邮件摘要发送。
