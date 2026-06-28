# Factor Intake Report: public_alpha101_panel_batch09_20260628

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-28T18:33:58.735248+00:00
**Factors evaluated:** 10
**Factor IDs:** wq101_alpha14, wq101_alpha15, wq101_alpha16, wq101_alpha17, wq101_alpha18, wq101_alpha19, wq101_alpha20, wq101_alpha22, wq101_alpha26, wq101_alpha27

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| wq101_alpha14 | wq101 | conditional | 10 | True |
| wq101_alpha15 | wq101 | conditional | 5 | True |
| wq101_alpha16 | wq101 | conditional | 5 | True |
| wq101_alpha17 | wq101 | conditional | 24 | True |
| wq101_alpha18 | wq101 | conditional | 10 | True |
| wq101_alpha19 | wq101 | conditional | 251 | True |
| wq101_alpha20 | wq101 | conditional | 2 | True |
| wq101_alpha22 | wq101 | conditional | 20 | True |
| wq101_alpha26 | wq101 | conditional | 11 | True |
| wq101_alpha27 | wq101 | conditional | 7 | True |

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
| wq101_alpha14 | +0.016729 | 24h | +0.1469 | -0.000955 | -3.24 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha15 | +0.004495 | 72h | +0.0507 | +0.000805 | 3.74 | CONSISTENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha16 | +0.023715 | 24h | +0.2707 | -0.002997 | -10.25 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha17 | +0.021339 | 1h | +0.1815 | +0.000568 | 1.93 | CONSISTENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha18 | -0.008553 | 24h | -0.0714 | -0.001408 | -4.86 | CONSISTENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha19 | +0.016926 | 4h | +0.1234 | -0.002726 | -8.14 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha20 | +0.018098 | 72h | +0.1811 | +0.001190 | 4.61 | CONSISTENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha22 | +0.004244 | 24h | +0.0413 | +0.000126 | 0.92 | CONSISTENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha26 | +0.026428 | 24h | +0.2507 | -0.002385 | -8.17 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha27 | +0.024071 | 24h | +0.1532 | -0.001740 | -3.02 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### wq101_alpha14

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** +0.016729
- **Best LS t-stat:** -3.24
- **Monthly stability:** STABLE (23/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (3 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha15

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** +0.004495
- **Best LS t-stat:** 3.74
- **Monthly stability:** MIXED (13/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (2 sign changes)
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha16

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** +0.023715
- **Best LS t-stat:** -10.25
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (3 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha17

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.021339
- **Best LS t-stat:** 1.93
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** MONOTONIC_INCREASING
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha18

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** -0.008553
- **Best LS t-stat:** -4.86
- **Monthly stability:** UNSTABLE (6/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha19

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.016926
- **Best LS t-stat:** -8.14
- **Monthly stability:** STABLE (23/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (3 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha20

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** +0.018098
- **Best LS t-stat:** 4.61
- **Monthly stability:** STABLE (22/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha22

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** +0.004244
- **Best LS t-stat:** 0.92
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha26

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** +0.026428
- **Best LS t-stat:** -8.17
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha27

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** +0.024071
- **Best LS t-stat:** -3.02
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (3 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
