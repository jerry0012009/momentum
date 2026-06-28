# Public Alpha158 Batch16 Intake Audit - 2026-06-28

## Scope

This batch adds 4 public Alpha158 30h rolling regression and position factors:

- `q158_beta_30h`
- `q158_rsqr_30h`
- `q158_resi_30h`
- `q158_imax_30h`

Source reference: Microsoft Qlib Alpha158DL rolling feature block in
`qlib/contrib/data/loader.py`. This batch maps Qlib's rolling BETA, RSQR,
RESI, and IMAX formulas to thirty one-hour crypto bars using canonical OHLC
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
| `q158_beta_30h` | `Slope($close,30)/$close` | `close` | 30 | conditional |
| `q158_rsqr_30h` | `Rsquare($close,30)` | `close` | 30 | conditional |
| `q158_resi_30h` | `Resi($close,30)/$close` | `close` | 30 | conditional |
| `q158_imax_30h` | `IdxMax($high,30)/30` | `high` | 30 | conditional |

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
- Bilingual card generator validation: PASS, 166 cards.
- Registry total after registration: 166.
- Batch16 manifest rows: 4.
- Public manifest rows: 112 total, 100 implemented, 12 skipped.
- Implemented public rows by family: Alpha158 91, Alpha101 9.

Intake command:

```bash
.venv/bin/python scripts/run_factor_intake.py --factor-ids q158_beta_30h q158_rsqr_30h q158_resi_30h q158_imax_30h --run-id public_alpha158_batch16_20260628
```

Intake result:

- Runtime: 737.2s.
- Status: COMPLETE.
- Quality checks: 8 PASS / 0 FAIL.
- Factor values: 4/4 computed.
- Missing factor values: 0.
- Coverage: 99.754% to 99.767% across the four rolling regression/position
  factors.
- Redundancy intake pairs: 654.
- Redundancy distribution: 1 `NEAR_DUPLICATE`, 2 `HIGH_REDUNDANCY`,
  22 `MODERATE_REDUNDANCY`, 493 `LOW_REDUNDANCY`, and
  136 `INSUFFICIENT_DATA`.
- Conclusion cards: 3 `CONDITIONAL_DIRECTION_REVIEW` and
  1 `REDUNDANT_WITH_EXISTING`.
- Interpretation: these rows extend Alpha158 30h rolling regression and
  position coverage. They are valid public-factor diagnostics, not signal
  additions.

Post-intake command:

```bash
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids q158_beta_30h,q158_rsqr_30h,q158_resi_30h,q158_imax_30h
```

Post-intake result:

- Runtime: 827.4s across 18 stages.
- Partial evaluation merged 4 factors.
- Paper diagnostics processed 4 factors.
- State: 166 registered, 166 computed, 0 missing factor values, 0 missing
  inputs.
- Diagnostics summary: 166 factors.
- Redundancy diagnostics: 13,695 pair rows across 166 factors.
- Redundancy cluster diagnostics: 70 clusters.
- Regime, shape/stability, decile, capacity/liquidity, scorecard, robust
  RankIC, robust LS, and unified profile artifacts regenerated.
- RankIC robust significance: 664 output rows.
- LS robust significance: 664 output rows.
- Factor evaluation page: 13,957,733 bytes.
- Page profile manifest generation time: `2026-06-28T08:18:26.474683+00:00`.
- Page QA: 108 PASS / 0 FAIL.
- Post-intake integrity QA for the 4 new factors: 92 PASS / 0 FAIL / 4 WARN.
- Full implemented public-manifest integrity QA: 100 factors, 2,400 checks,
  2,305 PASS, 0 FAIL, 95 WARN.

The warnings are optional PM-59A overlapping-sleeve summaries for eligible
diagnostic factors, not missing factor values, missing source metadata, page
coverage failures, or core workflow failures.

## Resource Note

This batch stays at the lower bound of the small-batch rule. It reuses
existing rolling slope, rolling R-squared, rolling residual, rolling idxmax,
and division semantics, requires no new data source, and extends Alpha158
rolling regression coverage without adding a parallel workflow.
