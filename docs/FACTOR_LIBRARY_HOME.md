# Factor Library Home

**Project:** Momentum — Factor Library Research Framework
**Current Run ID:** `crypto_top50_usdt_perp_1h`
**Current Phase:** 12D-A-R (Repository Map Repair)
**Last Updated:** 2026-06-17

---

## What Is This?

This project has two distinct layers:

1. **Factor Library Framework** — a reusable, general-purpose factor research pipeline for systematic discovery, evaluation, and curation of trading factors. It can be applied to different universes, asset classes, and timeframes.

2. **Current Research Run (`crypto_top50_usdt_perp_1h`)** — the first complete execution of that framework, targeting the Binance USDT-margined perpetual futures top-50 universe at 1-hour frequency. **This run is a complete sample and audit archive of the framework, not the framework itself.**

The research run lives in `research/factor_runs/crypto_top50_factor_library/` (273 files). It is the primary audit dossier for this specific run. Future runs on different universes will produce their own audit dossiers.

The framework follows a strict phase-gated workflow: each phase produces auditable artifacts, gets PM review, and only advances on PASS.

---

## Quick Navigation

| Document | Purpose | Status |
|----------|---------|--------|
| [FACTOR_LIBRARY_HOME.md](FACTOR_LIBRARY_HOME.md) | **This file** — primary navigation hub | CURRENT |
| [PROJECT_TREE_UPDATED.md](PROJECT_TREE_UPDATED.md) | Current repository structure | CURRENT |
| [FACTOR_REGISTRY.md](FACTOR_REGISTRY.md) | Factor definitions and status | CURRENT |
| [FACTOR_LIBRARY_SKELETON.md](FACTOR_LIBRARY_SKELETON.md) | Factor schema, interface, protocol | CURRENT |
| [FACTOR_LIBRARY_DESIGN.md](FACTOR_LIBRARY_DESIGN.md) | Design rationale, universe, labels | CURRENT |
| [FACTOR_EVALUATION_STANDARD.md](FACTOR_EVALUATION_STANDARD.md) | Evaluation criteria | CURRENT |
| [FACTOR_LIBRARY_ROADMAP.md](FACTOR_LIBRARY_ROADMAP.md) | Early-to-mid phase roadmap | REFERENCE |
| [DOCS_INDEX.md](DOCS_INDEX.md) | Full documentation index | CURRENT |

> **Note on FACTOR_LIBRARY_ROADMAP.md:** This document covers Phases 0–10 and is a historical roadmap reference. For current Phase 12+ status, use FACTOR_LIBRARY_HOME.md, PROJECT_TREE_UPDATED.md, and the latest Phase closeout documents.

---

## Factor Library Transparency (Phase 12C)

Phase 12C (Grand Transparency Closeout) is **COMPLETE**.

The [factor_library_transparency/](factor_library_transparency/) folder contains the Phase 12C transparency documentation:

| File | Purpose |
|------|---------|
| [README.md](factor_library_transparency/README.md) | Overview and navigation |
| [factor_handbook.md](factor_library_transparency/factor_handbook.md) | Factor definitions and families |
| [signal_construction_handbook.md](factor_library_transparency/signal_construction_handbook.md) | How signals are built from factors |
| [evaluation_methodology.md](factor_library_transparency/evaluation_methodology.md) | How factors are evaluated |
| [data_lineage.md](factor_library_transparency/data_lineage.md) | Where data comes from and how it flows |
| [workflow_map.md](factor_library_transparency/workflow_map.md) | End-to-end workflow |
| [phase_decision_log.md](factor_library_transparency/phase_decision_log.md) | PM decisions across phases |
| [pm_decision_memo_phase13_readiness.md](factor_library_transparency/pm_decision_memo_phase13_readiness.md) | Phase 13 readiness assessment |
| [risk_register.csv](factor_library_transparency/risk_register.csv) | Known risks and mitigations |

---

## Repository Structure

See [PROJECT_TREE_UPDATED.md](PROJECT_TREE_UPDATED.md) for the full repository tree.

Key folders:
- **`research/factor_runs/crypto_top50_factor_library/`** — Audit dossier for the `crypto_top50_usdt_perp_1h` research run (273 files). This is **one run's archive**, not the entire factor library.
- **`docs/factor_library_transparency/`** — Human-readable transparency docs for the current run
- **`scripts/`** — Reproducible generation logic (601 scripts)
- **`src/momentum/`** — Core Python package (the framework itself)
- **`tests/`** — Test suite protecting logic and assumptions
- **`reports/site/factor-library/`** — Generated showcase website (do not edit directly)

---

## Document Status Labels

Documents in this project carry one of the following status labels:

| Label | Meaning |
|-------|---------|
| **CURRENT** | Primary reading; up-to-date for Phase 12+ |
| **REFERENCE** | Useful background but not the primary entry point |
| **GENERATED** | Produced by scripts; do not hand-edit |
| **SUPERSEDED** | Replaced by a newer document |
| **LEGACY** | Historical; preserved for audit trail |
| **DO_NOT_EDIT** | Managed by pipeline; manual edits will be overwritten |

This phase defines the label taxonomy. Per-document tagging will follow in a later phase if needed.

---

## Current Status

**Research Run:** `crypto_top50_usdt_perp_1h`

- **Candidate:** Frozen (core_only 1h no_guard)
- **30-day rolling:** low-cost net +0.295, mid-cost net +0.209
- **Phase 12C:** COMPLETE (Grand Transparency Closeout)
- **Phase 13:** NOT STARTED

**Important disclaimers:**
- **No real execution.** No exchange connection, no order placement.
- **No alpha claim.** Research metrics are in-sample/backtest results.
- **No production claim.** This is a research pipeline, not a live trading system.
- **Next steps:** Transparency portal, repository structure, workflow map, documentation governance, and Phase 13A decision preparation.

---

## Source-of-Truth Rules

1. `research/factor_runs/crypto_top50_factor_library/` = audit dossier for the **current `crypto_top50_usdt_perp_1h` research run**
2. `docs/factor_library_transparency/` = human-readable transparency documentation
3. `reports/site/factor-library/` = generated website output; **not the sole source of truth**; do not edit directly
4. `scripts/` = reproducible generation logic
5. `src/momentum/` = reusable package code
6. `data/` = generated/cached data; do not hand-edit
7. `tests/` = protect logic and assumptions

---

## Showcase Website

The factor library showcase is served at `/momentum/factor-library/` and lives in `reports/site/factor-library/`.

**Important:** The showcase website is **generated output** — do not edit it directly. All content should be derivable from the research dossier and transparency docs.
