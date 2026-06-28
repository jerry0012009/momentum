# Factor Intake Report: public_alpha158_batch11_20260628

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-28T05:21:42.417979+00:00
**Factors evaluated:** 4
**Factor IDs:** q158_ma_5h, q158_std_5h, q158_max_5h, q158_min_5h

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| q158_ma_5h | alpha158_rolling_price | conditional | 5 | False |
| q158_std_5h | alpha158_rolling_price | negative | 5 | False |
| q158_max_5h | alpha158_rolling_price | conditional | 5 | False |
| q158_min_5h | alpha158_rolling_price | conditional | 5 | False |

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
| q158_ma_5h | +0.038322 | 1h | +0.2349 | -0.002466 | -6.74 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_std_5h | +0.074624 | 72h | +0.4259 | -0.004818 | -11.73 | DIVERGENT | DIRECTION_REVIEW_REQUIRED |
| q158_max_5h | -0.061924 | 72h | -0.3685 | +0.002910 | 7.36 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_min_5h | +0.065899 | 72h | +0.4129 | -0.004469 | -11.24 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### q158_ma_5h

- **Family:** alpha158_rolling_price
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.038322
- **Best LS t-stat:** -6.74
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** q158_close_close_4h (|ρ|=0.883, HIGH_REDUNDANCY); q158_high_close_4h (|ρ|=0.818, MODERATE_REDUNDANCY); q158_low_close_4h (|ρ|=0.813, MODERATE_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: HIGH_REDUNDANCY. Consider dropping one factor.

### q158_std_5h

- **Family:** alpha158_rolling_price
- **Expected direction:** negative
- **Best horizon:** 72h
- **Best adj IC:** +0.074624
- **Best LS t-stat:** -11.73
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** LOW_REDUNDANCY
- **Nearest existing:** q158_high_low_range (|ρ|=0.654, LOW_REDUNDANCY); range_1h (|ρ|=0.654, LOW_REDUNDANCY); q158_klen_open (|ρ|=0.654, LOW_REDUNDANCY)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

### q158_max_5h

- **Family:** alpha158_rolling_price
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** -0.061924
- **Best LS t-stat:** 7.36
- **Monthly stability:** UNSTABLE (1/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** MODERATE_REDUNDANCY
- **Nearest existing:** q158_high_close_0h (|ρ|=0.722, MODERATE_REDUNDANCY); q158_high_close_4h (|ρ|=0.720, MODERATE_REDUNDANCY); q158_ma_5h (|ρ|=0.679, LOW_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### q158_min_5h

- **Family:** alpha158_rolling_price
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** +0.065899
- **Best LS t-stat:** -11.24
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** MODERATE_REDUNDANCY
- **Nearest existing:** q158_low_close_0h (|ρ|=0.734, MODERATE_REDUNDANCY); q158_low_close_4h (|ρ|=0.698, LOW_REDUNDANCY); q158_min_20h (|ρ|=0.676, LOW_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

## Redundancy Warnings

- **q158_ma_5h ↔ q158_close_close_4h**: HIGH_REDUNDANCY (|ρ| = 0.883)

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
