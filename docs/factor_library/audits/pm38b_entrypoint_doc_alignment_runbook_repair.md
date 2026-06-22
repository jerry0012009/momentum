# PM-38B Audit — Entrypoint Doc Alignment & Runbook Repair

**Generated:** 2026-06-22  
**Verdict:** ENTRYPOINT_DOC_ALIGNMENT_PASS  
**Status:** Research diagnostics. NOT production. NOT live trading.

---

## 1. Why PM-38B Was Required

PM-38 created three new documents:
- `POST_INTAKE_WORKFLOW_RUNBOOK.md`
- `RESOURCE_AWARE_REFRESH_GUIDE.md`
- `check_factor_evaluation_page_completeness.py`

However, PM-38 did NOT update the three existing entrypoint docs:
- `START_HERE.md`
- `FACTOR_LIBRARY_CONTROL_CENTER.md`
- `REGENERATION_CONTRACT.md`

PM-38B aligns all entrypoint docs to reference the new runbook and resource guide, and repairs factual errors in the runbook itself.

---

## 2. Files Changed

| File | Change type |
|------|-------------|
| `docs/factor_library/START_HERE.md` | Added "Resource-Aware Post-Intake Workflow" section |
| `docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md` | Added runbook/guide to Extension Points and Audit First Steps |
| `docs/factor_library/REGENERATION_CONTRACT.md` | Added Section 10: Post-Intake Completion Path (Resource-Aware) |
| `docs/factor_library/POST_INTAKE_WORKFLOW_RUNBOOK.md` | Full rewrite — fixed FactorSpec fields, paths, CLI args, evidence progression |
| `docs/factor_library/RESOURCE_AWARE_REFRESH_GUIDE.md` | Full rewrite — added heavy stage table, recommended commands, recovery |
| `docs/factor_library/prompts/PM38_POST_INTAKE_FACTOR_INTERPRETATION_DIRECTION_REVIEW_PROMPT_20260622.md` | Added SUPERSEDED/DEFERRED header |
| `scripts/check_factor_evaluation_page_completeness.py` | Added 3 new doc-alignment checks |

---

## 3. Entrypoint Doc Updates Confirmed

### START_HERE.md
- ✅ New section "Resource-Aware Post-Intake Workflow / 资源感知的入库后工作流" added before "Current Numbers"
- ✅ References `POST_INTAKE_WORKFLOW_RUNBOOK.md`
- ✅ References `RESOURCE_AWARE_REFRESH_GUIDE.md`
- ✅ References `check_factor_evaluation_page_completeness.py`
- ✅ States: "Future factor intake should prefer incremental/missing-only diagnostics over blind full refresh"

### FACTOR_LIBRARY_CONTROL_CENTER.md
- ✅ Extension Points: added "Post-intake completion (small batches)" entry
- ✅ Extension Points: added "Signal/live/strategy code: OUT OF SCOPE" entry
- ✅ Audit First Steps: added steps 9-12 referencing runbook, resource guide, QA script
- ✅ States: `run_factor_intake.py` remains intake entrypoint
- ✅ States: `run_factor_library_refresh.py` remains canonical full refresh runner
- ✅ States: signal/live/strategy code remains out of scope

### REGENERATION_CONTRACT.md
- ✅ New Section 10: Post-Intake Completion Path (Resource-Aware)
- ✅ 10.1: Why not full refresh after small intake
- ✅ 10.2: Recommended incremental completion path
- ✅ 10.3: Evidence closure table (12/12 items with sources)
- ✅ 10.4: Heavy stages and subset flags table
- ✅ 10.5: Page completeness QA reference
- ✅ 10.6: Resource-aware reference docs

---

## 4. Runbook Corrections Made

`POST_INTAKE_WORKFLOW_RUNBOOK.md` was fully rewritten. Corrections:

