# 别逼 EMA 或 breakout 单独扛 alpha：在 crypto 里，更像有效的是“按市场状态动态组合”
- 时间：2026-03-15 13:42 UTC
- 类型：论文
- 主题标签：trend / breakout / ema / combination / regime / crypto
- 证据类型：论文全文（期刊全文）

## 1. 这次看了什么
这次看的是：
- **Héctor A. Mugueta-Aguinaga, Eduardo Bazán-Palomino, Nour Meddahi, Manuel Urquhart, John Cotter (2023)**
- **Trend following with machine learning in cryptocurrency markets**
- Venue: **Journal of Forecasting**
- DOI: **10.1002/for.2936**

这篇不是在问“哪个单一指标最神”，而是在问更贴近你现在困惑的一件事：**EMA 家族、breakout 家族、TSMOM 家族，到底该当独立 alpha，还是该当可切换的组件？**

## 2. 核心结论
- **结论 1：trend-following 家族在 crypto 里有用，但更像“组件池”，不是谁都适合单独扛策略。** 作者在 **20 个资产（15 个发达市场 ETF + 5 个 crypto）、2014–2020、21 条趋势规则** 上做 OOS 比较，发现机器学习动态组合整体优于 buy-and-hold 和简单基准组合。
- **结论 2：在 crypto 子样本里，动态组合明显优于固定组合。** 文中给出的 crypto 子样本结果是：**机器学习方法平均年化收益 6.4%，信息比率 0.53；传统 trend-following 基准组合是 3.2% / 0.39；buy-and-hold 只有 1.4% / 0.23（成本后）**。
- **结论 3：优势在 turbulence 时更强。** 作者明确写到：**out-of-sample gains are generally larger during episodes of market turbulence**。翻成人话：**行情越乱，越不该迷信单一 EMA 或单一 breakout；越该让不同趋势信号分工。**
- **结论 4：真正值钱的不是“KNN 本身”，而是角色判断。** 论文里最好的实现是 KNN，但对你现在更重要的启发是：**moving average、breakout、time-series momentum 的价值，取决于市场状态；它们更像互补模块。**

## 3. 为什么和当前项目有关
一句话核心结论：**EMA / breakout / retest 不该争谁是唯一 alpha，更合理的做法是先承认它们是不同市场状态下的分工组件。**

一句话证明方式：**作者在多资产、含 crypto 子样本的 OOS 框架里，比较固定组合与动态加权组合，并在交易成本后仍看到优势。**

这篇对三条收口线都有直接帮助：
1. **`EMA / PSAR raw alpha focus`**：支持把 EMA / PSAR 从“独立引擎”降级成**可加权组件 / 方向层 / 风险开关**。
2. **`V3 final-verdict / breakout-short follow-up`**：支持把 breakout 视为**在某些状态下才加权上升的触发层**，不是全时段硬开。
3. **`Fibonacci confirmation / retest_hold`**：更像**确认增强组件**，适合在已知趋势/波动状态下加分，而不是单独开仓。

## 4. 可复刻的最小实验
### 研究假设
在 15m crypto 里，**固定规则层级**（永远 EMA > breakout > retest）大概率不如 **简单状态切换下的动态加权**。

### 最小对照
- 资产：BTC / ETH / SOL perpetual
- 周期：15m
- 样本：最近 180d

做三组：
1. **fixed-priority**：EMA 方向过滤 + breakout 触发 + retest/fib 确认，固定顺序不变
2. **equal-vote**：EMA、breakout、retest 各给 1 票，达到阈值才开仓
3. **state-weighted**：按简单 turbulence / trend regime 切换权重
   - 趋势清晰：`EMA=0.5, breakout=0.3, retest=0.2`
   - 高噪声/高波动：`EMA=0.2, breakout=0.2, retest=0.6`
   - 震荡：提高 no-trade 权重，降低 breakout 权重

### 最小状态定义
- `trend_regime = sign(EMA50 - EMA200)`
- `turbulence = ATR_ratio 或 realized_vol_quantile`

### 先看哪 2 个指标
- `post_cost_return`
- `return_per_trade`

如果 state-weighted 明显优于 fixed-priority，就说明当前该继续做的是“角色分工 + 状态切换”，而不是再问一次“到底 EMA 还是 breakout 更真”。

## 5. 风险与保留意见
- 论文的最优实现用了 ML；你当前不一定要直接上 KNN。更稳妥的吸收方式是：**先用手写状态切换 / 简单权重，验证组合思想，再谈 ML。**
- 样本是日频到月频的跨资产组合，不是 15m crypto；因此要迁移的是**设计原则**，不是参数。
- 这篇最适合回答“组件怎么分工”，不适合直接回答“某个单因子阈值该设多少”。

## 6. 来源
1. Mugueta-Aguinaga, H. A., Bazán-Palomino, E., Meddahi, N., Urquhart, M., & Cotter, J. (2023). *Trend following with machine learning in cryptocurrency markets*. Journal of Forecasting.
   - DOI: https://doi.org/10.1002/for.2936
   - Readable URL: https://onlinelibrary.wiley.com/doi/full/10.1002/for.2936
