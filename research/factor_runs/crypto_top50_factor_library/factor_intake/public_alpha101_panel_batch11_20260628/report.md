# Factor Intake Report: public_alpha101_panel_batch11_20260628

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-28T20:26:52.134271+00:00
**Factors evaluated:** 4
**Factor IDs:** wq101_alpha73, wq101_alpha81, wq101_alpha84, wq101_alpha98

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| wq101_alpha73 | wq101 | conditional | 26 | True |
| wq101_alpha81 | wq101 | conditional | 82 | True |
| wq101_alpha84 | wq101 | conditional | 35 | True |
| wq101_alpha98 | wq101 | conditional | 55 | True |

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
| wq101_alpha73 | -0.005964 | 72h | -0.0498 | -0.003040 | -10.19 | CONSISTENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha81 | +0.014868 | 24h | +0.1449 | -0.000600 | -2.19 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha84 | +0.016951 | 4h | +0.1425 | -0.002654 | -8.65 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha98 | -0.002531 | 72h | -0.0175 | +0.001348 | 2.92 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### wq101_alpha73

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** -0.005964
- **Best LS t-stat:** -10.19
- **Monthly stability:** UNSTABLE (7/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha81

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** +0.014868
- **Best LS t-stat:** -2.19
- **Monthly stability:** STABLE (22/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (3 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha84

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.016951
- **Best LS t-stat:** -8.65
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (2 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha98

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** -0.002531
- **Best LS t-stat:** 2.92
- **Monthly stability:** MIXED (10/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (3 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
