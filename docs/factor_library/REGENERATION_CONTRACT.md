# Factor Library Regeneration Contract — PM-20

**Generated:** 2026-06-22
**Status:** Research diagnostics. NOT production. NOT live trading.

---

## 0. Purpose

This document defines the canonical regeneration pipeline for the factor library.
It answers:

1. After a new factor is registered, which scripts must run?
2. Which outputs are regenerated at each step?
3. Which steps are expensive and should be optional?
4. How does a new factor reach the public factor-evaluation page?
5. Which entry docs must be updated so future AI agents do not use stale information?

This contract makes the pipeline reproducible and extensible without creating new parallel scripts or pages.

---

## 1. Canonical Pipeline

The full pipeline runs in this dependency order:

```
factor registry (scripts/factor_formula_registry.py)
  → registry integrity check (scripts/check_factor_registry_integrity.py)
  → build factor catalog (scripts/build_factor_catalog.py)
  → catalog integrity check (scripts/check_factor_catalog_integrity.py)
  → build factor values (scripts/build_factor_values.py)
  → direction semantics audit (scripts/audit_factor_direction_semantics.py)
  → factor-level evaluation (scripts/evaluate_factors.py)           [EXPENSIVE]
  → diagnostics metrics (scripts/build_factor_diagnostics_metrics.py)
  → bilingual factor cards (scripts/build_factor_bilingual_cards.py)
  → quality scorecard (scripts/build_factor_quality_scorecard.py)
  → pairwise redundancy matrix (scripts/build_factor_pairwise_redundancy_matrix.py) [EXPENSIVE]
  → refreshed scorecard (scripts/build_factor_quality_scorecard.py)
  → factor-evaluation page (scripts/_build_factor_eval_html.py)
  → factor_library_state (scripts/build_factor_library_state.py)
```

The orchestration script is:

```bash
python scripts/run_factor_library_refresh.py --stage <stage|preset> [--dry-run] [--expensive-ok]
```

---

## 2. Standard Commands

### 2.1 Full refresh (all stages)

```bash
# Dry run first — see what would execute
python scripts/run_factor_library_refresh.py --stage all --dry-run

# Actual run (requires --expensive-ok for evaluate + redundancy)
python scripts/run_factor_library_refresh.py --stage all --expensive-ok
```

### 2.2 Cheap refresh only (skip evaluate + redundancy)

```bash
python scripts/run_factor_library_refresh.py --stage cheap
```

### 2.3 Rebuild public page only

```bash
python scripts/run_factor_library_refresh.py --stage page
```

### 2.4 Rebuild scorecard only

```bash
python scripts/run_factor_library_refresh.py --stage scorecard
```

### 2.5 Rebuild metadata only (bilingual cards)

```bash
python scripts/run_factor_library_refresh.py --stage metadata
```

### 2.6 Rebuild diagnostics only

```bash
python scripts/run_factor_library_refresh.py --stage diagnostics
```

### 2.7 Full redundancy matrix (expensive)

```bash
python scripts/run_factor_library_refresh.py --stage redundancy --expensive-ok
```

### 2.8 Factor-level evaluation (expensive)

```bash
python scripts/run_factor_library_refresh.py --stage evaluate --expensive-ok
```

### 2.9 Individual script commands

```bash
# Registry integrity
python scripts/check_factor_registry_integrity.py

# Catalog
python scripts/build_factor_catalog.py
python scripts/check_factor_catalog_integrity.py

# Factor values (all registered factors)
python scripts/build_factor_values.py

# Factor values (subset)
python scripts/build_factor_values.py --factor-ids mom_20h vol_5h

# Direction audit
python scripts/audit_factor_direction_semantics.py

# Factor evaluation
python scripts/evaluate_factors.py
python scripts/evaluate_factors.py --factor-ids mom_20h vol_5h

# Diagnostics
python scripts/build_factor_diagnostics_metrics.py \
  --input-dir research/factor_runs/crypto_top50_factor_library/factor_level_evaluation \
  --state-path research/factor_runs/crypto_top50_factor_library/factor_library_state.json \
  --output-dir research/factor_runs/crypto_top50_factor_library/factor_diagnostics

# Bilingual cards
python scripts/build_factor_bilingual_cards.py

# Scorecard
python scripts/build_factor_quality_scorecard.py

# Redundancy matrix
python scripts/build_factor_pairwise_redundancy_matrix.py

# Evaluation page
python scripts/_build_factor_eval_html.py

# State
python scripts/build_factor_library_state.py
```

