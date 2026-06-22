# PM-31 Prompt — Redundancy Cluster and Marginal Information Diagnostics

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows:

- PM-19/20: factor quality scorecard and pairwise redundancy matrix
- PM-21B through PM-30: paper, regime, shape/stability/decile, capacity/liquidity diagnostics and page integration

We are still in the **factor evaluation** phase. Do **not** enter signal construction or signal evaluation.

## 0. PM objective

Add a reusable data-layer diagnostic module for **factor redundancy clusters** and **marginal information value**.

Current redundancy diagnostics identify pairwise overlap / nearest redundant factors, but they do not yet answer:

1. Which factors form the same information cluster?
2. Which factors are representative within each cluster?
3. Which factors add marginal information versus duplicate an existing cluster?
4. Which high-quality factors are actually redundant with better alternatives?
5. Which low-redundancy factors are worth keeping despite weak standalone performance?

This is needed before factor expansion and later factor combination.

Do **not** update public HTML in PM-31. Page integration or unified profile can happen later.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify signal panel construction.

Do **not** create or modify public HTML pages.

Do **not** enter signal evaluation.

Do **not** delete or suppress any factor.

Do **not** claim that a factor should be traded or dropped. Use diagnostic language only.

## 2. Required inputs

Use existing local outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_pairwise_redundancy.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_diagnostics_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_exposure_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_capacity_liquidity_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quantile_shape_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_rolling_stability_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_decile_shape_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_library_state.json
```

If some inputs are unavailable, degrade gracefully and report limitations.

## 3. Required script

Create:

```text
scripts/build_factor_redundancy_cluster_diagnostics.py
```

Recommended CLI:

```bash
python scripts/build_factor_redundancy_cluster_diagnostics.py
```

Optional arguments:

```bash
--redundancy-threshold 0.80
--strong-redundancy-threshold 0.90
--output-dir research/factor_runs/crypto_top50_factor_library/factor_diagnostics
```

## 4. Clustering method

Inspect `factor_pairwise_redundancy.csv` schema first. Use the strongest available redundancy/similarity field.

If the file provides a normalized redundancy score, use it.

If only correlations are available, use absolute correlation or the existing project convention.

Build clusters using a transparent graph method:

```text
nodes = factors
edges = factor pairs where redundancy_score >= redundancy_threshold
clusters = connected components
```

This avoids adding heavy dependencies.

Also compute strong edges using:

```text
redundancy_score >= strong_redundancy_threshold
```

## 5. Required outputs

Write to:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/
```

Required outputs:

```text
factor_redundancy_cluster_summary.csv
factor_redundancy_cluster_members.csv
factor_redundancy_cluster_representatives.csv
factor_marginal_information_summary.csv
factor_redundancy_cluster_payload.json
factor_redundancy_cluster_manifest.json
```

Payload should be compact and suitable for future page integration.

## 6. Cluster summary schema

`factor_redundancy_cluster_summary.csv` should include:

```text
cluster_id
cluster_size
representative_factor_id
representative_quality_score
avg_intra_redundancy
max_intra_redundancy
n_strong_edges
family_count
families
cluster_quality_class
cluster_interpretation_zh
cluster_interpretation_en
```

Suggested cluster quality classes:

```text
HIGH_QUALITY_CLUSTER
MIXED_QUALITY_CLUSTER
LOW_QUALITY_CLUSTER
SINGLETON_DISTINCT
REDUNDANT_WEAK_CLUSTER
```

## 7. Cluster members schema

`factor_redundancy_cluster_members.csv` should include:

```text
factor_id
cluster_id
cluster_size
family
quality_score
scorecard_class
redundancy_score_to_representative
nearest_redundant_factor
novelty_score
paper_net_return_10bps
cost_sensitivity_class
regime_dependency_class
capacity_liquidity_class
quantile_shape_class
stability_class
decile_shape_class
member_role
member_note_zh
member_note_en
```

Suggested `member_role` values:

```text
CLUSTER_REPRESENTATIVE
REDUNDANT_HIGH_QUALITY_ALTERNATIVE
REDUNDANT_WEAK_MEMBER
DISTINCT_SINGLETON
DIVERSIFYING_WEAK_SIGNAL
INSUFFICIENT_DATA
```

## 8. Representative selection

Choose representative factor per cluster using a transparent scoring rule.

The score should consider available evidence:

```text
quality_score
novelty_score / inverse redundancy
paper net return / paper Sharpe
cost robustness
regime robustness
capacity/liquidity class
shape/stability evidence
```

Do not overfit. If some fields are missing, use available fields and report fallback.

