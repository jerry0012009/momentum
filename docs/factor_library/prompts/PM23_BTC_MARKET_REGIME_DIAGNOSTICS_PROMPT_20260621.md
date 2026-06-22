# PM-23 Prompt — BTC / Market Regime Factor Diagnostics

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-22:

- `docs/factor_library/audits/pm22_single_factor_paper_page_integration.md`
- `scripts/build_single_factor_paper_page_payload.py`
- `scripts/_build_factor_eval_html.py`
- `reports/site/factor-library/factor-evaluation.html`
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_monthly_returns.csv`
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_summary.csv`
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_monthly_ic_series.csv`
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_monthly_long_short_series.csv`

The factor page now shows scorecard, redundancy, and single-factor paper portfolio diagnostics. The next evidence layer is market regime sensitivity: whether factor evidence depends on BTC bull/bear/sideways states, high/low volatility, or BTC drawdown periods.

This task should build a data layer only. Do not update public HTML pages in PM-23. Page integration is PM-24.

## 0. PM objective

Build BTC / market regime diagnostics for all 71 factors.

The diagnostics should answer:

1. Does this factor work only in BTC bull or bear regimes?
2. Does RankIC deteriorate during BTC drawdowns?
3. Does the single-factor paper portfolio collapse in high-volatility regimes?
4. Is the factor paper return mostly BTC beta rather than cross-sectional alpha?
5. Which factors are regime-robust vs regime-dependent?

Research diagnostics only. No trading/live/production claims.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify `scripts/factor_formula_registry.py`.

Do **not** modify `scripts/factor_ops.py`.

Do **not** modify signal panel construction.

Do **not** rebuild signal panel.

Do **not** create or modify public HTML pages.

Do **not** fetch external market data. Use cached repository data only.

Do **not** use BTC regime diagnostics as proof of tradeability.

## 2. Inputs

Use cached raw bars:

```text
data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet
```

Use existing factor diagnostics:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_monthly_ic_series.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_monthly_long_short_series.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_monthly_returns.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.csv
```

If the BTC symbol naming is uncertain, detect it from `bars_1h.parquet` by searching symbols containing `BTC` and choose the canonical BTCUSDT perpetual symbol. Record the chosen symbol in manifest/audit.

## 3. Required script

Create:

```text
scripts/build_factor_market_regime_diagnostics.py
```

Recommended CLI:

```bash
python scripts/build_factor_market_regime_diagnostics.py \
  --btc-symbol auto \
  --fee-bps 10 \
  --output-dir research/factor_runs/crypto_top50_factor_library/factor_diagnostics
```

Arguments:

```text
--btc-symbol          auto by default
--fee-bps             paper portfolio fee assumption for regime analysis, default 10
--output-dir          diagnostics output directory
--min-months-per-regime default 3
```

## 4. Regime construction

Build monthly BTC regime labels.

Use BTC 1h close prices aggregated to monthly.

For each month compute:

```text
btc_monthly_return
btc_monthly_realized_vol
btc_monthly_max_drawdown
btc_rolling_3m_return
btc_drawdown_from_peak
```

Suggested regime labels:

```text
btc_trend_regime:
  BULL if btc_monthly_return >= +5%
  BEAR if btc_monthly_return <= -5%
  SIDEWAYS otherwise

btc_vol_regime:
  HIGH_VOL if monthly realized vol >= median monthly vol
  LOW_VOL otherwise

btc_drawdown_regime:
  DEEP_DRAWDOWN if drawdown_from_peak <= -20%
  NORMAL otherwise
```

Also include combined labels if useful:

```text
BULL_HIGH_VOL
BEAR_HIGH_VOL
SIDEWAYS_LOW_VOL
...
```

Keep thresholds explicit in manifest.

## 5. Required outputs

Write to:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/
```

Required files:

```text
market_regime_monthly_labels.csv
factor_regime_ic_summary.csv
factor_regime_long_short_summary.csv
factor_regime_paper_summary.csv
factor_regime_exposure_summary.csv
factor_regime_diagnostics_payload.json
factor_market_regime_manifest.json
```

### 5.1 `market_regime_monthly_labels.csv`

One row per month.

Required columns:

```text
month
btc_symbol
btc_monthly_return
btc_monthly_realized_vol
btc_monthly_max_drawdown
btc_rolling_3m_return
btc_drawdown_from_peak
btc_trend_regime
btc_vol_regime
btc_drawdown_regime
combined_regime
```

### 5.2 `factor_regime_ic_summary.csv`

One row per factor × regime dimension × regime value.

Required columns:

```text
factor_id
regime_dimension
regime_value
n_months
mean_rankic
median_rankic
rankic_positive_rate
mean_icir_proxy
regime_ic_strength_class
```

`regime_dimension` examples:

```text
btc_trend_regime
btc_vol_regime
btc_drawdown_regime
combined_regime
```

### 5.3 `factor_regime_long_short_summary.csv`

One row per factor × regime dimension × regime value.

Required columns:

```text
factor_id
regime_dimension
regime_value
n_months
mean_monthly_long_short_return
median_monthly_long_short_return
positive_month_rate
regime_ls_strength_class
```

### 5.4 `factor_regime_paper_summary.csv`

