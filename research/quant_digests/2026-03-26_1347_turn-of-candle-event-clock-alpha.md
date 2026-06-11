# 别把 15m 边界分钟当默认顺风点：这篇 2023 Heliyon 论文更该先测的是「turn-of-the-candle event clock」raw alpha，但 2025Q4~2026Q1 Binance 映射已转负
- 时间：2026-03-26 13:47 UTC
- 类型：论文 + Binance 公共 `1m` 最小 transfer check
- 主题类型：raw alpha
- 基础 alpha：BTC 在每个 `15m` K 线切换分钟（`00/15/30/45`）出现可交易的单资产事件时钟 drift
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/event-clock/intraday/seasonality/btc/single-asset/1m/3m/5m/15m/binance/paper/external-data
- 证据类型：论文证据 + 公共数据最小快检

## 1. 这次看了什么
看的是 Savva Shanaev、Mikhail Vasenin、Roman Stepanov 2023 年 Heliyon 论文《Turn-of-the-candle effect in bitcoin returns》，并用 Binance Spot / Futures 公共 `1m` K 线对 `2026-01-25~2026-03-26` 与 `2025-09-27~2026-03-26` 做了最小迁移快检。

## 2. 核心结论
- 论文的 **base alpha 很清楚**：不是趋势、不是 breakout，而是 **BTC 在每个 `15m` K 线切换分钟有系统性正漂移**。作者把 `00/15/30/45` 分钟定义为事件分钟，其他分钟做对照。
- 原论文用 7 家交易所、`1m` 数据、样本截止 `2021-12-31`。2021 年各交易所该效应都很强，Binance 的 turn-minute OLS 系数是 **`+0.9008 bps/min`**；全样本平均图上，turn-minute 平均收益约 **`+0.58 bps/min`**，而其他分钟平均是负的。
- 这不是只靠极端点撑起来：2021 条件中位数回归里，Binance 仍有 **`+0.3666 bps`**；Bitfinex 的 TGARCH-M 鲁棒性检验里，turn-minute 系数大致落在 **`+0.22 ~ +0.49 bps`**。
- 论文给了完整策略骨架：只在 `00/15/30/45` 分钟持有 BTC。按 Bitfinex 2021 费用+点差模拟，**$5,000 初始资金年化净收益 `74.18%`**，高于 buy-and-hold 的 **`60.27%`**；若按作者的 PSR 评估，策略 Sharpe **`4.96`**，显著高于 buy-and-hold 的 **`0.77`**。
- 但 **当前 Binance 迁移先判负**。我用公共 `1m` 数据快检：最近 `60d`，Binance Spot turn-minute 平均收益 **`-0.0720 bps`**，非事件分钟 **`-0.0213 bps`**；Binance Perp 分别是 **`-0.0784 bps`** 与 **`-0.0205 bps`**。放大到最近 `180d` 也一样：Spot **`-0.0557 bps` vs -0.0123 bps`**，Perp **`-0.0664 bps vs -0.0110 bps`**。也就是说，这个 event clock 在我们当前目标 venue 上不但没复现，短期还出现了**反向 drift**。

## 3. 为什么和当前项目有关
这篇东西对当前 desk 的价值，不是让我们无脑把「每逢 `15m` 切线就做多 BTC」塞进素材池，而是提醒：**event-time raw alpha 本身可以是独立信号，不一定附着在 breakout / momentum / retest 上。**

更重要的是，它非常适合服务 `1m / 3m / 5m / 15m` 研发：
- `1m/3m` 上可以直接做事件分钟 drift / fade；
- `5m/15m` 上可以把它降级成 **execution scheduler**：如果 rolling edge 为负，就避免在新 `15m` K 线刚切换时追价；
- 对 BTC→alt 的 lead-lag、microstructure、事件驱动策略，也能作为统一的 **boundary-time veto / throttle** 模块。

## 3.5 策略拆解（必填）
- 方向属性：单资产 / 时间序列 / 事件时钟
- 基础 alpha：`15m` 边界分钟的 BTC 单分钟漂移
- regime：论文里效应在 `2020H2` 后出现；当前 Binance 最近 `60d/180d` 已明显衰减并转负
- filter / veto：必须加 rolling `30d~60d` event-edge 为正的开关；若边界分钟 edge 转负，则不能把它当 long alpha
- risk / sizing / execution overlay：极端依赖低成本、低延迟和精确分钟切换；更像低摩擦 venue / maker-friendly venue 的超短事件模块

## 4. 可复刻的最小实验
- 研究假设：`15m` 边界分钟的 drift 不是稳定常数，而是 **venue- and regime-specific**；在当前 Binance 上，它更可能是反向执行风险而不是正向 alpha。
- 一个可计算定义：
  - `event_minute = minute in {0,15,30,45}`
  - `edge = mean(ret_1m | event_minute) - mean(ret_1m | non_event_minute)`
  - 用 rolling `30d/60d` 追踪 edge 的符号和稳定性。
- 最小回测切口：
  1. `BTCUSDT` Spot / Perp，`1m`，最近 `180d`；
  2. 再做 `3m` 变体：只持有每个新 `15m` candle 的前 `3m`；
  3. 若 `1m` 为负、`3m` 仍为负，则直接把该主题从“raw alpha 候选”降级成“execution veto”。
- 最该先看 2 个指标：
  1. `edge` 的 rolling 均值与 t-stat；
  2. 扣掉 taker round-trip 后的单次交易期望（当前快检：Spot 约 **`-2.06 bps/trade`**，Perp 约 **`-4.07 bps/trade`**，均按最近 `180d`）。

## 5. 风险与保留意见
- 这是非常典型的 **adaptive-market** 异象：论文自己也强调它在 `2020H2` 才明显出现，所以失效并不意外。
- 论文盈利样本主要落在 Bitfinex 2021，不能直接外推到 2026 Binance，更不能直接外推到 perp。
- 该信号天然高换手、强依赖 fee tier / spread / latency；对 taker 执行极不友好。
- 所以它目前更像一个 **event-clock library entry**：告诉我们要系统检查 K 线边界时间，而不是说明“BTC 每到 `15m` 切线都该做多”。

## 6. 来源
- Shanaev, S., Vasenin, M., & Stepanov, R. S. (2023). *Turn-of-the-candle effect in bitcoin returns*. Heliyon.
- DOI: `10.1016/j.heliyon.2023.e14236`
- Readable URL: `https://pmc.ncbi.nlm.nih.gov/articles/PMC10015199/`
- DOI URL: `https://doi.org/10.1016/j.heliyon.2023.e14236`
- Binance Spot API docs: `https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data`
- Binance Futures API docs: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`
- Local artifact: `reports/artifacts/literature/turn_of_candle_binance_transfer_2026-03-26.json`
