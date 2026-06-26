# Factor Intake Report: public_alpha158_batch01_20260626

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-26T19:21:10.806600+00:00
**Factors evaluated:** 6
**Factor IDs:** q158_klen_open, q158_kup_open, q158_klow_open, q158_ksft_open, q158_ksft_range, q158_rsv_20h

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| q158_klen_open | alpha158_kbar | conditional | 1 | False |
| q158_kup_open | alpha158_kbar | negative | 1 | False |
| q158_klow_open | alpha158_kbar | positive | 1 | False |
| q158_ksft_open | alpha158_kbar | positive | 1 | False |
| q158_ksft_range | alpha158_kbar | positive | 1 | False |
| q158_rsv_20h | alpha158_rolling | conditional | 20 | False |

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
| q158_klen_open | -0.090915 | 72h | -0.4677 | +0.005248 | 11.77 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_kup_open | +0.056496 | 72h | +0.3831 | -0.004317 | -11.26 | DIVERGENT | DIRECTION_REVIEW_REQUIRED |
| q158_klow_open | -0.054924 | 72h | -0.3729 | +0.002896 | 7.73 | DIVERGENT | DIRECTION_REVIEW_REQUIRED |
| q158_ksft_open | -0.038870 | 1h | -0.2464 | +0.000729 | 2.02 | DIVERGENT | DIRECTION_REVIEW_REQUIRED |
| q158_ksft_range | -0.033409 | 1h | -0.2728 | +0.000256 | 0.84 | DIVERGENT | DIRECTION_REVIEW_REQUIRED |
| q158_rsv_20h | -0.021722 | 1h | -0.1617 | +0.003510 | 10.29 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### q158_klen_open

- **Family:** alpha158_kbar
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** -0.090915
- **Best LS t-stat:** 11.77
- **Monthly stability:** UNSTABLE (1/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** NEAR_DUPLICATE
- **Nearest existing:** q158_high_low_range (|ρ|=1.000, NEAR_DUPLICATE); range_1h (|ρ|=1.000, NEAR_DUPLICATE); vol_5h (|ρ|=0.696, LOW_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: NEAR_DUPLICATE. Consider dropping one factor.

### q158_kup_open

- **Family:** alpha158_kbar
- **Expected direction:** negative
- **Best horizon:** 72h
- **Best adj IC:** +0.056496
- **Best LS t-stat:** -11.26
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** MODERATE_REDUNDANCY
- **Nearest existing:** candle_wick_upper (|ρ|=0.788, MODERATE_REDUNDANCY); q158_klen_open (|ρ|=0.455, LOW_REDUNDANCY); q158_high_low_range (|ρ|=0.454, LOW_REDUNDANCY)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

### q158_klow_open

- **Family:** alpha158_kbar
- **Expected direction:** positive
- **Best horizon:** 72h
- **Best adj IC:** -0.054924
- **Best LS t-stat:** 7.73
- **Monthly stability:** UNSTABLE (2/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** NEAR_DUPLICATE
- **Nearest existing:** klow_close (|ρ|=1.000, NEAR_DUPLICATE); candle_wick_lower (|ρ|=0.767, MODERATE_REDUNDANCY); vol_of_vol_20h (|ρ|=0.471, LOW_REDUNDANCY)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

### q158_ksft_open

- **Family:** alpha158_kbar
- **Expected direction:** positive
- **Best horizon:** 1h
- **Best adj IC:** -0.038870
- **Best LS t-stat:** 2.02
- **Monthly stability:** UNSTABLE (0/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** q158_ksft_range (|ρ|=0.938, HIGH_REDUNDANCY); intraday_ret (|ρ|=0.816, MODERATE_REDUNDANCY); candle_body (|ρ|=0.803, MODERATE_REDUNDANCY)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

### q158_ksft_range

- **Family:** alpha158_kbar
- **Expected direction:** positive
- **Best horizon:** 1h
- **Best adj IC:** -0.033409
- **Best LS t-stat:** 0.84
- **Monthly stability:** UNSTABLE (0/25 months positive)
- **Quantile monotonicity:** MONOTONIC_DECREASING
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** q158_ksft_open (|ρ|=0.938, HIGH_REDUNDANCY); candle_body (|ρ|=0.823, MODERATE_REDUNDANCY); intraday_ret (|ρ|=0.770, MODERATE_REDUNDANCY)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

### q158_rsv_20h

- **Family:** alpha158_rolling
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** -0.021722
- **Best LS t-stat:** 10.29
- **Monthly stability:** UNSTABLE (1/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** NEAR_DUPLICATE
- **Nearest existing:** breakout_dist_20h (|ρ|=0.984, NEAR_DUPLICATE); bb_zscore_20h (|ρ|=0.929, HIGH_REDUNDANCY); vwap_dev_20h (|ρ|=0.918, HIGH_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: NEAR_DUPLICATE. Consider dropping one factor.

## Redundancy Warnings

- **q158_klow_open ↔ klow_close**: NEAR_DUPLICATE (|ρ| = 1.000)
- **q158_klen_open ↔ q158_high_low_range**: NEAR_DUPLICATE (|ρ| = 1.000)
- **q158_klen_open ↔ range_1h**: NEAR_DUPLICATE (|ρ| = 1.000)
- **q158_rsv_20h ↔ breakout_dist_20h**: NEAR_DUPLICATE (|ρ| = 0.984)
- **q158_ksft_open ↔ q158_ksft_range**: HIGH_REDUNDANCY (|ρ| = 0.938)
- **q158_rsv_20h ↔ bb_zscore_20h**: HIGH_REDUNDANCY (|ρ| = 0.929)
- **q158_rsv_20h ↔ vwap_dev_20h**: HIGH_REDUNDANCY (|ρ| = 0.918)
- **q158_rsv_20h ↔ rsi_14h**: HIGH_REDUNDANCY (|ρ| = 0.870)

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
