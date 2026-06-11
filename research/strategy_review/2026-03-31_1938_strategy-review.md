# 2026-03-31 19:38 UTC strategy review

本轮严格按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 执行；先读 policy + state，再看 repo 状态、最近 `research/optimization_loop/`、最近 `research/strategy_review/`，不反向改 policy，不把 background pool 旧候选拉回前排。

## 只回答 4 个问题

1. **`Paper launch queue` 是否非空？**
   - 结论：**否。**
   - 证据：`BOT2_BOT3_STATE.md` 当前仍写明 `Paper launch queue.current_target: none`；`Rank 200 / 201 / 213 / 229` 都已在 `connected_runner_live`，没有新的待接线 queue 头。

2. **本轮 `fresh intake` 是什么？**
   - 结论：**`plateau-first parameter selection + in-trade ADF kill-switch pairs`（`Rank 272`）。**
   - 证据：`Fresh intake slot.current_target` 已是该对象，`latest_result_record = research/optimization_loop/2026-03-31_1936_rank272_pairs_plateau_adf_killswitch_intake_keep_p1.md` 已明确写成 fresh intake 首判完成、正式分配 `Rank 272` 并首判 `keep_P1`。

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - 结论：**值得。**
   - 证据：`Surviving candidate slot.current_target = Rank 272`，`followup_budget_remaining = 1`；最近 intake 结论已把对象收口成一个独立的 `beta-hedged cointegration spread mean reversion` raw alpha skeleton，真正值得测的是多 pair / 多 venue clean-room replication，而不是继续围绕单个 repo best-cell 打转。当前最便宜且 decisive 的下一步，就是在统一分腿成本和统一 kill-switch 口径下，直接回答多 pair 是否仍有 `10~15bps` 成本后存活 pocket，以及 `ADF kill-switch` 是否真能减少 tail loss / duration drift。

4. **当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - 结论：**不存在。当前 `Active P2 = none`。**
   - 证据：`BOT2_BOT3_STATE.md` 已写明 `Active P2 slot.current_target: none`；最近一条 `Active P2` 是 `Rank 267`，并已在 `research/optimization_loop/2026-03-31_1240_rank267_p2_exit_rescope_to_p1_exmajors_scope.md` 收口为一次性 `P2 -> P1 re-scope`，当前不再占 active 槽位。

## 前排 / rank 合法性检查

- `Paper launch queue.current_target = none`
- `Surviving candidate slot.current_target = Rank 272`
- `Active P2 slot.current_target = none`
- 当前前排对象里唯一占槽的是 `Rank 272`，其正式 rank 已存在。
- 结论：**本轮无需补 rank。**

## `P2 -> P3` 兜底检查

policy 要求：若 desk review 已清楚表明某个 `Active P2` 足够值得进入 paper trade / paper launch，而 bot3 尚未升级，bot2 必须直接改写 state 进入 `P3 / handoff`。

本轮复核结果：**不触发该兜底。**
- 当前 `Active P2 = none`；
- 不存在“已经够格 paper trade 但仍被 bot3 卡在 P2”的对象；
- 因此本轮不应伪造 `P3`，而应优先收口 `Rank 272` 的 survivor follow-up。

## cycle_plan 重排逻辑

按 policy 默认顺序从高到低扫描：
1. `P3 handoff`：无待接线对象；
2. `P2 admission/promote/park`：无，`Active P2 = none`；
3. `P1 survivor follow-up`：有，且必须优先执行 `Rank 272` 的唯一一次 decisive follow-up；
4. 在 survivor 动作已经被诚实排到前部后，才用剩余预算补新的 `fresh intake`。

结合最近结果，本轮把 `cycle_plan` 重写为：
1. `Rank 272 / plateau-first parameter selection + in-trade ADF kill-switch pairs` survivor follow-up
2. `research/quant_digests/2026-03-31_1929_edgex-lighter-samecontract-crossvenue-arb-alpha.md`
3. `research/quant_digests/2026-03-31_1748_cheapest-spot-richest-perp-contango-alpha.md`
4. `research/quant_digests/2026-03-31_1714_positive-premium-basis-reversion-alpha.md`

这样写符合 policy：
- 没把新的 intake 排到现存 `P1 survivor` 前面；
- 没有伪造 `P2` 或 `P3` 出口；
- 新 intake 都来自最近新的 digest，而不是从 background pool 自动 reopen 旧候选；
- 前两项都是真实推进动作，不是空模板；
- `Rank 272` 的唯一 survivor follow-up 继续保有前排锁定权，没有被另一条新的 `keep_P1` 候选覆盖；
- 在 survivor 之后优先放入最新的 `same-contract perp cross-venue quote-gap reversion` 新 digest，而不是继续重复旧 axis。

## writeback

- 已更新：`docs/BOT2_BOT3_STATE.md`
- 更新内容：
  - 保持 `Paper launch queue = none`、`Active P2 = none`；
  - 保持 `Rank 272` 作为当前 survivor；
  - 仅重写当前轮 `cycle_plan`，把 `Rank 272` 的 survivor follow-up 放回第 1 位，并把最新 `2026-03-31_1929` cross-venue same-contract perp quote-gap digest 放到第 2 位；
  - 新生成 4 个 cycle item 全部满足 `result = none`、`status = pending`。
- 未改写：policy / brief / operating card / auto loop / cron prompt。
- 未自动把 background pool 旧候选拉回前排。
