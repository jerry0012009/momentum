# 2026-04-10 08:11 UTC · Rank 24 park reframe review

## Scope
- source rank: `Rank 24 / trend regime filter / trend-strength-over-noise gate`
- original status kept: `park`
- this round verdict: `keep_park`
- review reason:
  - 本轮按用户约束只看 `Rank 1~37` 的已 `park` 条目；
  - `Rank 24` 上一次 bot6 复盘是 `2026-04-02 09:09 UTC`，已超过 `7` 天窗口；
  - 它属于典型“原命题像环境过滤，但近期新证据把主题往更上位 market-state shell / router 外推”的条目，适合做一次低频收口。

## Files read this round
### Required
1. `docs/TODO.md`
2. `docs/PARK_REFRAME_QUEUE.md`
3. `docs/RECENT_PAPER_SEEDS.md`
4. `research/quant_digests/INDEX.md`
5. `research/park_reframe/INDEX.md`

### Recent park-reframe context
- `research/park_reframe/2026-04-10_0611_rank89-park-reframe.md`
- `research/park_reframe/2026-04-10_0254_rank15-park-reframe.md`
- `research/park_reframe/2026-04-10_0030_rank68-park-reframe.md`

### Rank-specific source notes
- `research/optimization_loop/2026-03-17_0531_rank24-trend-regime-intake.md`
- `research/optimization_loop/2026-03-17_0549_rank24-clean-replication-park.md`

### Nearby evidence consulted
- `research/quant_digests/INDEX.md` 中的 `2026-04-04_2223_tsmom-bull-third-noshort-alpha.md`
- `research/quant_digests/INDEX.md` 中的 `2026-04-10_0010_tailstate-partialmoment-tsmom-router-alpha.md`
- `research/quant_digests/INDEX.md` 中的 `2026-04-01_1811_ma-breakout-bubble-gated-trend-alpha.md`

## What Rank 24 originally tried to do
原始 `Rank 24` 想做的事很直接：
- 不自己重新发明 breakout / EMA trigger；
- 只根据过去 `N` 根的 `trend_strength`、`noise_level` 与 `regime_score`，决定当前 `15m` 环境是否足够“像趋势”；
- 然后把这层 `trend-strength-over-noise` 当成可独立成立的 regime filter。

人话就是：
> 它赌的不是“进场形状更聪明”，而是“先把趋势环境挑干净，baseline 自然会活”。

## Why it was parked
原 clean replication 给出的 hard facts 已经很清楚：
- baseline `mean_total_return ≈ -38.69%`；
- `trend_regime_default` 只是把亏损收窄到约 `-28.29%`，仍然 `positive_asset_ratio = 0/3`；
- 更严格的 `trend_threshold` 虽把均值拉到约 `-9.81%`，但本质上还是 `1/3` 资产转正，且 `mean_no_trade_ratio ≈ 74.94%`；
- `stricter_regime_score` 重新回到约 `-24.24%`；
- 成本一抬高，`10/15/20bps` 梯度继续恶化，没有形成诚实的成本后存活 pocket。

所以它被 park，不是因为“趋势状态完全没信息”，而是因为：
1. 原写法只证明了 **少做一点可以少亏一点**；
2. 没证明 `trend_strength / noise_level` 这套旧壳能稳定挑出跨资产可用的 pocket；
3. 局部时间桶的亮点没有聚成可复用结构，更像零散 sample split。

## Hard park or soft park?
**结论：`soft park`，但对原 `Rank 24` 本体已经明显向 `hard park` 靠。**

为什么还留一丝 soft：
- 原 rank 至少说明“环境层/状态层”比完全裸做 baseline 更接近正确方向；
- 也就是说，问题不完全在“先看状态”这个想法本身。

为什么又不该乐观：
- 一旦要求跨资产、成本后、不过度砍样本，旧的 `trend-strength-over-noise` gate 就站不住；
- 这说明被证伪的不是“状态重要”，而是 **“用 Rank 24 这套简化 trend/noise score，就足以当成 queue-facing 过滤层”**。

