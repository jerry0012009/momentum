# Phase 7E — Diagnostic Factor Classification & Library Curation

> Date: 2026-06-14
>
> Status: COMPLETE

---

## A. Scope

- Phase: 7E
- Factors: 27 selected_for_7B only
- Input artifacts:
  - `phase7c_b_dynamic_eval_summary_ret_fwd_1h.csv`
  - `phase7c_b_dynamic_eval_summary_all_labels.csv`
  - `phase7d_b_static_eval_summary_ret_fwd_1h.csv`
  - `phase7d_b_static_eval_summary_all_labels.csv`
  - `phase7d_b_static_vs_dynamic_comparison_ret_fwd_1h.csv`
  - `phase7d_b_static_vs_dynamic_comparison_all_labels.csv`
  - `factor_mining_candidates_v0_1.csv`
- No new evaluation was run.
- No backtest. No alpha promotion.

---

## B. Tier Summary

| Tier | Count |
|------|-------|
| TIER_1_STABLE_DIAGNOSTIC | 14 |
| TIER_2_PROMISING_BUT_NEEDS_REVIEW | 5 |
| TIER_3_WEAK_DIAGNOSTIC | 3 |
| TIER_4_UNSTABLE_OR_SIGN_FLIP | 5 |

---

## C. High-Turnover Factors (8)

| Factor | Turnover Flag | Max Turnover |
|--------|--------------|--------------|
| vol_zscore_20h | HIGH_TURNOVER | 0.5695 |
| vol_zscore_48h | HIGH_TURNOVER | 0.5198 |
| qvol_zscore_20h | HIGH_TURNOVER | 0.5676 |
| qvol_zscore_48h | HIGH_TURNOVER | 0.5170 |
| candle_body | EXTREME_TURNOVER | 0.7911 |
| candle_wick_upper | EXTREME_TURNOVER | 0.7832 |
| candle_wick_lower | EXTREME_TURNOVER | 0.7853 |
| xs_rank_ret_1h | EXTREME_TURNOVER | 0.7519 |

High turnover is a transaction cost risk flag, not a quality judgment.

---

## D. Sign-Flip Factors (5)

| Factor | Static RankIC | Dynamic RankIC |
|--------|--------------|----------------|
| vol_zscore_20h | +0.0029 | -0.0048 |
| vol_zscore_48h | +0.0019 | -0.0054 |
| qvol_zscore_20h | +0.0028 | -0.0054 |
| qvol_zscore_48h | +0.0021 | -0.0060 |
| ma_gap_10_40 | +0.0006 | -0.0079 |

All sign flips occur in factors with weak absolute RankIC (< 0.01 in at least one regime), suggesting instability rather than regime-dependent signal.

---

## E. Direction Mismatch Factors (16)

Factors where expected_direction does not match static and/or dynamic RankIC sign:

**misaligned_both (both static and dynamic RankIC contradict expected_direction):**
- `mom_5h`, `mom_10h`, `mom_40h` (expected positive, RankIC negative)
- `rev_3h`, `rev_10h`, `rev_24h` (expected negative, RankIC positive — reversal factors showing positive IC)
- `ma_gap_5_20`, `breakout_dist_20h`, `breakout_dist_48h` (expected positive, RankIC negative)
- `candle_wick_upper` (expected negative, RankIC positive)
- `candle_wick_lower` (expected positive, RankIC negative)

**aligned_static_only (dynamic diverges):**
- `vol_zscore_20h`, `vol_zscore_48h`, `qvol_zscore_20h`, `qvol_zscore_48h` (expected positive, static aligned, dynamic negative)
- `ma_gap_10_40` (expected positive, static aligned, dynamic negative)

> Note: Momentum and reversal factors showing RankIC opposite to expected direction suggests the expected_direction in candidate CSV may need review — these are short-horizon crypto effects where traditional momentum/reversal definitions may not apply.

---

## F. Family-Level Observations

| Family | N | T1 | T2 | T3 | T4 | Notes |
|--------|---|----|----|----|----|----|
| range_position | 3 | 3 | 0 | 0 | 0 | All stable diagnostic |
| cross_sectional_normalized | 2 | 2 | 0 | 0 | 0 | Both stable, but extreme turnover |
| momentum | 3 | 2 | 1 | 0 | 0 | Direction mismatch (expected positive, RankIC negative) |
| reversal | 3 | 2 | 1 | 0 | 0 | Direction mismatch (expected negative, RankIC positive) |
| breakout | 2 | 1 | 1 | 0 | 0 | Direction mismatch |
| intraday_candle | 3 | 1 | 1 | 1 | 0 | Mixed; candle_body T3 due to weak RankIC |
| price_position | 2 | 1 | 0 | 1 | 0 | price_pos_72h T3 (weak) |
| volatility | 3 | 2 | 0 | 1 | 0 | vol_5h T3 (weak) |
| trend_ma | 2 | 0 | 1 | 0 | 1 | ma_gap_10_40 sign flip |
| quote_volume_liquidity | 2 | 0 | 0 | 0 | 2 | All T4: sign flips |
| volume_liquidity | 2 | 0 | 0 | 0 | 2 | All T4: sign flips |

**Redundancy note:** Families with 2+ TIER_1 factors (range_position, cross_sectional_normalized, momentum, reversal, volatility) may have within-family correlation — Phase 7F should check.

---

## G. Required Negative Declarations

- No new factor_values were built.
- No static evaluation was run.
- No dynamic evaluation was run.
- No static-vs-dynamic comparison was rerun.
- No strategy backtest was run.
- No portfolio simulation was run.
- No Qlib / VectorBT integration was run.
- No Alphalens tear sheet was run.
- No factor status was upgraded.
- No alpha claim was made.
- No factor was removed or selected for trading.

---

## H. Phase 7F Readiness

- ✓ 27/27 factors classified
- ✓ Family summary generated
- ✓ No alpha promotion
- ✓ All outputs diagnostic only

Phase 7F redundancy / correlation diagnostics is allowed pending PM review.
