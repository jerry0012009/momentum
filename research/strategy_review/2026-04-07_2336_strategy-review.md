# 2026-04-07 23:36 UTC strategy review

## Scope
按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 执行本轮 40 分钟 desk review；本轮只重写 runtime state，不改 policy / brief / operating card / auto loop / cron prompt。

## 先回答 4 个问题

### 1) `Paper launch queue` 是否非空？
**否。**

当前 `Paper launch queue.current_target = none`。`Rank 200 / 201 / 213 / 229 / 342` 都已在 `connected_runner_live`；最近完成记录仍是 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md`。因此当前没有待接线的 `P3` 队头。

### 2) 本轮 `fresh intake` 是什么？
**是 `research/quant_digests/2026-04-07_2321_benchmark-beta-pairs-meanreversion-alpha.md`。**

原因：
- `Rank 357` 已在 `research/optimization_loop/2026-04-07_2203_rank357_candlestick_pattern_next_hour_drift_intake_keep_p1.md` 完成 fresh first verdict，并正式进入 `Surviving candidate slot`
- 当前存在合法 `P1` 前排动作，所以新的 fresh intake 不能抢到它前面；但在 survivor follow-up 之后，当前最新、仍未做 first verdict 的具体对象队头就是 `2321 benchmark-beta pairs`
- 相比 `2236 chart-image trend score`，`2321` 时间更近，且主语更容易和既有 plain pairs 家族做独立性审计

因此，本轮 fresh intake 队头应切到 `benchmark-beta return differential × thresholded pair fade`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**

上一条 fresh intake 是 `research/quant_digests/2026-04-07_2117_candlestick-shorthorizon-pattern-alpha.md`。它已在 `research/optimization_loop/2026-04-07_2203_rank357_candlestick_pattern_next_hour_drift_intake_keep_p1.md` 被正式写成：
- 已压清为独立于既有 breakout / trend-shell / event overlay 家族的单资产 raw alpha intake
- 有明确 paper shortlist（`Harami / Hikkake / Three White Soldiers / Three Black Crows`）
- 有明确最小迁移壳（`15m持有4bar / 5m持有12bar`，next-hour drift）

因此它不是 `background / P0` 首判，而是合规 `keep_P1`；按 policy，它应占据 survivor 锁位，并享有那唯一一次最小 decisive follow-up。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。**

`Active P2 slot.current_target = none`。最近的 `Active P2` 仍是 `Rank 342`，但它已在 `research/optimization_loop/2026-04-05_2300_rank342_p2_exit_promote_p3_lowgas_samechain_paper_queue.md` 完成 `P2 -> P3`，并在 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md` 完成最小接线。因此本轮没有 bot2 需要兜底推进到 `P3 / P1 / P0` 的在场 `Active P2`。

## Rank / 前排合法性检查
- `Paper launch queue.current_target = none`，合法。
- `Surviving candidate slot.current_target = Rank 357`，且已有正式 rank，合法。
- `Active P2 slot.current_target = none`，合法。
- 当前前排不存在达到 `keep_P1 / P2 / P3` 但无正式 `Rank` 的对象，因此本轮无需补 rank。

## 最近证据与判断
本轮先读 fixed policy / runtime state，再看 repo 状态、最近 `optimization_loop` 与最近 `strategy_review`：

1. `research/optimization_loop/2026-04-07_2203_rank357_candlestick_pattern_next_hour_drift_intake_keep_p1.md`
   - `Rank 357` 已完成 fresh first verdict，并被明确写成 `keep_P1`；这意味着当前前排最优先动作不是再开新题，而是先消费 survivor 那唯一一次 follow-up。
2. `research/optimization_loop/2026-04-07_2216_rank33_false_reclaim_failure_routing_hint_soft_reframe_candidate.md`
   - `Rank 33` 已被诚实收口为继续留在 `soft_reframe_candidate`；不形成新的前排对象。
3. `research/optimization_loop/2026-04-07_2231_rank57b_compression_admission_forward_to_source_intake.md`
   - `Rank 57b` 已被前推为新的 `fresh/source-intake` 候选；说明它现在可以作为条件补位项进入本轮预算，但优先级仍落后于 survivor 跟进和最新 digest first verdict。
