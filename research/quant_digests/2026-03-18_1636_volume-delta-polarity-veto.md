# 别把外部 flow veto 再重演一遍：对 15m 来说，更便宜先测的是 lower-TF volume-delta polarity mismatch
- 时间：2026-03-18 16:36 UTC
- 类型：GitHub
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/volume-delta/divergence/filter/repo/crypto/15m
- 证据类型：仓库脚本 + 公开 OHLCV / lower-TF 可复现实验

## 1. 这次看了什么
这次看的是 GitHub 仓库 `Dropio12/MTF-EMA-ALMA-Strategy-with-RSI-Supertrend-and-Advanced-Volume-Delta-Divergence-Visualization`（2024）。这不是一份适合整仓照抄的策略模板，反而像一个典型的“把太多东西塞进一个 Pine 脚本”的大杂烩；但它里面有一块旁支思路，反而非常适合我们现在的 desk：**别再把 volume-delta 当 15m 主信号去单独开仓，而是把 lower-TF volume-delta 与价格 K 线方向是否同向，降级成 shared veto / confirmation layer。** 这对 `breakout-short follow-up`、`Fib retest_hold`、`EMA / PSAR raw alpha focus` 都是同一个问题——价格动作已经出来了，但这一下到底有没有真实跟随，还是只是“形状上看起来像”。

## 2. 核心结论
- **一句话核心结论**：这份 repo 最值得偷的不是它 README 里那些夸张回测数字，而是一个更朴素、也更适合 15m 的问题：**当 setup 触发时，若 lower-TF volume-delta polarity 和价格方向相反，就把它当 veto；若同向，只把它当 continuation-confirmation，而不是主 alpha。**
- **一句话证明方式**：源码里真正可抽离的结构很清楚：它用 `request.security_lower_tf(...)` 去抓更低周期数据，`Auto` 模式下对 `<=15m` 图表默认落到 **30 秒** 子周期；随后用子周期 `close-open` 或 candle pressure 近似拆分买/卖量，再在图上专门标记 **“价格 K 线方向 vs volume delta 符号不一致”** 的 bar。这其实已经不是“找新方向”，而是在做 **failure / participation veto**。
- 这题现在比继续追“外部 aggTrades flow veto”更值得测，原因很直接：我们今天已经把 `trade-flow imbalance veto` 那条外部数据线跑到 `park / evidence pool`，说明“更强、更贵、更接近真实成交”的外部 flow 不一定自然能救 15m setup。那下一步最该问的，不是再找更花的微结构源，而是：**更便宜、更好部署的内生 proxy，能不能保住一部分 veto 价值？**
- 这也是它比继续堆新的 price-only confirmation 更值钱的地方：它不是偏题，而是在给三条收口线补一层**共享、低摩擦、容易批量回测的参与度判断**。尤其对 `EMA / PSAR raw alpha focus` 来说，这很像当前最该补的那块——不是再多一条均线，而是一句“翻向时到底有没有跟随量”。
- 但要先把口径压诚实：这不是交易所逐笔 bid/ask volume delta，也不是完整 order-flow reconstruction；它只是 **public lower-TF OHLCV 上的 delta proxy**。如果这种粗糙 proxy 都没有边，那更没必要继续美化它。

## 3. 为什么和当前项目有关
这题值得现在做，不是因为它“新”，而是因为它正好卡在三条收口线共同缺的那一层：
- 对 `V3 final-verdict / breakout-short follow-up`：最实用的读法不是“破位时 delta 为负就追空”，而是 **价格已经给出 short continuation 结构后，若最近 3~5 分钟的 lower-TF delta 明显转正，直接把这次 follow-up 降级或 veto**。它回答的是“这波破位有没有真空头跟随”。
- 对 `Fibonacci confirmation / retest_hold`：很多 `0.5 / 0.618` 回踩的问题不在 Fib 位，而在 **回踩后抬头那一下没有真实参与**。如果 retest 刚出现，lower-TF delta 仍持续逆向，那就比再堆一层形态共振更像有效否决条件。
- 对 `EMA / PSAR raw alpha focus`：它最适合作为一个与价格形状半独立的 participation gate。EMA / PSAR 继续给方向和结构，delta proxy 只回答一句话——**这次翻向/延续是不是有人在推，而不是自己空转。**
- 更关键的是，这个方向能直接对照今天已经被 park 的 `trade-flow imbalance veto`：如果外部 aggTrades 版本太重、太贵、OOS 不稳，而 lower-TF OHLCV proxy 反而能留下更朴素的 veto 效果，那 desk 更该要后者。

