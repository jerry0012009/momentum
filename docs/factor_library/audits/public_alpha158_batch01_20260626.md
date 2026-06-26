# Public Alpha158 Batch 01 Audit - 2026-06-26

## Scope

Controlled pilot intake for 6 public Alpha158 candidates:

- `q158_klen_open`
- `q158_kup_open`
- `q158_klow_open`
- `q158_ksft_open`
- `q158_ksft_range`
- `q158_rsv_20h`

Source reference: Microsoft Qlib Alpha158DL kbar / rolling formulas:
`https://github.com/microsoft/qlib/blob/main/qlib/contrib/data/loader.py`

This batch did not change signal composition, signal panel weights, backtest logic, live trading code, or execution code.

## Implementation Notes

- Registry entry point: `scripts/factor_formula_registry.py`
- Public candidate manifest: `docs/factor_library/public_factor_candidate_manifest.csv`
- START_HERE entry pointer: `docs/factor_library/START_HERE.md`
- Metadata source cards: `research/factor_runs/crypto_top50_factor_library/factor_metadata/factor_bilingual_cards.csv`
- Factor values dataset: `data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/`

All 6 factors are single-symbol OHLCV factors. No new operator or parallel workflow was added.

## Formulas

| factor_id | formula | fields | lookback | expected_direction |
|---|---|---|---:|---|
| `q158_klen_open` | `(high - low) / open` | `open, high, low` | 1 | `conditional` |
| `q158_kup_open` | `(high - max(open, close)) / open` | `open, high, close` | 1 | `negative` |
| `q158_klow_open` | `(min(open, close) - low) / open` | `open, low, close` | 1 | `positive` |
| `q158_ksft_open` | `(2 * close - high - low) / open` | `open, high, low, close` | 1 | `positive` |
| `q158_ksft_range` | `(2 * close - high - low) / (high - low + 1e-12)` | `high, low, close` | 1 | `positive` |
| `q158_rsv_20h` | `(close - rolling_min(low, 20)) / (rolling_max(high, 20) - rolling_min(low, 20) + 1e-12)` | `high, low, close` | 20 | `conditional` |

## Workflow Evidence

Intake command:

```bash
.venv/bin/python scripts/run_factor_intake.py --factor-ids q158_klen_open q158_kup_open q158_klow_open q158_ksft_open q158_ksft_range q158_rsv_20h --run-id public_alpha158_batch01_20260626
```

Intake result:

- Run directory: `research/factor_runs/crypto_top50_factor_library/factor_intake/public_alpha158_batch01_20260626/`
- Status: `COMPLETE`
- Quality checks: `8 PASS / 0 FAIL`
- Factor values coverage:
  - 5 one-bar kbar factors: `100.000%`
  - `q158_rsv_20h`: `99.848%` because of 20-bar warmup
- Conclusion cards:
  - `REVIEW_REQUIRED`: 4
  - `REDUNDANT_WITH_EXISTING`: 2

Post-intake workflow:

```bash
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids q158_klen_open,q158_kup_open,q158_klow_open,q158_ksft_open,q158_ksft_range,q158_rsv_20h --start-from profile
```

Final QA evidence:

- `check_post_intake_workflow_integrity.py`: `PASS=138`, `FAIL=0`, `WARN=6`
- `check_factor_evaluation_page_completeness.py`: `PASS=108`, `FAIL=0`
- `check_factor_registry_integrity.py`: `90 factors checked`, `Critical issues: 0`
- `build_factor_library_state.py`: `Registered=90`, `Computed=90`, `Missing FV=0`, `Missing Input=0`

## Guardrail Notes

The page QA script was updated to remove hard-coded 84-factor assumptions:

- HTML size threshold now scales from the 84-factor baseline.
- PM-55 / PM-57 factor-count checks now compare against the current profile count.

This is a workflow guardrail change, not a factor promotion.

