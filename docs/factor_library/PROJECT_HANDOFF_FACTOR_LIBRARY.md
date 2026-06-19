# Project Handoff — Momentum Factor Library Research System

Generated: 2026-06-20

This document is intended to be pasted into a new conversation so work can continue with context. It records the user's goals, working style, current repository state, recent phase history, and near-term plan.

---

## 1. User's Core Goal

The user is building a crypto perpetual cross-sectional factor research system.

The goal is not to rush into live trading. The immediate objective is to find, evaluate, organize, and govern more factors and more diagnostic signals.

The system should become:

- a reliable factor library;
- a maintainable research pipeline;
- a transparent factor/signal diagnostic system;
- a foundation that may later support more production-oriented work, but only after enough factor and signal research has been done.

Do not treat this as a live trading system yet. Do not connect exchange APIs, do not place orders, and do not make production or alpha claims. However, Phase 13 is not permanently forbidden. The correct interpretation is: do not rush into Phase 13 / live trading / production-readiness now. Continue factor and signal research first.

---

## 2. Important Working Style

The user wants a strict PM-style workflow:

1. Review the current commit and code before giving the next task.
2. Search historical work before proposing new analyses.
3. Avoid repeatedly rediscovering work that old phases already did.
4. Prefer code, manifests, CSV/JSON outputs, and tests over long narrative documents.
5. Keep public-facing pages clean and readable.
6. Avoid making the repository a document dump.
7. Give explicit PASS / PARTIAL PASS / FAIL judgments when reviewing commits.
8. If writing a prompt for a server-side coding agent, make it precise, scoped, and defensive.
9. Do not invent claims that are not supported by code outputs.
10. Do not keep every future task artificially under `Phase 12D`. Future phases may move beyond 12D when the project naturally progresses. The next phase name should reflect the actual stage of work rather than being frozen.

The user's major concern is project drift: code, scripts, outputs, reports, and old phase artifacts can scatter across the repo and mislead future work. Always check the governance files and historical artifacts first.

---

## 3. Repository and Site

Repository:

```text
https://github.com/jerry0012009/momentum
```

Public factor-library site:

```text
https://jp.jerrypsy.top/momentum/factor-library/
```

Expected public site structure should remain simple:

```text
index.html
actual-script-map.html
factor-evaluation.html
signal-evaluation-summary.html
```

Historical pages should remain archived and should not pollute the public navigation.

---

## 4. Current Research Pipeline

The current factor-library pipeline is:

```text
raw bars / cached data
→ dynamic/current universe
→ labels / forward returns
→ factor registry
→ factor values
→ factor-level evaluation
→ factor catalog
→ signal panel
→ signal-level evaluation
→ signal composition review
→ public summary pages
```

Important files:

```text
scripts/factor_specs.py
scripts/factor_formula_registry.py
scripts/factor_ops.py
scripts/build_factor_values.py
scripts/evaluate_factors.py
scripts/check_factor_ic_parity.py
scripts/check_factor_registry_integrity.py
scripts/build_factor_catalog.py
scripts/check_factor_catalog_integrity.py
scripts/audit_factor_direction_semantics.py
scripts/build_phase9b_signal_panel.py
scripts/evaluate_signals.py
```

Important output root:

```text
research/factor_runs/crypto_top50_factor_library/
```

Important feature directory:

```text
data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/
```

---

## 5. Current Factor Library State

Recent state before the next expansion stage:

```text
registered factors: 53
computed factors: roughly 47
missing input / missing FV factors: 6
active signal factors: 10
signal variants: 3
```

The 6 missing input factors are:

```text
taker_buy_ratio_20h
taker_buy_zscore_20h
taker_buy_delta_5h
funding_rate_level_20h
funding_rate_zscore_80h
funding_rate_change_24h
```

Reason: current raw bars do not contain:

```text
taker_buy_quote_volume
funding_rate
```

Therefore the next factor expansion should use only currently available OHLCV-style columns:

```text
open
high
low
close
volume
quote_volume
```

Do not add taker/funding/open_interest/liquidation factors until the required data exists.

---

## 6. Active Signal Factors

Current signal panel uses 10 factors:

```text
vol_5h
vol_40h
downside_vol_20h
vol_of_vol_20h
rsi_7h
rsi_28h
xs_rank_vol
range_1h
range_4h
price_pos_24h
```

Current signal construction uses explicit direction transforms:

- negative risk/oscillator factors are multiplied by -1;
- range/position overlay factors are multiplied by -1 under a mean-reversion hypothesis;
- `xs_rank_vol` is a liquidity gate, not direct alpha.

Do not add new factors directly to signal. New factors first enter the library and are evaluated as diagnostic probes.

