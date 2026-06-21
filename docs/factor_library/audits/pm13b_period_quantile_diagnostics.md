# PM-13B Period-Level Quantile Diagnostics

**Date:** 2026-06-21
**Follows:** PM-13 (factor diagnostics metrics builder)

---

## Summary Verdict

**`PERIOD_LS_DIAGNOSTICS_PASS`**

Period-level monthly long-short returns, cumulative curves, Sharpe ratios, and drawdowns are now available for all 71 factors across all 4 horizons (25 months).

---

## 1. Code Changes

### `scripts/evaluate_factors.py`

- Added `period_quantile_long_short` accumulator list.
- After computing per-timestamp `bucket_ts`, added monthly period grouping:
  - Per-bucket: mean/median forward return, n_timestamps per month.
  - Per-period LS: top_bucket - bottom_bucket, mean LS, long/short leg returns, positive flag.
- Added CSV outputs:
  - `factor_level_period_quantile_return_summary.csv` (35,380 rows)
  - `factor_level_period_long_short_summary.csv` (7,076 rows)
- Existing aggregate outputs unchanged (backward-compatible).

### `scripts/build_factor_diagnostics_metrics.py`

- Replaced `build_monthly_ls_series()` stub with real implementation that reads `factor_level_period_long_short_summary.csv`.
- Monthly LS, cumulative curve, Sharpe, drawdown now computed from real data.

---

## 2. New Evaluator Outputs

| File | Rows | Columns |
|------|------|---------|
| factor_level_period_quantile_return_summary.csv | 35,380 | factor_name, category, expected_direction, horizon, period, bucket, bucket_label, mean_forward_return, median_forward_return, n_timestamps, n_obs, status |
| factor_level_period_long_short_summary.csv | 7,076 | factor_name, category, expected_direction, horizon, period, bucket, bucket_label, mean_forward_return, median_forward_return, n_timestamps, n_obs, status, long_short_return, long_leg_return, short_leg_return, positive_ls |

---

## 3. Diagnostics Outputs

| File | Rows | Status |
|------|------|--------|
| factor_diagnostics_summary.csv | 71 | ✅ Sharpe + drawdown populated |
| factor_monthly_long_short_series.csv | 7,076 | ✅ 71 factors × 25 months |
| factor_cumulative_long_short_curve.csv | 7,076 | ✅ cumulative + drawdown |
| factor_monthly_ic_series.csv | 7,076 | ✅ (unchanged from PM-13) |

---

## 4. Metrics Now Available

- ✅ Monthly long-short return series
- ✅ Cumulative long-short curve
- ✅ Sharpe ratio (annualized)
- ✅ Annualized return
- ✅ Annualized volatility
- ✅ Max drawdown
- ✅ Positive LS month rate

---

## 5. Factor Count

- Registered: 71
- Computed: 71
- Horizons: 4 (1h, 4h, 24h, 72h)
- Months: 25 (2024-06 to 2026-06)

---

## 6. Known Limitations

1. Monthly aggregation: LS returns are mean of per-timestamp LS within each month, not end-of-period portfolio returns.
2. Sharpe assumes i.i.d. monthly returns (no autocorrelation adjustment).
3. No transaction cost deduction.
4. No slippage modeling.
5. Direction semantics from factor registry — not independently validated.

---

## 7. Non-Change Statement

- No factor formulas modified.
- No signal panel modified.
- No public HTML pages built or modified.
- No new factors added.
- No production/live/tradeability claims.

---

## 8. Recommended Next PM

**PM-14: Bilingual Factor Cards and Diagnostics Display Pages**

Build public-facing HTML pages with bilingual (EN/ZH) factor names, formulas, intuition, and diagnostic charts.