## Is there a rescue signal?
**有主题级可救信号，但已经不再属于 `Rank 24` 这条旧壳。**

近期新证据都在把同主题往更窄、也更上位的宿主推进：
1. `2026-04-04 bull-state-only × no-short-veto`：
   - 提示真正可能有信息的不是“全天候连续 trend/noise 打分”；
   - 而是更粗、更诚实的 market-level bull-state / no-short 路由。
2. `2026-04-10 tail-state partial-moment router`：
   - 进一步把信息收窄成 tail-state router；
   - 重点从“是否处于趋势”转成“当前尾部状态该续行还是该反手/停手”。
3. `2026-04-01 MA / breakout × bubble-state gate`：
   - 也说明状态层如果还有边际价值，更像要服务明确的趋势壳 / breakout 壳；
   - 而不是单独保留一个抽象的 `trend_strength-over-noise` 过滤器。

所以本轮判断是：
- **状态主题没有死；**
- **但 Rank 24 原本那种 generic trend/noise regime filter 的表达，已经不是最诚实的载体。**

## The single best modification axis
如果硬要保留“唯一值得改的一刀”，那只能是：

> **把 standalone 的 `trend_strength-over-noise` regime filter，收窄成 market-level `bull-state-only / no-short` veto or router。**

但问题在于，这一刀现在已经明显不再属于 `Rank 24`：
- 它更像新的 market-TSMOM / state-router raw-alpha shell；
- 或者被相邻的环境层提案（如 `Rank 9b / 21b / 25b`）与更新的 raw-alpha family 吸收。

所以这轮虽然能指出“唯一能改的方向”，但**它不是一个还值得从原 Rank 24 再单列出来的 queue-only reframe**。

## Should this become a derived hypothesis now?
**不值得。最终结论：`keep_park`。**

原因有三条：
1. **旧 blocker 没被推翻**
   - Rank 24 从头到尾都没证明自己能在跨资产 + 成本后形成稳定存活 pocket。
2. **新证据在推主题外流，不是在救旧壳**
   - 近期证据更支持 `bull-state shell` / `tail-state router` 这类新宿主；
   - 不支持把原来的 `trend_strength / noise_level / regime_score` 再写成 `Rank 24b`。
3. **distinctness 不够**
   - 如果今天硬 draft，一个最自然的版本会非常靠近既有环境层提案或新的 market-state raw-alpha family；
   - 它不会是 bot2 值得单独判断的新鲜 intake。

## Trade on / trade off if revisited later
> 本轮不 draft，只记录未来若要再碰这个主题时的唯一诚实方向。

- trade on:
  - 保留“市场状态/尾部状态确实可能决定 trend lane 是否值得参与”这个主题判断；
  - 若以后要做，更像应该写成 market-level bull-state router / no-short veto，而不是连续打分的 generic filter。
- trade off:
  - 放弃 `Rank 24` 原先那种“抽象 trend/noise score 自己就能筛出可交易环境”的读法；
  - 也放弃把它再包装成旧风格的 shared gate。

## Bottom line
1. **原 rank 为什么 park？**
   - 因为它只做到“少亏”，没做到跨资产、成本后、不过度砍样本的可复用生存。
2. **更像 hard 还是 soft park？**
   - `soft park`，但对原旧壳已经明显向 `hard park` 靠。
3. **有没有可救信号？**
   - 有，但只剩主题级信号，而且已经外流到 bull-state shell / tail-state router 新宿主。
4. **最值得改的唯一一刀是什么？**
   - 把旧的 standalone trend/noise filter 收窄成 market-level `bull-state-only / no-short` router。
5. **是否值得形成新的 derived hypothesis？**
   - 现在不值得；保持 `keep_park` 更诚实。

## File-update / commit note
- 本轮只做 park-reframe 侧最小必要文档更新：本日志、`research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md`。
- 未尝试 git commit：共享工作区长期存在大量与本轮无关的脏文件，当前不适合安全 selective commit。
