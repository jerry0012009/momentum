# PM-35 Prompt — Controlled Factor Intake Batch 01

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-34:

- factor expansion backlog created;
- intake-readiness checklist passed;
- no factors were registered in PM-34;
- BATCH_01_CONTROLLED_INTAKE identified 5 candidate factors.

PM-35 is the first actual controlled factor intake batch after the workflow was built.

The goal is to register a small batch of new factors, compute factor values, run the fixed evaluation workflow, and confirm the new factors appear in evidence matrix, unified profile, and factor-evaluation page.

## 0. PM objective

Register and evaluate BATCH_01 factors under the fixed workflow.

Candidate list from PM-34:

```text
rev_2h
mom_vol_adjusted_20h
range_breakout_vol_confirm_20h
volume_pressure_20h
xs_rank_mom_accel
```

This is still factor research evaluation. Do **not** modify signal panel or construct signals.

## 1. Strict prohibitions

Do **not** modify `scripts/build_phase9b_signal_panel.py`.

Do **not** add new signal variants.

Do **not** enter signal evaluation.

Do **not** enter portfolio construction.

Do **not** make alpha/trading claims.

Do **not** modify live trading, strategy, broker, exchange, or execution code.

Do **not** create a parallel evaluator or one-off report format.

Do **not** bypass `run_factor_intake.py` or `run_factor_library_refresh.py`.

## 2. Required files to inspect first

Read:

```text
docs/factor_library/START_HERE.md
docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md
docs/factor_library/REGENERATION_CONTRACT.md
docs/factor_library/FACTOR_EXPANSION_BACKLOG.md
scripts/factor_formula_registry.py
scripts/factor_specs.py
scripts/factor_ops.py
scripts/build_factor_values.py
scripts/run_factor_intake.py
scripts/run_factor_library_refresh.py
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_expansion_backlog.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_workflow_contract.json
```

## 3. Candidate implementation rules

### 3.1 `rev_2h`

Formula sketch:

```text
-(close / delay(close, 2) - 1)
```

Expected direction: positive.

Use existing delay / return operators where possible.

### 3.2 `mom_vol_adjusted_20h`

Formula sketch:

```text
mom_20h / rolling_std(pct_change(close), 20)
```

Expected direction: positive.

Must handle zero/near-zero volatility safely.

### 3.3 `range_breakout_vol_confirm_20h`

Formula sketch:

```text
breakout_dist_20h * zscore(volume, 20), preferably only when breakout_dist_20h > 0
```

Expected direction: positive.

Use existing range/breakout and zscore operators where possible.

### 3.4 `volume_pressure_20h`

Formula sketch:

```text
rolling_mean(sign(delta(close, 1)) * volume, 20)
```

Expected direction: positive.

If sign/where/conditional operators do not exist, add only a small reusable helper to `factor_ops.py`; do not modify factor value pipeline globally.

### 3.5 `xs_rank_mom_accel`

Formula sketch:

```text
cross-sectional rank of momentum acceleration per timestamp
```

Expected direction: positive.

This candidate is MEDIUM complexity.

Only implement it if the existing factor pipeline already supports cross-sectional ranking or a small, localized implementation is possible without invasive changes to `build_factor_values.py`.

If implementation requires broad changes to factor value generation, defer `xs_rank_mom_accel` to a later PM and document it in the audit. Do not break pipeline consistency for this one candidate.

## 4. Allowed implementation changes

Allowed:

```text
scripts/factor_formula_registry.py
scripts/factor_ops.py              # only small reusable helpers if necessary
docs/factor_library/audits/pm35_controlled_factor_intake_batch01.md
```

Generated/updated outputs from pipeline are allowed, including:

```text
data/features/.../<new_factor_id>/factor_values.parquet
research/factor_runs/crypto_top50_factor_library/factor_intake/<run_id>/...
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/...
reports/site/factor-library/factor-evaluation.html
research/factor_runs/crypto_top50_factor_library/factor_library_state.json
research/factor_runs/crypto_top50_factor_library/factor_library_state.md
```

