# 别把这篇 2021 全球 intraday momentum 论文只读成“股票市场小异象”：对 short-cycle crypto desk，更该先回答的是「短窗收益延续 × 市场特征 admission」这条 raw alpha 在 24/7 市场里还能剩下什么

- 时间：2026-04-23 12:49 UTC
- 类型：2021 *Journal of Financial Markets* 论文 audit（Crossref + Semantic Scholar abstract + accepted-version metadata）+ Binance USDⓈ-M public-data portability probe（8 liquid majors，`15m`）
- 主题类型：raw alpha
- 基础 alpha：**刚刚走出的短窗收益，在很短的后续窗口里仍有延续；并且这条延续在特定市场状态下更强。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/single-asset/intraday/momentum/continuation/market-characteristics/liquidity/volatility/15m/paper/public-data/cost/risk
- 证据类型：paper evidence + public-data portability probe

## 1. 这次看了什么
主线材料：
- **Authors：** Zeming Li, Athanasios Sakkas, Andrew Urquhart
- **Year：** 2021（刊于 2022 年卷期）
- **Title：** *Intraday time series momentum: Global evidence and links to market characteristics*
- **Venue：** *Journal of Financial Markets*, Volume 57
- **DOI：** `10.1016/j.finmar.2021.100619`
- **Readable URL：** <https://doi.org/10.1016/j.finmar.2021.100619>
- **Open-access manuscript：** <https://centaur.reading.ac.uk/95566/1/Accepted-Version.pdf>

先把 base alpha 说清楚：
> **这篇东西讲的不是日频 trend-following，而是“刚刚这段 intraday 涨跌，下一小段里还会不会顺着走”这条最原始的短窗 continuation。**

论文摘要给出的核心证据是：
- intraday time-series momentum 在多数已开发市场里 **样本内、样本外都显著**；
- 这条 edge 在 **高波动、低流动性、信息离散到来** 的环境里更强；
- 作者把它解释为 **微观结构 + 行为因素** 共同驱动，而不是单纯数据挖掘。

## 2. 一句话结论
- **一句话核心结论：** “短窗收益延续”本身是条清楚的 raw alpha，但把它直接搬到 Binance `15m` liquid majors 上裸跑，当前更像手续费陷阱；真正值得借的是它的 **market-characteristic gate 思路**。  
- **一句话证明方式：** 论文靠 16 个发达市场高频样本做 in-sample / out-of-sample 实证；我这轮再用 Binance 公共 `15m` 数据做了一个最小 portability probe，看 raw alpha 本体在 crypto 里还有没有毛边。

## 3. 为什么和当前项目有关
它对 `momentum` 主线的价值，不是“又来一篇 momentum 论文”，而是把两层东西拆开了：
1. **raw alpha 本体**：recent-return continuation；
2. **shared gate**：什么时候这条 continuation 更容易活下来。

这正好适合我们现在的 desk：
- 若 base alpha 本身成立，可做成单币 intraday momentum / cross-asset router；
- 若 base alpha 不够厚，也能把“高波动 / 流动性 / 信息离散”这些维度抽成 **共享 admission filter**，给别的趋势 alpha 服务。

## 3.5 策略拆解（必填）
- 方向属性：顺势
- 基础 alpha：短窗收益延续（recent intraday return continuation）
- regime：高波动 / 信息离散到来时更强
- filter / veto：低质量时段、低 edge 时段、成本不足覆盖时不开仓
- risk / sizing / execution overlay：inverse-vol sizing + maker-first child execution + trade-count throttle

## 4. 本轮最小 portability probe
我先不复刻论文全部市场设计，只抓最核心一句：
- **信号：** 过去 `30m` 收益的符号
- **交易：** 若过去 `30m` 为正，做多下一段 `30m`；若为负，做空下一段 `30m`
- **资产：** `BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK`
- **周期：** Binance USDⓈ-M `15m`
- **样本：** 近 `1500` 根 `15m` bar（每币约两周）
- **成本：** 粗扣 `8 bps` round-trip

先给 4 个数：
1. **8 币平均 gross**：`-0.56 bps/笔`
2. **8 币平均 net**：`-8.56 bps/笔`
3. **平均胜率**：`47.4%`
4. **高波动四分位 net**：`-6.00 bps/笔`，明显好于低波动四分位的 `-9.56 bps/笔`

补两条和论文最相关的状态差异：
- **高流动性四分位**：`-6.71 bps/笔`
- **低流动性四分位**：`-9.28 bps/笔`

翻成人话：
- 在 24/7 crypto liquid majors 上，**“刚涨继续涨 / 刚跌继续跌”这条裸 intraday alpha 当前没过线**；
- 但“高波动时更像样”这半句还在；
- 论文里的“低流动性更强”搬到 Binance majors 后没有保留，反而更像 **高流动性时段伤得没那么重**。

## 5. 风险与保留意见
1. **市场结构差异很大**：论文是股票市场，有开收盘、信息集中过夜、流动性分层；crypto 是 `24/7` 连续交易，直接平移天然会变形。  
2. **当前 probe 很轻**：只测了一个最朴素的 `30m -> 30m` continuation，没有复刻论文的完整时段设计。  
3. **liquid majors 可能不是最佳土壤**：这类 edge 可能更适合 alt、事件窗口或 cross-sectional winner/loser 子集，而不是全体大币统一裸做。  
4. **它目前更像“gate 研究入口”**：若 base alpha 本体不过费，不该硬包装成完整策略。

## 6. 下一步怎么测
1. **做 hour-of-day 切片**：把 UTC 24 小时拆开，看是否只在少数“信息更离散”的时段有正毛边。  
2. **做 gated continuation**：只在 `rv_pct >= 75%` 的高波动档开仓，再看 trade count 与 net bps/trade 是否抬升。  
3. **做 cross-sectional 版本**：不要全币裸做，改成“只交易过去 `30m` move 最极端的前/后 2 只”，看 recent-return continuation 是否在 leader bucket 更厚。  
4. **做 `15m parent / 5m child`**：父层只给方向，子层等 pullback 或 maker-friendly 入场，检验是否能把 gross edge 从负数拉回到接近零以上。

## 7. 来源
- Li, Z., Sakkas, A., & Urquhart, A. (2021/2022). *Intraday time series momentum: Global evidence and links to market characteristics*. *Journal of Financial Markets*, 57, 100619.
- DOI: <https://doi.org/10.1016/j.finmar.2021.100619>
- Accepted-version PDF: <https://centaur.reading.ac.uk/95566/1/Accepted-Version.pdf>
- Semantic Scholar metadata/abstract: <https://www.semanticscholar.org/paper/cee647f6b9ddd0d3a86d5f93dd0010f6f39bb696>
