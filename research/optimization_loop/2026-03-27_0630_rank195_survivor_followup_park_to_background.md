# Rank 195 / same-community lagged-return mean score — survivor follow-up park_to_background
- Time: 2026-03-27 06:30 UTC
- Cycle step: `cycle_plan` item 1
- Source digest: `research/quant_digests/2026-03-26_2218_same-community-lagged-return-network-alpha.md`
- Prior state: `Surviving candidate slot`
- Verdict: `park_to_background`

## 这轮只回答的那一个问题
只检查这件事：

> 在 liquid perp universe 上，用 **slow-updating community 标签** 定义
> `score_i(t)=mean(r_j(t-1), j∈same-community, j≠i)`，
> 这个 `same-community peers lagged-return mean score` 是否比更朴素的 **全市场 peers 均值 score** / **无 community 的 common-shock beta score** 更能解释下一根的横截面相对收益。

没有把对象扩写回整套动态 network science，也没有补第二个 follow-up 维度。

## 最小 clean-room 快检口径
- 数据：Binance Futures 公共 `15m` klines
- 样本：最近 `45d`
- 币种：`BTC, ETH, SOL, XRP, DOGE, BNB, ADA, LINK` 这 8 个较 liquid 的 USDT perp
- community 更新频率：`7d` 一次
- community 估计：用过去 `14d` 的 `15m` 收益相关矩阵做简化 spectral embedding，再用 `k=3` 的 k-means 分桶
- 对照组：
  1. `community score`：同 community 其他币上一根收益均值
  2. `market score`：全市场其他币上一根收益均值
  3. `beta score`：无 community、只保留对上一根全市场 shock 的滚动 beta 暴露
- 目标变量：下一根 `15m` 的**横截面相对收益**（`future_rel = r_i(t+1) - mean_j r_j(t+1)`）
- 评价：
  - 每根 bar 的横截面 Spearman IC
  - top quartile - bottom quartile 的下一根相对收益 spread

## 快检结果
样本共得到 `2,974` 个横截面时点；community proxy 在这套最小口径下**没有表现出比 no-community 基线更强的解释力**。

### 1) 横截面 IC
- `community score`: mean IC `+0.00095`, `t = 0.12`
- `market score`: mean IC `+0.00992`, `t = 1.24`
- `beta score`: mean IC `+0.00404`, `t = 0.46`

### 2) top-minus-bottom 下一根相对收益 spread
- `community score`: `-0.11 bps`, `t = -0.32`
- `market score`: `+0.17 bps`, `t = +0.47`
- `beta score`: `+0.48 bps`, `t = +1.35`

## 为什么这一步直接收口成 park
这轮 survivor follow-up 的目标不是证明论文错，而是判断这个**被压缩后的最小对象**值不值得进 `P2`。当前答案是否定的：

1. **community 分桶没有带来增益。** 在这套 slow-updating proxy 下，`community score` 的 IC 基本为零，spread 还略负，连最朴素的 no-community 对照都没赢。
2. **它没有留下“只差一个明确 blocker”的状态。** 如果现在继续做，不会是廉价 admission，而会滑回“再换 community 构造、再换 universe、再换 rebalance 频率”的开放式研究，这不符合 survivor 只能做一次收口检查的 policy。
3. **因此不能诚实地升到 P2。** 这条线目前更像“论文里的可能中频/日频结构”，而不是已经在 short-cycle liquid perp clean-room 下留下足够硬增益的前排 raw alpha。

## 本轮改变的系统认知
- `Rank 195` 的唯一 survivor follow-up 已经用完。
- 现有最小 proxy 证据显示：**same-community peers lagged-return mean score 在 liquid perp / 15m / slow-updating community 口径下，没有比无 community 基线更能解释下一根横截面相对收益。**
- 因而 `Rank 195` 本轮应从 `Surviving candidate slot` 收口并 `park_to_background`，不进入 `P2`。