Use PM-21 paper monthly returns at selected fee bps, default 10bps.

One row per factor × regime dimension × regime value.

Required columns:

```text
factor_id
fee_bps
regime_dimension
regime_value
n_months
mean_monthly_paper_return
median_monthly_paper_return
positive_month_rate
regime_paper_strength_class
```

### 5.5 `factor_regime_exposure_summary.csv`

One row per factor.

Required columns:

```text
factor_id
fee_bps
paper_return_btc_corr
paper_return_btc_beta
long_short_btc_corr
long_short_btc_beta
ic_btc_return_corr
bull_minus_bear_paper_return
highvol_minus_lowvol_paper_return
drawdown_minus_normal_paper_return
regime_dependency_class
main_regime_note_zh
main_regime_note_en
```

Suggested `regime_dependency_class` values:

```text
REGIME_ROBUST
BULL_DEPENDENT
BEAR_DEPENDENT
VOL_DEPENDENT
DRAWDOWN_FRAGILE
BTC_BETA_SENSITIVE
INSUFFICIENT_REGIME_DATA
```

## 6. Interpretation rules

Do not overclaim.

A factor can be useful even if regime-dependent, but it should be labeled honestly.

Suggested rules:

- `REGIME_ROBUST`: not strongly dependent on trend/vol/drawdown, no extreme BTC beta.
- `BULL_DEPENDENT`: materially better in BULL than BEAR.
- `BEAR_DEPENDENT`: materially better in BEAR than BULL.
- `VOL_DEPENDENT`: materially different in HIGH_VOL vs LOW_VOL.
- `DRAWDOWN_FRAGILE`: poor paper returns or IC during DEEP_DRAWDOWN.
- `BTC_BETA_SENSITIVE`: high correlation/beta to BTC monthly return.
- `INSUFFICIENT_REGIME_DATA`: too few months in relevant regimes.

Document thresholds in audit and manifest.

## 7. Performance guidance

This should be relatively cheap.

Do not load factor_values again.

Use monthly diagnostics already generated:

- monthly IC series;
- monthly long-short series;
- PM-21 monthly paper returns.

Only raw BTC bars are needed to create monthly regime labels.

## 8. Required audit note

Create:

```text
docs/factor_library/audits/pm23_btc_market_regime_diagnostics.md
```

Audit must include:

1. Summary verdict:
   - `MARKET_REGIME_DIAGNOSTICS_PASS`
   - `MARKET_REGIME_DIAGNOSTICS_PASS_WITH_LIMITATIONS`
   - `MARKET_REGIME_DIAGNOSTICS_BLOCKED`
2. Files generated.
3. BTC symbol selected.
4. Month count and regime distribution.
5. Factor coverage: expected 71 vs actual.
6. Regime dependency class distribution.
7. Top 10 regime-robust factors.
8. Top 10 BTC-beta-sensitive factors.
9. Top 10 drawdown-fragile factors.
10. Limitations.
11. Non-change statement: no factors, formulas, factor_values, signal panel, public pages.
12. Recommended next PM.

## 9. Validation

Run:

```bash
python -m py_compile scripts/build_factor_market_regime_diagnostics.py
python scripts/build_factor_market_regime_diagnostics.py --btc-symbol auto --fee-bps 10
```

Then:

```bash
python - <<'PY'
import pandas as pd
from pathlib import Path
base = Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics')
labels = pd.read_csv(base / 'market_regime_monthly_labels.csv')
expo = pd.read_csv(base / 'factor_regime_exposure_summary.csv')
ic = pd.read_csv(base / 'factor_regime_ic_summary.csv')
paper = pd.read_csv(base / 'factor_regime_paper_summary.csv')
print('months', len(labels))
print('trend regimes')
print(labels['btc_trend_regime'].value_counts(dropna=False))
print('expo rows', len(expo), 'factors', expo['factor_id'].nunique())
print('ic factors', ic['factor_id'].nunique(), 'paper factors', paper['factor_id'].nunique())
print('dependency classes')
print(expo['regime_dependency_class'].value_counts(dropna=False))
PY
```

Expected:

- regime labels cover the monthly evaluation period;
- exposure summary covers 71 factors;
- output files are not huge;
- no public HTML page changes.

## 10. Allowed files to change

Allowed script:

```text
scripts/build_factor_market_regime_diagnostics.py
```

Allowed outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/market_regime_monthly_labels.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_ic_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_long_short_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_paper_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_exposure_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_diagnostics_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_market_regime_manifest.json
```

Allowed audit:

```text
docs/factor_library/audits/pm23_btc_market_regime_diagnostics.md
```

Do not update public HTML pages in PM-23.

## 11. Stop conditions

Stop and report if:

- BTC symbol cannot be reliably identified;
- monthly regime labels cannot align with factor monthly diagnostics;
- too few months make all regime labels meaningless;
- implementation would require changing factor formulas, factor_values, or signal panel logic;
- external data would be required.

## 12. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
feat: add BTC market regime diagnostics
```

Final response should include:

- commit hash
- summary verdict
- BTC symbol selected
- month/regime coverage
- factor coverage
- regime dependency class distribution
- top robust / beta-sensitive / drawdown-fragile factors
- limitations
- recommended next PM
