# Factor Intake Report: public_alpha101_panel_batch07_20260628

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-28T16:55:28.346894+00:00
**Factors evaluated:** 10
**Factor IDs:** wq101_alpha77, wq101_alpha78, wq101_alpha83, wq101_alpha85, wq101_alpha86, wq101_alpha88, wq101_alpha92, wq101_alpha94, wq101_alpha95, wq101_alpha99

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| wq101_alpha77 | wq101 | conditional | 47 | True |
| wq101_alpha78 | wq101 | conditional | 65 | True |
| wq101_alpha83 | wq101 | conditional | 7 | True |
| wq101_alpha85 | wq101 | conditional | 39 | True |
| wq101_alpha86 | wq101 | conditional | 58 | True |
| wq101_alpha88 | wq101 | conditional | 95 | True |
| wq101_alpha92 | wq101 | conditional | 49 | True |
| wq101_alpha94 | wq101 | conditional | 82 | True |
| wq101_alpha95 | wq101 | conditional | 81 | True |
| wq101_alpha99 | wq101 | conditional | 87 | True |

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
| wq101_alpha77 | -0.012733 | 72h | -0.1183 | -0.000895 | -3.13 | CONSISTENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha78 | -0.007726 | 72h | -0.0676 | +0.002698 | 8.04 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha83 | +0.023146 | 1h | +0.2018 | -0.000143 | -0.48 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha85 | -0.005769 | 72h | -0.0565 | +0.000969 | 3.42 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha86 | +0.011610 | 1h | +0.1146 | -0.000103 | -0.83 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha88 | +0.032982 | 72h | +0.2670 | -0.002782 | -7.63 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha92 | +0.006586 | 4h | +0.0349 | -0.003352 | -2.82 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha94 | -0.014450 | 72h | -0.1113 | -0.002049 | -7.10 | CONSISTENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha95 | -0.010725 | 72h | -0.1079 | -0.001488 | -6.12 | CONSISTENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha99 | +0.007412 | 24h | +0.0757 | -0.000535 | -2.29 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### wq101_alpha77

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** -0.012733
- **Best LS t-stat:** -3.13
- **Monthly stability:** UNSTABLE (6/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha78

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** -0.007726
- **Best LS t-stat:** 8.04
- **Monthly stability:** UNSTABLE (7/25 months positive)
- **Quantile monotonicity:** MONOTONIC_INCREASING
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha83

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.023146
- **Best LS t-stat:** -0.48
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha85

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** -0.005769
- **Best LS t-stat:** 3.42
- **Monthly stability:** UNSTABLE (5/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha86

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.011610
- **Best LS t-stat:** -0.83
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (2 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha88

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** +0.032982
- **Best LS t-stat:** -7.63
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (2 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha92

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.006586
- **Best LS t-stat:** -2.82
- **Monthly stability:** MODERATE (17/24 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha94

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** -0.014450
- **Best LS t-stat:** -7.10
- **Monthly stability:** UNSTABLE (9/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha95

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** -0.010725
- **Best LS t-stat:** -6.12
- **Monthly stability:** UNSTABLE (4/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (2 sign changes)
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha99

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** +0.007412
- **Best LS t-stat:** -2.29
- **Monthly stability:** STABLE (21/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (3 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
