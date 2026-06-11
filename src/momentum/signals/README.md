# signals

## 职责
- 将因子结果转换为交易信号（如 long/flat）

## 当前状态
- 默认参数配置：`config/signals/up_down_wave.yaml`
- 已实现 `up_down_wave.py`：
  - Pandas 批处理函数 `compute_up_down_wave_signals`
  - Backtrader 指标 `UpDownWaveIndicator`
- 已实现 `regime_triplet.py`：
  - `compute_regime_triplet_signals`（up/side/down regime）
- 已实现 `box_consolidation.py`：
  - `compute_box_consolidation_signals`
  - 输出 `narrow_accum_ready` / `box_breakout_ready` / `accumulation_ready`
  - 对应配置：`config/signals/box_consolidation.yaml`
- 已实现 `multi_tf_momentum.py`：
  - `compute_multi_tf_momentum_signals`
  - 输出 `mom_5m` / `mom_15m` / `long_signal` / `short_signal`
  - 对应配置：`config/signals/multi_tf_momentum.yaml`
- 已实现 `pullback_recovery_confirmation.py`：
  - `compute_pullback_recovery_confirmation_signals`
  - 在多周期动量基础上增加“缩量回调 + 放量恢复”确认
  - 输出 `vol_z` / `long_pullback_ok` / `long_recovery_ok` / `long_signal` 等中间列
## M1 进展
- 已新增 `trendline_breakout_navigator.py`：clean reimplementation 的趋势线突破导航信号

## M1 下一步
- 将 UpWave/DownWave 接入策略决策流程
- 叠加筹码分布特征形成组合信号
- 继续对照 `pytrendline` / 外部 breakout 逻辑，审计参数稳定性与因果口径
