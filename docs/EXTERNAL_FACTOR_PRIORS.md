# External Factor Priors

> This document catalogs external factor prior families that may be adapted for crypto factor research.
>
> Phase: 2D (External Factor Priors)
>
> Last updated: 2026-06-13
>
> **This is a research catalog, not an implementation plan.** No factors here are implemented.

---

## 1. WorldQuant 101 Alphas

| Field | Value |
|-------|-------|
| **source_name** | WorldQuant 101 Formulaic Alphas |
| **citation** | Kakushadze, Z. (2016). "101 Formulaic Alphas." SSRN 2701346 |
| **asset_class_origin** | US equities (cross-sectional) |
| **typical_data_requirements** | Open, High, Low, Close, Volume, Amount (dollar volume), Returns, VWAP |
| **factor_style** | Short-term cross-sectional alphas; operator-based expressions |
| **operator_examples** | `rank(x)`, `delay(x, d)`, `delta(x, d)`, `correlation(x, y, d)`, `covariance(x, y, d)`, `ts_min(x, d)`, `ts_max(x, d)`, `ts_rank(x, d)`, `sum(x, d)`, `std(x, d)`, `signedpower(x, a)`, `decay_linear(x, d)`, `scale(x)`, `indneutralize(x, g)`, `sequentially_replace(x)` |
| **number_of_factors** | 101 closed-form expressions |
| **implementation_difficulty** | MEDIUM — operator set is well-defined; main challenge is adapting cross-sectional `rank()` to time-series context |
| **crypto_transferability** | MODERATE — ~30-40 factors use only volume/returns and transfer directly; others use `amount` (dollar volume = quote_volume ✓) or cross-sectional rank (needs adaptation) |
| **notes** | Designed for daily US equity cross-section. For crypto: (1) replace `rank(x)` with rolling zscore or percentile; (2) `indneutralize` has no crypto equivalent (no sector classification); (3) `amount` ≈ `quote_volume` in crypto; (4) some factors use `returns` only — these transfer directly. Window sizes may need rescaling (daily→hourly). |

---

## 2. GTJA 191 Style Factors

| Field | Value |
|-------|-------|
| **source_name** | Guotai Junan Securities 191 Style Factors |
| **citation** | GTJA quantitative research reports |
| **asset_class_origin** | China A-shares (cross-sectional) |
| **typical_data_requirements** | Open, High, Low, Close, Volume, Amount, Market Cap, Financial Statements (some), Limit-up/down data (some) |
| **factor_style** | Cross-sectional style factors; categorized into 10 families |
| **factor_families** | Size, Value, Momentum, Volatility, Quality, Growth, Liquidity, Reversal, Turnover, Technical |
| **operator_examples** | `rank(x)`, `zscore(x)`, `regression_residuals(y, X)`, `winsorize(x)`, `neutralize(x, industry)`, various financial ratios |
| **number_of_factors** | 191 factors across 10 families |
| **implementation_difficulty** | MEDIUM-HIGH — many factors are straightforward, but ~30% require financial statement data or A-share specific features |
| **crypto_transferability** | MODERATE — Momentum, Reversal, Volatility, Technical families are highly transferable. Size (market cap) has no direct crypto perp equivalent. Value/Growth/Quality require fundamentals. |
| **notes** | A-share specific features (T+1 settlement, limit-up/down, industry classification) do not apply to crypto. The Momentum, Reversal, Volatility, and Technical families (~80-100 factors) are the most promising for crypto adaptation. Factors requiring market cap, financial statements, or industry classification are not suitable. |

---

## 3. Qlib Alpha158 / Alpha360

