# Rank444 — Data Contract

## 当前数据来源

### 1. yfinance（美股、国际期货、黄金）

| 字段 | 说明 |
|------|------|
| 来源 | Yahoo Finance API（`yfinance` Python 库） |
| 调用方式 | `yf.Ticker(symbol).history(start, end, auto_adjust=True)` |
| 复权 | `auto_adjust=True` → 自动前复权 |
| 时区 | 原始返回带时区信息，代码中 `.dt.tz_localize(None)` 去除 |
| 时间区间 | v1: 3年; v2-v6: 3-15年不等 |
| 频率 | 1d（主）, 1h, 15m（部分测试） |

### 2. akshare（A股、国内期货）

| 字段 | 说明 |
|------|------|
| 来源 | akshare 库（新浪/东财等国内数据源） |
| A股调用 | `ak.stock_zh_a_hist(symbol, period="daily", adjust="qfq")` |
| 期货调用 | `ak.futures_zh_daily_sina(symbol)` |
| 复权 | A股: `adjust="qfq"`（前复权）; 期货: 不涉及复权 |
| 时区 | 无时区信息（假设为北京时间） |
| 时间区间 | 2-3年（A股）; 2022年起（期货） |

## 数据问题（Critical）

### ❌ 数据未固化

**当前状态：** 每次运行脚本都实时从 API 拉取数据。不存在 `data/cache/` 或任何本地数据快照。

**后果：**
- 同一脚本在不同日期运行，可能拿到不同的数据（yfinance 会修正历史数据）
- 无法复现今天的结果
- Yahoo Finance 偶尔调整历史收盘价（dividend adjustment, split correction）

### ❌ 无 manifest.json

按照 DATA_CONTRACT.md 标准，应产出：

```json
{
  "name": "rank444_rsi_bb",
  "source": "yfinance / akshare",
  "downloaded_at": "<timestamp>",
  "symbols": [],
  "timeframe": "1d",
  "data_start": "",
  "data_end": "",
  "adjusted_or_raw": "auto_adjust=True / qfq",
  "script": "scripts/rank444_rsi_bb_backtest.py",
  "commit_sha": ""
}
```

当前不存在。

### ❌ 无标准化数据目录

DATA_CONTRACT.md 要求的目录结构：

```text
data/raw/<source>/<market>/...          ← 不存在
data/bronze/<market>/...                ← 不存在
data/silver/<market>/...                ← 不存在
data/features/<market>/<strategy>/...   ← 不存在
data/cache/<name>/bars.parquet          ← 不存在
data/cache/<name>/manifest.json         ← 不存在
```

### ⚠️ 时区不一致

- yfinance 数据被 `tz_localize(None)` 去除了时区
- akshare 数据无时区信息
- 两者混合使用时，跨市场对齐可能有时区偏移问题

### ⚠️ 复权方式不透明

- yfinance `auto_adjust=True` 的具体复权算法未文档化
- akshare `adjust="qfq"` 是前复权，但不同版本 akshare 可能有差异

## 标的覆盖

### v1 回测（13 标的）

| 标的 | 代码 | 市场 | 数据源 |
|------|------|------|--------|
| 贵州茅台 | 600519 | A股 | akshare |
| 中国平安 | 601318 | A股 | akshare |
| 宁德时代 | 300750 | A股 | akshare |
| 招商银行 | 600036 | A股 | akshare |
| 五粮液 | 000858 | A股 | akshare |
| 苹果 | AAPL | 美股 | yfinance |
| 特斯拉 | TSLA | 美股 | yfinance |
| 标普500 ETF | SPY | 美股 | yfinance |
| 纳指100 ETF | QQQ | 美股 | yfinance |
| COMEX 黄金 | GC=F | 期货 | yfinance |
| 黄金 ETF | GLD | 黄金 | yfinance |
| WTI 原油 | CL=F | 期货 | yfinance |
| COMEX 铜 | HG=F | 期货 | yfinance |

### v2-v6 扩展

- 增加 MSFT, SI=F（白银）
- 增加 14 个国内期货（I0/RB0/J0/JM0/CU0/AL0/ZN0/AU0/AG0/SC0/P0/M0/SR0/LC0）

### 潜在偏差

- **存活者偏差** — 标的选择偏向当前知名/流动性好的标的
- **A股样本极小** — 仅 5 只大盘股，不代表 A 股全貌
- **无加密货币** — 未覆盖 crypto

## 修复建议

1. **立即固化当前数据** — 跑一次 `save_data_snapshot.py`，存为 parquet + manifest
2. **统一时区** — 全部存为 UTC，展示层再转
3. **文档化复权逻辑** — 明确 auto_adjust=True 对 OHLCV 各字段的调整方式
4. **扩展标的池** — 加入随机抽样或分层抽样，减少存活者偏差
