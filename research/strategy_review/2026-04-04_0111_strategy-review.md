# Strategy Review — 2026-04-04 01:11 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-04_0101_rank320_wilder_rsi_fast_exit_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-04_0030_rank319_dc_vwap_ema_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-03_1940_rank314_p2_exit_background_p0.md`
  - `research/optimization_loop/2026-04-03_2353_poc_valuearea_fill_first_verdict_background_p0.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-04_0007_strategy-review.md`

## 只回答 4 个问题

1) `Paper launch queue` 是否非空？
- 否。
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有新的待接线 queue 头对象。

2) 本轮 `fresh intake` 是什么？
- 当前 fresh intake 是：
  - `research/quant_digests/2026-04-03_2141_wilder-rsi-fast-exit-trend-shell-alpha.md`
- 依据：
  - `Rank 319` 已在 `research/optimization_loop/2026-04-04_0030_rank319_dc_vwap_ema_first_verdict_keep_p1.md` 完成 first verdict，并不是当前 fresh intake，而是上一条 fresh intake；
  - `Rank 320` 已在 `research/optimization_loop/2026-04-04_0101_rank320_wilder_rsi_fast_exit_first_verdict_keep_p1.md` 完成最新一条 fresh intake first verdict，并已占用当前唯一 survivor 槽位；
  - 因此本轮运行态里的 fresh intake 主语仍是 `Wilder RSI breakout × EMA200/ADX/volume allow × fast RSI-45 exit` 这条刚完成 first verdict 的对象。

3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得，但它那次机会已经不能再优先于当前 survivor 槽位。
- 上一条 fresh intake 是：
  - `research/quant_digests/2026-04-03_2251_dc-vwap-ema-asymmetric-trend-shell.md`（`Rank 319`）
- 最近证据表明它当时值得进入 `P1`：
  - 它已有清楚的 `VWAP-EMA directional-change continuation × ~1% reversal exit` 主语；
  - 也有完整的 entry/exit/cost 壳；
  - first verdict 已明确说它至少值得做一次 `asset-admission` 类型的 survivor follow-up，而不是直接扔回 `background/P0`。
- 但按 policy，`Surviving candidate` **只能是上一条 fresh intake**；当前上一条 fresh intake 已变成 `Rank 320`，所以 `Rank 319` 不得再自动抢回 survivor 槽位。

4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 不存在。
- `Active P2 slot.current_target = none`。
- 最近唯一明确的 `Active P2` 是 `Rank 314 / tradability-aware cluster pairs`，但它已在 `research/optimization_loop/2026-04-03_1940_rank314_p2_exit_background_p0.md` 完成出口决策并收口到 `background/P0`。
- 因此本轮不存在需要 bot2 兜底直推 `P3 / Paper launch queue` 的漏升对象。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Fresh intake slot.current_target = research/quant_digests/2026-04-03_2141_wilder-rsi-fast-exit-trend-shell-alpha.md`
- `Surviving candidate slot.current_target = Rank 320 / Wilder RSI breakout × EMA200/ADX/volume allow × fast RSI-45 exit`
- `Active P2 slot.current_target = none`
- 当前前排对象不存在已达 `keep_P1 / P2 / P3` 但无正式 rank 的情况；本轮无需补新的整数 `Rank`。

## P2 -> P3 兜底裁判检查
- 当前没有 `Active P2`。
- 最近证据里也没有“已经足够值得 paper trade、但 bot3 尚未升级”的漏升对象。
- 因此本轮不写入新的 `P3 / Paper launch queue` 或 handoff 路径。

## 本轮排班改写
按 policy 默认顺序扫描后：
- `P3`：无待接线对象
- `P2`：无 active P2
- `P1`：有且只有一个合法动作 —— `Rank 320` 的唯一 survivor follow-up
- 因此前两项必须先留给 `Rank 320` 收口后的 fresh intake 回补，不能再把新的 intake 排到 survivor 前面

因此本轮把 `cycle_plan` 重写为 4 项：
1. `Rank 320 / Wilder RSI breakout × EMA200/ADX/volume allow × fast RSI-45 exit` 的唯一 survivor follow-up，直接回答 `promote_P2` 还是 `background/P0`
2. `research/quant_digests/2026-04-04_0020_extreme-divergence-exhaustion-fade-alpha.md` 作为新的 fresh intake
3. `research/quant_digests/2026-04-03_2103_reverse-grid-tradecontrol-meanreversion-alpha.md` 作为 conditional fresh intake
4. `research/quant_digests/2026-04-03_2354_fng-extremity-adverse-selection-overlay.md` 作为 conditional fresh intake

改写理由：
- 现有前排对象的合法收口优先级高于新的发现；因此 `Rank 320` 必须放在第 1 位；
- 当前没有 `P3` 和 `P2` 动作，不得虚构 queue guard 或空槽确认来占轮次；
- `Rank 319` 虽曾值得 survivor follow-up，但它已不是“上一条 fresh intake”，不得自动抢回 survivor 锁定权；
- 一旦 survivor 收口完成，本轮预算再切回具体 fresh intake；优先补最近新增的 `2026-04-04_0020_extreme-divergence-exhaustion-fade-alpha.md`，然后才是 `reverse-grid` 与 `F&G overlay`；
- 全程未把 background pool 旧候选拉回前排。

## 本轮写回
- 已更新：`docs/BOT2_BOT3_STATE.md`（仅重写 `cycle_plan`）
- 未改动 policy / brief / operating card / auto loop / cron prompt。
