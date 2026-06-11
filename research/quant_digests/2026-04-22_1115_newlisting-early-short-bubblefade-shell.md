# 别把新币做空仓只读成“30 天慢交易”：对 short-cycle desk，更该先拆的是「新上币早期泡沫高点 × funding-positive short fade」这条完整 raw alpha 壳

- 时间：2026-04-22 11:15 UTC
- 类型：2026 GitHub repo source audit + Binance USDⓈ-M public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：新上币上线约 3 天后，若价格仍处在最近 3 天高位且 funding 为正，做空“早期泡沫/拥挤多头”并吃回落
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：new-listing / single-asset / mean-reversion / short-bias / funding / bubble-fade / 15m / public-data / cost / risk
- 证据类型：工程经验 + public-data 快速复现

## 1. 这次看了什么

看的是 `frozen-cherry/binance-futures-short-strategy`：它把 Binance Futures 2025 新上线合约做成一个完整回测壳，核心规则很直白：上线满 `3d` 后，如果当前价仍高于过去 `3d` 的 `95%` 高位、且 funding rate `> 0`，开空；repo 默认用 `+30%` 止盈、`-15%` 止损、`30d` 超时。

## 2. 核心结论

- 这不是传统 `5m/15m` 连续信号，而是 **listing-age event alpha**：入场时钟来自“上线第几天”，执行和风控可以落在 `15m/5m`。
- repo README headline 给出 `397` 笔、胜率 `57.43%`、总盈亏 `+1335.16%`、平均持仓 `14.2d`；这些数不能直接照搬，但说明作者已经把 entry/exit/risk/backtest 串成完整壳。
- 我用 repo 的 2025 新币清单前 `28` 个 USDT 合约、Binance public `15m` K 线 + funding 做了快检：repo 默认式 `30%TP/15%SL/30d` 产生 `76` 笔，胜率 `50.0%`，平均 gross `+6.52%/笔`，粗扣 `8bps` 后平均 net `+6.44%/笔`，平均持仓 `3.16d`。
- 更贴 short-cycle desk 的 `8%TP/5%SL/3d` 变体产生 `239` 笔，胜率 `49.4%`，平均 gross `+0.84%/笔`，扣 `8bps` 后平均 net `+0.76%/笔`，平均持仓约 `0.35d`。换句话说：边不一定来自胜率，而来自“跌起来时足够快”。

## 3. 为什么和当前项目有关

当前素材池已经有很多常规 `BB/EMA/pairs/funding`，但“新上币早期拥挤多头回落”是另一类可独立复现的事件型 raw alpha。它对 `momentum` 的价值不是每天都交易，而是做一个 **new-listing short sleeve**：低频 admission，`15m/5m` 负责触发、限价、止损和降杠杆。对实盘更重要的是，它天然带有容量/流动性/交易所上线事件约束，不能和普通 liquid majors 同一套 router 混用。

## 3.5 策略拆解（必填）

- 方向属性：逆势 / 事件驱动 / single-asset short
- 基础 alpha：新币上线初期价格泡沫在 funding 为正、价格仍处高位时更容易向下回归
- regime：仅限新上线合约的早期窗口；不适用于成熟大币常态行情
- filter / veto：上线满 `3d`、最近 `3d` 高位 `95%`、funding `> 0`；实盘还要加盘口深度、borrow/费率、涨跌停/异常撮合 veto
- risk / sizing / execution overlay：固定 notional 或波动缩放；`15m/5m` 分批 maker-first 入场；硬 SL、TP、最大持有天数；单币和同批上市币组总风险上限

## 4. 可复刻的最小实验

- 研究假设：新上币在上线 `3~7d` 内若再次冲到短窗高位，且 funding 为正，后续 `3h~3d` 更容易下跌而不是继续趋势。
- 可计算定义：`age_days >= 3` 且 `close >= rolling_high_3d 的 95% 分位` 且 `last_funding > 0` 时 short；比较 `TP/SL/timeout = 8/5/3d`、`15/8/7d`、`30/15/30d`。
- 最小回测切口：Binance USDⓈ-M 新上市 USDT perps，`15m` 父级信号，`5m/3m` 做 child execution；样本按上市月份做 walk-forward，避免只吃 2025 meme season。
- 先看指标：每笔 net bps / net %、trade count、按上市批次 positive ratio、最大单币回撤、TP vs SL 的触发时间分布。

## 5. 风险与保留意见

最大风险是样本选择与时代性：2025 新币/meme 币结构可能特别适合 short bubble fade，但未来若上线机制、做市质量或监管改变，edge 会变薄。第二个风险是实盘可做性：新币上线早期盘口薄、滑点大、强平/插针多，`8bps` 成本假设偏乐观；真正 admission 必须加 depth / impact / borrow / funding-cashflow / symbol blacklist。第三，repo 原逻辑会在同一币上多次重复开空，可能把单币风险放大；desk 版应限制每个 symbol 每个 listing window 的最多交易次数。

## 6. 来源

- frozen-cherry. (2026). *Binance Futures Short Strategy Backtester*. GitHub repo. Repo URL: https://github.com/frozen-cherry/binance-futures-short-strategy
- Source files audited: `README.md`, `config.py`, `run_full_backtest.py`, `binance_new_contracts_2025.json`
- Public-data probe artifacts:
  - `reports/artifacts/quant_digests/2026-04-22_newlisting_short_probe.py`
  - `reports/artifacts/quant_digests/newlisting_short_15m_summary_2026-04-22.csv`
  - `reports/artifacts/quant_digests/newlisting_short_15m_trades_2026-04-22.csv`
