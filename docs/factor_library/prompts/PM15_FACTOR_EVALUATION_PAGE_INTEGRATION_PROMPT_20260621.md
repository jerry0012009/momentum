# PM-15 Prompt — Integrate Diagnostics Metrics and Bilingual Cards into Existing Factor Evaluation Page

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-14B:

- `docs/factor_library/audits/pm14b_factor_card_review_polish.md`
- `scripts/build_factor_bilingual_cards.py`
- `research/factor_runs/crypto_top50_factor_library/factor_metadata/`

It also depends on PM-13B diagnostics outputs:

- `docs/factor_library/audits/pm13b_period_quantile_diagnostics.md`
- `scripts/evaluate_factors.py`
- `scripts/build_factor_diagnostics_metrics.py`
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/`

PM-13B completed the quantitative diagnostics layer. PM-14B completed the bilingual factor-card metadata layer with review flags.

Now PM-15 should upgrade the existing factor evaluation page so the factor library becomes readable, navigable, and decision-oriented.

## 0. PM objective

Upgrade the existing static page:

```text
reports/site/factor-library/factor-evaluation.html
```

by modifying the existing page builder:

```text
scripts/_build_factor_eval_html.py
```

The page should consume:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_diagnostics_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_monthly_ic_series.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_monthly_long_short_series.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_cumulative_long_short_curve.csv
research/factor_runs/crypto_top50_factor_library/factor_metadata/factor_bilingual_cards.csv
research/factor_runs/crypto_top50_factor_library/factor_metadata/factor_card_qa_report.csv
```

Do **not** create a random new HTML page. PM-15 must upgrade the existing factor-evaluation page.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify `scripts/factor_formula_registry.py`.

Do **not** modify `scripts/factor_ops.py`.

Do **not** modify signal panel construction.

Do **not** rebuild signal panel.

Do **not** create a new public page unless the existing builder requires a small asset file. The canonical page remains:

```text
reports/site/factor-library/factor-evaluation.html
```

Do **not** use external CDN dependencies.

Do **not** make production/live/tradeability/alpha claims.

Do **not** hide metadata review flags. If a card is `DIRECTION_AMBIGUOUS`, `NEEDS_REVIEW`, or `FORMULA_AMBIGUOUS`, display that clearly.

## 2. Repository structure to respect

Existing builder:

```text
scripts/_build_factor_eval_html.py
```

Existing page:

```text
reports/site/factor-library/factor-evaluation.html
```

Existing site entry pages:

```text
reports/site/factor-library/index.html
reports/site/factor-library/actual-script-map.html
reports/site/factor-library/signal-evaluation-summary.html
```

Do not change the site architecture in PM-15.

## 3. Required pre-checks

Run:

```bash
git status --short
```

Inspect schemas:

```bash
python - <<'PY'
import pandas as pd
from pathlib import Path
paths = [
 'research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_diagnostics_summary.csv',
 'research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_monthly_ic_series.csv',
 'research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_monthly_long_short_series.csv',
 'research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_cumulative_long_short_curve.csv',
 'research/factor_runs/crypto_top50_factor_library/factor_metadata/factor_bilingual_cards.csv',
 'research/factor_runs/crypto_top50_factor_library/factor_metadata/factor_card_qa_report.csv',
]
for p in paths:
    p = Path(p)
    print('\n', p, p.exists())
    if p.exists():
        df = pd.read_csv(p)
        print('rows=', len(df))
        print('cols=', list(df.columns))
        for c in ['factor_id','factor_name']:
            if c in df.columns:
                print('n_factors=', df[c].nunique())
PY
```

Verify expected minimums:

- diagnostics summary: 71 factors;
- bilingual cards: 71 factors;
- monthly IC series: non-empty;
- monthly long-short series: non-empty;
- cumulative long-short curve: non-empty.

If any core input is missing, stop and report.

## 4. Required page behavior

The upgraded `factor-evaluation.html` should remain static and interactive, with no backend.

It should include:

### 4.1 Top summary section

Show:

- factor count: 71;
- horizons: 1h / 4h / 24h / 72h;
- months covered;
- number of COMPLETE / DIRECTION_AMBIGUOUS / NEEDS_REVIEW / FORMULA_AMBIGUOUS cards;
- explanation that this is research diagnostics, not production trading advice.

### 4.2 Main factor table

Each row should show at least:

```text
factor_id
name_zh / name_en
family
metadata_quality
best_horizon
rankic_mean or best adjusted IC
rankic_ir
monthly_ic_positive_rate
long_short_sharpe
long_short_annualized_return
long_short_max_drawdown
long_short_positive_month_rate
coverage_rate
decision_bucket or recommended_action
```

Include basic filters/search:

- factor_id/name search;
- family filter;
- metadata_quality filter;
- best_horizon filter;
- sort by Sharpe / IC / drawdown / coverage.

