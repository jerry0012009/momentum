# PM-34 Prompt — Factor Expansion Backlog and Intake-Readiness Test

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-33:

- unified factor evaluation workflow is visible on the factor-evaluation page;
- evidence matrix and workflow readiness are page-visible;
- each factor has a unified profile and source lineage.

PM-34 should prepare for factor expansion, but it should **not** add new factors yet.

The goal is to create a disciplined backlog of candidate factors and verify that the current workflow is ready for controlled intake.

## 0. PM objective

Create a factor expansion backlog and intake-readiness checklist so that future PMs can add new factors in controlled batches, using the existing fixed workflow.

This task should answer:

1. What candidate factors or factor families should be considered next?
2. Which candidates are likely incremental versus redundant?
3. Which candidates can be implemented using existing `factor_ops.py` operators?
4. Which candidates require new operators or new input data?
5. Which candidates should be in the first controlled intake batch?
6. Is the workflow ready to evaluate new factors end-to-end?

Do not register new factors in PM-34.

## 1. Strict prohibitions

Do **not** add new `FactorSpec` entries.

Do **not** modify `factor_formula_registry.py`.

Do **not** modify `factor_ops.py`.

Do **not** compute new factor_values.

Do **not** modify signal panel construction.

Do **not** modify public HTML pages.

Do **not** enter signal evaluation or portfolio construction.

Do **not** use external data.

Do **not** make alpha/trading claims.

## 2. Required files to inspect

Read:

```text
docs/factor_library/START_HERE.md
docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md
docs/factor_library/REGENERATION_CONTRACT.md
scripts/factor_formula_registry.py
scripts/factor_specs.py
scripts/factor_ops.py
scripts/run_factor_intake.py
scripts/run_factor_library_refresh.py
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_unified_profile_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_cluster_members.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_workflow_contract.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_evidence_matrix.csv
```

## 3. Required script

Create:

```text
scripts/build_factor_expansion_backlog.py
```

The script should generate a machine-readable backlog from:

- existing registry/families;
- existing factor profile classes;
- redundancy cluster gaps;
- current available operators;
- current available input columns;
- known evaluation workflow requirements.

The backlog may be rule-based. Do not use external research scraping.

## 4. Required outputs

Create:

```text
docs/factor_library/FACTOR_EXPANSION_BACKLOG.md
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_expansion_backlog.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_expansion_backlog.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_intake_readiness_checklist.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_intake_readiness_checklist.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_expansion_backlog_manifest.json
```

## 5. Backlog schema

`factor_expansion_backlog.csv` should include:

```text
candidate_factor_id
candidate_family
candidate_theme
formula_sketch
required_inputs
available_inputs_check
operator_reuse_plan
requires_new_operator
requires_new_data
expected_direction
expected_direction_basis
likely_existing_cluster_overlap
likely_redundancy_risk
expected_diagnostic_value
expected_failure_mode
implementation_complexity
intake_priority
suggested_batch
review_notes_zh
review_notes_en
```

Allowed `intake_priority`:

```text
P1_CONTROLLED_BATCH
P2_BACKLOG
P3_REQUIRES_OPERATOR
P4_REQUIRES_DATA
P5_DEFER
```

Allowed `likely_redundancy_risk`:

```text
LOW
MEDIUM
HIGH
UNKNOWN
```

Allowed `implementation_complexity`:

```text
LOW
MEDIUM
HIGH
BLOCKED_BY_DATA
```

## 6. Candidate families to consider

Use only ideas that can be evaluated with current data unless clearly marked as requiring new data.

Candidate families may include:

```text
short_term_reversal
medium_term_momentum
range_breakout
volatility_adjusted_momentum
volume_pressure
liquidity_stress
funding_rate_structure
taker_flow_structure
intraday_candle_structure
realized_volatility_shape
cross_sectional_rank_acceleration
mean_reversion_after_extreme_move
```

Do not add formulas that require order book data unless marked `P4_REQUIRES_DATA`.

## 7. Intake-readiness checklist

Create checklist rows for key workflow gates:

```text
registry_integrity_ready
factor_ops_reuse_ready
factor_values_build_ready
intake_runner_ready
full_refresh_runner_ready
expensive_stage_guardrails_ready
profile_stage_ready
evidence_matrix_ready
staleness_monitor_ready
page_ready_payload_ready
no_signal_mutation_guard_ready
```

