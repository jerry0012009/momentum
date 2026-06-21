# Factor Intake Report: pm11b_funding_rate_integration_20260621

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-21T06:58:05.021653+00:00
**Factors evaluated:** 3
**Factor IDs:** funding_rate_level_20h, funding_rate_zscore_80h, funding_rate_change_24h

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| funding_rate_level_20h | funding_rate | negative | 20 | False |
| funding_rate_zscore_80h | funding_rate | negative | 80 | False |
| funding_rate_change_24h | funding_rate | negative | 25 | False |

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
| funding_rate_level_20h | -0.044669 | 72h | -0.4185 | -0.010421 | -30.85 | CONSISTENT | STRONG_DIAGNOSTIC_CANDIDATE |
| funding_rate_zscore_80h | -0.013803 | 24h | -0.1247 | +0.001474 | 4.50 | DIVERGENT | TAIL_OR_MONOTONICITY_REVIEW_REQUIRED |
| funding_rate_change_24h | -0.006731 | 24h | -0.0696 | +0.000390 | 1.28 | DIVERGENT | TAIL_OR_MONOTONICITY_REVIEW_REQUIRED |

## Conclusion Cards

### funding_rate_level_20h

- **Family:** funding_rate
- **Expected direction:** negative
- **Best horizon:** 72h
- **Best adj IC:** -0.044669
- **Best LS t-stat:** -30.85
- **Monthly stability:** UNSTABLE (1/24 months positive)
- **Quantile monotonicity:** MONOTONIC_DECREASING
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** LOW_REDUNDANCY
- **Nearest existing:** mom_120h (|ρ|=0.175, LOW_REDUNDANCY); mom_40h (|ρ|=0.139, LOW_REDUNDANCY); ema_12_26_gap (|ρ|=0.127, LOW_REDUNDANCY)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Monthly IC stability insufficient.
- **Caveats:** Unstable monthly IC. May not generalize.

### funding_rate_zscore_80h

- **Family:** funding_rate
- **Expected direction:** negative
- **Best horizon:** 24h
- **Best adj IC:** -0.013803
- **Best LS t-stat:** 4.50
- **Monthly stability:** UNSTABLE (6/24 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (3 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** LOW_REDUNDANCY
- **Nearest existing:** funding_rate_change_24h (|ρ|=0.649, LOW_REDUNDANCY); price_pos_72h (|ρ|=0.241, LOW_REDUNDANCY); rsi_28h (|ρ|=0.236, LOW_REDUNDANCY)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

### funding_rate_change_24h

- **Family:** funding_rate
- **Expected direction:** negative
- **Best horizon:** 24h
- **Best adj IC:** -0.006731
- **Best LS t-stat:** 1.28
- **Monthly stability:** UNSTABLE (6/24 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (3 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** LOW_REDUNDANCY
- **Nearest existing:** funding_rate_zscore_80h (|ρ|=0.649, LOW_REDUNDANCY); ma_gap_20_80 (|ρ|=0.146, LOW_REDUNDANCY); mom_20h (|ρ|=0.114, LOW_REDUNDANCY)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
