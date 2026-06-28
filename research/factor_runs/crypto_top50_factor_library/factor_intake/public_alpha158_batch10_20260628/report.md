# Factor Intake Report: public_alpha158_batch10_20260628

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-28T04:52:52.490386+00:00
**Factors evaluated:** 4
**Factor IDs:** q158_open_close_4h, q158_high_close_4h, q158_low_close_4h, q158_close_close_4h

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| q158_open_close_4h | alpha158_price | conditional | 5 | False |
| q158_high_close_4h | alpha158_price | conditional | 5 | False |
| q158_low_close_4h | alpha158_price | conditional | 5 | False |
| q158_close_close_4h | alpha158_price | conditional | 5 | False |

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
| q158_open_close_4h | +0.032344 | 1h | +0.2007 | -0.002860 | -7.73 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_high_close_4h | +0.023414 | 1h | +0.1393 | -0.001096 | -2.91 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_low_close_4h | +0.042225 | 4h | +0.2672 | -0.003791 | -10.09 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_close_close_4h | +0.032395 | 1h | +0.2016 | -0.002488 | -6.78 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### q158_open_close_4h

- **Family:** alpha158_price
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.032344
- **Best LS t-stat:** -7.73
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** q158_low_close_4h (|ρ|=0.906, HIGH_REDUNDANCY); q158_high_close_4h (|ρ|=0.906, HIGH_REDUNDANCY); q158_close_close_4h (|ρ|=0.849, MODERATE_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: HIGH_REDUNDANCY. Consider dropping one factor.

### q158_high_close_4h

- **Family:** alpha158_price
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.023414
- **Best LS t-stat:** -2.91
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** q158_close_close_4h (|ρ|=0.913, HIGH_REDUNDANCY); q158_open_close_4h (|ρ|=0.906, HIGH_REDUNDANCY); q158_low_close_4h (|ρ|=0.837, MODERATE_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: HIGH_REDUNDANCY. Consider dropping one factor.

### q158_low_close_4h

- **Family:** alpha158_price
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.042225
- **Best LS t-stat:** -10.09
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** q158_close_close_4h (|ρ|=0.909, HIGH_REDUNDANCY); q158_open_close_4h (|ρ|=0.906, HIGH_REDUNDANCY); q158_high_close_4h (|ρ|=0.837, MODERATE_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: HIGH_REDUNDANCY. Consider dropping one factor.

### q158_close_close_4h

- **Family:** alpha158_price
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.032395
- **Best LS t-stat:** -6.78
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** q158_high_close_4h (|ρ|=0.913, HIGH_REDUNDANCY); q158_low_close_4h (|ρ|=0.909, HIGH_REDUNDANCY); q158_open_close_4h (|ρ|=0.849, MODERATE_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: HIGH_REDUNDANCY. Consider dropping one factor.

## Redundancy Warnings

- **q158_high_close_4h ↔ q158_close_close_4h**: HIGH_REDUNDANCY (|ρ| = 0.913)
- **q158_low_close_4h ↔ q158_close_close_4h**: HIGH_REDUNDANCY (|ρ| = 0.909)
- **q158_open_close_4h ↔ q158_low_close_4h**: HIGH_REDUNDANCY (|ρ| = 0.906)
- **q158_open_close_4h ↔ q158_high_close_4h**: HIGH_REDUNDANCY (|ρ| = 0.906)

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
