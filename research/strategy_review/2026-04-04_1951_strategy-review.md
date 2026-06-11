# Strategy Review — 2026-04-04 19:51 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short --branch`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-04_1951_rank334_candidate_blocked_due_to_survivor_priority_conflict.md`
  - `research/optimization_loop/2026-04-04_1916_rank333_dynamic_coint_pairs_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-04_1903_rank332_survivor_snapshot_stability_failed_background_p0.md`
  - `research/optimization_loop/2026-04-04_1833_rank331_p2_admission_effectiveness_cross_asset_failed_drop_to_background.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-04_1906_strategy-review.md`

## repo 状态摘录
- `jerry/momentum` 工作树仍有大量未跟踪临时 artifact / tmp 文件；这些只作环境 evidence，不改变本轮 policy 判定。
- 本轮遵守硬约束：未改写 policy / brief / operating card / auto loop / cron prompt；runtime 只写回 `docs/BOT2_BOT3_STATE.md`。

## 只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- **否。**
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有新的待接线 queue 头对象。

### 2) 本轮 `fresh intake` 是什么？
- **当前 runtime 中最近完成 first verdict 的 fresh intake 是**：`Rank 333 / dynamic-coint spread forecast × percentile trigger`。
- 它已在 19:16 UTC 完成 first verdict，结论为 `keep_P1`，并因此占据唯一合法的 `Surviving candidate slot`。
- 这也意味着：虽然 `thresholded VVV weight-gap spread` 是下一个候选 fresh intake，但它在 19:51 UTC 被明确记录为 **尚未合法进入 first-verdict 流程**，因为 survivor 前排锁尚未收口。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得，而且现在就该优先执行。**
- 上一条 fresh intake 就是 `Rank 333` 本身；它不是又一版普通 `z-score fade` 的旧壳，而是已经讲清了 `dynamic-coint admission × spread-direction forecast × percentile trigger` 这条 distinct 的 forecast-driven pairs raw alpha 骨架。
- 因此它配得上那唯一一次 follow-up；而且 follow-up 目标已经很窄：只回答在同一 `15m discovery -> 5m execution`、同 admission、同成本、同 time-stop 下，`forecast shell` 是否能系统性打赢 `plain z-score fade`。
- 在这一步诚实收口之前，不应让新的 `keep_P1` 候选挤占 survivor 槽位。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **不存在。**
- `Rank 331` 已在 18:33 UTC 的 P2 admission 中被明确收口到 `drop_to_background`：BTC/ETH 成本前毛利都只有约 `+1.3bps/trade`，funding 增量近乎为零，连 `2bps` roundtrip 成本都扛不住。
- 因此当前 `Active P2 slot = none`，不存在需要在 `P3 / P1 / P0` 之间继续判断“离哪个出口最近”的对象。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Active P2 slot.current_target = none`
- `Surviving candidate slot.current_target = Rank 333`
- `Rank 333` 已有正式 rank；当前前排不存在“已达 keep_P1 / P2 / P3 但仍无 rank”的对象。
- 因此前排 rank 完整性满足 policy，本轮无需补新 rank。

## P2 -> P3 兜底裁判检查
- 本轮**不触发** bot2 的强制 `P2 -> P3` 兜底升级。
- 原因：当前没有 `Active P2`；最近一个 P2（`Rank 331`）已被最新 admission 证据直接否决，不存在“desk review 已清楚表明足够值得 paper trade、但 bot3 尚未升级”的对象。

## 本轮排班结论
按 policy 默认顺序：`P3 handoff > P2 admission/promote/park > P1 唯一 follow-up > fresh intake > P0`。

当前运行态下：
- `P3`：无待接线对象
- `P2`：无 active P2
- `P1`：有且仅有 `Rank 333` survivor follow-up

因此本轮 `cycle_plan` 必须先把 `Rank 333` 的 survivor 收口排在首位，其后才能继续补新的 fresh intake。重排后的 4 项为：

1. `Rank 333 / dynamic-coint spread forecast × percentile trigger` survivor 唯一一次 clean-room A/B follow-up
2. `research/quant_digests/2026-04-04_1826_thresholded-vvv-rebalance-spread-alpha.md`
3. `research/quant_digests/2026-04-04_1748_orderbook-pressure-downbar-reversal-alpha.md`
4. `research/quant_digests/2026-04-04_1702_altperp-maker-inventory-skew-alpha.md`

这样排的理由：
- `Rank 333` 仍有合法且未消化的 survivor 动作，享有前排锁定权；
- 19:51 的 `rank334_candidate_blocked_due_to_survivor_priority_conflict` 已明确证明，不能在 survivor 未收口时把新的 fresh intake 排到它前面；
- 但 policy 也允许在前排动作已被诚实排入轮次前部后，用剩余预算继续补具体 fresh intake，因此保留 3 个明确对象作为后续动作。

## 本轮写回
已写回 `docs/BOT2_BOT3_STATE.md`：
- 保持 `Fresh intake slot = Rank 333 / done`
- 保持 `Surviving candidate slot = Rank 333 / followup_budget_remaining = 1`
- 保持 `Active P2 slot = none`
- 仅重写 `cycle_plan`，把 `Rank 333` survivor follow-up 置于第 1 位，并把新的 intake 顺延到其后；所有新生成项均满足：
  - 只写 `target / action / success_criterion / result / status`
  - `result = none`
  - `status = pending`

## 本轮结论一句话
当前前排唯一真实动作是 `Rank 333` 的 survivor 唯一 follow-up；bot2 已把 runtime 排班改回合规顺序，先收口 survivor，再继续 `thresholded VVV / orderbook reversal / maker inventory skew` 三条 fresh intake。