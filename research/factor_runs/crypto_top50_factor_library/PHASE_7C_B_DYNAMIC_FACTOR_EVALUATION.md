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

## B. Factor Values Build Summary

All 27 factors built successfully. All missing rate ≤ 0.65% → PASS gate (≤ 5%).

| factor_id | rows | coverage | missing_rate | gate |
|-----------|------|----------|-------------|------|
| mom_5h | 3,316,259 | 99.96% | 0.04% | PASS |
| mom_10h | 3,316,259 | 99.92% | 0.08% | PASS |
| mom_40h | 3,316,259 | 99.68% | 0.32% | PASS |
| rev_3h | 3,316,259 | 99.98% | 0.02% | PASS |
| rev_10h | 3,316,259 | 99.92% | 0.08% | PASS |
| rev_24h | 3,316,259 | 99.81% | 0.19% | PASS |
| vol_5h | 3,316,259 | 99.96% | 0.04% | PASS |
| vol_40h | 3,316,259 | 99.68% | 0.32% | PASS |
| vol_ratio_5_20 | 3,316,259 | 99.57% | 0.43% | PASS |
| range_1h | 3,316,259 | 100.00% | 0.00% | PASS |
| range_4h | 3,316,259 | 99.98% | 0.02% | PASS |
| range_24h | 3,316,259 | 99.82% | 0.18% | PASS |
| price_pos_24h | 3,316,259 | 99.82% | 0.18% | PASS |
| price_pos_72h | 3,316,259 | 99.43% | 0.57% | PASS |
| vol_zscore_20h | 3,316,259 | 99.58% | 0.42% | PASS |
| vol_zscore_48h | 3,316,259 | 99.36% | 0.64% | PASS |
| qvol_zscore_20h | 3,316,259 | 99.58% | 0.42% | PASS |
| qvol_zscore_48h | 3,316,259 | 99.36% | 0.64% | PASS |
| ma_gap_5_20 | 3,316,259 | 99.85% | 0.15% | PASS |
| ma_gap_10_40 | 3,316,259 | 99.69% | 0.31% | PASS |
| breakout_dist_20h | 3,316,259 | 99.85% | 0.15% | PASS |
| breakout_dist_48h | 3,316,259 | 99.62% | 0.38% | PASS |
| candle_body | 3,316,259 | 100.00% | 0.00% | PASS |
| candle_wick_upper | 3,316,259 | 100.00% | 0.00% | PASS |
| candle_wick_lower | 3,316,259 | 100.00% | 0.00% | PASS |
| xs_rank_ret_1h | 3,316,259 | 99.99% | 0.01% | PASS |
| xs_rank_vol | 3,316,259 | 99.85% | 0.15% | PASS |

**xs_rank QA:**
- xs_rank_ret_1h: no inf, 100% values in [0, 1] ✓
- xs_rank_vol: no inf, 100% values in [0, 1] ✓

---

## C. Dynamic Evaluation Summary (ret_fwd_1h)

27/27 factors evaluated. All direction_source = `candidate_csv`. Zero fallback positive.

