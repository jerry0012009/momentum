# Public Alpha158 Batch05 Intake Audit - 2026-06-27

## Scope

This batch added 8 public Alpha158 rolling direction / volume factors:

- `q158_sump_20h`
- `q158_sumn_20h`
- `q158_vma_20h`
- `q158_vstd_20h`
- `q158_wvma_20h`
- `q158_vsump_20h`
- `q158_vsumn_20h`
- `q158_vsumd_20h`

Source reference: Microsoft Qlib Alpha158DL rolling formulas in
`qlib/contrib/data/loader.py`.

Guardrails:

- Registry is the only factor-definition entry point.
- No signal, trading, execution, or live-production code changed.
- No new reusable operator was required.
- All factors were evaluated through the existing post-intake workflow.

## Formula Mapping

| factor_id | Qlib formula shape | required inputs | direction |
| --- | --- | --- | --- |
| `q158_sump_20h` | `Sum(Greater($close-Ref($close,1),0),20)/(Sum(Abs($close-Ref($close,1)),20)+1e-12)` | `close` | positive |
| `q158_sumn_20h` | `Sum(Greater(Ref($close,1)-$close,0),20)/(Sum(Abs($close-Ref($close,1)),20)+1e-12)` | `close` | negative |
| `q158_vma_20h` | `Mean($volume,20)/($volume+1e-12)` | `volume` | conditional |
| `q158_vstd_20h` | `Std($volume,20)/($volume+1e-12)` | `volume` | conditional |
| `q158_wvma_20h` | `Std(Abs($close/Ref($close,1)-1)*$volume,20)/(Mean(Abs($close/Ref($close,1)-1)*$volume,20)+1e-12)` | `close`, `volume` | negative |
| `q158_vsump_20h` | `Sum(Greater($volume-Ref($volume,1),0),20)/(Sum(Abs($volume-Ref($volume,1)),20)+1e-12)` | `volume` | conditional |
| `q158_vsumn_20h` | `Sum(Greater(Ref($volume,1)-$volume,0),20)/(Sum(Abs($volume-Ref($volume,1)),20)+1e-12)` | `volume` | conditional |
| `q158_vsumd_20h` | `(Sum(Greater($volume-Ref($volume,1),0),20)-Sum(Greater(Ref($volume,1)-$volume,0),20))/(Sum(Abs($volume-Ref($volume,1)),20)+1e-12)` | `volume` | conditional |

## Validation

Pre-intake checks:

- Python compile checks passed for the registry and workflow scripts.
- Manifest, bilingual card CSV/JSON, and card QA metadata parsed successfully.
- Registry integrity checked 118 factors with 0 critical issues.
- Smoke computation on one symbol produced non-null values for all 8 factors.

Intake command:

```bash
.venv/bin/python scripts/run_factor_intake.py --factor-ids q158_sump_20h q158_sumn_20h q158_vma_20h q158_vstd_20h q158_wvma_20h q158_vsump_20h q158_vsumn_20h q158_vsumd_20h --run-id public_alpha158_batch05_20260627
```

Intake result:

- Runtime: 950s.
- Quality checks: 8 PASS / 0 FAIL.
- Conclusion buckets: 5 `REDUNDANT_WITH_EXISTING`, 3 `REVIEW_REQUIRED`.
- State after intake: 118 registered, 118 computed, 0 missing factor values, 0 missing inputs.

Post-intake command:

```bash
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids q158_sump_20h,q158_sumn_20h,q158_vma_20h,q158_vstd_20h,q158_wvma_20h,q158_vsump_20h,q158_vsumn_20h,q158_vsumd_20h
```

Post-intake result:

- 17 workflow stages completed successfully in 1033.0s.
- Incremental redundancy covered 6903 pairs across 118 factors.
- Unified profile covered 118 factors.
- Factor evaluation page QA: 108 PASS / 0 FAIL.
- Post-intake integrity QA: 184 PASS / 0 FAIL / 8 WARN.
- Final state: 118 registered, 118 computed, 0 missing factor values, 0 missing inputs.

## Resource Note

Batch05 was intentionally small enough to complete, but it still took over 30 minutes
across intake and post-intake completion because redundancy and page-generation
artifacts scale with the full library. Future public Alpha158/Alpha101 intake batches
should prefer 5-6 factors unless the formulas are trivial and no new diagnostics are
required.