Each row should include:

```text
check_id
status
what_it_checks
evidence_file_or_command
blocking_if_failed
notes_zh
notes_en
```

Allowed status:

```text
PASS
WARN
FAIL
NOT_CHECKED
```

## 8. Controlled first batch recommendation

The backlog should identify a small first batch, ideally 3–5 candidates, with:

```text
suggested_batch = BATCH_01_CONTROLLED_INTAKE
```

Selection criteria:

- implementable with current data;
- likely not exact duplicate of dominant clusters;
- covers more than one family/theme;
- expected diagnostic value is clear;
- expected direction can be justified from domain logic, not from evaluation results.

Do not implement them in PM-34.

## 9. Required audit

Create:

```text
docs/factor_library/audits/pm34_factor_expansion_backlog_intake_readiness.md
```

Audit must include:

1. Summary verdict:
   - `FACTOR_EXPANSION_BACKLOG_PASS`
   - `FACTOR_EXPANSION_BACKLOG_PASS_WITH_LIMITATIONS`
   - `FACTOR_EXPANSION_BACKLOG_BLOCKED`
2. Why PM-34 is needed after PM-33.
3. Files changed.
4. Candidate count.
5. Candidate family distribution.
6. Intake priority distribution.
7. Required input availability summary.
8. Operator reuse summary.
9. Suggested BATCH_01 candidates.
10. Intake readiness checklist summary.
11. Explicit confirmation no new factors were registered.
12. Explicit confirmation no factor formulas/factor_values/signal/page changed.
13. Limitations.
14. Recommended next PM: PM-35 controlled factor intake batch.

## 10. Validation

Run:

```bash
python -m py_compile scripts/build_factor_expansion_backlog.py
python scripts/build_factor_expansion_backlog.py
python scripts/run_factor_library_refresh.py --stage profile --dry-run
python scripts/check_factor_library_staleness.py
```

Then:

```bash
python - <<'PY'
import json
import pandas as pd
from pathlib import Path
base = Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics')
backlog = pd.read_csv(base / 'factor_expansion_backlog.csv')
checklist = pd.read_csv(base / 'factor_intake_readiness_checklist.csv')
print('candidate count', len(backlog))
print('families')
print(backlog['candidate_family'].value_counts(dropna=False).to_string())
print('priorities')
print(backlog['intake_priority'].value_counts(dropna=False).to_string())
print('suggested batch')
print(backlog[backlog['suggested_batch'].eq('BATCH_01_CONTROLLED_INTAKE')][['candidate_factor_id','candidate_family','implementation_complexity','likely_redundancy_risk']].to_string(index=False))
print('checklist')
print(checklist['status'].value_counts(dropna=False).to_string())
assert len(backlog) > 0
assert len(backlog[backlog['suggested_batch'].eq('BATCH_01_CONTROLLED_INTAKE')]) >= 3
PY
```

Also confirm no registry changes:

```bash
git diff -- scripts/factor_formula_registry.py scripts/factor_ops.py scripts/build_factor_values.py scripts/build_phase9b_signal_panel.py
```

This diff should be empty.

## 11. Allowed files to change

Allowed script:

```text
scripts/build_factor_expansion_backlog.py
```

Allowed docs:

```text
docs/factor_library/FACTOR_EXPANSION_BACKLOG.md
docs/factor_library/audits/pm34_factor_expansion_backlog_intake_readiness.md
```

Allowed outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_expansion_backlog.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_expansion_backlog.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_intake_readiness_checklist.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_intake_readiness_checklist.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_expansion_backlog_manifest.json
```

Do not modify:

```text
scripts/factor_formula_registry.py
scripts/factor_ops.py
scripts/build_factor_values.py
scripts/build_phase9b_signal_panel.py
reports/site/factor-library/factor-evaluation.html
scripts/_build_factor_eval_html.py
```

## 12. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
feat: add factor expansion backlog
```

Final response should include:

- commit hash
- summary verdict
- candidate count
- priority distribution
- suggested BATCH_01 candidates
- intake-readiness checklist summary
- confirmation no factors were registered
- validation results
- limitations
- recommended next PM
