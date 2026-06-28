# Public Alpha158 Batch11 Intake Audit - 2026-06-28

## Scope

This batch adds 4 public Alpha158 rolling 5h price factors:

- `q158_ma_5h`
- `q158_std_5h`
- `q158_max_5h`
- `q158_min_5h`

Source reference: Microsoft Qlib Alpha158DL rolling price feature block in
`qlib/contrib/data/loader.py`. This batch maps Qlib's rolling MA, STD, MAX,
and MIN formulas to five one-hour crypto bars using only canonical OHLC fields.

Guardrails:

- Registry remains the only factor-definition entry point.
- No signal panel, trading, execution, broker, or live-production code changed.
- Generated HTML was rebuilt by workflow, not edited by hand.
- No new reusable operator was required.
- All factors are diagnostic research assets only.

## Formula Mapping

| factor_id | Qlib formula shape | required inputs | lookback | direction |
| --- | --- | --- | --- | --- |
| `q158_ma_5h` | `Mean($close,5)/$close` | `close` | 5 | conditional |
| `q158_std_5h` | `Std($close,5)/$close` | `close` | 5 | negative |
| `q158_max_5h` | `Max($high,5)/$close` | `high`, `close` | 5 | conditional |
| `q158_min_5h` | `Min($low,5)/$close` | `low`, `close` | 5 | conditional |

All four factors are single-symbol canonical-bar OHLC factors. Initial
per-symbol nulls are expected from the rolling window.

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
- Bilingual card generator validation: PASS, 146 cards.
- Registry total after registration: 146.
- Batch11 manifest rows: 4.
- Public manifest rows: 92 total, 80 implemented, 12 skipped.
- Implemented public rows by family: Alpha158 71, Alpha101 9.

Intake command:

```bash
.venv/bin/python scripts/run_factor_intake.py --factor-ids q158_ma_5h q158_std_5h q158_max_5h q158_min_5h --run-id public_alpha158_batch11_20260628
```

Intake result:

- Runtime: 608.6s.
- Status: COMPLETE.
- Quality checks: 8 PASS / 0 FAIL.
- Factor values: 4/4 computed.
- Missing factor values: 0.
- Coverage: 99.968% for all four 5h rolling price ratios.
- Redundancy intake pairs: 574.
- Conclusion cards: 2 `CONDITIONAL_DIRECTION_REVIEW`, 1
  `REDUNDANT_WITH_EXISTING`, and 1 `REVIEW_REQUIRED`.
- Interpretation: these rows expand short-window Alpha158 rolling price
  coverage. They are valid public-factor diagnostics, not signal additions.

Post-intake command:

```bash
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids q158_ma_5h,q158_std_5h,q158_max_5h,q158_min_5h
```

Post-intake result:

- Partial evaluation merged 4 factors.
- Paper diagnostics processed 4 factors.
- State: 146 registered, 146 computed, 0 missing factor values, 0 missing
  inputs.
- Diagnostics summary: 146 factors.
- Redundancy diagnostics: 10,585 pair rows across 146 factors.
- Redundancy cluster diagnostics: 67 clusters.
- Regime, shape/stability, decile, capacity/liquidity, scorecard, robust
  RankIC, robust LS, and unified profile artifacts regenerated.
- RankIC robust significance: 584 output rows.
- LS robust significance: 584 output rows.
- Factor evaluation page: 12,328,991 bytes.
- Page payload: 146 factors, generation time `2026-06-28 05:34 UTC`.
- Page QA: 108 PASS / 0 FAIL.
- Full implemented public-manifest integrity QA: 80 factors, 1,920 checks,
  1,845 PASS, 0 FAIL, 75 WARN.

The warnings are optional PM-59A overlapping-sleeve summaries for eligible
diagnostic factors, not missing factor values, missing source metadata, page
coverage failures, or core workflow failures.

## Resource Note

This batch stays at the lower bound of the small-batch rule. The factors reuse
existing rolling mean, rolling standard deviation, rolling max, rolling min,
and division semantics, require no new data source, and extend Alpha158 rolling
price coverage without adding a parallel workflow.
