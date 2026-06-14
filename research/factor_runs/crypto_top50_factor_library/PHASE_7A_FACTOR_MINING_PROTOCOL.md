# Phase 7A — Large-Scale Factor Mining Protocol & Candidate Backlog

> Date: 2026-06-14
>
> Status: COMPLETE — PHASE 7B IMPLEMENTATION ALLOWED

---

## 1. Goal

Establish the factor mining protocol, candidate backlog, batching design, and
anti-snooping engineering constraints before implementing any new factors.

## 2. New Files

| File | Description |
|------|-------------|
| `docs/LARGE_SCALE_FACTOR_MINING_PROTOCOL.md` | Mining protocol, anti-snooping controls |
| `docs/PHASE_7_BATCHING_DESIGN.md` | Batch structure and completion gates |
| `research/.../factor_mining_candidates_v0_1.csv` | 85 candidate factors |

## 3. Candidate Factor Count

**85 candidates** across **15 families**.

## 4. Family Coverage Table

| Family | Total | 7B Selected | 7C | 7D |
|--------|-------|-------------|-----|-----|
| momentum | 5 | 5 | 0 | 0 |
| reversal | 4 | 4 | 0 | 0 |
| volatility | 4 | 4 | 0 | 0 |
| range_position | 5 | 5 | 0 | 0 |
| volume_liquidity | 3 | 3 | 0 | 0 |
| quote_volume_liquidity | 3 | 3 | 0 | 0 |
| trend_ma | 3 | 3 | 0 | 0 |
| breakout | 2 | 2 | 0 | 0 |
| intraday_candle | 3 | 3 | 0 | 0 |
| cross_sectional_normalized | 3 | 3 | 0 | 0 |
| technical_indicators | 7 | 0 | 7 | 0 |
| wq101_expansion | 16 | 0 | 16 | 0 |
| alpha158_expansion | 5 | 0 | 5 | 0 |
| realized_skew_kurtosis | 8 | 0 | 6 | 2 |

## 5. 7B Selected Factor Count

**35 factors** across **10 families**.

## 6. Data-Snooping Controls

- expected_direction set before evaluation (theory_prior or structural_prior)
- No PnL-based selection
- No multiple testing correction (batch discipline instead)
- No factor status upgrade in Phase 7
- No re-evaluation of dropped factors

## 7. expected_direction Policy

| Policy | Count |
|--------|-------|
| theory_prior | 52 |
| structural_prior | 25 |
| conditional_by_design | 8 |

No direction is set from evaluation results.

## 8. Whether Phase 7B Is Allowed

**Yes — Phase 7B implementation is allowed.**
