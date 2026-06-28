# Factor Intake Report: public_alpha158_batch13_20260628

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-28T06:24:16.336426+00:00
**Factors evaluated:** 4
**Factor IDs:** q158_ma_30h, q158_std_30h, q158_max_30h, q158_min_30h

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| q158_ma_30h | alpha158_rolling_price | conditional | 30 | False |
| q158_std_30h | alpha158_rolling_price | negative | 30 | False |
| q158_max_30h | alpha158_rolling_price | conditional | 30 | False |
| q158_min_30h | alpha158_rolling_price | conditional | 30 | False |

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
| q158_ma_30h | +0.034802 | 4h | +0.2071 | -0.004802 | -12.73 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_std_30h | +0.082825 | 72h | +0.4364 | -0.004095 | -9.51 | DIVERGENT | DIRECTION_REVIEW_REQUIRED |
| q158_max_30h | -0.063023 | 72h | -0.3519 | +0.000807 | 3.74 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_min_30h | +0.068910 | 72h | +0.4333 | -0.006008 | -14.97 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### q158_ma_30h

- **Family:** alpha158_rolling_price
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.034802
- **Best LS t-stat:** -12.73
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (2 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** rsi_14h (|ρ|=0.944, HIGH_REDUNDANCY); q158_ma_20h (|ρ|=0.926, HIGH_REDUNDANCY); rev_24h (|ρ|=0.905, HIGH_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: HIGH_REDUNDANCY. Consider dropping one factor.

### q158_std_30h

- **Family:** alpha158_rolling_price
- **Expected direction:** negative
- **Best horizon:** 72h
- **Best adj IC:** +0.082825
- **Best LS t-stat:** -9.51
- **Monthly stability:** STABLE (23/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** q158_std_20h (|ρ|=0.873, HIGH_REDUNDANCY); mom_20h (|ρ|=0.754, MODERATE_REDUNDANCY); q158_roc_20h (|ρ|=0.754, MODERATE_REDUNDANCY)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

### q158_max_30h

- **Family:** alpha158_rolling_price
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** -0.063023
- **Best LS t-stat:** 3.74
- **Monthly stability:** UNSTABLE (1/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** q158_max_20h (|ρ|=0.912, HIGH_REDUNDANCY); q158_qtlu_20h (|ρ|=0.762, MODERATE_REDUNDANCY); downside_vol_20h (|ρ|=0.754, MODERATE_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: HIGH_REDUNDANCY. Consider dropping one factor.

### q158_min_30h

- **Family:** alpha158_rolling_price
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** +0.068910
- **Best LS t-stat:** -14.97
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** q158_min_20h (|ρ|=0.911, HIGH_REDUNDANCY); ema_12_26_gap (|ρ|=0.835, MODERATE_REDUNDANCY); mom_20h (|ρ|=0.824, MODERATE_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: HIGH_REDUNDANCY. Consider dropping one factor.

## Redundancy Warnings

- **q158_ma_30h ↔ rsi_14h**: HIGH_REDUNDANCY (|ρ| = 0.944)
- **q158_ma_30h ↔ q158_ma_20h**: HIGH_REDUNDANCY (|ρ| = 0.926)
- **q158_max_30h ↔ q158_max_20h**: HIGH_REDUNDANCY (|ρ| = 0.912)
- **q158_min_30h ↔ q158_min_20h**: HIGH_REDUNDANCY (|ρ| = 0.911)
- **q158_ma_30h ↔ rev_24h**: HIGH_REDUNDANCY (|ρ| = 0.905)
- **q158_ma_30h ↔ q158_roc_20h**: HIGH_REDUNDANCY (|ρ| = 0.884)
- **q158_ma_30h ↔ mom_20h**: HIGH_REDUNDANCY (|ρ| = 0.884)
- **q158_ma_30h ↔ ma_gap_5_20**: HIGH_REDUNDANCY (|ρ| = 0.874)
- **q158_ma_30h ↔ ema_12_26_gap**: HIGH_REDUNDANCY (|ρ| = 0.874)
- **q158_std_30h ↔ q158_std_20h**: HIGH_REDUNDANCY (|ρ| = 0.873)
- **q158_ma_30h ↔ q158_qtlu_20h**: HIGH_REDUNDANCY (|ρ| = 0.865)
- **q158_ma_30h ↔ vwap_dev_20h**: HIGH_REDUNDANCY (|ρ| = 0.864)
- **q158_ma_30h ↔ bb_zscore_20h**: HIGH_REDUNDANCY (|ρ| = 0.860)
- **q158_ma_30h ↔ q158_beta_20h**: HIGH_REDUNDANCY (|ρ| = 0.856)
- **q158_ma_30h ↔ q158_qtld_20h**: HIGH_REDUNDANCY (|ρ| = 0.853)

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
