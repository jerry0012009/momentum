# Factor Intake Report: a101_curated_1h_equivalent_no_cap

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-24T01:34:10.075137+00:00
**Factors evaluated:** 4
**Factor IDs:** a101_volume_xs_z_mean_neg_112h, a101_vol_xs_z_product_112h, a101_volume_low_alpha_min_84_120, a101_volume_high_alpha_min_84_84

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| a101_volume_xs_z_mean_neg_112h | alpha101_curated_volume_crowding | positive | 112 | True |
| a101_vol_xs_z_product_112h | alpha101_curated_volume_regime | conditional | 112 | True |
| a101_volume_low_alpha_min_84_120 | alpha101_curated_volume_price_regression | conditional | 203 | True |
| a101_volume_high_alpha_min_84_84 | alpha101_curated_volume_price_regression | conditional | 167 | True |

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
| a101_volume_xs_z_mean_neg_112h | +0.068354 | 72h | +0.4423 | +0.001735 | 5.01 | CONSISTENT | STRONG_DIAGNOSTIC_CANDIDATE |
| a101_vol_xs_z_product_112h | +0.056717 | 72h | +0.4487 | -0.000431 | -2.45 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| a101_volume_low_alpha_min_84_120 | +0.062473 | 72h | +0.4781 | +0.001146 | 4.23 | CONSISTENT | CONDITIONAL_DIRECTION_REVIEW |
| a101_volume_high_alpha_min_84_84 | +0.058513 | 72h | +0.4482 | +0.002075 | 7.57 | CONSISTENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### a101_volume_xs_z_mean_neg_112h

- **Family:** alpha101_curated_volume_crowding
- **Expected direction:** positive
- **Best horizon:** 72h
- **Best adj IC:** +0.068354
- **Best LS t-stat:** 5.01
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** MODERATE_REDUNDANCY
- **Nearest existing:** a101_vol_xs_z_product_112h (|ρ|=0.801, MODERATE_REDUNDANCY); xs_rank_vol (|ρ|=0.607, LOW_REDUNDANCY); a101_volume_high_alpha_min_84_84 (|ρ|=0.461, LOW_REDUNDANCY)
- **Decision bucket:** PASS_DIAGNOSTIC
- **Recommended action:** Candidate for future signal research. Not auto-promoted.
- **Caveats:** nan

### a101_vol_xs_z_product_112h

- **Family:** alpha101_curated_volume_regime
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** +0.056717
- **Best LS t-stat:** -2.45
- **Monthly stability:** STABLE (22/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** MODERATE_REDUNDANCY
- **Nearest existing:** a101_volume_xs_z_mean_neg_112h (|ρ|=0.801, MODERATE_REDUNDANCY); xs_rank_vol (|ρ|=0.438, LOW_REDUNDANCY); a101_volume_high_alpha_min_84_84 (|ρ|=0.319, LOW_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### a101_volume_low_alpha_min_84_120

- **Family:** alpha101_curated_volume_price_regression
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** +0.062473
- **Best LS t-stat:** 4.23
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** LOW_REDUNDANCY
- **Nearest existing:** xs_rank_vol (|ρ|=0.550, LOW_REDUNDANCY); tech_atr (|ρ|=0.440, LOW_REDUNDANCY); mom_120h (|ρ|=0.194, LOW_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### a101_volume_high_alpha_min_84_84

- **Family:** alpha101_curated_volume_price_regression
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** +0.058513
- **Best LS t-stat:** 7.57
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (2 sign changes)
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** MODERATE_REDUNDANCY
- **Nearest existing:** xs_rank_vol (|ρ|=0.805, MODERATE_REDUNDANCY); tech_atr (|ρ|=0.663, LOW_REDUNDANCY); a101_volume_xs_z_mean_neg_112h (|ρ|=0.461, LOW_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
