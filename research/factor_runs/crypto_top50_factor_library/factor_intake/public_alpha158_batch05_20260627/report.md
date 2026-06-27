# Factor Intake Report: public_alpha158_batch05_20260627

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-27T13:49:19.538065+00:00
**Factors evaluated:** 8
**Factor IDs:** q158_sump_20h, q158_sumn_20h, q158_vma_20h, q158_vstd_20h, q158_wvma_20h, q158_vsump_20h, q158_vsumn_20h, q158_vsumd_20h

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| q158_sump_20h | alpha158_rolling_direction | positive | 21 | False |
| q158_sumn_20h | alpha158_rolling_direction | negative | 21 | False |
| q158_vma_20h | alpha158_rolling_volume | conditional | 20 | False |
| q158_vstd_20h | alpha158_rolling_volume | conditional | 20 | False |
| q158_wvma_20h | alpha158_rolling_volume | negative | 21 | False |
| q158_vsump_20h | alpha158_rolling_volume | conditional | 21 | False |
| q158_vsumn_20h | alpha158_rolling_volume | conditional | 21 | False |
| q158_vsumd_20h | alpha158_rolling_volume | conditional | 21 | False |

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
| q158_sump_20h | -0.026750 | 4h | -0.1915 | +0.004484 | 12.75 | DIVERGENT | DIRECTION_REVIEW_REQUIRED |
| q158_sumn_20h | -0.026314 | 4h | -0.1863 | +0.005379 | 15.63 | DIVERGENT | DIRECTION_REVIEW_REQUIRED |
| q158_vma_20h | +0.007225 | 1h | +0.0640 | -0.000398 | -1.29 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_vstd_20h | +0.006670 | 1h | +0.0602 | +0.000591 | 1.98 | CONSISTENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_wvma_20h | +0.004430 | 4h | +0.0403 | -0.000616 | -4.19 | DIVERGENT | TAIL_OR_MONOTONICITY_REVIEW_REQUIRED |
| q158_vsump_20h | -0.006561 | 24h | -0.0581 | +0.001051 | 3.32 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_vsumn_20h | +0.005867 | 4h | +0.0520 | -0.001866 | -5.96 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_vsumd_20h | -0.006016 | 24h | -0.0531 | +0.001526 | 4.87 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### q158_sump_20h

