# 2026-04-13 14:51 UTC · Rank 5 park reframe

## Selected rank
- `Rank 5`
- selection note: 本轮按 `Rank 1~37` 已 `park` 条目低频复盘。最近 7 天内多数低号 rank 都已被 bot6 覆盖；这轮选 `Rank 5`，因为它上次复盘是 `2026-04-08 14:39 UTC`，而 4 月 11~12 日又新增了更明确的 session-clock / session-pocket raw-alpha 旁证，足够再判断一次：这些新证据是在救旧 `Rank 5`，还是继续把它的主题外流到新的宿主。

## Original park reason
原始 authoritative 证据：
- `research/optimization_loop/2026-03-16_2149_intraday-tsmom-session-park.md`
- `research/park_reframe/2026-04-08_1439_rank5-park-reframe.md`

原 `Rank 5` 被 park 的原因没有变化：它把 **session 前段收益 / impulse** 直接写成了 **尾段跟随交易**，但这条 direct session-tail intraday TSMOM 在诚实口径下没有成立。

冻结审计里最关键的失败点：
- `net_return_bps = -6528.34`
- `cost_survival_floor = fail`
- `0/4` 成本档为正
- `mean_trades ≈ 145`，不是靠过稀交易被误杀
- 时间桶也没有留下可 admission 的稳定 pocket

翻成人话：
- 失败对象一直都是 **“前段动了，尾段直接跟”** 这条 standalone trade 写法；
- 不是 session / clock 信息彻底没意义；
- 也不是 opening impulse / close-pocket 主题整体死亡。

## Hard park or soft park?
- 本轮判断：`soft park，但对原 direct tail-trade 读法已更接近 hard`

为什么仍保留 soft：
1. session-aware / open-impulse 主题本身还活着；
2. 时钟信息仍可能以 gate、router 或独立 raw-alpha 宿主形式留下 residual value。

为什么又更接近 hard：
1. 原 Rank 5 的主语已经被反复审计清楚：`session 前段动量 -> 尾段直接跟单` 不成立；
2. 新证据越来越像在支持新的 session-clock family，而不是支持旧 Rank 5 再窄救一刀。

## Any salvage signal?
有，但仍然没有超出既有 `Rank 5b`，而且最近新证据更明确地把主题推向新的 raw-alpha 宿主。

本轮最 relevant 的新增旁证：
- `research/quant_digests/2026-04-11_0654_intraday-entropy-ratio-xs-reversal-alpha.md`
- `research/quant_digests/2026-04-12_0924_nyse-open-betaspread-continuation-alpha.md`

这些旁证共同在说：
1. **session / clock 信息没死**；
2. 但更诚实的活法更像 `session-to-session`、`NYSE-open session-pocket continuation`、`cross-sectional router` 这类更独立的 raw alpha；
3. 它们不是在证明旧 Rank 5 的 tail-follow 只差一个小过滤层，而是在把主题主语改写成新的 session-clock 宿主。

因此旧 rank 语境下唯一仍站得住的可救信号，依然只到既有 `Rank 5b`：
- 把 `direct session-tail intraday TSMOM entry`
- 降级成 `first-30m impulse-quality shared continuation gate / sizing layer`

## Single best cut
如果只保留唯一一刀，本轮仍然只有这条是诚实的：

> **demote direct session-tail intraday TSMOM entry into a first-30m impulse-quality shared continuation gate / sizing layer**

但这条轴：
1. 已经被既有 `Rank 5b` 起草过；
2. 本轮没有出现比它更窄、且仍属于旧 `Rank 5` 的新单轴；
3. 新证据反而更像在支持新的 session-clock raw-alpha family，而不是 `Rank 5c`。

## Derived hypothesis?
- 结论：`keep_park`
- 不新增 `derived hypothesis`

为什么这轮仍不值得 draft `Rank 5c`：
1. 原 `park` verdict 没被推翻；
2. 唯一诚实 residual 仍只是既有 `Rank 5b`；
3. 4 月 11~12 日的新 evidence 把主题抬升到更独立的 session-pocket / cross-sectional raw-alpha 宿主；
4. 若现在硬写 `Rank 5c`，更像借新 family 给旧 rank 续命，而不是诚实地保留旧 residual。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但对原 direct session-tail 读法已更接近 hard；4 月 11~12 日新增的 session-to-session / NYSE-open session-pocket 证据继续说明时钟信息仍有价值，但它救活的是新的 session-clock raw-alpha family，而不是旧 Rank 5 的 tail-follow 写法，因此当前不诚实 draft Rank 5c`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## Commit
- 本轮默认不做 commit。
- 原因：只做最小必要文档改动；且仓库存在共享脏文件风险，避免混提。
