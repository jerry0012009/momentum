# Factor Intake Report: public_alpha158_batch16_20260628

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-28T08:05:02.358913+00:00
**Factors evaluated:** 4
**Factor IDs:** q158_beta_30h, q158_rsqr_30h, q158_resi_30h, q158_imax_30h

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| q158_beta_30h | alpha158_rolling_regression | conditional | 30 | False |
| q158_rsqr_30h | alpha158_rolling_regression | conditional | 30 | False |
| q158_resi_30h | alpha158_rolling_regression | conditional | 30 | False |
| q158_imax_30h | alpha158_rolling_position | conditional | 30 | False |

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
| q158_beta_30h | -0.023284 | 24h | -0.1412 | +0.004937 | 12.91 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_rsqr_30h | +0.004903 | 4h | +0.0391 | +0.002430 | 8.24 | CONSISTENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_resi_30h | -0.028652 | 1h | -0.1779 | +0.001562 | 4.29 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_imax_30h | +0.012692 | 4h | +0.1055 | -0.003805 | -12.37 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### q158_beta_30h

- **Family:** alpha158_rolling_regression
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** -0.023284
- **Best LS t-stat:** 12.91
- **Monthly stability:** UNSTABLE (6/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** NEAR_DUPLICATE
- **Nearest existing:** ma_gap_10_40 (|ρ|=0.959, NEAR_DUPLICATE); rev_24h (|ρ|=0.910, HIGH_REDUNDANCY); ema_12_26_gap (|ρ|=0.859, HIGH_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: NEAR_DUPLICATE. Consider dropping one factor.

### q158_rsqr_30h

- **Family:** alpha158_rolling_regression
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.004903
- **Best LS t-stat:** 8.24
- **Monthly stability:** MIXED (14/25 months positive)
- **Quantile monotonicity:** MONOTONIC_INCREASING
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** MODERATE_REDUNDANCY
- **Nearest existing:** mom_vol_adjusted_20h (|ρ|=0.772, MODERATE_REDUNDANCY); q158_sump_20h (|ρ|=0.757, MODERATE_REDUNDANCY); q158_sumd_20h (|ρ|=0.756, MODERATE_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### q158_resi_30h

- **Family:** alpha158_rolling_regression
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** -0.028652
- **Best LS t-stat:** 4.29
- **Monthly stability:** UNSTABLE (0/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** MODERATE_REDUNDANCY
- **Nearest existing:** q158_ma_10h (|ρ|=0.792, MODERATE_REDUNDANCY); q158_resi_20h (|ρ|=0.755, MODERATE_REDUNDANCY); rev_10h (|ρ|=0.747, MODERATE_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### q158_imax_30h

- **Family:** alpha158_rolling_position
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.012692
- **Best LS t-stat:** -12.37
- **Monthly stability:** STABLE (21/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (2 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** MODERATE_REDUNDANCY
- **Nearest existing:** q158_beta_30h (|ρ|=0.710, MODERATE_REDUNDANCY); ma_gap_10_40 (|ρ|=0.695, LOW_REDUNDANCY); rev_24h (|ρ|=0.648, LOW_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

## Redundancy Warnings

- **q158_beta_30h ↔ ma_gap_10_40**: NEAR_DUPLICATE (|ρ| = 0.959)
- **q158_beta_30h ↔ rev_24h**: HIGH_REDUNDANCY (|ρ| = 0.910)
- **q158_beta_30h ↔ ema_12_26_gap**: HIGH_REDUNDANCY (|ρ| = 0.859)

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
