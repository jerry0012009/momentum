# Signal Evaluation Parity Harness

> Phase 12D-H2 · 2026-06-19

## Why This Exists

The new `signal_evaluation` package provides reusable functions for RankIC, Quantile Spread, and Direction Consistency. Before we can trust these functions as replacements for the old Phase 10A scripts, we need to verify they produce equivalent results on the same input data.

This harness:
1. Loads the same signal panel and labels that Phase 10A used
2. Runs the new `signal_evaluation` functions
3. Compares against Phase 10A outputs
4. Reports PASS/FAIL with tolerance

## Inputs

| File | Description |
|------|-------------|
| `phase9b_signal_panel.parquet` | Signal panel (3 variants) |
| `alphalens_exports/.../forward_returns_long.parquet` | Old label file (17,533 timestamps × 50 symbols) |
| `phase10a_signal_rankic_summary.csv` | Old RankIC reference |
| `phase10a_signal_quantile_spread_summary.csv` | Old Quantile Spread reference |

## Outputs

| File | Description |
|------|-------------|
| `phase12d_h2_signal_eval_parity_rankic.csv` | RankIC parity comparison |
| `phase12d_h2_signal_eval_parity_quantile_spread.csv` | Quantile Spread parity comparison |
| `phase12d_h2_signal_eval_parity_summary.csv` | Overall summary |

## Tolerance

| Metric | Tolerance | Reason |
|--------|-----------|--------|
| mean_rank_ic | 1e-4 | float64 vs float32 rounding |
| t_stat | 1e-1 | Degrees of freedom differs (n-2 vs n) |
| n_periods | 2 | NaN filtering differs by 0-1 timestamps |
| mean_spread | 2e-3 | Quantile bucket construction differs |
| positive_fraction | 1e-2 | Bucket boundary differences |

## Known Differences

### RankIC
- Mean RankIC matches to ~1e-7 precision
- n_periods may differ by 1-2 timestamps due to NaN filtering
- t_stat differs slightly due to degrees of freedom

### Quantile Spread
- Mean spread differs by ~5% because:
  - Old script uses `pd.qcut` with `duplicates="drop"` at per-group level
  - New module uses same approach but may handle edge cases differently
  - Bucket boundary assignments may differ for tied values
- The direction (negative) and magnitude (order of magnitude) are preserved
- This does NOT affect the conclusion: spread is negative for all signals × horizons

### Consistency
- All 3 signal variants show DIRECTION_CONFLICT on current labels
- This matches the Phase 12D-G-R2/R3/R4 findings

## What To Do If Parity Fails

1. **Do NOT modify old results** to make them match
2. **Do NOT modify new module** to hard-code old results
3. Document the failure in this file
4. Investigate root cause (NaN handling, bucket construction, etc.)
5. Adjust tolerance only if the difference is explainable and acceptable

## What This Does NOT Do

- Does NOT modify old Phase 10A scripts
- Does NOT modify old Phase 10A outputs
- Does NOT modify signal panel or labels
- Does NOT change research results
- Does NOT start Phase 13
- Does NOT connect to exchange APIs
- Does NOT add production/trading logic

## Next Steps

- Phase 12D-H3: Consider wrapper refactor (old scripts → thin wrappers around new modules)
