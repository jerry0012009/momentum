# 别把这份 2025 cross-sectional horizon-map repo 只读成“4H 到 24H 的风格切换作业”：对 short-cycle crypto desk，更该先测的是「短窗 loser→winner fade」这条 raw alpha

- 时间：2026-04-19 16:36 UTC
- 类型：2025 GitHub repo source audit（`README.md`）+ Binance USDⓈ-M `15m/5m` portability probe
- 主题类型：raw alpha
- 基础 alpha：**横截面上，最近短窗跌得最狠的币，下一根/下一小段更容易相对反弹；最近短窗涨得最猛的币，更容易相对回吐。也就是短窗 `loser long / winner short` 的 cross-sectional reversal。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否（repo 更像 alpha map；entry/exit 已清楚，但 sizing/risk/cost 还要我们自己补）
- 主题标签：raw-alpha / cross-sectional / mean-reversion / loser-winner / horizon-map / 15m / 5m / repo / binance / cost
- 证据类型：工程经验 + 本地 public-data portability probe

## 1. 这次看了什么

看的是 **Kunal（GitHub: `kunal14901`，2025）** 的仓库 **`crypto-reversal-momentum-analysis`**。它做的不是复杂模型，而是一个很朴素、但对 desk 很有用的问题：**crypto 横截面到底是短窗反转、还是长一点开始动量？**

repo 用 Binance `4h` 数据（`2020–2022`）做 rank-demeaned-normalized 组合：按过去 `4h~24h` 收益给币排序，再构造多空组合，观察下一根 `4h` 的表现。作者原始读法是：**短窗更像 reversal，拉长一点可能转向 momentum。**

## 2. 核心结论

- **一句话核心结论：** 对我们 short-cycle desk，最值钱的不是“等它切到动量”，而是先把 **短窗横截面 loser→winner fade** 当成 raw alpha 母体。
- **一句话证明方式：** 我把 repo 的 horizon-map 框架直接压到 Binance USDⓈ-M liquid majors（`BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK/AVAX/LTC`），用 rank-demeaned-normalized 横截面权重，比较 `5m/15m` 上 recent-winner momentum 与 recent-loser reversal 的下一根收益。
- repo 原文主张：`4h~8h` 更像 reversal，`20h~24h` 开始出现 momentum 迹象；也就是说它提供的是 **“风格转折地图”**，不是单一固定因子。
- 但本地 `15m` portability probe 里，**reversal 明显比 momentum 更稳**：过去 `30m` 横截面信号、持有下一根 `15m`，组合平均约 **`+0.143 bps/bar gross`**，年化 Sharpe 约 **`4.39`**；`60m~90m` lookback 也仍是 reversal 占优。
- `5m` 上这个现象更极端：过去 `15m~20m` 的 loser→winner fade，下一根 `5m` 约 **`+0.111~0.119 bps/bar gross`**，年化 Sharpe 约 **`10.54~11.01`**；反过来追 recent winners 基本是负的。
- 唯一像“超短动量”的 pocket 只出现在 **`5m` 的过去 `5m` lookback**：recent-winner momentum 约 **`+0.022 bps/bar`**、Sharpe 约 **`2.07`**，但一拉到 `10m+` 就迅速翻负，说明它更像瞬时延续，不像稳定母信号。
- 所以 repo 对我们最重要的启发不是“crypto 会从反转切到动量”这句大话，而是：**先用 horizon-map 找 reversal/momentum 的分界点，再把最稳那一段单独拿出来做策略。** 当前 `5m/15m` 上最稳的还是 reversal。

## 3. 为什么和当前项目有关

这条线直接补的是 **横截面 raw alpha 素材池**，而且和最近几篇 desk intake 是连得上的：
- 它不是单币 trend，也不是 pairs spread；
- 它更像一个很通用的 **relative-value / cross-sectional router**；
- 可以和 volume、funding、OI、risk-on/off 这些二层模块自然拼接。

翻成人话就是：**不用先争论“市场到底顺势还是逆势”，先问“在这个具体 horizon 上，最近涨最多的币是更容易续涨，还是更容易回吐？”** 这个 repo 的价值就在于给了一个很便宜的测法。

## 3.5 策略拆解（必填）

- 方向属性：横截面 / 相对价值 / 均值回归
- 基础 alpha：recent losers rebound, recent winners mean-revert
- regime：更适合短窗离散度已经拉开、但还没进入持续单边扩散的时段
- filter / veto：先保留 `5m` 的 `15m~20m` lookback、`15m` 的 `30m~90m` lookback；可叠加成交量分位、单边趋势过强 veto
- risk / sizing / execution overlay：先做 rank-demeaned-normalized 或 top1/bottom1 等权；严格单 bar / 单事件 time-stop；把双边 taker 成本当第一道 admission check

## 4. 可复刻的最小实验

- **研究假设：** Binance liquid majors 在 `5m/15m` 上，短窗横截面 recent losers 的下一根相对收益高于 recent winners。
- **可计算定义：** 每根 bar 计算过去 `L` 根收益（`L=2~6`）；按横截面排序后构造 `rank-demeaned-normalized` 权重；做 **reversal**（long losers / short winners）与 **momentum**（long winners / short losers）A/B。
- **最小回测切口：** Binance USDⓈ-M，`10` 个 liquid majors；`15m` 先看近 `60d`，`5m` 先看近 `20d`；持有固定为下一根 bar。
- **先看两件事：**
  1. 加上双边 taker 费后是否还活；
  2. 把 rank basket 收缩成 **top1 loser vs top1 winner** 后，edge 是变厚还是直接消失。

## 5. 风险与保留意见

- 这个 repo 本身更像研究卡片，不是 production 策略；没有认真处理滑点、容量、资金费率与并发仓位。
- 本地 probe 只用了 liquid majors 与近样本，属于 portability check，不是正式 OOS 结论。
- rank-demeaned 组合在真实交易里会面临腿数、换手和成交成本问题；纸面 alpha 不等于可实盘 alpha。
- 当前结果说明 **短窗 reversal 很强**，但也可能只是近期 majors 的高噪声回摆特征，仍要做 rolling / cross-month / bull-bear split。
- `5m` 的 `5m` 动量 pocket 很窄，容易被手续费和撮合噪声吃掉，不应误读成“超短动量已成立”。

## 6. 来源

- Kunal (`kunal14901`). (2025). *Cryptocurrency Reversal/Momentum Analysis*. GitHub repository.
- Repo URL: https://github.com/kunal14901/crypto-reversal-momentum-analysis
- README URL: https://raw.githubusercontent.com/kunal14901/crypto-reversal-momentum-analysis/main/README.md
- 本地实验产物：
  - `reports/artifacts/quant_digests/2026-04-19_reversal_momentum_horizon_portability.csv`
