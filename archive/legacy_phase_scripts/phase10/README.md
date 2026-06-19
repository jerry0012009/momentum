# Legacy Phase Scripts — Archived

> These scripts are historical, inactive references. They are NOT part of the active pipeline.

## Active Entrypoint

**`scripts/evaluate_signals.py`** — canonical signal evaluation pipeline.

```bash
python scripts/evaluate_signals.py \
    --signal-panel <path> \
    --labels <path> \
    --signals signal_v0_core_only \
    --horizons 1h 4h 24h 72h \
    --output-dir <dir>
```

## Archived Scripts

| Script | Original Purpose | Archive Date |
|--------|-----------------|--------------|
| `run_phase10a_signal_backtest.py` | Old RankIC + Spread evaluation | 2026-06-19 |
| `run_phase10a_r_diagnostics.py` | Old diagnostic checks | 2026-06-19 |
| `run_phase10b_tail_diagnostics.py` | Old tail distribution analysis | 2026-06-19 |
| `run_phase10d_tail_aware_variants.py` | Old tail-aware signal variants | 2026-06-19 |

## Why Archived

These scripts used inline implementations for RankIC and Spread computation. The public `momentum.signal_evaluation` API now provides these functions with verified parity (see `SIGNAL_EVALUATION_PARITY_HARNESS.md`).

The new `evaluate_signals.py` uses the public API exclusively, is CLI-driven, and produces standardized outputs.

## Historical Outputs

Old output files (`phase10a_signal_rankic_summary.csv`, etc.) remain in `research/factor_runs/crypto_top50_factor_library/` and are untouched. The new pipeline writes differently named files (`signal_evaluation_*.csv`).
