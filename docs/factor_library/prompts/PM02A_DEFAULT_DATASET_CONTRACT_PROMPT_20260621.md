# PM-02A Prompt — Default Dataset Contract Repair

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-01 (`docs/factor_library/audits/pm01_canonical_pipeline_reality_audit.md` and `docs/factor_library/audits/pm01_pipeline_node_audit.csv`). PM-01 found that the current factor-library pipeline has a dataset contract problem: some active scripts default to or write into `crypto_top50_usdt_perp_1h`, while current factor evaluation, signal panel construction, factor intake, and factor library state use `crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1`.

Your task is to make the current crypto factor-library evaluation pipeline **default-correct** for the current canonical dataset, without changing factor logic, signal logic, universe membership, or research conclusions.

## 0. Current product boundary

The current active product goal is a research-grade crypto perpetual cross-sectional factor library.

The current dataset/universe target for factor evaluation and signal evaluation is:

`crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1`

Future universes such as US equities or Hong Kong equities may be supported later. Do **not** implement multi-universe abstraction in this task. The immediate goal is to make the current crypto monthly Top50 pipeline internally consistent and safer to run.

## 1. Scope

This is a narrow engineering hygiene task.

You may modify only these files unless a directly necessary test/import adjustment is discovered:

- `scripts/build_factor_values.py`
- `scripts/evaluate_factors.py`
- `scripts/build_phase9b_signal_panel.py`
- optionally `scripts/run_factor_intake.py` only if needed to ensure it passes the same dataset ID consistently
- optionally a small test file if an existing test framework already covers these scripts

Do not modify public HTML pages in this task.

Do not modify factor definitions.

Do not modify signal construction weights or factor list.

Do not modify universe construction logic.

Do not modify data files or generated parquet outputs.

Do not move, delete, rename, or archive files in this task.

Do not update `FILE_STATUS_REGISTER.csv`, manifest, README, START_HERE, or Control Center in this task unless the code change absolutely requires a one-line command example correction. Prefer not to touch docs here.

## 2. Strict prohibitions

Do **not** change any factor formula in `scripts/factor_formula_registry.py`.

Do **not** change `scripts/factor_ops.py`.

Do **not** change `scripts/factor_specs.py`.

Do **not** add factors.

Do **not** remove factors.

Do **not** change the 10 signal factor IDs in `scripts/build_phase9b_signal_panel.py`.

Do **not** change signal weights, winsorization, z-scoring, liquidity gate, position overlay, or output column names.

Do **not** regenerate `phase9b_signal_panel.parquet`.

Do **not** regenerate factor values.

Do **not** regenerate labels.

Do **not** regenerate universe files.

Do **not** change public site HTML.

Do **not** create a new config framework.

Do **not** create a new dataset registry system.

Do **not** make production, live trading, alpha, or tradeability claims.

## 3. Required fixes

### 3.1 Add a single current default dataset constant where appropriate

For each modified script, define a clear constant near the top, for example:

```python
DEFAULT_DATASET_ID = "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
```

Use the same literal value across modified scripts.

Do not introduce a new shared module in this task. A shared config module may be useful later, but it is out of scope for PM-02A.

### 3.2 `scripts/build_factor_values.py`

Current issue from PM-01:

- `build_factor_values.py` defaults to `crypto_top50_usdt_perp_1h`
- evaluators and signal panel read from `crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1`

Required change:

- Change the default `--dataset-id` to `DEFAULT_DATASET_ID`
- Preserve existing CLI behavior: callers can still pass another `--dataset-id`
- Do not change factor computation logic
- Do not change cross-sectional postprocessing logic
- Do not change output schema
- Add an explicit printed line showing the resolved dataset ID before building
- Add a preflight check that the expected bars path exists:

```text
data/cache/<dataset_id>/bars_1h.parquet
```

If missing, fail with a clear error message that says which path is missing and how to pass `--dataset-id` explicitly.

### 3.3 `scripts/evaluate_factors.py`

Current issue from PM-01:

- evaluator hardcodes `FEATURES_DIR = data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1`
- no `--dataset-id` parameter

Required change:

