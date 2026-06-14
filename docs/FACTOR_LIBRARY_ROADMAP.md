# Factor Library Roadmap

> Last updated: 2026-06-14 (Phase 7G complete)

---

## Current Status

**Phase 7G COMPLETE** — 27-factor curated library (v0.2) established.

| Metric | Value |
|--------|-------|
| Total factors | 27 |
| Families | 11 |
| Diagnostic tiers | T1: 7, T2: 12, T3: 3, T4: 5 |
| Redundancy groups | 6 |
| Core diagnostic candidates | 6 |
| Tests | 115 total |

---

## Completed Phases

| Phase | Status | Key Output |
|-------|--------|------------|
| 7A | DONE | 86 candidate factors mined |
| 7B | DONE | 27 selected_for_7B |
| 7C-A | DONE | Dynamic factor_values built |
| 7C-B | DONE | Dynamic evaluation + summary |
| 7D-A | DONE | Static adapter + comparison plan |
| 7D-B | DONE | Static evaluation + static-vs-dynamic comparison |
| 7E | DONE | Diagnostic tier classification (T1/T2/T3/T4) |
| 7F | DONE | Pairwise redundancy + 6 groups identified |
| 7G | DONE | Curated library v0.2 + documentation consolidation |

---

## Next: Phase 7H — Batch-2 Factor Mining Preparation

Allowed pending PM review.

### Planned scope
- Mine new candidates from additional data sources or formula variants
- Apply lessons from Phase 7B-7G (redundancy-aware, turnover-aware, direction-aware)
- Target: expand library beyond 27 factors while maintaining quality gates

### Key constraints to carry forward
- Calendar-time join only
- Universe = dynamic_from_current_listed_pool
- No shift(-h), no row-based forward return
- expected_direction from theory only, never reverse-engineered
- All new factors: `IMPLEMENTED_PENDING_EVAL` or diagnostic status only
- No alpha promotion until PM explicit approval

---

## Factor Quality Summary (Phase 7G)

### CORE_DIAGNOSTIC_CANDIDATE (6 factors)
These are stable, clean, non-redundant factors suitable as baseline diagnostics:
- range_24h, range_72h, range_pos_24h (range_position family)
- cross_sectional_normalized (cross_sectional_normalized family)
- xs_rank_vol (cross_sectional_normalized family)
- price_pos_24h (price_position family)

### REVIEW_DIRECTION_OR_FORMULA (16 factors)
Direction mismatch between static and dynamic evaluation — formula or direction needs review before further use.

### MONITOR_TURNOVER_RISK (2 factors)
High/extreme turnover — may have high transaction costs in live trading.

### WEAK_DIAGNOSTIC_ONLY (1 factor)
Weak RankIC signal — use only as secondary diagnostic, not primary.

### REDUNDANCY_REVIEW (2 factors)
Member of a redundancy group, not the representative — review for potential consolidation.
