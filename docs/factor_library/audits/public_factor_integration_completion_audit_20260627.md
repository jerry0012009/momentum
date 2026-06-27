# Public Alpha101 / Alpha158 Integration Completion Audit - 2026-06-27

## Verdict

The controlled public Alpha101 / Alpha158 integration goal is complete for the
current scope. The library now has a manifest-led, registry-backed, batch-sized
workflow for public factors, with explicit skipped-candidate dispositions and
current QA evidence.

This is not a production, live-trading, tradeability, or alpha claim.

## Requirement Evidence

| Requirement | Evidence | Status |
| --- | --- | --- |
| `README.md` keeps `docs/factor_library/START_HERE.md` as the developer entry point | `README.md` links to `docs/factor_library/START_HERE.md`; `START_HERE.md` defines public-factor manifest status rules and workflow commands | PASS |
| Registry remains the only factor definition entry point | Implemented public rows in `docs/factor_library/public_factor_candidate_manifest.csv` all map to `scripts/factor_formula_registry.py`; skipped rows are explicitly absent from registry | PASS |
| First phase used small, formula-clear batches | `research/factor_runs/crypto_top50_factor_library/factor_intake/public_alpha158_batch01_20260626` through `public_alpha158_batch07_20260627` each have manifest/report/quality artifacts; batch sizes are 5-8 | PASS |
| Formula source, field mapping, operators, scope, lookback, direction, and skip reason are recorded | Manifest has required columns enforced by `tests/unit/test_public_factor_candidate_manifest.py`; current rows: 74 total, 62 implemented, 12 skipped | PASS |
| Existing public-factor coverage is complete | Guard found 62 public-family registry factors and no missing implemented manifest row | PASS |
| Skipped public candidates are auditable and do not create aliases | 6 Alpha158 duplicate skips and 6 Alpha101 industry-neutralization blockers use `_skipped`, have non-empty `skip_reason`, and are absent from registry | PASS |
| Existing intake/post-intake/state/page QA workflow remains usable | Current commands passed: manifest test 4/4, state refresh 128 registered / 128 computed / 0 missing factor values / 0 warnings, page QA 108 PASS / 0 FAIL, implemented-row integrity 62 factors / 1488 checks / 0 FAIL | PASS |
| No signal panel or trading/execution surface changed for the public-factor integration | Public-factor commit range does not modify `scripts/build_phase9b_signal_panel.py`, `scripts/evaluate_signals.py`, `src/momentum/signal_evaluation/`, or broker/exchange/execution/live-trading code | PASS |
| Generated HTML was not hand-edited | Factor-library HTML changes in the public-factor range are generated workflow output; the active source and workflow docs state generated HTML must not be edited by hand | PASS |
| No parallel workflow or `*_v2.py` entry point was introduced | Public-factor workflow uses existing registry, factor ops, `run_factor_intake.py`, `run_post_intake_workflow_completion.py`, integrity QA, page QA, and state refresh | PASS |
| Work was committed and pushed by functional units | Latest pushed commits include public batch additions, generated evidence refreshes, manifest backfills, skipped dispositions, Alpha101 blockers, and manifest status-rule hardening through `839f570` | PASS |

## Current Public Manifest Counts

| source_family | implemented rows | skipped rows | total rows |
| --- | ---: | ---: | ---: |
| alpha158 | 53 | 6 | 59 |
| alpha101 | 9 | 6 | 15 |
| total | 62 | 12 | 74 |

Implemented rows are included in factor-value and post-intake checks. Skipped
rows are blocked or duplicate candidates and are intentionally excluded from
factor-value and post-intake factor ID lists.

## Current QA Snapshot

Commands last verified on 2026-06-27:

```bash
.venv/bin/python -m pytest tests/unit/test_public_factor_candidate_manifest.py -q
python scripts/build_factor_library_state.py
python scripts/check_factor_evaluation_page_completeness.py
python scripts/check_post_intake_workflow_integrity.py --factor-ids <62 implemented public manifest factor IDs>
```

Results:

- Manifest guard: 4 passed.
- State: 128 registered, 128 computed, 0 missing factor values, 0 missing input, 0 warnings.
- Page completeness: 108 PASS, 0 FAIL.
- Implemented public-factor integrity: 62 factors, 1488 checks, 1431 PASS, 0 FAIL, 57 WARN.

The 57 warnings are optional PM-59A overlapping-sleeve summaries for eligible
diagnostic factors, not missing factor values, missing inputs, page failures, or
core post-intake failures.

## Residual Guidance

Future Alpha101 / Alpha158 expansion should continue to:

- add one manifest row before implementation or skip;
- keep batches at 4-8 candidates;
- filter skipped rows out of intake/post-intake commands;
- reuse existing operators and workflow scripts;
- add only reusable operators when a formula genuinely needs one;
- avoid signal panel, trading, execution, production, and alpha claims.
