# 2026-04-12 15:40 UTC strategy review（bot2）

## 读取顺序（按约束）
1. `docs/BOT2_BOT3_POLICY.md`
2. `docs/BOT2_BOT3_STATE.md`
3. repo / 最近记录：`git status --short`、最近 `research/optimization_loop/`、最近 `research/strategy_review/`

## 本轮只答 4 个问题
1. `Paper launch queue` 是否非空？
- **是，非空**。`Rank 389 / cross-venue net-carry ranking alpha` 仍在 queue，且已写明 `connected_runner_live`（wiring 已完成）。

2. 本轮 `fresh intake` 是什么？
- 当前 state 里的 fresh intake 结论对象是 `Rank 390 / passivbot EMA forager bounce`（已完成 first-verdict 并首判 `keep_P1`）。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得**。`Rank 390` 已进入 `Surviving candidate slot`，且 `followup_budget_remaining = 1`；本轮应优先消耗这唯一一次 follow-up 做收口。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **当前不存在明确 `Active P2`**（`none`）。

## rank 合规检查
- 前排对象均有正式 rank：`Paper launch queue`=Rank 389，`Surviving candidate`=Rank 390。
- 未发现“前排对象达到 keep_P1/P2/P3 但无 rank”的违规；本轮无需补号。

## 本轮排班重写（按 policy 默认顺序）
按 `P3 > P2 > P1 > fresh intake > P0` 扫描后，当前可执行前排动作为 `P1 survivor 收口`（`P3` 无待接线动作、`P2` 空槽），因此重写为：
1. Rank 390 survivor 唯一 follow-up（maker fill honesty haircut + slippage stress），并强制二选一收口 `promote_P2` / `background/P0`
2. 若步骤1升入 P2，则同轮执行 Rank 390 的 `P2 exit decision`（三选一：`P3 / one-time P2->P1 re-scope / P0`）
3. fresh intake：`btc-dominance-slope-rotation-alpha`
4. conditional fresh intake：`Rank 89 soft_reframe_candidate`（single-axis + distinctness 快检）

以上 4 项均已写成 `result: none`、`status: pending`。

## 状态文件改写
- 已更新：`docs/BOT2_BOT3_STATE.md`（仅 runtime state / cycle_plan）
- 未改动：policy / brief / operating card / auto loop / cron prompt
- 未执行 background pool 自动 reopen
