# Signal Pipeline（信号流水线维护指南）

这是当前仓库里“从数据到信号再到粗测”的最短闭环。

## Step 0: 准备输入数据
- 使用 `data/silver/...` 的标准化 OHLCV 数据。
- 当前默认示例：`1810.HK`（小米，5y，1d）。

## Step 1: 生成 Up/Down Wave 信号
```bash
python scripts/build_up_down_wave_signals.py
```
产物：`outputs/signals/1810.HK_up_down_wave_ma20.csv`

## Step 2: 执行 5 日事件回测
```bash
python scripts/backtest_wave_hold.py
```
产物：`outputs/backtests/wave_hold_5d/*`

## Step 3: 查看关键指标
重点看：
- `win_rate`
- `avg_ret`
- `median_ret`
- 按 `upwave/downwave` 分开看

## 目录映射
- 规则定义文档：`docs/SIGNALS_UP_DOWN_WAVE.md`
- 信号计算代码：`src/momentum/signals/up_down_wave.py`
- 回测代码：`src/momentum/analytics/wave_hold_backtest.py`
- 运行脚本：`scripts/build_up_down_wave_signals.py`, `scripts/backtest_wave_hold.py`
- 默认参数：`config/signals/up_down_wave.yaml`

## 维护约定（推荐）
1. 先改文档，再改代码，再补测试。
2. 信号规则改动必须补 `tests/unit/test_up_down_wave.py`。
3. 回测规则改动必须补 `tests/unit/test_wave_hold_backtest.py`。
4. 提交时在 commit message 里标注是 `signal-rule` 还是 `backtest-rule` 变更。
