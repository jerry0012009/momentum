# PM-32B Prompt — Workflow Alignment and Evidence Matrix Repair

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task repairs PM-32.

PM-32 successfully created a unified factor profile, workflow contract, and evidence matrix. However, PM-32 has workflow alignment problems that must be fixed before we treat the factor library as reusable for future factor intake.

Read first:

```text
docs/factor_library/START_HERE.md
docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md
docs/factor_library/REGENERATION_CONTRACT.md
scripts/run_factor_library_refresh.py
scripts/build_unified_factor_profile.py
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_workflow_contract.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_evidence_matrix.csv
```

## 0. Why PM-32B is required

PM-32 is conceptually correct but structurally incomplete.

Known issues to repair:

1. `run_factor_library_refresh.py` places `profile` immediately after `cluster`, before paper diagnostics, paper payload, regime, shape/stability, decile, and capacity/liquidity.
2. `REGENERATION_CONTRACT.md` also places `profile` too early.
3. `factor_evaluation_workflow_contract.json` lists stages such as `quantile-shape`, `rolling-stability`, `decile-shape`, and `capacity-liquidity`, but not all of those stages are actually present in `run_factor_library_refresh.py`.
4. The contract uses script names that may not match actual scripts, for example split quantile/rolling scripts even though the actual PM-26 script is `build_factor_shape_stability_diagnostics.py`.
5. Evidence matrix is narrower than required. It lacks direct checks such as `has_factor_values`, `has_factor_level_evaluation`, and `has_unified_profile`.
6. Staleness monitor was not updated for profile / workflow contract / evidence matrix outputs.

PM-32B must make the workflow contract, runner, regeneration contract, staleness checks, and evidence matrix consistent.

Do **not** update public HTML in PM-32B.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify signal panel construction.

Do **not** create or modify public HTML pages.

Do **not** enter signal evaluation or portfolio construction.

Do **not** overfit profile scoring.

This is workflow correctness and evidence coverage repair.

## 2. Required workflow alignment

Update:

```text
scripts/run_factor_library_refresh.py
docs/factor_library/REGENERATION_CONTRACT.md
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_workflow_contract.json
```

The actual runner stage order, regeneration contract order, and workflow contract `stage_order` must agree.

The profile stage must run **after all upstream factor-evaluation diagnostics** and before staleness/page/state.

