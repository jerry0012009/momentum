# Public Alpha158 Batch 02 Audit - 2026-06-26

## Scope

Controlled second-batch intake for 6 public Alpha158 rolling candidates:

- `q158_qtlu_20h`
- `q158_qtld_20h`
- `q158_rank_close_20h`
- `q158_cntp_20h`
- `q158_cntn_20h`
- `q158_sumd_20h`

Source reference: Microsoft Qlib Alpha158DL rolling formulas:
`https://github.com/microsoft/qlib/blob/main/qlib/contrib/data/loader.py`

This batch did not change signal composition, signal panel weights, backtest logic, live trading code, or execution code.

## Selection Notes

Selected factors are single-symbol, close-only, 20h/21h rolling candidates. They were chosen to avoid another Kbar-only batch after Batch 01 showed heavy Kbar redundancy.

Deferred candidates are recorded in `docs/factor_library/public_factor_candidate_manifest.csv`:

- `q158_beta_20h`, `q158_rsqr_20h`, `q158_resi_20h`: require reusable rolling regression operators.
- `q158_imax_20h`, `q158_imin_20h`, `q158_imxd_20h`: require reusable rolling index-position operators.

## Formulas

| factor_id | formula | fields | lookback | expected_direction |
|---|---|---|---:|---|
| `q158_qtlu_20h` | `rolling_quantile(close, 20, 0.8) / close` | `close` | 20 | `conditional` |
| `q158_qtld_20h` | `rolling_quantile(close, 20, 0.2) / close` | `close` | 20 | `conditional` |
| `q158_rank_close_20h` | `rank(close, 20)` | `close` | 20 | `conditional` |
| `q158_cntp_20h` | `mean(close > close_1h_ago, 20)` | `close` | 21 | `positive` |
| `q158_cntn_20h` | `mean(close < close_1h_ago, 20)` | `close` | 21 | `negative` |
| `q158_sumd_20h` | `(sum(up moves, 20) - sum(down moves, 20)) / (sum(abs moves, 20) + 1e-12)` | `close` | 21 | `positive` |

## Workflow Evidence

Intake command:

```bash
.venv/bin/python scripts/run_factor_intake.py --factor-ids q158_qtlu_20h q158_qtld_20h q158_rank_close_20h q158_cntp_20h q158_cntn_20h q158_sumd_20h --run-id public_alpha158_batch02_20260626
```

Intake result:

- Run directory: `research/factor_runs/crypto_top50_factor_library/factor_intake/public_alpha158_batch02_20260626/`
- Status: `COMPLETE`
- Quality checks: `8 PASS / 0 FAIL`
- Runtime: `1014s`
- Factor values coverage:
  - 20h factors: `99.848%`
  - 21h factors: `99.840%`
- Conclusion cards:
  - `REDUNDANT_WITH_EXISTING`: 3
  - `REVIEW_REQUIRED`: 3

Post-intake workflow:

```bash
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids q158_qtlu_20h,q158_qtld_20h,q158_rank_close_20h,q158_cntp_20h,q158_cntn_20h,q158_sumd_20h
```

Final QA evidence:

- Post-intake workflow: all 17 stages completed successfully in `751.5s`
- `check_post_intake_workflow_integrity.py`: `PASS=138`, `FAIL=0`, `WARN=6`
- `check_factor_evaluation_page_completeness.py`: `PASS=108`, `FAIL=0`
- `check_factor_registry_integrity.py`: `96 factors checked`, `Critical issues: 0`
- `build_factor_library_state.py`: `Registered=96`, `Computed=96`, `Missing FV=0`, `Missing Input=0`

## Guardrail Notes

Only one reusable operator was added:

- `rolling_quantile(series, n, q)` in `scripts/factor_ops.py`

No parallel workflow, `*_v2.py`, signal promotion, or production claim was introduced.

