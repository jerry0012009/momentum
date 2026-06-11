# 别把 CME 月度到期只当“波动提醒”：这篇 2023 IREF 论文对短周期 desk 更该先测的是「到期后 60~120 分钟 short BTC」事件型 raw alpha

- 时间：2026-03-26 10:35 UTC
- 类型：raw alpha
- 主题类型：raw alpha
- 基础 alpha：CME BTC 月度到期（last Friday, 16:00 London）后，BTC 现货/永续在接下来 `60~120m` 出现相对普通周五更弱的负漂移；优先做事件时钟 short，而不是全天候方向交易
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/event-driven/btc/cme-expiry/expiration-effect/post-expiry/spot/perpetual/intraday/1m/3m/5m/15m/time-series/momentum/reversal/paper/external-data
- 证据类型：2023 IREF 论文（OpenAlex 摘要可得）+ CME 公共合约规则 + Binance Spot/Perp 公共 `1m` 最小快检

先把 **base alpha** 说死：**不是“expiry 日会比较热闹”这种泛泛事件感，而是“月度 CME 到期时钟一敲，BTC 在后续 60~120 分钟更容易走弱”这条可交易的事件后漂移。**

这轮我优先选它，不是因为 desk 缺一个宏观解释，而是因为它本身已经能落成一条 **exact-time、可直接回测、可直接上线 watchlist 的 raw alpha**：

1. **信号时钟公开且精确**：last Friday、16:00 London；
2. **交易数据公开可拿**：Binance spot / perp `1m` 就够做最小实验；
3. **不是继续在 breakout/retest 上内循环**，而是给素材池补一个很稀缺的 **event-time BTC directional alpha**。

## 1. 这篇东西真正值得 desk 化的，不是“到期有效应”，而是「到期后 drift」

主论文是：

- **Blasco, N., Corredor, P., & Satrústegui, N. (2023). _Is there an expiration effect in the bitcoin market?_ International Review of Economics & Finance.**
- DOI：`10.1016/j.iref.2023.02.013`
- Readable URL：`https://doi.org/10.1016/j.iref.2023.02.013`

论文原问题是：**Bitcoin 市场在 futures 到期附近，是否存在类似传统市场的 expiration effect？**

对我们这种做 `1m / 3m / 5m / 15m` 的 desk 来说，最值钱的读法不是“学术上有无效应”，而是把它翻译成一句更能交易的话：

> **如果月度到期窗口真的改变了盘面行为，那最该先测的不是日级别均值，而是 exact event time 之后的短时漂移。**

也就是说，这篇论文更适合被读成：

- 一个 **公开、可提前知道、时间精确** 的事件；
- 一个可能改变短时 order flow / roll pressure / inventory adjustment 的时点；
- 一个可以直接变成 entry/exit/risk/cost 规则的 **event-driven BTC alpha**。

## 2. 为什么这次先测「到期后 short」，而不是把它降级成 overlay

如果只看论文标题，这个题目很容易被写成：

- `regime gate`
- `volatility reminder`
- `execution veto`

但这次我不想这么保守，因为做完最小快检后，**方向性已经够清楚**：

- **Binance Perp**：2025-01 到 2026-02 共 **14 个**月度到期事件里，`event -> +60m` 平均收益 **-21.0bp**；
- 同期 **47 个非月度普通周五** 的同一本地时钟窗口，`event -> +60m` 平均收益 **+15.5bp**；
- 也就是 **expiry - placebo = -36.5bp**。

Spot 端几乎一样：

- **Binance Spot**：`event -> +60m` 平均收益 **-20.8bp**；
- 普通周五对应窗口是 **+15.4bp**；
- **expiry - placebo = -36.2bp**。

如果继续把它只叫“overlay”，反而有点低估了这条线。更诚实的分类应该是：

> **event-driven BTC raw alpha**，只是它不是 always-on，而是按月触发。

## 3. 当前最小快检：方向性已经出来了，而且现货/永续一致

