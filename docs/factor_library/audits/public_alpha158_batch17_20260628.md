# Public Alpha158 Batch17 Intake Audit - 2026-06-28

## Scope

This batch adds 4 public Alpha158 30h rolling direction factors:

- `q158_cntp_30h`
- `q158_cntn_30h`
- `q158_cntd_30h`
- `q158_sumd_30h`

Source reference: Microsoft Qlib Alpha158DL rolling direction feature block in
`qlib/contrib/data/loader.py`. This batch maps Qlib's CNTP, CNTN, CNTD, and
SUMD formulas to thirty one-hour crypto bars using canonical close prices.

Guardrails:

- Registry remains the only factor-definition entry point.
- No signal panel, trading, execution, broker, or live-production code changed.
- Generated HTML was rebuilt by workflow, not edited by hand.
- No new reusable operator was required.
- All factors are diagnostic research assets only.

## Formula Mapping

| factor_id | Qlib formula shape | required inputs | lookback | direction |
| --- | --- | --- | --- | --- |
| `q158_cntp_30h` | `Mean($close > Ref($close,1),30)` | `close` | 31 | positive |
| `q158_cntn_30h` | `Mean($close < Ref($close,1),30)` | `close` | 31 | negative |
| `q158_cntd_30h` | `Mean(up,30) - Mean(down,30)` | `close` | 31 | positive |
| `q158_sumd_30h` | `(Sum(up moves,30) - Sum(down moves,30)) / Sum(abs moves,30)` | `close` | 31 | positive |

All four factors are single-symbol canonical-bar close-only factors. The
lookback is 31 because each rolling 30-bar direction measure also uses
`Ref(close,1)`.

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
- Bilingual card generator validation: PASS, 170 cards.
- Registry total after registration: 170.
- Batch17 manifest rows: 4.
- Public manifest rows: 116 total, 104 implemented, 12 skipped.
- Implemented public rows by family: Alpha158 95, Alpha101 9.

Intake command:

```bash
.venv/bin/python scripts/run_factor_intake.py --factor-ids q158_cntp_30h q158_cntn_30h q158_cntd_30h q158_sumd_30h --run-id public_alpha158_batch17_20260628
```

Intake result:

- Runtime: 674s.
- Status: COMPLETE.
- Quality checks: 8 PASS / 0 FAIL.
- Factor values: 4/4 computed.
- Missing factor values: 0.
- Coverage: 99.759% across all four factors.
- Redundancy intake pairs: 670.
- Redundancy distribution: 2 `NEAR_DUPLICATE`, 3 `HIGH_REDUNDANCY`,
  17 `MODERATE_REDUNDANCY`, 304 `LOW_REDUNDANCY`, and
  344 `INSUFFICIENT_DATA`.
- Conclusion cards: 4 `REVIEW_REQUIRED`.
- Interpretation: these rows complete more of the Alpha158 rolling direction
  family, but they are not promotion candidates. The intake cards flag
  RankIC/long-short divergence and direction-semantics review.

Post-intake command:

```bash
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids q158_cntp_30h,q158_cntn_30h,q158_cntd_30h,q158_sumd_30h
```

Post-intake result:

- Runtime: 807.3s across 18 stages.
- Partial evaluation merged 4 factors.
- Paper diagnostics processed 4 factors.
- State: 170 registered, 170 computed, 0 missing factor values, 0 missing
  inputs.
- Diagnostics summary: 170 factors.
- Redundancy diagnostics: 14,365 pair rows across 170 factors.
- Redundancy cluster diagnostics: 71 clusters.
- Regime, shape/stability, decile, capacity/liquidity, scorecard, robust
  RankIC, robust LS, and unified profile artifacts regenerated.
- RankIC robust significance: 680 output rows.
- LS robust significance: 680 output rows.
- Factor evaluation page: 14,042,269 bytes.
- Page profile manifest generation time: `2026-06-28T08:57:06.014507+00:00`.
- Page QA: 108 PASS / 0 FAIL.
- Post-intake integrity QA for the 4 new factors: 92 PASS / 0 FAIL / 4 WARN.
- Full implemented public-manifest integrity QA: 104 factors, 2,496 checks,
  2,397 PASS, 0 FAIL, 99 WARN.

The warnings are optional PM-59A overlapping-sleeve summaries for eligible
diagnostic factors, not missing factor values, missing source metadata, page
coverage failures, or core workflow failures.

## Resource Note

This batch stays at the lower bound of the small-batch rule. It reuses existing
delay, comparison, rolling mean, rolling sum, and division semantics, requires
no new data source, and extends Alpha158 rolling direction coverage without
adding a parallel workflow.
