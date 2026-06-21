# PM-12 Factor Diagnostics Product Spec and Gap Audit

**Date:** 2026-06-21
**Type:** Read-only spec / gap audit. No code changes, no chart builds, no metric computation.

---

## 1. Current State Verification

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| Registered factors | 71 | 71 | ✅ |
| Computed factor_values | 71 | 71 | ✅ |
| Missing factor_values | 0 | 0 | ✅ |
| Missing input | 0 | 0 | ✅ |
| Signal factors | 10 | 10 | ✅ |
| Signal variants | 3 | 3 | ✅ |
| Warnings | 0 | 0 | ✅ |

**Verdict: Factor library data layer is COMPLETE.**

## 2. Existing Artifact Inventory

### 2.1 Evaluation Outputs (factor_level_evaluation/)

| Artifact | Rows | Key Fields | Status |
|----------|------|------------|--------|
| factor_level_metric_panel.csv | 260 (65×4h) | IC, ICIR, t-stat, long-short spread, win rate | ✅ Rich |
| factor_level_rankic_summary.csv | 260 | mean_rank_ic, t_stat, coverage | ✅ |
| factor_level_long_short_summary.csv | 236 | bucket returns, long-short spread | ✅ |
| factor_level_period_ic_summary.csv | 5900 | period-level IC (monthly granularity) | ✅ |
| factor_level_quantile_return_summary.csv | 1180 | bucket-level returns by horizon | ✅ |
| factor_level_coverage_summary.csv | 65 | coverage, best horizon | ✅ |
| factor_redundancy.csv | 6 | pairwise Spearman correlation | ⚠️ Sparse |
| factor_catalog.json | 65 | IC fields, recommendation | ✅ No bilingual |

### 2.2 Public Pages (reports/site/factor-library/)

| Page | Status | Issues |
|------|--------|--------|
| index.html | ✅ | Clean entry point |
| actual-script-map.html | ✅ | Bilingual pipeline map |
| factor-evaluation.html | ✅ | Basic IC display |
| signal-evaluation-summary.html | ✅ | Signal-level summary |
| _archive/ (21 pages) | ✅ | Historical, not in nav |

### 2.3 Scripts

| Script | Role | Status |
|--------|------|--------|
| evaluate_factors.py | Factor-level IC, quantile returns, coverage | ✅ |
| build_factor_conclusion_cards.py | Decision cards per factor | ✅ |
| generate_intake_report.py | Markdown intake report | ✅ |
| build_phase9b_signal_panel.py | Signal construction | ✅ (not modified) |
| evaluate_signals.py | Signal-level evaluation | ✅ |

## 3. User-Need Gap Table

| # | User Need | Existing Artifact | Existing Status | Gap | Recommended Next PM | Risk |
|---|-----------|-------------------|-----------------|-----|---------------------|------|
| 1 | Bilingual factor names/explanations | factor_catalog.json | No bilingual fields | name_en/zh, formula_en/zh, intuition_en/zh missing | PM-14 | LOW |
| 2 | Factor formula + intuition display | factor_catalog.json | formula_proxy exists | No intuition, no bilingual formula | PM-14 | LOW |
| 3 | Monthly IC series | period_ic_summary.csv | Has monthly data | Not aggregated to monthly IC curve CSV | PM-13 | LOW |
| 4 | Monthly long-short return | quantile_return_summary.csv | Has bucket data | No monthly LS aggregation, no long/short leg decomposition | PM-13 | LOW |
| 5 | Cumulative LS equity curve | — | Not computed | Need cumulative product of monthly LS returns | PM-15 | MED |
| 6 | Sharpe ratio | metric_panel.csv | Has long_short_spread_mean | No annualized Sharpe, no std | PM-13 | LOW |
| 7 | Annualized return / vol | — | Not computed | Need monthly LS returns → annualize | PM-13 | LOW |
| 8 | Max drawdown | — | Not computed | Need cumulative curve → peak-to-trough | PM-15 | MED |
| 9 | Monthly hit rate | period_ic_summary.csv | Has ic_win_rate | Not aggregated as positive-month ratio for LS | PM-13 | LOW |
| 10 | ICIR / RankIC stability | metric_panel.csv | Has ICIR, t-stat | Already available; needs display | PM-15 | LOW |
| 11 | Coverage / missingness | coverage_summary.csv | Has coverage | Not displayed on public pages | PM-15 | LOW |
| 12 | Redundancy clustering | factor_redundancy.csv | 6 pairs only | Sparse; needs full pairwise or clustering | PM-13 | MED |
| 13 | Decision bucket | candidate_review.csv | Has review_bucket | Not surfaced on diagnostic pages | PM-16 | LOW |
| 14 | Horizon-specific best metric | coverage_summary.csv | Has best_adj_ic_horizon | Not displayed per-factor | PM-15 | LOW |
| 15 | Public page usability | 4 pages exist | Basic | No bilingual, no diagnostic charts | PM-15 | MED |

## 4. Target Diagnostics Artifact Schemas

### 4.1 `factor_diagnostics_summary.csv/json`

