# PM-28: Quantile Shape, Rolling Stability & Direction-Aware Decile Diagnostics — Page Integration

**Date:** 2026-06-22
**Script:** `scripts/_build_factor_eval_html.py`
**Output:** `reports/site/factor-library/factor-evaluation.html`

---

## Summary

Integrated PM-26 (quantile shape & rolling stability) and PM-27B (direction-aware decile shape) compact payloads into the factor-evaluation.html detail panel. Each factor now displays a "Quantile Shape & Rolling Stability / 分位收益形状与滚动稳定性" section with:

1. **Summary badges** — quantile_shape_class, stability_class, decile_shape_class, shape_consistency_with_q5, expected_direction, direction_handling
2. **Q1–Q5 shape chart** — 5 bars showing mean returns per quantile (derived from expected_order_decile_returns pairs)
3. **Direction-aware D1–D10 decile chart** — 10 bars showing expected-order returns
4. **Rolling IC/LS stability chart** — 3M/6M bars from latest rolling values
5. **Interpretation notes** — bilingual (Chinese + English) for shape, stability, and decile

## Data Sources

| Payload | Size | Content |
|---------|------|---------|
| `factor_shape_stability_payload.json` | ~239KB | 71 factors × 4 horizons: quantile shape class, stability class, scores, notes |
| `factor_decile_shape_payload.json` | ~365KB | 71 factors × 4 horizons: 10 decile returns, direction-aware metrics, shape class, notes |

Q1–Q5 quantile returns are derived from the decile payload: `Q_i = mean(D_(2i-1), D_(2i))` from expected_order_decile_returns.

## Changes Made

### `scripts/_build_factor_eval_html.py`

1. **Payload loading** — Added loading of `factor_shape_stability_payload.json` and `factor_decile_shape_payload.json`
2. **Lookup maps** — Built `ss_map` and `ds_map` keyed by factor_id
3. **Factor data merge** — For each factor, merged shape/stability/decile data per horizon into `factor["shape_stability"]`
4. **CSS** — Added `.shape-badge` classes for shape/stability/decile badges (green/amber/red/purple scheme)
5. **JS label maps** — Added QUANTILE_SHAPE_LABELS, STABILITY_CLASS_LABELS, DECILE_SHAPE_LABELS, SHAPE_CONSISTENCY_LABELS, TAIL_CONC_LABELS, DIR_HANDLING_LABELS with bilingual labels
6. **JS helpers** — Added shapeBadge(), stabilityBadge(), decileShapeBadge(), shapeConsistencyBadge(), tailConcBadge()
7. **Detail panel section** — Added new section after regime diagnostics with badges, metric grid, Q1–Q5 bar chart, D1–D10 bar chart, rolling IC/LS mini-chart, and bilingual notes

### Preserved Sections

- Factor scoreboard table
- Quality scorecard summary
- Paper portfolio summary
- Regime diagnostics summary
- Factor detail: formula, intuition, direction, limitations, metrics, redundancy, monthly IC/LS, cumulative curve, paper portfolio, regime diagnostics
- All filters and sort functionality

## Validation Results

| Check | Result |
|-------|--------|
| `py_compile` | ✅ OK |
| Script execution | ✅ Wrote 2,531,869 bytes |
| 'Quantile Shape & Rolling Stability' in HTML | ✅ True |
| '分位收益形状与滚动稳定性' in HTML | ✅ True |
| 'quantile_shape_class' in HTML | ✅ True |
| 'stability_class' in HTML | ✅ True |
| 'decile_shape_class' in HTML | ✅ True |
| 'shape_consistency_with_q5' in HTML | ✅ True |
| 'expected_direction' in HTML | ✅ True |
| 'direction_handling' in HTML | ✅ True |
| 'Expected-order decile' in HTML | ✅ True |
| 'Single-Factor Paper Portfolio' in HTML | ✅ True |
| 'BTC / Market Regime Diagnostics' in HTML | ✅ True |
| '不是交易策略' in HTML | ✅ True |
| JS syntax check (node --check) | ✅ OK |
| Page size | ✅ 2.61MB (under 4MB target) |

## Size Budget

- Previous page: ~2.12MB
- New page: ~2.61MB
- Delta: +490KB (from ~605KB of compact payloads, reduced by JSON minification)
- Target: <4MB ✅

## Limitations

1. **Q1–Q5 returns are derived** — Not raw per-quantile mean returns; estimated as pair-means from decile data (D1+D2=Q1, ..., D9+D10=Q5). This is a reasonable approximation but not identical to the original 5-bucket quantile computation.
2. **Rolling IC/LS chart shows summary bars only** — The compact payloads contain latest 3M/6M values and min/max, not full time series. A full rolling line chart would require the raw monthly IC/LS series, which would significantly increase page size.
3. **No horizon-switching UI** — The section displays data for the factor's best_horizon only. Adding a horizon selector for the shape section would require additional UI work.
