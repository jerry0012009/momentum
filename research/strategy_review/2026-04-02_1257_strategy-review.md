# Strategy Review — 2026-04-02 12:57 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并已复核当前 repo/runtime 与最近证据：
- `git status --short`
- `research/optimization_loop/2026-04-02_1255_rank293_ivspike_creditspread_keep_p1.md`
- `research/optimization_loop/2026-04-02_1204_rank292_survivor_followup_background_p0_increment_not_shown.md`
- `research/optimization_loop/2026-04-02_1102_rank292_crossasset_integrated_ofi_keep_p1.md`
- `research/strategy_review/2026-04-02_1200_strategy-review.md`
- `research/quant_digests/2026-04-02_1124_pca-eigenportfolio-residual-statarb-alpha.md`
- `research/quant_digests/2026-04-02_1140_extreme-ofi-tradeflow-continuation-alpha.md`
- `research/quant_digests/2026-04-02_1007_pressure-ratio-capitulation-fade-alpha.md`

## Repo / runtime quick check
- repo 当前没有新的已写回 runtime 结论会改变前排判断；`git status` 仍主要是未跟踪研究产物，不构成新的运行态优先级。
- `Paper launch queue` 当前仍为 `current_target = none`；已接线运行的仍是 `Rank 200 / 201 / 213 / 229`。
- 当前没有明确 `Active P2`；最近一次 active P2 出口裁决仍是 `Rank 285` 的 `one-time P2->P1 re-scope`，之后没有新的 admission 对象进入 active 槽位。
- 当前真正占前排的是 `Rank 293` survivor；`Rank 292` 已于 `2026-04-02 12:04 UTC` 用完唯一 follow-up 并回 `background/P0`。

## 本轮只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- 否，当前为空。
- `current_target = none`，queue 头没有待接线对象。
- 因此本轮没有 `P3 handoff / launch wiring` 优先动作。

### 2) 本轮 `fresh intake` 是什么？
- 严格按当前前排顺序，本轮第一动作不是 fresh intake，而是 `Rank 293` 的 survivor follow-up。
- 在 survivor 已被诚实排入并等待 bot3 执行后，本轮第一条 fresh intake 应是：
  - `research/quant_digests/2026-04-02_1124_pca-eigenportfolio-residual-statarb-alpha.md`
- 原因：它是最近尚未首判、且具备完整 raw-alpha 母体、明确 desk transfer 与最小 cost-aware clean-room path 的具体新对象；同时当前没有 `P3/P2` 动作可排在它前面。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得。
- 上一条 fresh intake 就是当前 survivor：
  - `Rank 293 / near-expiry IV spike × 1m liquidity sweep -> short vertical credit spread`
- `2026-04-02_1255_rank293_ivspike_creditspread_keep_p1.md` 已把唯一 cheap decisive follow-up 定义得很清楚：
  - 不是继续泛讲 0DTE theta / IV spike 故事；
  - 而是直接回答在连续 near-expiry chain 样本下，扣除双腿 half-spread + taker fee + 现实成交惩罚后，这条 short vertical credit spread 是否仍有正净期望。
- 因此它值得占用 survivor 唯一 follow-up；在这个问题没回答前，新的 fresh intake 依法不能排到它前面。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`。
- 最近一个 active P2 是 `Rank 285`，但它已完成出口裁决并转回一次性 `P1 re-scope` 路径，所以现在 `Active P2 = none`。
- 因而本轮不存在仍需在 `P3 / P1 / P0` 三出口间继续裁决的 active 对象。

## Rank 完整性检查
- `Paper launch queue`: `none`，无 rank 缺口。
- `Surviving candidate slot`: `Rank 293`，已有正式 rank。
- `Active P2 slot`: `none`。
- 当前前排对象不存在“达到 `keep_P1 / P2 / P3` 但无正式 rank”的情况，因此本轮无需补新 rank。

## 本轮排班判断
按 policy 默认顺序：`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0归档`。

当前真实顺序应为：
1. 没有 `P3` queue 头待接线；
2. 没有 `Active P2`；
3. 有且只有一个合法前排动作：`Rank 293` survivor 唯一一次成本后存在性 follow-up；
4. 只有它收口后，才能切回新的 fresh intake；
5. 因此本轮以 4 项预算重写为：
   1. `Rank 293` survivor follow-up
   2. `pca-eigenportfolio-residual-statarb` fresh intake
   3. `extreme-ofi-tradeflow-continuation` fresh intake
   4. `pressure-ratio-capitulation-fade` 条件式 fresh intake

这里没有把 `Paper launch queue = none` 或 `Active P2 = none` 单独写成 cycle item，因为 policy 明确这类空槽确认属于隐式护栏，不占默认轮次。

## 对 `BOT2_BOT3_STATE.md` 的实际写回
本轮仅更新 `BOT2_BOT3_STATE.md`，没有改动 policy / brief / operating card / cron prompt。

实际写回内容：
- 重写 `cycle_plan`，把当前合法优先级恢复为：
  1. `Rank 293` survivor follow-up
  2. `2026-04-02_1124_pca-eigenportfolio-residual-statarb-alpha.md`
  3. `2026-04-02_1140_extreme-ofi-tradeflow-continuation-alpha.md`
  4. `2026-04-02_1007_pressure-ratio-capitulation-fade-alpha.md`
- 没有新增/改写任何 policy 层内容。
- 没有把 background pool 旧候选拉回前排。

## 结论
- `Paper launch queue`：空
- 本轮 `fresh intake`：在 `Rank 293` survivor 之后，首个 fresh intake 为 `pca-eigenportfolio-residual-statarb`
- 上一条 fresh intake 是否值得唯一 follow-up：值得，而且已占用 survivor 锁
- 当前明确 `Active P2`：无
- 本轮不需要补 rank
- 本轮需要改写 state：需要，且已完成；原因是前排应先收口 `Rank 293`，再切 fresh intake，且需要把更具体、最近的新对象按 policy 顺序写回 `cycle_plan`
