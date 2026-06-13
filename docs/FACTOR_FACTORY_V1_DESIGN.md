# Factor Factory v1 — Design Document

> Date: 2026-06-13
>
> Status: IMPLEMENTED

---

## 1. Why Not Use Existing Frameworks

### Why not Qlib as core?

- Qlib's expression engine is powerful but introduces opaque data transformations
- Our crypto data protocol (bar_close_time timestamps, per-symbol groupby, no cross-symbol rolling) doesn't map cleanly to Qlib's default data handlers
- Qlib's Alpha expression parser is designed for Chinese A-share factor formulas — our factors are simpler OHLCV-based
- Dependency overhead: Qlib pulls in a large ecosystem we don't need yet
- **What we borrow later:** Qlib's Alpha expression parser if we need to batch-translate 100+ formula factors

### Why not Alphalens as core?

- Alphalens assumes a specific data format (MultiIndex with asset/date) that adds transformation overhead
- Its IC/turnover/quantile analysis is excellent but we already have a working evaluation pipeline
- Alphalens is unmaintained (last release 2020)
- **What we borrow later:** Alphalens-style tear sheets for presentation if we need publication-quality reports

### Why not VectorBT now?

- VectorBT is for portfolio backtesting, not factor computation
- We're not at the backtest stage yet — still in factor discovery
- **What we borrow later:** VectorBT for portfolio construction and execution simulation when we have alpha-worthy factors

## 2. What We Self-Develop

A lightweight Python factor factory with:

- **Factor ops** — pure-function building blocks (delay, delta, rolling_mean, etc.)
- **Factor specs** — dataclass declaring each factor's metadata and compute function
- **Factor registry** — central list of all registered FactorSpec objects
- **Integration** — build_factor_values.py iterates the registry instead of hand-coding each factor

## 3. Architecture

```
scripts/
├── factor_ops.py              # Pure-function building blocks
├── factor_specs.py            # FactorSpec dataclass definition
├── factor_formula_registry.py # Registry of all 11 FactorSpec objects
├── crypto_factor_functions.py # Legacy batch1 functions (kept for reference)
├── build_factor_values.py     # Modified: iterates registry
└── evaluate_factors.py        # Unchanged
```

### Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| `factor_ops.py` | Stateless pure functions: delay, delta, rolling_mean, etc. |
| `factor_specs.py` | FactorSpec dataclass: factor_id, family, required_columns, lookback_window, expected_direction, compute_fn, status |
| `factor_formula_registry.py` | `REGISTRY: list[FactorSpec]` — all registered factors |
| `build_factor_values.py` | Iterates REGISTRY, calls compute_fn per symbol group, writes parquet |

### Data Flow

```
bars_1h.parquet
    ↓ groupby("symbol")
    ↓ for each FactorSpec in REGISTRY:
    ↓     spec.compute_fn(group_df) → Series
    ↓ write factor_values.parquet per factor
```

## 4. Implementation Plan

1. **Phase 4a (this task):** factor_ops + factor_specs + registry + migrate 11 factors
2. **Phase 4b:** Add more ops if needed (e.g., rank, decay_linear, stddev_ratio)
3. **Phase 4c:** Batch 2 factor expansion using the registry
4. **Phase 4d:** Formula parser (optional, only if >50 factors need it)

## 5. Forbidden Scope

- No Qlib integration
- No Alphalens integration
- No VectorBT integration
- No formula DSL / expression parser
- No industry neutralization (crypto has no sectors)
- No cross-symbol rolling
- No shift(-k) future leak
- No strategy backtest
- No portfolio construction
