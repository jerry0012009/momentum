# Time-Series Momentum：最朴素、也最值得先理解的基础 alpha 候选
- 时间：2026-03-10 11:09 UTC
- 类型：论文
- 主题标签：trend / momentum / alpha / futures
- 证据类型：论文证据 + 工程经验

## 1. 这次看了什么
这次看的核心论文是 Moskowitz, Ooi, Pedersen 的 **Time Series Momentum**。它讨论的是一个非常朴素但极重要的问题：**一个资产自己的过去收益，能不能预测它自己的未来收益。** 这比“横向比较谁更强”更接近你当前要找的“基础 alpha 本体”。

## 2. 核心结论
- 论文证据：作者在 58 个 futures / forwards 合约上发现，**资产自身过去 12 个月的超额收益**，对其未来收益具有显著正向预测力；这种 time-series momentum / trend 效应在多类资产上都能看到。
- 论文证据：这种趋势延续大致会持续约一年，之后在更长周期上会出现部分反转；也就是说，趋势不是永久的，而是有“延续窗口”。
- 工程上的重要提醒：这个结论说明“看一个资产自己的历史路径”本身就可能构成 alpha，不必一开始就上多因子大杂烩。
- 但对你最关键的保留意见是：后续实践总结显示，**月频/周频动量往往更强，日频已明显变弱，超短频更容易出现反转与噪音主导**。所以不能把“12 个月趋势有效”直接翻译成“15m 纯动量也必然有效”。

## 3. 为什么和当前项目有关
这篇论文对你当前阶段很重要，因为你现在缺的不是“怎么优化一个已有策略”，而是**先确认最基础的 alpha 逻辑到底长什么样**。它和 `momentum` 项目的关系在于：
- 它是 `multi_tf_momentum` 这类对象背后的最基础学术母体
- 它支持“趋势/动量可以先从最简单定义开始”这条路线
- 它也提醒你：**短周期里不能只照搬长周期动量，需要加入结构、确认和过滤**

换句话说，这篇论文给你的不是成品 15m 策略，而是一个很重要的出发点：
**先承认‘资产自己的过去收益’可能有信息，再研究它在短周期里为什么会失真。**

## 4. 可复刻的最小实验
- 研究假设：单纯的“过去 N 根收益率方向”在 15m Crypto 上未必稳健，但把它作为方向底座，再叠加结构/确认层，可能比纯裸动量更可用。
- 一个可计算定义：
  - baseline A：`mom_N = close / close.shift(N) - 1`
  - 方向规则：`signal = sign(mom_N)`
  - 对照组：
    1. 裸 `sign(mom_N)`
    2. `sign(mom_N)` + 1h EMA 方向过滤
    3. `sign(mom_N)` + breakout / volume confirmation
- 最小回测切口：
  - 资产：BTC, ETH, SOL
  - 周期：15m
  - 样本：近 180d
  - 验证：先单样本，再 rolling
- 最该先看：
  1. `post_cost_return`
  2. `positive_window_ratio`

## 5. 风险与保留意见
- 这篇论文的经典证据主要来自中低频 futures 趋势，不是直接来自 15m Crypto。
- 越往短周期走，市场微观结构、噪音、反转、交易成本的破坏越大。
- 如果 15m 裸动量表现差，不代表“动量无效”，更可能代表：**你需要结构过滤、确认层、风险层，而不是直接否定趋势 alpha。**
- 因此最合理的学习顺序不是放弃动量，而是把它当作**基础 alpha 胚胎**，再逐层加结构。

## 6. 来源
- Moskowitz, T. J., Ooi, Y. H., & Pedersen, L. H. *Time Series Momentum* (AQR article page / paper summary): https://www.aqr.com/Insights/Research/Journal-Article/Time-Series-Momentum
- Quantpedia. *Time Series Momentum Effect*（含相关文献与实践摘要）: https://quantpedia.com/strategies/time-series-momentum-effect
