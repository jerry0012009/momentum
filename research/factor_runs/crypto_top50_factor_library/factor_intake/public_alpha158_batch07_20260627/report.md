# Factor Intake Report: public_alpha158_batch07_20260627

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-27T15:01:27.449307+00:00
**Factors evaluated:** 5
**Factor IDs:** q158_high_close_0h, q158_low_close_0h, q158_open_close_1h, q158_high_close_1h, q158_low_close_1h

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| q158_high_close_0h | alpha158_price | conditional | 1 | False |
| q158_low_close_0h | alpha158_price | conditional | 1 | False |
| q158_open_close_1h | alpha158_price | conditional | 2 | False |
| q158_high_close_1h | alpha158_price | conditional | 2 | False |
| q158_low_close_1h | alpha158_price | conditional | 2 | False |

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
| q158_high_close_0h | -0.060671 | 72h | -0.3739 | +0.004035 | 10.17 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_low_close_0h | +0.062831 | 72h | +0.4030 | -0.003957 | -10.17 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_open_close_1h | +0.036120 | 1h | +0.2238 | -0.001983 | -5.48 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_high_close_1h | -0.029936 | 72h | -0.1919 | +0.000870 | 2.31 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_low_close_1h | +0.047763 | 1h | +0.2990 | -0.003343 | -8.87 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### q158_high_close_0h

- **Family:** alpha158_price
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** -0.060671
- **Best LS t-stat:** 10.17
- **Monthly stability:** UNSTABLE (1/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** MODERATE_REDUNDANCY
- **Nearest existing:** q158_ksft_range (|ρ|=0.743, MODERATE_REDUNDANCY); q158_ksft_open (|ρ|=0.721, MODERATE_REDUNDANCY); range_1h (|ρ|=0.616, LOW_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### q158_low_close_0h

- **Family:** alpha158_price
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** +0.062831
- **Best LS t-stat:** -10.17
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** MODERATE_REDUNDANCY
- **Nearest existing:** q158_ksft_range (|ρ|=0.728, MODERATE_REDUNDANCY); q158_ksft_open (|ρ|=0.688, LOW_REDUNDANCY); q158_min_20h (|ρ|=0.622, LOW_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### q158_open_close_1h

- **Family:** alpha158_price
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.036120
- **Best LS t-stat:** -5.48
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** NEAR_DUPLICATE
- **Nearest existing:** rev_2h (|ρ|=0.996, NEAR_DUPLICATE); q158_high_close_1h (|ρ|=0.784, MODERATE_REDUNDANCY); q158_low_close_1h (|ρ|=0.784, MODERATE_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: NEAR_DUPLICATE. Consider dropping one factor.

### q158_high_close_1h

- **Family:** alpha158_price
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** -0.029936
- **Best LS t-stat:** 2.31
- **Monthly stability:** UNSTABLE (2/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** MODERATE_REDUNDANCY
- **Nearest existing:** rev_2h (|ρ|=0.816, MODERATE_REDUNDANCY); q158_open_close_1h (|ρ|=0.784, MODERATE_REDUNDANCY); rev_1h (|ρ|=0.771, MODERATE_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### q158_low_close_1h

- **Family:** alpha158_price
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.047763
- **Best LS t-stat:** -8.87
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** MODERATE_REDUNDANCY
- **Nearest existing:** q158_open_close_1h (|ρ|=0.784, MODERATE_REDUNDANCY); rev_2h (|ρ|=0.783, MODERATE_REDUNDANCY); rev_1h (|ρ|=0.758, MODERATE_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

## Redundancy Warnings

- **q158_open_close_1h ↔ rev_2h**: NEAR_DUPLICATE (|ρ| = 0.996)

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
