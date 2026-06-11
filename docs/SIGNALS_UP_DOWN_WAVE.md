# UpWave / DownWave 信号（学习笔记落地版）

本文档对应你当前学习的第一组信号定义，已落地为可复用代码。

## 1) 规则定义（t 日收盘后确认）

### UpWave(t)
满足以下条件记为 `1`，否则 `0`：
1. `t-3` 是阳线：`close[t-3] > open[t-3]`
2. `close[t-3], close[t-2], close[t-1], close[t]` 全部在 `MA20` 上方

### DownWave(t)
满足以下条件记为 `1`，否则 `0`：
1. `close[t-3], close[t-2], close[t-1], close[t]` 全部在 `MA20` 下方

> 这是经典的：`MA过滤 + 连续4根持久性过滤 (persistence filter)`。

## 2) 与“未来函数”关系
- 信号仅使用 `t` 及更早数据（`t-3..t`）计算。
- 在后续粗略回测中，统一使用 `t+1` 开盘进场，避免未来函数。

## 3) 代码位置
- 信号模块：`src/momentum/signals/up_down_wave.py`
  - `compute_up_down_wave_signals`（Pandas 批处理）
  - `UpDownWaveIndicator`（Backtrader 指标）
- 信号脚本：`scripts/build_up_down_wave_signals.py`
- 配置文件：`config/signals/up_down_wave.yaml`

## 4) 默认配置
见 `config/signals/up_down_wave.yaml`：
- `ma_period: 20`
- 默认输入：小米 5y silver
- 默认输出：`outputs/signals/1810.HK_up_down_wave_ma20.csv`

## 5) 运行方式
```bash
cd jerry/momentum
source .venv/bin/activate

# 用默认配置运行（推荐）
python scripts/build_up_down_wave_signals.py

# 或显式参数
python scripts/build_up_down_wave_signals.py \
  --input data/silver/hk/1810.HK_1d_5y_silver.csv \
  --output outputs/signals/1810.HK_up_down_wave_ma20.csv \
  --ma-period 20 \
  --symbol 1810.HK
```

## 6) 输出字段
- `timestamp`
- `symbol`
- `open`
- `close`
- `ma_20`（当 `ma_period=20`）
- `upwave`（0/1）
- `downwave`（0/1）

## 7) 维护建议
- 修改信号定义时，先改本文件，再改代码与测试。
- 每次规则改动，必须同步更新 `tests/unit/test_up_down_wave.py`。
- 新信号建议遵循同样模式：
  1) 纯函数计算（pandas）
  2) 可接入回测引擎的 Indicator（backtrader）
  3) 独立脚本 + 配置文件 + 文档
