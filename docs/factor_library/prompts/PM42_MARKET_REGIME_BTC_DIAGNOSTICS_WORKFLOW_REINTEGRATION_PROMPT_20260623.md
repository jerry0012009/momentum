# PM-42 Prompt — Market Regime / BTC Diagnostics Workflow Reintegration

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-41 LS aggregate canonicalization.

Jerry noted that paper regime decomposition and BTC correlation were likely already implemented earlier. This is correct: the repository already has `scripts/build_factor_market_regime_diagnostics.py`, originally from PM-23/PM-24, which computes BTC monthly regimes, paper/LS/IC regime summaries, BTC correlations, BTC beta, and regime dependency classification.

The current problem is not absence of code. The problem is that this script may not be fully reintegrated into the post-intake workflow for PM-35 new factors after canonical outputs were repaired.

PM-42 should reintegrate existing market regime / BTC diagnostics into the current 76-factor post-intake workflow.

## 0. PM objective

Re-use existing market regime / BTC diagnostics code and ensure it operates on current canonical 76-factor outputs.

This PM should answer:

1. Does `build_factor_market_regime_diagnostics.py` already calculate the missing fields?
2. Does it currently see all 76 factors, including the five PM-35 factors?
3. Does it use current canonical monthly IC / monthly LS / paper monthly returns?
4. Does `factor_regime_exposure_summary.csv` include the five PM-35 factors?
5. Does `factor_regime_summary.csv` include paper_return / long_short / IC rows for the five PM-35 factors?
6. Does `factor-evaluation.html` correctly render these regime/BTC diagnostics after regeneration?
7. Is the script included in `run_factor_library_refresh.py` or documented as part of post-intake workflow?

This is workflow reintegration. Do not implement a duplicate regime script unless existing code is unusable.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify expected_direction.

Do **not** modify factor_values.

Do **not** modify signal panel construction.

Do **not** enter factor interpretation or direction semantics review.

Do **not** do live trading / broker / execution work.

Do **not** create a parallel regime diagnostics pipeline if the existing script can be reused.

## 2. Required files to inspect first

Read:

```text
scripts/build_factor_market_regime_diagnostics.py
scripts/run_factor_library_refresh.py
scripts/_build_factor_eval_html.py
scripts/check_factor_evaluation_page_completeness.py
scripts/build_single_factor_paper_portfolio_diagnostics.py
scripts/build_single_factor_paper_page_payload.py
docs/factor_library/REGENERATION_CONTRACT.md
docs/factor_library/POST_INTAKE_WORKFLOW_RUNBOOK.md
docs/factor_library/RESOURCE_AWARE_REFRESH_GUIDE.md
docs/factor_library/audits/pm23_btc_market_regime_diagnostics.md
docs/factor_library/audits/pm24_btc_market_regime_page_integration.md
docs/factor_library/audits/pm24b_refresh_regime_page_after_paper_repair.md
docs/factor_library/audits/pm41_ls_aggregate_canonicalization.md
```

Inspect current inputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_monthly_ic_series.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_monthly_long_short_series.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_monthly_returns.csv
research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_period_ic_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_period_long_short_summary.csv
```

Inspect current outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/market_regime_monthly_labels.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_exposure_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_diagnostics_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_market_regime_manifest.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_class_distribution.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_top_lists.csv
```

## 3. Required discovery result

Before modifying code, write in the audit:

- whether `build_factor_market_regime_diagnostics.py` already computes:
  - `paper_return_btc_corr`
  - `paper_return_btc_beta`
  - `long_short_btc_corr`
  - `long_short_btc_beta`
  - `ic_btc_return_corr`
  - `bull_minus_bear_paper_return`
  - `highvol_minus_lowvol_paper_return`
  - `drawdown_minus_normal_paper_return`
- which files receive those fields;
- whether those fields are currently populated for PM-35 factors.

Do not guess. Use the actual script and current CSVs.

## 4. Required reintegration steps

If the existing script is valid, run or repair it so current outputs cover 76 factors.

Recommended command:

```bash
python scripts/build_factor_market_regime_diagnostics.py \
  --btc-symbol auto \
  --fee-bps 10 \
  --output-dir research/factor_runs/crypto_top50_factor_library/factor_diagnostics
```

However, if current `factor_monthly_ic_series.csv` / `factor_monthly_long_short_series.csv` do not include PM-35 new factors, adapt the script to accept canonical factor-level period IC/LS fallback, using:

```text
factor_level_evaluation/factor_level_period_ic_summary.csv
factor_level_evaluation/factor_level_period_long_short_summary.csv
```

Do not make the page builder do the only conversion. The regime script should use canonical inputs directly.

## 5. Required page integration

After regime outputs cover 76 factors:

1. Rebuild factor-evaluation page.
2. Confirm the BTC / Market Regime Diagnostics section for the five PM-35 factors is no longer incorrectly empty when data is available.
3. If some regime diagnostics remain unavailable because minimum months per regime is not met, show explicit unavailable reason rather than blank values.

## 6. Required QA updates

Update or add checks in:

