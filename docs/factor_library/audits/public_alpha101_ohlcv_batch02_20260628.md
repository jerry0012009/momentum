# Public Alpha101 OHLCV Batch02 Intake Audit - 2026-06-28

## Scope

This batch adds 5 public WorldQuant 101 Alpha factors using only canonical
OHLCV bar fields and the existing factor-library workflow:

- `wq101_alpha23`
- `wq101_alpha24`
- `wq101_alpha46`
- `wq101_alpha49`
- `wq101_alpha51`

Source reference: Kakushadze, "101 Formulaic Alphas"
(`https://arxiv.org/pdf/1601.00991`).

Guardrails:

- Registry remains the only factor-definition entry point.
- No signal panel, trading, execution, broker, or live-production code changed.
- Generated HTML was rebuilt by workflow, not edited by hand.
- No new workflow or `*_v2.py` script was added.
- `ts_rank` received a reusable performance-preserving implementation cleanup,
  guarded by existing operator tests.
- All factors are diagnostic research assets only.

## Formula Mapping

| factor_id | WQ101 formula shape | required inputs | lookback | direction |
| --- | --- | --- | --- | --- |
| `wq101_alpha23` | `where(mean(high,20)<high,-delta(high,2),0)` | `high` | 20 | conditional |
| `wq101_alpha24` | mean-close drift branch or `-delta(close,3)` | `close` | 200 | conditional |
| `wq101_alpha46` | 20/10-bar close slope state with `-delta(close,1)` fallback | `close` | 21 | conditional |
| `wq101_alpha49` | close slope state with `-0.1` threshold or `-delta(close,1)` | `close` | 21 | conditional |
| `wq101_alpha51` | close slope state with `-0.05` threshold or `-delta(close,1)` | `close` | 21 | conditional |

All five are single-symbol formulas. No taxonomy, cap, taker, funding, or
industry-neutralization input is required.

## Resource Note

The first candidate set included rank-heavy formulas (`wq101_alpha7`,
`wq101_alpha35`, `wq101_alpha43`). They were not included in this batch because
the current per-symbol rolling-rank path made factor-value generation too slow
for a controlled 15GB-machine batch. Those formulas should be revisited as a
separate rank-heavy batch after profiling/optimizing the rolling-rank path and
post-intake redundancy stages.

The final batch uses close/high slope-state formulas that completed factor-value
generation quickly while still moving Alpha101 coverage forward.

## Validation

Commands run:

```bash
python -m py_compile scripts/factor_ops.py scripts/factor_formula_registry.py scripts/build_factor_bilingual_cards.py scripts/build_factor_values.py
.venv/bin/python -m pytest tests/unit/test_factor_ops.py tests/unit/test_public_alpha101_ohlcv_batch02.py tests/unit/test_public_alpha101_ohlcv_batch01.py tests/unit/test_public_factor_candidate_manifest.py -q
.venv/bin/python scripts/build_factor_values.py --factor-ids wq101_alpha23,wq101_alpha24,wq101_alpha46,wq101_alpha49,wq101_alpha51
.venv/bin/python scripts/run_factor_intake.py --factor-ids wq101_alpha23 wq101_alpha24 wq101_alpha46 wq101_alpha49 wq101_alpha51 --run-id public_alpha101_ohlcv_batch02_20260628
.venv/bin/python scripts/build_factor_bilingual_cards.py
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids wq101_alpha23,wq101_alpha24,wq101_alpha46,wq101_alpha49,wq101_alpha51
.venv/bin/python scripts/run_post_intake_workflow_completion.py --factor-ids wq101_alpha23,wq101_alpha24,wq101_alpha46,wq101_alpha49,wq101_alpha51 --start-from scorecard
```

Results:

- Factor values computed for all 5 factors.
- Coverage: `wq101_alpha23` 99.848%, `wq101_alpha24` 98.404%,
  `wq101_alpha46` 99.840%, `wq101_alpha49` 99.840%,
  `wq101_alpha51` 99.840%.
- Intake run `public_alpha101_ohlcv_batch02_20260628`: COMPLETE.
- Intake conclusion cards: 3 `CONDITIONAL_DIRECTION_REVIEW`,
  2 `REDUNDANT_WITH_EXISTING`.
- Post-intake state: 180 registered, 180 computed, 0 missing factor values,
  0 missing inputs.
- Factor evaluation page QA: 112 PASS / 0 FAIL.
- Post-intake integrity QA for the 5 new factors: 115 PASS / 0 FAIL /
  5 WARN.
- Public manifest status after refresh: Alpha101 25 total,
  19 accounted/non-skipped, 6 skipped taxonomy-blocked; Alpha158 101 total,
  95 accounted/non-skipped, 6 skipped duplicates.

The warnings are optional overlapping-sleeve diagnostics, not missing factor
values, missing source metadata, page coverage failures, or core workflow
failures.

## Batch Scaling Note

Future batches can include more factors when they share the same lightweight
compute profile. Rank-heavy formulas and formulas that require new panel
operators should be grouped separately and profiled before intake. The largest
post-intake cost observed in this batch was the incremental pairwise redundancy
matrix stage (~412s), not factor-value generation.
