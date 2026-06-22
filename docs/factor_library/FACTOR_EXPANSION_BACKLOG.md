# Factor Expansion Backlog — PM-34

Generated: 2026-06-22 17:18 UTC

Current library: **71 factors** across **23 families**

---

## BATCH_01_CONTROLLED_INTAKE — Recommended for Next Intake

**5 candidates** selected for controlled intake:

| # | Factor ID | Family | Direction | Redundancy Risk | Complexity | Diagnostic Value |
|---|-----------|--------|-----------|-----------------|------------|-----------------|
| 1 | `rev_2h` | short_term_reversal | positive | LOW | LOW | — |
| 2 | `mom_vol_adjusted_20h` | medium_term_momentum | positive | LOW | LOW | — |
| 3 | `range_breakout_vol_confirm_20h` | range_breakout | positive | LOW | LOW | — |
| 4 | `volume_pressure_20h` | volume_pressure | positive | LOW | LOW | — |
| 5 | `xs_rank_mom_accel` | cross_sectional_rank_acceleration | positive | LOW | MEDIUM | — |

---

### Candidate Details — BATCH_01

#### `rev_2h` (short_term_reversal)

- **Theme:** 2-hour reversal signal filling gap between 1h and 3h lookbacks
- **Formula:** `-(close / delay(close, 2) - 1)`
- **Required inputs:** close
- **Available inputs:** PASS — close available in standard OHLCV cache
- **Operator reuse:** delay() from factor_ops
- **New operator needed:** NO
- **New data needed:** NO
- **Expected direction:** positive
- **Direction basis:** Short-term mean reversion: recent losers rebound within 2h in crypto microstructure
- **Cluster overlap:** LOW — gap between rev_1h (cluster 0) and rev_3h (cluster 1 singleton)
- **Redundancy risk:** LOW
- **Diagnostic value:** HIGH — tests granularity of short-term reversal curve; incremental signal vs 1h/3h
- **Failure mode:** May be too correlated with rev_1h or rev_3h if reversal is smooth
- **Complexity:** LOW
- **Notes (zh):** 填补1h与3h反转信号之间的空白，用于测试短期反转曲线粒度
- **Notes (en):** Fills gap between 1h and 3h reversal; tests granularity of short-term reversal curve

#### `mom_vol_adjusted_20h` (medium_term_momentum)

- **Theme:** Risk-adjusted momentum normalizing by realized volatility
- **Formula:** `mom_20h / rolling_std(pct_change(close), 20)`
- **Required inputs:** close
- **Available inputs:** PASS — close available
- **Operator reuse:** rolling_std(), delay() from factor_ops; compute mom_20h inline
- **New operator needed:** NO
- **New data needed:** NO
- **Expected direction:** positive
- **Direction basis:** Risk-adjusted momentum: high-return/low-vol assets should outperform (quality momentum)
- **Cluster overlap:** LOW — distinct from raw momentum (cluster 4) and vol factors (cluster 8); combines signal and risk
- **Redundancy risk:** LOW
- **Diagnostic value:** HIGH — tests whether volatility-adjusting momentum adds marginal info vs raw mom + vol
- **Failure mode:** May simply replicate ranking of raw momentum if vol is not cross-sectionally dispersed
- **Complexity:** LOW
- **Notes (zh):** 风险调整动量：测试波动率调整是否增加边际信息
- **Notes (en):** Risk-adjusted momentum: tests whether vol-normalization adds marginal info

#### `range_breakout_vol_confirm_20h` (range_breakout)

- **Theme:** Breakout confirmed by above-average volume
- **Formula:** `breakout_dist_20h * zscore(volume, 20) [when breakout_dist > 0]`
- **Required inputs:** high, low, close, volume
- **Available inputs:** PASS — all OHLCV available
- **Operator reuse:** zscore() from factor_ops; rolling_max, rolling_min from factor_ops
- **New operator needed:** NO
- **New data needed:** NO
- **Expected direction:** positive
- **Direction basis:** Volume-confirmed breakouts are more reliable; high volume + new high = continuation signal
- **Cluster overlap:** LOW — breakout_dist_20h is singleton-ish; adding volume confirmation is structurally distinct
- **Redundancy risk:** LOW
- **Diagnostic value:** HIGH — tests interaction of price breakout and volume surge; cross-factor composition diagnostic
- **Failure mode:** Breakout without volume confirmation may be noise; conditional signal reduces effective sample
- **Complexity:** LOW
- **Notes (zh):** 成交量确认突破：测试价格突破与成交量激增的交互效应
- **Notes (en):** Volume-confirmed breakout: tests price breakout × volume surge interaction

