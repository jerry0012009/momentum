# Factor Intake Report: public_alpha101_panel_batch06_20260628

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-28T15:58:17.754542+00:00
**Factors evaluated:** 6
**Factor IDs:** wq101_alpha47, wq101_alpha61, wq101_alpha65, wq101_alpha68, wq101_alpha74, wq101_alpha75

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| wq101_alpha47 | wq101 | conditional | 20 | True |
| wq101_alpha61 | wq101 | conditional | 197 | True |
| wq101_alpha65 | wq101 | conditional | 73 | True |
| wq101_alpha68 | wq101 | conditional | 37 | True |
| wq101_alpha74 | wq101 | conditional | 80 | True |
| wq101_alpha75 | wq101 | conditional | 61 | True |

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
| wq101_alpha47 | -0.012680 | 72h | -0.1060 | -0.000714 | -2.39 | CONSISTENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha61 | -0.019046 | 72h | -0.1687 | +0.000733 | 2.92 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha65 | -0.013427 | 72h | -0.1228 | +0.000157 | 1.29 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha68 | +0.011326 | 1h | +0.0653 | +0.002401 | 3.39 | CONSISTENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha74 | +0.010451 | 24h | +0.1005 | +0.002291 | 7.53 | CONSISTENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha75 | +0.011269 | 24h | +0.1050 | -0.000917 | -2.94 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### wq101_alpha47

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** -0.012680
- **Best LS t-stat:** -2.39
- **Monthly stability:** UNSTABLE (5/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (3 sign changes)
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha61

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** -0.019046
- **Best LS t-stat:** 2.92
- **Monthly stability:** UNSTABLE (5/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha65

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** -0.013427
- **Best LS t-stat:** 1.29
- **Monthly stability:** UNSTABLE (6/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (3 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha68

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.011326
- **Best LS t-stat:** 3.39
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (2 sign changes)
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha74

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** +0.010451
- **Best LS t-stat:** 7.53
- **Monthly stability:** STABLE (22/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (3 sign changes)
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha75

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** +0.011269
- **Best LS t-stat:** -2.94
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
