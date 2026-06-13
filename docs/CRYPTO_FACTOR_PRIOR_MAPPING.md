# Crypto Factor Prior Mapping

> This document maps external factor priors to crypto availability buckets.
>
> Phase: 2D (External Factor Priors)
>
> Last updated: 2026-06-13
>
> **This is a classification document, not an implementation plan.**

---

## Bucket Definitions

| Bucket | Code | Description | Current V0 Data Available? |
|--------|------|-------------|---------------------------|
| A | `ohlcv_direct` | OHLCV-only, directly adaptable with minimal changes | ✅ Yes |
| B | `ohlcv_rewrite` | OHLCV-only but requires formula rewrite (e.g., cross-sectional → time-series) | ✅ Yes |
| C | `requires_vwap` | Requires VWAP or amount/turnover data | ⚠️ Derivable from quote_volume/volume |
| D | `requires_microstructure` | Requires order book or trade-level data | ❌ Not in current bars |
| E | `requires_derivatives` | Requires funding, OI, basis, or other derivatives data | ❌ Not in current bars |
| F | `requires_fundamentals` | Requires financial statements, market cap, or accounting data | ❌ Not applicable to crypto perps |
| G | `not_suitable` | Not suitable for crypto perpetual futures | ❌ N/A |

---

## A. OHLCV-Only Directly Adaptable

These factors can be implemented using only Open, High, Low, Close, Volume from `bars_1h.parquet` with minimal or no formula changes.

### From WQ101
- **Alpha#1**: `(rank(Ts_ArgMax(SignedPower(((returns < 0) ? stddev(returns, 20) : close), 2.), 5)) - 0.5)` — uses returns only
- **Alpha#6**: `-1 * correlation(open, volume, 10)` — uses open and volume
- **Alpha#12**: `sign(delta(volume, 1)) * (-1 * delta(close, 1))` — uses volume and close
- **Alpha#26**: `-1 * ts_max(correlation(ts_rank(volume, 5), ts_rank(high, 5), 5), 3)` — uses volume and high
- **Alpha#34**: `(((((delta(close, 1) / delay(close, 1)) * (1 - rank(delta(close, 1) / delay(close, 1)))) + (close / delay(close, 5))) < 0) ? 1 : -1)` — returns only
- **Alpha#41**: `power(high * low, 0.5) - vwap` — needs VWAP (bucket C) but high*low is OHLCV
- **Alpha#53**: `-1 * delta((((close - low) - (high - close)) / (close - low)), 9)` — OHLCV only
- **Alpha#101**: `(close - open) / ((high - low) + .001)` — OHLCV only

### From Alpha158
- Return features: `close/close.shift(k) - 1` for k in {1, 2, 3, 4, 5, 10, 20, 30, 60}
- Volatility features: `std(returns, k)` for k in {5, 10, 20, 30, 60}
- Moving average features: `close / SMA(close, k) - 1` for k in {5, 10, 20, 30, 60}
- Volume ratio: `volume / SMA(volume, k)` for k in {5, 10, 20, 30, 60}
- Price range: `(high - low) / close`
- Upper/lower shadow: `(high - max(open, close)) / close`, `(min(open, close) - low) / close`

### From Technical Indicators
- **RSI** (14, already implemented as `rsi_14h`)
- **Bollinger Bands Z-Score** (already implemented as `bb_zscore_20h`)
- **MACD**: `EMA(close, 12) - EMA(close, 26)` and signal line
- **Stochastic %K, %D**: `(close - low_14) / (high_14 - low_14)`
- **CCI**: `(typical_price - SMA(TP, 20)) / (0.015 * mean_deviation)`
- **Williams %R**: `(high_14 - close) / (high_14 - low_14)`
- **ADX**: Based on +DM, -DM, and ATR
- **OBV**: Cumulative volume signed by price direction
- **Aroon**: Days since highest high / lowest low

### From Crypto-Specific
- **Volume Pressure**: `volume / SMA(volume, 20)` — pure OHLCV

---

## B. OHLCV-Only but Requires Formula Rewrite

These factors use OHLCV data but their original formula assumes cross-sectional ranking. They need adaptation to time-series context.

### From WQ101
Most WQ101 factors use `rank(x)` which is cross-sectional (rank across stocks at each timestamp). For crypto:
- Replace `rank(x)` with rolling zscore: `(x - rolling_mean) / rolling_std`
- Or rolling percentile: `rolling_percentile_rank(x, window)`
- `indneutralize(x, g)` has no crypto equivalent — skip or replace with time-series demean

