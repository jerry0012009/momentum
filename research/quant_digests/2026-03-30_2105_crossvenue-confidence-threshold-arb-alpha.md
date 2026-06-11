# 别把这篇 2025 ML arbitrage 论文直接抄成黑箱分类器：对 desk 更该先测的是「inventory-funded cross-venue quote gap × confidence threshold」完整 raw alpha

- 时间：2026-03-30 21:05 UTC
- 类型：2025 *International Journal of Network Management* 论文摘要元数据（Crossref）+ Binance/OKX/Bybit 公开 spot API live quick check
- 主题类型：raw alpha
- 基础 alpha：**同一币种在多交易所的最优买一/卖一会反复出现短命错位；若预先在多所备库存，且只在“价差足够大 + 置信度足够高”时出手，吃的是 cross-venue quote gap 的可成交收敛 alpha，而不是链上转币慢吞吞搬砖。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/relative-value/stat-arb/cross-venue/same-underlier/spot/arbitrage/quote-gap/confidence-threshold/inventory-funded/binance/okx/bybit/btc/eth/xrp/doge/1m/3m/5m/15m/paper/public-data/cost
- 证据类型：论文摘要级证据 + 公开 live API 快检

## 1. 这次看了什么

这次主看的是一篇很新、而且很像“可直接 desk 化”的跨所套利论文：

- **Authors**：Kristína Okasová, Michal Géci, Kristián Košťál
- **Year**：2025
- **Title**：*Predicting Arbitrage Occurrences With Machine Learning and Improved Decision Threshold Level in Live‐Trading Crypto Environments*
- **Venue**：*International Journal of Network Management*
- **DOI**：10.1002/nem.70030
- **Readable URL**：https://doi.org/10.1002/nem.70030
- **Metadata / abstract URL**：https://api.crossref.org/works/10.1002/nem.70030
- **Repo URL**：未见作者公开配套 repo

如果只用一句人话概括，这篇东西真正值得我们拿来测的，不是“机器学习又来预测市场了”，而是：

> **先承认跨所价差这件事本来就存在，再把“什么时候这次价差真的值得打”写成一个 confidence-threshold admission rule。**

这就比“看见跨所差价就无脑搬砖”诚实得多，也比“纯 ML 黑箱方向预测”更符合我们当前的短周期研发目标。

## 2. 核心结论

先把 base alpha 说清楚：

> **base alpha 不是 ML。base alpha 是同一标的在不同 venue 的 quote gap / micro dislocation 会在极短时间内回归；ML 只是决定“这次 gap 值不值得打”的 admission layer。**

这篇 paper 从摘要里给出的最有价值信息有 4 点：

1. **它研究的是跨交易所 arbitrage，不是单所方向预测。** 也就是说，主题本身就是 `relative value / stat-arb`，符合当前 desk 要补的 raw alpha 池。
2. **它不是等“罕见大价差”才动，而是想提前预测离散时间窗口内是否会出现可盈利 arbitrage。** 这点对 `1m / 3m / 5m` 特别重要，因为真正的问题不是“有没有 gap”，而是“能不能在 friction 前提下留下净边”。
3. **它把信号使用方式写成 decision threshold，而不是分类概率直接下单。** 这对 desk 的意义非常大：先有 `gap`，再有 `probability/confidence`，最后才有 `trade on / trade off`。
4. **论文摘要声称整套策略 1 周收益超过 100%。** 这个数字非常夸张，默认不能直接信；但恰好反过来提醒我们：**应该偷的是它的 admission logic，不是它的 headline 收益率。**

一句话核心结论：

> **对 desk 更值得先测的，不是“ML 会不会神奇预测一切”，而是“跨所 quote gap 本身是 raw alpha；confidence threshold 只是把可打事件筛得更干净”。**

一句话说明它怎么证明：

> **论文摘要明确把研究对象写成“跨所 arbitrage strategy + ML + improved decision threshold”，并宣称只有在模型置信度足够高时才触发套利；再配合我们对 Binance/OKX/Bybit 公开 top-of-book 的 live 快检，可以确认 raw quote gap 的确经常出现，但绝大多数边本身很薄，必须靠 admission rule 和成本治理。**

## 3. 为什么和当前项目有关

这轮值得 intake，原因很直接：

1. **它是 raw alpha，不是解释型材料。** base alpha 就是 `cross-venue same-underlier quote-gap convergence`。
2. **它是完整策略候选。** 有 entry（gap+hurdle）、exit（gap close/max hold）、sizing（inventory/capacity）、risk（venue/quote-age kill-switch）、cost（maker/taker/withdrawal 不同场景）这整条链。
3. **它补的是 relative-value / stat-arb 素材池。** 不是继续在 breakout / trend 单线内循环。
4. **它天然适配短周期。** 真正的时间尺度不是日频，也不是 8h funding；而是 `sub-second -> 1m` 的事件流，`3m/5m` 只是为了容纳执行摩擦与对账。

