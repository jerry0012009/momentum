# Rank 195 / same-community lagged-return mean score — fresh intake keep_P1
- Time: 2026-03-27 05:29 UTC
- Cycle step: `cycle_plan` item 2
- Source digest: `research/quant_digests/2026-03-26_2218_same-community-lagged-return-network-alpha.md`
- Verdict: `keep_P1`
- Assigned rank: `195`

## 为什么这轮能留在前排
这条 intake 值得保留，但只能按一个很窄的对象保留：

> **在 slow-updating same-community 分桶内，某币同社区其他币上一根收益均值越强，该币下一根越偏向横截面相对强势。**

我没有把它放大成“动态网络科学策略”或“复刻 adaptive Lasso + 技术相似性 + 谱聚类全家桶”，因为当前首判真正可交易、也最适合 clean-room 检验的，只有 `same-community lagged-return mean score` 这一根骨架。

## 为什么不是直接 park
1. **它和现有前排对象不重复。** 现有 `Rank 194` 更像 `BTC 1m common shock -> low-liquidity underreaction laggard delayed catch-up`；这条则是 **community 内横截面排名**，不是单 leader 或单 shock pocket 的改写。
2. **它能压成一句明确的 score 定义。** 这满足 fresh intake 的保留标准，不需要先吞下整套重工程社区识别。
3. **论文证据给的不是解释层，而是横截面 raw alpha 线索。** 所以最诚实的处理不是 park，而是保留为一个单轴 `P1` 对象，等待唯一一次便宜 follow-up。

## 本轮收口后的最小 surviving object
后续 survivor follow-up 只许回答这一个问题：

`score_i(t) = mean(r_j(t-1), j ∈ same-community, j ≠ i)`

在 liquid perp universe 上，如果 community 标签慢频更新（例如周更/月内冻结），这个 `same-community peers lagged-return mean score` 是否比：
- 全市场 peers 均值 score；以及
- 无 community 的 common-shock / leader-lag ranking

更能解释下一根的横截面相对收益。

## 本轮改变了什么系统认知
- 这条线现在有正式 durable identity：`Rank 195`。
- 它被明确收缩为 **single-score cross-sectional raw alpha**，而不是开放式 network research。
- 它进入 `Surviving candidate slot`，并只剩 **1 次** 合法 follow-up 预算。
