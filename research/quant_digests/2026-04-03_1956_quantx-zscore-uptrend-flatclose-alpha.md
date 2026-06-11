# 别把这份 intraday mean-reversion repo 只读成美股回测秀：对 crypto short-cycle desk，更该先测的是「short-horizon z-score oversold × 5d trend-allow × one-trade-per-day flat-close shell」
- 时间：2026-04-03 19:56 UTC
- 类型：2025 GitHub repo source audit（GitHub API metadata + `README.md` + `src/strategy.py` + `src/backtest.py` + `docs/Report_Notes.txt`）+ Binance Futures 公共 `1m/3m/5m/15m` 最小便携性快检
- 主题类型：raw alpha
- 基础 alpha：**短周期价格偏离短均值后会向均值回归，但只在更高一层短趋势仍向上的时候做“顺大势的回撤买入”**；repo 真正值得 desk 先抄的不是“z-score 很神”，而是 `intraday z-score oversold + 5-day trend allow + flat-close + vol/ATR sizing` 这条完整单资产壳
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / mean-reversion / single-asset / zscore / short-horizon / daily-trend-gate / flat-close / intraday / no-overnight / vol-normalized-sizing / 1m / 3m / 5m / 15m / repo / public-data / cost / risk
- 证据类型：repo（完整策略壳）+ README 已给回测指标 + 本地 public-data portability probe

**先回答 base alpha：这篇东西的 base alpha 很清楚，不是“机器学习、报表、可视化框架”这些外围，而是一个非常具体的单资产 raw alpha——`短周期 oversold 回撤，在更高层日内/日间趋势仍向上的前提下，做 intraday mean reversion`。**

## 1）为什么这条线现在值得 intake
这轮值得写它，不是因为它在美股上回测数字好看，而是因为它刚好补了我们当前 research queue 里的一个缺口：

- 它是**raw alpha 本体**，不是纯 filter / regime / overlay；
- 它是**单资产均值回归**，能补我们最近 pairs / carry / cross-market / maker 类素材之外的另一条主线；
- 它的结构**非常可解释**，没有一上来就把研究重心带去黑盒 ML；
- 它把 `entry / exit / sizing / stop / cost / no-overnight` 一次写齐，适合快速做 first verdict。

结合当前 `LEARNING_TRACK` / `FACTOR_BACKLOG`：我们还处在**继续积累可独立复现的基础 alpha**阶段，而这条线正好是“解释性强、可快速搬到 crypto 的完整 mean-reversion 壳”。

## 2）这次看了什么
### 2.1 主来源
1. **Alqama Ansari (2025), *Quant Strategy Backtester*, GitHub repository**  
   - Venue：GitHub  
   - DOI：N/A  
   - Readable URL：<https://github.com/Alqama-svg/Quant_Strategy_Backtester>  
   - Repo URL：<https://github.com/Alqama-svg/Quant_Strategy_Backtester>  
   - GitHub API metadata：仓库创建于 `2025-10-16`，最近 push `2026-01-16`

2. 这次重点看的文件：
   - `README.md`
   - `src/strategy.py`
   - `src/backtest.py`
   - `docs/Report_Notes.txt`

### 2.2 repo 自带的关键数字
README 里直接给出一组完整的回测摘要（`QuantX V4.9 Full-Year 2024 Backtest`）：

- Universe：`32` 个大盘股 ticker
- Initial Capital：`$1,000,000`
- Final Capital：`$1,401,058`
- Total Return：`+40.11%`
- Annualized Return：`26.30%`
- Max Drawdown：`-1.91%`
- Sharpe Ratio：`2.36`
- Trades Executed：`3,308`
- Win Rate：`66.63%`

`docs/Report_Notes.txt` 还补了两个对我们很重要的点：
- **全是 intraday trade，没有隔夜暴露**；
- 数据口径是**intraday OHLCV**，并且研究对象本质上是**price vs short-term moving average 的 standardized z-score deviation**。

