# Public Alpha158 Batch07 Intake Audit - 2026-06-27

## Scope

This batch added 5 public Alpha158 normalized price factors:

- `q158_high_close_0h`
- `q158_low_close_0h`
- `q158_open_close_1h`
- `q158_high_close_1h`
- `q158_low_close_1h`

Source reference: Microsoft Qlib Alpha158DL price feature block in
`qlib/contrib/data/loader.py`.

Guardrails:

- Registry remains the only factor-definition entry point.
- No signal panel, trading, execution, broker, or live-production code changed.
- No generated HTML was edited by hand.
- No new reusable operator was required.
- All factors were evaluated as diagnostic research assets only.

## Formula Mapping

| factor_id | Qlib formula shape | required inputs | lookback | direction |
| --- | --- | --- | --- | --- |
| `q158_high_close_0h` | `$high/$close` | `high`, `close` | 1 | conditional |
| `q158_low_close_0h` | `$low/$close` | `low`, `close` | 1 | conditional |
| `q158_open_close_1h` | `Ref($open,1)/$close` | `open`, `close` | 2 | conditional |
| `q158_high_close_1h` | `Ref($high,1)/$close` | `high`, `close` | 2 | conditional |
| `q158_low_close_1h` | `Ref($low,1)/$close` | `low`, `close` | 2 | conditional |

All five factors are single-symbol OHLC factors. Window 1 formulas require one
lagged bar, so their first per-symbol observation is expected to be missing.

## Validation

Pre-intake checks:

- Python compile checks passed for registry and workflow scripts.
- Manifest, bilingual card CSV/JSON, and card QA metadata parsed successfully.
- Registry integrity checked 128 factors with 0 critical issues.
- Smoke computation on one symbol produced non-null values for all 5 factors.

Intake command:

```bash
.venv/bin/python scripts/run_factor_intake.py --factor-ids q158_high_close_0h q158_low_close_0h q158_open_close_1h q158_high_close_1h q158_low_close_1h --run-id public_alpha158_batch07_20260627
```

Intake result:

- Runtime: 617s.
- Quality checks: 8 PASS / 0 FAIL.
- Factor values: 5/5 computed.
- Coverage: 100.000% for 0h factors; 99.992% for 1h lag factors.
- Redundancy intake pairs: 625.
- Conclusion buckets: 4 `CONDITIONAL_DIRECTION_REVIEW`, 1 `REDUNDANT_WITH_EXISTING`.
- `q158_open_close_1h` is near-duplicate with `rev_2h`; do not promote without redundancy review.

Post-intake command:

```bash
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids q158_high_close_0h,q158_low_close_0h,q158_open_close_1h,q158_high_close_1h,q158_low_close_1h
```

Post-intake result:

- Runtime: 792.5s across 18 stages.
- State: 128 registered, 128 computed, 0 missing factor values, 0 missing inputs.
- Diagnostics summary: 128 factors.
- Incremental redundancy: 625 new pairs; merged matrix has 8,128 pairs across 128 factors.
- Redundancy cluster diagnostics: 128/128 coverage, 63 clusters.
- Regime diagnostics: 128 factors.
- Decile diagnostics: 128 factors.
- Capacity diagnostics: 128 factors.
- Scorecard: 128 rows.
- RankIC robust significance: 512 expected/output rows.
- Unified profile: 128 factors, evidence status 122 `COMPLETE` and 6 `COMPLETE_WITH_WARNINGS`.
- Factor evaluation page: 10,676,790 bytes.
- Page QA: 108 PASS / 0 FAIL.
- Post-intake integrity QA: 115 PASS / 0 FAIL / 5 WARN.

## Resource Note

Batch07 confirmed that even simple price-normalized public Alpha158 factors are
not free: intake took 617s and post-intake completion took 792.5s. Future batches
should stay at 4-5 factors and prioritize formulas with more expected information
increment than raw price-location variants.
