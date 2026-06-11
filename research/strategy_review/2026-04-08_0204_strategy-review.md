# 2026-04-08 02:04 UTC strategy review

## Scope
按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 执行本轮 40 分钟 desk review；本轮不改 policy / brief / operating card / auto loop / cron prompt，只核对 runtime truth，并在需要时重写 `BOT2_BOT3_STATE.md`。

## 先回答 4 个问题

### 1) `Paper launch queue` 是否非空？
**否。**

当前 `Paper launch queue.current_target = none`。`Rank 200 / 201 / 213 / 229 / 342` 都已在 `connected_runner_live`；最近完成记录仍是 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md`。因此现在没有待接线的 queue 头对象。

### 2) 本轮 `fresh intake` 是什么？
**是 `research/quant_digests/2026-04-08_0012_spot-perp-openclose-basis-shell.md`。**

原因：
- 上一条 fresh intake `Rank 360 / rest-of-window impulse × close-pocket continuation` 已在 `research/optimization_loop/2026-04-08_0138_rank360_rod_closepocket_hedgingmomentum_intake_keep_p1.md` 完成 first verdict；
- 它唯一一次 survivor follow-up 又已在 `research/optimization_loop/2026-04-08_0150_rank360_survivor_followup_exhausted_background.md` 诚实收口并退回 background；
- 因此前排 fresh 队头自然切到尚未做 first verdict 的 `00:12 spot-perp executable basis × open/close hysteresis shell`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得，而且已经给过并用完。**

上一条 fresh intake 就是 `Rank 360`。它先被判为 `keep_P1`，所以值得且应获得那唯一一次 follow-up；而该 follow-up 现在已经执行完毕，明确结论是：
- 它仍是独立的 `event-clock pocket alpha` 想法；
- 但当前缺少 crypto 真实时钟锚点下、相对 plain intraday momentum 的 after-cost 独立增量与最小执行壳证据；
- 因此正式收口为 `keep_P1 exhausted -> background`。

所以这里的答案不是“还要不要给”，而是：**已经给过，而且已诚实用完。**

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。**

`Active P2 slot.current_target = none`。最近需要 bot2 兜底裁决的 `P2` 仍是 `Rank 342`，但它早已完成 `P2 -> P3 -> connected_runner_live`，因此本轮没有漏升、也没有待判出口的在场 `Active P2`。

## Rank / 前排合法性检查
- `Paper launch queue.current_target = none`，合法。
- `Surviving candidate slot.current_target = none`，且 `followup_budget_remaining = 0`，与 `Rank 360` 已收口回 background 一致，合法。
- `Active P2 slot.current_target = none`，合法。
- 当前前排不存在达到 `keep_P1 / P2 / P3` 但无正式 rank 的对象，因此本轮无需补 rank。

## 最近证据摘要
本轮补读与核对：
1. `research/optimization_loop/2026-04-08_0150_rank360_survivor_followup_exhausted_background.md`
   - 确认 `Rank 360` 的 survivor 预算已经用尽，且不能诚实升 `P2`。
2. `research/optimization_loop/2026-04-08_0138_rank360_rod_closepocket_hedgingmomentum_intake_keep_p1.md`
   - 确认上一条 fresh intake 的 `keep_P1` 成立，因此那一次 follow-up 本来就该给。
3. `research/strategy_review/2026-04-08_0158_strategy-review.md`
   - 上一轮 review 已把 runtime truth 改成“fresh 队头切到 00:12 spot-perp basis shell”。
4. `research/optimization_loop/2026-04-08_0058_rank57b_source_intake_candidate_kept.md`
   - 确认 `Rank 57b` 仍只是 `source-intake candidate`，但作为最近、具体、尚未 front-slot 化的候选，仍可放在本轮剩余预算里做是否晋升为正式 fresh intake 的判断。
5. repo 工作树
   - 存在大量历史未跟踪研究文件；这只算 repo hygiene 现状，不构成自动 reopen background pool 或改写当前前排顺序的理由。

## 排班判断
按 policy 默认顺序：
`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0/background`

本轮扫描结果：
- `P3`：无待接线对象；
- `P2`：无在场 `Active P2`；
- `P1`：上一条 survivor `Rank 360` 已收口，不再有合法 survivor 动作；
- 因此本轮应直接切回 `fresh intake`，并必须指定具体对象；
- 当前最该排的 fresh intake 仍是 `00:12 spot-perp basis shell`；
- 在没有 `P3/P2/P1` 前排链条占位的前提下，剩余预算可诚实补入一个最近的新近 source-intake candidate（`Rank 57b`）和两个具体 park-reframe 派生（`Rank 60`、`Rank 27`）。

## 为什么本轮不需要 bot2 兜底升 P3
policy 要求 bot2 在 desk review 已明确看到某个**在场 `Active P2`** 已足够值得进入 paper trade，而 bot3 尚未升级时，直接改写到 `P3 / handoff`。

本轮不满足这个条件：
- `Active P2 = none`；
- 最近的 `Rank 342` 已经完成 `P2 -> P3 -> connected_runner_live`；
- 当前需要维持的是 fresh/front-slot 排班，而不是漏升的 `P2 exit decision`。

因此，本轮不存在需要 bot2 强制推进到 `P3 / Paper launch queue` 的对象。

## Runtime writeback
本轮复核后，`docs/BOT2_BOT3_STATE.md` 当前内容与 policy 下的最诚实排班一致，**无需新增改写**。当前 runtime truth 继续保持：

### cycle_plan
1. target: `research/quant_digests/2026-04-08_0012_spot-perp-openclose-basis-shell.md`
   action: 作为当前最前的 fresh intake，判断 `spot-perp executable basis × open/close hysteresis shell` 是否已足够形成独立于既有 funding/carry/basis 主题的 raw alpha intake，并给出 `keep_P1` 或 `background / P0` 的 first verdict
   success_criterion: 必须给出明确 first verdict：若对象把 `same-underlier executable basis dislocation -> close-spread mean reversion` 的主语、双腿净成本与 hysteresis 开平仓壳、以及相对泛 funding/carry 叙事的独立职责压清，则写成 `keep_P1`；若主要仍只是成熟教程级执行模板、没有独立 raw-alpha 主语，则明确写成 `background / P0`
   result: none
   status: pending
2. target: `research/optimization_loop/2026-04-08_0058_rank57b_source_intake_candidate_kept.md`
   action: 作为当前新近且尚未进入前排的 source-intake 候选，判断 `breakout-family-local pre-break compression admission` 是否已经足够冻结为正式 fresh intake，还是应继续维持 `source-intake candidate`
   success_criterion: 必须给出明确结论：若对象把唯一 compression 定义、唯一宿主 `baseline breakout_short`、以及单轴 `baseline vs compression-admission` A/B 与 trade-retention 口径压清，则给出 fresh first verdict；若这些前提仍未冻结，则明确维持 `source-intake candidate / not front-slot`
   result: none
   status: pending
3. target: `research/park_reframe/2026-04-06_1034_rank60-park-reframe.md`
   action: 作为当前前排 fresh intake 已诚实排入后的 conditional fresh intake，判断 `retest-window impulse re-break confirmation` 是否已足够从 `derived_hypothesis_drafted` 升为正式 fresh intake，还是应继续留在 park reframe，不进入前排
   success_criterion: 必须给出明确结论：若对象能把 `retest-window impulse -> re-break continuation` 的独立主语、相对既有 breakout/retest 家族的唯一修改轴、以及最小 clean-room 实验口径压清，则给出 fresh first verdict；若仍只是旧 breakout residual 的改写、没有独立 front-slot 问题，则明确维持 `park reframe / not front-slot`
   result: none
   status: pending
4. target: `research/park_reframe/2026-04-06_0606_rank27-park-reframe.md`
   action: 作为剩余预算里的具体 conditional fresh intake，判断 `breakout-bar taker-imbalance confirmation on neckline break` 是否已足够从 `derived_hypothesis_drafted` 升为正式 fresh intake，还是应继续留在 park reframe，不进入前排
   success_criterion: 必须给出明确结论：若对象能把 `neckline break taker-imbalance -> breakout continuation` 的独立主语、相对既有 retest confirmation 家族的唯一修改轴、以及最小 clean-room 实验口径压清，则给出 fresh first verdict；若仍只是旧 breakout residual 的改写、没有独立 front-slot 问题，则明确维持 `park reframe / not front-slot`
   result: none
   status: pending

## 执行回执
- 本日志已落库到 `research/strategy_review/2026-04-08_0204_strategy-review.md`。

## 一句话总结
这轮没有新的 `P3 / P2 / survivor` 收口动作；当前最诚实的 runtime 仍应保持“先做 `00:12 spot-perp basis shell`，再用剩余预算处理 `Rank 57b / Rank 60 / Rank 27`”。