翻成人话：

> 这不是“看到跌就抄底”，而是一个**有上层方向允许、下层偏离触发、并且日内强平归零**的短周期回归壳。

## 3）repo 里真正能直接搬走的策略骨架
从 `src/strategy.py` 和 `src/backtest.py` 看，这条线最值钱的是它把完整交易母板写得非常具体：

### 3.1 信号层
- `DAILY_TREND_WINDOW = 5`
- `INTRADAY_LOOKBACK = 15`
- `Z_THRESHOLD = 0.65`
- `VOLUME_MIN_FACTOR = 0.35`
- `CONFIRM_BARS = 0`

在 `backtest.py` 里，入场不是裸做反转，而是同时满足：
- 短周期 `z-score <= -0.65`
- 成交量条件通过
- 当日 close 仍在 `5-day trend` 之上
- 同一资产**当天只进一次**（`entered_today`）

这说明它真正的 base alpha 不是“无脑均值回复”，而是：

> **上层仍偏强时，做短周期 oversold 回撤修复。**

这和纯粹的逆势抄底差别很大，也更适合 crypto 的短周期实盘：
- 它把均值回复限制在“顺大势的小回撤”里；
- 它避免在明显下跌日里把每次下跌都错当成可回归噪音。

### 3.2 风控与仓位层
repo 直接给了能落地的参数：

- `RISK_PER_TRADE = 0.035`
- `MAX_POSITION_FRACTION = 0.05`
- `MAX_GROSS_EXPOSURE = 2.2`
- `STOP_LOSS_PCT = 0.022`
- `TAKE_PROFIT_PCT = 0.10`
- `TRANSACTION_COST_PCT = 0.0002`
- `SLIPPAGE_PCT = 0.0005`

`backtest.py` 里的 sizing 也不是瞎分配，而是：
- 先算 `risk_budget = total_value * RISK_PER_TRADE`
- 再用 `max(ATR, exec_price * volatility, floor)` 估单股 dollar risk
- 再受 `MAX_POSITION_FRACTION` 和 gross exposure 上限约束

这点很关键，因为它不是“只有信号没有壳”的研究仓库，而是把：
- entry
- stop
- take profit
- position sizing
- capacity / exposure control
- cost proxy

一次写齐了。

### 3.3 出场层
这份 repo 很适合我们 desk 的一点，是它明确坚持：
- 日内 stop / take-profit 先走；
- **收盘前全部平掉，不留 overnight**。

对 crypto 来说，24/7 没有美股那种固定收盘，但这个思想非常有价值：

> 你可以把它翻译成“**pseudo-session flat-close**”，比如 UTC `00:00`、北京时间 `08:00`、或美股 regular session close 对应时刻，把它当成强制降风险和结算点。

## 4）为什么这不是“又一个 BB/RSI 抄底脚本”
这份 repo 最值得 intake 的地方，不是指标名，而是它把单资产 mean reversion 写成了一个**非常诚实的完整策略壳**：

- **raw alpha 本体**：短均值偏离后修复
- **方向允许层**：只在上层趋势没坏时做回撤买入
- **risk shell**：ATR / 波动率参与 sizing
- **time boundary**：强制日内 flat-close
- **capacity shell**：position fraction / gross exposure
- **cost shell**：显式写了 cost + slippage

所以它不是一个“指标堆砌”的 filter，而是一条**能直接进入复现实验队列**的 raw alpha 母板。

## 5）Binance 公共数据最小便携性快检：这条壳迁到 crypto 居然挺顺
先强调口径：下面**不是** repo 的原始复现，也不是 production PnL，只是做一个最小便携性检查，看这条壳搬到 crypto `1m/3m/5m/15m` 后，是否还能形成像样的 short-cycle alpha。

