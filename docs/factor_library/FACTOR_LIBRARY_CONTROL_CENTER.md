# Factor Library Control Center

**Generated:** 2026-06-20  
**Status:** Factor library research governance. NOT production. NOT live trading.

---

## Current Status

- Registered factors in `scripts/factor_formula_registry.py` — see `factor_library_state.md` (auto-generated)
- Computed factor_values — see `factor_library_state.md` (auto-generated)
- **6** taker/funding factors missing `factor_values` (not yet computed)
- **10** factors used in current signal panel (`signal_v0_core_only`)
- **3** signal variants: `core_only`, `pm_full_structured`, `family_balanced_diagnostic`
- **4** horizons: 1h, 4h, 24h, 72h
- Factor intake workflow is active for adding one or many new factors. Production/live trading is not in scope.

---

## Current Main Pipeline (text version)

```
download_full_binance_1h_universe.py
  → data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet

build_dynamic_universe_monthly_volume.py
  → data/universe/crypto_usdt_perp_monthly_volume_top50_current_listed_v1/universe_snapshots.parquet

build_labels.py
  → data/features/crypto_top50_usdt_perp_monthly_volume_top50_current_listed_1h_v1/labels.parquet

factor_formula_registry.py (see factor_library_state.md)
  ↓
build_factor_values.py
  → data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/⟨factor⟩/factor_values.parquet (see factor_library_state.md)

build_phase9b_signal_panel.py
  → research/factor_runs/crypto_top50_factor_library/phase9b_signal_panel.parquet

evaluate_signals.py (signal-level RankIC/Spread)
  → src/momentum/signal_evaluation/

evaluate_factors.py (factor-level RankIC)
  → research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/

run_factor_intake.py (isolated new-factor workflow)
  → research/factor_runs/crypto_top50_factor_library/factor_intake/<run_id>/

check_factor_ic_parity.py (H8-R parity guard)
  → 10/10 PASS, exact match vs compute_rank_ic API
```

---

## Active Mainline Scripts

| Script | Role |
|--------|------|
| `scripts/download_full_binance_1h_universe.py` | Data download |
| `scripts/build_dynamic_universe_monthly_volume.py` | Universe construction (monthly volume Top50) |
| `scripts/build_labels.py` | Forward-return labels |
| `scripts/factor_formula_registry.py` | Factor spec registry (see factor_library_state.md) |
| `scripts/factor_specs.py` | FactorSpec dataclass |
| `scripts/factor_ops.py` | Factor building-block operators |
| `scripts/build_factor_values.py` | Factor value computation |
| `scripts/build_phase9b_signal_panel.py` | Signal panel construction |
| `scripts/evaluate_signals.py` | Signal-level evaluation |
| `scripts/evaluate_factors.py` | Factor-level IC evaluation |
| `scripts/run_factor_intake.py` | Standard isolated workflow for adding one or many factors |
| `scripts/build_factor_redundancy.py` | Current-library redundancy diagnostics |
| `scripts/build_factor_conclusion_cards.py` | Conservative per-factor conclusion cards |
| `scripts/generate_intake_report.py` | Readable intake report |
| `scripts/build_factor_library_state.py` | Generated state JSON/MD; canonical counts |
| `scripts/promote_factor_intake.py` | Promotion guard only; no automatic signal promotion |
| `scripts/check_factor_ic_parity.py` | Factor IC parity guard |
| `scripts/run_signal_evaluation_parity_harness.py` | Signal evaluation parity |
| `scripts/run_phase11a_cost_slippage_capacity.py` | Cost/slippage diagnostic |
| `scripts/run_phase11b_liquidity_capacity.py` | Liquidity capacity diagnostic |
| `scripts/run_phase12a_paper_signal_harness.py` | Paper signal generation |
| `scripts/run_phase12b_paper_monitoring.py` | Paper signal monitoring |

---

## Active Modules (src/)

| Module | Role |
|--------|------|
| `src/momentum/signal_evaluation/` | Public API: `compute_rank_ic`, `compute_quantile_spread`, `evaluate_signal` |
| `src/momentum/factors/` | Reusable factor modules (chip_dist, confirmed_extrema, endpoint_nw, pytrendline) |
| `src/momentum/signals/` | Reusable signal modules (ema_donchian, multi_tf_momentum, etc.) |
| `src/momentum/strategies/` | **OUT_OF_SCOPE** — Adjacent strategy research (rank154, rank32c). Not part of factor library mainline. Does not participate in factor registry → factor values → factor IC → signal panel chain. |

---

## Current Dataset

| Asset | Path |
|-------|------|
| Raw bars | `data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet` |
| Universe | `data/universe/crypto_usdt_perp_monthly_volume_top50_current_listed_v1/` |
| Labels | `data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/labels.parquet` |
| Factor values | `data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/⟨factor⟩/factor_values.parquet` |
| Signal panel | `research/factor_runs/crypto_top50_factor_library/phase9b_signal_panel.parquet` |

---

## Factor-Level Evaluation Status

- **Evaluator:** `scripts/evaluate_factors.py` (H8, fixed in H8-R)
- **Parity guard:** `scripts/check_factor_ic_parity.py` (H8-R, 10/10 PASS)
- **Root cause fixed:** NaN factor_value rows must be dropped before ranking
- **Outputs:** `research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/`
- **Public page:** `reports/site/factor-library/factor-evaluation.html`

