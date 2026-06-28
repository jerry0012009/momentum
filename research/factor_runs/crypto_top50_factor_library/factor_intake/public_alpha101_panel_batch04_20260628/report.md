# Factor Intake Report: public_alpha101_panel_batch04_20260628

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-28T14:31:47.365631+00:00
**Factors evaluated:** 6
**Factor IDs:** wq101_alpha34, wq101_alpha40, wq101_alpha42, wq101_alpha50, wq101_alpha55, wq101_alpha60

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| wq101_alpha34 | wq101 | conditional | 6 | True |
| wq101_alpha40 | wq101 | conditional | 10 | True |
| wq101_alpha42 | wq101 | conditional | 1 | True |
| wq101_alpha50 | wq101 | conditional | 9 | True |
| wq101_alpha55 | wq101 | conditional | 17 | True |
| wq101_alpha60 | wq101 | conditional | 10 | True |

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
| wq101_alpha34 | +0.015234 | 1h | +0.1374 | -0.000837 | -3.08 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha40 | +0.025420 | 24h | +0.2202 | -0.002548 | -8.34 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha42 | -0.026725 | 72h | -0.1893 | -0.000362 | -1.22 | CONSISTENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha50 | +0.033995 | 72h | +0.2540 | -0.002117 | -6.91 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha55 | +0.018497 | 24h | +0.2234 | -0.000357 | -1.46 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha60 | +0.027581 | 1h | +0.2027 | -0.001950 | -6.11 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### wq101_alpha34

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.015234
- **Best LS t-stat:** -3.08
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha40

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** +0.025420
- **Best LS t-stat:** -8.34
- **Monthly stability:** STABLE (22/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha42

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** -0.026725
- **Best LS t-stat:** -1.22
- **Monthly stability:** UNSTABLE (6/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha50

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** +0.033995
- **Best LS t-stat:** -6.91
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha55

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** +0.018497
- **Best LS t-stat:** -1.46
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha60

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.027581
- **Best LS t-stat:** -6.11
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
