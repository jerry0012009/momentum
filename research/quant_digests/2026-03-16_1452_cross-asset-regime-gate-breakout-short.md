# breakout-short 别只盯本币 K 线：跨市场动量更适合当 continuation / failure 的先验过滤器
- 时间：2026-03-16 14:52 UTC
- 类型：论文
- 主题标签：breakout-short/cross-asset/regime/confirmation/avoid-chop
- 证据类型：论文全文（working paper + JFE 发表版）
- 证据强度提示：**中等**（大样本跨国债券/股票，非 crypto、非 15m）

## 1. 这次看了什么
这次看的是：
- **Aleksi Pitkäjärvi, Matti Suominen, Lauri Vaittinen (2020)**
- **Cross-asset signals and time series momentum**
- Venue: **Journal of Financial Economics**, 136(1), 63–85
- DOI: **10.1016/j.jfineco.2019.02.011**
- Readable URL: https://www.sciencedirect.com/science/article/pii/S0304405X19302156
- Working paper DOI / PDF: https://doi.org/10.2139/ssrn.2891434 （文内可见 SSRN 预印本）

这篇的关键不是“再做一个单资产动量信号”，而是：**别只看本资产过去收益，别的市场的趋势状态本身也会预测你这个市场接下来更容易延续还是失败。**

## 2. 核心结论
- **一句话核心结论**：把“跨市场方向”当作先验状态来过滤交易，通常比只盯本资产历史收益更稳。
- **一句话证明方式**：作者用 20 个国家债券+股票的大样本，做 time-series / cross-asset predictability 与组合层面的 alpha、spanning test，验证跨市场信号不是简单 TSMOM 的重复包装。
- 论文给出的代表性结果：
  1) 多元跨市场组合（XTSMOM）年化 Sharpe **0.89**，高于传统 TSMOM 的 **0.61**、买入持有的 **0.52**（样本 1980–2016）。
  2) XTSMOM 相对 TSMOM 的 Sharpe 提升约 **45%**，相对 buy-and-hold 约 **70%**。
  3) spanning test 中，XTSMOM 仍有 **0.33%~0.50% 月度 alpha**（t 统计约 **3.82~4.39**），说明它抓到的是增量信息而不是同义替换。

## 3. 为什么和当前项目有关（优先服务 breakout-short follow-up）
这篇对当前三条收口线里最直接的是 **`V3 final-verdict / breakout-short follow-up`**：
- 你现在遇到的核心痛点之一是：**很多 short breakout 在“看起来跌破”后又被快速拉回（failure）**。
- 这篇给出的可迁移原则是：**先看跨市场状态，再决定是否相信当前资产的局部跌破。**
- 翻成 15m 语言：
  - 若主导市场（例如 BTC）与风险代理（如 ETH/BTC、TOTAL3 proxy）同向走弱，则本币 short breakout 更像 continuation；
  - 若本币跌破但跨市场背景并不支持，优先把它归为高 failure 风险，收紧入场或降杠杆。

它也可作为 `EMA / PSAR raw alpha focus` 的角色分工补丁：EMA/PSAR 决定“本币是否在走弱”，跨市场因子决定“这次弱势是否有共振支撑”。

## 4. 可复刻的最小实验（直接可测）
### 研究假设
在 crypto 15m 上，给 breakout-short 加一层跨市场 regime gate，会降低假跌破率并提升成本后收益质量。

### 最小可计算定义
- baseline（现有）：`short_trigger = close < rolling_low_N - k*ATR`
- 新增 gate：
  - `cross_regime = 1` 当且仅当 `BTC_1h_ret < 0` 且 `BTC_4h_ret < 0`
  - 可选增强：`ETHBTC_1h_ret <= 0`（风险偏好未改善）
- 执行：仅当 `short_trigger & cross_regime==1` 才允许开空。

### 最小回测切口
- 标的：BTC/ETH/SOL perpetual
- 周期：15m
- 样本：最近 180d
- 对照：
  1) baseline short breakout
  2) + 跨市场 gate
  3) + 跨市场 gate + retest 失败确认（如 2-of-3 closes below）

### 先看 2 个指标
- `false_break_ratio`（跌破后 X 根内回到区间上方的比例）
- `post_cost_return`（扣费后收益）

## 5. 风险与保留意见
- 原论文是**债券/股票月频**，不是 crypto 5m/15m；迁移的是“设计原则”，不是参数。
- 跨市场 gate 若过严，会显著减少交易次数，可能“胜率升、总收益降”。
- crypto 里“主导市场”会阶段性变化（BTC 主导 vs alt 内部轮动），需做滚动再校准。

## 6. 来源
1. Pitkäjärvi, A., Suominen, M., & Vaittinen, L. (2020). *Cross-asset signals and time series momentum*. Journal of Financial Economics, 136(1), 63–85.
   - DOI: https://doi.org/10.1016/j.jfineco.2019.02.011
   - Readable URL: https://www.sciencedirect.com/science/article/pii/S0304405X19302156
2. Pitkäjärvi, A., Suominen, M., & Vaittinen, L. (Working paper). *Cross-Asset Signals and Time Series Momentum*.
   - DOI: https://doi.org/10.2139/ssrn.2891434
   - SSRN record: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2891434
