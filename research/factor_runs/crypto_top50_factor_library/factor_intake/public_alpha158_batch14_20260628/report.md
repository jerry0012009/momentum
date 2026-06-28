# Factor Intake Report: public_alpha158_batch14_20260628

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-28T06:53:56.944369+00:00
**Factors evaluated:** 4
**Factor IDs:** q158_ma_60h, q158_std_60h, q158_max_60h, q158_min_60h

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| q158_ma_60h | alpha158_rolling_price | conditional | 60 | False |
| q158_std_60h | alpha158_rolling_price | negative | 60 | False |
| q158_max_60h | alpha158_rolling_price | conditional | 60 | False |
| q158_min_60h | alpha158_rolling_price | conditional | 60 | False |

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
| q158_ma_60h | +0.034401 | 24h | +0.2005 | -0.005884 | -15.57 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_std_60h | +0.080723 | 72h | +0.4069 | -0.003896 | -8.98 | DIVERGENT | DIRECTION_REVIEW_REQUIRED |
| q158_max_60h | -0.062725 | 72h | -0.3358 | -0.001465 | -3.77 | CONSISTENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_min_60h | +0.067793 | 24h | +0.4349 | -0.006857 | -17.16 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### q158_ma_60h

- **Family:** alpha158_rolling_price
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** +0.034401
- **Best LS t-stat:** -15.57
- **Monthly stability:** STABLE (21/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** NEAR_DUPLICATE
- **Nearest existing:** ema_12_26_gap (|ρ|=0.956, NEAR_DUPLICATE); mom_40h (|ρ|=0.908, HIGH_REDUNDANCY); mom_20h (|ρ|=0.868, HIGH_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: NEAR_DUPLICATE. Consider dropping one factor.

### q158_std_60h

- **Family:** alpha158_rolling_price
- **Expected direction:** negative
- **Best horizon:** 72h
- **Best adj IC:** +0.080723
- **Best LS t-stat:** -8.98
- **Monthly stability:** STABLE (23/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** MODERATE_REDUNDANCY
- **Nearest existing:** vol_40h (|ρ|=0.794, MODERATE_REDUNDANCY); q158_std_30h (|ρ|=0.769, MODERATE_REDUNDANCY); volatility_20h (|ρ|=0.704, MODERATE_REDUNDANCY)
- **Decision bucket:** REVIEW_REQUIRED
- **Recommended action:** Do not promote. Investigate direction semantics.
- **Caveats:** RankIC-longshort divergence. Direction semantics need review.

### q158_max_60h

- **Family:** alpha158_rolling_price
- **Expected direction:** conditional
- **Best horizon:** 72h
- **Best adj IC:** -0.062725
- **Best LS t-stat:** -3.77
- **Monthly stability:** UNSTABLE (1/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** MODERATE_REDUNDANCY
- **Nearest existing:** q158_max_30h (|ρ|=0.833, MODERATE_REDUNDANCY); downside_vol_20h (|ρ|=0.784, MODERATE_REDUNDANCY); q158_max_20h (|ρ|=0.730, MODERATE_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### q158_min_60h

- **Family:** alpha158_rolling_price
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** +0.067793
- **Best LS t-stat:** -17.16
- **Monthly stability:** STABLE (25/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** MODERATE_REDUNDANCY
- **Nearest existing:** q158_min_30h (|ρ|=0.836, MODERATE_REDUNDANCY); ema_12_26_gap (|ρ|=0.738, MODERATE_REDUNDANCY); q158_min_20h (|ρ|=0.736, MODERATE_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

## Redundancy Warnings

- **q158_ma_60h ↔ ema_12_26_gap**: NEAR_DUPLICATE (|ρ| = 0.956)
- **q158_ma_60h ↔ mom_40h**: HIGH_REDUNDANCY (|ρ| = 0.908)
- **q158_ma_60h ↔ mom_20h**: HIGH_REDUNDANCY (|ρ| = 0.868)
- **q158_ma_60h ↔ q158_roc_20h**: HIGH_REDUNDANCY (|ρ| = 0.868)
- **q158_ma_60h ↔ ma_gap_10_40**: HIGH_REDUNDANCY (|ρ| = 0.865)
- **q158_ma_60h ↔ rsi_14h**: HIGH_REDUNDANCY (|ρ| = 0.857)

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
