# 别把这篇全球 ITSM 论文继续只读成“单市场开盘效应”：对 desk 更该先测的是「leader 首窗方向 → 多资产篮子尾窗同向」raw alpha

- 时间：2026-03-28 15:45 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：leader 资产/主市场在首个锚点窗口里的方向，能预测一组相关资产在同一 session 尾窗继续同向
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-market/lead-lag/basket/intraday/time-series-momentum/diversification/breadth/btc-eth-alt/5m/15m/paper/public-data/cost
- 证据类型：论文证据（accepted PDF 全文）

## 1. 这次看了什么

主看 **Zeming Li, Athanasios Sakkas, Andrew Urquhart (2022), _Intraday time series momentum: Global evidence and links to market characteristics_, Journal of Financial Markets**。和上午那篇更偏“单资产锚点续动 + micro gate”不同，这次真正值得 desk 拿走的不是再讲一次开盘/收盘，而是它的 **篮子化、跨市场、leader-driven** 读法。

## 2. 核心结论

- 论文在 **16 个发达市场** 上发现：**12/16** 的市场里，首个 30 分钟收益能正向预测最后 30 分钟收益。
- 但更值钱的是：全球 commonality 并不强，**PC1 只解释 27.7%** 的 ITSM 方差；按地区分组后，PC1 升到 **40.3%~63.1%**。翻成人话：有共性，但没强到把所有市场压成一个因子，**因此篮子化还有分散与增益空间**。
- 用 **US 首个半小时方向** 去交易各国尾盘，是三类 GITSM 里最强的一支：等权版本年化 **Sharpe 1.77**；均值-方差版本年化收益 **6.75%**，对单国 ITSM 的 spanning alpha 约 **5.63%~7.19%**。
- 加入 US 首窗收益后，跨国回归的 adjusted R² 在 **除 1 国外全部提高**，并且论文在 **10/16** 市场拒绝“US 没有跨市场预测力”。

一句话核心结论：

> **别只盯单币自己第一段涨跌，更该先测“主导资产先定方向，相关资产篮子在尾段跟随”的 basket raw alpha。**

一句话证明方式：

> **作者用 16 国 1 分钟股指数据，直接做首窗→尾窗回归、跨市场回归、组合构建和 spanning alpha 检验，证明 leader-driven 篮子版比单市场版更强。**

## 3. 为什么和当前项目有关

这条线和 desk 当前主线是直接相连的，因为它补的是 **raw alpha 素材池**，不是纯 filter。

我们现在已经有不少：
- 单币趋势 / breakout / session-anchor 续动
- BTC→ALT lead-lag 事件 pocket
- 一些横截面排序与 pairs 框架

但还缺一个更中间层、又容易快速验证的骨架：

> **用 leader 的早段信号，去驱动一个相关资产篮子的尾段交易。**

这比纯单币更稳一些，比复杂 stat-arb 更快落地，也天然适合 `5m / 15m`。

## 3.5 策略拆解（必填）

- 方向属性：顺势 + cross-market lead-lag + basket
- 基础 alpha：leader 首窗方向预测 laggard basket 尾窗同向
- regime：leader 与篮子 breadth 同向、且 session 内相关性不塌
- filter / veto：首窗绝对涨跌幅过小不做；breadth < 60% 不做；成本后 edge 不够不做
- risk / sizing / execution overlay：篮子等权或逆波动；单币权重上限；统一时间退出；先按 `4~6 bps` round-trip 做摩擦压力测试

## 4. 可复刻的最小实验

**研究假设**：在 crypto 的真实锚点 session 里，`BTC` 或 `BTC+ETH` 的首个 `15m` 方向，可预测 alt 篮子最后 `15m` 的同向收益。

**可计算定义**：
- session 先试 `00:00 / 08:00 / 16:00 / 13:30 UTC`
- leader 信号：`sign(r_leader_first_15m)`
- basket：Top 8~12 流动性 USDT perp（先去掉 BTC/ETH 本身）
- breadth filter：首窗内同向资产占比 ≥ 60%
- entry：首窗结束后下一根 `5m` 开盘入场
- exit：session 最后 `15m` 收盘前平仓
- sizing：篮子等权；或按过去 7~14 天 session 尾窗波动做逆波动

**最小回测切口**：
- 资产：Binance USDⓈ-M perpetual，top 8~12 liquid alts
- 周期：先 `5m / 15m`
- 样本：最近 180~365 天
- 成本：先统一扣 `4 bps`，再做 `6 bps` stress

**最先看 2 个指标**：
1. 成本后的平均每次收益 / hit rate
2. leader-only 单币交易 vs leader-driven 篮子交易的 Sharpe / 稳定性差异

## 5. 风险与保留意见

- 论文原场景是股票指数，不是 24/7 crypto；这里迁移的是“leader 首窗 → basket 尾窗”的结构，不是机械照抄开盘/收盘。
- 如果 crypto 里 common shock 太强，篮子可能只是 beta 放大，不是真正的 lead-lag，需要和“直接做 BTC”对照。
- 若 breadth filter 太宽，会退化成追 beta；太窄又会让 trade count 不够。
- 这条线最怕费用和尾窗流动性恶化，所以第一轮就必须把 `4~6 bps` 成本、尾窗滑点、币种容量一起压测。

## 6. 下一步怎么测

先别做太复杂：

1. 只测 `BTC`、`ETH`、`BTC+ETH 同向` 三种 leader 定义；
2. 只测 `13:30 UTC` 和 `08:00 / 16:00 UTC` 三类锚点；
3. 篮子先固定 top 10 liquid alts；
4. 先比三组：
   - 直接做 BTC 尾窗
   - leader-driven 等权 alt 篮子
   - leader-driven 逆波动 alt 篮子
5. 若篮子版在成本后明显优于单币版，再加第二层：breadth 分层 + low-liquidity 分层。

如果这一步成立，它就能进入一个很实用的位置：

> **不是替代单币动量，而是补一个“leader → basket”层的完整 raw alpha。**

## 7. 来源

- **Li, Z., Sakkas, A., & Urquhart, A. (2022).** *Intraday time series momentum: Global evidence and links to market characteristics*. *Journal of Financial Markets*, 57, 100619.
  - DOI: `https://doi.org/10.1016/j.finmar.2021.100619`
  - Readable URL: `https://centaur.reading.ac.uk/95566/1/Accepted-Version.pdf`
  - Repo URL: 未找到官方公开 repo

- **Gao, L., Han, Y., Li, S. Z., & Zhou, G. (2018).** *Market intraday momentum*. *Journal of Financial Economics*, 129(2), 394-414.
  - DOI: `https://doi.org/10.1016/j.jfineco.2018.05.009`
  - Readable URL: `https://doi.org/10.1016/j.jfineco.2018.05.009`
  - Repo URL: 未找到官方公开 repo
