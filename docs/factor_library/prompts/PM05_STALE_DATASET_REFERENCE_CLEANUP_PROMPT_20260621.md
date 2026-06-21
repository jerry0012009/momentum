# PM-05 Prompt — Stale Dataset Reference Cleanup in Supporting Scripts

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-04:

- `docs/factor_library/audits/pm04_current_env_pipeline_contract_check.md`

PM-04 verdict was `PASS_WITH_WARNINGS`. The active mainline pipeline is contracted and not blocked, but PM-04 found that several supporting or non-mainline scripts still reference old dataset IDs such as `crypto_top50_usdt_perp_1h`.

The user's priority is to keep the repository clean and prevent future agents from using stale paths. This task should clean up those stale references in one bounded pass.

## 0. Current canonical truth

Use these IDs as current active factor-library truth:

- Universe ID: `crypto_usdt_perp_monthly_volume_top50_current_listed_v1`
- Dataset ID: `crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1`
- Research run folder: `research/factor_runs/crypto_top50_factor_library/`

Current active mainline scripts include:

- `scripts/download_full_binance_1h_universe.py`
- `scripts/build_dynamic_universe_monthly_volume.py`
- `scripts/build_labels.py`
- `scripts/build_factor_values.py`
- `scripts/evaluate_factors.py`
- `scripts/run_factor_intake.py`
- `scripts/build_factor_library_state.py`
- `scripts/build_phase9b_signal_panel.py`
- `scripts/evaluate_signals.py`

Do not modify active mainline computation logic in this task.

## 1. PM-05 objective

Resolve PM-04 warning class:

> Supporting/non-mainline scripts still reference old `crypto_top50_usdt_perp_1h` dataset ID.

For each script with stale dataset references, decide one of:

1. **UPDATE_TO_CANONICAL** — if the script is still useful and should operate on the current canonical dataset.
2. **DELETE_STALE** — if the script is historical/non-mainline, has no active code refs, and would mislead future agents.
3. **KEEP_HISTORICAL_WITH_LABEL** — if it should remain for historical reference only.
4. **BLOCKED_REVIEW** — if active code depends on it and the correct fix is not obvious.

Do not blindly replace strings. Inspect each file's role first.

## 2. Candidate scripts from PM-04 warning table

Start with these files if present:

- `scripts/apply_factor_warning_flags.py`
- `scripts/audit_crypto_factor_results.py`
- `scripts/fetch_crypto_top50_bars.py`
- `scripts/fetch_crypto_long_window.py`
- `scripts/build_crypto_native_caches.py`
- `scripts/run_signal_evaluation_parity_harness.py`
- `scripts/run_phase11a_cost_slippage_capacity.py`
- `scripts/run_phase11b_liquidity_capacity.py`
- `scripts/run_phase12b_paper_monitoring.py`

Also search for any other active non-archive references to:

- `crypto_top50_usdt_perp_1h`
- `crypto_top50_usdt_perp_monthly_volume_top50_current_listed_v1`

Do not edit historical PM audit/prompt/archive references unless they are active instructions.

## 3. Strict prohibitions

Do **not** change factor formulas.

Do **not** change signal construction weights or factor list.

Do **not** change universe data or universe generation logic.

Do **not** regenerate bars, labels, factor values, factor evaluations, signal panels, signal evaluations, cost outputs, paper outputs, or public result pages.

Do **not** run long downloads.

Do **not** add a new config framework.

Do **not** add a new pipeline orchestrator.

Do **not** edit `src/momentum/strategies/`.

Do **not** perform another broad repository deletion pass. This task only targets stale dataset-reference scripts found by PM-04 and their governance records.

## 4. Required pre-change checks

Run:

```bash
git status --short
```

Search stale dataset refs:

```bash
rg -n "crypto_top50_usdt_perp_1h|crypto_top50_usdt_perp_monthly_volume_top50_current_listed_v1" scripts docs/factor_library reports/site/factor-library/assets reports/site/factor-library/*.html || true
```

For each candidate script, check whether any active code calls/imports it:

```bash
rg -n "apply_factor_warning_flags|audit_crypto_factor_results|fetch_crypto_top50_bars|fetch_crypto_long_window|build_crypto_native_caches|run_signal_evaluation_parity_harness|run_phase11a_cost_slippage_capacity|run_phase11b_liquidity_capacity|run_phase12b_paper_monitoring" scripts src docs/factor_library reports/site/factor-library || true
```

Classify every reference as:

- active code import/subprocess
- active governance/doc reference
- public site reference
- historical audit/prompt/archive reference
- self-reference only

Only active code refs block deletion.

