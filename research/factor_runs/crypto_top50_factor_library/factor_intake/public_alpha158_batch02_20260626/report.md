# Factor Intake Report: public_alpha158_batch02_20260626

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-26T20:08:13.902304+00:00
**Factors evaluated:** 6
**Factor IDs:** q158_qtlu_20h, q158_qtld_20h, q158_rank_close_20h, q158_cntp_20h, q158_cntn_20h, q158_sumd_20h

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| q158_qtlu_20h | alpha158_rolling | conditional | 20 | False |
| q158_qtld_20h | alpha158_rolling | conditional | 20 | False |
| q158_rank_close_20h | alpha158_rolling | conditional | 20 | False |
| q158_cntp_20h | alpha158_rolling | positive | 21 | False |
| q158_cntn_20h | alpha158_rolling | negative | 21 | False |
| q158_sumd_20h | alpha158_rolling | positive | 21 | False |

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
| q158_qtlu_20h | +0.022359 | 4h | +0.1336 | -0.003740 | -10.10 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_qtld_20h | +0.046721 | 24h | +0.2955 | -0.004542 | -12.05 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_rank_close_20h | -0.031611 | 4h | -0.2312 | +0.003919 | 11.83 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_cntp_20h | -0.011981 | 4h | -0.1045 | +0.003713 | 11.81 | DIVERGENT | TAIL_OR_MONOTONICITY_REVIEW_REQUIRED |
| q158_cntn_20h | -0.009749 | 4h | -0.0830 | +0.004046 | 13.15 | DIVERGENT | TAIL_OR_MONOTONICITY_REVIEW_REQUIRED |
| q158_sumd_20h | -0.026634 | 4h | -0.1882 | +0.004993 | 14.42 | DIVERGENT | DIRECTION_REVIEW_REQUIRED |

## Conclusion Cards

### q158_qtlu_20h

