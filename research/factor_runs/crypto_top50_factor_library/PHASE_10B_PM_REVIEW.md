# Phase 10B-lite — PM Review

> Date: 2026-06-15
> Status: PASS WITH PM INTERPRETATION CORRECTION

---

## 1. Review Conclusion

Phase 10B-lite passes the computational requirements.

The commit correctly added:

- bucket0 top contributor audit;
- robust spread addendum;
- PM decision matrix;
- quality checks;
- closeout and tests.

No signal flip, no overwrite of Phase 10A / 10A-R, no Phase 11, no cost/slippage/capacity analysis.

---

## 2. Key Computational Findings

1. Median per-timestamp spread is positive for most signal × horizon combinations.
2. Standard mean spread remains negative.
3. Winsorized and tail-trimmed spread remain negative but are materially smaller.
4. Bucket0 top-1% contribution is around 11%; top-5% around 28–30%, indicating moderate concentration rather than a few isolated samples.
5. Decision matrix recommends:
   - 1h/4h: tail-aware signal redesign;
   - 24h/72h: horizon-specific direction policy.

---

## 3. PM Interpretation Correction

The closeout states that negative mean spread is pulled by extreme negative outliers in the short leg. This wording is not precise.

Correct interpretation:

- Standard spread is long minus short.
- The short leg corresponds to the lowest-signal / bucket0 side.
- The observed issue is that bucket0 / short leg has unusually strong positive forward returns.
- Therefore long-minus-short spread becomes negative.

This is not simply a few isolated outliers. It is a moderate-concentration structural tail effect, with mean-vs-median divergence.

---

## 4. PM Decision

Do not proceed to Phase 11 yet.

Proceed to:

```text
Phase 10C — Tail-aware Signal Policy Design
```

Phase 10C should be design-only. It should decide how to handle:

1. bucket0 / lowest-signal tail;
2. mean-vs-median spread conflict;
3. 1h/4h direction conflict;
4. 24h/72h possible inversion;
5. whether signal v1 should avoid shorting bucket0, neutralize tails, or use horizon-specific rules.

No signal v1 backtest should be run until PM approves a design.