## 5. Expected decisions by file type

Use judgment, but default to the following principles:

### 5.1 Parity / QA scripts

`run_signal_evaluation_parity_harness.py` is likely active-supporting. If it only has stale defaults, update it to current canonical dataset/path. Do not delete unless proven unused and duplicated by a better current script.

### 5.2 Cost/liquidity/paper diagnostic scripts

`run_phase11a_cost_slippage_capacity.py`, `run_phase11b_liquidity_capacity.py`, and `run_phase12b_paper_monitoring.py` may still be useful as diagnostic tools. If they only reference stale dataset IDs or labels paths, update the default paths to canonical current dataset.

Do not change their diagnostic logic.

### 5.3 Old fetch/cache scripts

`fetch_crypto_top50_bars.py`, `fetch_crypto_long_window.py`, and `build_crypto_native_caches.py` are likely old data-fetch/cache scripts. If they are not active code dependencies and overlap with current `download_full_binance_1h_universe.py` or `build_dynamic_universe_monthly_volume.py`, prefer deleting them or marking them historical. Do not leave misleading old fetchers in `scripts/` if unused.

### 5.4 Audit/flag helper scripts

`apply_factor_warning_flags.py` and `audit_crypto_factor_results.py` may be useful only if current docs or site builders use them. Inspect before deciding. If retained, update stale dataset references to canonical. If unused and historical, delete.

## 6. Allowed changes

Allowed code changes:

- Update stale default dataset/path strings in retained supporting scripts.
- Delete unused stale supporting/non-mainline scripts from `scripts/` if reference checks permit.
- Do not change core computation algorithms.

Allowed governance/docs changes:

- `docs/factor_library/FILE_STATUS_REGISTER.csv`
- `docs/factor_library/factor_library_manifest.json`
- `docs/factor_library/ORPHAN_WORK_AUDIT.md`
- `docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md` only if it references a changed/deleted script
- `docs/factor_library/START_HERE.md` only if it references a changed/deleted script
- `docs/factor_library/audits/pm05_stale_dataset_reference_cleanup.md`

Do not edit unrelated docs.

## 7. Required audit note

Create:

`docs/factor_library/audits/pm05_stale_dataset_reference_cleanup.md`

It must include a table:

```text
path | action | stale_refs_before | active_code_refs | active_doc_refs | change_made | remaining_refs | risk | validation
```

Actions:

- `UPDATED_TO_CANONICAL`
- `DELETED_STALE`
- `KEPT_HISTORICAL_WITH_LABEL`
- `BLOCKED_REVIEW`
- `NOT_FOUND`

Also include:

- total scripts updated
- total scripts deleted
- governance files updated
- remaining stale dataset refs and whether they are historical only
- explicit non-change statement: no data, factor logic, signal logic, universe logic, or public result outputs changed

## 8. Validation after changes

Run py_compile on all retained changed scripts and key active scripts:

```bash
python -m py_compile \
  scripts/download_full_binance_1h_universe.py \
  scripts/build_dynamic_universe_monthly_volume.py \
  scripts/build_labels.py \
  scripts/build_factor_values.py \
  scripts/evaluate_factors.py \
  scripts/run_factor_intake.py \
  scripts/build_factor_library_state.py \
  scripts/build_phase9b_signal_panel.py \
  scripts/evaluate_signals.py \
  scripts/check_factor_ic_parity.py \
  scripts/run_signal_evaluation_parity_harness.py
```

If any of the following files are retained, also compile them:

```bash
python -m py_compile \
  scripts/apply_factor_warning_flags.py \
  scripts/audit_crypto_factor_results.py \
  scripts/run_phase11a_cost_slippage_capacity.py \
  scripts/run_phase11b_liquidity_capacity.py \
  scripts/run_phase12b_paper_monitoring.py
```

Run stale-ref check again:

```bash
rg -n "crypto_top50_usdt_perp_1h|crypto_top50_usdt_perp_monthly_volume_top50_current_listed_v1" scripts docs/factor_library reports/site/factor-library/assets reports/site/factor-library/*.html || true
```

Expected result:

- No active retained script should use stale dataset IDs as defaults.
- Historical audit/prompt/archive references may remain.
- Deleted scripts may appear only in historical audit/prompt records.

## 9. Commit rules

Before commit:

```bash
git diff --stat
git diff -- scripts docs/factor_library reports/site/factor-library/assets reports/site/factor-library/*.html
```

Commit with:

```bash
chore: clean stale dataset references in supporting scripts
```

Final response should include:

- commit hash
- scripts updated
- scripts deleted
- files retained as historical
- validation commands run
- remaining warnings/blockers
