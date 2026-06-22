# PM-25 Prompt — Reusable Staleness Monitor and Workflow Reconciliation

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows the repaired paper/regime sequence:

- PM-21B: reproducible paper portfolio data repair
- PM-22B: repaired paper portfolio page integration
- PM-23B: refreshed regime diagnostics using repaired paper returns
- PM-24B: refreshed regime section on `factor-evaluation.html`

The current canonical workflow is incomplete: `REGENERATION_CONTRACT.md` and `scripts/run_factor_library_refresh.py` include regime and page stages, but they do not yet explicitly include PM-21B/PM-22B stages:

- `paper-diagnostics`
- `paper-page-payload`

PM-25 must therefore do two things:

1. Reconcile the workflow contract/orchestrator with the actual repaired pipeline.
2. Add a reusable staleness/workflow monitor that dynamically infers expected counts and stale stages.

This must **not** be a one-off checker for the current 71 factors.

## 0. PM objective

Create a reusable workflow monitor and align the canonical pipeline with the repaired factor-library stack.

The monitor should answer:

1. Given the current registry/state, what is the current factor count?
2. Which downstream outputs should cover all current factors?
3. Which outputs are missing or stale relative to their dependencies?
4. If a user adds new factors, which stages need to be rerun?
5. Does the public page reflect the latest scorecard / redundancy / paper / regime outputs?
6. Does `run_factor_library_refresh.py` know about all current official stages?
7. Does `REGENERATION_CONTRACT.md` document the current official pipeline?

The monitor is a workflow navigation tool, not a static audit artifact.

## 1. Strict prohibitions

Do **not** hardcode `71` or any current factor count.

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify signal panel construction.

Do **not** create a new public page.

Do **not** rebuild expensive outputs unless explicitly required for validation.

Do **not** create multiple narrative docs. Keep docs minimal and canonical.

Do **not** make production/live/trading claims.

## 2. Required workflow reconciliation

Before building the monitor, inspect:

```text
docs/factor_library/REGENERATION_CONTRACT.md
scripts/run_factor_library_refresh.py
```

The canonical pipeline must include these stage concepts in dependency order:

```text
registry-integrity
catalog
values
direction-audit
evaluate                    [EXPENSIVE]
diagnostics
metadata
scorecard
redundancy                  [EXPENSIVE]
scorecard refresh
paper-diagnostics           [MODERATE or EXPENSIVE-GUARDED]
paper-page-payload          [CHEAP]
regime                      [CHEAP]
page                        [CHEAP]
state                       [CHEAP]
```

### 2.1 Required orchestrator update

Update `scripts/run_factor_library_refresh.py` so it supports at least:

```bash
python scripts/run_factor_library_refresh.py --stage paper-diagnostics
python scripts/run_factor_library_refresh.py --stage paper-page-payload
python scripts/run_factor_library_refresh.py --stage staleness
```

`paper-diagnostics` should run:

```bash
python scripts/build_single_factor_paper_portfolio_diagnostics.py
```

`paper-page-payload` should run:

```bash
python scripts/build_single_factor_paper_page_payload.py
```

`staleness` should run:

```bash
python scripts/check_factor_library_staleness.py
```

If the orchestrator only supports boolean `expensive`, classify `paper-diagnostics` as expensive/guarded if needed to avoid accidentally running a long job in `cheap`. Document the choice in the audit.

`paper-page-payload` and `staleness` should be cheap.

Update presets carefully:

- `all` should include paper-diagnostics and paper-page-payload before regime and page.
- `cheap` should not unexpectedly run a very long paper-diagnostics job if it is marked expensive.
- Add aliases/presets only if useful and simple.

### 2.2 Required contract update

Update `docs/factor_library/REGENERATION_CONTRACT.md` so the pipeline documents:

```text
paper diagnostics -> paper page payload -> regime diagnostics -> factor-evaluation page
```

The contract must state that regime diagnostics depend on the repaired PM-21B paper monthly returns.

Do not create a second workflow document.

## 3. Required script

Create:

```text
scripts/check_factor_library_staleness.py
```

Recommended CLI:

```bash
python scripts/check_factor_library_staleness.py
python scripts/check_factor_library_staleness.py --json
python scripts/check_factor_library_staleness.py --strict
```

The script should be cheap and read-only except for writing its own report files.

## 4. Required outputs

