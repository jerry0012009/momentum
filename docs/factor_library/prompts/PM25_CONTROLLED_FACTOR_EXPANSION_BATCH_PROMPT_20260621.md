# PM-25 Prompt — Controlled Factor Expansion Batch via Existing Intake Workflow

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-24:

- The factor-evaluation page now includes scorecard, redundancy, paper portfolio diagnostics, cost sensitivity, and BTC / market regime diagnostics.
- The regeneration workflow is defined in `docs/factor_library/REGENERATION_CONTRACT.md`.
- New factors must go through the existing factor intake workflow; do not create a parallel workflow.

PM-25 should test and extend the factor library by adding a small, controlled batch of new factors through the existing intake/regeneration path.

This is not a documentation PM and not a health-monitor PM.

## 0. PM objective

Add a small batch of new, economically interpretable, low-redundancy candidate factors and run them through the canonical workflow.

The purpose is to prove that the current factor library is extensible:

```text
new FactorSpec
  → registry integrity
  → factor values
  → intake evaluation
  → full library diagnostics refresh
  → scorecard
  → redundancy
  → paper diagnostics
  → regime diagnostics
  → factor-evaluation page
```

Do this without creating new parallel scripts/pages.

## 1. Strict prohibitions

Do **not** create a new factor pipeline.

Do **not** create a new evaluator.

Do **not** create a new public page.

Do **not** modify signal panel construction.

Do **not** promote any new factor into a signal.

Do **not** touch `src/momentum/strategies/`.

Do **not** modify existing factor formulas unless there is a small bug required to support intake.

Do **not** hand-edit generated CSV/JSON outputs.

Do **not** make production/live/tradeability/alpha claims.

Do **not** add a large undisciplined batch of factors. Target 4–6 factors.

## 2. Required documents/scripts to read first

Read:

```text
docs/factor_library/START_HERE.md
docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md
docs/factor_library/REGENERATION_CONTRACT.md
docs/factor_library/factor_library_manifest.json
research/factor_runs/crypto_top50_factor_library/factor_library_state.json
scripts/factor_formula_registry.py
scripts/factor_ops.py
scripts/run_factor_intake.py
scripts/run_factor_library_refresh.py
```