**Granularity:** One row per factor (best horizon fields).

**Rationale:** Per-factor row avoids 4× duplication. Horizon-specific details in separate monthly series files.

```
factor_id                   # str
family                      # str
lifecycle_status            # str
name_en                     # str (PM-14)
name_zh                     # str (PM-14)
formula_short               # str (PM-14)
formula_zh                  # str (PM-14)
intuition_en                # str (PM-14)
intuition_zh                # str (PM-14)
required_columns            # str (comma-separated)
expected_direction          # str
best_horizon                # str (1h/4h/24h/72h)
rankic_mean                 # float (best horizon)
rankic_std                  # float
rankic_ir                   # float
rankic_t_stat               # float
monthly_ic_positive_rate    # float (fraction of months with positive IC)
long_short_mean             # float (monthly LS return mean)
long_short_std              # float
long_short_sharpe           # float (annualized: mean/std * sqrt(12))
long_short_annualized_return # float
long_short_annualized_vol   # float
long_short_max_drawdown     # float
long_short_positive_month_rate # float
coverage_rate               # float
redundancy_level            # str (NONE/LOW/MODERATE/HIGH)
nearest_redundant_factor    # str
decision_bucket             # str (from candidate_review)
recommended_action          # str
```

### 4.2 `factor_monthly_ic_series.csv`

**Granularity:** One row per factor × horizon × month.

```
factor_id, horizon, month, rank_ic, rank_ic_adj, n_obs, positive_ic
```

**Source:** Derivable from `factor_level_period_ic_summary.csv` (period column is monthly).

### 4.3 `factor_monthly_long_short_series.csv`

**Granularity:** One row per factor × horizon × month.

```
factor_id, horizon, month, long_short_return, long_leg_return, short_leg_return, n_long, n_short, positive_ls
```

**Source:** Derivable from `factor_level_quantile_return_summary.csv` (bucket 5 = top, bucket 1 = bottom).

### 4.4 `factor_cumulative_long_short_curve.csv`

**Granularity:** One row per factor × horizon × month.

```
factor_id, horizon, month, long_short_return, cum_long_short_return, drawdown
```

**Source:** Computed from 4.3 cumulative product.

### 4.5 `factor_bilingual_cards.json`

**Granularity:** One object per factor.

```
factor_id, name_en, name_zh, family_en, family_zh,
formula_en, formula_zh, intuition_en, intuition_zh,
required_columns, expected_direction_explanation_en, expected_direction_explanation_zh,
known_limitations_en, known_limitations_zh, status_explanation_en, status_explanation_zh
```

**Source:** Requires manual/human-authored bilingual content. PM-14.

## 5. Metric Formula Definitions

| Metric | Formula | Assumptions |
|--------|---------|-------------|
| Monthly IC | Mean of daily rank IC within each month | From period_ic_summary |
| Monthly LS return | (top_bucket_return - bottom_bucket_return) per month | From quantile_return_summary |
| Cumulative LS curve | ∏(1 + monthly_LS_return) - 1 | Compound returns, not log |
| Sharpe ratio | mean(monthly_LS) / std(monthly_LS) × √12 | Monthly frequency, annualized |
| Annualized return | mean(monthly_LS) × 12 | Simple annualization |
| Annualized vol | std(monthly_LS) × √12 | Monthly vol × √12 |
| Max drawdown | max(peak - trough) / peak of cumulative curve | Peak-to-trough |
| Positive month rate | count(months where LS > 0) / total_months | |
| ICIR | mean(rank_ic) / std(rank_ic) | Per horizon |
| Coverage | fraction of non-null factor_values | From coverage_summary |

## 6. Recommended Implementation Sequence

| Phase | Task | Scope | Depends On |
|-------|------|-------|------------|
| PM-13 | Factor Diagnostics Metrics Builder | Compute monthly IC series, monthly LS returns, cumulative curve, Sharpe, annualized return/vol, max drawdown, positive month rate from existing evaluation outputs. Generate factor_diagnostics_summary.csv/json, factor_monthly_ic_series.csv, factor_monthly_long_short_series.csv, factor_cumulative_long_short_curve.csv. | — |
| PM-14 | Bilingual Factor Cards | Generate factor_bilingual_cards.json with name/formula/intuition in EN+ZH. Requires human review for quality. | — |
| PM-15 | Static Diagnostic Pages | Build/upgrade public HTML pages with IC charts, LS curves, coverage tables, Sharpe/drawdown display. Bilingual. | PM-13, PM-14 |
| PM-16 | Factor Quality Decision Framework | Scorecard combining IC quality, LS performance, redundancy, coverage into decision buckets. Surfaced on pages. | PM-13 |
| PM-17 | Next Factor Expansion / Signal Redesign | Only after diagnostics are decision-grade. | PM-15, PM-16 |

## 7. Non-Change Statement

- No factors added or modified
- No factor formulas changed
- No scripts modified
- No public pages rebuilt
- No signal panel changes
- No production/live/tradeability/alpha claims
- No charts or metrics computed (spec only)
