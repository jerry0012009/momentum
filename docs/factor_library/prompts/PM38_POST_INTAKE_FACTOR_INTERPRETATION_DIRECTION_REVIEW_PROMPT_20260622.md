# PM-38 Prompt — Post-Intake Factor Interpretation and Direction-Semantics Review

**SUPERSEDED / DEFERRED:** This prompt was not executed as PM-38. Use after PM-38B as PM-39 if factor interpretation remains the next task.

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-37:

- PM-35 registered 5 controlled-intake factors;
- PM-36 completed decile-shape and capacity-liquidity incrementally;
- PM-37 completed redundancy / cluster / marginal information / rolling stability evidence;
- all five PM-35 factors now have 12/12 evidence blocks and `WORKFLOW_READY`.

PM-38 is the first interpretation PM after the controlled intake workflow has fully completed.

This task should interpret the five new factors as **research diagnostics**, not trading signals.

## 0. PM objective

Produce a post-intake interpretation review for the five PM-35 factors.

The review should answer:

1. What does each new factor actually measure?
2. Is its expected_direction semantically consistent with the formula?
3. Does empirical evidence align or conflict with the expected_direction?
4. Is the factor redundant with existing clusters?
5. Does it provide marginal information?
6. Is it regime-dependent, cost-sensitive, or capacity constrained?
7. Is it worth keeping as a research candidate, repairing, deprioritizing, or sending back to backlog?

Do not modify formulas in PM-38. This is an interpretation and direction-semantics review.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify expected_direction values.

Do **not** modify factor_values.

Do **not** modify signal panel construction.

Do **not** enter signal evaluation or portfolio construction.

Do **not** make trading recommendations.

Do **not** remove or delete factors.

If a formula or direction appears wrong, create a repair recommendation for a later PM. Do not apply it here.

## 2. Target factors

Review exactly these five factors:

```text
rev_2h
mom_vol_adjusted_20h
range_breakout_vol_confirm_20h
volume_pressure_20h
xs_rank_mom_accel
```

## 3. Required files to inspect

Read:

```text
docs/factor_library/START_HERE.md
docs/factor_library/REGENERATION_CONTRACT.md
docs/factor_library/audits/pm35_controlled_factor_intake_batch01.md
docs/factor_library/audits/pm36_resource_audit_incremental_diagnostics.md
docs/factor_library/audits/pm37_incremental_redundancy_stability_completion.md
scripts/factor_formula_registry.py
scripts/factor_ops.py
scripts/build_factor_values.py
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_evidence_matrix.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_unified_profile_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_profile_component_scores.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_diagnostics_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_fee_sensitivity.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_exposure_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quantile_shape_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_rolling_stability_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_decile_shape_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_capacity_liquidity_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_cluster_members.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_marginal_information_summary.csv
```

## 4. Required output files

Create:

```text
docs/factor_library/reviews/PM38_BATCH01_FACTOR_INTERPRETATION_REVIEW.md
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_batch01_interpretation_review.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_batch01_interpretation_review.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_batch01_direction_semantics_review.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_batch01_direction_semantics_review.json
docs/factor_library/audits/pm38_post_intake_factor_interpretation_direction_review.md
```

Create the directory if needed:

```text
docs/factor_library/reviews/
```

## 5. Interpretation review schema

`factor_batch01_interpretation_review.csv` should include:

```text
factor_id
formula_summary
expected_direction
workflow_ready_status
evidence_status
profile_class
profile_score
profile_confidence
primary_empirical_strength
primary_empirical_risk
rankic_1h
rankic_4h
rankic_24h
rankic_72h
best_horizon
paper_return_10bps
paper_sharpe_gross
cost_sensitivity_class
regime_dependency_class
quantile_shape_class
rolling_stability_class
decile_shape_class
capacity_liquidity_class
cluster_id
cluster_size
cluster_member_role
marginal_information_class
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
```

Allowed `next_action`:

```text
MONITOR_IN_LIBRARY
REVIEW_EXPECTED_DIRECTION
REVIEW_FORMULA_SPECIFICATION
DEPRIORITIZE_UNTIL_MORE_EVIDENCE
KEEP_AS_DIAGNOSTIC_PROBE
ADD_TO_REPAIR_BACKLOG
```

These are research actions, not trading decisions.

## 6. Direction-semantics review schema

`factor_batch01_direction_semantics_review.csv` should include:

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

Important: PM-38 must not change `expected_direction`; it can only recommend review.

## 7. Specific issues to examine

Pay special attention to:

