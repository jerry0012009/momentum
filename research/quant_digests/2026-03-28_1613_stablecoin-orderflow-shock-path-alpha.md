# 别把 stablecoin 市场只当流动性通道：这篇 2023 Digital Finance 更该先测的是「signed order-flow shock → 1 bar 延续 / 5m inventory fade」raw alpha

- 时间：2026-03-28 16:13 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：BTC/ETH 对 USDT 的标准化 signed order-flow shock（主动买量 − 主动卖量）会先推着价格做超短续动；当 order flow 确认消失后，`5m` 级别更容易出现 inventory / contrarian 式回吐
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/microstructure/order-flow/signed-volume/taker-imbalance/stablecoin/crypto-crypto/btc-usdt/eth-usdt/eth-btc/follow-through/inventory-fade/1m/3m/5m/15m/paper/public-data/cost
- 证据类型：2023 Digital Finance 开放获取全文 PDF + 本地表格抽取 + Springer article page

## 1. 这次看了什么

主看 **Emilio Barucci, Giancarlo Giuffra Moncayo, Daniele Marazzina (2023), _Market impact and efficiency in cryptoassets markets_, Digital Finance**。

这篇 paper 表面上写的是 market impact / efficiency，但对当前 desk 更值钱的，不是再讲一次“stablecoin 很重要”，而是把它拆成一个能直接测的 **microstructure raw alpha**：

> **不要先去盯 BTC-USD 这种法币腿；更该先盯 `BTC-USDT / ETH-USDT / ETH-BTC` 里的 signed order-flow shock，看它在超短窗口里如何先延续、再回吐。**

## 2. 核心结论

### 2.1 论文真正给 desk 的，不是抽象效率结论，而是一个清楚的价格路径骨架

作者把市场分成两类：

- **crypto-crypto / stablecoin 腿**：`BTC-USDT`、`ETH-USDT`、`ETH-BTC`
- **crypto-USD 腿**：`BTC-USD`、`ETH-USD`、`USDT-USD`

然后用 **tick-by-tick Kaiko** 数据，聚合成 **1 秒价格、1 分钟收益、1 分钟 signed volume OF**，检查两件事：

1. **当下 OF 对当下收益的冲击有多强**
2. **滞后 OF / 滞后收益，对后续路径还有没有解释力**

最值得拿走的结论是：

- **crypto-crypto 腿的 contemporaneous impact 明显更强**；
- **超短窗口里先是顺着 OF 冲击走**；
- **再往后，尤其到 `5m+`，更容易出现 inventory-stabilization / contrarian 式回吐。**

这就不是“解释市场结构”而已，而是已经足够改写成一个 **事件驱动 alpha path**。

### 2.2 几个最关键的数字

样本本身不小：

- **样本期**：`2019-04-01 ~ 2020-10-31`
- **数据源**：Kaiko tick-by-tick
- **市场**：6 个 pair、21 家交易所
- **1 分钟样本量**：**833,760**

最重要的表是 contemporaneous OF → return 的回归（Table 4）。

在 **1m** 上，`OrderFlow_t` 对 `return_t` 的系数：

- `BTC-USDT`：**0.4533**
- `ETH-USDT`：**0.4966**
- `ETH-BTC`：**0.2813**
- `BTC-USD`：**0.1274**
- `ETH-USD`：**0.0875**
- `USDT-USD`：基本不显著

同一个表里，回归解释度也差很大：

- `BTC-USDT` 的 `R²`：**20.55%**
- `ETH-USDT` 的 `R²`：**24.67%**
- `ETH-BTC` 的 `R²`：**7.91%**
- `BTC-USD` 的 `R²`：**1.62%**
- `ETH-USD` 的 `R²`：**0.77%**

翻成人话：

> **真正“order flow 一打进来，价格立刻有像样反应”的，不是法币腿，而是 stablecoin / crypto-crypto 腿。**

### 2.3 这条路径不是只有“冲一下就完”，后面还有可交易的第二段

Table 5 看的是 `return_t` 对 `return_{t-1}` 和 `OF_{t-1}` 的关系。

先看 **1m 的滞后 OF**，在 crypto-crypto 腿上仍是正的：

- `BTC-USDT`：**0.0093**
- `ETH-USDT`：**0.0099**
- `ETH-BTC`：**0.0052**

这意味着：

> **大的 OF shock，不只是同分钟推价；到下一分钟，仍留有一点同向 follow-through。**

但再往后看滞后收益，路径开始变味：

- `BTC-USDT` 的 `return_{t-1}`：
  - `1m`：**+0.0080**
  - `5m`：**-0.0210**
  - `1h`：**-0.0340**
  - `1d`：**-0.1407**
- `ETH-USDT` 的 `return_{t-1}`：
  - `1m`：约 **0**
  - `5m`：**-0.0143**
  - `10m`：**-0.0092**
  - `1h`：**-0.0250**

这正是 desk 最该偷的结构：

