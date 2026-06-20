# Scripts

**Current active focus:** crypto perpetual cross-sectional factor library research.

For adding one or many factors, do not start from scratch and do not create a
parallel evaluator. Use the factor intake workflow:

```bash
python scripts/run_factor_intake.py --factor-ids <factor_id...> --run-id <run_id>
```

Read first:

- `docs/factor_library/START_HERE.md`
- `docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md`
- `research/factor_runs/crypto_top50_factor_library/factor_library_state.md`
- `scripts/factor_formula_registry.py`
- `scripts/factor_specs.py`
- `scripts/factor_ops.py`

Core factor-library scripts:

| Script | Role |
| --- | --- |
| `factor_formula_registry.py` | Canonical factor definitions |
| `factor_specs.py` | `FactorSpec` dataclass |
| `factor_ops.py` | Reusable factor operators |
| `build_factor_values.py` | Builds `factor_values.parquet` from registered specs |
| `evaluate_factors.py` | Factor-level diagnostics |
| `run_factor_intake.py` | Isolated intake runner for new factors |
| `build_factor_redundancy.py` | Current-library redundancy diagnostics |
| `build_factor_conclusion_cards.py` | Per-factor conservative diagnostic cards |
| `generate_intake_report.py` | Human-readable intake report |
| `build_factor_library_state.py` | Generated state JSON/MD |
| `promote_factor_intake.py` | Guard only; no automatic signal promotion |

Do not use these as current factor-intake entry points:

- `evaluate_factors_dynamic_universe.py` — deprecated stale evaluator
- `build_crypto_native_factor_values.py` — old alternative pipeline; review before reuse
- `build_factor_values_batch.py` — older batch helper, not the default intake workflow
- report publishing scripts — adjacent website/report tooling, not factor intake

Rules:

- New factor code usually belongs in `factor_formula_registry.py`.
- Add a small helper to `factor_ops.py` only when existing operators cannot express the formula.
- Do not add intake factors to `build_phase9b_signal_panel.py`.
- Do not modify live trading, execution, broker, strategy-live, or exchange API code.
- Do not make production, tradeability, or alpha claims.
