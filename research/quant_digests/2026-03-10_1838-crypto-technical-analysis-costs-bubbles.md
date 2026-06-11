# Crypto 技术分析在扣成本后还剩多少：交易成本与泡沫阶段会不会改写结论？
- 时间：2026-03-10 18:38 UTC
- 类型：论文
- 主题标签：breakout / trend / crypto / transaction-cost / regime
- 证据类型：论文证据

## 1. 这次看了什么
这次主看 Svogun, Bazán-Palomino (2022) 的 **Technical analysis in cryptocurrency markets: Do transaction costs and bubbles matter?**。它很适合接在你当前阶段后面，因为它不是继续空谈“技术分析有没有用”，而是直接追问：**放到 crypto、再扣掉交易成本、再区分泡沫阶段之后，技术规则还剩多少。**

## 2. 核心结论
- 作者把 **69 个参数化技术规则**（主要是 moving average 与 breakout 类）应用到 BTC、ETH、XRP、LTC、BCH，覆盖 **1-min 与 1-day** 两种频率，并明确比较“扣成本前/后”的结果。
- 论文明确给出的结论是：**一旦计入交易成本，盈利规则数量会下降**；而且这种打击在 **1-min** 上特别明显，说明超短频里“看起来有效”的技术规则很容易被摩擦成本吃掉。
- 但论文也没有把技术分析一棍子打死：在作者样本中，**扣成本后仍有一部分规则能保持正收益**，只是显著少于不计成本时。
- 另一个重要点是：**bubble periods matter**。作者用 PSY 方法识别泡沫期后发现，泡沫阶段会改变某些规则获得超额收益的概率；这说明技术规则并不是“永远同样有效”，而是明显受市场状态影响。

## 3. 为什么和当前项目有关
这篇很适合拿来给当前 `momentum` 主线“校准现实感”。你现在已经有 EMA 结构、Donchian breakout、pullback recovery、volume confirmation 等候选层；这篇提醒的是：
- breakout / trend 规则在 crypto 里**不是天然无效**；
- 但如果不做 **成本后评估**，很可能高估 alpha；
- 同一个规则在不同 **市场状态 / 泡沫阶段** 下可能表现不同，因此后续把 regime 标签接回 breakout / pullback 研究是有必要的。

换句话说，它不是帮你发明新因子，而是帮你避免把“纸面 alpha”误当成“可交易 alpha”。

## 4. 可复刻的最小实验
- 研究假设：15m 上的 breakout / pullback 规则，在不计成本时可能好看，但计入手续费 + 滑点后会显著分化；这种分化在强趋势 / 类泡沫阶段可能更小。
- 一个可计算定义：直接拿现有 `EMA + Donchian breakout` 或 `pullback recovery confirmation` 做 A/B：
  1. `gross`：不计成本；
  2. `net_low`：低手续费 + 低滑点；
  3. `net_high`：偏保守手续费 + 滑点；
  再额外按 `trend_strength` 或价格偏离长期均线的简单代理，把样本切成“强趋势/弱趋势”两组。
- 最小回测切口：BTC、ETH、SOL；15m；近 180d；先做单市场，再做 rolling。
- 最该先看：`post_cost_return`、`positive_window_ratio`；辅助看“成本后仍为正”的窗口占比。

## 5. 风险与保留意见
- 这篇论文的直接频率是 1-min 与 1-day，不是 15m；因此它给你的更多是**边界条件**，不是现成答案。
- 文中泡沫识别用了 PSY 方法；你在当前工程里不必急着完整照搬，可以先用更轻量的 trend / expansion 代理做第一版。
- 这篇更像“alpha 生存性检验”，不是“alpha 发明论文”；所以它最适合和现有 breakout / pullback 基线配套阅读。

## 6. 来源
- Svogun, D., & Bazán-Palomino, W. (2022). *Technical analysis in cryptocurrency markets: Do transaction costs and bubbles matter?* Journal of International Financial Markets, Institutions and Money.
- DOI: <https://doi.org/10.1016/j.intfin.2022.101601>
- Readable URL: <https://www.sciencedirect.com/science/article/pii/S1042443122000816>
- Crossref metadata: <https://api.crossref.org/works/10.1016/j.intfin.2022.101601>
