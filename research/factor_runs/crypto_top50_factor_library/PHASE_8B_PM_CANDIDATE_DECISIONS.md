# Phase 8B Closeout — PM Candidate Review Decisions

> Date: 2026-06-15
> Previous phase: Phase 8A COMPLETE
> PM decision: Approve 10 factors for CANDIDATE_REVIEW
> Human review required for Phase 9 entry: yes

---

## Status

Phase 8B: COMPLETE, pending PM approval for Phase 9 entry.

---

## 1. Scope

Phase 8B applies the explicit PM candidate-review decisions from the Phase 8A
review packet. This phase translates PM decisions into machine-readable status
files. Phase 8B does **not** run backtests, create portfolio simulations, or
make alpha claims.

---

## 2. PM Decision Summary

| Metric | Count |
|--------|-------|
| Total factors | 42 |
| Approved CANDIDATE_REVIEW | 10 |
| Remaining diagnostic / parked | 32 |

### Non-approved breakdown

| pm_decision | Count |
|-------------|-------|
| PARK_DIRECTION_REVIEW | 14 |
| PARK_REDUNDANCY_REVIEW | 10 |
| PARK_WEAK_OR_LOW_PRIORITY | 8 |

---

## 3. Approved CANDIDATE_REVIEW Factors (10)

| factor_id | factor_family | diagnostic_tier | recommended_research_use |
|-----------|---------------|-----------------|--------------------------|
| vol_5h | volatility | TIER_1_STABLE_DIAGNOSTIC | CORE_DIAGNOSTIC_CANDIDATE |
| vol_40h | volatility | TIER_1_STABLE_DIAGNOSTIC | CORE_DIAGNOSTIC_CANDIDATE |
| range_1h | range_position | TIER_1_STABLE_DIAGNOSTIC | CORE_DIAGNOSTIC_CANDIDATE |
| range_4h | range_position | TIER_1_STABLE_DIAGNOSTIC | CORE_DIAGNOSTIC_CANDIDATE |
| price_pos_24h | price_position | TIER_1_STABLE_DIAGNOSTIC | CORE_DIAGNOSTIC_CANDIDATE |
| xs_rank_vol | cross_sectional_normalized | TIER_1_STABLE_DIAGNOSTIC | CORE_DIAGNOSTIC_CANDIDATE |
| rsi_28h | technical_indicators | TIER_1_STABLE_DIAGNOSTIC | CORE_DIAGNOSTIC_CANDIDATE |
| rsi_7h | technical_indicators | TIER_1_STABLE_DIAGNOSTIC | CORE_DIAGNOSTIC_CANDIDATE |
| downside_vol_20h | realized_skew_kurtosis | TIER_1_STABLE_DIAGNOSTIC | CORE_DIAGNOSTIC_CANDIDATE |
| vol_of_vol_20h | realized_skew_kurtosis | TIER_1_STABLE_DIAGNOSTIC | CORE_DIAGNOSTIC_CANDIDATE |


**CANDIDATE_REVIEW is not alpha.** These factors have passed diagnostic screening
and PM review, but no alpha claim, backtest, or tradeable signal exists.

**CANDIDATE_REVIEW is not a tradable signal.** These factors require further
evaluation (multi-factor signal design, portfolio construction, cost/slippage
analysis) before any trading decision.

---

## 4. Non-approved Factors (32)

### PARK_DIRECTION_REVIEW (14 factors)

| factor_id | factor_family | diagnostic_tier |
|-----------|---------------|------------------|
| mom_5h | momentum | TIER_2_PROMISING_BUT_NEEDS_REVIEW |
| mom_40h | momentum | TIER_2_PROMISING_BUT_NEEDS_REVIEW |
| rev_3h | reversal | TIER_2_PROMISING_BUT_NEEDS_REVIEW |
| rev_10h | reversal | TIER_2_PROMISING_BUT_NEEDS_REVIEW |
| rev_24h | reversal | TIER_2_PROMISING_BUT_NEEDS_REVIEW |
| qvol_zscore_48h | quote_volume_liquidity | TIER_4_UNSTABLE_OR_SIGN_FLIP |
| ma_gap_5_20 | trend_ma | TIER_2_PROMISING_BUT_NEEDS_REVIEW |
| breakout_dist_48h | breakout | TIER_2_PROMISING_BUT_NEEDS_REVIEW |
| candle_body | intraday_candle | TIER_2_PROMISING_BUT_NEEDS_REVIEW |
| candle_wick_upper | intraday_candle | TIER_2_PROMISING_BUT_NEEDS_REVIEW |
| xs_rank_ret_1h | cross_sectional_normalized | TIER_2_PROMISING_BUT_NEEDS_REVIEW |
| mom_accel_20h | momentum | TIER_2_PROMISING_BUT_NEEDS_REVIEW |
| taker_buy_ratio_20h | taker_imbalance | TIER_2_PROMISING_BUT_NEEDS_REVIEW |
| funding_rate_level_20h | funding_rate | TIER_3_WEAK_DIAGNOSTIC |

