# Factor Intake Report: public_alpha101_panel_batch05_20260628

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-28T15:16:45.178582+00:00
**Factors evaluated:** 6
**Factor IDs:** wq101_alpha25, wq101_alpha28, wq101_alpha30, wq101_alpha35, wq101_alpha43, wq101_alpha52

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| wq101_alpha25 | wq101 | conditional | 20 | True |
| wq101_alpha28 | wq101 | conditional | 24 | True |
| wq101_alpha30 | wq101 | conditional | 20 | True |
| wq101_alpha35 | wq101 | conditional | 33 | True |
| wq101_alpha43 | wq101 | conditional | 39 | True |
| wq101_alpha52 | wq101 | conditional | 241 | True |

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
| wq101_alpha25 | +0.019627 | 1h | +0.1656 | -0.001281 | -4.16 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha28 | -0.015551 | 24h | -0.1401 | +0.001030 | 3.55 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha30 | +0.015163 | 1h | +0.1367 | -0.001609 | -5.47 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha35 | +0.026088 | 1h | +0.2149 | -0.002038 | -6.56 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha43 | +0.009322 | 1h | +0.0857 | -0.000335 | -1.16 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| wq101_alpha52 | +0.009118 | 4h | +0.0726 | -0.001823 | -6.02 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### wq101_alpha25

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.019627
- **Best LS t-stat:** -4.16
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha28

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** -0.015551
- **Best LS t-stat:** 3.55
- **Monthly stability:** UNSTABLE (1/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha30

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.015163
- **Best LS t-stat:** -5.47
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha35

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.026088
- **Best LS t-stat:** -6.56
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha43

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.009322
- **Best LS t-stat:** -1.16
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### wq101_alpha52

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.009118
- **Best LS t-stat:** -6.02
- **Monthly stability:** MODERATE (19/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (3 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** UNKNOWN
- **Nearest existing:** nan
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
