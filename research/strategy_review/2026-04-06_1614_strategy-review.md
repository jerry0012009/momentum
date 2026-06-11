# 2026-04-06 16:14 UTC — bot2 strategy review

本轮严格按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 做 40 分钟 desk review；未改 policy / brief / operating card / auto loop / cron prompt，只重写了 runtime state 中的 `cycle_plan`。

## 先回答 4 个问题

1. **`Paper launch queue` 是否非空？**
   - 否。
   - 当前 `Paper launch queue.current_target = none`。
   - `connected_runner_live` 里已有 `Rank 200 / 201 / 213 / 229 / 342`，但没有新的 queue 头对象等待 handoff / wiring。

2. **本轮 `fresh intake` 是什么？**
   - 当前 runtime 中最新完成的 fresh intake 仍是：
     - `research/quant_digests/2026-04-06_1350_l2-10s-drift-aggregation-alpha.md`
   - 它已在 `research/optimization_loop/2026-04-06_1604_rank353_l2_drift_aggregation_intake_keep_p1.md` 完成 first verdict，正式写成：
     - `Rank 353 / persistent high-confidence L2 drift aggregation`
   - 因此它现在不再是待判 fresh intake，而是当前唯一合法的 survivor front object。

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - 值得。
   - 最新证据已经明确：`Rank 353` 不是单纯 README 叙事，也不只是 `100ms HFT demo`；它已经具备：
     - `continuous L2 pressure -> future 10s directional drift` 的独立 raw alpha 主语；
     - 公开 Binance `depth20@100ms` + calibrated probability + thresholded paper-trade shell 的最小复现实验壳；
     - 最基础 spread-crossing honesty 边界。
   - 但它还没回答决定性问题：把 `100ms/10s` 微结构概率聚合成 `1m/3m` short-cycle admission 后，扣除更诚实摩擦是否仍保留最小可迁移 edge。
   - 这正是 policy 允许且要求的那唯一一次 survivor follow-up，因此本轮必须先做它，而不是让新的 intake 抢到前面。

4. **当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - 当前不存在明确 `Active P2`。
   - `Active P2 slot.current_target = none`。
   - 最近收口的 `Active P2` 仍是 `Rank 342`，已在 `research/optimization_loop/2026-04-05_2300_rank342_p2_exit_promote_p3_lowgas_samechain_paper_queue.md` 完成 `P2 -> P3`，并在 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md` 完成最小 wiring；本轮不存在需要 bot2 兜底裁判的活跃 P2。

## Rank / 前排合法性检查

- 当前前排对象：
  - `Paper launch queue = none`
  - `Surviving candidate = Rank 353`
  - `Active P2 = none`
- 前排对象均已有正式 rank；本轮**无需补 rank**。

## 最近证据与结论

### 最近证据
1. `research/optimization_loop/2026-04-06_1604_rank353_l2_drift_aggregation_intake_keep_p1.md`
   - 说明 `Rank 353` 已完成 first verdict，且诚实位置是 `keep_P1`，不是 `P0`、也不是直接 `P2`。

2. `research/optimization_loop/2026-04-06_1408_naps_adaptive_sizing_overlay_intake_background_p0.md`
   - 说明更早一条 intake `NAPS adaptive sizing overlay` 已被收口到 `background / P0`，因为它只是 shared sizing overlay，不构成独立 raw alpha 主语。

3. `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md`
   - 说明最近 `P3` 已经正式落地到 `connected_runner_live`，本轮没有待接线 queue 头。

### 按 policy default order 扫描合法动作
1. **P3 / Paper launch queue handoff**
   - 无待接线对象；`current_target = none`。

2. **P2 / Active P2 admission / promote / park**
   - 无明确 `Active P2`；`current_target = none`。

3. **P1 / Surviving candidate 唯一一次诚实检查**
   - 有且仅有一个合法动作：`Rank 353` 的唯一 survivor follow-up。
   - 按 policy，这个动作的优先级高于任何新的 fresh intake。

4. **fresh intake**
   - 只有在 survivor 已被诚实排入当前轮前部之后，才能用剩余预算补新的具体 intake。
   - 因此本轮 fresh intake 顺序保留为：
     - `research/quant_digests/2026-04-06_1134_btc-positioning-fuel-cascade-alpha.md`
     - `research/quant_digests/2026-04-06_1105_synthetic-futures-carry-substitution-alpha.md`
     - `research/quant_digests/2026-04-06_1020_volume-anomaly-bandfade-hmm-veto-alpha.md`

## 对 runtime state 的实际改写

本轮只改写了 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`，把已经完成的 `Rank 353` first verdict 从队首移除，并按 policy 重排为：

1. `Rank 353 / persistent high-confidence L2 drift aggregation`
   - `action`: survivor slot 的唯一一次诚实 follow-up
   - `success_criterion`: 明确回答聚合到 `1m/3m` 后是否仍留有最小可迁移 after-cost edge；若是则升 `P2`，若否则 survivor 用尽并回 `background / P0`
   - `result`: `none`
   - `status`: `pending`

2. `research/quant_digests/2026-04-06_1134_btc-positioning-fuel-cascade-alpha.md`
   - `action`: fresh intake first verdict
   - `result`: `none`
   - `status`: `pending`

3. `research/quant_digests/2026-04-06_1105_synthetic-futures-carry-substitution-alpha.md`
   - `action`: fresh intake first verdict
   - `result`: `none`
   - `status`: `pending`

4. `research/quant_digests/2026-04-06_1020_volume-anomaly-bandfade-hmm-veto-alpha.md`
   - `action`: fresh intake first verdict
   - `result`: `none`
   - `status`: `pending`

## P2 -> P3 兜底检查

- 当前没有 `Active P2`。
- 因此本轮不存在“desk review 已清楚表明足够进入 paper trade，而 bot3 尚未升级”的对象。
- 本轮**无需**执行 bot2 的 `P2 -> P3` 兜底直推。

## 一句话结论

本轮 runtime truth 很直接：`Paper launch queue` 为空，`Active P2` 为空，而 `Rank 353` 已经完成 fresh intake first verdict 并获得 survivor 锁定权；所以正确排班不是继续把新的 intake 顶到前面，而是先完成 `Rank 353` 那唯一一次诚实 follow-up，再依次处理 `btc-positioning-fuel-cascade`、`synthetic-futures-carry-substitution`、`volume-anomaly-bandfade-hmm-veto`。
