# 2026-04-12 18:40 UTC strategy review（bot2）

## 读取顺序（按约束）
1. `docs/BOT2_BOT3_POLICY.md`
2. `docs/BOT2_BOT3_STATE.md`
3. repo / 最近记录：`git status --short`、最近 `research/optimization_loop/`、最近 `research/strategy_review/`

## 本轮只答 4 个问题
1. `Paper launch queue` 是否非空？
- **是，非空。** 当前目标仍为 `Rank 389 / cross-venue net-carry ranking alpha`，且已在 `connected_runner_live`。

2. 本轮 `fresh intake` 是什么？
- 本轮切换为：`distance-first intraday pairs spread z-score fade`（来源：`research/quant_digests/2026-04-12_1738_distancefirst-intraday-pairs-alpha.md`）。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **不值得。** 上一条 fresh intake `mm-live OFI fair-value 偏离（maker-first）` 已 first verdict 直接收口为 `background/P0`，未形成 `keep_P1`，因此不存在 survivor 唯一 follow-up。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **存在。** 当前 `Active P2 = Rank 391 / BTC dominance slope × strongest/weakest alt switch`。
- 结合最近证据（低成本区间费后仍正、6h 调仓容量可控），该对象当前**离 `P3` 最近**；但仍需完成本轮 admission 主结论（`effectiveness + cross-asset + time` 同口径快检 + 最小 honesty/execution realism）后给出明确出口。

## Rank 合规检查
- 前排对象均有正式 rank：`Paper launch queue: Rank 389`、`Active P2: Rank 391`。
- 无需补发新 Rank。

## 本轮改写（仅 state）
已更新 `docs/BOT2_BOT3_STATE.md`：
1. `Fresh intake slot`
   - `status -> pending`
   - `current_target -> distance-first intraday pairs spread z-score fade`
   - `source_record -> 2026-04-12_1738_distancefirst-intraday-pairs-alpha.md`
2. `cycle_plan` 重写为 4 项（均 `result: none`、`status: pending`）并遵循默认顺序：
   - #1 `Active P2`：`Rank 391` admission 主结论轮（含最小 honesty/execution realism）
   - #2 fresh intake：distance-first intraday pairs first verdict
   - #3 fresh intake：sign-aware XS momentum first verdict
   - #4 conditional fresh intake：仅在前 3 项收口后，从 `park_reframe` 取 1 条新对象做 first verdict

## P2->P3 兜底裁判判断
- 本轮未直接把 `Rank 391` 强制写入 `P3 / Paper launch queue`：当前证据显示其接近 `P3`，但尚未完成本轮 admission 主结论所需的三轴同口径收口；先把该动作放在 `cycle_plan #1` 并要求直接给出口结论，避免继续开放式拖延。

## 约束符合性
- 未改 policy / brief / operating card / auto loop / cron prompt。
- 未新增运行槽位。
- 未将 background pool 旧候选自动拉回前排。
- `TODO.md` 未作为排班依据。