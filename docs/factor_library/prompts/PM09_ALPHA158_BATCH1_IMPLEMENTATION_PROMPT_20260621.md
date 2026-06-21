# PM-09 Prompt — Alpha158-Inspired Factor Batch 1 Implementation

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-08:

- `docs/factor_library/audits/pm08_factor_candidate_source_map.md`

PM-08 was documentation / analysis only. It found that the current library has only one explicit Alpha158-family factor (`q158_high_low_range`) plus many OHLCV-derived factors. It recommended a first batch of 6 implementable OHLCV-only factors.

## 0. PM objective

Implement the first small batch of Alpha158-inspired / OHLCV-only factors, then run the standard factor intake workflow.

This is the first real factor expansion after pipeline cleanup. Keep the batch small, auditable, and reversible.

Implement exactly these 6 factors unless a pre-check proves one is already registered:

1. `vwap_dev_20h`
2. `wvma_20h`
3. `vol_ret_corr_20h`
4. `intraday_ret`
5. `klow_close`
6. `ksft_5h`

Do not add extra factors.

Do not implement external research-report factors in this task. Research-report factors require source PDFs/links/exact formulas and a separate PM task.

## 1. Strict prohibitions

Do **not** modify signal panel construction.

Do **not** modify `scripts/build_phase9b_signal_panel.py`.

Do **not** add any of these factors to current signal variants.

Do **not** modify signal weights.

Do **not** rebuild canonical signal panel.

Do **not** rebuild public result pages.

Do **not** make production, live trading, alpha, or tradeability claims.

Do **not** modify live trading, execution, broker, exchange, or `src/momentum/strategies/` code.

Do **not** use unavailable data sources such as funding, taker buy, orderbook, open interest, basis, market cap, or fundamentals.

Do **not** implement vague research-report factors without exact formula source.

## 2. Required pre-checks

Run:

```bash
git status --short
```

Verify the 6 factor IDs are not already registered:

```bash
python - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, str(Path('scripts').resolve()))
from factor_formula_registry import REGISTRY_BY_ID
ids = ['vwap_dev_20h','wvma_20h','vol_ret_corr_20h','intraday_ret','klow_close','ksft_5h']
existing = [x for x in ids if x in REGISTRY_BY_ID]
print('existing:', existing)
raise SystemExit(1 if existing else 0)
PY
```

If any ID already exists, stop and report. Do not silently rename or duplicate.

Inspect current factor coding style in:

- `scripts/factor_formula_registry.py`
- `scripts/factor_ops.py`
- `scripts/factor_specs.py`

Use existing operator helpers when available. Add a small helper to `factor_ops.py` only if required.

## 3. Factor definitions

### 3.1 `vwap_dev_20h`

- Family: `alpha158_ohlcv`
- Conceptual formula: `(close - vwap_20h) / vwap_20h`
- `vwap_20h = rolling_sum(close * volume, 20) / rolling_sum(volume, 20)`
- Required columns: `close`, `volume`
- Expected direction: `conditional`
- Lookback window: `20`
- Notes: price deviation from 20h volume-weighted consensus. Use epsilon/NaN guard for zero volume denominator.

### 3.2 `wvma_20h`

- Family: `alpha158_ohlcv`
- Conceptual formula: `rolling_std(ret_1h * volume, 20) / rolling_mean(volume, 20)`
- `ret_1h = close / delay(close, 1) - 1`
- Required columns: `close`, `volume`
- Expected direction: `negative`
- Lookback window: `21`
- Notes: volume-weighted volatility / volume-volatility interaction. Use denominator guard.

### 3.3 `vol_ret_corr_20h`

- Family: `alpha158_ohlcv`
- Conceptual formula: `rolling_corr(ret_1h, delta(volume, 1), 20)`
- Required columns: `close`, `volume`
- Expected direction: `conditional`
- Lookback window: `21`
- Notes: return-volume-change correlation. Positive may indicate trend confirmation; negative may indicate divergence.

### 3.4 `intraday_ret`

- Family: `alpha158_ohlcv`
- Conceptual formula: `(close - open) / open`
- Required columns: `open`, `close`
- Expected direction: `conditional`
- Lookback window: `1`
- Notes: in this 1h crypto system, this is the open-to-close return of the current 1h bar, not an equity daily intraday factor. Document this clearly in notes.