### 5.1 快检口径
- 数据源：Binance USDⓈ-M Futures 公共 klines
- 标的：`BTCUSDT / ETHUSDT / SOLUSDT`
- 区间：`2026-03-01` 到 `2026-04-03 19:5x UTC`
- proxy 假设：
  - `5-day` 日线趋势允许
  - `15-bar` intraday z-score
  - `1 trade / symbol / day` 上限
  - `-2.2%` 止损、`+10%` 止盈
  - pseudo-EOD 平仓：按 `UTC` 日切
  - 成本：`7bps / side`（沿 repo 的 `cost + slippage`）
- 结果文件：
  - `reports/artifacts/quant_digests/2026-04-03_quantx_mean_reversion_portability_probe.csv`

### 5.2 `5m` proxy 结果（更接近当前 desk 默认频段）
- **BTCUSDT 5m**：`15` 笔，胜率 `66.7%`，累计收益 proxy `+11.3%`，最大回撤约 `-2.38%`
- **ETHUSDT 5m**：`16` 笔，胜率 `81.3%`，累计收益 proxy `+28.2%`，最大回撤约 `-1.49%`
- **SOLUSDT 5m**：`14` 笔，胜率 `57.1%`，累计收益 proxy `+8.4%`，最大回撤约 `-4.25%`

### 5.3 `15m` proxy 结果（仍然能活）
- **BTCUSDT 15m**：`15` 笔，胜率 `66.7%`，累计收益 proxy `+13.6%`，最大回撤约 `-2.47%`
- **ETHUSDT 15m**：`16` 笔，胜率 `75.0%`，累计收益 proxy `+21.4%`，最大回撤约 `-1.49%`
- **SOLUSDT 15m**：`14` 笔，胜率 `64.3%`，累计收益 proxy `+10.9%`，最大回撤约 `-3.97%`

### 5.4 `1m / 3m` sidecar 结果（说明它也能下压到更高强度 alpha）
- **ETHUSDT 1m**：`16` 笔，胜率 `87.5%`，累计收益 proxy `+30.9%`
- **ETHUSDT 3m**：`16` 笔，胜率 `87.5%`，累计收益 proxy `+32.2%`
- **BTC / SOL** 在 `1m / 3m` 也维持正累计收益

这组快检最重要的结论不是“收益数值本身”，而是：

> **这条 repo-based shell 不仅能搬到 crypto，而且在 `5m / 15m` 上也不是一搬就死。**

## 6）对当前 short-cycle desk 的正确翻译
### 6.1 这条 alpha 的正确命名
如果要把它写进素材池，我会这样命名：

**`short-horizon z-score oversold × 5d trend-allow × flat-close`**

这比笼统写“均值回归”更准确，因为它强调了三件核心事：
1. **不是纯反转**，而是顺大势下的短回撤修复；
2. **不是无限持有等均值**，而是日内壳；
3. **不是只有 entry**，而是完整执行与风险框架。

### 6.2 它服务于哪类 desk 组件
这条线可以直接扩成：
- 单资产 long-only dip-buy shell
- 单资产 long/short 对称回归 shell
- 多币 one-trade-per-day rotation shell
- 作为更复杂 MR / breakout 组合里的一条独立 sleeve

### 6.3 对 crypto 的一个关键改写
repo 当前更像 equities long-only 逻辑。放到 crypto perp，我会优先补一条**对称 short sleeve**：
- 若 `z >= +z_th` 且 `day_close < 5-day trend`，允许做空回归
- 若市场整体 regime 明显 risk-on，则 short sleeve 降仓或停机

也就是说：

> repo 的 long-only 版本已经足够做 first verdict；但真要变成 perp desk 的 production 候选，下一步必须加**下行趋势中的 overbought fade**。

## 7）这条线的优点与最大风险
### 优点
- **可解释性强**：比很多 ML / 多特征堆叠策略更适合当前学习阶段
- **完整度高**：entry/exit/sizing/risk/cost 都写了
- **频段友好**：`5m / 15m` 都能快速做实验，`1m / 3m` 也可向下压
- **迁移成本低**：只需要公共 OHLCV 就能做第一轮 verdict

