# Rank 191 / lowest-price-anchor cross-sectional reversal — fresh intake keep_P1

- 时间：2026-03-27 01:46 UTC
- 对象：`research/quant_digests/2026-03-27_0018_lowest-price-anchor-xs-reversal.md`
- 结论：`keep_P1`
- 新分配正式身份：`Rank 191`

## 这轮只回答一个问题
`lowest-price-anchor` 横截面反转，是否已经值得作为一个**单一可执行对象**保留进前排；还是它本质上只是把既有 loser-basket reversal 换个说法，应该直接 `park`。

## 结论
答案：**值得保留，但只能保留为一个很窄的对象。**

这轮不保留“最低价锚点家族”“behavioral anchoring 大主题”，只保留下面这条最小对象：

**`Rank 191 / loser-bucket low-anchor relative-value reversal`**

它的诚实定义是：
- 在可交易 universe 里先按 `24h/72h/7d formation return` 取 loser bucket；
- 仅在 loser bucket 内，再按 `low_gap = close / rolling_low - 1` 做二次排序；
- 先测最纯的增量检验：`long lowest low_gap losers / short highest low_gap losers`；
- 主时钟优先 `15m`，把 `5m` 当扩展而不是首轮主战场。

## 为什么这轮给 keep_P1
1. **对象边界清楚，不是空泛概念。**
   它不是“anchoring 也许有用”，而是一个可以直接写成 clean-room 实验的双排序横截面反转对象：`formation loser × distance-to-low`。
2. **相对现有 loser-basket 池，确实新增了一根独立排序轴。**
   这篇 digest 的关键不是再证明 plain reversal，而是主张：在 loser 内部，是否仍贴着 formation low，能把“真超跌”与“已反抽的 stale loser”分开。这个增量信息本身就值得一刀 cheap follow-up。
3. **MVP 执行口径已经足够具体。**
   universe、formation windows、bar clock、long/short 构造、成本口径都能直接落成一个最小 replication；不是那种还要先补半页 spec 才能开测的抽象题。
4. **但它还没到 P2。**
   当前证据主要来自论文摘要页/section snippet，且原文主样本更偏跨日 formation horizon；短周期 `15m/5m` transfer 目前仍是待检假设，不该在 intake 轮就直接抬成 `P2`。

## 为什么不是 park
- 不是简单复读现有 `24h loser basket reversal`：这轮新东西就是 loser 内部的 `low_gap` 二次排序，而不是“再做一次 loser vs winner”。
- 也不是必须依赖不可得数据：最低价锚点只需要 rolling OHLCV low，公开可复现。
- 更重要的是，它天然带着一个**唯一且便宜的 decisive follow-up**：
  > 在 loser bucket 内，`low_gap` 是否真的带来独立于 plain loser return 的增量区分？

这正适合 survivor 的唯一一次预算。

## 为什么还不能 promote_P2
- 还没有最小 replication 证明 `low_gap` 在短周期可交易 universe 下能 survive 成本；
- 原文优势主要是相对传统 reversal 的学术证据，不等于我们 desk 口径下 `15m` 就已经能交易；
- 当前最关键 blocker 已经压缩到一个非常具体的问题，按 policy 应先进入 survivor，而不是越级。

## 唯一 survivor follow-up 应该测什么
只测一刀：

**在 Binance 风格主流可交易 universe、`15m` 主时钟下，`loser bucket` 内的 `low_gap` 二次排序，是否在显式成本后仍保有独立于 plain loser return 的残余 alpha。**

如果答案是：
- **有**：可直接考虑 `promote_P2`；
- **没有**：就应诚实 `park_to_background`，不要把它放大成泛化 anchoring 研究。

## 本轮会改变系统认知的话
**`Rank 191 / loser-bucket low-anchor relative-value reversal` fresh intake 首判成立：它相对现有 plain loser reversal 新增的是 `distance-to-formation-low` 这根可公开复现、可直接 clean-room 检验的二次排序轴，因此值得进入 survivor 做唯一一次“anchor 是否真有独立增量信息”的 cheap decisive follow-up。**
