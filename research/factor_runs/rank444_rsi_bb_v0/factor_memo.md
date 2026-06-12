# Rank444 — Factor Memo

## 1. 这个研究捕捉什么市场现象？

Rank444 研究的是**均值回归（mean reversion）**现象：当资产价格短期极端偏离均值后，倾向于向均值回归。

具体场景：当价格同时满足两个条件时——
- RSI 低于阈值（超卖）
- 收盘价跌破布林带下轨（统计极端）

——预期价格会反弹回布林带中轨附近。

这是一种经典的"统计极端后押注回归"的思路，本质上是赌分布的尾部不会持续。

## 2. 它包含哪些 factor？

当前代码中**没有独立的 factor 产物**。以下 factor 计算嵌入在回测函数内部：

| Factor | 公式 | 窗口 | 说明 |
|--------|------|------|------|
| RSI(7) | `100 - 100/(1 + avg_gain/avg_loss)` | 7 bars | Wilder 平滑，com=period-1 |
| BB_mid(20) | `SMA(close, 20)` | 20 bars | 布林带中轨 |
| BB_upper(20) | `BB_mid + 2*std(close,20)` | 20 bars | 上轨 |
| BB_lower(20) | `BB_mid - 2*std(close,20)` | 20 bars | 下轨 |
| BB_zscore（隐含） | `(close - BB_mid) / (2*std)` | 20 bars | 未显式计算，但等价于"是否跌破下轨" |

**注意：** 这些 factor 没有独立的 `data/features/` 产物，无法单独审计或复用。

## 3. 它包含哪些 signal？

| Signal | 规则 | 含义 |
|--------|------|------|
| entry_signal | `RSI(7) < 30 AND close < BB_lower(20)` | 超卖 + 跌破下轨 → 做多 |
| exit_signal_v1 | `close > BB_mid(20)` | 价格回到中轨上方 → 平仓（推荐版本） |
| exit_signal_v2 | `close > open` | 收阳线即平仓（源码原始版本，已被标记为 bug） |

**Signal 时间戳问题：**
- `signal_time = close[t]`（bar 收盘时才知道）
- `execution_price = close[t]`（同一根 bar 的收盘价执行）
- 这是 **same-bar signal + execution**，存在乐观偏差

## 4. 它包含哪些 strategy rules？

### 入场
- **方向：** 仅做多（long-only）
- **仓位：** 100% 资金投入（单标的回测）
- **执行：** 信号 bar 收盘价

### 出场
- **主方案（middle_band）：** 收盘价 > BB 中轨
- **备选方案（close_gt_open）：** 收阳线（已被确认为逻辑 bug）
- **无止损：** 当前版本没有止损
- **无止盈：** 以中轨为唯一目标

### 成本
- **手续费：** 0.1% 单边（0.2% 往返）
- **滑点：** 未建模
- **Spread：** 未建模
- **资金成本：** 未建模

### 参数网格（v2 稳定性测试）
- RSI period: [5, 7, 10, 14]
- RSI limit: [25, 30, 35]
- BB period: [15, 20, 25]
- BB mult: [1.5, 2.0, 2.5]
- 共 144 种组合

## 5. 当前结论是否可信？

**部分可信，但有重大 caveat：**

### 可信部分
- 美股大盘 ETF（SPY/QQQ）长期日线做多方向确实有利可图
- 策略核心 alpha 来源是"空仓避险"——在统计极端时不入场，避免了部分下跌
- 参数稳定性测试显示 144 组合中多数盈利（方向一致）
- 时间稳定性：15 年回测中多数年份正收益

### 不可信 / 待验证部分
- **绝对收益数字不可信** — same-bar execution + 无滑点 → 乐观偏差
- **Sharpe 不可信** — trade-level 简化计算，非标准 bar-level
- **短线频率结果不可信** — 1h/15m 级别表现差，可能受数据质量和成本低估影响
- **期货结果可信度低** — 国内期货只有 3/14 盈利，样本不足
- **做空方向已证伪** — v6 显示做空普遍亏损（SPY -31%, AAPL -90%）

### 核心风险
1. Same-bar close execution 可能高估 10-30% 的收益
2. 无滑点假设在低流动性标的上严重低估真实成本
3. "空仓避险"的 alpha 可能只是 beta 的另一种表述

## 6. 下一步要拆出哪些标准产物？

按优先级：

### P0 — 阻断性修复（不做则其他审计无意义）
1. **数据固化** — 跑一次回测后把 OHLCV 存为 parquet + manifest.json
2. **信号/执行时间拆分** — `signal_time = close[t]`, `execution_price = open[t+1]`
3. **加入滑点** — 至少 5bps 默认滑点

### P1 — 独立产物拆分
4. **Factor values** — `data/features/rank444/factor_values.parquet`（RSI, BB_mid, BB_upper, BB_lower, BB_zscore）
5. **Signals** — `data/features/rank444/signals.parquet`（entry_signal, exit_signal, signal_time, tradable_at）
6. **Trades** — `reports/artifacts/rank444_rsi_bb/trades.parquet`（标准化列名）

### P2 — 指标修正
7. **标准 Sharpe** — bar-level equity curve 计算
8. **完整成本模型** — 加入 slippage_model, spread_assumption
9. **止损测试** — 8% stop-loss（HTML 报告已建议）

### P3 — 拆解 alpha 来源
10. **空仓时间分析** — 量化"空仓避险"贡献 vs 纯 entry timing alpha
11. **Beta 剥离** — 对 SPY 做 CAPM 回归，看残差 alpha 是否显著