## 3.5 策略拆解（必填）

- 方向属性：**cross-venue / same-underlier / spot stat-arb / inventory-funded arbitrage**
- 基础 alpha：**不同交易所对同一币种的最优报价会短暂错位，随后向更一致的价格带收敛**
- regime：**高流动、高更新频率、跨所都活跃、链路稳定的时段更适合；宏观数据、交易所异常、单所维护时更容易出现“假 gap”**
- filter / veto：**只有当 `raw gap > fee + slip + inventory carry + stale-quote buffer` 且模型/规则置信度过线时才交易；若 quote age 异常、盘口 size 不对称、其中一所 spread 突然外扩则 veto**
- risk / sizing / execution overlay：**必须预先在多所备库存；按最短板 venue 的可成交名义 sizing；优先 maker-taker 或 maker-maker 场景；禁用“发现价差再转币过去”的慢速搬砖口径**

## 4. 3 个关键数据点

### 4.1 论文摘要给出的 headline 很激进
Crossref 收到的摘要原文写到：

- 目标是 **“predict the potential for arbitrage”**；
- 通过 **“confidence level metrics”** 只在模型足够确定时触发；
- 并声称 **“profitability of the entire strategy exceeds 100% within a 1-week timeframe.”**

这个收益数字默认只能当 **待复核 claim**，不能当已验证事实。

### 4.2 公开 live quick check：majors 的 raw top-of-book cross-gap 确实频繁出现
我用 Binance / OKX / Bybit 公共 spot API，对 `BTCUSDT / ETHUSDT / DOGEUSDT / XRPUSDT` 做了 **12 次、约 1.5 秒间隔** 的 distinct-venue 最优 bid-vs-ask 快检（只允许 `bid venue != ask venue`）。结果：

- **BTCUSDT**：12/12 次为正，**median 0.5531 bps**，**max 1.6141 bps**
- **ETHUSDT**：12/12 次为正，**median 1.2489 bps**，**max 2.5945 bps**
- **DOGEUSDT**：10/12 次为正，**median 1.0965 bps**，**max 2.1939 bps**
- **XRPUSDT**：11/12 次为正，**median 1.1268 bps**，**max 4.5079 bps**

这说明：**可观察的 raw gap 并不稀缺**。

### 4.3 但 raw gap 很可能不够厚，除非你是“有库存的人”
同样一组 live 数据也说明另一件事：

- majors 的常态 raw gap 常常只有 **0.5~1.5 bps**；
- 若按普通 taker/taker 两边都吃单，很多场景会直接被费率吃掉；
- 真正更像可交易策略的是：**预布库存 + 低费率/VIP + venue 内/venue 间库存再平衡 + 只打高置信度事件。**

所以这条线更像 **inventory-funded micro stat-arb**，不是链上转账搬砖。

## 5. 真正值得 desk 先偷哪一段

最该偷的不是“用哪个模型”，而是它的逻辑顺序：

1. **先确认 raw alpha 存在：** 有没有 distinct-venue 的净价差事件；
2. **再确认成本后是否还有肉：** fee/slip/inventory carry/quote staleness 都算进去；
3. **最后才上 confidence threshold：** 只打最像真机会的子集。

也就是说，正确的研发顺序不是：

> 先堆模型 -> 找到高概率 -> 再去想交易什么。

而应该是：

> 先定义 `best_bid - best_ask` 的 executable gap -> 跑 friction ladder -> 再看一个极简 classifier / threshold 有没有增益。

这非常适合当前 desk，因为它不要求我们先搞一个重型预测系统；**先从 rule-based threshold baseline 起步就够了。**

## 6. 可复刻的最小实验

### 6.1 数据源、公开性、更新频率

- **Binance Spot bookTicker / depth**：公开 REST / WebSocket，可毫秒级更新
- **OKX Spot ticker / books**：公开 REST / WebSocket，可毫秒级更新
- **Bybit Spot ticker / orderbook**：公开 REST / WebSocket，可毫秒级更新
- **公开性**：公开可得，无需私钥即可先做 snapshot / replay
- **最小实验频率**：底层建议 `250ms~1s`，第一轮聚合到 `1m / 3m` 做 first verdict

### 6.2 最小可复现实验口径

