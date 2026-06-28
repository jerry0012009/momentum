# Public Alpha158 Batch08 Intake Audit - 2026-06-28

## Scope

This batch adds 6 public Alpha158 normalized price lag factors:

- `q158_open_close_2h`
- `q158_high_close_2h`
- `q158_low_close_2h`
- `q158_open_close_3h`
- `q158_high_close_3h`
- `q158_low_close_3h`

Source reference: Microsoft Qlib Alpha158DL price feature block in
`qlib/contrib/data/loader.py`. The Qlib price block generates
`Ref($field, d) / $close` for `open`, `high`, and `low` lag windows.

Guardrails:

- Registry remains the only factor-definition entry point.
- No signal panel, trading, execution, broker, or live-production code changed.
- No generated HTML was edited by hand.
- No new reusable operator was required.
- All factors were evaluated as diagnostic research assets only.

## Formula Mapping

| factor_id | Qlib formula shape | required inputs | lookback | direction |
| --- | --- | --- | --- | --- |
| `q158_open_close_2h` | `Ref($open,2)/$close` | `open`, `close` | 3 | conditional |
| `q158_high_close_2h` | `Ref($high,2)/$close` | `high`, `close` | 3 | conditional |
| `q158_low_close_2h` | `Ref($low,2)/$close` | `low`, `close` | 3 | conditional |
| `q158_open_close_3h` | `Ref($open,3)/$close` | `open`, `close` | 4 | conditional |
| `q158_high_close_3h` | `Ref($high,3)/$close` | `high`, `close` | 4 | conditional |
| `q158_low_close_3h` | `Ref($low,3)/$close` | `low`, `close` | 4 | conditional |

All six factors are single-symbol OHLC factors. The 2h lag formulas require
three bars; the 3h lag formulas require four bars. Initial per-symbol nulls are
expected from the lag operator.

## Validation

Pre-intake checks:

```bash
python -m py_compile scripts/factor_formula_registry.py
.venv/bin/python -m pytest tests/unit/test_public_factor_candidate_manifest.py -q
PYTHONPATH=scripts python - <<'PY'
from factor_formula_registry import REGISTRY, REGISTRY_BY_ID
ids = "q158_open_close_2h q158_high_close_2h q158_low_close_2h q158_open_close_3h q158_high_close_3h q158_low_close_3h".split()
print("registry_total", len(REGISTRY))
for fid in ids:
    fs = REGISTRY_BY_ID[fid]
    print(fid, fs.family, fs.lookback_window, fs.required_columns)
PY
```

Results:

- Python compile passed.
- Manifest guard: 4 passed.
- Registry total after registration: 134.
- Batch08 manifest rows: 6.
- Public manifest rows: 80 total, 68 implemented, 12 skipped.
- Implemented public rows by family: Alpha158 59, Alpha101 9.

Intake command:

```bash
.venv/bin/python scripts/run_factor_intake.py --factor-ids q158_open_close_2h q158_high_close_2h q158_low_close_2h q158_open_close_3h q158_high_close_3h q158_low_close_3h --run-id public_alpha158_batch08_20260628
```

Intake result:

- Runtime: 676s.
- Status: COMPLETE.
- Quality checks: 8 PASS / 0 FAIL.
- Factor values: 6/6 computed.
- Coverage: 99.984% for 2h lag factors; 99.976% for 3h lag factors.
- Redundancy intake pairs: 783.
- Conclusion cards: 6 `REDUNDANT_WITH_EXISTING`.
- Interpretation: the factors are valid public Alpha158 coverage rows but should
  not be treated as independent signal discoveries without redundancy review.

Post-intake command:

```bash
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids q158_open_close_2h,q158_high_close_2h,q158_low_close_2h,q158_open_close_3h,q158_high_close_3h,q158_low_close_3h
```

Post-intake result:

- Partial evaluation merged 6 factors.
- Paper diagnostics processed 6 factors, 0 errors.
- State: 134 registered, 134 computed, 0 missing factor values, 0 missing inputs.
- Diagnostics summary: 134 factors.
- Incremental redundancy: 783 new target pairs; merged matrix has 8,911 pairs
  across 134 factors.
- Redundancy cluster diagnostics: 134/134 coverage, 61 clusters.
- Regime diagnostics: 134 factors.
- Shape/stability diagnostics verified all 6 incremental factors.
- Decile diagnostics merged to 134 factors.
- Capacity/liquidity diagnostics merged to 134 factors.
- Scorecard: 134 rows.
- RankIC robust significance: 536 expected/output rows.
- Unified profile: 134 factors, evidence status 128 `COMPLETE` and 6
  `COMPLETE_WITH_WARNINGS`.
- Factor evaluation page: 11,155,267 bytes.
- Page QA: 108 PASS / 0 FAIL.
- Post-intake integrity QA for the 6 new factors: 138 PASS / 0 FAIL / 6 WARN.

The first post-intake integrity attempt failed only on `source_metadata` because
the bilingual card metadata layer still had 128 rows. The fix was to update the
existing reproducible `scripts/build_factor_bilingual_cards.py` generator so it
validates against current registry size, preserves the
`SOURCE_MAPPED_REVIEW_REQUIRED` quality class, and emits `alpha158_price`
metadata. Then the metadata, scorecard, profile, page, page QA, and integrity QA
were regenerated. No generated HTML was edited by hand.

## Resource Note

This batch intentionally stays within the small-batch rule. It extends the
already validated Alpha158 normalized price block without adding a new operator,
data source, workflow, signal surface, or trading/execution behavior.
