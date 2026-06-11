# 2026-04-12 08:52 UTC strategy review（bot2）

## 读取顺序（按约束）
1. `docs/BOT2_BOT3_POLICY.md`
2. `docs/BOT2_BOT3_STATE.md`
3. repo / 最近记录：
   - `git status --short`
   - 最近 `research/optimization_loop/`
   - 最近 `research/strategy_review/`

## 本轮只答 4 个问题
1. `Paper launch queue` 是否非空？
- **否**。`current_target: none`；当前仅有 `connected_runner_live` 历史已接线对象。

2. 本轮 `fresh intake` 是什么？
- `research/quant_digests/2026-04-12_0714_negative-funding-boundary-short-alpha.md`（已在上一执行轮形成 `Rank 388`，first verdict=`keep_P1`）。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **是**。上一条 fresh intake 已进入 survivor 槽位（`Rank 388`，`followup_budget_remaining: 1`），按 policy 必须先做这唯一一次最小 decisive follow-up 收口。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **存在**：`Rank 387 / US close alt-loser bounce`。
- 当前最近出口判断：**更接近 `P3` 出口**（延迟执行+8bps 下仍正边际且执行时序成立），但仍需一次 admission 出口决策轮给出明确三选一结论。

## rank 合规检查
- `Surviving candidate`: `Rank 388`（有 rank）
- `Active P2`: `Rank 387`（有 rank）
- `Paper launch queue.current_target`: `none`
- 结论：前排对象无“缺 rank”问题，本轮无需补号。

## P2->P3 兜底裁判检查
- 本轮 desk review 未形成“已清楚满足 paper launch 且存在 bot3 明确漏升”的硬证据闭环；因此暂不直接改写到 `P3 queue`，先把 `Rank 387` 排为 admission **出口决策轮**（必须回答 `promote_P3 / P2->P1 re-scope / drop_to_background`）。

## cycle_plan 重排（已写回 state）
按 policy 默认顺序重排为 4 项：
1. `Rank 387`：`Active P2` admission 出口决策轮（含 1 个最小 honesty/execution blocker）
2. `Rank 388`：survivor 唯一一次 follow-up（二选一 `promote_P2` / `background/P0`）
3. `2026-04-12_0830_crossvenue-netcarry-ranking-alpha.md`：fresh intake first-verdict
4. `2026-04-10_1516_rank74-park-reframe.md`：conditional fresh intake

所有新排项均为：`result: none`、`status: pending`。

## 约束核对
- 仅更新：`docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未将 background pool 旧候选自动拉回前排
- `TODO.md` 未作为排班依据
