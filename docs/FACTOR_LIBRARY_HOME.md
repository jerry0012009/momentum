# Factor Library Home

**Project:** Momentum — Crypto Cross-Sectional Factor Library
**Current Phase:** 12D-A (Repository Map & File Ownership Audit)
**Last Updated:** 2026-06-17

---

## What Is This?

This is the **crypto cross-sectional momentum factor library** — a systematic research pipeline that discovers, evaluates, and curates trading factors for crypto perpetual futures (USDT-margined, Binance).

The library follows a strict phase-gated workflow: each phase produces auditable artifacts, gets PM review, and only advances on PASS.

---

## Quick Navigation

| Document | Purpose |
|----------|---------|
| [FACTOR_LIBRARY_ROADMAP.md](FACTOR_LIBRARY_ROADMAP.md) | Phase 0–10 roadmap (authoritative) |
| [FACTOR_REGISTRY.md](FACTOR_REGISTRY.md) | Factor definitions and status |
| [FACTOR_LIBRARY_SKELETON.md](FACTOR_LIBRARY_SKELETON.md) | Factor schema, interface, protocol |
| [FACTOR_LIBRARY_DESIGN.md](FACTOR_LIBRARY_DESIGN.md) | Design rationale, universe, labels |
| [FACTOR_EVALUATION_STANDARD.md](FACTOR_EVALUATION_STANDARD.md) | Evaluation criteria |
| [DOCS_INDEX.md](DOCS_INDEX.md) | Full documentation index |

---

## Factor Library Transparency (Phase 12C)

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
- **`research/factor_runs/crypto_top50_factor_library/`** — Primary audit dossier (273 files)
- **`docs/factor_library_transparency/`** — Human-readable transparency docs
- **`scripts/`** — Reproducible generation logic (601 scripts)
- **`src/momentum/`** — Core Python package
- **`tests/`** — Test suite protecting logic and assumptions
- **`reports/site/factor-library/`** — Generated showcase website

---

## Current Status

- **Candidate:** Frozen (core_only 1h no_guard)
- **30-day rolling:** low-cost net +0.295, mid-cost net +0.209
- **PM decision required:** Phase 12C transparency closeout or Phase 13 paper execution
- **Phase 13:** NOT STARTED

---

## Showcase Website

The factor library showcase is served at `/momentum/factor-library/` and lives in `reports/site/factor-library/`.

**Important:** The showcase website is **generated output** — do not edit it directly. All content should be derivable from the research dossier and transparency docs.
