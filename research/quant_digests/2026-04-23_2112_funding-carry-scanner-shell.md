# Funding carry scanner shell：把正资金费率当成可筛选的 raw alpha，而不是“顺手看一下 APR”
- 时间：2026-04-23 21:12 UTC
- 类型：GitHub
- 主题类型：raw alpha
- 基础 alpha：positive funding carry（short perp / long spot，或反向低 funding pocket）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：carry / funding / basis / relative-value / stat-arb / cross-venue / risk / sizing
- 证据类型：工程经验 + 公开数据快检

## 1. 这次看了什么
看了一个新仓库 `vvonha/crypto-trading-tools`，它把 funding rate scanner、cross-venue hedging、market monitor 和 risk sizing 放在同一个工具箱里；同时用 Binance USDⓈ-M 公共 funding 数据做了一个最小快检。

## 2. 核心结论
- 这套东西的 base alpha 很清楚：**抓正资金费率 pocket，做 perp 空头 + 现货多头的 carry**。
- 它不是“只看 funding 值”的小抄，代码里已经把**扫描、监控、风控**放在一起了，说明可落地性比单点信号强。
- 我跑的 8 币快检里，**DOGE / ADA / XRP / AVAX / LINK** 近 30 个 funding 点大多偏正；**BTC / ETH** 仍偏负，说明 carry 机会是**分币种口袋化**，不是全市场常开。
- 当前 8 币当前 funding 也很分裂：BTC `-8.50% APR`、ETH `-5.25%`、SOL `-8.59%`；DOGE `+7.93%`、XRP `+4.09%`、ADA `+5.48%`、AVAX `+2.27%`。

## 3. 为什么和当前项目有关
对 `momentum` 来说，这不是纯“收益率面板”，而是一个能直接塞进素材池的**carry raw alpha 组件**：
- 适合做独立策略：`正 funding × 流动性门槛 × 风险仓位`
- 也适合做其他 alpha 的 overlay：比如只在 funding 口袋足够厚时才启用别的方向单
- 1m/3m/5m/15m 主要负责**child execution / hedge timing**，不是主信号本体

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / carry
- 基础 alpha：perp funding 收租（正 funding pocket）
- regime：高 funding、低冲击、可对冲时段
- filter / veto：最小 funding 阈值、成交额阈值、basis/premium 过大则 veto
- risk / sizing / execution overlay：半凯利/固定风险上限、maker-first、分批进场、到期前/费率回落前退出

## 4. 可复刻的最小实验
- 假设：**正 funding 且持续性更强的币种，做 short perp + long spot 的 carry，在扣成本后仍能保留正收益。**
- 可计算定义：`funding_apr = lastFundingRate * 3 * 365 * 100`；再加一个 `premium_pct` 过滤。
- 最小切口：Binance USDⓈ-M，8~20 个 liquid majors，`30d~90d` funding history，按 8h 费率滚动统计。
- 先看 2 个指标：**成本前后 APR**、**正 funding 持续率**（positive ratio / streak length）。

## 5. 风险与保留意见
- funding carry 很容易被手续费、滑点、资金占用和借币/保证金约束吃掉；APR 看起来漂亮，不代表净值漂亮。
- 如果正 funding 只是短暂脉冲，而不是持续 pocket，就会变成“追费率”而不是“收租”。
- 这类策略更像**可控的完整策略**，不是单根 K 线 alpha；1m/3m/5m/15m 只能帮执行，不该伪装成主信号。

## 6. 来源（尽量结构化）
- Source A（主来源，仓库）
  - Authors：vvonha
  - Year：2026（仓库活跃更新时间）
  - Title：crypto-trading-tools
  - Venue：GitHub repository
  - DOI：N/A
  - Readable URL：https://github.com/vvonha/crypto-trading-tools
  - Repo URL：https://github.com/vvonha/crypto-trading-tools
- Source B（辅助来源，仓库）
  - Authors：R1cK-ChaN
  - Year：2026（仓库活跃更新时间）
  - Title：crypto-funding-arbitrage
  - Venue：GitHub repository
  - DOI：N/A
  - Readable URL：https://github.com/R1cK-ChaN/crypto-funding-arbitrage
  - Repo URL：https://github.com/R1cK-ChaN/crypto-funding-arbitrage
- Source C（公开数据接口）
  - Authors / Provider：Binance USDⓈ-M API
  - Year：2026（本次抓取时间）
  - Title：premiumIndex / fundingRate endpoints
  - Venue：Binance public REST API
  - DOI：N/A
  - Readable URL：https://fapi.binance.com/fapi/v1/premiumIndex
  - Data URL：https://fapi.binance.com/fapi/v1/fundingRate
