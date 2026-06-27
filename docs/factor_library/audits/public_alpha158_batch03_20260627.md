# Public Alpha158 Batch 03 Audit - 2026-06-27

## Scope

Controlled third-batch intake for 6 public Alpha158 rolling candidates:

- `q158_beta_20h`
- `q158_rsqr_20h`
- `q158_resi_20h`
- `q158_imax_20h`
- `q158_imin_20h`
- `q158_imxd_20h`

Source reference: Microsoft Qlib Alpha158DL rolling formulas:
`https://github.com/microsoft/qlib/blob/main/qlib/contrib/data/loader.py`

This batch did not change signal composition, signal panel weights, backtest logic, live trading code, or execution code.

## Implementation Notes

Reusable operators added in `scripts/factor_ops.py`:

- `rolling_slope(series, n)`
- `rolling_rsquare(series, n)`
- `rolling_residual(series, n)`
- `rolling_idxmax(series, n)`
- `rolling_idxmin(series, n)`

The rolling regression operators use vectorized rolling sums instead of Python-level rolling regression loops. `rolling_idxmax` / `rolling_idxmin` return bars since the latest max/min in the window, matching the Alpha158 recency interpretation.

## Formulas

| factor_id | formula | fields | lookback | expected_direction |
|---|---|---|---:|---|
| `q158_beta_20h` | `rolling_slope(close, 20) / close` | `close` | 20 | `conditional` |
| `q158_rsqr_20h` | `rolling_rsquare(close, 20)` | `close` | 20 | `conditional` |
| `q158_resi_20h` | `rolling_residual(close, 20) / close` | `close` | 20 | `conditional` |
| `q158_imax_20h` | `rolling_idxmax(high, 20) / 20` | `high` | 20 | `conditional` |
| `q158_imin_20h` | `rolling_idxmin(low, 20) / 20` | `low` | 20 | `conditional` |
| `q158_imxd_20h` | `(rolling_idxmax(high, 20) - rolling_idxmin(low, 20)) / 20` | `high, low` | 20 | `conditional` |

## Workflow Evidence

Intake command:

```bash
.venv/bin/python scripts/run_factor_intake.py --factor-ids q158_beta_20h q158_rsqr_20h q158_resi_20h q158_imax_20h q158_imin_20h q158_imxd_20h --run-id public_alpha158_batch03_20260627
```

Intake result:

- Run directory: `research/factor_runs/crypto_top50_factor_library/factor_intake/public_alpha158_batch03_20260627/`
- Status: `COMPLETE`
- Quality checks: `8 PASS / 0 FAIL`
- Runtime: `776s`
- Factor values coverage: `99.848%`
- Conclusion cards:
  - `CONDITIONAL_DIRECTION_REVIEW`: 5
  - `REDUNDANT_WITH_EXISTING`: 1

Post-intake workflow:

```bash
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids q158_beta_20h,q158_rsqr_20h,q158_resi_20h,q158_imax_20h,q158_imin_20h,q158_imxd_20h
```

The first post-intake attempt reached `redundancy` after successful evaluate/paper/diagnostics stages and failed because new bilingual metadata rows had unescaped CSV commas. The CSV was repaired and the workflow resumed with:

```bash
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids q158_beta_20h,q158_rsqr_20h,q158_resi_20h,q158_imax_20h,q158_imin_20h,q158_imxd_20h --start-from redundancy
```

Final QA evidence:

- Resumed post-intake workflow: all 13 remaining stages completed successfully in `514.1s`
- `check_post_intake_workflow_integrity.py`: `PASS=138`, `FAIL=0`, `WARN=6`
- `check_factor_evaluation_page_completeness.py`: `PASS=108`, `FAIL=0`
- `check_factor_registry_integrity.py`: `102 factors checked`, `Critical issues: 0`
- `build_factor_library_state.py`: `Registered=102`, `Computed=102`, `Missing FV=0`, `Missing Input=0`

## Guardrail Notes

No parallel workflow, `*_v2.py`, signal promotion, or production claim was introduced.

