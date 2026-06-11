# Published pairs shell：dynamic lookback × vol filter × trailing stop，到了 15m crypto 还能剩多少？
- 时间：2026-04-25 12:27 UTC
- 类型：论文 + GitHub + Binance USDⓈ-M public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：cointegrated / hedge-adjusted pair spread 的均值回归（spread z-score fade）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / pairs / stat-arb / relative-value / mean-reversion / zscore / dynamic-lookback / vol-filter / trailing-stop / 15m / 5m / repo / paper / public-data / cost / risk
- 证据类型：论文证据 + 工程实现 + public-data portability

## 1. 这次看了什么
看的是 Rafael Baptista Palazzi（2025, *Journal of Futures Markets*）的论文 *Trading Games: Beating Passive Strategies in the Bullish Crypto Market*，以及作者同步公开的 `trading-games-crypto` 仓库。它不是只给一个“pair spread 回归”概念，而是把 **dynamic lookback、volatility filter、minimum holding period、adaptive trailing stop** 都写进了可跑代码，属于少见的完整 pairs shell。

## 2. 核心结论
- 这篇东西的 **base alpha 很清楚**：两资产价差偏离均值后，做 spread fade，等它回归。
- 论文/仓库给出的作者口径结果很强：年化 Sharpe 约 `2.0`，年化收益约 `71%`，而且强调优于 buy-and-hold 与 momentum benchmark。
- 对 desk 更值钱的不是“pairs 又有效了”，而是：**lookback 不是固定常数，而是一个要先被优化/筛掉的 admission layer**；vol filter 和 trailing stop 是让 raw alpha 变成完整策略壳的关键组件。
- 但我用 Binance USDⓈ-M 最近 `1500` 根 `15m` 公共数据，对 `BTC/ETH/SOL/BNB/XRP/DOGE` 做最小诚实快检后，发现这条壳 **直接搬到短周期 perp 并不自然成立**：`z=1.0` 时 pooled `hold 1/3/6` 平均 net 分别约 `-15.13 / -13.97 / -13.10 bps/笔`（按两腿 round-trip `16 bps` 成本）。
- 唯一接近能留样的 pocket 是 `SOL-DOGE`：当 `|z|>=2.0` 且 `hold 6` 根 `15m` 时，平均 gross 约 `+18.70 bps/笔`、net 约 `+2.70 bps/笔`，但只有 `22` 笔，样本明显太薄。

## 3. 为什么和当前项目有关
这篇更像 **raw alpha + 完整策略壳**，不是单纯 pair 教材。它补的是当前素材池里相对缺的一层：
- raw alpha：spread mean reversion
- entry admission：dynamic lookback / z-threshold
- filter：volatility filter
- exit：mean reversion + trailing stop + minimum hold
- cost discipline：代码里显式带交易成本参数

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / stat-arb / 均值回归
- 基础 alpha：pair spread 偏离后的回归
- regime：更适合相关性高、spread 波动稳定、成本没把 edge 吃光的区间
- filter / veto：rolling volatility filter；极端噪声期抬高 admission 标准
- risk / sizing / execution overlay：dynamic lookback、minimum holding period、adaptive trailing stop、显式 transaction cost

## 4. 可复刻的最小实验
- 研究假设：published pairs shell 在 crypto `15m` 不是“到处都能跑”，但 **高 z 极端 + 较长一点持有 + mid/alt pair** 可能还留有 pocket。
- 可计算定义：对 liquid universe 先做 rolling hedge ratio；当 `|z|>=2.0` 才入场，做 spread fade；先测 `hold 3/6/9` 根，再加 `vol filter` 与 `min-hold`。
- 最小回测切口：Binance USDⓈ-M，先测 `SOL/BNB/DOGE/XRP` 两两组合，周期 `15m`，样本先放到近 `120d`。
- 最先看两个指标：`cost-after avg bps/trade`、`trade count`；第三个才看 `positive pair ratio`。

## 5. 风险与保留意见
- 当前 portability probe 还没把 repo 的完整 trailing stop / dynamic lookback 全量搬进来，只能算 first verdict。
- 论文结果可能更依赖作者的数据切口、pair 选择与较低频执行环境；直接压到 perp `15m` 后，成本与噪声会先吃掉大部分 edge。
- 如果最后只剩少数 `|z|>=2` 的 pocket，说明它更像 **稀疏 admission shell**，而不是“全 universe 常开型 pairs 主引擎”。

## 6. 一句话核心结论
这篇最值钱的地方不是“pair trade 重新伟大”，而是提醒我们：**spread fade 要先过 lookback / vol / hold / stop 这几道 admission，裸 pair mean reversion 到短周期 perp 往往先死在成本上。**

## 7. 一句话说明它怎么证明
作者主要靠 **论文回测 + 开源代码实现** 把完整策略壳讲清；我这边再用 **Binance 15m 公共数据诚实快检** 验证它在 short-cycle crypto 上是否还能站住。

## 8. 来源
- Palazzi, Rafael Baptista. (2025). *Trading Games: Beating Passive Strategies in the Bullish Crypto Market*. Journal of Futures Markets. DOI: `10.1002/fut.70018`
- Readable URL: `https://doi.org/10.1002/fut.70018`
- Repo URL: `https://github.com/rafaelpalazzi/trading-games-crypto`
- Dataset URL: `https://doi.org/10.17632/2kky7c6xkn.1`
