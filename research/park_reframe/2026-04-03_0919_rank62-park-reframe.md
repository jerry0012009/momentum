# 2026-04-03 09:19 UTC · Rank 62 park reframe

## Selected rank
- `Rank 62`
- selection note: 本轮按 queue-facing 轮转优先从 `50~79` 号段里挑 1 条已 `park` 的 rank。`Rank 57` 刚在本日复盘过，而 `Rank 62` 自 `2026-03-18` 被压回 `park` 后尚未被 bot6 正式复盘；同时它属于“主题未必全死、但原 shared 角色明显摆错”的典型条目，适合做一次低频 reframe 审计。

## Original park reason
原始 authoritative 证据：
- `research/optimization_loop/2026-03-18_1813_rank62-source-intake.md`
- `research/optimization_loop/2026-03-18_1830_rank62-clean-replication-park.md`

原 `Rank 62` 被 park 的原因没有变：它想把 **continuation fail-fast overlay** 写成 `ema_psar_long / fib_retest_long / breakout_short` 三条 archetype 共用的 shared failure protocol，但最小 clean replication 只证明了“在 `ema_psar_long` 上更早认错能少亏一点”，没有证明它能形成跨 archetype 一致、值得 queue-facing 继续推进的 shared overlay。

冻结版最关键结果（`6bps/side`）：
- `ema_psar_long`: `base≈-5.55% -> ema+vwap+atr≈-3.92%`，但 `winner_truncation_rate≈37.5%`，`early_exit_rate≈76.2%`
- `fib_retest_long`: `base≈+0.88% -> ema+atr≈-0.35% -> ema+vwap+atr≈-1.88%`
- `breakout_short`: `base≈-2.58% -> ema+atr≈-3.25% -> ema+vwap+atr≈-3.12%`

翻成人话：
- fail-fast 主题不是完全没信息；
- 但把它写成三条线共用的 shared continuation-failure overlay 并不成立；
- 原审计意义必须保留：**失败对象是“continuation fail-fast 作为跨 archetype shared overlay 值得继续占用 scout 预算”这件事，不是快速认错 / 提前退出主题永远无效。**

## Hard park or soft park?
- 本轮判断：`soft park，但已明显偏硬`

为什么不是 pure hard park：
- `ema_psar_long` 上确实留下了一个可解释的残余：更快承认 continuation 走坏，能缩小 loser size。
- 说明 fail-fast / early-accept-loss 这类语义本身不是伪问题。

为什么又已明显偏硬：
- 改善只集中在单一 archetype；
- `fib_retest_long` 被明显过早截断，`breakout_short` 也没被修好；
- 这说明 shared overlay 这层角色基本已经被审计掉了。

## Any salvage signal?
有，但只剩一条很窄、而且更像“局部实现纪律”而不是 queue-facing 新对象。

本轮最 relevant 的新增旁证不是直接来自原 Rank 62，而是最近两批更短时钟 / execution 导向的材料继续把同主题分层得更清楚：
- `research/quant_digests/2026-04-02_0550_orderbook-delta-vote-microstructure-alpha.md`
- `research/quant_digests/2026-04-02_1140_extreme-ofi-tradeflow-continuation-alpha.md`

两者合起来给出的启发是：
1. 真正值得前排推进的，是 `1m/3m` 的 microstructure continuation raw-alpha / execution family；
2. 这类 family 需要自己的 entry/exit/cost 骨架，而不是先把 “早认错” 包装成一个上位 shared overlay；
3. 因而 `Rank 62` 还能留下的残余，不再像新的 queue-facing hypothesis，更像 **只对 EMA continuation lane 有用的本地 exit hygiene / loser-control note**。

换句话说：
- 可救信号存在；
- 但它不是在救原 `Rank 62` 的 shared overlay 读法；
- 它更像在提醒我们：真正活着的是更下游的 execution / microstructure family，而 `Rank 62` 自身只剩一点局部止损纪律价值。

## Single best cut
如果只保留唯一一刀，本轮最诚实的写法是：

> **demote shared continuation fail-fast overlay into an EMA-continuation-local exit-hygiene note**

也就是：
- 不再试图给 `fib_retest_long / breakout_short` 共用；
- 只承认它在 `ema_psar_long` 这类 continuation lane 里，可能有一点“缩 loser size、提前认错”的本地纪律价值；
- 但这条一刀并不值得升格成新的 queue-facing hypothesis，因为它更像 implementation hygiene，而不是新的独立 scout 对象。

## Derived hypothesis?
- 结论：`keep_park`
- 不新增 `derived hypothesis`

为什么这次不值得 draft `Rank 62b`：
1. 原 `park` verdict 仍完整成立；
2. 当前唯一还诚实的一刀，只是把它继续收口成局部 exit hygiene，而不是新的 queue-facing alpha / setup / admission package；
3. 最近新增的真正有活力的证据，已经转向 `1m/3m microstructure continuation` 原型，它们属于新的 raw-alpha / execution family，不该错挂到旧 `Rank 62` 名下；
4. 若硬写 `Rank 62b`，只会模糊原 `park` 的审计边界，并把“局部少亏”误包装成值得入板的新对象。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但已明显偏硬；原 shared fail-fast overlay 只在 ema continuation lane 留下很薄的 loser-control 残余，而最近新增的 microstructure / OFI 证据更像新的 1m/3m raw-alpha / execution family，不足以诚实派生 Rank 62b`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## Commit
- 本轮默认不做 commit。
- 原因：仓库存在大量共享脏文件，且 `docs/PARK_REFRAME_QUEUE.md` 可能有并发修改；本轮只做最小必要文档改动，避免混提。