### From GTJA191
- Cross-sectional size factors (market cap rank) — no direct equivalent for perps
- Industry-neutral factors — no industry classification in crypto
- **Adaptation**: Use time-series zscore instead of cross-sectional rank

---

## C. Requires VWAP / Amount / Turnover

These factors need VWAP or dollar volume data beyond standard OHLCV.

### Data Availability
- **VWAP**: Derivable as `quote_volume / volume` from Binance OHLCV
- **Amount (dollar volume)**: Equivalent to `quote_volume`
- **Turnover**: Not directly available (would need market cap or float supply)

### Factors
- **WQ101 Alpha#41**: `power(high * low, 0.5) - vwap` — needs VWAP
- **WQ101 Alpha#44**: `-1 * correlation(high, rank(volume), 5)` — needs cross-sectional volume rank
- **Alpha158 VWAP features**: `(close - VWAP) / VWAP` — VWAP derivable
- **MFI (Money Flow Index)**: Uses typical_price × volume — derivable
- **AD Line (Accumulation/Distribution)**: Uses close/low/high relationship × volume — derivable
- **OBV with VWAP confirmation**: Needs VWAP — derivable

---

## D. Requires Order Book / Microstructure Data

These factors need order book depth, trade-level data, or microstructure information.

### Factors
- **Taker Buy/Sell Imbalance**: Needs aggregated trades with buy/sell classification
- **Bid-Ask Spread**: Needs order book top-of-book data
- **Order Book Imbalance**: Needs bid/ask depth levels
- **Trade Size Distribution**: Needs individual trade data
- **VPIN (Volume-Synchronized PIN)**: Needs trade-level classified flow data
- **Kyle's Lambda**: Needs trade-level price impact estimation

### Data Source
- Binance WebSocket `aggTrades` endpoint (taker buy/sell classification)
- Binance REST API `depth` endpoint (order book)
- Not in current `bars_1h.parquet`

---

## E. Requires Funding / Open Interest / Basis / Derivatives Data

These factors need data from perpetual futures beyond OHLCV.

### Factors
- **Funding Rate**: `funding_rate`, `funding_rate_ma_8h`, `funding_zscore`
- **Open Interest Delta**: `oi_change_1h`, `oi_change_pct`, `oi_vs_vol_ratio`
- **Basis Spread**: `basis_1q`, `basis_annualized`, `basis_zscore`
- **Long/Short Ratio**: `ls_ratio`, `ls_ratio_zscore`
- **Liquidation Volume**: `liq_volume_1h`, `liq_imbalance`

### Data Source
- Binance API: `fundingRate`, `openInterestHist`, `globalLongShortAccountRatio`
- Binance spot API for basis calculation
- Coinglass for liquidation data (external)

---

## F. Requires Fundamentals / Accounting Data

These factors are not suitable for crypto perpetual futures.

### Factors
- **GTJA Size factors**: Market cap (no float supply data for perps)
- **GTJA Value factors**: P/E, P/B, dividend yield — no equivalent
- **GTJA Growth factors**: Revenue growth, earnings growth — no equivalent
- **GTJA Quality factors**: ROE, ROA, debt ratio — no equivalent

### Note
Some "quality" proxies exist (e.g., market cap ≈ fully diluted valuation from CoinGecko) but these are not available from exchange OHLCV data.

---

## G. Not Suitable / Park

These factors have no meaningful adaptation path for crypto perpetual futures.

### Factors
- **GTJA191 Industry factors**: No industry classification in crypto
- **WQ101 indneutralize**: No sector/industry to neutralize against
- **A-share limit-up/down factors**: No price limits in crypto
- **T+1 settlement factors**: Crypto is T+0
- **Margin requirement factors**: Varies by exchange, not standardized

---

## Summary by Bucket

| Bucket | Count (approx) | Implementation Readiness |
|--------|----------------|-------------------------|
| A: ohlcv_direct | ~80-100 | Ready (need implementation) |
| B: ohlcv_rewrite | ~30-50 | Ready after adaptation |
| C: requires_vwap | ~10-15 | Ready (VWAP derivable) |
| D: requires_microstructure | ~10-15 | Need new data pipeline |
| E: requires_derivatives | ~15-20 | Need new data pipeline |
| F: requires_fundamentals | ~40-60 | Not applicable |
| G: not_suitable | ~20-30 | Skip |

**Immediate implementation candidates (A + B + C):** ~120-165 factors
**Deferred (D + E):** ~25-35 factors (need new data)
**Not applicable (F + G):** ~60-90 factors
