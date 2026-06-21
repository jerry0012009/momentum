# PM-18 Prompt — Full Pairwise Factor Redundancy Matrix

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-17:

- `docs/factor_library/audits/pm17_scorecard_page_integration.md`
- `scripts/build_factor_quality_scorecard.py`
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.csv`
- `reports/site/factor-library/factor-evaluation.html`

PM-17 integrated the factor quality scorecard into the existing factor-evaluation page. The largest remaining limitation is redundancy coverage: current redundancy evidence covers only 6/2485 factor pairs, so redundancy confidence is LOW for most factors.

## 0. PM objective

Build a memory-safe full pairwise factor redundancy matrix for the 71-factor library.

Then refresh the factor quality scorecard so redundancy confidence and novelty scoring reflect the new redundancy evidence.

Do **not** update public HTML pages in PM-18. Page rebuild/integration after refreshed scorecard should be PM-19.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify `scripts/factor_formula_registry.py`.

Do **not** modify `scripts/factor_ops.py`.

Do **not** modify signal panel construction.

Do **not** rebuild signal panel.

Do **not** modify public HTML pages.

Do **not** make production/live/tradeability/alpha claims.

Do **not** build a memory-heavy wide matrix from full 3.3M rows × 71 factors unless memory usage is explicitly safe.

## 2. Required inputs

Use canonical state and factor values:

```text
research/factor_runs/crypto_top50_factor_library/factor_library_state.json
data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/<factor_id>/factor_values.parquet
research/factor_runs/crypto_top50_factor_library/factor_metadata/factor_bilingual_cards.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.csv
```

Use all 71 registered/computed factors.

## 3. Required script

Create:

```text
scripts/build_factor_pairwise_redundancy_matrix.py
```

The script must be memory-safe and configurable.

Recommended CLI:

```bash
python scripts/build_factor_pairwise_redundancy_matrix.py \
  --sample-step 24 \
  --max-sampled-rows 250000 \
  --min-pairwise-obs 5000 \
  --output-dir research/factor_runs/crypto_top50_factor_library/factor_diagnostics
```

Arguments:

```text
--sample-step                deterministic row/time sampling interval
--max-sampled-rows           cap sampled rows after alignment
--min-pairwise-obs           minimum overlapping observations for pair validity
--output-dir                 output directory
--pair-scope                 all | within_family, default all
```

Default should be `pair-scope all` if memory-safe. If full all-pair run is too slow, the script should still produce within-family output and clearly mark full output as incomplete. But the target is all 2485 pairs.

## 4. Memory-safe implementation guidance

Use a deterministic sampled design.

Preferred approach:

1. Read factor IDs and families from state/metadata.
2. For each factor, load only its `factor_values.parquet`.
3. Keep only columns needed:

```text
timestamp
symbol
factor_value
```

4. Drop NaNs.
5. Apply deterministic sampling consistently across row keys.
6. Build a sampled wide matrix only after sampling.
7. Ensure sampled matrix size is safe, for example <= 250k rows × 71 columns.
8. Compute pairwise Pearson and Spearman correlations from sampled aligned data.

Do not load full 71-factor × full-row matrix into memory.

## 5. Required outputs

Write to:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/
```

Required files:

```text
factor_pairwise_redundancy.csv
factor_redundancy_summary.csv
factor_redundancy_matrix_spearman.csv
factor_redundancy_matrix_pearson.csv
factor_redundancy_clusters.csv
factor_pairwise_redundancy_manifest.json
```

### 5.1 `factor_pairwise_redundancy.csv`

One row per factor pair.

Required columns:

```text
factor_i
factor_j
family_i
family_j
same_family
n_pairwise_obs
pearson_corr
spearman_corr
abs_pearson_corr
abs_spearman_corr
redundancy_level
recommendation
```

Target row count for all-pair run:

```text
C(71, 2) = 2485
```

### 5.2 `factor_redundancy_summary.csv`

One row per factor.

Required columns:

```text
factor_id
family
nearest_factor
nearest_family
nearest_abs_spearman_corr
nearest_abs_pearson_corr
strongest_redundancy_level
n_high_redundancy_pairs
n_moderate_redundancy_pairs
n_low_redundancy_pairs
n_valid_pairs
redundancy_confidence
novelty_assessment
```

Suggested `novelty_assessment` values:

```text
LIKELY_DISTINCT
MODERATELY_REDUNDANT
HIGHLY_REDUNDANT
NEEDS_REVIEW
INSUFFICIENT_OVERLAP
```

### 5.3 Matrices

`factor_redundancy_matrix_spearman.csv`: symmetric 71 × 71 matrix.

