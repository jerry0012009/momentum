# PM-08 Factor Candidate Source Map

**Date:** 2026-06-21
**Type:** Documentation / analysis only. No code changes, no new factors, no intake run, no signal modification.

---

## 1. Current Library: Alpha158 / q158 / OHLCV-Derived Factors

The current registry has **65 factors** across 22 families. Only **1 factor** is explicitly from the Alpha158 family:

| factor_id | family | formula_proxy | required_columns | direction | in_signal |
|-----------|--------|---------------|-----------------|-----------|-----------|
| q158_high_low_range | alpha158 | (high - low) / close | high, low, close | conditional | No |

Additionally, **3 WorldQuant 101-style factors** exist:

| factor_id | family | formula_proxy | required_columns | direction | in_signal |
|-----------|--------|---------------|-----------------|-----------|-----------|
| wq101_alpha101 | wq101 | (close - open) / (high - low + eps) | open, high, low, close | conditional | No |
| wq101_alpha12 | wq101 | sign(dvol) * (-dclose) | volume, close | conditional | No |
| wq101_alpha53 | wq101 | -delta(intraday_position, 9) | high, low, close | conditional | No |

**OHLCV-derived factors already implemented** (not labeled alpha158 but using OHLCV data):

| factor_id | family | formula_proxy | required_columns |
|-----------|--------|---------------|-----------------|
| range_1h | range_position | (high - low) / close | high, low, close |
| range_4h | range_position | (HH4 - LL4) / close | high, low, close |
| range_24h | range_position | (HH24 - LL24) / close | high, low, close |
| candle_body | intraday_candle | (close - open) / (high - low + eps) | open, high, low, close |
| candle_wick_upper | intraday_candle | (high - max(open, close)) / (high - low + eps) | open, high, low, close |
| candle_wick_lower | intraday_candle | (min(open, close) - low) / (high - low + eps) | open, high, low, close |
| price_pos_24h | price_position | (close - LL24) / (HH24 - LL24 + eps) | high, low, close |
| price_pos_72h | price_position | (close - LL72) / (HH72 - LL72 + eps) | high, low, close |
| price_pos_120h | price_position | (close - LL120) / (HH120 - LL120 + eps) | high, low, close |
| breakout_dist_20h | breakout | (close - HH20) / (HH20 - LL20 + eps) | high, low, close |
| breakout_dist_48h | breakout | (close - HH48) / (HH48 - LL48 + eps) | high, low, close |
| tech_atr | technical | Average True Range 14 bars | high, low, close |
| williams_r_14h | technical_indicators | (HH14 - close) / (HH14 - LL14 + eps) | high, low, close |
| wq101_alpha53 | wq101 | -delta(intraday_position, 9) | high, low, close |

**Conclusion:** The library has decent OHLCV coverage but very few Alpha158-specific factors. Only 1/158 Alpha158 factors are implemented.

---

## 2. Candidate Factor Classification

### A. ALREADY_IMPLEMENTED (cannot duplicate)

These Alpha158 factors are already covered by existing factors:

| Alpha158 ID | Formula | Already Implemented As |
|-------------|---------|----------------------|
| KMID | (close - open) / close | candle_body (normalized differently) |
| KLEN | (high - low) / close | range_1h, q158_high_low_range |
| KMID2 | (close - open) / (high - low) | candle_body, wq101_alpha101 |
| KUP | (high - max(open, close)) / close | candle_wick_upper (normalized differently) |
| KUP2 | (high - max(open, close)) / (high - low) | candle_wick_upper |
| KLOW | (min(open, close) - low) / close | candle_wick_lower (normalized differently) |
| KLOW2 | (min(open, close) - low) / (high - low) | candle_wick_lower |
| KSFT | skewness(ret, N) | realized_skew_20h |
| ROC_5h | close/close_5h_ago - 1 | mom_5h |
| ROC_10h | close/close_10h_ago - 1 | mom_10h |
| ROC_20h | close/close_20h_ago - 1 | mom_20h |
| MA_Cross | SMA(fast) / SMA(slow) - 1 | ma_gap_5_20, ma_gap_10_40, ma_gap_20_80 |
| WVMA | rolling_std(ret*vol) / rolling_mean(vol) | vol_of_vol_20h (similar concept) |
| VSMA | volume / delay(volume, d) | vol_zscore_20h, qvol_zscore_20h |

