# 2026-04-12 13:21 UTC strategy review（bot2）

## 读取顺序（按约束）
1. `docs/BOT2_BOT3_POLICY.md`
2. `docs/BOT2_BOT3_STATE.md`
3. repo / 最近记录：`git status --short`、最近 `research/optimization_loop/`、最近 `research/strategy_review/`

## 本轮只答 4 个问题
1. `Paper launch queue` 是否非空？
- **是**。本轮已改写为：`current_target = Rank 389 / cross-venue net-carry ranking alpha`。

2. 本轮 `fresh intake` 是什么？
- `research/quant_digests/2026-04-12_1217_passivbot-ema-forager-bounce-alpha.md`。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得且已执行完成**。上一条 fresh intake（`Rank 389`）的 survivor 唯一 follow-up 已在 `2026-04-12_1315_rank389_survivor_followup_promote_p2.md` 完成，并给出正向结果。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **当前不存在 Active P2**（已置为 `none`）。
- 原 Active P2（`Rank 389`）在 desk review 证据下已满足 `P2 -> P3` 门槛：`collector_receive_ts` 同窗护栏通过、成本后 `edge_after_cost_apr ≈ +0.0104` 仍为正、无单一 decisive honesty/execution blocker，因此由 bot2 兜底裁判直接升级进 `P3 / Paper launch queue`，不再继续开放式 P2 研究。

## rank 合规检查
- `Paper launch queue` 当前目标有正式 rank（`Rank 389`）。
- `Fresh intake` 当前对象为 digest 路径，不涉及缺 rank 前排对象。
- `Surviving candidate` 当前为 `none`（预算 0）。
- `Active P2` 当前为 `none`。
- 结论：无“前排对象已达 keep_P1/P2/P3 但无正式 rank”违规，无需补号。

## cycle_plan 重排（按 policy 默认优先级）
已按 `P3 launch wiring > P2 > P1 > fresh intake > P0` 重写：
1. `Rank 389` P3 wiring：dedicated runner 落库并可产出标准 artifact
2. `Rank 389` P3 wiring：scheduler 启用 + first verified run + 回写 `connected_runner_live`
3. `passivbot-ema-forager-bounce-alpha` fresh intake first-verdict
4. `btc-dominance-slope-rotation-alpha` fresh intake first-verdict

新生成项均为 `result = none`、`status = pending`。

## 本轮状态改写
- 已更新：`docs/BOT2_BOT3_STATE.md`
- 未改动：policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排
