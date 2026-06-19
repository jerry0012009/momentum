# Signal Evaluation Performance

> Phase 12D-H4-R · 2026-06-19

## H4-R: RankIC Parity Regression Fix

### Problem
Phase 12D-H4 vectorized `_rank_rows` used ordinal rank (argsort). This fails for ties — ordinal rank assigns rank 1,2,3 to tied values instead of the correct average rank 2,2,2. Result: `diff_mean_rank_ic` up to 5.19e-06, exceeding 5e-07 tolerance → 10/12 INVESTIGATE.

### Fix
Changed `_rank_rows` to use scipy-compatible average rank for ties:
- Sort values, detect tied groups, assign average rank to each group
- Matches `scipy.stats.rankdata(method='average')` exactly

### Result
- **RankIC**: 12/12 PASS_ROUNDED_REFERENCE (all diff < 5e-07)
- **Spread (legacy)**: 12/12 PASS_ROUNDED_REFERENCE
- **H3 Gate**: OPEN_FULL_WRAPPER

## Previous Bottleneck

`compute_rank_ic` and `compute_quantile_spread` used per-timestamp Python for-loops over ~17,520 timestamps. Total: ~30-35 minutes for 3 signals × 4 horizons.

## Vectorization Strategy

### RankIC
1. Pivot long data to (timestamps × symbols) matrix
2. Rank each row using numpy with **average tie-breaking** (scipy-compatible)
3. Compute row-wise Pearson correlation via vectorized numpy operations

### Quantile Spread (legacy_phase10a)
1. Pivot long data to (timestamps × symbols) matrix
2. Per-row: numpy argsort descending → take head/tail n_q → compute mean difference

### Quantile Spread (standard)
Not vectorized — uses pd.qcut with `duplicates="drop"`. Retained as reference path.

## Benchmark (2000 timestamps × 50 symbols)

| Operation | Reference | Vectorized | Speedup |
|-----------|-----------|------------|---------|
| RankIC | 9.72s | 0.28s | 35x |
| Legacy Spread | 6.79s | 0.26s | 27x |

## Estimated Full Run Time

Previous: ~30-35 minutes
Expected: ~3 minutes (vectorized RankIC + legacy spread; standard spread still reference)

## Not Changed

- Public API signatures
- Default spread mode (standard)
- Reference implementations (kept as fallback)
- Research results
- Phase 13 status (NOT STARTED)
