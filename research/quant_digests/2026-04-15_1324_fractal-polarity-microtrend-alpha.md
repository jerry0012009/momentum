# 别把这篇 2025 Fractal Market Hypothesis 论文只读成“非线性金融物理”：对 short-cycle desk，更该先拆的是「fractal polarity flip × micro-trend follow」这条 raw alpha 候选

- 时间：2026-04-15 13:24 UTC
- 类型：2025 *Commodities* 论文摘要/元数据复核（DOAJ + Crossref + OpenAlex）
- 主题标签：raw-alpha/single-asset/trend/micro-trend/fractal-market-hypothesis/beta-to-volatility/lyapunov-to-volatility/symbolic-regression/btc/eth/5m/15m/paper/abstract-only/public-data
- 证据类型：论文摘要证据 / 待验证

- 主题类型：raw alpha
- 基础 alpha：**当市场的局部“分形状态”从一边翻到另一边时，顺着新出现的 micro-trend 做多/做空；具体信号是 `Beta-to-Volatility` 与 `Lyapunov-to-Volatility` 两个比率的极性翻转。**
- 是否可独立复现：否（当前只拿到摘要/元数据，未拿到正文参数细节）
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否

## 1. 这次看了什么

主来源是一篇 2025 年的 open-access 论文：Jonathan Blackledge、Anton Blackledge，*Optimisation of Cryptocurrency Trading Using the Fractal Market Hypothesis with Symbolic Regression*，发表于 *Commodities*。

- DOI：`10.3390/commodities4040022`
- Readable URL：`https://doi.org/10.3390/commodities4040022`
- Journal URL：`https://www.mdpi.com/2813-2432/4/4/22`
- DOAJ 摘要页：`https://doaj.org/article/35c21117f3794f6db8f7007d168cb068`

当前能稳定拿到的是 Crossref/DOAJ 摘要与元数据，**拿不到正文全文**。所以这轮不能把它写成“完整可复刻策略壳”，只能把它当成一个**值得 intake 的新 raw alpha 候选**。

## 2. 核心结论

一句话版：**这篇东西最值得 desk 拿走的，不是“分形市场假说”这层大词，而是一个可程序化的 raw alpha 方向——用分形状态比率的“极性翻转”去抓 BTC/ETH 的短期趋势切换。**

它是怎么证明这点的：摘要明确说，作者用 BTC/ETH 对美元汇率做分析，重点看两个比率——`Beta-to-Volatility` 与 `Lyapunov-to-Volatility`——其**极性变化**是否能预示价格趋势切换；随后基于这些信号给出 `long / short / hold` 建议，并声称优化后策略可跑赢 buy-and-hold，在稳定市场条件下短 horizon 的“micro-trend”收益可到 **约 10%**。

## 3. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha = fractal-polarity flip trend-follow：当局部分形/不稳定性状态的方向从负翻正或从正翻负时，顺着新方向去跟随 BTC/ETH 的短期 micro-trend。**

翻成人话：
- 它不是单纯的 Hurst 指标解释文；
- 也不是纯 ML 黑箱预测；
- 更不是 risk overlay。

它更像一条**单资产趋势切换 raw alpha**：
1. 先从价格路径里提取“分形状态”代理；
2. 观察两个状态比率的正负极性是否同步翻转；
3. 同步翻正时偏多、同步翻负时偏空、冲突时观望；
4. 赚的是趋势切换后的一小段 continuation / micro-trend，而不是长期 buy-and-hold beta。

## 4. 为什么这轮值得进池

原因主要有三点：

1. **它补的是一个目前 digest 里几乎没怎么系统 intake 过的 raw alpha 家族：fractal / roughness / instability state-driven trend。** 现在池子里 pairs、basis、funding、lead-lag 已经很多，这条线至少有明确增量。
2. **它服务的是当前主线 1 的“趋势跟随模块”，但不是又一个 EMA/Donchian 变体。** 对当前学习地图来说，这更像“趋势信号的上游状态定义器”。
3. **它天然适合先做 `5m/15m` 最小实验。** 因为输入只需要公开价格序列，不依赖私有链上数据，也不依赖难抓的订单簿全量历史。

## 5. 这篇材料现在的真实强弱

强的地方：
- 来源靠谱：正式期刊 + DOI；
- 主题直接是 crypto trading，而不是泛金融解释文；
- 摘要里已经给出很关键的信号骨架：`Beta-to-Volatility`、`Lyapunov-to-Volatility`、极性翻转、`long/short/hold`、BTC/ETH、micro-trend。

弱的地方：
- **现在只有摘要，没有正文**；
- 摘要没交代完整参数、窗口、具体开平仓规则；
- “up to ~10%” 这类收益说法目前只能当作者摘要陈述，不能当我们自己的已验证结论；
- `TuringBot` / symbolic regression 更像加速层，不是必须先信的 alpha 本体。

所以这轮最诚实的定位是：
> **raw alpha 候选，方向新鲜，值得进研究池；但证据强度低于 full-text paper / source-code repo shell。**

## 6. 对 short-cycle desk 的正确翻译

如果把它翻成我们能测的语言，最合理的版本是：

- 交易对象：`BTCUSDT`、`ETHUSDT` perpetual
- 基线周期：`15m`，再下探 `5m`
- 信号主干：
  - rolling 估计一个 roughness / fractal proxy；
  - rolling 估计一个 local instability / Lyapunov proxy；
  - 两者都用 realized volatility 做归一化；
  - 只在两个 ratio **同向翻转** 时开仓；
  - 出场用：反向翻转 / 固定 time stop / ATR stop 三选一做对照。

也就是说，它更像：
**状态翻转触发器 + micro-trend follow**，而不是传统 breakout 触发器。

## 7. 下一步怎么测

最小实验建议直接分三层：

1. **弱复刻层**：先不等正文，直接用公开 `5m/15m` K 线，为 BTC/ETH 做两个 proxy：
   - roughness / Hurst 类代理；
   - local divergence / Lyapunov 类代理；
   都再除以 rolling realized vol。
2. **信号层**：只测最简单规则——两个归一化 ratio 同步翻正做多、同步翻负做空、冲突空仓；持有 `1/2/4/8` bars 做 time-stop 梯度。
3. **成本层**：统一跑 `2/4/6/8 bps` friction ladder，看它是不是只在零成本世界里成立。

如果弱复刻连 gross 都站不住，就不用继续；如果 gross 能站住，再去补正文或找等价实现，把论文里的正式定义补全。

## 8. 来源信息

1. Blackledge, J., & Blackledge, A. (2025). *Optimisation of Cryptocurrency Trading Using the Fractal Market Hypothesis with Symbolic Regression*. *Commodities*.
   - DOI: `10.3390/commodities4040022`
   - Readable URL: `https://doi.org/10.3390/commodities4040022`
   - Journal URL: `https://www.mdpi.com/2813-2432/4/4/22`
2. DOAJ article page:
   - `https://doaj.org/article/35c21117f3794f6db8f7007d168cb068`
3. Crossref metadata:
   - `https://api.crossref.org/works/10.3390/commodities4040022`
