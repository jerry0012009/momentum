# PM-38B Prompt — Entrypoint Documentation Alignment and Runbook Repair

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-38:

- PM-38 created `POST_INTAKE_WORKFLOW_RUNBOOK.md`;
- PM-38 created `RESOURCE_AWARE_REFRESH_GUIDE.md`;
- PM-38 created page completeness QA script and report;
- PM-38 did **not** update existing entrypoint docs such as `START_HERE.md`, `FACTOR_LIBRARY_CONTROL_CENTER.md`, or `REGENERATION_CONTRACT.md`;
- PM-38 also left a potentially confusing prompt file named `PM38_POST_INTAKE_FACTOR_INTERPRETATION_DIRECTION_REVIEW_PROMPT_20260622.md`, even though factor interpretation was deferred.

PM-38B must align the documentation layer so future factor intake starts from the correct entrypoints and follows the resource-aware 12/12 workflow.

## 0. PM objective

Make the documentation coherent and operationally correct.

This PM should:

1. Update the existing START_HERE / control / regeneration docs to reference the post-intake workflow runbook and resource-aware guide.
2. Correct any runbook details that do not match the actual repository code structure.
3. Clarify that PM-38 deferred factor interpretation to a later PM.
4. Ensure the page QA script remains the canonical check for factor-evaluation page completeness.
5. Avoid changing any factor computation, diagnostics, or page outputs unless strictly necessary.

This is a documentation alignment and runbook repair task, not a factor research interpretation task.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify expected_direction.

Do **not** modify factor_values.

Do **not** modify diagnostics outputs.

Do **not** modify public HTML pages.

Do **not** modify signal panel construction.

Do **not** enter factor interpretation or direction semantics review.

Do **not** touch live / strategy / broker / execution code.

## 2. Required files to inspect first

Read:

```text
docs/factor_library/START_HERE.md
docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md
docs/factor_library/REGENERATION_CONTRACT.md
docs/factor_library/POST_INTAKE_WORKFLOW_RUNBOOK.md
docs/factor_library/RESOURCE_AWARE_REFRESH_GUIDE.md
docs/factor_library/audits/pm35_controlled_factor_intake_batch01.md
docs/factor_library/audits/pm36_resource_audit_incremental_diagnostics.md
docs/factor_library/audits/pm37_incremental_redundancy_stability_completion.md
docs/factor_library/audits/pm38_post_intake_workflow_runbook_page_qa.md
scripts/factor_specs.py
scripts/factor_formula_registry.py
scripts/build_factor_values.py
scripts/run_factor_intake.py
scripts/run_factor_library_refresh.py
scripts/check_factor_evaluation_page_completeness.py
```

## 3. Required entrypoint doc updates

Update:

```text
docs/factor_library/START_HERE.md
docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md
docs/factor_library/REGENERATION_CONTRACT.md
```

### 3.1 START_HERE.md

Add a clear section near the existing “Adding a new factor” or workflow section:

```text
Resource-aware post-intake workflow
```

It must reference:

```text
docs/factor_library/POST_INTAKE_WORKFLOW_RUNBOOK.md
docs/factor_library/RESOURCE_AWARE_REFRESH_GUIDE.md
scripts/check_factor_evaluation_page_completeness.py
```

It must say that after PM-35 to PM-37, future factor intake should prefer incremental / missing-only diagnostics over blind full refresh.

### 3.2 FACTOR_LIBRARY_CONTROL_CENTER.md

Add the runbook and resource guide to the control-center navigation.

Make clear:

- `run_factor_intake.py` remains the intake entrypoint;
- `run_factor_library_refresh.py` remains the canonical full refresh runner;
- post-intake completion should use the resource-aware runbook when only a few new factors are added;
- signal/live/strategy code remains out of scope.

### 3.3 REGENERATION_CONTRACT.md

Update the regeneration contract so it explicitly includes:

- 12/12 evidence closure after controlled intake;
- resource-aware missing diagnostics path;
- page completeness QA after page rebuild;
- heavy stages and subset flags;
- warning that full refresh should not be the default after a small controlled intake batch.

## 4. Required runbook corrections

Update:

```text
docs/factor_library/POST_INTAKE_WORKFLOW_RUNBOOK.md
```

Correct any mismatch with actual code.

At minimum fix these issues if present:

### 4.1 FactorSpec example

The runbook must use the actual `FactorSpec` structure.

Correct pattern should resemble:

```python
FactorSpec(
    factor_id="new_factor_id",
    family="family_name",
    required_columns=["close", "volume"],
    lookback_window=20,
    expected_direction="positive",  # or negative / conditional
    compute_fn=_compute_new_factor_id,
    notes="Short explanation of the formula and direction semantics",
)
```

Do not show non-existent fields such as `formula=` or `description=` if the actual dataclass does not support them.

### 4.2 Registry validation command

Prefer actual validation commands:

```bash
python scripts/check_factor_registry_integrity.py
python scripts/check_factor_catalog_integrity.py || true
```

Avoid incorrect imports such as `FACTOR_SPECS` if the actual registry exports `REGISTRY` / `REGISTRY_BY_ID`.

### 4.3 factor_values path

Correct factor_values path.

The canonical path should match actual pipeline output, e.g.:

```text
data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/<factor_id>/factor_values.parquet
```

Do not say factor_values live under `research/.../factor_values` if that is not true.

### 4.4 Paper portfolio merge warning

Clarify that paper diagnostics can overwrite existing outputs if run directly.

State the safe rule:

- run subset to temp output if script supports it;
- merge new rows back;
- validate total factor count after merge;
- never allow a 5-factor subset to replace a 76-factor paper file.

### 4.5 Expensive stages wording

Clarify which scripts support `--factor-ids` / `--only-missing`.

