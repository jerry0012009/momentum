# Strategy Review — 2026-04-05 16:41 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git -C /root/clawd/jerry/momentum status --short`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-05_1535_rank339_rotating_universe_anti_survivor_xs_momentum_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-05_1527_rank338_survivor_followup_background_p0.md`
  - `research/optimization_loop/2026-04-05_1607_top20_depth_imbalance_tightspread_continuation_blocked_by_survivor_lock.md`
  - `research/optimization_loop/2026-04-05_1640_powerlaw_tailgate_overlay_blocked_by_survivor_lock.md`
  - `research/optimization_loop/2026-04-04_1833_rank331_p2_admission_effectiveness_cross_asset_failed_drop_to_background.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-05_1518_strategy-review.md`
  - `research/strategy_review/2026-04-05_0454_strategy-review.md`

## repo 状态摘录
- 工作树仍有大量未跟踪的 research / tmp / artifact 文件；这些只作环境 evidence。
- 本轮遵守硬约束：只更新 `docs/BOT2_BOT3_STATE.md`，未改写 policy / brief / operating card / auto loop / cron prompt。

## 只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- **否。**
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有新的待接线 queue 头对象。

### 2) 本轮 `fresh intake` 是什么？
- **是** `research/quant_digests/2026-04-05_0059_top20-depth-imbalance-tightspread-continuation-alpha.md`。
- 原因：`Rank 339` 已在 15:35 UTC 完成 fresh intake first verdict 并进入 survivor 前排锁；因此 fresh intake 前位依法顺延到下一条尚未执行 first verdict 的具体对象，也就是 top20 depth imbalance + tight spread continuation。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得。**
- 上一条 fresh intake 是 `Rank 339 / rotating-universe anti-survivor XS momentum`，其 first verdict 已明确写成 `keep_P1`。
- 它值得且只值得那唯一一次 survivor follow-up，目标也已经足够具体：把对象压成 `survivor sleeve vs rotating sleeve vs combined sleeve` 的最小 Binance perp clean-room，直接回答 alpha 是否真的主要活在 rotating sleeve，且 after-cost 仍留下独立于 survivor sleeve 的净收益壳。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **不存在。**
- `Active P2 slot.current_target = none`。
- 最近一个 active P2 仍是 `Rank 331`，且已在 `research/optimization_loop/2026-04-04_1833_rank331_p2_admission_effectiveness_cross_asset_failed_drop_to_background.md` 直接收口为 `P0`；当前没有需要继续回答 `P3 / P1 / P0` 出口的 active P2。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Surviving candidate slot.current_target = Rank 339 / rotating-universe anti-survivor XS momentum`
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
- `P1`：有且只有 `Rank 339` 的 survivor 唯一一次 follow-up，必须排在 fresh intake 之前
- 因此前排链条**并未清空**；本轮第一优先级是 `Rank 339` 的 survivor 收口，而不是继续跳过前排去追新的 intake

所以本轮 `cycle_plan` 重写为：
1. `Rank 339 / rotating-universe anti-survivor XS momentum` survivor follow-up
2. `research/quant_digests/2026-04-05_0059_top20-depth-imbalance-tightspread-continuation-alpha.md`
3. `research/quant_digests/2026-04-05_1606_twotier-funding-rate-crossvenue-arb-alpha.md`
4. `research/quant_digests/2026-04-05_1625_btceth-fairvalue-gap-rv-alpha.md`

这个顺序的含义是：
- 先把唯一合法 survivor 前排对象诚实收口；
- 再切回当前 fresh intake 前位 top20 depth imbalance；
- 只有在前排链条已经被诚实排入当前轮前部后，才用剩余预算补新的具体 intake；
- 后两项补的是最近新增的具体 digest，而不是继续保留已经被 survivor lock 挡住的旧 blocked 占位。

## 本轮写回
已写回 `docs/BOT2_BOT3_STATE.md`：
- 保持 `Paper launch queue = none`
- 保持 `Active P2 slot = none`
- 保持 `Surviving candidate slot = Rank 339 / rotating-universe anti-survivor XS momentum`
- 保持 `Fresh intake slot.current_target = research/quant_digests/2026-04-05_0059_top20-depth-imbalance-tightspread-continuation-alpha.md`
- 重写 `cycle_plan`，使第 1 项是 `Rank 339` survivor 唯一一次 follow-up，第 2 项才回到当前 fresh intake，后两项再补最近新增的具体 intake

## 本轮结论一句话
这轮没有 P3、也没有 P2；真正的前排只有 `Rank 339` 的 survivor 唯一一次 follow-up，所以 bot2 不能继续假装前排已清空，必须先把它收口，再把 top20 depth imbalance 作为当前 fresh intake 往后推进。