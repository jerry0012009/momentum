# Factor Intake Report: public_alpha158_batch15_20260628

**Run status:** ✅ COMPLETE
**Generated:** 2026-06-28T07:33:24.710332+00:00
**Factors evaluated:** 4
**Factor IDs:** q158_rsv_30h, q158_qtlu_30h, q158_qtld_30h, q158_rank_close_30h

---

## Factor Inventory

| factor_id | family | direction | lookback | fv_exists |
|-----------|--------|-----------|----------|-----------|
| q158_rsv_30h | alpha158_rolling | conditional | 30 | False |
| q158_qtlu_30h | alpha158_rolling | conditional | 30 | False |
| q158_qtld_30h | alpha158_rolling | conditional | 30 | False |
| q158_rank_close_30h | alpha158_rolling | conditional | 30 | False |

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
| q158_rsv_30h | -0.020704 | 4h | -0.1474 | +0.004056 | 11.73 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_qtlu_30h | +0.022735 | 4h | +0.1319 | -0.004286 | -11.45 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_qtld_30h | +0.048889 | 24h | +0.3120 | -0.004877 | -12.90 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |
| q158_rank_close_30h | -0.032059 | 4h | -0.2309 | +0.004577 | 13.57 | DIVERGENT | CONDITIONAL_DIRECTION_REVIEW |

## Conclusion Cards

### q158_rsv_30h

