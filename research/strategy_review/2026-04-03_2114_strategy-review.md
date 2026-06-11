# Strategy Review — 2026-04-03 21:14 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-03_2113_polymarket_finalwindow_lagarb_blocked_by_rank317_survivor_lock.md`
  - `research/optimization_loop/2026-04-03_2044_rank317_pacifica_hl_maker_taker_xemm_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-03_2036_rank316_survivor_followup_background_p0.md`
  - `research/optimization_loop/2026-04-03_1940_rank314_p2_exit_background_p0.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-03_2016_strategy-review.md`
  - `research/strategy_review/2026-04-03_1938_strategy-review.md`
- 最近 fresh intake / conditional intake 材料：
  - `research/quant_digests/2026-04-03_1647_polymarket-finalwindow-lagarb-alpha.md`
  - `research/quant_digests/2026-04-03_1845_pacifica-hl-maker-taker-xemm-alpha.md`
  - `research/quant_digests/2026-04-03_1425_hyperliquid-public-trigger-cluster-alpha.md`
  - `research/quant_digests/2026-04-03_2103_reverse-grid-tradecontrol-meanreversion-alpha.md`

## 只回答 4 个问题

1) `Paper launch queue` 是否非空？
- 否。
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有新的待接线 queue 头对象。

2) 本轮 `fresh intake` 是什么？
- 当前 fresh intake 头是：
  - `research/quant_digests/2026-04-03_1647_polymarket-finalwindow-lagarb-alpha.md`
- 原因：`Pacifica maker × Hyperliquid taker XEMM` 已在 `research/optimization_loop/2026-04-03_2044_rank317_pacifica_hl_maker_taker_xemm_first_verdict_keep_p1.md` 完成 first verdict，获得正式 `Rank 317` 并进入 `Surviving candidate slot`；按 policy，它的唯一 survivor follow-up 还没消耗完，所以 fresh intake 头仍合法停在 `Polymarket final-window lag arb`。

3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得。
- 上一条 fresh intake 就是 `Rank 317 / Pacifica maker quote edge × Hyperliquid taker hedge`。
- 它首判 `keep_P1` 的理由已足够具体：
  1. raw alpha 主语清楚，不是方向预测，而是 `maker venue quote edge -> taker venue hedge` 的跨 venue 微观流动性不对称；
  2. repo 已把 entry / cancel / hedge / fee 逻辑写到规则级；
  3. public-data 路径清楚，至少可立刻在 `BTC/ETH/SOL` 上做 top-of-book edge occupancy 与 spell-duration 验证。
- 唯一值得做的 follow-up 也已收敛：
  - 只回答 `edge occupancy / 持续时间 / 最保守 fill proxy / hedge slippage stress` 后是否仍有净 pocket；
  - 若仍成立，直接 `promote_P2`；
  - 若净后主要被 fill probability 或 hedge slippage 吃光，就直接 `background/P0`。

4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 不存在。
- `Active P2 slot.current_target = none`。
- 最近唯一明确的 `Active P2` 是 `Rank 314 / tradability-aware cluster pairs`，但它已在 `research/optimization_loop/2026-04-03_1940_rank314_p2_exit_background_p0.md` 完成出口决策并收口到 `background/P0`。
- 因此本轮不存在需要 bot2 兜底直推 `P3 / Paper launch queue` 的漏升对象。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Fresh intake slot.current_target = research/quant_digests/2026-04-03_1647_polymarket-finalwindow-lagarb-alpha.md`
- `Surviving candidate slot.current_target = Rank 317 / Pacifica maker quote edge × Hyperliquid taker hedge`
- `Active P2 slot.current_target = none`
- 当前前排对象不存在无 rank 的 `P1 / P2 / P3`；本轮无需补新的整数 `Rank`。

## P2 -> P3 兜底裁判检查
- 当前没有 `Active P2`。
- 最近证据里也没有“已经足够值得 paper trade、但 bot3 尚未升级”的漏升对象。
- 因此本轮不写入新的 `P3 / Paper launch queue` 或 handoff 路径。

## 本轮排班改写
按 policy 默认顺序扫描后：
- `P3`：无待接线对象
- `P2`：无 active P2
- `P1`：有且仅有 `Rank 317` survivor follow-up，必须占据队首
- 然后才允许切回 fresh intake

因此本轮 `cycle_plan` 改写为 4 项：
1. `Rank 317 / Pacifica maker quote edge × Hyperliquid taker hedge`
2. `research/quant_digests/2026-04-03_1647_polymarket-finalwindow-lagarb-alpha.md`
3. `research/quant_digests/2026-04-03_1425_hyperliquid-public-trigger-cluster-alpha.md`
4. `research/quant_digests/2026-04-03_2103_reverse-grid-tradecontrol-meanreversion-alpha.md`

改写理由：
- `Rank 317` 是当前前排唯一尚未收口的 survivor，且仍有 1 次 follow-up 预算；它的收口优先级高于任何新的 fresh intake。
- `Polymarket final-window lag arb` 仍是合法的 fresh intake 头：对象主语清楚、public path 清楚、但本轮不能再抢在 survivor 前面。
- 在 survivor 与 fresh intake 头都已诚实放进前部后，剩余预算优先给两条具体、异质且较新的 intake：
  - `Hyperliquid public trigger cluster continuation`：event-driven / public-cluster 方向，与当前 maker-taker survivor 不重复；
  - `bounded-bounce reverse-grid × ADX/DI trend veto`：单资产 short-cycle mean-reversion 母板，也不与前两条重复。
- 没有把任何 background pool 旧对象拉回前排。

## repo 状态备注（仅作 evidence）
- 工作区存在大量历史未跟踪 `research/*` 与脚本文件；这些只作为 repo 脏状态 evidence，不反向改写 policy，也不触发任何 background pool 自动 reopen。

## 本轮写回内容
- 已更新：`docs/BOT2_BOT3_STATE.md`
- 已新增：`research/strategy_review/2026-04-03_2114_strategy-review.md`
- 未改动：policy / brief / operating card / auto loop / cron prompt

## 本轮改变系统认知的一句话
当前前排已经收敛成“`Rank 317` 的唯一 survivor follow-up + `Polymarket final-window lag arb` fresh intake 头”；所以这轮 bot3 应先把 `Rank 317` 诚实推向 `P2` 或 `background/P0`，再恢复新的 intake 流。