# Public Alpha158 Batch10 Intake Audit - 2026-06-28

## Scope

This batch adds 4 public Alpha158 normalized price lag factors:

- `q158_open_close_4h`
- `q158_high_close_4h`
- `q158_low_close_4h`
- `q158_close_close_4h`

Source reference: Microsoft Qlib Alpha158DL price feature block in
`qlib/contrib/data/loader.py`. The Qlib price block generates
`Ref($field, d) / $close` for lag windows, with available fields including
`OPEN`, `HIGH`, `LOW`, `CLOSE`, and `VWAP`. This batch uses only fields present
in the canonical crypto bars and does not require VWAP input.

Guardrails:

- Registry remains the only factor-definition entry point.
- No signal panel, trading, execution, broker, or live-production code changed.
- Generated HTML was rebuilt by workflow, not edited by hand.
- No new reusable operator was required.
- All factors are diagnostic research assets only.

## Formula Mapping

| factor_id | Qlib formula shape | required inputs | lookback | direction |
| --- | --- | --- | --- | --- |
| `q158_open_close_4h` | `Ref($open,4)/$close` | `open`, `close` | 5 | conditional |
| `q158_high_close_4h` | `Ref($high,4)/$close` | `high`, `close` | 5 | conditional |
| `q158_low_close_4h` | `Ref($low,4)/$close` | `low`, `close` | 5 | conditional |
| `q158_close_close_4h` | `Ref($close,4)/$close` | `close` | 5 | conditional |

All four factors are single-symbol canonical-bar OHLC factors. Initial
per-symbol nulls are expected from the lag operator.

## Validation

Pre-intake checks:

```bash
python -m py_compile scripts/factor_formula_registry.py scripts/build_factor_bilingual_cards.py
.venv/bin/python -m pytest tests/unit/test_public_factor_candidate_manifest.py -q
python scripts/build_factor_bilingual_cards.py
```

Results:

- Python compile passed.
- Manifest guard: 4 passed.
- Bilingual card generator validation: PASS, 142 cards.
- Registry total after registration: 142.
- Batch10 manifest rows: 4.
- Public manifest rows: 88 total, 76 implemented, 12 skipped.
- Implemented public rows by family: Alpha158 67, Alpha101 9.

Intake command:

```bash
.venv/bin/python scripts/run_factor_intake.py --factor-ids q158_open_close_4h q158_high_close_4h q158_low_close_4h q158_close_close_4h --run-id public_alpha158_batch10_20260628
```

Intake result:

- Runtime: 596s.
- Status: COMPLETE.
- Quality checks: COMPLETE.
- Factor values: 4/4 computed.
- Coverage: 99.968% for all four 4h-lag price ratios.
- Redundancy intake pairs: 558.
- Conclusion cards: 4 `REDUNDANT_WITH_EXISTING`.
- Interpretation: these rows complete the short-lag Alpha158 price block
  coverage and are high-redundancy diagnostic references, not signal additions.

Post-intake command:

```bash
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids q158_open_close_4h,q158_high_close_4h,q158_low_close_4h,q158_close_close_4h
```

Post-intake result:

- Runtime: 767.4s across 18 stages.
- Partial evaluation merged 4 factors.
- Paper diagnostics processed 4 factors, 0 errors.
- State: 142 registered, 142 computed, 0 missing factor values, 0 missing inputs.
- Diagnostics summary: 142 factors.
- Incremental redundancy: 558 target pairs; merged matrix has 10,011 pairs
  across 142 factors.
- Redundancy cluster diagnostics: 142/142 coverage, 65 clusters.
- Regime diagnostics: 142 factors.
- Shape/stability diagnostics verified all 4 incremental factors.
- Decile diagnostics merged to 142 factors.
- Capacity/liquidity diagnostics merged to 142 factors.
- Scorecard: 142 rows.
- RankIC robust significance: 568 expected/output rows.
- Unified profile: 142 factors, evidence status 136 `COMPLETE` and 6
  `COMPLETE_WITH_WARNINGS`.
- Factor evaluation page: 11,798,949 bytes.
- Page QA: 108 PASS / 0 FAIL.
- Post-intake integrity QA for the 4 new factors: 92 PASS / 0 FAIL / 4 WARN.
- Full implemented public-manifest integrity QA: 76 factors, 1,824 checks,
  1,753 PASS, 0 FAIL, 71 WARN.

The warnings are optional PM-59A overlapping-sleeve summaries for eligible
diagnostic factors, not missing factor values, missing source metadata, page
coverage failures, or core workflow failures.

## Resource Note

This batch stays at the lower bound of the small-batch rule. The factors reuse
the existing `delay` and division semantics, require no new data source, and
expand Alpha158 price-block coverage without adding a parallel workflow.
