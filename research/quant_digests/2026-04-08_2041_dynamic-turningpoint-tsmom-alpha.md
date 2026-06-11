# 别把这篇 2021 NAJEF 论文只读成“又一个动量论文”：对 short-cycle desk，更该先测的是 `turning-point-confirmed trend leg × short-horizon continuation` 这条 raw alpha

- 时间：2026-04-08 20:41 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：**局部 turning point 确认后的同向短周期续行**，也就是“不是简单看过去 N 根涨跌，而是看价格在局部转折后有没有进入新的 momentum leg”
- 是否可独立复现：**是**
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：**否**（论文更像 alpha 母体，完整执行壳还要我们自己补）
- 主题标签：trend / momentum / turning-point / continuation / single-asset / 5m / 15m
- 证据类型：论文证据（ScienceDirect 摘要页 + 引言片段 + Crossref metadata）+ Binance USDⓈ-M public-data portability probe

## 1. 这次看了什么
看的是 **Oliver Borgards (2021), _Dynamic time series momentum of cryptocurrencies_, The North American Journal of Economics and Finance**。这篇东西有价值的地方，不是重复“涨了还会涨”，而是把动量读成一种**围绕局部转折点展开的动态过程**：formation period 之后，价格常常不是立刻结束，而会继续跑出 1 个或多个 momentum cycle。

## 2. 核心结论
- **一句话核心结论：** crypto 的 TSMOM 不一定是固定 lookback 收益率本身，而更像“局部转折被确认后，新 trend leg 继续跑一小段”。
- **一句话证明方式：** 作者不是只拿静态 N 日收益做分组，而是用动态价格模式/turning point 视角去看 formation period 之后是否跟着出现后续 momentum cycles。
- 这比 desk 常见的“过去 20 根涨就追”更贴近短周期实盘，因为它更像**事件触发的顺势续行**，不是全时段常开。
- 对 `1m/3m/5m/15m` 最有启发的，不是论文原参数，而是**entry 触发方式**：先等局部转折完成，再只交易刚启动的新方向。
- 我做了一个**诚实的薄近似 probe**：不用论文原始完整动态算法，只测 `smoothed local-slope sign flip + conviction threshold + 1-bar confirm` 这条最薄 turning-point momentum 壳。结果在 Binance USDⓈ-M 近 `120d`、`BTC/ETH/SOL/XRP/ADA/DOGE/LINK/AVAX` 上，`15m` 事件后的同向 forward return 约为：`1/3/6 bars = +6.81 / +8.53 / +8.68 bps`（按每个资产的事件均值再平均）；`5m` 约为 `+5.00 / +6.51 / +7.13 bps`。
- 这说明：**方向续行本身大概率有 transferable edge，但 5m 很吃成本，15m 更像先能活的第一站。**

## 3. 为什么和当前项目有关
这篇最适合放进当前 desk 的地方，是把它当成一个新的 **trend / momentum raw alpha intake**，而不是继续围绕固定窗口 breakout 或 EMA 交叉内循环。

它补的是一个很具体的空白：
- 不是 `lookback return` 动量
- 不是 `breakout above rolling high`
- 也不是纯 filter

而是：**局部转折确认 → 新 trend leg 续行**。这类 alpha 很适合拿来和 desk 现有的：
- breakout 触发层
- pullback recovery 确认层
- volatility / cost veto
做并列比较，而不是混成一个黑箱。

## 3.5 策略拆解（必填）
- 方向属性：**顺势 / 单资产 directional**
- 基础 alpha：**turning-point-confirmed continuation**
- regime：高流动性主流币、非极端反转噪音阶段更像能工作；当前 probe 里 `15m` 明显强于 `5m`
- filter / veto：`slope-z` 阈值、sign-flip 后再确认 1 根、只做 top-liquid majors、对超高 funding / 极端 news bar 做 veto
- risk / sizing / execution overlay：先做固定持有 `1/3/6` 根事件研究；实盘壳再补 `ATR time-stop / maker-first / post-cost hurdle`

## 4. 可复刻的最小实验
**研究假设：** 当平滑后的局部斜率刚完成 sign flip，且这个 flip 不是纯噪音时，后续 `1~6` 根存在同向续行。

**一个可计算定义：**
1. 对 `close` 取 log price；
2. 用短窗平滑（我这次先用 `EMA` 做薄近似，后续可换成 `Savitzky-Golay` 更贴近 turning-point 视角）；
3. 定义 `slope = smooth.diff()`；
4. 当 `sign(slope)` 刚翻转、`|slope_z| >= 0.8`，且下一根仍同号时记为事件；
5. 统计同方向 forward return（`1/3/6` bars）。

**最小回测切口：**
- 资产：`BTC/ETH/SOL/XRP/ADA/DOGE/LINK/AVAX`
- 市场：Binance USDⓈ-M perpetual
- 周期：先 `15m`，再降到 `5m`
- 样本：近 `120d`

**最该先看的 2 个指标：**
- `post-cost expectancy / event`
- `positive asset ratio`

## 5. 风险与保留意见
- 这次拿到的是 **ScienceDirect 摘要页 + 引言片段**，不是全文 PDF，所以对作者完整动态算法的理解还不算最终版。
- 我这次的 portability probe 是**薄近似**，不是 faithful replication；它只能回答“turning-point continuation 这类 edge 有没有 transfer 可能”，不能回答“论文原算法是否原样可搬到 15m”。
- 从 probe 看，`5m` 的原始毛 edge 不算差，但若按 taker-taker 估 `6~8 bps` round-trip，很多 1-bar 版本会变得很勉强；因此当前优先级应是：**先做 `15m`，再看能否靠 maker / veto / asset admission 往 `5m` 压。**
- 下一步若想更 faithful，需要把 turning point 检测改成更接近论文语义的局部 extremum / cycle 定义，而不是只用 EMA slope sign flip。

## 6. 来源
- Borgards, O. (2021). *Dynamic time series momentum of cryptocurrencies*. *The North American Journal of Economics and Finance*.
- DOI: `10.1016/j.najef.2021.101428`
- Readable URL: `https://doi.org/10.1016/j.najef.2021.101428`
- Article page: `https://www.sciencedirect.com/science/article/pii/S1062940821000590`
- Crossref metadata: `https://api.crossref.org/works/10.1016/j.najef.2021.101428`
- Repo URL: `未找到官方公开实现`

## 7. 下一步怎么测
1. **faithful 版**：把当前 `EMA slope flip` 替换成 `Savitzky-Golay / local-extrema` turning-point 检测，重跑 `15m` 事件研究。
2. **admission 版**：只保留 `top-liquidity + funding neutral + no major event bar` 的样本，看 `post-cost expectancy` 是否明显抬升。
3. **落地壳版**：把 `entry = sign-flip confirm`、`exit = opposite flip or max-hold`、`risk = ATR cap`、`cost = maker/taker ladder` 写成完整 A/B 策略，先在 `15m` 做 first verdict。