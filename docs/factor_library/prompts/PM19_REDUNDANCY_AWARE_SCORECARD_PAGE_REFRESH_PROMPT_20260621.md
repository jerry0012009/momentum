# PM-19 Prompt — Redundancy-Aware Scorecard Calibration and Page Refresh

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-18:

- `docs/factor_library/audits/pm18_full_pairwise_redundancy_matrix.md`
- `scripts/build_factor_pairwise_redundancy_matrix.py`
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_pairwise_redundancy.csv`
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_summary.csv`
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_clusters.csv`
- refreshed `factor_quality_scorecard.csv/json/manifest`

PM-18 successfully produced full pairwise redundancy coverage: 2485/2485 pairs. However, the PM-18 audit also shows a likely over-conservative scorecard confidence effect: score confidence HIGH dropped to 0 because all factors have some insufficient-overlap pairs. That is not the right product interpretation. A factor should not be globally penalized merely because a subset of its pairs has insufficient overlap.

PM-19 should calibrate redundancy confidence and then refresh the existing factor-evaluation page with redundancy-aware scorecard information.

## 0. PM objective

1. Calibrate redundancy confidence logic in the scorecard.
2. Refresh `factor_quality_scorecard.csv/json/manifest`.
3. Rebuild existing `factor-evaluation.html` so the page displays redundancy/novelty evidence from PM-18.

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

Do **not** blindly propagate the PM-18 scorecard confidence drop without reviewing the redundancy-confidence logic.

## 2. Inputs

Use PM-18 outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_pairwise_redundancy.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_clusters.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_matrix_spearman.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_matrix_pearson.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_pairwise_redundancy_manifest.json
```

Use scorecard/page inputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard_manifest.json
scripts/build_factor_quality_scorecard.py
scripts/_build_factor_eval_html.py
reports/site/factor-library/factor-evaluation.html
```

## 3. Required correction: redundancy confidence calibration

Update `scripts/build_factor_quality_scorecard.py` so redundancy confidence is based on useful valid-pair coverage and nearest redundancy evidence, not on whether *any* pair has insufficient overlap.

Suggested fields to add to `factor_quality_scorecard.csv`:

```text
valid_redundancy_pair_count
expected_redundancy_pair_count
valid_redundancy_pair_coverage
insufficient_overlap_pair_count
nearest_factor
nearest_abs_spearman_corr
strongest_redundancy_level
novelty_assessment
redundancy_cluster_id
redundancy_cluster_size
```

Suggested confidence logic:

```text
HIGH: valid_redundancy_pair_coverage >= 0.70 and n_valid_pairs >= 40
MEDIUM: valid_redundancy_pair_coverage >= 0.40 and n_valid_pairs >= 20
LOW: otherwise
```

Also allow confidence to be MEDIUM/HIGH if a factor has clear high-redundancy evidence, even if some unrelated pairs have insufficient overlap.

Do not overclaim uniqueness. If nearest redundancy is high, novelty assessment should reflect that.

## 4. Required scorecard refresh

Rerun:

```bash
python scripts/build_factor_quality_scorecard.py
```

Regenerate:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard_manifest.json
```

Audit class/confidence distribution before vs after calibration.

## 5. Required page refresh

Update existing builder:

```text
scripts/_build_factor_eval_html.py
```

Regenerate existing page:

```text
reports/site/factor-library/factor-evaluation.html
```

Add redundancy-aware display.

### 5.1 Main table additions

Add or expose columns/fields:

```text
Novelty / 新颖性
Nearest factor / 最近相似因子
Redundancy / 冗余等级
Redundancy confidence / 冗余置信度
Cluster / 聚类
```

Keep the existing scorecard and diagnostics columns.

### 5.2 Detail panel additions

Add a section:

```text
Redundancy & Novelty / 冗余与新颖性
```

Show:

- nearest factor;
- nearest abs Spearman;
- strongest redundancy level;
- novelty assessment;
- redundancy confidence;
- valid pair coverage;
- cluster id / cluster size / cluster members if available;
- explanation that redundancy is a research similarity diagnostic, not a reason by itself to delete a factor.

### 5.3 Top summary additions

Show:

- number of NEAR_DUPLICATE pairs;
- number of HIGH_REDUNDANCY pairs;
- number of clusters;
- largest cluster size;
- scorecard class/confidence distribution after calibration.

## 6. Required audit note

Create:

```text
docs/factor_library/audits/pm19_redundancy_aware_scorecard_page_refresh.md
```

Audit must include:

1. Summary verdict:
   - `REDUNDANCY_AWARE_PAGE_REFRESH_PASS`
   - `REDUNDANCY_AWARE_PAGE_REFRESH_PASS_WITH_LIMITATIONS`
   - `REDUNDANCY_AWARE_PAGE_REFRESH_BLOCKED`
2. Files changed/generated.
3. Explanation of confidence calibration change.
4. Scorecard class distribution before vs after PM-19 calibration.
5. Score confidence distribution before vs after PM-19 calibration.
6. Redundancy confidence distribution after calibration.
7. Number of factors whose confidence changed.
8. Top 20 most redundant pairs, actually filled from `factor_pairwise_redundancy.csv` (not placeholder text).
9. Page features added.
10. Validation results.
11. Limitations.
12. Non-change statement: no factors, formulas, factor_values, signal panel.
13. Recommended next PM.

## 7. Validation

Run:

```bash
python -m py_compile scripts/build_factor_quality_scorecard.py scripts/_build_factor_eval_html.py
python scripts/build_factor_quality_scorecard.py
python scripts/_build_factor_eval_html.py
```

Then:

```bash
python - <<'PY'
import pandas as pd
from pathlib import Path
base = Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics')
score = pd.read_csv(base / 'factor_quality_scorecard.csv')
red = pd.read_csv(base / 'factor_pairwise_redundancy.csv')
summary = pd.read_csv(base / 'factor_redundancy_summary.csv')
print('score rows', len(score), 'factors', score['factor_id'].nunique())
print('pair rows', len(red))
print('redundancy confidence')
print(score['redundancy_confidence'].value_counts(dropna=False))
print('score confidence')
print(score['score_confidence'].value_counts(dropna=False))
html = Path('reports/site/factor-library/factor-evaluation.html').read_text(encoding='utf-8')
checks = [
  'Redundancy & Novelty',
  '冗余与新颖性',
  'nearest_factor',
  'novelty_assessment',
  'redundancy_confidence',
  'cluster',
  'NEAR_DUPLICATE',
  'HIGH_REDUNDANCY',
]
for c in checks:
    print(c, c in html)
PY
```

Expected:

- score rows = 71;
- pair rows = 2485;
- HTML contains redundancy/novelty section;
- final page remains under a reasonable size, preferably < 2MB.

## 8. Allowed files to change

Allowed code:

```text
scripts/build_factor_quality_scorecard.py
scripts/_build_factor_eval_html.py
```

Allowed outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard_manifest.json
reports/site/factor-library/factor-evaluation.html
reports/site/factor-library/assets/factor_diagnostics_payload.json
```

Allowed audit:

```text
docs/factor_library/audits/pm19_redundancy_aware_scorecard_page_refresh.md
```

Do not modify other public pages unless required for broken navigation, and document it if done.

## 9. Stop conditions

Stop and report if:

- scorecard cannot join redundancy summary for 71 factors;
- confidence calibration would require changing factor formulas or factor_values;
- page build breaks existing scorecard/diagnostic sections;
- page size becomes unreasonably large;
- redundancy fields are too sparse to display honestly.

## 10. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
feat: refresh factor page with redundancy-aware scorecard
```

Final response should include:

- commit hash
- summary verdict
- confidence calibration summary
- scorecard class/confidence changes
- redundancy confidence distribution
- page features added
- validation results
- limitations
- recommended next PM