#### `volume_pressure_20h` (volume_pressure)

- **Theme:** Net directional volume pressure over 20h
- **Formula:** `rolling_mean(sign(delta(close, 1)) * volume, 20)`
- **Required inputs:** close, volume
- **Available inputs:** PASS — close and volume available
- **Operator reuse:** rolling_mean(), delta() from factor_ops
- **New operator needed:** NO
- **New data needed:** NO
- **Expected direction:** positive
- **Direction basis:** Persistent buying volume pressure indicates informed flow; positive pressure = bullish
- **Cluster overlap:** LOW — structurally distinct from vol_zscore and vol_ret_corr; directional volume composite
- **Redundancy risk:** LOW
- **Diagnostic value:** HIGH — tests directional volume as a signal distinct from raw volume and return-volume correlation
- **Failure mode:** May correlate with momentum if volume is not cross-sectionally informative
- **Complexity:** LOW
- **Notes (zh):** 定向成交量压力信号，测试方向性成交量是否独立于原始成交量和量价相关性
- **Notes (en):** Directional volume pressure signal; tests whether directional volume is independent of raw volume

#### `xs_rank_mom_accel` (cross_sectional_rank_acceleration)

- **Theme:** Cross-sectional rank of momentum acceleration
- **Formula:** `xs_rank(mom_accel_20h) per timestamp`
- **Required inputs:** close
- **Available inputs:** PASS — close available; cross-sectional ranking done by caller
- **Operator reuse:** Reuses mom_accel_20h computation; cross-sectional rank done in build_factor_values.py
- **New operator needed:** NO
- **New data needed:** NO
- **Expected direction:** positive
- **Direction basis:** Cross-sectionally ranked acceleration: high rank = accelerating momentum relative to peers
- **Cluster overlap:** LOW — xs_rank_ret_1h exists but is rank of raw return, not acceleration; structurally distinct
- **Redundancy risk:** LOW
- **Diagnostic value:** HIGH — tests cross-sectional normalization of a second-order signal (acceleration)
- **Failure mode:** May be noisy if acceleration is itself noisy; cross-sectional rank amplifies noise
- **Complexity:** MEDIUM
- **Notes (zh):** 动量加速度的截面排名，测试二阶信号的截面标准化效果
- **Notes (en):** Cross-sectional rank of momentum acceleration; tests cross-sectional normalization of second-order signal

---

## Backlog — 16 Additional Candidates

