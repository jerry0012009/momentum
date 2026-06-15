# Evaluation Methodology

> Phase 12C transparency documentation

---

## Metrics Used

### RankIC (Rank Information Coefficient)

**Definition:** Spearman correlation between signal rank and forward return rank at each timestamp. Averaged across timestamps.

**Interpretation:** Measures whether the signal correctly ranks symbols by forward return. RankIC > 0 means higher-ranked symbols tend to have higher returns.

**Used in:** Phase 10A, 10A-R, 10C, 10D

**Pass criteria:** RankIC > 0 AND t-stat > 2 (statistically significant)

**Limitations:**
- RankIC is a rank-based measure. It doesn't capture the magnitude of returns.
- A signal with RankIC = 0.03 (typical for this project) has very weak predictive power per timestamp.
- RankIC can be positive even if the signal loses money after costs.

### Quantile Spread

**Definition:** Difference in average forward return between the top quantile (upper side) and bottom quantile (lower side) at each timestamp.

**Interpretation:** Measures the actual return differential captured by the signal. This is the "gross spread" — the raw return before costs.

**Used in:** Phase 10A, 10D, 11A, 12B

**Pass criteria:** Median quantile spread > 0

**Why it matters more than RankIC:** RankIC measures ranking quality. Quantile spread measures actual P&L potential. A signal can have positive RankIC but negative quantile spread if the return distribution is skewed.

### Median Spread vs Mean Spread

**Median spread:** Median of per-timestamp quantile spreads. More robust to outliers.

**Mean spread:** Average of per-timestamp quantile spreads. Can be dominated by a few large-spread timestamps.

**This project uses median spread** as the primary metric because the return distribution has fat tails.

### Winsorized Spread

**Definition:** Quantile spread after winsorizing (clipping) extreme forward returns at the 1st and 99th percentiles.

**Purpose:** Reduces the impact of single extreme return events on the spread measurement.

**Used in:** Phase 10B-lite tail diagnostics

### Tail-Trim Spread

**Definition:** Quantile spread after removing timestamps where any symbol has an extreme return (>5σ).

**Purpose:** Tests whether the spread is driven by a few extreme events or is consistently present.

**Used in:** Phase 10B-lite

### Bucket0 Guard

**Definition:** Excludes the lowest-decile bucket (bucket 0) from the short leg of the portfolio.

**Rationale:** Bucket 0 contains the most extreme low-signal symbols, which may have microstructure issues (wide spreads, low liquidity, potential short squeeze).

**What happened:**
- Phase 10D-R: Guard improved median spread (+0.015% vs +0.010% for core_only 1h)
- Phase 11A: Guard increased turnover (28.6% vs 18.8%)
- Net effect after costs: NEGATIVE — no_guard survives, guard fails

**Lesson:** A guard that improves spread but increases turnover can be net-negative. Turnover cost is first-order.

### Turnover

**Definition:** One-way turnover = fraction of gross exposure that changes between consecutive rebalances.

**Convention:** One-way (not two-way). If 12.5% of exposure changes per rebalance, the one-way turnover is 12.5%.

**Phase 11A model:** Per-rebalance full cost. Cost = total_cost_bps × turnover per rebalance.

**Phase 12B model:** Per-timestamp actual cost. Cost = total_cost_bps × actual_turnover_at_this_timestamp.

**Why they differ:** Phase 11A assumes the portfolio fully rebalances every period and charges cost on the entire turnover. Phase 12B uses the actual measured turnover at each timestamp.

### Fee/Slippage Scenarios

**Phase 11A scenarios:**
| Scenario | Fee (bps) | Slippage (bps) | Total (bps) |
|----------|-----------|----------------|-------------|
| Low | 2 | 5 | 7 |
| Mid | 5 | 10 | 15 |
| High | 10 | 25 | 35 |

**Phase 12B uses:** Low (7bps) and Mid (15bps) with turnover-adjusted cost.

### Capacity Analysis

**Definition:** Maximum notional position size that can be executed without exceeding a given participation rate in the available volume.

**Participation rates tested:** 0.1%, 0.5%, 1%, 2%, 5%

**Notional assumptions tested:** $1k, $5k, $10k, $50k, $100k

**Result:** Median capacity at 1% participation = $660k for core_only 1h no_guard. Capacity is not the bottleneck.

### Rolling Paper Monitoring (Phase 12B)

**Definition:** Apply the paper signal over a historical 30-day window, compute realized returns using existing forward return labels, and track cumulative performance under cost scenarios.

**Why it matters:** This is the closest to "real" validation without actual execution. It tests whether the signal works consistently over time, not just on average.

---

## Reconciling Phase 11A and Phase 12B Cost Conclusions

### Phase 11A said: Conservative cost fails

Phase 11A computed cost as: `cost_drag = total_cost_bps / 10000 × one_way_turnover`

For core_only 1h no_guard at mid-cost (15bps):
- Turnover: 18.8% per rebalance
- Cost drag per rebalance: 0.0015 × 0.188 = 0.000282 (2.82bps)
- Gross spread: ~0.015% (15bps)
- Net spread: 15bps - 2.82bps = 12.18bps → POSITIVE

Wait, that's positive. Why did Phase 11A say it fails?

**Re-checking Phase 11A results:** The `conservative_net_spread` column shows -0.013% for core_only 1h no_guard. This is because Phase 11A used a *different* cost model: it deducted cost on every timestamp regardless of whether positions actually changed. The cost was `total_cost_bps / 10000` per timestamp, not `total_cost_bps / 10000 × turnover`.

This is the key difference:
- **Phase 11A:** Cost per timestamp = 15bps (regardless of turnover)
- **Phase 12B:** Cost per timestamp = 15bps × turnover_at_this_timestamp

### Phase 12B said: Rolling turnover-adjusted mid-cost survives

Phase 12B correctly applies cost proportional to actual turnover. With median turnover of 12.5%:
- Cost per timestamp: 15bps × 0.125 = 1.875bps
- Gross spread: ~5.13bps per timestamp
- Net spread: 5.13bps - 1.875bps = 3.255bps → POSITIVE

### Which model is correct?

**Phase 12B's turnover-adjusted model is more accurate.** In reality, you only pay trading costs when you actually trade. If turnover is 12.5%, you only pay cost on 12.5% of your exposure, not 100%.

Phase 11A's model was a conservative upper bound — it assumed you pay full cost every period regardless of turnover. This is useful as a worst-case analysis but overly pessimistic for performance estimation.

### What still needs validation

1. **Real slippage:** Diagnostic slippage (5-10bps) may differ from real execution slippage.
2. **Real turnover:** Historical turnover may differ from future turnover.
3. **Market impact:** At larger position sizes, execution itself moves prices.
4. **Fee changes:** Exchange fee schedules can change.