Read current evidence to avoid duplicate/weak factors:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_exposure_summary.csv
```

## 3. Factor selection principles

Choose candidates that address current evidence gaps.

PM-21 showed many high-turnover factors collapse after costs. Therefore prioritize:

- lower-turnover factors;
- slower horizon factors;
- carry/funding structure;
- liquidity/illiquidity structure;
- volatility shape/asymmetry;
- return consistency rather than short-horizon churn;
- economically interpretable signals;
- formulas that can be computed from existing cached bars/funding/taker fields.

Avoid:

- near-duplicates of existing factors;
- pure variants of mom/reversal/rsi with only small window tweaks;
- ultra-short-horizon high-turnover factors;
- factors requiring unavailable data;
- opaque formula mining.

## 4. Suggested candidate families

Inspect existing registry before deciding. If a candidate already exists, skip or replace it.

Prioritize 4–6 from this style of candidates:

### 4.1 Funding / carry structure

Potential factor IDs:

```text
funding_rate_zscore_72h
funding_rate_change_24h
funding_rate_vol_72h
funding_rate_persistence_72h
```

Ideas:

- funding level relative to its rolling mean/std;
- change in funding over 24h;
- volatility of funding over 72h;
- fraction of positive funding observations over 72h.

### 4.2 Low-turnover trend persistence

Potential factor IDs:

```text
return_consistency_72h
trend_efficiency_72h
close_to_vwap_trend_72h
```

Ideas:

- fraction of positive 1h returns over a 72h window;
- net return divided by sum of absolute hourly returns;
- price relative to rolling VWAP over 72h.

### 4.3 Volatility shape / asymmetry

Potential factor IDs:

```text
realized_skew_72h
downside_upside_vol_ratio_72h
vol_term_structure_20_72h
```

Ideas:

- rolling skewness of returns;
- downside vol divided by upside vol;
- short realized vol vs long realized vol.

### 4.4 Liquidity / volume structure

Potential factor IDs:

```text
volume_trend_72h
amihud_change_72h
quote_volume_zscore_72h
```

Ideas:

- rolling change in quote volume;
- change in amihud illiquidity;
- quote volume z-score.

Do not add all candidates. Select 4–6 after checking existing registry and redundancy risk.

## 5. Implementation requirements

Add selected candidates as `FactorSpec` entries in:

```text
scripts/factor_formula_registry.py
```

Use `scripts/factor_ops.py` where possible.

Only add new helper functions to `factor_ops.py` if existing operators cannot express the formula. If adding helpers, keep them pure, vectorized, and no future leakage.

Each factor must include:

- clear `factor_id`;
- family;
- source resolution;
- input columns;
- lookback;
- expected direction if economically defensible;
- bilingual description if registry supports it;
- no future data use.

## 6. Required workflow

Use the canonical workflow. Do not bypass it.

### 6.1 Registry and static checks

Run:

```bash
python scripts/check_factor_registry_integrity.py
python scripts/build_factor_catalog.py
python scripts/check_factor_catalog_integrity.py
python scripts/audit_factor_direction_semantics.py
```

### 6.2 Intake run

Run an isolated intake:

```bash
python scripts/run_factor_intake.py --factor-ids <new_factor_ids...> --run-id pm25_controlled_factor_expansion_batch
```

The run directory should be:

```text
research/factor_runs/crypto_top50_factor_library/factor_intake/pm25_controlled_factor_expansion_batch/
```

### 6.3 Full library refresh

After intake passes, refresh the canonical library so the new factors reach the page.

Use `run_factor_library_refresh.py` if it supports the needed stages.

Suggested:

```bash
python scripts/run_factor_library_refresh.py --stage all --expensive-ok
```

If that is too expensive or unsupported, run the documented stage sequence from `REGENERATION_CONTRACT.md` and explain the exact commands in the audit.

The final page should include the new factors in existing sections, not a new page.

## 7. Required outputs / audit

Create:

```text
docs/factor_library/audits/pm25_controlled_factor_expansion_batch.md
```

Audit must include:

1. Summary verdict:
   - `CONTROLLED_FACTOR_EXPANSION_PASS`
   - `CONTROLLED_FACTOR_EXPANSION_PASS_WITH_LIMITATIONS`
   - `CONTROLLED_FACTOR_EXPANSION_BLOCKED`
2. Selected factor IDs and why they were chosen.
3. Candidate factors skipped and why.
4. Registry checks result.
5. Intake run path and status.
6. Factor values coverage for new factors.
7. Evaluation coverage for new factors.
8. Redundancy results for new factors.
9. Scorecard class for new factors.
10. Paper portfolio / cost sensitivity results for new factors.
11. Regime dependency class for new factors.
12. Updated total registered factor count.
13. Updated page coverage.
14. Non-change statement: no signal promotion, no strategy/live code, no new public page.
15. Recommended next PM.

## 8. Validation

Run or verify:

```bash
python -m py_compile scripts/factor_formula_registry.py scripts/factor_ops.py
python scripts/check_factor_registry_integrity.py
python scripts/check_factor_catalog_integrity.py
python scripts/audit_factor_direction_semantics.py
python scripts/run_factor_intake.py --factor-ids <new_factor_ids...> --run-id pm25_controlled_factor_expansion_batch
python scripts/run_factor_library_refresh.py --stage all --expensive-ok
```

Then run a compact verification:

```bash
python - <<'PY'
import json
import pandas as pd
from pathlib import Path
base = Path('research/factor_runs/crypto_top50_factor_library')
state = json.loads((base / 'factor_library_state.json').read_text(encoding='utf-8'))
diag = base / 'factor_diagnostics'
score = pd.read_csv(diag / 'factor_quality_scorecard.csv')
paper = pd.read_csv(diag / 'single_factor_paper_summary.csv')
regime = pd.read_csv(diag / 'factor_regime_exposure_summary.csv')
print('registered', state.get('registered_factors'))
print('scorecard factors', score['factor_id'].nunique())
print('paper factors', paper['factor_id'].nunique())
print('regime factors', regime['factor_id'].nunique())
PY
```

Expected:

- registered factor count increases by the number of accepted new factors;
- scorecard/paper/regime/page coverage match the new total;
- no new signal factors are added.

## 9. Stop conditions

Stop and report if:

- candidate formulas duplicate existing factors;
- required input columns are missing;
- registry integrity fails;
- factor values cannot be computed;
- intake fails;
- full refresh would require modifying signal panel or strategy code;
- page integration fails due to payload size or schema mismatch.

Do not force a bad factor into the library.

## 10. Allowed files to change

Allowed code:

```text
scripts/factor_formula_registry.py
scripts/factor_ops.py       # only if necessary for reusable helper ops
```

Allowed generated outputs under canonical paths:

```text
research/factor_runs/crypto_top50_factor_library/factor_intake/pm25_controlled_factor_expansion_batch/
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/
research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/
research/factor_runs/crypto_top50_factor_library/factor_library_state.json
research/factor_runs/crypto_top50_factor_library/factor_library_state.md
reports/site/factor-library/factor-evaluation.html
```

Allowed docs:

```text
docs/factor_library/audits/pm25_controlled_factor_expansion_batch.md
```

Do not create new public pages or broad new docs.

## 11. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
feat: add controlled factor expansion batch
```

Final response should include:

- commit hash
- summary verdict
- new factor IDs
- intake status
- updated factor count
- scorecard/paper/regime summary for new factors
- page coverage
- limitations
- recommended next PM
