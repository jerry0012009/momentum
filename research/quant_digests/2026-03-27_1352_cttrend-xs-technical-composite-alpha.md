# 别把这篇 2025 JFQA 新论文只当日频因子：它更该先测的是「多窗口技术指标压缩成一个横截面趋势分数」raw alpha
- 时间：2026-03-27 13:52 UTC
- 类型：2025 JFQA 开放获取全文 PDF（Cambridge 可读）
- 主题类型：raw alpha
- 基础 alpha：多窗口技术/量价趋势更强的币，未来一个再平衡窗口里继续跑赢横截面；更弱的币继续跑输
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/trend/momentum/technical-indicators/composite-signal/elastic-net/forecast-combination/market-neutral/price-volume-volatility/5m/15m/1m/3m/paper/cost
- 证据类型：论文全文证据

## 1. 这次看了什么
这次看的是 **Fieberg, Liedtke, Poddig, Walker, Zaremba (2025), _A Trend Factor for the Cross Section of Cryptocurrency Returns_**, 发表在 **Journal of Financial and Quantitative Analysis**。这篇东西对 desk 真正有价值的，不是把一个周频因子原样照搬进 `5m`，而是它把一条 **可独立复现的横截面 raw alpha** 讲得很完整：

> **base alpha 很清楚：把多窗口价格/成交量/波动率技术指标压缩成一个横截面趋势分数，做多最强那篮子，做空最弱那篮子。**

所以它不是“某个 filter 帮你确认 breakout”，而是一条可以独立成策略的 **cross-sectional trend / relative-strength continuation** 主线。

## 2. 核心结论
- **一句话核心结论：** 这篇论文的 alpha 本体不是单一 RSI / MACD，而是 **28 个技术指标的组合信号 CTREND**；它预测的是“下一个持有窗口里，谁会在截面上继续更强/更弱”。
- **样本和构造：** 论文覆盖 **3,245 个币、2015-04 到 2022-05**；输入包括 **28 个指标**，分成四组：
  - 动量震荡类：`RSI / stochastic / stochRSI / CCI`
  - 价格均线类：`3/5/10/20/50/100/200d SMA`、`MACD`
  - 成交量类：`volume SMA / volume MACD / Chaikin`
  - 波动类：`Bollinger lower/mid/upper/width`
- **组合方法：** 论文不是手拍权重，而是先对每个指标各自做预测，再用 **cross-sectional combined elastic net (CS-C-ENet)** 做“保留哪些预测，再等权合成”。这点对 desk 很重要，因为它比黑箱 RF 更轻，也比“单特征排序”更像可扩展的研究骨架。
- **headline 数字：** 周频 value-weighted `Q5 - Q1` 多空组合，**gross return = `3.87%/week`，t-stat = `5.19`**。
- **不是只活在小垃圾币里：** 在 **Top 100 largest** 币里，`H-L` 仍有 **`3.39%/week`**（t = `4.49`）；在 **Top 100 most liquid** 币里，`H-L` 仍有 **`3.30%/week`**（t = `4.36`）。
- **不是成本一扣就死：** 论文按 **long 30bps / short 40bps** 的保守周频交易成本估计，全集合 `H-L` 的 **net return 仍有 `2.90%/week`**（t = `3.89`）；Top 100 大币版也还有 **`2.45%/week`**（t = `3.22`）。
- **不是单一设定偶然撞出来：** 论文系统扫了 **55,296** 组实现，CTREND 在 **79%** 的设定里仍拿到显著正 Sharpe，说明它更像一个“稳定的组合型 technical raw alpha”，而不是某个参数碰巧有效。
- **一个很 desk-relevant 的细节：** 文中明确提到，在 crypto 里，像 **RSI、stochastic 这类本来常被当成 reversal 指标的东西，实际更像 continuation 指标**。这点很值钱，因为它提醒我们：短周期别默认“高 RSI 必 fade”，crypto 往往先表现成趋势延续资产。

## 3. 为什么和当前项目有关
这篇东西值得进池，不是因为它“又给了一个日频因子”，而是因为它正好补了当前素材池里一个很缺的槽位：

- 它是 **raw alpha**，不是 overlay；
- 它是 **cross-sectional / market-neutral**，能和当前单币 directional 线互补；
- 它不是只押一个特征，而是给出一套 **多特征压缩 -> 排名 -> 多空组合** 的完整流程；
- 它比今天已经 intake 过的 RF stat-arb 路线 **更可解释、实现更轻、特征更容易搬到 `1m/3m/5m/15m`**；
- 它比“risk-managed XS momentum”更像 alpha 本体，因为这里 **组合分数本身就是预测信号**，不是在已有动量上再套一个 risk overlay。

如果 bot7 当前目标是继续补 **可复现、可独立落地、能形成完整策略骨架的 raw alpha**，这篇是合格的。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对强弱 / market-neutral
- 基础 alpha：多窗口技术趋势强者继续强、弱者继续弱
- entry：每次再平衡时，按综合技术分数排序，做多 top bucket、做空 bottom bucket
- exit：固定持有到下一个再平衡窗口，或在分数反转时换仓
- sizing：先做 long-short 等权；第二层可改成 inverse-vol / liquidity-cap / score-proportional
- risk：控制单币权重、行业/主题暴露、beta 偏移、极端 funding / event window
- cost：这是高换手策略，必须做 friction ladder；若短周期迁移后 turnover 爆炸，edge 很容易被吃掉
- 更适合的 regime：截面分化高、趋势 breadth 不差、流动性充足
- 主要 veto：stablecoin、极低流动性币、疑似 wash-volume 币、重大公告前后极端跳空时段

