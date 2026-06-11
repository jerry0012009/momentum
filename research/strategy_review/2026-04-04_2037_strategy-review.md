# Strategy Review — 2026-04-04 20:37 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git -C /root/clawd/jerry/momentum status --short`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-04_2033_rank333_survivor_followup_forecast_vs_plainz_background_p0.md`
  - `research/optimization_loop/2026-04-04_1951_rank334_candidate_blocked_due_to_survivor_priority_conflict.md`
  - `research/optimization_loop/2026-04-04_1916_rank333_dynamic_coint_pairs_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-04_1833_rank331_p2_admission_effectiveness_cross_asset_failed_drop_to_background.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-04_1951_strategy-review.md`
- 新近 digest 候选：
  - `research/quant_digests/2026-04-04_2028_ga-triplebarrier-pair-label-veto-alpha.md`
  - `research/quant_digests/2026-04-04_1920_dual-momentum-breakout-expansion-alpha.md`
  - `research/quant_digests/2026-04-04_1826_thresholded-vvv-rebalance-spread-alpha.md`
  - `research/quant_digests/2026-04-04_1748_orderbook-pressure-downbar-reversal-alpha.md`

## repo 状态摘录
- `jerry/momentum` 工作树仍有大量未跟踪 artifact / tmp / 历史 research 文件；这些只作环境 evidence，不改变本轮排班。
- 本轮遵守硬约束：未改写 policy / brief / operating card / auto loop / cron prompt；runtime 只写回 `docs/BOT2_BOT3_STATE.md`。

## 只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- **否。**
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有新的待接线 queue 头对象。

### 2) 本轮 `fresh intake` 是什么？
- **当前 runtime 中最近完成 first verdict 的 fresh intake 仍是 `Rank 333 / dynamic-coint spread forecast × percentile trigger`。**
- 它的 first verdict 历史记录保持为 `keep_P1`，但这只是“最近一条 fresh intake 是谁”的答案，不代表它仍占据前排。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得，但该唯一一次 follow-up 已经执行完并明确失败。**
- `Rank 333` 的 survivor 唯一 follow-up 已在 `research/optimization_loop/2026-04-04_2033_rank333_survivor_followup_forecast_vs_plainz_background_p0.md` 收口：在同一 `15m discovery -> 5m execution`、同 admission、同成本、同 time-stop 下，`forecast shell` 只实现“少亏一点”的 trade thinning，没有把任何 major pair 变成成本后正净边 lane。
- 因此这条 fresh intake **不再值得额外 follow-up**；survivor 预算已用尽，且对象已转入 `Background pool / P0`。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **不存在。**
- `Rank 331` 已在 18:33 UTC 的 P2 admission 中被明确收口到 `drop_to_background`：BTC/ETH 成本前毛利都只有约 `+1.3bps/trade`，funding 增量近乎为零，连 `2bps` roundtrip 成本都扛不住。
- 当前 `Active P2 slot = none`，因此不存在需要继续判定最接近 `P3 / P1 / P0` 哪个出口的对象。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Active P2 slot.current_target = none`
- `Surviving candidate slot.current_target = none`
- 当前前排没有任何 `keep_P1 / P2 / P3` 但缺正式 rank 的对象。
- 因此前排 rank 完整性满足 policy，本轮无需补新 rank。

## P2 -> P3 兜底裁判检查
- 本轮**不触发** bot2 的强制 `P2 -> P3` 兜底升级。
- 原因：当前没有 `Active P2`；最近一个 P2（`Rank 331`）已被最新 admission 证据直接否决，不存在“desk review 已清楚表明足够值得 paper trade、但 bot3 尚未升级”的对象。

## 本轮排班结论
按 policy 默认顺序：`P3 handoff > P2 admission/promote/park > P1 唯一 follow-up > fresh intake > P0`。

当前运行态下：
- `P3`：无待接线对象
- `P2`：无 active P2
- `P1`：无 survivor 待执行动作（`Rank 333` 已收口失败）

因此本轮应当**直接切回 fresh intake**。重排后的 4 项为：

1. `research/quant_digests/2026-04-04_2028_ga-triplebarrier-pair-label-veto-alpha.md`
2. `research/quant_digests/2026-04-04_1920_dual-momentum-breakout-expansion-alpha.md`
3. `research/quant_digests/2026-04-04_1826_thresholded-vvv-rebalance-spread-alpha.md`
4. `research/quant_digests/2026-04-04_1748_orderbook-pressure-downbar-reversal-alpha.md`

这样排的理由：
- 前排 `P3 / P2 / P1` 已诚实收口，不再存在合法优先动作；
- 新的 fresh intake 默认优先从最近新 repo / paper / alpha 报告里挑；
- 20:28 的 `GA triple-barrier pair-label veto` 与 19:20 的 `dual momentum breakout expansion` 都比旧一轮候选更新，因此应先于更早的 `thresholded VVV` 与 `orderbook reversal`；
- 这四项都是真实、具体、可执行的对象，不含抽象模板或空占位。

## 本轮写回
已写回 `docs/BOT2_BOT3_STATE.md`：
- 保持 `Paper launch queue = none`
- 保持 `Active P2 slot = none`
- 明确 `Surviving candidate slot = none`，并记录 `Rank 333` follow-up 已失败收口
- 保持 `Fresh intake slot` 的最近 first-verdict 历史对象仍为 `Rank 333`
- 重写 `cycle_plan` 为 4 条 fresh intake，新生成项均满足：
  - 只写 `target / action / success_criterion / result / status`
  - `result = none`
  - `status = pending`

## 本轮结论一句话
`Rank 333` 的 survivor 唯一 follow-up 已诚实失败，`Rank 331` 也已不构成 active P2；当前前排全空，因此 bot2 已把 runtime 切回 fresh intake，并按最新素材顺序排成 `GA pair-label veto > dual-momentum breakout sleeve > thresholded VVV spread > orderbook downbar reversal`。
