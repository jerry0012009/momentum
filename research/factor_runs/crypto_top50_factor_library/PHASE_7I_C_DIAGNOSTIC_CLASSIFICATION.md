# Phase 7I-C — Batch-2 Static-vs-Dynamic Comparison & Diagnostic Classification

> Date: 2026-06-14
>
> Status: COMPLETE

---

## A. Scope

- Phase: 7I-C
- 9 PM-approved Batch-2 factors only
- Static-vs-dynamic comparison on ret_fwd_1h and all 4 labels
- Diagnostic classification with tier assignment
- No redundancy, no backtest, no alpha promotion

---

## B. Comparison Summary

- ret_fwd_1h comparison: 9 rows
- All-label comparison: 36 rows (9 factors × 4 labels)

### Stability Buckets (ret_fwd_1h)

| Bucket | Count |
|--------|-------|
| STABLE | 4 |
| MODERATE_SHIFT | 3 |
| SIGN_FLIP | 2 |

### Sign Consistency (ret_fwd_1h)

- Same sign: 7/9
- Sign flip: 2/9 (ema_12_26_gap, qvol_ma_ratio_5_20)

---

## C. Classification Summary

### Tier Distribution

| Tier | Count | Factors |
|------|-------|---------|
| TIER_1_STABLE_DIAGNOSTIC | 4 | rsi_28h, rsi_7h, downside_vol_20h, vol_of_vol_20h |
| TIER_2_PROMISING_BUT_NEEDS_REVIEW | 3 | ema_12_26_gap, williams_r_14h, mom_accel_20h |
| TIER_3_WEAK_DIAGNOSTIC | 0 | — |
| TIER_4_UNSTABLE_OR_SIGN_FLIP | 2 | qvol_ma_ratio_5_20, ma_gap_20_80 |

### recommended_research_use

| Use | Count | Factors |
|-----|-------|---------|
| CORE_DIAGNOSTIC_CANDIDATE | 4 | rsi_28h, rsi_7h, downside_vol_20h, vol_of_vol_20h |
| REVIEW_DIRECTION_OR_FORMULA | 3 | ema_12_26_gap, williams_r_14h, mom_accel_20h |
| MONITOR_TURNOVER_RISK | 0 | — |
| WEAK_DIAGNOSTIC_ONLY | 0 | — |
| LOW_PRIORITY_RESEARCH | 2 | qvol_ma_ratio_5_20, ma_gap_20_80 |

---

## D. Important Observations

1. **Strongest diagnostic factors**: downside_vol_20h (|RankIC|=0.035), vol_of_vol_20h (|RankIC|=0.034) — both TIER_1, low turnover, stable sign.
2. **RSI factors**: rsi_7h and rsi_28h both TIER_1, direction aligned (negative), consistent across horizons.
3. **Direction mismatch — ema_12_26_gap**: expected positive but RankIC negative in both static and dynamic. TIER_2 flagged for direction review.
4. **Direction mismatch — williams_r_14h**: expected negative but RankIC positive in both datasets. Also HIGH_TURNOVER (0.354). TIER_2.
5. **Sign flip — qvol_ma_ratio_5_20**: static RankIC positive, dynamic RankIC negative. TIER_4.
6. **Sign flip — ma_gap_20_80**: static RankIC positive, dynamic RankIC negative. TIER_4.
7. **High turnover**: williams_r_14h (0.354), mom_accel_20h (0.348).
8. **Multi-horizon**: downside_vol_20h and vol_of_vol_20h CONSISTENT_4H (sign consistent across all 4 labels in both datasets).

---

## E. Required Negative Declarations

No factor_values were built.
No static evaluation was run.
No dynamic evaluation was run.
No redundancy analysis was run.
No strategy backtest was run.
No portfolio simulation was run.
No Qlib / VectorBT / Backtrader integration was run.
No Alphalens tear sheet was run.
No factor status was upgraded to CANDIDATE_REVIEW.
No alpha claim was made.
No factor was removed or selected for trading.

---

## F. Phase 7I-D Readiness

- ✓ ret_fwd_1h comparison has 9 rows
- ✓ All-label comparison has 36 rows
- ✓ Classification has 9 rows
- ✓ Family summary exists (5 families)
- ✓ No alpha/status promotion occurred
- ✓ No factor removal occurred

Phase 7I-D Batch-2 redundancy diagnostics is allowed pending PM review.
