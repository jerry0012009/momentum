# <Research Name> — Audit Notes

## Audit Priority

Use this file to record blocking issues before interpreting performance.

Priority levels:

- P0: blocking issue; results are not decision-useful until resolved
- P1: material issue; results can be read only with caveats
- P2: robustness issue; needed before promotion
- P3: improvement or future work

---

## P0 — Data Entry Audit

Questions:

- [ ] Is the input data frozen?
- [ ] Is a manifest available?
- [ ] Is the provider documented?
- [ ] Is the adjustment policy documented?
- [ ] Is the universe fixed before evaluation?
- [ ] Can reruns reproduce the same input rows?

Findings:

- 

Required action:

- 

---

## P0 — Timestamp and Causality Audit

Questions:

- [ ] When is the factor known?
- [ ] When is the signal known?
- [ ] When is the order executed?
- [ ] Is there same-bar signal + execution?
- [ ] Does the strategy use future confirmation?
- [ ] Are `origin_time` and `confirmed_at` separated when needed?

Findings:

- 

Required action:

- 

---

## P0 — Future Leak / Hindsight Audit

Trigger if any of the following appear:

- [ ] pivot confirmation
- [ ] swing high / swing low
- [ ] trendline
- [ ] support / resistance
- [ ] HH / LL
- [ ] segment lifecycle
- [ ] delayed state machine confirmation
- [ ] regime labels that rewrite historical bars
- [ ] future bucket labels
- [ ] same-bar signal and execution

Findings:

- 

Required action:

- 

---

## P1 — Indicator / Factor Calculation Audit

Questions:

- [ ] Are indicators separated from the backtest?
- [ ] Are rolling windows strictly causal?
- [ ] Are warmup periods handled?
- [ ] Are factor values exported?
- [ ] Are factor formulas documented?

Findings:

- 

Required action:

- 

---

## P1 — Signal and Execution Audit

Questions:

- [ ] Are signals exported separately?
- [ ] Are signal reasons recorded?
- [ ] Is `tradable_at` recorded?
- [ ] Is execution price realistic?
- [ ] Is same-bar execution labeled as optimistic if used?

Findings:

- 

Required action:

- 

---

## P1 — Cost Model Audit

Questions:

- [ ] Commission included?
- [ ] Slippage included?
- [ ] Spread included?
- [ ] Funding / borrow / tax included where relevant?
- [ ] Cost sensitivity tested?

Findings:

- 

Required action:

- 

---

## P1 — PnL / Drawdown / Sharpe Audit

Questions:

- [ ] Is PnL gross or net?
- [ ] Is return simple or compounded?
- [ ] Is drawdown bar-level or trade-level?
- [ ] Is Sharpe standard bar-level or trade-level simplified?
- [ ] Is an equity curve exported?

Findings:

- 

Required action:

- 

---

## P2 — Parameter Search and Selection Bias

Questions:

- [ ] Were parameters chosen before or after seeing results?
- [ ] Is there train/test or walk-forward validation?
- [ ] Is there data snooping risk?
- [ ] Does performance survive parameter perturbation?
- [ ] Is the number of tried combinations disclosed?

Findings:

- 

Required action:

- 

---

## P2 — Robustness

Questions:

- [ ] Across assets?
- [ ] Across time windows?
- [ ] Across market regimes?
- [ ] Across cost assumptions?
- [ ] Across execution assumptions?

Findings:

- 

Required action:

- 

---

## Audit Summary

```yaml
audit_status: REVIEW_REQUIRED
blocking_issues_open: true
promotion_allowed: false
```

Summary:

- 
