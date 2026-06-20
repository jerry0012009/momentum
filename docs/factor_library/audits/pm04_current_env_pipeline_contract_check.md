# PM-04 Current Environment Pipeline Contract Check

**Date:** 2026-06-21
**Verdict:** `PASS_WITH_WARNINGS`

---

## A. Summary Verdict

**PASS_WITH_WARNINGS** — The active mainline pipeline is correctly contracted. All core artifacts exist. All 15 active scripts compile clean. The canonical dataset ID is consistently used in active mainline scripts. Some supporting scripts still reference old dataset IDs (warning, not blocker).

---

## B. Current Canonical Command Sequence

| step | command | input | output | run_now? | notes |
|------|---------|-------|--------|----------|-------|
| 1 | `python scripts/download_full_binance_1h_universe.py` | Binance API | `data/cache/.../bars_1h.parquet` | no | ~127M, 3.3M rows |
| 2 | `python scripts/build_dynamic_universe_monthly_volume.py --universe-id crypto_usdt_perp_monthly_volume_top50_current_listed_v1` | bars_1h.parquet | `data/universe/.../universe_snapshots.parquet` | no | 1,250 rows, 25 months |
| 3 | `python scripts/build_labels.py --dataset-id crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1` | bars_1h.parquet | `data/features/.../labels.parquet` | no | 3.3M rows, matches bars |
| 4 | `python scripts/build_factor_values.py --dataset-id crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1` | bars_1h.parquet, registry | `data/features/.../factor_values.parquet` (×59) | no | 59 computed, 6 missing |
| 5 | `python scripts/evaluate_factors.py --dataset-id crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1` | factor_values, labels | `research/factor_runs/.../factor_level_evaluation/` | no | Full IC evaluation |
| 6 | `python scripts/run_factor_intake.py --factor-ids <ids> --run-id <id> --dataset-id crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1` | factor_values, labels | intake report + eval | no | Per-factor intake |
| 7 | `python scripts/build_factor_library_state.py` | registry, catalog, evals | `research/.../factor_library_state.json` | no | 65 registered, 59 computed |
| 8 | `python scripts/build_phase9b_signal_panel.py --dataset-id crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1` | 10 active factors | `research/.../phase9b_signal_panel.parquet` | no | 3.3M rows, 215M |
| 9 | `python scripts/evaluate_signals.py --signal-panel ... --labels ...` | signal panel, labels | signal eval CSVs | no | Uses explicit paths |

---

## C. Artifact Table

| artifact | exists | size_or_rows | authority_script | status | notes |
|----------|--------|-------------|-----------------|--------|-------|
| `data/cache/.../bars_1h.parquet` | ✅ | 127M, 3,316,259 rows | download_full_binance_1h_universe.py | OK | |
| `data/universe/.../universe_snapshots.parquet` | ✅ | 25K, 1,250 rows | build_dynamic_universe_monthly_volume.py | OK | 25 months × 50 symbols |
| `data/universe/.../monthly_selection_detail.parquet` | ✅ | 18K, 25 rows | build_dynamic_universe_monthly_volume.py | OK | |
| `data/features/.../labels.parquet` | ✅ | 110M, 3,316,259 rows | build_labels.py | OK | Row count matches bars |
| `data/features/.../factor_values.parquet` (×59) | ✅ | ~40M each | build_factor_values.py | OK | 59 computed |
| `research/.../factor_library_state.json` | ✅ | 8.0K | build_factor_library_state.py | OK | 65 registered, 59 computed, 6 missing |
| `research/.../phase9b_signal_panel.parquet` | ✅ | 215M, 3,314,397 rows | build_phase9b_signal_panel.py | OK | 10 active signal factors |

---

## D. Dataset Consistency Table

| script_or_doc | dataset_or_universe_id | status | notes |
|---------------|----------------------|--------|-------|
| `build_dynamic_universe_monthly_volume.py` | `crypto_usdt_perp_monthly_volume_top50_current_listed_v1` | OK | canonical universe |
| `build_labels.py` | `crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1` | OK | canonical dataset |
| `build_factor_values.py` | `crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1` | OK | DEFAULT_DATASET_ID |
| `evaluate_factors.py` | `crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1` | OK | DEFAULT_DATASET_ID |
| `run_factor_intake.py` | `crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1` | OK | passes to sub-scripts |
| `build_phase9b_signal_panel.py` | `crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1` | OK | DEFAULT_DATASET_ID |
| `factor_library_state.json` | `crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1` | OK | matches canonical |
| `scripts/apply_factor_warning_flags.py` | `crypto_top50_usdt_perp_1h` | WARNING | stale ID, supporting script |
| `scripts/audit_crypto_factor_results.py` | `crypto_top50_usdt_perp_1h` | WARNING | stale ID, supporting script |
| `scripts/fetch_crypto_top50_bars.py` | `crypto_top50_usdt_perp_1h` | WARNING | stale ID, non-mainline |
| `scripts/fetch_crypto_long_window.py` | `crypto_top50_usdt_perp_1h` | WARNING | stale ID, non-mainline |
| `scripts/build_crypto_native_caches.py` | `crypto_top50_usdt_perp_1h` | WARNING | stale ID, non-mainline |
| `scripts/run_signal_evaluation_parity_harness.py` | `crypto_top50_usdt_perp_1h` | WARNING | stale ID, supporting script |
| `scripts/run_phase11a_cost_slippage_capacity.py` | `crypto_top50_usdt_perp_1h` | WARNING | stale ID, non-mainline |
| `scripts/run_phase11b_liquidity_capacity.py` | `crypto_top50_usdt_perp_1h` | WARNING | stale ID, non-mainline |
| `scripts/run_phase12b_paper_monitoring.py` | `crypto_top50_usdt_perp_1h` | WARNING | stale ID, supporting script |

---

## E. Warnings / Blockers

### Warnings (acceptable, do not block current work)

1. **~10 supporting/non-mainline scripts still reference old `crypto_top50_usdt_perp_1h`** — These are not part of the active mainline pipeline. They can be fixed in a future cleanup pass. No blocker.

2. **6 factors missing input data** — taker_buy_ratio_20h, taker_buy_zscore_20h, taker_buy_delta_5h, funding_rate_level_20h, funding_rate_zscore_80h, funding_rate_change_24h. These require taker-buy and funding-rate data that is not yet downloaded. Not a pipeline contract issue.

3. **`evaluate_signals.py` uses explicit file paths** not `--dataset-id` — This is by design; the script takes `--signal-panel` and `--labels` paths directly.

### Blockers

None.

---

## F. Non-Change Statement

No data, factor logic, signal logic, universe data, labels, factor values, evaluation outputs, or public result pages were changed in this audit.
