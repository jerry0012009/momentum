# 2026-04-25 09:11 UTC · Rank 12 park reframe

## Scope
- source rank: `Rank 12 / averaged S/R zone + context gate`
- original status kept: `park`
- this round verdict: `keep_park`
- review reason:
  - 本轮只处理 `1` 条已 `park` rank；
  - 用户约束限定在 `Rank 1~37` 内复盘；
  - `Rank 12` 上次 park-reframe 复盘为 `2026-04-18 08:30 UTC`，已刚好超过 `7` 天窗口；
  - 4 月 23 日又新增了更贴近 `anchor / fairness` 主题的旁证，适合最小复核一次：这些新证据是在救 old `Rank 12`，还是继续把它的 residual value 推向新的 raw-alpha 宿主。

## Files read this round
### Required
1. `docs/TODO.md`
2. `docs/PARK_REFRAME_QUEUE.md`
3. `docs/RECENT_PAPER_SEEDS.md`
4. `research/quant_digests/INDEX.md`
5. `research/park_reframe/INDEX.md`

### Recent park-reframe context
- `research/park_reframe/2026-04-24_2113_rank53-park-reframe.md`
- `research/park_reframe/2026-04-18_0830_rank12-park-reframe.md`

### Rank-specific source notes
- `research/optimization_loop/2026-03-17_0011_rank12-clean-replication-park.md`
- `research/optimization_loop/2026-04-09_0811_rank12b_fresh_intake_background_absorbed.md`

### Nearby evidence consulted
- `research/quant_digests/2026-04-18_0049_auction-profile-poc-lvn-shell.md`
- `research/quant_digests/2026-04-23_0419_anchored-vwap-regimeextreme-reversion-alpha.md`

## What Rank 12 originally tried to do
原始 `Rank 12` 想把 `averaged support/resistance zone + context` 写成一条能直接承担 `15m` 入场职责的 standalone strategy body：
- 先从历史价格压出 averaged zone；
- 再加一层 context，解释哪里更像 breakout / retest / continuation；
- 最后让 zone 本身承担 queue-facing 主语。

一句话：
> old `Rank 12` 赌的是“平滑化后的 S/R zone + context` 本身就能长成可交易 entry alpha”。

## Why it was parked
原 clean replication 的 blocker 没变：
- `winner_variant = averaged_zone_context_gate`
- `6bps/side mean_total_return ≈ -4.34%`
- `positive_asset_ratio = 1/3`
- Light Stability Pack 四项全 fail：时间 `0/3`、参数 `0/5`、跨标的 `1/3`、成本 `0/4`

所以它被 `park`，不是因为 `zone / anchor / fairness` 主题完全没信息，而是因为：
1. old `Rank 12` 没证明 standalone zone-entry skeleton 本身有足够厚的成本后 edge；
2. 失败不再像“zone 宽度再调一档”就能补；
3. 一旦继续往前推，就容易滑成新的 anchor-based raw alpha，而不是 old rank 的诚实窄派生。

## Hard park or soft park?
**本轮判断仍是：更像 `soft park`，但对旧 `Rank 12` 本体已进一步接近 `hard park with consumed residual`。**

为什么还不是纯 hard：
- `zone / anchor` 主题并未死亡；
- 市场仍会为“公平价锚 / 价值区 / 回归锚”给预算。

为什么又更接近 hard：
- old `Rank 12` 的唯一自然 residual 仍只到既有 `Rank 12b`；
- `Rank 12b` 又已在 `2026-04-09` 收口为 `background / P0 / absorbed`；
- 说明旧 rank 的剩余信息量已经不够再支撑新的 queue-facing reframe。

## Is there any rescue signal?
**有主题级可救信号，但没有旧 rank 级可救信号。**

### A. 4 月 18 日的 auction / POC / LVN 旁证
`2026-04-18_0049_auction-profile-poc-lvn-shell.md` 已经指出：
- zone / anchor 如果还有价值，更像 `auction-structure raw alpha`；
- 主语应是 `POC / value area / LVN acceptance / rejection`；
- 而不是继续给 old `averaged zone + context gate` 打补丁。

### B. 4 月 23 日的 anchored VWAP 回归旁证
`2026-04-23_0419_anchored-vwap-regimeextreme-reversion-alpha.md` 进一步把这点钉实：
- `anchor` 主题还活，但更像 `swing-anchored VWAP deviation -> reclaim` 的 **独立 raw alpha**；
- 它直接把 anchor 提升成公平价锚，而不是 old `Rank 12` 那种 shared / standalone averaged zone gate；
- 这等于再次说明：主题活着，不代表 old host 值得续命。

换句话说：
- 市场仍然愿意为 `anchor / zone / fairness` 买单；
- 但它买的是新的 `auction / AVWAP / explicit-anchor` 宿主；
- 不是 old `Rank 12` 这条 averaged zone-context 线。

## The single best modification axis
如果只保留唯一一刀，本轮答案**仍没有变化**：

**`demote standalone averaged support/resistance zone + context entry into a volume-weighted zone-persistence shared quality gate`**

也就是：旧 `Rank 12` 的唯一自然 residual 仍只到既有 `Rank 12b`。

为什么这轮不应再写 `Rank 12c`：
- `auction / POC / LVN` 和 `anchored VWAP` 新证据都已经换了主语；
- 它们改的不是 old `Rank 12` 的“一刀”，而是在借旧主题外壳，转写成新的 raw-alpha 宿主；
- 这不符合本轮“最多 1 条唯一主修改轴，且不能推翻原 park 审计意义”的约束。

## Should this become a derived hypothesis now?
**不值得。结论：`keep_park`。**

原因：
1. 原 `park` verdict 没被推翻；
2. old `Rank 12` 的唯一诚实 residual 仍只到既有 `Rank 12b`；
3. `Rank 12b` 已被 runtime truth 收口为 `background / P0 / absorbed`；
4. 最新旁证救活的是新的 `auction-structure / anchored-VWAP raw-alpha` 宿主，不是 old `Rank 12` 的 `Rank 12c`。

## Bottom line
1. **原 rank 为什么 park？**
   - 因为 `averaged zone + context` 作为 standalone zone-entry skeleton，在收益、稳定性、跨资产与成本口径上一起失败。
2. **更像 hard 还是 soft park？**
   - 仍是 `soft park`，但对旧 Rank 12 本体已更接近 `hard park with consumed residual`。
3. **有没有可救信号？**
   - 有，但只存在于新的 `auction / AVWAP / explicit-anchor` raw-alpha 宿主，不属于旧 Rank 12 本体。
4. **最值得改的唯一一刀是什么？**
   - 仍只到既有 `Rank 12b`：把 standalone zone-entry 降级成 `volume-weighted zone-persistence shared quality gate`。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得；当前继续 `keep_park` 最诚实。

## File-update / commit note
- 本轮只做 park-reframe 侧最小必要文档更新：本日志、`research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md`。
- 未做 git commit：共享工作区长期存在大量与本轮无关的脏文件，当前不适合安全 selective commit。
