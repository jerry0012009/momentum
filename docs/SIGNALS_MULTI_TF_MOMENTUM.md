# SIGNALS_MULTI_TF_MOMENTUM

多周期动量（5m / 15m）基线信号。

## 规则定义

在 5m bar 收盘时刻 `t`：

- `mom_5m(t, M) = close_5m[t] / close_5m[t-M] - 1`
- `mom_15m(T, N) = close_15m[T] / close_15m[T-N] - 1`
  - `T` 为 `t` 时刻之前最近一根已完成的 15m bar
  - 15m close 由 5m bars 重采样得到

信号：

- `long_signal = (mom_5m > th_5m) and (mom_15m > th_15m)`
- `short_signal = (mom_5m < -th_5m) and (mom_15m < -th_15m)`

## 代码位置

- 信号模块：`src/momentum/signals/multi_tf_momentum.py`
- 构建脚本：`scripts/build_multi_tf_momentum_signals.py`
- 配置文件：`config/signals/multi_tf_momentum.yaml`
- 单测：`tests/unit/test_multi_tf_momentum.py`

## 输出列

- `mom_5m`
- `mom_15m`
- `long_signal`
- `short_signal`

## 运行示例

```bash
cd jerry/momentum
source .venv/bin/activate

python scripts/build_multi_tf_momentum_signals.py \
  --input /path/to/your_5m_bars.csv \
  --output outputs/signals/multi_tf_momentum.csv \
  --window-5m 6 \
  --window-15m 6 \
  --threshold-5m 0.003 \
  --threshold-15m 0.006
```

## 说明

- 当前版本是信号层 baseline，只生成动量值与多空信号。
- 暂未包含持仓管理、反手规则、手续费/滑点扣减；这些属于回测/执行层。
- 若后续需要扩展，可继续加入：
  - 波动率标准化阈值
  - 市场状态过滤（regime filter）
  - 成交量确认
  - ATR 风控
