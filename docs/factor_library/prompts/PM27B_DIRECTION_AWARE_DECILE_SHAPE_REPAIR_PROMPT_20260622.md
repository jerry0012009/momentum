# PM-27B Prompt — Direction-Aware Decile Shape Repair

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-27:

- `docs/factor_library/audits/pm27_decile_quantile_shape_diagnostics.md`
- `scripts/build_factor_decile_shape_diagnostics.py`
- decile outputs in `factor_diagnostics/`

PM-27 generated useful decile diagnostics, but its audit explicitly states:

> No direction metadata used — decile ordering is raw (D1=lowest factor value, D10=highest).

This is not sufficient for page integration because the repository has explicit `FactorSpec.expected_direction` metadata. Direction-aware interpretation is required before we display decile shape as a factor quality signal.

Do **not** update public HTML in PM-27B.

## 0. PM objective

Repair decile shape diagnostics so monotonicity, spread, tail dependence, and shape classes are computed in **expected-direction order** when direction metadata is available.

A high-quality factor evaluation system must distinguish:

- raw decile order: D1 = lowest factor value, D10 = highest factor value;
- expected-direction order: D10-equivalent bucket should represent the expected best return side.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify signal panel construction.

Do **not** create or modify public HTML pages.

Do **not** enter signal evaluation.

Do **not** make production/live/trading claims.

Do **not** silently overwrite direction information using observed returns.

## 2. Required direction source

Use registry/domain metadata:

```text
scripts/factor_formula_registry.py
scripts/factor_specs.py
```

`FactorSpec.expected_direction` should be used. It may be:

```text
positive
negative
conditional
```

Do not infer expected_direction from realized performance.

## 3. Direction-aware decile convention

Keep raw decile identity, but add expected-direction ordering.

Recommended convention:

```text
raw_decile: 1..10
expected_order_decile: 1..10
```

For `expected_direction == positive`:

```text
expected_order_decile = raw_decile
```

For `expected_direction == negative`:

```text
expected_order_decile = 11 - raw_decile
```

For `expected_direction == conditional` or missing:

```text
expected_order_decile = raw_decile
direction_handling = raw_order_conditional
```

The audit must report how many factor-horizon pairs use each direction handling mode.

## 4. Required script repair

Modify:

```text
scripts/build_factor_decile_shape_diagnostics.py
```

The script must:

1. Load `expected_direction` per factor from registry metadata.
2. Preserve raw decile return data.
3. Compute direction-aware spread, slope, Spearman, monotonicity, tail concentration, U-shape, and nonlinearity.
4. Include `expected_direction` and `direction_handling` in all relevant outputs.
5. Mark conditional factors explicitly rather than pretending they are positive or negative.

Do not modify `evaluate_factors.py` unless absolutely necessary.

## 5. Required outputs to regenerate

Regenerate existing PM-27 outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_decile_return_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_decile_shape_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_decile_shape_summary.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_decile_shape_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_decile_shape_manifest.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_decile_shape_timeseries.csv
```

## 6. Required schema additions

`factor_decile_return_summary.csv` should include at minimum:

```text
factor_id
horizon
month
raw_decile
expected_order_decile
expected_direction
direction_handling
mean_return
median_return
n_obs
```

If preserving the old `decile` column is useful for compatibility, keep it as alias for `raw_decile`, but avoid ambiguity in the audit.

`factor_decile_shape_summary.csv` should include at minimum:

```text
factor_id
horizon
expected_direction
direction_handling
n_months
n_deciles
expected_d1_return
expected_d2_return
expected_d3_return
expected_d4_return
expected_d5_return
expected_d6_return
expected_d7_return
expected_d8_return
expected_d9_return
expected_d10_return
expected_d10_minus_d1_spread
expected_d10_minus_d1_positive_month_rate
direction_aware_slope
direction_aware_spearman_corr
direction_aware_monotonicity_score
direction_aware_monotonicity_class
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

Payload should expose both raw and direction-aware series compactly for later PM-28 page integration.

## 7. Required comparison with PM-27 raw version

If possible, compare old raw-order PM-27 classifications with direction-aware PM-27B classifications before overwriting.

If the old file is already overwritten, document that comparison is unavailable.

At minimum audit:

```text
raw_order_class_distribution_before_if_available
direction_aware_class_distribution_after
n_class_changed_if_available
```

## 8. Dynamic coverage requirements

Use expected factor count from `factor_library_state.json` or registry. Do not hardcode 71.

Audit must report:

```text
expected_factor_count
expected_factor_horizon_pairs
actual_factor_count
actual_factor_horizon_pairs
missing_factor_ids
missing_horizons
expected_direction_distribution
direction_handling_distribution
```

Do not silently drop factors. Mark insufficient data explicitly.

## 9. Required audit

Create:

```text
docs/factor_library/audits/pm27b_direction_aware_decile_shape_repair.md
```

Audit must include:

1. Summary verdict:
   - `DIRECTION_AWARE_DECILE_REPAIR_PASS`
   - `DIRECTION_AWARE_DECILE_REPAIR_PASS_WITH_LIMITATIONS`
   - `DIRECTION_AWARE_DECILE_REPAIR_BLOCKED`
2. Why PM-27B was required before page integration.
3. Evidence that `FactorSpec.expected_direction` is used.
4. Files changed.
5. Factor/horizon coverage.
6. Expected direction distribution.
7. Direction handling distribution.
8. Direction-aware decile shape class distribution.
9. Tail concentration distribution.
10. Consistency distribution versus PM-26 Q5 shape.
11. Examples where direction-aware analysis changes interpretation.
12. Payload size.
13. Validation results.
14. Limitations.
15. Non-change statement: no factors, formulas, factor_values, signal panel, public page.
16. Recommended next PM: PM-28 page integration for quantile/rolling/direction-aware decile diagnostics.

## 10. Validation

Run:

```bash
python -m py_compile scripts/build_factor_decile_shape_diagnostics.py
python scripts/build_factor_decile_shape_diagnostics.py
```

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
print('expected direction distribution')
print(shape['expected_direction'].value_counts(dropna=False).to_string())
print('direction handling distribution')
print(shape['direction_handling'].value_counts(dropna=False).to_string())
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

## 11. Allowed files to change

Allowed script:

```text
scripts/build_factor_decile_shape_diagnostics.py
```

Allowed regenerated outputs:

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
docs/factor_library/audits/pm27b_direction_aware_decile_shape_repair.md
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

## 12. Stop conditions

Stop and report if:

- expected_direction cannot be loaded from registry;
- raw deciles cannot be mapped to expected-order deciles;
- factor/horizon coverage is materially reduced;
- implementation would require modifying factor formulas, factor_values, or signal panel;
- direction-aware output becomes too large for repository use.

## 13. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
fix: make decile shape diagnostics direction-aware
```

Final response should include:

- commit hash
- summary verdict
- evidence expected_direction is used
- factor/horizon coverage
- direction handling distribution
- direction-aware decile shape distribution
- examples of changed interpretation
- validation results
- limitations
- recommended next PM
