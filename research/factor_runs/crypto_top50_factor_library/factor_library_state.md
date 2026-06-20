# Factor Library State

**Generated:** 2026-06-20T15:16:20.808722+00:00
**Dataset:** crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1

## Counts

| Metric | Count |
|--------|-------|
| Registered factors | 65 |
| Computed factor_values | 59 |
| Missing factor_values | 6 |
| Missing input data | 6 |
| Active signal factors | 10 |
| Signal variants | 0 |

## Lifecycle Distribution

- **CANDIDATE:** 27
- **COMPUTED:** 12
- **DIAGNOSTIC_ONLY:** 10
- **ACTIVE_IN_SIGNAL:** 10
- **MISSING_INPUT_DATA:** 6

## Candidate Review Distribution

- **STRONG_DIAGNOSTIC_CANDIDATE:** 22
- **CONDITIONAL_DIRECTION_REVIEW:** 16
- **ACTIVE_IN_SIGNAL_REVIEW:** 10
- **LONGSHORT_STRONG_RANKIC_WEAK:** 8
- **MISSING_INPUT:** 6
- **METADATA_REVIEW:** 3

## Signal Factor IDs

- downside_vol_20h
- price_pos_24h
- range_1h
- range_4h
- rsi_28h
- rsi_7h
- vol_40h
- vol_5h
- vol_of_vol_20h
- xs_rank_vol

## Missing Input Factors

- taker_buy_ratio_20h
- taker_buy_zscore_20h
- taker_buy_delta_5h
- funding_rate_level_20h
- funding_rate_zscore_80h
- funding_rate_change_24h

## Top Factors by Adjusted IC

| factor_id | best_adj_ic | horizon |
|-----------|-------------|---------|
| vol_40h | +0.103597 | 72h |
| volatility_20h | +0.100062 | 72h |
| range_24h | -0.094086 | 72h |
| range_4h | -0.092339 | 72h |
| q158_high_low_range | -0.090894 | 72h |
| range_1h | -0.090894 | 72h |
| downside_vol_20h | +0.089635 | 72h |
| vol_5h | +0.080509 | 72h |
| vol_of_vol_20h | +0.080223 | 72h |
| xs_rank_vol | -0.068675 | 72h |
| price_volume_corr_20h | -0.040248 | 24h |
| xs_rank_ret_1h | -0.036506 | 1h |
| rev_1h | +0.036506 | 1h |
| rev_3h | +0.034385 | 1h |
| rsi_14h | +0.033554 | 4h |

## Warnings

- 6 factors have missing input data: taker_buy_ratio_20h, taker_buy_zscore_20h, taker_buy_delta_5h, funding_rate_level_20h, funding_rate_zscore_80h, funding_rate_change_24h

---
*Diagnostic only. Not production. Not live trading.*
