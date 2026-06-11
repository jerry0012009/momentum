# 2026-03-31 15:21 UTC strategy review

本轮严格按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 执行；只读取 fixed policy、runtime state、repo 状态、最近 `research/optimization_loop/`、最近 `research/strategy_review/`，不反向改 policy，不把 background pool 旧候选拉回前排。

## 只回答 4 个问题

1. **`Paper launch queue` 是否非空？**
   - 结论：**否。**
   - 证据：`BOT2_BOT3_STATE.md` 当前仍写明 `Paper launch queue.current_target: none`；`Rank 200 / 201 / 213 / 229` 只是 `connected_runner_live`，没有新的待接线 queue 头。

2. **本轮 `fresh intake` 是什么？**
   - 结论：**`asynchronous funding clock × net-hour hurdle`。**
   - 证据：`Fresh intake slot.current_target` 仍是该对象，且 `latest_result_record = research/optimization_loop/2026-03-31_1516_async_funding_clock_carry_intake_background_p0.md` 已明确写成 fresh intake 首判完成、直接并回 `background/P0`。

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - 结论：**不值得。**
   - 证据：`asynchronous funding clock × net-hour hurdle` 的最新结论已经明确：它补到的是旧 cross-venue funding carry 家族的 `expected_net_carry(H)` honesty/accounting 口径，而不是新的独立 raw alpha 主体；因此最诚实出口已是 `background/P0`，不应再占 survivor follow-up 配额。

4. **当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - 结论：**不存在。当前 `Active P2 = none`。**
   - 证据：`BOT2_BOT3_STATE.md` 已写明 `Active P2 slot.current_target: none`；最近一条 `Active P2` 是 `Rank 267`，并已在 `research/optimization_loop/2026-03-31_1240_rank267_p2_exit_rescope_to_p1_exmajors_scope.md` 收口为一次性 `P2 -> P1 re-scope`，当前不再占 active 槽位。

## 前排 / rank 合法性检查

- `Paper launch queue.current_target = none`
- `Surviving candidate slot.current_target = none`
- `Active P2 slot.current_target = none`
- 当前不存在需要保留在前排但缺正式 rank 的对象。
- 结论：**本轮无需补 rank。**

## `P2 -> P3` 兜底检查

policy 要求：若 desk review 已清楚表明某个 `Active P2` 足够值得进入 paper trade / paper launch，而 bot3 尚未升级，bot2 必须直接改写 state 进入 `P3 / handoff`。

本轮复核结果：**不触发该兜底。**
- 当前 `Active P2 = none`；
- 不存在“已经足够 paper trade 但仍被 bot3 卡在 P2”的对象；
- 因此本轮不应伪造 `P3`，而应诚实切回新的 `fresh intake` 排班。

## cycle_plan 重排逻辑

按 policy 默认顺序从高到低扫描：
1. `P3 handoff`：无待接线对象；
2. `P2 admission/promote/park`：无，`Active P2 = none`；
3. `P1 survivor follow-up`：无，`Surviving candidate = none`；
4. 因此前排链条已收口，本轮默认切回 `fresh intake`。

结合最近未处理、且属于最近新 repo/paper/alpha 报告的对象，本轮把 `cycle_plan` 重写为：
1. `cointegration pair + graduation + daily throttle`
2. `front/back annualized basis calendar spread`
3. `rolling-VWAP anchor × short-rich basket`
4. `delta-neutral CLMM fee harvest × futures carry`

这满足 policy：
- 没有把新的 intake 排到任何现存 `P3 / P2 / P1` 前面；
- 每一项都是具体对象，不是抽象模板句；
- 都是最近新的 digest / repo / paper，而不是从 background pool 自动重开旧候选。

## writeback

- 已更新：`docs/BOT2_BOT3_STATE.md`
- 更新内容：
  - 保持 `Paper launch queue / Surviving candidate / Active P2` 都为空；
  - 仅重写当前轮 `cycle_plan`；
  - 新生成 4 个 cycle item 全部满足 `result = none`、`status = pending`。
- 未改写：policy / brief / operating card / auto loop / cron prompt。
- 未自动把 background pool 旧候选拉回前排。
