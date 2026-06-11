# 2026-04-07 12:23 UTC strategy review

## Scope
按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 做本轮 40 分钟 desk review；只更新 runtime state，不改 policy / brief / operating card / auto loop / cron prompt。

## 先回答 4 个问题

### 1) `Paper launch queue` 是否非空？
**否。**

当前 `Paper launch queue.current_target = none`。`Rank 200 / 201 / 213 / 229 / 342` 都已经在 `connected_runner_live`，最近一条仍是 `Rank 342`，其 dedicated runner、scheduler 与首跑验证已在 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md` 完成，因此本轮没有待接线的 `P3` 头对象。

### 2) 本轮 `fresh intake` 是什么？
**当前 runtime 里的 fresh intake 仍是 `research/quant_digests/2026-04-07_0740_polymarket-term-structure-kalman-ou-alpha.md`。**

它已经在 `research/optimization_loop/2026-04-07_1054_rank355_polymarket_term_structure_intake_keep_p1.md` 完成 first verdict，并被正式赋予 `Rank 355`，所以本轮不再是“重新 intake 一条新对象”，而是围绕这条 fresh intake 的后续前排收口。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**

`Rank 355 / Polymarket adjacent-horizon YES-price spread × Kalman-OU reversion` 已经不是旧 `Polymarket lag / continuation` 的换壳，而是 prediction-market 内部 term-structure relative-value 的独立 raw alpha 主语；公开 repo 也给出了最小执行壳（`pairing + dynamic HR + OU half-life + entry/exit + sizing`）。

它没直接升 `P2` 的原因，不是主语不成立，而是最关键 blocker 还没被压成单点：**最流动 recurring crypto markets 上，adjacent-horizon pair 在诚实 `fee / slippage / stale-quote / expiry jump` 口径下是否仍保留可迁移的 post-cost pocket。**

这正是 policy 允许、也要求它消耗那唯一一次 survivor follow-up 去回答的问题。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。**

`Active P2 slot.current_target = none`。最近的明确 `Active P2` 仍是 `Rank 342`，但它已经在 `research/optimization_loop/2026-04-05_2300_rank342_p2_exit_promote_p3_lowgas_samechain_paper_queue.md` 完成 `P2 -> P3`，随后在 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md` 完成最小接线。因此本轮没有需要 bot2 兜底裁判并强行推向 `P3 / P1 / P0` 的在场 `Active P2`。

## Rank / 前排合法性检查
- `Paper launch queue.current_target = none`，合法。
- `Fresh intake slot.latest_result` 已给出正式 `Rank 355`，合法。
- `Surviving candidate slot.current_target = Rank 355`，且带正式 rank，合法。
- `Active P2 slot.current_target = none`，合法。
- 当前前排不存在达到 `keep_P1 / P2 / P3` 但无正式 `Rank` 的对象，因此本轮无需补 rank。

## 最近证据与本轮判断
本轮关键不是出现了需要 bot2 兜底直升 `P3` 的 `Active P2`，而是 runtime 排班歪了：

1. `research/optimization_loop/2026-04-07_1054_rank355_polymarket_term_structure_intake_keep_p1.md`
   - 已经清楚写出 `Rank 355` 是独立 raw alpha 主语，首判为 `keep_P1`，并进入 survivor 槽位。
2. `research/optimization_loop/2026-04-07_1058_crashtrim_volmanaged_xs_momentum_blocked_by_rank355_survivor_lock.md`
3. `research/optimization_loop/2026-04-07_1141_halflife_kelly_coint_pairs_blocked_by_rank355_survivor_lock.md`
4. `research/optimization_loop/2026-04-07_1220_cycle_plan_missing_pending_blocked.md`
   - 这三条合起来说明：`Rank 355` 仍合法占用 survivor 槽位且 follow-up 预算未用完，但旧 `cycle_plan` 没把它的唯一 follow-up 显式写成 `pending`，反而让后续 fresh intake 先后被锁住，最终 bot3 无合法 pending 小点可执行。

因此，本轮正确动作不是继续空谈新 intake，也不是硬造一个 `P3`；而是把 **`Rank 355` 的 survivor follow-up 显式恢复到 `cycle_plan` 第一位**，然后再把具体 fresh intake 排在它后面。

## 本轮 runtime 调整
本轮只重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`，新的当前轮顺序为：

1. `Rank 355 / Polymarket adjacent-horizon YES-price spread × Kalman-OU reversion`
   - 用掉唯一 survivor follow-up，只回答 `after-cost pocket 是否真实存在` 这个 decisive 问题；结论必须是 `promote_P2` / `keep_P1 but exhausted -> background` / `background / P0` 三选一。
2. `research/quant_digests/2026-04-07_0333_crashtrim-volmanaged-xs-momentum-alpha.md`
   - 作为 survivor 收口后的第一条具体 fresh intake。
3. `research/quant_digests/2026-04-07_0241_halflife-kelly-coint-pairs-alpha.md`
   - 作为下一条具体 fresh intake。
4. `research/quant_digests/2026-04-07_1129_polymarket-pairsum-shield-maker-alpha.md`
   - 作为 conditional fresh intake，满足“前排已有 P1 survivor 时，先把 survivor 诚实排在前面，再用剩余预算补具体 intake”的约束。

所有新生成项均已写成：
- 只含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 为什么这轮不需要 bot2 兜底升 P3
这轮没有任何 `Active P2` 在前排，因此也不存在“desk review 已清楚表明足够值得进入 paper trade、但 bot3 尚未升级”的漏升对象：
- `Rank 342` 已完成 `P2 -> P3 -> connected_runner_live`；
- `Rank 355` 仍只是 `keep_P1` survivor，关键 blocker 是 `after-cost pocket` 是否真实存在，而不是已到 `P3` 仍未被升级；
- 其余对象都还只是后续可执行的 fresh intake，不构成 P2/P3 兜底升级条件。

## 一句话总结
本轮真正需要修的是排班，不是研究结论：`Rank 355` 明明已合法占用 survivor 槽位，却没被写成首条 `pending`。我已经把它的唯一 follow-up 放回 `cycle_plan` 第一位，并把后续具体 fresh intake 顺到后面，恢复成符合 policy 的前排链条。