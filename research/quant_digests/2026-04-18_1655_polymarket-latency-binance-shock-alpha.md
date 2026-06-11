# Polymarket latency arb：Binance 先动、5m binary odds 后调，才是 base alpha

- 时间：2026-04-18 16:55 UTC
- 类型：GitHub repo source audit + Binance public-data sanity probe
- 主题类型：raw alpha
- 基础 alpha：CEX 现货/永续价格先发生短窗冲击，而 Polymarket 5m UP/DOWN 盘口概率尚未完全重定价，买入 stale side 捕捉概率回归
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：event-driven / prediction-market / latency-arb / Binance / Polymarket / 1m / 3m / 5m / execution / cost
- 证据类型：GitHub 工程实现 + repo 自带 backtest 配置 + Binance 公共数据 sanity probe

## 1. 这次看了什么

看的是 `learningworship/polymarket-latency-bot`：一个专门交易 Polymarket 5 分钟 BTC/ETH UP/DOWN 市场的 latency arbitrage bot。它不是 `YES+NO<1` 的补体套利，而是**方向型事件 alpha**：Binance 价格快速上/下冲时，Polymarket odds 可能慢 `2–10s` 才追上。

## 2. 核心结论

- **base alpha 很清楚**：`Binance 30–60s price shock -> Polymarket binary probability stale -> 买 UP/DOWN`。
- repo 的 live 配置给了完整壳：`30s` 窗口、价格变动阈值 `0.15%`、Polymarket 价格带 `0.28–0.72`、最小 edge `12%`、单笔 `20 USDC`、最长持有 `240s`、TP `15%`、max spread `3c`。
- backtester 里的 validated config 更像研究口径：`60s` window、`0.15%` shock、vol-adjust、acceleration confirm、`3m` hold、`15%` TP；自报 holdout `683` 笔、Sharpe `5.2196`、win rate `44.95%`。
- 我用 Binance Spot `BTC/ETH 1m` 约 `25,000` 根 bar 做了裸 shock sanity：裸追 Binance 本身并不稳，BTC `0.15%` shock 后 next `3m/5m` 约 `-0.29/-1.01bps`，ETH `0.25%` shock 后 next `3m/5m` 约 `+3.70/+2.32bps`。所以这条线不能简化成“币价急涨就追”，真正价值在 **Polymarket 盘口 stale-price gate**。

## 3. 为什么和当前项目有关

它能补 short-cycle desk 当前较少的一类素材：**外部场所慢重定价 alpha**。传统 `1m/3m/5m` K 线只告诉我们 Binance 已经动了；Polymarket 盘口提供另一个交易面，如果概率价格还没反映这个移动，就可能出现短寿命可成交 edge。

这比泛 sentiment / prediction-market 指标更直接：entry、exit、sizing、risk、cost 都在源码里有对应模块，可直接做 paper feed，不需要先发明一套策略壳。

## 3.5 策略拆解

- 方向属性：事件驱动顺势 / latency arbitrage
- 基础 alpha：Binance 短窗冲击领先 Polymarket 5m binary odds 重定价
- regime：只在活跃 5m BTC/ETH binary market、剩余时间足够、价格还在中间概率带时启用
- filter / veto：Polymarket price band、`min_edge`、max spread、settlement buffer、盘口新鲜度
- risk / sizing / execution overlay：单笔 `20 USDC`、单方向最多 1 仓、最长持有 `3–4m`、TP `15%`、daily loss limit、taker fee + bid/ask spread 显式扣除

## 4. 可复刻的最小实验

- 研究假设：Binance `BTC/ETH` 在 `30–60s` 内移动超过 `0.15–0.40%` 后，若 Polymarket UP/DOWN 价格仍在 `0.28–0.72` 且 fair probability 与盘口价差超过 `10–12%`，买 stale side 的期望收益为正。
- 可计算定义：`shock = close_t / close_{t-60s} - 1`；`fair_up = logistic(k * shock)`；`edge = fair_side - poly_ask_side`。
- 最小切口：Polymarket 5m BTC/ETH UP/DOWN CLOB tick + Binance `1s/1m` price；先跑 `2026-04` holdout，再扩到 `60–90d`。
- 先看指标：`net_edge_after_fee_spread`、成交后 `180s/240s` PnL、按 market 剩余时间分桶的胜率。

## 5. 风险与保留意见

最大风险是**历史可测和实盘可吃不是一回事**：这个 alpha 的寿命可能只有几秒，入口价、盘口深度、CLOB fee、Polygon/签名延迟都会吃掉 edge。repo 自报 Sharpe 很漂亮，但我们不能直接采信；必须用自己的 Polymarket order book 采样重放，且先用 test mode / paper fill 验证 slippage。

## 6. 来源

- Author: learningworship
- Year: 2026
- Title: `polymarket-latency-bot`
- Venue: GitHub
- DOI: N/A
- Repo URL: https://github.com/learningworship/polymarket-latency-bot
- Readable URLs:
  - https://raw.githubusercontent.com/learningworship/polymarket-latency-bot/main/README.md
  - https://raw.githubusercontent.com/learningworship/polymarket-latency-bot/main/config.yaml
  - https://raw.githubusercontent.com/learningworship/polymarket-latency-bot/main/strategy/latency_arb.py
  - https://raw.githubusercontent.com/learningworship/polymarket-latency-bot/main/backtester/best_signal_config.json
- 本地 artifacts：
  - `reports/artifacts/quant_digests/2026-04-18_polymarket_latency_binance_shock_summary.json`
  - `reports/artifacts/quant_digests/2026-04-18_polymarket_latency_binance_shock_events.csv`
