# 2026-04-22 00:28 UTC — Rank 29 park reframe review

- loop: `bot6 park-reframe`
- source rank: `Rank 29 / trendline breakout navigator / multi-swing structural breakout state machine`
- current authoritative verdict: `park / archived`
- this round verdict: `keep_park`
- original park verdict kept: `yes`

## Why this rank this round
- 本轮按用户要求只看 `Rank 1~37` 里已 `park` 的旧条目，而不是做 bot2 desk review / bot3 主循环。
- 近 7 天内 `Rank 1~37` 大多数 parked 条目已被 bot6 复盘；`Rank 29` 上次 park-reframe 是 `2026-04-13 05:17 UTC`，已超过 7 天。
- 4 月 19~20 日又补了两条足够相关的新证据：
  - `2026-04-19_2049_retest-rebreak-short-continuation-alpha.md`
  - `2026-04-20_1310_liquidity-sweep-rejection-bounce-alpha.md`
  它们都说明“结构事件”主题仍有信息，但值得重新检查：这些新证据救活的是旧 `Rank 29`，还是只是在别的 strict-causal 宿主里成立。

## Read set used this round
- `docs/BOT6_PARK_REFRAME_BRIEF.md`
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent reframe reference: `research/park_reframe/2026-04-21_2220_rank13-park-reframe.md`
- prior rank evidence:
  - `research/optimization_loop/2026-03-17_0921_rank29-clean-replication.md`
  - `research/optimization_loop/2026-03-17_0925_rank29-no-overlap-honesty-check.md`
  - `docs/RANK29_POSTMORTEM_2026-04.md`
  - `research/park_reframe/2026-04-13_0517_rank29-park-reframe.md`
- new side evidence:
  - `research/quant_digests/2026-04-19_2049_retest-rebreak-short-continuation-alpha.md`
  - `research/quant_digests/2026-04-20_1310_liquidity-sweep-rejection-bounce-alpha.md`

## 1) 原 rank 为什么 park？
原 `Rank 29` 被 park，不是因为“结构 breakout 主题整体没戏”，而是因为**旧宿主的 baseline honesty 已失效**。

原先 3 月 17 日的 clean replication 一度看起来很强：
- `breakout_align_ge2`
- `6bps/side` 下 `mean_total_return≈+75%~80%`
- `positive_asset_ratio=3/3`
- no-overlap 后也一度还能存活

但 4 月 postmortem 把真正的 blocker 审计清楚了：
- `pivot / trendline` 状态会被后续确认信息回填到更早 bars；
- 这会改写历史上的 `line_value / line_slope / active_pivot_origin / composite trend`；
- 结果是旧回测里很多“当时可交易”的 breakout，其实是 hindsight-only。

strict-causal 审计的结论仍然是本轮最关键的锚：
- 主版本 `breakout_align_ge2` 在 `causal_replay` 下：`0` 笔交易；
- 放宽到 `breakout_align_ge1`：整体转负，且 `false_break_ratio` 很高；
- 主样本污染比例被审计成 `100%`（旧口径 `449` 笔，strict-causal 真信号 `0` 笔）。

所以原 `park` 的审计意义必须保留：
> 被否掉的是旧 `Rank 29` 这套 backfilled multi-swing trendline breakout 宿主，不是所有结构事件 alpha。

## 2) 它更像 hard park 还是 soft park？
**本轮判断：`hard park`。**

而且比 4 月 13 日那轮更能确认这一点：
1. blocker 不是“只差一个 gate / veto / bucket”；
2. blocker 是旧宿主的可交易性定义本身不诚实；
3. 4 月 19~20 的新证据虽然说明结构主题还活着，但都落在**可冻结的单事件宿主**上，不再支持旧 multi-swing trendline state machine。

换句话说，旧 `Rank 29` 的问题不是实现偏粗，而是母壳错了。

## 3) 有没有“可救信号”？
**有，但它已经明确是主题级 residual，不再是旧 rank 级 residual。**

两条新证据都指向同一方向：
- `retest-rebreak-short-continuation` 保留的是：下破后回踩、再在固定窗口内跌破 impulse low，这是一条 strict-causal 的短周期延续 raw alpha；
- `liquidity-sweep-rejection-bounce` 保留的是：扫穿前低但当根收回，随后做 panic-bounce continuation，这同样是单事件、因果冻结、可直接下单的 raw alpha。

它们共同说明：
> 结构主题若还有 edge，更像“事件锚 + 固定确认 + next-bar 执行”的新 raw-alpha family，而不是旧 `Rank 29` 那种需要多 swing trendline / composite trend 回填的宿主。

因此“可救信号”存在，但它救活的是新的 structural event family，不是旧 `Rank 29` 本体。

## 4) 最值得改的唯一一刀是什么？
如果只回答“最值得改的唯一一刀”，最诚实的说法仍然是：

> **放弃 backfilled multi-swing trendline breakout state machine，改写成 strictly causal 的单事件结构锚（如 retest→re-break / liquidity-sweep→reclaim）。**

但这正是本轮不 draft 的原因：
- 这不是旧 `Rank 29` 的窄修补；
- 它不是“原 rank + 一层确认”，而是把宿主换成新的 event-defined raw alpha；
- 因而更像新 intake family，不是诚实的 `Rank 29b`。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。本轮继续 `keep_park`。**

原因：
1. 原 `park / archived` verdict 没被推翻；
2. 新证据强化的是“结构主题能活在别的 causal 宿主里”，不是“旧 Rank 29 还能再切一刀”；
3. 若现在硬写 `Rank 29b`，会把“换宿主重开”误包装成“旧 rank 的窄 reframe”；
4. 对 bot2 更诚实的做法，是把这类新证据留给未来独立 intake / raw-alpha family，而不是继续给旧 `Rank 29` 维持 queue-facing residual 身份。

## Direct answers required by the brief
- **原 rank 为什么 park？**
  - 因为 strict-causal 审计确认旧 trendline breakout baseline 存在严重回填污染；主版本在 causal replay 下直接变成 `0` 笔交易，放宽版也整体转负，旧宿主不再诚实可交易。
- **它更像 hard park 还是 soft park？**
  - `hard park`。
- **有没有“可救信号”？**
  - 有；结构事件主题仍有信息，但只在 `retest→re-break`、`sweep→reclaim` 这类 strict-causal 单事件宿主里成立，不属于旧 `Rank 29` 本体残余。
- **最值得改的唯一一刀是什么？**
  - 把 backfilled trendline state machine 换成 strictly causal 的单事件结构锚。
- **是否值得形成新的 derived hypothesis？**
  - 不值得；本轮不 draft `Rank 29b`。

## Final verdict
- `final_status = keep_park`
- `original verdict kept = park`
- short note:
  - `hard park；4 月 19~20 的 retest→re-break 与 liquidity-sweep 新证据进一步说明，结构主题若还有信息，也只在 strictly causal 的单事件 raw-alpha 宿主里成立，而不是足以把 old Rank 29 backfilled trendline breakout 再诚实派生成 Rank 29b。`

## Queue action
- keep `Rank 29` parked / archived
- do **not** draft `Rank 29b`
- do **not** modify `docs/TODO.md`

## Git / commit note
- 本轮只做 park-reframe 所需最小文本更新。
- 当前共享工作区已有无关脏文件；为避免混入前序变更，本轮不做 commit。
