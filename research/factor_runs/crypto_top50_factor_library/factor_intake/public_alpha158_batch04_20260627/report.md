# Factor Intake Report: public_alpha158_batch04_20260627

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-27T03:29:39.670649+00:00
**Factors evaluated:** 8
**Factor IDs:** q158_roc_20h, q158_ma_20h, q158_std_20h, q158_max_20h, q158_min_20h, q158_cntd_20h, q158_corr_20h, q158_cord_20h

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| q158_roc_20h | alpha158_rolling_price | conditional | 21 | False |
| q158_ma_20h | alpha158_rolling_price | conditional | 20 | False |
| q158_std_20h | alpha158_rolling_price | negative | 20 | False |
| q158_max_20h | alpha158_rolling_price | conditional | 20 | False |
| q158_min_20h | alpha158_rolling_price | conditional | 20 | False |
| q158_cntd_20h | alpha158_rolling_direction | positive | 21 | False |
| q158_corr_20h | alpha158_rolling_volume_price | conditional | 20 | False |
| q158_cord_20h | alpha158_rolling_volume_price | conditional | 21 | False |

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
| q158_roc_20h | +0.030030 | 4h | +0.1823 | -0.004605 | -12.19 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_ma_20h | +0.034815 | 4h | +0.2100 | -0.004183 | -11.13 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_std_20h | +0.082791 | 72h | +0.4434 | -0.004584 | -10.74 | DIVERGENT | DIRECTION_REVIEW_REQUIRED |
| q158_max_20h | -0.062992 | 72h | -0.3599 | +0.000884 | 2.24 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_min_20h | +0.067445 | 72h | +0.4229 | -0.006099 | -15.08 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_cntd_20h | -0.011199 | 4h | -0.0953 | +0.003979 | 12.79 | DIVERGENT | TAIL_OR_MONOTONICITY_REVIEW_REQUIRED |
| q158_corr_20h | -0.044183 | 24h | -0.3690 | +0.002455 | 7.57 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_cord_20h | -0.039740 | 24h | -0.3433 | +0.002604 | 8.43 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### q158_roc_20h

