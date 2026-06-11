# 别把这份 2025/2026 pairs 仓库只当脚手架：对 short-cycle desk，更该先测的是「cointegrated spread z-score × stop-loss/time-exit」完整 raw alpha

- 时间：2026-04-04 03:16 UTC
- 类型：2025/2026 GitHub repo source audit（README + `backtester.py` + `cointegration_test.py` + `optimize_params.py` + `portfolio_backtest.py`）+ Binance USDⓈ-M 公共 `3m/5m/15m` 最小可移植性快检
- 主题类型：raw alpha
- 基础 alpha：**cointegrated pair 的 spread z-score 均值回归**（`|z|` 过阈值开仓，回归到中线附近平仓，极端偏离触发止损）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/zscore/stop-loss/parameter-grid/portfolio-shell/3m/5m/15m/repo/public-data/cost/risk
- 证据类型：仓库工程证据 + 公共数据快检

## 1. 这次看了什么
先回答这轮最关键的一句：

> **这篇东西的 base alpha 是什么？**
>
> **答：就是 pairs/stat-arb 的 spread 均值回归 raw alpha。**

本次主材料是 GitHub 仓库 **`seans-alt/crypto-pairs-arbitrage`**（创建于 2025-09，2026-02 仍有更新）。它不是只给“研究想法”，而是把完整壳子写出来了：
- pair 选择：Engle-Granger cointegration + hedge ratio
- 入场：`z_entry`（默认 2.0）
- 出场：`z_exit`（默认 0.5）
- 风险：`z_stop`（默认 3.0）
- 成本：换仓时扣交易成本
- 参数层：`z_entry × z_exit` 网格扫描
- 组合层：多 pair 等权组合回测

一句话核心结论：

> **这份 repo 最值得 intake 的不是“有没有新奇因子”，而是它把 pairs raw alpha 的 `entry/exit/stop/cost/portfolio` 五件事放进同一条可复现实验链。**

一句话证明方式：

> **我对源码逐文件拆解，并用 Binance 公共 `3m/5m/15m` 做同口径 z-score 壳子快检，验证这条壳子在 15m 更容易留净边，3m/5m 更容易被成本吃掉。**

## 2. 核心结论（给 desk 可执行的信息）
1. **这是完整策略壳，不是“只有信号没有出场”的半成品。**
   - `backtester.py` 明确写了入场阈值、回归出场、极值止损、交易成本扣减。
2. **它天然适合我们当前优先方向：pairs / stat-arb raw alpha 素材池。**
   - 不是 shared filter，不需要依赖外部低频数据才能成文。
3. **短周期可移植性有明显时间粒度分层（同壳子、同参数）**：
   - `SOLUSDT-XRPUSDT`：`15m` net4 约 **+0.240 bps/bar**，但 `5m` 约 **-0.105 bps/bar**、`3m` 约 **-0.030 bps/bar**。
   - `BTCUSDT-XRPUSDT`：`15m` net4 约 **+0.199 bps/bar**，`5m` 仅 **+0.017 bps/bar**，`3m` 转负。
4. **结论不是“3m/5m 不能做 pairs”，而是：同一套阈值壳在更快周期对成本和滑点更敏感。**
   - 3m/5m 要活，必须额外加 execution/cost 约束，而不是直接把 15m 参数平移下去。

## 3. 为什么和当前项目直接相关
我们最近 intake 已经覆盖了不少 raw alpha 分支（carry、microstructure、prediction-market、maker、pairs）。当前更缺的是：

- **可直接复刻的 pairs“标准壳”**（而不是每次都从零写）；
- 能快速回答“这条 pair 线到底是 alpha 本体问题，还是参数/成本问题”的实验模板。

这个 repo 刚好补了这层：
- 是 raw alpha 本体；
- 可直接拆成组件（pair admission / signal / risk / cost / portfolio）；
- 非常适合放进 `1m/3m/5m/15m` 的统一 first-verdict 流程。

