# Phase 7N-R2 — Queue Category Precedence & Closeout Consistency Patch

> Date: 2026-06-14
>
> Status: COMPLETE

---

## A. Root Cause

`phase7n_r_phase8_review_queue_repaired.csv` had incorrect category precedence:
- `vol_ratio_5_20` was `WEAK_OR_LOW_PRIORITY` but closeout said only `funding_rate_change_24h` was
- `funding_rate_change_24h` was `REVIEW_DIRECTION_FIRST` instead of `WEAK_OR_LOW_PRIORITY`
- `qvol_ma_ratio_5_20` and `ma_gap_20_80` were `REVIEW_DIRECTION_FIRST` instead of `WEAK_OR_LOW_PRIORITY`

---

## B. Precedence Logic (fixed)

1. `PHASE8_READY_FOR_HUMAN_REVIEW` — clean TIER_1 CORE, no bad flags, not redundant
2. `WEAK_OR_LOW_PRIORITY` — WEAK_DIAGNOSTIC_ONLY or LOW_PRIORITY_RESEARCH or TIER_3/4 with weak signal
3. `REDUNDANCY_REVIEW_FIRST` — REDUNDANCY_REVIEW research_use or REDUNDANT_GROUP_MEMBER
4. `REVIEW_DIRECTION_FIRST` — direction mismatch, high turnover, unstable
5. `DIAGNOSTIC_BASELINE_ONLY` — remaining stable baselines

---

## C. Queue Distribution (from CSV)

| Category | Count |
|----------|-------|
| PHASE8_READY_FOR_HUMAN_REVIEW | 10 |
| WEAK_OR_LOW_PRIORITY | 8 |
| REDUNDANCY_REVIEW_FIRST | 10 |
| REVIEW_DIRECTION_FIRST | 14 |

Machine-readable summary: `phase7n_r2_queue_category_summary.csv`

---

## D. Phase 7N-R2 Status

`PHASE8_READY_FOR_HUMAN_REVIEW` is only a review queue label.
It is not CANDIDATE_REVIEW.
No factor was promoted.
No factor entered CANDIDATE_REVIEW.
No alpha claim.
No backtest.
Phase 8 remains pending PM/human decision.

---

## E. Negative Declarations

No factor_values were built.
No labels were rebuilt.
No strategy backtest was run.
No factor status was upgraded.
No alpha claim was made.
