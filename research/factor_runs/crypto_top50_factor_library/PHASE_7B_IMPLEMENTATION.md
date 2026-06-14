# Phase 7B — First Factor Mining Batch Implementation

> Date: 2026-06-14
>
> Status: COMPLETE — all 27 selected_for_7B factors implemented

---

## 1. Factors Implemented

All 27 `selected_for_7B` factors from `factor_mining_candidates_v0_1.csv`:

| # | factor_id | family | formula |
|---|-----------|--------|---------|
| 1 | mom_5h | momentum | close/close_lag_5-1 |
| 2 | mom_10h | momentum | close/close_lag_10-1 |
| 3 | mom_40h | momentum | close/close_lag_40-1 |
| 4 | rev_3h | reversal | -(close/close_lag_3-1) |
| 5 | rev_10h | reversal | -(close/close_lag_10-1) |
| 6 | rev_24h | reversal | -(close/close_lag_24-1) |
| 7 | vol_5h | volatility | std(ret_1h, 5) |
| 8 | vol_40h | volatility | std(ret_1h, 40) |
| 9 | vol_ratio_5_20 | volatility | std(ret_1h,5)/std(ret_1h,20) |
| 10 | range_1h | range_position | (high-low)/close |
| 11 | range_4h | range_position | (HH4-LL4)/close |
| 12 | range_24h | range_position | (HH24-LL24)/close |
| 13 | price_pos_24h | price_position | (close-LL24)/(HH24-LL24+eps) |
| 14 | price_pos_72h | price_position | (close-LL72)/(HH72-LL72+eps) |
| 15 | vol_zscore_20h | volume_liquidity | (vol-SMA20)/STD20 |
| 16 | vol_zscore_48h | volume_liquidity | (vol-SMA48)/STD48 |
| 17 | qvol_zscore_20h | quote_volume_liquidity | (qv-SMA20)/STD20 |
| 18 | qvol_zscore_48h | quote_volume_liquidity | (qv-SMA48)/STD48 |
| 19 | ma_gap_5_20 | trend_ma | (SMA5-SMA20)/SMA20 |
| 20 | ma_gap_10_40 | trend_ma | (SMA10-SMA40)/SMA40 |
| 21 | breakout_dist_20h | breakout | (close-HH20)/(HH20-LL20+eps) |
| 22 | breakout_dist_48h | breakout | (close-HH48)/(HH48-LL48+eps) |
| 23 | candle_body | intraday_candle | (close-open)/(high-low+eps) |
| 24 | candle_wick_upper | intraday_candle | (high-max(open,close))/(high-low+eps) |
| 25 | candle_wick_lower | intraday_candle | (min(open,close)-low)/(high-low+eps) |
| 26 | xs_rank_ret_1h | cross_sectional_normalized | rank(ret_1h) by timestamp |
| 27 | xs_rank_vol | cross_sectional_normalized | rank(vol_20h) by timestamp |

**Count: exactly 27.** No factors missing, no extra factors added.

---

## 2. Cross-Sectional Rank Note

`xs_rank_ret_1h` and `xs_rank_vol` use a two-stage approach:

1. **Per-symbol compute_fn** (`factor_formula_registry.py`): generates the raw
   time-series metric (pct_change / rolling mean volume).
2. **Cross-sectional postprocess** (`build_factor_values.py::apply_cross_sectional_postprocess`):
   after all symbols are concatenated, groups by `timestamp` and applies
   `rank(pct=True, method="average")` to produce percentile ranks in [0, 1].

Unit tests in `test_crypto_factor_batch7b.py` cover: basic rank correctness,
NaN preservation, and isolation from non-xs factors.

---

## 3. Formula Adjustments

No adjustments were necessary. All formulas match the candidate CSV exactly.

---

## 4. Files Modified

| File | Change |
|------|--------|
| `scripts/factor_formula_registry.py` | +27 compute functions, +27 REGISTRY entries, +2 imports |
| `scripts/factor_ops.py` | +1 new op: `rolling_sum` |
| `scripts/build_factor_values.py` | Added `apply_cross_sectional_postprocess()` and called it after concatenating per-symbol factor outputs, before writing factor_values |
| `tests/unit/test_crypto_factor_batch7b.py` | NEW: 37 tests (registry metadata, formula correctness, cross-sectional postprocess) |
| `research/.../PHASE_7B_IMPLEMENTATION.md` | NEW: this closeout |

---

## 5. Tests

```
82 passed in 1.05s
```

- `test_crypto_factor_batch7b.py`: 37/37 pass
- `test_crypto_factor_batch1.py`: 24/24 pass (existing, not modified)
- `test_factor_mining_candidates.py`: 15/15 pass (existing, not modified)
- `test_crypto_factor_values.py`: skipped (not applicable — no factor_values built)
- `test_crypto_factor_eval_smoke.py`: skipped (not applicable — no evaluation run)

---

## 6. Negative Declarations

- **No factor_values were built.**
- **No dynamic evaluation was run.**
- **No strategy backtest was run.**
- **No factor was promoted to alpha.**
- **All 27 new factors remain DIAGNOSTIC_PROBE / pending evaluation.**
