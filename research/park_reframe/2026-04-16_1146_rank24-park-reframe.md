# 2026-04-16 11:46 UTC · Rank 24 park reframe review

## Scope
- source rank: `Rank 24 / trend regime filter / trend-strength-over-noise gate`
- original status kept: `park`
- this round verdict: `keep_park`
- review reason:
  - 本轮按用户约束只处理 `Rank 1~37` 的已 `park` 条目；
  - `Rank 24` 虽距上次 bot6 复盘尚未满完整 `7` 天，但这轮有 **新证据**：`2026-04-16_0454_bubblestate-ma-cross-trend-alpha.md`；
  - 该新证据正好再次触碰 `trend / market-state gate` 主题，适合做一次最小复核，确认它是否足以把旧 `Rank 24` 收窄成新的窄 reframe hypothesis。

## Files read this round
### Required
1. `docs/TODO.md`
2. `docs/PARK_REFRAME_QUEUE.md`
3. `docs/RECENT_PAPER_SEEDS.md`
4. `research/quant_digests/INDEX.md`
5. `research/park_reframe/INDEX.md`

### Recent park-reframe context
- `research/park_reframe/2026-04-16_0912_rank20-park-reframe.md`
- `research/park_reframe/2026-04-16_0418_rank4-park-reframe.md`
- `research/park_reframe/2026-04-10_0811_rank24-park-reframe.md`

### Rank-specific source notes
- `research/optimization_loop/2026-03-17_0531_rank24-trend-regime-intake.md`
- `research/optimization_loop/2026-03-17_0549_rank24-clean-replication-park.md`

### Nearby evidence consulted
- `research/quant_digests/2026-04-16_0454_bubblestate-ma-cross-trend-alpha.md`

## What Rank 24 originally tried to do
原始 `Rank 24` 的主张很简单：
- 不重新发明 trigger；
- 只用 `trend_strength / noise_level / regime_score` 这套状态分数，决定当前 `15m` 环境是否值得放行趋势交易；
- 也就是把“趋势强度是否足以压过噪声”写成一个可独立成立的 regime filter。

一句话：
> 它赌的是“环境先筛干净，baseline 自然会活”，而不是“靠更复杂入场形状救回来”。

## Why it was parked
原 clean replication 已经把旧 blocker 审计得很清楚：
- `baseline_mtf` 约 `-38.69%`；
- `trend_regime_default` 只把亏损收窄到约 `-28.29%`，`positive_asset_ratio = 0/3`；
- 更严格阈值虽然把均值拉到约 `-9.81%`，但本质上主要来自 `mean_no_trade_ratio ≈ 74.94%` 的大幅砍样本；
- `stricter_regime_score` 仍约 `-24.24%`；
- 成本从 `10/15/20bps` 往上抬时持续恶化，没有形成诚实的跨资产成本后 pocket。

所以它被 park，不是因为“状态层完全没信息”，而是因为：
1. 它主要做到的是 **少做一点，所以少亏一点**；
2. 没证明 `trend-strength-over-noise` 这套旧壳能稳定挑出跨资产可交易 pocket；
3. 局部正 bucket 没有聚成可复用、可迁移的结构。

## Hard park or soft park?
**结论：仍是 `soft park`，但对旧 `Rank 24` 本体已进一步向 `hard park` 靠。**

原因：
- soft 的部分在于：状态层 / 市场环境层这个主题本身没有被否掉；
- hard 的部分在于：旧 `Rank 24` 这套 generic `trend/noise score` 写法，已经多次显示它不够独立，也不够诚实。

## Is there a rescue signal?
**有，但还是主题级，不是旧壳级。**

这轮唯一真正相关的新证据，是 `2026-04-16_0454_bubblestate-ma-cross-trend-alpha.md`：
- 它支持的是 **“MA 主壳 + bubble-state gate”**；
- 也就是 market-state/bubble-state 作为 admission / sizing layer，服务于明确的趋势主壳；
- 它并不支持“抽象 trend_strength-over-noise 分数本身就能单独成为 queue-facing filter”。

而且这份新 digest 的 desk 翻译也很明确：
- `bubble-state` 只负责 gate / overlay，**不是 alpha 本体**；
- 更像 `MA trend-following × bubble-state gate` 的完整 raw-alpha 壳；
- 不像旧 `Rank 24` 那种 generic state score。

因此，本轮可救信号只能写成：
- **状态层仍有信息；**
- **但这信息更像应该嫁接到明确 trend shell 上，而不是继续保留旧 Rank 24 这种抽象 gate。**

## The single best modification axis
如果只允许保留 **唯一一刀**，那最值得改的仍然是：

> **把 standalone 的 `trend_strength-over-noise` regime filter，改写成明确 trend shell 上的 market-state / bubble-state admission gate。**

但这条唯一修改轴并不诚实地属于 `Rank 24b`，原因有二：
1. 新证据强调的是 **MA 主壳为主语**，状态只是 gate；
2. 这样改写后，主语已经从“generic trend/noise score”变成“trend shell + state gate”，本质更像新的 raw-alpha / shell family，而不是旧 rank 的窄派生。

## Should this become a derived hypothesis now?
**不值得。最终结论：`keep_park`。**

原因：
1. **原 blocker 没被推翻**
   - 旧 `Rank 24` 仍然没有跨资产、成本后、不过度砍样本的存活证据。
2. **新证据救的是角色重写，不是旧壳重开**
   - `bubble-state` 新证据支持的是“状态层降级成 trend shell 的 gate / sizing”；
   - 不支持把旧 `trend_strength / noise_level / regime_score` 再诚实切成一个新的 queue-only `Rank 24b`。
3. **distinctness 依旧不够**
   - 如果今天硬 draft，一个最自然版本会非常接近新的 MA/bubble-state shell，已经不是原 `Rank 24` 的窄 reframe；
   - 这样写回 queue，只会制造身份重叠，而不是给 bot2 一个清晰的新鲜 intake。

## Trade on / trade off if revisited later
> 本轮不 draft，只记录若未来重碰该主题时，唯一还诚实的方向。

- trade on:
  - 保留“市场状态 / bubble-state 可能对趋势主壳有 admission 或 sizing 增量”这一主题判断；
  - 若以后要做，应直接写成 `trend shell + state gate`，而不是 generic score filter。
- trade off:
  - 放弃旧 `Rank 24` 的 standalone `trend-strength-over-noise` 主语；
  - 也放弃把它再包装成一个抽象 shared gate 再度排队。

## Bottom line
1. **原 rank 为什么 park？**
   - 因为它只做到减亏，没有做到跨资产、成本后、不过度砍样本的可复用生存。
2. **更像 hard 还是 soft park？**
   - 仍是 `soft park`，但比 4 月 10 日那轮更接近 `hard with consumed residual`。
3. **有没有可救信号？**
   - 有，来自 `bubble-state` 新证据；但它救的是“明确 trend shell 上的 state gate”，不是旧 `Rank 24` 的抽象 score 壳。
4. **最值得改的唯一一刀是什么？**
   - 把 standalone trend/noise score 改写成明确 trend shell 上的 market-state / bubble-state admission gate。
5. **是否值得形成新的 derived hypothesis？**
   - 现在不值得；保持 `keep_park` 更诚实。

## File-update / commit note
- 本轮只做 park-reframe 侧最小必要文档更新：本日志、`research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md`。
- 未尝试 git commit：共享工作区存在大量与本轮无关的脏文件，当前不适合安全 selective commit。
