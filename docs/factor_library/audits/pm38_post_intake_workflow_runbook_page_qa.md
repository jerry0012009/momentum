# PM-38: Post-Intake Workflow Runbook and Page Completeness QA

**Date:** 2026-06-22
**Verdict:** `POST_INTAKE_WORKFLOW_RUNBOOK_PAGE_QA_PASS`

## 1. Why PM-38 Deferred Factor Interpretation

PM-35→PM-37 achieved 12/12 evidence completion for 5 new factors. Before interpreting results, the team needs:
- A repeatable runbook for future factor intake batches
- Resource-aware strategies to avoid OOM on 15GB servers
- Page completeness verification to ensure all evidence is visible

Factor interpretation (direction semantics, formula review) deferred to PM-39.

## 2. PM-35 → PM-37 Workflow Closure Summary

| PM | Task | Result |
|---|---|---|
| PM-35 | Controlled intake batch01 (5 factors) | 2/12 evidence, factor_values + eval complete |
| PM-36 | Incremental decile-shape + capacity-liquidity | 8/12 evidence, resource audit created |
| PM-37 | Incremental redundancy + rolling stability | 12/12 evidence, all COMPLETE + WORKFLOW_READY |

Key resource optimizations:
- `--factor-ids` / `--only-missing` added to 4 heavy scripts
- Incremental pairwise: 365 pairs (vs 2850 full, 87% reduction)
- Paper portfolio: run to temp dir + merge (avoid overwrite)

## 3. Docs Created

- `docs/factor_library/POST_INTAKE_WORKFLOW_RUNBOOK.md` — 12-section runbook for adding new factors
- `docs/factor_library/RESOURCE_AWARE_REFRESH_GUIDE.md` — resource safety guide for 15GB servers

## 4. Scripts Created

- `scripts/check_factor_evaluation_page_completeness.py` — 16-check QA script

## 5. Page QA Result

**16/16 checks PASS**

| Check | Status |
|---|---|
| HTML exists | PASS |
| HTML size < 4.5MB | PASS |
| All 76 factors in HTML | PASS |
| PM-35 rev_2h in HTML | PASS |
| PM-35 mom_vol_adjusted_20h in HTML | PASS |
| PM-35 range_breakout_vol_confirm_20h in HTML | PASS |
| PM-35 volume_pressure_20h in HTML | PASS |
| PM-35 xs_rank_mom_accel in HTML | PASS |
| Unified Factor Profile section | PASS |
| evidence_status | PASS |
| workflow_ready_status | PASS |
| source_artifacts | PASS |
| Paper Portfolio section | PASS |
| Regime section | PASS |
| Disclaimer text | PASS |
| All sections present | PASS |

## 6. Factor/Page Coverage

- 76 registered factors, all in HTML
- 5 PM-35 factors: COMPLETE + WORKFLOW_READY, all visible in page
- Evidence/profile/page consistent

## 7. Non-Change Statement

- No factor formulas modified
- No factor_values modified
- No signal panel modified
- No live/strategy code modified
- No unrelated reports/site pages modified

## 8. Limitations

1. Runbook assumes 15GB server — larger servers can use full refresh
2. Paper portfolio merge is manual (no automated merge in script)
3. Rolling stability for new factors will be INSUFFICIENT_HISTORY until enough monthly data accumulates

## 9. Recommended Next PM

**PM-39: Post-intake factor interpretation and direction-semantics review**
