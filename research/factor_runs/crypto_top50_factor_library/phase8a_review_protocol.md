# Phase 8A Review Protocol

> Date: 2026-06-15
> Scope: Human review packet for v0.4 diagnostic factor library (42 factors, 15 families)
> Phase 8A does NOT promote any factor. This protocol defines review steps only.

---

## 1. Purpose

Phase 8A prepares a structured human review packet for all 42 v0.4 factors.
The human reviewer evaluates each factor and records a decision in the decision template.
Phase 8A itself does **not** promote, demote, or remove any factor.

---

## 2. Review Dimensions

For each factor, the human reviewer should evaluate:

### 2.1 Formula Correctness
- Is the factor formula mathematically sound?
- Does it use only current and past data (no future leakage)?
- Is the lookback window appropriate?

### 2.2 Expected Direction
- Does the catalog `expected_direction` match theoretical expectation?
- For conditional factors: is the ambiguity justified?
- Flag any direction mismatch for further investigation.

### 2.3 Static/Dynamic RankIC Stability
- Compare static and dynamic RankIC values.
- Check if the sign is consistent across universes.
- Large sign flips between static and dynamic indicate instability.

### 2.4 Redundancy Context
- Review `redundancy_status` and `max_static_corr` / `max_dynamic_corr`.
- For REDUNDANT_GROUP_MEMBER: is this the best representative?
- For INDEPENDENT: confirmed non-redundant.

### 2.5 Turnover / Coverage
- High turnover factors may be impractical at scale.
- Low coverage factors may have survivorship or data issues.

### 2.6 Multi-label Behavior
- Check RankIC across ret_fwd_1h, 4h, 24h, 72h.
- Consistent direction across horizons is stronger evidence.
- Inconsistent direction may indicate transient effects.

---

## 3. Review Workflow

1. Load `phase8a_human_review_packet.csv` for full 42-factor overview.
2. Load `phase8a_ready_for_human_review_shortlist.csv` for the 10 cleanest candidates.
3. For each factor, evaluate the dimensions above.
4. Record decisions in `phase8a_review_decision_template.csv`.
5. Allowed decision values: `PENDING_HUMAN_REVIEW`, `CANDIDATE_REVIEW`, `PARK`, `DROP`.

---

## 4. Important Constraints

- Phase 8A does **not** promote any factor.
- Phase 8A does **not** set any factor status to CANDIDATE_REVIEW.
- Phase 8A does **not** run backtests.
- Phase 8A does **not** make alpha claims.
- Phase 8A does **not** remove factors.
- All factors remain DIAGNOSTIC_PROBE after Phase 8A.
- v0.4 remains a diagnostic factor library.

---

## 5. Decision Recording

Use `phase8a_review_decision_template.csv` to record decisions:

| Column | Description |
|--------|-------------|
| `factor_id` | Factor identifier (pre-filled) |
| `proposed_human_decision` | Your decision: CANDIDATE_REVIEW / PARK / DROP |
| `reviewer_notes` | Free-text rationale |
| `decision_date` | YYYY-MM-DD |
| `reviewer` | Your name/handle |

**Do not** use ALPHA, TRADEABLE, LIVE, or DEPLOY as decision values.

---

## 6. Next Steps After Review

After human review is complete:
- Factors with `CANDIDATE_REVIEW` decision enter Phase 8B.
- Factors with `PARK` decision are held for future consideration.
- Factors with `DROP` decision are documented but not removed from the library.
- PM approval is required to proceed to Phase 8B.
