# Public Alpha101 / Alpha158 Integration Completion Audit - 2026-06-28

## Verdict

The controlled public Alpha101 / Alpha158 integration goal is complete for the
current supported scope. The library now has a manifest-led, registry-backed,
batch-sized workflow for public factors, with explicit skipped-candidate
dispositions, an industry-neutralization data contract for the remaining
Alpha101 blockers, and current QA evidence through Alpha158 Batch17.

This is not a production, live-trading, tradeability, or alpha claim.

## Requirement Evidence

| Requirement | Evidence | Status |
| --- | --- | --- |
| `README.md` keeps `docs/factor_library/START_HERE.md` as the developer entry point | `README.md` links to `docs/factor_library/START_HERE.md`; `START_HERE.md` defines public-factor manifest status rules and workflow commands | PASS |
| Registry remains the only factor definition entry point | Implemented public rows in `docs/factor_library/public_factor_candidate_manifest.csv` all map to `scripts/factor_formula_registry.py`; skipped rows are explicitly absent from registry | PASS |
| First phase used small, formula-clear batches | `research/factor_runs/crypto_top50_factor_library/factor_intake/public_alpha158_batch01_20260626` through `public_alpha158_batch07_20260627` each have manifest/report/quality artifacts; later batches through `public_alpha158_batch17_20260628` stay within 4-8 factors | PASS |
| Formula source, field mapping, operators, scope, lookback, direction, and skip reason are recorded | Manifest has required columns enforced by `tests/unit/test_public_factor_candidate_manifest.py`; current rows: 116 total, 104 implemented/non-skipped, 12 skipped | PASS |
| Existing public-factor coverage is complete for the supported scope | Guard found all public-family registry factors in the manifest; non-skipped rows map to registry entries; skipped rows remain intentionally absent | PASS |
| Skipped public candidates are auditable and do not create aliases | 6 Alpha158 duplicate skips and 6 Alpha101 industry-neutralization blockers use `_skipped`, have non-empty `skip_reason`, are absent from registry, and are documented in the rollup | PASS |
| Remaining Alpha101 industry-neutralization blockers have a data contract | `docs/factor_library/INDUSTRY_NEUTRALIZATION_DATA_CONTRACT.md` records required point-in-time taxonomy fields, reusable operator behavior, workflow extension requirements, and disallowed shortcuts | PASS |
| Existing intake/post-intake/state/page QA workflow remains usable | Current commands passed: manifest test 4/4, state 170 registered / 170 computed / 0 missing factor values / 0 missing inputs, page QA 108 PASS / 0 FAIL, implemented-row integrity 104 factors / 2496 checks / 0 FAIL | PASS |
| No signal panel or trading/execution surface changed for the public-factor integration | Public-factor commit range does not modify `scripts/build_phase9b_signal_panel.py`, `scripts/evaluate_signals.py`, `src/momentum/signal_evaluation/`, or broker/exchange/execution/live-trading code | PASS |
| Generated HTML was not hand-edited | Factor-library HTML changes in the public-factor range are generated workflow output; the active source and workflow docs state generated HTML must not be edited by hand | PASS |
| No parallel workflow or `*_v2.py` entry point was introduced | Public-factor workflow uses existing registry, factor ops, `run_factor_intake.py`, `run_post_intake_workflow_completion.py`, integrity QA, page QA, and state refresh | PASS |
| Work was committed and pushed by functional units | Latest pushed commits include Alpha158 Batch17 (`4f98754`) and the Alpha101 industry-neutralization blocker contract (`4c8145b`) | PASS |

## Current Public Manifest Counts

| source_family | implemented rows | skipped rows | total rows |
| --- | ---: | ---: | ---: |
| alpha158 | 95 | 6 | 101 |
| alpha101 | 9 | 6 | 15 |
| total | 104 | 12 | 116 |

Implemented rows are included in factor-value and post-intake checks. Skipped
rows are blocked or duplicate candidates and are intentionally excluded from
factor-value and post-intake factor ID lists.

## Current QA Snapshot

Commands last verified on 2026-06-28:

```bash
.venv/bin/python -m pytest tests/unit/test_public_factor_candidate_manifest.py -q
.venv/bin/python scripts/check_factor_evaluation_page_completeness.py
.venv/bin/python scripts/check_post_intake_workflow_integrity.py --factor-ids <104 implemented public manifest factor IDs>
jq '{registered_factors, computed_factor_values, missing_factor_values, missing_input_factors}' research/factor_runs/crypto_top50_factor_library/factor_library_state.json
```

Results:

- Manifest guard: 4 passed.
- State: 170 registered, 170 computed, 0 missing factor values, 0 missing input.
- Page completeness: 108 PASS, 0 FAIL.
- Implemented public-factor integrity: 104 factors, 2496 checks, 2397 PASS, 0 FAIL, 99 WARN.
- Online factor evaluation page: 170 factors, `WORKFLOW_READY` 170, Batch17 IDs present.

The 99 warnings are optional PM-59A overlapping-sleeve summaries for eligible
diagnostic factors, not missing factor values, missing inputs, page failures, or
core post-intake failures.

## Residual Blockers

The remaining skipped public candidates are intentionally not registry entries:

- 6 Alpha158 rows are duplicate formula aliases already covered by existing
  factors.
- 6 Alpha101 rows require `IndNeutralize(..., IndClass.*)` and remain blocked
  until `docs/factor_library/INDUSTRY_NEUTRALIZATION_DATA_CONTRACT.md` is
  satisfied with reviewed point-in-time sector, industry, and subindustry
  membership plus a reusable panel neutralization operator.

Do not replace `IndNeutralize` with temporary crypto buckets, market-cap
buckets, exchange buckets, or time-series demeaning.

## Residual Guidance

Future Alpha101 / Alpha158 expansion should continue to:

- add one manifest row before implementation or skip;
- keep batches at 4-8 candidates;
- filter skipped rows out of intake/post-intake commands;
- reuse existing operators and workflow scripts;
- add only reusable operators when a formula genuinely needs one;
- satisfy the industry-neutralization data contract before unskipping the
  remaining Alpha101 formulas;
- avoid signal panel, trading, execution, production, and alpha claims.
