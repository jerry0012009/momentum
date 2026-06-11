# 2026-04-23 15:33 UTC · Rank 24 park reframe

## Scope
- source rank: `Rank 24 / trend regime filter / trend-strength-over-noise gate`
- original status kept: `park`
- this round verdict: `keep_park`
- review reason:
  - 本轮按用户约束只处理 `Rank 1~37` 的已 `park` 条目；
  - `Rank 24` 上次 bot6 复盘是 `2026-04-16 11:46 UTC`，已超过 `7` 天窗口；
  - 4 月 21~23 又补了更贴近趋势主壳的新证据，适合再确认一次：这些证据是在救旧 `trend-strength-over-noise` gate，还是继续把状态层语义外流到新的 trend shell 宿主。

## Files read this round
### Required
1. `docs/TODO.md`
2. `docs/PARK_REFRAME_QUEUE.md`
3. `docs/RECENT_PAPER_SEEDS.md`
4. `research/quant_digests/INDEX.md`
5. `research/park_reframe/INDEX.md`

### Recent park-reframe context
- `research/park_reframe/2026-04-23_1309_rank10-park-reframe.md`
- `research/park_reframe/2026-04-23_1058_rank52-park-reframe.md`
- `research/park_reframe/2026-04-23_0731_rank51-park-reframe.md`
- `research/park_reframe/2026-04-16_1146_rank24-park-reframe.md`

### Rank-specific source notes
- `research/optimization_loop/2026-03-17_0549_rank24-clean-replication-park.md`

### Nearby evidence consulted
- `research/quant_digests/2026-04-16_0454_bubblestate-ma-cross-trend-alpha.md`
- `research/quant_digests/2026-04-21_1358_tripleema-rsi-atr-stack-alpha.md`
- `research/quant_digests/2026-04-23_0548_stochrsi-macd-pullback-continuation-alpha.md`

## What Rank 24 originally tried to do
原始 `Rank 24` 的主张一直很明确：
- 不自己发明新的 trigger；
- 只用 `trend_strength / noise_level / regime_score` 一类抽象状态分数，决定当前 `15m` 环境是否值得放行趋势交易；
- 也就是把“趋势强度是否足以压过噪声”写成一个可独立成立的 queue-facing gate。

一句话：
> 它赌的是“先把环境筛干净，baseline 自然会活”，而不是把状态层嫁接到某个明确 trend shell 上。

## Why it was parked
原 clean replication 的 blocker 没有变化，而且仍然足够硬：
- `baseline_mtf` 约 `-38.69%`；
- `trend_regime_default` 约 `-28.29%`，`positive_asset_ratio = 0/3`；
- 更严格阈值虽然把均值收窄到约 `-9.81%`，但对应 `mean_no_trade_ratio ≈ 74.94%`，本质主要是大幅砍样本；
- `stricter_regime_score` 仍约 `-24.24%`；
- 成本往 `10/15/20bps` 抬时持续恶化，没有形成诚实的跨资产 cost-after pocket。

所以 old `Rank 24` 被 park，不是因为“状态层完全没信息”，而是因为：
1. 它主要做到的是 **少做一点，所以少亏一点**；
2. 没证明这套 generic `trend/noise score` 能稳定挑出可交易 pocket；
3. 它缺的不是再多一个阈值，而是 **主语本身过于抽象、岗位放错层级**。

## Hard park or soft park?
**结论：仍是 `soft park`，但对旧 `Rank 24` 本体已经更接近 `hard park with consumed residual`。**

为什么还保留 `soft`：
- state / regime / market-condition 这层主题本身没有被否掉；
- 新证据继续说明“什么时候更该顺趋势出手”仍然有信息量。

为什么又更接近 `hard`：
- 新证据越来越一致地说明，状态层只在**明确 trend shell**里才像诚实岗位；
- 它们并没有支持 old `Rank 24` 这类抽象 `trend_strength-over-noise` 分数本身还能独立排成一条 queue-facing residual。

## Is there a rescue signal?
**有，但仍然只是主题级可救信号，不是旧 rank 级可救信号。**

### A. bubble-state × MA cross
`2026-04-16_0454_bubblestate-ma-cross-trend-alpha.md` 已经把角色说得很清楚：
- 真正可交易的 base alpha 是 `MA cross`；
- `bubble-state` 只负责 admission / sizing；
- 这不是在救 generic state score，而是在说明 **state 层应该服务明确 trend 主壳**。

