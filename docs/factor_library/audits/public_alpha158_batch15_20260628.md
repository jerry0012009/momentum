# Public Alpha158 Batch15 Intake Audit - 2026-06-28

## Scope

This batch adds 4 public Alpha158 30h rolling position and quantile factors:

- `q158_rsv_30h`
- `q158_qtlu_30h`
- `q158_qtld_30h`
- `q158_rank_close_30h`

Source reference: Microsoft Qlib Alpha158DL rolling feature block in
`qlib/contrib/data/loader.py`. This batch maps Qlib's rolling RSV, QTLU,
QTLD, and RANK formulas to thirty one-hour crypto bars using only canonical
OHLC fields.

Guardrails:

- Registry remains the only factor-definition entry point.
- No signal panel, trading, execution, broker, or live-production code changed.
- Generated HTML was rebuilt by workflow, not edited by hand.
- No new reusable operator was required.
- All factors are diagnostic research assets only.

## Formula Mapping

| factor_id | Qlib formula shape | required inputs | lookback | direction |
| --- | --- | --- | --- | --- |
| `q158_rsv_30h` | `($close-Min($low,30))/(Max($high,30)-Min($low,30)+eps)` | `high`, `low`, `close` | 30 | conditional |
| `q158_qtlu_30h` | `Quantile($close,30,0.8)/$close` | `close` | 30 | conditional |
| `q158_qtld_30h` | `Quantile($close,30,0.2)/$close` | `close` | 30 | conditional |
| `q158_rank_close_30h` | `Rank($close,30)` | `close` | 30 | conditional |

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
- Bilingual card generator validation: PASS, 162 cards.
- Registry total after registration: 162.
- Batch15 manifest rows: 4.
- Public manifest rows: 108 total, 96 implemented, 12 skipped.
- Implemented public rows by family: Alpha158 87, Alpha101 9.

Intake command:

```bash
.venv/bin/python scripts/run_factor_intake.py --factor-ids q158_rsv_30h q158_qtlu_30h q158_qtld_30h q158_rank_close_30h --run-id public_alpha158_batch15_20260628
```

Intake result:

- Runtime: 1062.6s.
- Status: COMPLETE.
- Quality checks: 8 PASS / 0 FAIL.
- Factor values: 4/4 computed.
- Missing factor values: 0.
- Coverage: 99.767% for all four 30h rolling position/quantile factors.
- Redundancy intake pairs: 638.
- Redundancy distribution: 32 `HIGH_REDUNDANCY`, 57 `MODERATE_REDUNDANCY`,
  413 `LOW_REDUNDANCY`, and 136 `INSUFFICIENT_DATA`.
- Conclusion cards: 4 `REDUNDANT_WITH_EXISTING`.
- Interpretation: these rows extend Alpha158 30h rolling position and quantile
  coverage. They are valid public-factor diagnostics, but their intake cards
  mark them as redundant with existing library factors, so they are not signal
  promotion candidates.

Post-intake command:

```bash
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids q158_rsv_30h,q158_qtlu_30h,q158_qtld_30h,q158_rank_close_30h
```

Post-intake result:

- Runtime: 819.3s across 18 stages.
- Partial evaluation merged 4 factors.
- Paper diagnostics processed 4 factors.
- State: 162 registered, 162 computed, 0 missing factor values, 0 missing
  inputs.
- Diagnostics summary: 162 factors.
- Redundancy diagnostics: 13,041 pair rows across 162 factors.
- Redundancy cluster diagnostics: 67 clusters.
- Regime, shape/stability, decile, capacity/liquidity, scorecard, robust
  RankIC, robust LS, and unified profile artifacts regenerated.
- RankIC robust significance: 648 output rows.
- LS robust significance: 648 output rows.
- Factor evaluation page: 13,632,375 bytes.
- Page profile manifest generation time: `2026-06-28T07:46:38.960986+00:00`.
- Page QA: 108 PASS / 0 FAIL.
- Post-intake integrity QA for the 4 new factors: 92 PASS / 0 FAIL / 4 WARN.
- Full implemented public-manifest integrity QA: 96 factors, 2,304 checks,
  2,213 PASS, 0 FAIL, 91 WARN.

The warnings are optional PM-59A overlapping-sleeve summaries for eligible
diagnostic factors, not missing factor values, missing source metadata, page
coverage failures, or core workflow failures.

## Resource Note

This batch stays at the lower bound of the small-batch rule. It reuses
existing rolling min, rolling max, rolling quantile, time-series rank, and
division semantics, requires no new data source, and extends Alpha158 rolling
coverage without adding a parallel workflow.