我这次没有去碰付费数据，直接用 **CME 月度到期规则 + Binance 公共 `1m` K 线** 做最小实验。

### 数据源与公开性

- **CME 月度事件时钟**：公开合约规则，按 **last Friday, 16:00 Europe/London** 对齐；
  - CME BTC futures 页面：`https://www.cmegroup.com/markets/cryptocurrencies/bitcoin/bitcoin.contractSpecs.html`
- **Binance Spot `BTCUSDT` 1m klines**：公开 REST；
  - 文档：`https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data`
- **Binance Perpetual `BTCUSDT` 1m klines**：公开 REST；
  - 文档：`https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

### 最小实验口径

- 样本：`2025-01-01` 到 `2026-03-01`
- 事件：每周五本地 `16:00 London`
- `expiry` 定义：**每月最后一个周五**
- `placebo`：其余普通周五同一本地时钟
- 观察窗口：`pre60m / post60m / post120m`

### 这次最重要的 4 个数

1. **Perp：expiry 后 60m 平均 -21.0bp，普通周五同窗 +15.5bp，差值 -36.5bp。**
2. **Spot：expiry 后 60m 平均 -20.8bp，普通周五同窗 +15.4bp，差值 -36.2bp。**
3. **Perp：expiry 后 120m 平均 -21.4bp，普通周五同窗 +20.0bp，差值 -41.4bp。**
4. **Spot：expiry 后 120m 平均 -21.2bp，普通周五同窗 +19.9bp，差值 -41.2bp。**

对应 artifact：

- `reports/artifacts/quant_digests/cme_expiry_postfix_short_20260326/btc_expiry_vs_friday_events.csv`
- `reports/artifacts/quant_digests/cme_expiry_postfix_short_20260326/bucket_summary.csv`
- `reports/artifacts/quant_digests/cme_expiry_postfix_short_20260326/expiry_minus_placebo_summary.csv`

这里最关键的不是“每个月都跌”。它当然 **不是 14/14 全中**。关键在于：

- **普通周五同一时钟是正漂移**；
- **月度到期那一窗却切成负漂移**；
- 而且 **spot/perp 同步成立**，不像单 venue 偶然噪声。

这就足够把它从“日历提醒”提升成一条值得进池的 raw alpha 候选。

## 4. desk 版本的最小完整策略骨架

### 4.1 最简版（先验证最粗 edge）

- **交易对象**：Binance `BTCUSDT` perp（优先），spot 作为对照
- **入场**：CME 月度到期时点 `T0 = last Friday 16:00 London`，在 `T0 ~ T0+5m` 内按 VWAP/分批做空
- **出场**：
  - 主退出：`T0+60m`
  - 备选退出：`T0+120m`
- **止损**：自入场起浮亏 `>= 35~45bp` 强平
- **仓位**：事件固定 risk budget，例如单次只打日风险预算的 `20~35%`
- **成本**：先按 `2~4bp taker + 2~4bp slippage` 做保守回测，验证净值还能不能活

### 4.2 更像 production 的增强版

不要无脑每月都空。更合理的是给它加两个 gate：

- **Gate A：pre-expiry ramp**
  - 只有当 `T0-60m -> T0` 本身先走出 `+20bp / +30bp / +40bp` 的上冲，才允许做 `post-expiry short`；
  - 逻辑：如果到期前已经被挤出一段正向 drift，后面的 inventory unwind / roll unwind 更有空间。

- **Gate B：basis / funding 不要逆着你**
  - 若到期前 8h funding 已显著转负，说明市场可能已经先消化部分压力；
  - 这时就别把 event short 当无条件信号。

换成人话：

> **这条线更像“到期前先被顶起来，再在到期后回吐”的事件后 short，不像纯日历开仓。**

## 5. 为什么它适合 `1m / 3m / 5m / 15m`

因为这条 alpha 不是靠低频宏观慢变量吃饭，而是靠 **精确时钟 + 短时 order flow 失衡**：

- `1m / 3m`：最适合做入场切片、观察首 5~15 分钟 follow-through；
- `5m`：最适合做主回测频率，成本与噪声比较平衡；
- `15m`：更适合做 event bucket 汇总，而不是最早入场。

所以它完全不是“论文里日级别有效，短周期做不了”的那类题。恰恰相反，**这题越短越像真交易。**

## 6. 这条线最大的风险，不是信号弱，而是样本少

要老实说，当前最大问题不是想法不对，而是：

- 月度事件 **一年只有 12 次左右**；
- 单看月度 CME 到期，样本天然小；
- 很容易被少数大行情月份污染。

所以这条线不能直接以“14 个样本均值为王”上线。必须继续做下面两层扩展：

1. **扩样本**：把历史往前拉到 2021/2022，至少做 `36~60` 个事件；
2. **扩家族**：把周度/季度 expiry、Deribit/OKX options settlement、Binance funding settlement 一起做 event family 对照。

也就是说，**这条 alpha 值得进池，但现在还更像 high-priority pilot，不是立刻满仓的生产信号。**

## 7. 下一步怎么测（最重要）

### P0：先把这条最小策略回测跑完整

- 标的：`BTCUSDT perp`
- 频率：`1m` 与 `5m`
- 规则：
  - `T0+0~5m` 做空
  - `T0+60m` / `T0+120m` 平仓
  - 成本：`4bp / 6bp / 8bp` 三档压力测试
- 输出：
  - 每次事件 PnL
  - hit rate
  - mean / median / skew
  - max adverse excursion

### P1：验证「pre-expiry ramp gate」

把事件按 `T0-60m -> T0` 的预热强度分桶：

- `<0bp`
- `0~20bp`
- `20~40bp`
- `>40bp`

看 **后 60m short edge 是否主要集中在预热最强桶**。如果是，这条线就从“日历空”升级成“event + setup”策略。

### P2：做 cross-venue / cross-instrument 验证

- Binance spot
- Binance perp
- Coinbase spot
- Deribit perp / futures（若公共 API 拿得到）

如果 edge 只在一处成立，它更像 venue microstructure；
如果多 venue 同向成立，它才更像可迁移的 desk alpha。

### P3：与其他事件时钟做对照

把它和以下事件摆在同一张 event board：

- funding settlement
- options expiry / settlement
- ETF open / close
- FOMC / CPI

看这条线到底是 **独立 alpha**，还是“事件波动家族”的一个成员。

## 8. 一句话结论

这篇 2023 论文如果只被读成“Bitcoin 到期附近可能有异常”，那对 desk 太浪费。**更适合我们现在的读法，是把它直接落成一条 exact-time raw alpha：月度 CME 到期后，优先测 `60~120m short BTC`。**

当前最小快检已经给出足够明确的方向：**2025-01 到 2026-02，spot/perp 都显示月度到期后的 60~120 分钟明显弱于普通周五同窗，差值大约在 `-36bp` 到 `-41bp`。**

这还不是 production-ready，但已经绝对值得进下一轮复现队列。

## 9. 来源

1. **Blasco, N., Corredor, P., & Satrústegui, N. (2023). _Is there an expiration effect in the bitcoin market?_ International Review of Economics & Finance.**  
   - Venue: International Review of Economics & Finance  
   - DOI: `10.1016/j.iref.2023.02.013`  
   - Readable URL: `https://doi.org/10.1016/j.iref.2023.02.013`

2. **CME Group — Bitcoin Futures Contract Specs / product page**  
   - URL: `https://www.cmegroup.com/markets/cryptocurrencies/bitcoin/bitcoin.contractSpecs.html`

3. **Binance Spot API — Kline/Candlestick Data**  
   - URL: `https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data`

4. **Binance USDⓈ-M Futures API — Kline/Candlestick Data**  
   - URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`
