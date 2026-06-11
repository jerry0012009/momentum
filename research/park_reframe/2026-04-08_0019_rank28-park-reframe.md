# 2026-04-08 00:19 UTC · Rank 28 park reframe review

## Scope
- source rank: `Rank 28 / cross-market intraday leader-laggard`
- source evidence read:
  - `docs/TODO.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - `docs/RECENT_PAPER_SEEDS.md`
  - `research/quant_digests/INDEX.md`
  - `research/park_reframe/INDEX.md`
  - `research/optimization_loop/2026-03-17_0841_rank28-crossmarket-clean-replication.md`
- recent external/internal evidence checked via digest index:
  - `2026-04-06_0558_btc-lead-liquidity-lag-alt-alpha.md`
  - `2026-04-07_1436_majorlead-closeslot-crossmarket-itsm-alpha.md`
  - `2026-04-07_1748_binance-okx-spot-leadlag-catchup-alpha.md`

## Why Rank 28 this round
- 仍在 `Rank 1~37` 的 bot6 处理范围内。
- 最近 7 天未复盘同一 rank；上次明确 bot6 复盘是 `2026-03-23 23:58 UTC`。
- 4 月初又连续出现几条 cross-market / lead-lag 新证据，值得判断它们是否足以把旧的 `park` 再收窄成新的单轴派生。

## Original rank：为什么会 park
原 Rank 28 的问题不是“cross-market 信息完全不存在”，而是**把它写成 15m 直接 leader-laggard 跟随入场**这件事，在 clean replication 里没有站住：
- source clean replication 明确记录 primary variant（`funding_8h_q60 @ 6bps/side`）直接为负，`mean_total_return ≈ -16.58%`；
- 问题不只是一组参数没调对，而是 direct lag-trade 在成本后、跨资产与时间稳定性上都没给出可继续前推的诚实 pocket；
- 所以原 `park` 的审计含义应保留：**旧 Rank 28 作为 queue-facing direct lag-trade 已经被否过。**

## Hard park 还是 soft park
结论：**soft park，但对原 direct lag-trade 读法已经更偏 hard。**

原因：
- soft 的部分：主题本身（leader impulse / follower catch-up / cross-market spillover）并没有死；
- 更偏 hard 的部分：这些残余信息越来越清楚地显示，真正可能存活的是**更窄、更快、更事件化**的宿主，而不是把旧 Rank 28 再补一层 shared gate 或宽 15m lag-trade 写法就能救回来。

## 有没有“可救信号”
有，但不在原 Rank 28 本体上，主要是以下三类新证据：
1. `BTC lead × low-liquidity alt lag`（2026-04-06）
   - 说明 lead-lag 主题更像**BTC 冲击驱动的小币滞后**，而不是泛化的同层 leader-laggard bucket。
2. `major-lead first-slot return × follower close-slot continuation`（2026-04-07）
   - 说明跨市场信息可能存在于**slot handoff / session handoff**，而不是原 Rank 28 那种平铺的 intraday direct follow。
3. `Binance spot impulse × OKX delayed catch-up`（2026-04-07）
   - 说明更强的可救信号落在**同一标的跨 venue 的更短时延 catch-up**，已经明显偏向新的 lower-TF / same-underlier raw-alpha 宿主。

换句话说：
- 可救的是“leader impulse 有后续信息”这个主题；
- 不可救的是“原 Rank 28 这套 15m direct cross-market lag-trade 写法”。

## 最值得改的唯一一刀是什么
本轮判断：**没有比既有 `Rank 28b` 更诚实的新一刀。**

原因：
- 既有 `Rank 28b` 已经把原 Rank 28 最自然的 queue-facing residual 收窄成：
  - `alt-vs-BTC RS breadth shared regime gate`
- 4 月初新增证据并没有指向另一个仍可归属于“原 Rank 28 reframe”的 queue-facing 单轴；
- 它们反而更一致地把主题推向：
  - lower-TF event-driven catch-up
  - same-underlier cross-venue lead-lag
  - session/slot handoff continuation
- 这些都更像**新的 raw-alpha family 宿主**，而不是再从 Rank 28 派生一个 `Rank 28c`。

## 是否值得形成新的 derived hypothesis
结论：**不值得。**

- 保留原 `park` verdict；
- 保留既有 `Rank 28b` 作为唯一仍诚实的 queue-facing residual；
- 本轮不新增 `Rank 28c`。

## Final verdict
`soft_reframe_candidate`

## Git / write hygiene
- 本轮只改了：
  - `research/park_reframe/2026-04-08_0019_rank28-park-reframe.md`
  - `research/park_reframe/INDEX.md`
  - `docs/PARK_REFRAME_QUEUE.md`
- 当前 git 工作区存在无关脏文件 / 截断输出显示的既有未收口改动；为避免混提，本轮不做 commit。

## Short decision for bot2/bot3 context
- 原 Rank 28 为什么 park：因为 15m direct leader-laggard 路线 clean replication 成本后直接为负，且缺少可前推的稳定 pocket。
- 它更像 hard park 还是 soft park：soft park，但对原写法已更偏 hard。
- 有没有可救信号：有；但信号在更快、更窄、更事件化的 lead-lag 宿主上，不在旧 Rank 28 本体上。
- 最值得改的唯一一刀是什么：没有比既有 `Rank 28b` 更诚实的新一刀。
- 是否值得形成新的 derived hypothesis：不值得；本轮不 draft `Rank 28c`。