### 最大风险
- **pseudo-session 选择会强烈影响结果**：crypto 没有自然收盘，flat-close 的切点本身就是参数
- **趋势允许层可能太宽**：`5-day trend` 在 crypto 可能过慢，需比较 `1d/3d/5d` 或 `288-bar EMA` 等替代
- **单日只进一次**会压低 turnover；对更高强度 desk，未必是最优
- **当前快检没有盘口成交、maker/taker 分层和 funding**，所以只够 admission，不够 production

## 8）下一步怎么测（最重要）
### A. 先做 exact-ish replication（优先级最高）
在 `momentum` 里做一个最小复刻版：
- 标的：`BTC / ETH / SOL`
- 频段：`5m` 为主，`15m` 为稳健对照，`3m` 为高强度附加组
- 信号：
  - `zscore(close, 15)` 或 `zscore(vwap, 15)`
  - 上层方向：`close > trend_filter`
- 出场：`stop / tp / pseudo-session flat-close`
- cost ladder：`7 / 10 / 15 bps per side`

### B. 把“flat-close 时间点”当成一级参数
至少测这三种：
- `UTC 00:00`
- `UTC 08:00`（更贴近北京时间日切）
- `UTC 21:00~22:00`（贴近美股 regular session 尾部）

因为这条策略不是简单信号，而是**信号 + 强制结算边界**。

### C. 增加 short sleeve
做对称版本：
- long：`z <= -z_th` 且 `trend_up`
- short：`z >= +z_th` 且 `trend_down`

这一步非常重要，因为我们 desk 不是只能做 equities long-only。

### D. 和现有单资产 MR baseline 做 A/B
最适合的对照不是继续和 pairs/carry 比，而是直接和现有单资产 MR 母板比：
- `BB/zscore + RSI confirm + trend veto`
- 本文这条 `zscore oversold + trend allow + flat-close`

要回答的问题是：
- 哪条更简洁？
- 哪条 trade count 更稳？
- 哪条对 cost / pseudo-session 更敏感？

## 9）结论
如果只用一句话总结：

> **这份 repo 最值得 desk intake 的，不是“美股回测成绩单”，而是一条非常清楚、能快速迁移到 crypto 的单资产 raw alpha 壳：`短周期 z-score oversold` 只在 `5-day trend` 仍向上时触发，并用 `flat-close + vol/ATR sizing` 把它收束成完整日内策略。**

它的研究价值在于：
- 不是纯 filter；
- 不是纯解释；
- 不是只能停留在论文摘要层；
- 而是**今天就能用公共数据做最小实验**，并且从这轮 `5m / 15m` 快检看，值得进入下一轮正式 admission check。

## Sources
1. **Alqama Ansari (2025), _Quant Strategy Backtester_, GitHub repository**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: <https://github.com/Alqama-svg/Quant_Strategy_Backtester>  
   - Repo URL: <https://github.com/Alqama-svg/Quant_Strategy_Backtester>

2. **Repository README / backtest summary**  
   - Source URL: <https://raw.githubusercontent.com/Alqama-svg/Quant_Strategy_Backtester/main/README.md>

3. **Strategy parameters**  
   - Source URL: <https://raw.githubusercontent.com/Alqama-svg/Quant_Strategy_Backtester/main/src/strategy.py>

4. **Sequential backtest logic / entry-exit-scaling shell**  
   - Source URL: <https://raw.githubusercontent.com/Alqama-svg/Quant_Strategy_Backtester/main/src/backtest.py>

5. **Report notes / data and interpretation notes**  
   - Source URL: <https://raw.githubusercontent.com/Alqama-svg/Quant_Strategy_Backtester/main/docs/Report_Notes.txt>

6. **This run’s local portability artifact**  
   - File: `reports/artifacts/quant_digests/2026-04-03_quantx_mean_reversion_portability_probe.csv`
