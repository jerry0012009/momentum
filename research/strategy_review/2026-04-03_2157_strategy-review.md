# Strategy Review — 2026-04-03 21:57 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short --branch`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-03_2154_rank317_survivor_followup_background_p0.md`
  - `research/optimization_loop/2026-04-03_2113_polymarket_finalwindow_lagarb_blocked_by_rank317_survivor_lock.md`
  - `research/optimization_loop/2026-04-03_2044_rank317_pacifica_hl_maker_taker_xemm_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-03_1940_rank314_p2_exit_background_p0.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-03_2114_strategy-review.md`
  - `research/strategy_review/2026-04-03_2016_strategy-review.md`
- 当前/候补 intake 材料：
  - `research/quant_digests/2026-04-03_1647_polymarket-finalwindow-lagarb-alpha.md`
  - `research/quant_digests/2026-04-03_1425_hyperliquid-public-trigger-cluster-alpha.md`
  - `research/quant_digests/2026-04-03_2103_reverse-grid-tradecontrol-meanreversion-alpha.md`
  - `research/quant_digests/2026-04-03_2141_wilder-rsi-fast-exit-trend-shell-alpha.md`

## 只回答 4 个问题

1) `Paper launch queue` 是否非空？
- 否。
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有新的待接线 queue 头对象。

2) 本轮 `fresh intake` 是什么？
- 当前 fresh intake 头是：
  - `research/quant_digests/2026-04-03_1647_polymarket-finalwindow-lagarb-alpha.md`
- 原因：`Rank 317 / Pacifica maker quote edge × Hyperliquid taker hedge` 已完成唯一 survivor follow-up，并在 `research/optimization_loop/2026-04-03_2154_rank317_survivor_followup_background_p0.md` 收口到 `background/P0`；survivor 槽位已清空，因此前排自然切回当前 fresh intake 头 `Polymarket final-window lag arb`。

3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得，但该 follow-up 已经做完，而且结论是否定的。
- 上一条 fresh intake 就是 `Rank 317 / Pacifica maker quote edge × Hyperliquid taker hedge`。
- 它首判 `keep_P1` 的理由当时足够具体，所以值得消耗唯一一次 follow-up；但 follow-up 已直接回答关键问题：按 repo 默认 `1.5bps maker + 4bps taker + 15bps target` 对 `BTC/ETH/SOL` 做的公开盘口 probe，在双向上都没有观察到任何 fee-adjusted 正 edge，更不存在可穿过目标利润的 pocket。
- 因此它已经不诚实支持 `promote_P2`，并已正式回到 `background/P0`；本轮不再保留 survivor 前排动作。

4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 不存在。
- `Active P2 slot.current_target = none`。
- 最近唯一明确的 `Active P2` 是 `Rank 314 / tradability-aware cluster pairs`，但它已在 `research/optimization_loop/2026-04-03_1940_rank314_p2_exit_background_p0.md` 完成出口决策并收口到 `background/P0`。
- 因此本轮不存在需要 bot2 兜底直推 `P3 / Paper launch queue` 的漏升对象。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Fresh intake slot.current_target = research/quant_digests/2026-04-03_1647_polymarket-finalwindow-lagarb-alpha.md`
- `Surviving candidate slot.current_target = none`
- `Active P2 slot.current_target = none`
- 当前前排不存在已达 `keep_P1 / P2 / P3` 但无 rank 的对象；本轮无需补新的整数 `Rank`。

## P2 -> P3 兜底裁判检查
- 当前没有 `Active P2`。
- 最近证据里也没有“已经足够值得 paper trade、但 bot3 尚未升级”的漏升对象。
- 因此本轮不写入新的 `P3 / Paper launch queue` 或 handoff 路径。

## 本轮排班改写
按 policy 默认顺序扫描后：
- `P3`：无待接线对象
- `P2`：无 active P2
- `P1`：无 survivor；`Rank 317` 已在本轮前刚刚诚实收口到 `background/P0`
- 因此前排合法动作全部切回 `fresh intake`

因此本轮 `cycle_plan` 重写为 4 项：
1. `research/quant_digests/2026-04-03_1647_polymarket-finalwindow-lagarb-alpha.md`
2. `research/quant_digests/2026-04-03_1425_hyperliquid-public-trigger-cluster-alpha.md`
3. `research/quant_digests/2026-04-03_2103_reverse-grid-tradecontrol-meanreversion-alpha.md`
4. `research/quant_digests/2026-04-03_2141_wilder-rsi-fast-exit-trend-shell-alpha.md`

改写理由：
- 当前不存在合法 `P3 / Active P2 / Surviving candidate` 动作，因此按 policy 必须直接切回 fresh intake。
- `Polymarket final-window lag arb` 仍是合法 fresh intake 头，且主题清楚、可独立 paper 化，理应队首。
- 剩余预算优先给三条最近、彼此异质、且仍像独立 raw alpha 的具体 intake：
  - `Hyperliquid public trigger / liquidation cluster continuation`：分钟级 event-driven cluster continuation；
  - `bounded-bounce reverse-grid × ADX/DI trend veto`：单资产短周期 mean-reversion 母板；
  - `Wilder RSI breakout × EMA200/ADX/volume allow × fast RSI-45 exit`：单资产短周期趋势延续母板。
- 没有把任何 background pool 旧候选拉回前排。

## repo 状态备注（仅作 evidence）
- 工作区存在大量历史未跟踪 `research/*` 与脚本文件；这些只作为 repo 脏状态 evidence，不反向改写 policy，也不触发任何 background pool 自动 reopen。

## 本轮写回内容
- 已更新：`docs/BOT2_BOT3_STATE.md`
- 已新增：`research/strategy_review/2026-04-03_2157_strategy-review.md`
- 未改动：policy / brief / operating card / auto loop / cron prompt

## 本轮改变系统认知的一句话
`Rank 317` 的 survivor 已被诚实证伪并收口到 `background/P0`，而当前又没有 `P3/P2/P1` 前排未决对象，所以本轮 bot3 应直接恢复 fresh intake 链，从 `Polymarket final-window lag arb` 开始顺序推进新的四条具体 intake。