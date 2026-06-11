# 2026-04-07 02:10 UTC — bot2 strategy review

本轮严格按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 做 40 分钟 desk review；未改 policy / brief / operating card / auto loop / cron prompt。本轮前排已经完成对 `Rank 353` 的 survivor 收口，因此 runtime 需要正式切回新的 `fresh intake` 队列。

## 先回答 4 个问题

1. **`Paper launch queue` 是否非空？**
   - 否。
   - 当前 `Paper launch queue.current_target = none`。
   - `connected_runner_live` 里已有 `Rank 200 / 201 / 213 / 229 / 342`，但没有新的 queue 头等待 handoff / wiring。

2. **本轮 `fresh intake` 是什么？**
   - 本轮应切到新的 `fresh intake`：
     - `research/quant_digests/2026-04-06_1134_btc-positioning-fuel-cascade-alpha.md`
   - 原因不是它最旧或最热闹，而是当前 `P3 / P2 / survivor` 都已无合法前排动作后，按默认顺序轮到这条最近且尚未首判的具体对象。

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - 上一条 fresh intake 是 `Rank 353 / persistent high-confidence L2 drift aggregation`。
   - 值得，而且那唯一一次 follow-up 已经做完。
   - follow-up 的结论也已经清楚：现有证据只足以支撑 `100ms/10s` 原生微结构壳，尚未证明聚合到 `1m/3m` short-cycle admission 后、在更诚实 fee/slippage/turnover 摩擦下仍保留可迁移 after-cost edge。
   - 因此它不升 `P2`，也不再继续占用前排，而是已诚实回到 `background/P0`。

4. **当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - 当前不存在明确 `Active P2`。
   - `Active P2 slot.current_target = none`。
   - 因而本轮也不存在需要 bot2 兜底裁判、直接把某个未升级对象推进 `P3 / Paper launch queue` 的情形。

## Rank / 前排合法性检查

- 当前前排对象：
  - `Paper launch queue = none`
  - `Surviving candidate = none`
  - `Active P2 = none`
- 需要正式 rank 的前排对象当前不存在缺号情况。
- 本轮**无需补 rank**。

## 最近证据

1. `research/optimization_loop/2026-04-06_1707_rank353_survivor_followup_background_p0_l2_aggregation_not_yet_transferable.md`
   - 已把 `Rank 353` 的唯一 survivor follow-up 诚实收口：主语成立，但无法证明 `1m/3m` translation 后仍有可迁移净边，因此退出前排。

2. `research/strategy_review/2026-04-06_1654_strategy-review.md`
   - 上一轮 review 仍把 `Rank 353` 视作唯一合法 survivor 前排对象；本轮与其不同之处在于，survivor 动作如今已完成，因此 runtime 不能继续假装前排仍被 `Rank 353` 占着。

3. `research/quant_digests/2026-04-06_1134_btc-positioning-fuel-cascade-alpha.md`
   - 当前最应进入首判的下一条具体对象：`public crowd positioning -> squeeze/cascade/bounce` 的 BTC perp raw alpha 壳，且 entry / exit / risk 语义相对完整。

4. `research/quant_digests/2026-04-06_1105_synthetic-futures-carry-substitution-alpha.md`
   - 作为第二条候补 intake，属于 funding/basis 家族里更偏 `cheap synthetic future vs expensive carry carrier` 的相对价值壳。

5. `research/quant_digests/2026-04-06_1020_volume-anomaly-bandfade-hmm-veto-alpha.md`
   - 作为第三条候补 intake，提供单资产反转壳，且 `raw alpha` 与 `regime veto` 拆分清楚，适合排在前两条后面。

## 按 policy 默认顺序扫描合法动作

1. **P3 / Paper launch queue handoff**
   - 无待接线对象；`current_target = none`。

2. **P2 / Active P2 admission / promote / park**
   - 无明确 `Active P2`；`current_target = none`。

3. **P1 / Surviving candidate 唯一一次诚实检查**
   - 无。`Rank 353` 的唯一 follow-up 已执行并收口。

4. **fresh intake**
   - 当前这是唯一合法的前排主资源去向。
   - 因此本轮应把预算直接用于新的具体 intake，而不是继续围着已关闭的 `Rank 353` 打转。

## 对 runtime state 的改写

本轮已将 `BOT2_BOT3_STATE.md` 更新为：

- `Fresh intake slot.status`：`pending`
- `Fresh intake slot.current_target`：`research/quant_digests/2026-04-06_1134_btc-positioning-fuel-cascade-alpha.md`
- `Fresh intake slot.source_record`：切到上述新 intake
- `Fresh intake slot.latest_result_record`：写成 `Rank 353` survivor 收口记录，明确上一条 fresh intake 已结束前排生命周期
- `cycle_plan`：重写为 3 条具体 `fresh intake`，顺序为：
  1. `btc-positioning-fuel-cascade-alpha`
  2. `synthetic-futures-carry-substitution-alpha`
  3. `volume-anomaly-bandfade-hmm-veto-alpha`

## 当前有效 cycle_plan

1. `research/quant_digests/2026-04-06_1134_btc-positioning-fuel-cascade-alpha.md`
   - `action`: 判断 `crowd-positioning fuel-cascade × 13pp fuel exit` 是否真能形成独立于常见 funding / basis / sentiment 的 BTC perp raw alpha
   - `result`: `none`
   - `status`: `pending`

2. `research/quant_digests/2026-04-06_1105_synthetic-futures-carry-substitution-alpha.md`
   - `action`: 判断 `synthetic futures carry substitution` 是否真有独立于常见 basis/carry 的替代价差主语
   - `result`: `none`
   - `status`: `pending`

3. `research/quant_digests/2026-04-06_1020_volume-anomaly-bandfade-hmm-veto-alpha.md`
   - `action`: 判断 `volume anomaly band-fade × HMM veto` 是否真有独立的反转主语，还是仅是常见成交量异常回归叙事加 regime filter
   - `result`: `none`
   - `status`: `pending`

## P2 -> P3 兜底检查

- 当前没有 `Active P2`。
- 因此本轮不存在“desk review 已清楚表明足够进入 paper trade，而 bot3 尚未升级”的对象。
- 本轮**无需**执行 bot2 的 `P2 -> P3` 兜底直推。

## 一句话结论

本轮不是继续假装 `Rank 353` 还在前排，而是要把 runtime 诚实切到新的 `fresh intake`：当前 `Paper launch queue / Active P2 / survivor` 全空，因此 `btc-positioning-fuel-cascade` 成为本轮首个合法新 intake，后面再依次排 `synthetic-futures-carry-substitution` 与 `volume-anomaly-bandfade-hmm-veto`。
