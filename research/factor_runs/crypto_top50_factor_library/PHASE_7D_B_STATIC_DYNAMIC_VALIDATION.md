# Phase 7D-B — Static Evaluation & Static-vs-Dynamic Validation

> Date: 2026-06-14
>
> Status: COMPLETE

---

## A. Scope

- Phase: 7D-B
- Factors: 27 selected_for_7B only
- Static dataset_id: `crypto_top50_usdt_perp_1h`
- Dynamic dataset_id: `crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1`
- Static universe limitation: `static_current_top50, not point-in-time`
- Dynamic universe limitation: `dynamic_from_current_listed_pool, not true PIT`

---

## B. Build Summary

- 27/27 static factor_values built
- All rows: 215,061
- All gate: PASS
- Worst coverage: `price_pos_72h` (98.35%)
- Build summary CSV: `phase7d_b_static_factor_values_build_summary.csv` (27 rows)

---

## C. Static Evaluation Summary

- 27/27 factors evaluated
- All direction_source = `candidate_csv`
- Zero fallback_positive
- Summary CSV: `phase7d_b_static_eval_summary_ret_fwd_1h.csv` (27 rows)
- All-label CSV: `phase7d_b_static_eval_summary_all_labels.csv` (108 rows)

**Highest absolute RankIC (ret_fwd_1h):**
- `xs_rank_ret_1h`: RankIC = -0.0301
- `candle_body`: RankIC = -0.0275
- `rev_3h`: RankIC = +0.0253

**Lowest absolute RankIC (ret_fwd_1h):**
- `vol_zscore_48h`: RankIC = +0.0019
- `mom_40h`: RankIC = -0.0007
- `ma_gap_10_40`: RankIC = +0.0006

---

## D. Static-vs-Dynamic Comparison

Comparison CSV: `phase7d_b_static_vs_dynamic_comparison_ret_fwd_1h.csv` (27 rows)
All-label comparison: `phase7d_b_static_vs_dynamic_comparison_all_labels.csv` (108 rows)

**ret_fwd_1h stability:**

| Bucket | Count |
|--------|-------|
| STABLE_NEGATIVE | 12 |
| STABLE_POSITIVE | 3 |
| SIGN_FLIP | 5 |
| DYNAMIC_ONLY | 3 |
| WEAK_BOTH | 3 |
| STATIC_ONLY | 1 |

- **Same RankIC sign:** 22/27
- **Sign flips:** 5

**Most stable (smallest |delta_RankIC|):**
- `price_pos_24h`: delta = -0.0002 [STABLE_NEGATIVE]
- `xs_rank_ret_1h`: delta = -0.0007 [STABLE_NEGATIVE]
- `breakout_dist_20h`: delta = -0.0012 [STABLE_NEGATIVE]

**Most unstable (largest |delta_RankIC|):**
- `vol_40h`: delta = +0.0253 [STABLE_NEGATIVE]
- `range_1h`: delta = +0.0252 [STABLE_NEGATIVE]
- `range_4h`: delta = +0.0245 [STABLE_NEGATIVE]

**Per-label stability:**

| Label | Same sign | Sign flips |
|-------|-----------|------------|
| ret_fwd_1h | 22/27 | 5 |
| ret_fwd_4h | 26/27 | 1 |
| ret_fwd_24h | 20/27 | 7 |
| ret_fwd_72h | 16/27 | 11 |

> These are diagnostic validation results only. No factor is promoted to alpha in Phase 7D-B.

---

## E. Required Negative Declarations

- No strategy backtest was run.
- No portfolio simulation was run.
- No Qlib / VectorBT integration was run.
- No Alphalens tear sheet was run.
- No factor status was upgraded.
- No alpha claim was made.
- No factor was removed or selected based on this comparison.

---

## F. Phase 7E Readiness

- ✓ 27/27 static factor_values built
- ✓ 27/27 static factors evaluated
- ✓ 0 fallback_positive
- ✓ Comparison CSV generated
- ✓ Closeout remains diagnostic only

Phase 7E allowed pending PM review.
