# Phase 7I-A — Batch-2 Factor Implementation

> Date: 2026-06-14
>
> Status: COMPLETE

---

## A. Scope

- Phase: 7I-A
- Only PM-approved factors from `phase7h_pm_approved_batch2.csv`
- No factor_values build, no evaluation, no backtest

---

## B. Implemented Factors (9)

| factor_id | family | direction | formula_short |
|-----------|--------|-----------|---------------|
| ema_12_26_gap | technical_indicators | positive | (EMA12 - EMA26) / EMA26 |
| rsi_7h | technical_indicators | negative | Wilder RSI lookback=7, 0-100 |
| rsi_28h | technical_indicators | negative | Wilder RSI lookback=28, 0-100 |
| williams_r_14h | technical_indicators | negative | (HH14 - close) / (HH14 - LL14 + eps), 0-1 |
| downside_vol_20h | realized_skew_kurtosis | negative | std(min(ret,0), 20) |
| vol_of_vol_20h | realized_skew_kurtosis | negative | std(std(ret,5), 20) |
| mom_accel_20h | momentum | positive | mom_20h - delay(mom_20h, 5) |
| qvol_ma_ratio_5_20 | quote_volume_liquidity | positive | SMA(qvol,5)/SMA(qvol,20) - 1 |
| ma_gap_20_80 | trend_ma | positive | (SMA20 - SMA80) / SMA80 |

---

## C. Files Modified

| File | Change |
|------|--------|
| `scripts/factor_formula_registry.py` | +9 compute functions, +9 FactorSpec entries (38→47 total) |
| `tests/unit/test_crypto_factor_batch7i.py` | New: 13 tests |

---

## D. Tests

13 tests, all PASS:
- All 9 approved factors exist in registry
- No rejected SELECT_NOW factor implemented
- No WQ101/Alpha158 batch-2 factors implemented
- Correct family and direction for all 9
- No forbidden status language
- RSI 7h/28h bounded in [0, 100]
- Williams %R bounded in [0, 1]
- downside_vol uses only past returns (no future shift)
- vol_of_vol uses nested rolling std
- qvol_ma_ratio uses quote_volume (not volume)
- ma_gap_20_80 uses 20/80 windows
- mom_accel_20h formula verified against manual computation

---

## E. Not Implemented (explicitly rejected by PM)

- mom_80h, rev_48h, vol_ma_ratio_5_20, ema_gap_12_26
- range_breakout_20h, range_breakdown_20h, breakout_dist_72h, breakout_high_20h
- wq101_alpha23 and all WQ101/Alpha158 factors

---

## F. Negative Declarations

- No factor_values were built.
- No static evaluation was run.
- No dynamic evaluation was run.
- No static-vs-dynamic comparison was run.
- No redundancy analysis was rerun.
- No strategy backtest was run.
- No portfolio simulation was run.
- No Qlib / VectorBT / Backtrader integration was run.
- No Alphalens tear sheet was run.
- No factor status was upgraded to CANDIDATE_REVIEW.
- No alpha claim was made.
- No unapproved factor was implemented.

---

## G. Phase 7I-B Readiness

- ✓ 9 PM-approved factors implemented with unit tests
- ✓ No unapproved factors added
- ✓ All tests pass

Phase 7I-B build/evaluation may start pending PM review.
