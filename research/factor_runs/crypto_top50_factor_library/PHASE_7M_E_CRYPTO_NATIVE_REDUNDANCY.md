# Phase 7M-E — Crypto-native Redundancy Diagnostics

> Date: 2026-06-14
>
> Status: COMPLETE

---

## A. Scope

- Phase 7M-E: redundancy diagnostics only
- 6 crypto-native factors
- No factor removal, no alpha promotion, no CANDIDATE_REVIEW, no backtest

---

## B. Results

### Pairwise Correlation Summary

**No redundancy pairs found (abs(correlation) >= 0.80).**

Top same-family correlations (dynamic):

| factor_1 | factor_2 | family | spearman_corr |
|----------|----------|--------|--------------|
| taker_buy_delta_5h | taker_buy_zscore_20h | taker_imbalance | 0.694 |
| funding_rate_change_24h | funding_rate_zscore_80h | funding_rate | 0.668 |

Top cross-family correlations (dynamic):

| factor_1 | factor_2 | spearman_corr |
|----------|----------|--------------|
| funding_rate_zscore_80h | taker_buy_ratio_20h | 0.091 |
| funding_rate_level_20h | taker_buy_ratio_20h | -0.071 |

### Family Summary

| family | n_factors | max_corr | mean_corr | redundant | medium |
|--------|-----------|----------|-----------|-----------|--------|
| taker_imbalance | 3 | 0.694 | 0.237 | 0 | 1 |
| funding_rate | 3 | 0.668 | 0.270 | 0 | 1 |
| CROSS_FAMILY | 6 | 0.091 | 0.027 | 0 | 0 |

---

## C. Observations

- **taker_imbalance**: taker_buy_delta_5h and taker_buy_zscore_20h have moderate correlation (0.694), below redundancy threshold. taker_buy_ratio_20h is nearly orthogonal to the other two (~0.009).
- **funding_rate**: funding_rate_change_24h and funding_rate_zscore_80h have moderate correlation (0.668), below redundancy threshold. funding_rate_level_20h is nearly orthogonal (~0.09).
- **Cross-family**: taker and funding families are essentially orthogonal (max 0.091, mean 0.027).
- All 6 factors are non-redundant at the 0.80 threshold. One medium pair per family at the 0.60 threshold.
- Crypto-native factors are additive across families — combining taker and funding signals would add independent dimensions.

---

## D. Phase 7M-E Status

Phase 7M-E is redundancy diagnostics only.
No factor was removed.
No factor was promoted.
No alpha claim was made.
No backtest was run.
Dynamic universe remains diagnostic and not true PIT.
CSV outputs are canonical source for redundancy analysis.
Crypto-native factors are non-redundant within family and additive across families.

---

## E. Negative Declarations

No factor_values were built.
No labels were rebuilt.
No strategy backtest was run.
No portfolio simulation was run.
No factor status was upgraded to CANDIDATE_REVIEW.
No alpha claim was made.
No factor was removed or selected for trading.
