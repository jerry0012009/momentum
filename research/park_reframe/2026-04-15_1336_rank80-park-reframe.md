# 2026-04-15 13:36 UTC · Rank 80 park reframe

## Selected rank
- `Rank 80`
- selection note:
  - 本轮继续只处理 `1` 条已 `park` 的 rank。
  - 近两天 `50~79` 与 `80~110` 号段已被连续低频覆盖，但 `Rank 80` 上次 bot6 复盘是 `2026-04-04 13:52 UTC`，已超过 `7` 天，满足再看条件。
  - 4 月 12~14 日又新增了更直接的 session-clock / recurring-pocket 证据，值得确认：这些新证据是在修复旧 `Rank 80`，还是进一步证明主题应迁到新的 raw-alpha 宿主。

## Source evidence read
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/park_reframe/2026-04-15_1059_rank7-park-reframe.md`
- `research/park_reframe/2026-04-15_0355_rank56-park-reframe.md`
- `research/park_reframe/2026-04-15_0143_rank87-park-reframe.md`
- `research/park_reframe/2026-04-04_1352_rank80-park-reframe.md`
- `research/optimization_loop/2026-03-19_0547_rank80-clean-replication-keep-p1.md`
- `research/quant_digests/2026-04-03_0042_btc-volclock-first30-impulse-alpha.md`
- `research/quant_digests/2026-04-12_0924_nyse-open-betaspread-continuation-alpha.md`
- `research/quant_digests/2026-04-13_1220_pseudoopen-pseudoclose-tsmom-alpha.md`
- `research/quant_digests/2026-04-14_1718_sameclock-xsmomentum-recurring-pocket-alpha.md`

## Original park reason
原 `Rank 80 / first-30m impulse quality` 被 park 的审计逻辑没有变化：

- 它原本想做的是 **跨 `breakout_short / ema_psar_long / fib_retest_long` 三条 lane 的 shared continuation gate / sizing layer**；
- 但 clean replication 已经说明，这条线没有形成 desk 级统一改善：
  - `baseline`：`mean_total_return≈-2.00%`，`mean_expectancy≈-0.065%`，`early_fail≈27.25%`
  - `impulse_halfsize`：`mean_total_return≈-1.09%`，`mean_expectancy≈-0.039%`，但 `early_fail` 基本没降
  - `impulse_veto`：表面接近转正，但 `mean_trade_count_retention≈14.01%`，明显带着极端砍样本味道
- 分 lane 看，真正稍有帮助的 pocket 主要集中在 `breakout_short`；`fib_retest_long` 反而被稀释。

所以原 verdict 不是“开段冲击质量完全没信息”，而是：
> **它不够诚实地撑起一个 queue-facing、跨三条 lane 共用的 shared continuation gate。**

## Hard park or soft park?
- 结论：`soft park，但比 2026-04-04 那轮更接近 hard`

为什么仍保留 soft：
- `first30m impulse` 主题本身仍有残余信息；
- 原 clean replication 至少说明：严格 `veto` 太狠，`half-size` 比它更诚实，说明“冲击质量”不是纯噪音。

为什么又更接近 hard：
- 这点残余已经越来越不像 old `Rank 80` 还能再切出一条新的 shared-gate reframe；
- 近期新证据继续把主题分流到两个别处：
  1. shared-gate 语义早已被既有 `Rank 5b` 基本吸收；
  2. 更强的新 evidence 则把它抬升到新的 `session-clock / pseudo-open / recurring-pocket` raw-alpha 宿主。

## Any salvage signal?
有，但这次更明确地说明：**可救的是主题，不是旧 `Rank 80` 壳。**

### A. 2026-04-12 NYSE-open beta-spread continuation
这条证据说明：
- 真正能活的更像 `NYSE open first-15m pulse -> next 90~120m beta-spread continuation`；
- 主语已经是 **session-pocket relative-value raw alpha**；
- 不再是“开段 impulse 质量去给既有 continuation lanes 做 shared allow/deny”。

### B. 2026-04-13 pseudo-open overnight sign -> pseudo-close last-30m continuation
这条证据说明：
- session-clock 主题若还值得保留，更自然的是 **BTC pseudo-session 内的首尾动量传导 raw alpha**；
- 也不是旧 `Rank 80` 这种跨三条 lane 的 shared gate。

### C. 2026-04-14 same-clock winners-minus-losers recurring pocket
这条证据进一步扩大了同一方向：
- 真正还站得住的是 **same-clock recurring pocket 的 cross-sectional raw alpha**；
- 不是 old `Rank 80` 的 continuation quality overlay。

所以，本轮可救信号应写成：
> **session-clock / first-window impulse 主题仍有信息，但信息活在新的 session-pocket raw-alpha family，而不是旧 Rank 80 的 shared continuation gate。**

## Single best cut
如果只谈旧 `Rank 80` 最值得保留的唯一一刀，它仍只能是：

**把 shared continuation gate 继续收窄成单一 session-pocket / single-book 的 first-window impulse raw alpha 宿主。**

但这已经不是诚实的 `Rank 80b`：
- 角色从 `shared gate` 变成了 `independent raw alpha`；
- entry / holding / book 结构都换了；
- 与既有 `Rank 5b` 的 shared-gate residual 边界也会重叠。

换句话说，这一刀更像“迁移宿主”，不是“修补 old Rank 80”。

## Is a new derived hypothesis warranted?
- 结论：`keep_park`
- 不形成新的 `derived hypothesis`

原因：
1. 原 `park` blocker 没被推翻：作为 shared gate，它仍主要是 lane-specific pocket；
2. 近期新证据不是在修复 old `Rank 80`，而是在继续证明 session-clock / first-window impulse 应迁移到新的 raw-alpha family；
3. 如果现在硬写 `Rank 80b`，不是重复 `Rank 5b` 的 shared-gate residual，就是借旧 rank 名义回灌一个新宿主，审计上不诚实。

## Final verdict
- `verdict`: `keep_park`
- `original_verdict_kept`: `park`
- `one-line note`: `soft park，但比 4 月 4 日那轮更接近 hard；原 first30m impulse quality shared gate 的 blocker 没被推翻，而 4 月 12~14 日新增的 NYSE-open / pseudo-session / same-clock recurring-pocket 证据继续说明时钟主题若还有信息，也更像新的 session-pocket raw-alpha 宿主，而不是足以再诚实派生 Rank 80b。`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## Commit
- 本轮默认不做 commit。
- 原因：只做最小必要文档改动；且仓库存在与本轮无关的既有脏文件，避免混提。
