# PM-41 Prompt — Post-Intake Canonical Pipeline Consolidation

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-40B and PM-40C.

PM-40B/40C fixed the public factor-evaluation page for PM-35 new factors, especially `rev_2h`. However, the fixes also revealed deeper workflow debt:

1. old diagnostics pipeline;
2. new factor-level evaluation pipeline;
3. paper/profile/page payload pipeline;
4. page-builder fallback and override logic.

The immediate page is now readable, but future factor intakes should not rely on ad hoc page-builder overrides to make new factors look correct.

PM-41 should convert the PM-40B/40C lessons into a canonical post-intake workflow contract and minimal pipeline hardening.

This is still **workflow infrastructure**, not factor interpretation.

## 0. PM objective

Make the post-intake factor evaluation workflow robust, repeatable, and source-of-truth consistent.

The goal is to ensure that future small factor batches automatically produce coherent canonical outputs before page generation.

This PM should answer:

1. What is the canonical source of each page section after PM-40C?
2. Which outputs must be regenerated or merged after a new factor intake?
3. Which page-builder fallbacks are acceptable as defense-in-depth, and which should be replaced by upstream canonical outputs?
4. Can scorecard, redundancy, paper payload, monthly IC/LS, and unified profile all agree for new factors without manual patching?
5. Can future factor intake batches avoid the same rev_2h failure mode?

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify expected_direction.

Do **not** modify factor_values.

Do **not** enter factor interpretation or direction semantics review.

Do **not** modify signal panel construction.

Do **not** run live/strategy/broker/execution code.

Do **not** perform trading or portfolio construction.

## 2. Required context to read

Read:

```text
docs/factor_library/START_HERE.md
docs/factor_library/REGENERATION_CONTRACT.md
docs/factor_library/POST_INTAKE_WORKFLOW_RUNBOOK.md
docs/factor_library/RESOURCE_AWARE_REFRESH_GUIDE.md
docs/factor_library/audits/pm40b_factor_page_display_consistency_polish.md
docs/factor_library/audits/pm40c_scorecard_redundancy_consistency_repair.md
scripts/run_factor_intake.py
scripts/run_factor_library_refresh.py
scripts/_build_factor_eval_html.py
scripts/check_factor_evaluation_page_completeness.py
scripts/build_factor_quality_scorecard.py
scripts/build_unified_factor_profile.py
scripts/build_single_factor_paper_page_payload.py
scripts/build_factor_pairwise_redundancy_matrix.py
scripts/build_factor_redundancy_cluster_diagnostics.py
```

Also inspect current outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_diagnostics_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_evidence_matrix.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_unified_profile_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_profile_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_page_payload.json
research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_rankic_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_long_short_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_period_ic_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_period_long_short_summary.csv
reports/site/factor-library/factor-evaluation.html
```

## 3. Required analysis

Produce a source-of-truth map for page sections.

For each page section, specify canonical upstream source and fallback source:

```text
Bilingual Card
Best Horizon Metrics
Monthly RankIC
Monthly Long-Short
Cumulative Long-Short
Quality Scorecard
Redundancy & Novelty
Single-Factor Paper Portfolio
BTC / Regime Diagnostics
Quantile Shape
Decile Shape
Rolling Stability
Capacity / Liquidity
Unified Factor Profile
Evidence Matrix
```

For each section, answer:

```text
canonical_source
fallback_source
known_missing_fields
whether_page_builder_fallback_is_allowed
whether_upstream_pipeline_should_generate_it
post_intake_regeneration_command
qa_check_id
```

## 4. Required documentation

Create:

```text
docs/factor_library/POST_INTAKE_CANONICAL_OUTPUT_CONTRACT.md
```

This document must define:

1. canonical source for every page section;
2. fallback source for every page section;
3. which files must cover all registered factors;
4. which files may be sparse with explicit unavailable reason;
5. what must be regenerated after controlled factor intake;
6. what must be checked before page interpretation;
7. how PM-40B/40C failure modes are prevented in future.

Also update:

```text
docs/factor_library/START_HERE.md
docs/factor_library/POST_INTAKE_WORKFLOW_RUNBOOK.md
docs/factor_library/REGENERATION_CONTRACT.md
```

Add a short lesson:

```text
New factor 12/12 evidence completeness does not automatically guarantee legacy page sections are source-consistent. After intake, canonical outputs must be merged/regenerated before page generation, and page QA must include per-factor detail consistency checks.
```

## 5. Required script or QA hardening

Create or update a workflow integrity checker:

```text
scripts/check_post_intake_workflow_integrity.py
```

The checker should verify for PM-35 factors and, if possible, all computed factors:

```text
factor_id exists in factor_level_rankic_summary
factor_id exists in factor_level_period_ic_summary
factor_id exists in factor_level_period_long_short_summary
factor_id exists in factor_quality_scorecard
factor_id exists in single_factor_paper_page_payload
factor_id exists in factor_unified_profile_summary
factor_id exists in factor_profile_payload
factor_id appears in factor-evaluation.html
WORKFLOW_READY factors have non-empty best horizon metrics
WORKFLOW_READY factors have no stale no_horizon_data warning
WORKFLOW_READY factors have no unresolved redundancy conflict between scorecard and unified profile
PM-35 new factors have monthly_ic_count > 0
PM-35 new factors have monthly_ls_count > 0
PM-35 new factors have paper payload if paper summary exists
```

Outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/post_intake_workflow_integrity_report.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/post_intake_workflow_integrity_report.json
```

