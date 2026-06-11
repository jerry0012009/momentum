# Asymmetry, Tail Risk and TSMOM：动量不是对称硬币，最伤人的往往是反向急冲与横盘磨损
- 时间：2026-03-11 09:27 UTC
- 类型：论文
- 主题标签：trend / momentum / pullback / tail-risk / alpha
- 证据类型：论文证据 + 工程迁移假设

## 1. 这次看了什么
这次看的是 **Liu, Lu, Wang (2021), _Asymmetry, tail risk and time series momentum_**。它不是再证明一次“动量存在”，而是更具体地追问：**为什么 TSMOM 明明长期有效，却总会在某些阶段被打得很疼？** 作者用中国商品期货数据研究发现，动量亏损并不是随机出现，而是高度集中在几类特定情形：**上涨趋势里的下挫、下跌趋势里的反弹、以及长时间横盘。**

## 2. 核心结论
- 论文证据：TSMOM 的主要痛点不是“平时小亏很多”，而是**在趋势反向急冲与横盘阶段出现深且持久的回撤**；论文明确点名三类场景：`slumps in uptrend`、`rebounds in downtrend`、`sideways markets`。
- 论文证据：作者把最近收益拆成 **上行 partial moment** 和 **下行 partial moment**，发现这些“尾部分布的不对称性”能**部分预测后续的动量反转**，也就是说：同样是正的过去收益，内部的尾部结构不同，未来延续概率也不同。
- 论文证据：基于这类信息构造的 **managed TSMOM**，在中国商品期货样本外阶段带来 **Sharpe ratio 的显著提升**，而且对不同 lookback 窗口都较稳健。
- 对当前项目最重要的启发是：**别把 long momentum 和 short momentum 当成完全镜像，也别把“正动量”当作单一状态。** 动量里还藏着“顺趋势延续”和“快要被反抽打脸”这两种完全不同的局面。

## 3. 为什么和当前项目有关
这篇和 `momentum` 当前主线很贴，因为你现在并不缺“还能不能再造一个新动量定义”，更缺的是：**为什么裸趋势 / 裸 breakout 一上实盘就容易被 pullback 和假延续打穿。** 它对 15m 的意义主要有三点：
- 它把 **pullback** 从“主观看图”变成一个可以规则化的对象：不是所有回撤都一样，关键在于最近收益分布有没有出现对当前方向不利的尾部放大。
- 它支持把确认层做成 **非对称过滤器**：多头 continuation 时重点防“下行尾部突然变重”，空头 continuation 时重点防“上行尾部突然变重”。
- 它也解释了为什么很多短周期 breakout 会死在横盘：**问题不一定是方向定义错了，而是你把‘易反转状态’和‘可延续状态’混在一起交易。**

## 4. 可复刻的最小实验
- 研究假设：15m Crypto 上，裸 `sign(mom_N)` 很容易在反抽/回撤阶段被打脸；若先用最近收益的上/下 partial moments 做非对称过滤，能减少“看起来还顺势、其实已进入易反转状态”的入场。
- 一个可计算定义：
  - `mom_N = close / close.shift(N) - 1`
  - `up_pm = mean(max(ret_i, 0)^2)`，`down_pm = mean(max(-ret_i, 0)^2)`，在最近 `M` 根 15m bar 上计算
  - 多头只在 `mom_N > 0` 且 `down_pm / (up_pm + 1e-12) < th_long` 时开；空头只在 `mom_N < 0` 且 `up_pm / (down_pm + 1e-12) < th_short` 时开
- 最小回测切口：
  - 资产：BTC perpetual、ETH perpetual、SOL perpetual
  - 周期：15m
  - 样本：近 180d~365d
  - 对照：
    1. 裸 `sign(mom_N)`
    2. 非对称 partial-moment 过滤后的 `sign(mom_N)`
    3. 再叠加一个简单 EMA 方向层，看过滤器是否仍有边际价值
- 最该先看：
  1. `post_cost_return`
  2. `max_drawdown`

## 5. 风险与保留意见
- 论文样本是**中国商品期货日频**，不是 crypto 15m；它更像在教你“动量怎么死”，而不是直接给你一个可搬运的分钟级成品因子。
- partial moments 这种结构如果窗口太短，会对单次噪音很敏感；如果窗口太长，又可能滞后到错过真正的短周期延续。
- 这类过滤器最可能帮助的是**少亏在坏局面**，未必会让胜率暴涨；因此评估时别只看收益峰值，要特别看回撤收敛是否明显。
- 如果实验无效，也不一定说明思路错，可能只是 15m 上真正有信息的“非对称风险”不在收益尾部，而在成交量、funding、或会话切片里。

## 6. 来源
- Liu, Z., Lu, S., & Wang, S. (2021). *Asymmetry, tail risk and time series momentum*. International Review of Financial Analysis, 78, 101938.
- DOI: https://doi.org/10.1016/j.irfa.2021.101938
- Readable URL: https://www.sciencedirect.com/science/article/pii/S1057521921002581
- Abstract / metadata mirror: https://ideas.repec.org/a/eee/finana/v78y2021ics1057521921002581.html
