# Public Alpha158 Batch09 Intake Audit - 2026-06-28

## Scope

This batch adds 4 public Alpha158 normalized volume lag factors:

- `q158_volume_ratio_1h`
- `q158_volume_ratio_2h`
- `q158_volume_ratio_3h`
- `q158_volume_ratio_4h`

Source reference: Microsoft Qlib Alpha158DL volume feature block in
`qlib/contrib/data/loader.py`. The Qlib volume block generates
`Ref($volume, d) / ($volume + 1e-12)` for lag windows. Window 0 is a constant
ratio and is intentionally not added as a factor.

Guardrails:

- Registry remains the only factor-definition entry point.
- No signal panel, trading, execution, broker, or live-production code changed.
- No generated HTML was edited by hand.
- No new reusable operator was required.
- All factors are diagnostic research assets only.

## Formula Mapping

| factor_id | Qlib formula shape | required inputs | lookback | direction |
| --- | --- | --- | --- | --- |
| `q158_volume_ratio_1h` | `Ref($volume,1)/($volume+1e-12)` | `volume` | 2 | conditional |
| `q158_volume_ratio_2h` | `Ref($volume,2)/($volume+1e-12)` | `volume` | 3 | conditional |
| `q158_volume_ratio_3h` | `Ref($volume,3)/($volume+1e-12)` | `volume` | 4 | conditional |
| `q158_volume_ratio_4h` | `Ref($volume,4)/($volume+1e-12)` | `volume` | 5 | conditional |

All four factors are single-symbol canonical-bar volume factors. Initial
per-symbol nulls are expected from the lag operator.

## Validation

Pre-intake checks:

```bash
python -m py_compile scripts/factor_formula_registry.py scripts/build_factor_bilingual_cards.py
.venv/bin/python -m pytest tests/unit/test_public_factor_candidate_manifest.py -q
python scripts/build_factor_bilingual_cards.py
PYTHONPATH=scripts python - <<'PY'
from factor_formula_registry import REGISTRY, REGISTRY_BY_ID
ids = "q158_volume_ratio_1h q158_volume_ratio_2h q158_volume_ratio_3h q158_volume_ratio_4h".split()
print("registry_total", len(REGISTRY))
for fid in ids:
    fs = REGISTRY_BY_ID[fid]
    print(fid, fs.family, fs.lookback_window, fs.required_columns)
PY
```

Results:

- Python compile passed.
- Manifest guard: 4 passed.
- Bilingual card generator validation: PASS, 138 cards.
- Registry total after registration: 138.
- Batch09 manifest rows: 4.
- Public manifest rows: 84 total, 72 implemented, 12 skipped.
- Implemented public rows by family: Alpha158 63, Alpha101 9.

Intake command:

```bash
.venv/bin/python scripts/run_factor_intake.py --factor-ids q158_volume_ratio_1h q158_volume_ratio_2h q158_volume_ratio_3h q158_volume_ratio_4h --run-id public_alpha158_batch09_20260628
```

Intake result:

- Runtime: 529s.
- Status: COMPLETE.
- Quality checks: 8 PASS / 0 FAIL.
- Factor values: 4/4 computed.
- Coverage: 99.992% for 1h lag, 99.984% for 2h lag, 99.976% for
  3h lag, and 99.968% for 4h lag.
- Redundancy intake pairs: 542.
- Conclusion cards: 4 `CONDITIONAL_DIRECTION_REVIEW`.
- Interpretation: these are valid public Alpha158 coverage rows with
  conditional direction; they should remain diagnostic unless direction and
  redundancy are reviewed.

Post-intake command:

```bash
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids q158_volume_ratio_1h,q158_volume_ratio_2h,q158_volume_ratio_3h,q158_volume_ratio_4h
```

Post-intake result:

- Runtime: 763.8s across 18 stages.
- Partial evaluation merged 4 factors.
- Paper diagnostics processed 4 factors, 0 errors.
- State: 138 registered, 138 computed, 0 missing factor values, 0 missing inputs.
- Diagnostics summary: 138 factors.
- Incremental redundancy: 542 new target pairs; merged matrix has 9,453 pairs
  across 138 factors.
- Redundancy cluster diagnostics: 138/138 coverage, 65 clusters.
- Regime diagnostics: 138 factors.
- Shape/stability diagnostics verified all 4 incremental factors.
- Decile diagnostics merged to 138 factors.
- Capacity/liquidity diagnostics merged to 138 factors.
- Scorecard: 138 rows.
- RankIC robust significance: 552 expected/output rows.
- Unified profile: 138 factors, evidence status 132 `COMPLETE` and 6
  `COMPLETE_WITH_WARNINGS`.
- Factor evaluation page: 11,477,261 bytes.
- Page QA: 108 PASS / 0 FAIL.
- Post-intake integrity QA for the 4 new factors: 92 PASS / 0 FAIL / 4 WARN.
- Full implemented public-manifest integrity QA: 72 factors, 1,728 checks,
  1,661 PASS, 0 FAIL, 67 WARN.

The warnings are optional PM-59A overlapping-sleeve summaries for eligible
diagnostic factors, not missing factor values, missing source metadata, page
coverage failures, or core workflow failures.

## Resource Note

This batch intentionally stays at the lower bound of the small-batch rule. These
volume ratios reuse existing `delay` and safe division semantics, require no new
data source, and expand Alpha158 coverage without adding a parallel workflow.
