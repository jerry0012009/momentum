# Large-Scale Factor Mining Protocol

> Version: 1.0 | Phase: 7A
>
> This document defines the engineering and scientific protocol for large-scale
> factor mining in the momentum project.

---

## 1. Phase 7 Goal

Build a systematic, reproducible pipeline for discovering, evaluating, and
cataloging quantitative factors — without data snooping, multiple testing bias,
or premature alpha claims.

## 2. Core Principles

### 2.1 Factor ≠ Alpha

A factor is a computed feature. A diagnostic probe. Even a factor with
statistically significant RankIC in a backtest is not alpha until it survives:

- Out-of-sample validation
- Transaction cost analysis
- Capacity analysis
- Regime robustness
- Live paper trading

**Phase 7 does not claim alpha for any factor.**

### 2.2 Dynamic Universe Is Primary

The dynamic monthly-volume universe (`crypto_usdt_perp_monthly_volume_top50_current_listed_v1`)
is the primary evaluation framework. It reduces (but does not eliminate) survivorship
and selection bias.

Static universe (`crypto_top50_usdt_perp_1h_long_v1`) is diagnostic reference only.

### 2.3 Alphalens Is External Validation

Alphalens-compatible outputs exist for cross-checking. They do not drive decisions.
The project's own evaluation kernel is the source of truth.

### 2.4 expected_direction Is Theory-Driven

`expected_direction` is set **before evaluation**, based on:
- Economic theory (e.g., momentum → positive, reversal → negative)
- Structural property (e.g., volatility → negative for risk-averse market)
- Design intent (e.g., conditional if sign depends on regime)

**It is never changed after seeing evaluation results.**

## 3. Anti-Snooping Controls

### 3.1 No PnL-Based Selection

Factors are not selected based on backtest PnL, Sharpe, or returns.
Selection is based on:
- Theoretical motivation
- Implementation quality (coverage, warmup, turnover)
- Diagnostic evaluation (RankIC, direction consistency)

### 3.2 No Multiple Testing Correction (Yet)

Phase 7 does not apply Bonferroni, FDR, or other multiple testing corrections.
Instead, it controls snooping through:
- Pre-registered candidate lists (factor_mining_candidates_v0_1.csv)
- Batch discipline (one batch at a time, full closeout before next)
- No re-evaluation of dropped factors
- No parameter grid search within a batch

### 3.3 No Factor Status Upgrade

No factor status is upgraded in Phase 7. All factors remain DIAGNOSTIC_PROBE.
Status upgrades require Phase 8 (Candidate Factor Review) with PM approval.

## 4. Batch Protocol

Each batch follows a strict pipeline:

1. **Candidate selection** — from backlog, with rationale
2. **Implementation** — factor_formula_registry.py, with tests
3. **factor_values build** — build_factor_values.py --dataset-id
4. **Dynamic evaluation** — evaluate_factors_dynamic_universe.py
5. **Coverage QA** — audit_dynamic_universe_factor_values.py
6. **Static-vs-dynamic comparison** — compare_static_dynamic_factor_evals.py
7. **No alpha promotion** — all factors stay DIAGNOSTIC_PROBE
8. **Batch closeout** — markdown report, JSON summary, commit+push

No step may be skipped. No batch may start before the previous batch's closeout
is committed.

## 5. Failed Factor Recording

Factors that fail QA or show poor evaluation are recorded in the batch closeout
with their metrics. They are not deleted from the candidate list but are marked
with status `rejected` or `deferred` and the reason.

## 6. Batch Closeout Requirements

Each batch closeout must include:

- Factor list with expected_direction
- Rows per factor, coverage, missing rates
- Evaluation summary (RankIC, direction consistency)
- Static-vs-dynamic comparison (if applicable)
- QA decision (ALLOW next batch / BLOCK)
- Explicit statement: "No factor is alpha."

## 7. Entering the Next Batch

A new batch may begin only when:
- Previous batch closeout is committed and pushed
- PM reviews and approves
- No BLOCK status from QA

## 8. What Phase 7 Does NOT Do

- No strategy backtest
- No PnL computation
- No parameter optimization
- No alpha claims
- No factor status upgrades
- No Qlib / VectorBT integration