4. `research/optimization_loop/2026-04-07_2329_rank7c_bandpass_overlay_not_frontslot_intake.md`
   - `Rank 7c` 已再次被 guard 收口为 `not front-slot`；这条 residual 不应再抢当前轮前排预算。
5. `research/quant_digests/2026-04-07_2321_benchmark-beta-pairs-meanreversion-alpha.md`
   - 这是当前最新、且尚未做 first verdict 的新 paper alpha。它的主语不是普通 pair z-score，而是“先对 crypto market benchmark 去 beta，再交易双腿 residual 的均值回复”，与旧 plain-spread / OU / cointegration pairs 家族有清楚的切口可审。
6. `research/quant_digests/2026-04-07_2236_chart-image-trend-score-alpha.md`
   - 这是上一条未做 first verdict 的最新 paper alpha。它的主语是 `rolling chart image -> trend score -> next-hour drift`，是明确不同于 plain momentum / breakout / candlestick 标签器的 raw alpha；但当前证据仍偏摘要级，因此应排在 `2321` 之后做 first verdict。
7. `research/park_reframe/2026-04-03_0656_rank57-park-reframe.md`
   - `Rank 57b` 当前已不只是 drafted note，而是合规的 `source-intake candidate`。若本轮预算还有余位，可把它作为 conditional intake 小点，回答“是否已够拿到正式 fresh first verdict”。

因此，按 policy 的默认排班顺序：
`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0 归档`

本轮实际扫描结果是：
- `P3`：无待接线对象；
- `P2`：无在场 `Active P2`；
- `P1`：有且仅有 `Rank 357` 的 survivor follow-up；
- 所以第 1 条必须先给 `Rank 357`；
- 在 survivor 已诚实排入前部后，剩余预算可回到 fresh intake；
- 最新具体对象顺序应是：`2321 benchmark-beta pairs` → `2236 chart-image trend score`；
- 若预算还有余位，再用 `Rank 57b` 这条已被前推的 `source-intake candidate` 补第 4 条。

## 为什么本轮不需要 bot2 兜底升 P3
policy 只要求 bot2 在 desk review 已清楚看见某个**在场 `Active P2`** 已经足够值得进入 paper trade，而 bot3 尚未升级时，直接把它写入 `P3 / Paper launch queue` 或 handoff 路径。

本轮不满足这个前提：
- `Rank 342` 已完成 `P2 -> P3 -> connected_runner_live`；
- 当前没有在场 `Active P2`；
- 当前待做对象是 `Rank 357` 的 survivor follow-up，以及新 fresh intake / source-intake。

因此，本轮不存在 bot2 需要兜底强推到 `P3` 的漏升对象。

## Runtime writeback
本轮已按 policy 只改 `docs/BOT2_BOT3_STATE.md` 的 runtime 部分：

### 1) Fresh intake slot
- `status` 切回 `pending`
- `current_target` 切到 `research/quant_digests/2026-04-07_2321_benchmark-beta-pairs-meanreversion-alpha.md`
- `source_record` 同步切到该 digest
- `latest_result` / `latest_result_record` 保留刚落地的 `Rank 357 -> keep_P1`

### 2) cycle_plan
按当前合法动作重写为 4 条具体 pending：
1. `Rank 357 / pattern-shortlist × next-hour drift` survivor 唯一 follow-up
2. `2321 benchmark-beta return differential × thresholded pair fade` first verdict
3. `2236 chart-image trend score × next-hour drift` first verdict
4. `Rank 57b / breakout-family-local pre-break compression admission` conditional fresh/source-intake 判定

重排原则：
- 先诚实确认当前没有 `P3 / P2` 前排对象需要收口；
- 再把唯一合法的 `P1` survivor follow-up 放到队头；
- 只有在 survivor 已被诚实排入前部后，才切回新的 fresh intake；
- 新生成项统一保持 `result: none`、`status: pending`。

## 一句话总结
这轮没有漏升的 `P2`、没有待接线的 `P3`，但有一个明确的 `P1 survivor`：`Rank 357`。所以 runtime 现在必须先消费它那唯一一次 follow-up，然后再依次看 `2321 benchmark-beta pairs`、`2236 chart-image trend score`，最后用 `Rank 57b` 作为 conditional intake 补满本轮预算。
