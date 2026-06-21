# Factor Intake Report: pm11a_taker_field_integration_20260621

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-21T05:39:18.939400+00:00
**Factors evaluated:** 3
**Factor IDs:** taker_buy_ratio_20h, taker_buy_zscore_20h, taker_buy_delta_5h

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| taker_buy_ratio_20h | taker_imbalance | positive | 20 | False |
| taker_buy_zscore_20h | taker_imbalance | positive | 20 | False |
| taker_buy_delta_5h | taker_imbalance | positive | 6 | False |

## Quality Checks

**Result: 8 PASS, 0 FAIL**

- ✅ all factor IDs exist in registry: PASS
- ✅ registry integrity check passed: PASS
- ✅ evaluation manifest generated: PASS
- ✅ metric panel generated: PASS
- ✅ candidate review generated: PASS
- ✅ no signal panel modification: PASS
- ✅ no production claim: PASS
- ✅ all critical steps succeeded: PASS

## Key Metrics

| factor_id | best_adj_ic | horizon | best_icir | best_ls_spread | ls_t | consistency | review_bucket |
|-----------|-------------|---------|-----------|----------------|------|-------------|---------------|
| taker_buy_ratio_20h | -0.004995 | 1h | -0.0514 | +0.003801 | 14.34 | DIVERGENT | TAIL_OR_MONOTONICITY_REVIEW_REQUIRED |
| taker_buy_zscore_20h | -0.011372 | 1h | -0.1159 | +0.000385 | 1.52 | DIVERGENT | TAIL_OR_MONOTONICITY_REVIEW_REQUIRED |
| taker_buy_delta_5h | -0.008093 | 1h | -0.0868 | +0.000355 | 1.53 | DIVERGENT | TAIL_OR_MONOTONICITY_REVIEW_REQUIRED |

## Conclusion Cards

### taker_buy_ratio_20h

- **Family:** taker_imbalance
- **Expected direction:** positive
- **Best horizon:** 1h
- **Best adj IC:** -0.004995
- **Best LS t-stat:** 14.34
- **Monthly stability:** UNSTABLE (4/24 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** LOW_REDUNDANCY
- **Nearest existing:** mom_20h (|ρ|=0.285, LOW_REDUNDANCY); rsi_14h (|ρ|=0.243, LOW_REDUNDANCY); price_pos_72h (|ρ|=0.241, LOW_REDUNDANCY)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

### taker_buy_zscore_20h

- **Family:** taker_imbalance
- **Expected direction:** positive
- **Best horizon:** 1h
- **Best adj IC:** -0.011372
- **Best LS t-stat:** 1.52
- **Monthly stability:** UNSTABLE (1/24 months positive)
- **Quantile monotonicity:** MONOTONIC_DECREASING
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** LOW_REDUNDANCY
- **Nearest existing:** candle_body (|ρ|=0.535, LOW_REDUNDANCY); intraday_ret (|ρ|=0.524, LOW_REDUNDANCY); wq101_alpha101 (|ρ|=0.503, LOW_REDUNDANCY)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

### taker_buy_delta_5h

- **Family:** taker_imbalance
- **Expected direction:** positive
- **Best horizon:** 1h
- **Best adj IC:** -0.008093
- **Best LS t-stat:** 1.53
- **Monthly stability:** UNSTABLE (3/24 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (2 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** LOW_REDUNDANCY
- **Nearest existing:** wq101_alpha53 (|ρ|=0.420, LOW_REDUNDANCY); rev_1h (|ρ|=0.363, LOW_REDUNDANCY); candle_body (|ρ|=0.332, LOW_REDUNDANCY)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
