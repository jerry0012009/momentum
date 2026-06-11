# 2026-04-23 22:43 UTC · Rank 23 park reframe

## Scope
- source rank: `Rank 23 / volatility regime mid-band / cost-survival gate`
- original status kept: `park`
- this round verdict: `keep_park`
- review reason:
  - 本轮继续按 `Rank 1~37` 已 `park` 条目低频复盘；
  - `Rank 23` 虽在近一周看过，但 4 月 21~23 又出现了更贴近 `market-quality / market-characteristics` 的新证据，因此这轮主要确认：这些新证据是在救旧 `rv_midband` shared gate，还是继续把它的 residual 推向新的宿主。

## Files read this round
### Required
1. `docs/TODO.md`
2. `docs/PARK_REFRAME_QUEUE.md`
3. `docs/RECENT_PAPER_SEEDS.md`
4. `research/quant_digests/INDEX.md`
5. `research/park_reframe/INDEX.md`

### Recent park-reframe context
- `research/park_reframe/2026-04-23_1949_rank11-park-reframe.md`
- `research/park_reframe/2026-04-23_1533_rank24-park-reframe.md`
- `research/park_reframe/2026-04-23_1309_rank10-park-reframe.md`
- `research/park_reframe/2026-03-27_0430_rank23-park-reframe.md`

### Rank-specific source notes
- `research/optimization_loop/2026-03-17_0503_rank23-clean-replication-park.md`

### Nearby evidence consulted
- `research/quant_digests/2026-04-21_0946_hl-marketquality-shared-gate-overlay.md`
- `research/quant_digests/2026-04-23_1249_global-intraday-tsmom-marketchar-portability.md`

## What Rank 23 originally tried to do
原始 `Rank 23` 的主张很明确：
- 不自己发明新的方向触发；
- 只把 `realized-vol mid-band / no-high-vol-extreme` 写成 `15m` shared volatility regime gate；
- 期待通过避开极端高波动、只保留“中间波动带”，让原本的趋势/延续线在成本后更能活下来。

一句话：
> 它赌的是“先把波动环境筛干净，baseline 自然会变诚实”，而不是把 volatility 信息附着到一个更明确的 raw-alpha 宿主上。

## Why it was parked
原 clean replication 的 blocker 仍然没有变化：
- `baseline_mtf @ 6bps/side ≈ -38.69%`；
- `no_high_vol_extreme ≈ -43.30%`；
- 主变体 `rv_midband_q20_80 ≈ -33.33%`，`positive_asset_ratio = 0/3`；
- 更窄的 `rv_midband_q30_70 ≈ -31.75%`，但主要代价是 `mean_no_trade_ratio ≈ 63.71%`；
- 时间稳定性 `0/3`，参数邻域最佳仍为负，成本抬升到 `10/15/20bps` 后继续恶化。

所以 old `Rank 23` 被 park，不是因为“volatility 完全没信息”，而是因为：
1. 它主要做到的是 **少做一点，所以少亏一点**；
2. 没证明这套 `rv_midband` shared gate 能稳定挑出成本后可交易 pocket；
3. 它缺的不是再调一个 quantile，而是 **岗位放错层级**。

## Hard park or soft park?
**结论：仍是 `soft park`，但对旧 `Rank 23` 本体已更接近 `hard park with consumed residual`。**

为什么还留 `soft`：
- volatility / liquidity / market-quality 这层信息本身没被否掉；
- 新证据继续说明“什么波动环境更适合做 continuation / carry / fade”仍有信息。

为什么又更接近 `hard`：
- 这些信息越来越像明确 raw-alpha 或 execution 宿主上的 local admission / veto / size-down；
- 它们没有支持 old `Rank 23` 这种抽象 shared gate 还能独立保留一条 queue-facing residual。

## Is there a rescue signal?
**有，但仍然只是主题级可救信号，不是旧 rank 级可救信号。**

