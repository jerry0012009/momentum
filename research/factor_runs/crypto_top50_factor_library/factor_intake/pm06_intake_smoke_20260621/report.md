# Factor Intake Report: pm06_intake_smoke_20260621

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-21T03:25:57.609849+00:00
**Factors evaluated:** 3
**Factor IDs:** rev_1h, rev_3h, price_volume_corr_20h

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| rev_1h | reversal | positive | 1 | True |
| rev_3h | reversal | positive | 3 | True |
| price_volume_corr_20h | volume_price | conditional | 21 | True |

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
| rev_3h | +0.034385 | 1h | +0.2121 | -0.002109 | -5.78 | DIVERGENT | DIRECTION_REVIEW_REQUIRED |
| rev_1h | +0.036506 | 1h | +0.2300 | -0.001329 | -3.70 | DIVERGENT | DIRECTION_REVIEW_REQUIRED |
| price_volume_corr_20h | -0.040248 | 24h | -0.3481 | +0.002771 | 8.94 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### rev_1h

- **Family:** reversal
- **Expected direction:** positive
- **Best horizon:** 1h
- **Best adj IC:** +0.036506
- **Best LS t-stat:** -3.70
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

### rev_3h

- **Family:** reversal
- **Expected direction:** positive
- **Best horizon:** 1h
- **Best adj IC:** +0.034385
- **Best LS t-stat:** -5.78
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

### price_volume_corr_20h

- **Family:** volume_price
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** -0.040248
- **Best LS t-stat:** 8.94
- **Monthly stability:** UNSTABLE (2/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
