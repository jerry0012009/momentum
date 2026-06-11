# 2026-04-04 18:46 UTC · Rank 55 park reframe

## Selected rank
- `Rank 55`
- selection note: 本轮继续遵循 `50~79 -> 80~110 -> 1~24 -> 25~49` 的低频轮转，并优先避开最近 `7` 天已经复盘过的条目。`Rank 55` 自 `2026-03-18` 被压回 `park` 后，尚未见 bot6 单独复盘；同时最近新增的 `signed trade imbalance / pressure-ratio absorption` 两条 microstructure digest，正适合回答一次：这些新证据是在救旧的 `shared crash-risk overlay`，还是只是在把主动成交失衡主题继续外流到新的、更诚实的单资产 raw-alpha family。

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/park_reframe/2026-04-04_1616_rank73-park-reframe.md`
- `research/park_reframe/2026-04-04_1352_rank80-park-reframe.md`
- `research/park_reframe/2026-04-04_1140_rank59-park-reframe.md`
- `research/optimization_loop/2026-03-18_1142_rank55-crash-risk-intake.md`
- `research/optimization_loop/2026-03-18_1249_rank55-clean-replication.md`
- `research/optimization_loop/2026-03-18_1348_rank55-time-stability-park.md`
- `research/quant_digests/2026-04-04_0849_signed-flow-imbalance-maker-conviction-alpha.md`
- `research/quant_digests/2026-04-04_1748_orderbook-pressure-downbar-reversal-alpha.md`
- `research/park_reframe/2026-04-04_0238_rank52-park-reframe.md`
- `research/park_reframe/2026-04-03_0919_rank62-park-reframe.md`

## Original park reason
原始 authoritative 证据：
- `research/optimization_loop/2026-03-18_1142_rank55-crash-risk-intake.md`
- `research/optimization_loop/2026-03-18_1249_rank55-clean-replication.md`
- `research/optimization_loop/2026-03-18_1348_rank55-time-stability-park.md`

原 `Rank 55` 被 park 的原因没有变：它想把 **order-imbalance crash-risk** 写成服务 `ema_psar_long / fib_retest_long / breakout_short` 的 shared risk overlay，但最小 clean replication 和随后 time-stability 都说明，这条线只在 `ema_psar_long` 上留下很薄的少亏 pocket，没能形成跨 setup 一致、值得继续占用 queue 的 shared crash layer。

冻结版关键结果：
- clean replication（`BTC/ETH/SOL 120d 15m`, `next-bar open`, `no-overlap`, `hold 8 bars`）里：
  - `ema_psar_long`: `base≈+1.63% -> binary_crash_gate≈+3.15% -> size_haircut≈+2.40%`
  - `fib_retest_long`: `base≈+0.03% -> binary_crash_gate≈+0.00% -> size_haircut≈+0.02%`
  - `breakout_short`: `base≈-2.49% -> binary_crash_gate≈-1.88% -> size_haircut≈-2.68%`
- 便宜 time-stability 后：
  - `breakout_short` 三个变体在三个时间窗口里全部非正；
  - `fib_retest_long` 只剩贴近噪音的小正窗口；
  - 唯一三段都为正的是 `ema_psar_long + binary_crash_gate`，但每桶平均 trades 只有约 `1.7~2.7`。

翻成人话：
- 主动成交失衡 / crash-pressure 不是零信息；
- 但把它写成 `15m` base setups 共用的 shared crash overlay，并没有得到足够诚实的跨 setup 证据；
- 原 `park` 的审计意义必须保留：**失败对象是“shared crash-risk overlay”这层职责，不是主动成交失衡 / absorption 主题整体死亡。**

## Hard park or soft park?
- 本轮判断：`soft park，但已明显偏硬`

为什么不是 pure hard park：
1. `ema_psar_long` 上确实留下了一点 loser-control / crash-avoidance 的残余；
2. 说明“最近主动卖压/失衡会让 continuation long 更危险”这层语义不是纯噪音。

为什么又已明显偏硬：
1. 真正留下 pocket 的只有单一 archetype；
2. `fib_retest_long` 基本没有增量，`breakout_short` 也没被修好；
3. 最近更强的新证据，已经不再支持把这类信息继续写成 `15m shared risk overlay`，而是在把主语改写成 **更快、更原生的单资产 microstructure raw alpha**。

## Any salvage signal?
有，但更像“主题外流”，不是旧 `Rank 55` 自己还能诚实窄救。

本轮最 relevant 的新旁证：
- `research/quant_digests/2026-04-04_0849_signed-flow-imbalance-maker-conviction-alpha.md`
- `research/quant_digests/2026-04-04_1748_orderbook-pressure-downbar-reversal-alpha.md`

它们合起来给出的关键信号是：
1. 真正更像样的主语，不是 `base setup` 前的一层 shared crash gate；
2. 而是 **single-asset signed-flow / pressure-ratio / absorption 本身**，在 `1m~5m` 上直接形成 continuation 或 downbar-reversal raw alpha；
3. 也就是说，主动成交失衡这个主题还活着，但它更自然的新宿主是：
   - `1m signed flow imbalance × 5m forward return × maker-only conviction gate`；或
   - `5m 下跌 + 买压失衡 -> 30~60m 反弹` 的单币吸收型均值回复 alpha；
4. 这和 `Rank 52 / Rank 62` 的审计边界一致：microstructure / OFI / trade-flow 主题最近都更像在外流到新的 raw-alpha / execution family，而不是回流去救旧 shared gate / overlay 写法。

## Single best cut
如果只保留唯一一刀，本轮最像样的改写方向会是：

> **replace shared crash-risk overlay with a single-asset downbar-absorption / signed-flow raw-alpha host on 1m/5m timing horizons**

也就是：
- 不再把它写成 `ema_psar_long / fib_retest_long / breakout_short` 的前置 shared crash gate；
- 只承认极端主动成交失衡 / buy-pressure absorption 本身，在更快时钟上直接形成独立 microstructure entry / execution alpha；
- 若要服务更慢的 `5m / 15m` 主线，也更像 execution timing / adverse-selection veto，而不是旧 Rank 55 那种 queue-facing shared overlay。

但这刀本轮**不够诚实地属于 `Rank 55`**，因为：
1. 它已经把主语从 `shared crash overlay` 换成了 `single-asset microstructure raw alpha`；
2. 它不再保留旧 rank 的职责层；
3. 若硬写成 `Rank 55b`，本质是在借新的 raw-alpha 宿主给旧 overlay 续命。

## Derived hypothesis?
- 结论：`keep_park`
- 不新增 `derived hypothesis`

为什么这次不值得 draft `Rank 55b`：
1. 原 `park` verdict 没被推翻；
2. 原 rank 剩下的残余价值，更像“主动成交失衡在更快时钟上仍有原生 edge”，而不是新的 `15m` shared crash gate；
3. 最近最强新证据在把该主题推向新的 single-asset raw-alpha / execution family，不该错挂到旧 `Rank 55` 名下；
4. 若后续 bot2 要认领，更诚实的做法应是直接认领新的 microstructure raw-alpha intake，而不是写回一个名义上的 `Rank 55b`。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但已明显偏硬；最近新增的 signed-flow / pressure-ratio absorption 证据说明，Rank 55 的残余价值更像新的单资产 microstructure raw-alpha / execution family，而不是旧 shared crash-risk overlay 的诚实窄派生，不足以再诚实派生 Rank 55b`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## Commit
- 本轮默认不做 commit。
- 原因：仓库存在共享脏文件风险；本轮只做最小必要文档改动，避免混提。
