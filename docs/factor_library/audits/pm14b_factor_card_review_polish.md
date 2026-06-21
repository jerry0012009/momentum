# PM-14B Factor Card Review and Polish

**Date:** 2026-06-21
**Follows:** PM-14A (bilingual factor cards)

---

## Summary Verdict

**`FACTOR_CARD_REVIEW_PASS_WITH_FLAGS`**

All 71 factor cards have been reviewed and polished with per-factor overrides. Generic template text has been replaced with formula-specific, domain-aware explanations. Quality distribution is reasonable: 41 COMPLETE, 21 DIRECTION_AMBIGUOUS, 6 NEEDS_REVIEW, 3 FORMULA_AMBIGUOUS.

---

## 1. Files Changed/Generated

| File | Action |
|------|--------|
| `scripts/build_factor_bilingual_cards.py` | Modified: added overrides loading |
| `factor_metadata/factor_card_overrides.json` | Created: 71 per-factor overrides |
| `factor_metadata/factor_bilingual_cards.csv` | Regenerated |
| `factor_metadata/factor_bilingual_cards.json` | Regenerated |
| `factor_metadata/factor_card_qa_report.csv` | Created: 71 rows |
| `factor_metadata/manifest.json` | Regenerated |

Generator remains **reproducible**: `python scripts/build_factor_bilingual_cards.py` regenerates all outputs deterministically from registry + diagnostics + overrides.

---

## 2. Factor Count Coverage

- Expected: 71
- Generated: 71
- Missing: 0
- Overrides applied: 71/71 (497 total field overrides)

---

## 3. Metadata Quality Distribution

| Quality | PM-14A (Before) | PM-14B (After) | Description |
|---------|-----------------|----------------|-------------|
| AUTO_GENERATED_REVIEW_REQUIRED | 71 | **0** | Eliminated |
| COMPLETE | 0 | **41** | Hand-reviewed, polished |
| DIRECTION_AMBIGUOUS | 0 | **21** | Conditional direction factors |
| NEEDS_REVIEW | 0 | **6** | Taker/funding diagnostic-only |
| FORMULA_AMBIGUOUS | 0 | **3** | WQ101 factors (unknown direction) |

---

## 4. Data Source Type Distribution

| Type | Count |
|------|-------|
| MOMENTUM_REVERSAL | 12 |
| VOLATILITY | 8 |
| TECHNICAL | 12 |
| HYBRID | 10 |
| PRICE_POSITION | 7 |
| RANGE_CANDLE | 3 |
| CROSS_SECTIONAL | 2 |
| VOLUME | 8 |
| TAKER_FLOW | 3 |
| FUNDING_RATE | 3 |

---

## 5. Examples of Improved Cards

**Momentum (mom_20h) — COMPLETE:**
- Before: "Measures price continuation over 20h. Higher values indicate stronger recent upward drift."
- After: "20-hour price momentum: how much price has risen or fallen over the last 20 bars. In a trending market, momentum tends to persist (trend continuation)."
- Limitations now specific: "Momentum can reverse sharply in choppy/range-bound markets. Lookback of 20h is medium-term."

**Volatility (volatility_20h) — COMPLETE:**
- Before: "Measures return dispersion over 21h. Higher volatility = larger typical price swings."
- After: "20-hour realized volatility: standard deviation of hourly returns over 20 bars. Measures how much price typically moves per hour."
- Direction explanation now specific: "high-volatility assets historically underperform low-volatility assets in crypto cross-sections (volatility risk premium anomaly)."

**Taker (taker_buy_ratio_20h) — NEEDS_REVIEW:**
- Before: "Measures taker buy vs sell pressure over 20h. Requires taker-enriched bars."
- After: "20h taker buy ratio: rolling mean of (taker buy quote volume / total quote volume) over 20 bars. Measures buyer aggressiveness. NOT a standalone trading signal — diagnostic of flow conditions."
- Now explicitly marked as diagnostic-only.

**Funding (funding_rate_level_20h) — NEEDS_REVIEW:**
- Before: "Perpetual funding rate metric over 20h. High funding = crowded long."
- After: "20h funding rate level: rolling mean of perpetual funding rate over 20 bars. High positive funding = crowded longs paying shorts."
- Limitation now specific: "Funding rate has structural low coverage for newer symbols (8h settlement intervals)."

**Conditional (vwap_dev_20h) — DIRECTION_AMBIGUOUS:**
- Before: "Alpha158-derived factor using OHLCV data."
- After: "20h VWAP deviation: how far current price is from the 20-hour volume-weighted average price. Positive = price above VWAP."
- Direction: "price above VWAP can mean either bullish continuation or mean-reversion opportunity, depending on regime."

---

## 6. Remaining Review Flags and Why

**DIRECTION_AMBIGUOUS (21 factors):** Range, candle, price position, cross-sectional, correlation, skewness, kurtosis, vol ratio, RSI, ATR, intraday return factors. These have genuinely conditional direction that depends on market regime — marking them COMPLETE would be dishonest.

**NEEDS_REVIEW (6 factors):** 3 taker + 3 funding rate factors. These are diagnostics of flow/carry/crowding conditions, not standalone trading signals. Marking COMPLETE would overstate their utility. Human domain expert should validate their diagnostic interpretation.

**FORMULA_AMBIGUOUS (3 factors):** WQ101 alpha101/alpha12/alpha53. Direction intentionally left conditional to avoid post-hoc fitting. Requires empirical diagnostics to determine direction.

---

## 7. Non-Change Statement

- No factor formulas modified.
- No `scripts/factor_formula_registry.py` modified.
- No `scripts/factor_ops.py` modified.
- No factor_values modified.
- No factor diagnostics metrics modified.
- No signal panel modified.
- No public HTML pages modified.

---

## 8. Recommended Next PM

**PM-15: Integrate diagnostics metrics and bilingual cards into factor-evaluation.html**

Upgrade the existing `reports/site/factor-library/factor-evaluation.html` page with bilingual cards and diagnostics data.