### B. IMPLEMENTABLE_NOW (OHLCV only, can add immediately)

| Alpha158 ID | Conceptual Formula | Required Columns | Novelty vs Current Library |
|-------------|-------------------|-----------------|--------------------------|
| ROC_1h | close / close_1h_ago - 1 | close | **Partial overlap:** xs_rank_ret_1h exists but is cross-sectional normalized. Pure ROC_1h is different. |
| ROC_40h | close / close_40h_ago - 1 | close | **Novel:** No 40h momentum factor exists. |
| ROC_72h | close / close_72h_ago - 1 | close | **Exists:** mom_72h already registered. |
| ROC_120h | close / close_120h_ago - 1 | close | **Exists:** mom_120h already registered. |
| VWAP_Dev | (close - VWAP_N) / VWAP_N | close, volume | **Novel:** No VWAP deviation factor exists. |
| WVMA_N | rolling_std(ret*volume, N) / rolling_mean(volume, N) | close, volume | **Novel:** Volume-weighted volatility. Different from vol_of_vol. |
| KLOW_close | (min(open,close) - low) / close | open, high, low, close | **Partial:** candle_wick_lower uses /range normalization. /close normalization is different. |
| KSFT_short | skewness(ret, 5) | close | **Novel:** Short-window skewness. realized_skew_20h uses 20-bar window. |
| Intraday_Ret | (close - open) / open | open, close | **Novel:** Simple intraday return. Not in library. |
| Volume_xs_rank | cross-sectional rank(volume) | volume | **Exists:** xs_rank_vol already registered. |

### C. NEEDS_NEW_DATA

| Factor Type | Required Data | Current Status |
|-------------|--------------|----------------|
| Taker buy imbalance | taker_buy_quote_volume | Registered (3 factors) but data not downloaded |
| Funding rate | funding_rate | Registered (3 factors) but data not downloaded |
| Open interest | open_interest | Not available |
| Basis / futures-spot spread | spot_price | Not available |
| Orderbook depth | bid/ask depth | Not available |
| Borrow rate | borrow_rate | Not available |
| Market cap | circulating_supply * price | Not available |
| Fundamental | on-chain metrics | Not available |

### D. NOT_SUITABLE_FOR_CURRENT_CRYPTO_PERP

| Factor Type | Reason |
|-------------|--------|
| Earnings-related (SUE, EP surprise) | No earnings for crypto |
| Analyst revision | No analyst coverage |
| Sector rotation | No GICS sectors in crypto |
| Market-cap weighted factors | No market cap data |
| Short interest | No short interest data for perps |
| Dividend yield | No dividends in crypto |
| Correlation-to-market (beta) | Could implement but concept is equity-specific |
| Book-to-market | No book value for crypto |

---

## 3. First Batch: Recommended 6 Factors

### Candidate 1: `vwap_dev_20h`

- **Conceptual formula:** `(close - vwap_20h) / vwap_20h` where `vwap_20h = rolling_sum(close * volume, 20) / rolling_sum(volume, 20)`
- **Required columns:** close, volume
- **Expected direction:** conditional (mean-reversion: negative when above VWAP, positive when below)
- **Lookback window:** 20
- **Why implementable now:** Only needs close and volume, both available
- **Redundancy risk:** LOW — no existing VWAP-based factor
- **Reason for inclusion:** Classic microstructure signal; measures price vs volume-weighted consensus
- **Not yet promoted:** Not implemented

### Candidate 2: `wvma_20h`

- **Conceptual formula:** `rolling_std(ret_1h * volume, 20) / rolling_mean(volume, 20)`
- **Required columns:** close, volume
- **Expected direction:** negative (high volume-weighted vol → risk-off)
- **Lookback window:** 21 (pct_change + std(20))
- **Why implementable now:** Only needs close and volume
- **Redundancy risk:** MODERATE — vol_of_vol_20h exists but uses different construction (std of std vs volume-weighted std)
- **Reason for inclusion:** Captures volume-volatility interaction; qlib Alpha158 standard factor
- **Not yet promoted:** Not implemented

### Candidate 3: `vol_ret_corr_20h`

