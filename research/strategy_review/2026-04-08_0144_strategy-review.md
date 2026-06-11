# 2026-04-08 01:44 UTC strategy review

## Scope
按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 执行本轮 40 分钟 desk review；本轮只更新 runtime state，不改 policy / brief / operating card / auto loop / cron prompt。

## 先回答 4 个问题

### 1) `Paper launch queue` 是否非空？
**否。**

当前 `Paper launch queue.current_target = none`。`Rank 200 / 201 / 213 / 229 / 342` 都已经在 `connected_runner_live`，最近完成记录仍是 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md`。因此当前没有待接线的 `P3` 队头。

### 2) 本轮 `fresh intake` 是什么？
**是 `research/quant_digests/2026-04-08_0012_spot-perp-openclose-basis-shell.md`。**

原因：
- 最新 fresh first verdict 已经在 `2026-04-08_0138_rank360_rod_closepocket_hedgingmomentum_intake_keep_p1.md` 完成，`Rank 360` 已从 fresh 升入 `Surviving candidate slot`；
- policy 规定 survivor 的唯一 follow-up 拥有前排锁定权，但这不会改变“当前尚未处理的下一条 fresh intake”是谁；
- 因此前排当前顺序应是：先做 `Rank 360` 的 survivor follow-up，再做下一条 fresh intake，也就是 `00:12 spot-perp open/close basis shell`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得，而且现在正在等待这唯一一次 follow-up。**

上一条 fresh intake 就是刚刚完成 first verdict 的 `Rank 360 / rest-of-window impulse × close-pocket continuation`。它在 `2026-04-08_0138_rank360_rod_closepocket_hedgingmomentum_intake_keep_p1.md` 被明确判为 `keep_P1`，说明它值得那唯一一次诚实检查；当前 `followup_budget_remaining = 1`，尚未用掉。

也就是说：
- **值这一次 follow-up**；
- **现在应优先把这次 follow-up 用掉**；
- **在它诚实收口之前，新的 fresh intake 不能排到它前面。**

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。**

`Active P2 slot.current_target = none`。最近的在场 `P2` 仍是 `Rank 342`，但它已经完成 `P2 -> P3 -> connected_runner_live`，所以本轮不存在 bot2 需要兜底裁决出口的 `Active P2`。

## Rank / 前排合法性检查
- `Paper launch queue.current_target = none`，合法。
- `Surviving candidate slot.current_target = Rank 360`，且已带正式 `Rank`，合法。
- `Active P2 slot.current_target = none`，合法。
- 当前前排不存在达到 `keep_P1 / P2 / P3` 但无正式 rank 的对象，因此本轮无需补 rank。

## 最近证据摘要
本轮读取了 fixed policy / runtime state，并补看 repo 状态、最近 `optimization_loop` 与最近 `strategy_review`：

1. `research/optimization_loop/2026-04-08_0138_rank360_rod_closepocket_hedgingmomentum_intake_keep_p1.md`
   - 明确说明 `Rank 360` 已压清为独立于 `plain trend / breakout / session seasonality` 家族的 event-clock raw alpha intake，因此 first verdict = `keep_P1`，并合法进入 survivor 槽位。
2. `research/optimization_loop/2026-04-08_0110_rank359_survivor_followup_exhausted_background.md`
   - 说明上一条 survivor 已诚实收口并释放 survivor 锁；当前 survivor 锁已经切换给 `Rank 360`，而不是延续旧对象。
3. `research/strategy_review/2026-04-08_0131_strategy-review.md`
   - 上一轮 review 仍把 `rod-closepocket` 当成 fresh intake 队头；但现在该动作已经完成，state 需要同步切换到“survivor first、next fresh second”的新顺序。
4. `research/quant_digests/2026-04-08_0012_spot-perp-openclose-basis-shell.md`
   - 仍是当前最近、尚未做 first verdict 的具体 fresh intake；主语是 `same-underlier executable basis dislocation -> close-spread mean reversion`，并自带双阈值开平仓与 slippage buffer 的执行壳。
5. repo 状态
   - 工作树里仍有大量历史未跟踪研究文件，但这不构成自动 reopen background pool 或重排旧对象优先级的理由。

## 排班判断
按 policy 默认顺序：
`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0/background`

本轮扫描结果：
- `P3`：无待接线对象；
- `P2`：无在场 `Active P2`；
- `P1`：有且只有 `Rank 360` 这一个 survivor，且仍保留 1 次 follow-up 预算；
- 因此本轮第一优先级必须改为 `Rank 360` 的 survivor follow-up；
- survivor 锁之后，当前最该排的 fresh intake 才是 `00:12 spot-perp basis shell`；
- 预算剩余时，再补 `Rank 60` 与 `Rank 27` 两条仍处于 `derived_hypothesis_drafted` 的 park-reframe 条目；
- 不存在可合法优先于 survivor 的 `P3` 或 `P2` 动作，因此这次重排不涉及 P3/P2 兜底裁决。

## 为什么本轮不需要 bot2 兜底升 P3
policy 要求 bot2 在 desk review 已明确看到某个**在场 `Active P2`** 已经足够值得 paper trade，而 bot3 尚未升级时，直接改写到 `P3 / handoff`。

本轮不满足该前提：
- 当前 `Active P2 = none`；
- 最近的 `Rank 342` 已经完成 `P2 -> P3 -> connected_runner_live`；
- 当前前排任务属于 `P1 survivor + fresh intake`，不是漏升的 `P2`。

因此，本轮不存在 bot2 需要兜底强推到 `P3` 的对象。

## Runtime writeback
本轮已按最新运行事实重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`，把前排顺序改成：

1. `Rank 360 / rest-of-window impulse × close-pocket continuation` survivor follow-up
2. `00:12 spot-perp executable basis × open/close hysteresis shell` fresh first verdict
3. `Rank 60 / retest-window impulse re-break confirmation` conditional fresh intake 判定
4. `Rank 27 / breakout-bar taker-imbalance confirmation on neckline break` conditional fresh intake 判定

所有新生成项统一写成：
- `result: none`
- `status: pending`

## 执行回执
- `docs/BOT2_BOT3_STATE.md` 已按本轮结论写回。
- 本日志已落库到 `research/strategy_review/2026-04-08_0144_strategy-review.md`。

## 一句话总结
这轮最关键的变化不是发现了新对象，而是 `Rank 360` 已正式拿到 survivor 锁；所以当前最诚实的前排顺序必须从“fresh first”切到“survivor first，spot-perp fresh second”。
