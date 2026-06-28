# Factor Intake Report: public_alpha101_panel_batch08_20260628

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-28T17:46:05.601533+00:00
**Factors evaluated:** 10
**Factor IDs:** wq101_alpha1, wq101_alpha2, wq101_alpha3, wq101_alpha4, wq101_alpha5, wq101_alpha7, wq101_alpha8, wq101_alpha10, wq101_alpha11, wq101_alpha13

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| wq101_alpha1 | wq101 | conditional | 25 | True |
| wq101_alpha2 | wq101 | conditional | 8 | True |
| wq101_alpha3 | wq101 | conditional | 10 | True |
| wq101_alpha4 | wq101 | conditional | 9 | True |
| wq101_alpha5 | wq101 | conditional | 10 | True |
| wq101_alpha7 | wq101 | conditional | 67 | True |
| wq101_alpha8 | wq101 | conditional | 15 | True |
| wq101_alpha10 | wq101 | conditional | 5 | True |
| wq101_alpha11 | wq101 | conditional | 4 | True |
| wq101_alpha13 | wq101 | conditional | 5 | True |

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
| wq101_alpha1 | +0.013315 | 4h | +0.1273 | -0.001259 | -4.47 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha2 | +0.014940 | 4h | +0.1803 | -0.000201 | -0.82 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha3 | +0.010163 | 24h | +0.1103 | -0.000422 | -1.66 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha4 | +0.011069 | 4h | +0.1134 | -0.002124 | -7.13 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha5 | +0.020514 | 1h | +0.1742 | -0.000246 | -1.54 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha7 | +0.002218 | 24h | +0.0214 | -0.000463 | -1.65 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha8 | +0.010308 | 1h | +0.0888 | -0.000595 | -1.94 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha10 | +0.011902 | 1h | +0.1075 | +0.000069 | 1.16 | CONSISTENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha11 | +0.007091 | 24h | +0.0579 | -0.000417 | -1.36 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha13 | +0.017241 | 24h | +0.2054 | -0.001133 | -3.88 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### wq101_alpha1

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.013315
- **Best LS t-stat:** -4.47
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (3 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha2

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.014940
- **Best LS t-stat:** -0.82
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (2 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha3

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** +0.010163
- **Best LS t-stat:** -1.66
- **Monthly stability:** STABLE (20/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha4

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.011069
- **Best LS t-stat:** -7.13
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (2 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha5

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.020514
- **Best LS t-stat:** -1.54
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** MONOTONIC_INCREASING
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha7

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** +0.002218
- **Best LS t-stat:** -1.65
- **Monthly stability:** MODERATE (15/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha8

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.010308
- **Best LS t-stat:** -1.94
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (3 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha10

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.011902
- **Best LS t-stat:** 1.16
- **Monthly stability:** STABLE (23/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha11

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** +0.007091
- **Best LS t-stat:** -1.36
- **Monthly stability:** STABLE (23/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha13

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** +0.017241
- **Best LS t-stat:** -3.88
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
