# Strategy Review — 2026-04-04 09:55 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-04_0952_engle_pairs_walkforward_first_verdict_background_p0.md`
  - `research/optimization_loop/2026-04-04_0933_signed_hourpair_lagmap_first_verdict_background_p0.md`
  - `research/optimization_loop/2026-04-04_0920_rank326_signed_flow_imbalance_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-04_0630_rank322_p2_exit_rescope_to_p1_solxrp_only.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-04_0858_strategy-review.md`
  - `research/strategy_review/2026-04-04_0733_strategy-review.md`
- 最新候选 digest：
  - `research/quant_digests/2026-04-04_0905_frost-asian-ma-deviation-fade-alpha.md`
  - `research/quant_digests/2026-04-04_0947_adl-waterfill-factorleverage-overlay.md`
  - `research/quant_digests/2026-04-04_0620_par-prediction-line-cross-alpha.md`

## repo 状态摘录
- repo 仍有大量未跟踪研究产物、脚本与临时文件；这些只作环境 evidence，不改变本轮 policy 判定。
- 本轮继续遵守硬约束：**只更新 `docs/BOT2_BOT3_STATE.md`**；未改动 policy / brief / operating card / auto loop / cron prompt。

## 只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- **否。**
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有新的待接线 queue 头对象。

### 2) 本轮 `fresh intake` 是什么？
- **严格按 policy，本轮前排真实动作先不是 fresh intake，而是 survivor 收口。**
- 当前唯一前排合法动作是：`Rank 326 / signed flow imbalance × maker-only conviction gate` 的唯一一次 survivor follow-up。
- 在这条 survivor 被诚实排入并等待 bot3 依次执行之后，**当前轮 fresh intake 头** 才是：`research/quant_digests/2026-04-04_0905_frost-asian-ma-deviation-fade-alpha.md`。
- 理由：已有 survivor 槽位占用，fresh intake 不得越过它；而在最近新 digest 里，`09:05` 的 Frost 单币均值回复壳比 `09:47` 的 overlay 和 `06:20` 的 PAR trend 家族更像应优先做的独立 raw alpha intake。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得。**
- 上一条 fresh intake 已在 `2026-04-04_0920_rank326_signed_flow_imbalance_first_verdict_keep_p1.md` 被正式写成 `Rank 326`，并进入 `Surviving candidate slot`，`followup_budget_remaining = 1`。
- 其 first verdict 已说明：对象已经把 `1m signed trade imbalance -> 5m forward return`、`nonlinear conviction gate` 与 `maker-only execution economics` 三层分账讲清，形成了最小 `1m/5m` microstructure desk shell；因此它合法占有那唯一一次 survivor follow-up。
- 但这次 follow-up 必须直接回答出口：**升 `P2` 还是用尽预算后收口到 `background/P0`**，不能继续拖成第二次 survivor。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **不存在。**
- `Rank 322` 的 P2 exit 已在 `2026-04-04_0630_rank322_p2_exit_rescope_to_p1_solxrp_only.md` 收口：原先 `BTC-XRP / SOL-XRP × 15m` 双 lane 在更长样本与 honesty 重检后，只剩 `SOL-XRP` 单 lane 勉强保留，因此对象不升 `P3`，也不直接打回 `P0`，而是一次性 `P2->P1 re-scope` 到 `SOL-XRP-only × 15m`，并释放 `Active P2 slot`。
- 所以当前不存在需要 bot2 兜底推进到 `P3` 的在位 P2；最近一次明确出口落点是 **`P1`**。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Surviving candidate slot.current_target = Rank 326`
- `Active P2 slot.current_target = none`
- 前排对象均已有正式 rank；本轮无需补新 rank。

## P2 -> P3 兜底裁判检查
- 本轮 desk review 后，当前**不存在明确 `Active P2`**，因此也不存在一个“已足够值得 paper trade 但 bot3 尚未升级”的在位对象需要 bot2 直接推进到 `P3 / Paper launch queue`。
- `Rank 322` 的出口已被最新 evidence 诚实收口为一次性 `P2->P1 re-scope`，本轮不得越证据把它改写成 `P3`。

## 本轮排班改写
按 policy 默认顺序扫描：
1. `P3`：无待接线对象
2. `P2`：无明确 `Active P2`
3. `P1`：有且仅有 `Rank 326` survivor follow-up，必须排第 1
4. `fresh intake`：只能排在 survivor 之后

因此本轮将 `cycle_plan` 重写为 4 项：
1. `Rank 326 / signed flow imbalance × maker-only conviction gate` survivor follow-up
2. `2026-04-04_0905_frost-asian-ma-deviation-fade-alpha.md`
3. `2026-04-04_0947_adl-waterfill-factorleverage-overlay.md`
4. `2026-04-04_0620_par-prediction-line-cross-alpha.md`

改写理由：
- `Rank 326` 是当前唯一合法 survivor，按 policy 拥有前排锁定权，不能被新的 intake 覆盖；
- `Paper launch queue` 与 `Active P2` 都为空，不应凭空制造 P3/P2 动作；
- `Rank 322` 虽定义了 `SOL-XRP-only × 15m` 的一次性 re-scope，但当前不在 survivor / active P2 合法槽位，且 policy 不允许把它自动拉回前排默认主线；
- 在 fresh intake 候选里，Frost 单币 MA deviation fade 先于 ADL overlay 和 PAR trend family，被排为新的 intake 头；
- 新 `cycle_plan` 全部写成具体对象，且结果均重置为 `none`、状态均为 `pending`。

## 本轮写回
- 已更新：`docs/BOT2_BOT3_STATE.md`
- 本轮只改写 runtime state；未改动 policy / brief / operating card / auto loop / cron prompt。
