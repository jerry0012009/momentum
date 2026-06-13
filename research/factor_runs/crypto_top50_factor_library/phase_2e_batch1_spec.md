# Phase 2E Batch 1 — Formula Specifications

> 6 direct_formula / OHLCV-only factors
>
> Status: PLANNED_ONLY (no implementation yet)
>
> Date: 2026-06-13

---

## 1. wq101_alpha101

| Field | Value |
|-------|-------|
| **factor_id** | `wq101_alpha101` |
| **source_prior** | WQ101 Alpha#101 |
| **formula_plain_english** | Intraday price position: how far the close is between open and high-low range |
| **formula_pseudocode** | `(close - open) / (high - low + 0.001)` |
| **required_columns** | `open, high, low, close` |
| **lookback_window** | 1 (current bar only) |
| **known_at_rule** | `timestamp` (known at bar close) |
| **expected_direction** | positive = close above open (bullish candle); negative = close below open (bearish candle) |
| **output_path** | `data/features/crypto_top50_usdt_perp_1h/wq101_alpha101/factor_values.parquet` |
| **unit_test_idea** | Given O=100, H=110, L=95, C=105: output = (105-100)/(110-95+0.001) ≈ 0.3333 |
| **risk_notes** | Near-zero range (H≈L) produces extreme values; the +0.001 epsilon prevents division by zero. Winsorization may be needed for evaluation. |

---

## 2. wq101_alpha12

| Field | Value |
|-------|-------|
| **factor_id** | `wq101_alpha12` |
| **source_prior** | WQ101 Alpha#12 |
| **formula_plain_english** | Sign of volume change multiplied by negative price change. Rising volume + falling price = positive signal (selling pressure). |
| **formula_pseudocode** | `sign(delta(volume, 1)) * (-1 * delta(close, 1))` |
| **required_columns** | `volume, close` |
| **lookback_window** | 2 (needs lag 1) |
| **known_at_rule** | `timestamp` |
| **expected_direction** | conditional (sign(vol_delta)*neg(close_delta) can be positive or negative; interpret after evaluation) |
| **output_path** | `data/features/crypto_top50_usdt_perp_1h/wq101_alpha12/factor_values.parquet` |
| **unit_test_idea** | Volume [100, 120], Close [100, 98]: sign(120-100)=+1, -(98-100)=+2, output = +1 * +2 = +2 |
| **risk_notes** | `sign()` produces discrete {-1, 0, +1}; may need smoothing for some use cases. Volume=0 edge case. |

---

## 3. wq101_alpha53

| Field | Value |
|-------|-------|
| **factor_id** | `wq101_alpha53` |
| **source_prior** | WQ101 Alpha#53 |
| **formula_plain_english** | Change in intraday price position over 9 bars. Measures how the candle structure evolves. |
| **formula_pseudocode** | `-1 * delta(((close - low) - (high - close)) / (close - low + 0.001), 9)` |
| **required_columns** | `high, low, close` |
| **lookback_window** | 10 (current + lag 9) |
| **known_at_rule** | `timestamp` |
| **expected_direction** | conditional (sign ambiguity from -1 * delta; do not force direction before evaluation) |
| **output_path** | `data/features/crypto_top50_usdt_perp_1h/wq101_alpha53/factor_values.parquet` |
| **unit_test_idea** | Bar t: C=105, H=110, L=95 → pos = (10-10)/(10) = 0. Bar t-9: C=98, H=110, L=95 → pos = (3-12)/(3) = -3.0. delta = 0-(-3) = 3.0. output = -3.0. |
| **risk_notes** | `close - low` can be near zero; epsilon needed. The negative sign inverts the delta. |

---

## 4. q158_high_low_range

