# PM-32C Prompt — Evidence Truthfulness and Profile Calibration Repair

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task repairs PM-32B.

PM-32B fixed runner/contract stage order, but the evidence matrix still has a critical truthfulness problem:

- `has_factor_values` is False for sampled factors;
- `has_factor_level_evaluation` is False for sampled factors;
- `registry_or_data_status` is UNKNOWN;
- yet `evidence_status` remains COMPLETE and `workflow_ready_status` remains WORKFLOW_READY.

That is not acceptable for a reusable factor evaluation workflow. Future new factors must not be marked complete unless the required low-level evidence is actually present.

PM-32C must repair the evidence matrix truthfulness, workflow readiness logic, source status mapping, and profile classification usefulness.

## 0. PM objective

Make the unified factor workflow truthful and reliable.

The system should only mark a factor as fully evaluated if the required evidence really exists, including:

```text
factor_values
factor-level evaluation
unified profile
all downstream diagnostic artifacts
```

It should also reduce the excessive collapse of profile classifications into `BROAD_WATCHLIST` where possible, using rule-based distinctions without overfitting.

Do **not** update public HTML in PM-32C.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify signal panel construction.

Do **not** create or modify public HTML pages.

Do **not** enter signal evaluation or portfolio construction.

Do **not** fit profile weights to returns.

Do **not** hide missing evidence.

## 2. Required files to inspect

Inspect:

```text
scripts/build_unified_factor_profile.py
research/factor_runs/crypto_top50_factor_library/factor_library_state.json
research/factor_runs/crypto_top50_factor_library/factor_library_state.md
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_evidence_matrix.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_unified_profile_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/
data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/<factor_id>/factor_values.parquet
```

Also inspect `build_factor_library_state.py` if needed to understand factor_values paths and status fields.

## 3. Required evidence matrix repair

Modify:

```text
scripts/build_unified_factor_profile.py
```

Regenerate:

```text
factor_evaluation_evidence_matrix.csv
factor_evaluation_evidence_matrix.json
factor_unified_profile_summary.csv
factor_unified_profile_summary.json
factor_profile_component_scores.csv
factor_profile_payload.json
factor_profile_manifest.json
```

The evidence matrix must include and correctly compute:

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
registry_or_data_status
n_available_evidence_blocks
n_required_evidence_blocks
evidence_completeness_rate
evidence_status
missing_evidence_blocks
stale_evidence_blocks
```

Critical rule:

```text
If any required evidence block is False, evidence_status must not be COMPLETE.
```

Allowed evidence statuses:

```text
COMPLETE
COMPLETE_WITH_WARNINGS
INCOMPLETE
BLOCKED
```

## 4. Correct source of truth for has_factor_values

`has_factor_values` should be computed from either:

1. `factor_library_state.json`, if it contains computed/missing factor values; or
2. actual existence of per-factor `factor_values.parquet`; or
3. both, with actual file existence as stronger evidence.

Do not hardcode factor count or paths without checking state.

Audit must explain exactly how `has_factor_values` is computed.

## 5. Correct source of truth for has_factor_level_evaluation

`has_factor_level_evaluation` should be computed from factor-level evaluation artifacts, for example:

```text
factor_level_rankic_summary.csv
factor_level_period_quantile_return_summary.csv
factor_level_period_long_short_summary.csv
factor_monthly_ic_series.csv
factor_monthly_long_short_series.csv
```

If these files live under `factor_level_evaluation/`, read them there.

If they are also copied into `factor_diagnostics/`, use the canonical active location and document it.

Audit must explain exactly how `has_factor_level_evaluation` is computed.

## 6. registry_or_data_status repair

`registry_or_data_status` must not be UNKNOWN for registered factors unless the state file truly lacks status information.

Use available sources such as:

```text
factor_library_state.json
factor_library_state.md
factor_quality_scorecard.csv
factor catalog outputs
```

If a factor has `MISSING_INPUT_DATA`, preserve that separately from evidence completeness.

Important distinction:

```text
evidence_status = whether evaluation artifacts exist
registry_or_data_status = whether factor definition/input data status has caveats
workflow_ready_status = whether factor has complete usable workflow evidence without blocking caveats
```

## 7. workflow_ready_status logic

Profile summary must include:

```text
workflow_ready_status
workflow_missing_or_stale_blocks
```

Allowed workflow ready statuses:

```text
WORKFLOW_READY
WORKFLOW_READY_WITH_WARNINGS
WORKFLOW_INCOMPLETE
WORKFLOW_BLOCKED
```

Rules:

```text
WORKFLOW_READY: all required evidence True, no stale blocks, no blocking registry/data status.
WORKFLOW_READY_WITH_WARNINGS: all required evidence True, but non-blocking caveats exist, such as MISSING_INPUT_DATA status with downstream artifacts present, capacity warnings, or broad profile class.
WORKFLOW_INCOMPLETE: one or more required evidence blocks missing.
WORKFLOW_BLOCKED: factor_values or factor-level evaluation missing, or factor cannot be evaluated.
```

## 8. Profile classification calibration

The current profile class distribution collapses to:

```text
BROAD_WATCHLIST: 67
UNIQUE_BUT_WEAK: 4
```

This is too coarse for readability.

Improve rule-based classification without fitting to returns.

Use existing fields:

```text
profile_score
standalone_quality_class
paper_portfolio_class
cost_risk_class
regime_dependency_class
shape_quality_class
rolling_stability_class
decile_shape_class
capacity_liquidity_class
cluster_member_role
marginal_information_class
workflow_ready_status
```

Allowed profile classes:

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

Add class-specific logic such as:

```text
HIGH_QUALITY_DISTINCT: high score, distinct singleton or high marginal info, not unstable, not severe capacity issue.
HIGH_QUALITY_BUT_REDUNDANT: high score but cluster size > 1 and lower marginal information / redundant alternative.
STABLE_BUT_CAPACITY_CONSTRAINED: stable positive/strong paper but WATCH_LIQUIDITY or capacity risk.
PROMISING_BUT_REGIME_DEPENDENT: good paper/score but regime-dependent.
UNIQUE_BUT_WEAK: singleton/distinct but low paper/quality.
LOW_PRIORITY_DIAGNOSTIC: weak paper, unstable, no clear shape, low score.
INCOMPLETE_EVIDENCE: evidence incomplete.
INSUFFICIENT_DATA: blocking data status or missing key evidence.
```

Also improve `recommended_research_action` distribution where possible.

## 9. Required validation

Run:

```bash
python -m py_compile scripts/build_unified_factor_profile.py
python scripts/build_unified_factor_profile.py
python scripts/run_factor_library_refresh.py --stage profile --dry-run
python scripts/check_factor_library_staleness.py
```

Evidence validation:

```bash
python - <<'PY'
import pandas as pd
from pathlib import Path
base = Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics')
ev = pd.read_csv(base / 'factor_evaluation_evidence_matrix.csv')
profile = pd.read_csv(base / 'factor_unified_profile_summary.csv')
print('evidence factors', ev['factor_id'].nunique())
print('profile factors', profile['factor_id'].nunique())
for c in ['has_factor_values', 'has_factor_level_evaluation', 'has_unified_profile', 'registry_or_data_status']:
    print(c, ev[c].value_counts(dropna=False).to_string() if c in ev.columns else 'MISSING')
