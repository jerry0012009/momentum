# Factor Intake Report: public_alpha101_panel_batch10_20260628

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-28T19:33:43.333861+00:00
**Factors evaluated:** 10
**Factor IDs:** wq101_alpha29, wq101_alpha31, wq101_alpha36, wq101_alpha39, wq101_alpha57, wq101_alpha62, wq101_alpha64, wq101_alpha66, wq101_alpha71, wq101_alpha72

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| wq101_alpha29 | wq101 | conditional | 11 | True |
| wq101_alpha31 | wq101 | conditional | 31 | True |
| wq101_alpha36 | wq101 | conditional | 200 | True |
| wq101_alpha39 | wq101 | conditional | 251 | True |
| wq101_alpha57 | wq101 | conditional | 31 | True |
| wq101_alpha62 | wq101 | conditional | 51 | True |
| wq101_alpha64 | wq101 | conditional | 149 | True |
| wq101_alpha66 | wq101 | conditional | 17 | True |
| wq101_alpha71 | wq101 | conditional | 229 | True |
| wq101_alpha72 | wq101 | conditional | 49 | True |

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
| wq101_alpha29 | +0.011685 | 4h | +0.0994 | -0.002688 | -9.14 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha31 | -0.011574 | 72h | -0.1097 | -0.001095 | -4.02 | CONSISTENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha36 | +0.017858 | 24h | +0.1685 | -0.000269 | -1.97 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha39 | +0.018444 | 4h | +0.1495 | -0.003022 | -10.16 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha57 | +0.020796 | 1h | +0.1794 | -0.000369 | -1.22 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha62 | +0.006471 | 4h | +0.0631 | +0.000094 | 0.80 | CONSISTENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha64 | -0.005561 | 72h | -0.0537 | -0.000656 | -2.58 | CONSISTENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha66 | +0.011333 | 4h | +0.1079 | -0.002186 | -7.55 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha71 | +0.005693 | 4h | +0.0528 | -0.000451 | -1.81 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha72 | +0.008159 | 4h | +0.0810 | +0.000420 | 1.70 | CONSISTENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### wq101_alpha29

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.011685
- **Best LS t-stat:** -9.14
- **Monthly stability:** STABLE (22/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (3 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha31

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** -0.011574
- **Best LS t-stat:** -4.02
- **Monthly stability:** UNSTABLE (4/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha36

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** +0.017858
- **Best LS t-stat:** -1.97
- **Monthly stability:** STABLE (23/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (3 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha39

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.018444
- **Best LS t-stat:** -10.16
- **Monthly stability:** STABLE (23/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (3 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha57

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.020796
- **Best LS t-stat:** -1.22
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha62

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.006471
- **Best LS t-stat:** 0.80
- **Monthly stability:** MODERATE (19/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (3 sign changes)
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha64

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** -0.005561
- **Best LS t-stat:** -2.58
- **Monthly stability:** MIXED (11/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (3 sign changes)
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha66

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.011333
- **Best LS t-stat:** -7.55
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (3 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha71

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.005693
- **Best LS t-stat:** -1.81
- **Monthly stability:** MODERATE (19/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha72

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.008159
- **Best LS t-stat:** 1.70
- **Monthly stability:** STABLE (23/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (2 sign changes)
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
