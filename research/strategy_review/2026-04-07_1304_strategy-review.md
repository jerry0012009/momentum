# 2026-04-07 13:04 UTC strategy review

## Scope
按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 做本轮 40 分钟 desk review；只更新 runtime state，不改 policy / brief / operating card / auto loop / cron prompt。

## 先回答 4 个问题

### 1) `Paper launch queue` 是否非空？
**否。**

当前 `Paper launch queue.current_target = none`。`Rank 200 / 201 / 213 / 229 / 342` 都已经在 `connected_runner_live`，最近一条仍是 `Rank 342`，其 dedicated runner、scheduler 与首跑验证已在 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md` 完成，因此本轮没有待接线的 `P3` 头对象。

### 2) 本轮 `fresh intake` 是什么？
**本轮已切回新的 fresh intake：`research/quant_digests/2026-04-07_1206_ratio-band-corrvol-pairs-alpha.md`。**

上一条 fresh intake（`Rank 355`）已经完成 `keep_P1 -> survivor follow-up exhausted -> background` 的前排收口，因此 fresh intake 槽位重新开放。按 policy 的默认顺序，在当前无 `P3 / Active P2 / Surviving candidate` 真实动作时，应优先切回最近新的 strategy repo / paper / alpha 报告；最新、最具体的一条就是这份 `EMA-band ratio spread × corr/vol gate × 双腿对冲执行` pairs repo。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得，而且那次 follow-up 已经用完并收口。**

`Rank 355 / Polymarket adjacent-horizon YES-price spread × Kalman-OU reversion` 的 first verdict 把它定为 `keep_P1` 并锁定 survivor 槽位，这是诚实的：它确实提供了独立于旧 `Polymarket lag / continuation` 家族的 prediction-market term-structure raw alpha 主语，也给出了最小执行壳。随后唯一一次 follow-up 进一步把关键 blocker 压成单点：在最流动 recurring crypto pairs 上，公开证据仍不足以证明诚实计入 `fee / slippage / stale-quote / expiry jump` 后仍存在可审计的 post-cost pocket。因此它没有升 `P2`，而是按 policy 正常退出前排并回到 background。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。**

`Active P2 slot.current_target = none`。最近的明确 `Active P2` 仍是 `Rank 342`，但它已经在 `research/optimization_loop/2026-04-05_2300_rank342_p2_exit_promote_p3_lowgas_samechain_paper_queue.md` 完成 `P2 -> P3`，随后在 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md` 完成最小接线。因此本轮没有需要 bot2 兜底直推 `P3 / P1 / P0` 的在场 `Active P2`。

## Rank / 前排合法性检查
- `Paper launch queue.current_target = none`，合法。
- `Surviving candidate slot.current_target = none`，且 `followup_budget_remaining = 0`，说明 `Rank 355` 已正常退出前排。
- `Active P2 slot.current_target = none`，合法。
- 当前前排不存在达到 `keep_P1 / P2 / P3` 但无正式 `Rank` 的对象，因此本轮无需补 rank。

## 最近证据与本轮判断
最近 evidence 很清楚：

1. `research/optimization_loop/2026-04-07_1300_rank355_survivor_followup_exhausted_background.md`
   - 说明 `Rank 355` 的唯一 survivor follow-up 已执行完毕，且结论是 `keep_P1 but follow-up exhausted -> background`。
2. `research/optimization_loop/2026-04-07_1220_cycle_plan_missing_pending_blocked.md`
   - 说明上一轮 pending 小点设计曾导致执行阻塞，但现在这个 blocker 已被 `Rank 355` 的正式收口消除。
3. 最新 `research/quant_digests/` 中，`2026-04-07_1206_ratio-band-corrvol-pairs-alpha.md` 是当前最靠前的新对象；`2026-04-07_1129_polymarket-pairsum-shield-maker-alpha.md` 次之；再往后是 `2026-04-07_0333_crashtrim-volmanaged-xs-momentum-alpha.md` 与 `2026-04-07_0241_halflife-kelly-coint-pairs-alpha.md`。

所以，本轮正确动作不是再回头拖 `Rank 355`，也不是凭空制造 `P2/P3`，而是**按 policy 诚实切回 fresh intake**，并把最新、最具体的对象按优先级重排进 `cycle_plan`。

## 本轮 runtime 调整
本轮重写了 `docs/BOT2_BOT3_STATE.md`，核心变化只有两类：

1. **Fresh intake slot**
   - 从已完成的 `Rank 355` 切回新的 `pending` 对象：
   - `research/quant_digests/2026-04-07_1206_ratio-band-corrvol-pairs-alpha.md`

2. **cycle_plan**
   - 当前前排没有 `P3 / P2 / P1` 真实动作，因此本轮按默认顺序直接切回具体 fresh intake。
   - 新 `cycle_plan` 依次为：
     1. `2026-04-07_1206_ratio-band-corrvol-pairs-alpha.md`
     2. `2026-04-07_1129_polymarket-pairsum-shield-maker-alpha.md`
     3. `2026-04-07_0333_crashtrim-volmanaged-xs-momentum-alpha.md`
     4. `2026-04-07_0241_halflife-kelly-coint-pairs-alpha.md`

所有新生成项均符合 policy：
- 每项只含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`
- 没有抽象模板句子、空占位或无具体对象的泛任务

## 为什么这轮不需要 bot2 兜底升 P3
这轮没有任何 `Active P2` 在前排，因此也不存在“desk review 已清楚表明足够值得进入 paper trade、但 bot3 尚未升级”的漏升对象：
- `Rank 342` 已完成 `P2 -> P3 -> connected_runner_live`；
- `Rank 355` 只到 `keep_P1`，且唯一 follow-up 已经把它诚实收口回 background；
- 当前其余对象都还只是尚未 first verdict 的 fresh intake，不构成 `P2 -> P3` 兜底升级条件。

## 一句话总结
本轮主线已经从 `Rank 355` 的 survivor 收口，干净切回新的 fresh intake；我已把 runtime state 改成以 `ratio-band-corrvol pairs` 为第一条 intake，并按最新具体对象重排后续三条 pending 任务。