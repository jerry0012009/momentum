# Active Signal Evaluation Pipeline

> Canonical reference for the active signal evaluation pipeline.

## Active Entrypoint

**`scripts/evaluate_signals.py`** — single CLI entrypoint for all signal evaluation.

```bash
python scripts/evaluate_signals.py \
    --signal-panel <path> \
    --labels <path> \
    --signals signal_v0_core_only signal_v0_pm_full_structured \
    --horizons 1h 4h 24h 72h \
    --output-dir <dir> \
    [--spread-mode standard|legacy_phase10a]
```

## Active Module

**`src/momentum/signal_evaluation/`** — reusable Python package.

| Function | Purpose |
|----------|---------|
| `select_forward_return()` | Label adapter |
| `compute_rank_ic()` | Per-timestamp Spearman IC |
| `summarize_rank_ic()` | Mean IC, t-stat, periods |
| `compute_quantile_spread()` | Top-bottom bucket spread |
| `summarize_quantile_spread()` | Mean/median/std spread + hit rate |
| `check_rankic_spread_consistency()` | Cross-metric sanity check |

## Active Outputs

| File | Content |
|------|---------|
| `signal_evaluation_rankic_summary.csv` | RankIC results |
| `signal_evaluation_quantile_spread_summary.csv` | Spread results |
| `signal_evaluation_consistency_summary.csv` | Consistency checks |
| `signal_evaluation_manifest.json` | Run metadata |

## Legacy Scripts (Archived)

Old Phase 10 scripts are archived under `archive/legacy_phase_scripts/phase10/`:

| Script | Status |
|--------|--------|
| `run_phase10a_signal_backtest.py` | Archived (historical reference) |
| `run_phase10a_r_diagnostics.py` | Archived (historical reference) |
| `run_phase10b_tail_diagnostics.py` | Archived (historical reference) |
| `run_phase10d_tail_aware_variants.py` | Archived (historical reference) |

**Do not use archived scripts for new research.** They are retained for historical reference only.

## Legacy Outputs

Old output files (`phase10a_signal_rankic_summary.csv`, etc.) in `research/factor_runs/crypto_top50_factor_library/` are **historical artifacts**. They are not active pipeline outputs. The new pipeline writes `signal_evaluation_*.csv` files.

## Spread Modes

| Mode | Algorithm | Use Case |
|------|-----------|----------|
| `standard` (default) | pd.qcut quintile boundaries | New analyses |
| `legacy_phase10a` | rank-based head/tail | Historical parity checks only |

Default is `standard`. Use `legacy_phase10a` only when reproducing old Phase 10A results.
