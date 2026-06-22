# PM-23B: Refresh Regime Diagnostics After Paper Repair

**Date:** 2026-06-22
**Follows:** PM-21B (paper repair) / PM-22B (page integration) / PM-23/PM-24 (original regime)

---

## Summary Verdict

**`REGIME_REFRESH_AFTER_PAPER_REPAIR_PASS`**

## 1. Why PM-23B Was Needed

PM-23/PM-24 regime diagnostics were built using PM-21's original paper monthly returns, which used a **naive fee-adjustment formula**: `monthly_gross_ret - monthly_turnover * fee_bps / 10000 * 24`. PM-21B repaired this to use **hourly compounding**: `np.prod(1 + net_ret_hourly) - 1`. This changed the paper return values, which in turn changed regime dependency classifications.

## 2. Files Changed/Regenerated

### Script:
- `scripts/build_factor_market_regime_diagnostics.py` — **no code changes needed**. Already reads `single_factor_paper_monthly_returns.csv` and filters to `fee_bps=10`.

### Regenerated outputs (7 files):
- `market_regime_monthly_labels.csv` — 25 months (unchanged)
- `factor_regime_summary.csv` — 1,491 rows
- `factor_regime_exposure_summary.csv` — 71 factors
- `factor_regime_class_distribution.csv` — 5 classes
- `factor_regime_top_lists.csv` — top factors per class
- `factor_regime_diagnostics_payload.json` — full payload
- `factor_market_regime_manifest.json` — manifest

## 3. PM-21B Paper Monthly Returns Used: ✓

Confirmed. Script reads `single_factor_paper_monthly_returns.csv` with `fee_bps=10` filter. PM-21B repaired this file to use hourly compounding.

## 4. Selected Fee Bps: 10

## 5. BTC Coverage

- Symbol: BTCUSDT
- Months: 25 (2024-06 to 2026-06)
- Bars: 17,808 hourly bars

## 6. Factor Coverage: 71/71

## 7. Regime Dependency Class Distribution — Before vs After

| Class | Before (PM-23) | After (PM-23B) | Change |
|---|---|---|---|
| REGIME_ROBUST | 22 | 29 | +7 |
| BULL_DEPENDENT | 22 | 11 | -11 |
| VOL_DEPENDENT | 12 | 17 | +5 |
| BEAR_DEPENDENT | 7 | 12 | +5 |
| DRAWDOWN_FRAGILE | 8 | 2 | -6 |

**25 factors changed dependency class.** The shift is consistent with corrected paper returns showing less bull-market dependency and more regime-robust behavior.

## 8. Top Changes

### Factors that became REGIME_ROBUST:
- bb_zscore_20h (was VOL_DEPENDENT)
- klow_close (was BULL_DEPENDENT)
- mom_accel_20h (was BULL_DEPENDENT)
- qvol_zscore_48h (was BULL_DEPENDENT)
- realized_skew_20h (was BULL_DEPENDENT)
- rev_1h (was DRAWDOWN_FRAGILE)
- ksft_5h (was VOL_DEPENDENT)

### Largest paper_return_btc_beta changes:
- candle_wick_lower: 0.42 → 0.14 (Δ=0.28)
- klow_close: 0.31 → 0.09 (Δ=0.22)
- candle_wick_upper: 0.22 → 0.01 (Δ=0.21)
- rev_1h: 0.16 → -0.05 (Δ=0.20)

## 9. Top Regime-Robust Factors (after refresh)

29 factors classified as REGIME_ROBUST — these show consistent performance across bull/bear/high-vol/low-vol/deep-drawdown regimes.

## 10. Workflow Command Validation

```bash
python scripts/run_factor_library_refresh.py --stage regime --dry-run  # ✓
python scripts/run_factor_library_refresh.py --stage regime            # ✓
```

## 11. Limitations

1. Regime labels themselves (BULL/BEAR/SIDEWAYS, HIGH_VOL/LOW_VOL, NORMAL/DEEP_DRAWDOWN) are derived from BTC hourly bars and are unchanged.
2. Only paper_return metric uses PM-21B corrected returns. IC and long-short metrics are unchanged.
3. No public HTML page updated (PM-24B task).

## 12. Non-Change Statement

- No factors added or modified.
- No factor formulas changed.
- No factor_values changed.
- No signal panel changed.
- No public HTML page changed.
- No factor-evaluation.html modified.

## 13. Recommended Next PM

**PM-24B** — Refresh factor-evaluation.html regime section with updated regime payload.