### A. market-quality gate 旁证
`2026-04-21_0946_hl-marketquality-shared-gate-overlay.md` 的关键信息是：
- 真正该保留的是 `roll spread / Amihud / premium tail` 这类 **market-quality veto / size-down**；
- 它服务的是 `premium fade / funding carry / breakout child-exec` 等明确宿主；
- 这不是在救 `rv_midband` shared gate，而是在说 **波动 / 流动性信息应该附着在明确交易主语上**。

### B. intraday momentum × market characteristics 旁证
`2026-04-23_1249_global-intraday-tsmom-marketchar-portability.md` 进一步强化同一方向：
- `recent-return continuation` 才是 base alpha；
- 高波动 / 流动性 / 信息离散这类变量更像 admission layer；
- 在 crypto `15m` 上，值得借的是 `market-characteristic gate` 的岗位拆法，而不是“generic vol band 本身就是主角”。

### 小结
因此本轮真正的可救信号只能写成：
> **volatility / market-quality 仍有信息，但它更像明确 continuation / carry / fade 宿主上的 local gate；它没有把 old `Rank 23` 的 `rv_midband` shared gate 救回队列。**

## The single best modification axis
如果只允许保留 **1 条唯一主修改轴**，那本轮最值得改的一刀只能是：

> **把 standalone `rv_midband` shared gate，降级成明确 intraday host 上的 market-quality / volatility-quality veto。**

也就是：
- trade on：保留 volatility / liquidity 对 tradeability、tail-loss、execution-quality 的信息；
- trade off：放弃 old `Rank 23` 作为 queue-facing shared gate 的独立身份。

但关键问题也更清楚：
- 这刀一落下，就已经更像新的 host-local overlay / execution layer；
- 它不是 old `Rank 23` 还能诚实切出的 `Rank 23b`；
- 如果今天硬 draft，只会把“主题迁移到新宿主”误包装成“旧 rank 窄派生”。

## Should this become a derived hypothesis now?
**不值得。最终结论：`keep_park`。**

原因：
1. **原 blocker 没被推翻。**
   - old `Rank 23` 仍没有跨资产、成本后、不过度砍样本的 survival pocket。
2. **新证据救的是岗位迁移，不是旧壳重开。**
   - 4 月 21~23 的新旁证都在说明：volatility / market-quality 应该服务明确 raw alpha 或 execution 宿主。
3. **distinctness 继续变弱。**
   - 现在若硬写 `Rank 23b`，最自然的写法会与新的 market-quality overlay / continuation admission family 高重叠。
4. **原 `park` 的审计意义应保留。**
   - 原结论不是“volatility 信息无效”，而是“generic `rv_midband` shared gate 这具宿主不值得继续排队”。本轮新证据没有改变这一点。

## Trade on / trade off if revisited later
> 本轮不 draft，只记录若以后再碰该主题时，唯一还诚实的方向。

- trade on:
  - 保留 volatility / market-quality 对明确 intraday continuation、carry、fade 宿主可能有 admission 或 size-down 增量；
  - 若以后要做，应直接写成 `host + market-quality veto`。
- trade off:
  - 放弃 old `Rank 23` 的 standalone `rv_midband` shared-gate 主语；
  - 也放弃把它再包装成 queue-facing 独立 residual。

## Bottom line
1. **原 rank 为什么 park？**
   - 因为 `rv_midband / no-high-vol-extreme` 作为 `15m` shared gate 只做到减亏，没有做到跨资产、成本后、不过度砍样本的 survival。
2. **更像 hard 还是 soft park？**
   - 仍是 `soft park`，但对旧本体已更接近 `hard with consumed residual`。
3. **有没有可救信号？**
   - 有，但只是主题级：volatility / market-quality 仍有信息，不过它活在明确 host 上，不活在 old `Rank 23` 的 shared gate 壳里。
4. **最值得改的唯一一刀是什么？**
   - 把 standalone `rv_midband` shared gate，降级成明确 intraday host 上的 market-quality / volatility-quality veto。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得；本轮保持 `keep_park` 更诚实。

## File-update / commit note
- 本轮只做 park-reframe 侧最小必要文档更新：本日志、`research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md`。
- 未尝试 git commit：共享工作区存在大量与本轮无关的脏文件 / 未跟踪文件，当前不适合安全 selective commit。
