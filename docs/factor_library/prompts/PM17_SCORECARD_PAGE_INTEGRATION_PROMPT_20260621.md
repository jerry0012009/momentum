# PM-17 Prompt — Integrate Factor Quality Scorecard into Existing Factor Evaluation Page

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-16B:

- `docs/factor_library/audits/pm16b_factor_quality_scorecard.md`
- `scripts/build_factor_quality_scorecard.py`
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.csv`
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.json`
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard_manifest.json`

PM-16B built a deterministic factor quality scorecard for 71 factors. PM-17 should integrate this scorecard into the existing factor evaluation page.

## 0. PM objective

Upgrade the existing page:

```text
reports/site/factor-library/factor-evaluation.html
```

by modifying the existing builder:

```text
scripts/_build_factor_eval_html.py
```

The page should show the factor quality scorecard as a first-class decision layer while preserving the existing detailed diagnostics, charts, bilingual factor cards, and caveats.

Do **not** create a new page.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify `scripts/factor_formula_registry.py`.

Do **not** modify `scripts/factor_ops.py`.

Do **not** modify signal panel construction.

Do **not** rebuild signal panel.

Do **not** create a new public page.

Do **not** use external CDN dependencies.

Do **not** make production/live/tradeability/alpha claims.

Do **not** present `STRONG_RESEARCH_CANDIDATE` as a trading recommendation. It means research triage only.

## 2. Required inputs

Existing factor page inputs remain:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_diagnostics_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_monthly_ic_series.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_monthly_long_short_series.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_cumulative_long_short_curve.csv
research/factor_runs/crypto_top50_factor_library/factor_metadata/factor_bilingual_cards.csv
research/factor_runs/crypto_top50_factor_library/factor_metadata/factor_card_qa_report.csv
```

Add scorecard input:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard_manifest.json
```

## 3. Required page changes

### 3.1 Top summary section

Add scorecard summary cards:

- final quality class distribution;
- confidence distribution;
- count of strong research candidates;
- count of review-required factors;
- prominent caveat: redundancy confidence is LOW for most factors until PM-18.

### 3.2 Main factor table

Add or revise table columns:

```text
Quality Class 质量分类
Score 分数
Confidence 置信度
Main Action 建议动作
```

Keep existing metrics such as RankIC, ICIR, Sharpe, max drawdown, coverage, and metadata quality.

Add filters:

- final_quality_class filter;
- score_confidence filter;
- existing family / metadata quality / horizon filters should remain.

Default sort:

```text
final_quality_score descending
```

but make it clear this is a research score, not a trading score.

### 3.3 Factor detail panel

Add a dedicated section:

```text
Factor Quality Scorecard / 因子质量记分卡
```

Show:

- final_quality_class;
- final_quality_score;
- score_confidence;
- recommended_next_action;
- main_strengths_zh / main_strengths_en;
- main_weaknesses_zh / main_weaknesses_en;
- review_notes_zh / review_notes_en.

Show sub-scores as a compact visual grid or small bar set:

```text
computation_integrity_score
predictive_ranking_score
portfolio_extraction_score
stability_score
quantile_shape_score
direction_interpretability_score
redundancy_novelty_score
```

Do not use external chart libraries. Plain CSS bars or inline SVG are acceptable.

### 3.4 Caveats and interpretation

Add visible explanation:

- `STRONG_RESEARCH_CANDIDATE` means strong research evidence, not deployable strategy.
- `PROMISING_BUT_INCONSISTENT` means evidence is meaningful but mixed.
- `REVIEW_REQUIRED` means metadata/formula/direction needs review before quality judgment.
- Score confidence may be capped by sparse redundancy coverage.

### 3.5 Preserve existing page value

Do not remove:

- bilingual factor cards;
- formula / intuition / limitations;
- monthly IC chart;
- monthly LS chart;
- cumulative LS curve;
- Sharpe/drawdown metrics;
- quality badges;
- direction badges.

## 4. Required implementation approach

Modify:

```text
scripts/_build_factor_eval_html.py
```

Join scorecard data by `factor_id` with the existing payload.

If fields overlap, use scorecard fields only for scorecard-specific concepts:

- final_quality_class;
- final_quality_score;
- score_confidence;
- sub-scores;
- strengths/weaknesses/review notes;
- recommended_next_action.

Do not overwrite the underlying diagnostic metrics unless explicitly needed.

## 5. Validation

Run:

```bash
python -m py_compile scripts/_build_factor_eval_html.py
python scripts/_build_factor_eval_html.py
```

Then validate:

```bash
python - <<'PY'
from pathlib import Path
import pandas as pd
score = pd.read_csv('research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.csv')
print('score rows', len(score), 'factors', score['factor_id'].nunique())
html = Path('reports/site/factor-library/factor-evaluation.html').read_text(encoding='utf-8')
checks = [
  'Factor Quality Scorecard',
  '因子质量记分卡',
  'STRONG_RESEARCH_CANDIDATE',
  'PROMISING_BUT_INCONSISTENT',
  'REVIEW_REQUIRED',
  'final_quality_score',
  'score_confidence',
  'redundancy confidence',
  '冗余',
  '不是交易建议',
]
for c in checks:
    print(c, c in html)
PY
```

Expected:

- score rows = 71;
- factor_id unique = 71;
- HTML contains scorecard text and quality classes.

## 6. Required audit note

Create:

```text
docs/factor_library/audits/pm17_scorecard_page_integration.md
```

The audit note must include:

1. Summary verdict:
   - `SCORECARD_PAGE_INTEGRATION_PASS`
   - `SCORECARD_PAGE_INTEGRATION_PASS_WITH_LIMITATIONS`
   - `SCORECARD_PAGE_INTEGRATION_BLOCKED`
2. Files changed/generated.
3. Confirmation existing `factor-evaluation.html` was upgraded, not replaced by a new page.
4. Scorecard input coverage: 71/71.
5. Page features added.
6. Filters/sorting added.
7. Validation results.
8. Known limitations.
9. Non-change statement: no factors, no formulas, no factor_values, no signal panel.
10. Recommended next PM.

## 7. Allowed files to change

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
docs/factor_library/audits/pm17_scorecard_page_integration.md
```

Do not edit other public pages unless a broken link requires it, and document any such change.

## 8. Stop conditions

Stop and report if:

- scorecard cannot join to current page payload at 71 factors;
- adding scorecard breaks existing monthly charts;
- page size becomes unreasonably large or browser performance becomes poor;
- integrating scorecard requires changing formulas, factor_values, or signals.

## 9. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
feat: integrate factor scorecard into evaluation page
```

Final response should include:

- commit hash
- summary verdict
- confirmation existing page was upgraded
- scorecard coverage
- features added
- validation results
- limitations
- recommended next PM
