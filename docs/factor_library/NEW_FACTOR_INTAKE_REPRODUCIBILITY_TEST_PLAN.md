# New Factor Intake Reproducibility Test Plan

**Purpose:** Verify that the post-intake workflow can automatically bring a new factor to the same completeness level as `rev_2h`.

**Created:** 2026-06-23 (PM-44)

---

## Approach: Replay PM-35 Factor as Dry Run

We use an existing PM-35 factor (e.g., `rev_2h`) as a **replay case**. The test simulates what would happen if we added a brand new factor by replaying the same workflow steps.

**Why replay instead of synthetic?**
- We already have ground truth (rev_2h's current state) to compare against.
- No risk of polluting the factor library with test data.
- We can verify each step's output matches expectations.

## Test Steps

### Step 1: Registry Entry
```
# Verify factor exists in registry
python -c "import json; s=json.load(open('research/factor_runs/crypto_top50_factor_library/factor_library_state.json')); assert 'rev_2h' in s['registered_factor_ids']"
```
**Expected:** Factor ID in registered_factor_ids.

### Step 2: Factor Values
```
# Verify factor values exist
ls -la research/factor_runs/crypto_top50_factor_library/factor_values/
```
**Expected:** `rev_2h.parquet` exists and is non-empty.

### Step 3: Factor-Level Evaluation (EXPENSIVE)
```
python scripts/evaluate_factors.py --factor-ids rev_2h
```
**Expected output:** `factor_level_rankic_summary.csv` contains rev_2h with rankic_mean populated.

### Step 4: Monthly IC / LS
```
# Verify period IC data
python -c "import pandas as pd; df=pd.read_csv('research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_period_ic_summary.csv'); print(len(df[df['factor_name']=='rev_2h']), 'rows')"
```
**Expected:** ~100 rows (25 months × 4 horizons).

### Step 5: LS Aggregate
```
python -c "import pandas as pd; df=pd.read_csv('research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_long_short_summary.csv'); r=df[df['factor_name']=='rev_2h'].iloc[0]; print('std:', r['long_short_spread_std'])"
```
**Expected:** Non-NaN std, ann_return, ann_vol, max_dd, pos_rate.

### Step 6: Paper Portfolio
```
python scripts/build_single_factor_paper_page_payload.py
python -c "import json; d=json.load(open('research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_page_payload.json')); fids=[f['factor_id'] for f in d['factors']]; assert 'rev_2h' in fids"
```
**Expected:** rev_2h in payload with NAV series.

### Step 7: Fee Sensitivity
```
python -c "import pandas as pd; df=pd.read_csv('research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_fee_sensitivity.csv'); print(len(df[df['factor_id']=='rev_2h']), 'rows')"
```
**Expected:** Multiple fee_bps data points.

### Step 8: Regime / BTC
```
python scripts/build_factor_market_regime_diagnostics.py --canonical-ic-path research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_period_ic_summary.csv
python -c "import pandas as pd; df=pd.read_csv('research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_exposure_summary.csv'); r=df[df['factor_id']=='rev_2h'].iloc[0]; print('regime:', r['regime_dependency_class'])"
```
**Expected:** REGIME_ROBUST (not INSUFFICIENT_REGIME_DATA).

### Step 9: Redundancy / Pairwise / Cluster / Marginal
```
python scripts/build_factor_pairwise_redundancy_matrix.py --factor-ids rev_2h
python scripts/build_factor_redundancy_cluster_diagnostics.py
python -c "import pandas as pd; df=pd.read_csv('research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_pairwise_redundancy.csv'); pairs=df[(df['factor_i']=='rev_2h')|(df['factor_j']=='rev_2h')]; print(len(pairs), 'pairs')"
```
**Expected:** Multiple pairs. nearest_factor not None.

### Step 10: Capacity / Shape / Stability / Decile
```
# These run as part of the full refresh or can be run individually
python -c "import pandas as pd; df=pd.read_csv('research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_capacity_liquidity_summary.csv'); r=df[df['factor_id']=='rev_2h'].iloc[0]; print('capacity_class:', r['capacity_liquidity_class'])"
```
**Expected:** Non-empty capacity class.

### Step 11: Scorecard
```
python scripts/build_factor_quality_scorecard.py
python -c "import pandas as pd; df=pd.read_csv('research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.csv'); r=df[df['factor_id']=='rev_2h'].iloc[0]; print('score:', r['final_quality_score'], 'coverage:', r['coverage_rate'])"
```
**Expected:** Score > 0, coverage > 0 (not stale).

### Step 12: Unified Profile
```
python scripts/build_unified_factor_profile.py
python -c "import pandas as pd; df=pd.read_csv('research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_unified_profile_summary.csv'); r=df[df['factor_id']=='rev_2h'].iloc[0]; print('profile_score:', r['profile_score'])"
```
**Expected:** profile_score populated.

### Step 13: Page Build
```
python scripts/_build_factor_eval_html.py
```
**Expected:** HTML file written, non-empty.

### Step 14: Page QA
```
python scripts/check_factor_evaluation_page_completeness.py
```
**Expected:** 23/23 PASS (or at least no FAIL for rev_2h).

### Step 15: Integrity Checker
```
python scripts/check_post_intake_workflow_integrity.py --factor-ids rev_2h
```
**Expected:** 11/11 PASS.

### Step 16: Public Page Verification
```
curl -sI https://jp.jerrypsy.top/momentum/factor-library/factor-evaluation.html | head -3
```
**Expected:** HTTP 200.

## Automated Runner (All Steps)

```bash
python scripts/run_post_intake_workflow_completion.py --factor-ids rev_2h --skip-expensive
```

This runs steps 5-16 automatically (skipping the expensive evaluation and paper diagnostics).

## Pass Criteria

The dry run PASSES if:
1. All 16 steps complete without error.
2. `check_post_intake_workflow_integrity.py` reports 11/11 PASS.
3. `check_factor_evaluation_page_completeness.py` reports 23/23 PASS.
4. Public page returns HTTP 200.
5. No stale warnings (no_horizon_data, monthly_ls_unavailable) in factor JSON.
6. rev_2h's data matches known ground truth values.

## Known Limitations

- Steps 3, 4, 6 are EXPENSIVE and not run in `--skip-expensive` mode.
- The dry run uses an existing factor, not a truly new one.
- A real new factor would also need `factor_ops.py` to register it and `build_factor_values.py` to compute values.
