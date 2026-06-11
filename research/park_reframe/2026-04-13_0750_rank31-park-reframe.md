# 2026-04-13 07:50 UTC · Rank 31 park reframe review

## 本轮对象
- `Rank 31 / chanlun-pro second-buy / structural reclaim long continuation`
- 原始结论保留：`park / evidence pool`
- 本轮输出：`keep_park`

## 为什么这轮看 Rank 31
- 本轮只复盘 1 条已 `park` rank。
- 虽然 `Rank 31` 在 `2026-04-06 08:17 UTC` 刚被 bot6 复盘过，按默认规则本应尽量避开最近 7 天重复认领；
- 但这条线在上轮之后出现了**会改变 residual 读法的 runtime 新证据**：
  - `research/optimization_loop/2026-04-09_0424_rank31_stale_pending_duplicate_blocked.md`
- 这份 runtime truth 明确补齐了一个关键事实：`Rank 31` 唯一诚实 residual（`false structural reclaim -> short failure-followthrough`）不只是“已经 draft 过”，而且已经在 `Rank 246` 里被正式前排化、做完唯一 survivor follow-up、并回到 `background/P0`。
- 因此本轮只回答一件事：这条新 runtime 事实，是否把 `Rank 31` 从“hard park with consumed residual”进一步推向更接近纯 hard park。

## Read set
- `docs/BOT6_PARK_REFRAME_BRIEF.md`
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent park-reframe references:
  - `research/park_reframe/2026-04-13_0517_rank29-park-reframe.md`
  - `research/park_reframe/2026-04-13_0221_rank37-park-reframe.md`
  - `research/park_reframe/2026-04-12_2350_rank4-park-reframe.md`
- source / prior rank evidence:
  - `research/optimization_loop/2026-03-17_1057_rank31-clean-replication-park.md`
  - `research/park_reframe/2026-04-06_0817_rank31-park-reframe.md`
  - `research/optimization_loop/2026-03-30_0439_rank246_false_reclaim_short_intake_keep_p1.md`
  - `research/optimization_loop/2026-03-30_0456_rank246_survivor_followup_background.md`
  - `research/optimization_loop/2026-04-09_0424_rank31_stale_pending_duplicate_blocked.md`

## 1) 原 rank 为什么 park？
原 `Rank 31` 被 park 的核心 blocker 没变：把 `structural_higher_low_reclaim` 写成 **long continuation**，最小 clean replication 在 desk 口径下明显站不住。

`2026-03-17_1057_rank31-clean-replication-park.md` 的关键结果：
- `raw_pullback_recovery_baseline`: `mean_total_return≈-15.46%`，`positive_asset_ratio=1/3`
- `structural_higher_low_reclaim`: `mean_total_return≈-31.30%`，`positive_asset_ratio=0/3`
- `center_breakout_retest_reclaim`: `mean_total_return≈-41.25%`，`positive_asset_ratio=0/3`
- 同时主变体还有：`mean_false_reclaim_ratio≈35.04%`

所以原 `park` 的审计意义很清楚：
> 被否掉的是“结构 reclaim 后直接做 long continuation”这层旧主语，不是所有 reclaim / failure 主题都没信息。

## 2) 它更像 hard park 还是 soft park？
**本轮判断：更像 `hard park`；比 4 月 6 日那轮又更硬一点。**

4 月 6 日那轮还能说：
- 原 long-entry 已是 hard park；
- 但仍有一条已经被消费掉的 soft residual，即 `false reclaim -> short failure-followthrough`。

而 4 月 9 日的 runtime truth 又补了一刀：
- 这条 residual 不只被 draft 成 `Rank 31b`；
- 它已经被正式前排化为 `Rank 246`；
- 且在唯一 survivor follow-up 里，`6bps/side` 下三资产全负，随后已正式回 `background/P0`；
- runtime 甚至进一步把后续重复 pending 直接标成 `stale duplicate blocked`。

这意味着：
> `Rank 31` 不是“还有 soft residual 待将来找机会重开”，而是“唯一 soft residual 已被实盘化检验并消费完”。

## 3) 有没有“可救信号”？
**现在只剩历史上的“曾经有过可救信号”，但已没有未消费的可救信号。**

唯一曾经成立过的可救信号，就是：
- 原 long reclaim 失败率高（`false_reclaim_ratio≈35.04%`）；
- 因而值得把它倒过来，写成 short failure-followthrough。

但这条信号已经被后续 runtime 彻底消费：
1. `2026-03-30 04:39 UTC`：它被正式立项为 `Rank 246`
2. `2026-03-30 04:56 UTC`：在 survivor follow-up 中，`BTC/ETH/SOL` 于 `6bps/side` 全负，收口为 `background/P0`
3. `2026-04-09 04:24 UTC`：进一步确认不存在新的 `Rank 31c`；重复 pending 直接按 stale duplicate blocked 处理

因此今天如果再说 `Rank 31` 仍有“可救信号”，就会把**已经被验证为不成立的 residual**误写成还没做过的机会。

## 4) 最值得改的唯一一刀是什么？
如果今天还要回答“最值得改的唯一一刀是什么”，答案仍然只能是历史那一刀：

> **把 `false structural reclaim` 反向交易成 short failure-followthrough。**

但这轮关键判断也恰恰在这里：
- 这刀不是新的；
- 它已经被 `Rank 246` 正式验证并失败关闭；
- 因此它已不再是“值得继续提案的修改轴”，而只是原 rank 审计链条里**已经消费完的唯一残余**。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。本轮继续 `keep_park`。**

原因：
1. 原 `park` verdict 没有被推翻；
2. 原 long structural reclaim 的 hard fail 没有任何新证据修复；
3. 唯一诚实 residual 已被 `Rank 246` 前排化、做完唯一 follow-up，并回到 `background/P0`；
4. 4 月 9 日的 blocked runtime 进一步证明：当前若再写 `Rank 31c`，只会变成重复开启一个已收口的旧 residual。

## 单轮审查模板回答
### 原 rank 为什么 park？
因为 `structural_higher_low_reclaim` 作为 long continuation 在 `BTC/ETH/SOL 120d 15m 6bps/side` 的最小 clean replication 中三档都未过线，主变体跨资产显著为负。

### 它更像 hard park 还是 soft park？
`hard park`；而且比 4 月 6 日那轮更接近“纯 hard park”，因为唯一 residual 也已被 runtime 消费完。

### 有没有“可救信号”？
历史上有过——`false reclaim -> short failure-followthrough`；但这条信号已在 `Rank 246` 中被正式检验并失败关闭，因此当前没有未消费的可救信号。

### 最值得改的唯一一刀是什么？
仍只是历史上那一刀：把 `false structural reclaim` 反向交易成 short failure-followthrough；但它已经被 `Rank 246` 消费，不再是新的可提案修改轴。

### 是否值得形成新的 derived hypothesis？
不值得。本轮继续 `keep_park`。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `hard park；原 long structural reclaim 的 blocker 没被推翻，而唯一诚实 residual（false reclaim -> short failure-followthrough）已被 Rank 246 正式前排化、做完唯一 survivor follow-up 并回到 background/P0；4 月 9 日 runtime 进一步确认不存在新的 Rank 31c，因此当前不诚实再派生。`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## Commit
- 本轮不做 commit。
- 原因：git 工作区存在大量与本轮无关的共享脏文件 / 未跟踪文件；本轮只做最小必要文档改动，避免混提。
