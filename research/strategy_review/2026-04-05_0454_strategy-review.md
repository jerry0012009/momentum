# Strategy Review — 2026-04-05 04:54 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git -C /root/clawd/jerry/momentum status --short`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-05_0142_rank336_survivor_followup_background_p0.md`
  - `research/optimization_loop/2026-04-04_2359_rank336_liquidity_split_lastday_return_xs_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-04_1833_rank331_p2_admission_effectiveness_cross_asset_failed_drop_to_background.md`
  - `research/optimization_loop/2026-04-05_0033_rank337_candidate_blocked_by_rank336_survivor_lock.md`
  - `research/optimization_loop/2026-04-05_0109_extreme_funding_tail_carry_fresh_intake_blocked_by_survivor_lock.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-05_0110_strategy-review.md`
  - `research/strategy_review/2026-04-04_2356_strategy-review.md`

## repo 状态摘录
- 工作树仍有大量未跟踪 research / tmp / artifact 文件；这些只作环境 evidence。
- 本轮遵守硬约束：只更新 `docs/BOT2_BOT3_STATE.md`，未改写 policy / brief / operating card / auto loop / cron prompt。

## 只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- **否。**
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有新的待接线 queue 头对象。

### 2) 本轮 `fresh intake` 是什么？
- **当前 fresh intake 前位应重置为** `research/quant_digests/2026-04-04_2223_tsmom-bull-third-noshort-alpha.md`。
- 原因不是它最新，而是它是 survivor lock 释放后，上一轮已被 policy 合法拦截、且仍在前位等待 first verdict 的第一条具体对象。
- `Rank 336` 只是“最近完成 first verdict 的上一条 fresh intake”，不是本轮新的 fresh intake 前位。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得，而且已经用完。**
- `Rank 336 / liquidity-split last-day return cross-sectional` 的 first verdict 合法记为 `keep_P1`，因此它值得那唯一一次 survivor follow-up。
- 该 follow-up 已在 `research/optimization_loop/2026-04-05_0142_rank336_survivor_followup_background_p0.md` 诚实收口：它进一步确认了 `liquidity split` 会改写 `ret_24h` 的信号符号、liquid-major desk 更偏 continuation，但仍未把 `BTC beta` 剥离与正式 bucket governance 收成单一 admission 对象，因此不升 `P2`，直接 `drop_to_background/P0`。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **不存在。**
- `Active P2 slot.current_target = none`。
- 最近一个 active P2 是 `Rank 331`，其 admission 已在 `research/optimization_loop/2026-04-04_1833_rank331_p2_admission_effectiveness_cross_asset_failed_drop_to_background.md` 直接收口为 `P0`；当前没有需要继续回答 `P3 / P1 / P0` 出口的 active P2。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Surviving candidate slot.current_target = none`
- `Active P2 slot.current_target = none`
- 当前前排不存在无 rank 的 `keep_P1 / P2 / P3` 对象；无需补发新 `Rank`。

## P2 -> P3 兜底裁判检查
- 本轮**不触发** bot2 的强制 `P2 -> P3` 升级。
- 原因：当前没有 `Active P2`；最近 evidence 也没有出现“已足够值得 paper trade、但 bot3 尚未升级”的对象。

## 本轮排班结论
按 policy 默认顺序：`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0`。

当前运行态下：
- `P3`：无待接线对象
- `P2`：无 active P2
- `P1`：无 survivor；`Rank 336` 已在 `01:42 UTC` 收口为 `background/P0`
- 因此前排链条已诚实收口，本轮可以切回 fresh intake

本轮应把 `cycle_plan` 重写为 4 条具体 fresh intake，并保持具体对象而非抽象模板：
1. `research/quant_digests/2026-04-04_2223_tsmom-bull-third-noshort-alpha.md`
2. `research/quant_digests/2026-04-04_2203_extreme-funding-tail-carry-alpha.md`
3. `research/quant_digests/2026-04-05_0015_rotating-universe-anti-survivor-xs-momentum-alpha.md`
4. `research/quant_digests/2026-04-05_0059_top20-depth-imbalance-tightspread-continuation-alpha.md`

这个顺序的含义是：
- 先执行 survivor lock 期间被合法挡住的前两条既定 fresh intake；
- 再补最近新增、且足够具体的 rotating-universe XS momentum；
- 最后再排微结构 continuation。
- `power-law tailgate momentum overlay` 本轮不进前 4，不是因为无价值，而是因为当前预算下有更具体、且更靠前的 fresh intake 候选。

## 本轮写回
已写回 `docs/BOT2_BOT3_STATE.md`：
- `Fresh intake slot.status` 改为 `pending`
- `Fresh intake slot.current_target` 改为 `research/quant_digests/2026-04-04_2223_tsmom-bull-third-noshort-alpha.md`
- 保持 `Surviving candidate slot = none`
- 保持 `Active P2 slot = none`
- 重写 `cycle_plan` 为上述 4 条具体 fresh intake

## 本轮结论一句话
前排已经清空，所以这轮 bot2 不该再假装还有 survivor/P2 要收口；合法动作就是把 runtime state 切回 fresh intake，先从之前被 `Rank 336` survivor lock 挡住的 `bull-third no-short trend sleeve` 开始。