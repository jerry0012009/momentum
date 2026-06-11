# 2026-04-18 08:30 UTC · Rank 12 park reframe

## Scope
- source rank: `Rank 12 / averaged S/R zone + context gate`
- original status kept: `park`
- this round verdict: `keep_park`
- review reason: 本轮按 `50~79 -> 80~110 -> 1~24 -> 25~49` 轮转，`50+` 与 `80~110` 近几天已高频覆盖；在 `1~24` 中优先避开最近 `7` 天内刚复盘过的对象后，`Rank 12` 上次 `bot6` 复盘为 `2026-04-11 08:18 UTC`，已刚好超过 `7` 天窗口，且 4 月 18 日新增了更明确的 volume-profile / auction-structure 旁证，适合做一次最小复核。

## Files read this round
### Required
1. `docs/TODO.md`
2. `docs/PARK_REFRAME_QUEUE.md`
3. `docs/RECENT_PAPER_SEEDS.md`
4. `research/quant_digests/INDEX.md`
5. `research/park_reframe/INDEX.md`

### Recent park-reframe context
- `research/park_reframe/2026-04-18_0602_rank11-park-reframe.md`
- `research/park_reframe/2026-04-18_0403_rank74-park-reframe.md`
- `research/park_reframe/2026-04-18_0146_rank77-park-reframe.md`

### Rank-specific source notes
- `research/optimization_loop/2026-03-17_0011_rank12-clean-replication-park.md`
- `research/park_reframe/2026-04-11_0818_rank12-park-reframe.md`
- `research/optimization_loop/2026-04-09_0811_rank12b_fresh_intake_background_absorbed.md`

### Nearby evidence consulted
- `research/quant_digests/2026-04-18_0049_auction-profile-poc-lvn-shell.md`

## What Rank 12 originally tried to do
原始 `Rank 12` 想把 `averaged support/resistance zone + context` 写成一条可直接承担 `15m` 入场职责的 standalone strategy body：
- 先从历史价格压出 averaged zone；
- 再配合 context gate 解释“哪里值得做 breakout / retest / 反身 continuation”；
- 最终把 zone 本身当成 queue-facing 主语。

直白说：它赌的是“把 S/R zone 平滑化 + contextualize 后，就能自己长成一条可交易 entry alpha”。

## Why it was parked
原 clean replication 的审计结论没变：
- `winner_variant = averaged_zone_context_gate`；
- `6bps/side` 下 `mean_total_return ≈ -4.34%`；
- `positive_asset_ratio = 1/3`；
- Light Stability Pack 四项全 fail：时间 `0/3`、参数 `0/5`、跨标的 `1/3`、成本 `0/4`。

所以它被 park，不是因为 `zone / S/R / anchor` 主题整体死亡，而是因为：
- **失败对象是 old Rank 12 的 standalone zone-entry 角色本身**；
- 问题不再是“zone 宽度再调一档”或“再补一层 context”就能修；
- 原 rank 没证明自己能形成够厚、够稳、够可迁移的 strategy body。

## Hard park or soft park?
**仍更像 `soft park`，但对旧 Rank 12 本体已更接近 `hard park with consumed residual`。**

原因：
1. 主题层面上，`zone / anchor` 仍可能有信息；
2. 但旧 rank 的唯一诚实 residual 早已被 `Rank 12b` 收敛；
3. `2026-04-09` 的 runtime truth 又已把 `Rank 12b` first verdict 收口为 `background / P0 / absorbed`，说明这条 residual 已经不够独立，不值得再挂成新的 queue-facing intake。

## Is there any rescue signal?
**有主题级残余，但不再属于旧 `Rank 12` 的可继续派生空间。**

本轮新增旁证 `2026-04-18_0049_auction-profile-poc-lvn-shell.md` 反而把这点说得更清楚：
- volume-profile / auction 主题若还有价值，更像 `value-area re-entry -> POC mean reversion` 或 `LVN traverse -> acceptance breakout` 这种 **完整 raw-alpha shell**；
- 也就是以 `POC / value area / LVN` 为主语的 `auction-structure mother signal`；
- 而不是继续给旧 `averaged zone + context gate` 补丁。

换句话说：
- 市场并不是不给 `anchor / zone` 主题预算；
- 但预算更像会给新的 `auction-market raw-alpha / child-execution` 宿主；
- 不会再给 old Rank 12 这条 `15m shared/standalone zone gate` 续命。

## The single best modification axis
如果只保留唯一一刀，本轮答案仍然**没有变化**：

**`demote standalone averaged support/resistance zone + context entry into a volume-weighted zone-persistence shared quality gate`**

也就是：旧 Rank 12 的唯一自然 residual 仍只到既有 `Rank 12b`。

为什么这次不形成新的第二刀：
- `auction profile / POC / LVN` 新证据虽然重要，但它已经同时改了主语、宿主与职责层；
- 那不是“在 Rank 12 上补一刀”，而是在借 old Rank 12 的壳命名一条新的 auction-structure raw alpha；
- 这违反本轮只允许保留 **1 条唯一主修改轴** 的约束。

## Should this become a derived hypothesis now?
**不值得。结论：`keep_park`。**

原因：
1. 原 `park` verdict 没被推翻；
2. 旧 rank 的唯一诚实 residual 仍只到既有 `Rank 12b`；
3. `Rank 12b` 又已在 4 月 9 日被 runtime truth 收口为 `background / P0 / absorbed`；
4. 4 月 18 日新增的 `auction / POC / LVN` 证据，救活的是新的 `auction-structure raw-alpha shell`，不是旧 `Rank 12` 的 `Rank 12c`。

## Bottom line
1. **原 rank 为什么 park？**
   - 因为 `averaged zone + context` 作为 standalone zone-entry skeleton，在收益、稳定性、跨资产与成本口径上一起失败。
2. **更像 hard 还是 soft park？**
   - 主题层面仍算 `soft park`，但对旧 Rank 12 本体已更接近 `hard park with consumed residual`。
3. **有没有可救信号？**
   - 有，但只存在于新的 `auction-market / volume-profile / child-execution` raw-alpha 宿主，不属于旧 Rank 12 本体。
4. **最值得改的唯一一刀是什么？**
   - 仍只到既有 `Rank 12b`：把 standalone zone-entry 降级成 `volume-weighted zone-persistence shared quality gate`。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得；当前继续 `keep_park` 更诚实。

## File-update / commit note
- 本轮只做 park-reframe 侧最小必要文档更新：本日志、`research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md`。
- 未尝试 git commit：共享工作区长期存在大量与本轮无关的脏文件，当前不适合安全 selective commit。
