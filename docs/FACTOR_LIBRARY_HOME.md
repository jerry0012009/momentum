# Factor Library Home

**Status:** SUPERSEDED. Kept as a redirect for old links.

Use the current factor-library portal instead:

- `docs/factor_library/START_HERE.md`
- `docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md`
- `research/factor_runs/crypto_top50_factor_library/factor_library_state.md`
- `reports/site/factor-library/index.html`

Current rule for adding one or many factors:

1. Add or adjust `FactorSpec` entries in `scripts/factor_formula_registry.py`.
2. Reuse `scripts/factor_ops.py` where possible.
3. Run the intake workflow:

```bash
python scripts/run_factor_intake.py --factor-ids <factor_id...> --run-id <run_id>
```

Do not use this historical page as planning authority. Do not create a
parallel factor pipeline, standalone evaluator, or new report format.