## 4. 可复刻的最小实验
- **研究假设**：对现有 `breakout-short / fib retest_hold / EMA-PSAR raw` setup 来说，若入场前最后一段 lower-TF volume-delta polarity 与信号方向相反，则后续 `2~4 bar` follow-through 更差、假突破/假守住更高；反之，同向时 setup 的 continuation 质量更好。
- **公开数据源**：同一交易所的公开 `kline/candlestick` 数据即可，不要求逐笔成交。最小可行版本直接用 Binance USDⓈ-M Futures `GET /fapi/v1/klines`；字段里天然有 `open/high/low/close/volume`，更新时间随 bar 刷新。若 30 秒数据不方便统一抓取，第一轮可以退到 **1m 子周期 proxy**，先测方向性，不先追求最细粒度。
- **最小可计算定义**：
  1. 以 `15m` 为主图，给每个 setup 对齐一个 `1m`（或可得时 `30s`）子周期窗口；
  2. 对每个子 bar 先定义最朴素 delta proxy：`sub_delta = +volume` 当 `close > open`，`sub_delta = -volume` 当 `close < open`；可选进阶版再试 repo 里的 candle-pressure 口径：`(close-low) > (high-close)` 记为买压，否则卖压；
  3. `delta_align_pre5m = sum(sub_delta over last 5m) / sum(volume over last 5m)`；
  4. long setup 要求 `delta_align_pre5m > 0`，short setup 要求 `< 0`；若相反，则记为 `opposite_delta_veto = 1`；
  5. 可再补一个更硬的否决：`mismatch_share = share(sub bars whose sign != setup direction)`，若过去 `5m` 里逆向占比超过 `60%`，直接禁入。
- **第一轮 bucket**：
  1. `base`：现有 setup 原样；
  2. `same-direction delta gate`：只保留 pre-entry delta 同向样本；
  3. `opposite-delta veto`：只删除 pre-entry delta 反向样本；
  4. `strong-same-direction only`：要求 `|delta_align_pre5m|` 进入过去 20 次 setup 的上半区。
- **最先看的 4 个指标**：`2/4/8 bar forward return`、`false-break / false-hold rate`、`trade count retention`、`net expectancy @ 6/10 bps per side`。
- **下一步怎么测**：先别引进新的复杂特征，也别把 delta 算到入场后。第一轮就固定 `BTC / ETH / SOL` perpetual、最近 `120d`、`15m` 主图、`next-bar open` 入场、`no-overlap` 持有 `4~8 bars`，只比较 `base` vs `same-direction gate` vs `opposite veto`。如果 `opposite-delta veto` 能在不把样本砍废的前提下，稳定压低 `false-break / false-hold`，它就值得进三条线共用的 shared confirmation layer；如果它只在极少样本或零成本假设下才好看，就直接 park。

## 5. 风险与保留意见
- 这份 repo 是明显的 kitchen-sink script：EMA、ALMA、RSI、Supertrend、order block、volume delta 全堆在一起。**不要把整份脚本当作高质量策略证据**；真正可继承的只有其中那块 lower-TF delta mismatch 思路。
- README 里写的 `15m 96.7% win rate`、`Sharpe 22.1` 这类数字，当前都不该当成证据；这轮研究只把它们视为营销噪音，不进入 desk 的有效证据集。
- lower-TF OHLCV 推出来的 `volume-delta` 只是 proxy，不是逐笔成交方向，更不是订单簿失衡；所以它天然更适合当 **filter / veto**，不适合被包装成独立主信号。
- 时间对齐必须非常严格：只能用 **setup 触发前** 的子周期窗口，不能把 setup bar 里入场后的 volume 倒灌回 delta 判断，否则会直接污染结果。
- 如果 `1m` 版 proxy 已经没有任何稳定边际，就没必要再为 `30s` / 更复杂 candle-pressure 版本追加工程预算。

## 6. 来源
- Dropio12; Kokoabe. (2024). *MTF-EMA-ALMA-Strategy-with-RSI-Supertrend-and-Advanced-Volume-Delta-Divergence-Visualization*. GitHub repository.
  - Venue / DOI：GitHub / N/A
  - Repo URL: <https://github.com/Dropio12/MTF-EMA-ALMA-Strategy-with-RSI-Supertrend-and-Advanced-Volume-Delta-Divergence-Visualization>
  - Readable URL: <https://github.com/Dropio12/MTF-EMA-ALMA-Strategy-with-RSI-Supertrend-and-Advanced-Volume-Delta-Divergence-Visualization>
  - Raw README: <https://raw.githubusercontent.com/Dropio12/MTF-EMA-ALMA-Strategy-with-RSI-Supertrend-and-Advanced-Volume-Delta-Divergence-Visualization/main/README.md>
  - Raw strategy: <https://raw.githubusercontent.com/Dropio12/MTF-EMA-ALMA-Strategy-with-RSI-Supertrend-and-Advanced-Volume-Delta-Divergence-Visualization/main/strategy>
  - Repo metadata snapshot: created `2024-08-22`, updated `2024-08-22`, `3` stars, `1` fork.
- Binance USDⓈ-M Futures. *Kline Candlestick Data*.
  - Readable URL: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>
  - Endpoint: `GET /fapi/v1/klines`
  - Example fields used in the minimal experiment: `open`, `high`, `low`, `close`, `volume`, `taker buy base asset volume`.
