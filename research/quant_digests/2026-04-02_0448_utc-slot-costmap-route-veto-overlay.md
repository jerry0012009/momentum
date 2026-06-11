# 别把 15m 时段性只当盘感：这篇 2026 crypto 微观结构 working paper 更该先落地的是「UTC slot cost map × quote/venue routing × execution veto」共享 overlay

- 主题类型：overlay
- 基础 alpha：服务 `pairs/stat-arb`、`carry/funding/basis`、`breakout/continuation`、`lead-lag` 这些本来就想交易的 raw alpha；它本身**不是**独立 raw alpha，而是告诉我们**哪些 UTC 时段更贵、更吵、更适合改 route / size-down / 延后进场**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 时间：2026-04-02 04:48 UTC
- 类型：2026 SSRN working paper 摘要 / Crossref metadata + 2026 *Journal of Futures Markets* supporting abstract + Binance Spot 公共 `15m` 最小快检
- 主题标签：overlay/filter/execution/cost-map/time-of-day/utc-slot/liquidity/volatility/market-quality/quote-routing/venue-routing/shared-component/binance/coinbase/btc/eth/15m/5m/3m/1m/paper/public-data/cost
- 证据类型：paper metadata+abstract + public-data quick check

## 1. 这次看了什么
这轮主看的是：

1. **Aleksander R. Mercik, Barbara Będowska-Sojka (2026)** 的 working paper：
   *When Markets Never Sleep: Intraday Liquidity Patterns and Volatility Effects in Cryptocurrency Trading*
2. **Andrei Shynkevich (2026, Journal of Futures Markets)**：
   *Trading Periodicity and Algorithmic Divide in Cryptocurrency Markets*

这轮我没有把它硬包装成“新的方向 alpha”。先把话说清楚：

> **它不是 raw alpha，本质上是一个共享 execution / routing overlay。**

但它仍然值得写进研究池，因为最近 raw alpha 池已经在补：
- pairs / stat-arb
- carry / funding / basis
- breakout / continuation
- lead-lag / microstructure

这些策略有一个共同死法：**方向对了，但下单时段选错了，导致点差、滑点、拥挤流和噪音一起把薄 edge 吃掉。**

这篇材料最值钱的，不是告诉你“哪一根一定涨跌”，而是告诉你：
**crypto 的 intraday liquidity / volatility / activity 有可预测的 UTC slot 结构；时段本身就该进你的 route、size、veto 逻辑。**

## 2. 先回答一句：这篇东西的 base alpha 是什么？
**答不清，因为它不是 alpha 本体。**

所以它应该被归类为：**overlay / shared filter**。

它服务的 base alpha 可以是：
- `pairs/stat-arb`：同样的 spread 偏离，在“贵时段”做，净值可能被冲击和换手吞掉；
- `carry/funding/basis`：同样的 carry 或 basis 回归，在高噪音时段开腿，成本更差；
- `breakout/continuation`：同样的方向信号，在高活动窗口更可能继续，也更可能被高波动假动作打脸；
- `lead-lag`：leader 已经动了，但 follower 盘口很贵时，追不追应先看 slot cost map。

翻成人话：
**这张卡片回答的不是“做不做多空”，而是“什么时候做更便宜、更干净、更适合成交”。**

## 3. 为什么这轮值得写，而不是继续补一张 raw alpha 卡
按默认优先级，raw alpha 当然更高。但这轮这篇 overlay 仍然值得 intake，理由很直接：

1. **它是近 30 天的新 working paper（2026-03-12 posted）**，不是旧 backlog 翻炒；
2. **它直接用 `15m` 高频口径看 Binance / Coinbase、BTC / ETH、fiat / stablecoin quotes**，离 desk 当前 `5m/15m` 更近；
3. **它不是泛泛而谈 market quality**，而是明确落在 intraday periodicity 与 out-of-sample spread forecasting；
4. **它能同时服务至少 3 类已在池里的 raw alpha**，边际价值高于再补一张“相似的单腿 directional 卡”。

如果要心里先回答一句“它为什么比继续补 raw alpha 更值得？”——我的答案是：

> **因为 raw alpha 素材池最近已经扩得够快，而这篇材料补的是它们共同缺的那层：统一的时段成本地图与执行 veto 逻辑。**

## 3.5 策略拆解（必填）
- 方向属性：shared execution / routing overlay
- 基础 alpha：
  - `pairs/stat-arb spread MR`
  - `carry/funding/basis`
  - `breakout/continuation`
  - `lead-lag / event beta`
- regime：优先用于 `1m/3m/5m/15m` 的高换手策略，尤其是 **薄 edge、maker/taker 成本敏感、或多腿策略**
- filter / veto：对每个 `symbol × venue × quote × UTC slot` 预先打 `green / yellow / red` 成本标签；红区不轻易新开仓
- risk / sizing / execution overlay：
  - `green`：正常仓位
  - `yellow`：`0.5x~0.7x` 或要求更高 admission score
  - `red`：`0~0.3x`，或只允许减仓/平仓，不允许新开仓
  - route 优先级：低成本 quote / venue 优先；高成本 route 只在强信号下启用

