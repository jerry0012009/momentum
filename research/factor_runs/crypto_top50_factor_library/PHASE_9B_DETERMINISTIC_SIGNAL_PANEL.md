# Phase 9B Closeout — Deterministic Signal Panel Implementation

> Date: 2026-06-15
> Previous phase: Phase 9A-R2 COMPLETE
> Scope: Deterministic signal panel computation only
> PM decision: Build structured multi-factor signal panels using Phase 9A-R2 architecture

---

## Status

Phase 9B: COMPLETE, pending PM review.
Phase 10: NOT STARTED.

---

## 1. Implementation

Phase 9B computed deterministic signal panels from exactly 10 CANDIDATE_REVIEW factors using the PM-approved Phase 9A-R2 structured architecture.

### Factors Used

| Factor | Channel | Role |
|--------|---------|------|
| vol_5h | RISK_PRESSURE | CORE_RISK_REVERSION |
| vol_40h | RISK_PRESSURE | CORE_RISK_REVERSION |
| downside_vol_20h | RISK_PRESSURE | CORE_RISK_REVERSION |
| vol_of_vol_20h | RISK_PRESSURE | CORE_RISK_REVERSION |
| rsi_7h | TECHNICAL_REVERSION | OSCILLATOR_EXHAUSTION |
| rsi_28h | TECHNICAL_REVERSION | OSCILLATOR_EXHAUSTION |
| xs_rank_vol | LIQUIDITY_GATE | LIQUIDITY_PARTICIPATION_GATE |
| range_1h | RANGE_POSITION | POSITION_TIMING_OVERLAY |
| range_4h | RANGE_POSITION | POSITION_TIMING_OVERLAY |
| price_pos_24h | RANGE_POSITION | POSITION_TIMING_OVERLAY |

### Cross-Sectional Transformations (per timestamp)

1. Winsorize: 1st/99th percentile clip
2. Z-score normalization
3. Direction-adjust: negative factors (vol_5h, vol_40h, downside_vol_20h, vol_of_vol_20h, rsi_7h, rsi_28h) sign-flipped
4. Overlay: range_1h, range_4h, price_pos_24h sign-flipped (v0 mean-reversion hypothesis)
5. Liquidity gate: xs_rank_vol mapped to [0.50, 1.00] via rank percentile
6. Position overlay multiplier: clip(1 + 0.15 * overlay, 0.85, 1.15)

### Signal Formulas

1. `risk_pressure_component` = mean(-z(vol_5h), -z(vol_40h), -z(downside_vol_20h), -z(vol_of_vol_20h))
2. `oscillator_exhaustion_component` = mean(-z(rsi_7h), -z(rsi_28h))
3. `raw_core_score` = 0.60 × risk_pressure + 0.40 × oscillator_exhaustion
4. `signal_v0_core_only` = xs_zscore(raw_core_score)
5. `signal_v0_pm_full_structured` = xs_zscore(raw_core_score × liquidity_gate × position_overlay_multiplier)
6. `signal_v0_family_balanced_diagnostic` = xs_zscore(0.25×risk + 0.25×osc + 0.25×pos + 0.25×liq_centered)

---

## 2. Output Summary

| Metric | Value |
|--------|-------|
| Total rows | 3,314,397 |
| Timestamps | 17,801 |
| Symbols | 266 |
| Date range | 2024-06-01 to 2026-06-13 |
| Signals | 3 diagnostic |
| Components | 6 |

### 3 Diagnostic Signals

- `signal_v0_core_only`: risk pressure + oscillator (6 factors), z-scored
- `signal_v0_pm_full_structured`: core × liquidity gate × position overlay (10 factors), z-scored — **PM-preferred v0**
- `signal_v0_family_balanced_diagnostic`: 4-channel equal weight (10 factors), z-scored — **diagnostic only**

---

## 3. Deliverables

| Deliverable | File | Description |
|-------------|------|-------------|
| Closeout | `PHASE_9B_DETERMINISTIC_SIGNAL_PANEL.md` | This document |
| Script | `scripts/build_phase9b_signal_panel.py` | Reproducible signal panel builder |
| Manifest | `phase9b_signal_panel_manifest.csv` | 3-signal manifest |
| Component manifest | `phase9b_signal_component_manifest.csv` | 6-component manifest |
| Coverage | `phase9b_signal_coverage_summary.csv` | Coverage and statistics |
| Quality checks | `phase9b_signal_quality_checks.csv` | 11 quality checks |
| Signal panel | `phase9b_signal_panel.parquet` | 3.3M rows, 3 signals |

---

## 4. Negative Declarations

- **No backtest was run.** Phase 9B computes signal values only.
- **No PnL was computed.**
- **No portfolio simulation was created.**
- **No alpha claim was made.** All outputs are diagnostic.
- **No labels or forward returns were used.**
- **No weights were optimized.**
- **Phase 10 has not started.**
- **Phase 10 requires PM approval after 9B review.**

---

## 5. Next Required PM Decision

Phase 10 (backtest / evaluation) may **only** begin after:

1. PM reviews Phase 9B signal panels.
2. PM explicitly approves entry into Phase 10.
3. Phase 10 scope is defined (which signals to evaluate, evaluation protocol).

**No action is taken automatically.** All decisions require explicit PM approval.