| Field | Value |
|-------|-------|
| **source_name** | Microsoft Qlib Alpha158 and Alpha360 |
| **citation** | Microsoft Qlib documentation; Bian et al. (2021) |
| **asset_class_origin** | China A-shares (daily bars) |
| **typical_data_requirements** | Open, High, Low, Close, Volume, Amount (VWAP derived from Amount/Volume) |
| **factor_style** | Engineered features for ML models; pure OHLCV-derived |
| **Alpha158** | 158 features from daily bars: returns (multiple windows), volatility (multiple windows), moving averages, volume ratios, price-volume correlations, technical indicators (RSI, MA, MACD, etc.) across windows 5, 10, 20, 30, 60 days |
| **Alpha360** | 6 raw features (O, H, L, C, V, VWAP) across 60 timesteps — designed for sequence models (LSTM, Transformer) |
| **number_of_factors** | Alpha158: 158 features. Alpha360: 6×60 = 360 raw values |
| **implementation_difficulty** | LOW — all features are pure OHLCV derivatives with well-documented formulas |
| **crypto_transferability** | HIGH — directly adaptable. Only change: window size rescaling (daily→hourly: 5d→120h, 10d→240h, etc.) and VWAP derivation |
| **notes** | The most directly transferable factor family. Alpha158 features are mostly standard technical indicators with multiple lookback windows. Alpha360 is designed for deep learning and provides raw price/volume sequences. VWAP can be derived as `quote_volume / volume` in crypto. |

---

## 4. Traditional Technical Indicators

| Field | Value |
|-------|-------|
| **source_name** | Standard Technical Analysis Indicators |
| **citation** | Various (Murphy, 1999; Wilder, 1978; etc.) |
| **asset_class_origin** | Universal (equities, futures, forex, crypto) |
| **typical_data_requirements** | Open, High, Low, Close, Volume (minimal) |
| **factor_style** | Single-asset time-series signals; rule-based |
| **indicator_categories** | Trend (MA, MACD, ADX, Aroon), Momentum (RSI, Stochastic, CCI, Williams %R), Volatility (ATR, Bollinger Bands, Keltner), Volume (OBV, VWAP, MFI, AD Line) |
| **number_of_factors** | ~50 common indicators (with parameter variants: 100+) |
| **implementation_difficulty** | LOW — well-documented, many Python libraries (TA-Lib, pandas-ta) |
| **crypto_transferability** | HIGH — these indicators are already widely used in crypto. No adaptation needed beyond parameter tuning. |
| **notes** | Already partially covered by V0 probes (RSI, BB Z-Score). Remaining indicators are straightforward to implement. Main research question is which indicators provide incremental information beyond the V0 probes. |

---

## 5. Crypto-Specific Factor Families

| Field | Value |
|-------|-------|
| **source_name** | Crypto-native Derivatives and Microstructure Factors |
| **citation** | Industry research (Binance, Glassnode, Coinglass, etc.) |
| **asset_class_origin** | Crypto perpetual futures and spot markets |
| **typical_data_requirements** | Varies — see sub-families below |
| **factor_style** | Cross-sectional and time-series; crypto-native |

### 5.1 Funding Rate

| Field | Value |
|-------|-------|
| **data_requirements** | Perpetual futures funding rate (Binance API: `fundingRate`) |
| **description** | Funding rate reflects the cost of holding long positions. Positive funding = longs pay shorts (bullish crowding). |
| **example_factors** | `funding_rate`, `funding_rate_ma_8h`, `funding_rate_zscore`, `funding_rate_change_24h` |
| **transferability** | `requires_derivatives_data` — available from Binance API but not in current OHLCV bars |
| **difficulty** | LOW if data available |

### 5.2 Open Interest

| Field | Value |
|-------|-------|
| **data_requirements** | Open interest data (Binance API: `openInterestHist`) |
| **description** | Total outstanding notional value of perpetual contracts. Rising OI + rising price = new longs entering. |
| **example_factors** | `oi_change_1h`, `oi_change_pct_24h`, `oi_vs_vol_ratio`, `oi_zscore` |
| **transferability** | `requires_derivatives_data` — available from Binance API |
| **difficulty** | LOW if data available |

### 5.3 Basis (Spot-Futures Spread)

| Field | Value |
|-------|-------|
| **data_requirements** | Spot price + futures price (Binance spot + perp APIs) |
| **description** | Basis = futures price - spot price. Positive basis = contango (bullish). Negative basis = backwardation (bearish). |
| **example_factors** | `basis_1q`, `basis_annualized`, `basis_change_24h`, `basis_zscore` |
| **transferability** | `requires_derivatives_data` — needs both spot and perp data |
| **difficulty** | MEDIUM — need to align spot and perp timestamps |

