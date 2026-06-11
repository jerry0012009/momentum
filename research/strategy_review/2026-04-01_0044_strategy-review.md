# 2026-04-01 00:44 UTC strategy review

本轮严格按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 执行；先读 policy + state，再看 repo 状态、最近 `research/optimization_loop/`、最近 `research/strategy_review/`，不反向改 policy，不把 background pool 旧候选拉回前排。

## 只回答 4 个问题

1. **`Paper launch queue` 是否非空？**
   - 结论：**否。**
   - 证据：`BOT2_BOT3_STATE.md` 当前仍写明 `Paper launch queue.current_target: none`；已接线对象仍只有 `Rank 200 / 201 / 213 / 229`，没有新的 queue 头。

2. **本轮 `fresh intake` 是什么？**
   - 结论：**`Rank 275 / order-book confidence-threshold directional alpha`。**
   - 证据：最近 `optimization_loop` 头部显示 `2026-04-01_0040_rank275_orderbook_confidence_threshold_keep_p1.md` 刚完成 fresh intake 首判，并已写回 state：`Fresh intake slot.current_target = Rank 275`，且当前状态为 `locked_to_survivor`。

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - 结论：**值得。**
   - 证据：当前 survivor 就是上一条 fresh intake `Rank 275`；其首判已明确指出 cheap `5m` proxy 下 `coverage ↓ / accuracy↑ / gross edge↑` 的 admission 方向成立，只是当前 `10bps round-trip` 口径仍全 bucket 为负，因此最诚实动作不是直接升 `P2`，而是保留这唯一一次更细 microstructure + maker/taker 拆分 follow-up。

4. **当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - 结论：**不存在。当前 `Active P2 = none`。**
   - 证据：`BOT2_BOT3_STATE.md` 已明确写明 `Active P2 slot.current_target: none`；最近一次 active P2 仍是 `Rank 267`，但已在 `2026-03-31_1240_rank267_p2_exit_rescope_to_p1_exmajors_scope.md` 正式收口为一次性 `P2 -> P1 re-scope`，当前不再占 active 槽位。

## 前排 / rank 合法性检查

- `Paper launch queue.current_target = none`
- `Fresh intake slot.current_target = Rank 275`
- `Surviving candidate slot.current_target = Rank 275`
- `Active P2 slot.current_target = none`
- 当前前排对象都已有正式 `Rank`；不存在 `keep_P1 / P2 / P3` 级别却无 rank 的对象。
- 结论：**本轮无需补 rank。**

## `P2 -> P3` 兜底检查

policy 要求：若 desk review 已清楚表明某个 `Active P2` 足够值得进入 paper trade / paper launch，而 bot3 尚未升级，bot2 必须直接改写 state 进入 `P3 / handoff`。

本轮复核结果：**不触发该兜底。**
- 当前 `Active P2 = none`；
- 当前不存在“已经够格进入 paper trade、却仍被 bot3 卡在 P2”的对象；
- 因此前排最高优先级动作不是 `P3 handoff` 或 `P2 exit`，而是先收掉当前唯一合法 survivor `Rank 275`。

## repo / recent evidence 摘要

- repo 当前仍有大量未跟踪文件，但本轮只把它当作环境噪音，不反向改 policy。
- 最近 `optimization_loop` 头部顺序显示：
  1. `2026-04-01_0040_rank275_orderbook_confidence_threshold_keep_p1.md`
  2. `2026-04-01_0010_rank274_survivor_followup_background_p0.md`
  3. `2026-03-31_2346_rank274_eth_dual_thrust_keep_p1.md`
  4. `2026-03-31_2314_turning_point_confirmed_continuation_intake_background_p0_sparse_nontransferable.md`
- 这说明：
  - `Rank 274` 已经诚实收口回 `background/P0`；
  - 当前唯一前排对象就是 `Rank 275` survivor；
  - 只要这个 survivor 还未收口，按 policy 就不得把新的 `fresh intake` 排到它前面。
- 最近新 digest 里，当前最靠前且尚未执行的新对象应先看：
  - `research/quant_digests/2026-04-01_0034_cex-dex-priority-fee-delay-arb-alpha.md`
  - `research/quant_digests/2026-03-31_2156_inverse-options-maker-regime-skew-alpha.md`
  - `research/quant_digests/2026-03-31_2104_btc-leader-alt-loser-dispersion-alpha.md`

## cycle_plan 重排逻辑

按 policy 默认顺序从高到低扫描：
1. `P3 handoff`：无待接线对象；
2. `P2 admission/promote/park`：无，`Active P2 = none`；
3. `P1 survivor follow-up`：**有**，`Surviving candidate = Rank 275`，且 follow-up budget 还剩 1；
4. 因此前两类为空、但 survivor 仍未收口，当前轮必须先把 `Rank 275` 排在最前；
5. 只有把 survivor 诚实排入前部后，才允许用剩余预算补新的 `fresh intake`；
6. 新 intake 来源优先使用最近新的 alpha 报告，因此把刚生成的 `2026-04-01_0034_cex-dex-priority-fee-delay-arb-alpha.md` 插到旧候选 `2156 / 2104` 之前。

因此本轮把 `cycle_plan` 重写为：
1. `Rank 275 / order-book confidence-threshold directional alpha` survivor follow-up
2. `2026-04-01_0034_cex-dex-priority-fee-delay-arb-alpha.md`
3. `2026-03-31_2156_inverse-options-maker-regime-skew-alpha.md`
4. `2026-03-31_2104_btc-leader-alt-loser-dispersion-alpha.md`

这样写符合 policy：
- 没有把新的 fresh intake 排到未收口的 survivor 前面；
- 没有伪造空槽确认动作去占轮次；
- `Rank 275` 继续享有 survivor 锁定权，不被新的 `keep_P1` 覆盖；
- 剩余预算全部填入具体对象，而不是抽象模板句。

## writeback

- 已更新：`docs/BOT2_BOT3_STATE.md`
- 更新内容：
  - 保持 `Paper launch queue = none`、`Active P2 = none`；
  - 保持 `Fresh intake / Surviving candidate = Rank 275`；
  - 将当前轮 `cycle_plan` 重写为 `Rank 275 survivor follow-up -> 0034 CEX/DEX priority-fee delay arb -> 2156 inverse options maker skew -> 2104 BTC leader × alt loser dispersion`；
  - 新生成项全部满足 `result = none`、`status = pending`。
- 未改写 policy / brief / operating card / auto loop / cron prompt。
- 未自动把 background pool 旧候选拉回前排。
