# PM-25 Prompt — Reusable Staleness / Workflow Monitor

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows the repaired paper/regime sequence:

- PM-21B: reproducible paper portfolio data repair
- PM-22B: repaired paper portfolio page integration
- PM-23B: refreshed regime diagnostics using repaired paper returns
- PM-24B: refreshed regime section on `factor-evaluation.html`

Now the factor library has a richer evaluation stack. PM-25 should add a reusable workflow/staleness monitor.

This must **not** be a one-off checker for the current 71 factors. It must dynamically infer expected counts and dependencies from the current registry/state/manifest/pipeline outputs.

## 0. PM objective

Create a reusable monitor that answers:

1. Given the current registry, what is the current factor count?
2. Which downstream outputs should cover all current factors?
3. Which outputs are missing or stale relative to their dependencies?
4. If a user adds new factors, which stages need to be rerun?
5. Does the public page reflect the latest paper/regime/scorecard outputs?
6. Does the regeneration workflow know about current stages?

The monitor should be a workflow navigation tool, not a static audit artifact.

## 1. Strict prohibitions

Do **not** hardcode `71` or any current factor count.

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify signal panel construction.

Do **not** create a new public page.

Do **not** rebuild expensive outputs unless the user explicitly runs a refresh stage.

Do **not** create multiple narrative docs. Keep docs minimal and canonical.

Do **not** make production/live/trading claims.

## 2. Required script

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

The script should be cheap and read-only by default.

## 3. Required outputs

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

## 4. Dynamic expected count logic

Expected factor count must be dynamic.

Use, in order of preference:

1. `research/factor_runs/crypto_top50_factor_library/factor_library_state.json` if present and current;
2. fallback to `scripts/factor_formula_registry.py` / registry import if state is missing;
3. never hardcode the current factor count.

The report should include:

```text
expected_factor_count
expected_pair_count = n * (n - 1) / 2
source_of_expected_count
```

## 5. Coverage checks

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

Expected behavior:

- if a new factor is added to registry but paper outputs are stale, report that paper diagnostics need rerun;
- if regime outputs are stale after paper rerun, report that regime needs rerun;
- if page is older than paper/regime payloads, report that page needs rerun.

## 6. Pairwise redundancy checks

Check:

```text
factor_pairwise_redundancy.csv
```

Expected rows:

```text
expected_pair_count = n * (n - 1) / 2
```

Do not hardcode 2485.

If row count is lower, recommend rerunning redundancy stage.

## 7. Timestamp staleness checks

Implement dependency mtime checks.

Recommended dependency graph:

```text
factor_formula_registry.py
  -> factor_values
  -> factor diagnostics
  -> scorecard
  -> redundancy
  -> scorecard refresh
  -> paper diagnostics
  -> paper page payload
  -> regime diagnostics
  -> factor-evaluation page
  -> factor_library_state
```

At minimum check:

1. `factor_quality_scorecard.csv` newer than `factor_redundancy_summary.csv` when redundancy exists;
2. `single_factor_paper_page_payload.json` newer than PM-21B compact paper files;
3. `factor_regime_diagnostics_payload.json` newer than `single_factor_paper_monthly_returns.csv`;
4. `factor-evaluation.html` newer than `single_factor_paper_page_payload.json` and `factor_regime_diagnostics_payload.json`;
5. `factor_library_state.json` newer than major refreshed outputs, or report state may be stale.

If mtime is unavailable or unreliable, report WARN, not FAIL.

## 8. Workflow stage checks

Check `scripts/run_factor_library_refresh.py` supports current canonical stages or presets.

Expected stage concepts:

```text
registry-integrity
catalog
values
direction-audit
evaluate
diagnostics
metadata
scorecard
redundancy
paper-diagnostics
paper-page-payload
regime
page
state
cheap
all
```

Names may vary slightly; do not force exact spelling if the script has documented aliases. But the monitor should map missing capability to a recommended action.

If `paper-diagnostics` or `paper-page-payload` is missing from the refresh workflow, report WARN/HIGH and recommend integration.

Do not add new stages in PM-25 unless it is a minimal, obvious fix.

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

## 11. Optional workflow integration

If easy and clean, add a read-only stage to:

```text
scripts/run_factor_library_refresh.py
```

Suggested stage name:

```text
staleness
```

Example:

```bash
python scripts/run_factor_library_refresh.py --stage staleness
```

Do not make this stage modify outputs except the staleness report itself.

If adding the stage would require larger orchestration refactor, skip and document.

## 12. Required audit

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
4. Expected factor count source.
5. Coverage check summary.
6. Pairwise redundancy check summary.
7. Timestamp staleness summary.
8. Workflow stage check summary.
9. Page content check summary.
10. Recommended next commands from the monitor.
11. Validation results.
12. Limitations.
13. Non-change statement: no factors, formulas, factor_values, signal panel, public page creation.
14. Recommended next PM: PM-26 capacity/liquidity proxy diagnostics.

## 13. Validation

Run:

```bash
python -m py_compile scripts/check_factor_library_staleness.py
python scripts/check_factor_library_staleness.py
python scripts/check_factor_library_staleness.py --json
```

If `run_factor_library_refresh.py` is updated, also run:

```bash
python -m py_compile scripts/run_factor_library_refresh.py
python scripts/run_factor_library_refresh.py --stage staleness --dry-run
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
- report exists in CSV and JSON;
- monitor gives actionable rerun commands if anything is stale.

## 14. Allowed files to change

Allowed scripts:

```text
scripts/check_factor_library_staleness.py
scripts/run_factor_library_refresh.py   # optional, only for staleness stage
```

Allowed outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_library_staleness_report.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_library_staleness_report.json
```

Allowed docs:

```text
docs/factor_library/audits/pm25_reusable_staleness_workflow_monitor.md
```

Do not modify factor-evaluation.html in PM-25 unless you discover a critical issue; prefer reporting it.

## 15. Stop conditions

Stop and report if:

- expected factor count cannot be inferred;
- report cannot be generated without importing unstable runtime state;
- implementation would require recomputing factor_values or expensive diagnostics;
- adding workflow integration would require large refactor;
- checks would be hardcoded to current factor count.

## 16. Commit rules

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
- why it is reusable
- expected factor count source
- report status counts
- recommended next commands
- validation results
- limitations
- recommended next PM
