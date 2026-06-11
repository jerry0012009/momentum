# 2026-04-15 10:59 UTC · Rank 7 park reframe

## Selected rank
- `Rank 7`
- selection note:
  - 本轮继续严格只处理 `1` 条已 `park` 的 `Rank 1~37`。
  - `1~24` 里多数条目最近 `7` 天已被 bot6 复盘；`Rank 2 / Rank 17` 又不是 parked 对象。
  - `Rank 7` 上次 bot6 复盘是 `2026-04-08 21:44 UTC`，虽未满完整 `7` 天，但其后出现了与该主题直接相关的新证据（`2026-04-13_2044_watchlist-topscore-rotation-shell.md`、`2026-04-14_0140_dailyveto-technicalvote-shell.md`），足以做一次低频复核：这些新证据究竟支持旧 Rank 7 再切一刀，还是进一步证明主题应迁到新的 full-shell/raw-alpha 宿主。

## Source evidence read
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/park_reframe/2026-04-15_0859_rank1-park-reframe.md`
- `research/park_reframe/2026-04-15_0609_rank28-park-reframe.md`
- `research/park_reframe/2026-04-15_0355_rank56-park-reframe.md`
- `research/optimization_loop/2026-03-16_2221_rank7-clean-replication-park.md`
- `research/optimization_loop/2026-03-17_0524_rank7-honesty-recheck-park.md`
- `research/park_reframe/2026-03-25_2003_rank7-park-reframe.md`
- `research/optimization_loop/2026-04-07_2329_rank7c_bandpass_overlay_not_frontslot_intake.md`
- `research/quant_digests/2026-04-13_2044_watchlist-topscore-rotation-shell.md`
- `research/quant_digests/2026-04-14_0140_dailyveto-technicalvote-shell.md`

## Original park reason
原 `Rank 7 / adaptive trend combo` 被 park 的审计结论没有变化。

它被否掉的不是“趋势信息”本身，而是：
- **把 adaptive combo 写成 `15m` bar-level direct blended entry vote** 这件事不成立；
- 看起来最不差的 `fixed_priority` 版本依赖极端稀疏交易：`mean_no_trade_ratio≈98.60%`；
- 一旦把门槛放松到更可交易的密度，收益、跨资产与成本口径会一起塌掉：
  - `ema_plus_one`：`mean_no_trade_ratio≈21.10%`，但 `mean_total_return≈-33.68%`，`positive_asset_ratio=0/3`
  - `ema_plus_retest`：`mean_no_trade_ratio≈21.10%`，但 `mean_total_return≈-34.42%`，`positive_asset_ratio=0/3`

因此原 `park` verdict 的审计意义必须保留：
> **旧 Rank 7 不能再被诚实地读成一个统一的、可部署的 direct combo entry engine。**

## Hard park or soft park?
- 结论：`soft park，但对原 Rank 7 本体已更接近 hard with consumed residual`

为什么仍保留 soft：
- 被否掉的是“direct entry vote”这个角色，不是 adaptive trend / alignment 主题本身；
- 它确实曾留下过两个诚实 residual：
  - `Rank 7b`：`one-regime-per-session shared allocation overlay`
  - `Rank 7c`：`mid-score band-pass continuous alignment overlay`

为什么又更接近 hard：
- `2026-03-25` 已经明确写过：若继续从 Rank 7 往外长新旁支，大概率只是把“慢信号、快执行”换壳重述；
- `2026-04-07` 又专门做过一次 `Rank 7c` front-slot guard，结论是：`Rank 7c` 仍只应保留为 queue-only residual，不应再被重新包装成新的 intake；
- 也就是说，旧 Rank 7 的唯一自然 residual 已经被 `7b / 7c` 两条线基本消费完。

## Any salvage signal?
有，但这次仍然**不是旧 Rank 7 本体的新可救轴**，而是主题迁移信号更强了。

### A. 2026-04-13 watchlist top-score rotation shell
这条证据说明：
- 真正值得保留的是 **`oversold-in-uptrend resumption` 单币 alpha × `watchlist top-score rotation` 组合壳**；
- 也就是“单币 resumption + 跨币机会路由”的完整 raw-alpha / routing shell；
- 这已经不是旧 Rank 7 的 bar-level combo vote，而是新的 `single-asset pullback-resumption + routing` 宿主。

### B. 2026-04-14 daily-trend veto × 15m technical-vote continuation shell
这条证据更直接：
- `15m technical vote` 若还能活，关键也更像 **完整壳里的 `daily-trend veto` / score 分层 / risk shell**；
- 而不是旧 Rank 7 这种“把多组件投票压成直接开仓键”的写法。

因此，本轮真正读到的“可救信号”是：
> **adaptive / technical combo 主题仍有信息，但活着的方式更像完整 full-shell/raw-alpha 宿主，而不是旧 Rank 7 再切出一条新的 queue-facing 单轴 reframe。**

## Single best cut
如果只谈旧 `Rank 7` 最值得保留的唯一一刀，仍然只是既有那条：

**把 adaptive trend combo 从 direct blended entry vote 降级成 setup 触发后的 alignment overlay。**

也就是已存在的 `Rank 7c`：
- 不让 combo 自己直接触发；
- 只在 `breakout-short / Fib retest_hold / EMA-PSAR continuation` 已触发后，用 alignment score 做中段放行、尾部降仓/否决。

但这不是新的修改轴：
- 它已被 `Rank 7c` 完整表达；
- 也已被 `2026-04-07` 的 intake guard 明确消费过；
- 因此当前不诚实再写 `Rank 7d`。

## Is a new derived hypothesis warranted?
- 结论：`keep_park`
- 不形成新的 `derived hypothesis`

原因：
1. 原 `park` 结论没有被推翻；
2. 旧 Rank 7 唯一诚实 residual 仍只到既有 `Rank 7b / 7c`；
3. `2026-04-13 ~ 2026-04-14` 的新证据继续把主题抬升到新的 `pullback-resumption / technical-vote continuation` full-shell/raw-alpha 宿主，而不是支持从旧 Rank 7 再诚实切出新的单轴；
4. 现在再 draft `Rank 7d`，要么只是重复 `7b / 7c`，要么就是偷换到新的宿主，不诚实。

## Final verdict
- `verdict`: `keep_park`
- `original_verdict_kept`: `park`
- `one-line note`: `soft park，但对原 adaptive blended entry vote 读法已更接近 hard with consumed residual；4 月 13~14 日新证据继续说明 combo 主题若还有信息，更像新的 pullback-resumption / daily-veto technical-vote full-shell 宿主，而不是足以从旧 Rank 7 再诚实派生 Rank 7d。`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## Commit
- 本轮默认不做 commit。
- 原因：只做最小必要文档改动；且仓库长期存在无关脏文件，避免混提。
