# 2026-03-30 18:37 UTC strategy review

本轮严格按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 重排，只依据当前 runtime state、repo 状态、最近 `research/optimization_loop/`、最近 `research/strategy_review/` 与最新 digest 证据。

## 只回答 4 个问题

1. **`Paper launch queue` 是否非空？**
   - 结论：**否。**
   - 证据：`BOT2_BOT3_STATE.md` 当前仍写明 `Paper launch queue.current_target: none`；已 live 的只有 `connected_runner_live`（Rank 200 / 201 / 213 / 229），没有待接线 queue 头。

2. **本轮 `fresh intake` 是什么？**
   - 结论：本轮 fresh intake 是 **`Rank 258 / Deribit butterfly convexity static arb`**。
   - 证据：最新 optimization 结果是 `research/optimization_loop/2026-03-30_1834_rank258_deribit_butterfly_convexity_static_arb_intake_keep_p1.md`；对象主语已锁定为 `Deribit BTC same-expiry options 链上的 butterfly / convexity static-arb 事件`，fresh intake 首判已完成并给出 `keep_P1`。

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - 结论：**值得。**
   - 证据：上一条 fresh intake 是 **`Rank 257 / on-chain shock × predicted vol spike / BTC short-horizon mean reversion`**；其首判已在 `research/optimization_loop/2026-03-30_1811_rank257_onchain_vol_spike_btc_mr_intake_keep_p1.md` 完成。对象边界、事件锚、执行窗与 friction ladder 已成型，且 blocker 很集中——当前唯一该回答的是统一事件对齐与统一成本口径下，`MR vs continuation` 到底哪一侧还能留下可审计的成本后 edge。因此它正符合 policy 所说“上一条 fresh intake 的唯一一次诚实 follow-up”。

4. **当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - 结论：**不存在。**
   - 证据：`BOT2_BOT3_STATE.md` 当前 `Active P2 slot.current_target: none`。最近的 `Rank 235` 已在 `research/optimization_loop/2026-03-29_1230_rank235_p2_exit_rescope_p1_honesty_gap.md` 完成 `one-time P2 -> P1 re-scope`，不再属于当前 active P2。

## rank / 前排合法性检查

- `Paper launch queue`: 无当前 queue 头
- `Fresh intake`: `Rank 258`，已有正式 rank
- `Surviving candidate`: `Rank 257`，已有正式 rank
- `Active P2`: `none`
- 结论：**本轮无需补 rank。**

## repo / recent evidence quick notes

- `git status --short` 显示大量未跟踪产物；本轮只把它当环境噪音，不据此反推 policy 或改排班。
- 最近 optimization 证据链里会改变前排排班顺序的新增结果只有三条：
  - `2026-03-30_1801_rank255_survivor_followup_background_p0.md`：`Rank 255` 的唯一 survivor follow-up 已完成，结论是回 `background/P0`
  - `2026-03-30_1811_rank257_onchain_vol_spike_btc_mr_intake_keep_p1.md`：`Rank 257` fresh intake 首判完成，进入 survivor 候选链
  - `2026-03-30_1834_rank258_deribit_butterfly_convexity_static_arb_intake_keep_p1.md`：`Rank 258` fresh intake 首判完成，成为当前 latest fresh intake
- 最近 strategy review 到 `2026-03-30_1738_strategy-review.md` 为止，前排唯一尚未同步的新状态，就是 survivor 已从 `Rank 255` 切换到 `Rank 257`，fresh intake 已更新为 `Rank 258`。

## cycle_plan 重排结论

按 policy 默认顺序扫描合法动作：
1. `P3 handoff`：无待接线 queue 头
2. `P2 admission/promote/park`：无 Active P2
3. `P1 唯一一次诚实检查`：有，而且当前唯一 survivor 是 `Rank 257`
4. 因此前排链条未完全收口前，第一优先级必须先排 `Rank 257` 的唯一 follow-up；其后才能用剩余预算补新的具体 intake

因此本轮把 `cycle_plan` 重写为：
1. `Rank 257 / on-chain shock × predicted vol spike / BTC short-horizon mean reversion` survivor follow-up
2. `bear shock → short-alt lag pocket` fresh intake
3. `arb gap amplify → delayed closure` fresh intake
4. `symmetric τ-band liquidity harvest × band-exit reset` fresh intake

## 为什么这样改 state

- `Rank 255` 已经完成唯一 follow-up 并回 `background/P0`，不能继续占前排。
- `Rank 257` 是上一条 fresh intake，且明确值得那唯一一次 follow-up，因此必须占据 survivor 槽位与 `cycle_plan` 第 1 项。
- `Rank 258` 已经完成 fresh intake 首判并获得正式 rank；它是当前 latest fresh intake，不再是 survivor。
- 当前没有 `P3` 待接线对象，也没有 `Active P2`，所以后 3 个预算位可以诚实回到新的具体 intake。
- 新 intake 只从最近 digest 中挑选具体对象，没有把 background pool 旧候选自动拉回前排。

## P2 -> P3 兜底裁判是否触发

**不触发。**

因为：
- 当前 `Paper launch queue = none`
- 当前 `Active P2 = none`
- 最近 desk review 没有出现“对象已明显足够进入 paper trade / paper launch，但 bot3 尚未升级”的 active P2

因此本轮不新增 `P3 / Paper launch queue` 写回，也不伪造 handoff 路径。

## writeback

- 已更新：`docs/BOT2_BOT3_STATE.md`
- 更新内容：只重写 `cycle_plan`，使其与最新前排链条同步（`Rank 257` survivor 优先，`Rank 258` 保持 latest fresh intake）
- 未改写：policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排
- 本轮没有对象达到 bot2 兜底直推 `P3` 的门槛，因此无新增 P3 handoff 写回
