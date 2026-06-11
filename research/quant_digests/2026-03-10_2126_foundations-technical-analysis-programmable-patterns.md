# Foundations of Technical Analysis：先证明“形态能被程序化”，再谈 breakout / pullback alpha
- 时间：2026-03-10 21:26 UTC
- 类型：论文
- 主题标签：trend / breakout / pullback / structure / alpha
- 证据类型：论文证据 + 方法论地基

## 1. 这次看了什么
这次主看 Lo, Mamaysky, Wang (2000) 的 **Foundations of Technical Analysis: Computational Algorithms, Statistical Inference, and Empirical Implementation**。这篇虽然不新，但它正好补你当前最需要的地基：**技术分析不是只能靠主观看图，它可以被自动识别、统计检验，并与未来收益分布挂钩。**

## 2. 核心结论
- 论文摘要的第一层结论非常关键：作者明确指出，技术分析长期不被学界认真对待，一个核心障碍就是“图形识别太主观”；因此他们提出的是**systematic and automatic approach**，用非参数核回归去做技术形态识别。
- 第二层结论更重要：他们不是只画图，而是把“无条件收益分布”和“在特定技术指标/形态出现条件下的收益分布”做比较。摘要给出的口径是：**若干技术指标确实提供了 incremental information，并且可能有 practical value。**
- 对当前研究最值钱的启发是：真正值得保留的不是“某个神秘图形名称”，而是**可程序化的价格结构条件**。也就是说，breakout、double-bottom、回踩恢复这类东西，只有被写成可计算条件，才有资格进入因子池。
- 这篇也提醒你，结构 alpha 的正确研究方式不是先争论图形美不美，而是：**先把形态转成规则，再看条件收益分布有没有偏移。**

## 3. 为什么和当前项目有关
这篇和 `momentum` 当前主线非常贴，因为你现在正在学和做的，恰好就是“把图感压成规则”这件事：
- `EMA + Donchian` 其实是在把“趋势方向 + 突破触发”程序化；
- `pullback recovery confirmation` 是把“回踩后二次恢复”程序化；
- `endpoint NWE + confirmed extrema` 是把“摆点/结构”变成因果、非重绘的底层对象。

所以这篇论文的作用，不是直接给你一个能上实盘的 15m 信号，而是给你一条很清楚的研究路线：**先定义结构，再检验结构条件下的收益分布是否真的不同。** 这比一开始就围绕参数炼丹稳得多。

## 4. 可复刻的最小实验
- 研究假设：如果某个 breakout / pullback 结构是真的有 edge，那么它出现后的短期 forward return 分布，应该系统性区别于无条件样本。
- 一个可计算定义：先不追复杂图形，直接用现有项目里最成熟的两个结构条件：
  1. `breakout_confirm3`：收盘突破最近 `N` 根高点，且连续 3 根收盘维持在突破方向；
  2. `pullback_recovery`：高一级别趋势向上，回调不破前低/关键均线，随后重新站回短均线或最近摆点上方。
- 最小验证切口：BTC、ETH、SOL；15m；近 180d。先不做完整策略，先做**事件研究**：比较事件后 `1/3/6/12` 根 forward returns 与无条件样本的分布差异。
- 最该先看：`mean forward return`、`hit rate`；如果这一步都没有偏移，再谈完整回测大概率是浪费时间。

## 5. 风险与保留意见
- 这篇论文不是为 15m Crypto 写的，不能把它直接当成“币圈短周期已验证”。
- 论文证明的是“某些技术形态可能有统计信息”，不是“所有图形都有效”；形态空间一旦放太大，很容易过拟合。
- 对当前项目，最合理的迁移方式不是复刻论文里的全部图形库，而是保留其**研究范式**：先做少量、可解释、可因果实现的结构条件，再用条件分布和小型事件研究筛选。

## 6. 来源
- Lo, A. W., Mamaysky, H., & Wang, J. (2000). *Foundations of Technical Analysis: Computational Algorithms, Statistical Inference, and Empirical Implementation*. NBER Working Paper 7613.
- DOI: <https://doi.org/10.3386/w7613>
- Readable URL: <https://www.nber.org/papers/w7613>
- NBER 摘要页（可直接读取摘要）: <https://www.nber.org/papers/w7613>
- Jiang, J., Kelly, B., & Xiu, D. (2023). *(Re-)Imag(in)ing Price Trends*. The Journal of Finance.
- DOI: <https://doi.org/10.1111/jofi.13268>
- Readable URL: <https://onlinelibrary.wiley.com/doi/full/10.1111/jofi.13268>
