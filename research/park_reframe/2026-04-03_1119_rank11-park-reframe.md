# 2026-04-03 11:19 UTC · Rank 11 park reframe

## Selected rank
- `Rank 11`
- selection note: 本轮按 `Rank 1~37` 的 parked rank 低频轮转处理，优先避开最近 7 天内刚复盘过的条目。`Rank 11` 上次 bot6 复盘是 `2026-03-24 02:04 UTC`，已超过 7 天；同时最近又新增了更贴近“事件驱动 / pattern-triggered raw alpha”的旁证，值得再判断一次：这些新证据是在救旧 `Rank 11`，还是只是在把主题推向新的 raw-alpha family。

## Original park reason
原始 authoritative 证据：
- `research/optimization_loop/2026-03-16_2343_rank11-clean-replication-park.md`
- `research/park_reframe/2026-03-24_0204_rank11-park-reframe.md`

原 `Rank 11` 被 park 的原因没有变：它把 **Lo-style causal extrema pattern gate** 当成 `15m BTC/ETH/SOL` 上可复用的 pattern trigger，但最小 clean replication + Light Stability Pack 已经把这条线审计成 **主体 pocket 不成立**，不是“还差一个更聪明的 follow-up router”。

冻结版最关键结果（`6bps/side`）：
- `mean_total_return ≈ -4.33%`
- `positive_asset_ratio = 0/3`
- `mean_trades ≈ 58.3`
- Light Stability Pack 四项全 fail：
  - 时间稳定性：`1/3`
  - 参数稳定性：`0/5`
  - 跨标的稳定性：`0/3`
  - 成本/交易数稳定性：`0/4`

翻成人话：
- 原问题不是“模式识别大致对，只差诚实 exit / timeout”；
- 而是这条 `causal extrema` pattern trigger 自身就没有形成够厚、够稳、够可迁移的策略主体；
- 所以原 `park` 的审计意义必须保留：**失败对象是“Rank 11 这套 pattern gate 值得继续占用 queue-facing 预算”这件事，不是所有 reversal / event 主题都死了。**

## Hard park or soft park?
- 本轮判断：`hard park`

为什么仍是 hard park：
1. clean replication 已经不是“少亏但还可救”，而是收益、跨资产、时间、参数、成本五个面一起偏负；
2. 新证据没有把原 trigger 本体变厚，只是说明“pattern / event”这个大主题若要活，应该换成更窄、更像 raw alpha 的宿主；
3. 因而 `Rank 11` 更像一个已经完成审计的失败 pattern family 入口，不像还有诚实单轴可切的 soft park 母体。

## Any salvage signal?
有一点，但不属于 `Rank 11` 自身的可救信号，更像“主题外流”。

本轮最 relevant 的新增旁证：
- `research/quant_digests/2026-03-27_0448_cusum-triple-barrier-resnet-raw-alpha.md`
- `research/quant_digests/2026-04-02_0041_largebody-engulfing-reversal-alpha.md`

这两批新证据共同说明：
1. **事件驱动 / reversal pattern 主题并没死**；
2. 但真正更诚实的写法，是 `CUSUM event bars + triple barrier` 这种完整事件驱动 raw alpha，或 `large-body engulfing reversal × 1~2 bar timeout` 这种单一、短时、可程序化的 pattern-triggered reversal；
3. 它们都比原 `Rank 11` 的宽泛 `causal extrema pattern gate` 更具体，也更像完整策略骨架；
4. 所以新增价值是在把主题推向 **新的 raw-alpha family**，不是把旧 `Rank 11` 救成一个诚实的 `Rank 11b`。

换句话说：
- 可救信号存在，但救的是“pattern / event topic”，不是 `Rank 11` 这条旧 gate；
- 对原 rank 来说，这更像审计后的外部旁证：旧写法角色太宽、太抽象、太不像可交易主体。

## Single best cut
如果只保留唯一一刀，本轮最像样的改写方向是：

> **replace broad Lo-style causal-extrema pattern gate with a single event-defined reversal trigger + short timeout**

也就是：
- 不再让“因果极值模式”承担宽 pattern gate 角色；
- 改成只承认某一个更窄、更可程序化的事件定义（例如单一 reversal event / engulfing event）+ 明确的 `1~2 bar` timeout / barrier。

但这刀本轮**不够诚实地属于 `Rank 11`**，因为：
- 它实质上已经换了 trigger 语言与策略骨架；
- 更像一条新的 raw alpha，而不是在保留原失败对象边界下做单轴修补；
- 若硬写成 `Rank 11b`，会模糊“原 pattern gate 已 hard-fail”这件事。

## Derived hypothesis?
- 结论：`keep_park`
- 不新增 `derived hypothesis`

为什么这次仍不值得 draft `Rank 11b`：
1. 原 `park` verdict 没被推翻；
2. 最近新增的强旁证都在把主题推向新的 **event-driven / reversal raw-alpha family**，而不是支持原 `causal extrema gate` 的 residual pocket；
3. 若现在硬写 `Rank 11b`，本质会变成“借新 family 的名字替旧 rank 续命”，不够诚实；
4. bot2 若未来要认领，应直接认领新的窄 raw-alpha intake，而不是把它挂回 `Rank 11` 名下。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `hard park；最近新增的 CUSUM 事件条 / large-body engulfing 证据说明 event-driven reversal 主题更像新的 raw-alpha family，而不是旧 Rank 11 causal-extrema pattern gate 的诚实窄派生，不足以 draft Rank 11b`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## Commit
- 本轮默认不做 commit。
- 原因：仓库存在大量共享脏文件；本轮只做最小必要文档改动，避免混提。