- Add `--dataset-id` argument with default `DEFAULT_DATASET_ID`
- Resolve `features_dir` and `labels_path` from the selected dataset ID inside `main()`
- Do not rely on a global hardcoded `FEATURES_DIR` except possibly as a backwards-compatible default constant
- Preserve the partial-run safety guard: `--factor-ids` still requires `--output-suffix` or `--output-dir`
- Do not change RankIC, quantile, long-short, direction-adjustment, candidate-review, or manifest logic except to include the resolved dataset ID in the evaluation manifest if a manifest is already produced
- Print the resolved dataset ID, features path, and labels path at runtime
- Fail clearly if labels are missing
- For missing factor values, preserve current behavior: record `MISSING_FACTOR_VALUES`, do not crash the whole evaluation

### 3.4 `scripts/build_phase9b_signal_panel.py`

Current issue from PM-01:

- signal panel builder hardcodes the current dataset path
- this is acceptable for current use but bad for future universe migration

Required change:

- Add `--dataset-id` argument with default `DEFAULT_DATASET_ID`
- Resolve `DATA_BASE` from the selected dataset ID inside `main()`
- Keep the existing 10 factor IDs unchanged
- Keep all signal construction logic unchanged
- Keep output path unchanged:

```text
research/factor_runs/crypto_top50_factor_library/phase9b_signal_panel.parquet
```

- Print the resolved dataset ID and factor value base path at runtime
- Add a preflight check that all 10 required factor value files exist before loading
- If any are missing, fail clearly and list missing factor IDs + expected paths

### 3.5 `scripts/run_factor_intake.py`

Inspect only.

It already has `--dataset-id` defaulting to the current canonical dataset. Modify it only if you find that it still calls `evaluate_factors.py` without passing `--dataset-id` after you add that evaluator argument.

If modification is needed:

- Pass `--dataset-id args.dataset_id` to both `build_factor_values.py` and `evaluate_factors.py`
- Do not change run directory layout
- Do not change artifact names
- Do not change QC logic except if needed to record the dataset ID in manifest

## 4. Validation commands

After changes, run static checks at minimum:

```bash
python -m py_compile scripts/build_factor_values.py scripts/evaluate_factors.py scripts/build_phase9b_signal_panel.py scripts/run_factor_intake.py
```

Run help checks:

```bash
python scripts/build_factor_values.py --help
python scripts/evaluate_factors.py --help
python scripts/build_phase9b_signal_panel.py --help
python scripts/run_factor_intake.py --help
```

Run a dry-run or non-mutating check if available. If a script does not support dry-run, do not run a heavy data build.

Recommended safe checks:

```bash
python scripts/evaluate_factors.py --factor-ids vol_5h --output-suffix pm02a_smoke --dataset-id crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1
```

Only run the smoke evaluation if required data exists and runtime is reasonable. This writes suffixed outputs under the existing factor-level evaluation directory; do not overwrite canonical outputs.

Do **not** run full factor value generation.

Do **not** run full signal panel generation unless explicitly necessary and approved.

## 5. Expected implementation style

Keep the patch small.

Prefer explicit, readable changes over abstraction.

Do not introduce a config system.

Do not introduce environment variables unless already used by the script.

Do not add dependencies.

Use `Path` consistently.

Use clear error messages.

Keep backwards compatibility: explicit `--dataset-id other_dataset` should still work.

## 6. Required final audit note

Create one short Markdown note summarizing the change:

`docs/factor_library/audits/pm02a_default_dataset_contract_patch.md`

This file should include:

- summary of files changed
- before/after dataset default behavior
- validation commands run
- whether any smoke evaluation was run
- any files intentionally not modified
- explicit statement that factor formulas, signal weights, universe membership, and public site were not changed

This is the only documentation file you may add in this task.

## 7. Allowed changed files

Allowed code files:

- `scripts/build_factor_values.py`
- `scripts/evaluate_factors.py`
- `scripts/build_phase9b_signal_panel.py`
- `scripts/run_factor_intake.py` only if needed

Allowed documentation file:

- `docs/factor_library/audits/pm02a_default_dataset_contract_patch.md`

Do not change anything else unless there is a direct syntax/test necessity. If you believe another file must be changed, stop and explain before changing it.

## 8. Commit rules

Before committing, run:

```bash
git diff --stat
git diff -- scripts/build_factor_values.py scripts/evaluate_factors.py scripts/build_phase9b_signal_panel.py scripts/run_factor_intake.py docs/factor_library/audits/pm02a_default_dataset_contract_patch.md
```

Verify that no public HTML, generated parquet, factor registry, factor ops, factor specs, universe files, label files, or signal output parquet changed.

Commit with this message:

```bash
fix: align default dataset contract for factor pipeline
```

Final response should include:

- commit hash
- files changed
- validation commands run
- whether smoke evaluation was run
- any warnings