## 3.5 策略拆解（必填）
- 方向属性：pairs / stat-arb / relative-value / mean reversion
- 基础 alpha：cointegrated spread 回归
- regime：默认无硬 regime；可后续接 volatility/crowding gate
- filter / veto：`z_entry` 触发 + `z_stop` 否决极端失配
- risk / sizing / execution overlay：
  - 单 pair 头寸按 `1/(1+|beta|)` 做名义归一；
  - 换仓扣成本；
  - 组合可先等权，再扩展到 risk parity。

## 4. 最小可复现实验（这轮已给到可跑口径）
### 4.1 已完成的最小快检口径
- 数据源：Binance USDⓈ-M `fapi/v1/klines`（公开）
- 标的池：`BTC ETH SOL BNB XRP ADA DOGE LINK`
- 主周期：`15m`，每币 `1500` bars（约 15.6 天）
- 信号：
  - `spread = log(P1) - beta*log(P2)`
  - rolling `zscore(window=96)`
  - `|z|>2` 入场，回归到 `|z|<0.5` 出场，`|z|>3` 止损
- 成本：按换仓事件扣 `4 bps` round-trip proxy（用于快筛，不是最终成交模型）

### 4.2 本轮 3 个关键数据点
1. `15m` 扫描里，净值靠前 pair：
   - `SOL-XRP`：net4 **+0.240 bps/bar**，Sharpe4 **7.62**，trades **62**
   - `BTC-XRP`：net4 **+0.199 bps/bar**，Sharpe4 **8.51**，trades **44**
2. 同 pair 粒度降到 `3m/5m` 后明显恶化：
   - `SOL-XRP`：`15m +0.240` → `5m -0.105` → `3m -0.030`（bps/bar）
3. 结论指向：
   - **15m 更像“先能活的壳”**；
   - `3m/5m` 需要加 execution gate（盘口深度、入场分位、时段 veto）后再谈扩展。

## 5. 下一步怎么测（直接可执行）
1. **Pair admission**：先按 `phi/half-life/rolling corr` 过滤，再进 z-score 壳，避免“看起来相关、实则慢漂移”的假 pair。
2. **成本梯度**：固定同一信号，跑 `2/4/8/12 bps` 阶梯，画出每对 pair 的 cost cliff。
3. **周期迁移**：
   - 主线先保 `15m`；
   - `5m` 只做 top-decile entry（`|z|` 更高分位）+ maker 优先；
   - `3m` 默认先不开放全量交易。
4. **风险约束**：加 `max-hold bars`、`daily trade cap`、`pair-level drawdown stop`，避免“均值回归策略被趋势行情长时间拖死”。

## 6. 风险与保留意见
- 该 repo 目前 star 很低、README 较薄，工程上更像“可用原型”而非生产级框架。
- 本轮快检是 public kline proxy，不含真实盘口冲击与排队成交，不能当实盘收益承诺。
- z-score pairs 在结构性趋势阶段会出现“回不来”的长拖尾，`z_stop` 只是第一层防线，不够替代 regime 控制。

## 7. 来源
1. **Sean Alt (2025/2026). _crypto-pairs-arbitrage_ (GitHub Repository).**
   - Repo URL: `https://github.com/seans-alt/crypto-pairs-arbitrage`
   - Created: `2025-09-23`
   - Last push: `2026-02-18`
   - License: MIT
2. **Engle, R. F., & Granger, C. W. J. (1987). _Co-integration and Error Correction: Representation, Estimation, and Testing_. Econometrica.**
   - DOI: `10.2307/1913236`
   - Readable URL: `https://www.jstor.org/stable/1913236`
3. **Binance USDⓈ-M Futures API — Kline/Candlestick Data**
   - URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 8. 本地产物
- `reports/artifacts/quant_digests/pairs_repo_20260404/pair_scan_15m.csv`
- `reports/artifacts/quant_digests/pairs_repo_20260404/focus_pair_interval_portability.csv`
- `research/quant_digests/2026-04-04_0316_kraken-pairs-zscore-stoploss-shell.md`
