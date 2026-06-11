# Strategy Review — 2026-04-02 10:59 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并已复核当前 repo/runtime 与最近证据：
- `git status --short --branch`
- `research/strategy_review/2026-04-02_0952_strategy-review.md`
- `research/optimization_loop/2026-04-02_1031_rank291_survivor_followup_background_p0.md`
- `research/optimization_loop/2026-04-02_0950_coint_lookback_volfilter_pairs_background_p0.md`
- `research/optimization_loop/2026-04-02_0159_rank285_p2_exit_rescope_to_p1.md`
- `research/quant_digests/2026-04-02_0232_crossasset-integrated-ofi-leadlag-alpha.md`
- `research/quant_digests/2026-04-02_0936_ivspike-sweep-creditspread-options-alpha.md`
- `research/quant_digests/2026-04-02_1007_pressure-ratio-capitulation-fade-alpha.md`
- `research/quant_digests/2026-04-02_1050_polymarket-lateentry-binary-continuation-alpha.md`

## Repo / runtime quick check
- repo 当前未出现会改变前排判断的已跟踪 runtime 改动；`git status` 仍主要是大量未跟踪研究产物与临时文件，不构成新的前排对象。
- `Paper launch queue` 当前仍为 `current_target = none`；已接线运行的仍是 `Rank 200 / 201 / 213 / 229`。
- 最近没有新的 `Active P2` 证据，也没有对象达到需要 bot2 兜底直推 `P3` 的门槛。

## 本轮只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- 否，当前为空。
- `current_target = none`，queue 头没有待接线对象。
- 因此本轮没有 `P3 handoff / launch wiring` 优先动作。

### 2) 本轮 `fresh intake` 是什么？
- 当前前排不存在 `P3`、`Active P2` 或合法 `Surviving candidate` 动作。
- 所以 fresh intake 重新成为第一优先级。
- 本轮 fresh intake 头号对象应是：
  - `research/quant_digests/2026-04-02_0232_crossasset-integrated-ofi-leadlag-alpha.md`
- 原因：上一条 fresh intake `2026-04-02_0306_dynamic-coint-percentile-pairs-alpha.md` 已于 `09:50 UTC` 明确首判为 `background/P0`，而 `Rank 291` 的 survivor 也已于 `10:31 UTC` 用完唯一 follow-up 并回 `background/P0`；因此 fresh intake 槽位应滚到下一条尚未首判的新对象。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 不值得。
- 上一条 fresh intake 是：
  - `cointegration spread z-score × optimized lookback × volatility veto × adaptive trailing stop`
- 最近证据已把它收口得很清楚：
  - 母体仍是旧的 beta-hedged cointegration spread mean reversion；
  - 新增部分主要是 lookback search / vol veto / min-holding / trailing stop 等治理壳；
  - distinctness 不足，不值得占用 survivor 唯一 follow-up 配额。
- 因此它最诚实的结论就是停在 `background/P0`，不进 survivor。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`。
- 最近一个 active P2 是 `Rank 285`，但它已在 `2026-04-02 01:59 UTC` 完成出口决策：
  - broad `24h losers-vs-winners XS reversal` 不够诚实直接升 `P3`；
  - 同时存在明确 re-scope 方向，因此执行了一次性的 `P2 -> P1 re-scope`；
  - 所以现在 `Active P2 = none`，不存在仍需在 `P3 / P1 / P0` 三出口中继续裁决的 active 对象。

## Rank 完整性检查
- `Paper launch queue`: `none`，无 rank 缺口。
- `Surviving candidate slot`: `none`。
- `Active P2 slot`: `none`。
- 当前前排不存在任何已达 `keep_P1 / P2 / P3` 但无正式 rank 的对象，因此无需补新 rank。

## 本轮排班判断
按 policy 默认顺序：`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0归档`。

当前真实顺序是：
1. 没有 `P3` queue 头待接线；
2. 没有 `Active P2`；
3. 没有合法 survivor follow-up；
4. 因此前排必须直接切回新的 `fresh intake`；
5. 本轮按具体对象排为：
   - `crossasset-integrated-ofi-leadlag`
   - `ivspike-sweep-creditspread-options`
   - `pressure-ratio-capitulation-fade`
   - `polymarket-lateentry-binary-continuation`

## 对 `BOT2_BOT3_STATE.md` 的实际写回
本轮已写回 runtime state，主要包括：
- 将 `Fresh intake slot` 滚动到新的 pending 对象：
  - `research/quant_digests/2026-04-02_0232_crossasset-integrated-ofi-leadlag-alpha.md`
- 保持 `Surviving candidate slot = none`（`Rank 291` 已完成唯一 follow-up 并回 `background/P0`）
- 保持 `Active P2 slot = none`
- 重写 `cycle_plan` 为当前最诚实的 4 条 fresh intake 顺序：
  1. `crossasset-integrated-ofi-leadlag`
  2. `ivspike-sweep-creditspread-options`
  3. `pressure-ratio-capitulation-fade`
  4. `polymarket-lateentry-binary-continuation`

## 结论
- `Paper launch queue`：空
- 本轮 `fresh intake`：`crossasset-integrated-ofi-leadlag`
- 上一条 fresh intake 是否值得唯一 follow-up：不值得，已诚实收口为 `background/P0`
- 当前明确 `Active P2`：无
- 本轮不需要补 rank
- 本轮需要改写 state：需要，且已完成；原因是 `Rank 291` survivor 已收口、上一条 fresh intake 已完成首判，前排应切换到新的合法 fresh intake 队列
