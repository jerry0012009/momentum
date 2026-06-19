# Signal Evaluation Performance

> Phase 12D-H4 · 2026-06-19

## Previous Bottleneck

`compute_rank_ic` and `compute_quantile_spread` used per-timestamp Python for-loops over ~17,520 timestamps. Each iteration called pandas `.corr()` (Spearman) or `.sort_values()`. Total: ~30-35 minutes for 3 signals × 4 horizons.

## Vectorization Strategy

### RankIC
1. Pivot long data to (timestamps × symbols) matrix
2. Rank each row using numpy argsort (NaN-aware)
3. Compute row-wise Pearson correlation via vectorized numpy operations

### Quantile Spread (legacy_phase10a)
1. Pivot long data to (timestamps × symbols) matrix
2. Per-row: numpy argsort descending → take head/tail n_q → compute mean difference

### Quantile Spread (standard)
Not vectorized — uses pd.qcut with `duplicates="drop"` which is inherently per-group. Retained as reference path.

## Implementation

| File | Change |
|------|--------|
| `src/momentum/signal_evaluation/_vectorized.py` | New: vectorized RankIC + legacy spread |
| `src/momentum/signal_evaluation/rank_ic.py` | Updated: fast path with reference fallback |
| `src/momentum/signal_evaluation/quantile_spread.py` | Updated: fast path for legacy mode |

Public API unchanged. No new user-facing parameters.

## Parity

| Metric | Status | Max Diff |
|--------|--------|----------|
| RankIC (vectorized vs reference) | PASS | 1.11e-16 |
| Legacy Spread (vectorized vs reference) | PASS | 0.00e+00 |

## Benchmark (2000 timestamps × 50 symbols)

| Operation | Reference | Vectorized | Speedup |
|-----------|-----------|------------|---------|
| RankIC | 9.72s | 0.28s | 35x |
| Legacy Spread | 6.79s | 0.26s | 27x |

## Estimated Full Run Time

Previous: ~30-35 minutes (3 signals × 4 horizons × ~35s each)
Expected: ~1-2 minutes (35x speedup on ~17,520 timestamps)

## Not Changed

- Public API signatures
- Default spread mode (standard)
- Reference implementations (kept as fallback)
- Research results
- Phase 13 status (NOT STARTED)
