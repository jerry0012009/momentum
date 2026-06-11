# 2026-04-24 02:46 UTC · Rank 30 park reframe

## Scope
- source rank: `Rank 30 / trendline paired-channel corridor breach`
- original status kept: `park`
- this round verdict: `keep_park`
- review reason:
  - 本轮继续按 `bot6` 低频规则，只处理 `Rank 1~37` 的 1 条已 `park` 条目；
  - `Rank 30` 上次 park-reframe 复盘是 `2026-04-17 14:06 UTC`，已超过 `7` 天；
  - 4 月 23 日又补了两类更贴近 `AVWAP / continuation host` 的新证据，适合再确认一次：这些证据是在救 old `corridor breach`，还是继续把它的残余价值外流到新的宿主。

## Files read this round
### Required
1. `docs/TODO.md`
2. `docs/PARK_REFRAME_QUEUE.md`
3. `docs/RECENT_PAPER_SEEDS.md`
4. `research/quant_digests/INDEX.md`
5. `research/park_reframe/INDEX.md`

### Recent park-reframe context
- `research/park_reframe/2026-04-23_2243_rank23-park-reframe.md`
- `research/park_reframe/2026-04-23_1949_rank11-park-reframe.md`
- `research/park_reframe/2026-04-23_1533_rank24-park-reframe.md`
- `research/park_reframe/2026-04-17_1406_rank30-park-reframe.md`

### Rank-specific source notes
- `research/optimization_loop/2026-03-17_1029_rank30-clean-replication-park.md`
- `research/optimization_loop/2026-04-09_1526_rank30b_fresh_intake_background_absorbed.md`

### Nearby evidence consulted
- `research/quant_digests/2026-03-18_1500_event-anchored-vwap-hold-gate.md`
- `research/quant_digests/2026-04-23_0419_anchored-vwap-regimeextreme-reversion-alpha.md`
- `research/quant_digests/2026-04-23_2036_ema20-pullback-swingbreak-continuation-alpha.md`

## What Rank 30 originally tried to do
原始 `Rank 30` 的主张一直很清楚：
- 先识别 `paired-channel / corridor`；
- 再等价格收盘真正穿出外轨，试图把它当成延续性 `breach`；
- 后续用 `reclaim_hold` 之类的二次确认，减少假突破。

一句话：
> 它赌的是“通道外突破 + 再确认”足以把 continuation 和假突破分开，而不是把突破事件改写成别的 raw-alpha 宿主。

## Why it was parked
原 clean replication 的 blocker 没变：
- `raw_corridor_breach @ 6bps/side` 约 `-10.73%`，`positive_asset_ratio=0/3`，`mean_false_break_ratio≈86.11%`；
- 主变体 `breach_plus_reclaim_hold @ 6bps/side` 约 `-7.33%`，`positive_asset_ratio=0/3`，`mean_false_break_ratio≈82.39%`；
- 它确实比 raw 版少亏，但没有把这条线拉回成本后可独立存活的 admission 门槛。

所以 old `Rank 30` 被 park，不是因为“结构/突破主题完全没信息”，而是因为：
1. 它只证明了 **确认层比裸 breach 更少亏**；
2. 没证明 old `corridor breach` 这具宿主已经能诚实地区分真假突破；
3. 唯一自然改单轴很快就会滑向更上位的 `post-event acceptance / hold-reclaim` family。

## Hard park or soft park?
**结论：仍是 `soft park`，但已经非常接近 `hard park with consumed residual`。**

为什么还留 `soft`：
- 原 replication 至少说明 `confirmation > raw breach`；
- 也就是说，`post-breach acceptance` 这个方向并非完全无效。

为什么又更接近 `hard`：
- old `Rank 30` 唯一自然残余，早已收敛成既有 `Rank 30b`；
- 而 `Rank 30b` 又在 `2026-04-09` fresh intake first verdict 中收口为 `background / P0 / absorbed`；
- 新近证据继续说明，AVWAP 与 continuation 主题若还能活，也更像新的明确宿主，而不是 old `corridor breach` 还能再诚实切出 `Rank 30c`。

## Is there a rescue signal?
**有，但仍然只是主题级可救信号，不是旧 rank 级可救信号。**

### A. event-anchored VWAP 旧旁证仍成立
`2026-03-18_1500_event-anchored-vwap-hold-gate.md` 已经给出 old residual 的最自然翻译：
- 真问题不是“多收一根还在不在通道外”，
- 而是“breach 之后，这段新库存的 volume-weighted cost line 有没有被守住”。