print('evidence statuses')
print(ev['evidence_status'].value_counts(dropna=False).to_string())
print('workflow readiness')
print(profile['workflow_ready_status'].value_counts(dropna=False).to_string())
print('profile classes')
print(profile['profile_class'].value_counts(dropna=False).to_string())
print('research actions')
print(profile['recommended_research_action'].value_counts(dropna=False).to_string())

bad = ev[(ev['evidence_status'] == 'COMPLETE') & ((ev['has_factor_values'] == False) | (ev['has_factor_level_evaluation'] == False) | (ev['has_unified_profile'] == False))]
print('bad COMPLETE rows with missing core evidence:', len(bad))
assert len(bad) == 0
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
bad = ['trade this factor', 'deploy this factor', 'remove this factor', 'drop this factor', 'only keep', 'portfolio allocation', 'signal weight', 'buy', 'sell', '交易该因子', '上线该因子', '删除', '剔除', '淘汰', '只保留', '配置权重', '买入', '卖出']
for p in paths:
    txt = p.read_text(encoding='utf-8', errors='ignore').lower()
    hits = [b for b in bad if b.lower() in txt]
    print(p.name, 'BAD_HITS=', hits)
PY
```

## 10. Required audit

Create:

```text
docs/factor_library/audits/pm32c_evidence_truthfulness_profile_calibration.md
```

Audit must include:

1. Summary verdict:
   - `EVIDENCE_TRUTHFULNESS_PROFILE_CALIBRATION_PASS`
   - `EVIDENCE_TRUTHFULNESS_PROFILE_CALIBRATION_PASS_WITH_LIMITATIONS`
   - `EVIDENCE_TRUTHFULNESS_PROFILE_CALIBRATION_BLOCKED`
2. Why PM-32C was required.
3. Files changed.
4. How `has_factor_values` is computed.
5. How `has_factor_level_evaluation` is computed.
6. How `registry_or_data_status` is computed.
7. Evidence matrix before/after summary.
8. Workflow readiness logic.
9. Factor coverage.
10. Evidence status distribution.
11. Workflow ready status distribution.
12. Profile class distribution before/after.
13. Research action distribution before/after.
14. Examples of factors whose profile class changed.
15. Validation results, especially zero bad COMPLETE rows.
16. Forbidden-language scan.
17. Limitations.
18. Non-change statement: no factors, formulas, factor_values, signal panel, public page.
19. Recommended next PM: PM-33 unified profile page integration and workflow-readiness presentation.

## 11. Allowed files to change

Allowed script:

```text
scripts/build_unified_factor_profile.py
```

Allowed outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_evidence_matrix.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_evidence_matrix.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_unified_profile_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_unified_profile_summary.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_profile_component_scores.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_profile_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_profile_manifest.json
```

Allowed audit:

```text
docs/factor_library/audits/pm32c_evidence_truthfulness_profile_calibration.md
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

## 12. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
fix: repair profile evidence truthfulness
```

Final response should include:

- commit hash
- summary verdict
- evidence truthfulness repair summary
- factor coverage
- core evidence distributions
- workflow readiness distribution
- profile class distribution before/after
- examples of changed interpretation
- validation results
- limitations
- recommended next PM
