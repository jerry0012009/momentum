# 2026-04-22 23:51 UTC strategy review（bot2，40m desk review）

## 输入与约束确认
- 已读取：`docs/BOT2_BOT3_POLICY.md`、`docs/BOT2_BOT3_STATE.md`
- 已核对 repo 现状：`git status --short` 与最近 `research/optimization_loop/`、`research/strategy_review/`
- 本轮只改写 runtime state：`docs/BOT2_BOT3_STATE.md`
- rank 完整性检查：当前前排对象不存在无 rank 情况；`Paper launch queue.current_target = none`，`Surviving candidate = none`，`Active P2 = none`

## 四个问题（严格按要求）
1) `Paper launch queue` 是否非空？
- **否（就待执行 queue 而言为空）。**
- 说明：`connected_runner_live` 列表非空，但 `current_target = none`；当前没有仍待 bot3 补 runner / scheduler / first verified run 的 `P3` 前排对象。

2) 本轮 `fresh intake` 是什么？
- **`research/quant_digests/2026-04-22_2310_rs-semivariance-downside-continuation-alpha.md`。**
- 理由：上一条 fresh intake `research/quant_digests/2026-04-22_2118_highfreq-pairs-fixeddynamic-threshold-alpha.md` 已在 `research/optimization_loop/2026-04-22_2341_highfreq_pairs_fixeddynamic_freshintake_background_p0.md` 完成 first verdict 并收口 `background/P0`；当前前排不存在 `P3 / P2 / survivor` 动作，因此应顺延到更新、且尚未被消费的 `RS semivariance downside continuation`。

3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **不值得。**
- 上一条 fresh intake 是 `research/quant_digests/2026-04-22_2118_highfreq-pairs-fixeddynamic-threshold-alpha.md`。
- 最新 first verdict 已将它诚实收口为 `background/P0`：它只留下 pairs family 的 threshold / pair-pocket 调参提示，没有形成相对已 live `Rank 424 / 431` 的独立新增 after-cost pocket；因此不值得占用 survivor 唯一 follow-up。

4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 哪个出口最近？
- **当前不存在明确 `Active P2`。**
- 最近一个 `Active P2` 仍是 `Rank 434 / newlisting early-short bubble fade`，且已经由 bot2 兜底 `promote_P3` 后完成 launch wiring，当前不再停留在 `P2`。

## 本轮裁决
- 不需要新的 `P2 -> P3` 兜底动作：当前没有 `Active P2`。
- 不存在 survivor 锁槽对象：`Surviving candidate.current_target = none`。
- 不存在无 rank 前排对象：无需补号。
- 因此前排链条已经诚实收口，本轮继续切回 `fresh intake`；同时必须把 runtime 里已经 done / stale 的 pending 清干净，避免 bot3 继续追 `macd/ofi` 这种早已收口的旧项。

## cycle_plan 重写理由
按 policy 默认顺序扫描：
1. `P3 handoff / launch wiring`：无 pending 对象；`Rank 434` 已完成 runner + scheduler + first verified run。
2. `P2 / Active P2`：当前为 `none`，无 admission / promote / park 动作。
3. `P1 / Surviving candidate`：当前为 `none`，无唯一 follow-up 动作。
4. 因此前排链条全部收口，本轮预算回到具体 fresh intake。
5. 最新未消费的真实对象只有 `2026-04-22_2310_rs-semivariance-downside-continuation-alpha.md` 与较早但仍未被诚实消费的 `2026-04-22_0204_rollols-costaware-pairfade-shell.md`；若预算仍有余，按 policy 允许从 `research/park_reframe/INDEX.md` 的 `soft_reframe_candidate` 里挑具体对象补满，而不是让 background pool 旧候选自行回前排。

## 本轮写回的 cycle_plan
1. `research/quant_digests/2026-04-22_2310_rs-semivariance-downside-continuation-alpha.md`
2. `research/quant_digests/2026-04-22_0204_rollols-costaware-pairfade-shell.md`
3. `research/park_reframe/2026-04-10_1516_rank74-park-reframe.md`
4. `research/park_reframe/2026-04-10_0611_rank89-park-reframe.md`

## 为什么这样排
- `#1` 是当前最前、最新且尚未消费的合法 fresh intake，必须先诚实回答：`RS- dominance` 这条线到底是可独立承接的 short-only after-cost alpha，还是只是一层 downside 风险过滤。
- `#2` 是当前仍未被 first verdict 消费的旧 digest，但它不是 background reopen，而是之前就被多次 strategy review 点名、一直没真正执行的 conditional fresh intake；这轮要直接回答它相对已 live `Rank 424 / 431` 是否真有新增 shell 价值。
- `#3` 与 `#4` 不是自动把旧候选拉回前排，而是按 policy 允许的来源，从 `park_reframe/INDEX.md` 里现成的 `soft_reframe_candidate` 里挑最明确的两条具体对象；它们都被写成一次性诚实首判，只允许回答“值得 draft 成新 fresh hypothesis，还是继续 keep_park”，不会放任旧 rank 回到前排横跳。

## 状态改写摘要
- `Fresh intake slot.status`：改回 `pending`
- `Fresh intake slot.current_target`：改为 `research/quant_digests/2026-04-22_2310_rs-semivariance-downside-continuation-alpha.md`
- `Fresh intake slot.source_record`：同步改为该对象
- `Fresh intake slot.latest_result` / `latest_result_record`：保留刚完成的 `highfreq fixed/dynamic pairs -> background/P0` 收口
- `Active P2 slot.latest_result_record`：更新为本轮 review `research/strategy_review/2026-04-22_2351_strategy-review.md`
- `cycle_plan`：移除已 done / stale 的 `segmented-signature`、`highfreq fixed/dynamic` 以及早已收口却仍挂着 pending 的 `macd` / `ofi`，重写为 4 条当前仍合法的具体 pending 动作

## repo / recent evidence 摘要
- 最近 `optimization_loop` 明确新增的前排相关证据：
  - `2026-04-22_2341_highfreq_pairs_fixeddynamic_freshintake_background_p0.md`
  - `2026-04-22_2330_segmented_signature_pairfade_freshintake_background_p0.md`
  - `2026-04-22_2213_xs24h_loserwinner_stale_cycleplan_blocked.md`
  - 更早的 `2026-04-22_2010_ofi_kalman_maker_skew_freshintake_background_p0.md`、`2026-04-22_1049_macd_feetrap_freshintake_background_p0.md` 进一步证明当前 runtime 里的 `macd/ofi pending` 是 stale。
- 最近 `strategy_review` 最新一条为 `2026-04-22_2233_strategy-review.md`；本轮是在其基础上继续做 runtime 去 stale / 重排。
- repo 工作树存在大量历史未跟踪文件，但不改变本轮 runtime 调度结论。

## 尾部执行回执（非阻断）
- homepage 刷新：已按独立命令执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`；进程长时间无输出，已按 best-effort 终止处理，记为非阻断尾部失败，不回滚本轮 state / review log。
- 邮件摘要：已按独立命令执行 `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] 切到 RS semivariance 与 soft reframe intake" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-22_2351_strategy-review.md`，发送成功（`Email sent to: 18810813576@163.com`）。
