# Strategy Review — 2026-04-02 09:52 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并已复核当前 repo/runtime 与最近证据：
- `git status --short --branch`
- `research/strategy_review/2026-04-02_0854_strategy-review.md`
- `research/optimization_loop/2026-04-02_0915_rank291_kvsi_gate_keep_p1.md`
- `research/optimization_loop/2026-04-02_0950_coint_lookback_volfilter_pairs_background_p0.md`
- `research/optimization_loop/2026-04-02_0159_rank285_p2_exit_rescope_to_p1.md`
- `research/quant_digests/2026-04-02_0306_dynamic-coint-percentile-pairs-alpha.md`
- `research/quant_digests/2026-04-02_0232_crossasset-integrated-ofi-leadlag-alpha.md`
- `research/quant_digests/2026-04-02_0936_ivspike-sweep-creditspread-options-alpha.md`

## Repo / runtime quick check
- repo 当前无新的已跟踪改动需要纳入排班；`git status --short --branch` 主要显示工作区外层遗留 `tmp_*` 未跟踪文件，不改变本轮前排判断。
- `Paper launch queue` 当前 `current_target = none`；已连线运行的仍是 `Rank 200 / 201 / 213 / 229`。
- 最近没有新的 `Active P2` 证据显示某对象已足够被 bot2 兜底直推 `P3`。

## 本轮只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- 否，当前为空。
- `current_target = none`，queue 头没有待接线对象。
- 因此本轮没有 `P3 handoff / launch wiring` 的默认优先动作。

### 2) 本轮 `fresh intake` 是什么？
- 当前前排里唯一真实更高优先级动作，是 `Rank 291` 的 survivor follow-up。
- 在 survivor 之后，本轮 fresh intake 头号对象应切到：
  - `research/quant_digests/2026-04-02_0306_dynamic-coint-percentile-pairs-alpha.md`
- 原因：上一条 fresh intake（`2026-04-02_0405 coint lookback + vol veto + trailing stop`）已于 `09:50 UTC` 诚实首判为 `background/P0`，因此 fresh intake 槽位应滚动到下一条具体对象，而不是继续停留在已完成条目上。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 不值得。
- 上一条 fresh intake 是：
  - `cointegration spread z-score × optimized lookback × volatility veto × adaptive trailing stop`
- 它已经完成 fresh first verdict，而且结论是清楚的 `background/P0`：
  - alpha 母体仍是旧的 beta-hedged cointegration spread mean reversion；
  - 所谓增量主要是 lookback search / vol veto / min-holding / trailing-stop 这类熟悉的 pairs governance 壳；
  - distinctness 不足，不配占用 survivor 那唯一一次 follow-up 配额。
- 因此 survivor 槽位不应给它，而应继续保留给上一条已 `keep_P1` 的合法 survivor：`Rank 291`。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`。
- 最近一个 active P2 是 `Rank 285`，但它已在 `2026-04-02 01:59 UTC` 完成出口决策：
  - broad `24h losers-vs-winners XS reversal` 不够诚实直接升 `P3`；
  - 也未被 fatal flaw 判死到 `P0`；
  - 已执行一次性的 `P2 -> P1 re-scope`，收窄到 `mature liquid tail / high-RV`、`1h~4h` 慢节奏持有 pocket。
- 所以当前 `Active P2 = none`，不存在仍需在 `P3 / P1 / P0` 三出口中再择一的 active 对象。

## Rank 完整性检查
- `Paper launch queue`: `none`，无 rank 缺口。
- `Surviving candidate slot`: `Rank 291`，已有正式 rank。
- `Active P2 slot`: `none`。
- 本轮前排不存在“已到 keep_P1 / P2 / P3 但无正式 rank”的对象，因此无需补新 rank。

## 本轮重排后的 policy 一致性判断
按 policy 默认顺序：`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0归档`。

当前真实顺序应为：
1. 没有 `P3` queue 头待接线；
2. 没有 `Active P2`；
3. 存在合法 `Surviving candidate`：`Rank 291`，且 `followup_budget_remaining = 1`；
4. 因此第一优先级必须是 `Rank 291` 的唯一 follow-up；
5. 在此之后，fresh intake 才依次排入：
   - `dynamic coint percentile pairs`
   - `cross-asset integrated OFI lead/lag`
   - 条件式补位：`near-expiry IV spike × sweep credit spread`

## 对 `BOT2_BOT3_STATE.md` 的实际写回
本轮已写回 runtime state，主要包括：
- 将 `Fresh intake slot` 从已完成的 `2026-04-02_0405 coint lookback...` 滚动到新的 pending 对象：
  - `research/quant_digests/2026-04-02_0306_dynamic-coint-percentile-pairs-alpha.md`
- 重写 `cycle_plan` 为当前合法前排顺序：
  1. `Rank 291` survivor 唯一 follow-up
  2. `dynamic coint percentile pairs` fresh intake
  3. `cross-asset integrated OFI lead/lag` fresh intake
  4. `near-expiry IV spike × 1m liquidity sweep → short vertical credit spread` 条件式 fresh intake

## 结论
- `Paper launch queue`：空
- 本轮 `fresh intake`：`dynamic coint percentile pairs`（但排在 `Rank 291` survivor follow-up 之后）
- 上一条 fresh intake 是否值得唯一一次 follow-up：不值得，已诚实收口为 `background/P0`
- 当前明确 `Active P2`：无
- 本轮需要改写 state：需要，且已完成；原因是 `fresh intake` 槽位与 `cycle_plan` 必须从已完成的 pairs 壳条目滚动到新的合法前排顺序
