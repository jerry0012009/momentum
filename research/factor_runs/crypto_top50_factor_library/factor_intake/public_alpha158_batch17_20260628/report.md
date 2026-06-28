# Factor Intake Report: public_alpha158_batch17_20260628

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-28T08:43:55.115865+00:00
**Factors evaluated:** 4
**Factor IDs:** q158_cntp_30h, q158_cntn_30h, q158_cntd_30h, q158_sumd_30h

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| q158_cntp_30h | alpha158_rolling_direction | positive | 31 | False |
| q158_cntn_30h | alpha158_rolling_direction | negative | 31 | False |
| q158_cntd_30h | alpha158_rolling_direction | positive | 31 | False |
| q158_sumd_30h | alpha158_rolling_direction | positive | 31 | False |

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
| q158_cntp_30h | -0.008083 | 4h | -0.0706 | +0.003962 | 12.81 | DIVERGENT | TAIL_OR_MONOTONICITY_REVIEW_REQUIRED |
| q158_cntn_30h | -0.005471 | 4h | -0.0463 | +0.004575 | 15.09 | DIVERGENT | TAIL_OR_MONOTONICITY_REVIEW_REQUIRED |
| q158_sumd_30h | -0.024681 | 4h | -0.1726 | +0.005470 | 15.92 | DIVERGENT | DIRECTION_REVIEW_REQUIRED |
| q158_cntd_30h | -0.007254 | 4h | -0.0614 | +0.004352 | 14.28 | DIVERGENT | TAIL_OR_MONOTONICITY_REVIEW_REQUIRED |

## Conclusion Cards

### q158_cntp_30h

- **Family:** alpha158_rolling_direction
- **Expected direction:** positive
- **Best horizon:** 4h
- **Best adj IC:** -0.008083
- **Best LS t-stat:** 12.81
- **Monthly stability:** UNSTABLE (6/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (2 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** NEAR_DUPLICATE
- **Nearest existing:** q158_cntd_30h (|ρ|=0.976, NEAR_DUPLICATE); q158_cntn_30h (|ρ|=0.910, HIGH_REDUNDANCY); q158_cntp_20h (|ρ|=0.804, MODERATE_REDUNDANCY)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

### q158_cntn_30h

- **Family:** alpha158_rolling_direction
- **Expected direction:** negative
- **Best horizon:** 4h
- **Best adj IC:** -0.005471
- **Best LS t-stat:** 15.09
- **Monthly stability:** UNSTABLE (8/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** NEAR_DUPLICATE
- **Nearest existing:** q158_cntd_30h (|ρ|=0.977, NEAR_DUPLICATE); q158_cntp_30h (|ρ|=0.910, HIGH_REDUNDANCY); q158_cntn_20h (|ρ|=0.803, MODERATE_REDUNDANCY)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

### q158_cntd_30h

- **Family:** alpha158_rolling_direction
- **Expected direction:** positive
- **Best horizon:** 4h
- **Best adj IC:** -0.007254
- **Best LS t-stat:** 14.28
- **Monthly stability:** UNSTABLE (7/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** NEAR_DUPLICATE
- **Nearest existing:** q158_cntn_30h (|ρ|=0.977, NEAR_DUPLICATE); q158_cntp_30h (|ρ|=0.976, NEAR_DUPLICATE); q158_cntd_20h (|ρ|=0.798, MODERATE_REDUNDANCY)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

### q158_sumd_30h

- **Family:** alpha158_rolling_direction
- **Expected direction:** positive
- **Best horizon:** 4h
- **Best adj IC:** -0.024681
- **Best LS t-stat:** 15.92
- **Monthly stability:** UNSTABLE (3/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (2 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** q158_ma_60h (|ρ|=0.884, HIGH_REDUNDANCY); ema_12_26_gap (|ρ|=0.880, HIGH_REDUNDANCY); mom_40h (|ρ|=0.795, MODERATE_REDUNDANCY)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

## Redundancy Warnings

- **q158_cntn_30h ↔ q158_cntd_30h**: NEAR_DUPLICATE (|ρ| = 0.977)
- **q158_cntp_30h ↔ q158_cntd_30h**: NEAR_DUPLICATE (|ρ| = 0.976)
- **q158_cntp_30h ↔ q158_cntn_30h**: HIGH_REDUNDANCY (|ρ| = 0.910)
- **q158_sumd_30h ↔ q158_ma_60h**: HIGH_REDUNDANCY (|ρ| = 0.884)
- **q158_sumd_30h ↔ ema_12_26_gap**: HIGH_REDUNDANCY (|ρ| = 0.880)

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