Required logical order:

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
cluster
paper-diagnostics
paper-page-payload
regime
shape-stability
decile-shape
capacity-liquidity
profile
staleness
page
state
```

If exact stage names differ, choose clear names, but the runner, contract, and workflow JSON must match exactly.

## 3. Required runner stages

Ensure these stages exist in `scripts/run_factor_library_refresh.py` if the scripts exist:

```text
shape-stability -> python scripts/build_factor_shape_stability_diagnostics.py
decile-shape -> python scripts/build_factor_decile_shape_diagnostics.py
capacity-liquidity -> python scripts/build_factor_capacity_liquidity_diagnostics.py
profile -> python scripts/build_unified_factor_profile.py
```

`profile` must run after these stages.

If any script is missing, do not invent a fake stage. Document the mismatch and stop if the profile cannot be made reliable.

## 4. Required workflow contract checks

Modify `scripts/build_unified_factor_profile.py` so the generated `factor_evaluation_workflow_contract.json` reflects the actual runner.

Required fields:

```text
workflow_name
workflow_version
purpose
not_production_disclaimer
stage_order
stage_definitions
required_outputs_by_stage
expensive_stage_flags
rerun_rules
factor_added_required_stages
profile_required_inputs
page_ready_required_outputs
contract_alignment_checks
```

Add `contract_alignment_checks` with:

```text
runner_stage_order_matches_contract
regen_contract_mentions_profile_after_upstream_diagnostics
profile_stage_after_capacity_liquidity
profile_stage_before_staleness
missing_runner_stages
extra_contract_stages_not_in_runner
```

## 5. Required evidence matrix repair

Regenerate:

```text
factor_evaluation_evidence_matrix.csv
factor_evaluation_evidence_matrix.json
```

Evidence matrix must include these fields:

```text
factor_id
has_factor_values
has_factor_level_evaluation
has_diagnostics_summary
has_bilingual_card
has_scorecard
has_pairwise_redundancy
has_cluster_membership
has_marginal_information
has_paper_portfolio
has_fee_sensitivity
has_regime_diagnostics
has_quantile_shape
has_rolling_stability
has_decile_shape
has_capacity_liquidity
has_unified_profile
n_available_evidence_blocks
n_required_evidence_blocks
evidence_completeness_rate
evidence_status
missing_evidence_blocks
stale_evidence_blocks
```

If a factor has registry status such as `MISSING_INPUT_DATA` but still has downstream diagnostics, keep `evidence_status=COMPLETE` only if required artifacts exist, but add a separate column:

```text
registry_or_data_status
```

This avoids confusing evidence completeness with data availability status.

## 6. Required profile repair

Regenerate:

```text
factor_unified_profile_summary.csv
factor_unified_profile_summary.json
factor_profile_component_scores.csv
factor_profile_payload.json
factor_profile_manifest.json
```

Do not overfit scoring, but ensure profile fields reflect the repaired evidence matrix and workflow contract.

Add these fields if missing:

```text
registry_or_data_status
evidence_status
evidence_completeness_rate
workflow_ready_status
workflow_missing_or_stale_blocks
```

Allowed `workflow_ready_status` values:

```text
WORKFLOW_READY
WORKFLOW_READY_WITH_WARNINGS
WORKFLOW_INCOMPLETE
WORKFLOW_BLOCKED
```

## 7. Staleness monitor repair

Update if feasible:

```text
scripts/check_factor_library_staleness.py
```

Add checks for:

```text
factor_evaluation_workflow_contract.json
factor_evaluation_evidence_matrix.csv
factor_evaluation_evidence_matrix.json
factor_unified_profile_summary.csv
factor_unified_profile_summary.json
factor_profile_component_scores.csv
factor_profile_payload.json
factor_profile_manifest.json
```

The staleness report should flag if profile artifacts are older than upstream diagnostics.

If this becomes too large, document clearly in audit and stop only if workflow readiness cannot be assessed.

## 8. Required validation

Run:

```bash
python -m py_compile scripts/build_unified_factor_profile.py
python -m py_compile scripts/run_factor_library_refresh.py
python -m py_compile scripts/check_factor_library_staleness.py
python scripts/build_unified_factor_profile.py
python scripts/run_factor_library_refresh.py --stage profile --dry-run
python scripts/run_factor_library_refresh.py --stage all --dry-run
python scripts/check_factor_library_staleness.py
```

Then run alignment validation:

```bash
python - <<'PY'
import json
import importlib.util
from pathlib import Path

contract_path = Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_workflow_contract.json')
contract = json.loads(contract_path.read_text(encoding='utf-8'))

spec = importlib.util.spec_from_file_location('refresh', 'scripts/run_factor_library_refresh.py')
refresh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(refresh)

runner = list(refresh.STAGE_NAMES)
contract_order = list(contract['stage_order'])
print('runner stages:', runner)
print('contract stages:', contract_order)
print('runner==contract', runner == contract_order)

for a, b in [('capacity-liquidity', 'profile'), ('profile', 'staleness')]:
    print(a, '<', b, contract_order.index(a) < contract_order.index(b))
PY
```

Evidence validation:

```bash
python - <<'PY'
import pandas as pd
from pathlib import Path
base = Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics')
ev = pd.read_csv(base / 'factor_evaluation_evidence_matrix.csv')
profile = pd.read_csv(base / 'factor_unified_profile_summary.csv')
required_cols = [
    'has_factor_values', 'has_factor_level_evaluation', 'has_unified_profile',
    'registry_or_data_status', 'evidence_status', 'evidence_completeness_rate'
]
print('evidence factors', ev['factor_id'].nunique())
print('profile factors', profile['factor_id'].nunique())
for c in required_cols:
    print(c, c in ev.columns or c in profile.columns)
