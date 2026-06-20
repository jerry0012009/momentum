# PM-01 Prompt — Canonical Pipeline Reality Audit

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

Your role in this task is **not** to implement new features. Your role is to establish a factual baseline for the current factor-library pipeline so that later PM tasks do not create duplicate scripts, stale documentation, or parallel workflows.

## 0. Product / PM context

The current active product goal is a **research-grade crypto perpetual cross-sectional factor library**.

The current universe for factor evaluation and signal evaluation should be treated as:

`crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1`

In plain language: current work is based on the crypto USDT perpetual monthly-volume Top50 / current-listed universe.

Future universes may be added later, for example US equities or Hong Kong equities. However, this task must **not** implement universe abstraction, multi-asset support, or general dataset routing. The immediate task is to audit the current crypto factor-library mainline and identify where the current repo is inconsistent, stale, or unclear.

## 1. Non-negotiable scope

This task is a **read-only audit plus two audit artifacts**.

You may create only the following two files:

1. `docs/factor_library/audits/pm01_canonical_pipeline_reality_audit.md`
2. `docs/factor_library/audits/pm01_pipeline_node_audit.csv`

If the directory `docs/factor_library/audits/` does not exist, create it. Do not create any other new directory or file.

## 2. Strict prohibitions

Do **not** modify business logic.

Do **not** add factors.

Do **not** add signals.

Do **not** modify `scripts/build_phase9b_signal_panel.py`.

Do **not** modify `scripts/evaluate_factors.py`.

Do **not** modify `scripts/evaluate_signals.py`.

Do **not** modify `scripts/run_factor_intake.py`.

Do **not** create a new factor pipeline.

Do **not** create a new evaluator.

Do **not** create a new report format beyond the two audit artifacts listed above.

Do **not** move, delete, rename, or archive files.

Do **not** reactivate archived pages or old scripts.

Do **not** change public HTML pages.

Do **not** update README, START_HERE, Control Center, manifest, or FILE_STATUS_REGISTER in this task.

Do **not** make production, tradeability, live trading, or alpha claims.

Do **not** touch live trading, execution, broker, exchange, strategy-live, or strategy research modules.

`src/momentum/strategies/` is out of scope for this task.

## 3. Files that must be inspected

Inspect at minimum the following files and paths:

- `README.md`
- `docs/factor_library/START_HERE.md`
- `docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md`
- `docs/factor_library/factor_library_manifest.json`
- `docs/factor_library/FILE_STATUS_REGISTER.csv`
- `docs/factor_library/ORPHAN_WORK_AUDIT.md`
- `research/factor_runs/crypto_top50_factor_library/factor_library_state.md`
- `research/factor_runs/crypto_top50_factor_library/factor_library_state.json`
- `scripts/README.md`
- `scripts/download_full_binance_1h_universe.py`
- `scripts/build_crypto_top50_universe.py`
- `scripts/build_labels.py`
- `scripts/factor_specs.py`
- `scripts/factor_ops.py`
- `scripts/factor_formula_registry.py`
- `scripts/build_factor_values.py`
- `scripts/evaluate_factors.py`
- `scripts/run_factor_intake.py`
- `scripts/build_factor_library_state.py`
- `scripts/build_phase9b_signal_panel.py`
- `scripts/evaluate_signals.py`
- `src/momentum/signal_evaluation/`
- `reports/site/factor-library/assets/actual_script_map.json`
- `reports/site/factor-library/index.html`
- `reports/site/factor-library/actual-script-map.html`
- `reports/site/factor-library/factor-evaluation.html`
- `reports/site/factor-library/signal-evaluation-summary.html`

You may inspect additional files only if needed to resolve contradictions among the files above.

## 4. Required checks

You must explicitly check and report the following.

### 4.1 Dataset and universe naming consistency

Check all current references to:

- `crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1`
- `crypto_usdt_perp_monthly_volume_top50_current_listed_v1`
- `crypto_top50_usdt_perp_monthly_volume_top50_current_listed_v1`
- `crypto_top50_usdt_perp_1h`
- `crypto_top50_factor_library`

