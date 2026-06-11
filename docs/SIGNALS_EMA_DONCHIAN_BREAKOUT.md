# SIGNALS_EMA_DONCHIAN_BREAKOUT

一个学习型趋势系统模板：

- **方向层**：1h EMA 结构
- **触发层**：5m Donchian breakout
- **确认层**：连续收盘站稳上轨/下轨
- **风控层**：ATR 止损（在回测模块中处理）

## 角色定位

这不是“最优策略”，而是一个适合教学与 baseline 研究的最小模板。

它的目标是把趋势系统拆成清晰分层：
- 能不能做（方向 / 结构）
- 什么时候做（突破触发）
- 要不要再稳一点做（收盘确认）
- 做错了怎么退（ATR 止损）

## 规则定义

### 方向层（1h EMA 结构）

- `ema_1h = EMA(close_1h, ema_window_1h)`
- 多头偏置：`close_1h > ema_1h`
- 可选：`ema_1h` 斜率为正

### 触发层（Donchian breakout）

- `donchian_upper = rolling_max(high.shift(1), N)`
- `donchian_lower = rolling_min(low.shift(1), N)`
- 多头突破：`close > donchian_upper`
- 空头突破：`close < donchian_lower`

### 确认层（收盘确认）

- 连续 `confirm_bars` 根收盘维持在上轨之上 / 下轨之下

### 风控层（ATR 止损）

- 入场后：
  - 多头止损：`entry - atr_mult * ATR`
  - 空头止损：`entry + atr_mult * ATR`

## 当前教学结论

- 均线结构更适合做方向过滤
- Donchian breakout 更适合做触发
- 对 5m / 15m 来说，收盘确认通常比“盘中刺破”更适合做 baseline
- ATR 止损适合与入场逻辑分层处理，不要混在方向判断里

## 代码位置

- 信号模块：`src/momentum/signals/ema_donchian_breakout.py`
- 回测模块：`src/momentum/analytics/ema_donchian_breakout_backtest.py`
- 报告脚本：`scripts/build_ema_donchian_breakout_report.py`
