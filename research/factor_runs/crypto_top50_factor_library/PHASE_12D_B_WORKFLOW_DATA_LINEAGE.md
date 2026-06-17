# Phase 12D-B: Workflow Map & Data Lineage Visualization

**Phase:** 12D-B
**Date:** 2026-06-17
**Status:** COMPLETE
**Predecessor:** Phase 12D-A-R (Repository Map Repair)
**Current Run ID:** `crypto_top50_usdt_perp_1h`

---

## Purpose

On top of Phase 12D-A's repository map and file ownership audit, further visualize the research pipeline's data flow, script flow, and phase flow as readable, maintainable web pages. This phase only does transparency and visualization — no research results are changed.

---

## Deliverables

| # | File | Type | Description |
|---|------|------|-------------|
| 1 | `reports/site/factor-library/workflow-map.html` | New | Phase 2–12D workflow timeline |
| 2 | `reports/site/factor-library/data-lineage.html` | New | End-to-end data flow visualization |
| 3 | `reports/site/factor-library/pipeline-layers.html` | New | 8-layer repository structure explanation |
| 4 | `reports/site/factor-library/assets/workflow_map.json` | New | Structured workflow data |
| 5 | `reports/site/factor-library/assets/data_lineage.json` | New | Structured data lineage data |
| 6 | `docs/factor_library_transparency/workflow_map_v2.md` | New | V2 workflow map (v1 preserved) |
| 7 | `docs/factor_library_transparency/data_lineage_v2.md` | New | V2 data lineage (v1 preserved) |
| 8 | `reports/site/factor-library/index.html` | Modified | Navigation updated with 3 new pages |
| 9 | `PHASE_12D_B_WORKFLOW_DATA_LINEAGE.md` | New | This closeout document |
| 10 | `phase12d_b_quality_checks.csv` | New | Quality checks |
| 11 | `tests/unit/test_phase12d_b_workflow_data_lineage.py` | New | Unit tests |

---

## What Each Page Answers

### workflow-map.html
"整个因子库研究从 Phase 2 到 Phase 12D 是怎么一步步走过来的？"
- 15 phase cards with: name, goal, inputs, outputs, key scripts, key artifacts, PM decision, status
- "你现在在这里" indicator at Phase 12D-B
- Phase 13 marked as NOT STARTED

### data-lineage.html
"数据从哪里来，如何变成因子、信号、评估结果和网页？"
- 12 data nodes from raw klines to website output
- Each node shows: path, source, script, git-tracked, generated, editable, risk, regeneration

### pipeline-layers.html
"docs / scripts / research / data / src / tests / reports 在管道里扮演什么角色？"
- 8 layers: config, code, scripts, data, research, docs, reports, tests
- Each layer shows: what it is, what it isn't, who reads it, what it generates, common misconceptions

---

## Constraints Observed

- ✅ No Phase 13 started
- ✅ No real execution / trading / API logic
- ✅ No research results changed
- ✅ No research files moved
- ✅ `crypto_top50_factor_library` described as current run archive, not the framework
- ✅ `reports/site/factor-library/` described as generated output
- ✅ v1 workflow_map.md and data_lineage.md preserved (not overwritten)

---

## Disclaimers

- **No real execution.** No exchange connection, no order placement.
- **No alpha claim.** Research metrics are in-sample/backtest results.
- **No production claim.** This is a research pipeline, not a live trading system.
- **Phase 13 NOT STARTED.**
