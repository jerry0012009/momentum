# Factor Intake Report: public_alpha158_batch08_20260628

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-28T03:42:53.798164+00:00
**Factors evaluated:** 6
**Factor IDs:** q158_open_close_2h, q158_high_close_2h, q158_low_close_2h, q158_open_close_3h, q158_high_close_3h, q158_low_close_3h

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| q158_open_close_2h | alpha158_price | conditional | 3 | False |
| q158_high_close_2h | alpha158_price | conditional | 3 | False |
| q158_low_close_2h | alpha158_price | conditional | 3 | False |
| q158_open_close_3h | alpha158_price | conditional | 4 | False |
| q158_high_close_3h | alpha158_price | conditional | 4 | False |
| q158_low_close_3h | alpha158_price | conditional | 4 | False |

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
| q158_open_close_2h | +0.034376 | 1h | +0.2121 | -0.002192 | -6.00 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_high_close_2h | +0.022512 | 1h | -0.1333 | +0.000124 | 0.33 | CONSISTENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_low_close_2h | +0.045331 | 4h | +0.2873 | -0.003478 | -9.28 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_open_close_3h | +0.032388 | 1h | +0.2018 | -0.002540 | -6.94 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_high_close_3h | +0.023065 | 1h | +0.1362 | -0.000603 | -1.62 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_low_close_3h | +0.043500 | 4h | +0.2755 | -0.003552 | -9.47 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### q158_open_close_2h

- **Family:** alpha158_price
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.034376
- **Best LS t-stat:** -6.00
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** q158_high_close_2h (|ρ|=0.855, HIGH_REDUNDANCY); q158_low_close_2h (|ρ|=0.854, HIGH_REDUNDANCY); rev_2h (|ρ|=0.763, MODERATE_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: HIGH_REDUNDANCY. Consider dropping one factor.

### q158_high_close_2h

- **Family:** alpha158_price
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.022512
- **Best LS t-stat:** 0.33
- **Monthly stability:** STABLE (22/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** rev_2h (|ρ|=0.858, HIGH_REDUNDANCY); q158_open_close_2h (|ρ|=0.855, HIGH_REDUNDANCY); q158_high_close_1h (|ρ|=0.760, MODERATE_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: HIGH_REDUNDANCY. Consider dropping one factor.

### q158_low_close_2h

- **Family:** alpha158_price
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.045331
- **Best LS t-stat:** -9.28
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** q158_open_close_2h (|ρ|=0.854, HIGH_REDUNDANCY); rev_2h (|ρ|=0.852, HIGH_REDUNDANCY); mom_10h (|ρ|=0.795, MODERATE_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: HIGH_REDUNDANCY. Consider dropping one factor.

### q158_open_close_3h

- **Family:** alpha158_price
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.032388
- **Best LS t-stat:** -6.94
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** q158_high_close_3h (|ρ|=0.886, HIGH_REDUNDANCY); q158_low_close_3h (|ρ|=0.885, HIGH_REDUNDANCY); rev_3h (|ρ|=0.817, MODERATE_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: HIGH_REDUNDANCY. Consider dropping one factor.

### q158_high_close_3h

- **Family:** alpha158_price
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** +0.023065
- **Best LS t-stat:** -1.62
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** rev_3h (|ρ|=0.892, HIGH_REDUNDANCY); q158_open_close_3h (|ρ|=0.886, HIGH_REDUNDANCY); q158_low_close_3h (|ρ|=0.803, MODERATE_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: HIGH_REDUNDANCY. Consider dropping one factor.

### q158_low_close_3h

- **Family:** alpha158_price
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.043500
- **Best LS t-stat:** -9.47
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** rev_3h (|ρ|=0.890, HIGH_REDUNDANCY); q158_open_close_3h (|ρ|=0.885, HIGH_REDUNDANCY); q158_high_close_3h (|ρ|=0.803, MODERATE_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: HIGH_REDUNDANCY. Consider dropping one factor.

## Redundancy Warnings

- **q158_high_close_3h ↔ rev_3h**: HIGH_REDUNDANCY (|ρ| = 0.892)
- **q158_low_close_3h ↔ rev_3h**: HIGH_REDUNDANCY (|ρ| = 0.890)
- **q158_open_close_3h ↔ q158_high_close_3h**: HIGH_REDUNDANCY (|ρ| = 0.886)
- **q158_open_close_3h ↔ q158_low_close_3h**: HIGH_REDUNDANCY (|ρ| = 0.885)
- **q158_high_close_2h ↔ rev_2h**: HIGH_REDUNDANCY (|ρ| = 0.858)
- **q158_open_close_2h ↔ q158_high_close_2h**: HIGH_REDUNDANCY (|ρ| = 0.855)
- **q158_open_close_2h ↔ q158_low_close_2h**: HIGH_REDUNDANCY (|ρ| = 0.854)
- **q158_low_close_2h ↔ rev_2h**: HIGH_REDUNDANCY (|ρ| = 0.852)

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
