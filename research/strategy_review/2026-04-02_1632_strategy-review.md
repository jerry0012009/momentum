# Strategy Review — 2026-04-02 16:32 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并已复核当前 repo/runtime 与最近证据：
- `git status --short`
- `research/optimization_loop/2026-04-02_1421_rank294_coinbase_premium_impulse_keep_p1.md`
- `research/optimization_loop/2026-04-02_1334_rank293_survivor_followup_background_p0_cost_realism_fail.md`
- `research/optimization_loop/2026-04-02_1255_rank293_ivspike_creditspread_keep_p1.md`
- `research/optimization_loop/2026-04-02_1204_rank292_survivor_followup_background_p0_increment_not_shown.md`
- `research/strategy_review/2026-04-02_1411_strategy-review.md`
- `research/quant_digests/2026-04-02_1625_topn-reversal-pumpveto-confidence-alpha.md`
- `research/quant_digests/2026-04-02_1320_coinbase-premium-impulse-ema-alpha.md`
- `research/quant_digests/2026-04-02_1250_liquidity-risk-interaction-xs-alpha.md`
- `research/quant_digests/2026-04-02_1124_pca-eigenportfolio-residual-statarb-alpha.md`
- `research/quant_digests/2026-04-02_1140_extreme-ofi-tradeflow-continuation-alpha.md`

## Repo / runtime quick check
- repo 当前仍主要是未跟踪研究产物；没有新的已写回 runtime 结论会改变当前前排优先级。
- `Paper launch queue` 仍为 `current_target = none`；已接线运行的仍是 `Rank 200 / 201 / 213 / 229`。
- `Rank 294` 已在 `2026-04-02 14:21 UTC` 完成 fresh intake 首判并进入 survivor 槽位；这是当前唯一合法前排动作。
- 当前没有明确 `Active P2`；最近一次 active P2 出口仍是 `Rank 285` 的 `one-time P2->P1 re-scope`，之后没有新的 admission 对象升入 active 槽位。
- 最近新出现的未首判对象里，最新的是 `2026-04-02_1625_topn-reversal-pumpveto-confidence-alpha.md`；它只能排在 `Rank 294` survivor follow-up 之后，不能越过当前 survivor 锁。

## 本轮只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- 否，当前为空。
- `current_target = none`，queue 头没有待接线对象。
- 因此本轮没有 `P3 handoff / launch wiring` 优先动作。

### 2) 本轮 `fresh intake` 是什么？
- 严格按当前前排顺序，本轮第一动作不是 fresh intake，而是 `Rank 294` 的 survivor follow-up。
- 在 survivor 已被诚实排入前部后，本轮第一条 fresh intake 应是：
  - `research/quant_digests/2026-04-02_1625_topn-reversal-pumpveto-confidence-alpha.md`
- 原因：它是目前最近的新 alpha 报告，而且当前没有 `P3/P2` 动作可排在它前面；但它也不能覆盖 `Rank 294` 的 survivor 锁。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得。
- 上一条 fresh intake 是：
  - `Rank 294 / Coinbase premium impulse × EMA trend alignment × 60m hold`
- `2026-04-02_1421_rank294_coinbase_premium_impulse_keep_p1.md` 已经把唯一 cheap decisive follow-up 定义得很清楚：
  - 直接回答它是否只靠近 `30d` 样本和窄参数点位撑住；
  - 至少检查 `CPDiff_Zscore` 阈值、EMA 对齐窗口、hold 时长的小邻域，以及相邻时间切片是否仍保留成本后同向 edge。
- 因此它值得占用 survivor 唯一 follow-up；在这个问题没回答前，新的 fresh intake 依法不能排到它前面。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`。
- 最近一个 active P2 是 `Rank 285`，但它已完成出口裁决并转到一次性 `P1 re-scope` 路径，所以现在 `Active P2 = none`。
- 因而本轮不存在仍需在 `P3 / P1 / P0` 三出口间继续裁决的 active 对象。

## Rank 完整性检查
- `Paper launch queue`: `none`，无 rank 缺口。
- `Surviving candidate slot`: `Rank 294`，已有正式 rank。
- `Active P2 slot`: `none`。
- 当前前排对象不存在“达到 `keep_P1 / P2 / P3` 但无正式 rank”的情况，因此本轮无需补新 rank。

## 本轮排班判断
按 policy 默认顺序：`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0归档`。

当前真实顺序应为：
1. 没有 `P3` queue 头待接线；
2. 没有 `Active P2`；
3. 有且只有一个合法前排动作：`Rank 294` survivor 唯一一次参数邻域 / 时间稳定性 follow-up；
4. 只有它收口后，才能切回新的 fresh intake；
5. 因此本轮以 5 项预算重写为：
   1. `Rank 294` survivor follow-up
   2. `2026-04-02_1625_topn-reversal-pumpveto-confidence-alpha.md`
   3. `2026-04-02_1250_liquidity-risk-interaction-xs-alpha.md`
   4. `2026-04-02_1124_pca-eigenportfolio-residual-statarb-alpha.md`
   5. `2026-04-02_1140_extreme-ofi-tradeflow-continuation-alpha.md`

这里没有把 `Paper launch queue = none` 或 `Active P2 = none` 单独写成 cycle item，因为 policy 明确这类空槽确认属于隐式护栏，不占默认轮次。

## 对 `BOT2_BOT3_STATE.md` 的实际写回
本轮仅更新 `BOT2_BOT3_STATE.md`，没有改动 policy / brief / operating card / cron prompt。

实际写回内容：
- 保持 `Paper launch queue` 不变：仍为空；已接线运行对象不变。
- 保持 `Active P2 slot = none` 不变。
- 保持 `Rank 294` 为当前 survivor，不新增 rank。
- 重写 `cycle_plan`，把当前合法优先级恢复为：
  1. `Rank 294` survivor follow-up
  2. `2026-04-02_1625_topn-reversal-pumpveto-confidence-alpha.md`
  3. `2026-04-02_1250_liquidity-risk-interaction-xs-alpha.md`
  4. `2026-04-02_1124_pca-eigenportfolio-residual-statarb-alpha.md`
  5. `2026-04-02_1140_extreme-ofi-tradeflow-continuation-alpha.md`
- 所有新生成项均按要求写成 `target / action / success_criterion / result / status`，且 `result = none`、`status = pending`。
- 没有把 background pool 旧候选拉回前排。

## 结论
- `Paper launch queue`：空
- 本轮 `fresh intake`：在 `Rank 294` survivor 之后，首个 fresh intake 为 `2026-04-02_1625_topn-reversal-pumpveto-confidence-alpha.md`
- 上一条 fresh intake 是否值得唯一 follow-up：值得，而且当前就该先做
- 当前明确 `Active P2`：无
- 本轮不需要补 rank
- 本轮需要改写 state：需要，且已完成；原因是当前唯一前排动作仍是 `Rank 294` 的 survivor follow-up，而最新 `fresh intake` 只能诚实排在它之后
