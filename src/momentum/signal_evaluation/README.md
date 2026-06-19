# Signal Evaluation Framework

Reusable signal-level evaluation functions for the momentum factor library.

## Status

**Skeleton (v0.1.0)** — core metrics extracted as pure functions.
Old phase scripts (10A/10B/10D) remain as historical audit entry points.
This package does **not** change any research results.

## Modules

| Module | Function | Purpose |
|--------|----------|---------|
| `schema.py` | — | Input schema definitions (signal panel, label panel) |
| `rank_ic.py` | `compute_rank_ic` | Per-timestamp cross-sectional Spearman correlation |
| `rank_ic.py` | `summarize_rank_ic` | Mean/std/t-stat/positive_fraction over time |
| `quantile_spread.py` | `compute_quantile_spread` | Top-minus-bottom bucket spread |
| `quantile_spread.py` | `summarize_quantile_spread` | Mean/median/std/positive_fraction over time |
| `consistency.py` | `check_rankic_spread_consistency` | Direction agreement check |

## Input Format

### Signal Panel (required)
- `timestamp`, `symbol`, `signal_name`, `signal_value`

### Label Panel — tidy format (recommended)
- `timestamp`, `symbol`, `horizon`, `forward_return`

### Label Panel — wide format (also supported)
- `timestamp`, `symbol`, `ret_fwd_1h`, `ret_fwd_4h`, `ret_fwd_24h`, `ret_fwd_72h`

Long-term recommendation: use tidy format (horizon as a column).

## Usage

```python
from momentum.signal_evaluation import compute_rank_ic, summarize_rank_ic

ric_df = compute_rank_ic(signal_df, label_df)
summary = summarize_rank_ic(ric_df)
print(summary["mean_rank_ic"], summary["t_stat"])
```

## What This Does NOT Do

- Does not replace old phase scripts
- Does not run backtests
- Does not generate trade signals
- Does not connect to any exchange
