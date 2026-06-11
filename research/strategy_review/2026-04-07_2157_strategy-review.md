# 2026-04-07 21:57 UTC strategy review

## Scope
按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 执行本轮 40 分钟 desk review；本轮只重写 runtime state，不改 policy / brief / operating card / auto loop / cron prompt。

## 先回答 4 个问题

### 1) `Paper launch queue` 是否非空？
**否。**

当前 `Paper launch queue.current_target = none`。`Rank 200 / 201 / 213 / 229 / 342` 都已在 `connected_runner_live`；最近完成记录仍是 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md`。因此当前没有待接线的 `P3` 队头。

### 2) 本轮 `fresh intake` 是什么？
**是 `research/quant_digests/2026-04-07_2117_candlestick-shorthorizon-pattern-alpha.md`。**

原因：
- `Paper launch queue.current_target = none`
- `Surviving candidate slot.current_target = none`
- `Active P2 slot.current_target = none`
- 旧 `cycle_plan` 四条（`Rank 60 / 56 / 83 / 27`）都已完成，并全部诚实收口为 `background / P0`
- 最新新的 strategy/paper alpha 报告里，尚未进入 first verdict 的具体对象队头就是 `2117 candlestick-shorthorizon-pattern-alpha`

因此，本轮 fresh 队头应切到 `pattern-shortlist × next-hour drift`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
**不值得。**

上一条 fresh intake 是 `research/park_reframe/2026-04-06_0606_rank27-park-reframe.md`。它已在 `research/optimization_loop/2026-04-07_2150_rank27_breakoutbar_takerimbalance_first_verdict_background.md` 明确写成：
- 主语仍是旧 `Rank 27` neckline/breakout family
- 新增只是把确认方式从回踩改成 `breakout-bar taker-imbalance`
- 没有压出独立于旧 breakout/retest 家族的新 raw alpha 主语

因此它首判即 `background / P0`，不进 `keep_P1`，不配 survivor 那唯一一次 follow-up。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。**

`Active P2 slot.current_target = none`。最近的 `Active P2` 仍是 `Rank 342`，但它已在 `research/optimization_loop/2026-04-05_2300_rank342_p2_exit_promote_p3_lowgas_samechain_paper_queue.md` 完成 `P2 -> P3`，并在 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md` 完成最小接线。因此本轮没有 bot2 需要兜底推进到 `P3 / P1 / P0` 的在场 `Active P2`。

## Rank / 前排合法性检查
- `Paper launch queue.current_target = none`，合法。
- `Surviving candidate slot.current_target = none`，合法。
- `Active P2 slot.current_target = none`，合法。
- 当前前排不存在达到 `keep_P1 / P2 / P3` 但无正式 `Rank` 的对象，因此本轮无需补 rank。

## 最近证据与判断
本轮先读 fixed policy / runtime state，再看 repo 状态、最近 `optimization_loop` 与最近 `strategy_review`：

1. `research/optimization_loop/2026-04-07_2058_retest_window_impulse_rebreak_first_verdict_background.md`
   - `Rank 60` 已完成 first verdict，并被诚实记为 `background / P0`；说明上一轮排在最前的 park-reframe intake 已收口。
2. `research/optimization_loop/2026-04-07_2120_rank56_event_host_cluster_first_verdict_background.md`
   - `Rank 56` 已完成 first verdict；说明 `event-driven trigger/liquidation cluster` 目前仍只是迁移方向提示，不足以进入 survivor/P2 前排。
3. `research/optimization_loop/2026-04-07_2131_rank83_strongonly_fib_binary_confirm_first_verdict_background.md`
   - `Rank 83` 已完成 first verdict；说明 `strong-only Fib confirm` 仍只是旧 Fib confirmation 家族的收窄版。
4. `research/optimization_loop/2026-04-07_2150_rank27_breakoutbar_takerimbalance_first_verdict_background.md`
   - `Rank 27` 也已完成 first verdict；说明上一轮 4 条具体 intake 预算已经被诚实消费完。
