# 别把 `OBI` 当盘口神谕：对 breakout / Fib / EMA，更像该先测的是主动买卖量失衡 veto
- 时间：2026-03-18 09:41 UTC
- 类型：GitHub
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/microstructure/order-flow/filter/repo/crypto/15m
- 证据类型：仓库规则 + 公开数据可复现实验

## 1. 这次看了什么
这次看的是 GitHub 仓库 `tsuithomas/crypto_research_order_book_imbalance`（2026）。它表面上写的是 `Order Book Imbalance`，但真正落到代码里，并没有抓完整 L2 深度，而是用 Binance `aggTrades` 的主动买/卖成交量，算 `obi = (buy_vol - sell_vol) / volume`，再去预测 **5 分钟 forward return**。对我们 desk 来说，最值钱的不是它的 XGBoost 外壳，而是它提醒了一件很实用的事：**很多 15m breakout / retest / EMA 信号，缺的不是再一层价格确认，而是一个更快的“这一下到底有没有真跟随盘”判断。**

## 2. 核心结论
- **一句话核心结论**：这个 repo 最值得抄的，不是把 15m 做成高频模型，而是把 `OBI` 退火成一个更诚实的 **主动买卖量失衡 gate / veto**，专门回答“这次 breakout / retest / EMA 动作，背后到底有没有真实单边压力”。
- **一句话证明方式**：作者用 Binance 公开 `aggTrades` 做特征工程，1 分钟重采样后预测 5 分钟收益；在 README 里给出的结果中，`obi` 约占 **45% feature importance**，说明这个 pressure proxy 至少在作者样本里不是装饰变量。
- 但 repo 也顺手给了一个很重要的负面信息：**高频 alpha 一扣真实成本就很容易死**。README 写得很直白：用 aggressive taker 执行、跨点差再加 **4~8 bps** taker fee 时，净收益转负；只有改成 **1 bps maker** 假设、再加 **15 bps predictive threshold**，策略才翻成 **+3.21%**，而同期市场是 **-12.76%**。这对我们的启发不是“去做 HFT”，而是 **把它降级成 15m 的 entry veto / sizing overlay**。
- 还有一个对 desk 特别友好的地方：它并不依赖付费 OI、funding 或专有盘口库，而是直接用 Binance 公开 `GET /fapi/v1/aggTrades`。这意味着它不是“理论可得”，而是今天就能抓、今天就能映射到 `5m / 15m` 最小实验。
- 更关键的是，它正好补当前三条收口线都还缺的一层：**参与度是否朝信号方向倾斜**。`breakout-short` 需要它区分“真破位继续”还是“空头一脚踩空”；`Fib retest_hold` 需要它区分“回踩后真有人接”还是“只是位置到了”；`EMA / PSAR` 需要它区分“均线翻向有跟随”还是“低参与度空转”。

## 3. 为什么和当前项目有关
这题比继续写一篇 price-only confirmation 更值得，是因为它不是偏题，而是在给三条线补一个**共享的、因果更近的微观压力层**：
- 对 `V3 final-verdict / breakout-short follow-up`：最自然的用法不是让 `OBI` 决定方向，而是只在 **破位当下和破后 1~3 分钟仍持续卖压占优** 时才保留 short continuation；如果价格新低但主动卖压迅速衰减，反而更像 dead-on-arrival。
- 对 `Fibonacci confirmation / retest_hold`：很多“回到 0.5 / 0.618 后拉起”的 setup，问题不在 Fib 位，而在 **回踩后没有真实买盘吸收**。所以 `Fib hit + reclaim` 之后，再看最后几分钟的主动买量失衡是否同向，逻辑上比再堆一层形态更干净。
- 对 `EMA / PSAR raw alpha focus`：它可以当一个独立于价格形状的 participation gate。EMA / PSAR 继续给方向，主动买卖量失衡只回答“这次翻向是不是有人真在推”。这样比拿更多均线互相证明要健康。

