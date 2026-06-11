# Polymarket dump hedge：YES+NO < 1 的补体错价，才是 base alpha

- 主题类型：raw alpha
- 基础 alpha：Polymarket 二元合约的补体错价（YES+NO 合价低于 1）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 一句话结论
这不是“预测方向”的题，而是**买入 YES + NO 的结构性套利**：当同一二元市场的两腿合计买价低于 $1.00 时，持有到结算可锁定面值回归收益；源码里还能直接看到 entry、early-exit、size、cooldown、Kelly 和 kill switch。

## 这篇东西的 base alpha 是什么？
**base alpha = 二元互补合约的定价不守恒。**

对 Polymarket 这类 binary market，YES 和 NO 在结算时总和必然等于 $1。若当前 order book 里两腿买价之和显著低于 1，买双腿本身就是一笔锁定利润的 relative-value / stat-arb。

这类 alpha 的核心不是方向判断，而是：
- 合价偏离是否足够大
- 还能不能在结算前安全退出
- 交易成本、滑点、手续费后是否仍为正

## 为什么它值得进素材池
它很适合 short-cycle desk，因为它天然就是一个**完整策略壳**，不需要再硬补方向模型：
- entry：`YES ask + NO ask <= threshold`
- exit：早退阈值或持有到结算
- sizing：固定 USDC 或 Kelly
- risk：单笔上限、并发上限、daily halt、kill switch
- cost：Polymarket CLOB 费率 + 滑点

这比“只有信号没有执行”的外部数据主题更适合先做最小闭环。

## 源码里最值钱的 3 个点
1. **2.7 秒 latency arb 不是主线唯一内容**，主线还有 dump hedge。
2. **dump hedge 不依赖 Binance**，只看 Polymarket 自身订单簿。
3. **风险层是完整的**：单笔仓位、并发仓位、日内止损、总回撤 kill switch、circuit breaker。

## 适合的短周期实验口径
虽然这是预测市场，不是传统 K 线 alpha，但它仍然能映射到短周期：
- `5m / 15m` market series
- 盘口级别的秒级更新
- 结构性价差机会通常是短命的

最小实验可以先做：
1. 抓取活跃 binary market 的 YES/NO 最优买价
2. 统计 `YES + NO` 的分布、持续时间、可成交深度
3. 加上手续费和保守滑点后，测 `net edge`
4. 只保留 `net edge > 0` 且剩余时间足够的机会

## 下一步怎么测
- 用 Polymarket CLOB 逐分钟/逐秒采样，记录 `YES ask`、`NO ask`、`spread`、`depth`、`seconds remaining`
- 计算：
  - `combined = yes + no`
  - `discount = 1 - combined`
  - `net_discount = discount - fees - slippage`
- 分桶测：
  - 5m vs 15m
  - market 年化/窗口剩余时间
  - 流动性高低
- 看三件事：
  - 机会密度
  - 可成交率
  - 净利润分布

## 来源
- Authors: genoshide
- Year: 2026
- Title: Polymarket Arbitrage Trading Bot — OpenClaw Edition
- Venue: GitHub
- DOI: N/A
- Readable URL: https://raw.githubusercontent.com/genoshide/polymarket-arbitrage-trading-bot/main/README.md
- Repo URL: https://github.com/genoshide/polymarket-arbitrage-trading-bot

## 备注
这篇更像**raw alpha + 完整执行壳**，不是纯 filter/regime/overlay。它可以直接作为后续复现与实盘素材池里的一个独立模块：先做纸面回测，再做小额 live paper，再看是否值得真仓。