### B. triple EMA stack × RSI veto × ATR bracket
`2026-04-21_1358_tripleema-rsi-atr-stack-alpha.md` 继续强化同一个方向：
- `EMA stack` 是主 alpha；
- `RSI veto` 只是不过热不过冷的保护层；
- `ATR` 是 risk / exit layer；
- 真问题是“趋势主壳够不够厚”，不是“先抽象做个状态评分再说”。

### C. StochRSI pullback-continuation 旁证
`2026-04-23_0548_stochrsi-macd-pullback-continuation-alpha.md` 也在给同一类 desk 翻译：
- `StochRSI extreme -> RSI direction -> MACD phase flip` 是一个完整 pullback-continuation host；
- oscillator / direction / phase 的各组件都在围绕**一个明确 trend continuation 宿主**服务；
- 这进一步削弱了 old `Rank 24` 那种“先做抽象 trend/noise gate”的独立身份。

### 小结
因此本轮真正的可救信号只能写成：
> **状态层仍有信息，但它更像 trend shell 上的 local admission / veto / sizing layer；它没有把 old `Rank 24` 的 generic trend-strength-over-noise gate 救回队列。**

## The single best modification axis
如果只允许保留 **1 条唯一主修改轴**，那本轮仍然只能是：

> **把 standalone 的 `trend_strength-over-noise` filter，降级成明确 trend shell 上的 market-state / bubble-state / readiness admission gate。**

也就是：
- trade on：保留状态层对“哪些趋势段更值得参与”的信息；
- trade off：放弃 old `Rank 24` 作为抽象 shared gate / 独立 queue-facing rank 的身份。

但关键点也更清楚了：
- 这条唯一修改轴其实已经越界到新的 trend-shell family；
- 它不是 old `Rank 24` 内部还能再诚实切出的新 `Rank 24b`；
- 如果今天硬 draft，只会写成“新的完整 trend shell + state gate”，而不是旧 rank 的窄 reframe。

## Should this become a derived hypothesis now?
**不值得。最终结论：`keep_park`。**

原因：
1. **原 blocker 没被推翻。**
   - old `Rank 24` 仍没有跨资产、成本后、不过度砍样本的 survival pocket。
2. **新证据救的是岗位迁移，不是旧壳重开。**
   - 4 月 21~23 的新旁证都在说明：trend/state 信息该服务于明确的 EMA / pullback / MA-cross 宿主。
3. **distinctness 反而更弱了。**
   - 现在如果硬写 `Rank 24b`，最自然的写法会与新 trend-shell / pullback-continuation family 高重叠，不足以成为 bot2 可直接判断的新 intake。
4. **原 `park` 的审计意义应保留。**
   - 原结论不是“trend state 完全无效”，而是“generic trend-strength-over-noise gate 这具宿主不值得继续排队”。本轮新证据没有改变这一点。

## Trade on / trade off if revisited later
> 本轮不 draft，只记录若以后再碰该主题时，唯一还诚实的方向。

- trade on:
  - 保留 state / bubble / readiness 对明确 trend shell 可能有 admission 或 sizing 增量；
  - 若以后要做，应直接写成 `trend shell + state gate`。
- trade off:
  - 放弃 old `Rank 24` 的 standalone `trend-strength-over-noise` 主语；
  - 也放弃把它再包装成一个抽象 shared gate 继续排队。

## Bottom line
1. **原 rank 为什么 park？**
   - 因为它主要做到减亏，没有做到跨资产、成本后、不过度砍样本的可复用 survival。
2. **更像 hard 还是 soft park？**
   - 仍是 `soft park`，但对旧本体已更接近 `hard with consumed residual`。
3. **有没有可救信号？**
   - 有，但只是主题级：状态层仍有信息，不过它活在明确 trend shell 上，不活在 old `Rank 24` 的 generic score 壳里。
4. **最值得改的唯一一刀是什么？**
   - 把 standalone trend/noise score，降级成明确 trend shell 上的 state / bubble / readiness admission gate。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得；本轮保持 `keep_park` 更诚实。

## File-update / commit note
- 本轮只做 park-reframe 侧最小必要文档更新：本日志、`research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md`。
- 未尝试 git commit：共享工作区存在大量与本轮无关的脏文件 / 未跟踪文件，当前不适合安全 selective commit。
