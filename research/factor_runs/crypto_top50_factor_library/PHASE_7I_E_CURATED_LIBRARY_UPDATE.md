# Phase 7I-E — Batch-2 Curated Library Update

> Date: 2026-06-14
>
> Status: COMPLETE

---

## A. Scope

- Phase: 7I-E
- Batch-2 curated update into factor library v0.3
- Combined curated library: 27 Batch-1 + 9 Batch-2 = 36 factors
- No build/eval/classification/redundancy/backtest

---

## B. Batch-2 Curated Summary

- Batch-2 factor count: 9
- All registry_status: DIAGNOSTIC_PROBE

### Tier Distribution

| Tier | Count | Factors |
|------|-------|---------|
| TIER_1_STABLE_DIAGNOSTIC | 4 | rsi_7h, rsi_28h, downside_vol_20h, vol_of_vol_20h |
| TIER_2_PROMISING_BUT_NEEDS_REVIEW | 3 | ema_12_26_gap, williams_r_14h, mom_accel_20h |
| TIER_4_UNSTABLE_OR_SIGN_FLIP | 2 | qvol_ma_ratio_5_20, ma_gap_20_80 |

### recommended_research_use

| Use | Count |
|-----|-------|
| CORE_DIAGNOSTIC_CANDIDATE | 4 |
| REVIEW_DIRECTION_OR_FORMULA | 3 |
| LOW_PRIORITY_RESEARCH | 2 |

### redundancy_role

| Role | Count | Factors |
|------|-------|---------|
| NOT_IN_REDUNDANCY_GROUP | 5 | rsi_7h, downside_vol_20h, vol_of_vol_20h, mom_accel_20h, ma_gap_20_80 |
| REPRESENTATIVE_CANDIDATE | 2 | ema_12_26_gap, rsi_7h (wait — rsi_7h is in RG_B2_2) |
| REDUNDANT_GROUP_MEMBER | 2 | rsi_28h, williams_r_14h |

---

## C. Combined v0.3 Summary

- Total factors: 36
- Batch-1: 27
- Batch-2: 9
- Families: 13

### Tier Distribution (combined)

| Tier | Count |
|------|-------|
| TIER_1_STABLE_DIAGNOSTIC | 11 |
| TIER_2_PROMISING_BUT_NEEDS_REVIEW | 15 |
| TIER_3_WEAK_DIAGNOSTIC | 3 |
| TIER_4_UNSTABLE_OR_SIGN_FLIP | 7 |

### Redundancy Groups

- Batch-1: 6 groups
- Batch-2: 2 groups
- Total: 8 groups

---

## D. Key Observations

1. **Batch-2 added 2 new families**: technical_indicators (4 factors) and realized_skew_kurtosis (2 factors).
2. **Batch-2 TIER_1 factors** (4): downside_vol_20h, vol_of_vol_20h, rsi_7h, rsi_28h — all with stable static/dynamic sign consistency.
3. **Batch-2 redundancy** concentrated in technical_indicators: ema_12_26_gap↔rsi_28h (HIGH), rsi_7h↔williams_r_14h (HIGH).
4. **Batch-2 sign-flip factors** (TIER_4): qvol_ma_ratio_5_20, ma_gap_20_80 — static and dynamic RankIC disagree on sign.
5. **Combined library** now has 36 factors across 13 families, all diagnostic-only.

---

## E. Required Negative Declarations

No factor_values were built.
No static evaluation was run.
No dynamic evaluation was run.
No static-vs-dynamic comparison was rerun.
No diagnostic classification was rerun.
No redundancy analysis was rerun.
No strategy backtest was run.
No portfolio simulation was run.
No Qlib / VectorBT / Backtrader integration was run.
No Alphalens tear sheet was run.
No factor status was upgraded to CANDIDATE_REVIEW.
No alpha claim was made.
No factor was removed or selected for trading.

---

## F. Phase 7J Readiness

- ✓ Batch-2 curated file has 9 rows
- ✓ Combined v0.3 library has 36 rows
- ✓ Family summary exists (13 families)
- ✓ Redundancy review queue exists (8 groups)
- ✓ Docs index and roadmap updated
- ✓ No alpha/status promotion occurred
- ✓ No factor removal occurred

Phase 7J Batch-3 planning is allowed pending PM review.