- **Family:** alpha158_rolling
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.022359
- **Best LS t-stat:** -10.10
- **Monthly stability:** STABLE (22/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** vwap_dev_20h (|ρ|=0.924, HIGH_REDUNDANCY); bb_zscore_20h (|ρ|=0.900, HIGH_REDUNDANCY); q158_rank_close_20h (|ρ|=0.886, HIGH_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: HIGH_REDUNDANCY. Consider dropping one factor.

### q158_qtld_20h

- **Family:** alpha158_rolling
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** +0.046721
- **Best LS t-stat:** -12.05
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (3 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** bb_zscore_20h (|ρ|=0.916, HIGH_REDUNDANCY); q158_rank_close_20h (|ρ|=0.905, HIGH_REDUNDANCY); vwap_dev_20h (|ρ|=0.889, HIGH_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: HIGH_REDUNDANCY. Consider dropping one factor.

### q158_rank_close_20h

- **Family:** alpha158_rolling
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** -0.031611
- **Best LS t-stat:** 11.83
- **Monthly stability:** UNSTABLE (0/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (2 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** NEAR_DUPLICATE
- **Nearest existing:** bb_zscore_20h (|ρ|=0.979, NEAR_DUPLICATE); breakout_dist_20h (|ρ|=0.913, HIGH_REDUNDANCY); q158_rsv_20h (|ρ|=0.912, HIGH_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: NEAR_DUPLICATE. Consider dropping one factor.

### q158_cntp_20h

- **Family:** alpha158_rolling
- **Expected direction:** positive
- **Best horizon:** 4h
- **Best adj IC:** -0.011981
- **Best LS t-stat:** 11.81
- **Monthly stability:** UNSTABLE (5/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** q158_cntn_20h (|ρ|=0.922, HIGH_REDUNDANCY); mom_vol_adjusted_20h (|ρ|=0.710, MODERATE_REDUNDANCY); q158_sumd_20h (|ρ|=0.699, LOW_REDUNDANCY)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

### q158_cntn_20h

- **Family:** alpha158_rolling
- **Expected direction:** negative
- **Best horizon:** 4h
- **Best adj IC:** -0.009749
- **Best LS t-stat:** 13.15
- **Monthly stability:** UNSTABLE (5/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (3 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** q158_cntp_20h (|ρ|=0.922, HIGH_REDUNDANCY); mom_vol_adjusted_20h (|ρ|=0.708, MODERATE_REDUNDANCY); q158_sumd_20h (|ρ|=0.698, LOW_REDUNDANCY)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

### q158_sumd_20h

- **Family:** alpha158_rolling
- **Expected direction:** positive
- **Best horizon:** 4h
- **Best adj IC:** -0.026634
- **Best LS t-stat:** 14.42
- **Monthly stability:** UNSTABLE (1/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (2 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** NEAR_DUPLICATE
- **Nearest existing:** mom_vol_adjusted_20h (|ρ|=0.998, NEAR_DUPLICATE); mom_20h (|ρ|=0.963, NEAR_DUPLICATE); trend_efficiency_24h (|ρ|=0.921, HIGH_REDUNDANCY)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

## Redundancy Warnings

- **q158_sumd_20h ↔ mom_vol_adjusted_20h**: NEAR_DUPLICATE (|ρ| = 0.998)
- **q158_rank_close_20h ↔ bb_zscore_20h**: NEAR_DUPLICATE (|ρ| = 0.979)
- **q158_sumd_20h ↔ mom_20h**: NEAR_DUPLICATE (|ρ| = 0.963)
- **q158_qtlu_20h ↔ vwap_dev_20h**: HIGH_REDUNDANCY (|ρ| = 0.924)
- **q158_cntp_20h ↔ q158_cntn_20h**: HIGH_REDUNDANCY (|ρ| = 0.922)
- **q158_sumd_20h ↔ trend_efficiency_24h**: HIGH_REDUNDANCY (|ρ| = 0.921)
- **q158_qtld_20h ↔ bb_zscore_20h**: HIGH_REDUNDANCY (|ρ| = 0.916)
- **q158_rank_close_20h ↔ breakout_dist_20h**: HIGH_REDUNDANCY (|ρ| = 0.913)
- **q158_rank_close_20h ↔ q158_rsv_20h**: HIGH_REDUNDANCY (|ρ| = 0.912)
- **q158_qtld_20h ↔ q158_rank_close_20h**: HIGH_REDUNDANCY (|ρ| = 0.905)
- **q158_rank_close_20h ↔ vwap_dev_20h**: HIGH_REDUNDANCY (|ρ| = 0.901)
- **q158_qtlu_20h ↔ bb_zscore_20h**: HIGH_REDUNDANCY (|ρ| = 0.900)
- **q158_qtld_20h ↔ vwap_dev_20h**: HIGH_REDUNDANCY (|ρ| = 0.889)
- **q158_qtlu_20h ↔ q158_rank_close_20h**: HIGH_REDUNDANCY (|ρ| = 0.886)
- **q158_rank_close_20h ↔ rsi_14h**: HIGH_REDUNDANCY (|ρ| = 0.885)
- **q158_qtlu_20h ↔ breakout_dist_20h**: HIGH_REDUNDANCY (|ρ| = 0.865)
- **q158_qtlu_20h ↔ rsi_14h**: HIGH_REDUNDANCY (|ρ| = 0.864)
- **q158_qtld_20h ↔ rsi_14h**: HIGH_REDUNDANCY (|ρ| = 0.861)
- **q158_qtlu_20h ↔ q158_rsv_20h**: HIGH_REDUNDANCY (|ρ| = 0.858)
- **q158_qtld_20h ↔ q158_rsv_20h**: HIGH_REDUNDANCY (|ρ| = 0.857)
- **q158_qtld_20h ↔ breakout_dist_20h**: HIGH_REDUNDANCY (|ρ| = 0.850)

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
