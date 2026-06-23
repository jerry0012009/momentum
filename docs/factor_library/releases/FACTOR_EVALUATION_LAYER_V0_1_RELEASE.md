# Factor Evaluation Layer v0.1 — Release Freeze

**PM-48** | 2026-06-23 | `FACTOR_EVALUATION_LAYER_V0_1_RELEASE_PASS`

---

## 1. Release Summary

Factor Evaluation Layer v0.1 is frozen at **78 factors** across 24 families.
All factors pass post-intake workflow integrity (19/19 dimensions each).
The public page (`factor-evaluation.html`) displays 78/78 factors with complete diagnostics.
No signal construction, portfolio logic, or live trading code is included.

---

## 2. Current Factor Count

| Source | Count |
|--------|-------|
| `factor_library_state.json` — registered | 78 |
| `factor_library_state.json` — computed | 78 |
| `factor_unified_profile_summary.csv` | 78 |
| `factor_diagnostics_summary.csv` | 78 |
| `factor-evaluation.html` (public page) | 78 |

Zero missing. Zero gaps.

---

## 3. Scope IN (what v0.1 covers)

- **RankIC** — per-horizon rank information coefficient with t-stat, IR, win rate
- **Long-Short** — spread mean, Sharpe, annualized return/vol, max drawdown, monthly win rate
- **Paper Portfolio** — single-factor paper diagnostics (gross Sharpe, turnover, fee sensitivity)
- **Fee Sensitivity** — 10bps return, breakeven fee, cost sensitivity class
- **Regime / BTC** — bull/bear/vol/drawdown regime exposure, LS-BTC Corr/Beta
- **Quantile Shape** — 5-bucket return shape, Q5 classification, nonlinear/convex/concave
- **Rolling Stability** — shape stability over rolling windows
- **Decile Shape** — direction-aware 10-bin shape diagnostics
- **Capacity / Liquidity** — selected-basket turnover, liquidity fragility, capacity proxy
- **Redundancy / Cluster / Marginal** — pairwise Spearman, cluster ID, marginal info value
- **Scorecard** — weighted quality score with confidence, quality class, recommended action
- **Unified Profile** — evidence matrix, workflow readiness, profile class
- **Page** — single HTML with all sections, bilingual (ZH/EN), sortable, filterable
- **QA** — 26-check page completeness script + 19-dimension integrity checker

---

## 4. Scope OUT (not in v0.1)

- Signal panel construction
- Entry / exit logic
- Position sizing
- Portfolio construction
- Live trading code
- Multi-factor combination
- Execution / order management

---

## 5. Canonical Data Sources

| Metric | Primary Source | Fallback Source |
|--------|---------------|-----------------|
| RankIC mean/t_stat | `factor_diagnostics_summary.csv` | `factor_level_rankic_summary.csv` |
| LS Sharpe/Max DD | `factor_diagnostics_summary.csv` | `factor_level_long_short_summary.csv` |
| Monthly IC series | `factor_monthly_ic_series.csv` | `factor_level_period_ic_summary.csv` |
| Monthly LS series | `factor_monthly_long_short_series.csv` | `factor_level_period_long_short_summary.csv` |
| Best horizon | `factor_diagnostics_summary.csv` | `factor_level_coverage_summary.csv` |
| Redundancy | `factor_diagnostics_summary.csv` | `factor_unified_profile_summary.csv` |
| Regime | `factor_regime_exposure_summary.csv` | `factor_regime_diagnostics_payload.json` |
| Paper | `single_factor_paper_page_payload.json` | `single_factor_paper_portfolio_diagnostics*.csv` |

---

## 6. Defensive Fallback Rules

