# Strategy Review — 2026-04-04 21:41 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git -C /root/clawd/jerry/momentum status --short`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-04_2140_rank334_survivor_priority_guard_blocked_dual_momentum_fresh_intake.md`
  - `research/optimization_loop/2026-04-04_2106_rank334_ga_triplebarrier_pair_label_veto_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-04_2033_rank333_survivor_followup_forecast_vs_plainz_background_p0.md`
  - `research/optimization_loop/2026-04-04_1833_rank331_p2_admission_effectiveness_cross_asset_failed_drop_to_background.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-04_2037_strategy-review.md`

## repo 状态摘录
- `jerry/momentum` 工作树仍有大量未跟踪 research / tmp / artifact 文件；这些只作环境 evidence，不改变本轮排班。
- 本轮遵守硬约束：未改写 policy / brief / operating card / auto loop / cron prompt；runtime 只写回 `docs/BOT2_BOT3_STATE.md`。

## 只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- **否。**
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有新的待接线 queue 头对象。

### 2) 本轮 `fresh intake` 是什么？
- **本轮最新完成 first verdict 的 fresh intake 是 `Rank 334 / GA-optimized triple-barrier pair-label veto`。**
- 依据：`research/optimization_loop/2026-04-04_2106_rank334_ga_triplebarrier_pair_label_veto_first_verdict_keep_p1.md`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得，而且现在正占用那唯一一次 follow-up。**
- `Rank 334` 的 first verdict 不是“直接可升 P2”，但已经足够 distinct：底层是诚实承认 pair shell 依赖的 `cointegrated spread mean reversion`，增量在于 `GA-optimized triple-barrier label × take/skip veto` 这层 admission logic。
- 现在唯一该回答的 decisive question 也很清楚：在更诚实的 pair admission / barrier / cost 口径下，`selected subset` 能否从“少亏一点”推进到至少一个可辩护的 post-cost positive pocket；若不能，就应直接收口到 `background/P0`。
- 这也是为什么 bot3 在 `21:40` 把 `dual-momentum breakout expansion` 的 fresh intake 小点挡回去了：survivor 唯一 follow-up 尚未消耗，不能被新的 intake 越过。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **不存在。**
- `Active P2 slot.current_target = none`。
- 最近一个 active P2 是 `Rank 331`，已在 `research/optimization_loop/2026-04-04_1833_rank331_p2_admission_effectiveness_cross_asset_failed_drop_to_background.md` 中被明确收口到 `P0`；因此当前没有需要判 `P3 / P1 / P0` 出口距离的 active P2。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Surviving candidate slot.current_target = Rank 334`
- `Active P2 slot.current_target = none`
- 当前前排对象全部带正式 `Rank`，不存在需要补 rank 的前排对象。

## P2 -> P3 兜底裁判检查
- 本轮**不触发** bot2 的强制 `P2 -> P3` 升级。
- 原因：当前没有 `Active P2`；最近 P2（`Rank 331`）已被 admission 证据明确否决，不存在“desk review 已清楚表明足够值得进入 paper trade、但 bot3 尚未升级”的对象。

## 本轮排班结论
按 policy 默认顺序：`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0`。

当前运行态下：
- `P3`：无待接线对象
- `P2`：无 active P2
- `P1`：有且只有 `Rank 334` 的 survivor 唯一一次 follow-up

因此本轮 `cycle_plan` 必须先把 `Rank 334` 的 survivor follow-up 放回首位，再把新的 fresh intake 诚实排在后面。重写后的 4 项为：

1. `Rank 334 / GA-optimized triple-barrier pair-label veto` survivor follow-up
2. `research/quant_digests/2026-04-04_1920_dual-momentum-breakout-expansion-alpha.md`
3. `research/quant_digests/2026-04-04_1826_thresholded-vvv-rebalance-spread-alpha.md`
4. `research/quant_digests/2026-04-04_1748_orderbook-pressure-downbar-reversal-alpha.md`

这样排的理由：
- 前排 `P1` 仍有合法且必须优先执行的收口动作；
- `dual momentum breakout` 虽然新，但只能在 survivor follow-up 已被诚实排入之后占据后续 fresh intake 槽；
- 其余两条 fresh intake 继续按最近素材顺序保留，避免前排链条收口后出现空转。

## 本轮写回
已写回 `docs/BOT2_BOT3_STATE.md`：
- 保持 `Paper launch queue = none`
- 保持 `Fresh intake slot = Rank 334`
- 保持 `Surviving candidate slot = Rank 334`，`followup_budget_remaining = 1`
- 保持 `Active P2 slot = none`
- 重写 `cycle_plan`，把 `Rank 334` survivor 唯一 follow-up 放回第 1 位；其余 3 项作为条件成立后的具体 fresh intake

## 本轮结论一句话
当前没有 `P3` 也没有 `Active P2`，但有一个必须优先收口的 `Surviving candidate`：`Rank 334`；所以 bot2 已把 runtime 改回合法顺序，先做 `Rank 334` 的唯一一次诚实 follow-up，再轮到新的 fresh intake。