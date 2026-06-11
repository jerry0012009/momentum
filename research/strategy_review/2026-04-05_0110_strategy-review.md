# Strategy Review — 2026-04-05 01:10 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git -C /root/clawd/jerry/momentum status --short`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-04_2359_rank336_liquidity_split_lastday_return_xs_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-05_0033_rank337_candidate_blocked_by_rank336_survivor_lock.md`
  - `research/optimization_loop/2026-04-05_0109_extreme_funding_tail_carry_fresh_intake_blocked_by_survivor_lock.md`
  - `research/optimization_loop/2026-04-04_2326_rank335_survivor_followup_majors_ranking_not_decisive_background_p0.md`
  - `research/optimization_loop/2026-04-04_1833_rank331_p2_admission_effectiveness_cross_asset_failed_drop_to_background.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-04_2356_strategy-review.md`
  - `research/strategy_review/2026-04-04_2250_strategy-review.md`

## repo 状态摘录
- 工作树仍有大量未跟踪 research / tmp / artifact 文件；这些只作环境 evidence。
- 本轮遵守硬约束：只更新 `docs/BOT2_BOT3_STATE.md`，未改写 policy / brief / operating card / auto loop / cron prompt。

## 只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- **否。**
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有新的待接线 queue 头对象。

### 2) 本轮 `fresh intake` 是什么？
- **运行态最近完成 first verdict 的 fresh intake 是 `Rank 336 / liquidity-split last-day return cross-sectional`。**
- 依据：`research/optimization_loop/2026-04-04_2359_rank336_liquidity_split_lastday_return_xs_first_verdict_keep_p1.md`。
- 它已经不是待判 fresh intake，而是当前 survivor；因此若问“前排下一条尚未执行的新 intake”，则是 `research/quant_digests/2026-04-04_2223_tsmom-bull-third-noshort-alpha.md`，但它现在必须排在 `Rank 336` survivor 收口之后。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得。**
- `Rank 336` 的 first verdict 已明确给出 distinct 的 `liquid-major continuation / illiquid-tail reversal` raw alpha，其中真正值得 desk 推进的是 `liquid-major continuation` 主壳。
- 这正好对应那唯一一次高杠杆 follow-up：只看 `liquid-major continuation` 在 `perp / 5m-15m` 执行、含成本与 `BTC beta` 控制后是否仍能支撑 admission；若不行，就直接诚实收口。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **不存在。**
- `Active P2 slot.current_target = none`。
- 最近一个 active P2 是 `Rank 331`，其 admission 已在 `research/optimization_loop/2026-04-04_1833_rank331_p2_admission_effectiveness_cross_asset_failed_drop_to_background.md` 中收口到 `P0`；当前没有需要继续回答 `P3 / P1 / P0` 出口的 active P2。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Surviving candidate slot.current_target = Rank 336`
- `Active P2 slot.current_target = none`
- 当前前排对象都已有正式 rank；无需补发新 `Rank`。

## P2 -> P3 兜底裁判检查
- 本轮**不触发** bot2 的强制 `P2 -> P3` 升级。
- 原因：当前没有 `Active P2`；最近 evidence 也没有出现“已经明显足够 paper trade、但 bot3 尚未升级”的对象。

## 本轮排班结论
按 policy 默认顺序：`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0`。

当前运行态下：
- `P3`：无待接线对象
- `P2`：无 active P2
- `P1`：**有** `Rank 336` survivor，且 `followup_budget_remaining = 1`
- 因此前排并未收口；bot3 在 `00:33` 和 `01:09` 连续把新 intake 挡回去是对的，说明上一版 `cycle_plan` 顺序不合法

因此本轮必须把 `cycle_plan` 改回合法顺序：
1. 先做 `Rank 336` 的 survivor 唯一一次 follow-up，直接回答 `promote_P2` 或 `drop_to_background/P0`
2. 只有在 survivor 收口后，才轮到 `bull-third no-short trend sleeve`
3. 再轮到 `extreme funding tail carry`
4. 最后才是 `deribit put-call-perp parity`

## 本轮写回
已写回 `docs/BOT2_BOT3_STATE.md`：
- 保持 `Paper launch queue = none`
- 保持 `Fresh intake slot = Rank 336`
- 保持 `Surviving candidate slot = Rank 336`
- 保持 `Active P2 slot = none`
- 重写 `cycle_plan`，把 `Rank 336` survivor follow-up 放回第 1 位，并把后续 3 个新 intake 顺延为 pending

## 本轮结论一句话
前排其实没清空：`Rank 336` 仍握着 survivor 唯一一次 follow-up；所以本轮 bot2 的工作不是继续放新题，而是把 runtime 顺序修正回来，先逼 `Rank 336` 做一次诚实收口。