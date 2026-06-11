# Data Contract (Draft)

## 标准 K 线字段
- `timestamp` (UTC, ISO8601)
- `symbol` (如 BTCUSDT)
- `open`
- `high`
- `low`
- `close`
- `volume`
- `market` (crypto | a_share | us_equity | gold)
- `timeframe` (1m/5m/1h/1d ...)
- `source` (交易所或数据提供方)

## 约束
1. 所有进入 `data/silver` 的数据都必须满足上述字段完整性。
2. 时区统一存储为 UTC；展示层再做本地时区转换。
3. 缺失值处理必须记录在数据处理日志中。

## 目录约定
- `data/raw/<source>/<market>/...`
- `data/bronze/<market>/...`
- `data/silver/<market>/...`
- `data/features/<market>/<strategy>/...`