## 4. 这次看的主来源
### 4.1 主来源（paper）
1. **Mercik, A. R., & Będowska-Sojka, B. (2026).**
   **Title:** *When Markets Never Sleep: Intraday Liquidity Patterns and Volatility Effects in Cryptocurrency Trading*
   **Venue:** SSRN working paper
   **DOI:** `10.2139/ssrn.6401099`
   **DOI URL:** https://doi.org/10.2139/ssrn.6401099
   **Readable URL:** https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6401099
   **Repo URL:** N/A

### 4.2 supporting source
2. **Shynkevich, A. (2026).**
   **Title:** *Trading Periodicity and Algorithmic Divide in Cryptocurrency Markets*
   **Venue:** *Journal of Futures Markets*
   **DOI:** `10.1002/fut.70089`
   **DOI URL / Readable URL:** https://doi.org/10.1002/fut.70089
   **Repo URL:** N/A

## 5. 核心结论：这篇 paper 真正能带走什么
### 5.1 Mercik & Będowska-Sojka (2026) 给出的核心信息
Crossref 摘要已经够明确：

- 数据口径是 **high-frequency 15-minute data**；
- 交易场景覆盖 **Binance 与 Coinbase**；
- 标的覆盖 **BTC / ETH**；
- quote currency 同时看 **fiat 与 stablecoin**；
- 核心研究对象不是收益方向，而是 **liquidity / volatility / spread periodicities**；
- 作者使用 **depth-adjusted spread**，而不是只盯 close-to-close return；
- 结论是：
  1. **volatility 是 spread 变化的主驱动**；
  2. **periodic factors 还能提供额外解释力**；
  3. 这些 periodicity **能提升 out-of-sample spread forecasting**；
  4. **venue 与 quote currency 的差异是稳定存在的**。

对 desk 来说，最重要的翻译是：

> **别把“时段性”当成盘感。它应该是模型输入，而且最好是 `symbol × venue × quote × UTC slot` 级别的输入。**

### 5.2 supporting paper 的强化点
Shynkevich (2026) 这篇 supporting source 不是 15m，而是更细的 subsecond 交易活动周期。

Crossref 摘要给了三句很关键的话：

- **periodic surges in trading activity recurring at regular time intervals increase volatility and raise transaction costs**；
- 这些 surges **不一定造成显著 adverse price impact**；
- **largest share of price discovery** 发生在与 proprietary algorithms taking liquidity 相关的窗口。

这说明什么？

1. **高活动时段不等于不能做**；
2. 但它常常意味着 **更贵、更挤、更需要 execution discipline**；
3. 所以你不该用“一刀切不做”的方式处理，而该用：
   - route 选择
   - size-down
   - maker/taker 切换
   - admission score 提高

### 5.3 我这轮最小快检：Binance 公开 `15m` 数据已经能看出明显 slot 结构
我这轮没有直接拿到真实 order-book spread，所以先用公开 `kline` 做粗代理快检：

- **样本**：`2026-03-01 22:45 UTC ~ 2026-04-02 04:30 UTC`
- **数据量**：`12,000` 根 `15m` bars
- **交易对**：`BTCUSDT`, `ETHUSDT`, `BTCFDUSD`, `ETHFDUSD`
- **代理指标**：
  - `range_bps = (high / low - 1) * 1e4`
  - `abs_ret_bps = abs(close / open - 1) * 1e4`
  - `quote_volume`
  - `trade_count`
- **方法**：按 UTC `15m slot` 聚合，再用 `range + quote_volume + trade_count` 的 z-score 平均做 composite activity/cost proxy

#### 快检结果 1：最热窗口非常集中
综合最热的 8 个 `15m` slot 基本都落在：
- **13:30 UTC**
- **13:45 UTC**
- **14:00 ~ 15:30 UTC**

也就是明显偏向 **美盘开盘 / 宏观数据高敏感时段**。

#### 快检结果 2：热时段和冷时段差异并不小
把 composite 最高的 24 个 slot 和最低的 24 个 slot 对比：

- 热时段平均 `range_bps`：**56.9 bps**
- 冷时段平均 `range_bps`：**32.7 bps**
- **高出约 73.9%**

- 热时段平均 `quote_volume`：**9.63M**
- 冷时段平均 `quote_volume`：**4.80M**
- **约 2.01x**

- 热时段平均 `trade_count`：**38.5k**
- 冷时段平均 `trade_count`：**17.1k**
- **约 2.26x**

这说明：
**UTC slot 本身就能把“安静时段”和“昂贵拥挤时段”切开。**

#### 快检结果 3：quote currency 差异也很真实
同一 base asset 下，`FDUSD` 相对 `USDT`：

