# 2026-04-23 13:09 UTC · Rank 10 park reframe

## Scope
- source rank: `Rank 10 / volatility-managed EMA / ATR sizing overlay`
- original status kept: `park`
- this round verdict: `keep_park`
- review reason:
  - 本轮只处理 `1` 条已 `park` 的旧 rank；
  - 按 `Rank 1~37` 里最近 `7` 天尽量不重复的约束，`Rank 10` 上次 bot6 复盘是 `2026-04-16 01:42 UTC`，已越过 `7` 天窗口；
  - 近期 quant digests 又补了几条 `ATR / volume / regime` 新证据，适合再确认一次：它们是否真的足以把旧 `Rank 10` 诚实地再切出新的窄 reframe hypothesis。

## Files read this round
### Required
1. `docs/TODO.md`
2. `docs/PARK_REFRAME_QUEUE.md`
3. `docs/RECENT_PAPER_SEEDS.md`
4. `research/quant_digests/INDEX.md`
5. `research/park_reframe/INDEX.md`

### Recent park-reframe context
- `research/park_reframe/2026-04-23_1058_rank52-park-reframe.md`
- `research/park_reframe/2026-04-23_0731_rank51-park-reframe.md`
- `research/park_reframe/2026-04-23_0520_rank20-park-reframe.md`
- `research/park_reframe/2026-04-16_0142_rank10-park-reframe.md`

### Rank-specific source notes
- `research/optimization_loop/2026-03-16_2312_vol-managed-ema-park.md`

### Nearby evidence consulted
- `research/quant_digests/2026-04-12_1639_signaware-xsmomentum-atrvolume-alpha.md`
- `research/quant_digests/2026-04-19_0345_xsmom-atr-volume-regime-shell.md`
- `research/quant_digests/2026-04-14_2353_bbexpansion-pullback-continuation-shell.md`

## What Rank 10 originally tried to do
原始 `Rank 10` 的主张很窄：
- 方向主语仍是 `EMA20 > EMA50` 一类趋势跟随；
- `ATR_ref / ATR14` 或相近 clipping 只负责调仓；
- 它赌的是“波动管理 / ATR 缩放本身就足以把普通 EMA 趋势层修成更可交易的东西”。

换句话说，旧 rank 不是在问“ATR 是否有信息”，而是在问：
> **standalone volatility-managed EMA sizing，会不会自己就是一条值得保留的 queue-facing 线。**

## Why it was parked
原 clean replication 的 blocker 很清楚，而且并不是“证据还不够”：
- `baseline_100 @ 6bps/side` 已经约 `-15.66%`；
- 主变体 `atr_clip_050_150 @ 6bps/side` 反而更差，约 `-26.21%`；
- 其它 clip 变体（`0.75~1.25`, `0.25~1.75`）也都没有优于 baseline；
- `positive_asset_ratio = 0/3`；
- 时间、参数、跨标的、成本四项 stability pack 一起 fail；
- 它不是 trade 太少的稀疏误判，而是 **trade 很多、turnover 很高、成本后仍系统性偏负**。

所以它被 park，不是因为“ATR 完全没信息”，而是因为：
1. **ATR-managed EMA sizing 没把原方向层救活；**
2. 改善没有出现在跨资产、成本后、不过度依赖单个 clip 桶的诚实 pocket；
3. 旧 rank 的主语从一开始就更像 risk layer，而不是独立 alpha / 独立 front-slot 对象。

## Hard park or soft park?
**结论：仍是 `soft park`，但对旧 `Rank 10` 本体已经更接近 `hard park with consumed residual`。**

为什么还留 `soft`：
- `ATR / stop-distance / volatility-state` 这层信息本身没有被否掉；
- 它仍像 tradeability / sizing / veto 语义，而不是纯噪音。

为什么又更接近 `hard`：
- 这点残余早就不再支持 old `Rank 10` 作为独立 rank；
- 唯一自然 residual `Rank 10b` 也已在 `2026-04-09` first verdict 收口为 `background / P0`；
- 现在剩下的更像“主题还活，但宿主早该换掉了”。

## Is there a rescue signal?
**有，但只到主题级，而且比上轮更明确地指向“新宿主”，不是旧 rank。**

