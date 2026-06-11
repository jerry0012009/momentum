# 2026-04-08 04:17 UTC strategy review

## Scope
按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 执行本轮 40 分钟 desk review；本轮只更新 runtime state，不改 policy / brief / operating card / auto loop / cron prompt。

## 先回答 4 个问题

### 1) `Paper launch queue` 是否非空？
**否。**

- `Paper launch queue.current_target = none`
- `Rank 200 / 201 / 213 / 229 / 342` 都已在 `connected_runner_live`
- 最近 queue 侧完成记录仍是 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md`

因此当前没有待接线的 `P3 / Paper launch queue` 头对象。

### 2) 本轮 `fresh intake` 是什么？
**是 `research/quant_digests/2026-04-08_0405_htf-ema-rsi-pullback-trend-shell.md`。**

原因：
- `research/quant_digests/2026-04-08_0237_exchange-interruption-crossvenue-arb-alpha.md` 已在 `research/optimization_loop/2026-04-08_0410_rank362_exchange_interruption_crossvenue_intake_keep_p1.md` 完成 first verdict，并获得正式 `Rank 362`；
- 既然它已经进入 `Surviving candidate slot`，就不再属于“待判 first verdict 的 fresh intake”；
- 当前尚未做 first verdict、且时间上最新的具体新对象，是 `2026-04-08_0405_htf-ema-rsi-pullback-trend-shell.md`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**

这里的“上一条 fresh intake”就是 `Rank 362 / venue-freeze price gap × re-link close`。

理由：
- 它已经把主语压清为 `stale venue quote / heartbeat gap -> healthy reference gap -> re-link close`；
- 事件代理已明确为 `quote_age_sec / heartbeat_gap_sec / stale_flag`；
- 最小执行壳也已明确到同标的跨所、深度约束、fee/slippage/orphan-leg 风险；
- 当前缺的不是“对象是否存在”，而是**现代主流 venues 上用 proxy 事件做 quickcheck 后，after-cost capture 是否仍成立**。

这正好符合 policy 对 survivor 的定义：值得保留且只值得保留 **1 次** 便宜、决定性的 follow-up。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。**

- `Active P2 slot.current_target = none`
- 最近一次需要 bot2 兜底裁决的 `P2` 仍是 `Rank 342`，但它已经完成 `P2 -> P3 -> connected_runner_live`
- 本轮不存在“desk review 已明确够格升 P3、但 bot3 尚未升级”的在场 `Active P2`

因此本轮不存在需要 bot2 直接改写进 `P3 / Paper launch queue` 的漏升对象。

## 最近读取与证据核对
1. `docs/BOT2_BOT3_POLICY.md`
2. `docs/BOT2_BOT3_STATE.md`
3. repo 工作树：`git status --short --branch` 显示大量历史未跟踪研究/临时文件；这只算 repo hygiene 现状，不构成 background pool 自动 reopen 的理由
4. 最近 optimization 记录：
   - `2026-04-08_0416_rank60b_conditional_fresh_intake_blocked_by_survivor_lock.md`
   - `2026-04-08_0410_rank362_exchange_interruption_crossvenue_intake_keep_p1.md`
   - `2026-04-08_0305_rank361_survivor_followup_exhausted_background.md`
5. 最近 strategy review：
   - `2026-04-08_0303_strategy-review.md`
   - `2026-04-08_0204_strategy-review.md`
6. 最近新 digest：
   - `2026-04-08_0405_htf-ema-rsi-pullback-trend-shell.md`
   - `2026-04-08_0322_polymarket-kalshi-samehour-strike-arb-alpha.md`
7. recent park reframe 候选：`research/park_reframe/2026-04-08_0019_rank28-park-reframe.md`

## Rank / 前排合法性检查
- `Paper launch queue.current_target = none`，合法
- `Surviving candidate slot.current_target = Rank 362`，且 `Rank 362` 已有正式 rank，合法
- `Active P2 slot.current_target = none`，合法
- 当前前排不存在达到 `keep_P1 / P2 / P3` 但无 rank 的对象，因此本轮无需补 rank

## 排班判断
按 policy 默认顺序：
`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0`

本轮扫描结果：
- `P3`：无待接线对象
- `P2`：无在场 `Active P2`
- `P1`：存在明确 survivor `Rank 362`，必须优先于所有新 intake 收口
- 只有把 `Rank 362` 的唯一 follow-up 诚实排到前面后，才能切回新的 `fresh intake`
- 在没有 `P3/P2` 占位的情况下，剩余预算可补具体 fresh intake / conditional fresh intake

因此，上一版 runtime 已经完成的 `Rank 361` 和 `Rank 362` 结果不能继续留在新一轮 `cycle_plan` 里；本轮必须把 plan 改成新的 pending 队列，而不是沿用已完成项目。

## Runtime writeback
本轮已重写 `docs/BOT2_BOT3_STATE.md`：

### Fresh intake slot
- `status` 从 `done` 改为 `pending`
- `current_target` 改为 `research/quant_digests/2026-04-08_0405_htf-ema-rsi-pullback-trend-shell.md`
- `latest_result` 保留为上一条 fresh intake `Rank 362` 的 first verdict

### cycle_plan
1. `Rank 362 / venue-freeze price gap × re-link close`
   - 作为当前唯一合法 survivor，做那 1 次决定性 follow-up，直接回答 `promote_P2` 还是 `keep_P1 exhausted -> background`
2. `research/quant_digests/2026-04-08_0405_htf-ema-rsi-pullback-trend-shell.md`
   - 作为当前切回 fresh intake 后的首条具体对象
3. `research/quant_digests/2026-04-08_0322_polymarket-kalshi-samehour-strike-arb-alpha.md`
   - 作为前排 survivor 与首条 fresh intake 已诚实排入后的 conditional fresh intake
4. `research/park_reframe/2026-04-08_0019_rank28-park-reframe.md`
   - 作为剩余预算里的具体 conditional fresh intake

新生成项均保持：
- `result = none`
- `status = pending`

## 为什么本轮不需要 bot2 兜底升 P3
policy 要求 bot2 在 desk review 已明确看到某个**在场 `Active P2`** 已足够值得进入 paper trade，而 bot3 尚未升级时，直接改写到 `P3 / handoff`。

本轮不满足该条件：
- `Active P2 = none`
- 最近完成的 `Rank 342` 已经在 `connected_runner_live`
- 当前真正需要 bot2 做的是：**把 Rank 362 的 survivor follow-up 提到本轮最前，并把 fresh intake 队头切到 04:05 的新 digest**

因此，本轮不存在需要 bot2 强制推进到 `P3 / Paper launch queue` 的漏升对象。

## Ops note
- 已成功发送中文邮件摘要到默认收件人。
- `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 本轮已执行，但其内部 `build_site_index.py` 进程被系统 `SIGKILL`，因此首页刷新未成功完成；runtime state 与 strategy-review 日志已落库。

## 一句话总结
本轮没有待接线的 `P3`，也没有漏升的 `Active P2`；唯一必须优先收口的是 `Rank 362` 的 survivor follow-up，之后 fresh intake 队头应切到 `2026-04-08_0405_htf-ema-rsi-pullback-trend-shell.md`，剩余预算再给 `2026-04-08_0322` 与 `Rank 28`。