- **Family:** alpha158_rolling
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** -0.020704
- **Best LS t-stat:** 11.73
- **Monthly stability:** UNSTABLE (3/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (2 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** q158_rank_close_30h (|ρ|=0.915, HIGH_REDUNDANCY); q158_rsv_20h (|ρ|=0.910, HIGH_REDUNDANCY); rsi_14h (|ρ|=0.910, HIGH_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: HIGH_REDUNDANCY. Consider dropping one factor.

### q158_qtlu_30h

- **Family:** alpha158_rolling
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** +0.022735
- **Best LS t-stat:** -11.45
- **Monthly stability:** STABLE (22/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** q158_ma_30h (|ρ|=0.938, HIGH_REDUNDANCY); q158_qtlu_20h (|ρ|=0.912, HIGH_REDUNDANCY); rsi_14h (|ρ|=0.901, HIGH_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: HIGH_REDUNDANCY. Consider dropping one factor.

### q158_qtld_30h

- **Family:** alpha158_rolling
- **Expected direction:** conditional
- **Best horizon:** 24h
- **Best adj IC:** +0.048889
- **Best LS t-stat:** -12.90
- **Monthly stability:** STABLE (24/25 months positive)
- **Quantile monotonicity:** NEARLY_MONOTONIC
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** q158_ma_30h (|ρ|=0.923, HIGH_REDUNDANCY); q158_qtld_20h (|ρ|=0.914, HIGH_REDUNDANCY); ema_12_26_gap (|ρ|=0.907, HIGH_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: HIGH_REDUNDANCY. Consider dropping one factor.

### q158_rank_close_30h

- **Family:** alpha158_rolling
- **Expected direction:** conditional
- **Best horizon:** 4h
- **Best adj IC:** -0.032059
- **Best LS t-stat:** 13.57
- **Monthly stability:** UNSTABLE (0/25 months positive)
- **Quantile monotonicity:** NON_MONOTONIC (2 sign changes)
- **RankIC-LS consistency:** DIVERGENT
- **Redundancy:** HIGH_REDUNDANCY
- **Nearest existing:** q158_rank_close_20h (|ρ|=0.947, HIGH_REDUNDANCY); rsi_14h (|ρ|=0.944, HIGH_REDUNDANCY); bb_zscore_20h (|ρ|=0.943, HIGH_REDUNDANCY)
- **Decision bucket:** REDUNDANT_WITH_EXISTING
- **Recommended action:** Do not promote. Resolve redundancy first.
- **Caveats:** Redundancy level: HIGH_REDUNDANCY. Consider dropping one factor.

## Redundancy Warnings

- **q158_rank_close_30h ↔ q158_rank_close_20h**: HIGH_REDUNDANCY (|ρ| = 0.947)
- **q158_rank_close_30h ↔ rsi_14h**: HIGH_REDUNDANCY (|ρ| = 0.944)
- **q158_rank_close_30h ↔ bb_zscore_20h**: HIGH_REDUNDANCY (|ρ| = 0.943)
- **q158_qtlu_30h ↔ q158_ma_30h**: HIGH_REDUNDANCY (|ρ| = 0.938)
- **q158_qtld_30h ↔ q158_ma_30h**: HIGH_REDUNDANCY (|ρ| = 0.923)
- **q158_rank_close_30h ↔ q158_ma_30h**: HIGH_REDUNDANCY (|ρ| = 0.919)
- **q158_rsv_30h ↔ q158_rank_close_30h**: HIGH_REDUNDANCY (|ρ| = 0.915)
- **q158_qtld_30h ↔ q158_qtld_20h**: HIGH_REDUNDANCY (|ρ| = 0.914)
- **q158_qtlu_30h ↔ q158_qtlu_20h**: HIGH_REDUNDANCY (|ρ| = 0.912)
- **q158_rsv_30h ↔ q158_rsv_20h**: HIGH_REDUNDANCY (|ρ| = 0.910)
- **q158_rsv_30h ↔ rsi_14h**: HIGH_REDUNDANCY (|ρ| = 0.910)
- **q158_qtld_30h ↔ ema_12_26_gap**: HIGH_REDUNDANCY (|ρ| = 0.907)
- **q158_qtld_30h ↔ q158_rank_close_30h**: HIGH_REDUNDANCY (|ρ| = 0.907)
- **q158_rank_close_30h ↔ q158_ma_20h**: HIGH_REDUNDANCY (|ρ| = 0.906)
- **q158_qtlu_30h ↔ rsi_14h**: HIGH_REDUNDANCY (|ρ| = 0.901)
- **q158_qtld_30h ↔ rsi_14h**: HIGH_REDUNDANCY (|ρ| = 0.901)
- **q158_qtld_30h ↔ q158_roc_20h**: HIGH_REDUNDANCY (|ρ| = 0.899)
- **q158_qtld_30h ↔ mom_20h**: HIGH_REDUNDANCY (|ρ| = 0.899)
- **q158_rsv_30h ↔ q158_ma_30h**: HIGH_REDUNDANCY (|ρ| = 0.894)
- **q158_rsv_30h ↔ breakout_dist_20h**: HIGH_REDUNDANCY (|ρ| = 0.894)
- **q158_rank_close_30h ↔ breakout_dist_20h**: HIGH_REDUNDANCY (|ρ| = 0.892)
- **q158_rank_close_30h ↔ q158_rsv_20h**: HIGH_REDUNDANCY (|ρ| = 0.891)
- **q158_qtlu_30h ↔ q158_ma_20h**: HIGH_REDUNDANCY (|ρ| = 0.888)
- **q158_qtlu_30h ↔ q158_rank_close_30h**: HIGH_REDUNDANCY (|ρ| = 0.885)
- **q158_rank_close_30h ↔ q158_qtld_20h**: HIGH_REDUNDANCY (|ρ| = 0.882)
- **q158_qtld_30h ↔ q158_ma_20h**: HIGH_REDUNDANCY (|ρ| = 0.880)
- **q158_rank_close_30h ↔ vwap_dev_20h**: HIGH_REDUNDANCY (|ρ| = 0.867)
- **q158_rank_close_30h ↔ q158_qtlu_20h**: HIGH_REDUNDANCY (|ρ| = 0.867)
- **q158_rsv_30h ↔ q158_qtld_30h**: HIGH_REDUNDANCY (|ρ| = 0.857)
- **q158_rsv_30h ↔ q158_qtlu_30h**: HIGH_REDUNDANCY (|ρ| = 0.856)
- **q158_rsv_30h ↔ bb_zscore_20h**: HIGH_REDUNDANCY (|ρ| = 0.855)
- **q158_qtld_30h ↔ bb_zscore_20h**: HIGH_REDUNDANCY (|ρ| = 0.854)

---

**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. It is NOT live trading. It is NOT signal promotion. Factors listed here are under research evaluation only.