`factor_redundancy_matrix_pearson.csv`: symmetric 71 × 71 matrix.

### 5.4 Clusters

`factor_redundancy_clusters.csv` should group factors using a simple threshold graph, not a heavy dependency.

Suggested logic:

- Create edges where `abs_spearman_corr >= 0.80`.
- Connected components are redundancy clusters.
- One row per factor with `cluster_id`, `cluster_size`, `cluster_members`.

## 6. Redundancy levels

Use thresholds:

```text
NEAR_DUPLICATE: abs_spearman_corr >= 0.95
HIGH_REDUNDANCY: abs_spearman_corr >= 0.80
MODERATE_REDUNDANCY: abs_spearman_corr >= 0.60
LOW_REDUNDANCY: abs_spearman_corr < 0.60
INSUFFICIENT_OVERLAP: n_pairwise_obs < min_pairwise_obs
```

Document thresholds in manifest and audit.

## 7. Refresh scorecard

After generating redundancy outputs, update:

```text
scripts/build_factor_quality_scorecard.py
```

so it can consume the new redundancy summary if present:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_summary.csv
```

Then rerun:

```bash
python scripts/build_factor_quality_scorecard.py
```

Regenerate:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard_manifest.json
```

Do not update public HTML page in PM-18. PM-19 will rebuild the page with refreshed scorecard.

## 8. Validation

Run:

```bash
python -m py_compile scripts/build_factor_pairwise_redundancy_matrix.py scripts/build_factor_quality_scorecard.py
python scripts/build_factor_pairwise_redundancy_matrix.py --sample-step 24 --max-sampled-rows 250000 --min-pairwise-obs 5000
python scripts/build_factor_quality_scorecard.py
```

Then run:

```bash
python - <<'PY'
import pandas as pd
from pathlib import Path
base = Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics')
pair = pd.read_csv(base / 'factor_pairwise_redundancy.csv')
summary = pd.read_csv(base / 'factor_redundancy_summary.csv')
score = pd.read_csv(base / 'factor_quality_scorecard.csv')
print('pair rows', len(pair))
print('summary rows', len(summary), 'factors', summary['factor_id'].nunique())
print('score rows', len(score), 'factors', score['factor_id'].nunique())
print('redundancy levels')
print(pair['redundancy_level'].value_counts(dropna=False))
print('summary confidence')
print(summary['redundancy_confidence'].value_counts(dropna=False))
print('score confidence')
print(score['score_confidence'].value_counts(dropna=False))
PY
```

Expected target:

- pair rows = 2485 if full run completed;
- summary rows = 71;
- score rows = 71;
- no missing factor IDs.

If pair rows < 2485, audit must explain why.

## 9. Required audit note

Create:

```text
docs/factor_library/audits/pm18_full_pairwise_redundancy_matrix.md
```

Audit must include:

1. Summary verdict:
   - `REDUNDANCY_MATRIX_PASS`
   - `REDUNDANCY_MATRIX_PASS_WITH_LIMITATIONS`
   - `REDUNDANCY_MATRIX_BLOCKED`
2. Files generated/changed.
3. Pair coverage: expected 2485 vs actual.
4. Sampling method and parameters.
5. Memory-safety notes.
6. Redundancy level distribution.
7. Top 20 most redundant pairs.
8. Within-family redundancy summary.
9. Cluster summary.
10. Scorecard refresh impact:
    - class distribution before vs after if available;
    - confidence distribution before vs after if available;
    - number of factors whose redundancy confidence improved.
11. Limitations.
12. Non-change statement: no factors, formulas, factor_values, signal panel, public pages.
13. Recommended next PM.

## 10. Allowed files to change

Allowed code:

```text
scripts/build_factor_pairwise_redundancy_matrix.py
scripts/build_factor_quality_scorecard.py
```

Allowed diagnostics outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_pairwise_redundancy.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_matrix_spearman.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_matrix_pearson.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_clusters.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_pairwise_redundancy_manifest.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard_manifest.json
```

Allowed audit:

```text
docs/factor_library/audits/pm18_full_pairwise_redundancy_matrix.md
```

Do not modify public HTML pages in PM-18.

## 11. Stop conditions

Stop and report if:

- factor_values cannot be found for the 71 factors;
- memory usage becomes unsafe;
- pairwise alignment produces too few observations;
- full matrix cannot be completed and within-family only is all that is possible;
- scorecard refresh would require changing formulas, factor_values, or page logic.

## 12. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
feat: build full factor redundancy matrix
```

Final response should include:

- commit hash
- summary verdict
- pair coverage
- redundancy level distribution
- top redundant pairs
- cluster summary
- scorecard refresh impact
- limitations
- recommended next PM