### 3.5 `klow_close`

- Family: `alpha158_ohlcv`
- Conceptual formula: `(min(open, close) - low) / close`
- Required columns: `open`, `low`, `close`
- Expected direction: `positive`
- Lookback window: `1`
- Notes: lower wick as fraction of close. Different normalization from `candle_wick_lower`.

### 3.6 `ksft_5h`

- Family: `alpha158_ohlcv`
- Conceptual formula: `rolling_skewness(ret_1h, 5)`
- `ret_1h = close / delay(close, 1) - 1`
- Required columns: `close`
- Expected direction: `conditional`
- Lookback window: `6`
- Notes: short-window return skewness. Existing `realized_skew_20h` uses a longer 20h window; this is intended as a short-horizon complement.

If `factor_ops.py` lacks a rolling skew helper, add a minimal reusable helper such as `rolling_skew(series, window)` using pandas rolling skew, matching existing operator style.

## 4. Allowed code changes

Allowed:

- `scripts/factor_formula_registry.py`
- `scripts/factor_ops.py` only if a reusable helper is needed
- generated isolated intake run outputs under:
  - `research/factor_runs/crypto_top50_factor_library/factor_intake/pm09_alpha158_batch1_20260621/`
- generated factor library state files if running state refresh:
  - `research/factor_runs/crypto_top50_factor_library/factor_library_state.json`
  - `research/factor_runs/crypto_top50_factor_library/factor_library_state.md`
- audit note:
  - `docs/factor_library/audits/pm09_alpha158_batch1_implementation.md`

Do not modify unrelated docs or public site pages.

## 5. Validation after implementation

Run:

```bash
python -m py_compile \
  scripts/factor_ops.py \
  scripts/factor_formula_registry.py \
  scripts/build_factor_values.py \
  scripts/evaluate_factors.py \
  scripts/run_factor_intake.py \
  scripts/build_factor_redundancy.py \
  scripts/build_factor_conclusion_cards.py \
  scripts/generate_intake_report.py
```

Run registry integrity check if available:

```bash
python scripts/check_factor_registry_integrity.py
```

If this script does not exist or has a different CLI, inspect and use the correct command. Do not skip integrity validation silently.

## 6. Run standard intake

Use this run ID:

```text
pm09_alpha158_batch1_20260621
```

Run:

```bash
python scripts/run_factor_intake.py \
  --factor-ids vwap_dev_20h wvma_20h vol_ret_corr_20h intraday_ret klow_close ksft_5h \
  --run-id pm09_alpha158_batch1_20260621
```

Do not use `--dry-run`.

Do not use `--skip-build-values`; these are new factors and must build their factor_values.

Expected outputs:

- factor_values for all 6 factors
- isolated intake run directory
- evaluation outputs
- redundancy diagnostics
- conclusion cards
- report

Do not promote any factor.

## 7. Refresh state

After the intake run succeeds, run:

```bash
python scripts/build_factor_library_state.py
```

This should update registered/computed counts. Record before/after counts in the audit note.

Do not rebuild public site pages in this task.

## 8. Required audit note

Create:

```text
docs/factor_library/audits/pm09_alpha158_batch1_implementation.md
```

The audit note must include:

- factors added
- exact formula proxy for each factor
- required columns
- expected direction
- lookback window
- files changed
- validation commands run
- intake command and run ID
- whether factor_values were generated for all 6
- quality check summary
- conclusion card decision buckets
- redundancy summary
- before/after factor library counts
- explicit non-change statement: no signal panel, no signal weights, no public result pages, no production/live/alpha claims

## 9. Stop conditions

Stop and report instead of forcing through if:

- any factor ID already exists
- required columns are missing from current bars
- registry integrity fails and cannot be fixed with a minimal correct change
- build_factor_values fails for formula logic reasons
- intake run fails due to evaluation/schema bug
- redundancy OOM returns despite PM-07 patch

## 10. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
feat: add alpha158-inspired factor batch 1
```

Final response should include:

- commit hash
- factors added
- intake status
- factor_values generated yes/no
- conclusion card buckets
- redundancy summary
- before/after registered and computed counts
- files changed
- remaining warnings or blockers
