# 2026-04-19 21:15 UTC · Rank 22 park reframe review

## 本轮对象
- `Rank 22 / up/down wave + MA20 persistence gate`
- 原始结论保留：`park / evidence pool`
- 本轮输出：`keep_park`

## 为什么这轮看 Rank 22
- `Rank 1~37` 里最近 `7` 天没被 bot6 复盘、且仍明确处于 `park` 的候选很少；`Rank 2 / Rank 17` 虽未在最近 `7` 天复盘，但它们当前并不属于已 `park` 条目，因此不应误认领。
- 在仍属 `park` 的旧 rank 里，`Rank 22` 上次复盘是 `2026-04-13 10:06 UTC`，而这之后又新增了更直接的“急跌后反弹”旁证：
  - `research/quant_digests/2026-04-19_2019_highvol-selloff-bounce-5m-alpha.md`
  - `research/optimization_loop/2026-04-19_1425_vwap_lowerband_reclaim_freshintake_background_p0.md`
  - `research/optimization_loop/2026-04-19_1611_rank425_survivor_followup_background_p0_timeslice_concentration.md`
- 这些新证据足以重新回答一个窄问题：它们有没有把旧 `Rank 22` 的 `wave + MA persistence gate` 救回来，还是只是继续把“跌后修复”主题外流到新的 raw-alpha / single-name event 宿主。

## Read set
- `docs/BOT6_PARK_REFRAME_BRIEF.md`
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- source / prior rank evidence:
  - `research/optimization_loop/2026-03-17_0437_rank22-clean-replication-park.md`
  - `research/park_reframe/2026-04-13_1006_rank22-park-reframe.md`
- new side evidence:
  - `research/quant_digests/2026-04-19_2019_highvol-selloff-bounce-5m-alpha.md`
  - `research/optimization_loop/2026-04-19_1425_vwap_lowerband_reclaim_freshintake_background_p0.md`
  - `research/optimization_loop/2026-04-19_1611_rank425_survivor_followup_background_p0_timeslice_concentration.md`

## 1) 原 rank 为什么 park？
原 `Rank 22` 被 park 的 blocker 没变：把“跌后修复”写成 **shared `up/down wave + MA20 persistence gate`**，最多只是让 baseline 少亏，但没有形成可 admission 的独立 edge。

`2026-03-17_0437_rank22-clean-replication-park.md` 的关键结果：
- 主变体 `updownwave_ma20`：`6bps/side` 下 `mean_total_return≈-7.94%`，`positive_asset_ratio=1/3`
- 邻域最不差的 `MA15`：也只有 `≈-3.26%`，仍未转正
- 时间稳定性：`bucket_2≈-12.70%` 明显失守
- 跨标的：`BTC≈-14.05%`、`ETH≈-18.92%`、`SOL≈+9.15%`
- 成本抬升到 `10/15/20 bps` 后继续快速恶化

所以原 `park` 的审计意义仍然清楚：
> 被否掉的是“slow wave + MA persistence gate”这层旧表达，而不是所有 downside-recovery / panic-bounce 主题都没信息。

## 2) 它更像 hard park 还是 soft park？
**本轮判断：仍是 `soft park`，但比 4 月 13 日那轮更接近 hard。**

原因：
1. 原 rank 至少留过 `SOL` 单腿 pocket，所以还不能说主题彻底归零；
2. 但 4 月 19 日新增证据没有修复旧 gate，反而更一致地把残余信息指向 **更快、更窄的 event-driven / single-name bounce**；
3. 换句话说，今天还能保留的 soft 成分，越来越像主题级 residual，而不像旧 `Rank 22` 本体级 residual。

## 3) 有没有“可救信号”？
**有，但更明确地属于主题级可救信号，不属于旧 rank 级可救信号。**

新增旁证共同在说同一件事：
- `2026-04-19_2019_highvol-selloff-bounce-5m-alpha.md`：最像真的，不是 slow wave gate，而是 **高成交量急跌后的 `5m` 短窗 bounce raw alpha**；
- `2026-04-19_1425_vwap_lowerband_reclaim_freshintake_background_p0.md`：即便同属 bounce 母题，若只剩薄 `5m` reclaim gross、不能覆盖统一成本，也应直接收口，不能拿它回填旧 gate；
- `2026-04-19_1611_rank425_survivor_followup_background_p0_timeslice_concentration.md`：即便有表面净值，若最近月份、时段与单币集中度没闭合，也说明这类题材更适合被当成新的 event pocket 逐条审，而不是回包装成 shared persistence gate。

因此这轮“可救信号”更像：
> `single-name or strongest-shock downside event -> short-window bounce`

而不是：
> `up/down wave + MA persistence` 这层 shared allow/deny gate 仍值得窄重开。

## 4) 最值得改的唯一一刀是什么？
如果今天还要回答“唯一最值得改的一刀”，最诚实的版本只能是：

> **放弃 slow `wave + MA persistence` shared gate，改写成 strongest-shock / single-name 的高成交量 downside event 短窗 bounce。**

但关键也正卡在这里：
- 这已经不是旧 `Rank 22` 的窄 reframe；
- 它把主语从 shared gate 改成了 single-name / event-driven raw alpha；
- 因此更像新的 family intake，而不是诚实的 `Rank 22b`。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。本轮继续 `keep_park`。**

原因：
1. 原 `park` verdict 没被推翻；
2. 新 evidence 没有把 `wave + MA persistence gate` 修回可交易状态；
3. 新 evidence 只是在更一致地说明：可救信号属于新的 downside-shock bounce raw-alpha 宿主；
4. 若硬写 `Rank 22b`，会把新宿主的事件驱动证据误包装成旧 gate 的小修小补，削弱原 `park` 的审计意义。

## 单轮审查模板回答
### 原 rank 为什么 park？
因为 `wave + MA persistence gate` 在 clean replication 中只是减亏，不够形成 post-cost、跨资产、跨参数都能站住的 admission 级 edge。

### 它更像 hard park 还是 soft park？
`soft park`，但比 4 月 13 日那轮更接近 hard。

### 有没有“可救信号”？
有，但主要是 `high-volume downside shock -> short-window bounce` 这类新的事件驱动 raw alpha；可救的是主题，不是旧 `Rank 22` 壳。

### 最值得改的唯一一刀是什么？
把 slow shared gate 改写成 strongest-shock / single-name 的高成交量 downside event 短窗 bounce。

### 是否值得形成新的 derived hypothesis？
不值得。本轮继续 `keep_park`。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但比 4 月 13 日那轮更接近 hard；4 月 19 日新增的 high-volume selloff bounce、薄 VWAP reclaim 收口与 Rank 425 时间切片集中度证据继续说明“跌后修复”主题仍有信息，但它更像新的 strongest-shock / single-name event-driven raw-alpha 宿主，而不是旧 Rank 22 的 wave + MA persistence gate，因此当前不诚实 draft Rank 22b。`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## Commit
- 本轮不做 commit。
- 原因：git 工作区存在大量与本轮无关的共享脏文件 / 未跟踪文件；本轮只做最小必要文档改动，避免混提。
