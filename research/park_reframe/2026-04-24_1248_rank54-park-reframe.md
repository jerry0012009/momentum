# 2026-04-24 12:48 UTC · Rank 54 park reframe

## Scope
- source rank: `Rank 54 / LVN rejection + POC acceptance gate`
- original status kept: `park`
- this round verdict: `keep_park`
- review reason:
  - 本轮继续按 `bot6` 低频规则，只处理 `Rank 1~37` 外的已 `park` queue-facing rank 中 1 条，优先补 `50~79` 且近 `7` 天未复盘的对象；
  - `Rank 54` 上次 park-reframe 复盘是 `2026-04-15 21:09 UTC`，已超过 `7` 天；
  - 4 月 18 日又新增了更完整的 `auction-profile / POC / LVN` 新证据，适合再确认一次：这些证据是在救 old `shared gate`，还是继续把 residual 外流到新的 raw-alpha 宿主。

## Files read this round
### Required
1. `docs/TODO.md`
2. `docs/PARK_REFRAME_QUEUE.md`
3. `docs/RECENT_PAPER_SEEDS.md`
4. `research/quant_digests/INDEX.md`
5. `research/park_reframe/INDEX.md`

### Recent park-reframe context
- `research/park_reframe/2026-04-24_0246_rank30-park-reframe.md`
- `research/park_reframe/2026-04-23_2243_rank23-park-reframe.md`
- `research/park_reframe/2026-04-15_2109_rank54-park-reframe.md`

### Rank-specific source notes
- `research/optimization_loop/2026-03-18_1104_rank54-source-intake-guard-passed.md`
- `research/optimization_loop/2026-03-18_1135_rank54-clean-replication-park.md`

### Nearby evidence consulted
- `research/quant_digests/2026-04-05_1755_poc-cvd-absorption-alpha.md`
- `research/quant_digests/2026-04-13_0940_midpoint-split-dual-lvn-range-reversion-alpha.md`
- `research/quant_digests/2026-04-18_0049_auction-profile-poc-lvn-shell.md`

## What Rank 54 originally tried to do
原始 `Rank 54` 的主张一直很明确：
- 不自己产生方向；
- 先要求 base setup 触到 `LVN` 并出现 rejection；
- 再进一步要求价格重新站回 `POC` 强侧，把这当作 shared `acceptance` confirm；
- 期待用这层 `LVN rejection + POC acceptance`，替趋势/回踩/回落线过滤掉低质量 entry。

一句话：
> 它赌的是“auction / profile 信息适合作为通用 shared confirmation gate”，而不是把 `POC / LVN` 自己写成 primary alpha 宿主。

## Why it was parked
原 clean replication 的 blocker 没变，而且比 4 月中旬读得更清楚：
- 主读法 `breakdown_reclaim_short + lvn_rejection_plus_poc_acceptance @ 6bps/side` 基本变成 `0` 笔交易，`mean_trade_count_retention = 0.00%`；
- 稍微宽一点的 `ema_pullback_long + lvn_rejection` 虽有约 `+1.40%` 的轻微 gross pocket，但只有 `1/3` 资产为正，`retention≈22.45%`；
- 一旦把 `POC acceptance` 真按题面写成 hard confirm，改善主要来自 **直接把样本砍没**，而不是挑出可交易 pocket。

所以 old `Rank 54` 被 park，不是因为 `volume-profile / auction` 主题完全失效，而是因为：
1. 它没有证明 `shared gate` 这个岗位成立；
2. 它证明得更像 `POC acceptance` 在当前 desk 约束下只是极窄 sample veto；
3. 真正有活性的 residual，越来越像新的单资产 auction / range / absorption 宿主，而不是 old gate 壳还能再诚实切一刀。

## Hard park or soft park?
**结论：仍是 `soft park`，但已比 2026-04-15 那轮更接近 `hard park with consumed residual`。**

为什么还留 `soft`：
- `POC / LVN / value-area` 这组 auction 变量本身没有死；
- 4 月 5~18 日的新证据继续说明，`POC-proximal absorption`、`dual-LVN range reversion`、`value-area re-entry / LVN traverse` 都可能留下 raw-alpha pocket。

为什么又更接近 `hard`：
- 这些 pocket 越来越明确地要求 **换宿主职责**；
- 它们救活的是 `auction-structure raw alpha / HTF anchor / child execution`，不是 old `Rank 54` 的 `shared lvn_rejection + poc_acceptance gate`；
- 对 old rank 来说，可救信号已经越来越像“主题外流”，不是“旧壳细修”。

## Is there a rescue signal?
**有，但仍然只是主题级可救信号，不是旧 rank 级可救信号。**