1. **标的先只做高流动 `BTCUSDT / ETHUSDT / XRPUSDT / DOGEUSDT`。**
2. **venue 先只接 3 所：Binance / OKX / Bybit。**
3. **定义 executable gap：**
   - `gap_raw_bps = (max_bid_other_venue - min_ask_other_venue) / mid * 10000`
   - 必须要求 `bid venue != ask venue`
4. **定义可交易门槛：**
   - `gap_net_bps = gap_raw_bps - taker_fee_bid - taker_fee_ask - slip_buffer - stale_quote_buffer`
   - 若有 maker 能力，再单独跑 `maker-taker` 与 `maker-maker` 口径
5. **方向：**
   - 在 ask venue 买入、在 bid venue 卖出；
   - 不做链上转账版，默认是 **inventory-funded**
6. **出场：**
   - gap 回落至 `close_band`；或
   - `max_hold = 10s / 30s / 60s / 180s`；或
   - 任一 venue quote age / spread / API 状态异常强退
7. **第一轮 baseline：**
   - 不上 ML，只跑 `raw threshold` 与 `persistence threshold`
8. **第二轮才加 classifier：**
   - features 可先用 `gap level / gap velocity / venue spread / quote age / 最近 k 个 snapshot gap persistence / 同币 perp basis / 最近成交方向`

### 6.3 第一轮先回答什么

- 哪些币、哪些 venue 组合最常给出 **正的 distinct-venue gap**？
- `1s` 级别 gap 的持续时间分布如何？是 1 个 tick 闪一下，还是能撑到 5~30 秒？
- 在 `taker-taker / maker-taker / maker-maker` 三套 friction 下，正净边事件各剩多少？
- 若只做 **高置信度 persistent gap**，trade count 会掉多少、净边会厚多少？

## 7. 这张卡最容易错在哪里

- **错法 1：** 把它误做成“发现价差再转币”的传统搬砖。真正可活的版本更像**预布库存**。  
- **错法 2：** 用 last price 而不是 top-of-book + size + quote age。  
- **错法 3：** 只看 raw gap，不看 distinct venue、手续费、滑点、API 延迟。  
- **错法 4：** 先堆 ML，再发现 baseline 都没净边。  
- **错法 5：** 把论文里“1 周 >100%”的结果当成可直接照搬的事实。  

## 8. 为什么值得进入研究池

它值得进池，不是因为我们已经相信论文收益，而是因为它满足当前 Scout 最看重的几条：

1. **数据稳定可拿。** 三大所公开 book/ticker 足够起步；
2. **规则能清楚写成 trade-on / trade-off。** gap、成本、置信度、quote age 都能落成规则；
3. **能很快做 first verdict。** 连历史大样本都不用先等，先抓 1~3 天高频快照就能判断有没有肉；
4. **是完整 raw alpha。** 不是纯 filter，也不是解释型综述。

对当前 desk，这条线的价值在于：

> **它把“跨所价差”从一个泛泛而谈的 old story，压缩成了一个非常适合 `1m / 3m` 研发节奏的 executable alpha 候选。**

## 9. 下一步怎么测

1. **先做 72 小时跨所 quote 采集。** `BTC / ETH / XRP / DOGE` × `Binance / OKX / Bybit`，保留 top-of-book、size、timestamp、quote age。  
2. **先跑纯 baseline，不上 ML。** 比较 `0.5 / 1 / 2 / 3 / 5 bps` raw gap 阈值，在不同 friction 假设下的净边与事件数。  
3. **把持仓前提写死：inventory-funded only。** 同时记录各 venue 库存占用，别偷换成链上搬砖。  
4. **第二轮再加 confidence threshold。** 先从极简 logistic/GBM 做起，看它相对阈值基线是否真的提升 `net expectancy`，而不是只提升 in-sample accuracy。  
5. **如果 majors 太薄，就转向次一层高流动 alts。** 但仍要坚持先跑 friction ladder，再决定是否值得进正式 admission check。  

## 10. 来源

### 论文 / 元数据
- Kristína Okasová, Michal Géci, Kristián Košťál (2025), *Predicting Arbitrage Occurrences With Machine Learning and Improved Decision Threshold Level in Live‐Trading Crypto Environments*, *International Journal of Network Management*.
- DOI: https://doi.org/10.1002/nem.70030
- Crossref metadata + abstract: https://api.crossref.org/works/10.1002/nem.70030

### 公开 live 数据接口（本次快检）
- Binance Spot bookTicker: https://api.binance.com/api/v3/ticker/bookTicker
- OKX Spot ticker: https://www.okx.com/api/v5/market/ticker
- Bybit Spot tickers: https://api.bybit.com/v5/market/tickers
