# 别把 Fib retest_hold 默认写成“上一根 impulse 必须回抽 38–62 再续行”：它更像 second-chance branch，不是 shared hard gate
- 时间：2026-03-23 08:25 UTC
- 类型：GitHub 仓库 + Binance 公共数据最小快检
- 主题类型：filter
- 基础 alpha：breakout / fib retest continuation（既有 setup）
- 是否可独立复现：否
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：fibonacci/retest-hold/breakout-short/ema/psar/impulse-candle/next-bar/retracement/38-62/confirmation/filter/repo/crypto/15m/5m
- 证据类型：工程证据 + 本地快检（可复现）

## 1. 这次看了什么
这次看的是 **roshaneforde (2024) 的 `retracement-levels-indicator`**。它讲的不是“大 swing 的神奇 Fib”，而是一个很便宜的想法：**上一根方向很强的 candle，下一根是否会先回抽到前一根 range 的 38.2%~61.8%，再继续原方向。** 这和我们现在的 `Fibonacci confirmation / retest_hold` 很近，因为它能直接回答：15m 上要不要把“ textbook 回抽到 38~62 再走”写成默认确认层。

## 2. 核心结论
- **一句话核心结论：** 对 15m crypto，`上一根 impulse candle` 的 `Fib 38–62 回抽` 不适合升成三条收口线共享 hard gate；更诚实的角色是 **Fib setup 内部的 second-chance 进场分支**。
- **一句话证明方式：** 用 `BTC/ETH/SOL` 近 `180d` 的 Binance 15m 数据，先定义“前一根为 impulse bar”（`body/range>=0.6` 且收在边缘），再把下一根按回抽深度分成 `<38`、`38~62`、`>62` 三桶，比较 continuation 表现。

本地最小快检（pooled，`n=14,786`）里：
- 桶占比：`deep > 62% = 38.1%`，`Fib 38~62 = 28.7%`，`shallow < 38 = 33.3%`；
- **同根延续**（下一根本身继续收在 impulse 同方向）：`shallow 82.9%`，`Fib 42.2%`，`deep 14.3%`；
- **4-bar continuation**：`shallow 50.13%`，`Fib 49.40%`，`deep 49.96%`，几乎没拉开；
- **4-bar signed return**：`shallow +4.23bps`，`Fib +2.27bps`，`deep -2.90bps`；而全体 impulse baseline 约 `+1.95bps`。

可执行读法：**如果你把“下一根必须回到 38~62”写成默认放行条件，会把样本砍到只剩 28.7%，但并没有换来更好的 4-bar 延续。**

## 3. 为什么和当前三条收口线直接相关
- **Fibonacci confirmation / retest_hold**：这是最直接的帮助。它说明 `38~62` 更像 Fib 线路内部的“等回踩再上车”分支，不像 universal truth。
- **V3 final-verdict / breakout-short follow-up**：很多 breakout 的最快延续其实发生在 `shallow < 38`，如果默认强等 textbook retest，会错过最顺的一段。
- **EMA / PSAR raw alpha focus**：EMA/PSAR continuation 若想加回踩确认，先别直接继承 Fib 教条；应该把“no-wait continuation”和“wait-for-pullback”拆成两条 entry lane。

## 3.5 策略拆解（角色定位）
- 方向属性：顺势 continuation / 二次进场，不是独立 raw alpha。
- 基础 alpha：breakout / EMA continuation / Fib retest 既有 setup。
- regime：无额外 regime 结论，本轮只回答“entry style 怎么分支”。
- filter / veto：`deep > 62%` 可做降级或 veto；`38~62` 不应自动升 shared hard gate。
- risk / sizing / execution overlay：`38~62` 更适合当 wait-for-pullback lane；`shallow < 38` 更适合 no-wait lane。

## 4. 可复刻的最小实验（下一步怎么测）
- **研究假设：** 对 15m，最诚实的不是“统一等 Fib 回踩”，而是 **双路由**：
  1. `shallow < 38` → continuation fast lane；
  2. `38~62 + reclaim` → retest_hold second-chance lane；
  3. `deep > 62` → veto 或 size-down。
- **一个可计算定义：** 事件起点用 breakout / EMA impulse bar；下一根或后两根的最深回抽，相对上一根 range 分桶；只有 `38~62` 桶再额外要求 same-side reclaim close。
- **最小回测切口：** `BTC/ETH/SOL` perpetual，`15m`，近 `180d`，next-bar open，no-overlap，成本 `6/10/15bps`。
- **先看 4 个指标：** `post_cost_expectancy`、`trade_count_retention`、`missed_winner_ratio`、`MAE/MFE by bucket`。

## 5. 风险与保留意见
- 这个 repo 本来主打的是 `H12 -> H1` 的外汇/贵金属读法；我们这里只把它当**可映射到 15m 的结构假设**，不是照单全收它的原始宣传。
- 本轮是轻量快检，还没把“breakout 事件”“EMA 事件”“Fib swing 事件”彻底分开；真正升格前，必须做 setup-specific A/B。
- `previous-candle Fib` 和“大 swing Fib”不是同一件事；如果后续 swing 级实验结论不同，不冲突。

## 6. 来源
1. **roshaneforde. (2024). _Retracement Levels Indicator_. GitHub Repository.**
   - Authors / Year / Title / Venue: roshaneforde / 2024 / Retracement Levels Indicator / GitHub Repository
   - DOI: N/A
   - Readable URL: https://github.com/roshaneforde/retracement-levels-indicator
   - Repo URL: https://github.com/roshaneforde/retracement-levels-indicator
2. **Binance USDⓈ-M Futures Market Data API（最小实验数据口径）**
   - 数据源：Binance Developers（公开可得）
   - 更新频率：分钟级（可直接聚合 15m）
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data
   - Repo URL: https://github.com/binance/binance-futures-connector-python

## 7. 本地复现产物
- `reports/artifacts/quant_digests/prev_candle_fib_nextbar_20260323/btcusdt_events.csv`
- `reports/artifacts/quant_digests/prev_candle_fib_nextbar_20260323/ethusdt_events.csv`
- `reports/artifacts/quant_digests/prev_candle_fib_nextbar_20260323/solusdt_events.csv`
- `reports/artifacts/quant_digests/prev_candle_fib_nextbar_20260323/pooled_summary.csv`
- `reports/artifacts/quant_digests/prev_candle_fib_nextbar_20260323/summary_by_asset.csv`
- `reports/artifacts/quant_digests/prev_candle_fib_nextbar_20260323/meta.json`