- **Family:** alpha158_rolling_price
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.030030
- **Best LS t-stat:** -12.19
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (2 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** NEAR_DUPLICATE
- **Nearest existing:** mom_20h (|ρ|=1.000, NEAR_DUPLICATE); q158_sumd_20h (|ρ|=0.963, NEAR_DUPLICATE); mom_vol_adjusted_20h (|ρ|=0.959, NEAR_DUPLICATE)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: NEAR_DUPLICATE. Consider dropping one factor.

### q158_ma_20h

- **Family:** alpha158_rolling_price
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.034815
- **Best LS t-stat:** -11.13
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** NEAR_DUPLICATE
- **Nearest existing:** vwap_dev_20h (|ρ|=0.964, NEAR_DUPLICATE); bb_zscore_20h (|ρ|=0.937, HIGH_REDUNDANCY); q158_qtlu_20h (|ρ|=0.937, HIGH_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: NEAR_DUPLICATE. Consider dropping one factor.

### q158_std_20h

- **Family:** alpha158_rolling_price
- **Expected direction:** negative
- **Best horizon:** 72h
- **Best adj IC:** +0.082791
- **Best LS t-stat:** -10.74
- **Monthly stability:** STABLE (23/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** LOW_REDUNDANCY
- **Nearest existing:** vol_of_vol_20h (|ρ|=0.682, LOW_REDUNDANCY); ema_12_26_gap (|ρ|=0.626, LOW_REDUNDANCY); q158_max_20h (|ρ|=0.610, LOW_REDUNDANCY)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

### q158_max_20h

- **Family:** alpha158_rolling_price
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** -0.062992
- **Best LS t-stat:** 2.24
- **Monthly stability:** UNSTABLE (1/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** MODERATE_REDUNDANCY
- **Nearest existing:** q158_qtlu_20h (|ρ|=0.822, MODERATE_REDUNDANCY); breakout_dist_20h (|ρ|=0.765, MODERATE_REDUNDANCY); q158_rsv_20h (|ρ|=0.749, MODERATE_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### q158_min_20h

- **Family:** alpha158_rolling_price
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** +0.067445
- **Best LS t-stat:** -15.08
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** MODERATE_REDUNDANCY
- **Nearest existing:** q158_qtld_20h (|ρ|=0.815, MODERATE_REDUNDANCY); ema_12_26_gap (|ρ|=0.783, MODERATE_REDUNDANCY); q158_rsv_20h (|ρ|=0.744, MODERATE_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### q158_cntd_20h

- **Family:** alpha158_rolling_direction
- **Expected direction:** positive
- **Best horizon:** 4h
- **Best adj IC:** -0.011199
- **Best LS t-stat:** 12.79
- **Monthly stability:** UNSTABLE (5/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** NEAR_DUPLICATE
- **Nearest existing:** q158_cntn_20h (|ρ|=0.980, NEAR_DUPLICATE); q158_cntp_20h (|ρ|=0.978, NEAR_DUPLICATE); mom_vol_adjusted_20h (|ρ|=0.720, MODERATE_REDUNDANCY)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

### q158_corr_20h

- **Family:** alpha158_rolling_volume_price
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** -0.044183
- **Best LS t-stat:** 7.57
- **Monthly stability:** UNSTABLE (1/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** LOW_REDUNDANCY
- **Nearest existing:** range_breakout_vol_confirm_20h (|ρ|=0.490, LOW_REDUNDANCY); rev_10h (|ρ|=0.459, LOW_REDUNDANCY); mom_10h (|ρ|=0.459, LOW_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### q158_cord_20h

- **Family:** alpha158_rolling_volume_price
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** -0.039740
- **Best LS t-stat:** 8.43
- **Monthly stability:** UNSTABLE (2/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** NEAR_DUPLICATE
- **Nearest existing:** price_volume_corr_20h (|ρ|=0.992, NEAR_DUPLICATE); vol_ret_corr_20h (|ρ|=0.958, NEAR_DUPLICATE); q158_sumd_20h (|ρ|=0.612, LOW_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: NEAR_DUPLICATE. Consider dropping one factor.

## Redundancy Warnings

- **q158_roc_20h ↔ mom_20h**: NEAR_DUPLICATE (|ρ| = 1.000)
- **q158_cord_20h ↔ price_volume_corr_20h**: NEAR_DUPLICATE (|ρ| = 0.992)
- **q158_cntd_20h ↔ q158_cntn_20h**: NEAR_DUPLICATE (|ρ| = 0.980)
- **q158_cntd_20h ↔ q158_cntp_20h**: NEAR_DUPLICATE (|ρ| = 0.978)
- **q158_ma_20h ↔ vwap_dev_20h**: NEAR_DUPLICATE (|ρ| = 0.964)
- **q158_roc_20h ↔ q158_sumd_20h**: NEAR_DUPLICATE (|ρ| = 0.963)
- **q158_roc_20h ↔ mom_vol_adjusted_20h**: NEAR_DUPLICATE (|ρ| = 0.959)
- **q158_cord_20h ↔ vol_ret_corr_20h**: NEAR_DUPLICATE (|ρ| = 0.958)
- **q158_roc_20h ↔ rev_24h**: HIGH_REDUNDANCY (|ρ| = 0.946)
- **q158_ma_20h ↔ bb_zscore_20h**: HIGH_REDUNDANCY (|ρ| = 0.937)
- **q158_ma_20h ↔ q158_qtlu_20h**: HIGH_REDUNDANCY (|ρ| = 0.937)
- **q158_ma_20h ↔ q158_qtld_20h**: HIGH_REDUNDANCY (|ρ| = 0.923)
- **q158_ma_20h ↔ q158_rank_close_20h**: HIGH_REDUNDANCY (|ρ| = 0.918)
- **q158_ma_20h ↔ mom_10h**: HIGH_REDUNDANCY (|ρ| = 0.917)
- **q158_ma_20h ↔ rev_10h**: HIGH_REDUNDANCY (|ρ| = 0.917)
- **q158_ma_20h ↔ rsi_14h**: HIGH_REDUNDANCY (|ρ| = 0.911)
- **q158_ma_20h ↔ breakout_dist_20h**: HIGH_REDUNDANCY (|ρ| = 0.897)
- **q158_ma_20h ↔ q158_rsv_20h**: HIGH_REDUNDANCY (|ρ| = 0.896)
- **q158_ma_20h ↔ ma_gap_5_20**: HIGH_REDUNDANCY (|ρ| = 0.889)

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
