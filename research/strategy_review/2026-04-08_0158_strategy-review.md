# 2026-04-08 01:58 UTC strategy review

## Scope
按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 执行本轮 40 分钟 desk review；本轮只更新 runtime state，不改 policy / brief / operating card / auto loop / cron prompt。

## 先回答 4 个问题

### 1) `Paper launch queue` 是否非空？
**否。**

当前 `Paper launch queue.current_target = none`。`Rank 200 / 201 / 213 / 229 / 342` 都已写入 `connected_runner_live`；最近 `P3` 接线完成记录仍是 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md`。因此现在没有待接线的 queue 头对象。

### 2) 本轮 `fresh intake` 是什么？
**是 `research/quant_digests/2026-04-08_0012_spot-perp-openclose-basis-shell.md`。**

原因：
- 上一条 fresh intake `Rank 360 / rest-of-window impulse × close-pocket continuation` 已在 `2026-04-08_0138_rank360_rod_closepocket_hedgingmomentum_intake_keep_p1.md` 完成 first verdict；
- 它的唯一 survivor follow-up 又已在 `2026-04-08_0150_rank360_survivor_followup_exhausted_background.md` 诚实收口并退回 background；
- 因此前排 fresh 队头自然切到尚未做 first verdict 的 `00:12 spot-perp executable basis × open/close hysteresis shell`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得，而且这次 follow-up 已经用掉并收口。**

上一条 fresh intake 就是 `Rank 360`。它先被判为 `keep_P1`，所以值得且应当获得那唯一一次 follow-up；而这次 follow-up 现在已经执行完毕，明确结论是：
- 该对象仍是独立的 event-clock pocket alpha 想法；
- 但当前缺少 crypto 真实时钟锚点下、相对 plain intraday momentum 的 after-cost 独立增量与最小执行壳证据；
- 因此正式收口为 `keep_P1 exhausted -> background`。

所以本题的答案不是“还要不要给”，而是：**已经给过，而且已诚实用完。**

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。**

`Active P2 slot.current_target = none`。最近需要 bot2 兜底裁决的 `P2` 仍是 `Rank 342`，但它早已完成 `P2 -> P3 -> connected_runner_live`，所以本轮没有漏升、也没有待判出口的在场 `Active P2`。

## Rank / 前排合法性检查
- `Paper launch queue.current_target = none`，合法。
- `Surviving candidate slot.current_target = none`，且 `followup_budget_remaining = 0`，与 `Rank 360` 已收口回 background 一致，合法。
- `Active P2 slot.current_target = none`，合法。
- 当前前排不存在达到 `keep_P1 / P2 / P3` 但无正式 rank 的对象，因此本轮无需补 rank。

## 最近证据摘要
本轮读取了 fixed policy / runtime state，并补看 repo 状态、最近 `optimization_loop`、最近 `strategy_review` 与当前 fresh 材料：

1. `research/optimization_loop/2026-04-08_0150_rank360_survivor_followup_exhausted_background.md`
   - 说明 `Rank 360` 的唯一 survivor follow-up 已经用完，且明确不能升 `P2`；survivor 槽位已被释放。
2. `research/optimization_loop/2026-04-08_0138_rank360_rod_closepocket_hedgingmomentum_intake_keep_p1.md`
   - 说明上一条 fresh intake 的 `keep_P1` first verdict 是成立的，因此那次 follow-up 本来就应该给。
3. `research/strategy_review/2026-04-08_0144_strategy-review.md`
   - 上一轮 review 的主结论是“先做 Rank 360 survivor，再做 00:12 spot-perp fresh”；而现在第一步已完成，所以前排需要同步切到“fresh first”。
4. `research/quant_digests/2026-04-08_0012_spot-perp-openclose-basis-shell.md`
   - 当前最具体、最近且仍未做 first verdict 的 fresh intake；主语是 `same-underlier executable basis dislocation -> close-spread mean reversion`，并且自带双阈值开平仓与 slippage buffer 执行壳。
5. `research/optimization_loop/2026-04-08_0058_rank57b_source_intake_candidate_kept.md`
   - 这是当前最近的新近候选里，最接近可被继续判断的一条 source-intake 对象；它尚未被正式拉入 front-slot，但比旧 background 更接近当前可执行的新 intake 审核。
6. repo 状态
   - 工作树里仍有大量历史未跟踪研究文件；这只算 repo hygiene 现状，不构成自动 reopen background pool 或改变当前前排优先级的理由。

## 排班判断
按 policy 默认顺序：
`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0/background`

本轮扫描结果：
- `P3`：无待接线对象；
- `P2`：无在场 `Active P2`；
- `P1`：上一条 survivor `Rank 360` 已收口，不再有合法 survivor 动作；
- 因此本轮应直接切回 `fresh intake`，并必须指定具体对象；
- 当前最该排的 fresh intake 是 `00:12 spot-perp basis shell`；
- 在没有 `P3/P2/P1` 前排链条占位的前提下，剩余预算可诚实补入一个最近的新近 source-intake candidate（`Rank 57b`）和两个具体 park-reframe 派生（`Rank 60b`、`Rank 27c`）。

## 为什么本轮不需要 bot2 兜底升 P3
policy 要求 bot2 在 desk review 已明确看到某个**在场 `Active P2`** 已足够值得进入 paper trade、而 bot3 尚未升级时，直接改写到 `P3 / handoff`。

本轮不满足这个条件：
- `Active P2 = none`；
- 最近的 `Rank 342` 已经完成 `P2 -> P3 -> connected_runner_live`；
- 当前需要重排的是 `fresh intake` 顺序，而不是漏升的 `P2 exit decision`。

因此，本轮不存在需要 bot2 强制推进到 `P3 / Paper launch queue` 的对象。

## Runtime writeback
本轮已按最新运行事实重写 `docs/BOT2_BOT3_STATE.md`：

### Fresh intake slot
- 改成：
  - `status = pending`
  - `current_target = research/quant_digests/2026-04-08_0012_spot-perp-openclose-basis-shell.md`
- 保留上一条 fresh intake (`Rank 360`) 的 latest-result 语义，但明确说明其 survivor follow-up 已随后收口，不再占用前排。

### cycle_plan
重写为当前轮 4 项具体任务：
1. `research/quant_digests/2026-04-08_0012_spot-perp-openclose-basis-shell.md`
2. `research/optimization_loop/2026-04-08_0058_rank57b_source_intake_candidate_kept.md`
3. `research/park_reframe/2026-04-06_1034_rank60-park-reframe.md`
4. `research/park_reframe/2026-04-06_0606_rank27-park-reframe.md`

所有新生成项统一写成：
- `result: none`
- `status: pending`

## 执行回执
- `docs/BOT2_BOT3_STATE.md` 已按本轮结论写回。
- 本日志已落库到 `research/strategy_review/2026-04-08_0158_strategy-review.md`。

## 一句话总结
这轮最关键的变化是：`Rank 360` 的 survivor 预算已经诚实用完，所以前排不该再假装有 `P1/P2/P3` 收口动作；当前 runtime 应直接切回 `00:12 spot-perp basis shell` 作为 fresh 队头，并用剩余预算填入具体的新近 intake 候选。