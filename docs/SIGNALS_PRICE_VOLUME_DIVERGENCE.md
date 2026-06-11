# SIGNALS_PRICE_VOLUME_DIVERGENCE

量价背离（baseline A）过滤器，用于给多周期动量策略做“不要追弱量突破”的过滤。

## 角色定位

这不是一个独立反转主策略。

它更像：
- 趋势衰竭预警
- 不追高 / 不追空过滤器
- 给已有趋势信号提纯

## baseline A 规则定义

### 多头方向（bearish divergence warning）
当同时满足：

1. 价格创新高
   - `close[t] > rolling_high(close, N)[t-1]`
2. 当前突破 bar 的 `vol_z` 比“上一次向上突破 bar”的 `vol_z` 更弱
   - `vol_z[t] < prev_up_breakout_vol_z - delta`
3. 当前量能没有达到强确认阈值
   - `vol_z[t] < z_confirm`

则记为：
- `bearish_divergence_event = 1`
- 并在接下来 `warning_active_bars` 根内维持 `bearish_divergence_warning = 1`

含义：
- 价格还在创新高
- 但这次突破的量能不如上一次
- 因此不追这次多头突破

### 空头方向（bullish divergence warning）
对称定义：

1. 价格创新低
2. 当前向下突破 bar 的 `vol_z` 比“上一次向下突破 bar”的 `vol_z` 更弱
3. `vol_z[t] < z_confirm`

则记为：
- `bullish_divergence_event = 1`
- 并在接下来 `warning_active_bars` 根内维持 `bullish_divergence_warning = 1`

含义：
- 价格还在创新低
- 但这次下破的量能不如上一次
- 因此不追这次空头突破

## 与 multi_tf_momentum 的关系

先得到 base trend：
- `base_long_signal`
- `base_short_signal`

再做过滤：
- `long_signal = base_long_signal and not bearish_divergence_warning`
- `short_signal = base_short_signal and not bullish_divergence_warning`

## 代码位置

- 信号模块：`src/momentum/signals/price_volume_divergence.py`
- 报告脚本：`scripts/build_price_volume_divergence_report.py`
- 单测：`tests/unit/test_price_volume_divergence.py`

## 输出列

- `base_long_signal`
- `base_short_signal`
- `vol_z`
- `up_breakout_event`
- `down_breakout_event`
- `prev_up_breakout_vol_z`
- `prev_down_breakout_vol_z`
- `bearish_divergence_event`
- `bullish_divergence_event`
- `bearish_divergence_warning`
- `bullish_divergence_warning`
- `long_filtered_out`
- `short_filtered_out`
- `long_signal`
- `short_signal`

## 当前默认参数（baseline）

- `breakout_lookback = 24`
- `divergence_delta_z = 0.5`
- `z_confirm = 0.5`
- `warning_active_bars = 3`

## 说明

- 当前只实现 baseline A：比较“这次 breakout vs 上一次 breakout”的 `vol_z`。
- 用户已明确选择先做 A；更复杂的摆点背离（baseline B）留到后续学习地图。
- 这套规则更适合先验证：
  - 是否减少假突破
  - 是否减少追高 / 追空
  - 是否在不显著削弱有效趋势的前提下提升 signal quality
