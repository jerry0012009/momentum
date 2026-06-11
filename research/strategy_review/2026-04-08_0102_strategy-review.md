# 2026-04-08 01:02 UTC strategy review

## Scope
按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 执行本轮 40 分钟 desk review；本轮只更新 runtime state，不改 policy / brief / operating card / auto loop / cron prompt。

## 先回答 4 个问题

### 1) `Paper launch queue` 是否非空？
**否。**

当前 `Paper launch queue.current_target = none`。`Rank 200 / 201 / 213 / 229 / 342` 都已经在 `connected_runner_live`，最近完成记录仍是 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md`。因此当前没有待接线的 `P3` 队头。

### 2) 本轮 `fresh intake` 是什么？
**是 `research/quant_digests/2026-04-08_0056_rod-closepocket-hedgingmomentum-alpha.md`。**

原因很直接：
- 当前没有 `P3` 待接线对象；
- 当前没有 `Active P2`；
- 当前唯一合法前排对象是 `Rank 359` 的 survivor follow-up；
- 在把这个 survivor 诚实排到队头后，剩余 fresh 队头就应该切到最新、尚未做 first verdict 的具体对象；
- 最新的新 digest 依次是 `00:56 rod-closepocket`、`00:12 spot-perp basis shell`。

所以本轮 fresh intake 队头应切到 `rest-of-window impulse × close-pocket continuation`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**

上一条已经拿到 `keep_P1` 且仍合法占据 survivor 槽位的 fresh intake 是 `Rank 359 / chart-image trend score × next-hour drift`。`research/optimization_loop/2026-04-08_0027_rank359_chart_image_trend_score_intake_keep_p1.md` 已经把它压清为：
- 独立于既有 `momentum / candlestick / breakout` 家族的 raw alpha intake；
- 有明确的 `15m/5m` 最小迁移壳；
- 有清楚的 follow-up 焦点：相对 `simple ROC / EMA slope` 的增量、以及 after-cost 可交易性。

因此它合规地享有那唯一一次 survivor follow-up，且在诚实收口前不能被新的 keep_P1 候选挤掉。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。**

`Active P2 slot.current_target = none`。最近的在场 `P2` 仍是 `Rank 342`，但它已经完成 `P2 -> P3 -> connected_runner_live`，所以本轮不存在 bot2 需要兜底裁决出口的 `Active P2`。

## Rank / 前排合法性检查
- `Paper launch queue.current_target = none`，合法。
- `Surviving candidate slot.current_target = Rank 359`，且已有正式 `Rank`，合法。
- `Active P2 slot.current_target = none`，合法。
- 当前前排不存在达到 `keep_P1 / P2 / P3` 却无正式 rank 的对象，因此本轮无需补 rank。

## 最近证据摘要
本轮先读 fixed policy / runtime state，再看 repo 状态、最近 `optimization_loop` 与最近 `strategy_review`：

1. `research/optimization_loop/2026-04-08_0058_rank57b_source_intake_candidate_kept.md`
   - `Rank 57b` 已被诚实收口为继续留在 `source-intake candidate`；可以作为条件补位项，但不能抢前排。
2. `research/optimization_loop/2026-04-08_0027_rank359_chart_image_trend_score_intake_keep_p1.md`
   - `Rank 359` 已完成 fresh first verdict，并明确进入 survivor 轨道；这决定了当前轮第 1 项必须先消费这唯一一次 follow-up。
3. `research/optimization_loop/2026-04-08_0002_rank358_benchmark_beta_pairs_intake_keep_p1.md`
   - `Rank 358` 已经拿过 `keep_P1`，但按当前运行槽位硬约束，只有上一条 fresh intake 才能占 survivor；既然 `Rank 359` 已成为当前 survivor，`Rank 358` 不再属于前排，不得自动重拉回来。
4. `research/quant_digests/2026-04-08_0056_rod-closepocket-hedgingmomentum-alpha.md`
   - 这是当前最新且尚未做 first verdict 的新 paper alpha；主语是 `pre-close cumulative return -> close-pocket same-direction continuation`，依赖真实时钟锚点，和 plain trend / session seasonality 不是同一件事。
5. `research/quant_digests/2026-04-08_0012_spot-perp-openclose-basis-shell.md`
   - 这是当前次新的新 repo alpha；主语是 `same-underlier executable basis dislocation -> close-spread mean reversion`，并自带 open/close hysteresis 执行壳，优先级高于再去翻旧 digest。
6. repo 状态显示工作树里仍有大量历史临时文件未跟踪，但这不改当前 policy，也不构成把旧候选拉回前排的理由。

## 本轮排班判断
按 policy 默认顺序：
`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0/background`

本轮扫描结果是：
- `P3`：无待接线对象；
- `P2`：无在场 `Active P2`；
- `P1`：有且仅有 `Rank 359` 的 survivor follow-up；
- 因此第 1 条必须先给 `Rank 359`；
- 然后才能切回新的 fresh intake；
- 当前最该排的 fresh 顺序是：`00:56 rod-closepocket` -> `00:12 spot-perp basis shell`；
- 若预算仍有余位，再用 `Rank 57b` 作为 conditional fresh/source-intake 补位。

## 为什么本轮不需要 bot2 兜底升 P3
policy 只要求 bot2 在 desk review 已明确看到某个**在场 `Active P2`** 已经足够值得 paper trade，而 bot3 尚未升级时，直接改写到 `P3 / handoff`。

本轮不满足该前提：
- 当前 `Active P2 = none`；
- 最近的 `Rank 342` 已经完成 `P2 -> P3 -> connected_runner_live`；
- 当前前排任务全部属于 `P1 survivor + 新 fresh intake`。

因此，本轮不存在 bot2 需要兜底强推到 `P3` 的漏升对象。

## Runtime writeback
本轮已只改 `docs/BOT2_BOT3_STATE.md`：

### 1) Fresh intake slot
- `current_target` 改为 `research/quant_digests/2026-04-08_0056_rod-closepocket-hedgingmomentum-alpha.md`
- `source_record` 同步改为该 digest
- 其余 `latest_result` 仍保留最近已完成的 `Rank 359 -> keep_P1`

### 2) cycle_plan
按当前合法动作重写为 4 条具体 pending：
1. `Rank 359 / chart-image trend score × next-hour drift` survivor 唯一一次 follow-up
2. `00:56 rod-closepocket` first verdict
3. `00:12 spot-perp executable basis × open/close hysteresis shell` first verdict
4. `Rank 57b / breakout-family-local pre-break compression admission` conditional fresh/source-intake 判定

所有新项统一写成：
- `result: none`
- `status: pending`

## 执行回执
- `docs/BOT2_BOT3_STATE.md` 已按本轮结论写回。
- `research/strategy_review/2026-04-08_0102_strategy-review.md` 已落库。
- `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 连续两次执行均被系统 `SIGKILL`，本轮未成功刷新首页；未额外改脚本。
- 中文邮件摘要已通过 `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py` 成功发送到默认收件人。

## 一句话总结
这轮没有待接线的 `P3`、也没有漏升的 `Active P2`；真正该做的是先把 `Rank 359` 的唯一 survivor follow-up 收口，然后再依次看最新两条 fresh intake：`00:56 rod-closepocket` 和 `00:12 spot-perp basis shell`。