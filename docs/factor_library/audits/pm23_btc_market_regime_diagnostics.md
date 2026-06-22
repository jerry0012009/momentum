# PM-23: BTC Market Regime Diagnostics — Audit

**Verdict: MARKET_REGIME_DIAGNOSTICS_PASS**
**Date:** 2026-06-22
**Status:** Research diagnostics only. NOT production. NOT live trading.

---

## 1. Scope

Add BTC market regime diagnostics to the factor library pipeline:
- Classify each month by BTC trend, volatility, and drawdown regime
- Analyse how each factor's performance varies across regimes
- Compute per-factor BTC-correlation/beta exposure
- Classify each factor by regime dependency

**No changes to:** factor formulas, factor_values, signal composition, public page, or live trading.

---

## 2. BTC Symbol & Month Coverage

| Metric | Value |
|--------|-------|
| BTC symbol | BTCUSDT (auto-detected) |
| Months covered | 25 (2024-06 to 2026-06) |
| Trend regime | BULL: 9, BEAR: 8, SIDEWAYS: 8 |
| Volatility regime | HIGH_VOL: 13, LOW_VOL: 12 |
| Drawdown regime | NORMAL: 17, DEEP_DRAWDOWN: 8 |
| Fee bps | 10 |
| Min months per regime | 3 |

---

## 3. Factor Coverage

| Metric | Value |
|--------|-------|
| Total factors analysed | **71** (all registered factors) |
| Factors with IC data | 71 |
| Factors with LS data | 71 |
| Factors with Paper data | 71 |
| Coverage | **100%** |

---

## 4. Regime Dependency Class Distribution

| Class | Count | Description |
|-------|-------|-------------|
| REGIME_ROBUST | 22 | Consistent across all BTC regimes |
| BULL_DEPENDENT | 22 | Stronger in BTC bull months |
| VOL_DEPENDENT | 12 | Performance varies with BTC volatility |
| DRAWDOWN_FRAGILE | 8 | Underperforms during deep drawdowns |
| BEAR_DEPENDENT | 7 | Stronger in BTC bear months |
| BTC_BETA_SENSITIVE | 0 | (no factor had beta > 0.5) |
| INSUFFICIENT_REGIME_DATA | 0 | (all factors had sufficient data) |

---

## 5. Top 10 Regime-Robust Factors

These factors show the most consistent BTC-correlation across regimes:

| Factor | Paper-BTC Corr | Paper-BTC Beta |
|--------|---------------|----------------|
| vol_zscore_20h | 0.002 | 0.002 |
| ma_gap_20_80 | 0.002 | 0.003 |
| rsi_14h | -0.018 | -0.024 |
| price_pos_72h | 0.020 | 0.028 |
| vol_ratio_5_20 | 0.030 | 0.034 |
| rsi_28h | -0.034 | -0.047 |
| xs_rank_ret_1h | -0.036 | -0.057 |
| intraday_ret | -0.043 | -0.067 |
| rsi_7h | -0.057 | -0.077 |
| qvol_zscore_20h | 0.066 | 0.077 |

---

## 6. Top 10 BTC-Beta-Sensitive Factors

No factors classified as BTC_BETA_SENSITIVE (threshold: |beta| > 0.5 or |LS-BTC corr| > 0.5).
All factors had relatively low BTC beta, suggesting the factor library is broadly diversified away from BTC directional exposure.

---

## 7. Top 10 Drawdown-Fragile Factors

These factors perform worst (relative to normal periods) during deep BTC drawdowns:

| Factor | DD minus Normal Paper Return |
|--------|------------------------------|
| rev_1h | -0.122 |
| williams_r_14h | -0.106 |
| rev_3h | -0.084 |
| wq101_alpha12 | -0.074 |
| wq101_alpha53 | -0.068 |
| rev_72h | -0.067 |
| reversal_5h | -0.063 |
| candle_wick_lower | -0.062 |

Short-term reversal and momentum reversal factors dominate the drawdown-fragile list.

---

## 8. Integration Status

| Item | Status |
|------|--------|
| Script created | `scripts/build_factor_market_regime_diagnostics.py` |
| Regeneration contract updated | Yes — `regime` stage after `redundancy`, before `page` |
| `run_factor_library_refresh.py` updated | Yes — supports `--stage regime` |
| `factor_library_manifest.json` updated | Yes — new script and output files listed |
| New public page | **No** — diagnostics CSV/JSON only, no HTML page |
| Factor/formula changes | **None** |
| Signal composition changes | **None** |

---

## 9. Output Files

All in `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/`:

1. `market_regime_monthly_labels.csv` — 25 months × 14 columns (regime labels per month)
2. `factor_regime_summary.csv` — 1,491 rows (factor × regime dimension × regime value × metric)
3. `factor_regime_exposure_summary.csv` — 71 rows (per-factor BTC exposure + classification)
4. `factor_regime_class_distribution.csv` — 71 rows (simplified classification view)
5. `factor_regime_top_lists.csv` — curated top-10 lists per class
6. `factor_regime_diagnostics_payload.json` — machine-readable summary
7. `factor_market_regime_manifest.json` — script metadata

---

## 10. Commands

```bash
# Regenerate regime diagnostics standalone
python scripts/build_factor_market_regime_diagnostics.py --btc-symbol auto --fee-bps 10

# Via pipeline orchestrator
python scripts/run_factor_library_refresh.py --stage regime

# Included in cheap refresh
python scripts/run_factor_library_refresh.py --stage cheap
```

---

## 11. Guardrails

- No factor formulas modified
- No factor_values recomputed
- No signal composition changed
- No new public page created
- No production/tradeability claims
- Research diagnostics only
