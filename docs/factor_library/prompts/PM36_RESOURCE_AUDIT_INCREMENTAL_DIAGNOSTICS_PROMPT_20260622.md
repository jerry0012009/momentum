# PM-36 Prompt — Resource Audit and Incremental Missing Diagnostics Repair

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-35:

- BATCH_01 controlled factor intake registered 5 new factors;
- factor count increased from 71 to 76;
- factor values and factor-level evaluation were produced for the new factors;
- server crashed/restarted once during refresh, likely due to disk / memory pressure;
- PM-35 audit reports that decile-shape and capacity-liquidity stages timed out / hit OOM risk on a 15GB server;
- new factors are still `INCOMPLETE_EVIDENCE / WORKFLOW_INCOMPLETE` because decile-shape and capacity-liquidity are missing.

PM-36 must not blindly rerun the full workflow. First make the missing diagnostics incremental / resource-aware, then complete the missing diagnostics for the new factors.

## 0. PM objective

Repair the post-intake workflow so that new factors can be completed without recomputing every heavy diagnostic for the whole library.

This PM must answer:

1. Which stages are resource-heavy after factor intake?
2. Which stages recompute all factors unnecessarily?
3. Can decile-shape and capacity-liquidity be run only for new or missing factors?
4. Can the five PM-35 factors be brought from `INCOMPLETE_EVIDENCE` to complete or warning-complete status?
5. Can the profile/page/staleness artifacts be refreshed without touching unrelated site reports?

This remains factor evaluation. Do **not** enter signal construction or portfolio construction.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify `scripts/factor_formula_registry.py`.

Do **not** modify `scripts/factor_ops.py` unless a critical bug in PM-35 factor formulas is discovered and documented; default is no changes.

Do **not** modify existing factor formulas.

Do **not** modify signal panel construction.

Do **not** modify live/strategy/execution/broker/exchange code.

Do **not** run a full site rebuild that touches unrelated `reports/site/factors/*` or `reports/site/paper/*` unless unavoidable and documented.

Do **not** claim new factors are good/bad until their evidence is complete.

## 2. Required files to inspect first

Read:

```text
docs/factor_library/START_HERE.md
docs/factor_library/REGENERATION_CONTRACT.md
docs/factor_library/audits/pm35_controlled_factor_intake_batch01.md
scripts/run_factor_library_refresh.py
scripts/build_factor_decile_shape_diagnostics.py
scripts/build_factor_capacity_liquidity_diagnostics.py
scripts/build_factor_shape_stability_diagnostics.py
scripts/build_single_factor_paper_portfolio_diagnostics.py
scripts/build_unified_factor_profile.py
scripts/check_factor_library_staleness.py
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_evidence_matrix.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_unified_profile_summary.csv
```

## 3. New factor list

The PM-35 factors are:

```text
rev_2h
mom_vol_adjusted_20h
range_breakout_vol_confirm_20h
volume_pressure_20h
xs_rank_mom_accel
```

These should be the first targets for missing diagnostics repair.

## 4. Required resource audit

Create a resource audit that identifies heavy stages and unnecessary recomputation.

Create outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_workflow_resource_audit.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_workflow_resource_audit.json
```

At minimum include rows for:

```text
evaluate
redundancy
paper-diagnostics
shape-stability
decile-shape
capacity-liquidity
profile
staleness
page
```

Fields:

```text
stage_id
script
is_expensive
known_resource_risk
recomputes_all_factors
supports_factor_subset_before
supports_factor_subset_after
supports_append_or_replace
resource_notes_zh
resource_notes_en
recommended_use_after_intake
```

## 5. Required incremental support

Add low-risk factor subset support to the missing heavy diagnostics.

### 5.1 Decile-shape

Modify:

```text
scripts/build_factor_decile_shape_diagnostics.py
```

Add CLI args:

```bash
--factor-ids rev_2h,mom_vol_adjusted_20h,...
--only-missing
```

Required behavior:

- If `--factor-ids` is provided, compute only those factors.
- If `--only-missing` is provided, infer missing factors from the evidence matrix or existing decile outputs.
- Preserve existing outputs for other factors.
- Append/replace rows for target factors only.
- Deduplicate by factor_id / horizon / month / decile as appropriate.
- Preserve direction-aware ordering from PM-27B.
- Rebuild compact decile payload and summary after merge.

### 5.2 Capacity-liquidity

Modify:

```text
scripts/build_factor_capacity_liquidity_diagnostics.py
```

Add CLI args:

```bash
--factor-ids rev_2h,mom_vol_adjusted_20h,...
--only-missing
```

Required behavior:

- If `--factor-ids` is provided, compute only those factors.
- If `--only-missing` is provided, infer missing factors from the evidence matrix or existing capacity outputs.
- Preserve existing outputs for other factors.
- Append/replace rows for target factors only.
- Avoid loading all factor value parquet files when only a subset is requested.
- Keep selected-basket proxy caveats intact.

## 6. Optional helper script

If useful, create:

```text
scripts/run_post_intake_missing_diagnostics.py
```

This is allowed only as an orchestration helper, not as a parallel evaluator.

It should run:

```bash
python scripts/build_factor_decile_shape_diagnostics.py --only-missing
python scripts/build_factor_capacity_liquidity_diagnostics.py --only-missing
python scripts/build_unified_factor_profile.py
python scripts/check_factor_library_staleness.py
python scripts/_build_factor_eval_html.py
```

It must not run signal code.

If you create it, document it as a convenience wrapper for missing diagnostics after controlled factor intake.

## 7. Required completion run

After adding subset support, run the missing diagnostics for PM-35 factors:

```bash
python scripts/build_factor_decile_shape_diagnostics.py --factor-ids rev_2h,mom_vol_adjusted_20h,range_breakout_vol_confirm_20h,volume_pressure_20h,xs_rank_mom_accel
python scripts/build_factor_capacity_liquidity_diagnostics.py --factor-ids rev_2h,mom_vol_adjusted_20h,range_breakout_vol_confirm_20h,volume_pressure_20h,xs_rank_mom_accel
python scripts/build_unified_factor_profile.py
python scripts/check_factor_library_staleness.py
python scripts/_build_factor_eval_html.py
```

Do not run `--stage all --expensive-ok` unless necessary.

## 8. Required validation

Validate the five PM-35 factors:

```bash
python - <<'PY'
import pandas as pd
from pathlib import Path
new = ['rev_2h','mom_vol_adjusted_20h','range_breakout_vol_confirm_20h','volume_pressure_20h','xs_rank_mom_accel']
base = Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics')
ev = pd.read_csv(base / 'factor_evaluation_evidence_matrix.csv')
profile = pd.read_csv(base / 'factor_unified_profile_summary.csv')
for name, df in [('evidence', ev), ('profile', profile)]:
    missing = [f for f in new if f not in set(df['factor_id'])]
    print(name, 'missing', missing)
