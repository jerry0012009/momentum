# PM-32 Prompt — Unified Factor Profile / Scorecard v2

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows:

- PM-21B/22B: repaired single-factor paper portfolio and page integration
- PM-23B/24B: regime diagnostics and page integration
- PM-25: reusable staleness monitor and workflow reconciliation
- PM-26/27B/28: quantile shape, rolling stability, direction-aware deciles, and page integration
- PM-29B/30: selected-basket capacity/liquidity proxy and page integration
- PM-31/31B: redundancy clusters and marginal information, with diagnostic-only language

We are still in the **factor evaluation** phase. Do **not** enter signal construction or signal evaluation.

## 0. PM objective

Create a unified factor profile layer that consolidates all existing factor evaluation evidence into one canonical per-factor schema.

This should answer:

1. What is this factor good at?
2. What are its main risks?
3. Is its standalone quality strong?
4. Is it stable through time?
5. Is it regime-dependent?
6. Is it cost/capacity fragile?
7. Is it redundant with existing factors?
8. Does it provide marginal information?
9. Should it be classified as a core diagnostic candidate, watchlist factor, redundant alternative, or low-priority probe?

This is **not** a trading signal selection step. It is a factor evaluation summary layer.

Do **not** update public HTML in PM-32. Page integration can be PM-33.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify signal panel construction.

Do **not** create or modify public HTML pages.

Do **not** enter signal evaluation.

Do **not** recommend deleting factors.

Do **not** recommend portfolio weights.

Do **not** use language like trade, deploy, allocate, buy, sell, or final signal.

Use diagnostic language only.

## 2. Required inputs

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

If some optional fields are missing, degrade gracefully and report limitations.

## 3. Required script

Create:

```text
scripts/build_unified_factor_profile.py
```

Recommended CLI:

```bash
python scripts/build_unified_factor_profile.py
```

Optional arguments:

```bash
--output-dir research/factor_runs/crypto_top50_factor_library/factor_diagnostics
```

## 4. Required outputs

Write to:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/
```

Required outputs:

```text
factor_unified_profile_summary.csv
factor_unified_profile_summary.json
factor_profile_component_scores.csv
factor_profile_payload.json
factor_profile_manifest.json
```

Payload should be compact and suitable for future page integration.

## 5. Unified profile schema

`factor_unified_profile_summary.csv` should include:

```text
factor_id
family
status
expected_direction
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
INSUFFICIENT_DATA_REVIEW
```

Do not use `trade`, `deploy`, `remove`, `delete`, `drop`, or `allocate` language.

## 6. Component scores

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
profile_score
```

Suggested scoring range: 0–100.

Use transparent rule-based mapping from existing classes and numeric metrics. Do not fit or optimize weights from returns.

Suggested default weights:

```text
standalone_quality_component: 20%
paper_component: 15%
cost_component: 10%
regime_component: 10%
shape_component: 10%
stability_component: 15%
capacity_component: 10%
marginal_information_component: 10%
```

If fields are missing, renormalize weights across available components and report this in the manifest/audit.

## 7. Diagnostic language rules

Use careful language.

Allowed:

```text
higher priority for research review
useful cluster reference
requires capacity review
requires regime-dependence review
lower marginal information
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
```

## 8. Workflow integration

If low risk, add a new stage to:

```text
scripts/run_factor_library_refresh.py
```

Suggested stage:

```text
profile
```

Command:

```bash
python scripts/build_unified_factor_profile.py
```

The stage should run after:

```text
scorecard
redundancy
cluster
paper-diagnostics
paper-page-payload
regime
shape / decile / capacity diagnostics if present
```

If current runner does not yet contain all upstream diagnostics stages, add `profile` conservatively and document prerequisites. Do not perform large workflow restructuring.

Update `docs/factor_library/REGENERATION_CONTRACT.md` if low risk, so it mentions:

```text
cluster / marginal information → unified factor profile → page payloads / review outputs
```

## 9. Dynamic coverage requirements

Use expected factor count from `factor_library_state.json` or registry. Do not hardcode 71.

Audit must report:

```text
expected_factor_count
profile_factor_count
component_score_factor_count
payload_factor_count
missing_factor_ids
profile_class_distribution
recommended_research_action_distribution
component_missingness_summary
```

Do not silently drop factors.

## 10. Required audit

Create:

```text
docs/factor_library/audits/pm32_unified_factor_profile_scorecard_v2.md
```

Audit must include:

1. Summary verdict:
   - `UNIFIED_FACTOR_PROFILE_PASS`
   - `UNIFIED_FACTOR_PROFILE_PASS_WITH_LIMITATIONS`
   - `UNIFIED_FACTOR_PROFILE_BLOCKED`
2. Why PM-32 is needed before factor expansion and signal construction.
3. Files changed.
4. Input files used.
5. Scoring weights and class mapping summary.
6. Factor coverage.
7. Profile class distribution.
8. Recommended research action distribution.
9. Examples of high-quality distinct factors.
10. Examples of high-quality but redundant factors.
11. Examples of stable but capacity-constrained factors.
12. Examples of unique but weak factors.
13. Payload size.
14. Validation results.
15. Forbidden-language scan results.
16. Workflow integration status.
17. Contract update status.
18. Limitations.
19. Non-change statement: no factors, formulas, factor_values, signal panel, public page.
20. Recommended next PM: PM-33 unified profile page integration.

## 11. Validation

Run:

```bash
python -m py_compile scripts/build_unified_factor_profile.py
python scripts/build_unified_factor_profile.py
```

If workflow stage is added, run:

```bash
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
payload = json.loads((base / 'factor_profile_payload.json').read_text(encoding='utf-8'))
print('profile factors', profile['factor_id'].nunique())
print('component factors', components['factor_id'].nunique())
print('payload factors', len(payload.get('factors', [])))
print('profile classes')
print(profile['profile_class'].value_counts(dropna=False).to_string())
print('research actions')
print(profile['recommended_research_action'].value_counts(dropna=False).to_string())
PY
```

Forbidden language check:

```bash
python - <<'PY'
from pathlib import Path
paths = [
    Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_unified_profile_summary.csv'),
    Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_profile_payload.json'),
]
bad = ['trade this factor', 'deploy this factor', 'remove this factor', 'drop this factor', 'only keep', 'portfolio allocation', 'signal weight', '交易该因子', '上线该因子', '删除', '剔除', '淘汰', '只保留', '配置权重']
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

If PM-25 monitor does not yet know about profile outputs, report as future monitor extension.

## 12. Allowed files to change

Allowed script:

```text
scripts/build_unified_factor_profile.py
```

Allowed outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_unified_profile_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_unified_profile_summary.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_profile_component_scores.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_profile_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_profile_manifest.json
```

Allowed audit:

```text
docs/factor_library/audits/pm32_unified_factor_profile_scorecard_v2.md
```

Optional workflow/contract files:

```text
scripts/run_factor_library_refresh.py
docs/factor_library/REGENERATION_CONTRACT.md
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

## 13. Stop conditions

Stop and report if:

- too many required inputs are missing;
- factor coverage cannot be reconciled;
- scoring would require fitting to returns;
- implementation would require modifying factor formulas, factor_values, or signal panel;
- outputs would contain forbidden trading / deletion / allocation language.

## 14. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
feat: add unified factor profile scorecard
```

Final response should include:

- commit hash
- summary verdict
- factor coverage
- profile class distribution
- recommended research action distribution
- scoring weights
- examples of major profile classes
- workflow integration status
- validation results
- limitations
- recommended next PM