| Factor ID | Family | Priority | Complexity | Redundancy Risk | Notes |
|-----------|--------|----------|------------|-----------------|-------|
| `rev_48h` | short_term_reversal | P2_BACKLOG | LOW | MEDIUM | Fills 24h-72h gap but high correlation risk with neighboring reversals |
| `mom_168h` | medium_term_momentum | P2_BACKLOG | LOW | MEDIUM | 1-week momentum extension; risk of high correlation with mom_120h |
| `range_compression_breakout_48h` | range_breakout | P2_BACKLOG | LOW | MEDIUM | Tests pre-breakout range compression hypothesis |
| `vol_adj_mom_40h` | volatility_adjusted_momentum | P2_BACKLOG | LOW | LOW | 40h risk-adjusted momentum; conceptually similar to 20h variant, deferred to BATCH_02 |
| `volume_pressure_asymmetry_40h` | volume_pressure | P2_BACKLOG | LOW | LOW | Tests volume asymmetry hypothesis |
| `amihud_change_20h` | liquidity_stress | P2_BACKLOG | LOW | LOW | Dynamic liquidity stress; tests whether change in illiquidity adds info vs level |
| `funding_rate_skew_20h` | funding_rate_structure | P2_BACKLOG | LOW | LOW | Tests funding rate distribution shape beyond mean/zscore |
| `funding_rate_momentum_20h` | funding_rate_structure | P2_BACKLOG | LOW | LOW | Tests higher-order funding rate dynamics (acceleration) |
| `taker_flow_momentum_20h` | taker_flow_structure | P2_BACKLOG | LOW | MEDIUM | Taker flow momentum; tests whether flow dynamics are independent of level/zscore |
| `taker_flow_persistence_40h` | taker_flow_structure | P2_BACKLOG | LOW | LOW | Tests taker flow persistence (autocorrelation) as signal |
| `candle_body_ma_5h` | intraday_candle_structure | P2_BACKLOG | LOW | MEDIUM | Tests whether smoothing candle body adds signal vs raw single-bar body |
| `doji_frequency_20h` | intraday_candle_structure | P2_BACKLOG | LOW | LOW | Tests candle pattern frequency as a novel structural signal |
| `realized_vol_skew_40h` | realized_volatility_shape | P2_BACKLOG | LOW | MEDIUM | 40h realized skewness; tests whether longer window adds info vs 20h |
| `xs_rank_vol_change` | cross_sectional_rank_acceleration | P2_BACKLOG | MEDIUM | LOW | Cross-sectional rank of volume change rate |
| `extreme_reversal_5h` | mean_reversion_after_extreme_move | P2_BACKLOG | LOW | LOW | Conditional mean reversion after extreme 5h move; clear logic but needs effective sample confirmation, deferred to BATCH_02 |
| `extreme_reversal_24h` | mean_reversion_after_extreme_move | P2_BACKLOG | LOW | LOW | Conditional mean reversion after extreme 24h move |

---

## Excluded — 1 Duplicate(s)

- `realized_vol_regime_ratio_20_80` (realized_volatility_shape): EXCLUDED — duplicate of existing vol_ratio_20_80

---

## Intake-Readiness Checklist

| Check ID | Status | What It Checks | Blocking |
|----------|--------|----------------|----------|
| `registry_integrity_ready` | **PASS** | Factor registry (REGISTRY list in factor_formula_registry.py) is parseable, all ... | YES |
| `factor_ops_reuse_ready` | **PASS** | All primitive operators (delay, delta, rolling_mean, rolling_std, rolling_max, r... | YES |
| `factor_values_build_ready` | **PASS** | build_factor_values.py can compute factor values for all registered factors with... | YES |
| `intake_runner_ready` | **PASS** | Single-factor intake can be run incrementally (add new FactorSpec, run build, ev... | NO |
| `full_refresh_runner_ready` | **PASS** | Full factor library refresh pipeline (run_factor_library_refresh.py) is function... | NO |
| `expensive_stage_guardrails_ready` | **PASS** | Expensive stages (evaluate, redundancy, paper-diagnostics) require --expensive-o... | NO |
| `profile_stage_ready` | **PASS** | Unified profile stage produces factor_unified_profile_summary.csv/json with qual... | NO |
| `evidence_matrix_ready` | **PASS** | Evidence matrix (factor_evaluation_evidence_matrix.csv) contains IC, turnover, s... | NO |
| `staleness_monitor_ready` | **PASS** | check_factor_library_staleness.py detects stale factors and reports staleness se... | NO |
| `page_ready_payload_ready` | **PASS** | Single-factor paper page payload exists and contains NAV curves, drawdown, turno... | NO |
| `no_signal_mutation_guard_ready` | **PASS** | build_factor_values.py does not mutate signal_panel or ranking after factor comp... | YES |

---

## Priority Distribution

- **P1_CONTROLLED_BATCH:** 5
- **P2_BACKLOG:** 16
- **P5_DEFER:** 1

---

## Next Steps

1. Review BATCH_01 candidates and confirm no redundancy concerns
2. Register BATCH_01 factors in `factor_formula_registry.py`
3. Run full refresh pipeline to compute and evaluate new factors
4. Update evidence matrix and profile with new factor data
5. Review IC results and decide on retention/removal
