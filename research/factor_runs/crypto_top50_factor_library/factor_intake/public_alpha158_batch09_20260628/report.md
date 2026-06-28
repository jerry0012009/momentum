# Factor Intake Report: public_alpha158_batch09_20260628

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-28T04:20:13.403623+00:00
**Factors evaluated:** 4
**Factor IDs:** q158_volume_ratio_1h, q158_volume_ratio_2h, q158_volume_ratio_3h, q158_volume_ratio_4h

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| q158_volume_ratio_1h | alpha158_volume | conditional | 2 | False |
| q158_volume_ratio_2h | alpha158_volume | conditional | 3 | False |
| q158_volume_ratio_3h | alpha158_volume | conditional | 4 | False |
| q158_volume_ratio_4h | alpha158_volume | conditional | 5 | False |

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
| q158_volume_ratio_1h | +0.003392 | 1h | +0.0338 | -0.000933 | -3.31 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_volume_ratio_2h | +0.004928 | 4h | +0.0475 | -0.000996 | -3.38 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_volume_ratio_3h | +0.006547 | 4h | +0.0618 | -0.001114 | -3.74 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_volume_ratio_4h | +0.006875 | 4h | +0.0639 | -0.001149 | -3.83 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### q158_volume_ratio_1h

- **Family:** alpha158_volume
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.003392
- **Best LS t-stat:** -3.31
- **Monthly stability:** STABLE (20/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** LOW_REDUNDANCY
- **Nearest existing:** q158_volume_ratio_2h (|ρ|=0.619, LOW_REDUNDANCY); rsi_7h (|ρ|=0.525, LOW_REDUNDANCY); range_breakout_vol_confirm_20h (|ρ|=0.513, LOW_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### q158_volume_ratio_2h

- **Family:** alpha158_volume
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.004928
- **Best LS t-stat:** -3.38
- **Monthly stability:** STABLE (23/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** LOW_REDUNDANCY
- **Nearest existing:** q158_volume_ratio_1h (|ρ|=0.619, LOW_REDUNDANCY); q158_vsumn_20h (|ρ|=0.614, LOW_REDUNDANCY); range_breakout_vol_confirm_20h (|ρ|=0.601, LOW_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### q158_volume_ratio_3h

- **Family:** alpha158_volume
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.006547
- **Best LS t-stat:** -3.74
- **Monthly stability:** STABLE (22/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (3 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** LOW_REDUNDANCY
- **Nearest existing:** range_breakout_vol_confirm_20h (|ρ|=0.646, LOW_REDUNDANCY); q158_high_close_3h (|ρ|=0.136, LOW_REDUNDANCY); q158_low_close_3h (|ρ|=0.103, LOW_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### q158_volume_ratio_4h

- **Family:** alpha158_volume
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.006875
- **Best LS t-stat:** -3.83
- **Monthly stability:** STABLE (22/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** MODERATE_REDUNDANCY
- **Nearest existing:** range_breakout_vol_confirm_20h (|ρ|=0.725, MODERATE_REDUNDANCY); q158_vma_20h (|ρ|=0.683, LOW_REDUNDANCY); vol_zscore_20h (|ρ|=0.678, LOW_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