1. **FactorSpec example** — Fixed from non-existent `formula=` and `description=` fields to actual dataclass fields: `factor_id`, `family`, `required_columns`, `lookback_window`, `expected_direction`, `compute_fn`, `status`, `notes`
2. **Registry validation command** — Fixed from `FACTOR_SPECS` to `REGISTRY` (actual export name)
3. **factor_values path** — Fixed from `research/factor_runs/.../factor_values/` to canonical `data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/<factor_id>/factor_values.parquet`
4. **CLI args** — Aligned with actual `run_factor_intake.py` args: `--factor-ids` is space-separated (nargs="+"), not comma-separated
5. **Paper portfolio merge warning** — Added explicit safe rule: run to temp, merge, validate count
6. **Expensive stages** — Clarified which scripts support `--factor-ids` / `--only-missing`; clarified `--expensive-ok` is for refresh runner only
7. **Evidence progression** — Matched actual workflow: intake → factor_values → eval → partial diagnostics → decile+capacity → redundancy+cluster+marginal+rolling → profile+staleness+page QA
8. **Forbidden modifications** — Added explicit prohibition on `src/momentum/strategies/`, broker, execution, exchange API code

---

## 5. Resource Guide Corrections Made

`RESOURCE_AWARE_REFRESH_GUIDE.md` was fully rewritten. Additions:

1. **Heavy stage table with actual times** — All 12 expensive/cheap stages with approximate times and RAM peaks
2. **Recommended commands for small batches** — Complete 7-step command sequence for 3–5 factor batches
3. **When to use `--factor-ids`** — Clear guidance with list of supporting scripts
4. **When to use `--only-missing`** — Clear guidance with list of supporting scripts
5. **When full refresh is acceptable** — Specific conditions (RAM > 32GB, bulk changes, CI/CD)
6. **How to avoid OOM on 15GB/no-swap** — 6 concrete rules
7. **How to avoid unrelated reports/site diffs** — Lists of files to touch and not touch
8. **Paper portfolio temp+merge** — Step-by-step with shell commands
9. **Recovery from partial failure** — Three scenarios with recovery commands
10. **Batch size recommendations** — Kept from original

---

## 6. Prompt File Hygiene Result

- ✅ `docs/factor_library/prompts/PM38_POST_INTAKE_FACTOR_INTERPRETATION_DIRECTION_REVIEW_PROMPT_20260622.md` exists
- ✅ Header added: "SUPERSEDED / DEFERRED: This prompt was not executed as PM-38. Use after PM-38B as PM-39 if factor interpretation remains the next task."

---

## 7. QA Script Update Result

- ✅ `scripts/check_factor_evaluation_page_completeness.py` updated
- ✅ New function `check_entrypoint_doc_alignment()` added with 3 checks:
  - `doc_align_start_here`: START_HERE.md contains "POST_INTAKE_WORKFLOW_RUNBOOK.md"
  - `doc_align_control_center`: FACTOR_LIBRARY_CONTROL_CENTER.md contains "POST_INTAKE_WORKFLOW_RUNBOOK.md"
  - `doc_align_regen_contract`: REGENERATION_CONTRACT.md contains both "POST_INTAKE_WORKFLOW_RUNBOOK.md" and "RESOURCE_AWARE_REFRESH_GUIDE.md"
- ✅ Function called in `main()` as step 5 after section markers
- ✅ Python syntax check passes (`py_compile`)
- ✅ Lint passes (no new errors)

---

## 8. No Factor/Signal/Output Changes Confirmation

- ✅ No factor formulas changed
- ✅ No factor_values files modified
- ✅ No signal definitions changed
- ✅ No evaluation outputs modified
- ✅ No diagnostic CSVs/JSONs modified
- ✅ No HTML pages modified
- ✅ No code in `src/momentum/` modified
- ✅ Only docs and QA script changed

---

## 9. Limitations

- The heavy stage time estimates in RESOURCE_AWARE_REFRESH_GUIDE.md are approximate and based on typical 15GB server performance; actual times vary with data size and system load
- The `--only-missing` flag support was not individually verified for each script (inferred from PM-36/PM-37 descriptions)
- The paper portfolio temp+merge procedure is manual; no automated merge script exists yet

---

## 10. Recommended Next PM

**PM-39:** Post-Intake Factor Interpretation and Direction-Semantics Review (use the deferred PM-38 prompt: `docs/factor_library/prompts/PM38_POST_INTAKE_FACTOR_INTERPRETATION_DIRECTION_REVIEW_PROMPT_20260622.md`)