5. `research/quant_digests/2026-04-07_2117_candlestick-shorthorizon-pattern-alpha.md`
   - 这是当前最新、且尚未做 first verdict 的新 paper alpha。它把对象压成了一个相对便宜、可复现的单资产 raw alpha：`Harami / Hikkake / Three White Soldiers / Three Black Crows` 的 shortlist 在 `next-hour drift` 上给出条件方向标签；对 desk 而言，最自然的 first verdict 切口就是 `15m 持有 4 bar / 5m 持有 12 bar` 的最小执行壳。
6. `research/park_reframe/2026-04-07_2055_rank33-park-reframe.md`
   - `Rank 33` 目前仍是 `soft_reframe_candidate`。最新复盘把其残余价值进一步压到 `shared false-reclaim veto / failure-routing hint`，但尚未正式升级成 `derived_hypothesis_drafted`；这是当前最值得回答的 park-reframe 出口问题。
7. `research/park_reframe/2026-04-03_0656_rank57-park-reframe.md`
   - `Rank 57` 已有明确的 `derived_hypothesis_drafted`：`breakout-family-local pre-break compression admission`。如果当前前排为空，它是值得回答“该不该前推成 source-intake”的具体对象。
8. `research/park_reframe/2026-03-23_0914_rank7-park-reframe.md`
   - `Rank 7` 也已有明确的 `derived_hypothesis_drafted`：`mid-score band-pass continuous alignment overlay`。在没有 `P3/P2/P1` 前排对象时，它也属于合法且具体的剩余预算项。

因此，按 policy 的默认排班顺序：
`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0 归档`

本轮实际扫描结果是：
- `P3`：无待接线对象；
- `P2`：无在场 `Active P2`；
- `P1`：无 survivor 锁位；
- 所以应切回具体 `fresh intake`；
- 在只有 1 条明确新 digest 时，可以用剩余预算补 `park_reframe/INDEX.md` 里的 `soft_reframe_candidate / derived_hypothesis_drafted`；
- 按具体值得做的顺序，本轮应排：`2117 candlestick shortlist` → `Rank 33` → `Rank 57` → `Rank 7`。

## 为什么本轮不需要 bot2 兜底升 P3
policy 只要求 bot2 在 desk review 已清楚看见某个**在场 `Active P2`** 已经足够值得进入 paper trade，而 bot3 尚未升级时，直接把它写入 `P3 / Paper launch queue` 或 handoff 路径。

本轮不满足这个前提：
- `Rank 342` 已完成 `P2 -> P3 -> connected_runner_live`；
- 当前没有在场 `Active P2`；
- 当前待做对象都只是 fresh intake / park-reframe intake。

因此，本轮不存在 bot2 需要兜底强推到 `P3` 的漏升对象。

## Runtime writeback
本轮已按 policy 只改 `docs/BOT2_BOT3_STATE.md` 的 runtime 部分：

### 1) Fresh intake slot
- `current_target` 切到 `research/quant_digests/2026-04-07_2117_candlestick-shorthorizon-pattern-alpha.md`
- `source_record` 同步切到该 digest
- `latest_result` / `latest_result_record` 保持最近刚落地的 `Rank 27 -> background / P0`

### 2) cycle_plan
按当前合法动作重写为 4 条具体 pending：
1. `2117 candlestick shortlist × next-hour drift`
2. `Rank 33 / false-reclaim veto 是否值得从 soft reframe 升到 derived hypothesis`
3. `Rank 57 / compression admission 是否值得从 drafted hypothesis 前推到 fresh/source intake`
4. `Rank 7 / band-pass alignment overlay 是否值得从 drafted hypothesis 前推到 fresh/source intake`

重排原则：
- 先诚实确认当前没有 `P3 / P2 / P1` 前排对象需要收口；
- 再把唯一明确的新 digest `2117` 放在 fresh 队头；
- 剩余预算按 `park_reframe` 当前最具体、最值得回答的合法动作补满；
- 新生成项统一保持 `result: none`、`status: pending`。

## 一句话总结
这轮没有漏升的 `P2`、没有遗留的 `P1`、也没有待接线的 `P3`；`Rank 60 / 56 / 83 / 27` 已全部诚实收口，所以 runtime 现在应切到 `2117 candlestick shortlist × next-hour drift`，并用 `Rank 33 / 57 / 7` 三条具体 park-reframe 出口问题填满本轮剩余预算。