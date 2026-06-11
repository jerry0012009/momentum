# 别把横截面动量只写成花式 filter：这个 2026 Hyperliquid 新 repo 更值钱的是可直接复现的 RS 全策略骨架
- 时间：2026-03-28 05:12 UTC
- 类型：GitHub
- 主题类型：raw alpha
- 基础 alpha：横截面动量（relative-strength long-short）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：cross-sectional/momentum/relative-strength/long-short/risk-parity/rebalance/cost/crypto/5m/15m/repo
- 证据类型：工程经验

## 1. 这次看了什么
看了 Andrea Ambrosio 2026 年开源仓库 `hype-backtesting` 里的 `RelativeStrength` 策略实现。它不是在争论“动量有没有”，而是直接把 **排名、换仓、仓位、成本** 都写成可跑的骨架：`72 bar` 排名、`24 bar` 换仓、做多最强 `top 2`、做空最弱 `bottom 2`、`48 bar` 波动率估计、目标年化波动 `15%`、单腿仓位上限 `12%`，回测成本显式写成 `2 bps commission + 1 bp slippage`。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最值钱的不是证明“横截面动量天然赚钱”，而是给我们补上了一个可直接复现、可直接接 veto/filter 的 **XS raw-alpha 基线策略壳**。
- **一句话证明方式：** 结论来自可读代码 + 带成本的 Hyperliquid 小样本回测，而不是只靠 README 口号。
- repo 自带结果并不好：在 README 给出的 `90 days`、`7` 个 HL 币种、`hourly` 数据上，`Cross-Asset Relative Strength` 回测是 **-9.52% return / -7.49 Sharpe / 15.94% max DD / 116 trades**。这反而有价值：它告诉我们“XS 动量方向没错，但原始参数、宇宙、short leg 和换仓节奏大概率错了”。
- 代码把 base alpha 定义得很干净：**按过去 N 根收益排序，long winners / short losers**。这比最近很多“先上 3 层过滤再说 alpha”的材料更适合当主基线。
- 它天然适合承接我们最近两篇 digest 的改良件：`large-cap / short-leg veto`、`inverse-vol / low-sentiment basket` 都能直接插到这个骨架上，而不是重新发明一套回测框架。
- 对短周期 desk 来说，真正该测的不是“是否存在 XS 动量”，而是：**短腿是不是在 5m/15m 上吞掉了 edge，rebal 频率是不是过慢或过快，risk-parity 是否只是把 turnover 和噪声一起放大。**

## 3. 为什么和当前项目有关
这和当前 `momentum` 主线直接相关，因为我们最近已经连续积累了几篇 **XS momentum 的 branch idea**，但还缺一个足够朴素、足够诚实的 **full-stack baseline**。没有这个 baseline，后面所有 `veto / regime / sentiment / breadth` 的增量都容易变成“往空气里加过滤层”。这篇东西的价值，正好是把 **entry/exit/rebalance/sizing/cost** 一次性钉住，然后让我们把最近学到的 veto/filter 接上去做增量检验。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值
- 基础 alpha：过去 N 根收益排序后的 winner-minus-loser
- regime：更适合高离散度、趋势扩散而非同步拉扯的市场
- filter / veto：当前 repo 基本空白；可优先嫁接 `short-leg jump veto`、`liquidity floor`、`low-sentiment basket`、`dispersion gate`
- risk / sizing / execution overlay：inverse-vol / risk-parity sizing、固定间隔 rebalance、显式 fee+slippage、单腿仓位上限

## 4. 可复刻的最小实验
- 研究假设：在 `5m / 15m` crypto perp 上，**XS 动量的主要问题不一定是 long leg 不工作，而是 short leg 失真 + rebalance cadence 不合适**。
- 可计算定义：每次 rebalance 时，用过去 `24/48/96` 根收益做排名，long top `2`、short bottom `2`；仓位先做 `inverse-vol cap`，再比较是否加入 `short-leg veto`。
- 最小回测切口：`Binance 或 Hyperliquid` 的 `8~12` 个高流动 perp，先跑 `45~90d`；周期先做 `15m`，再下钻 `5m`；rebalance 先扫 `4/8/16` bars。
- 最先看 2 个指标：`after-cost spread pnl` 与 `leg attribution（long leg vs short leg）`。如果净值主要死在 short leg，就不要继续把问题表述成“XS 动量无效”。

## 5. 风险与保留意见
- 这份 repo 的公开结果本身是负收益，不能把它当现成可实盘策略。
- `7` 个币的 universe 偏小，且 `90d hourly` 样本太短，容易把单段风格误读成结构性结论。
- 代码只做了最朴素的 return ranking，尚未处理融资费、冲击成本分层、成交额门槛、跳空/尖刺短腿保护。
- `Cross-Asset` 这个命名略夸张，实际实现更像 **crypto cross-sectional momentum baseline**，不是成熟的广义多资产相对价值系统。

## 6. 来源
- Andrea Ambrosio. (2026). `hype-backtesting`. GitHub repository.
- Repo URL: `https://github.com/andreaambrosio/hype-backtesting`
- README (readable): `https://github.com/andreaambrosio/hype-backtesting/blob/main/README.md`
- Strategy code: `https://github.com/andreaambrosio/hype-backtesting/blob/main/src/strategies/relative_strength.py`
