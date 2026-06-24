# Factor Intake Report: a101_cap_unblocked_1h_equivalent

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-24T03:08:42.264881+00:00
**Factors evaluated:** 2
**Factor IDs:** a101_volume_cap_alpha_min_80_80, a101_volume_cap_alpha_min_56_84

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| a101_volume_cap_alpha_min_80_80 | alpha101_curated_volume_cap_regression | conditional | 159 | True |
| a101_volume_cap_alpha_min_56_84 | alpha101_curated_volume_cap_regression | conditional | 139 | True |

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
| a101_volume_cap_alpha_min_80_80 | +0.058173 | 72h | +0.4486 | +0.001275 | 4.33 | CONSISTENT | CONDITIONAL_DIRECTION_REVIEW |
| a101_volume_cap_alpha_min_56_84 | +0.057475 | 72h | +0.4232 | +0.002218 | 7.75 | CONSISTENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### a101_volume_cap_alpha_min_80_80

- **Family:** alpha101_curated_volume_cap_regression
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** +0.058173
- **Best LS t-stat:** 4.33
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (2 sign changes)
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** a101_volume_cap_alpha_min_56_84 (|ρ|=0.870, HIGH_REDUNDANCY); range_24h (|ρ|=0.139, LOW_REDUNDANCY); range_4h (|ρ|=0.122, LOW_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: HIGH_REDUNDANCY. Consider dropping one factor.

### a101_volume_cap_alpha_min_56_84

- **Family:** alpha101_curated_volume_cap_regression
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** +0.057475
- **Best LS t-stat:** 7.75
- **Monthly stability:** STABLE (23/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (2 sign changes)
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** a101_volume_cap_alpha_min_80_80 (|ρ|=0.870, HIGH_REDUNDANCY); range_24h (|ρ|=0.133, LOW_REDUNDANCY); range_4h (|ρ|=0.122, LOW_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: HIGH_REDUNDANCY. Consider dropping one factor.

## Redundancy Warnings

- **a101_volume_cap_alpha_min_80_80 ↔ a101_volume_cap_alpha_min_56_84**: HIGH_REDUNDANCY (|ρ| = 0.870)

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
