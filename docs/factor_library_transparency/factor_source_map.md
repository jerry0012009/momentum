# Factor Source Map — 因子来源地图

> Phase 12D-C-R · Authority: scripts/build_phase9b_signal_panel.py
> 修复说明: Phase 9B 当前主线因子以 build_phase9b_signal_panel.py 为准。早期 factor list 只作为历史/实验因子展示。

## 数据范围

| 数据集 | 范围 | 符号数 | 行数 | 来源 |
|--------|------|--------|------|------|
| Signal panel | 2024-06-01 → 2026-06-13 | 266 | 3,314,397 | PHASE_9B_DETERMINISTIC_SIGNAL_PANEL.md |
| Bars 1h (main run) | 2025-12-15 → 2026-06-13 | 50 | ~215K | parquet metadata |
| Bars 1h (full cache) | 2024-06-01 → 2026-06-13 | 266 | ~3.3M | parquet metadata |
| Paper monitoring | 2026-05-14 → 2026-06-13 | 43 | 31,003 | PHASE_12B_PAPER_MONITORING_DIAGNOSTIC.md |

## Phase 9B Signal Panel — 10 个因子

权威来源: `scripts/build_phase9b_signal_panel.py` 中的 `FACTOR_IDS`。

### 四通道结构

| 通道 | 因子 | 方向 |
|------|------|------|
| RISK_PRESSURE | vol_5h, vol_40h, downside_vol_20h, vol_of_vol_20h | NEGATIVE |
| TECHNICAL_REVERSION | rsi_7h, rsi_28h | NEGATIVE |
| LIQUIDITY_GATE | xs_rank_vol | OVERLAY |
| RANGE_POSITION | range_1h, range_4h, price_pos_24h | OVERLAY |

### 信号变体

#### signal_v0_core_only (存活候选)

```
risk_pressure = mean(z[vol_5h], z[vol_40h], z[downside_vol_20h], z[vol_of_vol_20h])
oscillator_exhaustion = mean(z[rsi_7h], z[rsi_28h])
raw_core_score = 0.60 × risk_pressure + 0.40 × oscillator_exhaustion
signal_v0_core_only = xs_zscore(raw_core_score)
```

粗略等效权重: vol 每因子 ≈ 0.60/4 = 0.15, RSI 每因子 ≈ 0.40/2 = 0.20 (非最终线性权重)

- 存活候选: signal_v0_core_only__1h__original_no_guard
- 核心因子: vol_5h, vol_40h, downside_vol_20h, vol_of_vol_20h, rsi_7h, rsi_28h
- 状态: PAPER_SIGNAL_DIAGNOSTIC_ONLY, allowed_for_real_execution = FALSE

#### signal_v0_pm_full_structured

```
signal = xs_zscore(raw_core × liquidity_gate × position_overlay_multiplier)
liquidity_gate = clip(0.50 + 0.50 × xs_rank_pct(z[xs_rank_vol]), 0.50, 1.00)
pos_multiplier = clip(1 + 0.15 × pos_timing, 0.85, 1.15)
```

使用全部 10 个因子。非存活候选。

#### signal_v0_family_balanced_diagnostic

```
signal = xs_zscore(0.25×risk + 0.25×osc + 0.25×pos_timing + 0.25×(liquidity_gate - 0.75))
```

使用全部 10 个因子。仅用于诊断。

## 历史/实验因子 (不属于 Phase 9B)

| Factor | Family | Script | In Phase 9B |
|--------|--------|--------|-------------|
| mom_20h | momentum | build_factor_values.py | ✗ |
| reversal_5h | mean_reversion | build_factor_values.py | ✗ |
| volatility_20h | volatility | build_factor_values.py | ✗ |
| rsi_14h | technical | build_factor_values.py | ✗ |
| bb_zscore_20h | technical | build_factor_values.py | ✗ |
| wq101_alpha101 | alpha | build_factor_values.py | ✗ |
| wq101_alpha12 | alpha | build_factor_values.py | ✗ |
| wq101_alpha53 | alpha | build_factor_values.py | ✗ |
| q158_high_low_range | range | build_factor_values.py | ✗ |
| tech_macd | technical | build_factor_values.py | ✗ |
| tech_atr | technical | build_factor_values.py | ✗ |

## Crypto-Native 因子 (不属于 Phase 9B)

| Factor | Script | In Phase 9B |
|--------|--------|-------------|
| funding_rate_change_24h | build_crypto_native_factor_values.py | ✗ |
| funding_rate_level_20h | build_crypto_native_factor_values.py | ✗ |
| funding_rate_zscore_80h | build_crypto_native_factor_values.py | ✗ |
| taker_buy_delta_5h | build_crypto_native_factor_values.py | ✗ |
| taker_buy_ratio_20h | build_crypto_native_factor_values.py | ✗ |
| taker_buy_zscore_20h | build_crypto_native_factor_values.py | ✗ |

若要使用 crypto-native 因子，应另起 Phase 9C/9D signal design，不要改写 Phase 9B 历史结果。

## 未来信号扩展

后续新增信号时，不应直接覆盖 Phase 9B 结果。应新增 Phase 9C/9D 或抽象 signal_spec/build_signal_panel.py。新信号必须重新走 Phase 10/11/12 评估。

---

Phase 12D-C-R · Phase 13 NOT STARTED · No real execution · No alpha claim · No production claim
