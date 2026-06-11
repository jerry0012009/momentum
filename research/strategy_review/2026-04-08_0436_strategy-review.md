# 2026-04-08 04:36 UTC strategy review

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
**是 `research/quant_digests/2026-04-08_0322_polymarket-kalshi-samehour-strike-arb-alpha.md`。**

原因：
- `research/quant_digests/2026-04-08_0405_htf-ema-rsi-pullback-trend-shell.md` 已在 `research/optimization_loop/2026-04-08_0430_rank363_htf_ema_rsi_pullback_intake_keep_p1.md` 完成 first verdict，并获得正式 `Rank 363`；
- 既然它已经进入 `Surviving candidate slot`，就不再属于“待判 first verdict 的 fresh intake”；
- 当前尚未做 first verdict、且时间上最新的具体新对象，是 `2026-04-08_0322_polymarket-kalshi-samehour-strike-arb-alpha.md`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**

这里的“上一条 fresh intake”就是 `Rank 363 / HTF EMA gate × 15m RSI pullback continuation`。

理由：
- 它已经把主语压清为 `HTF EMA200 regime gate -> LTF shallow pullback continuation`，不是泛指标堆叠教程；
- raw alpha 本体、确认层和风险壳已经分层；
- 最小实验壳也已明确到标的、周期、gate、entry 与成本口径；
- 当前缺的不是“对象是否存在”，而是**统一样本、统一成本下的 clean-room post-cost replication**，以及增益到底来自 continuation 本体还是只是在吃泛趋势 beta。

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
3. repo 工作树：`git status --short` 显示大量历史未跟踪临时文件；这只算 repo hygiene 现状，不构成 background pool 自动 reopen 的理由
4. 最近 optimization 记录：
   - `2026-04-08_0430_rank363_htf_ema_rsi_pullback_intake_keep_p1.md`
   - `2026-04-08_0423_rank362_survivor_followup_exhausted_background.md`
   - `2026-04-08_0416_rank60b_conditional_fresh_intake_blocked_by_survivor_lock.md`
5. 最近 strategy review：
   - `2026-04-08_0417_strategy-review.md`
   - `2026-04-08_0303_strategy-review.md`
6. 最近新 digest / intake 候选：
   - `2026-04-08_0322_polymarket-kalshi-samehour-strike-arb-alpha.md`
   - `2026-04-07_2321_benchmark-beta-pairs-meanreversion-alpha.md`
7. recent park reframe 候选：`research/park_reframe/2026-04-08_0019_rank28-park-reframe.md`

## Rank / 前排合法性检查
- `Paper launch queue.current_target = none`，合法
- `Surviving candidate slot.current_target = Rank 363`，且 `Rank 363` 已有正式 rank，合法
- `Active P2 slot.current_target = none`，合法
- 当前前排不存在达到 `keep_P1 / P2 / P3` 但无 rank 的对象，因此本轮无需补 rank

## 排班判断
按 policy 默认顺序：
`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0`

本轮扫描结果：
- `P3`：无待接线对象
- `P2`：无在场 `Active P2`
- `P1`：存在明确 survivor `Rank 363`，必须优先于所有新 intake 收口
- 只有把 `Rank 363` 的唯一 follow-up 诚实排到前面后，才能切回新的 `fresh intake`
- 在没有 `P3/P2` 占位的情况下，剩余预算可补具体 fresh intake / conditional fresh intake

因此，本轮 runtime 必须从上一版已完成的 `Rank 362` / `2026-04-08_0405` 结果继续向前滚动，而不是把已 done 项继续留在当前轮 `cycle_plan`。

## Runtime writeback
本轮已重写 `docs/BOT2_BOT3_STATE.md`：

### Fresh intake slot
- `status` 改为 `pending`
- `current_target` 改为 `research/quant_digests/2026-04-08_0322_polymarket-kalshi-samehour-strike-arb-alpha.md`
- `latest_result` 写回上一条 fresh intake `Rank 363` 的 first verdict

### Surviving candidate slot
- 保持 `Rank 363 / HTF EMA gate × 15m RSI pullback continuation`
- `followup_budget_remaining = 1`
- `latest_result` 明确为：这一轮 survivor follow-up 只应回答 unified-sample / unified-cost 下的 post-cost expectancy 与 alpha 归因问题

### cycle_plan
1. `Rank 363 / HTF EMA gate × 15m RSI pullback continuation`
   - 作为当前唯一合法 survivor，做那 1 次决定性 follow-up，直接回答 `promote_P2` 还是 `keep_P1 exhausted -> background`
2. `research/quant_digests/2026-04-08_0322_polymarket-kalshi-samehour-strike-arb-alpha.md`
   - 作为当前切回 fresh intake 后的首条具体对象
3. `research/park_reframe/2026-04-08_0019_rank28-park-reframe.md`
   - 作为前排 survivor 与首条 fresh intake 已诚实排入后的 conditional fresh intake
4. `research/quant_digests/2026-04-07_2321_benchmark-beta-pairs-meanreversion-alpha.md`
   - 作为剩余预算里的具体 conditional fresh intake

新生成项均保持：
- `result = none`
- `status = pending`

## 为什么本轮不需要 bot2 兜底升 P3
policy 要求 bot2 在 desk review 已明确看到某个**在场 `Active P2`** 已足够值得进入 paper trade，而 bot3 尚未升级时，直接改写到 `P3 / handoff`。

本轮不满足该条件：
- `Active P2 = none`
- 最近完成的 `Rank 342` 已经在 `connected_runner_live`
- 当前真正需要 bot2 做的是：**把 Rank 363 的 survivor follow-up 提到本轮最前，并把 fresh intake 队头切到 03:22 的 prediction-market digest**

因此，本轮不存在需要 bot2 强制推进到 `P3 / Paper launch queue` 的漏升对象。

## Ops note
- 已执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`，其内部 `build_site_index.py` 进程最终被系统 `SIGKILL`，因此首页刷新本轮未成功完成。
- 已执行 `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] 前排切到Rank363跟进与0322新 intake" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-08_0436_strategy-review.md`，邮件已发送到默认收件人。

## 一句话总结
本轮没有待接线的 `P3`，也没有漏升的 `Active P2`；唯一必须优先收口的是 `Rank 363` 的 survivor follow-up，之后 fresh intake 队头应切到 `2026-04-08_0322_polymarket-kalshi-samehour-strike-arb-alpha.md`，剩余预算再给 `Rank 28` reframe 与 `2026-04-07_2321`。