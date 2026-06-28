# Factor Intake Report: public_alpha101_cap_batch12_20260628

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-28T21:28:58.853253+00:00
**Factors evaluated:** 1
**Factor IDs:** wq101_alpha56

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| wq101_alpha56 | wq101 | conditional | 11 | True |

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
| wq101_alpha56 | +0.013335 | 1h | +0.1118 | -0.000411 | -1.36 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### wq101_alpha56

- **Family:** wq101
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.013335
- **Best LS t-stat:** -1.36
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** LOW_REDUNDANCY
- **Nearest existing:** wq101_alpha101 (|ρ|=0.427, LOW_REDUNDANCY); wq101_alpha49 (|ρ|=0.423, LOW_REDUNDANCY); wq101_alpha51 (|ρ|=0.418, LOW_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
