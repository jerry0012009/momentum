# PM-23B Prompt — Refresh Regime Diagnostics after Paper Portfolio Repair

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows:

- PM-21B: repaired single-factor paper portfolio data layer
- PM-22B: repaired paper portfolio page integration
- PM-23/PM-24: original BTC / market regime diagnostics and page integration

PM-22B audit states that PM-23/PM-24 regime diagnostics were built before PM-21B paper recalculation. Therefore regime diagnostics must be refreshed using repaired PM-21B paper monthly returns.

Do **not** update public HTML in PM-23B. PM-24B will refresh the page after PM-23B outputs are rebuilt.

## 0. PM objective

Refresh BTC / market regime diagnostics using the corrected PM-21B paper portfolio data.

The purpose is to make regime metrics consistent with repaired:

```text
single_factor_paper_monthly_returns.csv
single_factor_paper_summary.csv
single_factor_paper_page_payload.json
```

Specifically, PM-23B should verify and, if necessary, repair:

```text
scripts/build_factor_market_regime_diagnostics.py
```

so that paper-return regime diagnostics use PM-21B corrected monthly returns, especially fee_bps=10.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify signal panel construction.

Do **not** create or modify public HTML pages.

Do **not** change PM-21B paper portfolio outputs unless a schema incompatibility blocks regime refresh.

Do **not** fetch external market data.

Do **not** make production/live/tradeability/alpha claims.

## 2. Required inputs

Use current PM-21B repaired files:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_monthly_returns.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_page_payload.json
```

Use existing factor diagnostics:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_monthly_ic_series.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_monthly_long_short_series.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.csv
```

Use cached raw BTC data from:

```text
data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet
```

No external data.

## 3. Required outputs to regenerate

Regenerate these existing PM-23 outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/market_regime_monthly_labels.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_exposure_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_class_distribution.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_top_lists.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_diagnostics_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_market_regime_manifest.json
```

Do not create new regime output names unless necessary.

## 4. Required code checks / repairs

Inspect `scripts/build_factor_market_regime_diagnostics.py`.

Confirm:

1. It reads `single_factor_paper_monthly_returns.csv`.
2. It filters to selected `fee_bps`, default 10.
3. It uses `monthly_return` from PM-21B file directly.
4. It does not use stale summary-level paper returns.
5. It does not recompute paper monthly returns internally.
6. It joins by month consistently with BTC regime labels.
7. It handles all currently registered factors dynamically.

If any of the above is false, repair the script.

## 5. Required comparison with previous regime outputs

Before overwriting or after regeneration, compute a compact comparison if possible:

- previous regime dependency class distribution vs refreshed distribution;
- number of factors whose regime_dependency_class changed;
- top changed factors by paper_return_btc_beta or drawdown_minus_normal_paper_return;
- whether factor count remains unchanged.

If previous outputs are overwritten before comparison, still document the limitation.

## 6. Workflow integration

Use the existing workflow stage:

```bash
python scripts/run_factor_library_refresh.py --stage regime
```

If this stage is broken, repair it minimally.

Do not add a new workflow stage.

Update `REGENERATION_CONTRACT.md` or `factor_library_manifest.json` only if they still describe stale paper/regime dependencies.

## 7. Required audit

Create:

```text
docs/factor_library/audits/pm23b_refresh_regime_after_paper_repair.md
```

Audit must include:

1. Summary verdict:
   - `REGIME_REFRESH_AFTER_PAPER_REPAIR_PASS`
   - `REGIME_REFRESH_AFTER_PAPER_REPAIR_PASS_WITH_LIMITATIONS`
   - `REGIME_REFRESH_AFTER_PAPER_REPAIR_BLOCKED`
2. Explanation of why PM-23B was needed.
3. Files changed/regenerated.
4. Confirmation PM-21B paper monthly returns are used.
5. Selected fee_bps.
6. BTC symbol and month coverage.
7. Factor coverage count.
8. Regime dependency class distribution after refresh.
9. Changes versus previous PM-23 output if available.
10. Top regime-robust / bull-dependent / bear-dependent / drawdown-fragile factors after refresh.
11. Workflow command validation.
12. Limitations.
13. Non-change statement: no factors, formulas, factor_values, signal panel, public page.
14. Recommended next PM: PM-24B page refresh.

## 8. Validation

Run:

```bash
python -m py_compile scripts/build_factor_market_regime_diagnostics.py scripts/run_factor_library_refresh.py
python scripts/build_factor_market_regime_diagnostics.py --btc-symbol auto --fee-bps 10
python scripts/run_factor_library_refresh.py --stage regime --dry-run
python scripts/run_factor_library_refresh.py --stage regime
```

Then:

```bash
python - <<'PY'
import pandas as pd
from pathlib import Path
base = Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics')
paper = pd.read_csv(base / 'single_factor_paper_monthly_returns.csv')
expo = pd.read_csv(base / 'factor_regime_exposure_summary.csv')
summary = pd.read_csv(base / 'factor_regime_summary.csv')
labels = pd.read_csv(base / 'market_regime_monthly_labels.csv')
print('paper factors', paper['factor_id'].nunique(), 'paper fee values', sorted(paper['fee_bps'].unique()))
print('regime exposure factors', expo['factor_id'].nunique())
print('regime summary factors', summary['factor_id'].nunique())
print('months', len(labels))
print('dependency class distribution')
print(expo['regime_dependency_class'].value_counts(dropna=False).to_string())
PY
```

Expected:

- paper monthly returns cover all current factors;
- regime outputs cover all current factors;
- selected fee_bps is 10;
- no public HTML page changed.

## 9. Allowed files to change

Allowed script:

```text
scripts/build_factor_market_regime_diagnostics.py
scripts/run_factor_library_refresh.py   # only if regime stage is broken
```

Allowed regenerated outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/market_regime_monthly_labels.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_exposure_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_class_distribution.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_top_lists.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_diagnostics_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_market_regime_manifest.json
```

Allowed docs if needed:

```text
docs/factor_library/REGENERATION_CONTRACT.md
docs/factor_library/factor_library_manifest.json
docs/factor_library/audits/pm23b_refresh_regime_after_paper_repair.md
```

Do not modify:

```text
reports/site/factor-library/factor-evaluation.html
```

## 10. Stop conditions

Stop and report if:

- PM-21B paper monthly returns are missing required columns;
- regime outputs cannot join all factors;
- BTC symbol cannot be identified;
- workflow stage `regime` cannot be run without larger orchestration changes;
- implementation would require factor formula, factor_values, signal, or page changes.

## 11. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
fix: refresh regime diagnostics after paper repair
```

Final response should include:

- commit hash
- summary verdict
- factor coverage
- BTC regime coverage
- refreshed dependency class distribution
- changes versus previous regime outputs if available
- validation results
- limitations
- recommended next PM
