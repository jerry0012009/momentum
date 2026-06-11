# 别把 Fib 在 breakout 当场就画死：`confirmed extremum after BMS` 更像 15m retest_hold 的 honest anchor
- 时间：2026-03-19 22:20 UTC
- 类型：GitHub + 本地代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/bos/extremum/fib-anchor/confirmation/state-machine/repo/crypto/15m
- 证据类型：repo 规则（工程证据）+ 公开行情代理快检

## 1. 这次看了什么
主来源是 **Madrycrypto (2026) 的 `fibo71-bot`**。这次不复刻它最显眼的 `0.71-0.79` 深回踩主张，而是抽它源码里一个更适合我们 desk 的旁支：**BOS 后先追踪 post-break 极值，只有当价格重新穿回被突破的 BMS level，才把那个 extremum 冻结下来画 Fib。**

## 2. 核心结论
1. **一句话核心结论**：对 5m/15m 的 `Fib confirmation / retest_hold`，更该先确认“这一段 impulse 到底走到哪儿结束”，再谈回撤深浅；否则 Fib 很容易画早了。
2. **一句话证明方式**：repo 的状态机明确要求 `BMS -> tracking extremum -> close back through BMS level -> calculate Fibonacci`，不是 break 出去当根就立刻定锚。
3. 本地代理快检（BTC/ETH/SOL 永续，15m，近 120d）显示，这不是形式主义：
   - 有效 breakout 里，**62.7%** 会在 `12` 根内出现 `confirmed extremum`；
   - 一旦确认，最终 extremum 相比 breakout 当根 extreme 的额外延伸中位数约 **0.20 ATR**，75 分位约 **0.67 ATR**，90 分位约 **1.45 ATR**；
   - 若把“价格回到 broken level”视作一次最小回踩，**12.6%** 的事件会因为 extremum 重新冻结而落入**不同 Fib 深度桶**。
4. 最常见的重分类不是深区，而是：原本看起来只是 `<38.2%` 的浅回踩，确认后会被改判成 `38.2-50%`，甚至 `50-61.8%`。也就是说，**不少所谓“太浅、不能做”的回踩，只是因为你把锚点画早了。**

## 3. 为什么和当前项目有关
- **Fib retest_hold（最直接）**：它先解决“回踩深度怎么算”这个上游口径问题，比继续争 `0.5 / 0.618 / 0.71` 谁神更基础。
- **V3 breakout-short follow-up**：break 后若一直没出现“穿回 broken level”的确认，说明 impulse 还在延伸，过早做 failure verdict 容易把 continuation 当成反转。
- **EMA / PSAR raw alpha**：EMA/PSAR 继续做方向层；`confirmed extremum` 可以做执行层 admission，避免把同一段延伸腿误读成已经进入成熟 pullback。

## 4. 可复刻的最小实验
### 4.1 数据源与公开性
- 数据源：Binance USDⓈ-M Futures 公共 K 线
- 公开性：公开可得
- 更新频率：15m（本轮代理）

### 4.2 最小定义
- breakout：`close > prev_high_20` 或 `close < prev_low_20`，且 `body_ratio >= 0.40`、`extension >= 0.20 ATR`
- provisional extremum：breakout 当根 `high/low`
- confirmed extremum：breakout 后继续跟踪极值；只有当价格 **收回 broken level 对侧**，才冻结 extremum
- 对照：
  1. `provisional-anchor Fib`
  2. `confirmed-anchor Fib`

### 4.3 下一步怎么测
先在现有 `fib_retest_long` / `breakout-short follow-up` 上做一个最小 A/B：
1. A 组：breakout 当根就锚 Fib；
2. B 组：等 `confirmed extremum` 后再锚 Fib；
3. 先看 4 个指标：`post_cost_expectancy`、`depth_bucket distribution`、`retest_hit_rate`、`false-failure rate`。

## 5. 风险与保留意见
- 这是 repo 里的工程状态机启发，不是已发表论文结论。
- 代理实验只证明“锚点常被改写”，还没证明“confirmed-anchor` 一定直接转正 alpha`”；它更像 **honest anchor / 口径修正层**。
- 若行情单边过强、迟迟不穿回 broken level，这个规则会天然更慢，因此它更适合服务 `retest_hold / failure verdict`，不适合拿来替代所有 breakout continuation 进场。

## 6. 产物与留痕
- 代理实验明细：`reports/artifacts/quant_digests/confirmed_extremum_anchor_proxy/event_summary.csv`
- 代理实验摘要：`reports/artifacts/quant_digests/confirmed_extremum_anchor_proxy/summary_snapshot.json`

## 7. 来源
1. Madrycrypto. (2026). *fibo71-bot: Fibo 71 Trading Bot - Fibonacci retracement strategy with BOS detection*. GitHub Repository.
   - Authors: Madrycrypto
   - Year: 2026
   - Title: fibo71-bot
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: https://github.com/Madrycrypto/fibo71-bot
   - Repo URL: https://github.com/Madrycrypto/fibo71-bot
2. Madrycrypto. (2026). *BMS Fibo Liquidity Strategy* (`README_BMS_STRATEGY.md`).
   - Authors: Madrycrypto
   - Year: 2026
   - Title: BMS Fibo Liquidity Strategy - Kompletna Dokumentacja
   - Venue: GitHub Docs
   - DOI: N/A
   - Readable URL: https://github.com/Madrycrypto/fibo71-bot/blob/main/README_BMS_STRATEGY.md
   - Raw URL: https://raw.githubusercontent.com/Madrycrypto/fibo71-bot/main/README_BMS_STRATEGY.md
3. Madrycrypto. (2026). *BMS Fibonacci Liquidity Strategy implementation* (`src/strategies/bms_fibo_liquidity_strategy.py`).
   - Authors: Madrycrypto
   - Year: 2026
   - Title: bms_fibo_liquidity_strategy.py
   - Venue: GitHub Source
   - DOI: N/A
   - Readable URL: https://github.com/Madrycrypto/fibo71-bot/blob/main/src/strategies/bms_fibo_liquidity_strategy.py
   - Raw URL: https://raw.githubusercontent.com/Madrycrypto/fibo71-bot/main/src/strategies/bms_fibo_liquidity_strategy.py
4. Binance. (2026). *USDⓈ-M Futures API — Kline/Candlestick Data*.
   - Authors: Binance
   - Year: 2026
   - Title: USDⓈ-M Futures REST API / Kline-Candlestick Data
   - Venue: Binance Developers
   - DOI: N/A
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data
   - Repo URL: N/A
