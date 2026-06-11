# 2026-04-21 17:44 UTC · Rank 31 park reframe

## Selected rank
- `Rank 31`
- selection note: 本轮按你刚重申的范围，只在 `Rank 1~37` 的已 `park` 条目里挑 1 条。近 `7` 天内刚复盘过的 `Rank 19 / 27 / 15 / 3 / 6 / 37 / 33 / 22 / 32 / 16 / 35 / 14 / 25 / 21 / 18 / 26 / 34 / 12 / 11 / 23 / 24 / 20 / 4 / 10 / 7 / 1 / 28` 先跳过；`Rank 31` 上一次 park-reframe 是 `2026-04-13 07:50 UTC`，已超出最近 `7` 天窗口，且队列里仍残留旧 `Rank 31b` active draft，适合做一次低频复核并收口。

## Read set
- `docs/BOT6_PARK_REFRAME_BRIEF.md`
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- source / prior rank evidence:
  - `research/optimization_loop/2026-03-17_1057_rank31-clean-replication-park.md`
  - `research/park_reframe/2026-04-13_0750_rank31-park-reframe.md`
  - `research/optimization_loop/2026-03-30_0456_rank246_survivor_followup_background.md`
  - `research/optimization_loop/2026-04-09_0424_rank31_stale_pending_duplicate_blocked.md`

## 1) 原 rank 为什么 park？
原 `Rank 31 / chanlun-pro second-buy / structural reclaim long continuation` 被 park 的原因没有变化：
- 原始 long reclaim 主变体在 `BTC/ETH/SOL 120d 15m 6bps/side` 的最小 clean replication 中是明确负值；
- `structural_higher_low_reclaim` 这条主写法 `mean_total_return≈-31.30%`、`positive_asset_ratio=0/3`；
- 更复杂的 `center_breakout_retest_reclaim` 更差，`mean_total_return≈-41.25%`；
- 同时 `mean_false_reclaim_ratio≈35.04%`，说明这类 reclaim 事件本身经常失败。

所以原 `park` 的审计含义很清楚：
> 被否掉的是“结构 reclaim 后直接做 long continuation”这层旧主语，不是所有 reclaim / failure 主题都没有信息。

## 2) 它更像 hard park 还是 soft park？
**本轮判断：`hard park`，而且比 4 月 13 日那轮更接近 `hard park with consumed residual`。**

原因不是主 blocker 变了，而是剩余空间继续被压缩：
1. 旧 long reclaim 写法没有任何新证据被修复；
2. 唯一自然 residual 仍只是历史上那一刀：`false structural reclaim -> short failure-followthrough`；
3. 但这条 residual 已不只是“draft 过”，而是已经在 runtime 被正式前排化成 `Rank 246`，做完唯一 survivor follow-up，并回到 `background/P0`；
4. `2026-04-09` 还进一步把重复 pending 明确收口为 `stale duplicate blocked`。

因此今天再看，`Rank 31` 已不只是“原主语 hard fail、残余还留一丝 soft 可能”，而是：
> **原主语 hard fail，且唯一软残余也已经被正式消费完。**

## 3) 有没有“可救信号”？
**没有未消费的可救信号。**

历史上唯一成立过的“可救信号”是：
- 既然 long reclaim 经常失败，是否应把它反过来写成 short failure-followthrough。

但这条信号现在已经不再是待验证机会，因为：
- `2026-03-30 04:56 UTC` 的 `Rank 246` survivor follow-up 已在同一冻结口径下给出干净负结论；
- `6bps/side` 下 `BTC/ETH/SOL` 三资产全负，`positive_asset_ratio=0/3`；
- `2026-04-09 04:24 UTC` 又明确确认：这不是尚未处理的新 intake，而是过期重复项。

所以当前如果继续说 `Rank 31` 还有“可救信号”，实际上是在把**已经被 runtime 收口的旧 residual**误写成未消费的新机会。

## 4) 最值得改的唯一一刀是什么？
如果今天仍要回答“最值得改的唯一一刀”，答案仍然只有历史上那一刀：

> **把 `false structural reclaim` 反向交易成 short failure-followthrough。**

但关键点也在这里：
- 这不是新的修改轴；
- 它已经被正式分配为 `Rank 246`；
- 并且已在 survivor follow-up 里被成本后负结论关闭。

所以这刀如今只剩审计意义，不再是一个值得继续保留在 queue 里的 active derived hypothesis。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。本轮继续 `keep_park`。**

原因：
1. 原 `park` verdict 没有被推翻；
2. 原 long structural reclaim 的 hard fail 没有任何新证据修复；
3. 唯一诚实 residual 已被 `Rank 246` 前排化、验证并关闭；
4. runtime 还明确把后续重复开启判成 `stale duplicate blocked`；
5. 因此现在若继续保留 `Rank 31b` 或再写 `Rank 31c`，都只会重复开启一条已被消费完的旧 residual。

## 单轮审查模板回答
### 原 rank 为什么 park？
因为 `structural_higher_low_reclaim` 作为 long continuation 在最小 clean replication 中跨资产显著为负，且更复杂确认写法更差，未能形成可 admission 的成本后 pocket。

### 它更像 hard park 还是 soft park？
`hard park`，且比 4 月 13 日那轮更接近 `hard park with consumed residual`。

### 有没有“可救信号”？
历史上唯一可救信号是 `false reclaim -> short failure-followthrough`，但它已由 `Rank 246` 正式验证并关闭，因此当前没有未消费的可救信号。

### 最值得改的唯一一刀是什么？
仍只是历史上的那一刀：把 `false structural reclaim` 反向交易成 short failure-followthrough；但这条轴已被 `Rank 246` 消费完。

### 是否值得形成新的 derived hypothesis？
不值得。本轮继续 `keep_park`。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `hard park；原 long structural reclaim 的 blocker 没被推翻，而唯一诚实 residual（false reclaim -> short failure-followthrough）已被 Rank 246 正式前排化、做完 survivor follow-up 并回到 background/P0；2026-04-09 runtime 又把重复 pending 判成 stale duplicate blocked，因此当前应移除旧 Rank 31b active draft，而不是继续派生。`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## Commit
- 本轮不做 commit。
- 原因：git 工作区存在大量与本轮无关的共享脏文件 / 未跟踪文件；本轮只做最小必要文档改动，避免混提。
