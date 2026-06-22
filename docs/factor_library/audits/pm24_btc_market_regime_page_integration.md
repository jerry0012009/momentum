# PM-24: BTC Market Regime Page Integration

**Verdict:** MARKET_REGIME_PAGE_INTEGRATION_PASS

## Summary

Integrated BTC market regime diagnostics (PM-23 output) into the existing
`factor-evaluation.html` page. No new page created — all regime data is
embedded into the single-page factor library.

## Files Changed

| File | Action |
|------|--------|
| `scripts/_build_factor_eval_html.py` | Modified — added regime data loading, summary stats, filter, table columns, detail panel section |
| `reports/site/factor-library/factor-evaluation.html` | Rebuilt — 1,651,588 bytes (1.65 MB, well under 3.5 MB limit) |

## Data Sources Integrated

- `factor_regime_diagnostics_payload.json` — regime distribution counts, dependency class distribution
- `factor_regime_exposure_summary.csv` — 71 factors, per-factor BTC correlation/beta and regime metrics
- `factor_regime_summary.csv` — 1,491 rows of per-factor × per-regime breakdowns for chart rendering

## Coverage

- **71 / 71 factors** have regime diagnostics integrated (100% coverage from PM-23)
- Regime dependency class distribution:
  - REGIME_ROBUST: 22
  - BULL_DEPENDENT: 22
  - VOL_DEPENDENT: 12
  - DRAWDOWN_FRAGILE: 8
  - BEAR_DEPENDENT: 7
- BTC regime coverage: 25 months (2024-06 → 2026-06)
  - BULL: 9 / BEAR: 8 / SIDEWAYS: 8
  - HIGH_VOL: 13 / LOW_VOL: 12
  - NORMAL: 17 / DEEP_DRAWDOWN: 8

## Features Added

1. **Top summary section** "BTC / Market Regime Diagnostics Summary":
   - Regime dependency class distribution counts (5 classes)
   - BTC regime coverage (BULL/BEAR/SIDEWAYS, HIGH_VOL/LOW_VOL, NORMAL/DEEP_DRAWDOWN month counts)
   - Caveat: "Regime diagnostics identify conditional behavior, not trade rules"

2. **Table columns** (5 new):
   - Regime Dependency (with colored badge)
   - BTC Beta
   - BTC Corr
   - Bull-Bear Δ (with color coding)
   - DD Fragility / Drawdown Fragility

3. **Regime dependency filter dropdown** — filter by REGIME_ROBUST, BULL_DEPENDENT, BEAR_DEPENDENT, VOL_DEPENDENT, DRAWDOWN_FRAGILE

4. **Detail panel section** "BTC / Market Regime Diagnostics / BTC / 市场状态诊断":
   - Regime dependency badge with bilingual note
   - 8-metric grid: Paper-BTC Corr, Paper-BTC Beta, LS-BTC Corr, LS-BTC Beta, IC-BTC Corr, Bull−Bear Δ, HV−LV Δ, DD−Normal Δ
   - 4 inline SVG bar charts:
     * Paper Return by Trend Regime (BULL/BEAR/SIDEWAYS)
     * RankIC by Trend Regime
     * Paper Return by Volatility Regime (HIGH_VOL/LOW_VOL)
     * Paper Return by Drawdown Regime (NORMAL/DEEP_DRAWDOWN)
   - Bilingual caveat on conditional behavior interpretation

5. **Per-factor payload additions**:
   - `regime_dependency_class`, `paper_return_btc_corr`, `paper_return_btc_beta`
   - `long_short_btc_corr`, `long_short_btc_beta`, `ic_btc_return_corr`
   - `bull_minus_bear_paper_return`, `highvol_minus_lowvol_paper_return`, `drawdown_minus_normal_paper_return`
   - `main_regime_note_zh`, `main_regime_note_en`
   - `regime_detail` (chart data array)

## Validation Results

| Check | Result |
|-------|--------|
| "BTC / Market Regime Diagnostics" in HTML | ✅ (2 occurrences) |
| "BTC / 市场状态诊断" in HTML | ✅ (2 occurrences) |
| "regime_dependency_class" in HTML | ✅ (7 occurrences) |
| "REGIME_ROBUST" in HTML | ✅ (4 occurrences) |
| "BULL_DEPENDENT" in HTML | ✅ (4 occurrences) |
| "BEAR_DEPENDENT" in HTML | ✅ (4 occurrences) |
| "VOL_DEPENDENT" in HTML | ✅ (4 occurrences) |
| "DRAWDOWN_FRAGILE" in HTML | ✅ (4 occurrences) |
| "paper_return_btc_beta" in HTML | ✅ (4 occurrences) |
| "drawdown_minus_normal_paper_return" in HTML | ✅ (4 occurrences) |
| HTML size < 3.5 MB | ✅ (1.65 MB) |

## Limitations

- Regime detail data (`regime_detail` array) adds ~22 rows per factor to the embedded JSON payload, increasing page size by ~250 KB
- SVG charts use inline rendering with no interactivity (no tooltips or click-through)
- Regime labels are ex-post classifications; the page does not provide regime timing signals
- No REGENERATION_CONTRACT.md found; page dependency on regime files should be documented when contract is created
