# 2026-04-02 16:38 UTC · Rank 15 park reframe

## Selected rank
- `Rank 15`
- selection note: 本轮按 `1~24` 段继续轮转；`Rank 15` 距上次 park-reframe 已超过 7 天（上次为 `2026-03-22 18:39 UTC`），且近期未见属于它自己的新独立证据轴。

## Original park reason
来源：
- `research/optimization_loop/2026-03-17_0103_rank15-sr-regime-switch-intake.md`
- `research/optimization_loop/2026-03-17_0126_rank15-clean-replication-park.md`

原始假设是把 support/resistance 的 `touch_or_cross -> provisional_break -> confirmed_switch` 写成一条独立 confirmation entry 线；最不差变体是 `retest_hold_reclaim`，但在 `6bps/side` 下仍约：
- `mean_total_return ≈ -1.94%`
- `positive_asset_ratio = 1/3`
- `mean_no_trade_ratio ≈ 81.73%`

同时 Light Stability Pack 四项一起硬 fail：
- 时间稳定性：`1/3` positive buckets
- 参数稳定性：`0/5` positive neighbors
- 跨标的稳定性：`1/3` positive assets
- 成本稳定性：`0/4` positive cost buckets

因此原 rank 被 park，不是因为“确认还不够多”，而是因为**确认层本身没有把独立 S/R regime-switch entry 救成可晋升策略**。

## Hard park or soft park?
- 本轮判断：`更像 hard park`
- 原因：它虽然表面上仍有“retest_hold 比 raw touch/cross 少亏”的残余，但改善主要停留在“少亏/少做”，没有留下可独立 queue-facing 的 admission package；一旦追求更诚实的样本密度，结果仍是负且稳定性全线不足。

## Any salvage signal?
有，但很弱，而且已经基本被别的提案吸收：
1. `retest_hold_reclaim` 的方向说明 **S/R 线位不是完全没信息**；
2. 最近相关 digest 也都把同主题往“shared quality / veto / context”收缩，而不是重新扶正成独立 alpha：
   - `2026-03-19_1844_rsrs-right-skew-shared-gate.md`
   - `2026-03-19_1912_volume-weighted-sr-persistence-gate.md`
   - `2026-03-20_0640_freshness-weighted-retest-memory-gate.md`

但这些“可救信号”都更像：
- shared S/R strength / persistence / freshness layer，或
- 给已有 breakout / Fib / EMA-PSAR 主线做 veto / sizing / context

而不是继续给 `Rank 15` 单独派生一条新的 regime-switch confirmation 策略。

## Single best cut
如果硬要保留唯一一刀，最自然的也只是：
- **把 Rank 15 从 standalone S/R regime-switch confirmation，降级成 shared S/R quality / retest-freshness context layer**。

但这刀现在**不值得再单独起一个 `Rank 15b`**，因为：
- `Rank 12b` 已经更干净地占了 `volume-weighted S/R persistence` 这条轴；
- `RSRS right-skew`、`freshness-weighted retest memory` 也更像共享 gate / overlay 家族，而不是 Rank 15 自己的独立再生版本；
- 再派生只会变成“把同一批 S/R overlay 残余重复命名一次”。

## Derived hypothesis?
- 结论：`keep_park`
- 不形成新的 `derived hypothesis`

原因：
- 原 park 的审计意义仍完整成立；
- 最近新增证据没有长出只属于 Rank 15 的唯一主修改轴；
- 唯一还诚实的残余价值，已经被相邻 `S/R / zone / persistence / veto` 提案家族吸收，不值得重复 draft `Rank 15b`。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `更像 hard park；残余信息只够继续服务 shared S/R quality / veto family，且这条唯一诚实修改轴已基本被既有 Rank 12b 与相邻 S/R overlay 证据吸收，不值得再派生 Rank 15b`.
