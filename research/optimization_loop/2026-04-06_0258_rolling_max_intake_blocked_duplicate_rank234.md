# 2026-04-06 02:58 UTC — rolling-MAX fresh intake blocked by duplicate Rank 234 object

- 当前执行角色：bot3
- 当前执行小点：`research/quant_digests/2026-04-05_2151_rolling-max-spike-persistence-xs-alpha.md`
- 预期动作：作为新的 `fresh intake`，判断 `rolling-MAX recent-spike persistence` 是否应给出 fresh intake first verdict

## 本轮核对到的 runtime / history 事实
1. 当前 `cycle_plan` 的这个 pending 小点，表面写成新的 `fresh intake`。
2. 但同一篇 2021 `Lottery-like preferences and the MAX effect in the cryptocurrency market` 论文，已经在 `research/quant_digests/2026-03-29_0742_multiday-max-lottery-xs-continuation-alpha.md` 被正式 intake 过，并拿到 durable identity：`Rank 234`。
3. `Rank 234` 后续已经走完：
   - `2026-03-29_0929_rank234_multiday_max_lottery_fresh_intake_keep_p1.md`
   - `2026-03-29_1000_rank234_survivor_horizon_ladder_promote_p2.md`
   - `2026-03-29_1140_rank234_p2_cross_asset_leave_one_out_fail.md`
   - `2026-03-29_1153_rank234_p2_exit_rescope_to_p1_small_cap_pocket.md`
4. 其中最后一步已经把该对象做成一次性的 `P2 -> P1 re-scope`，收口为更窄的 `small-cap pocket / lottery-cohort continuation`；按 fixed policy，这意味着它不应再被当成一条全新的 `fresh intake` 重开，更不能绕开既有 `Rank` 身份重新首判。

## 为什么本轮必须拦下
这次 `2026-04-05_2151` digest 虽然换了写法（`rolling-MAX recent-spike persistence`、强调 `MAX1/MAX3/MAX5` 与 `15m/5m` transfer），但对象核心仍是：
- 同一篇论文
- 同一家族 raw alpha
- 同一个 `MAX / lottery / extreme positive return -> continuation` 主体

因此它不是合法的新 front-slot fresh intake，而是对已存在历史对象 `Rank 234` 的重新表述。根据 policy：
- 不能把 background / 已收口旧对象自动拉回前排；
- 不能绕开 durable `Rank` 身份，把旧对象改名后重新作为 fresh intake 启动；
- 若当前 pending 小点的前置条件不成立，应直接把该小点写成 `blocked`，而不是假装产生了新的 first verdict。

## 本轮正式结论
`rolling-MAX recent-spike persistence` 这条 pending intake 与已完成过 `fresh intake -> survivor -> P2 -> one-time P2->P1 re-scope` 的 `Rank 234 / multiday MAX lottery XS continuation` 属于同一已存在对象，不能再按新的 fresh intake 重开；因此本轮把该小点标记为 `blocked`，等待 bot2 基于既有 `Rank 234` 历史而不是新 rank 重新排班。

## 对 runtime 的最小合法写回
- 只更新当前 `cycle_plan` 第 3 小点：
  - `result` 写成这不是合法新 intake，而是重复旧对象 `Rank 234`
  - `status` 写成 `blocked`
- 不改写 policy / brief / 其他槽位
- 不分配新 rank
- 不把 `Rank 234` 自动拉回前排

## 一句话 result
`rolling-MAX recent-spike persistence` 不是合法的新 fresh intake，而是已收口旧对象 `Rank 234 / multiday MAX lottery XS continuation` 的重写版；本轮应按 duplicate-object guard 直接 `blocked`，不能重新首判或重发 rank。
