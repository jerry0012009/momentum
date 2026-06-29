# Public Alpha101 / Alpha158 Integration Completion Audit - 2026-06-29

## Verdict

The controlled public Alpha101 / Alpha158 integration goal is complete for the
current supported scope. The library now has a manifest-led, registry-backed,
batch-sized workflow for public factors, with explicit skipped-candidate
dispositions, skip guards across factor-ID CLIs, an industry-neutralization data
contract for the remaining Alpha101 blockers, and current QA evidence for 249
active factors.

This is not a production, live-trading, tradeability, or alpha claim.

## Requirement Evidence

| Requirement | Evidence | Status |
| --- | --- | --- |
| `README.md` keeps `docs/factor_library/START_HERE.md` as the developer entry point | `README.md` links to `docs/factor_library/START_HERE.md`; `START_HERE.md` defines public-factor manifest status rules and workflow commands | PASS |
| Registry remains the only factor definition entry point | Implemented public rows in `docs/factor_library/public_factor_candidate_manifest.csv` all map to `scripts/factor_formula_registry.py`; skipped rows are explicitly absent from registry | PASS |
| First phase used small, formula-clear batches | `research/factor_runs/crypto_top50_factor_library/factor_intake/public_alpha158_batch01_20260626` through `public_alpha158_batch07_20260627` each have manifest/report/quality artifacts; later Alpha101/Alpha158 batches were grouped by formula/data-source similarity and kept inside existing intake/post-intake workflows | PASS |
| Formula source, field mapping, operators, scope, lookback, direction, and skip reason are recorded | Manifest has required columns enforced by `tests/unit/test_public_factor_candidate_manifest.py`; current rows: 208 total, 183 implemented/non-skipped, 25 skipped | PASS |
| Existing public-factor coverage is complete for the supported scope | Guard found all public-family registry factors in the manifest; non-skipped rows map to registry entries; skipped rows remain intentionally absent | PASS |
| Skipped public candidates are auditable and do not create aliases | 6 Alpha158 duplicate skips, 18 Alpha101 industry-neutralization blockers, and 1 Alpha101 low-coverage blocker use `_skipped`, have non-empty `skip_reason`, are absent from registry, and are documented in the rollup | PASS |
| Remaining Alpha101 industry-neutralization blockers have a data contract | `docs/factor_library/INDUSTRY_NEUTRALIZATION_DATA_CONTRACT.md` records required point-in-time taxonomy fields, reusable operator behavior, workflow extension requirements, and disallowed shortcuts | PASS |
| Existing intake/post-intake/state/page QA workflow remains usable | Current commands passed: manifest/status/guard tests 20/20, state 249 registered / 249 computed / 0 missing factor values / 0 missing inputs, page QA 115 PASS / 0 FAIL, all-active integrity 249 factors / 5976 checks / 0 FAIL | PASS |
| No signal panel or trading/execution surface changed for the public-factor integration | Public-factor commit range does not modify `scripts/build_phase9b_signal_panel.py`, `scripts/evaluate_signals.py`, `src/momentum/signal_evaluation/`, or broker/exchange/execution/live-trading code | PASS |
| Generated HTML was not hand-edited | Factor-library HTML changes in the public-factor range are generated workflow output; the active source and workflow docs state generated HTML must not be edited by hand | PASS |
| No parallel workflow or `*_v2.py` entry point was introduced | Public-factor workflow uses existing registry, factor ops, `run_factor_intake.py`, `run_post_intake_workflow_completion.py`, integrity QA, page QA, and state refresh | PASS |
| Work was committed and pushed by functional units | Public-factor implementation, manifest guards, skipped-row CLI rejection, and QA/docs updates are kept as functional commit units | PASS |

## Current Public Manifest Counts

| source_family | implemented rows | skipped rows | total rows |
| --- | ---: | ---: | ---: |
| alpha158 | 95 | 6 | 101 |
| alpha101 | 88 | 19 | 107 |
| total | 183 | 25 | 208 |

Implemented rows are included in factor-value and post-intake checks. Skipped
rows are blocked or duplicate candidates and are intentionally excluded from
factor-value and post-intake factor ID lists.

## Current QA Snapshot

Commands last verified on 2026-06-29:

```bash
.venv/bin/python -m pytest tests/unit/test_public_factor_integration_status.py tests/unit/test_public_factor_candidate_manifest.py tests/unit/test_public_factor_manifest_guard.py tests/unit/test_post_intake_public_manifest_guard.py -q
.venv/bin/python scripts/check_public_factor_integration_status.py
.venv/bin/python scripts/check_factor_evaluation_page_completeness.py
.venv/bin/python scripts/check_post_intake_workflow_integrity.py --all-active --output-dir /tmp/public_factor_integrity_audit
jq '{registered_factors, computed_factor_values, missing_factor_values, missing_input_factors}' research/factor_runs/crypto_top50_factor_library/factor_library_state.json
```

Results:

- Manifest/status/guard tests: 20 passed.
- State: 249 registered, 249 computed, 0 missing factor values, 0 missing input.
- Public manifest: 208 rows, 183 implemented/non-skipped, 25 skipped.
- Alpha158: 95 implemented, 6 skipped duplicates, 101 total; supported Alpha158 scope complete.
- Alpha101: 88 implemented, 19 skipped, 107 total.
- Page completeness: 115 PASS, 0 FAIL; page payload count 249; public source-family count `alpha101=88`, `alpha158=95`.
- All-active post-intake integrity: 249 factors, 5976 checks, 5777 PASS, 0 FAIL, 199 WARN.
- Active-universe consistency: 14/14 tables PASS at 249/249.
- PM-58A, PM-58B, and PM-58C all-active checks: PASS.
- Online factor evaluation HTML payload currently reports `summary.factor_count=249`.

The 199 warnings are optional PM-59A overlapping-sleeve summaries for eligible
diagnostic factors, not missing factor values, missing inputs, page failures, or
core post-intake failures.

## Residual Blockers

The remaining skipped public candidates are intentionally not registry entries:

- 6 Alpha158 rows are duplicate formula aliases already covered by existing
  factors.
- 18 Alpha101 rows require `IndNeutralize(..., IndClass.*)` and remain blocked
  until `docs/factor_library/INDUSTRY_NEUTRALIZATION_DATA_CONTRACT.md` is
  satisfied with reviewed point-in-time sector, industry, and subindustry
  membership plus a reusable panel neutralization operator.
- 1 Alpha101 row, `wq101_alpha96_low_coverage_skipped`, remains skipped because
  current crypto coverage is too low for a defensible implementation.

Do not replace `IndNeutralize` with temporary crypto buckets, market-cap
buckets, exchange buckets, or time-series demeaning.

## Residual Guidance

Future Alpha101 / Alpha158 expansion should continue to:

- add one manifest row before implementation or skip;
- group formulas by shared inputs/operators and keep batches resource-aware;
- filter skipped rows out of intake/post-intake commands;
- reuse existing operators and workflow scripts;
- add only reusable operators when a formula genuinely needs one;
- satisfy the industry-neutralization data contract before unskipping the
  remaining Alpha101 formulas;
- avoid signal panel, trading, execution, production, and alpha claims.