- `BTCFDUSD` 的平均 `quote_volume` 只有 `BTCUSDT` 的 **5.5%**；
- `ETHFDUSD` 的平均 `quote_volume` 只有 `ETHUSDT` 的 **4.1%**；
- 但 `range_bps` 只略低于 USDT 主对（约 **96.5%~96.8%**）。

翻成人话：
**有些 quote route 没便宜多少波动，但深度和成交拥挤度完全不是一个量级。**

对 market-neutral 或高换手策略，这种差异足以决定：
- 你该不该走这个 quote；
- 是否只把它当补充 route；
- 或是否必须抬高 admission 门槛。

## 6. 这条 overlay 可以怎么直接落成完整规则
### 6.1 先做一张 `UTC slot cost map`
对每个：
- `symbol`
- `venue`
- `quote currency`
- `UTC slot`（`96` 个 `15m` 桶，或 `288` 个 `5m` 桶）

计算：
- realized range / realized vol
- quote volume
- trade count
- 若拿得到，再加：
  - bid-ask spread
  - order-book depth
  - taker buy/sell imbalance
  - mark-index premium deviation

然后压成一个 `slot_cost_score`。

### 6.2 把它接到 4 类策略上
1. **pairs / stat-arb**
   - 红区不新开双腿；
   - 或要求 spread z-score 更极端才开。

2. **carry / funding / basis**
   - carry 足够厚时才在黄区开腿；
   - 红区只允许平旧仓，不追新腿。

3. **breakout / continuation**
   - 热时段可保留方向单，但把 taker entry 换成更保守的分批 / maker-ish execution。

4. **lead-lag**
   - leader 动了以后，先看 follower route 是否正处于高成本 slot；
   - 若是，就提高追单阈值或延后到下个 slice。

### 6.3 直接可执行的第一版规则
- `green zone`：正常仓位 + 正常阈值
- `yellow zone`：仓位 `0.5x~0.7x`，或把 z-score / model score 门槛抬高一档
- `red zone`：
  - 不新开仓；或
  - 只允许 `0~0.3x` 的试探仓；或
  - 只允许 maker / passive route

这意味着：
**slot map 不决定方向，但直接决定你怎么成交。**

## 7. 风险与边界
- 这条材料不是“某 UTC 时刻一定涨/跌”的方向信号，不要伪装成 raw alpha；
- 我这轮快检没有真实 spread，只用了 `range / volume / trade_count` 代理，因此更像执行粗筛；
- Binance 单一 venue 的快检，不足以直接外推到 Coinbase / Bybit / OKX；
- `US open` 这类热时段虽然更贵，但也往往信息含量更高，不能机械 veto；
- 对极强 event-driven 信号，更合理的是 `size-down` 和 `route change`，不是一刀切停做。

## 8. 下一步怎么测
1. **先把 `slot_cost_score` 接进三条现有主线做 A/B test**
   - `pairs/stat-arb`
   - `funding/basis carry`
   - `breakout/continuation`
   比较：
   - baseline
   - `yellow/red veto`
   - `size-down only`
   - `route-switch only`
   看 net PnL、turnover、max drawdown 哪个改善最大。

2. **把代理成本升级成真实成本**
   - 拉 `bookTicker / depth`，直接做真实或准真实 spread；
   - 区分 maker / taker 成本，而不是只看 kline range。

3. **把 `15m` 下钻到 `5m/1m` 执行层**
   - 用 `15m` slot map 做高层 regime；
   - 用 `5m/1m` 决定具体切片、挂单与追单逻辑。

4. **补 venue / quote routing 实验**
   - 同一 base asset 对比 `USDT / FDUSD / USDC`；
   - 同一 symbol 对比 `Binance / Coinbase / Bybit / OKX`；
   - 目标不是找“最热交易所”，而是找**净成本最优 route**。

## 9. 来源
1. **Mercik, A. R., & Będowska-Sojka, B. (2026). _When Markets Never Sleep: Intraday Liquidity Patterns and Volatility Effects in Cryptocurrency Trading_.**
   - Venue: SSRN working paper
   - DOI: `10.2139/ssrn.6401099`
   - DOI URL: https://doi.org/10.2139/ssrn.6401099
   - Readable URL: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6401099
   - Repo URL: N/A

2. **Shynkevich, A. (2026). _Trading Periodicity and Algorithmic Divide in Cryptocurrency Markets_.**
   - Venue: *Journal of Futures Markets*
   - DOI: `10.1002/fut.70089`
   - DOI URL / Readable URL: https://doi.org/10.1002/fut.70089
   - Repo URL: N/A

## 10. 本地产物
- 研究笔记：`research/quant_digests/2026-04-02_0448_utc-slot-costmap-route-veto-overlay.md`
- 快检目录：`reports/artifacts/quant_digests/markets_never_sleep_slot_overlay_20260402/`
- 关键文件：
  - `slot_periodicity_summary.csv`
  - `symbol_slot_stats.csv`
  - `summary.json`
