# Phase 7I-B — Batch-2 Factor Values Build & Static/Dynamic Evaluation

> Date: 2026-06-14
>
> Status: COMPLETE

---

## A. Scope

- Phase: 7I-B
- 9 PM-approved Batch-2 factors only
- Static dataset: crypto_top50_usdt_perp_1h
- Dynamic dataset: crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1
- No classification, no redundancy, no backtest, no alpha promotion

---

## B. Build Summary

| Dataset | Factors | Rows | Worst Coverage |
|---------|---------|------|----------------|
| Static | 9/9 | 215,061 | ma_gap_20_80 (98.163%) |
| Dynamic | 9/9 | 3,316,259 | ma_gap_20_80 (99.366%) |

All 9 factor_values built successfully. No gate failures.

---

## C. Evaluation Summary

| Dataset | Factors | ret_fwd_1h rows | all_labels rows | direction_source |
|---------|---------|-----------------|-----------------|------------------|
| Static | 9/9 | 9 | 36 | candidate_csv |
| Dynamic | 9/9 | 9 | 36 | candidate_csv |

No fallback_positive. All directions from candidate_csv.

---

## D. Static ret_fwd_1h Results

| factor_id | RankIC | RankICIR | dir_adj_spread | turnover |
|-----------|--------|----------|----------------|----------|
| williams_r_14h | 0.0181 | 0.098 | 0.000230 | 0.347 |
| ma_gap_20_80 | 0.0068 | 0.034 | 0.000504 | 0.032 |
| qvol_ma_ratio_5_20 | 0.0006 | 0.003 | 0.000248 | 0.226 |
| mom_accel_20h | -0.0172 | -0.085 | 0.000182 | 0.339 |
| rsi_7h | -0.0198 | -0.106 | -0.000431 | 0.295 |
| ema_12_26_gap | -0.0035 | -0.018 | 0.000513 | 0.068 |
| rsi_28h | -0.0071 | -0.039 | -0.000459 | 0.153 |
| downside_vol_20h | -0.0121 | -0.061 | -0.000441 | 0.067 |
| vol_of_vol_20h | -0.0119 | -0.063 | -0.000753 | 0.070 |

---

## E. Dynamic ret_fwd_1h Results

| factor_id | RankIC | RankICIR | dir_adj_spread | turnover |
|-----------|--------|----------|----------------|----------|
| williams_r_14h | 0.0165 | 0.084 | 0.000087 | 0.354 |
| downside_vol_20h | -0.0351 | -0.126 | 0.000126 | 0.068 |
| vol_of_vol_20h | -0.0340 | -0.137 | 0.000114 | 0.076 |
| rsi_7h | -0.0237 | -0.118 | -0.000052 | 0.295 |
| mom_accel_20h | -0.0220 | -0.101 | 0.000025 | 0.348 |
| rsi_28h | -0.0175 | -0.087 | -0.000013 | 0.155 |
| ema_12_26_gap | -0.0111 | -0.050 | 0.000031 | 0.069 |
| qvol_ma_ratio_5_20 | -0.0062 | -0.034 | -0.000018 | 0.229 |
| ma_gap_20_80 | -0.0026 | -0.011 | -0.000013 | 0.034 |

---

## F. Initial Diagnostic Observations

1. **Top absolute RankIC (dynamic)**: downside_vol_20h (|-0.035|), vol_of_vol_20h (|-0.034|), rsi_7h (|-0.024|).
2. **Weakest factors**: ma_gap_20_80 (|-0.003|), qvol_ma_ratio_5_20 (|-0.006|) — very thin signal.
3. **Direction mismatch — williams_r_14h**: expected negative but RankIC positive in both static (+0.018) and dynamic (+0.016). Direction may need review.
4. **Direction mismatch — ema_12_26_gap**: expected positive but RankIC negative in both static (-0.004) and dynamic (-0.011). Signal very weak.
5. **High turnover**: williams_r_14h (0.354), mom_accel_20h (0.348), rsi_7h (0.295).
6. **Low turnover**: ma_gap_20_80 (0.034), downside_vol_20h (0.068), ema_12_26_gap (0.069).
7. **Coverage**: all >98%, no data issues.
8. **Static vs dynamic consistency**: RankIC signs mostly consistent between static and dynamic datasets.

---

## G. Required Negative Declarations

No new factors were implemented.
No factor registry was modified.
No factor_ops were modified.
No classification was run.
No redundancy analysis was run.
No static-vs-dynamic comparison was run.
No strategy backtest was run.
No portfolio simulation was run.
No Qlib / VectorBT / Backtrader integration was run.
No Alphalens tear sheet was run.
No factor status was upgraded to CANDIDATE_REVIEW.
No alpha claim was made.
No factor was removed or selected for trading.

---

## H. Phase 7I-C Readiness

- ✓ Static build summary has 9 rows
- ✓ Dynamic build summary has 9 rows
- ✓ Static ret_fwd_1h summary has 9 rows
- ✓ Dynamic ret_fwd_1h summary has 9 rows
- ✓ Static all-label summary has 36 rows
- ✓ Dynamic all-label summary has 36 rows
- ✓ No unapproved factor appears
- ✓ No alpha/status promotion occurred

Phase 7I-C static-vs-dynamic comparison and diagnostic classification is allowed pending PM review.
