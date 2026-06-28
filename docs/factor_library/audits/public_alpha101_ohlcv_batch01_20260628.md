# Public Alpha101 OHLCV Batch01 Intake Audit - 2026-06-28

## Scope

This batch adds 5 public WorldQuant 101 Alpha factors that do not require
`IndNeutralize`, industry taxonomy, cap data, taker data, funding data, or a new
workflow:

- `wq101_alpha6`
- `wq101_alpha9`
- `wq101_alpha21`
- `wq101_alpha41`
- `wq101_alpha54`

Source reference: Kakushadze, "101 Formulaic Alphas" (`https://arxiv.org/pdf/1601.00991`).
The formulas were checked from the source PDF text before implementation.

Guardrails:

- Registry remains the only factor-definition entry point.
- No signal panel, trading, execution, broker, or live-production code changed.
- Generated HTML was rebuilt by workflow, not edited by hand.
- No new reusable operator was required.
- All factors are diagnostic research assets only.

## Formula Mapping

| factor_id | WQ101 formula shape | required inputs | lookback | direction |
| --- | --- | --- | --- | --- |
| `wq101_alpha6` | `-correlation(open, volume, 10)` | `open`, `volume` | 10 | conditional |
| `wq101_alpha9` | conditional `delta(close,1)` using `ts_min/ts_max(delta,5)` | `close` | 6 | conditional |
| `wq101_alpha21` | close mean/std state with `volume / adv20` branch | `close`, `volume` | 20 | conditional |
| `wq101_alpha41` | `sqrt(high * low) - vwap` | `high`, `low`, `volume`, `quote_volume` | 1 | conditional |
| `wq101_alpha54` | `(-1*((low-close)*open^5))/((low-high)*close^5)` | `open`, `high`, `low`, `close` | 1 | conditional |

`wq101_alpha41` derives bar VWAP as `quote_volume / volume` from canonical
bars. No external VWAP source was added.

## Validation

Pre/post implementation checks:

```bash
python -m py_compile scripts/factor_formula_registry.py scripts/build_factor_values.py
.venv/bin/python -m pytest tests/unit/test_public_alpha101_ohlcv_batch01.py tests/unit/test_public_factor_candidate_manifest.py tests/unit/test_public_factor_integration_status.py -q
.venv/bin/python scripts/build_factor_values.py --factor-ids wq101_alpha6,wq101_alpha9,wq101_alpha21,wq101_alpha41,wq101_alpha54
.venv/bin/python scripts/run_factor_intake.py --factor-ids wq101_alpha6 wq101_alpha9 wq101_alpha21 wq101_alpha41 wq101_alpha54 --run-id public_alpha101_ohlcv_batch01_20260628
.venv/bin/python scripts/build_factor_bilingual_cards.py
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids wq101_alpha6,wq101_alpha9,wq101_alpha21,wq101_alpha41,wq101_alpha54
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids wq101_alpha6,wq101_alpha9,wq101_alpha21,wq101_alpha41,wq101_alpha54 --start-from scorecard
```

Results:

- Factor values computed for all 5 factors.
- Coverage: `wq101_alpha6` 99.660%, `wq101_alpha9` 99.960%,
  `wq101_alpha21` 99.848%, `wq101_alpha41` 99.727%,
  `wq101_alpha54` 99.727%.
- Intake run `public_alpha101_ohlcv_batch01_20260628`: COMPLETE.
- Intake conclusion cards: 3 `CONDITIONAL_DIRECTION_REVIEW`,
  2 `REDUNDANT_WITH_EXISTING`.
- Post-intake state: 175 registered, 175 computed, 0 missing factor values,
  0 missing inputs.
- Factor evaluation page QA: 112 PASS / 0 FAIL.
- Post-intake integrity QA for the 5 new factors: 115 PASS / 0 FAIL /
  5 WARN.
- Public manifest status: Alpha101 20 total, 14 accounted/non-skipped,
  6 skipped taxonomy-blocked; Alpha158 101 total, 95 accounted/non-skipped,
  6 skipped duplicates.

The warnings are optional overlapping-sleeve diagnostics, not missing factor
values, missing source metadata, page coverage failures, or core workflow
failures.

## Resource Note

This batch stays within the small-batch rule. It uses only existing canonical
bar fields and single-symbol compute functions. The expensive stages were run
incrementally for the 5 factor IDs; no full blind refresh was used.