### 5.4 Liquidation

| Field | Value |
|-------|-------|
| **data_requirements** | Liquidation data (Coinglass API or exchange WebSocket) |
| **description** | Forced close of leveraged positions. Cascade liquidations amplify price moves. |
| **example_factors** | `liq_volume_1h`, `liq_imbalance` (long vs short), `liq_cascade_flag`, `liq_volume_ratio` |
| **transferability** | `requires_external_data` — not available from standard exchange APIs; needs Coinglass or similar |
| **difficulty** | HIGH — data is fragmented across providers |

### 5.5 Long/Short Ratio

| Field | Value |
|-------|-------|
| **data_requirements** | Long/short account ratio (Binance API: `globalLongShortAccountRatio`) |
| **description** | Ratio of accounts with net long vs net short positions. Extreme readings may signal reversals. |
| **example_factors** | `ls_ratio`, `ls_ratio_zscore`, `ls_ratio_change_24h` |
| **transferability** | `requires_derivatives_data` — available from Binance API |
| **difficulty** | LOW if data available |

### 5.6 Taker Buy/Sell Imbalance

| Field | Value |
|-------|-------|
| **data_requirements** | Aggregated trades with buy/sell classification (Binance API: `aggTrades`) |
| **description** | Net taker buy volume - taker sell volume. Positive = aggressive buying pressure. |
| **example_factors** | `taker_buy_sell_ratio`, `taker_imbalance_1h`, `taker_imbalance_zscore` |
| **transferability** | `requires_microstructure_data` — available from Binance aggTrades but not in standard OHLCV bars |
| **difficulty** | MEDIUM — need to aggregate from trade-level data |

### 5.7 Volume Pressure

| Field | Value |
|-------|-------|
| **data_requirements** | OHLCV (basic) + optionally order book depth |
| **description** | Volume relative to recent average. Sudden volume spikes may precede price moves. |
| **example_factors** | `vol_ratio_1h/20h`, `vol_surprise_zscore`, `vol_price_corr` |
| **transferability** | `ohlcv_adaptable` — can be computed from standard bars |
| **difficulty** | LOW |

### 5.8 Exchange Flow / Reserve

| Field | Value |
|-------|-------|
| **data_requirements** | On-chain exchange flow data (Glassnode, CryptoQuant) |
| **description** | Net flow of tokens to/from exchanges. Large outflows may signal accumulation. |
| **example_factors** | `exchange_net_flow`, `exchange_reserve_change`, `whale_transfer_volume` |
| **transferability** | `requires_external_data` — on-chain data not available from exchange APIs |
| **difficulty** | HIGH — requires on-chain data provider subscription |

---

## Summary

| Source Family | # Factors (approx) | Data Requirement | Transferability | Priority |
|--------------|--------------------|-----------------|-----------------|---------|
| WQ101 | 101 | OHLCV + amount | MODERATE | HIGH |
| GTJA191 | 191 | OHLCV + financials (some) | MODERATE | MEDIUM |
| Alpha158 | 158 | OHLCV + VWAP | HIGH | HIGH |
| Alpha360 | 360 raw | OHLCV + VWAP | HIGH | MEDIUM |
| Technical Indicators | ~50 | OHLCV | HIGH | MEDIUM |
| Funding Rate | ~4 | derivatives API | MODERATE | HIGH |
| Open Interest | ~4 | derivatives API | MODERATE | HIGH |
| Basis | ~4 | spot + perp | MODERATE | MEDIUM |
| Liquidation | ~4 | external provider | LOW | LOW |
| Long/Short Ratio | ~3 | derivatives API | MODERATE | MEDIUM |
| Taker Imbalance | ~3 | aggTrades | MODERATE | MEDIUM |
| Volume Pressure | ~3 | OHLCV | HIGH | MEDIUM |
| Exchange Flow | ~3 | on-chain provider | LOW | LOW |
