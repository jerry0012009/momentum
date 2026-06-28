# Factor Intake Report: public_alpha101_ohlcv_batch01_20260628

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-28T11:43:04.617996+00:00
**Factors evaluated:** 5
**Factor IDs:** wq101_alpha6, wq101_alpha9, wq101_alpha21, wq101_alpha41, wq101_alpha54

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| wq101_alpha6 | wq101 | conditional | 10 | True |
| wq101_alpha9 | wq101 | conditional | 6 | True |
| wq101_alpha21 | wq101 | conditional | 20 | True |
| wq101_alpha41 | wq101 | conditional | 1 | True |
| wq101_alpha54 | wq101 | conditional | 1 | True |

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
| wq101_alpha6 | +0.023462 | 24h | +0.2098 | -0.001002 | -3.23 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha9 | +0.016387 | 1h | +0.1453 | -0.000394 | -1.35 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha21 | +0.007831 | 1h | +0.0751 | -0.000262 | -1.03 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha41 | +0.003494 | 1h | +0.0351 | -0.000478 | -1.71 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha54 | +0.028727 | 1h | +0.2391 | +0.000431 | 1.43 | CONSISTENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### wq101_alpha6

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** +0.023462
- **Best LS t-stat:** -3.23
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** LOW_REDUNDANCY
- **Nearest existing:** range_breakout_vol_confirm_20h (|ρ|=0.544, LOW_REDUNDANCY); q158_corr_20h (|ρ|=0.427, LOW_REDUNDANCY); mom_5h (|ρ|=0.389, LOW_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha9

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.016387
- **Best LS t-stat:** -1.35
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** wq101_alpha101 (|ρ|=0.859, HIGH_REDUNDANCY); candle_body (|ρ|=0.753, MODERATE_REDUNDANCY); q158_kmid_range (|ρ|=0.753, MODERATE_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: HIGH_REDUNDANCY. Consider dropping one factor.

### wq101_alpha21

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.007831
- **Best LS t-stat:** -1.03
- **Monthly stability:** STABLE (22/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** LOW_REDUNDANCY
- **Nearest existing:** vol_zscore_20h (|ρ|=0.497, LOW_REDUNDANCY); q158_vma_20h (|ρ|=0.489, LOW_REDUNDANCY); qvol_zscore_20h (|ρ|=0.484, LOW_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha41

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.003494
- **Best LS t-stat:** -1.71
- **Monthly stability:** MODERATE (18/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** LOW_REDUNDANCY
- **Nearest existing:** q158_resi_20h (|ρ|=0.529, LOW_REDUNDANCY); q158_ma_10h (|ρ|=0.455, LOW_REDUNDANCY); q158_min_10h (|ρ|=0.408, LOW_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha54

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.028727
- **Best LS t-stat:** 1.43
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** MONOTONIC_INCREASING
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** NEAR_DUPLICATE
- **Nearest existing:** q158_ksft_range (|ρ|=0.992, NEAR_DUPLICATE); q158_ksft_open (|ρ|=0.915, HIGH_REDUNDANCY); q158_kmid_range (|ρ|=0.782, MODERATE_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: NEAR_DUPLICATE. Consider dropping one factor.

## Redundancy Warnings

- **wq101_alpha54 ↔ q158_ksft_range**: NEAR_DUPLICATE (|ρ| = 0.992)
- **wq101_alpha54 ↔ q158_ksft_open**: HIGH_REDUNDANCY (|ρ| = 0.915)
- **wq101_alpha9 ↔ wq101_alpha101**: HIGH_REDUNDANCY (|ρ| = 0.859)

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
