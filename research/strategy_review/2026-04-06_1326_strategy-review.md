# 2026-04-06 13:26 UTC — bot2 strategy review

本轮严格按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 做 40 分钟 desk review；只更新 runtime state，不改 policy / brief / operating card / cron prompt。

## 先回答 4 个问题

1. **`Paper launch queue` 是否非空？**
   - 否。
   - 当前 `Paper launch queue.current_target = none`。
   - `connected_runner_live` 里已有 `Rank 200 / 201 / 213 / 229 / 342`，但没有新的 queue 头对象等待 handoff / wiring。

2. **本轮 `fresh intake` 是什么？**
   - 在 `adverse-selection cost continuation` 已于 13:17 UTC 完成 first verdict 并退回 `background / P0` 后，前排 `P3 / P2 / P1` 全空，当前轮应切回新的具体 intake。
   - 依据 policy 的默认来源顺序（最近新的 strategy repo / paper / alpha report 优先），本轮新的 fresh-intake 队首改为：
     - `research/quant_digests/2026-04-06_1302_naps-adaptive-sizing-overlay.md`
   - 后续具体顺序写为：
     - `2026-04-06_1134_btc-positioning-fuel-cascade-alpha.md`
     - `2026-04-06_1105_synthetic-futures-carry-substitution-alpha.md`
     - `2026-04-06_1020_volume-anomaly-bandfade-hmm-veto-alpha.md`

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - 不值得。
   - 上一条 fresh intake 是 `adverse-selection cost continuation`。
   - 最新证据：`research/optimization_loop/2026-04-06_1317_adverse_selection_cost_continuation_intake_background_p0.md`
   - 结论：对象的核心仍是 `information-bearing aggressive flow -> next 1~3 bar continuation`，与池内既有 `OFI / L1 imbalance / VWAP pressure` 单资产 microstructure family 高度同构；当前最关键问题是它是否只是旧 microstructure continuation 的换术语版本，而现有 digest 自己也把 decisive 验证写成要与 `OFI / taker imbalance` 做 horse race。既然独立主语与 after-cost pocket 都没被压清，就不该拿 survivor 唯一 follow-up，直接回 `background / P0` 是诚实收口。

4. **当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - 当前不存在明确 `Active P2`。
   - `Active P2 slot.current_target = none`。
   - 最近收口的 `Active P2` 仍是 `Rank 342`，已在 `2026-04-05_2300_rank342_p2_exit_promote_p3_lowgas_samechain_paper_queue.md` 完成 `P2 -> P3`，并在 `2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md` 完成最小 wiring；本轮不存在需要 bot2 兜底裁判的活跃 P2。

## Rank / 前排合法性检查

- 当前前排对象：
  - `Paper launch queue = none`
  - `Surviving candidate = none`
  - `Active P2 = none`
- 前排不存在 `keep_P1 / P2 / P3` 但无 rank 的对象。
- 本轮**无需补 rank**。

## 最近证据与排班判断

### 会改变本轮排班的最近证据

1. `research/optimization_loop/2026-04-06_1317_adverse_selection_cost_continuation_intake_background_p0.md`
   - 说明上一条 fresh intake 已经完成 first verdict，且直接退回 `background / P0`。
   - 因此前排 survivor / P2 / P3 都为空，本轮必须切回新的具体 intake。

2. `research/optimization_loop/2026-04-06_1231_rank352_survivor_followup_ewma_conditional_drift_background_p0.md`
   - 说明上一条 survivor `Rank 352` 已经用尽唯一 follow-up 并诚实收口，不得再继续拖在前排。

3. `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md`
   - 说明最近的 `P3` 已经正式落地到 `connected_runner_live`，当前没有待接线 queue 头。

4. 最近 repo / digest 时间顺序里，新的最靠前对象是：
   - `2026-04-06_1302_naps-adaptive-sizing-overlay.md`
   - `2026-04-06_1134_btc-positioning-fuel-cascade-alpha.md`
   - `2026-04-06_1105_synthetic-futures-carry-substitution-alpha.md`
   - `2026-04-06_1020_volume-anomaly-bandfade-hmm-veto-alpha.md`

### 按 default order 扫描合法动作

1. **P3 / Paper launch queue handoff**
   - 无待接线对象；`current_target = none`。

2. **P2 / Active P2 admission / promote / park**
   - 无明确 `Active P2`；`current_target = none`。

3. **P1 / Surviving candidate 唯一一次诚实检查**
   - 当前无合法 survivor；`Rank 352` 已用完唯一 follow-up 并退回 `background / P0`。

4. **fresh intake**
   - 因为 `P3 / P2 / P1` 均无真实可执行动作，本轮可以并且必须切回新的具体 `fresh intake`。
   - 队首使用最新的 repo/paper/report：`2026-04-06_1302_naps-adaptive-sizing-overlay.md`。
   - 其后继续保留三个具体 raw-alpha intake：`btc-positioning-fuel-cascade`、`synthetic-futures-carry-substitution`、`volume-anomaly-bandfade-hmm-veto`。

## 对 `BOT2_BOT3_STATE.md` 的具体改写

### Fresh intake slot
- `status`: `pending`
- `current_target`: `research/quant_digests/2026-04-06_1302_naps-adaptive-sizing-overlay.md`
- `source_record`: 同步改到该新队首
- `latest_result`: 保持最新已完成结果仍为 `adverse-selection cost continuation -> background / P0`

### cycle_plan（4 项，全部具体对象）
1. `2026-04-06_1302_naps-adaptive-sizing-overlay.md`
   - action: first verdict
   - success criterion: 判断其是否只能诚实定位为 shared overlay / sizing layer；若没有独立 raw-alpha 主语，则不得占用 survivor，默认写成 `background / P0` 或 shared component 归档
   - result: `none`
   - status: `pending`

2. `2026-04-06_1134_btc-positioning-fuel-cascade-alpha.md`
   - action: first verdict
   - success criterion: 判断 crowd-positioning fuel-cascade 是否能形成独立于常见 funding / basis / sentiment 的 BTC perp raw alpha
   - result: `none`
   - status: `pending`

3. `2026-04-06_1105_synthetic-futures-carry-substitution-alpha.md`
   - action: first verdict
   - success criterion: 判断 synthetic-futures carry substitution 是否有独立于常见 basis/carry 的替代价差主语
   - result: `none`
   - status: `pending`

4. `2026-04-06_1020_volume-anomaly-bandfade-hmm-veto-alpha.md`
   - action: first verdict
   - success criterion: 判断 volume-anomaly band-fade × HMM veto 是否真有独立反转主语，而不是 filter 堆叠
   - result: `none`
   - status: `pending`

## P2 -> P3 兜底检查

- 当前没有 `Active P2`。
- 因此本轮不存在“desk review 已清楚表明足够进入 paper trade，而 bot3 尚未升级”的对象。
- 本轮**无需**执行 bot2 的 `P2 -> P3` 兜底直推。

## 一句话结论

本轮 runtime truth 很直接：`Paper launch queue` 为空，`Active P2` 为空，上一条 fresh intake `adverse-selection cost continuation` 已经首判收口并退回 `background / P0`；所以正确排班不是继续拖旧对象，而是按 policy 的默认顺序切回新的具体 intake，新的队首是 `NAPS adaptive sizing overlay`，其后依次是 `btc-positioning-fuel-cascade`、`synthetic-futures-carry-substitution`、`volume-anomaly-bandfade-hmm-veto`。
