# Maintenance Guide (M1)

本文档用于记录当前可复现的本地维护流程。

## 1) 环境维护

### 创建/重建虚拟环境
```bash
cd jerry/momentum
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-m1.txt
```

### 依赖健康检查
```bash
python -c "import backtrader,pandas,yaml,matplotlib,yfinance; print('deps ok')"
```

## 2) 数据维护（小米港股示例）

### 当前基线文件
- `data/raw/yfinance/hk/1810.HK_1d_1y_raw.csv`
- `data/raw/yfinance/hk/1810.HK_1d_5y_raw.csv`
- `data/silver/hk/1810.HK_1d_5y_silver.csv`

### 重新拉取（示例）
```bash
cd jerry/momentum
source .venv/bin/activate
python - <<'PY'
import yfinance as yf
import pandas as pd
from pathlib import Path

symbol='1810.HK'
Path('data/raw/yfinance/hk').mkdir(parents=True, exist_ok=True)
Path('data/silver/hk').mkdir(parents=True, exist_ok=True)

raw5 = yf.download(symbol, period='5y', interval='1d', auto_adjust=False, progress=False)
raw1 = yf.download(symbol, period='1y', interval='1d', auto_adjust=False, progress=False)
raw5.to_csv('data/raw/yfinance/hk/1810.HK_1d_5y_raw.csv')
raw1.to_csv('data/raw/yfinance/hk/1810.HK_1d_1y_raw.csv')

if isinstance(raw5.columns, pd.MultiIndex):
    raw5.columns = [c[0] if isinstance(c, tuple) else c for c in raw5.columns]

df = raw5.reset_index().rename(columns={
    'Date':'timestamp','Open':'open','High':'high','Low':'low','Close':'close','Volume':'volume'
})
df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True).dt.strftime('%Y-%m-%dT%H:%M:%SZ')
df['symbol'] = symbol
df['market'] = 'hk_equity'
df['timeframe'] = '1d'
df['source'] = 'yfinance'
df = df[['timestamp','symbol','open','high','low','close','volume','market','timeframe','source']]
df.to_csv('data/silver/hk/1810.HK_1d_5y_silver.csv', index=False)
print('rows:', len(df), 'range:', df['timestamp'].iloc[0], '->', df['timestamp'].iloc[-1])
PY
```

## 3) 文档维护建议

每次关键变更后，至少同步更新：
- `README.md`（当前阶段和完成项）
- `docs/ROADMAP.md`（勾选进度）
- `docs/PROJECT_TREE.md`（结构变化）
- 对应专题文档（例如新增数据源时更新 `docs/DATASET_*.md`）

## 4) 筹码分布脚本使用

```bash
cd jerry/momentum
source .venv/bin/activate
python scripts/build_chip_distribution.py --symbols 1810.HK
```

输出目录：`outputs/chip_distribution/`

## 5) 上涨浪/下跌浪信号脚本使用

默认参数来源：`config/signals/up_down_wave.yaml`

```bash
cd jerry/momentum
source .venv/bin/activate
python scripts/build_up_down_wave_signals.py
```

## 6) Up/Down Wave 粗略回测（5日持有）

```bash
cd jerry/momentum
source .venv/bin/activate
python scripts/backtest_wave_hold.py
```

## 7) 生成与发布网页报告（UpWave/DownWave）

```bash
cd jerry/momentum
source .venv/bin/activate
python scripts/build_updownwave_report.py
bash scripts/publish_report_site.sh
```

或使用流水线入口：
```bash
python scripts/run_report_pipeline.py --stage all
```

仅更新文字洞察（快速，不重跑全量回测）：
```bash
python scripts/run_report_pipeline.py --stage insights
```

## 8) M1 下一步建议
1. 增加最小回测入口（`src/momentum/engines/backtrader_engine.py`）
2. 增加第一版策略实现与参数读取
3. 增加回测结果落盘（`outputs/`）与最小报告
4. 将筹码分布特征接入策略信号