但这条 residual 已经被 `Rank 30b` 明确表达，并在 runtime 中收口为 family-absorbed。

### B. 4 月 23 日 AVWAP 新证据救的是新 raw alpha 宿主
`2026-04-23_0419_anchored-vwap-regimeextreme-reversion-alpha.md` 进一步说明：
- AVWAP 不只像 shared confirmation，甚至可以直接升成 `swing-anchor -> AVWAP deviation -> mean reversion` 的 raw alpha；
- 这等于把 AVWAP 主题继续往 **独立回归宿主** 推，而不是往 old `Rank 30` 的 corridor-breach confirmation 壳里拉回。

### C. 4 月 23 日 EMA20 pullback 再次说明 continuation 应活在完整 host
`2026-04-23_2036_ema20-pullback-swingbreak-continuation-alpha.md` 又从另一个角度强化同一件事：
- continuation 真正可交易时，更像 `EMA20 pullback -> swing re-break` 这类完整、可执行的 host；
- 各种确认层变量应该服务明确宿主，而不是反过来把“generic breach confirmation”继续排成一条独立 residual。

### 小结
因此本轮真正的可救信号只能写成：
> **post-breach acceptance / AVWAP / continuation 仍有信息，但它们更像新 raw-alpha 或明确 host-local confirmation；它们没有把 old `Rank 30` 的 corridor-breach 本体救回队列。**

## The single best modification axis
如果只允许保留 **1 条唯一主修改轴**，本轮答案仍然没有变化：

> **把 binary `breach_plus_reclaim_hold` 改写成 `breach-event anchored VWAP hold/reclaim`。**

但关键点也没有变化：
- 这条唯一自然的一刀已经被 `Rank 30b` 消费过；
- `Rank 30b` 也已在 runtime 中收口为 `background / absorbed`；
- 因此今天再写 `Rank 30c`，大概率只是在 body/wick/volume/time-window 语法里继续碰运气，而不是新的诚实单轴。

## Should this become a derived hypothesis now?
**不值得。最终结论：`keep_park`。**

原因：
1. **原 blocker 没被推翻。**
   - old `Rank 30` 仍然是假突破率过高、成本后三腿全负。
2. **唯一自然 residual 已被消费。**
   - `Rank 30b` 已把最自然的改单轴走完一轮，并被 runtime 收口为 family-absorbed。
3. **新证据救的是别的宿主。**
   - 4 月 23 日的新 AVWAP 与 continuation 旁证，都在把主题推向新的 raw-alpha / host-local confirmation family。
4. **原 `park` 的审计意义应保留。**
   - 原结论不是“结构确认完全无效”，而是“old corridor-breach 这具宿主不值得继续排队”。本轮新证据没有改变这一点。

## Trade on / trade off if revisited later
> 本轮不 draft，只记录若以后再碰该主题时，唯一还诚实的方向。

- trade on:
  - 保留 `post-event acceptance / AVWAP hold-reclaim / continuation confirmation` 仍可能对明确宿主提供增量；
  - 若以后要做，应直接写成新的 raw alpha 或明确 host-local confirmation。
- trade off:
  - 放弃 old `Rank 30` 的 standalone `corridor breach` 主语；
  - 也放弃再把已被消费的 `Rank 30b` 换语法包装成新的 queue-facing residual。

## Bottom line
1. **原 rank 为什么 park？**
   - 因为 `corridor breach` 的确认仍太粗，假突破率过高；即使 `reclaim_hold` 比 raw 版少亏，仍不足以形成成本后、跨资产的诚实存活。
2. **更像 hard 还是 soft park？**
   - 仍是 `soft park`，但已非常接近 `hard with consumed residual`。
3. **有没有可救信号？**
   - 有，但只是主题级：`post-breach acceptance / AVWAP / continuation` 仍有信息，不过它们活在新宿主，不活在 old `Rank 30` 的 corridor-breach 壳里。
4. **最值得改的唯一一刀是什么？**
   - 仍只是已被消费的那一刀：`breach-event anchored VWAP hold/reclaim`。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得；本轮保持 `keep_park` 更诚实。

## File-update / commit note
- 本轮只做 park-reframe 侧最小必要文档更新：本日志、`research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md`。
- 未改 `docs/TODO.md` 顶部排班。
- `git status` 显示共享工作区存在大量与本轮无关的脏文件，当前不适合做安全 selective commit，因此不提交。