Clarify that `--expensive-ok` is for the refresh runner, not necessarily for individual scripts.

### 4.6 Evidence progression

Make the evidence progression match actual workflow after PM-37:

```text
Initial intake / factor values / factor-level eval
Partial downstream diagnostics
Decile + capacity repair
Redundancy + cluster + marginal + rolling stability completion
Unified profile + staleness + page QA
```

Avoid implying exact 2/12 / 4/12 / 8/12 counts unless they are guaranteed by current evidence-matrix logic.

## 5. Required resource guide corrections

Update if needed:

```text
docs/factor_library/RESOURCE_AWARE_REFRESH_GUIDE.md
```

It should include:

- heavy stage table;
- recommended commands for small factor batches;
- when to use `--factor-ids`;
- when to use `--only-missing`;
- when full refresh is acceptable;
- how to avoid OOM on 15GB/no-swap servers;
- how to avoid unrelated reports/site diffs;
- how to handle paper portfolio temp + merge;
- how to recover from partial failure.

## 6. Prompt file hygiene

The file:

```text
docs/factor_library/prompts/PM38_POST_INTAKE_FACTOR_INTERPRETATION_DIRECTION_REVIEW_PROMPT_20260622.md
```

was added even though interpretation was deferred.

Do one of the following:

1. Rename it to a PM-39 prompt if repository tooling allows safe rename; or
2. Add a clear header at the top:

```text
SUPERSEDED / DEFERRED: This prompt was not executed as PM-38. Use after PM-38B as PM-39 if factor interpretation remains the next task.
```

Do not delete useful content unless necessary.

## 7. Optional QA script improvement

If low-risk, update:

```text
scripts/check_factor_evaluation_page_completeness.py
```

so it also verifies that `START_HERE.md`, `CONTROL_CENTER`, and `REGENERATION_CONTRACT` link to the new runbook/resource guide.

If not updating script, document that this will be checked manually in the audit.

## 8. Required audit

Create:

```text
docs/factor_library/audits/pm38b_entrypoint_doc_alignment_runbook_repair.md
```

Audit must include:

1. Summary verdict:
   - `ENTRYPOINT_DOC_ALIGNMENT_PASS`
   - `ENTRYPOINT_DOC_ALIGNMENT_PASS_WITH_LIMITATIONS`
   - `ENTRYPOINT_DOC_ALIGNMENT_BLOCKED`
2. Why PM-38B was required after PM-38.
3. Files changed.
4. Confirmation whether START_HERE was updated.
5. Confirmation whether CONTROL_CENTER was updated.
6. Confirmation whether REGENERATION_CONTRACT was updated.
7. Runbook corrections made.
8. Resource guide corrections made.
9. Prompt file hygiene result.
10. Whether QA script was updated.
11. Confirmation no factor formulas / factor_values / diagnostics outputs / public HTML / signal code changed.
12. Limitations.
13. Recommended next PM: PM-39 post-intake factor interpretation and direction-semantics review.

## 9. Validation

Run:

```bash
python -m py_compile scripts/check_factor_evaluation_page_completeness.py
python scripts/check_factor_evaluation_page_completeness.py
```

Then check links/tokens:

```bash
python - <<'PY'
from pathlib import Path
files = [
    Path('docs/factor_library/START_HERE.md'),
    Path('docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md'),
    Path('docs/factor_library/REGENERATION_CONTRACT.md'),
    Path('docs/factor_library/POST_INTAKE_WORKFLOW_RUNBOOK.md'),
    Path('docs/factor_library/RESOURCE_AWARE_REFRESH_GUIDE.md'),
]
checks = [
    'POST_INTAKE_WORKFLOW_RUNBOOK.md',
    'RESOURCE_AWARE_REFRESH_GUIDE.md',
    'check_factor_evaluation_page_completeness.py',
    '--factor-ids',
    '--only-missing',
    'factor_values.parquet',
    'FactorSpec',
]
for p in files:
    txt = p.read_text(encoding='utf-8')
    print('\n', p)
    for c in checks:
        print(c, c in txt)
PY
```

Also confirm no forbidden code/output changes:

```bash
git diff --name-only HEAD~1..HEAD | grep -E 'factor_formula_registry|factor_ops|build_factor_values|build_phase9b_signal_panel|reports/site/factor-library/factor-evaluation.html|research/factor_runs' || true
```

Expected: no matches except audit/report if intentionally updated. PM-38B should primarily modify docs and maybe QA script.

## 10. Allowed files to change

Allowed docs:

```text
docs/factor_library/START_HERE.md
docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md
docs/factor_library/REGENERATION_CONTRACT.md
docs/factor_library/POST_INTAKE_WORKFLOW_RUNBOOK.md
docs/factor_library/RESOURCE_AWARE_REFRESH_GUIDE.md
docs/factor_library/prompts/PM38_POST_INTAKE_FACTOR_INTERPRETATION_DIRECTION_REVIEW_PROMPT_20260622.md
docs/factor_library/audits/pm38b_entrypoint_doc_alignment_runbook_repair.md
```

Allowed script if low-risk:

```text
scripts/check_factor_evaluation_page_completeness.py
```

Do not modify:

```text
scripts/factor_formula_registry.py
scripts/factor_ops.py
scripts/build_factor_values.py
scripts/build_phase9b_signal_panel.py
reports/site/factor-library/factor-evaluation.html
reports/site/factors/*
reports/site/paper/*
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/*.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/*.json
```

## 11. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
docs: align factor intake workflow entrypoints
```

Final response should include:

- commit hash
- summary verdict
- entrypoint docs updated
- runbook corrections
- resource guide corrections
- prompt file hygiene result
- QA validation result
- confirmation no factor/signal/output/page changes
- limitations
- recommended next PM
