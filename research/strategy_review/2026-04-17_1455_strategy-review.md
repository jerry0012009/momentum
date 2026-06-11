# 2026-04-17 14:55 UTC bot2 strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git status --short --branch`（仍主要是历史遗留未跟踪临时文件；本轮不把这些噪音当成排班依据）
- Recent optimization loop:
  - `2026-04-17_1443_rank419_survivor_followup_rescope_longonly_background.md`
  - `2026-04-17_1346_item3_rank60_conditional_freshintake_blocked_survivor_lock.md`
  - `2026-04-17_1332_rank419_xsmomentum_btcvoloverlay_first_verdict_keep_p1.md`
- Recent strategy review:
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
   - 结论：**当前运行态前排 fresh intake 已清空，下一条应切回 `Rank 60 / retest-window impulse re-break confirmation`。**
   - 理由：`Rank 419` 已在 `2026-04-17_1443...` 中完成 first verdict + survivor 唯一 follow-up 收口，`Fresh intake slot / Surviving candidate slot / Active P2 slot` 当前都没有存量前排对象；按 policy 必须回到新的具体 intake，而不能继续挂着 stale 条目。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
   - 结论：**值得，但那唯一一次 follow-up 已经用完并收口。**
   - 对象仍是 `Rank 419`。
   - 本轮 desk review 不再给第二次 follow-up：唯一 decisive blocker `short-leg cost` 已被回答，结论是旧 spec 不升 `P2`，只保留 `long-only top quintile + BTC realized vol gate` 这一条 one-time `P1 re-scope` 方向并移入 background。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
   - 结论：**不存在。**
   - `Active P2 = none`；最近一次 P2 出口仍是 `Rank 417` 的 one-time `P2->P1 re-scope`，但它已退出 active 槽位，不构成本轮待判对象。

## Rank 合规检查
- `Paper launch queue / Surviving candidate / Active P2` 当前不存在“已到 `keep_P1 / P2 / P3` 却没有正式 Rank”的违规。
- 本轮无需补发新 Rank。

## 排班判断
- 当前没有待接线 `P3`，也没有 `Active P2`，上一条 survivor（`Rank 419`）也已诚实收口。
- 因此前排链条已清空，默认应切回 `fresh intake`。
- 新 intake 来源优先级按 policy 执行：先吃 `research/park_reframe/INDEX.md` 里的 `derived_hypothesis_drafted`，再在预算尾部补 1 条 `soft_reframe_candidate` cheap fallback。
- 本轮最值得填满预算的具体对象：
  1. `Rank 60` — `retest-window impulse re-break confirmation`
  2. `Rank 27` — `neckline breakout + breakout-bar taker-imbalance confirmation`
  3. `Rank 57` — `breakout-family-local pre-break compression admission`
  4. `Rank 74` — `Fib-family-local ER-only trend-readiness veto/admission`（cheap fallback）

## cycle_plan rewrite（本轮执行）
已按 policy 重写 `docs/BOT2_BOT3_STATE.md`：
- `Fresh intake slot`
  - `status = open_pending_first_verdict`
  - `current_target = research/park_reframe/2026-04-06_1034_rank60-park-reframe.md`
  - `source_record` 同步切到 `Rank 60`
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
