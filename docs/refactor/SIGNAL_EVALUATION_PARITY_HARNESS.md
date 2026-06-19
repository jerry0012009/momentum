# Signal Evaluation Parity Harness

> Phase 12D-H2-T · 2026-06-19

## Purpose

Verify that the public `signal_evaluation` API reproduces old Phase 10A outputs using legacy_phase10a spread mode.

## Public API Used

```python
from momentum.signal_evaluation import (
    select_forward_return, compute_rank_ic, summarize_rank_ic,
    compute_quantile_spread, summarize_quantile_spread,
    check_rankic_spread_consistency,
)
```

## Spread Modes

| Mode | Algorithm | Use Case |
|------|-----------|----------|
| `standard` (default) | pd.qcut quintile boundaries | New analyses |
| `legacy_phase10a` | rank-based sort + head/tail | Exact Phase 10A reproducibility |

## Rounding Tolerances

| Field | Old CSV Precision | Rounding Tolerance |
|-------|-------------------|--------------------|
| mean_rankic | 6 decimal places | 0.5e-6 |
| t_stat | 5 decimal places | 0.5e-4 |
| mean_spread | 6 decimal places | 0.5e-6 |
| hit_rate (positive_fraction) | 4 decimal places | 0.5e-4 |
| n_periods / n_timestamps | exact integer | 0 |

## H3 Gate Logic

| Gate | Conditions |
|------|------------|
| OPEN_FULL_WRAPPER | RankIC pass + spread legacy pass (exact/rounded) |
| OPEN_STANDARD_V2_ONLY | RankIC pass + spread legacy behavioral only |
| BLOCKED | Investigate/missing |

## Output Files

| File | Description |
|------|-------------|
| `phase12d_h2_t_signal_eval_parity_rankic.csv` | RankIC parity |
| `phase12d_h2_t_signal_eval_parity_spread_legacy.csv` | Spread parity (legacy mode) |
| `phase12d_h2_t_signal_eval_parity_spread_standard.csv` | Spread parity (standard, reference) |
| `phase12d_h2_t_signal_eval_parity_summary.csv` | Summary with H3 gate |
