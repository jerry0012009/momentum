# Phase 7M-D-R — Crypto-native Classification Repair

> Date: 2026-06-14
>
> Status: COMPLETE

---

## A. Root Cause

`phase7m_d_static_vs_dynamic_comparison_all_labels.csv` was previously built by merging only on `factor_id`, causing dynamic ret_fwd_1h values to repeat for ret_fwd_4h / ret_fwd_24h / ret_fwd_72h rows. This invalidated multi-label consistency diagnostics.

## B. Repair

- Rebuilt all-label comparison by merging on `(factor_id, label)` — exact match.
- Verified: `taker_buy_ratio_20h` dynamic RankIC now correctly shows -0.0044 / -0.0031 / 0.0012 / 0.0077 (was all -0.0044).
- Recomputed classification, family summary, review flags from repaired data.
- Tiers unchanged (classification logic was already correct for ret_fwd_1h; multi-label flags correctly re-evaluated).

---

## C. Classification Summary (Repaired)

| factor_id | tier | review_flags |
|-----------|------|-------------|
| taker_buy_ratio_20h | TIER_2_PROMISING_BUT_NEEDS_REVIEW | EXPECTED_DIRECTION_MISMATCH;MULTI_LABEL_INCONSISTENT |
| taker_buy_zscore_20h | TIER_2_PROMISING_BUT_NEEDS_REVIEW | EXPECTED_DIRECTION_MISMATCH |
| taker_buy_delta_5h | TIER_3_WEAK_DIAGNOSTIC | EXPECTED_DIRECTION_MISMATCH |
| funding_rate_level_20h | TIER_3_WEAK_DIAGNOSTIC | EXPECTED_DIRECTION_MISMATCH;STATIC_DYNAMIC_SIGN_MISMATCH;MULTI_LABEL_INCONSISTENT |
| funding_rate_zscore_80h | TIER_3_WEAK_DIAGNOSTIC | EXPECTED_DIRECTION_MISMATCH;WEAK_SIGNAL;MULTI_LABEL_INCONSISTENT |
| funding_rate_change_24h | TIER_4_UNSTABLE_OR_SIGN_FLIP | EXPECTED_DIRECTION_MISMATCH;STATIC_DYNAMIC_SIGN_MISMATCH;WEAK_SIGNAL;MULTI_LABEL_INCONSISTENT |

---

## D. Multi-label RankIC Signs (from repaired data)

| factor_id | static 1h/4h/24h/72h | dynamic 1h/4h/24h/72h |
|-----------|---------------------|----------------------|
| taker_buy_ratio_20h | -/-/+/+ | -/-/+/+ |
| taker_buy_zscore_20h | -/-/-/- | -/-/-/- |
| taker_buy_delta_5h | -/-/-/- | -/-/-/- |
| funding_rate_level_20h | -/-/+/+ | +/+/+/+ |
| funding_rate_zscore_80h | +/-/-/- | +/+/+/+ |
| funding_rate_change_24h | -/+/+/- | +/+/+/+ |

---

## E. Negative Declarations

No factor_values were built.
No labels were rebuilt.
No redundancy analysis was run.
No strategy backtest was run.
No portfolio simulation was run.
No factor status was upgraded to CANDIDATE_REVIEW.
No alpha claim was made.
No factor was removed or selected for trading.

Phase 7M-E is blocked until PM reviews the repaired 7M-D-R commit.