## 4. 可复刻的最小实验
- **研究假设**：把 `aggTrades` 压成一个 15m 之前的微观压力特征后，`breakout / retest / EMA-PSAR` 信号在同向主动成交占优时，后续 `2~4 bar` 延续更强、反抽/假破更少。
- **公开数据源**：Binance USDⓈ-M Futures `GET /fapi/v1/aggTrades`，公开可得、最多看回 **1 年**，单次 `startTime-endTime < 1h`，返回字段含 `q`（quantity）和 `m`（buyer was maker）。这个 `m` 足够把成交拆成主动买/主动卖代理。
- **最小可计算定义**：
  1. 先把 `aggTrades` 重采样成 `1m`；
  2. `buy_vol = sum(q where m == false)`，`sell_vol = sum(q where m == true)`；
  3. `flow_imb_1m = (buy_vol - sell_vol) / (buy_vol + sell_vol + 1e-8)`；
  4. 映射到 15m setup 前，定义 `flow_align = mean(flow_imb_1m[-3:])` 或 `sum(sign(flow_imb_1m[-5:]) == direction)`。
- **第一轮 bucket**：
  1. `base`：现有 `breakout-short / fib retest_hold / EMA-PSAR raw`；
  2. `+ same-direction flow gate`：long 要 `flow_align > 0`，short 要 `< 0`；
  3. `+ strong-flow gate`：要求 `|flow_align|` 进入过去 20 个 15m setup 的上半区；
  4. `opposite-flow veto`：若价格触发但 `flow_align` 反向，直接禁入。
- **最先看的 4 个指标**：`2/4 bar follow-through`、`false-break / false-hold rate`、`net expectancy @ 6/10 bps per side`、`trade count retention`。
- **下一步怎么测**：别先上 ML。第一轮就做最笨、最诚实的 ablation：在 `BTC / ETH / SOL` perpetual 的最近 `90~180` 天 15m 上，只问一个问题——**当价格信号已经出现时，最后几分钟的主动成交失衡，能不能稳定压低假突破/假回踩？** 如果可以，它就值得进三条线共用的 `pressure veto`；如果只有在极低成本或极少样本下才好看，就别把它吹成主 alpha。

## 5. 风险与保留意见
- repo 名字叫 `order_book_imbalance`，但代码里实际上是 **trade-flow imbalance proxy**，不是完整盘口深度失衡；这一点必须说清，不然很容易高估证据强度。
- 作者的正收益依赖 `maker + threshold` 假设，说明它对交易成本非常敏感。对我们来说，这更支持“当 filter / veto”，不支持“直接当主交易器”。
- 公开 `aggTrades` 虽然可得，但 `start-end < 1h`，抓长窗历史要做稳定分页与缓存；工程成本不高，但不是零。
- repo 很新，`0 stars / 0 forks`，社会证明几乎没有；我们继承的是它的**可复现思路**，不是它的权威性。

## 6. 来源
- Tsui, Thomas. (2026). *crypto_research_order_book_imbalance*. GitHub repository.
  - Venue / DOI：GitHub / N/A
  - Repo URL: <https://github.com/tsuithomas/crypto_research_order_book_imbalance>
  - Readable URL: <https://github.com/tsuithomas/crypto_research_order_book_imbalance>
  - Raw README: <https://raw.githubusercontent.com/tsuithomas/crypto_research_order_book_imbalance/main/README.md>
  - Raw feature engineering: <https://raw.githubusercontent.com/tsuithomas/crypto_research_order_book_imbalance/main/src/feature_engineering.py>
  - Raw backtester: <https://raw.githubusercontent.com/tsuithomas/crypto_research_order_book_imbalance/main/src/backtester.py>
  - Repo API: <https://api.github.com/repos/tsuithomas/crypto_research_order_book_imbalance>
  - Repo metadata snapshot: created `2026-03-03`, updated `2026-03-03`, `0` stars, `0` forks.
- Binance USDⓈ-M Futures. *Compressed Aggregate Trades List*.
  - Readable URL: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Compressed-Aggregate-Trades-List>
  - Endpoint: `GET /fapi/v1/aggTrades`
- Binance USDⓈ-M Futures. *Order Book*.
  - Readable URL: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Order-Book>
  - Endpoint: `GET /fapi/v1/depth`
