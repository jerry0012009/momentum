# 2026-04-13 10:06 UTC · Rank 22 park reframe review

## 本轮对象
- `Rank 22 / up/down wave + MA20 persistence gate`
- 原始结论保留：`park / evidence pool`
- 本轮输出：`keep_park`

## 为什么这轮看 Rank 22
- `Rank 22` 上次 park-reframe 复盘是 `2026-04-08 17:04 UTC`，按默认规则本应尽量避开最近 `7` 天重复认领；
- 但 4 月 13 日新增了会改变“残余信息该记在谁账上”的旁支证据：
  - `research/quant_digests/2026-04-13_0639_eth-downside-outlier-fade-alpha.md`
- 这条新证据继续支持“跌后修复 / downside shock fade”主题仍有信息，但它的主语已经更像 **ETH 单币极端下跌事件后的 raw alpha**，不是旧 `Rank 22` 的 `wave + MA persistence gate` 壳。
- 因此本轮只回答一件事：这条新 evidence 是否足以把 `Rank 22` 从 `keep_park` 推到新的窄 reframe hypothesis。

## Read set
- `docs/BOT6_PARK_REFRAME_BRIEF.md`
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent park-reframe references:
  - `research/park_reframe/2026-04-13_0750_rank31-park-reframe.md`
  - `research/park_reframe/2026-04-13_0517_rank29-park-reframe.md`
  - `research/park_reframe/2026-04-13_0221_rank37-park-reframe.md`
- source / prior rank evidence:
  - `research/optimization_loop/2026-03-17_0437_rank22-clean-replication-park.md`
  - `research/park_reframe/2026-04-08_1704_rank22-park-reframe.md`
- new side evidence:
  - `research/quant_digests/2026-04-13_0639_eth-downside-outlier-fade-alpha.md`

## 1) 原 rank 为什么 park？
原 `Rank 22` 被 park 的 blocker 没变：把“跌后修复”写成 **shared `up/down wave + MA20 persistence gate`**，最多只是让 baseline 少亏，但没有形成可 admission 的独立 edge。

`2026-03-17_0437_rank22-clean-replication-park.md` 的关键结果：
- 主变体 `updownwave_ma20`：`6bps/side` 下 `mean_total_return≈-7.94%`，`positive_asset_ratio=1/3`
- 邻域最不差的 `MA15`：也只有 `≈-3.26%`，仍未转正
- 时间稳定性：`bucket_2≈-12.70%` 明显失守
- 跨标的：`BTC≈-14.05%`、`ETH≈-18.92%`、`SOL≈+9.15%`
- 成本抬升到 `10/15/20 bps` 后继续快速恶化

所以原 `park` 的审计意义很清楚：
> 被否掉的是“slow wave + MA persistence gate”这层旧表达，而不是所有 downside-recovery / snapback 主题都没信息。

## 2) 它更像 hard park 还是 soft park？
**本轮判断：仍是 `soft park`，但比 4 月 8 日那轮更接近 hard。**

原因：
1. 原 rank 至少留过 `SOL` 单腿 pocket，所以不能直接说主题彻底归零；
2. 但 4 月 13 日的新证据没有修复旧 gate，反而继续把残余信息从“shared persistence gate”外流到“单币极端 downside 事件 raw alpha”；
3. 也就是说，今天还能保留的 soft 成分，越来越像主题级 residual，而不像旧 `Rank 22` 本体级 residual。

## 3) 有没有“可救信号”？
**有，但更明确地属于主题级可救信号，不属于旧 rank 级可救信号。**

这轮新增的 `2026-04-13_0639_eth-downside-outlier-fade-alpha.md` 说明：
- 更像能活下来的不是“wave + MA persistence allow/deny”；
- 而是 `ETHUSDT` 在 `15m` 上出现极端 downside outlier 后的 **event-driven bounce pocket**；
- 且这条 pocket 还带明显的 `Europe-hours veto`，即强 session 条件与单币选择性。

这会进一步强化一个判断：
> “跌后修复”主题若还值得追，更像 `single-name downside shock fade` 这类更快、更窄、更事件化的 raw-alpha 宿主。

但它救不了旧 `Rank 22`，因为两者主语已不一样：
- `Rank 22`：shared gate / wave persistence / slow MA context
- 新 digest：ETH 单币 / 极端 shock 事件锚 / next-hour bounce

## 4) 最值得改的唯一一刀是什么？
如果今天还要回答“唯一最值得改的一刀”，最诚实的版本只能是：

> **放弃 slow `wave + MA persistence` shared gate，改写成 ETH downside outlier event 的短窗 fade。**

但这轮关键判断也恰恰在这里：
- 这已经不是旧 `Rank 22` 的窄 reframe；
- 它把主语从 shared gate 改成了 single-name event-driven raw alpha；
- 因此更像新 family intake，而不是诚实的 `Rank 22b`。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。本轮继续 `keep_park`。**

原因：
1. 原 `park` verdict 没被推翻；
2. 新 evidence 没有把 `wave + MA persistence gate` 修回可交易状态；
3. 新 evidence 只是在更明确地说：可救信号属于新的 ETH downside-shock raw-alpha 宿主；
4. 若硬写 `Rank 22b`，会把新宿主的 raw-alpha 证据误包装成旧 gate 的小修小补，削弱原 `park` 的审计意义。

## 单轮审查模板回答
### 原 rank 为什么 park？
因为 `wave + MA persistence gate` 在 clean replication 中只是减亏，不够形成 post-cost、跨资产、跨参数都能站住的 admission 级 edge。

### 它更像 hard park 还是 soft park？
`soft park`，但比 4 月 8 日那轮更接近 hard。

### 有没有“可救信号”？
有，但主要是 `ETH downside outlier fade × Europe-hours veto` 这类新的事件驱动 raw alpha，可救的是主题，不是旧 `Rank 22` 壳。

### 最值得改的唯一一刀是什么？
把 slow shared gate 改写成 ETH 单币极端 downside 事件后的短窗 fade。

### 是否值得形成新的 derived hypothesis？
不值得。本轮继续 `keep_park`。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但比 4 月 8 日那轮更接近 hard；4 月 13 日新增的 ETH downside outlier fade 证据继续说明“跌后修复”主题仍有信息，但它救活的是新的 single-name event-driven raw-alpha 宿主，而不是旧 Rank 22 的 wave + MA persistence gate，因此当前不诚实 draft Rank 22b。`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## Commit
- 本轮不做 commit。
- 原因：git 工作区存在大量与本轮无关的共享脏文件 / 未跟踪文件；本轮只做最小必要文档改动，避免混提。
