# PM-47: Controlled New Factor Intake Batch03 — Single OHLC Range Factor

**Date:** 2026-06-23  
**Verdict:** `BATCH03_SINGLE_FACTOR_INTAKE_PASS`

---

## 1. Duplicate Search Result

Searched for: `clv`, `close_location`, `range_position`, `high_low`, `close_low`, `high_close`, `q158`, `price_position`

**Found:**
- `range_1h/4h/24h`: (high - low) / close — measures volatility range
- `price_pos_24h/72h/120h`: (close - LL) / (HH - LL) — rolling window position

**CLV is distinct:** Single-bar indicator measuring close position within each bar's high-low range, vs `price_pos` which uses rolling window extremes. No duplication.

---

## 2. Selected Factor Formula

**Factor ID:** `clv_20h`

**Formula:**
```
mean(((close - low) - (high - close)) / (high - low + 1e-8), 20)
```

**Intuition:** Close Location Value averaged over 20 bars. Measures where the close is within the high-low range of each bar.
- CLV = +1: close at high (buyers dominate)
- CLV = -1: close at low (sellers dominate)
- CLV = 0: close at midpoint

Sustained positive CLV indicates buying pressure.

---

## 3. Expected Direction Rationale

**Direction:** `positive`

Sustained close near highs indicates buying pressure, increasing probability of continued upward drift.

---

## 4. Required Columns

- `high`
- `low`
- `close`

---

## 5. Factor Values Path

**Path:** `data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/clv_20h/factor_values.parquet`

**Coverage:** 99.85%  
**Unique Symbols:** 266

---

## 6. Post-Intake Workflow Result

All 15 stages completed successfully:
- evaluate ✅
- paper-diagnostics ✅
- paper-page-payload ✅
- diagnostics-metrics ✅
- redundancy ✅
- cluster ✅
- regime ✅
- shape-stability ✅
- decile ✅
- capacity ✅
- scorecard ✅
- profile ✅
- page ✅
- page-qa ✅
- integrity-qa ✅

---

## 7. Integrity 19/19 Result

```
✅ clv_20h    PASS=19 FAIL=0 WARN=0
```

All 19 checks pass:
- factor_values ✅
- factor_level_rankic ✅
- period_ic ✅
- period_ls ✅
- ls_aggregate ✅
- cumulative_ls ✅
- paper_payload ✅
- regime_btc ✅
- quantile_shape ✅
- rolling_stability ✅
- decile_shape ✅
- capacity_liquidity ✅
- pairwise_redundancy ✅
- cluster ✅
- marginal_info ✅
- scorecard_not_stale ✅
- unified_profile ✅
- ls_btc_corr ✅
- source_metadata ✅

---

## 8. Page QA Result

```
Total: 26  |  PASS: 26  |  FAIL: 0
```

All section markers present. clv_20h visible in HTML. Factor count = 78.

---

## 9. Public Page Result

**URL:** https://jp.jerrypsy.top/momentum/factor-library/factor-evaluation.html  
**Status:** HTTP 200 ✅  
**Factor Count:** 78

---

## 10. PM-35 + Batch02 Regression Result

| Factor | Status |
|--------|--------|
| rev_2h | 19/19 PASS ✅ |
| mom_vol_adjusted_20h | 19/19 PASS ✅ |
| range_breakout_vol_confirm_20h | 19/19 PASS ✅ |
| volume_pressure_20h | 19/19 PASS ✅ |
| xs_rank_mom_accel | 19/19 PASS ✅ |
| up_down_vol_ratio_20h | 19/19 PASS ✅ |

All PM-35 five factors and batch02 factor maintain 19/19 PASS.

---

## 11. No Formula/Factor Values/Signal Changes Confirmation

- ✅ No existing factor formulas modified
- ✅ No existing factor_values changed
- ✅ No signal panel changes
- ✅ Only new factor `clv_20h` added

---

## 12. Remaining Limitations

- 71 old factors have `ls_aggregate` FAIL (pre-existing, not regression)
- `funding_rate_level_20h` had corrupted parquet file (4 bytes), rebuilt during this session

---

## 13. Recommended Next PM

**PM-48:** Factor evaluation layer release tag or factor interpretation

---

## Files Changed

1. `scripts/factor_formula_registry.py` — Added `clv_20h` compute function and FactorSpec
2. `factor_metadata/factor_bilingual_cards.csv` — Added clv_20h bilingual metadata
3. `factor_library_state.json` — Updated to 78 factors
4. `factor_diagnostics_summary.csv` — Regenerated with 78 factors
5. `factor-evaluation.html` — Rebuilt with clv_20h
6. Various diagnostics CSVs/JSONs — Regenerated

---

**Commit:** Pending  
**Status:** Ready for commit
