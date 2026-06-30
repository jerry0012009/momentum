# Post-Intake Workflow Runbook

**生成时间:** 2026-06-22  
**最后更新:** 2026-06-22 (PM-38B alignment)  
**状态:** 研究诊断文档。非生产。非实盘。

---

## 1. 新增因子前的 Checklist

Before adding any new factor, verify:

- [ ] Factor formula is well-defined and reversible (direction semantics documented)
- [ ] Input data exists in `data/` for all required symbols and timeframes
- [ ] Factor is not a trivial duplicate of an existing registered factor
- [ ] Factor belongs to a recognized family (momentum, volatility, wq101, tech, etc.)
- [ ] Expected direction is stated (positive/negative/conditional)
- [ ] No signal or live strategy code is touched during this process

---

## 2. 选择 Batch

Select **3–5 factors** per batch.

Selection criteria:
- Prefer factors with available data (status ≠ `MISSING_INPUT_DATA`)
- Mix families (don't add 5 momentum variants at once)
- Include at least one factor that complements existing clusters

---

## 3. 注册 FactorSpec

Add a `FactorSpec(...)` entry to `scripts/factor_formula_registry.py`:

```python
FactorSpec(
    factor_id="new_factor_id",
    family="family_name",
    required_columns=["close", "high", "low", "volume"],  # columns compute_fn reads
    lookback_window=20,         # bars required including current bar
    expected_direction="positive",  # or "negative", "conditional"
    compute_fn=my_compute_fn,   # (DataFrame) -> Series
    status="DIAGNOSTIC_PROBE",  # default, do not change during intake
    notes="Brief English description",  # free-text notes
)
```

**FactorSpec actual fields** (from `scripts/factor_specs.py`):
- `factor_id: str` — unique identifier
- `family: str` — grouping (momentum, volatility, etc.)
- `required_columns: list[str]` — DataFrame columns the compute function reads
- `lookback_window: int` — bars required including current bar
- `expected_direction: str` — "positive", "negative", or "conditional"
- `compute_fn: Callable` — (DataFrame) -> Series
- `status: str` — default "DIAGNOSTIC_PROBE"
- `notes: str` — free-text notes

After registration, verify the entry is parseable:

```bash
python -c "from scripts.factor_formula_registry import REGISTRY; print(len(REGISTRY))"
```

---

## 4. 运行 Intake

```bash
python scripts/run_factor_intake.py \
  --factor-ids new_factor_1 new_factor_2 new_factor_3 \
  --run-id intake_batch_N
```

**CLI args** (from `run_factor_intake.py`):
- `--factor-ids <id ...>` — one or more factor IDs (required, space-separated)
- `--run-id <id>` — unique run identifier (required)
- `--dataset-id <id>` — default `crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1`
- `--skip-build-values` — skip factor_values build (assume they exist)
- `--skip-redundancy` — skip redundancy diagnostics
- `--output-dir <path>` — custom output directory
- `--dry-run` — print commands without executing

This computes `factor_values.parquet` and runs partial evaluation for the new factors.

---

## 5. 检查 factor_values

Verify parquet files exist for each new factor:

```bash
ls data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/<factor_id>/factor_values.parquet
```

Canonical path: `data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/<factor_id>/factor_values.parquet`

If missing, check intake logs for errors in the run directory:
```bash
cat research/factor_runs/crypto_top50_factor_library/factor_intake/<run_id>/manifest.json
```

---

## 6. 运行缺失诊断

Run diagnostics **incrementally** (only for new factors). Do NOT re-run full diagnostics on the 15GB server.

### 6.1 Decile-Shape

```bash
python scripts/build_factor_decile_shape_diagnostics.py \
  --factor-ids new_factor_1 new_factor_2 new_factor_3
```

Supports `--factor-ids` and `--only-missing`.

### 6.2 Capacity-Liquidity

```bash
python scripts/build_factor_capacity_liquidity_diagnostics.py \
  --factor-ids new_factor_1 new_factor_2 new_factor_3
```

Supports `--factor-ids` and `--only-missing`.

### 6.3 Shape Stability (Rolling)

```bash
python scripts/build_factor_shape_stability_diagnostics.py \
  --factor-ids new_factor_1 new_factor_2 new_factor_3
```

Supports `--factor-ids` and `--only-missing`.

### 6.4 Pairwise Redundancy

```bash
python scripts/build_factor_pairwise_redundancy_matrix.py \
  --factor-ids new_factor_1 new_factor_2 new_factor_3
```

With `--factor-ids`, computes only pairs involving new factors: O(k × n) instead of O(n²).

### 6.5 Cluster Diagnostics

```bash
python scripts/build_factor_redundancy_cluster_diagnostics.py
```

Note: cluster diagnostics requires the full pairwise matrix. Run after 6.4.

### 6.6 Paper Portfolio

```bash
python scripts/build_single_factor_paper_portfolio_diagnostics.py \
  --factor-ids new_factor_1 new_factor_2 new_factor_3
```

**⚠️ Paper portfolio merge — safe rule:**

1. Run to a temp directory to avoid overwriting existing results:
   ```bash
   python scripts/build_single_factor_paper_portfolio_diagnostics.py \
     --factor-ids new_factors --output-dir /tmp/paper_new
   ```
2. Merge new rows into existing summary CSV
3. Validate count (no existing rows dropped)

Running directly on the default output directory can overwrite the full paper summary with a partial run.

---

## 7. Evidence Progression

Evidence completeness progresses through stages. The actual workflow after intake is:

| Step | Action | Evidence achieved |
|------|--------|-------------------|
| 1 | intake (`run_factor_intake.py`) | factor_values.parquet + partial eval (RankIC, period IC, quantile returns, long-short) |
| 2 | decile-shape + capacity-liquidity (`--factor-ids`) | decile diagnostics + capacity diagnostics |
| 3 | redundancy + cluster + marginal | pairwise redundancy matrix + cluster assignments |
| 4 | shape-stability / rolling (`--factor-ids`) | rolling stability diagnostics |
| 5 | paper portfolio (temp + merge) | paper returns + fee sensitivity |
| 6 | profile + staleness | unified profile + staleness check |
| 7 | page rebuild + page QA | factor-evaluation.html + completeness report |

Check current status:

```bash
grep "evidence_completeness_rate" research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_unified_profile_summary.csv
```

---

## 8. Profile + Staleness + Page 刷新

After all diagnostics pass:

```bash
# Rebuild unified profile
python scripts/build_unified_factor_profile.py

# Check staleness
python scripts/check_factor_library_staleness.py

# Rebuild page
python scripts/_build_factor_eval_html.py

# QA check
python scripts/check_factor_evaluation_page_completeness.py
```

---

## 9. 判断 workflow_ready_status

A factor is `WORKFLOW_READY` when:

1. `evidence_completeness_rate == 1.0` (12/12)
2. All source artifacts exist and are fresh (not stale)
3. No `evidence_incomplete` or `fee_sensitivity` blocks remain

Otherwise status is `WORKFLOW_INCOMPLETE` with specific block reasons listed.

---

## 10. 出错恢复

**Partial failure during intake:**

```bash
# Re-run only failed factors
python scripts/run_factor_intake.py --factor-ids failed_factor --run-id intake_retry
```

**Corrupted diagnostics output:**

```bash
# Restore from git
git restore research/factor_runs/crypto_top50_factor_library/factor_diagnostics/specific_file.csv

# Re-run that diagnostic stage only
python scripts/build_factor_decile_shape_diagnostics.py --factor-ids affected_factor
```

**Full rollback:**

```bash
git stash   # or git restore research/
```

---

## 11. Expensive Stages

These scripts load large data or do O(n²) computations:

| Script | Why expensive | Supports `--factor-ids` | Notes |
|--------|--------------|------------------------|-------|
| `build_single_factor_paper_portfolio_diagnostics.py` | Simulates returns across all symbols | ✅ | Use `--factor-ids` for small batches |
| `build_factor_pairwise_redundancy_matrix.py` | O(n²) pairwise correlation | ✅ | With `--factor-ids`: O(k×n) |
| `build_factor_shape_stability_diagnostics.py` | Rolling window recomputation | ✅ | Use `--factor-ids` for small batches |

**`--expensive-ok` is a flag for `run_factor_library_refresh.py` only** (the orchestrator), not for individual diagnostic scripts. Individual scripts use `--factor-ids` to limit scope.

On a 15GB server, run expensive stages one at a time with `--factor-ids`. See `RESOURCE_AWARE_REFRESH_GUIDE.md`.

---

## 12. 禁止修改

During intake, **DO NOT** modify:

- ❌ Signal definitions or weights
- ❌ Live/production code
- ❌ Strategy portfolio allocations
- ❌ Factor formulas for existing factors
- ❌ Factor expected directions without audit
- ❌ `src/momentum/strategies/` code
- ❌ Broker, execution, or exchange API code

Only additions to registry and incremental diagnostics are permitted.

## 8. NaN in JSON payload — critical pitfall

**Symptom:** `factor-evaluation.html` fails to load with `Uncaught SyntaxError: Unexpected token 'N' ... is not valid JSON`

**Root cause:** Python's `json.dumps()` outputs `NaN` for `float('nan')` by default. JavaScript's `JSON.parse()` cannot parse `NaN` — it's not valid JSON.

**Where it happens:** Diagnostic scripts that compute rolling statistics, positive month rates, or stability metrics may produce `NaN` when data is insufficient (e.g., empty monthly IC series). If these `NaN` values are not converted to `None`/`null` before JSON serialization, the HTML page breaks silently.

**Prevention:**
1. **Source script guard:** Always use `round(val, N) if not np.isnan(val) else None` when assigning float values from numpy computations.
2. **HTML builder defense:** `_build_factor_eval_html.py` has a `_sanitize_nan()` function that recursively replaces `NaN`/`inf` with `null` in all loaded JSON data. This is the safety net.
3. **Post-build validation:** After regenerating `factor-evaluation.html`, always verify:
   ```bash
   python3 -c "
   import re, json
   from pathlib import Path
   txt = Path('reports/site/factor-library/factor-evaluation.html').read_text()
   nans = len(re.findall(r'\\\\bNaN\\\\b', txt.replace('Number.isNaN', '')))
   print(f'Data NaN count: {nans}')
   m = re.search(r'<script id=\"factorPayload\" type=\"application/json\">(.*?)</script>', txt, re.DOTALL)
   if m:
       data = json.loads(m.group(1))
       print(f'JSON valid. Factors: {len(data.get(\"factors\",[]))}')
   "
   ```
4. **Known vulnerable fields:** `ic_positive_month_rate`, `recent_vs_full_ic_delta`, `recent_vs_full_ls_delta` in `factor_shape_stability_payload.json` — these come from `build_factor_shape_stability_diagnostics.py` and will be `NaN` when a factor has empty monthly IC data but `n_months > 0` from LS data.

**Fix:** Regenerate the page after fixing the source script, then deploy to `/var/www/momentum-report/factor-library/`.

## 9. Data source hierarchy for page builder — critical pattern

**Problem:** The HTML page builder (`_build_factor_eval_html.py`) reads metrics from multiple data sources. When new factors are added via controlled intake, the OLD diagnostics files may not have horizon-level metrics, while the NEW factor-level evaluation files do. If the builder only reads from old sources, new factors show as blank.

**Data source hierarchy (OLD → NEW):**

| Metric | Old source (may be empty for new factors) | New source (always populated) |
|--------|------------------------------------------|-------------------------------|
| rankic_mean, rankic_t_stat | `factor_diagnostics_summary.csv` | `factor_level_rankic_summary.csv` |
| long_short_mean, sharpe | `factor_diagnostics_summary.csv` | `factor_level_long_short_summary.csv` |
| best_horizon | `factor_diagnostics_summary.csv` | `factor_level_coverage_summary.csv` |
| Monthly IC series | `factor_monthly_ic_series.csv` | `factor_level_period_ic_summary.csv` |
| Monthly LS series | `factor_monthly_long_short_series.csv` | `factor_level_period_long_short_summary.csv` |

**Key difference:** Old files use `factor_id` as key; new files use `factor_name` (same values).

**Column mapping (old → new):**
- `rankic_mean` → `direction_adjusted_mean_rank_ic`
- `rankic_t_stat` → `t_stat`
- `coverage_rate` → `1 - missing_rate` (coverage column is raw count, not rate)
- `monthly_ic_positive_rate` → computed from period IC data

**Builder fix pattern:** The builder now loads BOTH old and new sources, builds lookup maps keyed by `(factor_name, horizon)`, and falls back to factor-level data when diagnostics has None/NaN.

**5 factors affected by this issue (PM-35 batch):**
- `rev_2h`, `mom_vol_adjusted_20h`, `range_breakout_vol_confirm_20h`, `volume_pressure_20h`, `xs_rank_mom_accel`

**Prevention:** After any new factor intake batch, verify that the HTML builder can resolve metrics for ALL new factors. Add a check to `check_factor_evaluation_page_completeness.py` that validates: for each factor in the page payload, if `rankic_mean` is None and `ev_has_factor_level_evaluation` is True, flag as incomplete.

## 10. Post-intake payload regeneration checklist (PM-40B 教训)

After adding new factors to the factor library, the following payloads must be regenerated:

| Payload | Script | Manual? |
|---------|--------|---------|
| `factor_level_period_ic_summary.csv` | `evaluate_factors.py` + manual merge from batch CSV | Yes — merge batch → canonical |
| `single_factor_paper_page_payload.json` | `build_single_factor_paper_page_payload.py` | Yes — must run manually |
| `factor_shape_stability_payload.json` | `build_factor_shape_stability_diagnostics.py` | Usually auto |
| `factor_capacity_liquidity_payload.json` | `build_factor_capacity_liquidity_diagnostics.py` | Usually auto |
| `factor_profile_payload.json` | `build_unified_factor_profile.py` | Usually auto |

**Critical:** `rankic_std` and `rankic_ir` are NOT in `factor_diagnostics_summary.csv` or `factor_level_rankic_summary.csv`. They must be computed from period IC data. The HTML builder now computes them from `monthly_ic` if they're None.

**QA command:** `python scripts/check_factor_evaluation_page_completeness.py` (22 checks including per-factor detail completeness)

## 11. LS aggregate metrics — canonical outputs (PM-41, PM-58B)

LS aggregate statistics are now canonical outputs from `evaluate_factors.py`, written to `factor_level_long_short_summary.csv`:

| Field | Source | Annualization |
|-------|--------|---------------|
| `long_short_spread_std` | monthly period LS std(ddof=1) | N/A |
| `long_short_spread_annualized_return` | per-bar LS mean × bars_per_year | per_bar_mean_x_bars_per_year |
| `long_short_spread_annualized_vol` | monthly std × √12 | monthly edge stability |
| `long_short_spread_max_drawdown` | min(cumulative drawdown) | N/A |
| `long_short_spread_positive_period_rate` | count(r>0) / count(r) | N/A |
| `n_monthly_periods` | count of monthly periods | N/A |
| `annualization_method` | "per_bar_mean_x_bars_per_year" | PM-58B canonical |

**bars_per_year mapping (PM-58B):** 1h=8760, 4h=2190, 24h=365, 72h≈122.

**LS Sharpe / Ann Vol** are monthly edge stability metrics (×√12), not portfolio Sharpe/Vol.
**Ann Return** is annualized per-bar LS edge, not portfolio cumulative annual return.
These are research diagnostics, not portfolio metrics or trading signals.

**After new factor intake:** These fields are automatically populated by `evaluate_factors.py`. No separate step needed.

**Page builder fallback:** `_build_factor_eval_html.py` reads these from canonical LS summary when old diagnostics fields are empty.

## 11B. Window Diagnostics (PM-58C)

After new factor intake, run window diagnostics to generate per-horizon window-level LS stats:

```bash
.venv/bin/python scripts/build_ls_window_diagnostics.py \
  --period-path research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_period_long_short_summary.csv \
  --output-dir research/factor_runs/crypto_top50_factor_library/factor_diagnostics
```

This produces:
- `factor_ls_window_diagnostics.csv` — per-factor per-horizon window stats
- `factor_ls_window_diagnostics.json` — metadata and overlap warnings

**Fields:** n_windows, window_ls_mean, window_ls_std, window_ls_win_rate, window_ls_ann_edge, window_ls_ann_vol, window_ls_sharpe, bars_per_year, overlap_warning, nonoverlap_available, nonoverlap_window_ls_win_rate.

**Overlap warnings:** 1h=LOW_OVERLAP, 4h=MODERATE_OVERLAP, 24h=HIGH_OVERLAP, 72h=VERY_HIGH_OVERLAP.

**Metric semantics (PM-58C):**
- **Edge Diagnostics** = monthly per-bar LS edge stability (LS Edge Mean, Monthly Edge Std, Monthly Edge Sharpe, Annualized LS Edge, Monthly Edge Vol, Edge Curve Max DD, Monthly Edge Win Rate)
- **Window Diagnostics** = per-evaluation-window LS stats (Window LS Mean, Window LS Win Rate, Window LS Sharpe, etc.)
- Neither is a portfolio metric or trading signal.
- Window LS Win Rate for 24h/72h is NOT an independent trade win rate due to heavy overlap.

**After new factor intake:** Run this script after `evaluate_factors.py` populates `factor_level_period_long_short_summary.csv`.

**QA command:** `python scripts/check_factor_evaluation_page_completeness.py` (PM-58C checks verify edge semantics)

## 11C. Overlapping Sleeve Strategy Diagnostics (PM-59A)

After new factor intake, run overlapping sleeve strategy diagnostics:

```bash
python scripts/build_factor_overlapping_sleeve_strategy_diagnostics.py \
  --factor-ids new_factor_1 new_factor_2 \
  --only-missing
```

This produces:
- `factor_overlapping_sleeve_strategy_summary.csv` — per-factor strategy metrics
- `overlapping_sleeve_strategy_returns/<factor_id>__<horizon>.parquet` — hourly return series

**Key:** Do NOT run full refresh. Use `--factor-ids` for small batches.
**Note:** PM-59A is optional-but-standard. Not required for workflow_ready status.
**Conditional direction factors are skipped automatically.

## 12. Market Regime / BTC Diagnostics — workflow reintegration (PM-42)

After new factor intake, ensure `factor_monthly_ic_series.csv` includes new factors, then run:

```bash
python scripts/build_factor_market_regime_diagnostics.py \
  --btc-symbol auto --fee-bps 10 \
  --output-dir research/factor_runs/crypto_top50_factor_library/factor_diagnostics
```

This produces:
- `factor_regime_exposure_summary.csv` — per-factor BTC corr, regime class, bull-bear Δ
- `factor_regime_summary.csv` — per-factor per-regime mean/std/positive_rate
- `factor_regime_diagnostics_payload.json` — page payload

If `factor_monthly_ic_series.csv` is missing new factors, merge from canonical `factor_level_period_ic_summary.csv` before running the regime script.

## 13. Post-Intake Workflow Completion (PM-43A)

After new factor intake, run the full post-intake workflow:

```bash
# Option A: Automated runner
python scripts/run_post_intake_workflow_completion.py --factor-ids rev_2h,mom_vol_adjusted_20h

# Option B: Manual step-by-step (if runner fails)
python scripts/evaluate_factors.py --factor-ids rev_2h
python scripts/build_single_factor_paper_portfolio_diagnostics.py
python scripts/build_factor_pairwise_redundancy_matrix.py --factor-ids rev_2h
python scripts/build_factor_redundancy_cluster_diagnostics.py
python scripts/build_factor_market_regime_diagnostics.py --canonical-ic-path research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_period_ic_summary.csv
python scripts/build_factor_quality_scorecard.py
python scripts/build_unified_factor_profile.py
python scripts/_build_factor_eval_html.py
```

### Integrity Check

After completion, verify with:

```bash
python scripts/check_post_intake_workflow_integrity.py --factor-ids rev_2h
```

All 11 checks must pass before entering factor interpretation.

### Scorecard Canonical Fallback (PM-43A)

`build_factor_quality_scorecard.py` now automatically falls back to canonical factor-level evaluation data when `factor_diagnostics_summary.csv` has NaN. No manual merge needed.

### Regime IC Merge (PM-43A)

`build_factor_market_regime_diagnostics.py --canonical-ic-path <path>` automatically merges missing factors from canonical period IC. Use this when running regime diagnostics after new factor intake.

## 14. Active Factor Universe Consistency Gate (PM-53B)

**硬规则：每次新增因子或 partial workflow 后，必须执行以下三步一致性检查。**

### 14.1 Active Factor Workflow Consistency Checker

```bash
python scripts/check_active_factor_workflow_consistency.py
```

检查所有 active factor 是否完整存在于全部 13 个 required outputs (rankic, long_short, diagnostics_summary, shape, rolling_stability, decile, capacity, scorecard, redundancy_summary, regime_exposure, profile, bilingual_cards, html_payload)。

- 输出：active factor count, per-table count, missing/extra factor IDs, PASS/FAIL verdict
- exit code 非 0 = FAIL（有 required table 缺 active factor）

### 14.2 Page QA (含 PM-53B active universe check)

```bash
python scripts/check_factor_evaluation_page_completeness.py
```

新增检查：
1. page visible factor count == active factor count
2. every visible factor has required diagnostics presence (shape/decile/capacity/scorecard/profile)
3. 任何 visible factor 缺少 required downstream diagnostics → page QA FAIL

### 14.3 Integrity QA (active-universe mode)

```bash
python scripts/check_post_intake_workflow_integrity.py --all-active
```

新增 active-universe consistency table：
- 如果 active universe 是 N，则所有 required outputs 必须是 N
- 单因子 19/19 pass 不足以证明全库完整
- integrity report 中必须显示 active count consistency table

### 14.4 `--only-missing` 增强

`run_post_intake_workflow_completion.py --only-missing` 已增强，现在检查每个 active factor 是否完整存在于全部 required outputs（不仅是 pairwise redundancy）。缺失任一 required output 的 factor 会被纳入 missing list。

### 14.5 Robust Diagnostics Integration (PM-56A)

**Hard rule:** After any new factor intake or partial workflow, the following robust diagnostics must be generated and validated before factor review or page interpretation:

```bash
# Generate robust diagnostics
python scripts/compute_rankic_robust_significance.py
python scripts/compute_return_robust_significance.py

# Validate
python scripts/check_active_factor_workflow_consistency.py
python scripts/check_post_intake_workflow_integrity.py --all-active
python scripts/check_factor_evaluation_page_completeness.py
```

**Full-universe required outputs:**
- `factor_rankic_robust_significance_summary.csv` — 84 factors × 4 horizons = 336 rows
- `factor_ls_robust_significance_summary.csv` — 84 factors × 4 horizons = 336 rows

**Documented subset outputs (informational, not full-universe required):**
- `factor_paper_robust_significance_summary.csv` — 5 factors × 1 horizon (documented subset)
- `factor_fee_robust_significance_summary.csv` — 13 factors (documented subset)

**Workflow stage names:**
- `rankic-robust-significance` — runs `compute_rankic_robust_significance.py`
- `return-robust-significance` — runs `compute_return_robust_significance.py`

**`--only-missing` behavior:**
`run_post_intake_workflow_completion.py --only-missing` now detects missing robust RankIC and robust LS outputs. A factor missing from either robust output is flagged.

**Important:**
- Robust outputs are research diagnostics, not trading signals.
- Robust outputs do NOT alter scorecard or best_horizon unless a future PM explicitly changes that.
- Paper/fee subsets are documented limitations, not failures.

### 14.6 Core vs Optional Workflow Boundary (PM-58)

**Core full-universe diagnostics** are mandatory for every active factor. Missing any core diagnostic = workflow FAIL.

**Optional deep-dive diagnostics** (paper simulation, fee sensitivity, paper robust, fee cost-collapse) are candidate-only. Their absence is NOT a failure. Their presence is labeled "Optional evidence only" on the page.

**Hard rules:**
- Paper/fee absence must NOT be labeled "Missing" — use "Not run — optional"
- Paper/fee presence must NOT be treated as core requirement
- Paper/fee do NOT affect scorecard or best_horizon
- Robust RankIC and LS are core, not optional
- Cap is a conditional core input source, not a downstream diagnostic

**Page behavior:**
- Paper/fee sections are collapsed under "Optional Deep-dive Evidence" (default collapsed)
- Summary table columns for paper/fee are labeled "opt"
- How to Read section clarifies optional vs core reading path

See `FACTOR_EVALUATION_WORKFLOW_BOUNDARY.md` for full specification.

### 14.7 LS Monthly Aggregate Fields (PM-58A)

LS monthly aggregate fields are **core LS summary fields**. Missing fields block reading.

Required fields per active factor × 4 horizons:
- `long_short_spread_std`, `long_short_spread_annualized_return`, `long_short_spread_annualized_vol`
- `long_short_spread_max_drawdown`, `long_short_spread_positive_period_rate`, `n_monthly_periods`

**Normal path:** `evaluate_factors.py` PM-41 logic computes these during intake.
**Historical repair:** `backfill_ls_monthly_aggregate_fields.py` reads from `factor_monthly_long_short_series.csv`.
**QA gate:** `check_active_factor_workflow_consistency.py` + `check_post_intake_workflow_integrity.py --all-active`.

### 14.8 Funding / Cost / Tail Review Fields

`evaluate_factors.py` now treats funding-aware diagnostics as part of the factor evaluation workflow. The default run tries to locate the aligned funding cache for the selected dataset and adds after-funding labels without replacing the canonical price-only labels.

Required behavior:
- price-only RankIC / spread remains available for ranking-information analysis.
- after-funding RankIC / spread is written when funding coverage is complete for the forward window.
- funding coverage is explicit; missing funding windows stay null and are not filled with zero.
- funding intervals are read from `funding_interval_hours`; 1h, 4h, 8h, and mixed intervals are converted to hourly cost before forward-window summing.
- bucket tail diagnosis and funding-adjusted edge flip flags flow into `factor_level_candidate_review.csv`, `factor_quality_scorecard.csv`, page JSON, and the factor evaluation page.

Core commands:

```bash
python scripts/evaluate_factors.py
python scripts/build_factor_quality_scorecard.py
python scripts/_build_factor_eval_html.py
python scripts/check_factor_evaluation_page_completeness.py
```

Useful research planning command:

```bash
python scripts/build_factor_workflow_research_plan.py
```

This writes:
- `factor_workflow_universe_contrast_plan.csv`
- `crypto_native_next_factor_candidates.csv`
- `factor_workflow_research_plan.json`

These artifacts are research planning outputs. They do not create production signals and do not make trading claims.
