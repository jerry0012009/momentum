# Phase 7G — Factor Library Curation / Documentation Consolidation

> Date: 2026-06-14
>
> Status: COMPLETE

---

## A. Scope

- Phase: 7G
- Factors: 27 selected_for_7B only
- Inputs: Phase 7C-B build summaries, Phase 7D-B static eval + comparison, Phase 7E classification, Phase 7F redundancy groups
- No new build/evaluation/redundancy computation

---

## B. Curated Library Summary

Total factors: **27**

### By recommended_research_use

| recommended_research_use | Count |
|--------------------------|-------|
| CORE_DIAGNOSTIC_CANDIDATE | 6 |
| REVIEW_DIRECTION_OR_FORMULA | 16 |
| MONITOR_TURNOVER_RISK | 2 |
| WEAK_DIAGNOSTIC_ONLY | 1 |
| REDUNDANCY_REVIEW | 2 |

### By diagnostic_tier

| Tier | Count |
|------|-------|
| TIER_1_STABLE_DIAGNOSTIC | 7 |
| TIER_2_PROMISING_BUT_NEEDS_REVIEW | 12 |
| TIER_3_WEAK_DIAGNOSTIC | 3 |
| TIER_4_UNSTABLE_OR_SIGN_FLIP | 5 |

### By redundancy_role

| Role | Count |
|------|-------|
| NOT_IN_REDUNDANCY_GROUP | 13 |
| REPRESENTATIVE_CANDIDATE | 6 |
| REDUNDANT_GROUP_MEMBER | 8 |

---

## C. Family Summary

| Family | N | Core | Review Dir | Monitor To | Weak | Redundancy | RG groups |
|--------|---|------|-----------|-----------|------|-----------|-----------|
| breakout | 2 | 0 | 2 | 0 | 0 | 0 | 1 |
| cross_sectional_normalized | 2 | 2 | 0 | 0 | 0 | 0 | 0 |
| intraday_candle | 3 | 0 | 0 | 2 | 1 | 0 | 0 |
| momentum | 3 | 0 | 3 | 0 | 0 | 0 | 1 |
| price_position | 2 | 1 | 1 | 0 | 0 | 0 | 1 |
| quote_volume_liquidity | 2 | 0 | 0 | 0 | 0 | 2 | 1 |
| range_position | 3 | 3 | 0 | 0 | 0 | 0 | 1 |
| reversal | 3 | 0 | 3 | 0 | 0 | 0 | 1 |
| trend_ma | 2 | 0 | 2 | 0 | 0 | 0 | 1 |
| volatility | 3 | 0 | 3 | 0 | 0 | 0 | 1 |
| volume_liquidity | 2 | 0 | 2 | 0 | 0 | 0 | 1 |

---

## D. Redundancy Review Queue

| group_id | factors | families | representative | max_corr_s | max_corr_d | recommended_review |
|----------|---------|----------|---------------|-----------|-----------|-------------------|
| RG1 | breakout_dist_20h; price_pos_24h | breakout; price_position | price_pos_24h | 0.9665 | 0.9507 | REVIEW_DUPLICATE_FORMULAS |
| RG2 | breakout_dist_48h; price_pos_72h | breakout; price_position | breakout_dist_48h | 0.9119 | 0.8912 | REVIEW_CROSS_FAMILY_EQUIVALENCE |
| RG3 | ma_gap_10_40; rev_24h | trend_ma; reversal | rev_24h | 0.8503 | 0.8590 | REVIEW_CROSS_FAMILY_EQUIVALENCE |
| RG4 | mom_10h; rev_10h | momentum; reversal | rev_10h | 1.0000 | 1.0000 | REVIEW_DUPLICATE_FORMULAS |
| RG5 | qvol_zscore_20h; qvol_zscore_48h; vol_zscore_20h; vol_zscore_48h | quote_volume_liquidity; volume_liquidity | qvol_zscore_48h | 0.9983 | 0.9982 | REVIEW_DUPLICATE_FORMULAS |
| RG6 | range_24h; vol_40h | range_position; volatility | vol_40h | 0.8591 | 0.8180 | REVIEW_CROSS_FAMILY_EQUIVALENCE |

---

## E. Risk Flags

### Direction mismatch (16 factors)
mom_5h, mom_10h, mom_40h, rev_3h, rev_10h, rev_24h, ma_gap_5_20, ma_gap_10_40, breakout_dist_20h, breakout_dist_48h, candle_wick_upper, candle_wick_lower, vol_zscore_20h, vol_zscore_48h, qvol_zscore_20h, qvol_zscore_48h

### High/extreme turnover (8 factors)
vol_zscore_20h, vol_zscore_48h, qvol_zscore_20h, qvol_zscore_48h, candle_body, candle_wick_upper, candle_wick_lower, xs_rank_ret_1h

### Weak diagnostic (3 factors)
candle_body (T3), vol_ratio_5_20 (T3), price_pos_72h (T3)

### Sign flip / unstable (5 factors)
vol_zscore_20h, vol_zscore_48h, qvol_zscore_20h, qvol_zscore_48h, ma_gap_10_40

### Near-duplicate groups (3 groups)
RG1 (breakout_dist_20h ≈ price_pos_24h), RG4 (mom_10h ≈ -rev_10h), RG5 (vol/qvol zscore cluster)

---

## F. Required Negative Declarations

- No new factor_values were built.
- No static evaluation was run.
- No dynamic evaluation was run.
- No static-vs-dynamic comparison was rerun.
- No redundancy analysis was rerun.
- No strategy backtest was run.
- No portfolio simulation was run.
- No Qlib / VectorBT integration was run.
- No Alphalens tear sheet was run.
- No factor status was upgraded.
- No alpha claim was made.
- No factor was removed or selected for trading.

---

## G. Phase 7H Readiness

- ✓ Curated factor library CSV has exactly 27 rows
- ✓ All factors remain diagnostic only (DIAGNOSTIC_PROBE)
- ✓ No alpha/status promotion
- ✓ No factor removal
- ✓ Documentation index and roadmap updated

Phase 7H Batch-2 factor mining preparation is allowed pending PM review.
