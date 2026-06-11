# 别把高波动只当风控：这篇 JFQA 2024 更该先测的是「positive-jump variance 横截面 fade」raw alpha
- 时间：2026-03-25 16:00 UTC
- 类型：2024 JFQA 顶刊论文（全文 PDF）+ Cambridge 摘要页
- 主题类型：raw alpha
- 基础 alpha：做多过去一段时间里 `positive-jump variance` 最低的一篮子币、做空最高的一篮子币，赚“彩票型暴冲币随后横截面掉队”的回报
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/mean-reversion/lottery-fade/positive-jump-variance/jump-robust-variance/realized-variance/15m/5m/1m/binance/perpetual/paper
- 证据类型：顶刊论文全文证据 + 组合回测 + Fama-MacBeth 回归 + 机制检验

## 1. 这次看了什么
先回答 base alpha：**这篇的 base alpha 不是 filter，而是“横截面做空高 `positive-jump variance` 币、做多低 `positive-jump variance` 币”的独立 raw alpha。**

这次主看 Suzanne S. Lee、Minho Wang 发表于 *Journal of Financial and Quantitative Analysis* 的 2024 论文 *Variance Decomposition and Cryptocurrency Return Prediction*。一句话核心结论：**真正值得 desk 先复现的，不是“高波动币要避开”，而是“把高正跳变/高跳变稳健波动当成应被横截面做空的 lottery bucket”。** 一句话它怎么证明：**作者用 100 个币、2015-10~2023-06、15 分钟级数据构造 realized variance，再用 tercile 组合、多因子 alpha 和 Fama-MacBeth 回归把负向定价关系钉住。**

## 2. 核心结论
- **总 realized variance 本身就有负向预测力。** 论文按过去 1 个月估计的 variance 把 100 个币分 tercile，下一周 `Low - High` 收益差为 `+3.7%/周`（EW，对应年化约 `193%`），VW 也有 `+3.0%/周`。
- **最值得偷的不是“负跳变”，而是 `positive jump variance`。** 在 `positive jump variance` 分组里，`Low - High` 为 `+3.6%/周`（EW）和 `+2.3%/周`（VW）；控制滞后收益和市值后，FMB 回归系数约 `-1.492`，`t=-4.69`。
- **`jump-robust variance` 也有信息，但次于正跳变。** 其回归系数约 `-0.091`，`t=-2.00`；更像可与 `positive jump variance` 叠加的第二轴，而不是主轴。
- **效果在“更乱、更挤”的市场里更强。** 高市场波动阶段，`positive jump variance` 系数约 `-1.890`，显著强于低波动阶段的 `-1.032`；高 illiquidity 阶段也依然明显。
- **机制上很像 crypto 特有的“彩票偏好 + 散户拥挤”。** 高 `positive jump variance` 那一篮子往往更小盘、更宽点差、散户交易占比更高、社媒买入情绪更热，这说明它不是单纯风险补偿，更像被追捧过头后的横截面回吐。

## 3. 为什么和当前项目有关
这条线和我们当前 desk 的关系很直接：它补的是 **cross-sectional / relative-value / mean reversion** 素材池，而不是再补一个确认层。更具体地说：
- 它给了一个和“24h loser reversal”不同的 raw alpha 轴：**不是看谁跌多了，而是看谁最近“向上炸得太花”**。
- 它天然适合 `15m` 形成慢信号、`1m/3m/5m` 负责执行：信号更新不必每根 bar 变，换手可以比纯 1m 排名策略更低。
- 它还能服务于后续组合化：可和已有 `loser basket`、`beta-gap`、`funding/basis` 做正交性检查，看它是不是一条独立 edge，而不是别的因子的影子。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值 / 逆势（lottery-fade）
- 基础 alpha：高 `positive-jump variance` 币在后续窗口里横截面跑输，低 `positive-jump variance` 币相对更强
- regime：市场整体高波动、高清算、较差流动性阶段可考虑 size-up；极端单边牛市里谨防 short leg 被 squeeze
- filter / veto：仅保留可交易的 top-50~100 perp；剔除极端点差、异常 funding、临近下架/事件币；必要时只做 market-neutral basket
- risk / sizing / execution overlay：equal-dollar 或 beta-neutral 长短配；单币权重上限；15m 排名、1m/3m TWAP/VWAP 执行；显式计入手续费+滑点+冲击

## 4. 可复刻的最小实验
- **研究假设：** 在 Binance USDT perp 的可交易 universe 中，过去 `72h` 的 `positive-jump variance` 越高，未来 `4h~24h` 的横截面相对收益越差。
- **一个可计算定义：** 用 `5m` 或 `15m` 收益率；`RV=sum(r^2)`；`positive-jump variance ≈ sum(r^2 * 1[r > k·σ_roll])`，先用朴素阈值版做 MVP，第二轮再换 bipower / jump test。
- **最小回测切口：** top 50~100 永续合约，样本先取 2023-01 至今；每 `15m` 重算过去 `72h` 信号，做 `long bottom decile / short top decile`，持有 `16 bars(4h)`、`48 bars(12h)`、`96 bars(24h)` 三档。
- **最该先看：** `post-cost spread return`、`turnover`；其次看 `BTC beta`、short leg 集中度、不同市场波动分位下的分层表现。

## 5. 风险与保留意见
- 论文证据主窗口是“过去 1 个月波动 → 下一周收益”，直接压到 `1m/3m/5m/15m` 会损失一部分边，需要重新找最短还能活的 holding window。
- 论文使用的是 15 分钟中间价与较宽 universe；实盘 perp 更容易被点差、资金费、下架和冲击污染，特别是 short leg。
- 这条线很可能吃 liquidity / lottery crowding 的结构性溢价；若只剩大币高流动性子集，边际收益可能明显缩水。
- 论文也显示旧阶段更强、后期样本变弱，所以 desk 侧第一件事不是调参数，而是先确认 2023 之后还有没有净边。

## 6. 来源
1. **Lee, S. S., & Wang, M. (2024). _Variance Decomposition and Cryptocurrency Return Prediction_. Journal of Financial and Quantitative Analysis.**  
   - DOI: `https://doi.org/10.1017/S002210902400022X`  
   - Readable URL: `https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/variance-decomposition-and-cryptocurrency-return-prediction/9995E58095453CB44A3BC3C9C111969F`  
   - PDF URL: `https://www.cambridge.org/core/services/aop-cambridge-core/content/view/9995E58095453CB44A3BC3C9C111969F/S002210902400022Xa.pdf/variance-decomposition-and-cryptocurrency-return-prediction.pdf`
2. **Binance Developers. USDⓈ-M Futures Market Data API.**  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 7. 下一步怎么测（必须）
1. 先做 **朴素版 `positive-jump variance` 排名**：别一上来就上复杂 jump test，先验证 top-decile short / bottom-decile long 在 `4h~24h` 是否还有 post-cost 净边。  
2. 再做 **`positive-jump variance × market-vol regime` 双排序**：验证这条 edge 是否真的只在高波动周期开 size 才值钱。  
3. 做 **大币子集 vs 全 universe**：确认这条线到底是“可交易 edge”，还是只活在小币/高摩擦桶里。  
4. 最后和现有 `24h loser reversal`、`beta-gap` 做相关性矩阵：若相关性不高，就值得进 raw alpha 素材池优先队列。