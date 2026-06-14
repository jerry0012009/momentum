# Factor Library Roadmap

> This is the canonical roadmap for the momentum project's factor library.
>
> Each phase builds on the previous. No phase may be skipped.
>
> See also: `docs/RESEARCH_PHASE_CONSTITUTION.md` for full constraints.

---

## Current Status

| Phase | Name | Status |
|-------|------|--------|
| Phase 0 | Project Positioning & Data Contract | **COMPLETE** |
| Phase 1 | V0 Engineering Loop | **COMPLETE** |
| Phase 2 | Evaluation Protocol & Factor Library Skeleton | **COMPLETE** |
| Phase 3 | Long-window Baseline | **COMPLETE** |
| Phase 4 | Factor Factory & Evaluation Platform v1 | **COMPLETE** |
| Phase 5 | Alphalens-compatible Export / External Tool Compatibility | **COMPLETE** |
| Phase 6 | Dynamic Universe & Survivorship Control | **COMPLETE** |
| Phase 7 | Large-scale Factor Mining | NOT STARTED |
| Phase 8 | Candidate Factor Review | NOT STARTED |
| Phase 9 | Multi-factor Signal Construction | NOT STARTED |
| Phase 10 | Strategy Backtest with Borrowed Engine | NOT STARTED |
| Phase 11 | Cost / Slippage / Capacity / Risk | NOT STARTED |
| Phase 12 | Paper Trading | NOT STARTED |
| Phase 13 | Small-capital Live Validation | NOT STARTED |

**No factor promoted to alpha. No strategy backtest started.**

---

## Phase Definitions

### Phase 0: Project Positioning & Data Contract

Define what this project is and is not. Choose universe, data source, frequency, storage policy, timestamp convention.

**Status:** COMPLETE

---

### Phase 1: V0 Engineering Loop

Build the minimum viable data pipeline: fetch bars → build labels → build factors → evaluate factors. Get 5 simple OHLCV factors through end-to-end.

**Status:** COMPLETE

---

### Phase 2: Evaluation Protocol & Factor Library Skeleton

Systematically build the evaluation protocol: data audit, quality gates, factor library skeleton, external factor priors, batch factor evaluation.

Sub-phases:
- **2A:** V0 Audit — Data & Pipeline ✅
- **2B:** Lightweight Quality Gate ✅
- **2C:** Factor Library Skeleton ✅
- **2D:** External Factor Priors ✅
- **2E:** Batch Factor Evaluation ✅ (11 factors, all DIAGNOSTIC_PROBE)
- **2F:** Gate Refinement — DEFERRED

**Status:** COMPLETE

---

### Phase 3: Long-window Baseline

Extend data from ~180d to ~2yr. Rerun evaluation. Compare signal stability. Confirm that probe weakness is not a short-window artifact.

**Key result:** IC signs flip between 180d and 2yr for 5/11 factors. No stable signal.

**Status:** COMPLETE

---

### Phase 4: Factor Factory & Evaluation Platform v1

Build a lightweight factor factory: ops → specs → registry → registry-driven compute.

**Deliverables:**
- `factor_ops.py` — 12 pure-function building blocks ✅
- `factor_specs.py` — FactorSpec dataclass ✅
- `factor_formula_registry.py` — 11 factors registered ✅
- Registry-driven `build_factor_values.py` ✅
- 187 unit tests passing ✅

**Status:** CURRENT (implementation complete, pending closeout)

---

### Phase 5: Alphalens-compatible Export

Compatibility layer — not migration.

**Scope:**
- Export `factor_values` + prices into Alphalens-compatible `factor_data` format
- Run 1–2 sample tear sheets for comparison
- Verify IC / turnover / quantile metrics align

**Status:** NOT STARTED

---

### Phase 6: Dynamic Universe & Survivorship Control

Point-in-time TopN universe with survivorship bias handling.

**Scope:**
- Historical volume-based universe selection
- Delisted tokens included when active
- Rerun selected factor diagnostics

**Status:** NOT STARTED

---

### Phase 7: Large-scale Factor Mining

Systematic factor expansion.

**Sources:** WQ101, GTJA191, Alpha158, technical indicators, crypto-native factors.

**Rule:** All new factors start as `DIAGNOSTIC_PROBE`. No auto-upgrades.

**Status:** NOT STARTED

---

### Phase 8: Candidate Factor Review

Review accumulated DIAGNOSTIC_PROBEs. Promote promising ones to CANDIDATE_REVIEW (requires human review).

**Status:** NOT STARTED

---

### Phase 9: Multi-factor Signal Construction

Combine CANDIDATE_FACTOR signals: equal-weight, IC-weight, simple ML.

**Status:** NOT STARTED

---

### Phase 10: Strategy Backtest with Borrowed Engine

Backtest multi-factor portfolios using VectorBT or similar.

**Status:** NOT STARTED

---

### Phase 11: Cost / Slippage / Capacity / Risk

Slippage, spread, commission, market impact. Drawdown and concentration risk controls.

**Status:** NOT STARTED

---

### Phase 12: Paper Trading

Full strategy in paper trading mode.

**Status:** NOT STARTED

---

### Phase 13: Small-capital Live Validation

Minimal capital real-world deployment.

**Status:** NOT STARTED

---

## Progression Rules

1. **No phase skipping.** Each phase must be completed and reviewed before the next begins.
2. **No unauthorized roadmap changes.** All changes require human review.
3. **No unauthorized factor status upgrades.** Status changes require human review.
4. **No strategy backtest in factor evaluation.** Keep evaluation diagnostic.
5. **No over-interpretation.** A weak probe ≠ a dead factor family.
6. **No default tool migration.** Each integration must be justified.
7. **Human approval required.** Phase transitions require explicit human decision.
8. **Backward compatible.** Later phases must not break earlier conventions.
