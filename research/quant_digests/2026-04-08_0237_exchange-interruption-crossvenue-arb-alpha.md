# 别把交易所中断只读成运维事故：对 short-cycle desk，更该先测的是「venue-freeze price gap × re-link close」

- 时间：2026-04-08 02:37 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：单一交易所因延迟 / 宕机 / DDoS 出现**报价冻结**时，同一标的会相对健康交易所产生可交易的 cross-venue price gap；待该 venue 重新跟上全市场价格后，价差回补。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（更适合先做 `quote staleness / heartbeat gap` 代理版）
- 主题标签：raw-alpha / relative-value / stat-arb / cross-venue / exchange-interruption / outage / stale-quote / price-gap / event-driven / 1m / 3m / 5m / 15m
- 证据类型：论文证据

## 1. 这次看了什么
这次主看 **Andrew Morin, Tyler Moore (2023), _How Cryptocurrency Exchange Interruptions Create Arbitrage Opportunities_**。这篇东西最值得 desk 抄的，不是“交易所会掉线”这个常识，而是把它明确翻成一条可交易的 raw alpha：**某一 venue 的价格在中断时更容易卡住，其他 venue 继续走，于是同币种跨所价差会突然拉大；等中断缓解后，这个价差往往向全市场重新收口。**

## 2. 核心结论
- 论文研究 **Bitfinex 2015-04-01 到 2022-10-31 的 41 次中断事件**，把事件分成 `delay / DDoS / outage`，并用 **5 分钟** 粒度比较 Bitfinex 与 CoinMarketCap 聚合价。
- 作者把“显著套利机会”定义成：Bitfinex 与全市场价格差**超过交易费+提现费形成的 arbitrage band**。结果是：**中断窗口里 68.5%** 的时间伴随显著套利机会，非事件窗口只有 **46.8%**；卡方统计量 **27.49**，`p = 1.58e-7`。
- 更值钱的是持续时间：中断期间的套利窗口平均可持续 **109.0 分钟**，而非事件期约 **82.1 分钟**；按类型拆开，**delay 94.5 分钟、outage 81.4 分钟、DDoS 中位数 40 分钟（非事件中位数 20 分钟）**，说明这不是只活几秒的 HFT 幻觉。
- 作者按每个 5 分钟成交量乘价格差估算潜在利润，给出**中位事件利润约 64,821 美元**、样本总潜在利润约 **105,807,735 美元**。翻成人话：**运营故障不是噪音，而是会把同币跨所价差直接拽到“能下单”的级别。**

## 3. 为什么和当前项目有关
这条线和当前 desk 的关系非常直接：它不是解释型 overlay，而是一条**事件驱动的 relative-value raw alpha**。我们不用照抄“等交易所真的挂掉”，更适合拿来做 short-cycle 版本：
- 用 **websocket heartbeat gap / order book staleness / quote age** 当 `interruption proxy`
- 用健康 venue 的 mid / microprice 当 `fair reference`
- 在 `1m / 3m / 5m / 15m` 上测 **gap 是否在 proxy 解除后回补**

换句话说，这篇论文提供的不是“故障新闻解读”，而是一个很像 production admission layer 的主信号：**先识别哪边的价格“卡住了”，再做 re-link close。**

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / stat-arb
- 基础 alpha：`stale_venue_mid - healthy_reference_mid` 的异常偏离会在 venue 恢复同步后回补
- regime：单 venue 出现 `heartbeat gap / quote staleness / API error spike` 的运维异常窗口
- filter / veto：只做高流动性同标的跨所；若两边都异常、或健康腿 depth 不足，则 veto
- risk / sizing / execution overlay：按两边最小可成交深度定仓；优先 `maker on stale side + taker on healthy side` 或纯 taker 双腿；异常持续超时、单腿未成交、参考价反向继续扩张则强平/降仓

## 4. 可复刻的最小实验
- **研究假设**：当某交易所出现报价陈旧/链路异常时，同标的跨所价差会显著扩大，并在异常缓解后于 `1~12` 根短周期 bar 内回补。
- **可计算定义**：
  - `stale_flag = quote_age_sec > q_th` 或 `heartbeat_gap_sec > h_th`
  - `gap_z = (mid_stale - mid_ref) / rolling_sigma(spread)`
  - 入场：`stale_flag=1` 且 `|gap_z| > z_in` 且 `edge > fee + slippage + borrow_buffer`
  - 出场：`|gap_z| < z_out`、`stale_flag` 解除、或 `max_hold` 到时
- **最小回测切口**：BTC/ETH/SOL 同标的跨 `Binance / OKX / Bybit`，先做 `1m` 事件条，再聚合到 `3m/5m/15m`；先不碰小币。
- **先看 2 个指标**：`post-cost spread capture`、`fill asymmetry / orphan-leg ratio`。这条线如果单腿残留太多，再高 Sharpe 都是假象。

## 5. 风险与保留意见
- 论文样本核心是 **Bitfinex vs CoinMarketCap**，不是现代多 venue、低延迟、统一手续费的 perp 世界，直接搬运会高估收益。
- 真 outage 时最麻烦的不是“信号对不对”，而是**坏 venue 那条腿是否还能成交/撤单**；因此 production 更该先测 `stale quote proxy`，而不是等真宕机。
- 这条 alpha 天然稀疏，适合作为**事件型 raw alpha 池补充**，不适合作为全天候主策略。
- 一旦健康 venue 也同步进入剧烈单边，价差可能是“信息领先”不是“冻结失真”，因此必须加 `reference breadth / depth sanity` 过滤。

## 6. 来源
1. **Morin, A., & Moore, T. (2023). _How Cryptocurrency Exchange Interruptions Create Arbitrage Opportunities_. 2023 IEEE European Symposium on Security and Privacy Workshops.**
   - DOI: `https://doi.org/10.1109/EuroSPW59978.2023.00028`
   - Readable URL: `https://ieeexplore.ieee.org/document/10190776`
   - PDF: `https://tylermoore.utulsa.edu/wacco23arbitrage.pdf`
2. **论文内关键口径**：Bitfinex 中断事件 `41` 次；事件窗口显著套利占比 `68.5%` vs 非事件 `46.8%`；平均套利持续 `109.0` 分钟；中位事件潜在利润约 `$64,821`。
