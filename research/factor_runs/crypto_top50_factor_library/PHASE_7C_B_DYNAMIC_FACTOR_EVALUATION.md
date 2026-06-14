# Phase 7C-B — Dynamic Factor Values Build & Dynamic-Universe Evaluation

> Date: 2026-06-14
>
> Status: COMPLETE

---

## A. Scope

- Phase: 7C-B
- Factors: 27 selected_for_7B only
- dataset_id: `crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1`
- universe_id: `crypto_usdt_perp_monthly_volume_top50_current_listed_v1`
- evaluation_mode: dynamic_universe_membership
- universe_mode: dynamic_from_current_listed_pool, not true point-in-time
- n_symbols: 266
- n_months: 25
- n_rows_after_universe_filter: 890,400

---

## B. Audit Artifacts

Machine-generated CSVs for reproducibility:

| File | Rows | Description |
|------|------|-------------|
| `phase7c_b_factor_values_build_summary.csv` | 27 | Per-factor build: rows, coverage, missing_rate, gate |
| `phase7c_b_dynamic_eval_summary_ret_fwd_1h.csv` | 27 | Per-factor eval (ret_fwd_1h): IC, RankIC, spread, turnover |
| `phase7c_b_dynamic_eval_summary_all_labels.csv` | 108 | Per-factor × 4 labels long table |

All family labels sourced from `factor_mining_candidates_v0_1.csv`.

---

## C. Factor Values Build Summary

27/27 factors built. All rows = 3,316,259. All missing_rate ≤ 0.65%. All PASS.

See: `phase7c_b_factor_values_build_summary.csv`

---

## D. Dynamic Evaluation Summary (ret_fwd_1h)

27/27 factors evaluated. All direction_source = `candidate_csv`. Zero fallback positive.

See: `phase7c_b_dynamic_eval_summary_ret_fwd_1h.csv`

**Highest absolute RankIC:** vol_40h (|RankIC| = 0.042), range_1h (0.041), range_4h (0.041)

**Lowest absolute RankIC:** candle_wick_lower (0.002), vol_zscore_20h (0.005), vol_ratio_5_20 (0.006)

---

## E. Required Negative Declarations

- No strategy backtest was run.
- No portfolio simulation was run.
- No Qlib / VectorBT integration was run.
- No Alphalens tear sheet was run.
- No static-vs-dynamic comparison was run.
- No factor status was upgraded.
- No alpha claim was made.
- No factor was removed or selected based on this evaluation.

---

## F. Whether Phase 7D Is Allowed

All conditions met:

1. ✓ 27/27 factor_values built (27 rows in build summary CSV).
2. ✓ 27/27 factors evaluated (27 rows in ret_fwd_1h evaluation CSV).
3. ✓ Zero fallback_positive.
4. ✓ selected_missing_rate: all ≤ 0.65% (PASS gate ≤ 5%).
5. ✓ All family labels sourced from candidate CSV.
6. ✓ Closeout declares all results diagnostic only.

**Phase 7D static-vs-dynamic / validation is allowed pending PM review.**
