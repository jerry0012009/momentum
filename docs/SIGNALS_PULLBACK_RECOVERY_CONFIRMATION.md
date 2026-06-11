# SIGNALS_PULLBACK_RECOVERY_CONFIRMATION

在多周期动量 baseline 上，增加“缩量回调 + 放量恢复”确认的信号模块。

## 思路

- **趋势**：沿用多周期动量（5m / 15m 同向）
- **回调**：最近 `pullback_lookback` 根内出现逆向 bar，且该阶段平均 `vol_z < 0`
- **恢复**：当前 bar 突破前 `breakout_lookback` 根高点/低点，且 `vol_z > vol_recover_th`

## 代码位置

- 信号模块：`src/momentum/signals/pullback_recovery_confirmation.py`
- 报告脚本：`scripts/build_pullback_recovery_confirmation_report.py`
- 单测：`tests/unit/test_pullback_recovery_confirmation.py`

## 核心参数

- `pullback_lookback`: 回调窗口
- `vol_recover_th`: 恢复阶段的成交量 z-score 阈值
- `breakout_lookback`: 恢复突破时参考的前高/前低窗口

## 默认研究网格

- `pullback_lookback = [1, 2, 3]`
- `vol_recover_th = [0.5, 1.0, 1.5]`
- `breakout_lookback = [1, 2, 3]`

共 27 组参数。

## 报告输出

- `reports/artifacts/pullback_recovery_confirmation/`
- `reports/site/factors/pullback_recovery_confirmation/report.html`

## 研究定位

这是一个 **量价确认模块**，不是独立完整策略。它的目标是回答：

> 在裸多周期动量基础上，加入“缩量回调 + 放量恢复”是否能提升信号质量？
