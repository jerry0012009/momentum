# Research Phase Constitution

> This document is the **top-level constraint** for all phases of the momentum project.
> No phase may contradict this document without explicit human approval.

---

## 1. Project Positioning

**Not** a generic quant platform. **Not** a full Qlib. **Not** a full VectorBT. **Not** a single-strategy backtest.

**Is:** A **crypto perpetual cross-sectional factor research system**.

Core building blocks:

1. Crypto perpetual data protocol
2. Universe protocol (static → dynamic)
3. Factor factory (ops → specs → registry → compute)
4. Factor evaluation protocol (IC, RankIC, spread, turnover, coverage)
5. Audit / closeout protocol (PLAN → IMPLEMENTATION → EVALUATION → CLOSEOUT)

## 2. Current Research Judgment

The current 11 simple OHLCV factors showed no stable actionable signal in either 180d or 2yr windows.

This proves **only:**
- These 11 simple probe factors are weak.

This does **not** prove:
- Traditional factors are invalid for crypto.
- WQ101 / GTJA191 / Alpha158 factor families are useless.
- OHLCV-based factors are universally dead.
- Only crypto-native factors (funding, liquidation, on-chain) can work.

The 11 factors' primary role was to **validate the data → factor → label → evaluation pipeline.** They succeeded at that role.

## 3. Build-vs-Borrow Decision

### Self-developed (our protocol, our code)

- Crypto perpetual data ingestion (Binance Futures, bar_close_time timestamp)
- `known_at` protocol (known_at = bar_close_time)
- Calendar-time forward returns (no shift(-k))
- Static / dynamic universe protocol
- Listing-date and missing-bar handling
- Factor catalog and registry
- `factor_values` standard schema
- Diagnostic evaluation kernel
- Audit / closeout documents

### Borrow or stay compatible with

| Tool | Relationship | When |
|------|-------------|------|
| **Alphalens** | Factor tear sheet / IC report compatibility | Phase 5 |
| **Qlib** | Reference architecture; possible future ML workflow | Not current core |
| **VectorBT** | Future strategy backtest engine | Phase 10+ |
| **TA-Lib / pandas-ta / ta** | Optional technical indicator sources | Anytime, as formula input |

### Forbidden

- Do not rebuild a full Qlib.
- Do not rebuild a full VectorBT.
- Do not replace the current pipeline with Alphalens.
- Do not turn the project into a generic quant platform.

## 4. Phase Roadmap

| Phase | Name | Status |
|-------|------|--------|
| 0 | Project Positioning & Data Contract | **COMPLETE** |
| 1 | V0 Engineering Loop | **COMPLETE** |
| 2 | Evaluation Protocol & Factor Library Skeleton | **COMPLETE** |
| 3 | Long-window Baseline | **COMPLETE** |
| 4 | Factor Factory & Evaluation Platform v1 | **CURRENT** |
| 5 | Alphalens-compatible Export / External Tool Compatibility | NOT STARTED |
| 6 | Dynamic Universe & Survivorship Control | NOT STARTED |
| 7 | Large-scale Factor Mining | NOT STARTED |
| 8 | Candidate Factor Review | NOT STARTED |
| 9 | Multi-factor Signal Construction | NOT STARTED |
| 10 | Strategy Backtest with Borrowed Engine | NOT STARTED |
| 11 | Cost / Slippage / Capacity / Risk | NOT STARTED |
| 12 | Paper Trading | NOT STARTED |
| 13 | Small-capital Live Validation | NOT STARTED |

### Phase Gate Rules

- **No skipping phases.** Each phase must be closed before the next starts.
- **No roadmap changes** without human review.
- **No factor status upgrades** without human review.
- **Strategy backtest must not bleed into factor evaluation.**
- **A probe failure is not a family failure.** Weak probes don't invalidate entire factor classes.
- **Tool migration is not the default.** Justify each integration individually.

## 5. Phase 4 — Factor Factory v1 (CURRENT)

**Goal:** Build a lightweight Factor Factory v1.

**Scope:**
- `factor_ops.py` — pure-function building blocks ✅
- `factor_specs.py` — FactorSpec dataclass ✅
- `factor_formula_registry.py` — registry of 11 factors ✅
- Registry-driven `build_factor_values.py` ✅
- Unit tests (124 new) ✅
- Current 11 factors registered ✅

**Not in Phase 4:**
- Large-scale new factor expansion
- Dynamic universe
- Strategy backtest
- Qlib / Alphalens / VectorBT integration

**Completion criteria:**
- 11 factors computable through registry ✅
- Standard `factor_values` schema unchanged ✅
- All tests pass ✅
- No future leak introduced ✅
- Evaluation pipeline backward compatible ✅

## 6. Phase 5 — Alphalens-compatible Export

**Goal:** Compatibility layer, not migration.

**Scope:**
- Export our `factor_values` + prices into Alphalens-compatible `factor_data` format.
- Run 1–2 sample factor tear sheets for visual comparison.
- Check whether our IC / turnover / quantile metrics align with Alphalens output.

**Not in Phase 5:**
- Replacing our evaluation kernel with Alphalens.
- Adopting Alphalens data format as primary.

## 7. Phase 6 — Dynamic Universe

**Goal:** Point-in-time TopN universe with survivorship control.

**Scope:**
- Build point-in-time universe selection (by historical volume, not current).
- Avoid survivorship bias (delisted tokens included when active).
- Rerun selected factor diagnostics on dynamic universe.

**Not in Phase 6:**
- New factor discovery.
- Strategy construction.

## 8. Phase 7 — Large-scale Factor Mining

**Goal:** Expand factor library systematically.

**Sources:**
- WQ101 (WorldQuant 101 Alphas)
- GTJA191 (GuoTaiJunAn 191 Alphas)
- Alpha158 (Qlib Alpha158)
- Technical indicators
- Crypto-native factors (funding rate, liquidation, on-chain)

**Rule:** All new factors initial status = `DIAGNOSTIC_PROBE`.

**Forbidden auto-upgrades:**
- `DIAGNOSTIC_PROBE` → `CANDIDATE_REVIEW` (requires human review)
- `CANDIDATE_REVIEW` → `CANDIDATE_FACTOR` (requires human review)
- Any → `ALPHA` (requires strategy-level validation, not just factor-level)

## 9. Alpha Naming Convention

**Forbidden:** Calling a single unvalidated factor an "alpha."

**Allowed terms:**
- factor
- diagnostic probe
- candidate factor
- signal candidate

**Forbidden terms (for individual factors):**
- strong alpha
- confirmed alpha
- deployable alpha
- live alpha

An "alpha" requires: multi-factor signal → strategy backtest → cost/slippage model → paper trading validation.

## 10. Execution Rules for All Future Phases

1. **No phase skipping.** Complete current phase before starting next.
2. **No unauthorized roadmap changes.** All changes require human review.
3. **No unauthorized factor status upgrades.** Status changes require human review.
4. **No strategy backtest in factor evaluation.** Keep evaluation diagnostic.
5. **No over-interpretation.** A weak probe ≠ a dead factor family.
6. **No default tool migration.** Each integration must be justified.
7. **No silent scope creep.** If a task expands beyond the phase definition, stop and request approval.
