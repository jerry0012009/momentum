# PM-32 Prompt — Unified Factor Evaluation Workflow Contract and Factor Profile

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This PM is important. Read these files before coding:

```text
docs/factor_library/START_HERE.md
docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md
docs/factor_library/REGENERATION_CONTRACT.md
scripts/run_factor_library_refresh.py
scripts/run_factor_intake.py
research/factor_runs/crypto_top50_factor_library/factor_library_state.json
```

PM-32 is **not merely a profile table**. PM-32 should formalize a reusable factor evaluation workflow so that every future factor added through intake can be evaluated, explained, checked for completeness, and surfaced in a consistent human-readable format.

The repository goal is a reliable, extensible, readable crypto perpetual cross-sectional factor library research system. It is not live trading, not investment advice, and not alpha certification.

## 0. PM objective

Create a unified **factor evaluation workflow contract** plus a unified per-factor profile layer.

This should answer two linked questions:

1. **Workflow question:** after a new factor is introduced, what exact evaluation stages must run, in what order, and which artifacts must exist before the factor is considered fully evaluated?
2. **Interpretation question:** after all stages run, what does the system say about this factor across quality, paper portfolio, cost, regime, shape, rolling stability, decile shape, capacity/liquidity, redundancy, cluster, and marginal information?

This is still factor evaluation. Do **not** enter signal selection, signal construction, or portfolio construction.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify signal panel construction.

Do **not** create or modify public HTML pages.

Do **not** enter signal evaluation.

Do **not** recommend portfolio weights.

Do **not** recommend deleting, dropping, or removing factors.

Do **not** use trading language such as buy, sell, deploy, allocate, execute, or live.

Use diagnostic and research-review language only.

## 2. Required conceptual boundary

PM-32 should define the reusable **factor evaluation workflow**, not the signal workflow.

The full factor evaluation path should cover:

```text
registry
  → registry integrity
  → factor catalog
  → factor values
  → direction audit
  → factor-level evaluation
  → diagnostics metrics
  → bilingual cards
  → scorecard
  → pairwise redundancy
  → redundancy cluster / marginal information
  → paper portfolio diagnostics
  → paper page payload
  → regime diagnostics
  → quantile shape / rolling stability
  → direction-aware decile shape
  → selected-basket capacity/liquidity
  → unified factor profile
  → staleness / completeness check
  → page-ready payloads
  → factor_library_state
```

Signal panel and signal-level evaluation remain out of scope.

## 3. Required new script

Create:

```text
scripts/build_unified_factor_profile.py
```

This script must build both:

1. the unified per-factor profile outputs;
2. the factor evaluation workflow/evidence contract outputs.

Recommended command:

```bash
python scripts/build_unified_factor_profile.py
```

Optional arguments:

```bash
--output-dir research/factor_runs/crypto_top50_factor_library/factor_diagnostics
--state-path research/factor_runs/crypto_top50_factor_library/factor_library_state.json
```

## 4. Required workflow contract output

Create:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_workflow_contract.json
```

This must be machine-readable and include:

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
```

Each stage definition should include:

```text
stage_id
display_name_zh
display_name_en
script
is_expensive
inputs
outputs
must_run_after
what_it_answers_zh
what_it_answers_en
```

The contract must clearly say that when a new factor is added, downstream diagnostics must be refreshed before the factor is fully evaluated.

## 5. Required evidence matrix

Create:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_evidence_matrix.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_evidence_matrix.json
```

One row per factor, with evidence status across all dimensions:

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

Allowed `evidence_status` values:

```text
COMPLETE
COMPLETE_WITH_WARNINGS
INCOMPLETE
BLOCKED
```

This matrix is critical. It is what makes the workflow reusable for future new factors.

## 6. Required unified profile outputs

Create:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_unified_profile_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_unified_profile_summary.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_profile_component_scores.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_profile_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_profile_manifest.json
```

The profile should be page-ready, but PM-32 must not modify the page.

## 7. Required inputs for profile

Use existing outputs where available:

```text
research/factor_runs/crypto_top50_factor_library/factor_library_state.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_diagnostics_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_cluster_members.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_marginal_information_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_fee_sensitivity.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_exposure_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quantile_shape_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_rolling_stability_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_decile_shape_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_capacity_liquidity_summary.csv
```

Do not silently drop factors if some evidence is missing. Keep the factor and mark missing evidence in the evidence matrix.

## 8. Unified profile schema

`factor_unified_profile_summary.csv` should include:

