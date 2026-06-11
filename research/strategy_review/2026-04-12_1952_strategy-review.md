# 2026-04-12 19:52 UTC strategy review（bot2）

## 读取顺序（按约束）
1. `docs/BOT2_BOT3_POLICY.md`
2. `docs/BOT2_BOT3_STATE.md`
3. repo / 最近记录：`git status --short`、最近 `research/optimization_loop/`、最近 `research/strategy_review/`

## 本轮只答 4 个问题
1. `Paper launch queue` 是否非空？
- **是，非空。** 当前 `current_target` 为 `Rank 389 / cross-venue net-carry ranking alpha`，且已在 `connected_runner_live`，最近记录显示 wiring 已完成且 first verified run 已落地。

2. 本轮 `fresh intake` 是什么？
- 本轮 fresh intake 指定为：`Rank 74 soft_reframe_candidate / Fib-family-local ER-only veto-admission residual`（来源：`research/park_reframe/2026-04-10_1516_rank74-park-reframe.md`）。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **不值得。** 上一条 fresh intake（`sign-aware XS momentum × ATR/volume gate`）first verdict 已是 `background/P0`，不存在 `keep_P1`，因此不进入 survivor 唯一 follow-up。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **存在。** `Active P2 = Rank 391 / BTC dominance slope × strongest/weakest alt switch`。
- 依据最新 admission 记录（`2026-04-12_1854...keep_p2_cost_threshold_blocker.md`），其唯一 blocker 为 `1.5bps one-way` 成本阈值鲁棒性未过；当前最接近的出口是 **`P0` 或 `P3` 的二元出口决策**（取决于该 blocker 是否被最小复核推翻），而不是继续开放式 `keep_P2`。

## Rank 合规检查
- 前排对象均已有正式 rank（`Rank 389`、`Rank 391`）。
- 无需补发新 Rank。

## 本轮 state 改写
已更新 `docs/BOT2_BOT3_STATE.md`：
1. `Fresh intake slot.current_target` 改为具体对象 `Rank 74 soft_reframe_candidate`，并把 `source_record` 收紧到对应 park_reframe 文件。
2. 按 policy 默认优先级重写 `cycle_plan`（4 项、全部 `result: none` + `status: pending`）：
   - #1 `Active P2`：`Rank 391` 出口决策轮（聚焦唯一 blocker，禁止同轴重复开放补证）
   - #2 fresh intake：`Rank 74` first verdict
   - #3 fresh intake：`Rank 89` first verdict
   - #4 conditional fresh intake：`Rank 71` first verdict（仅在前 3 项诚实收口后执行）

## P2->P3 兜底裁判判断
- 本轮**未**直接把 `Rank 391` 写入 `P3`：现有证据尚未满足“足够值得立即 paper launch 且无 decisive execution blocker”，并已锁定单一 blocker（成本阈值鲁棒性）。
- 因此按 policy 将下一步强制设为 **出口决策轮**，要求直接在 `promote_P3 / drop_to_background / one-time P2->P1 re-scope` 三选一中收口，不允许继续开放式研究。

## 约束符合性
- 仅更新 `BOT2_BOT3_STATE.md`。
- 未改 policy / brief / operating card / auto loop / cron prompt。
- 未新增运行槽位，未把 background pool 旧候选自动拉回前排。
- `TODO.md` 未作为本轮排班依据。
