# 别把这份 spot-perp basis 仓只读成“0 交易失败案例”：对 short-cycle desk，更该先拆的是「funding percentile + z-score basis fade × stability admission」这条 raw alpha 壳
- 时间：2026-04-16 10:48 UTC
- 类型：GitHub
- 主题类型：raw alpha
- 基础 alpha：同标的 `spot-perp` 基差（basis）偏离的均值回归 + funding 方向筛选（carry-aware）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / relative-value / stat-arb / carry / funding / basis / mean-reversion / admission / risk
- 证据类型：工程经验（repo 自带规则与回测输出，需二次独立验算）

## 1. 这次看了什么
我这轮审计的是新仓库 `swingtradingtank/spot-perp-base-trading-strategy`（创建于 2026-02，最近更新 2026-04-07），重点看了 `README` 和 `spot_perp_basis_strategy.ipynb`。它不是只讲“基差会回归”，而是把 `entry/exit/risk/cost/walk-forward` 全链路都写出来了。

## 2. 核心结论
- 这份仓库最值钱的点，不是“赚了多少钱”，而是把**同一套 alpha**拆成三种 admission 强度（strict/moderate/research）并直接显示“可交易机会密度”如何塌陷。
- repo 报告里，`research` 模式（宽松准入）在 2022–2024、18 对、1H/15M/30M 合计给出 **15,973 笔、$8,306.06、平均 Sharpe 0.24**；但 `strict/moderate` 都是 **0 笔交易**。
- 成本假设并不低：每腿手续费 0.10% + 滑点 0.05%，即约 **0.30% round-trip**；这让它更像“可部署性筛选实验”，不是只看毛收益的学术演示。
- 一句话核心结论：**很多“paper-mode 可见 alpha”会在稳定性/可部署过滤后直接变成无交易，不是参数问题，是 admission 结构问题。**
- 一句话证明方式：**同一信号、同一数据窗口，只改变稳定性门槛（ADF/Hurst/half-life/beta + 风控阻断），结果从 15973 笔变成 0 笔。**

## 3. 为什么和当前项目有关
这和我们现在的 short-cycle 目标高度一致：我们不是缺“又一个 basis 故事”，而是缺一块可复用的 **raw alpha admission layer**。这份仓库给了一个很清楚的工程骨架：
- raw alpha 本体：`spot-perp spread z-score` 回归
- carry 信息：`funding percentile` 作为方向确认
- 可部署约束：稳定性门槛 + 风控 blocker

对当前 desk 的直接价值：可以把它作为 `pairs / basis / funding` 家族的统一准入模板，不再靠主观“这段看起来能跑”。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / 统计套利 / carry-aware mean reversion
- 基础 alpha：`basis_t = log(perp_t) - log(spot_t)` 的极端偏离回归（z-score fade）
- regime：波动分层后动态调整阈值（high/normal/low vol 下不同 z_entry/z_exit）
- filter / veto：funding 分位（>75% 或 <25%）+ ADF/Hurst/half-life/beta 稳定性筛选
- risk / sizing / execution overlay：单笔/总敞口上限、10% DD 限制、3% stop、funding circuit breaker、交易成本显式计入

## 4. 可复刻的最小实验
**研究假设**：在 crypto `15m`（并下钻到 `5m` 执行）里，`basis z-score` 的回归只有在“funding 与方向一致 + 稳定性过线”时才有成本后生存空间。  

**可计算定义（最小版）**：
1. `basis_t = log(perp_t) - log(spot_t)`，滚动窗口做 `z_t`
2. 入场：
   - Short basis：`z_t > 2.0` 且 `funding_pct_30d > 75%`
   - Long basis：`z_t < -2.0` 且 `funding_pct_30d < 25%`
3. 出场：`|z_t| < 0.5` 或 `pnl < -3%` 或 `max_hold` 到期
4. 成本：每腿 10bp 手续费 + 5bp 滑点（round-trip 30bp）

**最小回测切口**：
- 资产：BTC/ETH/SOL/BNB/ADA（先 5 对）
- 周期：信号 15m，执行对照 5m（可再补 3m）
- 样本：最近 12 个月 walk-forward（9m train + 3m test）

**先看 2 个指标**：
- 成本后 Sharpe / PnL（必须）
- `trade starvation ratio`（过滤后交易数衰减比例，衡量“可部署性”）

## 5. 风险与保留意见
- 证据主要来自 repo 自述与 notebook 输出，当前还不是独立第三方复核。
- `strict/moderate=0 trade` 说明参数可能对币圈短周期过严；不代表 alpha 不存在，但代表“原门槛不可直接抄”。
- funding 分位若处理不当容易引入对齐偏差（8h 数据映射到 15m/5m 时要防 look-ahead）。
- 若执行层用 taker-only，很多边际优势会被 30bp+ 成本吃掉，需要 maker/taker 混合或更细 execution veto。

## 6. 来源
- Authors：Tancredi Rosch
- Year：2026
- Title：*Spot-Perpetual Basis Trading Strategy*
- Venue：GitHub repository
- DOI：N/A（仓库材料，无 DOI）
- Readable URL：https://github.com/swingtradingtank/spot-perp-base-trading-strategy
- Repo URL：https://github.com/swingtradingtank/spot-perp-base-trading-strategy
- 关键源码/材料：`README`, `spot_perp_basis_strategy.ipynb`
- （仓内引用）Gatev et al. (2006), Do & Faff (2010), Avellaneda & Lee (2010), Vidyamurthy (2004)