Allowed statuses:

```text
PASS
PASS_WITH_WARNINGS
FAIL
NOT_APPLICABLE
```

## 6. Optional pipeline hardening

If low-risk and clearly justified, update the orchestrator so future small-batch intake cannot skip required canonicalization.

Candidate file:

```text
scripts/run_factor_library_refresh.py
```

Possible additions:

- document stage order after controlled intake;
- add a non-expensive `post-intake-integrity` stage;
- do not force full refresh;
- do not run expensive stages unless explicitly requested.

If touching orchestrator is risky, only document the required order and leave orchestrator unchanged.

## 7. Page-builder policy

Do not remove existing page-builder fallback immediately if it is useful as defense-in-depth.

But document that page-builder fallback is not the canonical source of truth. It should repair display only after canonical outputs are generated.

If `_build_factor_eval_html.py` contains page-only overrides for stale scorecard or redundancy fields, preserve them as defensive display logic, but add comments explaining:

```text
Defensive fallback only. Upstream canonical outputs should be fixed by post-intake workflow integrity checks.
```

## 8. Required audit

Create:

```text
docs/factor_library/audits/pm41_post_intake_canonical_pipeline_consolidation.md
```

Audit must include:

1. Summary verdict:
   - `POST_INTAKE_CANONICAL_PIPELINE_PASS`
   - `POST_INTAKE_CANONICAL_PIPELINE_PASS_WITH_LIMITATIONS`
   - `POST_INTAKE_CANONICAL_PIPELINE_BLOCKED`
2. Why PM-41 was required before factor interpretation.
3. Source-of-truth map summary.
4. Files changed.
5. Integrity checker result.
6. PM-35 five-factor integrity table.
7. Remaining page-builder fallbacks.
8. Whether run_factor_library_refresh.py was changed.
9. Confirmation no formulas / expected_direction / factor_values / signal changes.
10. Remaining limitations.
11. Recommended next PM: PM-42 post-intake factor interpretation and direction-semantics review.

## 9. Validation

Run:

```bash
python -m py_compile scripts/check_post_intake_workflow_integrity.py
python scripts/check_post_intake_workflow_integrity.py
python scripts/check_factor_evaluation_page_completeness.py
```

Then validate output:

```bash
python - <<'PY'
import pandas as pd
from pathlib import Path
p = Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics/post_intake_workflow_integrity_report.csv')
df = pd.read_csv(p)
print(df.head().to_string(index=False))
print(df['status'].value_counts(dropna=False).to_string())
new = {'rev_2h','mom_vol_adjusted_20h','range_breakout_vol_confirm_20h','volume_pressure_20h','xs_rank_mom_accel'}
assert new.issubset(set(df['factor_id']))
PY
```

## 10. Allowed files to change

Allowed docs:

```text
docs/factor_library/POST_INTAKE_CANONICAL_OUTPUT_CONTRACT.md
docs/factor_library/START_HERE.md
docs/factor_library/POST_INTAKE_WORKFLOW_RUNBOOK.md
docs/factor_library/REGENERATION_CONTRACT.md
docs/factor_library/audits/pm41_post_intake_canonical_pipeline_consolidation.md
```

Allowed scripts:

```text
scripts/check_post_intake_workflow_integrity.py
scripts/check_factor_evaluation_page_completeness.py
scripts/_build_factor_eval_html.py
scripts/run_factor_library_refresh.py
```

Allowed outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/post_intake_workflow_integrity_report.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/post_intake_workflow_integrity_report.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_page_completeness_report.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_page_completeness_report.json
```

Do not modify:

```text
scripts/factor_formula_registry.py
scripts/factor_ops.py
scripts/build_factor_values.py
scripts/build_phase9b_signal_panel.py
research/factor_runs/crypto_top50_factor_library/factor_values/*
reports/site/factors/*
reports/site/paper/*
src/momentum/strategies/*
```

## 11. Stop conditions

Stop and report if:

- integrity checker reveals unresolved source-of-truth conflicts for PM-35 factors;
- resolving conflicts requires recomputing factor values;
- resolving conflicts requires formula or expected_direction changes;
- orchestration changes would trigger expensive full refresh by default;
- page-builder fallbacks cannot be documented safely.

## 12. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
docs: consolidate post-intake canonical workflow
```

Final response should include:

- commit hash
- summary verdict
- canonical output contract summary
- integrity checker result
- PM-35 five-factor integrity table
- remaining fallbacks
- confirmation no formula/factor_values/signal changes
- limitations
- recommended next PM
