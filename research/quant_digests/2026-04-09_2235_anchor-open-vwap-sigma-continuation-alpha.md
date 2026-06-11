# 别把这套 SPY 日内策略只读成 equities ORB：对 crypto short-cycle desk，更该先测的是「anchor-open displacement × minute-vol breakout continuation」
- 时间：2026-04-09 22:35 UTC
- 类型：2025 GitHub repo source audit（配套 2024 SSRN 论文 metadata + Concretum writeup）
- 主题类型：raw alpha
- 基础 alpha：会话早段相对 `open / prev_close / session VWAP` 的异常同向位移，若已超过“这个分钟平时该有的噪音”，更容易在该会话剩余时间继续扩展
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：trend / momentum / session-anchor / VWAP / volatility-normalization / continuation
- 证据类型：工程实现 + 论文 metadata / 二手写作

## 1. 这次看了什么
主看 **Carlo Zarattini, Andrew Aziz, Andrea Barbon (2024), _Beat the Market: An Effective Intraday Momentum Strategy for S&P500 ETF (SPY)_** 的 DOI / metadata，再配合 **Ascensao/Ascensao-intraday-momentum-strategy** 的实现代码与 Concretum 的可读总结。要先说清楚：**这轮没直接拿到 SSRN 正文 PDF**，所以业绩数字来自 Concretum writeup，规则细节主要来自 repo 源码，而不是我假装完整通读了 paper。

## 2. 核心结论
- **一句话核心结论：** 不是“开盘涨了就追”，而是“如果开盘后不久的价格位移已经大到超过该分钟历史常态波动、且方向与 session VWAP 一致，后面更像继续走，不像立刻回去”。
- **一句话证明方式：** 这条线用分钟级 `sigma_open` 做标准化 breakout，再配合 VWAP 对齐、波动率目标仓位和会话内平仓；Concretum writeup 引的样本期 `2007-2024` 结果约为 **累计 `1985%`、年化 `19.6%`、Sharpe `1.33`**。
- repo 最值钱的不是“SPY 早盘追单”本身，而是它把 **entry / sizing / exit** 写得很完整：`prepare_indicators.py` 先按 `minute_of_day` 计算过去 `14` 天同一分钟的 `sigma_open`；`backtest_strategy.py` 再用 `UB/LB` 与 `VWAP` 生成多空信号。
- 规则骨架非常清楚：多头要求 `close > UB` 且 `close > VWAP`，空头对称；`UB/LB` 以 `max(open, prev_close)` / `min(open, prev_close)` 为基准，再乘 `1 ± band_mult * sigma_open`；仓位按 `volatility_target / rolling_vol` 调整，杠杆上限 `4x`。
- 对我们 desk，真正值得抄的不是“美股开盘”，而是 **minute-of-session 波动标准化 + session VWAP 同向确认** 这一层；它比朴素 opening-range breakout 更像一个可迁移的短周期 raw alpha 壳。

## 3. 为什么和当前项目有关
这条线直接补的是 **trend / momentum raw alpha**，不是纯 filter。它尤其适合当前 `1m / 3m / 5m / 15m` desk，因为它天然回答了 4 个最常见问题：
- 什么时候算“真突破”，不是噪音？→ 用 `sigma_open`
- 为什么不是乱追？→ 必须和 session VWAP 同向
- 仓位怎么放？→ 波动率目标 + leverage cap
- 当天怎么收？→ 会话内平仓，不把日内 alpha 硬拖成隔夜持有

## 3.5 策略拆解（必填）
- 方向属性：顺势
- 基础 alpha：会话早段异常位移 × 会话内 continuation
- regime：存在明确 anchor 的会话（如美股开盘、UTC 固定时段、4h pseudo-session）
- filter / veto：价格必须和 session VWAP 同向；`sigma_open` 不可缺失
- risk / sizing / execution overlay：`volatility_target=2%`、`max_leverage=4`、信号翻转退出、会话结束强平；源码里手续费按 SPY 每股口径处理，迁到 crypto 必须重建 fee/slippage 模型

## 4. 可复刻的最小实验
- **研究假设：** 在 crypto 里，若某个 anchor session 的前 `15-30m` 已出现超出 same-minute 常态波动的 open-displacement，且价格位于 session VWAP 同侧，则未来 `3-12` 根 `5m` 更可能继续同向。
- **可计算定义：** 对每个锚点会话计算 `session_open`、`session_vwap`、`move_open`，再按过去 `14` 个同类会话的同一分钟求 `sigma_open`；若 `close > max(session_open, prev_session_close) * (1 + sigma_open)` 且 `close > session_vwap`，开多；空头对称。
- **最小回测切口：** Binance USDⓈ-M `BTC / ETH / SOL`，`1m` 原始数据聚合到 `5m` 执行，样本先做近 `120-180d`；anchor 先比三组：`UTC 00:00`、`UTC 08:00`、`13:30 UTC`（美股开盘 proxy）。
- **最该先看：** `post-cost expectancy / trade`、anchor 分组后的胜率与 `time-in-market`；第二眼再看 session 内 MFE/MAE，判断它是快 continuation 还是拖尾趋势。

## 5. 风险与保留意见
- 这条 edge 有明显 **session 依赖**；SPY 有真实开盘，crypto 是 `24/7`，所以不能假装所有 UTC 分钟都一样。
- 当前 repo 的实现比文章描述更朴素，主要是 **信号翻转 / 会话收盘退出**；如果要搬到 crypto，可能还要补 time-stop 与 maker/taker 分流。
- 源码里的手续费口径是美股每股收费，不可直接拿来判断 crypto 成本后生存性。
- 若 anchor 选错，这条线很容易退化成“高噪音 breakout 追单”。所以第一步不是全市场上线，而是先做 **anchor ranking**。

## 6. 来源
1. **Carlo Zarattini, Andrew Aziz, Andrea Barbon. (2024). _Beat the Market: An Effective Intraday Momentum Strategy for S&P500 ETF (SPY)_. SSRN Working Paper.**
   - DOI: `10.2139/ssrn.4824172`
   - Readable URL: `https://doi.org/10.2139/ssrn.4824172`
   - SSRN URL: `https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4824172`
2. **Concretum Group. _Beat the Market: An Effective Intraday Momentum Strategy for S&P500 ETF SPY_.**
   - URL: `https://concretumgroup.com/beat-the-market-an-effective-intraday-momentum-strategy-for-sp500-etf-spy/`
3. **Ascensao. _Ascensao-intraday-momentum-strategy_. GitHub repository.**
   - Repo URL: `https://github.com/Ascensao/Ascensao-intraday-momentum-strategy`
   - 本轮主要审阅：`README.md`、`prepare_indicators.py`、`backtest_strategy.py`
