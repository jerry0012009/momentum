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

| metric | static | dynamic |
|--------|--------|---------|
| ret_fwd_1h rows | 6 | 6 |
| all-label rows | 24 | 24 |
| direction_source | candidate_csv | candidate_csv |
| fallback_positive | 0 | 0 |

### Static ret_fwd_1h Results

| factor_id | RankIC_mean | RankICIR | direction_adjusted_spread | coverage |
|-----------|------------|----------|---------------------------|----------|
| taker_buy_ratio_20h | -0.003 | -0.13 | -0.012 | 73.3% |
| taker_buy_zscore_20h | -0.008 | -0.36 | -0.032 | 73.3% |
| taker_buy_delta_5h | 0.012 | 0.35 | 0.048 | 73.6% |
| funding_rate_level_20h | 0.011 | 0.33 | 0.044 | 71.7% |
| funding_rate_zscore_80h | -0.005 | -0.18 | -0.018 | 64.2% |
| funding_rate_change_24h | -0.004 | -0.12 | -0.014 | 71.7% |

### Dynamic ret_fwd_1h Results

| factor_id | RankIC_mean | RankICIR | direction_adjusted_spread | coverage |
|-----------|------------|----------|---------------------------|----------|
| taker_buy_ratio_20h | -0.006 | -0.27 | -0.025 | 89.1% |
| taker_buy_zscore_20h | -0.010 | -0.46 | -0.041 | 89.1% |
| taker_buy_delta_5h | 0.008 | 0.26 | 0.030 | 89.2% |
| funding_rate_level_20h | 0.016 | 0.59 | 0.064 | 85.7% |
| funding_rate_zscore_80h | -0.006 | -0.26 | -0.025 | 73.1% |
| funding_rate_change_24h | -0.003 | -0.11 | -0.012 | 85.7% |

---

## D. Initial Observations

- RankIC signs:
  - taker_buy_ratio_20h: negative (weak, |RankIC| < 0.01)
  - taker_buy_zscore_20h: negative (weak-moderate, |RankIC| ~ 0.01)
  - taker_buy_delta_5h: positive (weak-moderate, |RankIC| ~ 0.01)
  - funding_rate_level_20h: positive (moderate, RankIC ~ 0.01-0.02, consistent static/dynamic)
  - funding_rate_zscore_80h: negative (weak, |RankIC| < 0.01)
  - funding_rate_change_24h: negative (weak, |RankIC| < 0.01)
- Coverage: taker ~73%/89%, funding ~64-72%/73-86% (lower for zscore_80h due to warmup)
- Turnover: all factors ~98-100% (high, typical for hourly factors)
- Static/dynamic consistency: funding_rate_level_20h most consistent (same sign, similar magnitude)
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