### 2.10 Adding a new factor (intake workflow)

```bash
# Step 1: Add FactorSpec to scripts/factor_formula_registry.py
# Step 2: Run intake
python scripts/run_factor_intake.py --factor-ids <factor_id> --run-id <run_id>
# Step 3: Refresh library
python scripts/run_factor_library_refresh.py --stage cheap
```

---

## 3. Expensive vs Cheap Steps

| Script | Cost | Reason |
|--------|------|--------|
| `check_factor_registry_integrity.py` | **Cheap** | Static analysis, no data loading |
| `build_factor_catalog.py` | **Cheap** | Registry-only, no data loading |
| `check_factor_catalog_integrity.py` | **Cheap** | Cross-check of catalog vs registry |
| `build_factor_values.py` | **Cheap** (if data cached) | Only expensive if raw data needs downloading |
| `audit_factor_direction_semantics.py` | **Cheap** | Static analysis of registry |
| `evaluate_factors.py` | **EXPENSIVE** | Loads all 71 factor_values + labels, computes RankIC across 4 horizons |
| `build_factor_diagnostics_metrics.py` | **Cheap** | Reads pre-computed evaluation CSVs |
| `build_factor_bilingual_cards.py` | **Cheap** | Template-based, no data loading |
| `build_factor_quality_scorecard.py` | **Cheap** | Reads pre-computed diagnostics/metadata CSVs |
| `build_factor_pairwise_redundancy_matrix.py` | **EXPENSIVE** | Loads and correlates all 71 factors pairwise |
| `_build_factor_eval_html.py` | **Cheap** | Reads pre-computed CSVs/JSONs, generates HTML |
| `build_factor_library_state.py` | **Cheap** | Reads pre-computed artifacts, generates state |

---

## 4. Dependency Graph

### 4.1 What each output depends on

```
factor_registry_integrity_report.csv/json
  ← factor_formula_registry.py (static)
  ← raw bars parquet schema (for column availability check)

factor_catalog.csv/json
  ← factor_formula_registry.py

factor_values.parquet (per factor)
  ← factor_formula_registry.py
  ← raw bars parquet

direction_semantics_audit/
  ← factor_formula_registry.py
  ← factor_values (optional, for validation)

factor_level_rankic_summary.csv (+ all eval artifacts)
  ← factor_values.parquet (all factors)
  ← labels.parquet

factor_diagnostics_summary.csv/json
  ← factor_level_evaluation/ (rankic, quantile, coverage, etc.)

factor_monthly_ic_series.csv
  ← factor_level_evaluation/factor_level_period_ic_summary.csv

factor_monthly_long_short_series.csv
  ← factor_level_evaluation/factor_level_period_long_short_summary.csv

factor_cumulative_long_short_curve.csv
  ← factor_monthly_long_short_series.csv

factor_bilingual_cards.csv/json
  ← factor_formula_registry.py (metadata only, no data)

factor_quality_scorecard.csv/json
  ← factor_diagnostics_summary
  ← factor_monthly_ic_series
  ← factor_bilingual_cards
  ← factor_level_metric_panel
  ← factor_level_quantile_return_summary
  ← factor_pairwise_redundancy (if available)

factor_pairwise_redundancy.csv (+ matrices, clusters, summary)
  ← factor_values.parquet (all factors)
  ← factor_bilingual_cards (for family mapping)

factor-evaluation.html
  ← factor_diagnostics_summary
  ← factor_monthly_ic_series
  ← factor_monthly_long_short_series
  ← factor_cumulative_long_short_curve
  ← factor_bilingual_cards
  ← factor_card_qa_report
  ← factor_quality_scorecard
  ← factor_quality_scorecard_manifest
  ← factor_redundancy_summary (if available)
  ← factor_redundancy_clusters (if available)

factor_library_state.json/md
  ← factor_formula_registry.py
  ← factor_values directories
  ← factor_catalog.json
  ← factor_registry_integrity_report.json
  ← factor_level_candidate_review.csv
  ← phase9b_signal_component_manifest.csv
  ← signal_composition_review_manifest.json
```

