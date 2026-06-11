# 别把 stat-arb 只做 pairs：2026 新仓库里 `PCA residual + signed k-NN clustering + cluster deviation` 是可独立复现的短周期 raw alpha 骨架
- 时间：2026-03-23 17:34 UTC
- 类型：GitHub 新仓库（含完整回测报告）+ 方法地基
- 主题类型：raw alpha
- 基础 alpha：同簇相对偏离（cluster-relative residual deviation）的均值回归
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/stat-arb/relative-value/cross-sectional/mean-reversion/pca/signed-graph/clustering/turnover/cost/crypto/1m/3m/5m/15m
- 证据类型：工程经验（开源 walk-forward 回测）

> 先回答 base alpha：这篇东西的核心不是“预测大盘方向”，而是**在市场中性前提下，做同簇资产相对偏离的回归交易**。

## 1. 这次看了什么
看的是 2026-01 新仓库 **Aroesler1/crypto_stat_arb**：把 token 收益先做 PCA 去市场因子，再构建 signed k-NN 相关图聚类（SPONGE/BNC/Signed Spectral），最后交易“簇内偏离回归”，并给了 walk-forward + 成本敏感性报告。

## 2. 核心结论
- 这不是 filter，而是可独立运行的 **raw alpha（cross-sectional stat-arb）**：入场、出场、仓位、成本都给了可执行骨架。  
- 仓库报告里最强配置是 **Cluster Deviation + SPONGE(k=3)**：Gross Sharpe 3.27，**break-even 54.2 bps**。  
- 在成本假设下仍有可用区间：**25 bps 时 Net Sharpe 1.76、年化 29.2%**；50 bps 时仍小幅为正（Net Sharpe 0.24）。  
- 组合暴露接近中性：ETH beta 约 0.02、PC1 beta 约 0.00，说明它主要吃的是相对价值偏离而非方向 Beta。  
- 一句话核心结论：**比“单对 pairs z-score”更可扩展的做法，是先做 residual + 聚类，再做簇内偏离回归。**
- 一句话证明方式：**作者用 365d train / 28d test 的 walk-forward 与成本阶梯（含 break-even bps）直接证明该骨架在成本下的生存区间。**

## 3. 为什么和当前项目有关
- 我们近期已经补了很多 trend / breakout / gate，本篇直接补齐 **raw alpha 素材池里的 stat-arb 横截面主线**。  
- 它天然适配短周期研发分层：signal（偏离）/ neutralization（中性化）/ execution（turnover cap）/ cost ladder（摩擦生存）。  
- 对 `1m/3m/5m/15m` 的意义：5m/15m 可先做稳健基线；1m/3m 可做高频版但必须先过成本与成交约束。

## 3.5 策略拆解（必填）
- 方向属性：横截面 + 相对价值 + 均值回归（市场中性）
- 基础 alpha：资产相对其簇合成收益的偏离 z-score 回归
- regime：横截面离散度高、但市场单边趋势不过热时更友好
- filter / veto：成交额门槛、最小历史长度、极端 funding/basis 拥挤 veto、重大事件 blackout
- risk / sizing / execution overlay：簇内与全组合双重中性化、目标毛杠杆上限、日换手上限、成本阶梯与 break-even 审核

## 4. 可复刻的最小实验（下一步怎么测）
**研究假设**：在 Binance 永续主流可交易池里，`residual + cluster deviation` 在 5m/15m 仍能产生成本后正向 Sharpe，并保持低市场暴露。  

**可计算定义（最小版）**：
1. Universe：按近 30d 成交额选 Top 40~80 永续，剔除稳定币映射资产。  
2. 每 4h 重拟合：用近 14d 的 5m 收益做 PCA（取 PC1）并 residualize。  
3. 在 residual 相关矩阵上建 signed k-NN 图（k=10），聚成 3~6 簇。  
4. 计算 token 对簇合成收益偏离，做 `lookback=20, zwin=60` 的 z-score。  
5. 入场：z < -2 做多、z > +2 做空；出场：|z| 回落到 0.5 或持仓超 24 bars。  
6. 组合约束：簇内中性 + 全组合中性，毛杠杆 1.5，上日换手 cap 15%。  

**最小回测切口**：
- 资产：Binance USDT-M perp Top 40（高流动先行）  
- 周期：先 15m（稳健）后 5m（增频）再 3m/1m（压力测试）  
- 样本：最近 9~12 个月，walk-forward（train 60d / test 14d）  

**先看 2 个关键指标**：
- Net Sharpe 与 break-even bps（先判断“活不活得下去”）
- Turnover 与 ETH/BTC beta（确认是不是在偷方向风险）

## 5. 风险与保留意见
- 该仓库主报告是日频口径，直接下放到 1m/3m 可能因冲击成本失真。  
- 聚类在短窗会漂移，簇稳定性不足会导致信号翻转频繁。  
- 低流动币在回测里容易“看起来可做、实盘做不满”；必须加成交占比与最小深度约束。  
- 该项目是单作者开源研究，仍需我们做独立 clean replication 才能升实盘候选。

## 6. 来源
- Alex Roesler. (2026). *crypto_stat_arb: Market-neutral crypto stat-arb research + backtest (signed graph clustering + PCA residualization + cluster-deviation signals).* GitHub Repository.  
  - Readable URL: `https://github.com/Aroesler1/crypto_stat_arb`  
  - Repo URL: `https://github.com/Aroesler1/crypto_stat_arb`
- Alex Roesler. (2026). *Stat-Arb Backtest: Final Report*（仓库内报告，含成本敏感性、break-even、beta 中性检验）。  
  - Readable URL: `https://raw.githubusercontent.com/Aroesler1/crypto_stat_arb/main/stat_arb/reporting/FINAL_REPORT.md`  
  - Repo URL: `https://github.com/Aroesler1/crypto_stat_arb`
