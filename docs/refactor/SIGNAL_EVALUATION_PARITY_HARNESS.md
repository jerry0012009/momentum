# Signal Evaluation Parity Harness

> Phase 12D-H2-S · 2026-06-19

## Purpose

Verify that the public `signal_evaluation` API reproduces old Phase 10A outputs. H2-R removed inline functions; H2-S corrects gate logic and RankIC status.

## Public API Used

```python
from momentum.signal_evaluation import (
    select_forward_return, compute_rank_ic, summarize_rank_ic,
    compute_quantile_spread, summarize_quantile_spread,
    check_rankic_spread_consistency,
)
```

## Results

### RankIC Parity

| Status | Meaning |
|--------|---------|
| EXACT | diff ≤ 1e-9 (float64 precision) |
| PASS_ROUNDED_REFERENCE | diff ≤ 0.5e-6 — old CSV stores 6 decimal places |
| NEEDS_INVESTIGATION | diff unexplained |

**Current**: 12/12 PASS_ROUNDED_REFERENCE. All diffs ~1e-7, explained by old CSV precision (6 decimal places).

### Quantile Spread Parity

| Status | Meaning |
|--------|---------|
| EXACT | Exact match |
| BEHAVIORAL | Same direction, diff < 2e-3 |
| NEEDS_INVESTIGATION | Direction mismatch |

**Current**: 12/12 BEHAVIORAL. Root cause: old uses rank-based head/tail, new uses pd.qcut quintile boundaries. See `SIGNAL_EVALUATION_SPREAD_PARITY_INVESTIGATION.md`.

### H3 Gate Status

| Gate | Conditions | Current |
|------|------------|---------|
| OPEN_FULL_WRAPPER | All exact | — |
| OPEN_FOR_RANKIC_WRAPPER_ONLY | RankIC pass + spread behavioral | **✓ Current** |
| BLOCK_FULL_WRAPPER_UNTIL_SPREAD_EXACT | Spread not exact | — |
| BLOCKED | Investigate/missing | — |

## Files

| File | Description |
|------|-------------|
| `phase12d_h2_s_signal_eval_parity_rankic.csv` | RankIC parity |
| `phase12d_h2_s_signal_eval_parity_quantile_spread.csv` | Spread parity |
| `phase12d_h2_s_signal_eval_parity_summary.csv` | Summary with H3 gate |
| `SIGNAL_EVALUATION_SPREAD_PARITY_INVESTIGATION.md` | Spread root-cause analysis |
| `phase12d_h2_s_spread_root_cause.csv` | Root cause data |
