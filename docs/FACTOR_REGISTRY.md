# Factor Registry

> 本文件是因子库的定义登记表，不是回测赢家表。
>
> 每个因子条目记录的是：它是什么、怎么算、什么时候已知、在哪个 universe 上评估过、当前状态是什么。
>
> 状态为 SCOPED 不代表已验证有效，仅代表公式和 universe 已定义。

## Registry Status

- All 5 registered factors are **DIAGNOSTIC_PROBE** status
- They serve as test inputs for the factor evaluation pipeline and audit framework
- None have been promoted to CANDIDATE status
- See `docs/FACTOR_EVALUATION_STANDARD.md` for evaluation criteria
- See `research/factor_runs/crypto_top50_factor_library/audit_v0/audit_summary.md` for audit results

## Experimental Catalog Boundary

`factor_catalog_v0_1.csv` contains **only the 5 official V0 diagnostic probes** listed below.

`experimental_catalog_v0_1.csv` contains 19 additional exploratory factors (window variants, volume factors, technical patterns). These are **exploratory diagnostics only** — they are NOT part of the official V0 factor registry. They were run through the evaluation pipeline for screening purposes but have not been individually validated. Do not treat experimental catalog entries as registered factors.

## Universe

| 字段 | 值 |
|------|-----|
| universe_name | `crypto_top50_usdt_perp_1h` |
| market | crypto |
| venue | Binance USDT-margined perpetual futures |
| frequency | 1h |
| selection_rule | static_current_top50_by_24h_quote_volume |
| rebalance_frequency | monthly |
| min_listing_age_days | 90 |
| data_path | `data/cache/crypto_top50_usdt_perp_1h/` |

## Factor Registry

### 1. mom_20h

| 字段 | 值 |
|------|-----|
| **factor_name** | `mom_20h` |
| **category** | momentum |
| **formula** | `close[t] / close[t-20] - 1` |
| **parameters** | lookback = 20 bars (20h) |
| **known_at** | `close[t]` — bar 收盘后可知 |
| **universe** | `crypto_top50_usdt_perp_1h` |
| **frequency** | 1h |
| **status** | DIAGNOSTIC_PROBE |
| **artifact_path** | `data/features/crypto_top50_usdt_perp_1h/mom_20h/factor_values.parquet` |
| **eval_path** | `reports/artifacts/factor_eval/crypto_top50_usdt_perp_1h/mom_20h/` |
| **notes** | 经典短期动量。crypto 中 20h ≈ 接近 1 个交易日。预期方向：正 IC（过去涨的继续涨）。可能在反转行情中失效。 **DIAGNOSTIC_PROBE**: Used for pipeline testing and audit mechanism validation. Not promoted to V1. Not used in strategy backtesting. See audit_v0/ for details. |

### 2. reversal_5h

| 字段 | 值 |
|------|-----|
| **factor_name** | `reversal_5h` |
| **category** | reversal |
| **formula** | `-(close[t] / close[t-5] - 1)` |
| **parameters** | lookback = 5 bars (5h) |
| **known_at** | `close[t]` — bar 收盘后可知 |
| **universe** | `crypto_top50_usdt_perp_1h` |
| **frequency** | 1h |
| **status** | DIAGNOSTIC_PROBE |
| **artifact_path** | `data/features/crypto_top50_usdt_perp_1h/reversal_5h/factor_values.parquet` |
| **eval_path** | `reports/artifacts/factor_eval/crypto_top50_usdt_perp_1h/reversal_5h/` |
| **notes** | 短期反转。取负号使因子值大 = 过去跌得多 = 预期反弹。与 mom_20h 方向相反，可用于正交性检验。 **DIAGNOSTIC_PROBE**: Used for pipeline testing and audit mechanism validation. Not promoted to V1. Not used in strategy backtesting. See audit_v0/ for details. |

### 3. volatility_20h

| 字段 | 值 |
|------|-----|
| **factor_name** | `volatility_20h` |
| **category** | volatility |
| **formula** | `std(returns_1h, window=20)` where `returns_1h = close[t] / close[t-1] - 1` |
| **parameters** | window = 20 bars (20h) |
| **known_at** | `close[t]` — bar 收盘后可知 |
| **universe** | `crypto_top50_usdt_perp_1h` |
| **frequency** | 1h |
| **status** | DIAGNOSTIC_PROBE |
| **artifact_path** | `data/features/crypto_top50_usdt_perp_1h/volatility_20h/factor_values.parquet` |
| **eval_path** | `reports/artifacts/factor_eval/crypto_top50_usdt_perp_1h/volatility_20h/` |
| **notes** | 已实现波动率。可用于波动率择时或作为其他因子的条件过滤器。本身不预判方向，预期 IC 接近 0 或微负（低波跑赢高波效应）。 **DIAGNOSTIC_PROBE**: Used for pipeline testing and audit mechanism validation. Not promoted to V1. Not used in strategy backtesting. See audit_v0/ for details. |

### 4. rsi_14h