| Field | Value |
|-------|-------|
| **factor_id** | `q158_high_low_range` |
| **source_prior** | Alpha158 High-Low Range |
| **formula_plain_english** | Intraday price range as fraction of close price. Higher = more volatile candle. |
| **formula_pseudocode** | `(high - low) / close` |
| **required_columns** | `high, low, close` |
| **lookback_window** | 1 (current bar only) |
| **known_at_rule** | `timestamp` |
| **expected_direction** | conditional (volatility proxy; direction-neutral by construction) |
| **output_path** | `data/features/crypto_top50_usdt_perp_1h/q158_high_low_range/factor_values.parquet` |
| **unit_test_idea** | H=110, L=95, C=100: output = 15/100 = 0.15 |
| **risk_notes** | Always non-negative. Pure volatility proxy; direction-neutral by construction. |

---

## 5. tech_macd

| Field | Value |
|-------|-------|
| **factor_id** | `tech_macd` |
| **source_prior** | Technical MACD Signal |
| **formula_plain_english** | MACD line: difference between fast EMA and slow EMA. Signal line: EMA of MACD line. Histogram: MACD - Signal. |
| **formula_pseudocode** | `macd_line = EMA(close, 12) - EMA(close, 26); signal = EMA(macd_line, 9); histogram = macd_line - signal` |
| **required_columns** | `close` |
| **lookback_window** | 26 + 9 = 35 bars (EMA26 needs ~52 bars for stability; EMA9 adds ~18) |
| **known_at_rule** | `timestamp` |
| **expected_direction** | positive histogram = bullish momentum; negative histogram = bearish momentum |
| **output_path** | `data/features/crypto_top50_usdt_perp_1h/tech_macd/factor_values.parquet` |
| **unit_test_idea** | Given constant prices, MACD should be 0. Given steadily rising prices, MACD should be positive. |
| **risk_notes** | EMA warmup period: first ~52 bars will be unstable. Use `adjust=False` for EMA to match standard TA-Lib behavior. |

**Implementation note:** Output the `histogram` (MACD - Signal) as the factor value, as it captures both direction and momentum strength.

---

## 6. tech_atr

| Field | Value |
|-------|-------|
| **factor_id** | `tech_atr` |
| **source_prior** | Technical ATR 14 |
| **formula_plain_english** | Average True Range over 14 bars. Measures average price volatility including gaps. |
| **formula_pseudocode** | `tr = max(high - low, abs(high - prev_close), abs(low - prev_close)); atr = rolling_mean(tr, 14)` |
| **required_columns** | `high, low, close` |
| **lookback_window** | 15 bars (current + lag 1 for TR, then 14-bar rolling mean) |
| **known_at_rule** | `timestamp` |
| **expected_direction** | conditional (volatility proxy; direction-neutral by construction) |
| **output_path** | `data/features/crypto_top50_usdt_perp_1h/tech_atr/factor_values.parquet` |
| **unit_test_idea** | Constant H=110, L=95, C=100 for 15 bars: TR = max(15, 10, 5) = 15. ATR = 15. |
| **risk_notes** | Always non-negative. First 14 bars will be NaN or use expanding mean. Use SMA (not Wilder's smoothing) for simplicity; document if switching to Wilder's. |

**Implementation note:** For crypto 1h bars, there are no real "gaps" (continuous market), so `high - low` dominates TR. But keep the full TR formula for correctness.

---

## Common Requirements

All 6 factors must:

1. **Not use future data**: no `shift(-k)`, no lookahead.
2. **Handle symbol grouping**: compute per-symbol, not across symbols (except cross-sectional rank factors in Batch 2).
3. **Return NaN for insufficient history**: first `lookback_window` bars should be NaN.
4. **Match standard factor_values schema**: output `factor_values.parquet` with columns:
   - `timestamp` — bar close time
   - `symbol` — trading pair
   - `factor_name` — must equal `factor_id`
   - `factor_value` — computed value
   - `known_at` — must equal `timestamp`
   - `source_timeframe` — `1h` for this dataset
   - `computed_at` — wall clock time when computation ran
5. **Have unit tests**: at least one synthetic test per factor.
6. **Expected direction documented**: used by `evaluate_factors.py` for direction-adjusted spread.
