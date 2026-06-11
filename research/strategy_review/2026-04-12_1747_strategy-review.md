# 2026-04-12 17:47 UTC strategy review（bot2）

## 读取顺序（按约束）
1. `docs/BOT2_BOT3_POLICY.md`
2. `docs/BOT2_BOT3_STATE.md`
3. repo / 最近记录：`git status --short --branch`、最近 `research/optimization_loop/`、最近 `research/strategy_review/`

## 本轮只答 4 个问题
1. `Paper launch queue` 是否非空？
- **是，非空**。当前为 `Rank 389 / cross-venue net-carry ranking alpha`，且已写入 `connected_runner_live`（runner + scheduler + first verified run 已完成）。

2. 本轮 `fresh intake` 是什么？
- 当前 fresh intake 槽位是：`research/quant_digests/2026-04-12_1352_mm-live-ofi-fairvalue-maker-alpha.md`（`mm-live OFI fair-value 偏离（maker-first）`）。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得**。上一条 fresh intake `Rank 391` 已首判 `keep_P1` 且进入 survivor；按 policy 其唯一 follow-up 预算尚未消费（`followup_budget_remaining: 1`），应优先执行，不得被新的 intake 覆盖。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **不存在**。`Active P2 slot = none`，因此本轮不存在 `P2 -> P3/P1/P0` 出口距离判断对象。

## rank 合规检查
- 前排对象 rank 合规：`Paper launch queue = Rank 389`，`Surviving candidate = Rank 391`。
- 未发现 `Surviving candidate / Active P2 / Paper launch queue` 无 rank 违规；无需补发新 rank。

## 本轮排班重写（按默认顺序）
- `P3`：当前 queue 对象已 `connected_runner_live`，无新增 wiring 动作。
- `P2`：当前无 active P2。
- `P1 survivor`：`Rank 391` 仍有唯一 follow-up 未执行，置于本轮第 1 优先级。
- 在前排收口动作已前置后，再补 fresh intake。

已将 `cycle_plan` 重写为 4 项（均 `result: none`、`status: pending`）：
1. `Rank 391` survivor 唯一 follow-up，直接输出 `promote_P2` 或 `drop_to_background/P0`
2. `mm-live-ofi-fairvalue-maker-alpha` fresh intake first-verdict
3. `distancefirst-intraday-pairs-alpha` fresh intake first-verdict
4. `signaware-xsmomentum-atrvolume-alpha` fresh intake first-verdict

## 状态文件改写
- 已更新：`docs/BOT2_BOT3_STATE.md`（仅 `cycle_plan`）
- 未改动：policy / brief / operating card / auto loop / cron prompt
- 未触发 background pool 自动 reopen