print('evidence statuses')
print(ev['evidence_status'].value_counts(dropna=False).to_string())
if 'workflow_ready_status' in profile.columns:
    print('workflow readiness')
    print(profile['workflow_ready_status'].value_counts(dropna=False).to_string())
PY
```

Forbidden language check:

```bash
python - <<'PY'
from pathlib import Path
paths = [
    Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_unified_profile_summary.csv'),
    Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_profile_payload.json'),
    Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_workflow_contract.json'),
]
bad = ['trade this factor', 'deploy this factor', 'remove this factor', 'drop this factor', 'only keep', 'portfolio allocation', 'signal weight', 'buy', 'sell', '交易该因子', '上线该因子', '删除', '剔除', '淘汰', '只保留', '配置权重', '买入', '卖出']
for p in paths:
    txt = p.read_text(encoding='utf-8', errors='ignore').lower()
    hits = [b for b in bad if b.lower() in txt]
    print(p.name, 'BAD_HITS=', hits)
PY
```

## 9. Required audit

Create:

```text
docs/factor_library/audits/pm32b_workflow_alignment_evidence_repair.md
```

Audit must include:

1. Summary verdict:
   - `WORKFLOW_ALIGNMENT_EVIDENCE_REPAIR_PASS`
   - `WORKFLOW_ALIGNMENT_EVIDENCE_REPAIR_PASS_WITH_LIMITATIONS`
   - `WORKFLOW_ALIGNMENT_EVIDENCE_REPAIR_BLOCKED`
2. Why PM-32B was required.
3. Files changed.
4. Runner stage order before/after.
5. Workflow contract stage order.
6. Confirmation runner stage order equals contract stage order.
7. Confirmation profile runs after capacity-liquidity and before staleness.
8. Evidence matrix column coverage.
9. Factor coverage.
10. Evidence status distribution.
11. Workflow ready status distribution.
12. Staleness monitor update status.
13. Regeneration contract update status.
14. Forbidden-language scan.
15. Limitations.
16. Non-change statement: no factors, formulas, factor_values, signal panel, public page.
17. Recommended next PM: PM-33 unified profile page integration and workflow-readiness presentation.

## 10. Allowed files to change

Allowed scripts:

```text
scripts/build_unified_factor_profile.py
scripts/run_factor_library_refresh.py
scripts/check_factor_library_staleness.py
```

Allowed docs:

```text
docs/factor_library/REGENERATION_CONTRACT.md
docs/factor_library/audits/pm32b_workflow_alignment_evidence_repair.md
```

Allowed outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_workflow_contract.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_evidence_matrix.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_evidence_matrix.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_unified_profile_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_unified_profile_summary.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_profile_component_scores.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_profile_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_profile_manifest.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_library_staleness_report.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_library_staleness_report.json
```

Do not modify:

```text
reports/site/factor-library/factor-evaluation.html
scripts/_build_factor_eval_html.py
scripts/factor_formula_registry.py
scripts/factor_ops.py
scripts/build_factor_values.py
scripts/build_phase9b_signal_panel.py
```

## 11. Stop conditions

Stop and report if:

- runner and contract cannot be aligned;
- required upstream diagnostic scripts are missing;
- profile cannot be placed after all required upstream diagnostics;
- evidence matrix cannot check factor_values or factor-level evaluation;
- fixing this would require modifying factor formulas, factor_values, signal panel, or public page.

## 12. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
fix: align unified profile workflow contract
```

Final response should include:

- commit hash
- summary verdict
- runner/contract alignment result
- stage order
- evidence matrix repair summary
- factor coverage
- workflow readiness distribution
- staleness integration status
- validation results
- limitations
- recommended next PM
