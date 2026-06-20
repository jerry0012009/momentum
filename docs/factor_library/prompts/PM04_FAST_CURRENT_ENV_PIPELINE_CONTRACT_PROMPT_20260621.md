# PM-04 Prompt — Fast Current-Environment Pipeline Contract Check

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows:

- PM-01: Canonical pipeline reality audit
- PM-02A: Default dataset contract repair
- PM-02B: Canonical monthly universe builder + stale universe builder deletion
- PM-03: Stale/orphan batch cleanup

The user does **not** need full cross-machine portability right now. Do not over-engineer for a new environment. The immediate goal is to quickly confirm that the current repository, in the current server environment, has a clear active factor-library pipeline contract.

## 0. Current PM objective

Move quickly. This is a short bridge task before PM-05.

The goal is to answer:

1. What is the current canonical command sequence for the active factor-library pipeline?
2. Do the active commands point to the same dataset/universe IDs?
3. Do the expected current artifacts exist in the current environment?
4. Is there any remaining obvious mismatch between docs/manifest/register and actual scripts?

Do not try to make the repo portable across arbitrary machines in this task.

## 1. Current canonical IDs

Use these as current truth unless the repository itself proves otherwise:

- Universe ID: `crypto_usdt_perp_monthly_volume_top50_current_listed_v1`
- Dataset ID: `crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1`
- Research run folder: `research/factor_runs/crypto_top50_factor_library/`

## 2. Active mainline scripts to check

Check these scripts only as active mainline:

- `scripts/download_full_binance_1h_universe.py`
- `scripts/build_dynamic_universe_monthly_volume.py`
- `scripts/build_labels.py`
- `scripts/build_factor_values.py`
- `scripts/evaluate_factors.py`
- `scripts/run_factor_intake.py`
- `scripts/build_factor_library_state.py`
- `scripts/build_phase9b_signal_panel.py`
- `scripts/evaluate_signals.py`

Also check these active support scripts only for compile/import consistency, not business redesign:

- `scripts/build_factor_redundancy.py`
- `scripts/build_factor_conclusion_cards.py`
- `scripts/generate_intake_report.py`
- `scripts/promote_factor_intake.py`
- `scripts/check_factor_registry_integrity.py`
- `scripts/check_factor_ic_parity.py`

## 3. Strict prohibitions

Do **not** regenerate raw data.

Do **not** run long downloads.

Do **not** regenerate universe parquet files.

Do **not** regenerate labels.

Do **not** regenerate factor values.

Do **not** run full factor evaluation.

Do **not** rebuild signal panel.

Do **not** run full signal evaluation.

Do **not** change factor formulas, factor ops, factor specs, or signal weights.

Do **not** add a general config framework.

Do **not** add a new pipeline orchestrator.

Do **not** add a new directory tree.

Do **not** do another broad deletion pass.

Do **not** edit public result pages unless a one-line stale reference is clearly wrong.

## 4. Allowed work

Allowed changes are intentionally small:

- Create one audit note:
  - `docs/factor_library/audits/pm04_current_env_pipeline_contract_check.md`
- Update `docs/factor_library/START_HERE.md` only if the canonical command sequence is missing or stale.
- Update `docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md` only if its active command sequence is stale.
- Update `docs/factor_library/factor_library_manifest.json` only if a script/path/status is clearly inconsistent with the current active pipeline.
- Update `docs/factor_library/FILE_STATUS_REGISTER.csv` only if the audit finds a concrete mismatch.
- Make a tiny code change only if one of the active scripts has an obvious dataset default mismatch or help-text mismatch discovered during `--help` checks.

If no code change is necessary, do not force one.

## 5. Required checks

### 5.1 Git state

```bash
git status --short
```

### 5.2 Compile checks

Run:

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
  scripts/build_factor_redundancy.py \
  scripts/build_factor_conclusion_cards.py \
  scripts/generate_intake_report.py \
  scripts/promote_factor_intake.py \
  scripts/check_factor_registry_integrity.py \
  scripts/check_factor_ic_parity.py
```

### 5.3 Help checks

Run `--help` for these scripts:

```bash
python scripts/build_dynamic_universe_monthly_volume.py --help
python scripts/build_labels.py --help
python scripts/build_factor_values.py --help
python scripts/evaluate_factors.py --help
python scripts/run_factor_intake.py --help
python scripts/build_phase9b_signal_panel.py --help
python scripts/evaluate_signals.py --help
```

Do not run heavy workflows.

### 5.4 Artifact existence checks

Check whether these current artifacts exist and record row counts / file sizes when cheap:

```text
data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet
data/universe/crypto_usdt_perp_monthly_volume_top50_current_listed_v1/universe_snapshots.parquet
data/universe/crypto_usdt_perp_monthly_volume_top50_current_listed_v1/monthly_selection_detail.parquet
data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/labels.parquet
data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/<some active factor>/factor_values.parquet
research/factor_runs/crypto_top50_factor_library/factor_library_state.json
research/factor_runs/crypto_top50_factor_library/phase9b_signal_panel.parquet
```

Use lightweight Python snippets if needed, e.g. read parquet metadata / head / row count. Avoid loading very large files into memory if unnecessary.

### 5.5 Dataset/default consistency check

Search active scripts for old/stale dataset IDs:

```bash
rg -n "crypto_top50_usdt_perp_1h|crypto_top50_usdt_perp_monthly_volume_top50_current_listed_v1|crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1|crypto_usdt_perp_monthly_volume_top50_current_listed_v1" scripts docs/factor_library reports/site/factor-library/assets || true
```

Classify any occurrence of old names as:

- active current path
- deleted/stale historical reference
- archive/prompt/audit reference
- harmless legacy output folder
- problematic active reference

Do not edit historical audit/prompt references.

## 6. Required output: audit note

Create:

`docs/factor_library/audits/pm04_current_env_pipeline_contract_check.md`

It must include:

### A. Summary verdict

One of:

- `PASS_CURRENT_ENV_CONTRACT`
- `PASS_WITH_WARNINGS`
- `FAIL_NEEDS_PM_FIX`

### B. Current canonical command sequence

Write the current command sequence as a concise table:

```text
step | command | input | output | run_now? | notes
```

Do not invent commands that do not exist.

For heavy commands, set `run_now? = no` and explain that only contract was checked.

### C. Artifact table

```text
artifact | exists | size_or_rows | authority_script | status | notes
```

### D. Dataset consistency table

```text
script_or_doc | dataset_or_universe_id | status | notes
```

### E. Warnings / blockers

Separate warnings from blockers.

A warning is acceptable if current work can continue.

A blocker means the next PM task must fix it before factor intake or signal work continues.

### F. Non-change statement

Explicitly state whether any data, factor logic, signal logic, or public result pages changed.

## 7. Optional minimal docs update

If the audit finds that START_HERE or Control Center still points to stale commands, update only the relevant command lines.

Do not rewrite the docs.

## 8. Commit rules

Before committing, run:

```bash
git diff --stat
git diff -- docs/factor_library/audits/pm04_current_env_pipeline_contract_check.md docs/factor_library/START_HERE.md docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md docs/factor_library/factor_library_manifest.json docs/factor_library/FILE_STATUS_REGISTER.csv
```

Commit with:

```bash
docs: add current environment pipeline contract check
```

Final response should include:

- commit hash
- summary verdict
- files changed
- validation checks run
- warnings
- blockers

