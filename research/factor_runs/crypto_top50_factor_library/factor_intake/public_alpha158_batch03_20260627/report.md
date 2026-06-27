# Factor Intake Report: public_alpha158_batch03_20260627

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-27T02:51:39.805581+00:00
**Factors evaluated:** 6
**Factor IDs:** q158_beta_20h, q158_rsqr_20h, q158_resi_20h, q158_imax_20h, q158_imin_20h, q158_imxd_20h

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| q158_beta_20h | alpha158_rolling_regression | conditional | 20 | False |
| q158_rsqr_20h | alpha158_rolling_regression | conditional | 20 | False |
| q158_resi_20h | alpha158_rolling_regression | conditional | 20 | False |
| q158_imax_20h | alpha158_rolling_position | conditional | 20 | False |
| q158_imin_20h | alpha158_rolling_position | conditional | 20 | False |
| q158_imxd_20h | alpha158_rolling_position | conditional | 20 | False |

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
| q158_beta_20h | -0.025228 | 24h | -0.1523 | +0.004202 | 11.10 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_rsqr_20h | +0.004251 | 24h | +0.0338 | +0.000953 | 3.18 | CONSISTENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_resi_20h | -0.030125 | 1h | -0.1897 | +0.001003 | 2.76 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_imax_20h | +0.013076 | 4h | +0.1087 | -0.003724 | -11.95 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_imin_20h | -0.013780 | 24h | -0.1149 | +0.002685 | 8.75 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_imxd_20h | +0.015832 | 4h | +0.1271 | -0.004176 | -12.93 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### q158_beta_20h

- **Family:** alpha158_rolling_regression
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** -0.025228
- **Best LS t-stat:** 11.10
- **Monthly stability:** UNSTABLE (5/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** ma_gap_5_20 (|ρ|=0.923, HIGH_REDUNDANCY); ema_12_26_gap (|ρ|=0.872, HIGH_REDUNDANCY); q158_imxd_20h (|ρ|=0.833, MODERATE_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: HIGH_REDUNDANCY. Consider dropping one factor.

### q158_rsqr_20h

- **Family:** alpha158_rolling_regression
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** +0.004251
- **Best LS t-stat:** 3.18
- **Monthly stability:** MIXED (14/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** CONSISTENT
- **Redundancy:** LOW_REDUNDANCY
- **Nearest existing:** trend_efficiency_24h (|ρ|=0.505, LOW_REDUNDANCY); vol_5h (|ρ|=0.455, LOW_REDUNDANCY); candle_wick_lower (|ρ|=0.455, LOW_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### q158_resi_20h

- **Family:** alpha158_rolling_regression
- **Expected direction:** conditional
- **Best horizon:** 1h
- **Best adj IC:** -0.030125
- **Best LS t-stat:** 2.76
- **Monthly stability:** UNSTABLE (0/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** MODERATE_REDUNDANCY
- **Nearest existing:** mom_5h (|ρ|=0.823, MODERATE_REDUNDANCY); reversal_5h (|ρ|=0.823, MODERATE_REDUNDANCY); q158_kup_open (|ρ|=0.592, LOW_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### q158_imax_20h

- **Family:** alpha158_rolling_position
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.013076
- **Best LS t-stat:** -11.95
- **Monthly stability:** STABLE (21/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (2 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** MODERATE_REDUNDANCY
- **Nearest existing:** q158_imxd_20h (|ρ|=0.840, MODERATE_REDUNDANCY); q158_beta_20h (|ρ|=0.705, MODERATE_REDUNDANCY); ma_gap_5_20 (|ρ|=0.645, LOW_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### q158_imin_20h

- **Family:** alpha158_rolling_position
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** -0.013780
- **Best LS t-stat:** 8.75
- **Monthly stability:** UNSTABLE (5/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (2 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** MODERATE_REDUNDANCY
- **Nearest existing:** q158_imxd_20h (|ρ|=0.843, MODERATE_REDUNDANCY); q158_beta_20h (|ρ|=0.700, MODERATE_REDUNDANCY); ema_12_26_gap (|ρ|=0.669, LOW_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

### q158_imxd_20h

- **Family:** alpha158_rolling_position
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.015832
- **Best LS t-stat:** -12.93
- **Monthly stability:** STABLE (22/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (2 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** MODERATE_REDUNDANCY
- **Nearest existing:** q158_imin_20h (|ρ|=0.843, MODERATE_REDUNDANCY); q158_imax_20h (|ρ|=0.840, MODERATE_REDUNDANCY); q158_beta_20h (|ρ|=0.833, MODERATE_REDUNDANCY)
- **Decision bucket:** CONDITIONAL_DIRECTION_REVIEW
- **Recommended action:** Keep for diagnostic. Do not promote without direction analysis.
- **Caveats:** Conditional direction — no expected sign to adjust IC.

## Redundancy Warnings

- **q158_beta_20h ↔ ma_gap_5_20**: HIGH_REDUNDANCY (|ρ| = 0.923)
- **q158_beta_20h ↔ ema_12_26_gap**: HIGH_REDUNDANCY (|ρ| = 0.872)

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
