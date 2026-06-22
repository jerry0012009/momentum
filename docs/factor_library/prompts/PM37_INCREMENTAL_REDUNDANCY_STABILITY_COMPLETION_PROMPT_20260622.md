# PM-37 Prompt — Incremental Redundancy / Cluster / Rolling-Stability Completion

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-36:

- PM-35 added 5 new controlled-intake factors;
- PM-36 made decile-shape and capacity-liquidity incremental and completed those blocks;
- PM-35 factors improved from 2/12 evidence blocks to 8/12;
- remaining missing blocks are:
  - redundancy_summary
  - redundancy_cluster_members
  - marginal_information
  - rolling_stability
- server previously OOMed during full refresh on a 15GB RAM / no-swap machine.

PM-37 must complete the remaining evidence without blindly running the full expensive workflow.

## 0. PM objective

Complete the remaining evidence blocks for the five PM-35 factors using resource-aware incremental diagnostics.

The target end state:

```text
rev_2h
mom_vol_adjusted_20h
range_breakout_vol_confirm_20h
volume_pressure_20h
xs_rank_mom_accel
```

should no longer be `INCOMPLETE_EVIDENCE` due to missing redundancy / cluster / marginal information / rolling stability artifacts.

This remains factor evaluation, not signal selection or portfolio construction.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify signal panel construction.

Do **not** modify live / strategy / broker / execution code.

Do **not** run full site rebuild that touches unrelated `reports/site/factors/*` or `reports/site/paper/*`.

Do **not** make trading or alpha claims.

Do **not** flip expected_direction post-hoc based only on PM-35 IC.

## 2. Required files to inspect first

Read:

```text
docs/factor_library/START_HERE.md
docs/factor_library/REGENERATION_CONTRACT.md
docs/factor_library/audits/pm35_controlled_factor_intake_batch01.md
docs/factor_library/audits/pm36_resource_audit_incremental_diagnostics.md
scripts/run_factor_library_refresh.py
scripts/check_factor_redundancy.py
scripts/build_factor_redundancy_cluster_diagnostics.py
scripts/build_factor_shape_stability_diagnostics.py
scripts/build_unified_factor_profile.py
scripts/check_factor_library_staleness.py
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_evidence_matrix.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_pairwise_redundancy.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_rolling_stability_summary.csv
```

If the redundancy script name differs, inspect `run_factor_library_refresh.py` to find the canonical command.

## 3. Required resource-aware redundancy repair

The current missing blocks suggest that redundancy artifacts were not recomputed for PM-35 factors.

Do **not** recompute old-old factor pairs unnecessarily.

Preferred approach:

1. Add or use existing support for `--factor-ids` / `--only-missing` in the redundancy computation script.
2. For target factors, compute:
   - new factor vs all existing factors;
   - new factor vs new factor;
3. Preserve existing old-old pairwise redundancy rows.
4. Drop and replace any rows involving target factors.
5. Regenerate:
   - `factor_pairwise_redundancy.csv`
   - `factor_redundancy_summary.csv`
6. Then rebuild cluster / marginal information from the merged pairwise file.

If true incremental pairwise is unsafe, run full redundancy only if it is demonstrably within memory/time budget. Audit must explain why.

## 4. Required cluster / marginal information repair

After pairwise redundancy is complete for 76 factors, run:

```bash
python scripts/build_factor_redundancy_cluster_diagnostics.py
```

If this script is light enough because it only reads CSVs, a full run is acceptable.

Verify that all 5 PM-35 factors appear in:

```text
factor_redundancy_summary.csv
factor_redundancy_cluster_members.csv
factor_marginal_information_summary.csv
factor_redundancy_cluster_payload.json
```

## 5. Required rolling stability repair

The PM-36 audit says rolling stability is still missing / None for new factors.

Inspect `scripts/build_factor_shape_stability_diagnostics.py`.

Add low-risk `--factor-ids` and/or `--only-missing` support if feasible.

If rolling stability is missing because the script did not include the new factors, recompute for only the five PM-35 factors and merge with existing outputs.

If rolling stability is missing because the new factors truly have insufficient monthly history, document this as `COMPLETE_WITH_WARNINGS`, not silent missing evidence.

Expected outputs to repair:

```text
factor_quantile_shape_summary.csv
factor_rolling_stability_summary.csv
factor_shape_stability_timeseries.csv
factor_shape_stability_payload.json
factor_shape_stability_manifest.json
```

## 6. Required profile/evidence/page refresh

After redundancy/cluster/marginal/rolling blocks are repaired, run:

