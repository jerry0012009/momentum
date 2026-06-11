# 2026-04-04 02:38 UTC · Rank 52 park reframe

## Selected rank
- `Rank 52`
- selection note: 本轮继续遵循 `50~79 -> 80~110 -> 1~24 -> 25~49` 的低频轮转，并优先避开最近 `7` 天已被 bot6 单独复盘的条目。`Rank 52` 自 `2026-03-18` clean replication 压回 `park` 后，尚未被 bot6 单独复盘；同时最近新增的 `extreme trade-flow z-score × next-5m continuation` 与更早的 `single-asset OFI + VWAP pressure taker raw alpha` 两条 microstructure digest，正适合回答一次：这些新证据是在救旧的 `15m trade-flow imbalance veto` shared gate，还是只是在把 trade-flow 主题继续外流到新的、更诚实的 raw-alpha / execution family。

## Original park reason
原始 authoritative 证据：
- `research/optimization_loop/2026-03-18_0950_rank52-trade-flow-intake.md`
- `research/optimization_loop/2026-03-18_1011_rank52-clean-replication-park.md`

原 `Rank 52` 被 park 的原因没有变：它把 **setup 前最后几分钟的主动成交失衡** 写成可服务 `ema_pullback_long / breakdown_reclaim_short` 的 shared veto gate，但最小 clean replication 证明，这条线虽然带有一点“少追错方向单子”的 loser-control 语义，却不足以在 desk 口径下形成可部署的 queue-facing gate。

冻结版关键结果（`BTC/ETH/SOL 120d 15m`, `next-bar open`, `no-overlap`, `hold 8 bars`）：
- 主读法 `breakdown_reclaim_short + opposite_flow_veto @ 6bps/side`：`mean_total_return ≈ -2.73%`，`positive_asset_ratio = 0/3`，`mean_trades ≈ 17.0`，`trade_count_retention ≈ 81.90%`，`mean_false_break_or_hold_4bars_rate ≈ 85.65%`
- 对照 `ema_pullback_long + opposite_flow_veto @ 6bps/side`：`mean_total_return ≈ -4.04%`，`trade_count_retention ≈ 57.87%`
- time pocket 仍是中后段偏负，没有形成可升格的单一稳定 pocket。

翻成人话：
- trade-flow 失衡不是零信息；
- 但把它降成 `15m` 级 shared veto 后，留下的主要是“略微少犯错”，不是足够诚实的 queue-facing admission；
- 因此原 `park` 的审计意义必须保留：失败对象是“把 trade-flow imbalance 写成 15m base setup 的 shared veto gate”，不是 trade-flow / OFI 主题整体死亡。

## Hard park or soft park?
- 本轮判断：`soft park，但已明显偏硬`

为什么不是 hard park：
1. 原 clean replication 至少说明，这条线并非纯噪音；它确实留下了一点反方向 veto / loser-control 的语义。
2. 这说明主动成交压力本身仍有 residual information，不是完全空的主题。

为什么又已明显偏硬：
1. `positive_asset_ratio = 0/3`，成本后三个币都没活下来；
2. 改善没有形成诚实的稳定 pocket，更多只是轻微降损；
3. 最近更强的新证据，不再支持把 trade-flow 继续写成 `15m` shared gate，而是在把主语改写成 **更快、更原生的 microstructure raw alpha / execution layer**。

## Any salvage signal?
有，但更像“主题外流”，不是旧 `Rank 52` 自己还能诚实窄救。

本轮最 relevant 的新旁证：
- `research/quant_digests/2026-04-02_1140_extreme-ofi-tradeflow-continuation-alpha.md`
- `research/quant_digests/2026-03-25_0318_single-asset-microstructure-taker-alpha.md`

它们合起来给出的关键信号是：
1. 真正更像样的主语，不是 `15m` base setup 前的一层 shared veto；
2. 而是 **同一标的自身 extreme trade-flow / OFI → 接下来 1m~5m 的短延续或 event-driven execution alpha**；
3. 换句话说，可救信号确实存在，但它救的是 trade-flow 主题作为 **raw alpha / execution host** 的角色，而不是旧 `Rank 52` 这条 `15m` shared veto 写法。

## Single best cut
如果只保留唯一一刀，本轮最像样的改写方向会是：

> **replace 15m shared trade-flow veto with an event-driven extreme trade-flow / OFI raw-alpha host on 1m/3m timing horizons**

也就是：
- 不再把 flow 写成 `ema_pullback_long / breakdown_reclaim_short` 的前置 shared deny gate；
- 只承认极端主动成交失衡本身，在更快时钟上直接形成独立 microstructure entry / execution alpha；
- 若要服务更慢的 `5m / 15m` 主线，也更像 execution timing / adverse-selection veto，而不是旧 Rank 52 那种 queue-facing shared gate。

但这刀本轮**不够诚实地属于 `Rank 52`**，因为：
1. 它已经把主语从 `15m shared veto` 换成了 `1m/3m raw alpha / execution family`；
2. 它不再保留旧 rank 的职责层；
3. 若硬写成 `Rank 52b`，本质是在借新的 microstructure 宿主给旧 gate 续命。

## Derived hypothesis?
- 结论：`keep_park`
- 不新增 `derived hypothesis`

为什么这次不值得 draft `Rank 52b`：
1. 原 `park` verdict 没被推翻；
2. 原 rank 剩下的残余价值，更像“主动成交失衡在更快时钟上可能仍有原生 edge”，而不是新的 `15m` 窄 gate；
3. 最近最强新证据在把 trade-flow / OFI 主题推向新的 single-asset microstructure raw-alpha / execution family，而不是支持旧 shared-veto residual；
4. 若后续 bot2 要认领，更诚实的做法应是直接认领新的 microstructure raw-alpha intake，而不是挂回 `Rank 52` 名下。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但已明显偏硬；最近新增的 extreme trade-flow / OFI 证据说明，Rank 52 的残余价值更像新的单资产 microstructure raw-alpha / execution family，而不是旧 15m trade-flow imbalance shared veto 的诚实窄派生，不足以再诚实派生 Rank 52b`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## Commit
- 本轮默认不做 commit。
- 原因：只做最小必要文档改动；且仓库存在共享脏文件风险，避免混提。
