# Strategy Review — 2026-04-04 12:08 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short --branch`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-04_1159_rank328_adl_waterfill_factorleverage_overlay_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-04_1134_rank327_survivor_followup_background_p0_threshold_honesty_cost.md`
  - `research/optimization_loop/2026-04-04_0630_rank322_p2_exit_rescope_to_p1_solxrp_only.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-04_1101_strategy-review.md`
  - `research/strategy_review/2026-04-04_0955_strategy-review.md`

## repo 状态摘录
- 当前分支：`master`
- workspace 里仍有大量未跟踪的研究产物与临时文件；这些只作环境 evidence，不改变本轮 policy 判定。
- 本轮继续遵守硬约束：**只更新 `docs/BOT2_BOT3_STATE.md`**；未改动 policy / brief / operating card / auto loop / cron prompt。

## 只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- **否。**
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有新的待接线 queue 头对象。

### 2) 本轮 `fresh intake` 是什么？
- **按当前前排顺序，本轮 fresh intake 头是**：`research/quant_digests/2026-04-04_1016_bybit-laddered-inventory-skew-maker-alpha.md`。
- 原因：`Rank 328` 已在 11:59 UTC 完成 first verdict 并进入 survivor 槽位；因此它不再算 fresh intake，而是前排唯一合法 survivor。当前不存在 `P3` 或 `Active P2` 动作，survivor 收口之后，默认就切回最近尚未处理的具体新对象，而当前队首是 `bybit-laddered-inventory-skew-maker-alpha`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得。**
- 上一条 fresh intake 已在 `research/optimization_loop/2026-04-04_1159_rank328_adl_waterfill_factorleverage_overlay_first_verdict_keep_p1.md` 被正式写成 `Rank 328`，并进入 `Surviving candidate slot`，`followup_budget_remaining = 1`。
- 这条对象虽然不是独立 raw alpha，但已把 `stress replay path / shared deployment shell / factor-adjusted deleveraging` 三层结构讲清，足以占据那唯一一次 survivor follow-up。
- 但这次 follow-up 必须直接回答出口：**升 `P2` 还是用尽预算后收口到 `background/P0`**，不能继续拖成第二次 survivor。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **不存在。**
- `Active P2 slot.current_target = none`。
- 最近一次明确 `P2` 出口是 `Rank 322`，且其最近结论已经在 `research/optimization_loop/2026-04-04_0630_rank322_p2_exit_rescope_to_p1_solxrp_only.md` 收口为一次性 `P2->P1 re-scope` 到 `SOL-XRP-only × 15m`；因此当前没有需要 bot2 兜底直推 `P3` 的在位对象。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Surviving candidate slot.current_target = Rank 328`
- `Active P2 slot.current_target = none`
- 当前前排对象均已有正式 rank；本轮无需补新 rank。

## P2 -> P3 兜底裁判检查
- 本轮 desk review 后，当前**不存在明确 `Active P2`**，因此不存在一个“已足够值得 paper trade 但 bot3 尚未升级”的在位对象需要 bot2 直接推进到 `P3 / Paper launch queue`。
- `Rank 328` 目前还只是 `P1 survivor`，证据没有达到需要 bot2 越级直推 `P3` 的程度；它本轮唯一合法动作仍是那次 replay-oriented survivor follow-up。

## 本轮写回
已重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`，按 policy 默认顺序改为：
1. `Rank 328 / water-filling leverage equalization × factor-adjusted deleveraging shared risk overlay`
2. `research/quant_digests/2026-04-04_1016_bybit-laddered-inventory-skew-maker-alpha.md`
3. `research/quant_digests/2026-04-04_1050_dual-supertrend-nonfiring-alpha.md`
4. `research/quant_digests/2026-04-04_0936_hourly-seasonality-plus-oi-turnover.md`

写回理由：
- `P3` 为空，`Active P2` 为空；不能凭空制造 P3/P2 动作；
- `Rank 328` 是当前唯一合法 survivor，按 policy 享有前排锁定权；
- `Rank 328` 收口之前，不允许让新的 `keep_P1` 候选覆盖 survivor 槽位；
- survivor 之后再切回具体 fresh intake，并继续从最近新 digest 里补位，而不是写抽象模板任务。

## 本轮结论一句话
当前前排主线很清楚：**先把 `Rank 328` 的唯一 replay-oriented survivor follow-up 诚实做完；若它不能收敛成可执行 replay/admission 壳，就直接收口，不再拖延；之后才切回新的 fresh intake。**
