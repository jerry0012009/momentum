# 2026-04-08 01:17 UTC strategy review

## Scope
按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 执行本轮 40 分钟 desk review；本轮只更新 runtime state，不改 policy / brief / operating card / auto loop / cron prompt。

## 先回答 4 个问题

### 1) `Paper launch queue` 是否非空？
**否。**

当前 `Paper launch queue.current_target = none`。`Rank 200 / 201 / 213 / 229 / 342` 都已经在 `connected_runner_live`，最近完成记录仍是 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md`。因此当前没有待接线的 `P3` 队头。

### 2) 本轮 `fresh intake` 是什么？
**是 `research/quant_digests/2026-04-08_0056_rod-closepocket-hedgingmomentum-alpha.md`。**

原因：
- 当前没有待接线 `P3`；
- 当前没有 `Active P2`；
- `Rank 359` 的唯一 survivor follow-up 已在 `2026-04-08_0110_rank359_survivor_followup_exhausted_background.md` 诚实收口并释放前排锁；
- 所以前排默认顺序已切回最新、尚未做 first verdict 的 fresh intake；
- 最新两个具体 fresh 对象就是 `00:56 rod-closepocket` 和 `00:12 spot-perp basis shell`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得，而且已经用完。**

上一条 fresh intake 是 `Rank 359 / chart-image trend score × next-hour drift`。它先在 `2026-04-08_0027_rank359_chart_image_trend_score_intake_keep_p1.md` 拿到 `keep_P1`，说明它确实值得那唯一一次 follow-up；随后在 `2026-04-08_0110_rank359_survivor_followup_exhausted_background.md` 被诚实收口为 `keep_P1 exhausted -> background`。

也就是说：
- **值过那唯一一次检查**；
- **但检查后没能升 `P2`**；
- **现在已不再占用 survivor/front-slot。**

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。**

`Active P2 slot.current_target = none`。最近的在场 `P2` 仍是 `Rank 342`，但它已经完成 `P2 -> P3 -> connected_runner_live`，所以本轮不存在 bot2 需要兜底裁决出口的 `Active P2`。

## Rank / 前排合法性检查
- `Paper launch queue.current_target = none`，合法。
- `Surviving candidate slot.current_target = none`，因为 `Rank 359` 已用尽唯一 follow-up，合法。
- `Active P2 slot.current_target = none`，合法。
- 当前前排不存在达到 `keep_P1 / P2 / P3` 但无正式 rank 的对象，因此本轮无需补 rank。

## 最近证据摘要
本轮读取了 fixed policy / runtime state，并补看 repo 状态、最近 `optimization_loop` 与最近 `strategy_review`：

1. `research/optimization_loop/2026-04-08_0110_rank359_survivor_followup_exhausted_background.md`
   - 明确说明 `Rank 359` 虽是独立 raw alpha，但 survivor 唯一检查后仍没压清相对 `simple ROC / EMA slope` 的 after-cost 独立增量与非摘要级实现口径，因此正确出口是 `keep_P1 exhausted -> background`。
2. `research/optimization_loop/2026-04-08_0027_rank359_chart_image_trend_score_intake_keep_p1.md`
   - 证明上一条 fresh intake 的确值过唯一一次 follow-up，但这一步已经成为历史，不得继续滞留前排。
3. `research/quant_digests/2026-04-08_0056_rod-closepocket-hedgingmomentum-alpha.md`
   - 这是当前最新且尚未做 first verdict 的新 paper alpha；主语是 `pre-close cumulative return -> close-pocket same-direction continuation`，依赖真实时钟锚点，更像 event-clock continuation，而不是 plain trend。
4. `research/quant_digests/2026-04-08_0012_spot-perp-openclose-basis-shell.md`
   - 这是当前次新的 repo alpha；主语是 `same-underlier executable basis dislocation -> close-spread mean reversion`，并且自带 executable spread、双阈值开平仓、slippage buffer、reopen delay 等执行壳。
5. `research/optimization_loop/2026-04-08_0058_rank57b_source_intake_candidate_kept.md`
   - `Rank 57b` 仍只是 `source-intake candidate`，可作为在前排链条已诚实收口后的 conditional intake，不应抢到新鲜 digest 前面。
6. `research/park_reframe/INDEX.md`
   - 当前较新的可用派生里，`Rank 57` 与 `Rank 60` 都属于 policy 允许的次级来源；其中 `Rank 60` 仍是 `derived_hypothesis_drafted`，适合作为第 4 个具体补位项。
7. repo 状态
   - 工作树里有大量历史未跟踪文件，但这不构成改 policy 或自动 reopen background pool 的理由。

## 排班判断
按 policy 默认顺序：
`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0/background`

本轮扫描结果：
- `P3`：无待接线对象；
- `P2`：无在场 `Active P2`；
- `P1`：无在场 survivor，因为 `Rank 359` 已刚刚收口；
- 因此前两项必须直接切回 fresh intake；
- 当前最该排的 fresh 顺序是：`00:56 rod-closepocket` -> `00:12 spot-perp basis shell`；
- 预算剩余时，再补 `Rank 57` 与 `Rank 60` 两条 park-reframe 条目作为 conditional fresh/source intake；
- 不把任何 background 旧候选拉回前排，也不把空槽确认写成独立任务。

## 为什么本轮不需要 bot2 兜底升 P3
policy 要求 bot2 在 desk review 已明确看到某个**在场 `Active P2`** 已经足够值得 paper trade，而 bot3 尚未升级时，直接改写到 `P3 / handoff`。

本轮不满足该前提：
- 当前 `Active P2 = none`；
- 最近的 `Rank 342` 已经完成 `P2 -> P3 -> connected_runner_live`；
- 当前前排任务全部属于 fresh/source intake，而不是漏升的 `P2`。

因此，本轮不存在 bot2 需要兜底强推到 `P3` 的对象。

## Runtime writeback
本轮已只改 `docs/BOT2_BOT3_STATE.md`：

### 1) Fresh intake slot
- 保持 `current_target = research/quant_digests/2026-04-08_0056_rod-closepocket-hedgingmomentum-alpha.md`
- 把 `latest_result` 改写为：`Rank 359` survivor 已诚实收口并释放前排锁，因此当前 fresh 队头继续等待 first verdict
- `latest_result_record` 同步改到 `2026-04-08_0110_rank359_survivor_followup_exhausted_background.md`

### 2) cycle_plan
按当前合法动作重写为 4 条具体 pending：
1. `00:56 rod-closepocket` first verdict
2. `00:12 spot-perp executable basis × open/close hysteresis shell` first verdict
3. `Rank 57 / breakout-family-local pre-break compression admission` conditional fresh/source-intake 判定
4. `Rank 60 / retest-window impulse re-break confirmation` conditional fresh intake 判定

所有新项统一写成：
- `result: none`
- `status: pending`

## 执行回执
- `docs/BOT2_BOT3_STATE.md` 已按本轮结论写回。
- 本日志已落库到 `research/strategy_review/2026-04-08_0117_strategy-review.md`。

## 一句话总结
这轮前排已经没有 `P3`、没有 `Active P2`、也没有 survivor 锁；所以最诚实的排法就是直接切回最新两条 fresh intake：先看 `rod-closepocket`，再看 `spot-perp basis shell`，最后才用 `Rank 57 / Rank 60` 这类 park-reframe 条目补预算。