1. **Dual-source LS aggregate**: Page builder reads `factor_diagnostics_summary.csv` first; falls back to `factor_level_long_short_summary.csv` for missing Sharpe/AnnRet/MaxDD.
2. **Dual-source RankIC**: Same pattern — diagnostics first, then canonical rankic summary.
3. **Period IC batch merge**: Monthly IC data may be in batch files (`factor_level_period_ic_summary_*.csv`). Merge via concat+dedup on `(factor_name, horizon, period)`.
4. **Stale scorecard override**: Scorecard with `rankic_mean=0 AND coverage_rate=0` is stale. Override with unified profile data.
5. **Redundancy reconciliation**: `redundancy_cluster_id=-1` or `INSUFFICIENT_OVERLAP` → fall back to profile `cluster_member_role`.
6. **Stale warning clearing**: `source_warning` containing `no_horizon_data` or `monthly_ls_unavailable` is cleared when `rankic_mean` exists.
7. **LS-BTC Corr**: Regime script receives `--canonical-ls-path` to auto-merge missing factors.

---

## 7. Post-Intake Workflow

After new factor intake, run:

```bash
python scripts/run_post_intake_workflow_completion.py --factor-ids <ids>
```

**15 stages** (PM-46 updated runner):

1. **evaluate** — factor-level RankIC/LS evaluation
2. **paper-diagnostics** — single-factor paper portfolio diagnostics
3. **paper-page-payload** — paper page JSON payload
4. **diagnostics-metrics** — cumulative LS, monthly IC/LS series, diagnostics summary
5. **redundancy** — pairwise Spearman redundancy matrix
6. **cluster** — redundancy cluster + marginal information
7. **regime** — BTC/market regime diagnostics (uses canonical IC/LS merge)
8. **shape-stability** — quantile shape + rolling stability
9. **decile** — direction-aware decile shape
10. **capacity** — capacity/liquidity proxy diagnostics
11. **scorecard** — weighted quality scorecard
12. **profile** — unified factor profile + evidence matrix
13. **page** — rebuild factor-evaluation.html
14. **page-qa** — 26-check page completeness
15. **integrity-qa** — 19-dimension workflow integrity check

Verify with:

```bash
python scripts/check_post_intake_workflow_integrity.py --factor-ids <ids>
```

19 dimensions per factor.

---

## 8. QA Commands

```bash
# Page completeness (26 checks)
python scripts/check_factor_evaluation_page_completeness.py

# Workflow integrity (19 dimensions × N factors)
python scripts/check_post_intake_workflow_integrity.py --all

# Staleness monitor
python scripts/check_factor_library_staleness.py

# Registry integrity
python scripts/check_factor_registry_integrity.py
```

---

## 9. Known Limitations

1. **Stale `source_warning` in diagnostics CSV**: PM-35 5 factors have `no_horizon_data;monthly_ls_unavailable` in `factor_diagnostics_summary.csv`. Page builder clears these at render time. No visible gap.
2. **LS aggregate legacy fallback**: 71/78 factors use `factor_diagnostics_summary.csv` for LS Sharpe/AnnRet/MaxDD (canonical `factor_level_long_short_summary.csv` has NaN for these from older batches). Page displays correctly.
3. **No live validation**: All diagnostics use historical 1h bars. No live paper trading feed.
4. **Single universe**: Only `crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1`.
5. **11 factors NEEDS_REVIEW**: `klow_close`, `tech_atr`, `xs_rank_vol`, `xs_rank_ret_1h`, `vol_ratio_20_80`, `qvol_ma_ratio_5_20`, `qvol_ma_ratio_20_80`, `candle_wick_lower`, `vol_ratio_5_20`, `taker_buy_zscore_20h`, `taker_buy_delta_5h`.

---

## 10. Recommended Next Stage

**Primary: PM-49 — Factor Interpretation / Research Review Layer**

- Explain factor mechanism (why does this factor predict?)
- Review `expected_direction` against empirical evidence
- Classify each factor: keep / review / repair / low priority
- Prepare candidate pool for signal construction
- No signal construction yet

**Alternative: PM-49 — v0.1 tag + deployment hardening**
- Git tag `v0.1-eval-layer`
- Docker/CI for automated refresh
- Monitoring + alerting

**Future (not next): Signal Construction Layer v0.1**
Signal construction should only start after factor interpretation and candidate selection are complete.