近期几条新证据的共同点很一致：
- `2026-04-12_1639_signaware-xsmomentum-atrvolume-alpha.md`
- `2026-04-19_0345_xsmom-atr-volume-regime-shell.md`
- `2026-04-14_2353_bbexpansion-pullback-continuation-shell.md`

它们都不是在说“ATR sizing 自己能单独站住”；
它们在说的是：
- ATR 更像 **完整 raw-alpha 壳里的 confirmation / regime / sizing / exit 变量**；
- 也就是 ATR 有信息，但这信息要附着在更完整的 momentum / breakout / basket shell 上，才像可交易故事；
- 反过来，这恰好进一步削弱了 old `Rank 10` 的独立身份。

所以本轮的可救信号只能写成：
> **ATR 主题还活，但它活在新的 full-shell / setup-local 宿主里，不活在旧 Rank 10 的 volatility-managed EMA sizing 本体里。**

## The single best modification axis
如果只允许保留 **1 条唯一主修改轴**，那仍然只能是：

> **把 standalone volatility-managed EMA sizing，彻底降级成 setup-local 的 ATR stopDistancePct / volatility-state size-down or veto overlay。**

也就是：
- trade on：保留 ATR 对高 stop-distance、低 tradeability、波动扩张阶段的风险提示；
- trade off：放弃“ATR 仓位管理本身可以独立构成一条 queue-facing rank”的旧读法。

但关键问题也没变：
- 这不是新的发现；
- 这正是既有 `Rank 10b` 已经表达过、并已经被 runtime truth 收口掉的唯一自然一刀。

## Should this become a derived hypothesis now?
**不值得。最终结论：`keep_park`。**

原因：
1. **原 blocker 没被推翻。**
   - old `Rank 10` 没有跨资产、成本后、不过度依赖 clip 的可复用 pocket。
2. **唯一诚实 residual 已被消费。**
   - `Rank 10b` 已经把“ATR stopDistancePct 只做 size-veto overlay”这条唯一修改轴写出来，并已在 4 月 9 日 first verdict 收口为 `background / P0`。
3. **近期新证据救的是新宿主，不是旧壳。**
   - 4 月中下旬新增 digest 进一步说明 ATR 更适合服务完整 trend / breakout / XS momentum shell；
   - 它们没有把 old `Rank 10` 重新拉回一个可诚实单列的新派生对象。
4. **再 draft `Rank 10c` 会变成换名复写。**
   - 若今天硬写，本质上只是把已被消费的 shared risk-layer 又包装一次，不够 distinct，也不够诚实。

## Trade on / trade off if revisited later
> 本轮不 draft，只记录若以后再碰该主题时，唯一还诚实的方向。

- trade on:
  - 保留 ATR / stop-distance / volatility-state 对 tradeability 与 sizing 仍可能有边际价值；
  - 若以后要做，应直接写成明确 trend / breakout / basket shell 里的 local overlay。
- trade off:
  - 放弃 old `Rank 10` 的 standalone volatility-managed EMA 主语；
  - 也放弃把它再包装成 queue-facing 独立 residual。

## Bottom line
1. **原 rank 为什么 park？**
   - 因为 ATR-managed EMA sizing 没把原方向层救活，反而在高 turnover / 成本后继续系统性偏负。
2. **更像 hard 还是 soft park？**
   - 仍是 `soft park`，但对旧本体已更接近 `hard with consumed residual`。
3. **有没有可救信号？**
   - 有，但只到主题级：ATR 仍有信息，不过它活在新的 full-shell / setup-local overlay 宿主里。
4. **最值得改的唯一一刀是什么？**
   - 把 standalone volatility-managed EMA sizing，降级成 setup-local 的 ATR stopDistancePct size-down / veto overlay。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得；这条唯一修改轴已由既有 `Rank 10b` 消费并收口，当前应维持 `keep_park`。

## File-update / commit note
- 本轮只做 park-reframe 侧最小必要文档更新：本日志、`research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md`。
- 未尝试 git commit：共享工作区存在大量与本轮无关的脏文件，当前不适合安全 selective commit。
