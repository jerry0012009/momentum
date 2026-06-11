# 别把 anti-chop 直接升级成反转模块：`1H ADX<18 + BB/RSI extreme` 还不够当 breakout-short / Fib / EMA-PSAR 的 shared range handoff
- 时间：2026-03-20 10:28 UTC
- 类型：GitHub 仓库 + Binance 公共数据快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/adx/bollinger/rsi/range-handoff/mean-reversion/chop/regime/filter/repo/crypto/5m/15m
- 证据类型：repo 规则骨架（工程证据）+ 公开行情代理快检（中等证据）

## 1. 这次看了什么
这轮主看 GitHub 仓库 **TheVision333/trading-bot** 里一条和当前三条收口线“反面问题”高度相关的旁支：`strategy/rr_signals.py`。

repo headline 是 **Range Mean Reversion**：
- `1H ADX(14) < 18` 先判成区间市；
- `15m` 再用 `Bollinger Bands(20,2) + RSI(14)` 找极值；
- 还要求下一根 candle 给一个反转确认（bullish/bearish 或 wick rejection）。

我这轮不想直接抄它做新策略，而是只问一个更贴我们 desk 的问题：

> **当 breakout-short / Fib retest_hold / EMA-PSAR continuation 被 anti-chop gate 拦下时，能不能顺手把同一段行情“交接”给一个简单的 `ADX<18 + BB/RSI` 反转模块？**

换成人话：
- `别追`，和 `反手做回归`，是两件不同的事；
- 我们现在已经有很多“别追”的理由，但还没有证据表明：**只要 ADX 低，就值得自动切到 mean-revert。**

## 2. 核心结论
1. **一句话核心结论：** `1H ADX<18` 更像三条收口线的 **skip / size-down 提醒**，还不够直接升级成 shared range handoff；`BB/RSI extreme` 在这个口径下没有稳定翻成可用的 15m 反转 edge。
2. **一句话证明方式：** repo 给了可编程规则骨架；我用 Binance Futures `BTC/ETH/SOL` 最近 `180d` 的 `15m + 1h` 公共 K 线，按 repo 的 `ADX<18 + BB/RSI extreme + next-candle confirm` 做最小代理，比较 range / non-range 下的短窗 mean-reversion 表现。
3. **关键数据点 1：`ADX<18` 覆盖面没有想象中大。** 最近 `180d` 里，`1H ADX<18` 只覆盖大约 **20.0%** 的 `15m` bar（BTC `16.5%`、ETH `19.7%`、SOL `23.9%`）。它更像局部 regime，不是全天候第二主系统的自然入口。
4. **关键数据点 2：pool 口径下，simple handoff 还没翻出正期望。** 在满足 repo 条件的确认事件里：
   - `range_adx<18`：`n=235`，**4-bar mean-reversion signed return = -5.43 bps**；
   - 同一批事件的 continuation proxy 反而是 **+5.43 bps**；
   - `trend_adx>=18`：`n=1046`，mean-reversion 也只有 **-3.74 bps**。
   也就是说，`ADX<18` 并没有把这批 BB/RSI 极值，稳定翻成“值得直接 fade”的 shared setup。
5. **关键数据点 3：就算按 repo 的第一目标去看，绝对命中率也偏弱。** 以 **BB 中轨** 作为最小 `TP1` 代理：
   - `range_adx<18` 下，**4 bar 内 hit rate 仅 11.9%**，**8 bar 内 20.0%**；
   - 对照 `trend_adx>=18`，分别是 **8.0% / 16.1%**。
   range 确实略有改善，但幅度还不足以支持“直接开一个共享反转模块”。
6. **关键数据点 4：跨资产不一致，不适合 shared 化。**
   - `BTC` 在 `ADX<18` 下接近打平：`-0.75 bps`，`mr_win_rate = 59.7%`；
   - 但 `ETH = -10.40 bps`、`SOL = -4.96 bps`；
   - 这更像 **BTC-specific 可疑旁支**，不是三条主线现在就该共用的 handoff。

## 3. 为什么这轮值得先做
这轮看似“偏题”，其实是在给三条收口线省时间。

### 3.1 对 `V3 final-verdict / breakout-short follow-up`
我们最近一直在补 `avoid-chop / failure / timeout / follow-up`。很自然会冒出一个诱惑：
- 既然 low-ADX 下不该追 breakout，
- 那是不是应该直接反手做回归？

这轮结论是：**先别这么快。**
`ADX<18` 可以继续留作 `skip short follow-up` 的负面 gate，但还不够支持“被 veto 的 breakout-short 自动改造成 fade entry”。

### 3.2 对 `Fibonacci confirmation / retest_hold`
Fib 线最近也在强化 `retest_hold` 的 honest confirm。区间市里，很多人会直觉把它写成“摸到边界就回中枢”。这轮提醒的是：
- **sideways ≠ automatic midline bounce alpha**；
- 对 Fib 来说，更值得保留的是 `hold / invalidate / timeout` 结构判决，
- 而不是因为 `ADX<18` 就把它降格成一个机械 BB 反转器。

