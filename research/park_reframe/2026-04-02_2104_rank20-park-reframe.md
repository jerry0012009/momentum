# 2026-04-02 21:04 UTC · Rank 20 park reframe

## Selected rank
- `Rank 20`
- selection note: 本轮按 `Rank 1~37` 范围执行；最近 7 天内已复盘过的低号条目包括 `Rank 15 / 18 / 23 / 24 / 33 / 36`，而 `Rank 20` 上次 bot6 复盘为 `2026-03-23 00:45 UTC`，已超过 7 天，且其主题最近又被新的 microstructure / trade-flow 证据间接重新定性，适合做一次低频复核。

## Original park reason
原始证据：`research/optimization_loop/2026-03-17_0326_rank20-price-volume-divergence-park.md`

原 Rank 20 被 park，不是因为“量价关系完全没信息”，而是因为它把 `price-volume divergence warning` 写成了 **standalone breakout filter**，结果 clean replication 直接失败：
- baseline `baseline_mtf_momentum @ 6bps/side`：`mean_total_return ≈ -38.69%`，`positive_asset_ratio = 0/3`
- 主变体 `pvd_break24_delta0.5_warn3 @ 6bps/side`：`mean_total_return ≈ -39.22%`，`positive_asset_ratio = 0/3`
- 时间稳定性：`0/3` 正 bucket
- 参数稳定性：无转正 pocket
- 跨资产：`BTC/ETH/SOL` 全负
- 成本：`10/15/20bps` 继续明显恶化

所以原审计结论必须保留：
**失败对象是“把量价背离 warning 当成独立 breakout 过滤器”这件事，不是“价格×成交参与度主题永远无效”。**

## Hard park or soft park?
- 本轮判断：`soft park，但比 3 月下旬时更偏硬`

原因：
1. 原 rank 的 standalone filter 写法已经被审计打穿，这一层很硬；
2. 但“价格 thrust × 成交参与度 × 吸收/失衡”这类主题并没死，仍然能留下残余信息；
3. 只是最近新增证据把这类残余继续往 **1m/3m microstructure raw-alpha / execution context** 推，而不是支持再把它写回 `15m breakout shared admission layer`。

## Any salvage signal?
有，但已经变弱，而且更像“主题迁移”而不是“Rank 20 自身可救”。

仍能保留的可救信号只有两层：
1. **interaction 仍优于单看 volume 阈值**：这点和旧的 `Rank 20b` 方向一致，说明别把 volume 当孤立门槛；
2. 但最近新证据（见 `research/quant_digests/INDEX.md` 中 2026-04-01~04-02 条目）显示，更值得优先追的是：
   - `2026-04-01_1548_obi-microprice-highthreshold-alpha.md`
   - `2026-04-02_0550_orderbook-delta-vote-microstructure-alpha.md`
   - `2026-04-02_1007_pressure-ratio-capitulation-fade-alpha.md`
   - `2026-04-02_1140_extreme-ofi-tradeflow-continuation-alpha.md`

这些新证据共同说明：
- desk 现在更容易把“成交参与/流强/盘口失衡”写成 **更上游的短周期 raw alpha**；
- 相比之下，Rank 20 原本那种 `15m breakout + divergence warning` 写法，已经更像一层被新 family 超过的旧 admission 语义。

翻成人话：
- 可救信号不是没有；
- 但它更像在说“去更短周期、去更原生的 flow / order-book 层找 alpha”；
- 不像在说“继续给 Rank 20 再开一条 20c”。

## Single best cut
若只保留唯一一刀，**仍然只能是旧的那一刀，不是新的第二刀**：

> 把 standalone `price-volume divergence breakout filter` 降级成 `volume-price interaction` shared admission layer。

也就是既有 `Rank 20b` 的方向。

为什么这轮不改成别的：
- 最近新证据虽然更强，但强在 **另起 microstructure family**，不是强在给 Rank 20 提供了新的、仍属同一家族的窄修改轴；
- 如果这轮硬把“order-book imbalance / OFI / pressure-ratio”挂成 `Rank 20c`，本质是在借旧 rank 名字收编一条已经长成新主语的 raw-alpha 线，边界会变脏。

## Derived hypothesis?
- 结论：`keep_park`
- 不新增 `derived hypothesis`

原因：
1. 原 `park` 结论仍完整成立；
2. 当前唯一诚实的 residual cut 仍是既有 `Rank 20b`，没有出现新的唯一主修改轴；
3. 最近新证据的增量价值，主要是把主题继续上移到 `microstructure / trade-flow raw alpha` 家族，而不是支持再派生一个名义上属于 Rank 20 的 `20c`。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但更偏硬；唯一还诚实的修改轴仍只是既有 Rank 20b（volume-price interaction shared admission layer），而最近新增的 OBI / order-book delta / OFI / pressure-ratio 证据更像新的 microstructure raw-alpha family，不足以再诚实派生 Rank 20c`