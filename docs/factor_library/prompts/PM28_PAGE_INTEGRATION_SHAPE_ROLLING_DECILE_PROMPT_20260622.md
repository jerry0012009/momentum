# PM-28 Prompt — Page Integration for Shape, Rolling Stability, and Direction-Aware Deciles

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows:

- PM-26: Q1–Q5 quantile shape + rolling stability diagnostics
- PM-27: raw decile-level quantile diagnostics
- PM-27B: direction-aware decile repair using `FactorSpec.expected_direction`

Now the factor evaluation data layer has Q5 shape, rolling stability, and direction-aware decile diagnostics. PM-28 should integrate these into the existing `factor-evaluation.html` page.

Do **not** compute new diagnostics in PM-28. This is page integration only.

## 0. PM objective

Update the existing factor-evaluation page so each factor detail panel can show:

1. Q1–Q5 quantile shape diagnostics;
2. rolling 3M / 6M IC and long-short stability;
3. direction-aware D1–D10 decile shape diagnostics;
4. consistency / conflict between Q5 and decile-level shape;
5. concise notes explaining whether the factor is monotonic, nonlinear, tail-dependent, unstable, or recently deteriorating.

This strengthens factor evaluation before capacity/liquidity diagnostics, factor expansion, or signal construction.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify signal panel construction.

Do **not** recompute PM-26 or PM-27B diagnostics.

Do **not** create a new public page.

Do **not** use external CDN dependencies.

Do **not** remove existing page sections.

Do **not** make production/live/trading claims.

## 2. Existing sections that must be preserved

The existing page must keep:

```text
Factor metadata / formula / bilingual cards
Factor Quality Scorecard
Redundancy & novelty
Single-Factor Paper Portfolio
Corrected paper NAV
Paper drawdown
Long / short leg decomposition
Turnover
Fee sensitivity
BTC / Market Regime Diagnostics
```

Do not regress PM-21B through PM-27B results.

## 3. Required inputs

Use existing compact payloads and summaries:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_shape_stability_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quantile_shape_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_rolling_stability_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_shape_stability_timeseries.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_decile_shape_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_decile_shape_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_decile_return_summary.csv
```

Do not load excessive raw rows into the HTML. Prefer compact per-factor payloads.

If `factor_decile_return_summary.csv` is too large for direct HTML embedding, use `factor_decile_shape_payload.json` instead.

## 4. Required files to update

Update:

```text
scripts/_build_factor_eval_html.py
reports/site/factor-library/factor-evaluation.html
```

Optional if the existing build pattern uses it:

```text
reports/site/factor-library/assets/factor_diagnostics_payload.json
```

## 5. Required page additions

Add a new section in factor detail panel:

```text
Quantile Shape & Rolling Stability
分位收益形状与滚动稳定性
```

This section should include the following components.

### 5.1 Summary badges

For the selected factor, show:

```text
Q5 quantile_shape_class
rolling stability_class
direction-aware decile_shape_class
shape_consistency_with_q5
expected_direction
direction_handling
```

Use clear warnings for:

```text
UNSTABLE_SIGN_FLIP
REGIME_OR_PERIOD_DEPENDENT
FLAT_NO_SHAPE
NONLINEAR_MIXED
BOTH_TAILS_U_SHAPED
CONFLICTING
raw_order_conditional
```

### 5.2 Q1–Q5 shape chart

Show Q1–Q5 mean return curve or compact shape profile using PM-26 payload.

Display:

```text
q_low_return
q_high_return
q_spread_return
q_spearman_corr
monotonicity_score
tail_concentration_class
```

### 5.3 Direction-aware D1–D10 decile chart

Show expected-order D1–D10 return curve using PM-27B payload.

Required labels:

```text
Expected-order decile 1 = expected worst side
Expected-order decile 10 = expected best side
```

For negative factors, page should make clear that raw deciles were flipped by expected_direction.

For conditional factors, show caveat:

```text
Conditional expected direction — deciles shown in raw order.
```

### 5.4 Rolling stability chart

Show rolling 3M / 6M IC and/or long-short stability from PM-26 timeseries.

Prefer compact charts:

```text
rolling_ic_3m
rolling_ic_6m
rolling_ls_3m
rolling_ls_6m
```

If showing all four is too crowded, show IC by default and LS as a second compact chart or table.

### 5.5 Interpretation notes

Show bilingual notes from payload where available:

```text
main_shape_note_zh
main_shape_note_en
main_stability_note_zh
main_stability_note_en
main_decile_note_zh
main_decile_note_en
```

## 6. Top-level table / filters

If clean and not disruptive, add optional filter columns or dropdowns for:

```text
quantile_shape_class
stability_class
decile_shape_class
shape_consistency_with_q5
direction_handling
```

Do not overcomplicate the UI. Detail panel integration is more important than table complexity.

## 7. Size and performance constraints

Current page is around 2.08 MB. Keep final page preferably under 4 MB.

Do not embed the full 70k-row decile return CSV directly. Use compact payloads.

Avoid duplicating large JSON blobs if already available in a unified payload.

## 8. Validation

Run:

```bash
python -m py_compile scripts/_build_factor_eval_html.py
python scripts/_build_factor_eval_html.py
```

Then validate HTML:

```bash
python - <<'PY'
from pathlib import Path
html = Path('reports/site/factor-library/factor-evaluation.html').read_text(encoding='utf-8')
checks = [
    'Quantile Shape & Rolling Stability',
    '分位收益形状与滚动稳定性',
    'quantile_shape_class',
    'stability_class',
    'decile_shape_class',
    'shape_consistency_with_q5',
    'expected_direction',
    'direction_handling',
    'Expected-order decile',
    'Single-Factor Paper Portfolio',
    'BTC / Market Regime Diagnostics',
    '不是交易策略',
]
for c in checks:
    print(c, c in html)