### 3.3 对 `EMA / PSAR raw alpha focus`
EMA / PSAR raw alpha 现在最怕的是：
- 本体 edge 还没坐实，
- 先又长出一个“趋势不行时切回归”的并行系统。

这轮更诚实的角色判断是：
- `ADX<18` 可以先继续做 **少做 / 缩仓 / 不追**；
- 但 **别因为有 anti-chop，就默认同时拥有了 range alpha。**

## 4. 可复刻的最小实验（下一步怎么测）
### 4.1 数据与公开性
- 数据源：Binance Futures `15m / 1h` K 线（公开 API）
- 公开性：公开可得
- 更新频率：逐根 K 线更新
- 最小实验口径：`BTC/ETH/SOL perp`，先 `15m`，再看 `5m` 执行细化

### 4.2 首轮建议别直接做“handoff 上线”，而是做三臂对照
1. **A：skip-only**
   - 当 `1H ADX<18` 时，当前三条主线直接 `no-trade / size-down`；
2. **B：naive handoff**
   - `A` 的同时，允许 `BB/RSI extreme + next-candle confirm` 的 range reversion；
3. **C：conditioned handoff**
   - 只在 `ADX<18` **且** 下列至少一条成立时才允许 handoff：
     - `same-clock RVOL < 0.8`（说明更像 dry / range，而不是事件冲击）；
     - 无宏观 blackout；
     - 结构上先出现 `outside -> back-inside` 或局部 rejection，而不是单纯触带。

### 4.3 先看哪 4 个指标
- `post-cost expectancy`（6 / 10 / 15 bps per side）
- `TP1(midline) hit before timeout`
- `trade count retention / overlap`
- `asset consistency`

### 4.4 我对下一步的明确建议
- **先不要把它接成 shared handoff。**
- 更好的下一步不是继续调 `RSI 30/70` 或 `ADX 18`，而是验证：
  - `skip-only` 是否已经比 `naive handoff` 更干净；
  - 若还想保留反转旁支，只能去测 **更苛刻的 conditioned handoff**。

## 5. 风险与保留意见
- 这是 **repo 规则 + 公共 K 线代理** 快检，不是完整成交级回测；
- 我没有复刻 repo 的完整止损/分批止盈，只用了 `4-bar signed return` 与 `4/8-bar midline hit` 做最小代理；
- 结果不能推出“mean reversion 永远没用”，只能推出：**`ADX<18` 单独拿来做 shared handoff 还不够。**
- `BTC` 有一点点例外迹象，因此这条可以保留成 **BTC-specific park hypothesis**，但不该现在就升成三线共享模块。

## 6. 来源
1. **TheVision333. (2026). _trading-bot_. GitHub repository.**
   - Authors: GitHub user `TheVision333`
   - Year: 2026
   - Title: `trading-bot`
   - Venue: GitHub
   - DOI: `N/A`
   - Readable URL: `https://github.com/TheVision333/trading-bot`
   - Repo URL: `https://github.com/TheVision333/trading-bot`
2. **TheVision333. (2026). _RR-v1 — Range Mean Reversion_ (`strategy/rr_signals.py`).**
   - Authors: GitHub user `TheVision333`
   - Year: 2026
   - Title: `strategy/rr_signals.py`
   - Venue: GitHub
   - DOI: `N/A`
   - Readable URL: `https://github.com/TheVision333/trading-bot/blob/main/strategy/rr_signals.py`
   - Raw URL: `https://raw.githubusercontent.com/TheVision333/trading-bot/main/strategy/rr_signals.py`
   - Repo URL: `https://github.com/TheVision333/trading-bot`
3. **Wilder, J. W. (1978). _New Concepts in Technical Trading Systems_.**
   - Authors: J. Welles Wilder
   - Year: 1978
   - Title: `New Concepts in Technical Trading Systems`
   - Venue: Book
   - DOI: `N/A`
   - Readable URL: `https://en.wikipedia.org/wiki/Average_directional_movement_index`
   - Repo URL: `N/A`
4. **Binance. _USDⓈ-M Futures Market Data REST API: Kline/Candlestick Data_.**
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`
   - Data URL example: `https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=15m&limit=1500`
   - 公开性：公开 API
   - 更新频率：逐根 K 线更新

---
快检文件：
- `reports/artifacts/literature/range_handoff_rr_adx18_asset_summary_2026-03-20.csv`
- `reports/artifacts/literature/range_handoff_rr_adx18_pool_summary_2026-03-20.csv`
- `reports/artifacts/literature/range_handoff_rr_adx18_events_2026-03-20.csv`
- `reports/artifacts/literature/range_handoff_rr_adx18_meta_2026-03-20.json`
