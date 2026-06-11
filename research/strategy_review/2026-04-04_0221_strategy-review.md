# Strategy Review — 2026-04-04 02:21 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short --branch`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-04_0120_rank320_survivor_followup_promote_p2.md`
  - `research/optimization_loop/2026-04-04_0101_rank320_wilder_rsi_fast_exit_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-04_0030_rank319_dc_vwap_ema_first_verdict_keep_p1.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-04_0111_strategy-review.md`
  - `research/strategy_review/2026-04-04_0007_strategy-review.md`

## repo 状态摘录
- 当前 repo 有大量工作区外层临时文件 `?? ../../tmp_*` 与 `?? ../../transcripts/` 未跟踪；这些只作为环境噪音 evidence，不改变本轮 policy / state 解释。
- 本轮按硬约束只更新 `docs/BOT2_BOT3_STATE.md`，未改动 policy / brief / operating card / auto loop / cron prompt。

## 只回答 4 个问题

1) `Paper launch queue` 是否非空？
- 否。
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有新的待接线 queue 头对象。

2) 本轮 `fresh intake` 是什么？
- 当前运行态里 **没有正在占用的 fresh intake**。
- 依据：`Fresh intake slot.current_target = none`，且最新 fresh intake `Rank 320` 已在 `research/optimization_loop/2026-04-04_0120_rank320_survivor_followup_promote_p2.md` 完成 survivor follow-up 后升入 `Active P2`，fresh slot 已释放。
- 因此本轮若预算允许、且前排动作已诚实排入，下一条 fresh intake 头应是：
  - `research/quant_digests/2026-04-04_0020_extreme-divergence-exhaustion-fade-alpha.md`

3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 不存在可再分配的 survivor follow-up。
- 上一条 fresh intake 就是 `Rank 320 / Wilder RSI breakout × EMA200/ADX/volume allow × fast RSI-45 exit`；它那唯一一次 follow-up 已经在 `2026-04-04_0120_rank320_survivor_followup_promote_p2.md` 被用掉，并且答案已经是 `promote_P2`。
- 因而本轮不能再把它当 survivor 续写；后续必须按 `Active P2 admission` 逻辑收口。

4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 存在。
- 当前明确 `Active P2 = Rank 320 / Wilder RSI breakout × EMA200/ADX/volume allow × fast RSI-45 exit`。
- 基于最近 desk evidence，它当前离 **`P3` 出口最近**，不是 `P1` 或 `P0`：
  - 已经完成从 `P1 survivor` 到 `P2` 的 decisive level change；
  - 已证明同一策略壳在 `BTC/ETH/SOL × 5m/15m` 上存在诚实、可复现、post-cost 为正的 admission 路径；
  - 当前剩下的是 `P2 admission` 的正式收口，重点在 `honesty/execution realism`、更长时间稳定性与参数稳定性，而不是回到“它是不是只有局部组件价值”的旧问题。
- 但就现有证据，还**没有**达到 bot2 必须直接兜底推入 `P3 / Paper launch queue` 的门槛；`2026-04-04_0120` 的结论本身也明确写明“足以升 P2，但还不足以直接升 P3”。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Fresh intake slot.current_target = none`
- `Surviving candidate slot.current_target = none`
- `Active P2 slot.current_target = Rank 320 / Wilder RSI breakout × EMA200/ADX/volume allow × fast RSI-45 exit`
- 当前前排对象不存在已达 `keep_P1 / P2 / P3` 但无正式 rank 的情况；本轮无需补新的整数 `Rank`。

## P2 -> P3 兜底裁判检查
- 当前只有一个明确 `Active P2`：`Rank 320`。
- 最近证据显示它已经明显高于 `P1`，且出口方向更接近 `P3`；但还没有清楚完成 `honesty / execution realism` 与更长窗 `time / parameter stability` 的 admission 收口。
- 因此本轮 **不**直接把它兜底写入 `P3 / Paper launch queue`；更诚实的做法是把本轮前两项都锁给 `Rank 320` 的 admission，争取下一轮把出口判定推清。

## 本轮排班改写
按 policy 默认顺序扫描后：
- `P3`：无待接线对象
- `P2`：有且只有一个明确对象 —— `Rank 320`
- `P1`：无 survivor
- 因此前两项必须先给 `Rank 320` 的 admission / promote / park 决策，不能跳回 fresh intake 抢前排

因此本轮把 `cycle_plan` 重写为 4 项：
1. `Rank 320`：先做 `honesty / execution realism + post-cost effectiveness` admission，回答更诚实执行口径下 edge 是否仍厚到值得继续朝 `P3` 走
2. `Rank 320`：若第 1 项未直接给出口，再做 `time stability + parameter stability` admission，判断它更接近 `P3` 还是应 `re-scope/P0`
3. `research/quant_digests/2026-04-04_0020_extreme-divergence-exhaustion-fade-alpha.md`：作为新的 fresh intake
4. `research/quant_digests/2026-04-03_2103_reverse-grid-tradecontrol-meanreversion-alpha.md`：作为 conditional fresh intake

改写理由：
- 当前存在合法 `Active P2`，已有前排对象的收口优先级高于新的发现；
- `Rank 320` 目前离 `P3` 最近，最该优先回答的是 admission 里最会改变层级的两件事：更诚实执行口径是否还能站住，以及时间/参数稳定性是否支撑继续朝 `P3` 走；
- 由于 `p2_last_evidence_axis = survivor_followup_asset_timeframe_admission_path`，本轮不能继续重复同一 axis，必须换到更高杠杆的 `honesty/execution/time/parameter` admission；
- 当前没有 survivor，也没有待接线 `P3`，因此在把 `Rank 320` 的前排动作诚实排入前两项后，剩余预算才切回具体 fresh intake；
- 未把 `Rank 319` 或任何 background pool 旧候选自动拉回前排。

## 本轮写回
- 已更新：`docs/BOT2_BOT3_STATE.md`（仅重写 `cycle_plan`）
- 未改动 policy / brief / operating card / auto loop / cron prompt。