---

## Signal-Level Evaluation Status

- **Evaluator:** `scripts/evaluate_signals.py`
- **API:** `src/momentum/signal_evaluation/` (compute_rank_ic, compute_quantile_spread)
- **Parity harness:** `scripts/run_signal_evaluation_parity_harness.py`
- **Outputs:** `research/factor_runs/crypto_top50_factor_library/signal_evaluation_*.csv`
- **Public page:** `reports/site/factor-library/signal-evaluation-summary.html`

---

## Cost / Paper Diagnostic Status

- **Cost:** `scripts/run_phase11a_cost_slippage_capacity.py` → COST_SENSITIVE
- **Liquidity:** `scripts/run_phase11b_liquidity_capacity.py` → CONTINUE_PAPER_DIAGNOSTIC_ONLY
- **Paper signal:** `scripts/run_phase12a_paper_signal_harness.py`
- **Paper monitoring:** `scripts/run_phase12b_paper_monitoring.py`
- **Status:** Diagnostic only. Not real trading.

---

## Public Site

| Page | Path |
|------|------|
| Index | `reports/site/factor-library/index.html` |
| Code structure | `reports/site/factor-library/actual-script-map.html` |
| Factor evaluation | `reports/site/factor-library/factor-evaluation.html` |
| Signal evaluation | `reports/site/factor-library/signal-evaluation-summary.html` |
| Archive | `reports/site/factor-library/_archive/` (21 pages, not in public nav) |

---

## Extension Points

- **New factor:** Add `FactorSpec` to `scripts/factor_formula_registry.py`, reuse `factor_ops.py` where possible, then run `scripts/run_factor_intake.py --factor-ids <factor_id...> --run-id <run_id>`
- **New factor operator:** Add a small reusable helper to `scripts/factor_ops.py` only when existing operators cannot express the formula
- **New factor diagnostics:** Extend `scripts/evaluate_factors.py`, `scripts/build_factor_redundancy.py`, or `scripts/build_factor_conclusion_cards.py`; keep output schemas explicit and tested
- **New signal:** Modify `scripts/build_phase9b_signal_panel.py`
- **New evaluation metric:** Add to `scripts/evaluate_factors.py` or `scripts/evaluate_signals.py`
- **Public site changes:** Edit files in `reports/site/factor-library/`

## Factor Intake Contract

For adding one or many factors, do not start from scratch. The standard command is:

```bash
python scripts/run_factor_intake.py --factor-ids <factor_id...> --run-id <run_id>
```

The run directory is:

```text
research/factor_runs/crypto_top50_factor_library/factor_intake/<run_id>/
```

Required review artifacts:

- `manifest.json`
- `command_log.json`
- `outputs_index.json`
- `quality_checks.csv`
- `factor_inventory.csv`
- `factor_metric_panel.csv`
- `factor_candidate_review.csv`
- `factor_redundancy.csv`
- `factor_conclusion_cards.csv/json`
- `report.md`

Do not promote intake factors into signals during intake. Do not modify live trading, execution, broker, strategy-live, or exchange API code.

---

## Archive Policy

- Phase 10 scripts: `archive/legacy_phase_scripts/phase10/` (4 files)
- Old site pages: `reports/site/factor-library/_archive/` (21 pages)
- Old factor evaluator: `scripts/evaluate_factors_dynamic_universe.py` → DEPRECATED_STALE / HISTORICAL_REFERENCE (broken, cannot run; kept as evidence of old design; canonical evaluator is `scripts/evaluate_factors.py`)
- Alphalens exports: `research/factor_runs/crypto_top50_factor_library/alphalens_exports/` → HISTORICAL_ARCHIVE
- Strategy research scripts (~440 files): NOT part of factor library mainline

---

## PM / AI Audit First Steps

1. Read this file (`FACTOR_LIBRARY_CONTROL_CENTER.md`)
2. Read `START_HERE.md`
3. Read `factor_library_state.md` for current counts and warnings
4. Read `factor_library_manifest.json` for machine-readable file map
5. Read `FILE_STATUS_REGISTER.csv` for file-level status
6. Read `ORPHAN_WORK_AUDIT.md` for orphan risks
7. For adding factors, use `run_factor_intake.py`; do not create a parallel workflow
8. **Scope note:** This control center covers the factor library research pipeline only, not the full momentum repository.

---

## Key Answers

1. **Active mainline scripts:** 16 (listed above)
2. **Active supporting scripts:** ~10 (parity, HTML builders, audit helpers)
3. **Public pages:** 4 (index, code structure, factor eval, signal eval)
4. **Factor-level outputs:** factor_level_rankic_summary.csv/json, coverage, manifest
5. **Signal-level outputs:** signal_evaluation_*.csv, manifest
6. **Cost/paper outputs:** phase11a/b, phase12a/b outputs (diagnostic only)
7. **Historical archive:** ~440 strategy research scripts, 4 phase10 scripts, 21 archive pages
8. **Deprecated/stale:** evaluate_factors_dynamic_universe.py, old alphalens smoke check
9. **Orphan review required:** 7 files (see ORPHAN_WORK_AUDIT.md)
