# Factor Evaluation Standard

## What This Document Is NOT

- A scoring rubric with pass/fail cutoffs.
- A thesis for why any specific factor "works."
- A guide to optimizing thresholds.
- A guarantee that factors meeting these diagnostics will make money.
- A replacement for out-of-sample testing, live paper trading, or human judgment.

This document describes how we interpret factor diagnostics. It sets a shared vocabulary and flags common pitfalls. Nothing more.

---

## 1. Factor Library Positioning

The momentum factor library is an **alpha research library**, not a trading strategy.

A factor library answers the question: *"Is there a persistent cross-sectional relationship between this signal and forward returns?"*

A trading strategy answers: *"Given transaction costs, capacity, risk limits, and execution, can I make money from this signal?"*

The library sits upstream of strategy construction. Factors that show weak diagnostics here are unlikely to survive strategy-level costs. But factors that look clean here still need to survive slippage, crowding, regime shifts, and portfolio construction before they become tradeable.

**Practical implication:** Do not treat a passing factor diagnostic as a green light to deploy capital. Do not treat a failing diagnostic as proof the signal is useless — it may behave differently in a different universe, holding period, or market regime.

---

## 2. Evaluation Method: Cross-Sectional Factor Evaluation

We evaluate factors cross-sectionally. On each date, we rank all symbols by factor value, group them into quintiles (Q1 through Q5), and compute the mean forward return for each quintile.

This is not a time-series backtest. We are not asking "would this strategy have made money?" We are asking "does this factor sort future returns?"

Key properties of cross-sectional evaluation:

- It is **relative**: a factor can rank stocks well even if the whole market goes down.
- It is **universe-dependent**: results change if you add or remove symbols.
- It does **not** account for transaction costs, capacity, or execution.

---

## 3. Spread Definition

**Spread = Q5 mean forward return − Q1 mean forward return**

Q5 = top quintile (highest factor values). Q1 = bottom quintile (lowest factor values).

A positive spread means the factor's top-ranked stocks outperformed its bottom-ranked stocks over the forward return window. The magnitude of the spread tells you the raw economic magnitude of the sort.

The spread is a simple, intuitive summary of the quintile sort. It does not tell you about monotonicity (whether Q2 > Q3 > Q4 in order), tail behavior, or stability over time.

---

## 4. IC, RankIC, and Spread Must Be Interpreted Together

No single number tells the full story. Here is what each metric captures and what it misses:

| Metric | What it measures | What it misses |
|--------|-----------------|----------------|
| **Pearson IC** | Linear correlation between factor values and forward returns | Sensitivity to outliers; nonlinear relationships |
| **RankIC** | Rank correlation (Spearman) between factor values and forward returns | Ignores magnitude of factor values or returns; only uses ordinal rank |
| **Spread** | Economic magnitude of the top-vs-bottom quintile gap | Middle quintiles; whether the relationship is monotonic |

A factor with high RankIC but low spread has a consistent rank relationship but tiny return differences — hard to monetize after costs. A factor with high spread but low RankIC may be driven by a few extreme observations. A factor where Pearson IC diverges substantially from RankIC is a signal to investigate further (see next section).

**Read them together.** Any two without the third gives you a partial picture.

---

## 5. Overlapping Labels Inflate t-Stat

When forward returns are computed over overlapping windows (e.g., 5-day forward returns computed daily), consecutive observations share most of their return path. This means the effective sample size is much smaller than the nominal observation count.

The consequence: t-statistics and p-values from standard formulas are **overstated**. A t-stat of 3.0 with overlapping labels may correspond to an effective t-stat of 1.5 or lower, depending on the overlap ratio.

**What to do:** Be skeptical of high t-stats when you know the labels overlap. The diagnostic gate accounts for this with a deflation factor, but the right mental model is: *overlapping labels make everything look more significant than it is.*

---

## 6. Pearson IC vs. RankIC Conflict: Extreme-Value Driven Signal

When Pearson IC and RankIC point in different directions (e.g., Pearson IC is positive and large, but RankIC is near zero or negative), the most common explanation is:

**The signal is driven by extreme factor values, not by the bulk of the distribution.**

A few symbols with very high or very low factor values have outsized returns, pulling the Pearson correlation up. But when you rank everything ordinally (RankIC), those extreme points lose their leverage and the relationship in the middle of the distribution is weak or absent.

This is not necessarily bad — some real alpha signals are concentrated in tails. But it means:

- The signal is **fragile**: it depends on a few names per cross-section.
- It is **vulnerable to single-name risk**: one outlier reversal can flip the sign.
- Standard linear models will overweight these extremes; tree-based models will not.

If you see this conflict, investigate the quintile returns directly. Check whether Q5 and Q1 are doing all the work while Q2-Q4 are flat.

---

## 7. Symbol Concentration Degrades Cross-Sectional Factors

A cross-sectional factor is supposed to differentiate across many symbols. If a large fraction of the factor's variation comes from a small number of symbols (e.g., because the factor is dominated by market-cap weighting, or because a few names have extreme raw values), then:

- The "cross-sectional" evaluation is really a **few-name bet** in disguise.
- Quintile composition becomes unstable: a single symbol entering or leaving Q5 swings the whole quintile return.
- The factor's apparent performance is inseparable from the performance of those few names.

**Check for this:** Look at quintile composition over time. If Q5 is always the same 5-10 symbols, the factor is not doing cross-sectional work — it is a concentrated bet on those names.

This is especially relevant in crypto, where a small number of tokens dominate volume and market cap.

---

## 8. Current 5 Factors Are Diagnostic Probes, Not Candidate Alphas

The five factors currently in the library (momentum variants based on volume, volatility, and return patterns) were designed as **diagnostic probes** — tools to explore the return structure of the cross-section and stress-test the evaluation pipeline.

They were not designed with a specific alpha thesis. They are simple, well-understood signals that should behave in predictable ways if the pipeline is working correctly. If a diagnostic probe produces surprising results, that tells you something about either the market or the pipeline.

**Do not treat these five factors as candidate alphas to deploy.** They are calibration instruments. Real alpha research starts after the pipeline is validated.

---

## 9. Current Gate Is a Warning System, Not a Final Elimination Gate

The evaluation gate (the automated check that produces pass/fail flags on factor diagnostics) is designed as a **warning system**. Its job is to surface cases where:

- A factor's diagnostic values are inconsistent with each other (e.g., high RankIC but negative spread).
- Statistical significance is likely an artifact of overlapping labels.
- Symbol concentration makes the cross-sectional evaluation unreliable.

When the gate flags something, it means: **"Look at this more carefully."** It does not mean: **"Throw this factor away."**

Factors that fail the gate should be investigated, not automatically discarded. Factors that pass the gate should not be assumed to be good — they just did not trigger any known warning conditions.

The gate is conservative by design. It will produce false positives (flagging things that are actually fine). This is intentional. Missing a real problem is worse than extra manual review.
