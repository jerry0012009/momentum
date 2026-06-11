# SIGNALS_MARKET_RISK_ON_OFF_FILTER

market-level risk-on / risk-off gate，用于给 `multi_tf_momentum` 这种趋势策略做“是否开机”的环境门控。

## 角色定位

这不是预测涨跌方向的新因子。

它回答的是：
- 当前大环境是否偏 risk-on？
- 这种环境值不值得让趋势策略上场？
- 我们是在“该开机的时候开机”，还是在坏环境里硬做？

所以它更接近：
- 环境门控层
- 策略启停层
- 介于底层信号与真正执行之间

## baseline v1：3 个最小可算特征

统一在 1h 上计算：

1. `trend_ok_1h`
   - `trend_1h = close / close.shift(trend_window_1h) - 1`
   - 条件：`trend_1h > trend_threshold_1h`

2. `ema_ok_1h`
   - 条件：`close_1h > EMA(ema_window_1h)`

3. `vol_ok_1h`
   - `rv_1h = rolling_std(ret_1h, vol_window_1h)`
   - 条件：`rv_1h <= rolling_quantile(rv_1h, vol_quantile_window_1h, vol_quantile_max)`

最终：

- `risk_on_score = trend_ok_1h + ema_ok_1h + vol_ok_1h`
- `risk_on_pass = risk_on_score >= min_pass_count`

然后：

- `long_signal = base_long_signal and risk_on_pass`
- `short_signal = base_short_signal and risk_on_pass`

## 直觉解释

这是一个很朴素的“开机检查表”：

- 趋势在不在？
- 位置差不差？
- 风险有没有过热？

至少满足其中 2/3，才允许策略出手。

## 代码位置

- 信号模块：`src/momentum/signals/market_risk_on_off_filter.py`
- 单测：`tests/unit/test_market_risk_on_off_filter.py`
- 报告集成：`scripts/build_multi_tf_momentum_report.py`

## 当前研究定位

- 这是模块 D 的 second baseline（比 trend/choppy gate 更高一层）
- 目标不是做复杂 regime 分类，而是先验证一个最小可解释 risk-on/off 门控是否值得保留