```text
scripts/check_factor_evaluation_page_completeness.py
```

or, if cleaner, create:

```text
scripts/check_factor_market_regime_workflow_integrity.py
```

The QA should verify for the five PM-35 factors:

```text
factor_id exists in factor_regime_exposure_summary.csv
factor_id has regime_dependency_class
factor_id has long_short_btc_corr or explicit unavailable reason
factor_id has paper_return_btc_corr if paper monthly returns exist, or explicit unavailable reason
factor_id has bull_minus_bear_paper_return if regime buckets are sufficient, or explicit unavailable reason
factor-evaluation.html contains BTC / Market Regime Diagnostics section for the factor
```

Outputs if a new QA script is created:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_market_regime_workflow_integrity_report.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_market_regime_workflow_integrity_report.json
```

## 7. Required docs update

Update:

```text
docs/factor_library/POST_INTAKE_WORKFLOW_RUNBOOK.md
docs/factor_library/REGENERATION_CONTRACT.md
```

Add the lesson:

```text
Market regime / BTC diagnostics already exist in build_factor_market_regime_diagnostics.py. After controlled factor intake and paper/period-series repair, this stage must be rerun or validated so PM-35 new factors receive current regime and BTC correlation diagnostics.
```

Also clarify:

- the script is not a trading timing model;
- regime labels are ex-post diagnostics;
- BTC correlation/beta are research diagnostics;
- insufficient regime data should be explicit, not blank.

## 8. Required audit

Create:

```text
docs/factor_library/audits/pm42_market_regime_btc_diagnostics_workflow_reintegration.md
```

Audit must include:

1. Summary verdict:
   - `MARKET_REGIME_BTC_WORKFLOW_PASS`
   - `MARKET_REGIME_BTC_WORKFLOW_PASS_WITH_LIMITATIONS`
   - `MARKET_REGIME_BTC_WORKFLOW_BLOCKED`
2. Existing script discovery result.
3. Whether current outputs had PM-35 factors before repair.
4. Repair/reintegration performed.
5. PM-35 five-factor regime/BTC diagnostics table.
6. Public/page rendering status.
7. QA result.
8. Files changed.
9. Confirmation no formulas / expected_direction / factor_values / signal changes.
10. Remaining limitations.
11. Recommended next PM: PM-43 post-intake factor interpretation and direction-semantics review.

## 9. Validation

Run:

```bash
python scripts/build_factor_market_regime_diagnostics.py --btc-symbol auto --fee-bps 10 --output-dir research/factor_runs/crypto_top50_factor_library/factor_diagnostics
python scripts/check_factor_evaluation_page_completeness.py
```

If a new QA script is created:

```bash
python -m py_compile scripts/check_factor_market_regime_workflow_integrity.py
python scripts/check_factor_market_regime_workflow_integrity.py
```

Then validate PM-35 coverage:

```bash
python - <<'PY'
import pandas as pd
from pathlib import Path
new = ['rev_2h','mom_vol_adjusted_20h','range_breakout_vol_confirm_20h','volume_pressure_20h','xs_rank_mom_accel']
base = Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics')
ex = pd.read_csv(base / 'factor_regime_exposure_summary.csv')
print(ex[ex['factor_id'].isin(new)].to_string(index=False))
assert set(new).issubset(set(ex['factor_id']))
PY
```

## 10. Allowed files to change

Allowed scripts:

```text
scripts/build_factor_market_regime_diagnostics.py
scripts/check_factor_evaluation_page_completeness.py
scripts/check_factor_market_regime_workflow_integrity.py
scripts/_build_factor_eval_html.py
scripts/run_factor_library_refresh.py
```

Allowed outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/market_regime_monthly_labels.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_exposure_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_diagnostics_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_market_regime_manifest.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_class_distribution.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_top_lists.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_market_regime_workflow_integrity_report.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_market_regime_workflow_integrity_report.json
reports/site/factor-library/factor-evaluation.html
```

Allowed docs:

```text
docs/factor_library/POST_INTAKE_WORKFLOW_RUNBOOK.md
docs/factor_library/REGENERATION_CONTRACT.md
docs/factor_library/audits/pm42_market_regime_btc_diagnostics_workflow_reintegration.md
```

Do not modify:

```text
scripts/factor_formula_registry.py
scripts/factor_ops.py
scripts/build_factor_values.py
scripts/build_phase9b_signal_panel.py
research/factor_runs/crypto_top50_factor_library/factor_values/*
src/momentum/strategies/*
```

## 11. Stop conditions

Stop and report if:

- existing regime script cannot be safely reused;
- PM-35 factor coverage requires full expensive recomputation outside this scope;
- BTC bars are unavailable;
- paper monthly returns for new factors are missing;
- fixing this would require modifying factor formulas or factor values.

## 12. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
fix: reintegrate market regime diagnostics for new factors
```

Final response should include:

- commit hash
- summary verdict
- existing script discovery result
- PM-35 five-factor regime/BTC table
- page status
- QA result
- files changed
- no formula/factor_values/signal confirmation
- limitations
- recommended next PM
