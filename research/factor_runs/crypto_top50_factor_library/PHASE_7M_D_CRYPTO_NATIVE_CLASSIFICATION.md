# Phase 7M-D — Crypto-native Static-vs-Dynamic Comparison & Diagnostic Classification

> Date: 2026-06-14
>
> Status: COMPLETE

---

## A. Scope

- Phase 7M-D: static-vs-dynamic comparison and diagnostic classification
- 6 crypto-native factors only
- No redundancy, no backtest, no alpha promotion
- CSV outputs are canonical source for classification

---

## B. Classification Summary

| factor_id | tier | review_flags |
|-----------|------|-------------|
| taker_buy_ratio_20h | TIER_2_PROMISING_BUT_NEEDS_REVIEW | EXPECTED_DIRECTION_MISMATCH;MULTI_LABEL_INCONSISTENT |
| taker_buy_zscore_20h | TIER_2_PROMISING_BUT_NEEDS_REVIEW | EXPECTED_DIRECTION_MISMATCH |
| taker_buy_delta_5h | TIER_3_WEAK_DIAGNOSTIC | EXPECTED_DIRECTION_MISMATCH |
| funding_rate_level_20h | TIER_3_WEAK_DIAGNOSTIC | EXPECTED_DIRECTION_MISMATCH;STATIC_DYNAMIC_SIGN_MISMATCH;MULTI_LABEL_INCONSISTENT |
| funding_rate_zscore_80h | TIER_3_WEAK_DIAGNOSTIC | EXPECTED_DIRECTION_MISMATCH;WEAK_SIGNAL;MULTI_LABEL_INCONSISTENT |
| funding_rate_change_24h | TIER_4_UNSTABLE_OR_SIGN_FLIP | EXPECTED_DIRECTION_MISMATCH;STATIC_DYNAMIC_SIGN_MISMATCH;WEAK_SIGNAL;MULTI_LABEL_INCONSISTENT |

### Family Summary

| family | n_factors | tier_distribution |
|--------|-----------|-------------------|
| funding_rate | 3 | TIER_3_WEAK_DIAGNOSTIC;TIER_4_UNSTABLE_OR_SIGN_FLIP |
| taker_imbalance | 3 | TIER_2_PROMISING_BUT_NEEDS_REVIEW;TIER_3_WEAK_DIAGNOSTIC |

---

## C. Ret_fwd_1h Comparison (Static vs Dynamic)

Source: `phase7m_d_static_vs_dynamic_comparison_ret_fwd_1h.csv`

| factor_id | static_RankIC | dynamic_RankIC | sign_consistent | expected_dir |
|-----------|---------------|----------------|-----------------|-------------|
| taker_buy_ratio_20h | -0.0124 | -0.0044 | True | positive |
| taker_buy_zscore_20h | -0.0084 | -0.0104 | True | positive |
| taker_buy_delta_5h | -0.0061 | -0.0079 | True | positive |
| funding_rate_level_20h | -0.0050 | 0.0109 | False | negative |
| funding_rate_zscore_80h | 0.0001 | 0.0033 | True | negative |
| funding_rate_change_24h | -0.0003 | 0.0021 | False | negative |

---

## D. Observations

- All 6 factors have `EXPECTED_DIRECTION_MISMATCH`: RankIC signs in static/dynamic do not match expected_direction (positive for taker, negative for funding).
- taker_imbalance factors: RankIC consistently negative across static/dynamic, but expected_direction=positive. This suggests the structural hypothesis may need revision.
- funding_rate_level_20h: static negative / dynamic positive (sign flip), weak signal in both.
- funding_rate_zscore_80h: near-zero static, weak positive dynamic — unstable.
- funding_rate_change_24h: TIER_4 — sign flip + weak signal + multi-label inconsistent.
- Taker factors have better static/dynamic sign consistency but wrong direction vs hypothesis.
- Dynamic universe remains diagnostic and not true PIT.

---

## E. Phase 7M-D Status

**Phase 7M-D is diagnostic classification only.**
No alpha claim.
No factor promotion.
No factor removal.
No backtest.
No trading conclusion.
Dynamic universe remains diagnostic and not true PIT.
CSV outputs are canonical source for classification.

---

## F. Negative Declarations

No factor_values were built.
No labels were rebuilt.
No redundancy analysis was run.
No strategy backtest was run.
No portfolio simulation was run.
No Qlib / VectorBT / Backtrader integration was run.
No Alphalens tear sheet was run.
No factor status was upgraded to CANDIDATE_REVIEW.
No alpha claim was made.
No factor was removed or selected for trading.