---

## 7. Recent Completed Phases and Findings

### H8 / H8-R — Factor-level IC restored and parity checked

`evaluate_factors.py` became the canonical factor-level evaluator. It computes RankIC by ranking factor values per timestamp and correlating those ranks with ranked forward returns.

`check_factor_ic_parity.py` was added to verify parity. NaN handling was fixed in H8-R.

### H9 / H9-R — Governance layer

Governance files were added under:

```text
docs/factor_library/
```

Key purpose: make scripts, outputs, deprecated files, and out-of-scope modules explicit.

### H10 — Signal composition review

Signal review found:

- `core_only` was strongest by RankIC;
- `pm_full_structured` and `family_balanced_diagnostic` degraded relative to core;
- RankIC positive but spread negative was not a simple direction bug;
- old Phase 10A-R showed bucket 0 tail / non-monotonic behavior;
- no signal is production ready;
- no alpha claim should be made.

### Historical Phase 10A-R

Important historical files:

```text
archive/legacy_phase_scripts/phase10/run_phase10a_r_diagnostics.py
tests/unit/test_phase10a_r_direction_quantile_repair.py
research/factor_runs/crypto_top50_factor_library/phase10a_r_direction_consistency_check.csv
research/factor_runs/crypto_top50_factor_library/phase10a_r_quantile_bucket_returns.csv
research/factor_runs/crypto_top50_factor_library/phase10a_r_inverted_signal_diagnostic.csv
research/factor_runs/crypto_top50_factor_library/phase10a_r_rankic_quantile_reconciliation.csv
```

Conclusion: signal-level RankIC/spread inconsistency was caused by non-monotonic tail behavior, especially bucket 0. Do not redo this analysis unless new evidence requires it.

### H11 / H11-R — Linter and catalog

Added:

```text
scripts/check_factor_registry_integrity.py
scripts/build_factor_catalog.py
factor_catalog.csv/json
factor_registry_integrity_report.csv/json
```

H11-R fixed IC column mapping and real raw schema detection. Taker/funding factors were correctly classified as missing input data.

### H12-A — Direction semantics audit with legacy recovery

Recovered Phase 6H and Phase 10A-R findings.

Main distinction:

- Phase 10A-R is signal-level bucket-tail / RankIC-spread analysis.
- H12-A is factor-level direction semantics: formula sign vs expected_direction vs raw/adjusted IC.

H12-A identified possible double inversion risk in reversal factors.

### H12-B — Reversal family direction metadata repair

Commit:

```text
5a91619
```

Fixed reversal family metadata:

```text
reversal_5h
rev_3h
rev_10h
rev_24h
```

These formulas are already sign-inverted:

```text
-(close / close_Xh_ago - 1)
```

Therefore `expected_direction` was changed from `negative` to `positive`.

Confirmed:

- compute functions unchanged;
- raw IC unchanged;
- adjusted IC flipped positive;
- catalog rebuilt;
- direction audit regenerated;
- signal unchanged;
- factor values unchanged;
- labels unchanged.

### H12-C0 — Safe incremental factor evaluation guard

Commit:

```text
09f2f24
```

Added safe output behavior to `evaluate_factors.py`:

```bash
python scripts/evaluate_factors.py
```

Full run writes canonical outputs.

```bash
python scripts/evaluate_factors.py --factor-ids rev_3h
```

Blocked, to prevent overwriting canonical outputs.

```bash
python scripts/evaluate_factors.py --factor-ids rev_3h --output-suffix scratch_rev3h
```

Allowed, writes suffixed scratch outputs.

```bash
python scripts/evaluate_factors.py --factor-ids rev_3h --output-dir /tmp/eval_scratch/
```

Allowed, writes to custom output directory.

### H12-C0-R — Evaluation guard cleanup

Commit:

```text
bad0b2c
```

Fixed:

1. quality check CSV row 2 status column;
2. output log now prints actual `out_dir`, not hardcoded `OUTPUT_DIR`.

This commit is PASS.

---

## 8. Current Evaluator Status

`evaluate_factors.py` is semi-vectorized:

```text
between factors: loops factor by factor
within a factor: pandas groupby rank + NumPy boundary loop
```

It is correct enough for current scale but not fully optimized for hundreds of factors.

Current full run is roughly 15 minutes for the existing factor set. This is acceptable for now.

Do not do a large vectorization rewrite before the first factor expansion sprint. The safety guard is enough for now.

---

## 9. Immediate Next Step

The next step should be a factor expansion sprint. Since the user specifically corrected that future work should not be forever labeled Phase 12D, use a cleaner phase name such as:

```text
Phase 13A — Factor Expansion Sprint 1
```

Important: this Phase 13A is not production/live trading. It is a research expansion phase focused on finding more factors and later more signals. Explicitly state:

```text
Phase 13A is research-only factor expansion, not live trading, not production, not exchange-connected.
```

The task should add 10–15 OHLCV-computable factors, evaluate them, build factor values, update catalog, run direction audit, and produce a short sprint summary.

Do not modify signal yet.

---

## 10. Next Prompt Skeleton

Use this as the next coding-agent prompt after reviewing `bad0b2c`:

```text
Please execute Phase 13A — Factor Expansion Sprint 1.

This is a research-only factor expansion phase. It is not production, not live trading, not exchange-connected, and not a signal deployment phase.

Goal:
Add 10–15 new OHLCV-computable factors to the factor library.

Allowed raw columns:
open, high, low, close, volume, quote_volume

Forbidden for this phase:
taker_buy_quote_volume, funding_rate, open_interest, long_short_ratio, liquidations

Do not modify signal construction.
Do not add new factors to signal.
Do not modify labels.
Do not modify raw bars.
Do not make alpha or production claims.

Before adding factors, read:
scripts/factor_formula_registry.py
scripts/factor_specs.py
scripts/factor_ops.py
scripts/build_factor_values.py
scripts/evaluate_factors.py
scripts/check_factor_registry_integrity.py
scripts/build_factor_catalog.py
scripts/check_factor_catalog_integrity.py
scripts/audit_factor_direction_semantics.py
factor_catalog.csv/json
factor_level_rankic_summary.csv
direction_semantics_audit outputs
docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md
docs/factor_library/factor_library_manifest.json

Requirements:
- Avoid duplicate factor IDs.
- Use snake_case factor IDs.
- Use DIAGNOSTIC_PROBE status.
- expected_direction must follow economic/formula semantics, not post-hoc IC fitting.
- If direction is unclear, use conditional.
- If a formula is sign-inverted, expected_direction must reflect the meaning of higher factor_value to avoid double inversion.

Run:
python scripts/check_factor_registry_integrity.py
python scripts/build_factor_values.py
python scripts/evaluate_factors.py --factor-ids <new_factor_ids> --output-suffix phase13a_new_factors
python scripts/evaluate_factors.py
python scripts/check_factor_ic_parity.py
python scripts/build_factor_catalog.py
python scripts/check_factor_catalog_integrity.py
python scripts/audit_factor_direction_semantics.py

Create:
research/factor_runs/crypto_top50_factor_library/factor_expansion_sprint_1/new_factor_inventory.csv
research/factor_runs/crypto_top50_factor_library/factor_expansion_sprint_1/new_factor_evaluation_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_expansion_sprint_1/new_factor_quality_checks.csv
research/factor_runs/crypto_top50_factor_library/factor_expansion_sprint_1/FACTOR_EXPANSION_SPRINT_1_SUMMARY.md

The summary must be short, no more than 150 lines.

Quality checks must confirm:
- no duplicate factor IDs
- all new factors use only allowed columns
- no taker/funding/open_interest dependency
- factor_values built
- partial scratch evaluation completed and did not overwrite canonical outputs
- full canonical evaluation completed
- factor IC parity PASS
- catalog integrity PASS
- direction audit regenerated
- no signal modified
- no labels modified
- no Phase 13 production/live trading work
- no alpha claim
- no production claim

Commit message:
Phase 13A: factor expansion sprint 1
```

---

## 11. Critical Correction for Future Conversations

Do not say “never Phase 13.” Correct wording:

```text
We are not ready for live trading / production Phase 13 yet. The near-term goal is to find more factors and more diagnostic signals first. Phase 13-style production or live work may come later, but not now.
```

Also do not keep every future task as `Phase 12D`. Phase naming should evolve as the project evolves.

Suggested near-term naming:

```text
Phase 13A — Factor Expansion Sprint 1
Phase 13B — Factor Expansion Sprint 2 or Factor Candidate Review
Phase 13C — Signal Candidate Construction / Diagnostic Signal Expansion
Phase 13D — Signal Robustness / Cost-Aware Diagnostic Review
```

Again: these Phase 13A/B/C names are research phases, not live trading.

---

## 12. Summary for New Assistant

The latest reviewed and accepted commit is:

```text
bad0b2c — Phase 12D-H12-C0-R: clean evaluation guard reporting
```

Current recommended next step:

```text
Phase 13A — Factor Expansion Sprint 1
```

This next step should focus on adding 10–15 OHLCV-computable diagnostic factors, not changing signal, not entering live trading, and not making alpha claims.