### 4.3 Factor detail panel

When a user selects a factor, show:

- name_zh / name_en;
- formula_zh / formula_en;
- intuition_zh / intuition_en;
- expected direction and direction explanation;
- known limitations;
- data source type;
- metadata quality and QA notes;
- best horizon metrics;
- horizon-level metrics table;
- monthly IC mini-chart;
- monthly long-short mini-chart;
- cumulative long-short curve;
- drawdown summary.

### 4.4 Charts

Charts can be lightweight SVG/canvas generated from embedded JSON or a local asset file.

No external chart library.

Minimum acceptable chart implementation:

- monthly IC line or bar chart;
- monthly long-short return bar chart;
- cumulative long-short line chart.

If full charting is too heavy, use compact SVG sparkline-style charts, but they must be readable.

### 4.5 Bilingual display

Default display may be Chinese-first, with English secondary.

Do not remove English fields.

Show review flags honestly. For example:

- `DIRECTION_AMBIGUOUS`: display as “方向依赖市场状态 / Direction regime-dependent”.
- `NEEDS_REVIEW`: display as “需要人工复核 / Requires review”.
- `FORMULA_AMBIGUOUS`: display as “公式/方向需要复核 / Formula or direction needs review”.

## 5. Implementation requirements

Modify:

```text
scripts/_build_factor_eval_html.py
```

It may generate an optional local payload file under:

```text
reports/site/factor-library/assets/factor_diagnostics_payload.json
```

if embedding all data directly into HTML becomes messy.

Either approach is acceptable:

1. Embed data in HTML for simplicity; or
2. Write local JSON asset and have the page load it.

But do not use remote dependencies and do not require a backend.

## 6. Validation requirements

Run:

```bash
python -m py_compile scripts/_build_factor_eval_html.py
python scripts/_build_factor_eval_html.py
```

Then verify output file exists and contains expected terms:

```bash
python - <<'PY'
from pathlib import Path
p = Path('reports/site/factor-library/factor-evaluation.html')
text = p.read_text(encoding='utf-8')
checks = [
    'Sharpe',
    '夏普',
    '最大回撤',
    'Monthly IC',
    '月度IC',
    'Long-Short',
    '多空',
    'DIRECTION_AMBIGUOUS',
    'NEEDS_REVIEW',
]
print('exists', p.exists(), 'size', p.stat().st_size if p.exists() else None)
for c in checks:
    print(c, c in text)
PY
```

Also run a small static sanity check:

```bash
python - <<'PY'
import pandas as pd
cards = pd.read_csv('research/factor_runs/crypto_top50_factor_library/factor_metadata/factor_bilingual_cards.csv')
diag = pd.read_csv('research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_diagnostics_summary.csv')
print('cards', cards['factor_id'].nunique())
print('diag', diag['factor_id'].nunique())
print('join', cards.merge(diag, on='factor_id', how='inner')['factor_id'].nunique())
PY
```

Expected join count: 71.

## 7. Required audit note

Create:

```text
docs/factor_library/audits/pm15_factor_evaluation_page_integration.md
```

The audit note must include:

1. Summary verdict:
   - `FACTOR_EVAL_PAGE_INTEGRATION_PASS`
   - `FACTOR_EVAL_PAGE_INTEGRATION_PASS_WITH_LIMITATIONS`
   - `FACTOR_EVAL_PAGE_INTEGRATION_BLOCKED`
2. Files changed/generated.
3. Inputs consumed.
4. Whether existing page was upgraded rather than a new page created.
5. Factor count coverage.
6. Metadata quality distribution shown on page.
7. Diagnostics metrics shown on page.
8. Chart types implemented.
9. Validation results.
10. Known limitations.
11. Non-change statement: no factors, no formulas, no factor_values, no signal panel.
12. Recommended next PM.

## 8. Allowed files to change

Allowed code:

```text
scripts/_build_factor_eval_html.py
```

Allowed public output:

```text
reports/site/factor-library/factor-evaluation.html
reports/site/factor-library/assets/factor_diagnostics_payload.json
```

Allowed audit:

```text
docs/factor_library/audits/pm15_factor_evaluation_page_integration.md
```

Do not edit other public pages unless absolutely necessary for a broken link, and if so document it.

## 9. Stop conditions

Stop and report if:

- factor metadata and diagnostics cannot be joined to 71 factors;
- required diagnostics files are missing;
- the page builder cannot be updated without creating a separate route/page;
- charting requires external dependencies;
- implementing the page would require changing formulas, signals, or data outputs.

## 10. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
feat: integrate factor diagnostics into evaluation page
```

Final response should include:

- commit hash
- summary verdict
- whether existing factor-evaluation.html was upgraded
- files changed/generated
- factor count coverage
- chart types implemented
- metadata quality distribution displayed
- validation results
- limitations
- recommended next PM