## 4. 可复刻的最小实验
**研究假设：** 论文里的周频 CTREND 不必原样照搬；但它的核心结构——**多窗口技术特征压缩成一个横截面趋势分数**——应该可以在 liquid perp universe 上做出一个 `5m/15m` 的 intraday CTREND-lite。

**最小实验建议：**
1. **Universe：** Binance / OKX / Bybit 的 `20~40` 个流动性最好的 USDT perpetual，先排除稳定币、低成交和新币。
2. **Bar：** 先做 `15m`，再下钻 `5m`；`1m/3m` 只在 `5m` 有雏形后再压缩。
3. **特征：** 不必一开始就凑满 28 个日频指标，先做 intraday 对应物：
   - 过去 `1/2/4/8/16/32` bar 收益
   - price-to-SMA 距离（`4/8/16/32` bar）
   - volume-to-volume-SMA 比例
   - intraday RSI / MACD / Bollinger mid & width
   - 过去 `N` bar realized vol / range
4. **信号压缩：** 先跑 3 档，从便宜到复杂：
   - `z-score` 等权合成
   - 单特征 rank IC/回归系数筛选后等权
   - elastic net 选特征后等权合成（最接近论文）
5. **组合定义：** 每 `30m` 或 `60m` 再平衡一次，`long top 20% / short bottom 20%`；持有 `1h / 2h / 4h` 三档；先做 non-overlap 版本避免统计错觉。
6. **成本口径：** 至少跑 `4 / 8 / 12 bps round-trip`，并记录 turnover、净 alpha、top-bottom spread、胜率、收益对少数币是否过度集中。
7. **成功标准：** 不是只看 gross，而是看：
   - 成本后 top-bottom spread 是否仍 > 0；
   - 是否主要来自 liquid majors / midcaps，而不是 microcaps；
   - `15m` 是否比 `5m` 更稳；
   - 特征压缩版是否明显优于单一 return-rank baseline。

## 5. 我对这条线的当前判断
我的判断是：**值得立刻进入研究池，而且优先级不低。**

原因不是“论文周频收益看起来很高”，而是它给了我们一条当前 desk 很需要的中间层骨架：
- 不是单特征；
- 不是纯黑箱；
- 不是只做 filter；
- 而是 **可解释的多特征横截面 raw alpha engine**。

但也要老实：**原论文是日频特征 + 周频调仓**，所以对 `5m/15m` 的价值是“结构可迁移”，不是“收益率可直接平移”。真正需要验证的只有两件事：
1. intraday 上这种“技术特征压缩”还能不能保留稳定的截面排序力；
2. 短周期换手会不会把它从 alpha 打回 feature engineering 幻觉。

如果这两点里第一点成立、第二点不太坏，它就能成为一条比“plain 24h momentum”“单一 reversal 排序”更像平台级母策略的原型；如果第一点不成立，也仍然可以把它退化成 **shared gate / score layer**，服务于已有 momentum、breakout、short-term reversal、pairs admission。

## 6. 下一步最该怎么测
如果只给一个最优先动作，我会做这个：

> **先在 Binance USDT perp 的 `15m` universe 上做一个“CTREND-lite vs plain return-rank” 对照实验。**

也就是：
- 同一 universe；
- 同一 holding window；
- 同一成本口径；
- 只比较 `多特征压缩分数` 是否真的优于 `过去 4~16 bar 累积收益排序`。

这是最便宜、最能迅速判断“这篇东西是在提供新 alpha，还是只是把已有 momentum 重新包装”的实验。

## 7. 来源与可复用材料
1. **Fieberg, C., Liedtke, G., Poddig, T., Walker, T., & Zaremba, A. (2025). _A Trend Factor for the Cross Section of Cryptocurrency Returns_. Journal of Financial and Quantitative Analysis, 60(7), 3116–3153.**  
   DOI：<https://doi.org/10.1017/S0022109024000747>  
   Readable URL：<https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/trend-factor-for-the-cross-section-of-cryptocurrency-returns/4C1509ACBA33D5DCAF0AC24379148178>  
   PDF URL：<https://www.cambridge.org/core/services/aop-cambridge-core/content/view/4C1509ACBA33D5DCAF0AC24379148178/S0022109024000747a.pdf/div-class-title-a-trend-factor-for-the-cross-section-of-cryptocurrency-returns-div.pdf>
2. **补充方法脉络（论文内直接承接）**：Han et al. 关于 technical composite / forecast combination / elastic-net selection 的股票市场方法文献，是把这篇东西往 intraday CTREND-lite 迁移时最值得复用的方法骨架。
3. **Repo URL：** 暂未见作者公开的官方复现仓库；这条线更适合按论文公式直接轻量重写，而不是等 repo。