- **第一段**：`1m` shock 先有 continuation
- **第二段**：确认衰减后，`5m+` 更容易出现 inventory fade / contrarian 回吐

也就是说，这篇 paper 给的不是单点信号，而是一个 **path-dependent alpha**。

### 2.4 order flow 本身也有持续性，但 crypto-crypto 和 USD 腿的“性格”不一样

Table 3 / Table 11 里，OF 的自相关也很关键。

在 `5m` 上，`OF_{t-1}` 系数：

- `BTC-USDT`：**0.1959**
- `ETH-USDT`：**0.2111**
- `ETH-BTC`：**0.1289**
- `BTC-USD`：**0.1960**
- `ETH-USD`：**0.1907**

但到 **1 day**，差异就拉开：

- `BTC-USDT`：**0.3312**
- `ETH-USDT`：**0.4416**
- `ETH-BTC`：**0.8615**
- `BTC-USD`：**0.0076**
- `ETH-USD`：**0.0751**

作者把这读成：

- crypto-crypto 腿里有更像 **inventory target / contrarian** 的交易者
- USD 腿里更像 **herding**，但 OF 对价格本身不太“有信息”

对我们来说，重点不是复述行为金融，而是策略含义：

> **如果你要在短周期里跟踪“谁真在推动价格”，先看 stablecoin / crypto-crypto 的 signed flow，不要先看法币腿。**

### 2.5 visible arbitrage 很多，但 USDT 腿扣费后并不美

这篇 paper 还给了一个很好的“别想当然”提醒。

单 pair 跨所 arbitrage（Table 6）：

- `BTC-USDT`：
  - arbitrage opportunity 秒占比 **20.84%**
  - 平均 spread **4.73 bps**
  - **net profits = 0**
- `ETH-USDT`：
  - 秒占比 **13.14%**
  - 平均 spread **4.64 bps**
  - **net profits = 0**
- `BTC-USD`：
  - 秒占比 **2.04%**
  - 平均 spread **26.05 bps**
  - **net profits ≈ 665,464 USD**
- `ETH-USD`：
  - 秒占比 **0.47%**
  - 平均 spread **41.75 bps**
  - **net profits ≈ 293,534 USD**

这对 desk 的提醒很直接：

> **stablecoin 腿更适合拿来读“价格被谁推动、冲击怎么走”；但别把肉眼可见的小 spread 当送钱。alpha 应该做流向冲击路径，不是做纸面无摩擦跨所套利。**

一句话核心结论：

> **对短周期 crypto desk，更值得先测的不是 BTC-USD 的慢反应，而是 `BTC/ETH-USDT` 的 signed order-flow shock：先抓 1 bar follow-through，再测 5m 级别的 inventory fade。**

一句话证明方式：

> **作者用 2019–2020 年 Kaiko tick 数据，对 6 个 pair 做 OF→return、lagged OF→return、autocorrelation 和 arbitrage 回归/统计，明确展示了 stablecoin / crypto-crypto 腿才是价格形成主战场。**

## 3. 为什么和当前项目有关

这轮我认为它值得进 digest，不是因为“市场微结构很重要”这种空话，而是因为它正好补了当前素材池里一块还不够系统的东西：

- 我们已经有不少 **return shock / breakout / basket lead-lag / Hawkes imbalance**
- 但还缺一条更朴素、公开数据也能先做的：
  - **signed taker flow shock path alpha**

它的好处是：

1. **base alpha 很清楚**：不是 filter，不是 overlay，就是 OF shock 路径
2. **数据公开可拿**：Binance / OKX / Bybit 的 taker buy/sell volume、agg trades 都能做 proxy
3. **能拆成两段**：
   - `1m/3m` 的 follow-through
   - `5m/15m` 的 delayed fade / veto
4. **还能服务别的 alpha**：以后即使单独策略不强，这套 OF state 也能反哺 breakout / continuation admission

但这轮我不把它写成 gate，原因很简单：

> **它首先就是一条 raw alpha path；只有做完 first verdict 之后，才考虑把它降级成 shared state。**

## 3.5 策略拆解（必填）

- 方向属性：microstructure / event-driven / same-asset 短窗路径 alpha
- 基础 alpha：`BTCUSDT` / `ETHUSDT` 的 standardized signed order-flow shock 先预测下一小段同向延续；若第二段 OF 不再确认，后续更容易出现回吐
- regime：只在 major coin 流动性够深、成交活跃、spread 正常时开启；优先 USDT perp / spot 主市场
- filter / veto：`|OF_z|` 过小不做；事件前后（如大宏观分钟）先 veto；若 funding 结算或异常跳价导致 bar 不可解释，先剔除
- risk / sizing / execution overlay：单次风险固定；先做 BTC/ETH 单资产；maker 优先、taker 兜底；默认先按 round-trip `4~6 bps` 压测

## 4. 可复刻的最小实验

### 4.1 数据源与公开性

**最小可复现实验数据：公开可得。**