```text
factor_id
family
status
expected_direction
evidence_status
evidence_completeness_rate
profile_score
profile_class
profile_confidence
standalone_quality_class
paper_portfolio_class
cost_risk_class
regime_dependency_class
shape_quality_class
rolling_stability_class
decile_shape_class
capacity_liquidity_class
cluster_id
cluster_size
cluster_member_role
marginal_information_class
primary_strength_zh
primary_strength_en
primary_risk_zh
primary_risk_en
profile_summary_zh
profile_summary_en
recommended_research_action
source_artifact_count
source_artifacts
```

Allowed `profile_class` values:

```text
HIGH_QUALITY_DISTINCT
HIGH_QUALITY_BUT_REDUNDANT
STABLE_BUT_CAPACITY_CONSTRAINED
PROMISING_BUT_REGIME_DEPENDENT
UNIQUE_BUT_WEAK
BROAD_WATCHLIST
LOW_PRIORITY_DIAGNOSTIC
INCOMPLETE_EVIDENCE
INSUFFICIENT_DATA
```

Allowed `recommended_research_action` values:

```text
PRIORITIZE_FOR_REVIEW
KEEP_AS_CLUSTER_REFERENCE
REVIEW_AS_REDUNDANT_ALTERNATIVE
WATCH_FOR_REGIME_DEPENDENCE
WATCH_FOR_CAPACITY_RISK
WATCH_FOR_STABILITY_RISK
KEEP_AS_DIAGNOSTIC_PROBE
LOWER_PRIORITY_REVIEW
COMPLETE_MISSING_EVIDENCE
INSUFFICIENT_DATA_REVIEW
```

These are research-review actions, not trading or portfolio actions.

## 9. Component score schema

`factor_profile_component_scores.csv` should include:

```text
factor_id
standalone_quality_component
paper_component
cost_component
regime_component
shape_component
stability_component
capacity_component
redundancy_component
marginal_information_component
evidence_completeness_component
profile_score
```

Suggested default weights:

```text
standalone_quality_component: 18%
paper_component: 14%
cost_component: 8%
regime_component: 10%
shape_component: 10%
stability_component: 14%
capacity_component: 8%
redundancy_component: 8%
marginal_information_component: 7%
evidence_completeness_component: 3%
```

Use transparent rule-based mapping. Do not fit weights to returns. Do not optimize weights.

If fields are missing, renormalize available components and reduce `profile_confidence`.

## 10. Source lineage requirement

For every profile factor, include a source lineage object in `factor_profile_payload.json`:

```text
factor_id
profile_score
profile_class
evidence_status
source_artifacts
component_source_map
missing_evidence_blocks
last_built_at
```

`component_source_map` should map each component to its source artifact and source columns where feasible.

This is necessary for readability and future auditability.

## 11. Workflow integration

Update:

```text
scripts/run_factor_library_refresh.py
```

Add a stage:

```text
profile
```

Command:

```bash
python scripts/build_unified_factor_profile.py
```

Position it after upstream diagnostics and before page/state. If current runner lacks some newer diagnostic stages, add `profile` conservatively and document prerequisites.

Update:

```text
docs/factor_library/REGENERATION_CONTRACT.md
```

The contract must explicitly include:

```text
capacity/liquidity + cluster/marginal information + shape/stability/decile
  → unified factor profile
  → page-ready outputs
  → state/staleness
```

Also update the “Adding a new factor” section so it clearly says that after intake, the library refresh must regenerate the unified profile before the factor is considered fully evaluated.

## 12. Staleness / completeness integration

Update if low risk:

```text
scripts/check_factor_library_staleness.py
```

Add checks for:

```text
factor_unified_profile_summary.csv
factor_profile_component_scores.csv
factor_profile_payload.json
factor_evaluation_evidence_matrix.csv
factor_evaluation_workflow_contract.json
```

If updating staleness monitor becomes too large, do not force it. Instead, audit must explicitly state that PM-33 should extend the staleness monitor. However, prefer updating it now if straightforward.

## 13. Diagnostic language rules

Allowed:

```text
higher priority for research review
useful cluster reference
requires capacity review
requires regime-dependence review
lower marginal information
complete missing evidence
```

Forbidden:

```text
trade this factor
deploy this factor
remove this factor
drop this factor
only keep this factor
portfolio allocation
signal weight
buy
sell
```

Chinese forbidden equivalents:

```text
交易该因子
上线该因子
删除
剔除
淘汰
只保留
配置权重
买入
卖出
```

## 14. Dynamic coverage requirements

Use expected factor count from `factor_library_state.json` or registry. Do not hardcode 71.

