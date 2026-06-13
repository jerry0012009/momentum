# Factor Library Roadmap

> This is the canonical roadmap for the momentum project's factor library.
>
> Each phase builds on the previous. No phase may be skipped.
>
> Last updated: 2026-06-13

---

## Current Status

| Phase | Name | Status |
|-------|------|--------|
| Phase 0 | Project Positioning & Data Convention | DONE |
| Phase 1 | V0 Engineering Close | DONE |
| Phase 2 | V0 Audit | IN PROGRESS |
| Phase 2A | V0 Audit — Data & Pipeline | **COMPLETE** |
| Phase 2B | Lightweight Quality Gate | **COMPLETE** |
| Phase 2C | Factor Library Skeleton | **SKELETON BUILT**, pending closeout review |
| Phase 2D | External Factor Priors | NOT STARTED |
| Phase 2E | Batch Factor Evaluation | NOT STARTED |
| Phase 2F | Gate Refinement | NOT STARTED |
| Phase 3 | V1 Long-window Baseline | NOT STARTED |
| Phase 4 | Dynamic Universe | NOT STARTED |
| Phase 5 | Factor Library Expansion | NOT STARTED |
| Phase 6 | Multi-factor Combination | NOT STARTED |
| Phase 7 | Portfolio Backtest | NOT STARTED |
| Phase 8 | Cost and Risk Modeling | NOT STARTED |
| Phase 9 | Paper Trading | NOT STARTED |
| Phase 10 | Small-capital Live Validation | NOT STARTED |

**No factor promoted to alpha. No strategy backtest started.**

---

## Phase Definitions

### Phase 0: Project Positioning & Data Convention

Define what this project is and is not. Choose first universe, data source, frequency, and storage policy.

**Status:** DONE

---

### Phase 1: V0 Engineering Close

Build the minimum viable data pipeline: fetch bars, build labels, build factors, evaluate factors. Get 3–5 simple factors through the pipeline end-to-end.

**Status:** DONE

---

### Phase 2: V0 Audit

Systematically audit the V0 pipeline for timing bugs, data leaks, survivorship bias, and evaluation protocol issues.

#### Phase 2A: V0 Audit — Data & Pipeline

Audit timestamp semantics, universe definition, manifest consistency, data validation.

**Status:** COMPLETE (commit `3329165`)

#### Phase 2B: Lightweight Quality Gate

Establish baseline quality checks: calendar-time labels, gap symbol exclusion, direction-adjusted spread. These are the "always-on health checks" — not hard thresholds.

**Status:** COMPLETE (commit `140e5c0`)

#### Phase 2C: Factor Library Skeleton

Build the batch factor onboarding scaffold: catalog schema, implementation interface, evaluation protocol, test requirements, status enum, promotion rules. Ensure future factors can enter without breaking timing or data conventions.

**Status:** SKELETON BUILT, pending human closeout review

Deliverables:
- `docs/FACTOR_LIBRARY_SKELETON.md` — full skeleton spec
- `docs/FACTOR_LIBRARY_ROADMAP.md` — this file
- `docs/FACTOR_REGISTRY.md` — updated status enum
- `research/.../factor_catalog_v0_1.csv` — updated schema (12 columns)
- `research/.../PHASE_2C_PLAN.md` — phase scope
- `research/.../PHASE_2C_CLOSEOUT.md` — closeout report

#### Phase 2D: External Factor Priors

Collect and classify external factor families before implementing them.

Scope:
- Collect external factor prior families: WQ101 (101 Formulaic Alphas), GTJA191 (style factors), Alpha158/360 (Qlib)
- Map each concept into crypto-compatible factor families
- Classify which can be adapted to OHLCV-only crypto data
- Document adaptation notes (e.g., cross-sectional rank → time-series zscore)
- Do NOT implement all factors yet
- Do NOT batch evaluate yet

**Status:** NOT STARTED

#### Phase 2E: Batch Factor Evaluation

Implement and evaluate the external factors identified in Phase 2D.

Scope:
- Implement factors following the Phase 2C interface
- Run each through the evaluation pipeline
- Apply quality gate checks
- Classify results: DIAGNOSTIC_PROBE / CANDIDATE_REVIEW / PARK / DROP

**Status:** NOT STARTED

#### Phase 2F: Gate Refinement

After seeing enough factors, refine the quality gate thresholds.

Scope:
- Review IC/RankIC/spread distributions across all evaluated factors
- Adjust thresholds based on empirical evidence (not arbitrary)
- Define what "enough factors" means for gate calibration
- Document refined gate criteria

**Status:** NOT STARTED

---

### Phase 3: V1 Long-window Baseline

Replace V0's static 24h-volume universe with true 30-day rolling volume ranking. Establish the V1 baseline with refined gates.

**Status:** NOT STARTED

---

### Phase 4: Dynamic Universe

Implement monthly universe rebalancing with proper survivorship bias handling.

**Status:** NOT STARTED

---

### Phase 5: Factor Library Expansion

Add more factor families beyond the initial set. May include crypto-specific factors (funding rate, basis, OI, liquidation).

**Status:** NOT STARTED

---

### Phase 6: Multi-factor Combination

Combine CANDIDATE_FACTOR signals into composite scores. Explore equal-weight, IC-weight, and simple ML combinations.

**Status:** NOT STARTED

---

### Phase 7: Portfolio Backtest

Backtest multi-factor portfolios with position sizing, rebalancing, and risk constraints.

**Status:** NOT STARTED

---

### Phase 8: Cost and Risk Modeling

Add slippage, spread, commission, and market impact models. Add drawdown and concentration risk controls.

**Status:** NOT STARTED

---

### Phase 9: Paper Trading

Run the full strategy in paper trading mode to validate execution feasibility.

**Status:** NOT STARTED

---

### Phase 10: Small-capital Live Validation

Deploy with minimal capital for real-world validation.

**Status:** NOT STARTED

---

## Progression Rules

1. **No phase skipping.** Each phase must be completed and reviewed before the next begins.
2. **No factor is alpha.** Factors are inputs. Alpha is a property of a complete strategy with execution and costs.
3. **Human approval required.** Phase transitions require explicit human decision.
4. **Backward compatible.** Later phases must not break earlier phase conventions (timing, labels, evaluation protocol).
