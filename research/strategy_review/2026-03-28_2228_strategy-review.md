# Strategy Review (bot2)

Time: 2026-03-28 22:28 UTC

## 本轮一句话判断
`Paper launch queue` 非空，但当前没有新的 `P3 wiring` 缺口，也没有在位 `Active P2`；前排唯一需要优先收口的对象是 `Rank 229 / abnormal-day continuation to close` 的 survivor follow-up。它是否能升到 `P2`，比任何新的 fresh intake 都更应该先回答。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short --branch`
- 最近 `research/optimization_loop/`：
  - `2026-03-28_2219_liquidity_ranked_ema_fresh_intake_blocked_survivor_precondition.md`
  - `2026-03-28_2128_rank229_abnormal_day_fresh_intake_keep_p1.md`
  - `2026-03-28_2045_rank76_reframe_fresh_intake_blocked_absorbed_by_rank201_clock_family.md`
  - `2026-03-28_2033_rank96_reframe_fresh_intake_blocked_not_distinct_from_parked_residual.md`
  - `2026-03-28_2002_rank86_reframe_fresh_intake_blocked_duplicate_of_rank222.md`
  - `2026-03-28_1943_rank228_survivor_followup_keep_p1_background.md`
  - `2026-03-28_1923_rank86b_conditional_intake_blocked_survivor_slot_occupied.md`
  - `2026-03-28_1120_rank213_p3_launch_wiring_connected_runner_live.md`
- 最近 `research/strategy_review/`：
  - `2026-03-28_2117_strategy-review.md`
  - `2026-03-28_1929_strategy-review.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改写 policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排
- 未把 `docs/TODO.md` 当成调度依据
- 当前前排对象无缺 rank 违规

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**是，非空。**

当前 state 仍有：
- `connected_runner_live: Rank 200 / Rank 201 / Rank 213`

而且 `Rank 213` 的最近证据已经说明：
- 它已从 `P2` 升到 `P3`
- 已完成最小 `launch wiring`
- 当前运行态应读作 `connected_runner_live`

因此 queue 非空，但本轮没有新的 queue-side handoff / runner / scheduler / first-run 缺口，需要抢在 survivor 前面处理。

### Q2. 本轮 `fresh intake` 是什么？
**严格说，本轮当前还没有新的 fresh intake 正式开跑；front-chain 头部仍是 `Rank 229` 的 survivor follow-up。**

若 `Rank 229` 本轮被诚实收口，下一条合法的 fresh intake 才是：
- `research/quant_digests/2026-03-28_0704_liquidity-ranked-ema-trend-fullstack.md`

原因很直接：
1. `2026-03-28_2219` 已明确把这条对象判为 `blocked`，不是因为对象消失，而是因为 survivor 前置条件仍在；
2. policy 明确要求已有 `Surviving candidate` 的收口优先于新的 fresh intake；
3. 因此这轮不应再把“abnormal-day”误写成 fresh intake，也不应让新的 intake 抢到最前面。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得，而且现在正轮到这唯一一次 follow-up。**

上一条 fresh intake 就是：
- `Rank 229 / abnormal-day continuation to close`

它值得 survivor follow-up 的理由已经够明确：
- 不是纯包装：ETH 上留下了显著的 same-day continuation net pocket；
- 但又不够干净：BTC 很薄，LTC 反向，因此不能直接按三币通用模板升 `P2`；
- 唯一高杠杆且便宜的下一问也很明确：
  - 这是否只是 `UTC day` 锚点效应？
  - 还是 ETH-led 的 continuation pocket 在替代会话切分/rolling session 下仍能站住？

所以答案是：
> **值得，而且 policy 要求现在先把这一次 follow-up 做完，再谈新的 intake。**

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在，当前 `Active P2 = none`。**

最近一个明确的 `Active P2` 是 `Rank 213`，但它已经：
- 在 `2026-03-28_0852` 完成 `P2 -> P3`
- 在 `2026-03-28_1120` 完成 `P3 launch wiring`

所以当前没有需要 bot2 兜底裁成 `P3 / P1 / P0` 的在位 `Active P2`。

## 3) rank 合规检查
- `Paper launch queue` 中的 `Rank 200 / 201 / 213` 都有正式 rank
- `Surviving candidate slot` 中的 `Rank 229` 已有正式 rank
- `Active P2 = none`
- 因此本轮无需补新的整数 `Rank`

## 4) 排班判断
按 policy 默认顺序扫描：
1. `P3 handoff`：queue 非空，但没有新的接线缺口；
2. `P2 admission/promote/park`：无在位 `Active P2`；
3. `P1 唯一一次诚实检查`：**有，而且就是 `Rank 229`**；
4. `fresh intake`：只能排在 survivor 收口之后。

因此本轮的关键修正是：
- 不再把 `liquidity-ranked-ema` 的 conditional intake 写成被动阻塞后的残留项；
- 直接把 `Rank 229` survivor follow-up 提到 `cycle_plan` 第 1 位；
- 只有在它诚实收口后，才继续往下排新的 fresh intake。

## 5) 本轮对 state 的实际写回
已重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`：

1. `Rank 229 / abnormal-day continuation to close`
   - action: 做唯一一次 `ETH-led` honest re-scope / session-robustness follow-up
   - success_criterion: 必须给出一次性 decisive verdict：`promote_P2` / `keep_P1 后转 background` / `fatal flaw -> background`
   - result: `none`
   - status: `pending`

2. `research/quant_digests/2026-03-28_0704_liquidity-ranked-ema-trend-fullstack.md`
   - conditional fresh intake
   - 仅在第 1 项收口后、且前排仍无 `P3/P2/P1` 动作时执行

3. `research/quant_digests/2026-03-28_0608_return-relvol-xs-momentum-alpha.md`
   - 第二条 conditional fresh intake

4. `research/quant_digests/2026-03-28_1033_eth-whale-balance-imbalance-alpha.md`
   - 第三条 conditional fresh intake

所有新项均满足：
- 只包含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 6) 是否需要 bot2 直接兜底推进到 P3？
**不需要。**

因为当前没有在位 `Active P2`，也没有对象已经明显达到 paper launch 门槛却仍被卡在 `P2`。最近满足该条件的 `Rank 213` 已经被正确推进到 `P3` 并完成 wiring。

## 7) 一句话结论
这轮最重要的不是再找新东西，而是先把 `Rank 229` 这次唯一合法 survivor follow-up 做干净：它要么靠 `ETH-led` re-scope / session-robustness 检查升到 `P2`，要么诚实收口回 background；在这件事没做完之前，新的 fresh intake 都不该抢到前面。
