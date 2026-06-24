# Factor Intake Report: pm09_alpha158_batch1_20260621

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-21T04:47:34.895327+00:00
**Factors evaluated:** 6
**Factor IDs:** vwap_dev_20h, wvma_20h, vol_ret_corr_20h, intraday_ret, klow_close, ksft_5h

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| vwap_dev_20h | alpha158_ohlcv | conditional | 20 | False |
| wvma_20h | alpha158_ohlcv | negative | 21 | False |
| vol_ret_corr_20h | alpha158_ohlcv | conditional | 21 | False |
| intraday_ret | alpha158_ohlcv | conditional | 1 | False |
| klow_close | alpha158_ohlcv | positive | 1 | False |
| ksft_5h | alpha158_ohlcv | conditional | 6 | False |

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
| vwap_dev_20h | -0.027278 | 4h | -0.1673 | +0.004258 | 11.29 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wvma_20h | +0.076279 | 72h | +0.4437 | -0.005183 | -13.30 | DIVERGENT | DIRECTION_REVIEW_REQUIRED |
| vol_ret_corr_20h | -0.037671 | 24h | -0.3255 | +0.002159 | 7.11 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| intraday_ret | -0.036555 | 1h | -0.2303 | +0.001399 | 3.89 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| klow_close | -0.054766 | 72h | -0.3716 | +0.002907 | 7.77 | DIVERGENT | DIRECTION_REVIEW_REQUIRED |
| ksft_5h | -0.007409 | 24h | -0.0709 | +0.000291 | 1.05 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### vwap_dev_20h

- **Family:** alpha158_ohlcv
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** -0.027278
- **Best LS t-stat:** 11.29
- **Monthly stability:** UNSTABLE (0/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** breakout_dist_20h (|ρ|=0.918, HIGH_REDUNDANCY); bb_zscore_20h (|ρ|=0.917, HIGH_REDUNDANCY); mom_10h (|ρ|=0.879, HIGH_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: HIGH_REDUNDANCY. Consider dropping one factor.

### wvma_20h

- **Family:** alpha158_ohlcv
- **Expected direction:** negative
- **Best horizon:** 72h
- **Best adj IC:** +0.076279
- **Best LS t-stat:** -13.30
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** volatility_20h (|ρ|=0.892, HIGH_REDUNDANCY); vol_of_vol_20h (|ρ|=0.847, MODERATE_REDUNDANCY); downside_vol_20h (|ρ|=0.812, MODERATE_REDUNDANCY)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

### vol_ret_corr_20h

- **Family:** alpha158_ohlcv
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** -0.037671
- **Best LS t-stat:** 7.11
- **Monthly stability:** UNSTABLE (2/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** price_volume_corr_20h (|ρ|=0.940, HIGH_REDUNDANCY); mom_20h (|ρ|=0.574, LOW_REDUNDANCY); realized_skew_20h (|ρ|=0.570, LOW_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: HIGH_REDUNDANCY. Consider dropping one factor.

### intraday_ret

- **Family:** alpha158_ohlcv
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** -0.036555
- **Best LS t-stat:** 3.89
- **Monthly stability:** UNSTABLE (0/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** candle_body (|ρ|=0.949, HIGH_REDUNDANCY); wq101_alpha101 (|ρ|=0.911, HIGH_REDUNDANCY); mom_5h (|ρ|=0.391, LOW_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: HIGH_REDUNDANCY. Consider dropping one factor.

### klow_close

- **Family:** alpha158_ohlcv
- **Expected direction:** positive
- **Best horizon:** 72h
- **Best adj IC:** -0.054766
- **Best LS t-stat:** 7.77
- **Monthly stability:** UNSTABLE (2/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** MODERATE_REDUNDANCY
- **Nearest existing:** candle_wick_lower (|ρ|=0.767, MODERATE_REDUNDANCY); vol_of_vol_20h (|ρ|=0.470, LOW_REDUNDANCY); range_1h (|ρ|=0.470, LOW_REDUNDANCY)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

### ksft_5h

- **Family:** alpha158_ohlcv
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** -0.007409
- **Best LS t-stat:** 1.05
- **Monthly stability:** UNSTABLE (6/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (3 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** LOW_REDUNDANCY
- **Nearest existing:** qvol_ma_ratio_5_20 (|ρ|=0.381, LOW_REDUNDANCY); realized_skew_20h (|ρ|=0.279, LOW_REDUNDANCY); qvol_zscore_20h (|ρ|=0.203, LOW_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

## Redundancy Warnings

- **intraday_ret ↔ candle_body**: HIGH_REDUNDANCY (|ρ| = 0.949)
- **vol_ret_corr_20h ↔ price_volume_corr_20h**: HIGH_REDUNDANCY (|ρ| = 0.940)
- **vwap_dev_20h ↔ breakout_dist_20h**: HIGH_REDUNDANCY (|ρ| = 0.918)
- **vwap_dev_20h ↔ bb_zscore_20h**: HIGH_REDUNDANCY (|ρ| = 0.917)
- **intraday_ret ↔ wq101_alpha101**: HIGH_REDUNDANCY (|ρ| = 0.911)
- **wvma_20h ↔ volatility_20h**: HIGH_REDUNDANCY (|ρ| = 0.892)
- **vwap_dev_20h ↔ mom_10h**: HIGH_REDUNDANCY (|ρ| = 0.879)
- **vwap_dev_20h ↔ rev_10h**: HIGH_REDUNDANCY (|ρ| = 0.879)
- **vwap_dev_20h ↔ rsi_14h**: HIGH_REDUNDANCY (|ρ| = 0.864)

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