```bash
python scripts/build_unified_factor_profile.py
python scripts/check_factor_library_staleness.py
python scripts/_build_factor_eval_html.py
```

Do **not** run `run_factor_library_refresh.py --stage all --expensive-ok` unless strictly necessary.

## 7. Required validation

Validate the five PM-35 factors:

```bash
python - <<'PY'
import pandas as pd
from pathlib import Path
new = ['rev_2h','mom_vol_adjusted_20h','range_breakout_vol_confirm_20h','volume_pressure_20h','xs_rank_mom_accel']
base = Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics')
ev = pd.read_csv(base / 'factor_evaluation_evidence_matrix.csv')
profile = pd.read_csv(base / 'factor_unified_profile_summary.csv')
cluster = pd.read_csv(base / 'factor_redundancy_cluster_members.csv')
marg = pd.read_csv(base / 'factor_marginal_information_summary.csv')
stab = pd.read_csv(base / 'factor_rolling_stability_summary.csv')
for name, df in [('evidence', ev), ('profile', profile), ('cluster', cluster), ('marginal', marg), ('stability', stab)]:
    missing = [f for f in new if f not in set(df['factor_id'])]
    print(name, 'missing', missing)
subset = ev[ev['factor_id'].isin(new)]
cols = ['factor_id','has_redundancy_summary','has_redundancy_cluster_members','has_marginal_information','has_rolling_stability','evidence_status','missing_evidence_blocks']
print(subset[cols].to_string(index=False))
profiles = profile[profile['factor_id'].isin(new)]
print(profiles[['factor_id','profile_class','workflow_ready_status','evidence_status','recommended_research_action']].to_string(index=False))
assert len(subset) == len(new)
assert subset['has_redundancy_summary'].all()
assert subset['has_redundancy_cluster_members'].all()
assert subset['has_marginal_information'].all()
# Rolling stability may be warning-complete if insufficient history, but must not be silently absent.
PY
```

Also check unrelated site report hygiene:

```bash
git diff --name-only HEAD~1..HEAD | grep '^reports/site/' || true
```

Expected: only `reports/site/factor-library/factor-evaluation.html`, unless audit explains otherwise.

## 8. Required audit

Create:

```text
docs/factor_library/audits/pm37_incremental_redundancy_stability_completion.md
```

Audit must include:

1. Summary verdict:
   - `INCREMENTAL_REDUNDANCY_STABILITY_COMPLETION_PASS`
   - `INCREMENTAL_REDUNDANCY_STABILITY_COMPLETION_PASS_WITH_LIMITATIONS`
   - `INCREMENTAL_REDUNDANCY_STABILITY_COMPLETION_BLOCKED`
2. Why PM-37 was required after PM-36.
3. Files changed.
4. Whether redundancy was run incrementally or full-library.
5. Resource safeguards used.
6. Pairwise redundancy coverage before/after.
7. Cluster membership coverage for PM-35 factors.
8. Marginal information coverage for PM-35 factors.
9. Rolling stability status for PM-35 factors.
10. Evidence matrix before/after for the 5 PM-35 factors.
11. Unified profile before/after for the 5 PM-35 factors.
12. Staleness result.
13. Page refresh result.
14. Unrelated report hygiene result.
15. Remaining limitations.
16. Non-change statement: no factors, formulas, factor_values, signal panel, live/strategy code.
17. Recommended next PM: PM-38 post-intake factor interpretation and direction-semantics review.

## 9. Allowed files to change

Allowed scripts:

```text
scripts/check_factor_redundancy.py
scripts/build_factor_redundancy_cluster_diagnostics.py
scripts/build_factor_shape_stability_diagnostics.py
```

Allowed outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_pairwise_redundancy.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_cluster_*.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_cluster_*.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_marginal_information_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_rolling_stability_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_shape_stability_*.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_shape_stability_*.json
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
docs/factor_library/audits/pm37_incremental_redundancy_stability_completion.md
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

## 10. Stop conditions

Stop and report if:

- redundancy cannot be completed without OOM;
- incremental pairwise merge would corrupt old-old pair rows;
- cluster outputs cannot include the five PM-35 factors;
- rolling stability cannot be meaningfully computed or warning-classified;
- completing evidence requires modifying formulas or factor_values;
- unrelated reports are modified unexpectedly.

## 11. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
fix: complete post-intake redundancy evidence
```

Final response should include:

- commit hash
- summary verdict
- redundancy completion method
- coverage for the five PM-35 factors
- evidence/profile before-after summary
- resource safeguards
- staleness result
- page result
- unrelated report hygiene result
- limitations
- recommended next PM
