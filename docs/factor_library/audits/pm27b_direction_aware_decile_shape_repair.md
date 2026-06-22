# PM-27B: Direction-Aware Decile Shape Repair

**Date:** 2026-06-22
**Follows:** PM-27 (raw decile shape)

---

## Summary Verdict

**`DIRECTION_AWARE_DECILE_REPAIR_PASS`**

## 1. Why PM-27B

PM-27 used raw decile ordering (D1=lowest factor value). The registry has `expected_direction` metadata. PM-27B adds direction-aware ordering so monotonicity/spread metrics reflect the expected relationship.

## 2. Evidence expected_direction is Used

```
Direction map loaded: 71 factors
  positive: 31
  negative: 16
  conditional: 24
```

- `expected_direction` loaded from `factor_formula_registry.py` FactorSpec
- Negative factors: `expected_order_decile = 11 - raw_decile` (flipped)
- Conditional factors: `expected_order_decile = raw_decile` + `direction_handling = raw_order_conditional`

## 3. Files Changed

- `scripts/build_factor_decile_shape_diagnostics.py` (modified)
- 6 regenerated output files in `factor_diagnostics/`
- `docs/factor_library/audits/pm27b_direction_aware_decile_shape_repair.md` (new)

## 4. Coverage

- Expected: 71 factors × 4 horizons = 284 pairs
- Actual: 71 factors × 4 horizons = 284 pairs
- Missing: 0

## 5. Expected Direction Distribution

| Direction | Factor-Horizon Pairs |
|---|---:|
| positive | 124 |
| conditional | 96 |
| negative | 64 |

## 6. Direction Handling Distribution

| Handling | Pairs |
|---|---:|
| positive_aligned | 124 |
| raw_order_conditional | 96 |
| negative_flipped | 64 |

## 7. Direction-Aware Decile Shape Class Distribution

| Class | Count | % |
|---|---:|---:|
| NONLINEAR_MIXED | 225 | 79.2% |
| BOTH_TAILS_U_SHAPED | 41 | 14.4% |
| DECILE_MONOTONIC_WEAK | 18 | 6.3% |

## 8. Consistency with PM-26 Q5

| Consistency | Count |
|---|---:|
| CONFLICTING | 206 |
| DECILE_REVEALS_NONLINEARITY | 59 |
| CONSISTENT | 9 |
| DECILE_REVEALS_TAIL_DEPENDENCE | 7 |
| DECILE_MORE_MONOTONIC | 3 |

## 9. Examples of Direction-Aware Interpretation

**amihud_illiquidity_20h** (negative direction):
- 1h: monotonicity=0.67, BOTH_TAILS_U_SHAPED
- 24h: monotonicity=0.78, DECILE_MONOTONIC_WEAK
- Negative direction flip means D10=best return = highest illiquidity, consistent with theory

**funding_rate_level_20h** (positive direction):
- Positive aligned, monotonicity retained after direction-aware ordering

## 10. Payload Size

- factor_decile_shape_payload.json: includes expected_direction per factor

## 11. Validation

All outputs verified: 71 factors, 284 pairs, direction metadata present.

## 12. Limitations

1. Shape class distribution unchanged from PM-27 — direction flip reorders deciles but doesn't change shape classification logic
2. Conditional factors (24) still use raw ordering — no automatic direction inference
3. Performance: ~1700s for 71 factors

## 13. Non-Change Statement

No factors, formulas, factor_values, signal panel, public page modified.

## 14. Recommended Next PM

**PM-28:** Page integration for quantile/rolling/direction-aware decile diagnostics.
