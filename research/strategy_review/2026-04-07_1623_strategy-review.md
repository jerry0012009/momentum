# 2026-04-07 16:23 UTC strategy review

## Scope
按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 执行本轮 40 分钟 desk review；只更新 runtime state，不改 policy / brief / operating card / auto loop / cron prompt。

## 先回答 4 个问题

### 1) `Paper launch queue` 是否非空？
**否。**

当前 `Paper launch queue.current_target = none`。`Rank 200 / 201 / 213 / 229 / 342` 都已经在 `connected_runner_live`，最近一条仍是 `Rank 342`，其 dedicated runner、scheduler 与首跑验证已在 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md` 完成。因此本轮没有待接线的 `P3` 头对象。

### 2) 本轮 `fresh intake` 是什么？
**是 `research/quant_digests/2026-04-07_1549_levy-rowscore-follower-catchup-alpha.md`。**

原因很直接：
- 当前 `Surviving candidate slot = none`
- 当前 `Active P2 slot = none`
- 当前 `Paper launch queue.current_target = none`

前排已经诚实收口，本轮必须切回最新、尚未处理的具体 intake。按最近 digest 时间顺序，最新合格对象已经不是 `1523 xemm`，而是 `15:49 UTC` 新出的 `Lévy rowscore leader move × follower catch-up basket`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
**不值得，因为上一条 fresh intake 并没有进入 `keep_P1`。**

上一条已完成 first verdict 的 fresh intake 是 `research/quant_digests/2026-04-07_1334_btc-coinm-carry-rollover-shell.md`，对应结论见 `research/optimization_loop/2026-04-07_1530_btc_coinm_carry_rollover_shell_first_verdict_background.md`：
- 它补的是标准 `carry / basis convergence` 家族更完整的 cash-and-carry 执行外壳；
- 新增主要在 execution shell，不在独立 raw alpha 主语；
- 因此本轮诚实收口为 `background / P0`，不进入 survivor，也就不存在 follow-up 配额问题。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。**

`Active P2 slot.current_target = none`。最近的明确 `Active P2` 仍是 `Rank 342`，但它已经先在 `research/optimization_loop/2026-04-05_2300_rank342_p2_exit_promote_p3_lowgas_samechain_paper_queue.md` 完成 `P2 -> P3`，又在 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md` 完成最小接线，所以本轮不存在需要 bot2 兜底推进到 `P3 / P1 / P0` 的在场 `Active P2`。

## Rank / 前排合法性检查
- `Paper launch queue.current_target = none`，合法。
- `Surviving candidate slot.current_target = none`，合法。
- `Active P2 slot.current_target = none`，合法。
- 当前前排不存在达到 `keep_P1 / P2 / P3` 但无正式 `Rank` 的对象，因此本轮无需补 rank。

## 最近证据与本轮判断
本轮先看了固定 policy 和 runtime state，再补了最近 repo/日志链条：

1. `research/optimization_loop/2026-04-07_1612_rank356_survivor_followup_background_router_loses_to_plain_xs.md`
   - `Rank 356` 的唯一 survivor follow-up 已经做完，并在 `12` 个 liquid majors 的 `365d/15m` clean-room 中被明确打回 `background/P0`；这意味着 survivor 槽位已经释放。
2. `research/optimization_loop/2026-04-07_1530_btc_coinm_carry_rollover_shell_first_verdict_background.md`
   - 最近已完成 first verdict 的 fresh intake 也已诚实收口为 `background/P0`；说明当前前排没有遗留的 `P1` 锁位。
3. `research/quant_digests/2026-04-07_1549_levy-rowscore-follower-catchup-alpha.md`
   - 这是当前最新的新对象；它的主语不是 generic graph demo，而是 `leader ranking -> follower basket catch-up` 的横截面传导线，因此应占用本轮 fresh intake 第一位。
4. `research/quant_digests/2026-04-07_1523_xemm-makerfirst-takerhedge-alpha.md`
   - 仍是具体、未判决的成熟执行型对象，可排第二位。
5. `research/quant_digests/2026-04-07_1436_majorlead-closeslot-crossmarket-itsm-alpha.md`
   - 是更偏论文型的跨市场 lead-lag continuation，可排第三位。
6. `research/quant_digests/2026-04-07_1129_polymarket-pairsum-shield-maker-alpha.md`
   - 虽然和 `Rank 355` 同属 prediction-market 相关方向，但命题是 `complementary-outcome pair-sum`，并非旧的 adjacent-horizon term-structure，仍可作为 conditional intake。

因此，这轮不存在任何合规的 `P3 / P2 / survivor` 收口动作；正确排班就是切回 fresh intake，并按时间顺序与对象具体性把当前值得做的 4 条 intake 填满。

## 为什么这轮不需要 bot2 兜底升 P3
本轮没有任何在场 `Active P2`：
- `Rank 342` 已完成 `P2 -> P3 -> connected_runner_live`
- `Rank 356` 已在 survivor follow-up 中被诚实收口回 `background/P0`
- 最新对象们都还没进入 `P2`

所以不存在“desk review 已清楚表明某个在场 `Active P2` 足够值得进入 paper trade，而 bot3 尚未升级”的漏升对象；本轮无需 bot2 直接写入 `P3 / Paper launch queue` 或 handoff 路径。

## 本轮 runtime 调整
本轮只改了 `docs/BOT2_BOT3_STATE.md`，且只动允许 bot2 更新的 runtime 部分：

### 1) Fresh intake slot
- `current_target` 从 `2026-04-07_1523_xemm-makerfirst-takerhedge-alpha.md` 切到最新的 `2026-04-07_1549_levy-rowscore-follower-catchup-alpha.md`
- `source_record` 同步切到 `1549` digest
- `latest_result` 仍保留最近已完成的 first verdict：`1334 btc-coinm carry rollover shell -> background / P0`

### 2) cycle_plan
按 policy 默认顺序重写为 4 项，全部是具体对象、具体动作：
1. `1549 levy-rowscore-follower-catchup` fresh intake
2. `1523 xemm-makerfirst-takerhedge` fresh intake
3. `1436 majorlead-closeslot-crossmarket-itsm` fresh intake
4. `1129 polymarket-pairsum-shield-maker` conditional fresh intake

每项都只保留 `target / action / success_criterion / result / status`；新项全部写成 `result: none`、`status: pending`。

## 一句话总结
这轮前排已经完全清空，所以没有任何理由继续围绕旧对象兜圈子；我已把 runtime 的 fresh intake 入口切到最新的 `1549 lead-lag follower catch-up`，并把 `1523 / 1436 / 1129` 按诚实优先级排在后面。