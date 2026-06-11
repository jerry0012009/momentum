# 别把这份微观结构 repo 只读成回测 plumbing：对 short-cycle desk，更该先测的是 `fill-aware OFI × quote-join flow-control shell`
- 时间：2026-04-08 22:49 UTC
- 类型：GitHub / 工程实现
- 主题类型：raw alpha
- 基础 alpha：`order-flow / queue-imbalance continuation`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：microstructure / OFI / queue imbalance / maker-taker / fill model / execution / BTCUSDT / 1m / 3m
- 证据类型：工程经验 + 本地 public-data portability probe

## 1. 这次看了什么
看的是 `jingyaolai17/tardis-python-private` 这套 BTCUSDT Binance 微观结构策略实现，重点审了 `README.md`、`strategy_core.py`、`ob_core.py`、`IS_backtest_BTCUSDT.py`、`IS_OOS_Validation_summary.md`。它不是“先有信号、再随手补个 execution”，而是把 **alpha、挂单/吃单决策、fill 概率、库存约束、成本门槛、freeze/kill** 写成一条完整链。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最值得学的，不是“OFI 能预测价格”这句老话，而是它把 **OFI/队列失衡 alpha** 直接翻成了一个可交易的 maker-first 壳：只有当预期 alpha 扛得住 spread、手续费和 fill 风险时才挂单/追单。
- **一句话证明方式：** 证据主要来自 repo 自带的 **in-sample / frozen OOS backtest**，并且在策略代码里把 `alpha_bps -> join/take -> inventory/risk` 的传导链条明确写死，而不是只展示预测分数。
- `strategy_core.py` 里的核心做法，是把 `ofi_z`、`qi_z`（queue imbalance）、`microprice deviation` 组合成 `alpha_bps`，再和 `join_thresh_bps` / `take_thresh_bps` 比较，决定是 maker join 还是 taker take。
- 这条线最值钱的地方在 **成本显式化**：repo 不把“预测方向对了”当胜利，而是要求 `expected_alpha` 先覆盖 fee / rebate / fill loss；这正是很多 1m 微观结构思路死在实盘前的一步。
- repo 自带摘要里，fill-aware baseline 的 **日频 Sharpe 约 1.47**，flow-control 版 **IS / OOS 日频 Sharpe 约 1.68 / 1.54**，说明 overlay 不是摆设；但作者也明确写了 **成本仍是主导项**，更严的 taker fee 假设会把 OOS 直接翻负。
- 我补了一个 Binance USDⓈ-M 公共 `1m` portability probe：用 `signed_quote = 2*taker_buy_quote - quote_volume` 做 kline 级 signed-flow proxy，事件定义为 `|flow_z|>=2` 且与当根 bar 方向同向。近 `30d` 上，`BTCUSDT` 的 next `1/3` bar 同向收益约 `-0.384 / -0.666 bps`，但 `ETHUSDT` 约 `+0.133 / +0.212 bps`，`SOLUSDT` 约 `+0.134 / +0.507 bps`。含义很直接：**裸 kline 级 flow proxy 不能替代真实 L2 OFI；repo 里的边，极可能依赖 queue / microprice / fill realism。**

## 3. 为什么和当前项目有关
这篇东西和 desk 当前最相关的点，不是“又一个高频故事”，而是它属于 **可直接落地的 raw alpha 完整策略壳**：
- raw alpha 本体很清楚：`order-flow / queue-imbalance continuation`
- 不是只给预测器，而是把 `entry / exit / sizing / cost / risk` 一起写清楚
- 对我们现在缺的 1m/3m 高强度 alpha 很有价值：哪怕最后不直接抄 BTC L2，也可以复用它的 **alpha-hurdle + maker/taker router + inventory cap** 结构
- 它还能给其他微观结构 alpha 当 shared execution shell，而不只是服务这一条 OFI

## 3.5 策略拆解（必填）
- 方向属性：单资产、顺势、微观结构 continuation
- 基础 alpha：`OFI z-score + queue imbalance + microprice deviation -> short-horizon drift`
- regime：更偏适合有短时失衡、但仍能成交的高流动窗口；极端毒性/过宽 spread 不应硬做
- filter / veto：`expected alpha > join/take threshold`、fill 概率不过线不挂、成本覆盖不了不追
- risk / sizing / execution overlay：maker-first、必要时 taker fallback、inventory cap/decay、freeze/halt、fee/rebate 显式计入

## 4. 可复刻的最小实验
**研究假设：** 如果短时 signed flow 真有信息，那么在 crypto major 的 `1m/3m` 上，`flow_z` 极端且与当根收益同向时，后续 1~3 根应该仍有一点同向漂移；但是否能活下来，取决于能不能把它放进 maker-first / fill-aware 壳里。

**最小定义：**
1. 数据：Binance USDⓈ-M 公共 `1m` klines（后续升级到 `aggTrades` / 真 L2）
2. 特征：`signed_quote = 2 * taker_buy_quote_volume - quote_volume`，再做 `120` 根 rolling z-score
3. 事件：`|flow_z| >= 2` 且 `sign(flow_z) = sign(bar_return)`
4. 交易：下一根按信号方向持有 `1` 或 `3` 根；先做 taker-taker 粗测，再上 maker-entry / taker-exit A/B
5. 最先看：`post-cost expectancy / event`、`positive-event ratio`

更像 repo 原味的下一步，是把数据升级到 **best bid/ask 级别**，真正计算 `OFI / queue imbalance / microprice`，再补一个简单 fill model，测试 `join-only` 与 `join+take fallback` 的差异。

## 5. 风险与保留意见
- 这条线**非常吃数据层级**：只用 kline signed volume，容易把真正的 queue alpha 压扁甚至翻号。
- repo 自带 OOS 看起来不差，但作者自己也承认：**成本和 fill 假设一收紧，结果会明显恶化**。
- 这不是“方向预测够高就能做”的模型，必须连 execution 一起测；否则研究结论会比真实可交易性乐观很多。
- 当前 public-data probe 已经提示：BTC 的 naive proxy 是负的，因此后续别把它误读成“BTC 1m taker flow 一定能裸冲”。

## 6. 来源
- `jingyaolai17`. **tardis-python-private**. GitHub repo.
  - Repo URL: `https://github.com/jingyaolai17/tardis-python-private`
  - Source-audited files: `README.md`, `strategy_core.py`, `ob_core.py`, `IS_backtest_BTCUSDT.py`, `IS_OOS_Validation_summary.md`
- Binance USDⓈ-M Futures public market data
  - Klines endpoint doc: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`
