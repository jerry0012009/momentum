# Phase 7M-C — Crypto-native Static/Dynamic Evaluation Closeout

> Date: 2026-06-14
>
> Status: COMPLETE

---

## A. Scope

- Phase 7M-C: static/dynamic evaluation
- 6 crypto-native factors only
- No classification, no redundancy, no backtest

---

## B. Label Handling

- Labels copied from base datasets (NOT rebuilt):
  - `data/features/crypto_top50_usdt_perp_1h/labels.parquet` → `.../crypto_native_v1/labels.parquet`
  - `data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/labels.parquet` → `.../crypto_native_v1/labels.parquet`
- Label definitions unchanged (ret_fwd_1h, ret_fwd_4h, ret_fwd_24h, ret_fwd_72h)

---

## C. Evaluation Summary

**CSV files are canonical; this markdown table is a human-readable summary generated from CSV.**

| metric | static | dynamic |
|--------|--------|---------|
| ret_fwd_1h rows | 6 | 6 |
| all-label rows | 24 | 24 |
| direction_source | candidate_csv | candidate_csv |
| fallback_positive | 0 | 0 |

### Static ret_fwd_1h Results

Source: `phase7m_c_static_eval_summary_ret_fwd_1h.csv`

| factor_id | RankIC_mean | RankICIR | direction_adjusted_spread | coverage | turnover |
|-----------|------------|----------|---------------------------|----------|----------|
| taker_buy_ratio_20h | -0.0124 | -0.0810 | -0.000112 | 0.7549 | 0.1469 |
| taker_buy_zscore_20h | -0.0084 | -0.0525 | -0.000037 | 0.7549 | 0.7713 |
| taker_buy_delta_5h | -0.0061 | -0.0399 | 0.000061 | 0.7581 | 0.7596 |
| funding_rate_level_20h | -0.0050 | -0.0284 | -0.000292 | 0.7392 | 0.0405 |
| funding_rate_zscore_80h | 0.0001 | 0.0008 | 0.000033 | 0.6666 | 0.1156 |
| funding_rate_change_24h | -0.0003 | -0.0017 | 0.000071 | 0.7383 | 0.1254 |

### Dynamic ret_fwd_1h Results

Source: `phase7m_c_dynamic_eval_summary_ret_fwd_1h.csv`

| factor_id | RankIC_mean | RankICIR | direction_adjusted_spread | coverage | turnover |
|-----------|------------|----------|---------------------------|----------|----------|
| taker_buy_ratio_20h | -0.0044 | -0.0385 | 0.000046 | 0.9357 | 0.1517 |
| taker_buy_zscore_20h | -0.0104 | -0.0915 | -0.000051 | 0.9357 | 0.7797 |
| taker_buy_delta_5h | -0.0079 | -0.0719 | -0.000048 | 0.9375 | 0.7699 |
| funding_rate_level_20h | 0.0109 | 0.0874 | 0.000025 | 0.8774 | 0.0365 |
| funding_rate_zscore_80h | 0.0033 | 0.0264 | 0.000006 | 0.7737 | 0.1141 |
| funding_rate_change_24h | 0.0021 | 0.0186 | 0.000015 | 0.8772 | 0.1204 |

---

## D. Initial Observations

- RankIC signs:
  - taker_buy_ratio_20h: negative (weak, RankIC ~ -0.004 to -0.012)
  - taker_buy_zscore_20h: negative (weak-moderate, RankIC ~ -0.008 to -0.010)
  - taker_buy_delta_5h: negative (weak, RankIC ~ -0.006 to -0.008)
  - funding_rate_level_20h: static negative / dynamic positive (sign flip)
  - funding_rate_zscore_80h: near zero static / weak positive dynamic
  - funding_rate_change_24h: near zero static / weak positive dynamic
- Coverage: taker ~75%/94%, funding ~67-74%/77-88% (lower for zscore_80h due to warmup)
- Turnover: taker_zscore/delta ~77%, others ~4-15%
- Static/dynamic consistency: taker factors show consistent negative sign; funding factors show sign inconsistency between static and dynamic
- All direction_source = candidate_csv, zero fallback_positive

---

## E. Phase 7M-D Readiness

**Phase 7M-D crypto-native static-vs-dynamic comparison and diagnostic classification is allowed pending PM review.**

---

## F. Negative Declarations

No factor_values were built.
No labels were rebuilt.
No diagnostic classification was run.
No redundancy analysis was run.
No strategy backtest was run.
No portfolio simulation was run.
No Qlib / VectorBT / Backtrader integration was run.
No Alphalens tear sheet was run.
No factor status was upgraded to CANDIDATE_REVIEW.
No alpha claim was made.
No factor was removed or selected for trading.
