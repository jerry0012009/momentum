# Public Alpha158 Batch14 Intake Audit - 2026-06-28

## Scope

This batch adds 4 public Alpha158 rolling 60h price factors:

- `q158_ma_60h`
- `q158_std_60h`
- `q158_max_60h`
- `q158_min_60h`

Source reference: Microsoft Qlib Alpha158DL rolling price feature block in
`qlib/contrib/data/loader.py`. This batch maps Qlib's rolling MA, STD, MAX,
and MIN formulas to sixty one-hour crypto bars using only canonical OHLC
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
| `q158_ma_60h` | `Mean($close,60)/$close` | `close` | 60 | conditional |
| `q158_std_60h` | `Std($close,60)/$close` | `close` | 60 | negative |
| `q158_max_60h` | `Max($high,60)/$close` | `high`, `close` | 60 | conditional |
| `q158_min_60h` | `Min($low,60)/$close` | `low`, `close` | 60 | conditional |

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
- Bilingual card generator validation: PASS, 158 cards.
- Registry total after registration: 158.
- Batch14 manifest rows: 4.
- Public manifest rows: 104 total, 92 implemented, 12 skipped.
- Implemented public rows by family: Alpha158 83, Alpha101 9.

Intake command:

```bash
.venv/bin/python scripts/run_factor_intake.py --factor-ids q158_ma_60h q158_std_60h q158_max_60h q158_min_60h --run-id public_alpha158_batch14_20260628
```

Intake result:

- Runtime: 651.2s.
- Status: COMPLETE.
- Quality checks: 8 PASS / 0 FAIL.
- Factor values: 4/4 computed.
- Missing factor values: 0.
- Coverage: 99.527% for all four 60h rolling price ratios.
- Redundancy intake pairs: 622.
- Redundancy distribution: 1 `NEAR_DUPLICATE`, 5 `HIGH_REDUNDANCY`,
  22 `MODERATE_REDUNDANCY`, 466 `LOW_REDUNDANCY`, and
  128 `INSUFFICIENT_DATA`.
- Conclusion cards: 2 `CONDITIONAL_DIRECTION_REVIEW`,
  1 `REDUNDANT_WITH_EXISTING`, and 1 `REVIEW_REQUIRED`.
- Interpretation: these rows extend the Alpha158 rolling price block to a
  longer 60h window. They are valid public-factor diagnostics, not signal
  additions.

Post-intake command:

```bash
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids q158_ma_60h,q158_std_60h,q158_max_60h,q158_min_60h
```

Post-intake result:

- Runtime: 793.0s across 18 stages.
- Partial evaluation merged 4 factors.
- Paper diagnostics processed 4 factors.
- State: 158 registered, 158 computed, 0 missing factor values, 0 missing
  inputs.
- Diagnostics summary: 158 factors.
- Redundancy diagnostics: 12,403 pair rows across 158 factors.
- Redundancy cluster diagnostics: 69 clusters.
- Regime, shape/stability, decile, capacity/liquidity, scorecard, robust
  RankIC, robust LS, and unified profile artifacts regenerated.
- RankIC robust significance: 632 output rows.
- LS robust significance: 632 output rows.
- Factor evaluation page: 13,307,295 bytes.
- Page profile manifest generation time: `2026-06-28T07:07:47.243806+00:00`.
- Page QA: 108 PASS / 0 FAIL.
- Post-intake integrity QA for the 4 new factors: 92 PASS / 0 FAIL / 4 WARN.
- Full implemented public-manifest integrity QA: 92 factors, 2,208 checks,
  2,121 PASS, 0 FAIL, 87 WARN.

The warnings are optional PM-59A overlapping-sleeve summaries for eligible
diagnostic factors, not missing factor values, missing source metadata, page
coverage failures, or core workflow failures.

## Resource Note

This batch stays at the lower bound of the small-batch rule. The factors reuse
existing rolling mean, rolling standard deviation, rolling max, rolling min,
and division semantics, require no new data source, and extend Alpha158 rolling
price coverage without adding a parallel workflow.
