# PM-31B Prompt — Cluster Diagnostic Language and Roadmap Repair

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-31:

- `scripts/build_factor_redundancy_cluster_diagnostics.py`
- `docs/factor_library/audits/pm31_redundancy_cluster_marginal_information.md`
- cluster / marginal information outputs in `factor_diagnostics/`

PM-31 successfully created redundancy clusters and added a `cluster` stage to the refresh workflow. However, some generated language is too prescriptive for the current research phase.

Examples that must be repaired:

```text
建议仅保留代表性因子
keep representative only
```

Also, the audit recommended portfolio construction next. That is too early. We are still strengthening factor evaluation, not entering signal / portfolio construction.

PM-31B should repair the diagnostic language and roadmap while preserving the useful cluster data.

## 0. PM objective

Repair PM-31 cluster outputs so they use **diagnostic language**, not portfolio construction decisions.

Cluster diagnostics should answer:

- which factors overlap;
- which factors are representatives;
- which factors have lower marginal information;
- which factors are distinct;
- what should be reviewed before later factor combination.

They should **not** say:

- remove this factor;
- keep only this representative;
- construct portfolio weights;
- move to signal construction now.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify signal panel construction.

Do **not** create or modify public HTML pages.

Do **not** enter signal evaluation.

Do **not** delete, suppress, or recommend deleting factors.

Do **not** use prescriptive portfolio construction language.

## 2. Required files to inspect

Inspect:

```text
scripts/build_factor_redundancy_cluster_diagnostics.py
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_cluster_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_cluster_members.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_marginal_information_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_cluster_payload.json
docs/factor_library/audits/pm31_redundancy_cluster_marginal_information.md
scripts/run_factor_library_refresh.py
docs/factor_library/REGENERATION_CONTRACT.md
```

## 3. Required repairs

Modify:

```text
scripts/build_factor_redundancy_cluster_diagnostics.py
```

Regenerate:

```text
factor_redundancy_cluster_summary.csv
factor_redundancy_cluster_members.csv
factor_redundancy_cluster_representatives.csv
factor_marginal_information_summary.csv
factor_redundancy_cluster_payload.json
factor_redundancy_cluster_manifest.json
```

Create new audit:

```text
docs/factor_library/audits/pm31b_cluster_diagnostic_language_roadmap_repair.md
```

Do not modify public HTML.

## 4. Language rules

Replace prescriptive language like:

```text
keep representative only
remove redundant factors
drop weak members
use for portfolio construction
```

With diagnostic language like:

```text
Representative factor provides a useful reference point for this cluster.
Other members require marginal-information review before combination.
High redundancy suggests overlap; do not interpret as an automatic exclusion decision.
Cluster membership should inform later factor combination, not determine it directly.
```

Chinese equivalent should use:

```text
该簇存在较高信息重叠，代表因子可作为后续比较基准；其他成员需结合边际信息、稳定性、容量与状态表现进一步评估。
```

Avoid:

```text
只保留
剔除
删除
淘汰
直接进入组合
```

## 5. Member role wording

Allowed diagnostic roles:

```text
CLUSTER_REPRESENTATIVE
REDUNDANT_HIGH_QUALITY_ALTERNATIVE
LOWER_MARGINAL_INFORMATION_MEMBER
DISTINCT_SINGLETON
DIVERSIFYING_WEAK_SIGNAL
INSUFFICIENT_DATA
```

Avoid roles that imply deletion.

If current outputs use `REDUNDANT_WEAK_MEMBER`, decide whether to keep it. If kept, notes must clearly say lower marginal information, not remove/drop.

## 6. Roadmap repair

The PM-31 audit recommended portfolio construction next. Repair roadmap language in the PM-31B audit.

Recommended next PM must be:

```text
PM-32: Unified Factor Profile / Scorecard v2
```

Rationale:

- We now have scorecard, paper, cost, regime, shape, rolling stability, decile, capacity/liquidity, and cluster/marginal information.
- The next step is to unify these into a single factor profile schema.
- We are still not entering signal construction.

## 7. Workflow verification

Verify that:

```bash
python scripts/run_factor_library_refresh.py --stage cluster --dry-run
```

works.

Verify `REGENERATION_CONTRACT.md` mentions cluster after redundancy and before unified profile / downstream outputs.

Do not do large workflow restructuring.

## 8. Required audit contents

Create:

```text
docs/factor_library/audits/pm31b_cluster_diagnostic_language_roadmap_repair.md
```

Audit must include:

1. Summary verdict:
   - `CLUSTER_LANGUAGE_ROADMAP_REPAIR_PASS`
   - `CLUSTER_LANGUAGE_ROADMAP_REPAIR_PASS_WITH_LIMITATIONS`
   - `CLUSTER_LANGUAGE_ROADMAP_REPAIR_BLOCKED`
2. Why PM-31B was required.
3. Files changed.
4. Examples of removed/replaced prescriptive phrases.
5. Confirmation no `keep representative only`, `只保留`, `delete`, `drop`, `remove` language remains in cluster outputs.
6. Factor coverage remains 71/71.
7. Cluster count and largest cluster unchanged or explain changes.
8. Marginal information class distribution unchanged or explain changes.
9. Workflow stage `cluster` still works.
10. Contract still references cluster stage.
11. Non-change statement: no factors, formulas, factor_values, signal panel, public page.
12. Recommended next PM: PM-32 Unified Factor Profile / Scorecard v2.

## 9. Validation

Run:

```bash
python -m py_compile scripts/build_factor_redundancy_cluster_diagnostics.py
python scripts/build_factor_redundancy_cluster_diagnostics.py
python scripts/run_factor_library_refresh.py --stage cluster --dry-run
```

Then run text checks:

```bash
python - <<'PY'
from pathlib import Path
paths = [
    Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_cluster_summary.csv'),
    Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_cluster_members.csv'),
    Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_marginal_information_summary.csv'),
    Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_cluster_payload.json'),
]
bad = ['keep representative only', '只保留', 'delete', 'drop', 'remove this factor', '剔除', '删除', '淘汰']
for p in paths:
    txt = p.read_text(encoding='utf-8', errors='ignore').lower()
    hits = [b for b in bad if b.lower() in txt]
    print(p.name, 'BAD_HITS=', hits)
PY
```

Also run:

```bash
python scripts/check_factor_library_staleness.py
```

If PM-25 monitor does not yet know about cluster outputs, report as future monitor extension.

## 10. Allowed files to change

Allowed script:

```text
scripts/build_factor_redundancy_cluster_diagnostics.py
```

Allowed regenerated outputs:

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
docs/factor_library/audits/pm31b_cluster_diagnostic_language_roadmap_repair.md
```

Optional, only if needed for one-line wording correction:

```text
docs/factor_library/REGENERATION_CONTRACT.md
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

## 11. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
fix: use diagnostic language for redundancy clusters
```

Final response should include:

- commit hash
- summary verdict
- language repair summary
- factor coverage
- cluster count
- largest cluster
- workflow stage verification
- contract verification
- validation results
- limitations
- recommended next PM