Audit must report:

```text
expected_factor_count
profile_factor_count
component_score_factor_count
evidence_matrix_factor_count
payload_factor_count
missing_factor_ids
profile_class_distribution
recommended_research_action_distribution
evidence_status_distribution
component_missingness_summary
```

## 15. Required audit

Create:

```text
docs/factor_library/audits/pm32_unified_factor_evaluation_workflow_profile.md
```

Audit must include:

1. Summary verdict:
   - `UNIFIED_FACTOR_EVALUATION_WORKFLOW_PASS`
   - `UNIFIED_FACTOR_EVALUATION_WORKFLOW_PASS_WITH_LIMITATIONS`
   - `UNIFIED_FACTOR_EVALUATION_WORKFLOW_BLOCKED`
2. Why PM-32 is a workflow/profile contract, not just a scorecard.
3. Why PM-32 is still factor evaluation, not signal construction.
4. Files changed.
5. Workflow contract summary.
6. Evidence matrix coverage.
7. Input artifacts used.
8. Component weights and class mappings.
9. Factor coverage.
10. Evidence status distribution.
11. Profile class distribution.
12. Recommended research action distribution.
13. Examples of high-quality distinct factors.
14. Examples of high-quality but redundant factors.
15. Examples of stable but capacity-constrained factors.
16. Examples of unique but weak factors.
17. Source lineage validation.
18. Workflow stage `profile` dry-run result.
19. Contract update status.
20. Staleness monitor update status.
21. Forbidden-language scan results.
22. Limitations.
23. Non-change statement: no factors, formulas, factor_values, signal panel, public page.
24. Recommended next PM: PM-33 unified profile page integration and workflow-readiness presentation.

## 16. Validation

Run:

```bash
python -m py_compile scripts/build_unified_factor_profile.py
python scripts/build_unified_factor_profile.py
python scripts/run_factor_library_refresh.py --stage profile --dry-run
```

Then:

```bash
python - <<'PY'
import json
import pandas as pd
from pathlib import Path
base = Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics')
profile = pd.read_csv(base / 'factor_unified_profile_summary.csv')
components = pd.read_csv(base / 'factor_profile_component_scores.csv')
evidence = pd.read_csv(base / 'factor_evaluation_evidence_matrix.csv')
payload = json.loads((base / 'factor_profile_payload.json').read_text(encoding='utf-8'))
contract = json.loads((base / 'factor_evaluation_workflow_contract.json').read_text(encoding='utf-8'))
print('profile factors', profile['factor_id'].nunique())
print('component factors', components['factor_id'].nunique())
print('evidence factors', evidence['factor_id'].nunique())
print('payload factors', len(payload.get('factors', [])))
print('workflow stages', len(contract.get('stage_order', [])))
print('profile classes')
print(profile['profile_class'].value_counts(dropna=False).to_string())
print('research actions')
print(profile['recommended_research_action'].value_counts(dropna=False).to_string())
print('evidence statuses')
print(evidence['evidence_status'].value_counts(dropna=False).to_string())
PY
```

Forbidden-language check:

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

Also run:

```bash
python scripts/check_factor_library_staleness.py
```

## 17. Allowed files to change

Allowed scripts:

```text
scripts/build_unified_factor_profile.py
scripts/run_factor_library_refresh.py
scripts/check_factor_library_staleness.py     # if low-risk and scoped
```

Allowed docs:

```text
docs/factor_library/REGENERATION_CONTRACT.md
docs/factor_library/audits/pm32_unified_factor_evaluation_workflow_profile.md
```

Allowed outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_unified_profile_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_unified_profile_summary.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_profile_component_scores.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_profile_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_profile_manifest.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_evidence_matrix.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_evidence_matrix.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_workflow_contract.json
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

## 18. Stop conditions

Stop and report if:

- too many required inputs are missing;
- factor coverage cannot be reconciled;
- workflow contract cannot be made consistent with `REGENERATION_CONTRACT.md`;
- scoring would require fitting to returns;
- implementation would require modifying factor formulas, factor_values, or signal panel;
- outputs would contain forbidden trading / deletion / allocation language.

## 19. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
feat: add unified factor evaluation workflow profile
```

Final response should include:

- commit hash
- summary verdict
- how PM-32 formalizes reusable workflow
- workflow contract summary
- evidence matrix coverage
- factor coverage
- profile class distribution
- research action distribution
- component weights
- source lineage status
- workflow integration status
- staleness integration status
- validation results
- limitations
- recommended next PM
