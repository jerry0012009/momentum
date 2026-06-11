# 2026-04-24 21:13 UTC · Rank 53 park reframe

## Scope
- source rank: `Rank 53 / close-confirmed CHoCH compression gate`
- original status kept: `park`
- this round verdict: `keep_park`
- review reason:
  - 按 `bot6` 低频规则，本轮只处理 `1` 条已 `park` rank；
  - `Rank 53` 上次 park-reframe 复盘是 `2026-04-15 18:22 UTC`，已超过 `7` 天；
  - 4 月 21~23 又出现了几条更贴近“recent-return continuation / event-conditioned drift / pullback→swing-break continuation”的旁证，适合再确认一次：这些新证据是在救 old `Rank 53`，还是继续把它的 residual value 推向新的 raw-alpha 宿主。

## Files read this round
### Required
1. `docs/TODO.md`
2. `docs/PARK_REFRAME_QUEUE.md`
3. `docs/RECENT_PAPER_SEEDS.md`
4. `research/quant_digests/INDEX.md`
5. `research/park_reframe/INDEX.md`

### Recent park-reframe context
- `research/park_reframe/2026-04-24_1851_rank36-park-reframe.md`
- `research/park_reframe/2026-04-24_0246_rank30-park-reframe.md`
- `research/park_reframe/2026-04-23_2243_rank23-park-reframe.md`
- `research/park_reframe/2026-04-15_1822_rank53-park-reframe.md`

### Rank-specific source notes
- `research/optimization_loop/2026-03-18_1102_rank53-clean-replication-park.md`

### Nearby evidence consulted
- `research/quant_digests/2026-04-23_2036_ema20-pullback-swingbreak-continuation-alpha.md`
- `research/quant_digests/2026-04-23_2251_abnormal-day-intraday-momentum-alpha.md`
- `research/quant_digests/2026-04-21_2332_intraday-momrev-regimeswitch-alpha.md`

## What Rank 53 originally tried to do
原始 `Rank 53` 的主语并不是完整 raw alpha，而是一条 shared structural failure / continuation gate：
- 上层用 `1h confirmed pivot close` 去定义 CHoCH / sweep；
- 下层不自己发明方向，只给既有 archetype（如 `ema_pullback_long`、`breakdown_reclaim_short`）加一个“不要被单次 wick / sweep 假翻向骗到”的结构 veto；
- 最关键的语义是：**至少等 confirmed close，再决定是否真翻结构；否则视作 compression / no-flip。**

一句话：
> old `Rank 53` 赌的是“close-confirmed CHoCH` 作为 shared gate，能把 continuation 与假翻向分开”。

## Why it was parked
原 clean replication 的 blocker 没变：
- `breakdown_reclaim_short + liquidity_sweep_veto @ 6bps/side ≈ -2.88%`
- `positive_asset_ratio = 0/3`
- `mean_trade_count_retention ≈ 39.97%`
- `mean_false_hold_4bars_rate ≈ 36.38%`
- 对照 `breakdown_reclaim_short + base @ 6bps/side ≈ -3.55%`

即使是相对更好看的 long pocket：
- `ema_pullback_long + liquidity_sweep_veto ≈ +0.43%`
- 也只有 `positive_asset_ratio = 1/3`
- `mean_trades ≈ 6.33`
- `trade_count_retention ≈ 37.73%`

所以 old `Rank 53` 被 park，不是因为“结构确认后 drift”这个母主题完全没信息，而是因为：
1. 它主要做到的是 **砍掉很多交易后少亏一点**；
2. 没证明 `close-confirmed CHoCH` 这层 shared gate 能跨资产、成本后稳定挑出可交易 pocket；
3. 一旦再往前推，很容易滑向新的 `structure-confirmed continuation` raw-alpha 宿主，而不是 old rank 本体。

## Hard park or soft park?
**本轮结论仍是：`keep_park`，且现在更像 `soft park`，但已更接近 `hard park with consumed residual`。**

为什么还没直接写成纯 hard：
- `confirmed close > wick poke` 这条审计结论仍成立；
- 也就是说，old rank 至少证明了“不要把未确认 sweep 直接当真翻向”。

为什么又更接近 hard：
- 这层 residual 越来越像研究 hygiene / host-local structural note，而不是 queue-facing hypothesis；
- 4 月 21~23 的新证据继续支持“结构确认后 continuation 仍有信息”，但它们给出的主语已经是 **新的 raw-alpha 宿主**，而不是 old `shared CHoCH gate` 本体。

## Is there a rescue signal?
**有，但仍然只是主题级可救信号，不是旧 rank 级可救信号。**

### A. EMA20 回踩 × 摆点再突破
`2026-04-23_2036_ema20-pullback-swingbreak-continuation-alpha.md` 说明：
- continuation 真正可交易时，更像“趋势壳 + 浅回踩 + 短摆点再突破”的完整 host；
- 结构确认不是独立 shared veto 主语，而是 raw alpha 触发的一部分。

### B. abnormal-return event gate
`2026-04-23_2251_abnormal-day-intraday-momentum-alpha.md` 说明：
- 真正有价值的是“异常日 / 异常时段之后的事件门控 continuation”；
- 也就是先有异常事件，再看后半段 drift，而不是 generic `close-confirmed CHoCH` 自己就能构成独立排队项。

### C. recent-return continuation × regime switch
`2026-04-21_2332_intraday-momrev-regimeswitch-alpha.md` 说明：
- 同一个 recent-return 信号会在 jump / event / liquidity 条件下切换 continuation 与 reversal；
- 这进一步把结构语言推向 `raw alpha + router / regime switch` 的宿主，而不是救活 old `Rank 53` 这种 shared gate 写法。

### 小结
因此本轮真正的可救信号只能写成：
> **结构确认后 drift 仍有信息，但它更像新的 event-defined / pullback-resumption / router-aware continuation host；它没有把 old `Rank 53` 的 shared CHoCH compression gate 救回队列。**

## The single best modification axis
如果只允许保留 **1 条唯一主修改轴**，本轮答案仍然只能是：

> **把 `shared close-confirmed CHoCH / liquidity-sweep veto` 升格为“confirmed structure -> continuation` 的 primary trigger / raw-alpha 宿主。**

