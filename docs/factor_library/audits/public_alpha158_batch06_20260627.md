# Public Alpha158 Batch06 Intake Audit - 2026-06-27

## Scope

This batch added 5 public Alpha158 kbar / normalized price factors:

- `q158_kmid_open`
- `q158_kmid_range`
- `q158_kup_range`
- `q158_klow_range`
- `q158_open_close_0h`

Source reference: Microsoft Qlib Alpha158DL formulas in
`qlib/contrib/data/loader.py`.

Guardrails:

- Registry remains the only factor-definition entry point.
- No signal panel, trading, execution, broker, or live-production code changed.
- No generated HTML was edited by hand.
- No new reusable operator was required.
- All factors were evaluated as diagnostic research assets only.

## Formula Mapping

| factor_id | Qlib formula shape | required inputs | direction |
| --- | --- | --- | --- |
| `q158_kmid_open` | `($close-$open)/$open` | `open`, `close` | positive |
| `q158_kmid_range` | `($close-$open)/($high-$low+1e-12)` | `open`, `high`, `low`, `close` | positive |
| `q158_kup_range` | `($high-Greater($open,$close))/($high-$low+1e-12)` | `open`, `high`, `low`, `close` | negative |
| `q158_klow_range` | `(Less($open,$close)-$low)/($high-$low+1e-12)` | `open`, `high`, `low`, `close` | positive |
| `q158_open_close_0h` | `$open/$close` | `open`, `close` | conditional |

## Validation

Pre-intake checks:

- Python compile checks passed for the edited workflow and registry scripts.
- Manifest, bilingual card CSV/JSON, and card QA metadata parsed successfully.
- Registry integrity checked 123 factors with 0 critical issues.
- Smoke computation on one symbol produced non-null values for all 5 factors.

Intake command:

```bash
.venv/bin/python scripts/run_factor_intake.py --factor-ids q158_kmid_open q158_kmid_range q158_kup_range q158_klow_range q158_open_close_0h --run-id public_alpha158_batch06_20260627
```

Intake result:

- Runtime: 668s.
- Quality checks: 8 PASS / 0 FAIL.
- Factor values: 5/5 computed, 3,316,259 rows each, 100% coverage.
- Conclusion buckets: 3 `REDUNDANT_WITH_EXISTING`, 2 `REVIEW_REQUIRED`.
- Direction semantics require review for `q158_kmid_open` and `q158_kmid_range`.
- Nearest duplicate examples include `intraday_ret`, `candle_body`, `candle_wick_upper`, and `candle_wick_lower`.

Post-intake command:

```bash
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids q158_kmid_open,q158_kmid_range,q158_kup_range,q158_klow_range,q158_open_close_0h
```

The first post-intake attempt completed `evaluate`, `paper-diagnostics`,
`paper-page-payload`, and `diagnostics-metrics`, then failed at `redundancy`
because `factor_library_state.json` still listed 118 factors while the merged
evaluation outputs already contained the 5 new factors.

Repair:

- Added an explicit `state` stage to `scripts/run_post_intake_workflow_completion.py`.
- The state stage runs `scripts/build_factor_library_state.py` before
  state-dependent diagnostics such as diagnostics metrics and redundancy.
- This avoids stale-state failures after partial evaluation merges.

Resume command:

```bash
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids q158_kmid_open,q158_kmid_range,q158_kup_range,q158_klow_range,q158_open_close_0h --start-from state
```

Post-intake result after repair:

- State: 123 registered, 123 computed, 0 missing factor values, 0 missing inputs.
- Diagnostics summary: 123 factors.
- Incremental redundancy: 600 new pairs; merged matrix has 7,503 pairs across 123 factors.
- Redundancy cluster diagnostics: 123/123 coverage, 59 clusters.
- Regime diagnostics: 123 factors.
- Decile diagnostics: 123 factors.
- Capacity diagnostics: 123 factors.
- Scorecard: 123 rows.
- RankIC robust significance: 492 expected/output rows.
- Unified profile: 123 factors, evidence status 117 `COMPLETE` and 6 `COMPLETE_WITH_WARNINGS`.
- Factor evaluation page: 10,275,504 bytes.
- Page QA: 108 PASS / 0 FAIL.
- Post-intake integrity QA: 115 PASS / 0 FAIL / 5 WARN.

## Resource Note

Even with 5 lightweight single-symbol factors, intake took 668s and the resumed
post-intake redundancy stage took 288s. The current workflow remains usable on
the 15GB machine, but future batches should stay near 4-5 factors unless the
redundancy and page-refresh layers are further optimized.
