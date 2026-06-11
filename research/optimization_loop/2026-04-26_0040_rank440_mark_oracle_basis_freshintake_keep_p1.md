# Rank 440 / mark-vs-oracle 极端溢价回归 — fresh intake keep P1

- 时间：2026-04-26 00:40 UTC
- 执行槽位：Fresh intake slot
- 对象：`research/quant_digests/2026-04-25_2225_hl-mark-oracle-basis-reversion.md`
- 结论：`keep_P1`
- 正式 Rank：`440`

## 本轮执行的小点
对 `mark-vs-oracle 极端溢价回归` 做 fresh intake first verdict，只补 1 个最小 decisive blocker：它是否已能在公开可迁移口径下收束成一句 queue-facing raw alpha 主语，而不是停留在 Hyperliquid venue-specific basis 故事。

## 读取后的最小判断
结论是：**可以收束成一句明确主语，因此不应直接打回 background。**

可保留的 raw alpha 主语已经足够具体：

> 当 perp `mark_price` 相对 `oracle_price` 出现滚动极端偏离时，未来 `1m~5m` 更倾向向 oracle 方向回归。

这不是泛泛的 funding/basis 叙事，原因有三点：
1. alpha 锚点明确：不是“价格可能回去”，而是 `mark - oracle` 这条可计算错位本身；
2. 交易壳明确：repo 已给出固定阈值 + 滚动极端分位、回归出场、time-stop、widening-stop、按偏离幅度调仓；
3. 后续 cheapest follow-up 也明确：不是继续读故事，而是只需补 1 次 majors portability / cost realism 检查，回答该主语是否能从 Hyperliquid 单 venue 推广到更一般的 liquid perp 口径。

## 为什么这轮先给 P1 而不是直接升 P2
还不宜直接进 `P2`，因为当前证据仍主要来自单 repo / 单 venue / 偏粗粒度回测叙述；还缺 1 次最小 survivor 级别检查去确认：
- 该信号在 `BTC/ETH/SOL` 等 majors 上是否仍有可迁移性；
- 扣掉更诚实的 taker/slippage 假设后，edge 是否不是纯执行幻觉；
- 所谓“oracle 锚点回归”是否在更细 `1m/3m` 口径下依然存在，而不是 `1h` 讲故事造成的平滑假象。

## runtime 改写
- 分配新正式身份：`Rank 440`
- Fresh intake slot 更新为该对象，结论写为 `keep_P1`
- Surviving candidate slot 锁定为 `Rank 440`，并保留唯一一次 follow-up 预算

## 本轮会改变系统认知的一句话
`Rank 440 / mark-vs-oracle 极端溢价回归` 完成 fresh intake first verdict 并保留为 `P1`：主语已收束到“极端 mark-oracle premium -> 短时向 oracle 回归”，值得做 1 次最小 majors portability / execution realism follow-up，而不是停留在 Hyperliquid venue-specific basis 故事。
