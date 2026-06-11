# 2026-04-12 20:38 UTC strategy review（bot2）

## 读取顺序（按约束）
1. `docs/BOT2_BOT3_POLICY.md`
2. `docs/BOT2_BOT3_STATE.md`
3. repo / 最近记录：`git status --short`、最近 `research/optimization_loop/`、最近 `research/strategy_review/`

## 本轮只答 4 个问题
1. `Paper launch queue` 是否非空？
- **是，非空。** 当前仍有 `Rank 389 / cross-venue net-carry ranking alpha`，并已处于 `connected_runner_live`。

2. 本轮 `fresh intake` 是什么？
- 本轮 fresh intake 主对象为：`research/park_reframe/2026-04-10_0611_rank89-park-reframe.md`（`Rank 89 / back-inside-bar anchored failure-followthrough`）。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得。** 上一条 fresh intake（`Rank 74`）已 first verdict=`keep_P1`，且 blocker 明确为“样本过薄”，符合 survivor 唯一 follow-up 的使用条件。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **不存在。** 当前 `Active P2 = none`（`Rank 391` 已在上一轮完成出口决策并 `drop_to_background`）。

## Rank 合规检查
- 前排对象均有正式 rank：`Rank 389`（P3 queue）、`Rank 74`（survivor）、`Rank 89`（fresh intake）。
- 本轮无需补发新 `Rank`。

## 本轮排班与 state 改写
已按 policy 默认优先级重写 `cycle_plan`（4 项，全部 `result: none` / `status: pending`）：
1. `Rank 74` survivor 唯一 follow-up（必须二选一收口：`promote_P2` 或 `drop_to_background`）
2. `Rank 89` fresh intake first-verdict
3. `Rank 71` fresh intake（在前两项诚实收口后）
4. `Rank 28` conditional fresh intake（仅在前排链条已收口且预算有余）

## P2 -> P3 兜底裁判判断
- 本轮无 `Active P2`，不存在“bot3 未升但应强制升 P3”的对象。
- `P3` 侧当前无待接线对象（`Rank 389` 已 `connected_runner_live`），因此本轮资源优先转向 survivor 收口与 fresh intake。

## 约束符合性
- 仅更新 `BOT2_BOT3_STATE.md`。
- 未改写 policy / brief / operating card / auto loop / cron prompt。
- 未把 background pool 旧候选自动拉回前排。
- `TODO.md` 未作为排班依据。