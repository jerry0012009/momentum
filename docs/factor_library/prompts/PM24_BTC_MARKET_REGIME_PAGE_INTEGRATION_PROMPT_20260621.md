# PM-24 Prompt — Integrate BTC / Market Regime Diagnostics into Factor Evaluation Page

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-23:

- `docs/factor_library/audits/pm23_btc_market_regime_diagnostics.md`
- `scripts/build_factor_market_regime_diagnostics.py`
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/market_regime_monthly_labels.csv`
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_summary.csv`
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_exposure_summary.csv`
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_class_distribution.csv`
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_top_lists.csv`
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_diagnostics_payload.json`
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_market_regime_manifest.json`

PM-23 generated BTC / market regime diagnostics and integrated the script into the regeneration workflow. PM-24 should display this evidence in the existing factor-evaluation page.

Do **not** create a new public page.

## 0. PM objective

Upgrade existing:

```text
reports/site/factor-library/factor-evaluation.html
```

by updating:

```text
scripts/_build_factor_eval_html.py
```

The page should show, for each factor, whether its IC / long-short / paper portfolio evidence is regime-robust, bull-dependent, bear-dependent, vol-dependent, drawdown-fragile, or BTC-beta-sensitive.

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

Do **not** embed raw 1h BTC bar data into HTML.

## 2. Inputs

Use PM-23 compact outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/market_regime_monthly_labels.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_exposure_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_class_distribution.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_top_lists.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_diagnostics_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_market_regime_manifest.json
```

Use existing page data as already consumed by `_build_factor_eval_html.py`.

## 3. Required page changes

### 3.1 Top summary section

Add market regime summary cards:

- BTC monthly regime coverage: BULL / BEAR / SIDEWAYS counts;
- volatility regime coverage: HIGH_VOL / LOW_VOL counts;
- drawdown regime coverage: NORMAL / DEEP_DRAWDOWN counts;
- factor regime dependency class distribution;
- caveat: BTC regime diagnostics are conditional evidence, not trading rules.

### 3.2 Main table additions

Add or expose compact columns:

```text
Regime dependency / 市场状态依赖
BTC beta / BTC暴露
BTC corr / BTC相关
Bull-Bear Δ
Drawdown fragility / 回撤脆弱性
```

Preserve existing columns for scorecard, redundancy, paper viability, cost sensitivity, RankIC, Sharpe, drawdown, etc.

Add a filter:

```text
regime_dependency_class
```

### 3.3 Detail panel additions

Add section:

```text
BTC / Market Regime Diagnostics
BTC / 市场状态诊断
```

Show:

- `regime_dependency_class`;
- paper_return_btc_corr;
- paper_return_btc_beta;
- long_short_btc_corr;
- long_short_btc_beta;
- ic_btc_return_corr;
- bull_minus_bear_paper_return;
- highvol_minus_lowvol_paper_return;
- drawdown_minus_normal_paper_return;
- main_regime_note_zh;
- main_regime_note_en.

### 3.4 Charts

Use lightweight inline SVG or existing chart pattern. No external libraries.

Add at minimum:

1. **Regime paper return bar chart**
   - mean 10bps paper return by BULL / BEAR / SIDEWAYS.
2. **Regime IC bar chart**
   - mean RankIC by BULL / BEAR / SIDEWAYS.
3. **Volatility regime chart**
   - paper return or IC in HIGH_VOL vs LOW_VOL.
4. **Drawdown regime chart**
   - paper return in NORMAL vs DEEP_DRAWDOWN.
5. Optional compact BTC regime timeline:
   - monthly labels only, not raw bars.

If some values are missing due to insufficient months, display `insufficient data` and do not fake a value.

## 4. Data shaping

If `factor_regime_summary.csv` combines IC/LS/Paper metrics, parse it carefully by metric or value type. If the schema is insufficient, stop and report rather than guessing.

Prefer using `factor_regime_diagnostics_payload.json` if it already contains per-factor compact data.

Do not recompute regimes in the page builder. The page builder should consume PM-23 outputs.

## 5. Copy / interpretation

Add clear caveats:

- Regime diagnostics identify conditional behavior, not trade rules.
- BTC beta/correlation is based on monthly factor paper returns and BTC monthly returns.
- Regime classes depend on threshold choices from PM-23.
- A factor can be useful even if regime-dependent, but it should not be treated as universally robust.

## 6. Regeneration contract integration

Because PM-23 already added `regime` to `run_factor_library_refresh.py`, PM-24 should update only documentation references if needed:

- ensure `REGENERATION_CONTRACT.md` states that `page` depends on regime diagnostics;
- ensure `factor_library_manifest.json` lists the updated page dependency if manifest has such a field.

Do not create new workflow stages unless necessary.

## 7. Validation

Run:

```bash
python -m py_compile scripts/_build_factor_eval_html.py
python scripts/_build_factor_eval_html.py
```

Then:

```bash
python - <<'PY'
from pathlib import Path
html = Path('reports/site/factor-library/factor-evaluation.html').read_text(encoding='utf-8')
checks = [
  'BTC / Market Regime Diagnostics',
  'BTC / 市场状态诊断',
  'regime_dependency_class',
  'REGIME_ROBUST',
  'BULL_DEPENDENT',
  'BEAR_DEPENDENT',
  'VOL_DEPENDENT',
  'DRAWDOWN_FRAGILE',
  'paper_return_btc_beta',
  'drawdown_minus_normal_paper_return',
]
for c in checks:
    print(c, c in html)
print('html size bytes', len(html.encode('utf-8')))
PY
```

Expected:

- page contains regime diagnostics section;
- page remains reasonably sized, preferably < 3.5MB;
- existing scorecard/redundancy/paper diagnostics sections still work.

## 8. Required audit note

Create:

```text
docs/factor_library/audits/pm24_btc_market_regime_page_integration.md
```

Audit must include:

1. Summary verdict:
   - `MARKET_REGIME_PAGE_INTEGRATION_PASS`
   - `MARKET_REGIME_PAGE_INTEGRATION_PASS_WITH_LIMITATIONS`
   - `MARKET_REGIME_PAGE_INTEGRATION_BLOCKED`
2. Files changed.
3. Confirmation no new public page was created.
4. Regime data coverage joined to page: expected 71 vs actual.
5. Page features added.
6. Filters added.
7. HTML size before/after.
8. Validation results.
9. Limitations.
10. Non-change statement: no factors, formulas, factor_values, signal panel.
11. Recommended next PM.

## 9. Allowed files to change

Allowed script:

```text
scripts/_build_factor_eval_html.py
```

Allowed public output:

```text
reports/site/factor-library/factor-evaluation.html
reports/site/factor-library/assets/factor_diagnostics_payload.json
```

Allowed docs if needed:

```text
docs/factor_library/REGENERATION_CONTRACT.md
docs/factor_library/factor_library_manifest.json
docs/factor_library/audits/pm24_btc_market_regime_page_integration.md
```

Do not change PM-23 raw diagnostic outputs unless a schema bug blocks page integration. Document any such change.

## 10. Stop conditions

Stop and report if:

- regime outputs cannot join to 71 factors;
- `factor_regime_summary.csv` schema is not parseable;
- page size becomes too large;
- adding regime charts breaks existing scorecard/redundancy/paper sections;
- implementation would require recomputing factor_values or signal panel.

## 11. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
feat: integrate BTC regime diagnostics into factor page
```

Final response should include:

- commit hash
- summary verdict
- regime page coverage
- features added
- HTML size
- validation results
- limitations
- recommended next PM
