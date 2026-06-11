# 别把 public trades 只压成整根 candle delta：`stacked price-bin imbalance` 更像 breakout-short / Fib / EMA-PSAR 的 shared microstructure confirm-veto 层
- 时间：2026-03-21 04:58 UTC
- 类型：GitHub 仓库 + 官方文档
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/microstructure/public-trades/stacked-imbalance/confirmation/veto/repo/docs/crypto/5m/15m
- 证据类型：仓库实现 + 官方文档规则

## 1. 这次看了什么
这次看的是 `freqtrade/freqtrade` 的 `advanced-orderflow.md` 与 `orderflow.py`。它最值钱的不是“能看 footprint 图”，而是把公开成交逐笔数据拆成**相邻价位上的同侧连续失衡**：不是问整根 15m 最后是买多还是卖多，而是问**某一侧是不是在连续几个价位上层层推进**。

## 2. 核心结论
- **一句话核心结论**：如果前面已经有 breakout-short / Fib reclaim / EMA-PSAR flip 这类价格触发，下一层更值得先测的，不是再堆一个价格指标，而是 `stacked imbalance`——同侧 aggressor 是否在相邻价位上连续占优。
- **一句话证明方式**：Freqtrade 直接把公开 trades 按价格分箱，再做对角比较与连续计数；默认参数就是 `stacked_imbalance_range=3`、`imbalance_ratio=3`，说明它本质上在抓“不是单点爆一下，而是连续三层都有推进”。
- 代码细节比表面更重要：`ask`/`bid` 先从逐笔 `buy/sell` 侧汇总，随后不是看整根 candle 的总 delta，而是比较**相邻 price bin** 的 ask-vs-bid 比值，再找连续 True 段；这比单个 `delta>0` 更接近“真跟随盘/真砸盘”。
- 这题比继续单修某一条线更值得，因为它能同时服务三条收口线：`breakout-short` 看破位后是否有连续卖压、`Fib retest_hold` 看回踩重夺后是否有连续买压、`EMA/PSAR` 看翻向后是否真有同侧参与者接力。
- 它还比盘口深度方案更现实：只需要**公开可得**的 public trades，不要求付费 L2，也不用把低频外部数据硬装成 15m 主信号。

## 3. 为什么和当前项目有关
这更像三条线共用的**微观确认层**，不是另起炉灶的新 alpha：价格结构先给方向，`stacked imbalance` 只负责回答“这一下是不是有人真在沿着价格梯子追”。这正好补 `breakout-short follow-up / Fib retest_hold / EMA-PSAR raw alpha` 现在共同缺的一层近因证据。

## 4. 可复刻的最小实验
- **研究假设**：在已有价格触发之后，同侧 `stacked imbalance` 比简单 candle delta 更能压低假突破 / 假回踩。
- **数据源**：Binance USDⓈ-M `aggTrades` 或任何支持 public trades 的交易所；公开可得，更新频率为逐笔/近实时。
- **最小定义**：把 setup 所在 5m 或 15m candle 内的 trades 按价格分箱（先用 tick size 的 4~8 倍试），做 `imbalance_ratio >= 3`、`stacked_imbalance_range >= 3`；long 看 `stacked_imbalances_ask` 是否出现在触发区上沿附近，short 镜像看 `stacked_imbalances_bid`。
- **先测哪个切口**：`base` vs `base + candle delta gate` vs `base + stacked imbalance gate`，优先在 `BTC/ETH/SOL perp` 最近 60~120 天 15m 上看 `2/4 bar follow-through`、`false-break/false-hold rate`、`trade-count retention`。
- **下一步怎么测**：第一轮不要上 ML，也不要先做全局最优参数；先问一个最朴素的问题——当价格信号已经成立时，**连续三层价位上的同侧 aggressor 推进**，能不能比“这根总 delta 同向”更稳定地区分 continuation 和 dead-on-arrival。

## 5. 风险与保留意见
- 这是工程实现启发，不是论文级统计结论；默认阈值 `3/3` 很可能需要按 tick size、币种活跃度和分箱尺度重标。
- `stacked imbalance` 依赖逐笔 trades，数据量和缓存成本会高于纯 OHLCV。
- 若分箱太粗，会退化成普通 candle delta；太细则会把噪音误当结构。
- 它更适合当 confirm/veto 层，不该直接升级成独立主信号。

## 6. 来源
- Freqtrade contributors. (2026). *Orderflow data / advanced-orderflow.md*. Freqtrade documentation.
  - Venue / DOI：Docs / N/A
  - Readable URL: <https://www.freqtrade.io/en/stable/advanced-orderflow/>
  - Raw docs: <https://raw.githubusercontent.com/freqtrade/freqtrade/develop/docs/advanced-orderflow.md>
- Freqtrade contributors. (2026). *freqtrade/data/converter/orderflow.py*. GitHub repository.
  - Repo URL: <https://github.com/freqtrade/freqtrade>
  - Raw source: <https://raw.githubusercontent.com/freqtrade/freqtrade/develop/freqtrade/data/converter/orderflow.py>
  - Repo metadata snapshot: created `2017-05-17`, updated `2026-03-21`, `47860` stars, `9991` forks.
- Binance USDⓈ-M Futures. *Compressed Aggregate Trades List*.
  - Readable URL: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Compressed-Aggregate-Trades-List>
  - Endpoint: `GET /fapi/v1/aggTrades`
