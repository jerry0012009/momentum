# 别把 StochRSI + Volume 只当 retail 指标拼盘：这份 2026 新 repo 给的是 15m 趋势内 exhaustion-reversion 完整策略骨架，但快检先把它判成负样本
- 时间：2026-03-23 20:32 UTC
- 类型：2026 GitHub 新仓库 + Binance 公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：上升趋势中的超卖反抽回归（trend-filtered pullback / exhaustion mean reversion）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/mean-reversion/pullback/exhaustion/stochrsi/volume/trend-filter/single-asset/repo/binance/crypto/5m/15m/cost/implementation-risk
- 证据类型：repo 策略代码 + 公开市场数据最小快检 + 实现诚实性检查

## 1. 这次看了什么
这次主看 **meripushko (2026)** 的新仓库 *binance-stochrsi-backtest*。先把 base alpha 说清楚：**不是“StochRSI 有用”这种空话，而是“价格仍在大级别上升趋势里时，短线超卖 + 成交量放大后的反抽回归”**。和 3 月 17 日那条只停在 source-template 的 `StochRSI + EMA pullback` 不同，这个 repo 把 `entry / exit / sizing / risk / fee` 都写出来了，所以它值得当成一条能被快速证伪或保留的完整 raw alpha intake。

## 2. 核心结论
- **这条东西的 base alpha 是清楚的。** 规则本质是：`close > EMA200` 的 uptrend 中，前一根 StochRSI 已超卖，当前 K 上穿 D 且仍处低位，同时放量，赌一次顺大势的小回调结束。
- **它确实是完整策略，不只是信号模板。** repo 明确写了：`stop = 最近 5 根最低点 - 0.1%`，`take profit = 2R`，`risk = 1%`，`fee = 10bp/side`，还有 `cooldown` 与 `max trades/day`。
- **但实现里有一个很硬的诚实性问题：`MAX_TRADES_PER_DAY` 实际上没有按天重置。** 代码里 `RiskManager.reset_daily()` 存在，但回测主循环从未调用，因此发布版代码按字面执行时，更像“整段回测最多只做 4 笔”。
- **我按 repo 逻辑抓 Binance 2024 年 15m 公共数据做最小快检，修掉 daily-reset 后，BTC/ETH 都是明显负 edge。** BTCUSDT：`80` 笔、胜率 `38.8%`、PF `0.44`、PnL `-28.7%`；ETHUSDT：`67` 笔、胜率 `40.3%`、PF `0.58`、PnL `-18.6%`。
- **把同一套规则直接压到 5m 更差。** BTCUSDT 2024 `5m`：`226` 笔、胜率 `27.9%`、PF `0.23`、PnL `-79.7%`。所以它现在不该直接进 `5m / 15m` fast lane，当“完整负样本”反而更有价值。

## 3. 为什么和当前项目有关
当前 bot7 的优先级不是继续找模糊 filter，而是补能独立复现、能完整落地的 raw alpha 素材池。这条 repo 的价值不在于“它能马上上线”，而在于：**它提供了一个非常具体、非常容易最小复现的 pullback raw alpha 骨架，并且能在几分钟内做出诚实否决。** 对 desk 来说，这比再收一条“可能有点用的确认条件”更值钱——因为我们现在需要的正是可快速进池、也可快速出局的完整策略候选。

## 3.5 策略拆解（必填）
- 方向属性：单资产、逆小级别回调但顺大级别趋势
- 基础 alpha：trend-filtered oversold bounce / exhaustion reversion
- regime：`close > EMA200`（只做多头趋势环境）
- filter / veto：前一根 `K <= 20 且 K < D`；当前 `K > D 且 K <= 30`；`volume > 1.5 x SMA20`
- risk / sizing / execution overlay：单笔风险 `1%`；`SL = 近 5 根最低点 - 0.1%`；`TP = 2R`；`K < D 且 K > 70` 早退；`fee = 10bp/side`；亏损后冷却 `2` 根；名义上每日最多 `4` 笔

## 4. 可复刻的最小实验
- **研究假设：** 这条 alpha 在 `BTC/ETH spot long-only` 上大概率不成立，但在 `perp long/short 对称版`、或更高 beta 山寨币的 `15m` 趋势段里，也许还能留下局部 edge。
- **一个可计算定义：** `signal_long = (close > EMA200) & (prev_k <= 20) & (prev_k < prev_d) & (k > d) & (k <= 30) & (volume > 1.5 * volume_sma20)`；short 端做镜像版。
- **最小回测切口：** Binance USDT perp，`BTC / ETH / SOL / DOGE`，样本先跑 `2024-01-01 ~ 2026-03-01`；先做 `15m`，再看是否值得下钻 `5m`；统一 `next-bar open` 成交、`6~10bp` 总成本、禁止 overlap。
- **最该先看 2 个指标：** `net PF / expectancy after cost`，以及 `trade count stability by regime`。如果连 `15m` 都过不了 `PF > 1` 和稳定交易数，就不用浪费预算去 `3m / 1m`。

## 5. 风险与保留意见
- 这是一份很新的个人 repo，不是经过同行评审的研究；README 里的示例业绩不能直接当真。
- 当前版本是 **spot long-only**，天然带有牛市偏置；直接映射到我们更关心的 perp 短周期，必须补 short 端与资金费/滑点口径。
- StochRSI 阈值、`1.5x` 放量阈值、`2R` 出场都很像固定参数模板，容易在单一时期过拟合。
- 从这次快检看，**它更像“完整但应快速否决的 raw alpha 模板”**，不该被包装成 high-conviction 主策略。

## 6. 来源
1. meripushko. (2026). *Binance StochRSI Volume Trading Bot*.
   - Repo URL: `https://github.com/meripushko/binance-stochrsi-backtest`
   - README: `https://raw.githubusercontent.com/meripushko/binance-stochrsi-backtest/main/README.md`
   - Strategy code: `https://raw.githubusercontent.com/meripushko/binance-stochrsi-backtest/main/src/strategy/stochrsi_volume.py`
2. Liu, Y., Lu, Y., & Wang, V. (2021). *Cryptocurrency Momentum Effect*. International Review of Financial Analysis.
   - DOI: `https://doi.org/10.1016/j.irfa.2021.101938`
   - Readable URL: `https://www.sciencedirect.com/science/article/pii/S1057521921002458`
3. Jiang, G. J., Kelly, B., & Xiu, D. (2023). *Technical Analysis in the Cryptocurrency Market* (related chart-signal evidence base).
   - DOI: `https://doi.org/10.1111/jofi.13268`
   - Readable URL: `https://onlinelibrary.wiley.com/doi/full/10.1111/jofi.13268`
