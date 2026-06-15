# Factor Handbook

> Phase 12C transparency documentation
> 10 CANDIDATE_REVIEW factors in the v0.4 factor library

---

## Overview

The 10 factors were selected from an initial pool of 18 during Phase 7 screening. Each factor is computed as a cross-sectional z-score per timestamp across all symbols in the universe.

---

## 1. vol_5h

- **Definition:** Realized volatility over the trailing 5 hours, computed as the standard deviation of log returns.
- **Intuition:** Short-term volatility captures recent price instability. High vol_5h symbols tend to be experiencing sudden moves.
- **Direction used:** Negative (multiply by -1). High recent volatility is a negative predictor of near-term forward return in the cross-section.
- **Sign-flipped:** Yes.
- **Role in signal:** Captures short-term risk. Contributes to the "avoid recent turbulence" component.
- **Limitations:** 5 hours is very short. May be noisy. Sensitive to single large moves.

## 2. vol_40h

- **Definition:** Realized volatility over the trailing 40 hours.
- **Intuition:** Medium-term volatility. More stable than vol_5h but slower to react.
- **Direction used:** Negative (multiply by -1). High medium-term volatility is also a negative predictor.
- **Sign-flipped:** Yes.
- **Role in signal:** Complements vol_5h with a smoother volatility measure.
- **Limitations:** May be too slow for 1h rebalancing. Correlated with vol_5h.

## 3. downside_vol_20h

- **Definition:** Downside volatility over 20 hours — standard deviation of negative returns only.
- **Intuition:** Measures tail risk asymmetry. A symbol with high downside_vol is dropping more violently than it rises.
- **Direction used:** Negative (multiply by -1). High downside vol is a negative predictor.
- **Sign-flipped:** Yes.
- **Role in signal:** Tail risk filter. Helps avoid symbols in free-fall.
- **Limitations:** Only captures downside moves, not the full distribution. May miss V-shaped recoveries.

## 4. vol_of_vol_20h

- **Definition:** Volatility of volatility over 20 hours — how much the rolling vol itself is changing.
- **Intuition:** Captures regime instability. A symbol with high vol_of_vol is in an unstable regime.
- **Direction used:** Negative (multiply by -1). High vol-of-vol is a negative predictor.
- **Sign-flipped:** Yes.
- **Role in signal:** Regime stability filter. Avoids symbols in chaotic regimes.
- **Limitations:** Second-order measure. Can be noisy. Hard to interpret intuitively.

## 5. rsi_7h

- **Definition:** Relative Strength Index over 7 hours. Standard RSI formula: 100 - 100/(1 + avg_gain/avg_loss).
- **Intuition:** Momentum oscillator. High RSI means the symbol has been rising recently.
- **Direction used:** Negative (multiply by -1). In the cross-section, high RSI predicts mean reversion (the symbol is overbought).
- **Sign-flipped:** Yes.
- **Role in signal:** Contrarian/momentum hybrid. Captures short-term mean reversion tendency.
- **Limitations:** RSI is bounded [0, 100], which compresses cross-sectional variation at extremes. 7h is very short.

## 6. rsi_28h

- **Definition:** RSI over 28 hours.
- **Intuition:** Longer-horizon RSI. More stable than rsi_7h.
- **Direction used:** Negative (multiply by -1). Same contrarian interpretation.
- **Sign-flipped:** Yes.
- **Role in signal:** Complements rsi_7h with a longer lookback.
- **Limitations:** Same RSI bounding issue. May be redundant with rsi_7h in trending markets.

## 7. xs_rank_vol

- **Definition:** Cross-sectional rank of quote_volume (trading volume in USD). Ranked [0, 1] across all symbols per timestamp.
- **Intuition:** Liquidity proxy. High-volume symbols are more liquid and may have different microstructure.
- **Direction used:** Positive. Used as a liquidity gate (bounded 0.50–1.00), not a directional signal.
- **Sign-flipped:** No.
- **Role in signal:** Liquidity gate in pm_full and family_balanced signals. Multiplies the raw score to reduce weight on illiquid symbols. Not used in core_only.
- **Limitations:** Volume can be manipulated (wash trading). Does not capture order book depth.

## 8. range_1h

- **Definition:** High-low range over the trailing 1 hour, normalized by close price.
- **Intuition:** Intraday volatility proxy. High range means large price swings in the last hour.
- **Direction used:** Negative (multiply by -1). Used as a position timing overlay. High range suggests the symbol has already moved and may revert.
- **Sign-flipped:** Yes (for mean-reversion hypothesis in pm_full).
- **Role in signal:** Position timing overlay in pm_full. Not used in core_only.
- **Limitations:** Overlaps with vol_5h. The sign-flip assumption (mean reversion) is debatable.

## 9. range_4h

- **Definition:** High-low range over 4 hours, normalized by close price.
- **Intuition:** Medium-term range. More stable than range_1h.
- **Direction used:** Negative (multiply by -1). Same mean-reversion interpretation.
- **Sign-flipped:** Yes (for mean-reversion hypothesis in pm_full).
- **Role in signal:** Position timing overlay in pm_full. Not used in core_only.
- **Limitations:** Same as range_1h. The 4h window may overlap with the rebalancing horizon.

## 10. price_pos_24h

- **Definition:** Current price position within the 24-hour high-low range. Formula: (close - low_24h) / (high_24h - low_24h).
- **Intuition:** Where is the price relative to its daily range? Near 1.0 = near the top, near 0.0 = near the bottom.
- **Direction used:** Negative (multiply by -1). Used as a position timing overlay. Price near the top of the range suggests limited upside.
- **Sign-flipped:** Yes (for mean-reversion hypothesis in pm_full).
- **Role in signal:** Position timing overlay in pm_full. Not used in core_only.
- **Limitations:** Bounded [0, 1]. In trending markets, price near the top may indicate strength, not weakness.

---

## Summary Table

| Factor | Direction | Sign-Flipped | Used in core_only | Used in pm_full | Role |
|--------|-----------|-------------|-------------------|-----------------|------|
| vol_5h | Negative | Yes | ✓ | ✓ | Short-term risk |
| vol_40h | Negative | Yes | ✓ | ✓ | Medium-term risk |
| downside_vol_20h | Negative | Yes | ✓ | ✓ | Tail risk |
| vol_of_vol_20h | Negative | Yes | ✓ | ✓ | Regime stability |
| rsi_7h | Negative | Yes | ✓ | ✓ | Short-term momentum |
| rsi_28h | Negative | Yes | ✓ | ✓ | Medium-term momentum |
| xs_rank_vol | Positive | No | ✗ | ✓ | Liquidity gate |
| range_1h | Negative | Yes | ✗ | ✓ | Position timing |
| range_4h | Negative | Yes | ✗ | ✓ | Position timing |
| price_pos_24h | Negative | Yes | ✗ | ✓ | Position timing |

**Key insight:** core_only uses only the first 6 factors (volatility + RSI family). pm_full adds 4 more (liquidity gate + position overlay). The additional factors did not improve gross spread, so core_only survived.
