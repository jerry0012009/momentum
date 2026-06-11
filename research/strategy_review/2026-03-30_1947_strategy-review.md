# 2026-03-30 19:47 UTC strategy review

本轮严格按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 重排，只依据当前 runtime state、repo 状态、最近 `research/optimization_loop/`、最近 `research/strategy_review/` 与最新 digest 证据。

## 只回答 4 个问题

1. **`Paper launch queue` 是否非空？**
   - 结论：**否。**
   - 证据：`BOT2_BOT3_STATE.md` 当前仍写明 `Paper launch queue.current_target: none`；已 live 的只有 `connected_runner_live`（Rank 200 / 201 / 213 / 229），没有待接线 queue 头。

2. **本轮 `fresh intake` 是什么？**
   - 结论：本轮 fresh intake 是 **`Rank 259 / bear-shock short-alt lag pocket`**。
   - 证据：最新 optimization 结果是 `research/optimization_loop/2026-03-30_1941_rank259_bear_shock_short_alt_lag_pocket_intake_keep_p1.md`；对象主语已锁定为 `bear regime 下 BTC 5m shock -> alt basket 15m delayed selloff`，fresh intake 首判已完成并给出 `keep_P1`。

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - 结论：**值得。**
   - 证据：上一条 fresh intake 现在正是 **`Rank 259 / bear-shock short-alt lag pocket`** 本身；其首判刚完成，且 blocker 很集中——当前唯一还值得做的一刀，就是把 `Spot proxy` 切到可交易 `perp` 口径，并在冻结 basket、统一执行与统一成本后，诚实回答成本后 edge 是否仍存活。这正符合 policy 所说“上一条 fresh intake 的唯一一次诚实 follow-up”。

4. **当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - 结论：**不存在。**
   - 证据：`BOT2_BOT3_STATE.md` 当前 `Active P2 slot.current_target: none`。最近的 `Rank 235` 已在 `research/optimization_loop/2026-03-29_1230_rank235_p2_exit_rescope_p1_honesty_gap.md` 完成 `one-time P2 -> P1 re-scope`，不再属于当前 active P2。

## rank / 前排合法性检查

- `Paper launch queue`: 无当前 queue 头
- `Fresh intake`: `Rank 259`，已有正式 rank
- `Surviving candidate`: `Rank 259`，已有正式 rank
- `Active P2`: `none`
- 结论：**本轮无需补 rank。**

## repo / recent evidence quick notes

- `git status --short` 仍显示大量未跟踪产物；本轮只把它当环境噪音，不据此反推 policy 或改排班。
- 最近 optimization 里真正改变前排链条的新增结果是：
  - `2026-03-30_1907_rank257_survivor_followup_background_p0.md`：`Rank 257` 的唯一 survivor follow-up 已完成并回 `background/P0`
  - `2026-03-30_1941_rank259_bear_shock_short_alt_lag_pocket_intake_keep_p1.md`：`Rank 259` fresh intake 首判完成，直接成为当前 latest fresh 与 survivor
- 最近 strategy review 到 `2026-03-30_1837_strategy-review.md` 为止，仍停留在 `Rank 257 survivor / Rank 258 fresh intake`；本轮需要把 runtime state 同步到最新的 `Rank 259` 前排链条。
- 最新值得补进 fresh intake 队列的具体新对象，按时间与独立性看，依次是：
  - `research/quant_digests/2026-03-30_1919_perp-perp-funding-diff-nethurdle-alpha.md`
  - `research/quant_digests/2026-03-30_1858_percentile-entry-cointegration-pairs-alpha.md`
  - `research/quant_digests/2026-03-30_1827_tau-reset-band-liquidity-harvest-alpha.md`

## cycle_plan 重排结论

按 policy 默认顺序扫描合法动作：
1. `P3 handoff`：无待接线 queue 头
2. `P2 admission/promote/park`：无 Active P2
3. `P1 唯一一次诚实检查`：有，而且当前唯一 survivor 是 `Rank 259`
4. 因此前排链条未完全收口前，第 1 优先级必须先排 `Rank 259` 的唯一 follow-up；其后才能用剩余预算补新的具体 intake

因此本轮把 `cycle_plan` 重写为：
1. `Rank 259 / bear-shock short-alt lag pocket` survivor follow-up
2. `perp-perp funding diff × net-EV hurdle` fresh intake
3. `percentile-entry cointegration spread mean reversion` fresh intake
4. `symmetric τ-band liquidity harvest × band-exit reset` fresh intake

## 为什么这样改 state

- `Rank 257` 已经完成唯一 follow-up 并回 `background/P0`，不能继续占前排。
- `Rank 258` 虽然首判为 `keep_P1`，但它不是当前 policy 允许的 survivor——survivor 只能是上一条 fresh intake；随着 `Rank 259` fresh intake 完成，前排 survivor 锁定权已切换到 `Rank 259`。
- `Rank 259` 是当前最新 fresh intake，且其唯一值得继续的一刀非常明确，所以必须占据 survivor 槽位与 `cycle_plan` 第 1 项。
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
- 更新内容：只重写 `cycle_plan`，使其与最新前排链条同步（`Rank 259` survivor 优先，后续补 3 条新的具体 intake）
- 未改写：policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排
- 本轮没有对象达到 bot2 兜底直推 `P3` 的门槛，因此无新增 P3 handoff 写回
