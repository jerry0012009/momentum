# Alphalens Compatibility Design

> Phase 5 — Alphalens-compatible Export Layer
>
> Status: IMPLEMENTED

---

## 1. Goal

Enable cross-checking our factor evaluation results against Alphalens-style tear sheets, **without** replacing our evaluation kernel.

Our `evaluate_factors.py` remains the source of truth. Alphalens-compatible export is a **presentation / cross-validation layer** only.

## 2. Why Not Migrate to Alphalens

| Reason | Detail |
|--------|--------|
| Alphalens is unmaintained | Last release 2020; pinned to old pandas |
| Data format overhead | Alphalens expects MultiIndex (asset, date); we use long format |
| Our protocol is crypto-specific | `known_at = bar_close_time`, per-symbol groupby, no cross-symbol rolling |
| Our evaluation kernel is proven | 194 tests, 11 factors evaluated, audit trail |
| Alphalens adds presentation, not rigor | Its IC/quantile analysis is good for visualization, not better than ours |

**What Alphalens gives us:** standardized tear sheets, quantile analysis plots, factor turnover visualizations that are easy to share and compare.

## 3. Data Schema Mapping

### Our factor_values schema

| Column | Type | Description |
|--------|------|-------------|
| timestamp | datetime | bar_close_time (UTC) |
| symbol | str | e.g. "BTCUSDT" |
| factor_name | str | e.g. "mom_20h" |
| factor_value | float | computed factor value |
| known_at | datetime | = timestamp (bar_close_time) |
| source_timeframe | str | "1h" |
| computed_at | datetime | computation timestamp |

### Our labels schema

| Column | Type | Description |
|--------|------|-------------|
| timestamp | datetime | bar_close_time |
| symbol | str | trading pair |
| ret_fwd_1h | float | 1h forward return |
| ret_fwd_4h | float | 4h forward return |
| ret_fwd_24h | float | 24h forward return |
| ret_fwd_72h | float | 72h forward return |

### Alphalens expected format

Alphalens `get_clean_factor_and_forward_returns()` expects:
- **factor**: Series with MultiIndex (date, asset)
- **prices**: DataFrame with DatetimeIndex, columns = assets, values = close
- **forward_returns**: computed by Alphalens from prices + factor

Our exporter produces **parquet files** that can be loaded into this format.

## 4. Exported Files

```
research/factor_runs/crypto_top50_factor_library/alphalens_exports/
└── <dataset-id>/
    └── <factor-id>/
        ├── factor_series.parquet        # timestamp, symbol, factor_value
        ├── prices_wide.parquet           # index=timestamp, columns=symbol, values=close
        ├── forward_returns_long.parquet  # timestamp, symbol, ret_fwd_1h/4h/24h/72h
        ├── alphalens_factor_data.parquet # combined: timestamp, symbol, factor, fwd returns, quantile
        └── export_manifest.json          # metadata
```

## 5. Limitations

- **No Alphalens package dependency required.** Exports are plain parquet.
- **Quantile labels** are computed per-timestamp cross-sectionally (our existing quantile logic).
- **No shift(-k) in exporter.** Forward returns come from pre-computed labels, not recomputed.
- **Our IC/RankIC/spread metrics are authoritative.** Alphalens tear sheets are supplementary.

## 6. Future Use

When Alphalens-compatible data exists:
1. Load `alphalens_factor_data.parquet` into a DataFrame
2. Use Alphalens API (if installed) to generate tear sheets
3. Compare our IC / quantile spread / turnover with Alphalens output
4. **No factor status upgrade can be based solely on Alphalens output.**

## 7. Anti-patterns

- ❌ Replace `evaluate_factors.py` with Alphalens
- ❌ Auto-upgrade factor status from Alphalens output
- ❌ Treat Alphalens IC as more authoritative than our evaluation
- ❌ Add Alphalens as a hard dependency
- ❌ Migrate data format to Alphalens MultiIndex
