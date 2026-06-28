# Public Alpha158 Batch12 Intake Audit - 2026-06-28

## Scope

This batch adds 4 public Alpha158 rolling 10h price factors:

- `q158_ma_10h`
- `q158_std_10h`
- `q158_max_10h`
- `q158_min_10h`

Source reference: Microsoft Qlib Alpha158DL rolling price feature block in
`qlib/contrib/data/loader.py`. This batch maps Qlib's rolling MA, STD, MAX,
and MIN formulas to ten one-hour crypto bars using only canonical OHLC fields.

Guardrails:

- Registry remains the only factor-definition entry point.
- No signal panel, trading, execution, broker, or live-production code changed.
- Generated HTML was rebuilt by workflow, not edited by hand.
- No new reusable operator was required.
- All factors are diagnostic research assets only.

## Formula Mapping

| factor_id | Qlib formula shape | required inputs | lookback | direction |
| --- | --- | --- | --- | --- |
| `q158_ma_10h` | `Mean($close,10)/$close` | `close` | 10 | conditional |
| `q158_std_10h` | `Std($close,10)/$close` | `close` | 10 | negative |
| `q158_max_10h` | `Max($high,10)/$close` | `high`, `close` | 10 | conditional |
| `q158_min_10h` | `Min($low,10)/$close` | `low`, `close` | 10 | conditional |

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
- Bilingual card generator validation: PASS, 150 cards.
- Registry total after registration: 150.
- Batch12 manifest rows: 4.
- Public manifest rows: 96 total, 84 implemented, 12 skipped.
- Implemented public rows by family: Alpha158 75, Alpha101 9.

Intake command:

```bash
.venv/bin/python scripts/run_factor_intake.py --factor-ids q158_ma_10h q158_std_10h q158_max_10h q158_min_10h --run-id public_alpha158_batch12_20260628
```

Intake result:

- Runtime: 623.9s.
- Status: COMPLETE.
- Quality checks: 8 PASS / 0 FAIL.
- Factor values: 4/4 computed.
- Missing factor values: 0.
- Coverage: 99.928% for all four 10h rolling price ratios.
- Redundancy intake pairs: 590.
- Conclusion cards: 2 `CONDITIONAL_DIRECTION_REVIEW`, 1
  `REDUNDANT_WITH_EXISTING`, and 1 `REVIEW_REQUIRED`.
- Interpretation: these rows fill the 10h Alpha158 rolling price window
  between the existing 5h and 20h blocks. They are valid public-factor
  diagnostics, not signal additions.

Post-intake command:

```bash
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids q158_ma_10h,q158_std_10h,q158_max_10h,q158_min_10h
```

Post-intake result:

- Runtime: 791.3s across 18 stages.
- Partial evaluation merged 4 factors.
- Paper diagnostics processed 4 factors.
- State: 150 registered, 150 computed, 0 missing factor values, 0 missing
  inputs.
- Diagnostics summary: 150 factors.
- Redundancy diagnostics: 11,175 pair rows across 150 factors.
- Redundancy cluster diagnostics: 66 clusters.
- Regime, shape/stability, decile, capacity/liquidity, scorecard, robust
  RankIC, robust LS, and unified profile artifacts regenerated.
- RankIC robust significance: 600 output rows.
- LS robust significance: 600 output rows.
- Factor evaluation page: 12,440,217 bytes.
- Page payload: 150 factors, generation time `2026-06-28 06:07 UTC`.
- Page QA: 108 PASS / 0 FAIL.
- Post-intake integrity QA for the 4 new factors: 92 PASS / 0 FAIL / 4 WARN.
- Full implemented public-manifest integrity QA: 84 factors, 2,016 checks,
  1,937 PASS, 0 FAIL, 79 WARN.

The warnings are optional PM-59A overlapping-sleeve summaries for eligible
diagnostic factors, not missing factor values, missing source metadata, page
coverage failures, or core workflow failures.

## Resource Note

This batch stays at the lower bound of the small-batch rule. The factors reuse
existing rolling mean, rolling standard deviation, rolling max, rolling min,
and division semantics, require no new data source, and extend Alpha158 rolling
price coverage without adding a parallel workflow.
