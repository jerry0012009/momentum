# Factor Library Pipeline Plan

> 本文档说明如何从 universe 数据生成因子值、标签、评价指标和报告。
> 当前状态：universe 已构建，目录结构和 schema 已就绪，以下步骤尚未执行。

## 已完成

- [x] `data/cache/crypto_top50_usdt_perp_1h/manifest.json` — 50 symbols
- [x] `data/cache/crypto_top50_usdt_perp_1h/universe_membership.parquet` — 507 rows
- [x] `data/cache/crypto_top50_usdt_perp_1h/bars_1h.parquet` — empty schema
- [x] `data/features/crypto_top50_usdt_perp_1h/labels.parquet` — empty schema
- [x] `data/features/crypto_top50_usdt_perp_1h/<factor>/factor_values.parquet` — 5 factors, empty schema
- [x] `docs/FACTOR_REGISTRY.md` — 5 factors registered, all SCOPED

## 待执行 Pipeline

### Step 1: 下载 OHLCV 数据

**脚本：** `scripts/fetch_crypto_top50_bars.py`（待创建）

**做什么：**
1. 读取 `manifest.json` 中的 50 个 symbols
2. 通过 Binance Futures API 下载每个 symbol 的 1h K线
3. 时间范围：建议最近 2 年（2024-06-01 ~ 2026-06-12），约 17,520 bars/symbol
4. 输出到 `data/cache/crypto_top50_usdt_perp_1h/bars_1h.parquet`
5. 更新 manifest.json 的 `data_start`, `data_end`, `downloaded_at`

**注意事项：**
- Binance API 限制：每次最多 1500 根 K线，需分页
- 50 symbols × ~12 pages = ~600 次 API 调用，约需 10-20 分钟
- 必须在下载完成后更新 manifest

**预估数据量：**
- 50 symbols × 17,520 bars × 13 columns ≈ ~50MB parquet

### Step 2: 计算标签（Labels）

**脚本：** `scripts/build_labels.py`（待创建）

**做什么：**
1. 读取 `bars_1h.parquet`
2. 对每个 symbol，计算 4 个前向收益：
   - `ret_fwd_1h = close[t+1] / close[t] - 1`
   - `ret_fwd_4h = close[t+4] / close[t] - 1`
   - `ret_fwd_24h = close[t+24] / close[t] - 1`
   - `ret_fwd_72h = close[t+72] / close[t] - 1`
3. 输出到 `data/features/crypto_top50_usdt_perp_1h/labels.parquet`

**Schema：**
```text
timestamp (UTC)  |  symbol  |  ret_fwd_1h  |  ret_fwd_4h  |  ret_fwd_24h  |  ret_fwd_72h
```

**注意：**
- 最后 72 行的 ret_fwd_72h 会是 NaN，这是正确的
- 标签可以使用未来价格（这是评估用的标签，不是因子）
- 不需要对标签做任何标准化

### Step 3: 计算因子值（Factor Values）

**脚本：** `scripts/build_factor_values.py`（待创建）

**做什么：**
1. 读取 `bars_1h.parquet`
2. 对每个 symbol，计算 5 个因子
3. 输出到 `data/features/crypto_top50_usdt_perp_1h/<factor>/factor_values.parquet`

**因子公式：**

```python
# mom_20h
df['mom_20h'] = df['close'] / df['close'].shift(20) - 1

# reversal_5h
df['reversal_5h'] = -(df['close'] / df['close'].shift(5) - 1)

# volatility_20h
returns_1h = df['close'].pct_change()
df['volatility_20h'] = returns_1h.rolling(20).std()

# rsi_14h (Wilder smoothing)
delta = df['close'].diff()
gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)
avg_gain = gain.ewm(com=13, min_periods=14).mean()
avg_loss = loss.ewm(com=13, min_periods=14).mean()
df['rsi_14h'] = 100 - 100 / (1 + avg_gain / avg_loss)

# bb_zscore_20h
sma = df['close'].rolling(20).mean()
std = df['close'].rolling(20).std()  # ddof=1
df['bb_zscore_20h'] = (df['close'] - sma) / std
```

