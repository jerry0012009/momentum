# 2026-04-06 12:39 UTC — bot2 strategy review

本轮严格按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 做 40 分钟 desk review；只更新 runtime state，不改 policy / brief / operating card / cron prompt。

## 先回答 4 个问题

1. **`Paper launch queue` 是否非空？**
   - 否。
   - 当前 `Paper launch queue.current_target = none`。
   - `connected_runner_live` 里已有 `Rank 200 / 201 / 213 / 229 / 342`，但没有新的 queue 头对象等待 handoff / wiring。

2. **本轮 `fresh intake` 是什么？**
   - 当前前排 `P3 / P2 / P1` 已全部诚实收口后，本轮重新切回 `fresh intake`。
   - 按最近新 digest 的默认来源顺序，本轮首个 fresh intake 改写为：
     - `research/quant_digests/2026-04-06_1224_adverse-selection-cost-continuation-alpha.md`
   - 其后续具体 intake 顺序写为：
     - `2026-04-06_1134_btc-positioning-fuel-cascade-alpha.md`
     - `2026-04-06_1105_synthetic-futures-carry-substitution-alpha.md`
     - `2026-04-06_1020_volume-anomaly-bandfade-hmm-veto-alpha.md`

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - 不值得继续追加；唯一一次 follow-up 已经用完并完成诚实收口。
   - 上一条 fresh intake 是 `Rank 352 / BTC perp conditional drift`。
   - 最新证据：`research/optimization_loop/2026-04-06_1231_rank352_survivor_followup_ewma_conditional_drift_background_p0.md`
   - 结论：`5m/15m` 上 `EWMA mean / EWMA vol` 版 `score=μ̂/σ̂` 虽有零散分桶相关性，但极端 decile 顺势收益仅 `0.14~0.72 bps` gross，显著低于 `4 bps` taker round-trip 成本，且单调性不稳定；因此对象不升 `P2`，也不再占用 survivor 槽位，直接退回 `background / P0`。

4. **当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - 当前不存在明确 `Active P2`。
   - `Active P2 slot.current_target = none`。
   - 最近收口的 `Active P2` 是 `Rank 342`，已在 `2026-04-05_2300_rank342_p2_exit_promote_p3_lowgas_samechain_paper_queue.md` 完成 `P2 -> P3`，并在 `2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md` 完成最小 wiring；本轮不存在需要 bot2 兜底裁判的活跃 P2。

## Rank / 前排合法性检查

- 当前前排对象：
  - `Paper launch queue = none`
  - `Surviving candidate = none`
  - `Active P2 = none`
- 前排不存在 `keep_P1 / P2 / P3` 但无 rank 的对象。
- 本轮**无需补 rank**。

## 最近证据与排班判断

### 最近会改变排班的证据

1. `research/optimization_loop/2026-04-06_1231_rank352_survivor_followup_ewma_conditional_drift_background_p0.md`
   - 说明 `Rank 352` 的 survivor follow-up 已经诚实收口，不升 `P2`，且 survivor 槽位已经释放。
   - 因此本轮默认顺序不再是 `P1 survivor`，而是直接切回新的 `fresh intake`。

2. `research/optimization_loop/2026-04-06_1113_rank352_btc_perp_conditional_drift_intake_keep_p1.md`
   - 说明上一条 fresh intake 的确曾达到 `keep_P1`，但现在已用完唯一 follow-up。
   - 因此不得再把 `Rank 352` 继续排成第二次 survivor 检查。

3. `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md`
   - 说明最近的 `P3` 已经正式落地到 `connected_runner_live`，本轮没有待接线 queue 头。

4. 最近新 digest 的时间顺序显示，当前最应优先进入 intake 的具体对象是：
   - `2026-04-06_1224_adverse-selection-cost-continuation-alpha.md`
   - `2026-04-06_1134_btc-positioning-fuel-cascade-alpha.md`
   - `2026-04-06_1105_synthetic-futures-carry-substitution-alpha.md`
   - `2026-04-06_1020_volume-anomaly-bandfade-hmm-veto-alpha.md`

### 按 authoritative 顺序扫描当前所有合法动作

1. **P3 / Paper launch queue handoff**
   - 无待接线对象；`current_target = none`。

2. **P2 / Active P2 admission / promote / park**
   - 无明确 `Active P2`；`current_target = none`。

3. **P1 / Surviving candidate 唯一一次诚实检查**
   - 当前无合法 survivor；`Rank 352` 已用完唯一 follow-up 并退回 `background / P0`。

4. **fresh intake**
   - 因为 `P3 / P2 / P1` 均无真实可执行动作，本轮可以并且必须切回新的具体 `fresh intake`。
   - 按最近新 digest 的默认来源顺序，优先级应为：
     1. `adverse-selection-cost-continuation`
     2. `btc-positioning-fuel-cascade`
     3. `synthetic-futures-carry-substitution`
     4. `volume-anomaly-bandfade-hmm-veto`

## 对 `BOT2_BOT3_STATE.md` 的具体改写

本轮已重写 `cycle_plan`，遵循当前合法顺序：`P3 none > P2 none > survivor none > fresh intake`。

1. `research/quant_digests/2026-04-06_1224_adverse-selection-cost-continuation-alpha.md`
   - action: first verdict
   - goal: 回答 `signed adverse-selection share shock × next-bar continuation` 是否是真正独立的 microstructure raw alpha，而不是旧 order-imbalance / OFI 题材的学术重命名

2. `research/quant_digests/2026-04-06_1134_btc-positioning-fuel-cascade-alpha.md`
   - action: first verdict
   - goal: 回答 `crowd-positioning fuel-cascade × 13pp fuel exit` 是否真能形成独立于 funding / basis / sentiment 的 BTC perp raw alpha

3. `research/quant_digests/2026-04-06_1105_synthetic-futures-carry-substitution-alpha.md`
   - action: first verdict
   - goal: 回答 `synthetic future vs listed perp carry gap` 是否真是独立 carry substitution 主语，而不是旧 carry 家族重命名

4. `research/quant_digests/2026-04-06_1020_volume-anomaly-bandfade-hmm-veto-alpha.md`
   - action: first verdict
   - goal: 回答 `volume anomaly -> band fade` 是否有独立反转主语，还是靠 filter 堆叠勉强成立

新计划项全部保持：`result = none`、`status = pending`。

## P2 -> P3 兜底检查

- 当前没有 `Active P2`。
- 因此本轮不存在“desk review 已清楚表明足够进入 paper trade，而 bot3 尚未升级”的对象。
- 本轮**无需**执行 bot2 的 `P2 -> P3` 兜底直推。

## 执行备注

- `BOT2_BOT3_STATE.md` 已按本轮 review 写回。
- 本轮未改写 policy / brief / operating card / auto loop / cron prompt。
- 当前没有合法理由把 background pool 旧候选拉回前排。

## 一句话结论

本轮 runtime truth 很清楚：`Paper launch queue` 为空，`Active P2` 为空，上一条 fresh intake `Rank 352` 的 survivor follow-up 也已经诚实收口并退回 `background / P0`；所以正确排班不是继续拖旧对象，而是按最近新 digest 顺序切回新的具体 intake，队首依次是 `adverse-selection-cost-continuation`、`btc-positioning-fuel-cascade`、`synthetic-futures-carry-substitution`、`volume-anomaly-bandfade-hmm-veto`。