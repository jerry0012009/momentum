# Strategy Review — 2026-04-04 16:46 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-04_1643_pancakeswap_fresh_intake_blocked_by_rank331_survivor_front_slot.md`
  - `research/optimization_loop/2026-04-04_1613_rank331_ml_basis_state_ensemble_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-04_1534_rank330_p2_admission_cross_asset_failed_drop_to_background.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-04_1543_strategy-review.md`

## repo 状态摘录
- repo 仍有大量未跟踪研究产物与临时文件；这些只作环境 evidence，不改变本轮 policy 判定。
- 本轮继续遵守硬约束：未改写 policy / brief / operating card / auto loop / cron prompt；runtime 只写回 `docs/BOT2_BOT3_STATE.md`。

## 只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- **否。**
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有新的待接线 queue 头对象。

### 2) 本轮 `fresh intake` 是什么？
- **当前 runtime 中的 fresh intake 来源仍是**：`research/quant_digests/2026-04-04_1525_ml-basis-state-ensemble-alpha.md`。
- 但它已经完成 first verdict，并以 `Rank 331` 的形式进入 `Surviving candidate slot`；因此本轮真正需要 bot3 先处理的，不再是 fresh intake 首判，而是 `Rank 331` 的唯一 survivor follow-up。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得。**
- `Rank 331` 的 first verdict 已经把对象压缩成一个很清楚的 raw-alpha 主语：`spot-perp basis state × funding-pressure × delta-neutral flip`，并把唯一 decisive blocker 收敛到 `canonical sign audit`。
- 这意味着唯一一次 follow-up 不是低杠杆重复，而是直接回答这条线到底是在做 `basis widening / convergence`，还是只是实现方向写反导致的伪 edge；因此它应当保留前排锁定权，直到这次 follow-up 诚实收口。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **不存在。**
- `Active P2 slot.current_target = none`。
- 最新证据已经把 `Rank 330` 从 `Active P2` 直接收口到 `background/P0`：canonical 化后虽恢复 firing density，但 `BTC/ETH/SOL/BNB 15m recent 90d` 上 aggregate `gross_return=+6.23%`、`net_return=-48.62%`（每币 `10k` 口径），且成本后四币全负，因此当前不存在任何合法的前排 `P2`。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Fresh intake slot.current_target = research/quant_digests/2026-04-04_1525_ml-basis-state-ensemble-alpha.md`
- `Surviving candidate slot.current_target = Rank 331 / spot-perp basis state × funding-pressure × delta-neutral flip`
- `Active P2 slot.current_target = none`
- 当前所有前排对象均已有正式 rank；本轮无需补新 rank。

## P2 -> P3 兜底裁判检查
- 本轮没有明确 `Active P2`。
- 最近唯一需要检查的前排 `P2` 是 `Rank 330`，但 desk review 并未表明它足够进入 paper trade，反而已清楚表明应直接 `drop_to_background`。
- 因此本轮**不触发** bot2 的强制 `P2 -> P3` 兜底升级。

## 本轮排班结论
上轮 state 把新的 fresh intake 排到了 survivor 前面，已被 `2026-04-04_1643` 的 bot3 日志明确判定为与 policy 冲突。按 authoritative 顺序，本轮必须改回：

1. `Rank 331` survivor follow-up：做 canonical sign audit，并直接回答 `promote_P2` 或 `background/P0`
2. `research/quant_digests/2026-04-04_1455_pancakeswap-latelock-ev-prediction-alpha.md`
3. `research/quant_digests/2026-04-04_1406_atr-overreaction-liquid-hours-veto-alpha.md`
4. `research/quant_digests/2026-04-04_1335_deribit-iv-calendar-spread-alpha.md`

这样排的理由：
- `P3` 为空，不能凭空制造接线动作；
- `P2` 为空，不能把已掉回 background 的对象继续前排化；
- `P1` 不为空，且 `Rank 331` 仍有唯一一次合法 follow-up；
- 因此前排收口必须先完成 `Rank 331`，之后才能把剩余预算给新的具体 fresh intake。

## 本轮写回
已重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`：
- 把 `Rank 331` survivor follow-up 调整到第 1 位
- 把新的 fresh intake 顺延到其后
- 所有新生成项均保持 `result = none`、`status = pending`

## 本轮结论一句话
当前前排唯一合法动作不是新的 fresh intake，而是 `Rank 331` 的唯一 survivor follow-up；bot2 已把运行态改回 policy 要求的顺序：先收口 survivor，再吃新的 intake。