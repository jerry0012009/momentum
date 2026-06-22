# PM-27: Decile-Level Quantile Shape Diagnostics

**Date:** 2026-06-22
**Follows:** PM-26 (Q1-Q5 shape) / PM-25 (staleness)

---

## Summary Verdict

**`DECILE_SHAPE_DIAGNOSTICS_PASS`**

## 1. Why PM-27

PM-26 used 5 quantile buckets — too coarse to distinguish monotonic factors from tail-dependent or nonlinear ones. PM-27 adds D1-D10 decile analysis.

## 2. Implementation Choice

New script `scripts/build_factor_decile_shape_diagnostics.py` — reads factor_values parquet + labels parquet directly. Did NOT modify `evaluate_factors.py` (too risky).

## 3. Files Changed

- `scripts/build_factor_decile_shape_diagnostics.py` (new)
- `research/.../factor_diagnostics/factor_decile_return_summary.csv` (70,760 rows)
- `research/.../factor_diagnostics/factor_decile_shape_summary.csv` (284 rows)
- `research/.../factor_diagnostics/factor_decile_shape_summary.json`
- `research/.../factor_diagnostics/factor_decile_shape_payload.json` (262KB)
- `research/.../factor_diagnostics/factor_decile_shape_manifest.json`
- `research/.../factor_diagnostics/factor_decile_shape_timeseries.csv` (7,076 rows)

## 4. Coverage

- Expected: 71 factors × 4 horizons = 284 pairs
- Actual: 71 factors × 4 horizons = 284 pairs
- Missing: 0

## 5. Decile Shape Class Distribution

| Class | Count | % |
|---|---:|---:|
| NONLINEAR_MIXED | 225 | 79.2% |
| BOTH_TAILS_U_SHAPED | 41 | 14.4% |
| DECILE_MONOTONIC_WEAK | 18 | 6.3% |

## 6. Consistency with PM-26 Q5

| Consistency | Count | % |
|---|---:|---:|
| CONFLICTING | 206 | 72.5% |
| DECILE_REVEALS_NONLINEARITY | 59 | 20.8% |
| CONSISTENT | 9 | 3.2% |
| DECILE_REVEALS_TAIL_DEPENDENCE | 7 | 2.5% |
| DECILE_MORE_MONOTONIC | 3 | 1.1% |

**Key insight:** 93% of factor-horizon pairs show different shape at decile level vs Q5 level. Q5 buckets were too coarse — most factors have nonlinear or U-shaped return curves that only become visible with 10 buckets.

## 7. Examples

**Consistent (confirmed monotonic):**
- funding_rate_level_20h / 4h: CONSISTENT, DECILE_MONOTONIC_WEAK
- amihud_illiquidity_20h / 1h: CONSISTENT, DECILE_MONOTONIC_WEAK

**Revealed nonlinearity:**
- Most factors show NONLINEAR_MIXED at decile level despite WEAK_MONOTONIC or NO_CLEAR_SHAPE at Q5 level

## 8. Payload Size

- factor_decile_shape_payload.json: 262KB (compact, suitable for PM-28 page integration)

## 9. Validation

All outputs verified: 71 factors, 284 pairs, payload includes all factors.

## 10. Limitations

1. Performance: 1780s for 71 factors (~25s/factor) — reads parquet per factor
2. No direction metadata used — decile ordering is raw (D1=lowest factor value, D10=highest)
3. Only 25 months of data limits robustness
4. Nonlinearity detection is sensitive to outlier months

## 11. Non-Change Statement

No factors, formulas, factor_values, signal panel, public page modified.

## 12. Recommended Next PM

**PM-28:** Page integration for quantile/rolling/decile diagnostics on factor-evaluation.html.
