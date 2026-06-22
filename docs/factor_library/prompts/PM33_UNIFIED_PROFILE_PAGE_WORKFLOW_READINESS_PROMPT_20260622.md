# PM-33 Prompt — Unified Profile Page Integration and Workflow Readiness Presentation

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-32C:

- unified factor evaluation workflow contract
- evidence matrix truthfulness repair
- unified factor profile summary
- profile component scores
- workflow readiness fields

PM-33 should integrate these outputs into the existing factor-evaluation page so that the factor library becomes human-readable as a reusable workflow, not just a set of CSV/JSON artifacts.

Do **not** recompute PM-32C outputs in PM-33.

## 0. PM objective

Update the existing factor-evaluation page to show:

1. a top-level workflow-readiness overview;
2. per-factor unified profile summary;
3. per-factor evidence completeness and missing/stale blocks;
4. per-factor profile component scores;
5. source artifact lineage;
6. research-review actions;
7. clear disclaimers that this is factor research diagnostics, not signal construction or trading.

This is page integration only.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify signal panel construction.

Do **not** recompute profile outputs.

Do **not** create a new public page.

Do **not** enter signal evaluation or portfolio construction.

Do **not** use external CDN dependencies.

Do **not** remove existing sections.

Do **not** use trading or allocation language.

## 2. Existing sections that must be preserved

Preserve all existing factor-evaluation page sections:

```text
Factor metadata / formula / bilingual cards
Factor Quality Scorecard
Redundancy & novelty
Single-Factor Paper Portfolio
Corrected paper NAV
Paper drawdown
Long / short leg decomposition
Turnover
Fee sensitivity
BTC / Market Regime Diagnostics
Quantile Shape & Rolling Stability
Direction-aware Decile Shape Diagnostics
Capacity / Liquidity Proxy Diagnostics
```

Do not regress previous PM outputs.

## 3. Required inputs

Use PM-32C outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_workflow_contract.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_evidence_matrix.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_evidence_matrix.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_unified_profile_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_unified_profile_summary.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_profile_component_scores.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_profile_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_profile_manifest.json
```

Use compact payloads. Do not duplicate large datasets in page JS.

## 4. Required files to update

Update:

```text
scripts/_build_factor_eval_html.py
reports/site/factor-library/factor-evaluation.html
```

Optional if the current page uses an asset payload pattern:

```text
reports/site/factor-library/assets/factor_diagnostics_payload.json
```

## 5. Required top-level page section

Add a new top-level section:

```text
Unified Factor Evaluation Workflow
统一因子评价工作流
```

This section should show:

```text
workflow_version
number_of_stages
evidence_status_distribution
workflow_ready_status_distribution
profile_class_distribution
recommended_research_action_distribution
contract alignment summary
not-production disclaimer
```

It should make the purpose clear:

```text
Every future factor should be evaluated through the same workflow before it is considered fully reviewed.
```

Chinese equivalent:

```text
未来每一个新增因子都应经过同一套评价流程，完成证据检查、画像汇总与页面展示后，才视为完成研究性评价。
```

## 6. Required factor detail section

Add a section in each factor detail panel:

```text
Unified Factor Profile
统一因子画像
```

Display:

```text
profile_score
profile_class
profile_confidence
workflow_ready_status
evidence_status
evidence_completeness_rate
registry_or_data_status
recommended_research_action
primary_strength_zh / en
primary_risk_zh / en
profile_summary_zh / en
workflow_missing_or_stale_blocks
```

## 7. Required component score display

Display profile component scores:

```text
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

A compact bar chart or table is acceptable. No external libraries.

## 8. Required evidence matrix display

For the selected factor, show evidence block status:

```text
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
```

Use simple pass/warn/missing badges.

If any evidence block is missing or stale, show it clearly.

## 9. Required source lineage display

For each factor, show source artifacts used by the profile.

At minimum show:

```text
source_artifact_count
source_artifacts
```

If `component_source_map` exists in payload, show it in a collapsible/details block.

