# 别把这份 funding-rate repo 只读成“资金费率预测方向”：对 short-cycle desk，更该先保留的是「extreme funding fade × 2% TP volatility harvest」这条完整 raw alpha 壳

- 时间：2026-04-16 02:57 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `Funding_Rate_Signal_Analysis.pdf` + `signals/zscore.py` + `signals/filters.py` + `backtest/engine.py` + `config.yaml` + GitHub API metadata）+ Bybit public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：**当 perp funding rate 的长窗 z-score 进入极端区间时，市场通常已进入拥挤单边；真正更稳的交易，不是赌完整趋势反转，而是反着 crowd 只收第一段 snapback——也就是 `extreme funding fade × tight TP volatility harvest`。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（**repo 已把 lookback / threshold / volume+OI filters / SL-TP / fixed position size / maker-taker fee 都写进完整回测壳**）
- 主题标签：raw-alpha/funding/carry/crowding/mean-reversion/volatility-harvest/tight-tp/oi-filter/volume-filter/bybit/perpetual/8h-event/5m/15m/repo/public-data/cost/risk
- 证据类型：repo source + bundled research memo + public-data probe

## 1. 这次看了什么

这轮看的是新仓：

- **Author：** Farrell H
- **Year：** 2026
- **Title：** *Crypto Funding Rate Strategy*
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/farrellh1/crypto-funding-rate-strategy>
- **Repo URL：** <https://github.com/farrellh1/crypto-funding-rate-strategy>
- **GitHub metadata：** repo 创建于 `2026-01-25`，最近 push 于 `2026-01-26`

先把一句话说清楚：

> **这篇东西的 base alpha 不是“funding 很高就一定跌 / funding 很低就一定涨”。更值钱的，是把 funding extreme 当成“拥挤事件触发器”，然后只吃第一段回摆，而不是贪完整反转。**

所以它不是纯 filter，也不是只会解释 crowding 的研究 memo；它本体仍是一条 **event-driven raw alpha shell**。

## 2. repo 真正有价值的地方

`signals/zscore.py` 把假设拆得很干净：
- 先对 funding 做 `168` 个 funding interval（约 `56d`）的 rolling z-score；
- z-score 超阈值才触发；
- 可选再加：
  - `8h` 聚合成交量 z-score 过滤；
  - open interest z-score 过滤；
- `backtest/engine.py` 再把 `SL / TP / opposite signal exit / backtest end`、fixed USD sizing、maker/taker fee 与 slippage 全接上。

这点对 desk 很重要，因为它不是“只给一个 signal idea”，而是已经把：
**entry / exit / sizing / cost / risk** 都搭成了可直接 smoke test 的完整壳。

## 3. bundled PDF 给出的第一结论

repo 自带的 `Funding_Rate_Signal_Analysis.pdf` 用 **BTCUSDT / Bybit / 2022-01 ~ 2025-12** 做了一个很有用的 A/B 矩阵：

- **Test A：** mean reversion + `2% SL / 4% TP`
- **Test B：** mean reversion + `4% SL / 2% TP`
- **Test C：** momentum + `2% SL / 4% TP`
- **Test D：** momentum + `4% SL / 2% TP`

PDF 里 after-cost 结果最值得记的不是“funding 能预测方向”，恰恰相反：

- **A：** `-$1,207`，Sharpe `-3.88`，Trades `37`
- **B：** `+$804`，Sharpe `2.71`，Max DD `1.29%`，Trades `36`，Win Rate `72.22%`
- **C：** `-$2,196`，Sharpe `-7.66`，Trades `36`
- **D：** `-$207`，Sharpe `-0.65`，Trades `37`

也就是说：

> **repo 自己最强的证据不是“押方向押对了”，而是 “funding extreme 之后有足够的短时波动，可让 opposite-side tight TP 先兑现”。**

这比“funding 解释价格”更适合 short-cycle desk，因为它更接近一个可执行的事件 alpha 壳。

## 4. public-data portability probe：recent majors 不同币、不同 sign

我另外补了一个最小迁移快检，artifact 在：

- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-16_funding_zscore_extremes_probe.py`
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-16_funding_zscore_extremes_probe_summary.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-16_funding_zscore_extremes_probe_summary.json`

口径：
- **数据源：** Bybit V5 public funding / klines / open interest
- **公开性：** 公开接口，无需 API key
- **更新频率：** funding `8h`、kline `1h`、OI `4h`
- **样本：** `2025-01-01 ~ 2026-04-01`
- **标的：** `BTCUSDT / ETHUSDT / SOLUSDT`
- **统一参数：** `lookback=168`、`threshold=2.0`、fixed size `$10k`、Bybit taker round-trip cost 约 `11bps`

几条关键数：

- **BTC mean reversion + vol/OI filter：** `9` 笔，net `+1.10%`，Sharpe `20.24`，Max DD `0.51%`
- **ETH momentum plain：** `33` 笔，net `+1.44%`，Sharpe `5.52`
- **SOL momentum plain：** `31` 笔，net `+2.26%`，Sharpe `10.01`
- **ETH mean reversion + vol/OI filter：** `16` 笔，net `-2.38%`

所以 first verdict 很明确：

> **这套壳值得保留，但别把“funding extreme 的方向”写死。BTC 最近更像 fade pocket，ETH/SOL 反而更像 continuation pocket。**

也就是说，真正可复用的不是“统一押反向”，而是：
- 用 funding z-score 定义事件；
- 再决定某个 symbol/venue 到底该走 **fade** 还是 **follow**；
- exit 默认先保留 tight TP，而不是幻想吃完整趋势段。

## 5. 为什么它和当前 desk 直接相关

这题虽然底层事件是 `8h` funding print，但并不妨碍短周期实验，原因是它天然适合作为：

- `5m / 15m` 的 **event router**
- 资金费率结算窗口前后的 **event-driven raw alpha**
- carry / funding 线里的 **最低门槛完整基线**

尤其我们这几轮已经积了不少 funding / basis / carry 题材，但很多更像：
- venue spread
- delta-neutral carry
- cross-venue ranking

这份 repo 的价值反而是把问题收敛成更朴素的一句：

> **“funding extreme 发生时，到底能不能只靠 public data、固定风控、固定成本，先打出一个最小可活的方向壳？”**

它给出的答案是：**可以先打，但 edge 更像 `tight TP` 的 volatility harvest，而不是无脑押大反转。**

## 6. 下一步怎么测

按 desk 口径，我建议下一轮不要继续抄 repo 的 `1h` 执行，而是直接做三件事：

1. **把事件映射到 `5m / 15m` 执行层**
   - 在 `00/08/16 UTC` funding print 后第一根 `5m` / `15m` bar 开始入场；
   - 对比 `fade` vs `follow` 两支。
2. **做 symbol-specific sign split**
   - BTC 默认先测 `fade + 2% TP`；
   - ETH/SOL 默认先测 `follow + 2% TP`；
   - 不再强行全市场统一方向。
3. **补更诚实的 friction ladder**
   - `maker/maker`、`maker/taker`、`taker/taker` 三档；
   - 再看这条线到底是“真的 alpha”，还是只是 repo 的 low-trade backtest 幻觉。

如果这三步里 `5m/15m` 版还能在 recent majors 留下正的 post-cost pocket，这条线就值得继续升成 desk 的 funding-event baseline。否则它也依然值钱——因为它已经告诉我们：

> **funding extreme 更像“事件触发器”，真正要优化的是 sign router 与 exit geometry。**
