# 别把 HTF `premium/discount` 当多空对称 shared gate：repo 里的 `prev-4h range midline` 在 15m 更像 Fib retest / EMA continuation 的 long-side context，不适合 breakout-short
- 时间：2026-03-20 03:23 UTC
- 类型：GitHub + 本地代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/fib/premium-discount/h4/context/asymmetry/continuation/filter/repo/crypto/15m
- 证据类型：工程证据（仓库源码）+ 代理快检（公开行情）

## 1. 这次看了什么
这轮主看 GitHub 仓库 **carlosrod723 / MQL5-Trading-Bot (2025)**。真正值得偷的不是它整套 SMC + ML 外壳，而是一个很轻、很快能复现的旁支：
- 用 **上一根完整 H4 K 线的 high / low** 定义 Fib 区间；
- 用 `mid = low + 0.5 * (high-low)` 把当前价格分成 `premium / discount`；
- 在它的 `FT (Follow-Through)` 里，**bullish 只在 discount 放行，bearish 只在 premium 放行**。

源码很直白：`GetFibonacciZone()` 直接取 `HigherTF` 上一根完整 K 线的 `high/low`，`EvaluateFibPosition()` 用 `FibEntryLevel=0.5` 切 midline，`CheckFTSetup()` 再把 `close1/close2` 对 `prevHigh/prevLow` 的连续收盘突破，与 `inDiscount / inPremium` 绑定在一起。

## 2. 核心结论
- **一句话核心结论**：这个 repo 里的 `premium/discount` 更像 **Fib retest / EMA continuation 的 long-side context gate**，不该直接镜像成 `breakout-short` 的 shared short gate。
- **一句话怎么证明**：在 `BTC/ETH/SOL perp, 15m, ~125d` 的本地 FT 代理里，`discount 做多` 有轻度但一致的改善；但 `premium 做空` 反而比不加这个条件更差。

### 2.1 repo 里真正有用的实现细节
不是传统“画一段 swing 再盯 0.618 回踩”，而是更便宜的状态读法：
1. `HigherTF = H4`
2. `fibHigh = iHigh(H4, shift=1)`，`fibLow = iLow(H4, shift=1)`
3. `midLevel = fibLow + (fibHigh-fibLow) * 0.5`
4. 当前价在 mid 下方记作 `discount`，上方记作 `premium`
5. `FT` 信号本体只要求：最近两根 `15m` 收盘同时突破前两根范围（bars 3-4）
6. 再额外要求：
   - bullish FT 必须 `inDiscount`
   - bearish FT 必须 `inPremium`

这点对我们 desk 很重要：**repo 借的是 Fib 语义，不是精细回撤位本身**。

### 2.2 本地 15m 代理快检（BTC/ETH/SOL，近约 125 天）
我按 repo 的 FT 核心骨架做了一个最小代理：
- long：最近两根 `15m` 收盘都高于 bars `3-4` 的前置区间高点
- short：最近两根 `15m` 收盘都低于 bars `3-4` 的前置区间低点
- context：使用**上一根完整 4h K 线**的 `midline`
- 评估：看未来 `4 bars`（1 小时）signed return

#### long 侧：`discount` 有轻度改善
- `discount match`：`n=916`，`mean = +2.60 bps`，`win rate = 49.78%`
- `discount mismatch`：`n=3101`，`mean = +1.23 bps`，`win rate = 45.15%`
- 差值：
  - `mean` 约 **+1.36 bps**
  - `win rate` 约 **+4.64 pct-pts**
  - `median` 从 `-4.82 bps` 改善到 `-0.13 bps`
  - `median MAE` 从 `-33.96 bps` 收窄到 `-29.69 bps`

解释：这更像一个 **long-side context filter**，能让 continuation/pullback long 的质量略微更干净。

#### short 侧：`premium` 不但没帮忙，反而更差
- `premium match`：`n=960`，`mean = -0.79 bps`，`win rate = 43.65%`
- `premium mismatch`：`n=3312`，`mean = +3.16 bps`，`win rate = 46.29%`
- 差值：
  - `mean` 约 **-3.95 bps**
  - `win rate` 约 **-2.64 pct-pts**
  - `median` 也更差（`-5.87 bps` vs `-4.79 bps`）

解释：**不能把“premium 做空”当成 long 侧的镜像真理**。这条 short gate 现阶段更像会误伤 `breakout-short follow-up`。

#### aggregate 也不支持把它升成 shared gate
- `context match` 总体：`n=1876`，`mean = +0.87 bps`
- `context mismatch` 总体：`n=6413`，`mean = +2.23 bps`

这说明：**一旦把 long/short 合起来看，它不是共享放行键，反而更像一个需要保留方向不对称的 context 读数。**

