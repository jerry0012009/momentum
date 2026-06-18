# 因子来源地图 — Factor Source Map

> Phase 12D-C · Run: `crypto_top50_usdt_perp_1h` · Generated: 2026-06-18

---

## 1. 因子目录 (Factor Catalog)

### 1.1 build_factor_values.py — 11 基础因子

| # | Factor Name | Family | Status | In Phase 9B | In Surviving | Weight | Notes |
|---|------------|--------|--------|-------------|--------------|--------|-------|
| 1 | `mom_20h` | momentum | DIAGNOSTIC_PROBE | ✓ | ✓ | 0.1667 | 20h cross-sectional momentum |
| 2 | `reversal_5h` | mean_reversion | DIAGNOSTIC_PROBE | ✓ | ✓ | 0.1667 | 5h mean reversion |
| 3 | `volatility_20h` | volatility | DIAGNOSTIC_PROBE | ✓ | ✓ | 0.1667 | 20h realized vol |
| 4 | `rsi_14h` | technical | DIAGNOSTIC_PROBE | ✓ | ✓ | 0.1667 | RSI 14h lookback |
| 5 | `bb_zscore_20h` | technical | DIAGNOSTIC_PROBE | ✓ | ✓ | 0.1667 | Bollinger Band z-score 20h |
| 6 | `wq101_alpha101` | alpha | DIAGNOSTIC_PROBE | ✓ | ✓ | 0.1667 | WorldQuant Alpha 101 |
| 7 | `wq101_alpha12` | alpha | DIAGNOSTIC_PROBE | ✓ | ✗ | — | WorldQuant Alpha 12 |
| 8 | `wq101_alpha53` | alpha | DIAGNOSTIC_PROBE | ✓ | ✗ | — | WorldQuant Alpha 53 |
| 9 | `q158_high_low_range` | range | DIAGNOSTIC_PROBE | ✓ | ✗ | — | High-low range factor |
| 10 | `tech_macd` | technical | DIAGNOSTIC_PROBE | ✓ | ✗ | — | MACD indicator |
| 11 | `tech_atr` | technical | DIAGNOSTIC_PROBE | ✗ | ✗ | — | ATR, not in Phase 9B panel |

**Input data:** bars_1h_universe (2025-12-15 → 2026-06-13)
**Output:** `data/features/*/factor_values.parquet`

### 1.2 build_crypto_native_factor_values.py — 6 Crypto-Native 特征

| # | Factor Name | Family | Status | In Phase 9B | Notes |
|---|------------|--------|--------|-------------|-------|
| 12 | `funding_rate_change_24h` | crypto_native | DIAGNOSTIC_PROBE | ✗ | 24h funding rate change |
| 13 | `funding_rate_level_20h` | crypto_native | DIAGNOSTIC_PROBE | ✗ | 20h rolling funding rate level |
| 14 | `funding_rate_zscore_80h` | crypto_native | DIAGNOSTIC_PROBE | ✗ | 80h funding rate z-score |
| 15 | `taker_buy_delta_5h` | crypto_native | DIAGNOSTIC_PROBE | ✗ | 5h taker buy delta |
| 16 | `taker_buy_ratio_20h` | crypto_native | DIAGNOSTIC_PROBE | ✗ | 20h taker buy ratio |
| 17 | `taker_buy_zscore_20h` | crypto_native | DIAGNOSTIC_PROBE | ✗ | 20h taker buy z-score |

**Input data:** funding_rate history, trades/taker data (2025-12-15 → 2026-06-13)
**Output:** `data/features/*/crypto_native_factor_values.parquet`

---

## 2. Phase 9B Signal Panel — 因子如何组成信号

> **📌 说明：** Phase 9B 是当前 run 中已经完整落地和评估的主线 signal panel。它不是未来唯一的因子组合方式。

### 四通道结构 (4-Channel Architecture)

| Channel | # Factors | Factors |
|---------|-----------|---------|
| **RISK_PRESSURE_CHANNEL** | 4 | volatility_20h, reversal_5h, bb_zscore_20h, q158_high_low_range |
| **TECHNICAL_REVERSION_CHANNEL** | 2 | rsi_14h, tech_macd |
| **LIQUIDITY_GATE_CHANNEL** | 1 | wq101_alpha101 |
| **RANGE_POSITION_CHANNEL** | 3 | mom_20h, wq101_alpha12, wq101_alpha53 |

### 三个信号变体 (Signal Variants)

| Variant | # Factors | Weight Scheme | Factors |
|---------|-----------|---------------|---------|
| `signal_v0_core_only` | 6 | equal (0.1667) | mom_20h, reversal_5h, volatility_20h, rsi_14h, bb_zscore_20h, wq101_alpha101 |
| `signal_v0_pm_full_structured` | 10 | structured | All 10 panel factors |
| `signal_v0_family_balanced_diagnostic` | 10 | family_balanced | All 10 panel factors |

---

## 3. 存活候选 (Surviving Candidate)

| Field | Value |
|-------|-------|
| **名称** | `signal_v0_core_only__1h__original_no_guard` |
| **因子数量** | 6 (equal weight 0.1667) |
| **符号数量** | 16 (8 long, 8 short) |
| **状态** | `PAPER_SIGNAL_DIAGNOSTIC_ONLY` |
| **allowed_for_real_execution** | `FALSE` |

---

## 4. 未来信号扩展指南

> **⚠️ 重要：** 以后在哪里增加新信号？后续新增信号时，不应直接覆盖 Phase 9B 结果。应新增 Phase 9C / 9D 或抽象 `signal_spec` / `build_signal_panel.py`。新信号必须重新走 Phase 10/11/12 评估。

6 个 crypto-native 因子（来自 `build_crypto_native_factor_values.py`）目前尚未加入任何信号变体。这些因子可作为 Phase 9C+ 的候选输入。

---

## 5. 数据溯源汇总

| 生成脚本 | 因子数量 | 输出文件 |
|---------|---------|---------|
| `scripts/build_factor_values.py` | 11 | `data/features/*/factor_values.parquet` |
| `scripts/build_crypto_native_factor_values.py` | 6 | `data/features/*/crypto_native_factor_values.parquet` |
| `scripts/build_factor_values_batch.py` | 批量扩展 | 上述文件的补充 |

**总计：17 个因子（11 基础 + 6 crypto-native）**

---

*Phase 12D-C · Generated 2026-06-18*
