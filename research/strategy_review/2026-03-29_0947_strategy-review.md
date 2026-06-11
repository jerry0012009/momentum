# Strategy Review (bot2)

Time: 2026-03-29 09:47 UTC

## 本轮一句话判断
当前没有待接线的 queue 头、没有 `Active P2`，但前排存在必须优先收口的 survivor：`Rank 234 / multiday MAX lottery XS continuation`。因此本轮必须先把它的唯一 follow-up 直接排成出口决策轮；只有它诚实收口后，才允许切回新的具体 fresh intake，第一条应是 `richest-venue routing × hysteresis hold` cross-venue carry。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short`
- 最近 `research/optimization_loop/`：
  - `2026-03-29_0944_rank64b_conditional_intake_keep_park_reframe.md`
  - `2026-03-29_0929_rank234_multiday_max_lottery_fresh_intake_keep_p1.md`
  - `2026-03-29_0921_rank233_survivor_180d_frozen_replication_keep_p1_background.md`
  - `2026-03-29_0857_multiday_max_lottery_intake_blocked_survivor_slot_occupied.md`
  - `2026-03-29_0836_rank233_volume_shock_polarity_fresh_intake_keep_p1.md`
- 最近 `research/strategy_review/`：
  - `2026-03-29_0900_strategy-review.md`
  - `2026-03-29_0812_strategy-review.md`
  - `2026-03-29_0655_strategy-review.md`
- 为决定本轮 fresh intake / conditional intake，再读：
  - `research/quant_digests/2026-03-29_0939_richest-venue-routing-hysteresis-carry-alpha.md`
  - `research/park_reframe/2026-03-28_1128_rank86-park-reframe.md`
  - `research/park_reframe/2026-03-26_0218_rank96-park-reframe.md`
  - `research/park_reframe/INDEX.md`

硬约束遵守：
- 只更新了 `docs/BOT2_BOT3_STATE.md`
- 未改写 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排
- `docs/TODO.md` 未参与本轮排班
- 当前前排对象均已有正式 `Rank`，无需补新的整数 `Rank`

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**广义上非空，但当前 queue 头为空。**

原因：
- `connected_runner_live` 里仍有 `Rank 200 / 201 / 213 / 229`
- 但 `current_target: none`
- 最近也没有新的 `promote_P3` 尚未接线对象

所以本轮不需要把资源放在 `P3 handoff`，只需承认 queue 头已清空。

### Q2. 本轮 `fresh intake` 是什么？
**本轮在前排合法收口之后应切回的 fresh intake 是 `research/quant_digests/2026-03-29_0939_richest-venue-routing-hysteresis-carry-alpha.md`。**

原因：
- `Rank 234` 已在 `2026-03-29_0929_rank234_multiday_max_lottery_fresh_intake_keep_p1.md` 完成 fresh intake 首判并转入 survivor
- 因此当前 front-chain 最高优先级不是再换一个新发现，而是先把 `Rank 234` 的唯一 decisive follow-up 做完
- 在 survivor 收口后，最新、最具体、且尚未进入前排的新 alpha 报告就是 `0939 richest-venue routing × hysteresis hold` 这条 cross-venue carry
- 它不是泛泛 funding filter，而是明确的 `route to richest venue + hysteresis/min_hold` 完整 raw alpha 骨架，因此比再回头翻旧 background 更符合默认 fresh intake 顺序

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**

上一条 fresh intake 是 `Rank 234 / multiday MAX lottery XS continuation`。根据 `2026-03-29_0929_rank234_multiday_max_lottery_fresh_intake_keep_p1.md`：
- 它不是已有 `past-hour MAX fade` 的换名重复，而是 formation-horizon 改变后可能发生符号翻转的 distinct branch
- 当前 blocker 也很集中：
  - `liquid USDT perp universe`
  - `1h / 24h / 72h formation × 1h / 4h / 8h holding`
  - `MAX rank` vs `plain return-rank`
- 这正符合 policy 对 survivor 的定义：保留 1 次最小但 decisive 的 follow-up，直接回答它能否进 `P2`

所以这唯一一次 follow-up 应继续由 `Rank 234` 占据，不得被别的新 intake 覆盖。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。当前 `Active P2 = none`。**

原因：
- `Rank 229` 已完成 `P2 -> P3 -> connected_runner_live`
- `Rank 233` 已完成 survivor 收口并转 background
- `Rank 234` 仍处于 survivor，而不是 `P2 admission`
- 最近结果里没有新的 `promote_P2` writeback

所以本轮没有合法的 `P2 -> P3 / P1 / P0` 出口决策对象。

## 3) rank 合规检查
- `Paper launch queue / connected_runner_live`：`Rank 200 / 201 / 213 / 229` 都有 rank
- `Surviving candidate slot`：`Rank 234` 已有 rank
- `Active P2 slot`：`none`
- 结论：**本轮无需补新的整数 `Rank`**

## 4) 本轮排班逻辑
按 policy 默认顺序扫描：
1. `P3 handoff`：无 queue 头，跳过
2. `P2 admission/promote/park`：无 active P2，跳过
3. `P1 survivor 唯一一次诚实检查`：**有，且必须优先处理 `Rank 234`**
4. `fresh intake`：只有在 `Rank 234` survivor 收口后，才切回 `0939 richest-venue routing × hysteresis hold`
5. `P0 / park-reframe`：若预算仍有余，再补具体 conditional intake；优先保留已明确 draft/candidate 的具体对象，而不是空泛 background 巡检

据此，本轮把 `cycle_plan` 重写为：

1. `Rank 234 / multiday MAX lottery XS continuation`
   - action: 作为当前 survivor 的唯一 follow-up，直接在 liquid USDT perp universe 上做 `MAX horizon ladder` 最小快检：至少并排 `1h / 24h / 72h formation × 1h / 4h / 8h holding`，并把 `MAX rank` 与 `plain return-rank` 并排；只回答更长 formation 是否真的从 fade 翻成 continuation，且不是 plain momentum 换名
   - success_criterion: 必须给出正式 survivor 结论：若 liquid perp 下较长 formation 的 `MAX` 分支在成本前后都保留清晰 continuation、且相对 `plain return-rank` 仍有独立信息，则 `promote_P2`；否则按 `keep_P1 后转 background` 收口，不得继续停留在开放式 survivor
   - result: `none`
   - status: `pending`

2. `research/quant_digests/2026-03-29_0939_richest-venue-routing-hysteresis-carry-alpha.md`
   - action: 仅在 `Rank 234` survivor 已诚实收口后，把 `richest-venue routing × hysteresis hold` cross-venue carry 作为新的具体 fresh intake 做最小首判；重点回答它是否提供了区别于泛泛 funding/carry filter 的完整 raw alpha 骨架，且 alpha 核心是否真来自 `richest-venue routing` 而非 repo headline 换皮
   - success_criterion: 必须给出正式 first verdict：`P2`、`keep_P1`、或 `background/P0`；并明确它是否值得作为独立的 cross-venue carry / relative-value family 保留
   - result: `none`
   - status: `pending`

3. `research/park_reframe/2026-03-28_1128_rank86-park-reframe.md`
   - action: 仅在前两项已诚实排入且预算仍有余时，把 `Rank 86b / breakout-short-specific short-side admission score-veto` 作为 conditional fresh intake 候选做一次最小 distinctness check；重点回答它是否足够脱离原 `Rank 86` penetration×ATR shared gate 失败史，值得正式建成新对象
   - success_criterion: 必须给出正式结论：`转成新的 fresh intake` 或 `继续留在 park/reframe`；若转正，必须明确它与既有 breakout-short family / short-veto family 的边界，避免换壳重复
   - result: `none`
   - status: `pending`

4. `research/park_reframe/2026-03-26_0218_rank96-park-reframe.md`
   - action: 仅在前 3 项已诚实排入且预算仍有余时，把 `Rank 96 / short-side second-touch + candle-quality admission delay` 作为 conditional fresh intake 候选做一次最小 distinctness check；重点回答它是否足够脱离原 `Rank 96` generic retestCount>=2 失败史，值得正式建成新对象，还是仍只是 failure / follow-up family 的弱残余
   - success_criterion: 必须给出正式结论：`转成新的 fresh intake` 或 `继续留在 park/reframe`；若转正，必须明确它与既有 short-side delayed-admission / failure-followthrough family 的边界，避免换壳重复
   - result: `none`
   - status: `pending`

## 5) 本轮对 runtime truth 的影响
- `Paper launch queue`：不改，仍为 queue 头为空 / connected runner live 保留历史已接线对象
- `Fresh intake slot`：保留 `Rank 234` 的最新首判记录不变
- `Surviving candidate slot`：继续由 `Rank 234` 占据，`followup_budget_remaining = 1`
- `Active P2 slot`：仍为 `none`
- `cycle_plan`：已按 policy 默认顺序重写为 `Rank 234 survivor 收口 > 0939 fresh intake > Rank 86b conditional intake > Rank 96 conditional intake`
