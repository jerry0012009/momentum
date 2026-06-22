# PM-25 Prompt — Factor Library Health, Staleness, and Workflow Consistency Monitor

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-24:

- `docs/factor_library/audits/pm24_btc_market_regime_page_integration.md`
- `scripts/_build_factor_eval_html.py`
- `reports/site/factor-library/factor-evaluation.html`

The factor evaluation page now includes scorecard, redundancy, paper portfolio diagnostics, cost sensitivity, and BTC / market regime diagnostics.

However, PM-24 audit contains a workflow inconsistency warning:

> `No REGENERATION_CONTRACT.md found; page dependency on regime files should be documented when contract is created`

This is incorrect/stale because PM-20 created `docs/factor_library/REGENERATION_CONTRACT.md`, and PM-23 already added the regime stage to the regeneration workflow.

PM-25 should not add new factor analytics. It should make the pipeline self-checking.

## 0. PM objective

Create a health / staleness / workflow consistency monitor for the factor library.

The monitor should answer:

1. Are all canonical artifacts present?
2. Do row counts and factor coverage match expected 71 factors?
3. Are generated outputs stale relative to their dependencies?
4. Does `run_factor_library_refresh.py` know about every official stage?
5. Does `REGENERATION_CONTRACT.md` document all current stages and page dependencies?
6. Do public pages include all current diagnostic sections?
7. Are entry docs free of stale old counts?

This is a governance / reliability PM, not a new analytics PM.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify `scripts/factor_formula_registry.py`.

Do **not** modify `scripts/factor_ops.py`.

Do **not** modify signal panel construction.

Do **not** rebuild signal panel.

Do **not** create a new public HTML page.

Do **not** add multiple new narrative docs. Keep documentation changes minimal and canonical.

Do **not** make production/live/tradeability/alpha claims.

## 2. Required script

Create:

```text
scripts/check_factor_library_health.py
```

Recommended CLI:

```bash
python scripts/check_factor_library_health.py
python scripts/check_factor_library_health.py --strict
```

The script should produce a machine-readable report and a compact table.

## 3. Required outputs

Write reports to:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/
```

Required files:

```text
factor_library_health_report.json
factor_library_health_report.csv
```

Create audit:

```text
docs/factor_library/audits/pm25_factor_library_health_staleness_monitor.md
```

Do not create more docs unless needed.

## 4. Health checks to implement

### 4.1 Canonical artifact presence

Check these required artifacts exist:

```text
research/factor_runs/crypto_top50_factor_library/factor_library_state.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_diagnostics_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_pairwise_redundancy.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_page_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_turnover.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_exposure_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_diagnostics_payload.json
reports/site/factor-library/factor-evaluation.html
docs/factor_library/REGENERATION_CONTRACT.md
scripts/run_factor_library_refresh.py
```

### 4.2 Coverage checks

Expected coverage:

```text
registered_factors = 71
factor_values = 71
scorecard_rows = 71
redundancy_summary_rows = 71
single_factor_paper_summary_rows = 71
single_factor_paper_payload_factors = 71
regime_exposure_rows = 71
```

If counts differ, report status WARN or FAIL.

### 4.3 Pair coverage checks

Expected:

```text
factor_pairwise_redundancy rows = C(71,2) = 2485
```

### 4.4 Workflow stage checks

Check `scripts/run_factor_library_refresh.py` supports stages/presets for at least:

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
paper-diagnostics or paper
paper-page-payload or paper-page
regime
page
state
cheap
all
```

If PM-21/22 paper stages are not in the orchestrator, add them.

If PM-23 regime stage is not in the orchestrator, add it.

Expensive stages must remain guarded by `--expensive-ok`:

```text
evaluate
redundancy
```

Do not mark page/paper payload/regime as expensive unless there is clear reason.

### 4.5 Regeneration contract checks

Check `docs/factor_library/REGENERATION_CONTRACT.md` documents current official stages:

```text
paper diagnostics
paper page payload
regime diagnostics
factor-evaluation page dependencies on paper and regime outputs
state regenerated last
```

If missing, update `REGENERATION_CONTRACT.md` minimally.

Do not create a second workflow document.

### 4.6 Manifest checks

Check `docs/factor_library/factor_library_manifest.json` lists:

- `build_single_factor_paper_portfolio_diagnostics.py`
- `build_single_factor_paper_page_payload.py`
- `build_factor_market_regime_diagnostics.py`
- paper diagnostic outputs
- regime diagnostic outputs
- factor-evaluation page dependency on paper/regime diagnostics if manifest has dependency fields

Update manifest minimally if missing.

### 4.7 Page section checks

Check `reports/site/factor-library/factor-evaluation.html` contains:

