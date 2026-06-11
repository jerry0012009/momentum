# Strategy Review — 2026-04-04 00:07 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-03_2353_poc_valuearea_fill_first_verdict_background_p0.md`
  - `research/optimization_loop/2026-04-03_2328_hyperliquid_public_trigger_cluster_first_verdict_background_p0.md`
  - `research/optimization_loop/2026-04-03_2317_rank318_survivor_followup_background_p0.md`
  - `research/optimization_loop/2026-04-03_2301_rank318_runtime_sync_keep_p1.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-03_2304_strategy-review.md`
- 当前/候补 intake 材料：
  - `research/quant_digests/2026-04-03_2251_dc-vwap-ema-asymmetric-trend-shell.md`
  - `research/quant_digests/2026-04-03_2141_wilder-rsi-fast-exit-trend-shell-alpha.md`
  - `research/quant_digests/2026-04-03_2103_reverse-grid-tradecontrol-meanreversion-alpha.md`
  - `research/quant_digests/2026-04-03_2354_fng-extremity-adverse-selection-overlay.md`

## 只回答 4 个问题

1) `Paper launch queue` 是否非空？
- 否。
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有新的待接线 queue 头对象。

2) 本轮 `fresh intake` 是什么？
- 当前 fresh intake 头是：
  - `research/quant_digests/2026-04-03_2251_dc-vwap-ema-asymmetric-trend-shell.md`
- 原因：
  - `Rank 318 / Polymarket final-window lag arb` 已在 `research/optimization_loop/2026-04-03_2317_rank318_survivor_followup_background_p0.md` 用完唯一一次 survivor follow-up，并诚实收口到 `background/P0`；
  - `Hyperliquid public trigger cluster` 已在 `research/optimization_loop/2026-04-03_2328_hyperliquid_public_trigger_cluster_first_verdict_background_p0.md` 收口到 `background/P0`；
  - `POC / value-area fill sanity` 已在 `research/optimization_loop/2026-04-03_2353_poc_valuearea_fill_first_verdict_background_p0.md` 收口到 `background/P0`；
  - 因此前排链条已清空，fresh intake 头顺延到 `directional-change × VWAP/EMA asymmetric trend shell`。

3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 不值得。
- 上一条 fresh intake 是 `research/quant_digests/2026-04-03_2224_poc-valuearea-fill-sanity-alpha.md`。
- 最近证据已直接回答它不该保留前排：
  - 在把成交口径改成诚实的 `next-open / 非 stale fill` 后，fade / follow 只剩约 `1.5~2.2 bps` 的毛边；
  - 当前优势主要来自乐观 fill，而不是足够厚的独立 alpha；
  - 因此它的 first verdict 已经是 `background/P0`，不存在再给一次 survivor follow-up 的空间。

4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 不存在。
- `Active P2 slot.current_target = none`。
- 最近唯一明确的 `Active P2` 是 `Rank 314 / tradability-aware cluster pairs`，但它已在 `research/optimization_loop/2026-04-03_1940_rank314_p2_exit_background_p0.md` 完成出口决策并收口到 `background/P0`。
- 因此本轮不存在需要 bot2 兜底直推 `P3 / Paper launch queue` 的漏升对象。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Fresh intake slot.current_target = research/quant_digests/2026-04-03_2251_dc-vwap-ema-asymmetric-trend-shell.md`
- `Surviving candidate slot.current_target = none`
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
- `P1`：无 survivor
- 因此前排链条已诚实收口，本轮应直接切回新的具体 fresh intake

因此本轮 `cycle_plan` 重写为 4 项：
1. `research/quant_digests/2026-04-03_2251_dc-vwap-ema-asymmetric-trend-shell.md`
2. `research/quant_digests/2026-04-03_2141_wilder-rsi-fast-exit-trend-shell-alpha.md`
3. `research/quant_digests/2026-04-03_2103_reverse-grid-tradecontrol-meanreversion-alpha.md`
4. `research/quant_digests/2026-04-03_2354_fng-extremity-adverse-selection-overlay.md`

改写理由：
- 当前没有合法 `P3 / Active P2 / Surviving candidate` 动作，因此不能再虚构前排收口任务；
- 既然已切回 `fresh intake`，就必须直接填具体对象，而不是写空模板；
- 第一优先仍是最新、最像 raw alpha 母板的 `DC × VWAP/EMA asymmetric trend shell`；
- 第二、第三项继续优先补最近的完整 raw alpha 壳：`Wilder RSI fast-exit trend shell` 与 `bounded-bounce reverse-grid × ADX/DI veto`；
- 第四项再补一条虽非 raw alpha、但可能对现有短周期壳有共享价值的 `F&G extremity adverse-selection overlay`；
- 本轮没有把任何 background pool 旧候选拉回前排。

## 本轮写回
- 已更新：`docs/BOT2_BOT3_STATE.md`
- 本轮仅改写 runtime state 与 `cycle_plan`；未改动 policy / brief / operating card / cron prompt。