### 4.2 Shortcut: diagnostics-only refresh

If `factor_values` and `evaluate_factors` outputs already exist:

```bash
# This rebuilds diagnostics → metadata → scorecard → page → state
python scripts/run_factor_library_refresh.py --stage cheap
```

---

## 5. Staleness Rules

| Change | What becomes stale |
|--------|-------------------|
| Registry changes (new factor, formula fix) | factor_values, evaluation, diagnostics, metadata, scorecard, redundancy, page, state |
| factor_values recomputed | evaluation, diagnostics, scorecard, redundancy, page, state |
| Evaluation outputs updated | diagnostics, scorecard, page, state |
| Redundancy matrix updated | scorecard, page, state |
| Metadata/cards updated | scorecard, page, state |
| Scorecard updated | page, state |
| Any output changed | state (always regenerate last) |

**Rule:** Always regenerate `state` last. It reads from all upstream outputs.

---

## 6. AI Guardrails

Future AI agents working on the factor library MUST follow these rules:

1. **Do not create a parallel evaluator.** Use `scripts/evaluate_factors.py`.
2. **Do not create a random new page.** Use `scripts/_build_factor_eval_html.py`.
3. **Do not hand-edit generated CSV/JSON** except documented overrides (e.g., `factor_card_overrides.json`).
4. **Do not use stale docs if `factor_library_state.json` disagrees.** The state JSON is the single source of truth for counts.
5. **Do not touch `src/momentum/strategies/`** for factor library work.
6. **Do not claim production/live/tradeability.** This is research diagnostics only.
7. **Do not modify factor formulas** unless explicitly tasked with formula changes.
8. **Do not modify `factor_values` manually.** Always use `build_factor_values.py`.
9. **Do not skip the dependency order.** The pipeline has strict upstream→downstream dependencies.
10. **Run `--dry-run` first** before any expensive stage.
11. **Use the intake workflow** (`run_factor_intake.py`) for adding new factors. Do not bypass it.

---

## 7. Orchestration Script

The `scripts/run_factor_library_refresh.py` script provides:

- `--stage <name|preset>`: Run a single stage or a named preset
- `--dry-run`: Print commands without executing
- `--expensive-ok`: Required for expensive stages (evaluate, redundancy)
- Stdout logging of every command
- Fail-fast on any non-zero exit code

Available stages: `registry-integrity`, `catalog`, `values`, `direction-audit`, `evaluate`, `diagnostics`, `metadata`, `scorecard`, `redundancy`, `page`, `state`

Available presets: `all`, `cheap`, `page-only`, `scorecard-only`, `metadata-only`, `diagnostics-only`, `redundancy-only`

---

## 8. Entry Docs That Must Be Kept Current

| Doc | What to keep current |
|-----|---------------------|
| `docs/factor_library/START_HERE.md` | Link to this contract; avoid hard-coding volatile counts |
| `docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md` | Link to this contract; pipeline description |
| `docs/factor_library/factor_library_manifest.json` | Machine-readable pipeline state; update stale counts |
| `docs/factor_library/FILE_STATUS_REGISTER.csv` | File-level status |
| `docs/factor_library/REGENERATION_CONTRACT.md` | This file |

**Pattern:** Use `factor_library_state.json` as source of truth. Do not hard-code volatile counts in docs unless clearly marked as generated.

---

## 9. Quick Reference

```
┌─────────────────────────────────────────────────────────────┐
│  Adding a new factor                                        │
│  1. Add FactorSpec to factor_formula_registry.py            │
│  2. python scripts/run_factor_intake.py --factor-ids <id>   │
│  3. python scripts/run_factor_library_refresh.py --stage cheap│
│  4. Review: factor_library_state.md                         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Full regeneration after bulk changes                       │
│  1. python scripts/run_factor_library_refresh.py --dry-run  │
│  2. python scripts/run_factor_library_refresh.py \          │
│       --stage all --expensive-ok                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Rebuild public page only                                   │
│  python scripts/run_factor_library_refresh.py --stage page  │
└─────────────────────────────────────────────────────────────┘
```