- **价格 / 成交**：Binance USDⓈ-M Perpetual 或 Binance Spot 公开成交 / aggTrade / kline
- **可计算 proxy**：
  - taker buy quote volume
  - total quote volume
  - `signed_volume = taker_buy_quote - (total_quote - taker_buy_quote)`
- **更新频率**：秒级 / 分钟级
- **映射周期**：
  - 主实验：`1m / 3m`
  - transfer：`5m / 15m`

这条线天然更偏 **更快高强度 alpha**，所以先从 `1m/3m` 起步是合理的；若成立，再转成 `5m/15m` 的 trigger / fade 版本。

### 4.2 先测最朴素的两段策略

#### A. Follow-through leg（主实验）

**信号定义**：

- `of_z_t = zscore(signed_volume_t / total_volume_t)`，滚动窗口先试 `240~480` 个 `1m` bar
- 触发条件：
  - `|of_z_t| >= 2.0`
  - `sign(ret_1m_t) == sign(of_z_t)`
  - 当前分钟成交额进入过去 `N` 分钟前 `60%~80%` 分位，避免假流量

**交易规则**：

- entry：当前 `1m` bar 结束，下一分钟开盘按 `sign(of_z_t)` 入场
- exit：持有 `1~3` 个 `1m` bar；或聚合成下一根 `3m` bar 收盘退出
- sizing：先固定 notional；第二版再做 inverse-vol
- risk：单次止损先试 `0.6~0.8 x` 近 20 bar `1m ATR`
- cost：先扣 round-trip `4 bps`，再做 `6 bps` stress

#### B. Inventory fade leg（transfer 实验）

**信号定义**：

- 先发生 A 类大 OF shock
- 但后续 `1~2` 个 `1m` bar 的 `of_z` 快速回落到 `|0.5|` 以下，或方向翻转
- 同时首个 `5m` 聚合收益已进入过去 20 天同 slot 前 `90%` 分位

**交易规则**：

- entry：第一个 `5m` 冲击窗结束后，若 OF 不再确认，则反向入场
- exit：持有 `1` 个 `5m` bar，必要时延长到 `3` 个 `5m` bar（即 `15m`）
- sizing：fade leg 仓位 <= continuation leg 的 `50%~70%`
- veto：若 BTC 与 ETH 两个 major 同时继续同向大 OF，不做 fade

### 4.3 第一轮先看哪些指标

先别一上来卷 Sharpe，先看 5 个最诚实的数：

1. 成本后 average markout（`1m / 3m / 5m / 15m`）
2. hit rate
3. 尾部损失（shock 反向继续扩散时的 worst decile）
4. `BTCUSDT` 与 `ETHUSDT` 的可迁移性
5. follow-through leg 与 fade leg 是否互补，而不是互相打脸

## 5. 风险与保留意见

- 论文样本是 **2019–2020 现货 / stablecoin 市场**，不是 2026 perp 主导结构；所以我们迁移的是 **机制**，不是直接照搬系数。
- 论文的 OF 来自 **tick-by-tick trade sign**；如果只用 kline 自带 taker buy volume 做 proxy，信息会更粗。
- 这条线很怕两种东西：
  1. 大事件分钟把正常 OF-path 彻底盖掉；
  2. 你以为在做 order-flow alpha，实际只是在追一根已走完的大 bar。
- arbitrage 部分也提醒了：**看见 spread 不等于赚得到**。这条策略更像在做“流向冲击路径”，不是做无摩擦套利。

## 6. 下一步怎么测

我建议直接按下面顺序，不要发散：

1. **只做 `BTCUSDT` / `ETHUSDT` 两个品种**；
2. **先跑 follow-through leg**，持有 `1m / 3m` 两版；
3. 再把同一批 shock 聚合到 `5m`，测试 **OF 消失后的 fade leg**；
4. 全程统一扣 `4 bps` 和 `6 bps` 两档成本；
5. 若 BTC、ETH 两条都成立，再测第三步：
   - `BTC/ETH OF shock` 能不能当 alt basket 的 leader trigger。

如果第一轮结果是：

- `1m/3m` continuation 成立；
- `5m` fade 也有稳定 pocket；

那它就值得进入正式素材池，名字甚至可以非常朴素：

> **signed-flow-shock path alpha**

## 7. 来源

- **Barucci, E., Giuffra Moncayo, G., & Marazzina, D. (2023).** *Market impact and efficiency in cryptoassets markets*. *Digital Finance*, 5, 519–562.
  - DOI: `https://doi.org/10.1007/s42521-023-00095-9`
  - Readable URL: `https://link.springer.com/article/10.1007/s42521-023-00095-9`
  - Repo URL: 未找到官方公开 repo

- **Kaiko**（论文数据提供方；本文实际研究数据来自其 tick-by-tick 交易记录）
  - Readable URL: `https://www.kaiko.com/`
  - 备注：论文使用的是商业数据；但 desk 最小实验可先用公开交易所 taker volume / agg trade 近似复刻机制
