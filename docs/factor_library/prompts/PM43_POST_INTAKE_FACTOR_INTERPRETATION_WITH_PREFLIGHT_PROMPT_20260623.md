# PM-43 Prompt — Post-Intake Factor Interpretation with Workflow Completeness Preflight

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-42 market regime / BTC diagnostics workflow reintegration.

PM-35 batch01 factors now have repaired page metrics, monthly IC/LS, paper portfolio payload, scorecard/profile consistency, LS aggregate canonical outputs, and regime/BTC diagnostics.

PM-43 is the first actual factor interpretation task, but it must begin with a strict workflow completeness preflight.

## 0. Objective

Interpret the five PM-35 batch01 factors as research diagnostics, after verifying that the current workflow outputs are complete and internally consistent.

Target factors:

```text
rev_2h
mom_vol_adjusted_20h
range_breakout_vol_confirm_20h
volume_pressure_20h
xs_rank_mom_accel
```

## 1. Strict prohibitions

Do not add new factors.
Do not modify factor formulas.
Do not modify expected_direction values.
Do not modify factor_values.
Do not modify signal panel construction.
Do not enter portfolio construction.
Do not make trading recommendations.
Do not change public page content except if preflight finds a trivial stale deployment issue and records it in audit.

## 2. Preflight checks before interpretation

Before writing any interpretation, verify that all five PM-35 factors have non-empty or explicitly unavailable outputs for:

```text
factor_values
factor_level_rankic_summary
factor_level_long_short_summary
factor_level_period_ic_summary
factor_level_period_long_short_summary
factor_quality_scorecard
factor_evaluation_evidence_matrix
factor_unified_profile_summary
factor_profile_payload
single_factor_paper_summary
single_factor_paper_page_payload
factor_regime_exposure_summary
factor_regime_summary
factor_quantile_shape_summary
factor_rolling_stability_summary
factor_decile_shape_summary
factor_capacity_liquidity_summary
factor_redundancy_summary or unified profile redundancy source
factor_redundancy_cluster_members or unified profile cluster role
factor_marginal_information_summary or unified profile marginal info
factor-evaluation.html
```

Run:

```bash
python scripts/check_factor_evaluation_page_completeness.py
```

If PM-42 added or updated a regime/BTC checker, run it too.

If any target factor fails completeness or has unresolved contradiction, stop and create an audit explaining why PM-43 is blocked. Do not interpret incomplete data.

## 3. Files to read

Read:

```text
docs/factor_library/START_HERE.md
docs/factor_library/POST_INTAKE_WORKFLOW_RUNBOOK.md
docs/factor_library/REGENERATION_CONTRACT.md
docs/factor_library/audits/pm35_controlled_factor_intake_batch01.md
docs/factor_library/audits/pm40b_factor_page_display_consistency_polish.md
docs/factor_library/audits/pm40c_scorecard_redundancy_consistency_repair.md
docs/factor_library/audits/pm41_ls_aggregate_canonicalization.md
docs/factor_library/audits/pm42_market_regime_btc_diagnostics_workflow_reintegration.md
scripts/factor_formula_registry.py
scripts/factor_ops.py
scripts/build_factor_values.py
scripts/evaluate_factors.py
scripts/build_factor_market_regime_diagnostics.py
scripts/_build_factor_eval_html.py
```

