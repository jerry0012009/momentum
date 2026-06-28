# Public Alpha158 Batch13 Intake Audit - 2026-06-28

## Scope

This batch adds 4 public Alpha158 rolling 30h price factors:

- `q158_ma_30h`
- `q158_std_30h`
- `q158_max_30h`
- `q158_min_30h`

Source reference: Microsoft Qlib Alpha158DL rolling price feature block in
`qlib/contrib/data/loader.py`. This batch maps Qlib's rolling MA, STD, MAX,
and MIN formulas to thirty one-hour crypto bars using only canonical OHLC
fields.

Guardrails:

- Registry remains the only factor-definition entry point.
- No signal panel, trading, execution, broker, or live-production code changed.
- Generated HTML was rebuilt by workflow, not edited by hand.
- No new reusable operator was required.
- All factors are diagnostic research assets only.

## Formula Mapping

| factor_id | Qlib formula shape | required inputs | lookback | direction |
| --- | --- | --- | --- | --- |
| `q158_ma_30h` | `Mean($close,30)/$close` | `close` | 30 | conditional |
| `q158_std_30h` | `Std($close,30)/$close` | `close` | 30 | negative |
| `q158_max_30h` | `Max($high,30)/$close` | `high`, `close` | 30 | conditional |
| `q158_min_30h` | `Min($low,30)/$close` | `low`, `close` | 30 | conditional |

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
- Bilingual card generator validation: PASS, 154 cards.
- Registry total after registration: 154.
- Batch13 manifest rows: 4.
- Public manifest rows: 100 total, 88 implemented, 12 skipped.
- Implemented public rows by family: Alpha158 79, Alpha101 9.

Intake command:

```bash
.venv/bin/python scripts/run_factor_intake.py --factor-ids q158_ma_30h q158_std_30h q158_max_30h q158_min_30h --run-id public_alpha158_batch13_20260628
```

Intake result:

- Runtime: 643.3s.
- Status: COMPLETE.
- Quality checks: 8 PASS / 0 FAIL.
- Factor values: 4/4 computed.
- Missing factor values: 0.
- Coverage: 99.767% for all four 30h rolling price ratios.
- Redundancy intake pairs: 606.
- Conclusion cards: 3 `REDUNDANT_WITH_EXISTING` and 1 `REVIEW_REQUIRED`.
- Interpretation: these rows extend the Alpha158 rolling price block to a
  medium 30h window. They are valid public-factor diagnostics, not signal
  additions.

Post-intake command:

```bash
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids q158_ma_30h,q158_std_30h,q158_max_30h,q158_min_30h
```

Post-intake result:

- Runtime: 788.2s across 18 stages.
- Partial evaluation merged 4 factors.
- Paper diagnostics processed 4 factors.
- State: 154 registered, 154 computed, 0 missing factor values, 0 missing
  inputs.
- Diagnostics summary: 154 factors.
- Redundancy diagnostics: 11,781 pair rows across 154 factors.
- Redundancy cluster diagnostics: 67 clusters.
- Regime, shape/stability, decile, capacity/liquidity, scorecard, robust
  RankIC, robust LS, and unified profile artifacts regenerated.
- RankIC robust significance: 616 output rows.
- LS robust significance: 616 output rows.
- Factor evaluation page: 12,761,464 bytes.
- Page payload: 154 factors, generation time `2026-06-28 06:37 UTC`.
- Page QA: 108 PASS / 0 FAIL.
- Post-intake integrity QA for the 4 new factors: 92 PASS / 0 FAIL / 4 WARN.
- Full implemented public-manifest integrity QA: 88 factors, 2,112 checks,
  2,029 PASS, 0 FAIL, 83 WARN.

The warnings are optional PM-59A overlapping-sleeve summaries for eligible
diagnostic factors, not missing factor values, missing source metadata, page
coverage failures, or core workflow failures.

## Resource Note

This batch stays at the lower bound of the small-batch rule. The factors reuse
existing rolling mean, rolling standard deviation, rolling max, rolling min,
and division semantics, require no new data source, and extend Alpha158 rolling
price coverage without adding a parallel workflow.