- **Conceptual formula:** `rolling_corr(ret_1h, delta(volume, 1), 20)` — correlation between returns and volume changes
- **Required columns:** close, volume
- **Expected direction:** conditional (positive = trend confirmation, negative = divergence)
- **Lookback window:** 21 (pct_change + delta + corr(20))
- **Why implementable now:** Only needs close and volume
- **Redundancy risk:** LOW — price_volume_corr_20h uses quote_volume, this uses raw volume; different normalization
- **Reason for inclusion:** Volume-return correlation captures trend confirmation; different from existing price_volume_corr_20h which uses quote_volume pct_change
- **Not yet promoted:** Not implemented

### Candidate 4: `intraday_ret`

- **Conceptual formula:** `(close - open) / open`
- **Required columns:** open, close
- **Expected direction:** conditional
- **Lookback window:** 1
- **Why implementable now:** Only needs open and close
- **Redundancy risk:** LOW — candle_body uses /range normalization, this uses /open normalization
- **Reason for inclusion:** Simple intraday return; captures overnight vs intraday drift patterns
- **Not yet promoted:** Not implemented

### Candidate 5: `klow_close`

- **Conceptual formula:** `(min(open, close) - low) / close`
- **Required columns:** open, low, close
- **Expected direction:** positive (long lower wick = buying pressure)
- **Lookback window:** 1
- **Why implementable now:** Only needs OHLC
- **Redundancy risk:** LOW — candle_wick_lower uses /range normalization, this uses /close normalization (different scale behavior)
- **Reason for inclusion:** Lower shadow as fraction of price; Alpha158 standard; complements existing candle_wick_lower
- **Not yet promoted:** Not implemented

### Candidate 6: `ksft_5h`

- **Conceptual formula:** `rolling_skewness(ret_1h, 5)`
- **Required columns:** close
- **Expected direction:** conditional (positive skew = momentum continuation; negative skew = reversal)
- **Lookback window:** 6 (pct_change + skew(5))
- **Why implementable now:** Only needs close
- **Redundancy risk:** LOW — realized_skew_20h uses 20-bar window; 5h is a much shorter regime
- **Reason for inclusion:** Short-window asymmetry; captures microstructure-level return distribution shifts
- **Not yet promoted:** Not implemented

---

## 4. Explicitly Excluded Factors and Reasons

| Factor | Reason Excluded |
|--------|----------------|
| ROC_5h, ROC_10h, ROC_20h | Duplicate of mom_5h, mom_10h, mom_20h (already registered) |
| ROC_72h, ROC_120h | Duplicate of mom_72h, mom_120h (already registered) |
| MA_Cross variants | Duplicate of ma_gap_5_20, ma_gap_10_40, ma_gap_20_80 |
| KMID, KLEN, KMID2, KUP, KUP2, KLOW2 | Duplicate of candle_body, range_1h, candle_wick_upper/lower |
| KSFT_20h | Duplicate of realized_skew_20h |
| WVMA_5h | Too short; overlaps with vol_5h conceptually |
| Volume_xs_rank | Duplicate of xs_rank_vol |
| Taker/funding factors (6) | Need data not currently downloaded |
| Open interest factors | Data not available |
| Basis factors | Data not available |
| Earnings/analyst/sector factors | Not applicable to crypto perps |
| Market-cap factors | Data not available |

---

## 5. Multi-Factor Research Report Handling Principle

**Rule:** No factor from external research reports may be implemented unless:
1. The report provides a specific, verifiable formula (not just a factor name)
2. The formula is documented with exact column references and computation steps
3. The source (PDF, URL, or quoted formula text) is attached to the PM task
4. A separate PM task is created for implementation after formula verification

**Rationale:** "凭空研报因子" (factors invented from vague report descriptions) risk:
- Incorrect formula reconstruction
- Invisible bugs from ambiguous specifications
- Redundancy with existing factors
- Attribution errors

If Jerry wants to extract factors from research reports, the workflow is:
1. Share the report PDF/link
2. Identify specific factors with exact formulas
3. Create a PM task for each factor with formula specification
4. Implement through standard intake pipeline

---

## 6. Non-Change Statement

This task did not:
- Modify `scripts/factor_formula_registry.py`
- Modify `scripts/factor_ops.py`
- Modify `scripts/factor_specs.py`
- Add any new factors
- Compute any factor_values
- Run factor intake
- Modify signal panel
- Modify any data files
- Make any production, alpha, or tradeability claims