| 字段 | 值 |
|------|-----|
| **factor_name** | `rsi_14h` |
| **category** | technical / reversal |
| **formula** | `RSI(close, period=14)` — Wilder 平滑 |
| **parameters** | period = 14 bars (14h) |
| **known_at** | `close[t]` — bar 收盘后可知 |
| **universe** | `crypto_top50_usdt_perp_1h` |
| **frequency** | 1h |
| **status** | DIAGNOSTIC_PROBE |
| **artifact_path** | `data/features/crypto_top50_usdt_perp_1h/rsi_14h/factor_values.parquet` |
| **eval_path** | `reports/artifacts/factor_eval/crypto_top50_usdt_perp_1h/rsi_14h/` |
| **notes** | 经典 RSI。作为连续因子使用（0-100），不做二值化。与 reversal_5h 有相关性但不完全相同（RSI 用 Wilder 平滑，reversal 用简单比值）。 **DIAGNOSTIC_PROBE**: Used for pipeline testing and audit mechanism validation. Not promoted to V1. Not used in strategy backtesting. See audit_v0/ for details. |

### 5. bb_zscore_20h

| 字段 | 值 |
|------|-----|
| **factor_name** | `bb_zscore_20h` |
| **category** | technical / mean reversion |
| **formula** | `(close[t] - SMA(close, 20)) / STD(close, 20)` |
| **parameters** | window = 20 bars (20h), SMA, sample std (ddof=1) |
| **known_at** | `close[t]` — bar 收盘后可知 |
| **universe** | `crypto_top50_usdt_perp_1h` |
| **frequency** | 1h |
| **status** | DIAGNOSTIC_PROBE |
| **artifact_path** | `data/features/crypto_top50_usdt_perp_1h/bb_zscore_20h/factor_values.parquet` |
| **eval_path** | `reports/artifacts/factor_eval/crypto_top50_usdt_perp_1h/bb_zscore_20h/` |
| **notes** | 布林带 z-score。值 > 0 表示价格高于均值，< 0 表示低于均值。预期均值回归效应：IC 为负（高 z-score → 未来跌）。与 rank444 RSI+BB 策略有渊源但此处作为独立因子评估。 **DIAGNOSTIC_PROBE**: Used for pipeline testing and audit mechanism validation. Not promoted to V1. Not used in strategy backtesting. See audit_v0/ for details. |

---

## Evaluation Protocol

### 指标定义

| 指标 | 含义 |
|------|------|
| **coverage** | 因子值非空的 (timestamp, symbol) 占比 |
| **IC_mean** | 截面 Pearson IC 的时间序列均值 |
| **IC_std** | 截面 Pearson IC 的时间序列标准差 |
| **ICIR** | IC_mean / IC_std |
| **RankIC_mean** | 截面 Spearman Rank IC 的时间序列均值 |
| **RankIC_std** | 截面 Spearman Rank IC 的时间序列标准差 |
| **RankICIR** | RankIC_mean / RankIC_std |
| **quantile_spread_mean** | Top quantile - Bottom quantile 的平均收益差 |
| **quantile_spread_tstat** | 价差的 t 统计量 |
| **turnover** | 相邻两期 top/bottom quantile 的换手率 |
| **missing_rate** | 缺失值占比 |

### 分组方法

- 每个 timestamp，按因子值对 symbol 排序
- 分为 5 组（quintile）
- 计算每组的平均未来收益
- 高减低 spread = Q5 - Q1（或 Q1 - Q5，取决于因子方向）

### 标签

| label | 定义 | 用途 |
|-------|------|------|
| `ret_fwd_1h` | `close[t+1] / close[t] - 1` | 超短期预测力 |
| `ret_fwd_4h` | `close[t+4] / close[t] - 1` | 短期预测力 |
| `ret_fwd_24h` | `close[t+24] / close[t] - 1` | 日频预测力 |
| `ret_fwd_72h` | `close[t+72] / close[t] - 1` | 三日预测力 |

### 输出路径

```text
data/features/crypto_top50_usdt_perp_1h/labels.parquet

data/features/crypto_top50_usdt_perp_1h/<factor_name>/factor_values.parquet

reports/artifacts/factor_eval/crypto_top50_usdt_perp_1h/<factor_name>/metrics.json
reports/artifacts/factor_eval/crypto_top50_usdt_perp_1h/<factor_name>/result_summary.md
```

---

## Status Legend

| Status | 含义 |
|--------|------|
| IDEA | 未实现 |
| SCOPED | 公式和 universe 已定义 |
| DIAGNOSTIC_PROBE | 因子用于流水线测试和审计机制验证，未升级为候选因子 |
| PROTOTYPED | 因子值已生成一次 |
| REVIEW_REQUIRED | AI 辅助或未审计 |
| REVIEWED | 公式、时序、数据、评价已检查 |
| KEEP | 有足够证据保留 |
| PARK | 证据不足但未证伪 |
| DROP | 评价失败或无稳定信号 |

---

## 后续因子添加规则

新增因子必须满足：

1. 有明确的公式定义
2. 有 `known_at` 说明
3. 初始状态为 `SCOPED`
4. 不直接从策略回测结果推断为有效
5. 经过 IC / Rank IC / ICIR / 分组收益 / turnover / coverage 评估后才能升级状态
