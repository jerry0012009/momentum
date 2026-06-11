# 别把 Polymarket candle bot 只读成“方向猜涨跌”：对 short-cycle desk，更该先拆的是「连续同向 K 线后的反向 binary bet × 入场价格上限」这条完整 raw alpha 壳

- 时间：2026-04-22 05:45 UTC
- 类型：GitHub repo source audit + Binance USDⓈ-M public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：`n` 根 `5m/15m` K 线连续同向后，下一根更容易短时反向；在 Polymarket/Kalshi 这类 fixed-payout candle market 里，只在 binary 合约价格低于胜率隐含上限时买反向 YES。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：binary-market / Polymarket / mean-reversion / streak-reversal / price-hurdle / 5m / 15m / external-venue / cost / risk
- 证据类型：工程经验 + public-data quick probe

## 1. 这次看了什么

来源是 2026 年仍活跃的 repo **0xrsydn/polymarket-crypto-toolkit**：README 把系统拆成 Binance 数据、指标、策略、backtest、executor；核心可读策略包括 `streak_reversal.py`（连续同向 candle 后反手）和 `candle_direction.py`（EMA/MACD/RSI 方向）。Repo URL：<https://github.com/0xrsydn/polymarket-crypto-toolkit>。

## 2. 核心结论

- 这不是简单“猜下一根涨跌”，真正值得复用的是 **binary payout 的价格纪律**：如果买价是 `p`、到期赢付约 `0.95`，最低胜率约是 `p / 0.95`；`0.50` 买入时要 `52.63%` 才打平。
- Binance USDⓈ-M 最近 `1500` 根 public bars 快检显示，repo 的 EMA/MACD/RSI 方向壳在 `5m/15m` 多数低于打平线；不宜直接搬成 binary 主信号。
- 但 `streak reversal` 分支更像可交易候选：`5m ETH trigger=5` 有 `52` 次、胜率 `65.38%`、next-bar signed return `+4.31 bps`；`5m XRP trigger=4` 有 `138` 次、胜率 `65.94%`、`+3.12 bps`；`15m SOL trigger=5` 有 `43` 次、胜率 `74.42%`、`+2.47 bps`。
- 这些高胜率样本偏少，不能直接实盘；但足以把它放进研究池：它是 `1m/3m/5m/15m` 都能快速验证的 binary / short-horizon mean-reversion raw alpha。

## 3. 为什么和当前项目有关

它补的是 desk 当前较少的 **外部 venue fixed-payout alpha**：同一个方向预测，在 perp 上可能只有几 bps，成本后很薄；但在 binary market 里，只要买入价足够低，胜率 edge 可以直接映射成可交易 EV。对 `momentum` 来说，它更适合做一个独立 sleeve：Binance/venue price feed 负责触发，Polymarket/Kalshi order book 负责 admission 和执行。

## 3.5 策略拆解

- Entry：在 `5m/15m` bar close 后计算连续同向 candle streak；若连续上涨 `>= trigger`，买下一期 DOWN；若连续下跌 `>= trigger`，买下一期 UP。
- Exit：持有到下一根 candle settlement；不做中途止盈，除非盘口给出明显 early-exit 正 EV。
- Sizing：按 `edge = 0.95 * win_prob - ask_price - fee/slippage_buffer` 分层；`edge <= 0` 不进。
- Risk：单市场未结算 notional cap；同一标的连续亏损暂停；距离 settlement 太近或 order book 太薄时 veto。
- Cost：必须用真实 ask、盘口深度、撤单/成交概率和平台费用重算，不能假设永远 `0.50` 成交。

## 4. 最小实验：下一步怎么测

1. 数据：Binance `1m/5m/15m` public OHLCV + Polymarket/Kalshi 对应 candle market 的 bid/ask/order book snapshots。
2. 先离线复现 `trigger=3/4/5/6`，按 symbol × interval × trigger 输出：trade count、win rate、`max_entry_price = 0.95 * win_rate`、真实可成交 ask 覆盖率。
3. 再做 event-time paper：只在 `ask <= max_entry_price - 3~5c safety margin` 且 depth 足够时入场，比较 `5m ETH/XRP/SOL` 与 `15m SOL/BNB` pocket。
4. 失败线：若真实 order book 中可成交 ask 长期高于胜率上限，或者信号到 market open/settlement 存在不可控延迟，就只保留为 binary venue research shell，不进实盘候选。

## 来源与本地产物

- Repo：0xrsydn, 2026, *polymarket-crypto-toolkit*, GitHub, <https://github.com/0xrsydn/polymarket-crypto-toolkit>
- Source audit files：`README.md`、`packages/strategies/src/polymarket_algo/strategies/streak_reversal.py`、`candle_direction.py`、`packages/backtest/src/polymarket_algo/backtest/engine.py`
- 本地 probe：`reports/artifacts/quant_digests/polymarket_streak_reversal_probe_2026-04-22.csv`；对照弱基线：`reports/artifacts/quant_digests/polymarket_candle_direction_probe_2026-04-22.csv`
