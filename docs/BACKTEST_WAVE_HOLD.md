# Wave Signal 粗略回测（事件法）

目标：快速验证 UpWave / DownWave 信号是否有方向性与正收益倾向。

## 1) 规则
- 信号在 `t` 日收盘后确认
- 在 `t+1` 开盘进场（无未来函数）
- 持有固定 `N` 个交易日（默认 5）
- 在 `t+N` 收盘离场
- `upwave` 做多，`downwave` 做空

## 2) 实现位置
- 核心函数：`src/momentum/analytics/wave_hold_backtest.py`
- 执行脚本：`scripts/backtest_wave_hold.py`
- 默认配置：`config/signals/up_down_wave.yaml` 中 `backtest` 段

## 3) 执行命令
```bash
cd jerry/momentum
source .venv/bin/activate

# 用默认配置（推荐）
python scripts/backtest_wave_hold.py

# 或显式参数
python scripts/backtest_wave_hold.py \
  --input outputs/signals/1810.HK_up_down_wave_ma20.csv \
  --output-dir outputs/backtests/wave_hold_5d \
  --hold-days 5
```

## 4) 输出文件
- `wave_hold_trades.csv`：每笔事件交易明细
- `wave_hold_summary.csv`：按 signal 汇总（胜率、均值、中位数）
- `wave_hold_meta.json`：参数与总体指标

## 5) 解释边界
- 这是“事件法粗测”，允许信号窗口重叠，不等同于完整组合回测。
- 当前默认不含滑点与借券成本；可通过 `fee_bps_roundtrip` 做简化扣费。
- 该回测用于“信号有效性初筛”，不是最终实盘绩效结论。
