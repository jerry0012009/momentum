# PM-35: Controlled Factor Intake Batch 01

**Date:** 2026-06-22
**Follows:** PM-34 (factor expansion backlog)

---

## Summary Verdict

**`CONTROLLED_FACTOR_INTAKE_BATCH01_PASS_WITH_LIMITATIONS`**

## 1. Implemented Factors

| Factor ID | Family | Direction | Coverage | 1h Adj IC | t-stat |
|---|---|---|---|---|---|
| rev_2h | short_term_reversal | positive | 99.98% | +0.036 | 29.82 |
| mom_vol_adjusted_20h | medium_term_momentum | positive | 99.57% | -0.021 | -20.47 |
| range_breakout_vol_confirm_20h | range_breakout | positive | 16.83% | -0.029 | -13.67 |
| volume_pressure_20h | volume_pressure | positive | 99.84% | -0.011 | -11.31 |
| xs_rank_mom_accel | cross_sectional_rank_acceleration | positive | 99.80% | -0.024 | -20.51 |

## 2. Formula Fix

`range_breakout_vol_confirm_20h` originally had 0% coverage because `breakout_dist = (close - hh) / (hh - ll)` is always <= 0 (close <= high by definition). Fixed to:
```
breakout_dist = (close - ll) / (hh - ll + 1e-8)  # position in range [0, 1]
```
Returns `breakout_dist * zscore(volume, 20)` when `breakout_dist > 0.8` (near high end of range).

## 3. Deferred Factors

None — all 5 implemented.

## 4. Files Changed

- `scripts/factor_formula_registry.py` — 5 new factors + formula fix
- `data/features/.../factor_values.parquet` — 5 new files
- `research/.../factor_level_evaluation/*_batch01.csv` — evaluation outputs (merged into main)
- Various diagnostics outputs regenerated

## 5. Factor Count

- Before: 71
- After: 76

## 6. Evidence Matrix

- 76 factors total
- 5 new factors: INCOMPLETE_EVIDENCE (missing decile-shape, capacity-liquidity)

## 7. Profile Classes

- 5 new factors: INCOMPLETE_EVIDENCE / WORKFLOW_INCOMPLETE

## 8. Limitations

1. Decile-shape and capacity-liquidity stages timed out (OOM risk on 15GB server)
2. New factors show INCOMPLETE_EVIDENCE until those stages complete
3. No new operators added — all used existing factor_ops

## 9. Non-Change Statement

No signal panel, live trading, or strategy code modified.

## 10. Recommended Next PM

**PM-36:** Post-intake workflow regression audit — complete missing diagnostics for new factors.
