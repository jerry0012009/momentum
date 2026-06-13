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

## Phase 2E Batch 1 Diagnostic Probes

### 6. wq101_alpha101

| 字段 | 值 |
|------|-----|
| **factor_name** | `wq101_alpha101` |
| **category** | intraday_position |
| **formula** | `(close - open) / (high - low + 0.001)` |
| **parameters** | lookback = 1 bar |
| **known_at** | `close[t]` — bar 收盘后可知 |
| **universe** | `crypto_top50_usdt_perp_1h` |
| **frequency** | 1h |
| **status** | DIAGNOSTIC_PROBE |
| **expected_direction** | positive |
| **artifact_path** | `data/features/crypto_top50_usdt_perp_1h/wq101_alpha101/factor_values.parquet` |
| **eval_path** | `reports/artifacts/factor_eval/crypto_top50_usdt_perp_1h/wq101_alpha101/` |
| **notes** | WQ101 Alpha#101. 日内位置因子：收盘价在日内范围的相对位置。Phase 2E Batch 1 diagnostic probe; not alpha evidence. |

### 7. wq101_alpha12

| 字段 | 值 |
|------|-----|
| **factor_name** | `wq101_alpha12` |
| **category** | volume_price_momentum |
| **formula** | `sign(volume.diff(1)) * (-close.diff(1))` |
| **parameters** | lookback = 2 bars |
| **known_at** | `close[t]` — bar 收盘后可知 |
| **universe** | `crypto_top50_usdt_perp_1h` |
| **frequency** | 1h |
| **status** | DIAGNOSTIC_PROBE |
| **expected_direction** | conditional |
| **artifact_path** | `data/features/crypto_top50_usdt_perp_1h/wq101_alpha12/factor_values.parquet` |
| **eval_path** | `reports/artifacts/factor_eval/crypto_top50_usdt_perp_1h/wq101_alpha12/` |
| **notes** | WQ101 Alpha#12. 量价背离因子。方向不确定（conditional），direction_adjusted_spread 不使用。Phase 2E Batch 1 diagnostic probe; not alpha evidence. |

### 8. wq101_alpha53

| 字段 | 值 |
|------|-----|
| **factor_name** | `wq101_alpha53` |
| **category** | intraday_position |
| **formula** | `-1 * delta(((close-low)-(high-close))/(close-low+0.001), 9)` |
| **parameters** | lookback = 10 bars |
| **known_at** | `close[t]` — bar 收盘后可知 |
| **universe** | `crypto_top50_usdt_perp_1h` |
| **frequency** | 1h |
| **status** | DIAGNOSTIC_PROBE |
| **expected_direction** | conditional |
| **artifact_path** | `data/features/crypto_top50_usdt_perp_1h/wq101_alpha53/factor_values.parquet` |
| **eval_path** | `reports/artifacts/factor_eval/crypto_top50_usdt_perp_1h/wq101_alpha53/` |
| **notes** | WQ101 Alpha#53. 日内位置变化率因子。公式含 -1*delta，方向不确定（conditional）。Phase 2E Batch 1 diagnostic probe; not alpha evidence. |

### 9. q158_high_low_range

| 字段 | 值 |
|------|-----|
| **factor_name** | `q158_high_low_range` |
| **category** | volatility |
| **formula** | `(high - low) / close` |
| **parameters** | lookback = 1 bar |
| **known_at** | `close[t]` — bar 收盘后可知 |
| **universe** | `crypto_top50_usdt_perp_1h` |
| **frequency** | 1h |
| **status** | DIAGNOSTIC_PROBE |
| **expected_direction** | conditional |
| **artifact_path** | `data/features/crypto_top50_usdt_perp_1h/q158_high_low_range/factor_values.parquet` |
| **eval_path** | `reports/artifacts/factor_eval/crypto_top50_usdt_perp_1h/q158_high_low_range/` |
| **notes** | Alpha158 HL Range. 日内振幅因子，波动率代理。方向中性（conditional），direction_adjusted_spread 不使用。Phase 2E Batch 1 diagnostic probe; not alpha evidence. |

### 10. tech_macd

| 字段 | 值 |
|------|-----|
| **factor_name** | `tech_macd` |
| **category** | technical |
| **formula** | `EMA(close, 12) - EMA(close, 26) - signal` where `signal = EMA(MACD_line, 9)` |
| **parameters** | EMA span 12/26/9 |
| **known_at** | `close[t]` — bar 收盘后可知 |
| **universe** | `crypto_top50_usdt_perp_1h` |
| **frequency** | 1h |
| **status** | DIAGNOSTIC_PROBE |
| **expected_direction** | positive |
| **artifact_path** | `data/features/crypto_top50_usdt_perp_1h/tech_macd/factor_values.parquet` |
| **eval_path** | `reports/artifacts/factor_eval/crypto_top50_usdt_perp_1h/tech_macd/` |
| **notes** | MACD Histogram. 经典趋势跟踪指标。Phase 2E Batch 1 diagnostic probe; not alpha evidence. |

### 11. tech_atr

| 字段 | 值 |
|------|-----|
| **factor_name** | `tech_atr` |
| **category** | volatility |
| **formula** | `SMA(TR, 14)` where `TR = max(H-L, |H-prev_C|, |L-prev_C|)` |
| **parameters** | lookback = 15 bars (14-bar ATR + 1 for prev_close) |
| **known_at** | `close[t]` — bar 收盘后可知 |
| **universe** | `crypto_top50_usdt_perp_1h` |
| **frequency** | 1h |
| **status** | DIAGNOSTIC_PROBE |
| **expected_direction** | conditional |
| **artifact_path** | `data/features/crypto_top50_usdt_perp_1h/tech_atr/factor_values.parquet` |
| **eval_path** | `reports/artifacts/factor_eval/crypto_top50_usdt_perp_1h/tech_atr/` |
| **notes** | ATR 14. 真实波幅均值，波动率代理。方向中性（conditional），direction_adjusted_spread 不使用。Phase 2E Batch 1 diagnostic probe; not alpha evidence. |

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

## Status Enum (Phase 2C canonical)

| Status | 含义 | 谁能设 |
|--------|------|--------|
| `DIAGNOSTIC_PROBE` | 流水线测试通过；非 alpha 证据 | auto (首次 eval run 后) |
| `CANDIDATE_REVIEW` | 通过基础质量门；需更深入统计审查 | human only |
| `CANDIDATE_FACTOR` | 通过 Phase 2C 审查；可接入模型 | human only |
| `PARK` | 证据不足但未证伪；稍后复查 | human only |
| `DROP` | 评价失败或有已知缺陷 | human or auto (with audit) |

**禁止使用的状态名:** `ALPHA`, `STRONG_ALPHA`, `DEPLOYABLE_ALPHA`, `LIVE`, `SHADOW`.
这些在因子库中不存在。Alpha 是策略的属性，不是单个因子的属性。

实现状态 (`implementation_status`) 独立于评价状态：
`NOT_IMPLEMENTED` → `IMPLEMENTED` → (first eval run) → `DIAGNOSTIC_PROBE`

详见 `docs/FACTOR_LIBRARY_SKELETON.md` §1-§2。

---

## 后续因子添加规则

新增因子必须满足：

1. 有明确的公式定义
2. 有 `known_at` 说明
3. 初始状态为 `SCOPED`
4. 不直接从策略回测结果推断为有效
5. 经过 IC / Rank IC / ICIR / 分组收益 / turnover / coverage 评估后才能升级状态