但这恰好也是为什么本轮不能 draft：
- 一旦这么改，主语已经不再是 old `Rank 53`；
- 它变成新的 `structure-confirmed continuation` / `pullback→re-break` / `event-conditioned drift` family intake；
- 这超出了对 old rank 的诚实窄派生边界。

## Should this become a derived hypothesis now?
**不值得。最终结论：`keep_park`。**

原因：
1. **原 blocker 没被推翻。** old `Rank 53` 仍主要靠 retention 压缩减亏，没有跨资产 survival pocket。
2. **新证据救的是新宿主。** 4 月 21~23 的新旁证都在把主题推向新的 raw-alpha / router 宿主。
3. **distinctness 不够。** 若今天硬写 `Rank 53b`，本质会把“新的 primary trigger family”误包装成“旧 shared gate 的窄 reframe”。
4. **原 park 的审计意义应保留。** old `Rank 53` 最值钱的遗产仍是：**别让 wick / 单次 sweep 把 15m 结构直接翻面。** 这是一条研究 hygiene note，不足以再次排成 queue-facing candidate。

## Trade on / trade off if revisited later
> 本轮不 draft，只记录若以后再碰这个主题，什么才是诚实边界。

- trade on:
  - 保留“confirmed structure 后的 drift”仍可能作为新 raw alpha / router family 的入口；
  - 结构确认可继续服务新的 pullback-resumption、event-conditioned continuation、re-break host。
- trade off:
  - 放弃 old `Rank 53` 作为 standalone shared gate 的 queue-facing 身份；
  - 也放弃把 `close-confirmed CHoCH` 继续包装成 `Rank 53b` 这类旧 rank 窄派生。

## Bottom line
1. **原 rank 为什么 park？**
   - 因为 `close-confirmed CHoCH / liquidity-sweep veto` 只做到砍样本减亏，没有做到跨资产、成本后、不过度稀疏的 survival。
2. **更像 hard 还是 soft park？**
   - 仍更像 `soft park`，但已继续向 `hard with consumed residual` 靠拢。
3. **有没有可救信号？**
   - 有，但只是主题级：结构确认后 continuation / event-conditioned drift 仍有信息，不过它们活在新的 raw-alpha / router 宿主里。
4. **最值得改的唯一一刀是什么？**
   - 只能是把 shared CHoCH gate 升格成新的 primary-trigger host；但这已不属于 old `Rank 53` 的诚实派生。
5. **是否值得形成新的 derived hypothesis？**
   - **不值得；本轮继续 `keep_park`。**

## File-update / commit note
- 本轮只做 park-reframe 侧最小必要文档更新：本日志、`research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md`。
- 未改 `docs/TODO.md` 顶部排班。
- 共享工作区存在与本轮无关的脏文件，本轮不做 commit，避免混提。
