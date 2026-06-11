# 2026-04-25 18:21 UTC · Rank 25c pending stale replay blocked

## 本轮执行对象
- target: `research/park_reframe/2026-03-23_0256_rank25-park-reframe.md`
- action: 检查当前 `cycle_plan` 第一个 pending 小点是否仍是合法 fresh intake：`Rank 25c / EMA context-only gate + Donchian breakout primary trigger` 是否还值得再做一次 first verdict。

## 最小核验
1. `research/park_reframe/2026-03-23_0256_rank25-park-reframe.md` 确实把唯一修改轴写成：`EMA` 从同层 co-trigger 降为 `HTF context-only gate`，`Donchian breakout` 保留为唯一主触发。
2. 但这条对象并不是 runtime 里尚未消费的新 intake：
   - `research/optimization_loop/2026-04-09_0121_rank25c_ema_context_donchian_primary_fresh_intake_background.md` 已经给过 first verdict，结论是 `background / P0`；
   - `research/optimization_loop/2026-04-17_2238_rank25c_conditional_freshintake_background_p0_consumed.md` 又明确写死：这条 residual 已被 `Rank 245` 的 intake + survivor A/B 诚实消费，`EMA context-only gate` 没有修复原 `Rank 25` 的 time-structure blocker。
3. 因此，当前 `cycle_plan` 里把同一对象再次写成 fresh intake pending，与 policy 的“不得继续消费已完成且不再改变层级的旧轴”相冲突；其前置条件（仍是未消费的新对象）已不成立。

## 本轮结论
- 本轮不重做 `Rank 25c` 的 first verdict。
- 该 pending 小点应直接写成 `blocked`，原因是：**这是已被 runtime 消费并得出否定结论的 stale replay，不再是合法 fresh intake。**

## 写回 runtime 的一句话
`Rank 25c / EMA context-only gate + Donchian breakout primary trigger` 早已在 `Rank 245` intake + survivor A/B 中被诚实消费并收口 `background/P0`，当前把它再次排成 fresh intake 属于 stale replay；其“仍是未消费新对象”的前置条件已失效，因此本轮只能标记 `blocked` 而不再重复执行。