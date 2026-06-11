# Xiaomi HK Dataset (M1 bootstrap)

## Source
- Provider: `yfinance`
- Ticker: `1810.HK` (Xiaomi Corp, HK)
- Interval: `1d`

## Saved Files
- Raw 5y: `data/raw/yfinance/hk/1810.HK_1d_5y_raw.csv`
- Raw 1y: `data/raw/yfinance/hk/1810.HK_1d_1y_raw.csv`
- Silver (standardized): `data/silver/hk/1810.HK_1d_5y_silver.csv`

## Current Snapshot (2026-02-28)
- 5y rows: 1228
- 1y rows: 247
- 5y range: `2021-03-01` to `2026-02-27` (UTC)

## Silver Schema
Columns:
- `timestamp`
- `symbol`
- `open`
- `high`
- `low`
- `close`
- `volume`
- `market`
- `timeframe`
- `source`

## Quick Verification
```bash
cd jerry/momentum
source .venv/bin/activate
python - <<'PY'
import pandas as pd
p='data/silver/hk/1810.HK_1d_5y_silver.csv'
df=pd.read_csv(p)
print('rows:', len(df))
print('cols:', list(df.columns))
print('range:', df['timestamp'].iloc[0], '->', df['timestamp'].iloc[-1])
PY
```