Identify whether these are:

- current canonical dataset IDs,
- current output folders,
- historical names,
- stale defaults,
- or ambiguous names requiring PM decision.

Pay special attention to whether the current universe is truly monthly-volume Top50, or whether some code still constructs a 24h volume snapshot while naming it like a monthly/trailing universe.

### 4.2 Hard-coded absolute paths

Search for hard-coded absolute paths such as:

- `/root/clawd/jerry/momentum`
- `/root/`
- local machine-specific paths

For each occurrence, identify:

- file path,
- line number,
- current status of the file,
- whether the file is part of the active mainline,
- and severity.

Do not fix these paths in this task.

### 4.3 Active / supporting / orphan / historical contradictions

Compare these sources:

- `FACTOR_LIBRARY_CONTROL_CENTER.md`
- `factor_library_manifest.json`
- `FILE_STATUS_REGISTER.csv`
- `ORPHAN_WORK_AUDIT.md`
- `scripts/README.md`

Identify conflicts in file status, especially for:

- `scripts/evaluate_factors_dynamic_universe.py`
- `scripts/compare_static_dynamic_factor_evals.py`
- `scripts/export_alphalens_factor_data.py`
- `scripts/run_alphalens_smoke_check.py`
- `scripts/audit_dynamic_universe_*.py`
- `scripts/build_crypto_native_factor_values.py`
- `scripts/build_factor_values_batch.py`
- root-level `PHASE_12D_*.md`
- `docs/factor_library_transparency/`

Classify each as:

- `ACTIVE_MAINLINE`
- `ACTIVE_SUPPORTING`
- `PUBLIC_SITE`
- `HISTORICAL_ARCHIVE`
- `DEPRECATED_STALE`
- `ORPHAN_REVIEW_REQUIRED`
- `OUT_OF_SCOPE`
- `AMBIGUOUS_NEEDS_PM_DECISION`

Use conservative status. If sources disagree, do not invent a resolution. Record the contradiction.

### 4.4 Canonical pipeline entrypoints

Confirm whether the current canonical entrypoints are:

- data download: `scripts/download_full_binance_1h_universe.py`
- universe build: `scripts/build_crypto_top50_universe.py`
- labels: `scripts/build_labels.py`
- factor definitions: `scripts/factor_formula_registry.py`
- factor metadata: `scripts/factor_specs.py`
- factor operators: `scripts/factor_ops.py`
- factor values: `scripts/build_factor_values.py`
- factor evaluation: `scripts/evaluate_factors.py`
- new factor intake: `scripts/run_factor_intake.py`
- state generation: `scripts/build_factor_library_state.py`
- signal panel: `scripts/build_phase9b_signal_panel.py`
- signal evaluation: `scripts/evaluate_signals.py`
- signal evaluation API: `src/momentum/signal_evaluation/`
- public site: `reports/site/factor-library/`

For each entrypoint, verify:

- whether the script exists,
- whether it uses repo-relative paths or absolute paths,
- whether default dataset ID matches the current expected universe,
- what it consumes,
- what it produces,
- and whether it appears to be current, stale, or ambiguous.

### 4.5 Factor and signal evaluation boundaries

Confirm the current boundary:

- factor evaluation and signal evaluation currently target the crypto monthly Top50 current-listed universe;
- future universe support is a plausible product direction;
- but this task must not implement universe abstraction or modify current evaluators.

Identify the minimum future-safe design principle only as a recommendation, for example:

“Dataset ID and universe ID should eventually be explicit parameters or config values, but current code should first be made internally consistent before generalization.”

Do not implement this recommendation.

### 4.6 Public site freshness

Check whether public site assets/pages reflect current state or older phases. At minimum inspect:

- `reports/site/factor-library/assets/actual_script_map.json`
- `reports/site/factor-library/index.html`
- `reports/site/factor-library/actual-script-map.html`
- `reports/site/factor-library/factor-evaluation.html`
- `reports/site/factor-library/signal-evaluation-summary.html`

