# PM-05 Stale Dataset Reference Cleanup

**Date:** 2026-06-21
**Follows:** PM-04 (PASS_WITH_WARNINGS)

## Summary

Resolved all PM-04 warnings about stale `crypto_top50_usdt_perp_1h` dataset references in supporting/non-mainline scripts. 4 scripts deleted, 5 scripts updated to canonical dataset ID.

## Per-candidate audit

| path | action | stale_refs_before | active_code_refs | active_doc_refs | change_made | remaining_refs | risk | validation |
|------|--------|------------------|-----------------|----------------|------------|---------------|------|-----------|
| scripts/apply_factor_warning_flags.py | DELETED_STALE | 1 (UNIVERSE constant) | 0 | manifest (removed) | deleted | 0 | LOW | grep scripts/ src/ |
| scripts/audit_crypto_factor_results.py | UPDATED_TO_CANONICAL | 2 (UNIVERSE + help text) | 0 | register ACTIVE_SUPPORTING | UNIVERSE → canonical, help text → f-string | 0 | LOW | py_compile + grep |
| scripts/fetch_crypto_top50_bars.py | DELETED_STALE | 1 (CACHE path) | 0 | none | deleted | 0 | LOW | grep scripts/ src/ |
| scripts/fetch_crypto_long_window.py | DELETED_STALE | 1 (DEFAULT_CACHE path) | 0 | none | deleted | 0 | LOW | grep scripts/ src/ |
| scripts/build_crypto_native_caches.py | DELETED_STALE | 1 (--static-dataset-id default) | 0 | none | deleted | 0 | LOW | grep scripts/ src/ |
| scripts/run_signal_evaluation_parity_harness.py | UPDATED_TO_CANONICAL | 2 (OLD_LABEL_FILE + LABEL_FILE) | 0 | register ACTIVE_SUPPORTING | both paths → canonical labels.parquet | 0 | LOW | py_compile + grep |
| scripts/run_phase11a_cost_slippage_capacity.py | UPDATED_TO_CANONICAL | 1 (FWD path) | 0 | register ACTIVE_SUPPORTING | FWD → canonical labels.parquet | 0 | LOW | py_compile + grep |
| scripts/run_phase11b_liquidity_capacity.py | UPDATED_TO_CANONICAL | 1 (FWD path) | 0 | register ACTIVE_SUPPORTING | FWD → canonical labels.parquet | 0 | LOW | py_compile + grep |
| scripts/run_phase12b_paper_monitoring.py | UPDATED_TO_CANONICAL | 1 (forward_returns path) | 0 | register ACTIVE_SUPPORTING | fp → canonical labels.parquet | 0 | LOW | py_compile + grep |

## Counts

- Scripts updated: 5
- Scripts deleted: 4
- Governance files updated: 2 (manifest, this audit note)
- Remaining stale `crypto_top50_usdt_perp_1h` refs in scripts/: **0**

## Non-change statement

No data, factor logic, signal logic, universe logic, labels, factor values, evaluation outputs, signal panels, or public result pages were changed.

## Validation

```bash
python -m py_compile scripts/audit_crypto_factor_results.py scripts/run_signal_evaluation_parity_harness.py scripts/run_phase11a_cost_slippage_capacity.py scripts/run_phase11b_liquidity_capacity.py scripts/run_phase12b_paper_monitoring.py scripts/download_full_binance_1h_universe.py scripts/build_dynamic_universe_monthly_volume.py scripts/build_labels.py scripts/build_factor_values.py scripts/evaluate_factors.py scripts/run_factor_intake.py scripts/build_factor_library_state.py scripts/build_phase9b_signal_panel.py scripts/evaluate_signals.py scripts/check_factor_ic_parity.py
# ALL OK

grep -rn "crypto_top50_usdt_perp_1h" scripts/
# No matches
```