**每个因子的 parquet schema（long format）：**
```text
timestamp (UTC)  |  symbol  |  factor_name  |  factor_value  |  known_at  |  source_timeframe  |  computed_at
```

**注意：**
- `known_at = timestamp`（close[t] 后可知）
- `computed_at = 运行时间`
- Warmup 期间（前 20 行左右）的因子值为 NaN，这是正确的

### Step 4: 生成评价指标（Metrics）

**脚本：** `scripts/evaluate_factors.py`（待创建）

**做什么：**
1. 读取因子值和标签
2. 对每个 timestamp，做截面 IC / Rank IC
3. 分 5 组（quintile），计算组间 spread
4. 计算 turnover
5. 输出 metrics.json 和 result_summary.md

**评价流程：**

```python
for each timestamp t:
    # 去掉该期有 NaN 的 symbol
    valid = merge(factor_values[t], labels[t]).dropna()
    
    if len(valid) < 10:  # 覆盖率太低跳过
        continue
    
    # Pearson IC
    ic = corr(valid['factor_value'], valid['ret_fwd_XXh'])
    
    # Spearman Rank IC
    rank_ic = spearmanr(valid['factor_value'], valid['ret_fwd_XXh'])
    
    # Quintile 分组
    valid['quintile'] = pd.qcut(valid['factor_value'], 5, labels=[1,2,3,4,5])
    q5_ret = valid[valid['quintile']==5]['ret_fwd_XXh'].mean()
    q1_ret = valid[valid['quintile']==1]['ret_fwd_XXh'].mean()
    spread = q5_ret - q1_ret

# 聚合
IC_mean = mean(all_ics)
IC_std = std(all_ics)
ICIR = IC_mean / IC_std
# ... 同理 RankIC
```

**metrics.json schema：**
```json
{
  "factor_name": "mom_20h",
  "universe": "crypto_top50_usdt_perp_1h",
  "evaluation_period": "2024-06-01 ~ 2026-06-12",
  "label": "ret_fwd_1h",
  "coverage": 0.95,
  "IC_mean": 0.002,
  "IC_std": 0.05,
  "ICIR": 0.04,
  "RankIC_mean": 0.003,
  "RankIC_std": 0.05,
  "RankICIR": 0.06,
  "quantile_spread_mean": 0.001,
  "quantile_spread_tstat": 1.2,
  "turnover": 0.3,
  "missing_rate": 0.05,
  "n_timestamps": 17000,
  "n_symbols_avg": 48
}
```

**输出路径：**
```text
reports/artifacts/factor_eval/crypto_top50_usdt_perp_1h/<factor_name>/metrics.json
reports/artifacts/factor_eval/crypto_top50_usdt_perp_1h/<factor_name>/result_summary.md
```

### Step 5: 生成结果摘要（Result Summary）

**脚本：** 可合并到 Step 4

**输出：** 每个因子一个 `result_summary.md`，包含：
- 因子定义
- 评价期间
- IC / Rank IC / ICIR（对 4 个标签）
- Quintile 收益表
- 时间序列图（可选）
- 一句话结论

---

## 执行顺序

```text
Step 1 (下载数据) → Step 2 (标签) → Step 3 (因子值) → Step 4 (评价) → Step 5 (摘要)
   ~15 min            ~1 min          ~2 min          ~5 min        ~1 min
```

**总预估时间：** ~25 分钟（主要是数据下载）

## 约束

- 不做策略回测
- 不做策略 PnL
- 不判断因子"赚钱"还是"亏钱"
- 评价标准是 IC / Rank IC / ICIR / 分组收益 / turnover / coverage
- 所有输出路径与 `docs/FACTOR_LIBRARY_DESIGN.md` 对齐
- 下载数据必须生成并更新 manifest

## 依赖

```
pandas>=2.0
numpy>=1.24
pyarrow>=12.0
requests>=2.28
scipy>=1.10   # for spearmanr
```