```text
Factor Quality Scorecard
Redundancy & Novelty
Single-Factor Paper Portfolio
BTC / Market Regime Diagnostics
研究诊断
不是交易策略
```

Report PASS/WARN/FAIL.

### 4.8 Stale doc checks

Check entry docs do not contain stale old status:

```text
65 registered
59 computed
6 missing
6 taker/funding factors missing
Missing factor_values: **6**
```

If present, update canonical entry docs minimally:

```text
docs/factor_library/START_HERE.md
docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md
```

### 4.9 Staleness checks by mtime

Implement a simple dependency timestamp check.

Examples:

- if `factor_quality_scorecard.csv` older than `factor_redundancy_summary.csv`, scorecard may be stale;
- if `factor-evaluation.html` older than `single_factor_paper_page_payload.json`, page may be stale;
- if `factor-evaluation.html` older than `factor_regime_diagnostics_payload.json`, page may be stale;
- if `factor_library_state.json` older than major diagnostics outputs, state may be stale.

Use WARN, not hard FAIL, unless clearly broken.

## 5. Required report schema

`factor_library_health_report.csv` should have one row per check.

Required columns:

```text
check_id
check_group
status
severity
message
artifact_path
expected
actual
recommended_action
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

`factor_library_health_report.json` should include:

```text
summary_status
generated_at
n_pass
n_warn
n_fail
n_skip
checks
```

Suggested summary status:

```text
HEALTH_PASS
HEALTH_PASS_WITH_WARNINGS
HEALTH_FAIL
```

## 6. Optional integration into workflow

Add `health` stage to `scripts/run_factor_library_refresh.py`:

```bash
python scripts/run_factor_library_refresh.py --stage health
```

If added, update `REGENERATION_CONTRACT.md` and manifest accordingly.

The health stage should be cheap.

## 7. Validation

Run:

```bash
python -m py_compile scripts/check_factor_library_health.py scripts/run_factor_library_refresh.py
python scripts/check_factor_library_health.py
python scripts/check_factor_library_health.py --strict
python scripts/run_factor_library_refresh.py --stage health --dry-run
```

Then:

```bash
python - <<'PY'
import json
import pandas as pd
from pathlib import Path
base = Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics')
report = json.loads((base / 'factor_library_health_report.json').read_text(encoding='utf-8'))
checks = pd.read_csv(base / 'factor_library_health_report.csv')
print('summary_status', report.get('summary_status'))
print('status counts')
print(checks['status'].value_counts(dropna=False))
print('high severity warnings/failures')
print(checks[checks['severity'].isin(['HIGH','BLOCKER'])][['check_id','status','message','recommended_action']].to_string(index=False))
PY
```

Expected:

- no BLOCKER failures;
- warnings are acceptable if documented;
- stale PM-24 audit text itself does not need rewriting unless you choose to append a correction note. Prefer not to rewrite old audits.

## 8. Required audit note

Create:

```text
docs/factor_library/audits/pm25_factor_library_health_staleness_monitor.md
```

Audit must include:

1. Summary verdict:
   - `FACTOR_LIBRARY_HEALTH_PASS`
   - `FACTOR_LIBRARY_HEALTH_PASS_WITH_WARNINGS`
   - `FACTOR_LIBRARY_HEALTH_FAIL`
2. Files changed.
3. Health report summary counts.
4. Coverage checks result.
5. Workflow stage checks result.
6. Regeneration contract updates, if any.
7. Manifest updates, if any.
8. Page section checks result.
9. Staleness checks result.
10. Validation results.
11. Remaining warnings.
12. Non-change statement: no factors, formulas, factor_values, signal panel, public page creation.
13. Recommended next PM.

## 9. Allowed files to change

Allowed scripts:

```text
scripts/check_factor_library_health.py
scripts/run_factor_library_refresh.py
```

Allowed reports:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_library_health_report.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_library_health_report.csv
```

Allowed docs:

```text
docs/factor_library/REGENERATION_CONTRACT.md
docs/factor_library/START_HERE.md
docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md
docs/factor_library/factor_library_manifest.json
docs/factor_library/audits/pm25_factor_library_health_staleness_monitor.md
```

Do not modify page HTML unless the health check discovers a clear missing required section. Prefer reporting over modifying page in PM-25.

## 10. Stop conditions

Stop and report if:

- health script cannot determine canonical paths;
- artifacts are missing in a way that requires recomputation;
- fixing the issue would require changing factors, formulas, factor_values, or signal panel;
- page repair would require a major redesign.

## 11. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
feat: add factor library health and staleness monitor
```

Final response should include:

- commit hash
- summary verdict
- health report status counts
- key warnings/failures
- workflow/contract updates
- validation results
- limitations
- recommended next PM
