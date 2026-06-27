# Factor Library State

**Generated:** 2026-06-27T16:50:56.219384+00:00
**Dataset:** crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1

## Counts

| Metric | Count |
|--------|-------|
| Registered factors | 128 |
| Computed factor_values | 128 |
| Missing factor_values | 0 |
| Missing input data | 0 |
| Active signal factors | 10 |
| Signal variants | 3 |

## Lifecycle Distribution

- **CANDIDATE:** 35
- **DIAGNOSTIC_ONLY:** 20
- **ACTIVE_IN_SIGNAL:** 10
- **MISSING_INPUT_DATA:** 6
- **COMPUTED:** 5

## Candidate Review Distribution

- **DIRECTION_REVIEW_REQUIRED:** 27
- **CONDITIONAL_DIRECTION_REVIEW:** 25
- **TAIL_OR_MONOTONICITY_REVIEW_REQUIRED:** 15
- **ACTIVE_IN_SIGNAL_REVIEW:** 10
- **METADATA_REVIEW:** 2
- **STRONG_DIAGNOSTIC_CANDIDATE:** 2
- **LONGSHORT_STRONG_RANKIC_WEAK:** 1
- **RANKIC_STRONG_LONGSHORT_WEAK:** 1

## Signal Factor IDs

*Source: phase9b_signal_component_manifest.csv*

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

## Signal Variants: 3

*Source: signal_composition_review_manifest.json*

## Top Factors by Adjusted IC

| factor_id | best_adj_ic | horizon |
|-----------|-------------|---------|
| vol_40h | +0.103597 | 72h |
| volatility_20h | +0.100062 | 72h |
| range_24h | -0.094086 | 72h |
| range_4h | -0.092339 | 72h |
| q158_klen_open | -0.090915 | 72h |
| q158_high_low_range | -0.090894 | 72h |
| range_1h | -0.090894 | 72h |
| downside_vol_20h | +0.089635 | 72h |
| q158_std_20h | +0.082791 | 72h |
| vol_5h | +0.080509 | 72h |
| vol_of_vol_20h | +0.080223 | 72h |
| wvma_20h | +0.076279 | 72h |
| xs_rank_vol | -0.068675 | 72h |
| a101_volume_xs_z_mean_neg_112h | +0.068354 | 72h |
| q158_min_20h | +0.067445 | 72h |

---
*Diagnostic only. Not production. Not live trading.*