Do not manually edit generated outputs except through scripts.

## 5. Required commands

Use a clear run id:

```text
pm35_batch01_controlled_intake
```

After registering factors, run:

```bash
python scripts/check_factor_registry_integrity.py
python scripts/check_factor_catalog_integrity.py || true
python scripts/run_factor_intake.py --factor-ids <implemented_factor_ids...> --run-id pm35_batch01_controlled_intake
```

Then run full workflow refresh:

```bash
python scripts/run_factor_library_refresh.py --stage all --expensive-ok
```

If a full refresh is too slow, do not silently skip it. Report partial execution and stop with a clear audit status.

## 6. Required validation after refresh

Verify new factors appear in:

```text
factor_library_state.json
factor_evaluation_evidence_matrix.csv
factor_unified_profile_summary.csv
factor_profile_payload.json
factor_expansion_backlog.csv / docs, if marked as consumed or registered
reports/site/factor-library/factor-evaluation.html
```

Run:

```bash
python - <<'PY'
import json
import pandas as pd
from pathlib import Path
new = ['rev_2h', 'mom_vol_adjusted_20h', 'range_breakout_vol_confirm_20h', 'volume_pressure_20h', 'xs_rank_mom_accel']
base = Path('research/factor_runs/crypto_top50_factor_library')
state = json.loads((base / 'factor_library_state.json').read_text(encoding='utf-8'))
diag = base / 'factor_diagnostics'
evidence = pd.read_csv(diag / 'factor_evaluation_evidence_matrix.csv')
profile = pd.read_csv(diag / 'factor_unified_profile_summary.csv')
html = Path('reports/site/factor-library/factor-evaluation.html').read_text(encoding='utf-8')
for f in new:
    print(f, {
        'in_state': f in str(state),
        'in_evidence': f in set(evidence['factor_id']),
        'in_profile': f in set(profile['factor_id']),
        'in_html': f in html,
    })
print('total evidence factors', evidence['factor_id'].nunique())
print('total profile factors', profile['factor_id'].nunique())
print('new profiles')
print(profile[profile['factor_id'].isin(new)][['factor_id','profile_class','workflow_ready_status','evidence_status','recommended_research_action']].to_string(index=False))
PY
```

Also run:

```bash
python scripts/check_factor_library_staleness.py
```

## 7. Required audit

Create:

```text
docs/factor_library/audits/pm35_controlled_factor_intake_batch01.md
```

Audit must include:

1. Summary verdict:
   - `CONTROLLED_FACTOR_INTAKE_BATCH01_PASS`
   - `CONTROLLED_FACTOR_INTAKE_BATCH01_PASS_WITH_LIMITATIONS`
   - `CONTROLLED_FACTOR_INTAKE_BATCH01_BLOCKED`
2. Implemented factor list.
3. Deferred factor list, if any.
4. Files changed.
5. Formula summary and expected direction for each implemented factor.
6. Whether any new factor_ops helper was added.
7. Registry integrity validation.
8. Intake run id and output location.
9. Full refresh status.
10. Evidence matrix coverage for new factors.
11. Unified profile rows for new factors.
12. Workflow readiness status for new factors.
13. Page inclusion status for new factors.
14. Staleness result.
15. Confirmation no signal panel modification.
16. Confirmation no live/strategy/execution code modification.
17. Limitations.
18. Recommended next PM: PM-36 post-intake workflow regression audit.

## 8. Stop conditions

Stop and report if:

- factor registry integrity fails;
- factor values cannot be computed for a new factor;
- intake runner fails;
- full refresh fails;
- new factors do not appear in evidence matrix/profile;
- implementing `xs_rank_mom_accel` requires invasive pipeline changes;
- signal panel or live/strategy code would need modification.

## 9. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
feat: add controlled factor intake batch 01
```

Final response should include:

- commit hash
- summary verdict
- implemented factors
- deferred factors, if any
- validation results
- factor count before/after
- evidence/profile/page inclusion status
- profile classes for new factors
- staleness result
- limitations
- recommended next PM