## 3. 为什么和当前三条收口线直接相关
这题不是偏题，反而是在帮三条线少走弯路：
- `Fibonacci confirmation / retest_hold`：Fib 不一定非得继续炼成“0.618 精确触位触发”，先把它降级成 **HTF context**，更快、更诚实。
- `EMA / PSAR raw alpha focus`：如果想给 raw alpha 加一层低复杂度结构背景，这个 `prev-4h midline` 比继续叠更细的回撤比例更便宜。
- `V3 breakout-short follow-up`：本轮最有价值的信息恰恰是**别把这条逻辑镜像到 short 侧**。也就是说，它帮我们明确了一件事：`breakout-short` 先不要认领这条 gate。

如果现在继续把所有结构过滤层都写成多空对称，只会让三条收口线越来越乱；这轮更值得做的是把 **可保留的不对称** 先钉死。

## 4. 可复刻的最小实验（下一步怎么测）
### 研究假设
`prev-4h premium/discount midline` 只应作为 **long-side context gate** 服务 `Fib retest_hold / EMA continuation`，不应直接镜像成 `breakout-short` 的 mandatory short gate。

### 一个可计算定义
- `prev4h_high = high` of previous completed `4h` bar
- `prev4h_low = low` of previous completed `4h` bar
- `mid = (prev4h_high + prev4h_low) / 2`
- long context match：`entry_price < mid`
- short context match：`entry_price > mid`

### 最小回测切口
优先做 **三臂 honesty test**：
1. baseline（现有 `Fib retest_hold` / `EMA continuation` / `breakout-short` 原规则）
2. **long-only context gate**：只给 `Fib retest_hold` 与 `EMA continuation` 加 `entry < prev4h_mid`
3. **symmetric gate 对照组**：long 要 `discount`、short 也强行要 `premium`

### 建议样本与口径
- 资产：`BTC/ETH/SOL perp`
- 周期：`15m` 主判定，`5m` 可做执行细化
- 样本：最近 `180~365d`
- 成本：`6 / 10 / 15 bps per side`
- 观察窗：先看 `4 bars` 与 `8 bars` 两档

### 最先看 4 个指标
1. `post_cost_return`
2. `long vs short decomposition`
3. `trade_count / turnover`
4. `p5 trade pnl` 与 `max_drawdown`

### 如果只做一个最小实验
先只在 `Fib retest_hold` 上测：
- 触发仍按现有 retest_hold 定义
- 只额外要求 `retest bar close < prev4h_mid`
- 再和“同一套规则 + short 也加 premium gate”的版本对照

如果 long-only 版本改善而 symmetric 版本变差，就说明这条 context 的角色已经很清楚了。

## 5. 风险与保留意见
- 这是一份 **repo 工程逻辑 + 本地代理快检**，不是正式论文结论。
- 该 repo 主语境是 `M15 + H4` 的 MetaTrader/FX 执行框架，还带 `kill zone`、fractal sweep、order block 等别的条件；我们本轮只抽取其中最便宜的一根旁支。
- 它的“Fib”本质上只是 **上一根完整 H4 K 线的 midline 分层**，不等于传统 swing-based Fibonacci retracement。
- 本地快检未纳入 funding / basis / 冲击成本，也不是完整策略回测；只能说明“这层 context 在 15m 上更像 long-side asymmetric gate”。

## 6. 来源
1. carlosrod723. (2025). *MQL5 Trading Bot*. GitHub Repository.
   - Authors: carlosrod723
   - Year: 2025
   - Title: MQL5 Trading Bot
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://raw.githubusercontent.com/carlosrod723/MQL5-Trading-Bot/main/README.md>
   - Repo URL: <https://github.com/carlosrod723/MQL5-Trading-Bot>
2. carlosrod723. (2025). *MyTradingBot.mq5* (`MQL5/Experts/MyTradingBot.mq5`).
   - Authors: carlosrod723
   - Year: 2025
   - Title: MyTradingBot.mq5
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://raw.githubusercontent.com/carlosrod723/MQL5-Trading-Bot/main/MQL5/Experts/MyTradingBot.mq5>
   - Repo URL: <https://github.com/carlosrod723/MQL5-Trading-Bot>
3. Binance. (2026). *USDⓈ-M Futures REST API — Kline/Candlestick Data* (`/fapi/v1/klines`).
   - Authors: Binance
   - Year: 2026
   - Title: USDⓈ-M Futures API Docs
   - Venue: Binance Developers
   - DOI: N/A
   - Readable URL: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>
   - Repo URL: N/A

## 7. 本轮落地产物
- `reports/artifacts/quant_digests/htf_premium_discount_ft_proxy_2026-03-20.csv`
- `reports/artifacts/quant_digests/htf_premium_discount_ft_proxy_summary_2026-03-20.csv`
