# PM-27 Prompt — Decile-Level Quantile Shape Diagnostics

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows:

- PM-25: reusable staleness monitor + workflow reconciliation
- PM-26: Q1–Q5 quantile shape and rolling stability diagnostics

PM-26 passed, but its audit identified an important limitation: current quantile shape uses only 5 buckets. That is not enough to robustly distinguish monotonic factors from tail-only, U-shaped, or nonlinear factors.

PM-27 should add decile-level quantile analysis as a data-layer enhancement before page integration.

Do **not** update public HTML in PM-27.

## 0. PM objective

Add reusable **decile-level** factor return shape diagnostics.

The goal is to answer:

1. Does the factor show monotonic D1–D10 return ordering?
2. Is performance concentrated only in D1/D10 tails?
3. Is the return curve U-shaped, inverted, flat, or nonlinear?
4. Is D10–D1 spread stable across months?
5. Does decile shape confirm or contradict PM-26 Q1–Q5 shape classification?

This should strengthen factor evaluation before factor expansion or signal construction.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify signal panel construction.

Do **not** create or modify public HTML pages.

Do **not** enter signal evaluation.

Do **not** make production/live/trading claims.

Do **not** create a parallel factor-library workflow. Integrate with the existing diagnostics structure.

## 2. Required design choice

Inspect existing code before implementing:

```text
scripts/evaluate_factors.py
scripts/build_factor_shape_stability_diagnostics.py
scripts/run_factor_library_refresh.py
```

Choose the least risky implementation:

### Preferred option

If `evaluate_factors.py` can be cleanly extended to output decile returns without breaking existing Q1–Q5 outputs, add a decile output there or add a small companion function.

### Acceptable option

If modifying `evaluate_factors.py` is risky, create a new script that reads committed factor_values and labels and computes decile returns directly:

```text
scripts/build_factor_decile_shape_diagnostics.py
```

If using the acceptable option, document why it is not a parallel workflow but a diagnostics-layer extension.

Do not recompute factor_values.

## 3. Required inputs

Use canonical sources:

```text
research/factor_runs/crypto_top50_factor_library/factor_library_state.json
data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/*/factor_values.parquet
data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/labels.parquet
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quantile_shape_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_rolling_stability_summary.csv
```

Use horizons:

```text
1h, 4h, 24h, 72h
```

If labels for all horizons are not available in `labels.parquet`, inspect canonical label columns and use the same horizon naming as existing evaluator.

## 4. Required outputs

