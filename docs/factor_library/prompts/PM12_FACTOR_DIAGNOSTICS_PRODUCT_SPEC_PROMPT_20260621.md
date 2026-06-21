# PM-12 Prompt — Factor Diagnostics Product Spec and Gap Audit

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-11B:

- `docs/factor_library/audits/pm11b_funding_rate_integration.md`

PM-11B completed the data/factor-value completeness milestone: all 71 registered factors now have computed canonical factor_values.

The user now reports that the factor library still feels incomplete as a decision tool:

- factor content feels incomplete;
- pages are not bilingual Chinese/English;
- there are no clear monthly PnL / long-short return curves;
- there are no monthly IC curves;
- there is no Sharpe ratio or risk metric summary;
- current pages do not provide enough evidence to judge factor quality.

## 0. PM objective

Perform a read-only product/spec audit for the next stage: turning the factor library from a data/registry project into a decision-grade factor diagnostics product.

This task should define what artifacts, metrics, pages, and bilingual factor-card fields are missing, and propose a concrete implementation sequence.

Do **not** implement charts or metrics in this task. First produce the spec and gap audit.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify `scripts/factor_formula_registry.py`.

Do **not** modify `scripts/factor_ops.py`.

Do **not** modify `scripts/build_phase9b_signal_panel.py`.

Do **not** rebuild signal panel.

Do **not** rebuild public site pages.

Do **not** run full factor evaluation unless only reading existing outputs is impossible. Prefer read-only inspection of existing artifacts.

Do **not** make production/live/tradeability/alpha claims.

Do **not** create a parallel evaluator.

## 2. Current milestone to verify

Verify current factor library state:

```text
research/factor_runs/crypto_top50_factor_library/factor_library_state.json
research/factor_runs/crypto_top50_factor_library/factor_library_state.md
```

Expected after PM-11B:

- registered factors: 71
- computed factor_values: 71
- missing factor_values: 0
- missing input: 0

If state does not match, record the mismatch but do not fix it in this task.

## 3. Artifacts to inspect

Inspect existing factor evaluation and public-report artifacts, including but not limited to:

```text
research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/
research/factor_runs/crypto_top50_factor_library/factor_catalog.csv
research/factor_runs/crypto_top50_factor_library/factor_catalog.json
research/factor_runs/crypto_top50_factor_library/factor_library_state.json
research/factor_runs/crypto_top50_factor_library/factor_library_state.md
reports/site/factor-library/index.html
reports/site/factor-library/factor-evaluation.html
reports/site/factor-library/signal-evaluation-summary.html
reports/site/factor-library/assets/
```

Also inspect scripts that generate existing outputs:

```text
scripts/evaluate_factors.py
scripts/build_factor_library_state.py
scripts/build_factor_conclusion_cards.py
scripts/generate_intake_report.py
scripts/build_phase9b_signal_panel.py
scripts/evaluate_signals.py
```

## 4. Required gap audit

Produce a gap table with these columns:

```text
user_need | existing_artifact | existing_status | gap | recommended_next_pm | implementation_risk
```

At minimum cover:

1. bilingual Chinese/English factor names and explanations;
2. factor formula and intuition display;
3. monthly IC series;
4. monthly long-short return / PnL series;
5. cumulative long-short equity curve;
6. Sharpe ratio;
7. annualized return and annualized volatility;
8. max drawdown;
9. monthly hit rate / positive-month ratio;
10. ICIR / RankIC stability;
11. coverage / missingness;
12. redundancy and near-duplicate clustering;
13. decision bucket and recommended action;
14. horizon-specific best metric display;
15. public page usability.

## 5. Proposed target data model

Define a target machine-readable diagnostics layer.

At minimum specify the schema for these proposed artifacts:

### 5.1 `factor_diagnostics_summary.csv/json`

One row per factor × horizon, or one row per factor with best horizon fields. Decide and explain.

Required candidate fields:

```text
factor_id
family
status/lifecycle
name_en
name_zh
formula_short
formula_zh
intuition_en
intuition_zh
required_columns
expected_direction
horizon
rankic_mean
rankic_std
rankic_ir
rankic_t_stat
monthly_ic_positive_rate
long_short_mean
long_short_std
long_short_sharpe
long_short_annualized_return
long_short_annualized_vol
long_short_max_drawdown
long_short_positive_month_rate
coverage_rate
redundancy_level
nearest_redundant_factor
decision_bucket
recommended_action
```

### 5.2 `factor_monthly_ic_series.csv`

One row per factor × horizon × month.

Required candidate fields:

```text
factor_id
horizon
month
rank_ic
rank_ic_adj
n_obs
positive_ic
```

### 5.3 `factor_monthly_long_short_series.csv`

One row per factor × horizon × month.

Required candidate fields:

```text
factor_id
horizon
month
long_short_return
long_leg_return
short_leg_return
n_long
n_short
positive_ls
```

### 5.4 `factor_cumulative_long_short_curve.csv`

One row per factor × horizon × timestamp or month.

Required candidate fields:

```text
factor_id
horizon
date_or_month
long_short_return
cum_long_short_return
drawdown
```

### 5.5 `factor_bilingual_cards.json`

One object per factor.

Required candidate fields:

```text
factor_id
name_en
name_zh
family_en
family_zh
formula_en
formula_zh
intuition_en
intuition_zh
required_columns
expected_direction_explanation_zh
expected_direction_explanation_en
known_limitations_zh
known_limitations_en
status_explanation_zh
status_explanation_en
```

## 6. Proposed implementation sequence

Recommend the next 3–5 PM tasks after this spec.

The sequence should probably be:

- PM-13: implement factor diagnostics metrics builder from existing evaluation outputs;
- PM-14: generate bilingual factor cards from registry/catalog;
- PM-15: build static diagnostic pages/tables with IC and long-short curves;
- PM-16: factor quality decision framework / scorecard;
- PM-17: next factor expansion or signal redesign only after diagnostics are decision-grade.

But inspect the repo and adjust if there is a better sequence.

## 7. Required output

Create:

```text
docs/factor_library/audits/pm12_factor_diagnostics_product_spec.md
```

The audit/spec must include:

1. current state verification;
2. existing artifact inventory;
3. user-need gap table;
4. target diagnostics artifact schemas;
5. bilingual factor card schema;
6. proposed metric formulas, including Sharpe and drawdown definitions;
7. recommended implementation sequence;
8. explicit non-change statement.

## 8. Metric formula definitions

Be explicit but do not overclaim.

Suggested definitions:

- monthly IC curve: monthly mean of rank IC by factor/horizon;
- monthly long-short return: monthly aggregation of factor quantile long-short return;
- cumulative curve: cumulative product or cumulative sum depending on whether returns are expressed as simple returns; state the choice;
- Sharpe: mean periodic long-short return divided by std periodic long-short return, annualized using the chosen periodicity; state assumptions;
- max drawdown: max peak-to-trough drawdown of the cumulative long-short curve;
- positive month rate: fraction of months with positive long-short return or positive IC.

If existing outputs do not support exact formula, flag the missing field rather than inventing.

## 9. Validation

Run read-only / compile checks only:

```bash
python -m py_compile scripts/evaluate_factors.py scripts/build_factor_library_state.py scripts/build_factor_conclusion_cards.py scripts/generate_intake_report.py scripts/evaluate_signals.py
```

Do not run expensive full rebuilds.

## 10. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
docs: specify decision-grade factor diagnostics
```

Final response should include:

- commit hash
- whether current state is complete at 71/71/0
- biggest user-facing gaps
- recommended PM-13 task
- warnings/blockers
