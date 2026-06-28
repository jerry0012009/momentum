# Factor Intake Report: public_alpha101_ohlcv_batch02_20260628

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-28T12:51:11.420874+00:00
**Factors evaluated:** 5
**Factor IDs:** wq101_alpha23, wq101_alpha24, wq101_alpha46, wq101_alpha49, wq101_alpha51

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| wq101_alpha23 | wq101 | conditional | 20 | True |
| wq101_alpha24 | wq101 | conditional | 200 | True |
| wq101_alpha46 | wq101 | conditional | 21 | True |
| wq101_alpha49 | wq101 | conditional | 21 | True |
| wq101_alpha51 | wq101 | conditional | 21 | True |

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
| wq101_alpha23 | +0.011681 | 4h | +0.1051 | -0.001611 | -5.58 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha24 | -0.030559 | 72h | -0.2327 | -0.001392 | -4.77 | CONSISTENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha46 | +0.015403 | 1h | +0.1327 | -0.001484 | -5.11 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha49 | +0.020842 | 1h | +0.1819 | -0.000488 | -1.68 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha51 | +0.021089 | 1h | +0.1847 | -0.000336 | -1.16 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### wq101_alpha23

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.011681
- **Best LS t-stat:** -5.58
- **Monthly stability:** STABLE (23/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (3 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** LOW_REDUNDANCY
- **Nearest existing:** q158_kup_open (|ρ|=0.520, LOW_REDUNDANCY); candle_wick_lower (|ρ|=0.473, LOW_REDUNDANCY); q158_klow_range (|ρ|=0.473, LOW_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha24

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** -0.030559
- **Best LS t-stat:** -4.77
- **Monthly stability:** UNSTABLE (5/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** LOW_REDUNDANCY
- **Nearest existing:** tech_atr (|ρ|=0.633, LOW_REDUNDANCY); a101_volume_high_alpha_min_84_84 (|ρ|=0.523, LOW_REDUNDANCY); xs_rank_vol (|ρ|=0.506, LOW_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha46

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.015403
- **Best LS t-stat:** -5.11
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** LOW_REDUNDANCY
- **Nearest existing:** q158_open_close_2h (|ρ|=0.602, LOW_REDUNDANCY); rev_10h (|ρ|=0.566, LOW_REDUNDANCY); mom_10h (|ρ|=0.566, LOW_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha49

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.020842
- **Best LS t-stat:** -1.68
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** NEAR_DUPLICATE
- **Nearest existing:** wq101_alpha51 (|ρ|=0.977, NEAR_DUPLICATE); wq101_alpha101 (|ρ|=0.899, HIGH_REDUNDANCY); wq101_alpha9 (|ρ|=0.825, MODERATE_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: NEAR_DUPLICATE. Consider dropping one factor.

### wq101_alpha51

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.021089
- **Best LS t-stat:** -1.16
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** NEAR_DUPLICATE
- **Nearest existing:** wq101_alpha49 (|ρ|=0.977, NEAR_DUPLICATE); wq101_alpha101 (|ρ|=0.882, HIGH_REDUNDANCY); wq101_alpha9 (|ρ|=0.803, MODERATE_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: NEAR_DUPLICATE. Consider dropping one factor.

## Redundancy Warnings

- **wq101_alpha49 ↔ wq101_alpha51**: NEAR_DUPLICATE (|ρ| = 0.977)
- **wq101_alpha49 ↔ wq101_alpha101**: HIGH_REDUNDANCY (|ρ| = 0.899)
- **wq101_alpha51 ↔ wq101_alpha101**: HIGH_REDUNDANCY (|ρ| = 0.882)

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