Representative selection should be diagnostic, not a trading recommendation.

## 9. Marginal information summary

`factor_marginal_information_summary.csv` should include one row per factor:

```text
factor_id
cluster_id
cluster_size
marginal_information_score
marginal_information_class
redundancy_penalty
quality_component
paper_component
stability_component
regime_component
capacity_component
nearest_better_factor
reason_zh
reason_en
```

Suggested `marginal_information_class`:

```text
HIGH_MARGINAL_INFORMATION
USEFUL_CLUSTER_REPRESENTATIVE
REDUNDANT_BUT_HIGH_QUALITY
MOSTLY_REDUNDANT
LOW_QUALITY_DISTINCT
INSUFFICIENT_DATA
```

Important: do not say “remove factor.” Say “mostly redundant” or “lower marginal information.”

## 10. Dynamic coverage requirements

Use expected factor count from `factor_library_state.json` or registry. Do not hardcode 71.

Audit must report:

```text
expected_factor_count
cluster_member_factor_count
marginal_summary_factor_count
payload_factor_count
missing_factor_ids
n_clusters
n_singletons
largest_cluster_size
cluster_size_distribution
marginal_information_class_distribution
```

## 11. Required audit

Create:

```text
docs/factor_library/audits/pm31_redundancy_cluster_marginal_information.md
```

Audit must include:

1. Summary verdict:
   - `REDUNDANCY_CLUSTER_DIAGNOSTICS_PASS`
   - `REDUNDANCY_CLUSTER_DIAGNOSTICS_PASS_WITH_LIMITATIONS`
   - `REDUNDANCY_CLUSTER_DIAGNOSTICS_BLOCKED`
2. Why PM-31 is needed before factor expansion and signal construction.
3. Files changed.
4. Input files used.
5. Redundancy field used and thresholds.
6. Factor coverage.
7. Number of clusters and singleton factors.
8. Largest clusters with representative factors.
9. Cluster size distribution.
10. Marginal information class distribution.
11. Examples of high marginal information factors.
12. Examples of mostly redundant factors.
13. Examples of distinct but weak factors.
14. Payload size.
15. Validation results.
16. Limitations.
17. Non-change statement: no factors, formulas, factor_values, signal panel, public page.
18. Recommended next PM: PM-32 unified factor profile / scorecard v2.

## 12. Validation

Run:

```bash
python -m py_compile scripts/build_factor_redundancy_cluster_diagnostics.py
python scripts/build_factor_redundancy_cluster_diagnostics.py
```

Then:

```bash
python - <<'PY'
import json
import pandas as pd
from pathlib import Path
base = Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics')
clusters = pd.read_csv(base / 'factor_redundancy_cluster_summary.csv')
members = pd.read_csv(base / 'factor_redundancy_cluster_members.csv')
marg = pd.read_csv(base / 'factor_marginal_information_summary.csv')
payload = json.loads((base / 'factor_redundancy_cluster_payload.json').read_text(encoding='utf-8'))
print('clusters', len(clusters))
print('member factors', members['factor_id'].nunique())
print('marginal factors', marg['factor_id'].nunique())
print('payload factors', len(payload.get('factors', [])))
print('largest cluster', clusters['cluster_size'].max())
print('cluster size distribution')
print(clusters['cluster_size'].value_counts(dropna=False).sort_index().to_string())
print('marginal info classes')
print(marg['marginal_information_class'].value_counts(dropna=False).to_string())
PY
```

Also run:

```bash
python scripts/check_factor_library_staleness.py
```

If PM-25 monitor does not yet know about cluster outputs, report as future monitor extension. Do not modify PM-25 here unless trivial.

## 13. Allowed files to change

Allowed script:

```text
scripts/build_factor_redundancy_cluster_diagnostics.py
```

Allowed outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_cluster_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_cluster_members.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_cluster_representatives.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_marginal_information_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_cluster_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_cluster_manifest.json
```

Allowed audit:

```text
docs/factor_library/audits/pm31_redundancy_cluster_marginal_information.md
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

- pairwise redundancy file is missing;
- redundancy score field cannot be identified;
- factor coverage cannot be reconciled;
- outputs would require recomputing expensive redundancy matrix;
- implementation would require modifying factor formulas, factor_values, or signal panel.

## 15. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
feat: add redundancy cluster diagnostics
```

Final response should include:

- commit hash
- summary verdict
- redundancy field used
- factor coverage
- number of clusters
- largest clusters and representatives
- marginal information class distribution
- representative examples
- validation results
- limitations
- recommended next PM
