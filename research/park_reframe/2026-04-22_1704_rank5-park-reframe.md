# 2026-04-22 17:04 UTC · Rank 5 park reframe revisit

## Selected rank
- `Rank 5`
- selection note: 本轮回到 `Rank 1~24` 号段轮转；`Rank 5` 上次 bot6 复盘是 `2026-04-13 14:51 UTC`，已超过默认 `7` 天回避窗口。4 月 20~22 又新增了更贴近时钟主题的旁证，足够再回答一次：这些证据是在救旧 `Rank 5`，还是继续把 session-clock 信息抬升为新的 event-defined raw-alpha 宿主。

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-16_2149_intraday-tsmom-session-park.md`
- `research/optimization_loop/2026-03-30_0130_rank5_double_clock_residual_stays_park_reframe.md`
- `research/park_reframe/2026-04-13_1451_rank5-park-reframe.md`
- `research/quant_digests/2026-04-20_1856_speed-volume-momentum-shell-alpha.md`
- `research/quant_digests/2026-04-22_0429_us-close-midcap-reversal-alpha.md`

## 1) 原 rank 为什么 park？
原 `Rank 5 / session-aware intraday TSMOM` 被 park 的核心原因没有变化：
- 它把 **session 前段收益 / impulse** 直接写成 **尾段跟随交易**；
- clean replication 在诚实口径下是广泛负值，不是只差一个小过滤层；
- 失败对象是 `open/session early move -> tail follow trade` 这条 standalone 写法，而不是 session / clock 信息整体死亡。

冻结审计里的关键硬证据仍成立：
- `funding_8h_q60 @ 6bps/side mean_total_return ≈ -22.74%`
- `positive_asset_ratio = 0/3`
- `0/4` 成本档为正
- `mean_trades ≈ 145`，不是样本过稀导致的假阴性
- 时间 / 参数 / 跨标的 / 成本四项稳定性一起 fail

所以原 `park` 的审计意义仍然是：
> **失败的是旧 Rank 5 的 direct session-tail trade 写法，不是时钟信息本身。**

## 2) 它更像 hard park 还是 soft park？
本轮判断：`soft park`，但比 4 月 13 日那轮更接近 `hard park with consumed residual`。

为什么仍保留 soft：
- session-aware / open-impulse / close-window 信息本身仍有研究价值；
- 旧 Rank 5 至少留过一条诚实 residual：把开段 impulse 降级成 shared continuation gate / sizing layer。

为什么更接近 hard：
- 这条唯一自然 residual 早已被既有 `Rank 5b` 表达；
- `2026-03-30` 的 double-clock 审计也已明确：一旦把主题扩成 `open impulse + pre-close reversal` 双腿组合，就已经是在开新 family，不再是旧 `Rank 5` 的窄 reframe；
- 4 月 20~22 的新证据继续强化的也是新的 event/time-window raw alpha，而不是 old tail-follow 本体。

## 3) 有没有“可救信号”？
有，但仍然不是新的，且没有超出既有 `Rank 5b`。

旧 rank 语境下唯一仍站得住的可救信号，依然只是：
- 把 `direct session-tail intraday TSMOM entry`
- 降级成 `first-30m impulse-quality shared continuation gate / sizing layer`

但 4 月 20~22 的新旁证没有把这条 residual 重新拉开：
1. `2026-04-20` 的 `speed-volume momentum shell` 指向的是 **短窗涨速 + 成交量放大** 的完整 continuation raw alpha；它强调的是 event-strength shell，不是“session 前段动了 -> 尾段直接跟”的修补。
2. `2026-04-22` 的 `US close-window loser→winner fade` 指向的是 **固定 close-window 的横截面反转 raw alpha**；它说明时钟主题仍有信息，但主语已经是 `time-scheduled cross-sectional event router`，不是旧 Rank 5 的 tail-follow residual。

因此现在更诚实的说法是：
> **有主题级可救信号，但没有新的 Rank 5 本体级可救信号。**

## 4) 最值得改的唯一一刀是什么？
如果今天仍然只允许保留一刀，答案仍然不变：

> **把 `direct session-tail intraday TSMOM entry` 降级成 `first-30m impulse-quality shared continuation gate / sizing layer`。**

但这不是本轮新提案，因为：
1. 它已经由 `Rank 5b` 明确表达；
2. 本轮没有出现第二条仍然诚实、且不同于 `Rank 5b` 的主修改轴；
3. 若继续加入 close-window / reversal / cross-sectional 元素，就会越界成新的时钟 raw-alpha family。

## 5) 是否值得形成新的 derived hypothesis？
- 结论：**不值得**
- 本轮 verdict：`keep_park`

原因：
1. 原 `park` blocker 没有被推翻；
2. 唯一诚实 residual 仍只到既有 `Rank 5b`；
3. 4 月 20~22 的新证据继续把时钟主题上移到新的 `speed-volume continuation` / `US close-window reversal` 等完整 raw-alpha 宿主；
4. 若现在硬 draft `Rank 5c`，不是重复 `Rank 5b`，就是偷换成新的 family 主语，都会削弱旧 `park` 的审计边界。

## 6) 按模板直答
1. **原 rank 为什么 park？**  
   因为 `session 前段收益 -> 尾段直接跟单` 这条 standalone trade 在 BTC/ETH/SOL 15m 诚实复制下 post-cost 持续为负，且四项稳定性一起失败。
2. **它更像 hard park 还是 soft park？**  
   `soft park`，但比 4 月 13 日那轮更接近 `hard park with consumed residual`。
3. **有没有“可救信号”？**  
   有，但只剩既有 `Rank 5b` 那条 `first-30m impulse-quality shared gate / sizing` residual；没有新的本体级可救信号。
4. **最值得改的唯一一刀是什么？**  
   `direct session-tail trade -> first-30m impulse-quality shared continuation gate / sizing layer`。
5. **是否值得形成新的 derived hypothesis？**  
   不值得。

## Final verdict
- `verdict`: `keep_park`
- `original_verdict_kept`: `park`
- `one-line note`: `soft park，但比 4 月 13 日那轮更接近 hard with consumed residual；4 月 20~22 的 speed-volume continuation 与 US close-window reversal 新证据继续说明，时钟信息若还有价值，更像新的 event/time-window raw-alpha 宿主，而不是足以把 old Rank 5 的 direct session-tail 写法再诚实派生成 Rank 5c。`

## File actions
- 新增：`research/park_reframe/2026-04-22_1704_rank5-park-reframe.md`
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## Git / 提交
- 本轮默认不做 commit。
- 原因：`git status --short` 显示工作区存在大量无关未跟踪脏文件；按要求不混提，本轮只做最小必要文档更新。