Write to:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/
```

Required outputs:

```text
factor_decile_return_summary.csv
factor_decile_shape_summary.csv
factor_decile_shape_summary.json
factor_decile_shape_payload.json
factor_decile_shape_manifest.json
```

Optional if useful:

```text
factor_decile_shape_timeseries.csv
```

Payload should be compact and suitable for PM-28 page integration.

## 5. Decile return summary schema

`factor_decile_return_summary.csv` should include:

```text
factor_id
horizon
month
decile
mean_return
median_return
n_obs
```

Deciles should be ordered in expected-direction order when direction metadata is available. If direction is uncertain, store raw decile order and flag it.

## 6. Decile shape summary schema

For each `factor_id` and `horizon`, compute:

```text
n_months
n_deciles
d1_return
d2_return
d3_return
d4_return
d5_return
d6_return
d7_return
d8_return
d9_return
d10_return
d10_minus_d1_spread
d10_minus_d1_positive_month_rate
decile_slope
decile_spearman_corr
decile_monotonicity_score
decile_monotonicity_class
tail_concentration_score
tail_concentration_class
middle_bucket_flatness
u_shape_score
nonlinearity_score
decile_shape_class
q5_shape_class_from_pm26
shape_consistency_with_q5
main_decile_note_zh
main_decile_note_en
```

Suggested class values:

```text
DECILE_MONOTONIC_STRONG
DECILE_MONOTONIC_WEAK
TOP_TAIL_DEPENDENT
BOTTOM_TAIL_DEPENDENT
BOTH_TAILS_U_SHAPED
NONLINEAR_MIXED
FLAT_NO_SHAPE
INSUFFICIENT_DATA
```

## 7. Tail diagnostics

Tail concentration should distinguish:

- signal mostly in D10 only;
- signal mostly in D1 only;
- both tails strong but middle weak;
- broadly monotonic across all deciles;
- no clear shape.

Use D1/D2/D9/D10 versus D4–D7 middle buckets.

## 8. Consistency with PM-26

Join with PM-26 `factor_quantile_shape_summary.csv` where possible.

For each factor/horizon, report whether decile-level shape agrees with Q1–Q5 shape:

```text
CONSISTENT
DECILE_MORE_MONOTONIC
DECILE_REVEALS_TAIL_DEPENDENCE
DECILE_REVEALS_NONLINEARITY
CONFLICTING
INSUFFICIENT_DATA
```

## 9. Dynamic coverage requirements

Use expected factor count from `factor_library_state.json` or registry. Do not hardcode 71.

Audit must report:

```text
expected_factor_count
expected_factor_horizon_pairs
actual_factor_count
actual_factor_horizon_pairs
missing_factor_ids
missing_horizons
```

Do not silently drop factors. Mark insufficient data explicitly.

## 10. Workflow integration

If implementation is a new script, add an optional stage to `scripts/run_factor_library_refresh.py` only if clean and small:

```text
shape-stability
```

or, if PM-26 already created a natural shape/stability stage name, extend that stage to include decile analysis.

If workflow integration is not clean, do not force it; document in the audit and recommend a future PM-25B/PM-31 integration.

Do not disturb existing `paper-diagnostics`, `paper-page-payload`, `regime`, `page`, or `staleness` stages.

## 11. Required audit

Create:

```text
docs/factor_library/audits/pm27_decile_quantile_shape_diagnostics.md
```

Audit must include:

1. Summary verdict:
   - `DECILE_SHAPE_DIAGNOSTICS_PASS`
   - `DECILE_SHAPE_DIAGNOSTICS_PASS_WITH_LIMITATIONS`
   - `DECILE_SHAPE_DIAGNOSTICS_BLOCKED`
2. Why PM-27 was needed after PM-26.
3. Implementation choice: evaluator extension or new diagnostics script.
4. Files changed.
5. Input files used.
6. Factor/horizon coverage.
7. Decile shape class distribution.
8. Tail concentration class distribution.
9. Consistency distribution versus PM-26 Q1–Q5 shape.
10. Examples where decile analysis confirms PM-26.
11. Examples where decile analysis reveals tail dependence or nonlinearity hidden by Q1–Q5.
12. Payload size.
13. Validation results.
14. Limitations.
15. Non-change statement: no factors, formulas, factor_values, signal panel, public page.
16. Recommended next PM: PM-28 page integration for quantile/rolling/decile diagnostics.

## 12. Validation

Run:

```bash
python -m py_compile scripts/build_factor_decile_shape_diagnostics.py
python scripts/build_factor_decile_shape_diagnostics.py
```

If you chose to modify `evaluate_factors.py`, run py_compile on it and validate that existing outputs are not broken.

Then:

```bash
python - <<'PY'
import json
import pandas as pd
from pathlib import Path
base = Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics')
ret = pd.read_csv(base / 'factor_decile_return_summary.csv')
shape = pd.read_csv(base / 'factor_decile_shape_summary.csv')
payload = json.loads((base / 'factor_decile_shape_payload.json').read_text(encoding='utf-8'))
print('return factors', ret['factor_id'].nunique())
print('shape factors', shape['factor_id'].nunique())
print('factor-horizon pairs', len(shape))
print('payload factors', len(payload.get('factors', [])))
print('decile shape classes')
print(shape['decile_shape_class'].value_counts(dropna=False).to_string())
if 'shape_consistency_with_q5' in shape.columns:
    print('consistency with q5')
    print(shape['shape_consistency_with_q5'].value_counts(dropna=False).to_string())
PY
```

Also run:

```bash
python scripts/check_factor_library_staleness.py
```

## 13. Allowed files to change

Allowed scripts:

```text
scripts/build_factor_decile_shape_diagnostics.py
scripts/evaluate_factors.py                    # only if necessary and safe
scripts/run_factor_library_refresh.py          # optional, small stage integration only
```

Allowed outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_decile_return_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_decile_shape_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_decile_shape_summary.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_decile_shape_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_decile_shape_manifest.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_decile_shape_timeseries.csv
```

Allowed audit:

```text
docs/factor_library/audits/pm27_decile_quantile_shape_diagnostics.md
```

Do not modify:

```text
reports/site/factor-library/factor-evaluation.html
scripts/_build_factor_eval_html.py
scripts/factor_formula_registry.py
scripts/factor_ops.py
scripts/build_factor_values.py
scripts/build_phase9b_signal_panel.py
```

## 14. Stop conditions

Stop and report if:

- factor_values or labels cannot support decile computation;
- horizon labels cannot be reconciled;
- outputs become too large;
- implementation would require formula/factor_values/signal changes;
- decile calculations cannot be made consistent with expected factor direction.

## 15. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
feat: add decile-level quantile shape diagnostics
```

Final response should include:

- commit hash
- summary verdict
- implementation choice
- factor/horizon coverage
- decile shape distribution
- q5 consistency distribution
- examples of newly revealed tail dependence/nonlinearity
- validation results
- limitations
- recommended next PM
