# Factor Intake Report: public_alpha158_batch06_20260627

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-27T14:26:23.570432+00:00
**Factors evaluated:** 5
**Factor IDs:** q158_kmid_open, q158_kmid_range, q158_kup_range, q158_klow_range, q158_open_close_0h

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| q158_kmid_open | alpha158_kbar | positive | 1 | False |
| q158_kmid_range | alpha158_kbar | positive | 1 | False |
| q158_kup_range | alpha158_kbar | negative | 1 | False |
| q158_klow_range | alpha158_kbar | positive | 1 | False |
| q158_open_close_0h | alpha158_price | conditional | 1 | False |

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
| q158_kmid_open | -0.036555 | 1h | -0.2303 | +0.001399 | 3.89 | DIVERGENT | DIRECTION_REVIEW_REQUIRED |
| q158_kmid_range | -0.031132 | 1h | -0.2450 | +0.001053 | 3.39 | DIVERGENT | DIRECTION_REVIEW_REQUIRED |
| q158_kup_range | -0.010027 | 1h | -0.0897 | -0.000418 | -1.40 | CONSISTENT | METADATA_REVIEW |
| q158_klow_range | -0.006121 | 1h | -0.0549 | -0.001253 | -4.25 | CONSISTENT | LONGSHORT_STRONG_RANKIC_WEAK |
| q158_open_close_0h | +0.036555 | 1h | +0.2303 | -0.001323 | -3.68 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### q158_kmid_open

- **Family:** alpha158_kbar
- **Expected direction:** positive
- **Best horizon:** 1h
- **Best adj IC:** -0.036555
- **Best LS t-stat:** 3.89
- **Monthly stability:** UNSTABLE (0/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** NEAR_DUPLICATE
- **Nearest existing:** q158_open_close_0h (|ρ|=1.000, NEAR_DUPLICATE); intraday_ret (|ρ|=1.000, NEAR_DUPLICATE); candle_body (|ρ|=0.949, HIGH_REDUNDANCY)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

### q158_kmid_range

- **Family:** alpha158_kbar
- **Expected direction:** positive
- **Best horizon:** 1h
- **Best adj IC:** -0.031132
- **Best LS t-stat:** 3.39
- **Monthly stability:** UNSTABLE (0/25 months positive)
- **Quantile monotonicity:** MONOTONIC_DECREASING
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** NEAR_DUPLICATE
- **Nearest existing:** candle_body (|ρ|=1.000, NEAR_DUPLICATE); q158_kmid_open (|ρ|=0.949, HIGH_REDUNDANCY); intraday_ret (|ρ|=0.949, HIGH_REDUNDANCY)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

### q158_kup_range

- **Family:** alpha158_kbar
- **Expected direction:** negative
- **Best horizon:** 1h
- **Best adj IC:** -0.010027
- **Best LS t-stat:** -1.40
- **Monthly stability:** UNSTABLE (4/25 months positive)
- **Quantile monotonicity:** MONOTONIC_DECREASING
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** NEAR_DUPLICATE
- **Nearest existing:** candle_wick_upper (|ρ|=1.000, NEAR_DUPLICATE); q158_kup_open (|ρ|=0.788, MODERATE_REDUNDANCY); q158_resi_20h (|ρ|=0.436, LOW_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: NEAR_DUPLICATE. Consider dropping one factor.

### q158_klow_range

- **Family:** alpha158_kbar
- **Expected direction:** positive
- **Best horizon:** 1h
- **Best adj IC:** -0.006121
- **Best LS t-stat:** -4.25
- **Monthly stability:** UNSTABLE (4/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** NEAR_DUPLICATE
- **Nearest existing:** candle_wick_lower (|ρ|=1.000, NEAR_DUPLICATE); klow_close (|ρ|=0.767, MODERATE_REDUNDANCY); q158_klow_open (|ρ|=0.767, MODERATE_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: NEAR_DUPLICATE. Consider dropping one factor.

### q158_open_close_0h

- **Family:** alpha158_price
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.036555
- **Best LS t-stat:** -3.68
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** NEAR_DUPLICATE
- **Nearest existing:** q158_kmid_open (|ρ|=1.000, NEAR_DUPLICATE); intraday_ret (|ρ|=1.000, NEAR_DUPLICATE); candle_body (|ρ|=0.949, HIGH_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: NEAR_DUPLICATE. Consider dropping one factor.

## Redundancy Warnings

- **q158_kmid_open ↔ q158_open_close_0h**: NEAR_DUPLICATE (|ρ| = 1.000)
- **q158_kmid_open ↔ intraday_ret**: NEAR_DUPLICATE (|ρ| = 1.000)
- **q158_open_close_0h ↔ intraday_ret**: NEAR_DUPLICATE (|ρ| = 1.000)
- **q158_kmid_range ↔ candle_body**: NEAR_DUPLICATE (|ρ| = 1.000)
- **q158_klow_range ↔ candle_wick_lower**: NEAR_DUPLICATE (|ρ| = 1.000)
- **q158_kup_range ↔ candle_wick_upper**: NEAR_DUPLICATE (|ρ| = 1.000)
- **q158_open_close_0h ↔ candle_body**: HIGH_REDUNDANCY (|ρ| = 0.949)
- **q158_kmid_open ↔ candle_body**: HIGH_REDUNDANCY (|ρ| = 0.949)
- **q158_kmid_open ↔ q158_kmid_range**: HIGH_REDUNDANCY (|ρ| = 0.949)
- **q158_kmid_range ↔ intraday_ret**: HIGH_REDUNDANCY (|ρ| = 0.949)
- **q158_kmid_range ↔ q158_open_close_0h**: HIGH_REDUNDANCY (|ρ| = 0.949)
- **q158_kmid_range ↔ wq101_alpha101**: HIGH_REDUNDANCY (|ρ| = 0.929)
- **q158_kmid_open ↔ wq101_alpha101**: HIGH_REDUNDANCY (|ρ| = 0.911)
- **q158_open_close_0h ↔ wq101_alpha101**: HIGH_REDUNDANCY (|ρ| = 0.911)

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
