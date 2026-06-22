# PM-42: Market Regime / BTC Diagnostics Workflow Reintegration

**Date:** 2026-06-23
**Verdict:** `MARKET_REGIME_BTC_WORKFLOW_PASS`
**Commit:** `61ab330`

---

## Existing Script Discovery

`scripts/build_factor_market_regime_diagnostics.py` (PM-23/PM-24) already computes ALL required fields:

| Field | Computed? | Output file |
|-------|-----------|-------------|
| `paper_return_btc_corr` | ✅ | `factor_regime_exposure_summary.csv` |
| `paper_return_btc_beta` | ✅ | `factor_regime_exposure_summary.csv` |
| `long_short_btc_corr` | ✅ | `factor_regime_exposure_summary.csv` |
| `long_short_btc_beta` | ✅ | `factor_regime_exposure_summary.csv` |
| `ic_btc_return_corr` | ✅ | `factor_regime_exposure_summary.csv` |
| `bull_minus_bear_paper_return` | ✅ | `factor_regime_exposure_summary.csv` |
| `highvol_minus_lowvol_paper_return` | ✅ | `factor_regime_exposure_summary.csv` |
| `drawdown_minus_normal_paper_return` | ✅ | `factor_regime_exposure_summary.csv` |
| `regime_dependency_class` | ✅ | `factor_regime_exposure_summary.csv` |

**No code duplication needed.** Script was reused as-is.

## Root Cause of PM-35 Missing Data

`factor_monthly_ic_series.csv` only had 71 factors — PM-35's 5 new factors were missing. The regime script reads from this file for IC-level regime analysis. Since PM-35 factors weren't in the IC file, the script classified them as `INSUFFICIENT_REGIME_DATA`.

**Fix:** Merged PM-35 monthly IC data from canonical `factor_level_period_ic_summary.csv` into `factor_monthly_ic_series.csv` (7076 → 7576 rows, 71 → 76 factors).

## PM-35 Five-Factor Regime/BTC Diagnostics

| Factor | Regime Class | BTC Corr | Bull-Bear Δ | HiVol-LoVol Δ |
|--------|-------------|----------|-------------|---------------|
| rev_2h | REGIME_ROBUST | -0.004 | +0.020 | -0.003 |
| mom_vol_adjusted_20h | REGIME_ROBUST | -0.086 | -0.048 | -0.049 |
| range_breakout_vol_confirm_20h | BTC_BETA_SENSITIVE | -0.277 | -0.083 | +0.045 |
| volume_pressure_20h | VOL_DEPENDENT | +0.064 | +0.017 | -0.088 |
| xs_rank_mom_accel | REGIME_ROBUST | +0.085 | +0.022 | -0.016 |

## Page Status

- Public page: HTTP 200 ✓
- JSON valid ✓
- factor_count=76 ✓
- All 5 PM-35 factors show regime data on page ✓

## QA Result

- `check_factor_evaluation_page_completeness.py`: 23/23 PASS

## Files Changed

1. `factor_monthly_ic_series.csv` — merged PM-35 monthly IC data
2. `factor_regime_exposure_summary.csv` — regenerated (76 factors)
3. `factor_regime_summary.csv` — regenerated (76 factors)
4. `factor_regime_diagnostics_payload.json` — regenerated
5. `factor_market_regime_manifest.json` — regenerated
6. `factor_regime_class_distribution.csv` — regenerated
7. `factor_regime_top_lists.csv` — regenerated
8. `factor-evaluation.html` — rebuilt

## No Formula / Factor Values / Signal Changes

- No `factor_formula_registry.py` changes
- No `factor_ops.py` changes
- No `build_factor_values.py` changes
- No `expected_direction` changes
- No signal panel changes

## Important Clarification

- Regime labels are **ex-post diagnostics**, not trading timing signals
- BTC correlation/beta are **research diagnostics**, not execution signals
- `INSUFFICIENT_REGIME_DATA` is shown explicitly when minimum months per regime is not met

## Remaining Limitations

None — all 76 factors now have regime/BTC diagnostics.

## Recommended Next PM

**PM-43: Post-intake factor interpretation and direction-semantics review**