### PARK_REDUNDANCY_REVIEW (10 factors)

| factor_id | factor_family | diagnostic_tier |
|-----------|---------------|------------------|
| mom_10h | momentum | TIER_2_PROMISING_BUT_NEEDS_REVIEW |
| range_24h | range_position | TIER_1_STABLE_DIAGNOSTIC |
| vol_zscore_20h | volume_liquidity | TIER_4_UNSTABLE_OR_SIGN_FLIP |
| vol_zscore_48h | volume_liquidity | TIER_4_UNSTABLE_OR_SIGN_FLIP |
| qvol_zscore_20h | quote_volume_liquidity | TIER_4_UNSTABLE_OR_SIGN_FLIP |
| ma_gap_10_40 | trend_ma | TIER_4_UNSTABLE_OR_SIGN_FLIP |
| breakout_dist_20h | breakout | TIER_2_PROMISING_BUT_NEEDS_REVIEW |
| ema_12_26_gap | technical_indicators | TIER_2_PROMISING_BUT_NEEDS_REVIEW |
| williams_r_14h | technical_indicators | TIER_2_PROMISING_BUT_NEEDS_REVIEW |
| taker_buy_zscore_20h | taker_imbalance | TIER_2_PROMISING_BUT_NEEDS_REVIEW |

### PARK_WEAK_OR_LOW_PRIORITY (8 factors)

| factor_id | factor_family | diagnostic_tier |
|-----------|---------------|------------------|
| vol_ratio_5_20 | volatility | TIER_3_WEAK_DIAGNOSTIC |
| price_pos_72h | price_position | TIER_3_WEAK_DIAGNOSTIC |
| candle_wick_lower | intraday_candle | TIER_3_WEAK_DIAGNOSTIC |
| qvol_ma_ratio_5_20 | quote_volume_liquidity | TIER_4_UNSTABLE_OR_SIGN_FLIP |
| ma_gap_20_80 | trend_ma | TIER_4_UNSTABLE_OR_SIGN_FLIP |
| taker_buy_delta_5h | taker_imbalance | TIER_3_WEAK_DIAGNOSTIC |
| funding_rate_zscore_80h | funding_rate | TIER_3_WEAK_DIAGNOSTIC |
| funding_rate_change_24h | funding_rate | TIER_4_UNSTABLE_OR_SIGN_FLIP |


---

## 5. Negative Declarations

- **CANDIDATE_REVIEW is not alpha.** No alpha claim was made.
- **CANDIDATE_REVIEW is not a tradable signal.** No tradeable signal exists.
- **No strategy backtest was run.** Backtesting starts at Phase 10.
- **No portfolio simulation was run.**
- **No alpha claim was made.**
- **No factor was removed.** All 42 factors remain in the library.
- **Phase 9 has not started.** Multi-factor signal construction requires
  explicit PM approval after Phase 8B review.
- **Phase 10 has not started.** Strategy backtest requires Phase 9 completion.
- **v0.5 is a status-metadata extension of v0.4.** No formulas or evaluations
  were changed.

---

## 6. Deliverables

| Deliverable | File | Description |
|-------------|------|-------------|
| PM decisions | `phase8b_candidate_review_decisions.csv` | 42-row decision file |
| Candidate shortlist | `phase8b_candidate_review_shortlist.csv` | 10 approved factors |
| v0.5 status | `phase8b_factor_library_v0_5_status.csv` | v0.4 + Phase 8B status metadata |
| Non-candidate queue | `phase8b_non_candidate_review_queue.csv` | 32 parked/diagnostic factors |
| Closeout | `PHASE_8B_PM_CANDIDATE_DECISIONS.md` | This document |

---

## 7. Next Required PM Decision

Phase 9 (Multi-factor Signal Construction) may **only** begin after:

1. PM reviews the 10 CANDIDATE_REVIEW factors.
2. PM explicitly approves entry into Phase 9.
3. Phase 9 scope is defined (which factors, which signal construction method).

**No action is taken automatically.** All decisions require explicit PM approval.