Report whether each page/asset appears current, stale, or mixed.

Do not edit public site files.

## 5. Suggested commands

Start with:

```bash
git status --short
pwd
```

Then use ripgrep if available:

```bash
rg -n "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1|crypto_usdt_perp_monthly_volume_top50_current_listed_v1|crypto_top50_usdt_perp_monthly_volume_top50_current_listed_v1|crypto_top50_usdt_perp_1h|crypto_top50_factor_library|/root/clawd/jerry/momentum|/root/|24h dollar volume|trailing_30d|monthly_volume|evaluate_factors_dynamic_universe|build_crypto_native_factor_values|export_alphalens|run_alphalens|compare_static_dynamic" README.md docs scripts src reports research || true
```

If `rg` is not available, use `grep -RIn`.

You may use short Python scripts to parse JSON/CSV files and generate the final audit CSV. Keep helper code temporary; do not commit helper scripts.

## 6. Required output file 1: Markdown audit

Create:

`docs/factor_library/audits/pm01_canonical_pipeline_reality_audit.md`

The report must include these sections:

1. `# PM-01 Canonical Pipeline Reality Audit`
2. `## Scope and Non-Changes`
3. `## Current Product Boundary`
4. `## Current Canonical Pipeline — As Documented`
5. `## Current Canonical Pipeline — As Implemented`
6. `## Dataset / Universe Naming Findings`
7. `## Hard-Coded Path Findings`
8. `## File Status Contradictions`
9. `## Factor Evaluation Boundary`
10. `## Signal Evaluation Boundary`
11. `## Public Site Freshness Findings`
12. `## Risk Register`
13. `## Recommended PM-02 Options`
14. `## Appendix: Commands / Evidence`

The report must be factual and conservative. Use evidence from file paths and line-level references where practical.

The report must not claim that any signal is tradeable alpha.

The report must not claim production readiness.

## 7. Required output file 2: Pipeline audit CSV

Create:

`docs/factor_library/audits/pm01_pipeline_node_audit.csv`

Required columns:

```csv
node_id,node_name,documented_authority,actual_script_or_module,documented_input,actual_input,documented_output,actual_output,documented_dataset_id,actual_dataset_id,path_style,status_from_control_center,status_from_manifest,status_from_file_register,status_from_orphan_audit,observed_issue,severity,recommended_next_action
```

Recommended `node_id` values:

- `raw_data`
- `universe`
- `labels`
- `factor_specs`
- `factor_ops`
- `factor_registry`
- `factor_values`
- `factor_evaluation`
- `factor_intake`
- `factor_state`
- `signal_panel`
- `signal_evaluation`
- `signal_evaluation_api`
- `public_site`
- `archive_orphans`

Severity values must be one of:

- `LOW`
- `MEDIUM`
- `HIGH`
- `BLOCKER`

Use `BLOCKER` only if the current mainline cannot be trusted without resolving the issue.

## 8. Recommended PM-02 options

The Markdown report must end with 2–4 possible PM-02 options. Do not perform them.

Likely PM-02 options may include:

1. Normalize current dataset / universe naming.
2. Replace hard-coded absolute paths in active mainline scripts with repo-relative paths.
3. Reconcile manifest / FILE_STATUS_REGISTER / ORPHAN_WORK_AUDIT status contradictions.
4. Update public site assets only after canonical state is reconciled.

Each option must include:

- expected benefit,
- risk,
- affected files,
- whether it changes logic,
- and recommended order.

## 9. Completion rules

Before finishing, run:

```bash
git diff -- docs/factor_library/audits/pm01_canonical_pipeline_reality_audit.md docs/factor_library/audits/pm01_pipeline_node_audit.csv
```

Verify that only the two allowed files are changed.

Then commit only those two files with this commit message:

```bash
docs: add PM01 canonical pipeline reality audit
```

Final response should include:

- commit hash,
- the two file paths,
- and a short summary of top findings.

Do not include unrelated commentary.