Write to:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/
```

Required outputs:

```text
factor_library_staleness_report.csv
factor_library_staleness_report.json
```

Create audit:

```text
docs/factor_library/audits/pm25_reusable_staleness_workflow_monitor.md
```

## 5. Dynamic expected count logic

Expected factor count must be dynamic.

Use, in order of preference:

1. `research/factor_runs/crypto_top50_factor_library/factor_library_state.json` if present and current;
2. fallback to importing the registry from `scripts/factor_formula_registry.py` if state is missing;
3. never hardcode the current factor count.

The report should include:

```text
expected_factor_count
expected_pair_count = n * (n - 1) / 2
source_of_expected_count
```

## 6. Coverage checks

Check coverage for these outputs, dynamically against expected factor count:

```text
factor_diagnostics_summary.csv
factor_quality_scorecard.csv
factor_redundancy_summary.csv
single_factor_paper_summary.csv
single_factor_paper_page_payload.json
single_factor_paper_turnover.csv
single_factor_paper_leg_decomposition.csv
single_factor_paper_drawdown_curve.csv
factor_regime_exposure_summary.csv
factor_regime_diagnostics_payload.json
```

For each output, report:

```text
output_path
expected_factors
actual_factors
missing_factor_ids
extra_factor_ids
status
recommended_stage
```

If a new factor is added to registry but paper outputs are stale, report that `paper-diagnostics` and `paper-page-payload` need rerun.

If paper outputs are newer than regime outputs, report that `regime` needs rerun.

If page is older than paper/regime payloads, report that `page` needs rerun.

## 7. Pairwise redundancy checks

Check:

```text
factor_pairwise_redundancy.csv
```

Expected rows:

```text
expected_pair_count = n * (n - 1) / 2
```

Do not hardcode 2485.

If row count is lower, recommend rerunning `redundancy` and then `scorecard`.

## 8. Timestamp staleness checks

Implement dependency mtime checks.

At minimum check:

1. `factor_quality_scorecard.csv` newer than `factor_redundancy_summary.csv` when redundancy exists;
2. `single_factor_paper_page_payload.json` newer than PM-21B compact paper files;
3. `factor_regime_diagnostics_payload.json` newer than `single_factor_paper_monthly_returns.csv`;
4. `factor-evaluation.html` newer than `single_factor_paper_page_payload.json` and `factor_regime_diagnostics_payload.json`;
5. `factor_library_state.json` newer than major refreshed outputs, or report state may be stale.

If mtime is unavailable or unreliable, report WARN, not FAIL.

## 9. Page content checks

Check existing page:

```text
reports/site/factor-library/factor-evaluation.html
```

It should contain evidence sections for:

```text
Factor Quality Scorecard
Redundancy
Single-Factor Paper Portfolio
Turnover
Drawdown
BTC / Market Regime Diagnostics
```

Use these as soft checks. Do not parse DOM deeply.

## 10. Report schema

`factor_library_staleness_report.csv` columns:

```text
check_id
check_group
status
severity
artifact_path
expected
actual
message
recommended_stage
recommended_command
```

Statuses:

```text
PASS
WARN
FAIL
SKIP
```

Severity:

```text
INFO
LOW
MEDIUM
HIGH
BLOCKER
```

`factor_library_staleness_report.json` should include:

```text
summary_status
generated_at
expected_factor_count
expected_pair_count
source_of_expected_count
n_pass
n_warn
n_fail
n_skip
recommended_next_commands
checks
```

Summary status:

```text
STALENESS_PASS
STALENESS_PASS_WITH_WARNINGS
STALENESS_FAIL
```

## 11. Required audit

Create:

```text
docs/factor_library/audits/pm25_reusable_staleness_workflow_monitor.md
```

Audit must include:

1. Summary verdict:
   - `REUSABLE_STALENESS_MONITOR_PASS`
   - `REUSABLE_STALENESS_MONITOR_PASS_WITH_WARNINGS`
   - `REUSABLE_STALENESS_MONITOR_BLOCKED`
2. Why this monitor is reusable and not tied to current 71 factors.
3. Files changed.
4. Workflow reconciliation performed.
5. Whether `paper-diagnostics`, `paper-page-payload`, and `staleness` stages were added.
6. Whether `REGENERATION_CONTRACT.md` now documents paper diagnostics and page payload stages.
7. Expected factor count source.
8. Coverage check summary.
9. Pairwise redundancy check summary.
10. Timestamp staleness summary.
11. Page content check summary.
12. Recommended next commands from the monitor.
13. Validation results.
14. Limitations.
15. Non-change statement: no factors, formulas, factor_values, signal panel, public page creation.
16. Recommended next PM: PM-26 capacity/liquidity proxy diagnostics.

## 12. Validation

Run:

```bash
python -m py_compile scripts/check_factor_library_staleness.py scripts/run_factor_library_refresh.py
python scripts/check_factor_library_staleness.py
python scripts/check_factor_library_staleness.py --json
python scripts/run_factor_library_refresh.py --stage staleness --dry-run
python scripts/run_factor_library_refresh.py --stage paper-page-payload --dry-run
python scripts/run_factor_library_refresh.py --stage paper-diagnostics --dry-run
```

Then:

```bash
python - <<'PY'
import json
import pandas as pd
from pathlib import Path
base = Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics')
report = json.loads((base / 'factor_library_staleness_report.json').read_text(encoding='utf-8'))
checks = pd.read_csv(base / 'factor_library_staleness_report.csv')
print('summary_status', report.get('summary_status'))
print('expected_factor_count', report.get('expected_factor_count'))
print('expected_pair_count', report.get('expected_pair_count'))
print(checks['status'].value_counts(dropna=False).to_string())
print('recommended commands')
for cmd in report.get('recommended_next_commands', []):
    print(cmd)
PY
```

Expected:

- no hardcoded factor count;
- expected pair count is computed dynamically;
- paper stages are present in the orchestrator;
- contract documents paper diagnostics before regime/page;
- report exists in CSV and JSON;
- monitor gives actionable rerun commands if anything is stale.

## 13. Allowed files to change

Allowed scripts:

```text
scripts/check_factor_library_staleness.py
scripts/run_factor_library_refresh.py
```

Allowed outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_library_staleness_report.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_library_staleness_report.json
```

Allowed docs:

```text
docs/factor_library/REGENERATION_CONTRACT.md
docs/factor_library/audits/pm25_reusable_staleness_workflow_monitor.md
```

Do not modify `factor-evaluation.html` in PM-25 unless the staleness monitor discovers a critical page issue. Prefer reporting it.

## 14. Stop conditions

Stop and report if:

- expected factor count cannot be inferred;
- report cannot be generated without unstable imports;
- implementation would require recomputing factor_values or expensive diagnostics;
- adding paper stages to the workflow would require a large refactor;
- checks would be hardcoded to current factor count.

## 15. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
feat: add reusable factor library staleness monitor
```

Final response should include:

- commit hash
- summary verdict
- workflow reconciliation summary
- why it is reusable
- expected factor count source
- report status counts
- recommended next commands
- validation results
- limitations
- recommended next PM