1. `rev_2h`: PM-35 showed positive 1h adjusted IC. Determine whether it behaves like a legitimate short-horizon reversal extension or is redundant with existing reversal cluster.
2. `mom_vol_adjusted_20h`: PM-35 showed negative 1h adjusted IC despite positive expected_direction. Determine whether this is horizon-specific, direction-semantics conflict, or sign issue.
3. `range_breakout_vol_confirm_20h`: low coverage ~16.8%, capacity-liquidity WATCH_BOTH / capacity-blocked-by-turnover. Determine whether it is formula repair candidate or low-priority diagnostic.
4. `volume_pressure_20h`: negative 1h adjusted IC despite positive expected_direction. Determine if directional volume pressure may be contrarian rather than continuation.
5. `xs_rank_mom_accel`: cross-sectional rank postprocess factor; negative 1h adjusted IC despite positive expected_direction. Determine if acceleration is reversal-prone or if formula should be reviewed.

## 8. Required human-readable review

`PM38_BATCH01_FACTOR_INTERPRETATION_REVIEW.md` should be readable by a human researcher.

It should include:

1. Overall summary.
2. Table of five factors.
3. Per-factor interpretation.
4. Direction-semantics review.
5. Redundancy / marginal information review.
6. Capacity / liquidity review.
7. Regime and stability review.
8. Recommended research next actions.
9. Explicit no-signal / no-trading disclaimer.

## 9. Validation

Run:

```bash
python - <<'PY'
import pandas as pd
from pathlib import Path
new = ['rev_2h','mom_vol_adjusted_20h','range_breakout_vol_confirm_20h','volume_pressure_20h','xs_rank_mom_accel']
base = Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics')
review = pd.read_csv(base / 'factor_batch01_interpretation_review.csv')
dirrev = pd.read_csv(base / 'factor_batch01_direction_semantics_review.csv')
print('review factors', review['factor_id'].tolist())
print('direction factors', dirrev['factor_id'].tolist())
assert set(review['factor_id']) == set(new)
assert set(dirrev['factor_id']) == set(new)
print(review[['factor_id','research_decision_class','next_action']].to_string(index=False))
print(dirrev[['factor_id','direction_alignment_class','recommended_direction_action']].to_string(index=False))
PY
```

Forbidden language check:

```bash
python - <<'PY'
from pathlib import Path
paths = [
    Path('docs/factor_library/reviews/PM38_BATCH01_FACTOR_INTERPRETATION_REVIEW.md'),
    Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_batch01_interpretation_review.csv'),
]
bad = ['trade this factor', 'deploy this factor', 'remove this factor', 'drop this factor', 'portfolio allocation', 'signal weight', 'buy', 'sell', '交易该因子', '上线该因子', '删除', '剔除', '淘汰', '配置权重', '买入', '卖出']
for p in paths:
    txt = p.read_text(encoding='utf-8', errors='ignore').lower()
    hits = [b for b in bad if b.lower() in txt]
    print(p.name, 'BAD_HITS=', hits)
PY
```

## 10. Required audit

Create:

```text
docs/factor_library/audits/pm38_post_intake_factor_interpretation_direction_review.md
```

Audit must include:

1. Summary verdict:
   - `POST_INTAKE_FACTOR_INTERPRETATION_PASS`
   - `POST_INTAKE_FACTOR_INTERPRETATION_PASS_WITH_LIMITATIONS`
   - `POST_INTAKE_FACTOR_INTERPRETATION_BLOCKED`
2. Why PM-38 follows PM-37.
3. Files changed.
4. Confirmation no formulas / factor_values / signal / page changed.
5. Coverage: exactly 5 PM-35 factors reviewed.
6. Research decision distribution.
7. Direction alignment distribution.
8. Factors requiring expected_direction review.
9. Factors requiring formula review.
10. Factors suitable for monitoring in library.
11. Key limitations.
12. Forbidden language scan.
13. Recommended next PM:
    - If formula/direction repairs are needed: PM-39 formula/direction repair backlog.
    - If no repairs are needed: PM-39 second intake batch planning.

## 11. Allowed files to change

Allowed docs/outputs only:

```text
docs/factor_library/reviews/PM38_BATCH01_FACTOR_INTERPRETATION_REVIEW.md
docs/factor_library/audits/pm38_post_intake_factor_interpretation_direction_review.md
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
scripts/build_phase9b_signal_panel.py
reports/site/factor-library/factor-evaluation.html
reports/site/factors/*
reports/site/paper/*
```

## 12. Stop conditions

Stop and report if:

- any of the 5 PM-35 factors is missing from profile/evidence outputs;
- direction evidence cannot be extracted;
- interpretation would require changing formulas or expected_direction;
- output would contain trading or signal-construction language.

## 13. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
analysis: review controlled intake batch 01 factors
```

Final response should include:

- commit hash
- summary verdict
- five-factor interpretation summary
- research decision distribution
- direction alignment distribution
- direction/formula review candidates
- limitations
- recommended next PM