- **Family:** alpha158_rolling_direction
- **Expected direction:** positive
- **Best horizon:** 4h
- **Best adj IC:** -0.026750
- **Best LS t-stat:** 12.75
- **Monthly stability:** UNSTABLE (1/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (2 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** NEAR_DUPLICATE
- **Nearest existing:** mom_vol_adjusted_20h (|ρ|=0.998, NEAR_DUPLICATE); q158_sumd_20h (|ρ|=0.996, NEAR_DUPLICATE); q158_sumn_20h (|ρ|=0.984, NEAR_DUPLICATE)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

### q158_sumn_20h

- **Family:** alpha158_rolling_direction
- **Expected direction:** negative
- **Best horizon:** 4h
- **Best adj IC:** -0.026314
- **Best LS t-stat:** 15.63
- **Monthly stability:** UNSTABLE (1/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (2 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** NEAR_DUPLICATE
- **Nearest existing:** mom_vol_adjusted_20h (|ρ|=0.998, NEAR_DUPLICATE); q158_sumd_20h (|ρ|=0.996, NEAR_DUPLICATE); q158_sump_20h (|ρ|=0.984, NEAR_DUPLICATE)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

### q158_vma_20h

- **Family:** alpha158_rolling_volume
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.007225
- **Best LS t-stat:** -1.29
- **Monthly stability:** STABLE (22/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** NEAR_DUPLICATE
- **Nearest existing:** range_breakout_vol_confirm_20h (|ρ|=0.973, NEAR_DUPLICATE); vol_zscore_20h (|ρ|=0.936, HIGH_REDUNDANCY); qvol_zscore_20h (|ρ|=0.934, HIGH_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: NEAR_DUPLICATE. Consider dropping one factor.

### q158_vstd_20h

- **Family:** alpha158_rolling_volume
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.006670
- **Best LS t-stat:** 1.98
- **Monthly stability:** STABLE (21/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** q158_vma_20h (|ρ|=0.870, HIGH_REDUNDANCY); range_breakout_vol_confirm_20h (|ρ|=0.832, MODERATE_REDUNDANCY); vol_zscore_20h (|ρ|=0.727, MODERATE_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: HIGH_REDUNDANCY. Consider dropping one factor.

### q158_wvma_20h

- **Family:** alpha158_rolling_volume
- **Expected direction:** negative
- **Best horizon:** 4h
- **Best adj IC:** +0.004430
- **Best LS t-stat:** -4.19
- **Monthly stability:** MODERATE (19/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (2 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** MODERATE_REDUNDANCY
- **Nearest existing:** realized_kurt_20h (|ρ|=0.712, MODERATE_REDUNDANCY); wvma_20h (|ρ|=0.621, LOW_REDUNDANCY); vol_of_vol_20h (|ρ|=0.521, LOW_REDUNDANCY)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

### q158_vsump_20h

- **Family:** alpha158_rolling_volume
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** -0.006561
- **Best LS t-stat:** 3.32
- **Monthly stability:** UNSTABLE (9/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** NEAR_DUPLICATE
- **Nearest existing:** q158_vsumd_20h (|ρ|=0.996, NEAR_DUPLICATE); q158_vsumn_20h (|ρ|=0.984, NEAR_DUPLICATE); range_breakout_vol_confirm_20h (|ρ|=0.718, MODERATE_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: NEAR_DUPLICATE. Consider dropping one factor.

### q158_vsumn_20h

- **Family:** alpha158_rolling_volume
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.005867
- **Best LS t-stat:** -5.96
- **Monthly stability:** MODERATE (17/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** NEAR_DUPLICATE
- **Nearest existing:** q158_vsumd_20h (|ρ|=0.996, NEAR_DUPLICATE); q158_vsump_20h (|ρ|=0.984, NEAR_DUPLICATE); range_breakout_vol_confirm_20h (|ρ|=0.718, MODERATE_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: NEAR_DUPLICATE. Consider dropping one factor.

### q158_vsumd_20h

- **Family:** alpha158_rolling_volume
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** -0.006016
- **Best LS t-stat:** 4.87
- **Monthly stability:** MIXED (11/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** NEAR_DUPLICATE
- **Nearest existing:** q158_vsumn_20h (|ρ|=0.996, NEAR_DUPLICATE); q158_vsump_20h (|ρ|=0.996, NEAR_DUPLICATE); range_breakout_vol_confirm_20h (|ρ|=0.718, MODERATE_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: NEAR_DUPLICATE. Consider dropping one factor.

## Redundancy Warnings

- **q158_sumn_20h ↔ mom_vol_adjusted_20h**: NEAR_DUPLICATE (|ρ| = 0.998)
- **q158_sump_20h ↔ mom_vol_adjusted_20h**: NEAR_DUPLICATE (|ρ| = 0.998)
- **q158_sumn_20h ↔ q158_sumd_20h**: NEAR_DUPLICATE (|ρ| = 0.996)
- **q158_vsumn_20h ↔ q158_vsumd_20h**: NEAR_DUPLICATE (|ρ| = 0.996)
- **q158_vsump_20h ↔ q158_vsumd_20h**: NEAR_DUPLICATE (|ρ| = 0.996)
- **q158_sump_20h ↔ q158_sumd_20h**: NEAR_DUPLICATE (|ρ| = 0.996)
- **q158_vsump_20h ↔ q158_vsumn_20h**: NEAR_DUPLICATE (|ρ| = 0.984)
- **q158_sump_20h ↔ q158_sumn_20h**: NEAR_DUPLICATE (|ρ| = 0.984)
- **q158_vma_20h ↔ range_breakout_vol_confirm_20h**: NEAR_DUPLICATE (|ρ| = 0.973)
- **q158_sumn_20h ↔ q158_roc_20h**: NEAR_DUPLICATE (|ρ| = 0.959)
- **q158_sumn_20h ↔ mom_20h**: NEAR_DUPLICATE (|ρ| = 0.959)
- **q158_sump_20h ↔ mom_20h**: NEAR_DUPLICATE (|ρ| = 0.958)
- **q158_sump_20h ↔ q158_roc_20h**: NEAR_DUPLICATE (|ρ| = 0.958)
- **q158_vma_20h ↔ vol_zscore_20h**: HIGH_REDUNDANCY (|ρ| = 0.936)
- **q158_vma_20h ↔ qvol_zscore_20h**: HIGH_REDUNDANCY (|ρ| = 0.934)
- **q158_sump_20h ↔ trend_efficiency_24h**: HIGH_REDUNDANCY (|ρ| = 0.921)
- **q158_sumn_20h ↔ trend_efficiency_24h**: HIGH_REDUNDANCY (|ρ| = 0.921)
- **q158_vma_20h ↔ q158_vstd_20h**: HIGH_REDUNDANCY (|ρ| = 0.870)

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
