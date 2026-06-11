# SIGNALS_TREND_REGIME_FILTER

趋势 / 震荡 regime gate，用于给 `multi_tf_momentum` 这种趋势信号做环境过滤。

## 角色定位

这不是预测涨跌方向的因子。

它回答的是：
- 当前环境有没有足够方向？
- 当前环境的方向是否被噪音严重污染？
- 这种环境配不配让趋势信号上场？

## baseline 规则定义

定义：

- `ret[t] = close[t] / close[t-1] - 1`
- `trend_return[t] = close[t] / close[t-N] - 1`
- `trend_strength[t] = abs(trend_return[t])`
- `noise_level[t] = rolling_std(ret, N)`
- `regime_score[t] = trend_strength[t] / noise_level[t]`

通过条件：

- `trend_strength > trend_threshold`
- `regime_score > regime_score_threshold`

然后：

- `long_signal = base_long_signal and regime_filter_pass`
- `short_signal = base_short_signal and regime_filter_pass`

## 直觉解释

- `trend_strength` 告诉你：最近 N 根到底有没有明显走出来。
- `noise_level` 告诉你：这段路走得乱不乱。
- `regime_score` 告诉你：这个方向是不是足以压过噪音。

所以这个 gate 本质是在筛掉：
- 方向太弱的环境
- 高噪音、假突破很多的环境

## 默认参数（first baseline）

- `regime_window = 36`（约 3 小时）
- `trend_threshold = 0.015`
- `regime_score_threshold = 2.0`

这组默认值的含义：
- 最近约 3 小时至少走出 1.5%
- 且趋势强度至少大致达到噪音的 2 倍

## 代码位置

- 信号模块：`src/momentum/signals/trend_regime_filter.py`
- 单测：`tests/unit/test_trend_regime_filter.py`
- 报告集成：`scripts/build_multi_tf_momentum_report.py`

## 输出列

- `base_long_signal`
- `base_short_signal`
- `ret_1`
- `trend_return`
- `trend_strength`
- `noise_level`
- `regime_score`
- `regime_filter_pass`
- `long_filtered_out`
- `short_filtered_out`
- `long_signal`
- `short_signal`

## 当前研究定位

- 这是模块 D 的 first baseline，不是完整市场状态分类系统。
- 先做最小可用 gate，再研究更复杂的：
  - risk-on / risk-off
  - bull / bear / sideways
  - cross-asset regime