### A. POC-proximal absorption 旁证
`2026-04-05_1755_poc-cvd-absorption-alpha.md` 说明：
- `POC` 更像 `1H parent signal` / `fair-value anchor`；
- 真正值得保留的是“价格在 POC 一侧 + 流向背离 + absorption”的 raw-alpha 主语；
- 这不是在救 old `shared acceptance gate`，而是在说 `POC` 更适合做母锚点。

### B. dual-LVN range reversion 旁证
`2026-04-13_0940_midpoint-split-dual-lvn-range-reversion-alpha.md` 进一步说明：
- `LVN` 自己就可以是 entry anchor；
- 可测的是 `midpoint-split dual-LVN` 的单资产 range-reversion pocket；
- 这继续把 residual 往 `LVN as alpha` 推，而不是往 old `LVN as shared gate` 拉回。

### C. auction-profile shell 新旁证
`2026-04-18_0049_auction-profile-poc-lvn-shell.md` 又把这件事说得更完整：
- 真正自然的宿主，是 `value-area re-entry -> POC` 的回归腿，或 `LVN traverse -> next acceptance zone` 的穿越腿；
- `POC / VAH / VAL / LVN` 值得保留的方式，是完整 `auction-market raw alpha shell`；
- 这已经不再是“给别的 setup 做 allow/deny gate”的语言。

### 小结
因此本轮真正的可救信号只能写成：
> **auction / volume-profile 主题仍有信息，但它更像新的 `POC/VA/LVN` raw-alpha 或 HTF-anchor 宿主；它没有把 old `Rank 54` 的 shared gate 救回队列。**

## The single best modification axis
如果只允许保留 **1 条唯一主修改轴**，本轮最值得改的一刀只能是：

> **把 `POC/LVN` 从 shared acceptance gate，改写成 auction-structure primary host（优先 `value-area re-entry -> POC` 或 `LVN traverse`）。**

但关键点也因此更明确：
- 这不是 old `Rank 54` 的窄修正；
- 这是一条 **宿主职责迁移**；
- 如果今天硬把它写成 `Rank 54b`，本质是在把“新 raw-alpha 壳”误包装成“旧 gate 残余”。

## Should this become a derived hypothesis now?
**不值得。最终结论：`keep_park`。**

原因：
1. **原 blocker 没被推翻。**
   - old `Rank 54` 仍然是一旦把 `POC acceptance` 认真写进去，就坍缩成零交易或极薄 retention。
2. **新证据救的是新宿主。**
   - 4 月 5~18 日的新旁证都在把主题推向 `POC absorption`、`dual-LVN range reversion`、`auction-profile shell` 这类新 raw-alpha 宿主。
3. **distinctness 继续变弱。**
   - 现在若硬写 `Rank 54b`，最自然的写法会与新的 auction / value-area / LVN raw-alpha family 高重叠，而不是 old gate 的单轴残余。
4. **原 `park` 的审计意义应保留。**
   - 原结论不是“volume-profile 无效”，而是“old shared `LVN rejection + POC acceptance` gate 不值得继续排队”。本轮新证据没有改变这一点。

## Trade on / trade off if revisited later
> 本轮不 draft，只记录若以后再碰该主题时，唯一还诚实的方向。

- trade on:
  - 保留 `POC / value-area / LVN` 作为 auction 结构锚点，仍可能对单资产回归腿、穿越腿或 HTF-parent / LTF-child execution 提供增量；
  - 若以后要做，应直接写成新的 `auction-structure raw alpha` 或 `HTF anchor + child execution`。
- trade off:
  - 放弃 old `Rank 54` 的 standalone shared-gate 主语；
  - 也放弃再把“新宿主”包装成 queue-facing `Rank 54b` residual。

## Bottom line
1. **原 rank 为什么 park？**
   - 因为 `LVN rejection + POC acceptance` 作为 shared gate 主要靠把样本砍到极薄甚至归零，并没有形成成本后、跨资产的可交易 pocket。
2. **更像 hard 还是 soft park？**
   - 仍是 `soft park`，但已比 4 月 15 日那轮更接近 `hard with consumed residual`。
3. **有没有可救信号？**
   - 有，但只是主题级：auction / volume-profile 仍有信息，不过它活在新的 `POC / VA / LVN` raw-alpha 或 HTF-anchor 宿主上，不活在 old shared gate 壳里。
4. **最值得改的唯一一刀是什么？**
   - 把 `POC/LVN` 从 shared gate，改写成 `value-area re-entry -> POC` 或 `LVN traverse` 这类 auction-structure primary host。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得；本轮保持 `keep_park` 更诚实。

## File-update / commit note
- 本轮只做 park-reframe 侧最小必要文档更新：本日志、`research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md`。
- 未改 `docs/TODO.md` 顶部排班。
- `git status` 显示共享工作区存在大量与本轮无关的脏文件，当前不适合做安全 selective commit，因此不提交。
