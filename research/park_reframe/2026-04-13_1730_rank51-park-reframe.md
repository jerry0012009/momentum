# 2026-04-13 17:30 UTC · Rank 51 park reframe

## Selected rank
- `Rank 51`
- selection note: 本轮继续按 `50~79` 号段低频轮转，只处理 1 条已 `park` 条目。`Rank 51` 上次 park-reframe 是 `2026-04-04 00:38 UTC`，已超过 `7` 天；同时 4 月 9 日又新增了更明确的 `session-anchor / VWAP` continuation 旁证，足够再判断一次：这些新证据是在救旧 `session VWAP reclaim + breadth gate`，还是继续把它的主题外流到新的宿主。

## Original park reason
原始 authoritative 证据：
- `research/optimization_loop/2026-03-18_0845_rank51-vwap-source-intake.md`
- `research/optimization_loop/2026-03-18_0922_rank51-clean-replication-park.md`
- 上轮 bot6 复盘：`research/park_reframe/2026-04-04_0038_rank51-park-reframe.md`

原 `Rank 51 / session VWAP reclaim + breadth gate` 被 park 的原因没有变化：它把 **session VWAP reclaim + breadth** 写成可服务 continuation / retest 主线的 shared confirmation gate，但最小 clean replication 证明，这条线虽然能明显降低 false retest，却仍主要是在“少犯错”，不是 desk 口径下可部署的赚钱 gate。

冻结版关键结果（`BTC/ETH/SOL 120d 15m`, `6bps/side`, `next-bar open`, `no-overlap`）：
- `touch_only`：`mean_total_return ≈ -79.13%`，`mean_trades ≈ 1081.7`，`false_retest_4bars_rate ≈ 75.57%`
- `touch_plus_reclaim`：`mean_total_return ≈ -49.69%`，`mean_trades ≈ 580.0`，`false_retest_4bars_rate ≈ 47.70%`
- `touch_reclaim_plus_breadth`：`mean_total_return ≈ -43.79%`，`positive_asset_ratio = 0/3`，`mean_trades ≈ 423.3`，`trade_count_retention ≈ 39.10%`，`false_retest_4bars_rate ≈ 39.20%`
- time pocket 三段仍全负，说明不是某个时段 pocket 没挖到，而是 24/7 crypto 迁移版本整体不成立。

翻成人话：
- `VWAP reclaim` 不是零信息；
- `breadth` 也确实把假回踩压下来了；
- 但它留下的价值更像“把明显差的单子过滤掉一些”，而不是形成诚实的 queue-facing admission；
- 因此原 `park` 的审计意义必须保留：失败对象是“把 session VWAP reclaim + breadth 写成跨宿主共享 gate”，不是 `VWAP` 主题整体死亡。

## Hard park or soft park?
- 本轮判断：`soft park，但比 4 月 4 日那轮更接近 hard`

为什么仍不是 hard park：
1. 原 clean replication 至少证明了 `VWAP reclaim` 的方向感不完全错，`false_retest` 的确能明显下降；
2. 这说明“接受度 / hold-reclaim”语义仍有 residual information。

为什么又更接近 hard：
1. `positive_asset_ratio = 0/3` 这点没有变；
2. 改善仍主要来自把交易砍到约 `39% retention`，不是把 shared gate 抬成正期望；
3. 新证据越来越像在支持 **新的 session-anchor / VWAP raw-alpha 宿主**，而不是支持旧 `Rank 51` 再窄救一刀。

## Any salvage signal?
有，但更像“session-anchor / VWAP 主题外流”，不是旧 `Rank 51` 自己还能诚实窄救。

本轮最 relevant 的新增旁证：
- `research/quant_digests/2026-04-09_2235_anchor-open-vwap-sigma-continuation-alpha.md`

这条新 digest 比 4 月 4 日那轮又更明确地说明：
1. `session anchor + VWAP` 主题本身仍有信息；
2. 但更自然的活法是 **anchor-open displacement × minute-vol breakout continuation** 这种完整 raw-alpha 壳；
3. 也就是把 `session anchor` 当成 **主语**，再配 `VWAP` 同向确认与会话内 continuation，而不是把 `session VWAP reclaim + breadth` 降级成现有 15m setups 的 shared defense gate；
4. 这进一步说明，旧 Rank 51 的 blocker 不是 breadth 还不够精细，而是 **宿主层摆错了**。

因此，本轮能保留的“可救信号”只有一句：
- **session-anchor / VWAP 主题仍有价值，但它更像新的 raw-alpha 宿主，而不是旧 Rank 51 这条 shared gate 还值得再派生出 `Rank 51b`。**

## Single best cut
如果只保留唯一一刀，本轮最值得改的唯一一刀仍然是：

> **把 fixed session VWAP reclaim + breadth gate 改写成 session-anchor-led VWAP continuation host。**

但这刀为什么仍不诚实地属于 `Rank 51b`：
1. 它已经把主语从 `shared gate` 改成了 `raw alpha host`；
2. 也把原 rank 的职责层从 “existing setup 的防守确认” 改成了 “anchor-open displacement 自己驱动入场”；
3. 这不是旧 rank 内部的窄 reframe，而是换宿主。

## Derived hypothesis?
- 结论：`keep_park`
- 不新增 `derived hypothesis`

为什么这轮仍不值得 draft `Rank 51b`：
1. 原 `park` verdict 没被推翻；
2. 原 rank 唯一还诚实的残余，仍只是“VWAP reclaim 有减少假回踩的语义”，而不是新的 queue-facing gate；
3. 4 月 9 日的新证据把主题进一步推向新的 `session-anchor / VWAP continuation` raw-alpha 宿主；
4. 若现在硬写 `Rank 51b`，本质会是借新 family 给旧 session-gate 续命，模糊原审计边界。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但比 4 月 4 日那轮更接近 hard；4 月 9 日新增的 anchor-open displacement × VWAP continuation 证据继续说明 session-anchor / VWAP 主题仍有信息，但它救活的是新的 session-anchor raw-alpha 宿主，而不是旧 Rank 51 的 session VWAP reclaim + breadth gate，因此当前不诚实 draft Rank 51b`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## Commit
- 本轮默认不做 commit。
- 原因：工作区存在大量与本轮无关的共享脏文件，不安全做 selective commit，避免混提。