| factor_id | family | expected_direction | direction_source | RankIC_mean | IC_mean | dir_adj_spread | turnover |
|-----------|--------|-------------------|-----------------|-------------|---------|----------------|----------|
| mom_5h | momentum | positive | candidate_csv | -0.0282 | -0.0235 | 0.000024 | 0.352 |
| mom_10h | momentum | positive | candidate_csv | -0.0234 | -0.0190 | -0.000044 | 0.255 |
| mom_40h | momentum | positive | candidate_csv | -0.0123 | -0.0089 | 0.000038 | 0.133 |
| rev_3h | reversal | negative | candidate_csv | 0.0300 | 0.0248 | -0.000022 | 0.443 |
| rev_10h | reversal | negative | candidate_csv | 0.0234 | 0.0190 | -0.000041 | 0.253 |
| rev_24h | reversal | negative | candidate_csv | 0.0190 | 0.0156 | -0.000026 | 0.166 |
| vol_5h | volatility | negative | candidate_csv | -0.0382 | -0.0314 | 0.000132 | 0.232 |
| vol_40h | volatility | negative | candidate_csv | -0.0421 | -0.0343 | 0.000100 | 0.036 |
| vol_ratio_5_20 | volatility | conditional | candidate_csv | -0.0064 | -0.0053 | N/A | 0.344 |
| range_1h | range_position | conditional | candidate_csv | -0.0413 | -0.0346 | N/A | 0.396 |
| range_4h | range_position | conditional | candidate_csv | -0.0406 | -0.0340 | N/A | 0.224 |
| range_24h | range_position | conditional | candidate_csv | -0.0371 | -0.0308 | N/A | 0.070 |
| price_pos_24h | price_position | conditional | candidate_csv | -0.0153 | -0.0127 | N/A | 0.285 |
| price_pos_72h | price_position | conditional | candidate_csv | -0.0093 | -0.0077 | N/A | 0.180 |
| vol_zscore_20h | volume_liquidity | positive | candidate_csv | -0.0048 | -0.0039 | 0.000046 | 0.569 |
| vol_zscore_48h | volume_liquidity | positive | candidate_csv | -0.0054 | -0.0044 | 0.000016 | 0.520 |
| qvol_zscore_20h | quote_volume | positive | candidate_csv | -0.0054 | -0.0044 | 0.000035 | 0.566 |
| qvol_zscore_48h | quote_volume | positive | candidate_csv | -0.0060 | -0.0049 | 0.000035 | 0.515 |
| ma_gap_5_20 | trend_ma | positive | candidate_csv | -0.0129 | -0.0106 | 0.000089 | 0.117 |
| ma_gap_10_40 | trend_ma | positive | candidate_csv | -0.0079 | -0.0064 | 0.000007 | 0.063 |
| breakout_dist_20h | breakout | positive | candidate_csv | -0.0154 | -0.0127 | 0.000096 | 0.307 |
| breakout_dist_48h | breakout | positive | candidate_csv | -0.0114 | -0.0094 | 0.000063 | 0.214 |
| candle_body | intraday_candle | conditional | candidate_csv | -0.0217 | -0.0181 | N/A | 0.788 |
| candle_wick_upper | intraday_candle | negative | candidate_csv | 0.0071 | 0.0058 | -0.000138 | 0.783 |
| candle_wick_lower | intraday_candle | positive | candidate_csv | -0.0019 | -0.0015 | -0.000047 | 0.782 |
| xs_rank_ret_1h | xs_normalized | conditional | candidate_csv | -0.0294 | -0.0248 | N/A | 0.752 |
| xs_rank_vol | xs_normalized | conditional | candidate_csv | -0.0221 | -0.0181 | N/A | 0.008 |

---

## D. Best/Worst Diagnostic Only

These are diagnostic observations only. No factor is promoted to alpha in Phase 7C-B.

**Highest absolute RankIC (ret_fwd_1h):** vol_40h (|RankIC| = 0.042), range_1h (0.041), range_4h (0.041)

**Lowest absolute RankIC (ret_fwd_1h):** candle_wick_lower (0.002), vol_zscore_20h (0.005), vol_ratio_5_20 (0.006)

**Highest direction-adjusted spread:** vol_5h (0.000132), vol_40h (0.000100), breakout_dist_20h (0.000096)

**Highest turnover:** candle_body (0.788), candle_wick_upper (0.783), candle_wick_lower (0.782)

**Lowest coverage (still PASS):** vol_zscore_48h (99.36%), qvol_zscore_48h (99.36%), price_pos_72h (99.43%)

**Note on momentum/reversal direction:** Several momentum factors show negative RankIC (expected positive) and reversal factors show positive RankIC (expected negative). This is a diagnostic observation about short-horizon momentum reversal in crypto, not a data error.

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

1. ✓ 27/27 factor_values built.
2. ✓ 27/27 factors evaluated.
3. ✓ Zero fallback_positive.
4. ✓ selected_missing_rate: all ≤ 0.65% (PASS gate ≤ 5%).
5. ✓ Closeout declares all results diagnostic only.

**Phase 7D static-vs-dynamic / validation is allowed pending PM review.**
