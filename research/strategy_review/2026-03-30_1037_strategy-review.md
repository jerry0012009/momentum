# 2026-03-30 10:37 UTC strategy review

本轮严格按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 重排，且只依据当前 runtime state、repo 状态、最近 `research/optimization_loop/` 与最近 `research/strategy_review/`。

## 只回答 4 个问题

1. **`Paper launch queue` 是否非空？**
   - 结论：**否。**
   - 证据：`BOT2_BOT3_STATE.md` 当前写明 `Paper launch queue.current_target: none`；已 live 的仅是 `connected_runner_live` 列表（Rank 200 / 201 / 213 / 229），没有待接线 queue 头。

2. **本轮 `fresh intake` 是什么？**
   - 结论：本轮刚完成的 fresh intake 是 **`Rank 251 / intraday hour-pair momentum / reversal within pseudo trading day`**。
   - 证据：`research/optimization_loop/2026-03-30_1033_rank251_intraday_hourpair_pseudoday_intake_keep_p1.md` 已明确写成 fresh intake first verdict，并已写回 state。

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - 结论：**值得，而且当前就该占用 survivor 槽。**
   - 证据：Rank 251 不是旧 `clock-conditioned mode switch` / `weekday-hour schedule` / `open-preclose double-clock` 的换壳；它把主语锁在 `pseudo trading day` 内的 `earlier hour -> later hour` 映射，允许 continuation 与 reversal 在不同 hour-pair 共存，且已具备 `BTCUSDT perp × 1h predictor -> 15m/5m execution` 的最小 honest 骨架。当前最便宜且 decisive 的唯一 follow-up 是：在 `UTC 00/08/16` 锚点约束下做 rolling / OOS + anchor sensitivity 审查，判断是否还留有少数稳定 pair。

4. **当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - 结论：**不存在。**
   - 证据：`BOT2_BOT3_STATE.md` 当前 `Active P2 slot.current_target: none`。上一条 P2 相关对象 `Rank 235` 已在 `research/optimization_loop/2026-03-29_1230_rank235_p2_exit_rescope_p1_honesty_gap.md` 中完成 `one-time P2 -> P1 re-scope`，因此当前没有合法 active P2 需要做出口裁决，也不存在 bot2 需要兜底直推 `P3` 的对象。

## rank / 前排合法性检查

- 当前前排对象检查结果：
  - `Paper launch queue`: 无当前 queue 头，不涉及 rank 缺失
  - `Surviving candidate`: `Rank 251`，已有正式 rank
  - `Active P2`: none
- 结论：**本轮无需补 rank。**

## 本轮默认排班顺序重写结论

前排收口顺序按 policy 落地为：
1. `P3 handoff`：无待接线 queue 头，因此不占本轮预算；
2. `P2 admission/promote/park`：无明确 Active P2，因此不占本轮预算；
3. `P1 唯一一次诚实检查`：必须先做 `Rank 251` survivor follow-up；
4. 在 survivor 已诚实排入前部后，再用剩余预算补最新 fresh intake。

因此本轮 `cycle_plan` 改写为：
1. `Rank 251` survivor follow-up（pending）
2. `order-flow imbalance × fill-aware maker/taker routing` fresh intake（pending）
3. `same-venue conversion / parity reversal` fresh intake（pending）
4. `trend continuation × pullback re-entry × correlation-budget shell` fresh intake（pending）

## 本轮 writeback

- 已更新：`docs/BOT2_BOT3_STATE.md`
- 未改写：policy / brief / operating card / cron prompt
- 未把 background pool 旧候选自动拉回前排

## repo / recent evidence quick notes

- `git status --short` 显示 repo 当前有大量未跟踪产物；本轮未据此反向改 policy，只把它视作环境噪音。
- 最近 optimization 证据链显示：
  - `Rank 250` survivor 已在 `2026-03-30_1011` 诚实收口回 `background/P0`
  - `Rank 251` 已在 `2026-03-30_1033` 完成 fresh intake first verdict 并进入 survivor
- 最近 strategy review 仅显示上一轮 `2026-03-30_0940_strategy-review.md` 等常规 review 节奏，未提供足以覆盖当前 runtime truth 的更高优先级信号。
