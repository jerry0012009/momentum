# Public Alpha158 Batch 04 Audit - 2026-06-27

## Scope

Controlled fourth-batch intake for 8 public Alpha158 rolling candidates:

- `q158_roc_20h`
- `q158_ma_20h`
- `q158_std_20h`
- `q158_max_20h`
- `q158_min_20h`
- `q158_cntd_20h`
- `q158_corr_20h`
- `q158_cord_20h`

Source reference: Microsoft Qlib Alpha158DL rolling formulas:
`https://github.com/microsoft/qlib/blob/main/qlib/contrib/data/loader.py`

This batch did not change signal composition, signal panel weights, backtest logic, live trading code, or execution code.

## Selection Notes

Selected factors are single-symbol Alpha158 20h rolling formulas with available OHLCV fields. No new reusable operator was required:

- Price rolling formulas reused `delay`, `rolling_mean`, `rolling_std`, `rolling_max`, and `rolling_min`.
- Direction-balance formula reused lag comparison plus `rolling_mean`.
- Volume-price formulas reused `rolling_corr` and `numpy.log`.

This batch deliberately stayed away from Alpha101 panel/cap formulas because those require cross-sectional handling or additional data contracts.

## Formulas

| factor_id | formula | fields | lookback | expected_direction |
|---|---|---|---:|---|
| `q158_roc_20h` | `Ref(close,20) / close` | `close` | 21 | `conditional` |
| `q158_ma_20h` | `Mean(close,20) / close` | `close` | 20 | `conditional` |
| `q158_std_20h` | `Std(close,20) / close` | `close` | 20 | `negative` |
| `q158_max_20h` | `Max(high,20) / close` | `high, close` | 20 | `conditional` |
| `q158_min_20h` | `Min(low,20) / close` | `low, close` | 20 | `conditional` |
| `q158_cntd_20h` | `Mean(close > Ref(close,1),20) - Mean(close < Ref(close,1),20)` | `close` | 21 | `positive` |
| `q158_corr_20h` | `Corr(close, Log(volume+1),20)` | `close, volume` | 20 | `conditional` |
| `q158_cord_20h` | `Corr(close/Ref(close,1), Log(volume/Ref(volume,1)+1),20)` | `close, volume` | 21 | `conditional` |

## Workflow Evidence

Intake command:

```bash
.venv/bin/python scripts/run_factor_intake.py --factor-ids q158_roc_20h q158_ma_20h q158_std_20h q158_max_20h q158_min_20h q158_cntd_20h q158_corr_20h q158_cord_20h --run-id public_alpha158_batch04_20260627
```

Intake result:

- Run directory: `research/factor_runs/crypto_top50_factor_library/factor_intake/public_alpha158_batch04_20260627/`
- Status: `COMPLETE`
- Quality checks: `8 PASS / 0 FAIL`
- Runtime: `863s`
- Factor values coverage:
  - 20h price factors: about `99.848%`
  - `q158_cntd_20h`: `99.840%`
  - `q158_corr_20h`: `99.580%`
  - `q158_cord_20h`: `99.495%`

Conclusion cards:

- `REDUNDANT_WITH_EXISTING`: `q158_roc_20h`, `q158_ma_20h`, `q158_cord_20h`
- `REVIEW_REQUIRED`: `q158_std_20h`, `q158_cntd_20h`
- `CONDITIONAL_DIRECTION_REVIEW`: `q158_max_20h`, `q158_min_20h`, `q158_corr_20h`

Post-intake workflow:

```bash
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids q158_roc_20h,q158_ma_20h,q158_std_20h,q158_max_20h,q158_min_20h,q158_cntd_20h,q158_corr_20h,q158_cord_20h
```

Post-intake result:

- All `17` workflow stages completed successfully in `965.5s`
- Redundancy stage used incremental mode: `5995` pairs covering `110` factors
- Unified profile: `110` factors, evidence completeness `100.00%`
- Page build: `reports/site/factor-library/factor-evaluation.html`

Final QA evidence:

- `check_factor_evaluation_page_completeness.py`: `PASS=108`, `FAIL=0`
- `check_post_intake_workflow_integrity.py`: `PASS=184`, `FAIL=0`, `WARN=8`
- `check_factor_registry_integrity.py`: `110 factors checked`, `Critical issues: 0`
- `build_factor_library_state.py`: `Registered=110`, `Computed=110`, `Missing FV=0`, `Missing Input=0`

## Guardrail Notes

No parallel workflow, `*_v2.py`, signal promotion, or production claim was introduced.

Metadata hygiene was also tightened:

- `factor_bilingual_cards.json` was synchronized from `factor_bilingual_cards.csv` so both contain `110` rows.
- `factor_card_qa_report.csv` was synchronized to `110` rows so scorecard metadata coverage matches the active factor count.