subset = ev[ev['factor_id'].isin(new)]
print(subset[['factor_id','has_decile_shape','has_capacity_liquidity','evidence_status','missing_evidence_blocks']].to_string(index=False))
profiles = profile[profile['factor_id'].isin(new)]
print(profiles[['factor_id','profile_class','workflow_ready_status','evidence_status','recommended_research_action']].to_string(index=False))
assert len(subset) == len(new)
assert subset['has_decile_shape'].all()
assert subset['has_capacity_liquidity'].all()
PY
```

Also validate no unrelated site files were touched by this PM except `factor-evaluation.html`:

```bash
git diff --name-only HEAD~1..HEAD | grep '^reports/site/' || true
```

Expected: ideally only `reports/site/factor-library/factor-evaluation.html`.

## 9. Required audit

Create:

```text
docs/factor_library/audits/pm36_resource_audit_incremental_diagnostics.md
```

Audit must include:

1. Summary verdict:
   - `RESOURCE_AUDIT_INCREMENTAL_DIAGNOSTICS_PASS`
   - `RESOURCE_AUDIT_INCREMENTAL_DIAGNOSTICS_PASS_WITH_LIMITATIONS`
   - `RESOURCE_AUDIT_INCREMENTAL_DIAGNOSTICS_BLOCKED`
2. Why PM-36 was required after PM-35 server crash/restart.
3. Files changed.
4. Stages identified as heavy.
5. Which stages were made incremental.
6. Whether decile-shape supports `--factor-ids` and `--only-missing`.
7. Whether capacity-liquidity supports `--factor-ids` and `--only-missing`.
8. PM-35 factor completion status.
9. Evidence matrix before/after for PM-35 factors.
10. Unified profile before/after for PM-35 factors.
11. Staleness result.
12. Page refresh result.
13. Unrelated report file hygiene check.
14. Any remaining resource limitations.
15. Non-change statement: no factors, formulas, factor_values, signal panel, live/strategy code.
16. Recommended next PM: PM-37 post-intake factor interpretation review.

## 10. Allowed files to change

Allowed scripts:

```text
scripts/build_factor_decile_shape_diagnostics.py
scripts/build_factor_capacity_liquidity_diagnostics.py
scripts/run_post_intake_missing_diagnostics.py     # optional
```

Allowed outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_workflow_resource_audit.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_workflow_resource_audit.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_decile_*.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_decile_*.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_capacity_liquidity_*.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_capacity_liquidity_*.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_evidence_matrix.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_evidence_matrix.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_unified_profile_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_unified_profile_summary.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_profile_*.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_profile_component_scores.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_library_staleness_report.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_library_staleness_report.json
reports/site/factor-library/factor-evaluation.html
```

Allowed audit:

```text
docs/factor_library/audits/pm36_resource_audit_incremental_diagnostics.md
```

Do not modify:

```text
scripts/factor_formula_registry.py
scripts/factor_ops.py
scripts/build_factor_values.py
scripts/build_phase9b_signal_panel.py
reports/site/factors/*
reports/site/paper/*
```

## 11. Stop conditions

Stop and report if:

- subset mode cannot be implemented without corrupting existing outputs;
- decile-shape or capacity-liquidity still OOMs for five factors;
- preserving existing outputs and replacing target-factor rows is unsafe;
- completing missing diagnostics requires modifying factor formulas or factor_values;
- unrelated report files are modified by the page refresh.

## 12. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
fix: add incremental missing diagnostics workflow
```

Final response should include:

- commit hash
- summary verdict
- resource audit summary
- scripts made incremental
- PM-35 factor completion status
- evidence/profile status before/after
- staleness result
- page refresh result
- unrelated report hygiene result
- limitations
- recommended next PM
