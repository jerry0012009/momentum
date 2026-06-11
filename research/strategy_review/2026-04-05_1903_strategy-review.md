# Strategy Review — 2026-04-05 19:03 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git -C /root/clawd/jerry/momentum status --short --branch`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-05_1858_rank341_twotier_funding_crossvenue_arb_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-05_1818_rank340_survivor_followup_post_cost_cross_asset_failed_background_p0.md`
  - `research/optimization_loop/2026-04-05_1745_rank340_top20_depth_imbalance_tight_spread_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-05_1722_rank339_survivor_followup_background_p0.md`
  - `research/optimization_loop/2026-04-04_1833_rank331_p2_admission_effectiveness_cross_asset_failed_drop_to_background.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-05_1748_strategy-review.md`
  - `research/strategy_review/2026-04-05_1641_strategy-review.md`

## repo 状态摘录
- 工作树仍有大量未跟踪的 research / tmp / artifact 文件；这些只作环境 evidence。
- 本轮遵守硬约束：只更新 `docs/BOT2_BOT3_STATE.md`，未改写 policy / brief / operating card / auto loop / cron prompt。

## 只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- **否。**
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有新的待接线 queue 头对象。

### 2) 本轮 `fresh intake` 是什么？
- **是** `research/quant_digests/2026-04-05_1740_samechain-crossdex-pricegap-close-alpha.md`。
- 原因：`Rank 341 / two-tier funding-rate cross-venue arb` 已在 18:58 UTC 完成 fresh intake first verdict 并依法进入 survivor 槽位；因此当前 fresh intake 前位顺延到上一轮 cycle_plan 里最靠前、尚未执行 first verdict 的具体对象，也就是 `same-chain cross-DEX price-gap close`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得。**
- 上一条 fresh intake 是 `Rank 341 / two-tier funding-rate cross-venue arb`，其 first verdict 已明确写成 `keep_P1`。
- 它值得且只值得那唯一一次 survivor follow-up，目标也已经足够具体：把对象压成 `BTC/ETH/SOL/BNB/XRP × 20/30/40bps × persistence / sign-flip / CEX-lead` 的最小 admission clean-room，直接回答 `CEX-DEX funding spread × duration` 在 majors 与 realistic fee / slippage / transfer friction 下，到底还能不能留下独立 alpha 壳。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **不存在。**
- `Active P2 slot.current_target = none`。
- 最近一个 active P2 仍是 `Rank 331`，且已在 `research/optimization_loop/2026-04-04_1833_rank331_p2_admission_effectiveness_cross_asset_failed_drop_to_background.md` 直接收口为 `P0`；当前没有需要继续回答 `P3 / P1 / P0` 出口的 active P2。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Surviving candidate slot.current_target = Rank 341 / two-tier funding-rate cross-venue arb`
- `Active P2 slot.current_target = none`
- 当前前排对象均已有正式 rank；不存在需要补发 rank 的 `keep_P1 / P2 / P3` 对象。

## P2 -> P3 兜底裁判检查
- 本轮**不触发** bot2 的强制 `P2 -> P3` 升级。
- 原因：当前没有 `Active P2`，最近证据中也不存在“desk review 已清楚证明足够进入 paper trade，但 bot3 尚未升级”的对象。

## 本轮排班结论
按 policy 默认顺序：`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0`。

当前运行态下：
- `P3`：无待接线对象
- `P2`：无 active P2
- `P1`：有且只有 `Rank 341` 的 survivor 唯一一次 follow-up，必须排在 fresh intake 之前
- 因此前排链条并未清空；本轮第一优先级必须是 `Rank 341` 的 survivor 收口，而不是继续跳过前排去追新的 intake

所以本轮 `cycle_plan` 重写为：
1. `Rank 341 / two-tier funding-rate cross-venue arb`
2. `research/quant_digests/2026-04-05_1740_samechain-crossdex-pricegap-close-alpha.md`
3. `research/quant_digests/2026-04-05_1755_poc-cvd-absorption-alpha.md`
4. `research/quant_digests/2026-04-05_1701_chartpattern-neckline-imbalance-alpha.md`

这个顺序的含义是：
- 先把当前唯一合法 survivor 前排对象诚实收口；
- 再切回当前 fresh intake 前位 `same-chain cross-DEX price-gap close`；
- 只有在前排链条已经被诚实排入当前轮前部后，才用剩余预算补新的具体 intake；
- 补位对象继续优先用最近新的 alpha digest，而不是把 background 旧候选拉回前排。

## 本轮写回
已写回 `docs/BOT2_BOT3_STATE.md`：
- 保持 `Paper launch queue = none`
- 保持 `Active P2 slot = none`
- 保持 `Surviving candidate slot = Rank 341 / two-tier funding-rate cross-venue arb`
- 保持 `Fresh intake slot` 的 latest_result 仍指向 `Rank 341` 的 first verdict 完成事实
- 重写 `cycle_plan`，使第 1 项是 `Rank 341` survivor 唯一一次 follow-up，第 2 项才回到当前 fresh intake，后两项再补最近新增的具体 intake

## 本轮结论一句话
这轮没有 P3、也没有 P2；真正的前排只有 `Rank 341` 的 survivor 唯一一次 follow-up，所以 bot2 不能继续假装前排已清空，必须先把它收口，再把 `same-chain cross-DEX price-gap close` 作为当前 fresh intake 往后推进。