## 10. Filters / table columns

If low risk, add filter or table columns for:

```text
profile_class
workflow_ready_status
evidence_status
recommended_research_action
profile_confidence
```

Do not overcomplicate UI. Detail section is more important than new filters.

## 11. Required caveats

The page must explicitly state:

```text
Unified profiles are research diagnostics. They summarize evidence; they do not select signals, construct portfolios, or recommend trading.
```

Chinese:

```text
统一因子画像是研究性诊断汇总，用于整理证据；它不选择信号、不构建组合，也不构成交易建议。
```

## 12. Size and performance constraints

Keep final HTML preferably under 4.5MB.

Do not embed redundant copies of the same profile payload.

If page size grows too much, compact the payload rather than dropping the section.

## 13. Validation

Run:

```bash
python -m py_compile scripts/_build_factor_eval_html.py
python scripts/_build_factor_eval_html.py
```

Then validate HTML:

```bash
python - <<'PY'
from pathlib import Path
html = Path('reports/site/factor-library/factor-evaluation.html').read_text(encoding='utf-8')
checks = [
    'Unified Factor Evaluation Workflow',
    '统一因子评价工作流',
    'Unified Factor Profile',
    '统一因子画像',
    'workflow_ready_status',
    'evidence_status',
    'profile_class',
    'recommended_research_action',
    'has_factor_values',
    'has_factor_level_evaluation',
    'has_unified_profile',
    'source_artifacts',
    'research diagnostics',
    '不选择信号',
    'Single-Factor Paper Portfolio',
    'Capacity / Liquidity Proxy Diagnostics',
    'Quantile Shape & Rolling Stability',
    'BTC / Market Regime Diagnostics',
    '不是交易策略',
]
for c in checks:
    print(c, c in html)
print('html size bytes', len(html.encode('utf-8')))
PY
```

Also run:

```bash
python scripts/check_factor_library_staleness.py
```

## 14. Required audit

Create:

```text
docs/factor_library/audits/pm33_unified_profile_page_workflow_readiness.md
```

Audit must include:

1. Summary verdict:
   - `UNIFIED_PROFILE_PAGE_INTEGRATION_PASS`
   - `UNIFIED_PROFILE_PAGE_INTEGRATION_PASS_WITH_LIMITATIONS`
   - `UNIFIED_PROFILE_PAGE_INTEGRATION_BLOCKED`
2. Files changed.
3. No new public page confirmation.
4. Payloads consumed.
5. Workflow overview section confirmation.
6. Factor detail profile section confirmation.
7. Evidence matrix display confirmation.
8. Component score display confirmation.
9. Source lineage display confirmation.
10. Caveat / no-signal / no-trading language confirmation.
11. Existing sections preserved.
12. HTML size before/after.
13. Validation results.
14. Limitations.
15. Non-change statement: no factors, formulas, factor_values, signal panel.
16. Recommended next PM: PM-34 factor expansion backlog and intake-readiness test.

## 15. Allowed files to change

Allowed script:

```text
scripts/_build_factor_eval_html.py
```

Allowed page output:

```text
reports/site/factor-library/factor-evaluation.html
reports/site/factor-library/assets/factor_diagnostics_payload.json
```

Allowed audit:

```text
docs/factor_library/audits/pm33_unified_profile_page_workflow_readiness.md
```

Do not modify:

```text
scripts/build_unified_factor_profile.py
scripts/run_factor_library_refresh.py
scripts/check_factor_library_staleness.py
scripts/factor_formula_registry.py
scripts/factor_ops.py
scripts/build_factor_values.py
scripts/build_phase9b_signal_panel.py
```

## 16. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
feat: add unified profile workflow readiness to factor page
```

Final response should include:

- commit hash
- summary verdict
- sections added
- payloads consumed
- workflow overview confirmation
- factor detail profile confirmation
- evidence matrix display confirmation
- existing sections preserved
- HTML size
- validation results
- limitations
- recommended next PM