Read current diagnostic outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_evidence_matrix.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_unified_profile_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_profile_component_scores.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_fee_sensitivity.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_exposure_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quantile_shape_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_rolling_stability_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_decile_shape_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_capacity_liquidity_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_cluster_members.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_marginal_information_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_rankic_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_long_short_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_period_ic_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_period_long_short_summary.csv
```

## 4. Required outputs

Create:

```text
docs/factor_library/reviews/PM43_BATCH01_FACTOR_INTERPRETATION_REVIEW.md
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_batch01_interpretation_review.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_batch01_interpretation_review.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_batch01_direction_semantics_review.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_batch01_direction_semantics_review.json
docs/factor_library/audits/pm43_post_intake_factor_interpretation_with_preflight.md
```

## 5. Interpretation schema

`factor_batch01_interpretation_review.csv` must include:

```text
factor_id
formula_summary
expected_direction
best_horizon
rankic_1h
rankic_4h
rankic_24h
rankic_72h
rankic_t_stat_best
icir_best
monthly_ic_positive_rate_best
ls_mean_best
ls_sharpe_best
ls_max_drawdown_best
paper_viability_class
cost_sensitivity_class
gross_sharpe
break_even_fee_bps
regime_dependency_class
paper_return_btc_corr
long_short_btc_corr
ic_btc_return_corr
bull_minus_bear_paper_return
highvol_minus_lowvol_paper_return
quantile_shape_class
rolling_stability_class
decile_shape_class
capacity_liquidity_action
cluster_role
marginal_info_class
profile_class
profile_score
workflow_ready_status
evidence_status
interpretation_zh
interpretation_en
research_decision_class
next_action
```

Allowed `research_decision_class`:

```text
KEEP_FOR_RESEARCH_REVIEW
DIRECTION_SEMANTICS_REVIEW_REQUIRED
FORMULA_REPAIR_CANDIDATE
LOW_PRIORITY_DIAGNOSTIC
CAPACITY_CONSTRAINED_DIAGNOSTIC
REGIME_DEPENDENT_DIAGNOSTIC
INSUFFICIENT_HISTORY_MONITOR
PAGE_OR_DATA_QA_FOLLOWUP_REQUIRED
```

Allowed `next_action`:

```text
MONITOR_IN_LIBRARY
REVIEW_EXPECTED_DIRECTION
REVIEW_FORMULA_SPECIFICATION
DEPRIORITIZE_UNTIL_MORE_EVIDENCE
KEEP_AS_DIAGNOSTIC_PROBE
ADD_TO_REPAIR_BACKLOG
WAIT_FOR_MORE_HISTORY
```

## 6. Direction semantics schema

`factor_batch01_direction_semantics_review.csv` must include:

```text
factor_id
formula_semantics
expected_direction
expected_direction_basis
empirical_direction_1h
empirical_direction_best_horizon
direction_alignment_class
possible_explanation
recommended_direction_action
notes_zh
notes_en
```

Allowed `direction_alignment_class`:

```text
ALIGNED
CONFLICTS_WITH_1H_ONLY
CONFLICTS_ACROSS_HORIZONS
CONDITIONAL_OR_AMBIGUOUS
FORMULA_SIGN_MAY_BE_WRONG
INSUFFICIENT_EVIDENCE
```

Allowed `recommended_direction_action`:

```text
KEEP_EXPECTED_DIRECTION
REVIEW_EXPECTED_DIRECTION_NEXT_PM
REVIEW_FORMULA_SIGN_NEXT_PM
MARK_CONDITIONAL_NEXT_PM
NO_ACTION_YET_MORE_HISTORY_NEEDED
```

PM-43 must not change expected_direction.

## 7. Per-factor issues to address

### rev_2h

Evaluate whether short-horizon reversal is semantically aligned with positive direction and whether the apparent 1h strength survives paper/cost/regime/capacity review.

### mom_vol_adjusted_20h

Investigate why expected positive momentum has negative 1h adjusted IC. Determine whether this is a direction review candidate or a horizon-specific conflict.

### range_breakout_vol_confirm_20h

Investigate sparse coverage, redundancy, BTC beta sensitivity, and capacity limits. Decide whether it is low-priority diagnostic or formula repair candidate.

### volume_pressure_20h

Investigate whether volume pressure is empirically contrarian rather than continuation-oriented.

### xs_rank_mom_accel

Investigate whether cross-sectional momentum acceleration is reversal-prone or direction-misaligned.

## 8. Required audit

`pm43_post_intake_factor_interpretation_with_preflight.md` must include:

1. Preflight result.
2. Whether PM-35 factors have complete workflow outputs.
3. Summary verdict:
   - `POST_INTAKE_FACTOR_INTERPRETATION_PASS`
   - `POST_INTAKE_FACTOR_INTERPRETATION_PASS_WITH_LIMITATIONS`
   - `POST_INTAKE_FACTOR_INTERPRETATION_BLOCKED`
4. Five-factor interpretation table.
5. Direction alignment distribution.
6. Research decision distribution.
7. Formula/direction review candidates.
8. Limitations.
9. Forbidden language scan.
10. No formula / expected_direction / factor_values / signal changes confirmation.
11. Recommended next PM:
    - PM-44 repair backlog if direction/formula repairs are needed;
    - otherwise PM-44 controlled batch02 planning.

## 9. Validation

Run:

```bash
python - <<'PY'
import pandas as pd
from pathlib import Path
new = {'rev_2h','mom_vol_adjusted_20h','range_breakout_vol_confirm_20h','volume_pressure_20h','xs_rank_mom_accel'}
base = Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics')
review = pd.read_csv(base / 'factor_batch01_interpretation_review.csv')
dirrev = pd.read_csv(base / 'factor_batch01_direction_semantics_review.csv')
assert set(review['factor_id']) == new
assert set(dirrev['factor_id']) == new
print(review[['factor_id','research_decision_class','next_action']].to_string(index=False))
print(dirrev[['factor_id','direction_alignment_class','recommended_direction_action']].to_string(index=False))
PY
```

Forbidden language scan:

```bash
python - <<'PY'
from pathlib import Path
paths = [
    Path('docs/factor_library/reviews/PM43_BATCH01_FACTOR_INTERPRETATION_REVIEW.md'),
    Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_batch01_interpretation_review.csv'),
]
bad = ['trade this factor', 'deploy this factor', 'remove this factor', 'buy', 'sell', '交易该因子', '上线该因子', '删除', '买入', '卖出']
for p in paths:
    txt = p.read_text(encoding='utf-8', errors='ignore').lower()
    hits = [b for b in bad if b.lower() in txt]
    print(p.name, hits)
PY
```

## 10. Allowed files to change

Allowed outputs:

```text
docs/factor_library/reviews/PM43_BATCH01_FACTOR_INTERPRETATION_REVIEW.md
docs/factor_library/audits/pm43_post_intake_factor_interpretation_with_preflight.md
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_batch01_interpretation_review.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_batch01_interpretation_review.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_batch01_direction_semantics_review.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_batch01_direction_semantics_review.json
```

Do not modify:

```text
scripts/factor_formula_registry.py
scripts/factor_ops.py
scripts/build_factor_values.py
scripts/evaluate_factors.py
scripts/_build_factor_eval_html.py
scripts/build_phase9b_signal_panel.py
reports/site/factor-library/factor-evaluation.html
research/factor_runs/crypto_top50_factor_library/factor_values/*
src/momentum/strategies/*
```

## 11. Commit rules

Commit with:

```bash
analysis: interpret controlled intake batch 01 factors
```

Final response should include:

- commit hash
- preflight result
- summary verdict
- five-factor interpretation summary
- direction alignment distribution
- research decision distribution
- repair candidates
- limitations
- recommended next PM
