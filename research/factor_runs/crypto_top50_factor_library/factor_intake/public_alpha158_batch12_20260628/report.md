# Factor Intake Report: public_alpha158_batch12_20260628

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-28T05:54:41.242640+00:00
**Factors evaluated:** 4
**Factor IDs:** q158_ma_10h, q158_std_10h, q158_max_10h, q158_min_10h

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| q158_ma_10h | alpha158_rolling_price | conditional | 10 | False |
| q158_std_10h | alpha158_rolling_price | negative | 10 | False |
| q158_max_10h | alpha158_rolling_price | conditional | 10 | False |
| q158_min_10h | alpha158_rolling_price | conditional | 10 | False |

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
| q158_ma_10h | +0.035448 | 4h | +0.2174 | -0.003232 | -8.64 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_std_10h | +0.080886 | 72h | +0.4399 | -0.004933 | -11.72 | DIVERGENT | DIRECTION_REVIEW_REQUIRED |
| q158_max_10h | -0.062742 | 72h | -0.3657 | +0.002321 | 5.87 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_min_10h | +0.067080 | 72h | +0.4186 | -0.005289 | -13.12 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### q158_ma_10h

- **Family:** alpha158_rolling_price
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.035448
- **Best LS t-stat:** -8.64
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** reversal_5h (|ρ|=0.930, HIGH_REDUNDANCY); mom_5h (|ρ|=0.930, HIGH_REDUNDANCY); q158_open_close_4h (|ρ|=0.891, HIGH_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: HIGH_REDUNDANCY. Consider dropping one factor.

### q158_std_10h

- **Family:** alpha158_rolling_price
- **Expected direction:** negative
- **Best horizon:** 72h
- **Best adj IC:** +0.080886
- **Best LS t-stat:** -11.72
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** vol_5h (|ρ|=0.862, HIGH_REDUNDANCY); q158_std_20h (|ρ|=0.762, MODERATE_REDUNDANCY); q158_std_5h (|ρ|=0.750, MODERATE_REDUNDANCY)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

### q158_max_10h

- **Family:** alpha158_rolling_price
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** -0.062742
- **Best LS t-stat:** 5.87
- **Monthly stability:** UNSTABLE (1/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** MODERATE_REDUNDANCY
- **Nearest existing:** q158_max_5h (|ρ|=0.840, MODERATE_REDUNDANCY); q158_max_20h (|ρ|=0.840, MODERATE_REDUNDANCY); q158_qtlu_20h (|ρ|=0.697, LOW_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### q158_min_10h

- **Family:** alpha158_rolling_price
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** +0.067080
- **Best LS t-stat:** -13.12
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** MODERATE_REDUNDANCY
- **Nearest existing:** q158_min_5h (|ρ|=0.844, MODERATE_REDUNDANCY); q158_min_20h (|ρ|=0.840, MODERATE_REDUNDANCY); q158_klen_open (|ρ|=0.797, MODERATE_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

## Redundancy Warnings

- **q158_ma_10h ↔ reversal_5h**: HIGH_REDUNDANCY (|ρ| = 0.930)
- **q158_ma_10h ↔ mom_5h**: HIGH_REDUNDANCY (|ρ| = 0.930)
- **q158_ma_10h ↔ q158_open_close_4h**: HIGH_REDUNDANCY (|ρ| = 0.891)
- **q158_std_10h ↔ vol_5h**: HIGH_REDUNDANCY (|ρ| = 0.862)
- **q158_ma_10h ↔ q158_rank_close_20h**: HIGH_REDUNDANCY (|ρ| = 0.856)
- **q158_ma_10h ↔ bb_zscore_20h**: HIGH_REDUNDANCY (|ρ| = 0.854)
- **q158_ma_10h ↔ q158_high_close_4h**: HIGH_REDUNDANCY (|ρ| = 0.850)

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
