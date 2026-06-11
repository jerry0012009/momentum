# 先别把 intraday predictability 读成“日内动量老故事”：对 short-cycle crypto desk，更该先拆的是「前段小时收益 × 后段小时延续/反转」这条 raw alpha
- 时间：2026-04-18 08:41 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：同一交易日内，较早小时段的收益方向与幅度，可预测后续小时段出现 continuation 或 reversal
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / single-asset / intraday / momentum / reversal / hour-block / btc / eth / xrp / ltc / 5m / 15m / paper
- 证据类型：论文证据（IDEAS 摘要 + 出版商可读引言/section snippets；正文受限）

## 1. 这次看了什么
一篇直接研究 crypto **日内收益可预测性** 的论文：Wen, Bouri, Xu, Zhao (2022) 检查 BTC 在同一日内不同时段收益之间，哪些是顺着走、哪些会反手打脸，并且把这个框架外推到 ETH / LTC / XRP。

## 2. 核心结论
- **一句话核心结论**：crypto 的日内 alpha 不是单纯“追涨杀跌”，而是**某些小时段更像 continuation，某些更像 reversal**，而且这种结构会被 jump、流动性、FOMC、COVID 阶段明显改写。
- **一句话证明方式**：作者用 **2013-03-03 到 2020-05-31 的 BTC 5 分钟数据** 聚合成小时收益，做 **IS/OOS predictability** 检验，只保留 **IS 显著且 OOS R² 为正** 的 predictor-target 小时对，再做 timing strategy 与基准比较。
- 对我们最值钱的不是“照抄某个固定 hour-of-day 规则”，而是把它翻译成：**前 1~2 小时冲击的 sign、幅度、是否伴随 jump / 低流动性，能不能决定接下来 1~2 小时该跟还是该反着做。**
- 论文明确指出：crypto 里既有 momentum，也有 reversal；其中 reversal 被作者解释为**对非基本面信息的过度反应/过度自信**，这正适合做我们 desk 的 shock-fade 与 veto 分层。
- 他们还说明 timing strategy 的经济价值**优于 always-long / buy-and-hold**，且现象在 ETH / LTC / XRP 也能看到，说明这不是只属于单一 BTC 时段噪音的故事。

## 3. 为什么和当前项目有关
这篇东西和当前 `momentum` 主线高度相关，因为它补的是一个**真正可独立复现的 raw alpha**：`hour-block continuation/reversal`。它既能服务 trend/momentum，也能自然延伸到 mean reversion。更重要的是，它提醒我们：短周期里不要预设“短线永远顺势”或“短线永远反转”，而要先回答**当前这段前置收益更像信息迟到，还是情绪过冲**。

## 3.5 策略拆解（必填）
- 方向属性：顺势 + 逆势（条件切换）
- 基础 alpha：前段小时收益对后段小时收益的条件预测
- regime：是否有 jump、是否低流动性、是否处于 FOMC/宏观事件窗口
- filter / veto：仅在 predictor bar 的绝对收益、成交额分位、jump 标记满足阈值时开仓
- risk / sizing / execution overlay：ATR 或 predictor-bar range 定仓；固定持有 2~4 根 `15m` 或 4~12 根 `5m`；事件窗前后降仓；先用 taker 粗测，再看 maker-first 是否可活

## 4. 可复刻的最小实验
- 研究假设：当过去 `60m` 收益为极端正/负，且没有 jump 时，后续 `60m` 更容易 continuation；若伴随异常 jump 或超短时冲击过深，则更容易 reversal。
- 可计算定义：在 Binance BTCUSDT perpetual 上，用 `15m` 聚合成 rolling `60m` predictor return；再按 `jump_flag`（如 `|ret_15m| > 2.5 * rolling_vol_20`）与成交额分位分桶，分别预测未来 `60m` 收益。
- 最小回测切口：资产先做 `BTCUSDT`，再扩到 `ETHUSDT/SOLUSDT`；周期先 `15m`，补 `5m`；样本先近 12 个月，交易成本先按双边 `6~10 bps` 粗测。
- 最先看 2 个指标：`post-cost expectancy per trade`、`不同 regime 下的 trade count / hit-rate`。如果 continuation 与 reversal 只在少数事件窗成立，就把它降级成 event-conditioned alpha，而不是全时段主引擎。

## 5. 风险与保留意见
- 当前可读到的是 IDEAS 摘要与出版商引言/section snippets，**不是完整正文逐表核对**，所以不能假装已经吃透全部回测细节。
- 论文口径是 **BTC 5 分钟数据聚合到小时**，直接搬到 `5m/15m` 可能会放大噪音与成本，需要重新找 predictor-target 配对。
- 论文覆盖到 2020，中间包含疫情与早期高低效阶段；2026 的主流永续市场可能只剩“事件窗 pocket”，不一定适合作为全天候主信号。
- 它更像一块**alpha 母板**：真正落地时，要把 “continuation 触发” 和 “reversal 触发” 分开评估，而不是合并成一个模糊规则。

## 6. 来源
- Zhuzhu Wen, Elie Bouri, Yahua Xu, Yang Zhao. (2022). *Intraday return predictability in the cryptocurrency markets: Momentum, reversal, or both*. *The North American Journal of Economics and Finance*, 62, 101733.
- DOI: `10.1016/j.najef.2022.101733`
- Readable URL: `https://ideas.repec.org/a/eee/ecofin/v62y2022ics1062940822000833.html`
- Publisher URL: `https://www.sciencedirect.com/science/article/abs/pii/S1062940822000833`
- Related preprint DOI: `10.2139/ssrn.4080253`
- Preprint URL: `https://doi.org/10.2139/ssrn.4080253`
