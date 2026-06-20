# PM-02A Default Dataset Contract Patch

**Date:** 2026-06-21
**Follows:** PM-01 (`docs/factor_library/audits/pm01_canonical_pipeline_reality_audit.md`)

## Summary

Aligned the default dataset ID across the factor pipeline so that all active scripts default to the canonical dataset `crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1`. Previously, `build_factor_values.py` defaulted to `crypto_top50_usdt_perp_1h`, causing a silent path split with downstream evaluators.

## Files changed

| File | Change |
|------|--------|
| `scripts/build_factor_values.py` | Added `DEFAULT_DATASET_ID` constant; changed `--dataset-id` default from `crypto_top50_usdt_perp_1h` to canonical ID; improved preflight error message with path and hint |
| `scripts/evaluate_factors.py` | Added `DEFAULT_DATASET_ID` constant; added `--dataset-id` argument; resolved `features_dir`/`labels_path` from selected dataset; added labels-missing error; updated manifest to use `args.dataset_id` |
| `scripts/build_phase9b_signal_panel.py` | Added `DEFAULT_DATASET_ID` constant; added `--dataset-id` argument with argparse; added preflight check for all 10 factor value files; prints dataset and features path |
| `scripts/run_factor_intake.py` | Now passes `--dataset-id args.dataset_id` to `evaluate_factors.py` subprocess |

## Before / After

| Aspect | Before | After |
|--------|--------|-------|
| `build_factor_values.py` default | `crypto_top50_usdt_perp_1h` | `crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1` |
| `evaluate_factors.py` --dataset-id | Not available | Available, default = canonical ID |
| `build_phase9b_signal_panel.py` --dataset-id | Not available | Available, default = canonical ID |
| `run_factor_intake.py` → evaluate_factors | Did not pass --dataset-id | Passes --dataset-id |
| Missing bars error | `FileNotFoundError` (traceback) | Clear message with path + hint |
| Missing labels error | `FileNotFoundError` (traceback) | Clear message with path + hint |
| Missing factor values (signal panel) | `FileNotFoundError` per factor | Lists all missing + hint |

## Validation commands run

```bash
python -m py_compile scripts/build_factor_values.py scripts/evaluate_factors.py scripts/build_phase9b_signal_panel.py scripts/run_factor_intake.py
# Result: OK

python scripts/build_factor_values.py --help
python scripts/evaluate_factors.py --help
python scripts/build_phase9b_signal_panel.py --help
python scripts/run_factor_intake.py --help
# All show --dataset-id with correct default
```

## Smoke evaluation

Not run — full evaluation requires complete data and takes ~44 min. The changes are parameter-default swaps and do not alter computation logic.

## Intentionally not modified

- Factor formulas (`factor_formula_registry.py`) — not changed
- Factor ops (`factor_ops.py`) — not changed
- Factor specs (`factor_specs.py`) — not changed
- Signal weights, winsorization, z-scoring, liquidity gate, position overlay — not changed
- Universe construction logic — not changed
- Public HTML pages — not changed
- Generated parquet files — not changed
- Labels — not changed
- No production/live/alpha/tradeability claims
