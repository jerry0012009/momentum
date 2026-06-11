# 2026-04-04 00:38 UTC · Rank 51 park reframe

## Selected rank
- `Rank 51`
- selection note: 本轮继续遵循 `50~79 -> 80~110 -> 1~24 -> 25~49` 的低频轮转，并优先避开最近 `7` 天已被 bot6 单独复盘的条目。`Rank 51` 自 `2026-03-18` clean replication 压回 `park` 后，尚未被 bot6 单独复盘；同时最近新增的 `VWAP-EMA directional change` 新 digest 与更早的 `Rank 58 / event-anchored VWAP hold-reclaim spine` 都能帮助判断：这些新证据是在救旧的 `session VWAP reclaim + breadth gate`，还是只是在把 VWAP 主题继续外流到别的、更诚实的宿主。

## Original park reason
原始 authoritative 证据：
- `research/optimization_loop/2026-03-18_0845_rank51-vwap-source-intake.md`
- `research/optimization_loop/2026-03-18_0922_rank51-clean-replication-park.md`

原 `Rank 51` 被 park 的原因没有变：它把 **session VWAP reclaim + breadth** 写成一条可服务 continuation / retest 主线的 shared confirmation gate，但最小 clean replication 证明，这条线虽然明显降低了 false retest，却仍主要是在“少犯错”，不是在 desk 口径下形成可部署的赚钱 gate。

冻结版关键结果（`BTC/ETH/SOL 120d 15m`, `6bps/side`, `next-bar open`, `no-overlap`）：
- `touch_only`：`mean_total_return ≈ -79.13%`，`mean_trades ≈ 1081.7`，`false_retest_4bars_rate ≈ 75.57%`
- `touch_plus_reclaim`：`mean_total_return ≈ -49.69%`，`mean_trades ≈ 580.0`，`false_retest_4bars_rate ≈ 47.70%`
- `touch_reclaim_plus_breadth`：`mean_total_return ≈ -43.79%`，`positive_asset_ratio = 0/3`，`mean_trades ≈ 423.3`，`trade_count_retention ≈ 39.10%`，`false_retest_4bars_rate ≈ 39.20%`
- time pocket 三段仍全负，说明不是某个时段特例，而是 24/7 crypto 迁移版本整体不成立。

翻成人话：
- VWAP reclaim 不是零信息；
- breadth 也确实帮它少踩了不少假回踩；
- 但它留下的主要价值是“把明显差的单子过滤掉一些”，而不是形成足够诚实的 queue-facing admission；
- 因此原 `park` 的审计意义必须保留：失败对象是“把 session VWAP reclaim + breadth 写成跨宿主共享 gate”，不是 VWAP 主题整体死亡。

## Hard park or soft park?
- 本轮判断：`soft park，但已明显偏硬`

为什么不是 hard park：
1. 原 clean replication 至少证明了 `VWAP reclaim` 的方向感不完全错，确实能把 `false_retest` 大幅压下来；
2. 这说明“库存成本线 / 接受度”这类语义仍有 residual information，不是纯噪音。

为什么又已明显偏硬：
1. `positive_asset_ratio = 0/3`，成本后三个币都没活下来；
2. 改善主要来自把交易砍到约 `39%` retention，而不是把共享 gate 直接抬成正期望；
3. `session VWAP` 在 `24/7 crypto` 上的任意性已经被原审计暴露得很清楚；
4. 最近更强的新证据都不再支持“继续把 Rank 51 收窄成一个 session gate”，而是在把 VWAP 主题改写成别的宿主。

## Any salvage signal?
有，但更像“VWAP 主题外流”，不是旧 `Rank 51` 自己还能诚实窄救。

本轮最 relevant 的旁证：
- `research/optimization_loop/2026-03-18_1505_rank58-source-intake.md`
- `research/quant_digests/2026-04-03_2251_dc-vwap-ema-asymmetric-trend-shell.md`

它们合起来给出的关键信号是：
1. `Rank 51` 的真正 blocker 不是“reclaim 这个词不对”，而是 **session anchor 放错了宿主层**；
2. `Rank 58` 已经给出更诚实的一刀：若还要保留 VWAP hold/reclaim 语义，更自然的是 **event-anchored VWAP**，而不是固定 `UTC session VWAP`；
3. 2026-04-03 的新 digest 又继续把 VWAP 主题往外推：更像一条 **VWAP-EMA directional change 的完整 trend raw-alpha shell**，甚至配套自己的非对称 exit，而不再只是 shared confirm line；
4. 换句话说，可救信号存在，但它更像“VWAP 本身仍有信息”，不是“旧 Rank 51 这条 session-gate 还值得再派生一个 Rank 51b”。

## Single best cut
如果只保留唯一一刀，本轮最像样的改写方向会是：

> **replace fixed session VWAP reclaim + breadth gate with an event-anchored / trend-spine VWAP host**

也就是：
- 不再把 `session VWAP` 当成 24/7 crypto 的共享 admission 线；
- 若保留 hold/reclaim 角色，应转向 `Rank 58` 那类 **event-anchored VWAP hold-reclaim spine**；
- 若进一步顺着最新证据走，则更像一条新的 **VWAP-EMA directional-change raw alpha / exit shell**。

但这刀本轮**不够诚实地属于 `Rank 51`**，因为：
1. 它已经把主语从 `session gate` 改成了 `event anchor` 或 `raw trend shell`；
2. 它不再保留旧 rank 的职责层；
3. 若硬写成 `Rank 51b`，本质是在借别的 VWAP 宿主给旧 session-gate 续命。

## Derived hypothesis?
- 结论：`keep_park`
- 不新增 `derived hypothesis`

为什么这次不值得 draft `Rank 51b`：
1. 原 `park` verdict 没被推翻；
2. 原 rank 唯一还诚实的残余，只是“VWAP reclaim 有过滤假回踩的语义”，而不是新的 queue-facing gate；
3. 这层残余已经被更诚实的宿主吸收或外流：
   - shared hold/reclaim 宿主：`Rank 58 / event-anchored VWAP`
   - 更上位的新对象：`VWAP-EMA directional-change` 完整 trend shell
4. 若现在硬写 `Rank 51b`，要么重复 `Rank 58`，要么偷换成新的 raw-alpha family，都会模糊原审计边界。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但已明显偏硬；Rank 51 的 residual value 更像“VWAP 主题外流到 event-anchored hold/reclaim 宿主或 VWAP-EMA trend shell”，而不是旧 session VWAP reclaim + breadth gate 的诚实窄派生，不足以再诚实派生 Rank 51b`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## Commit
- 本轮默认不做 commit。
- 原因：只做最小必要文档改动；且仓库存在共享脏文件风险，避免混提。