print('html size bytes', len(html.encode('utf-8')))
PY
```

Also run:

```bash
python scripts/check_factor_library_staleness.py
```

If PM-25 monitor reports page stale before rebuild but clean after rebuild, mention in audit.

## 9. Required audit

Create:

```text
docs/factor_library/audits/pm28_shape_rolling_decile_page_integration.md
```

Audit must include:

1. Summary verdict:
   - `SHAPE_ROLLING_DECILE_PAGE_INTEGRATION_PASS`
   - `SHAPE_ROLLING_DECILE_PAGE_INTEGRATION_PASS_WITH_LIMITATIONS`
   - `SHAPE_ROLLING_DECILE_PAGE_INTEGRATION_BLOCKED`
2. Files changed.
3. Confirmation no new page was created.
4. Payloads consumed.
5. Confirmation Q5 shape appears.
6. Confirmation rolling stability appears.
7. Confirmation direction-aware decile appears.
8. Confirmation expected_direction / direction_handling appears.
9. Confirmation PM-22B paper charts preserved.
10. Confirmation PM-24B regime diagnostics preserved.
11. HTML size before/after.
12. Validation results.
13. Limitations.
14. Non-change statement: no factors, formulas, factor_values, signal panel.
15. Recommended next PM: PM-29 capacity/liquidity proxy diagnostics.

## 10. Allowed files to change

Allowed script:

```text
scripts/_build_factor_eval_html.py
```

Allowed page output:

```text
reports/site/factor-library/factor-evaluation.html
reports/site/factor-library/assets/factor_diagnostics_payload.json
```

Allowed audit:

```text
docs/factor_library/audits/pm28_shape_rolling_decile_page_integration.md
```

Do not modify:

```text
scripts/factor_formula_registry.py
scripts/factor_ops.py
scripts/build_factor_values.py
scripts/build_factor_shape_stability_diagnostics.py
scripts/build_factor_decile_shape_diagnostics.py
scripts/build_phase9b_signal_panel.py
```

## 11. Stop conditions

Stop and report if:

- PM-26 payload is missing;
- PM-27B payload is missing;
- direction-aware fields are missing;
- HTML would exceed acceptable size;
- integration would require recomputing diagnostics;
- existing paper/regime sections would be broken.

## 12. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
feat: add quantile and decile shape diagnostics to factor page
```

Final response should include:

- commit hash
- summary verdict
- sections added
- payloads consumed
- confirmation existing sections preserved
- HTML size
- validation results
- limitations
- recommended next PM
