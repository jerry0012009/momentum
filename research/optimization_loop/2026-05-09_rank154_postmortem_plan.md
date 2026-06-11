# Rank154 Postmortem Implementation Plan

> **For Hermes:** Execute directly in the momentum repo; keep outputs reproducible under `reports/artifacts/rank154_postmortem/` and publish a Chinese report under `reports/site/paper/`.

**Goal:** Stop optimizing rank154 as a release candidate and convert it into a rigorous failure/postmortem package.

**Architecture:** Reuse the long-history Binance archive daily panel from `reports/artifacts/rank154_long_history/daily_panel.pkl`. Compute causal forward returns from D close to D+h close, factor IC/ICIR, decile spread, long/short leg returns, age-bucket attribution, and yearly/regime-style summaries. Then render a Chinese report that explains what failed and which research branches, if any, remain worth pursuing.

**Tech Stack:** Python 3 system environment (`/usr/bin/python3`), pandas/numpy/scipy-compatible rank correlations via pandas, existing `momentum.html_render` utilities.

---

## Task 1: Build factor attribution script

**Objective:** Create one reproducible script for IC/IR, decile spreads, leg attribution, and age buckets.

**Files:**
- Create: `scripts/analyze_rank154_postmortem.py`
- Read: `reports/artifacts/rank154_long_history/daily_panel.pkl`
- Write: `reports/artifacts/rank154_postmortem/*.csv|*.json`

**Checks:**
- Uses only same-day factor values and future close-to-close returns.
- Computes `fwd_ret_1d/3d/5d/10d` by symbol shift.
- Computes factor scores exactly from rank154 components: carry, momo, breakout, combined.
- Does not use current 24h ticker universe.

## Task 2: Run attribution and sanity checks

**Objective:** Run the script and verify output consistency.

**Commands:**

```bash
/usr/bin/python3 scripts/analyze_rank154_postmortem.py
```

**Verification:**
- `factor_ic_summary.csv` exists and contains all factors/horizons.
- `yearly_factor_ic.csv` includes 2021-2026.
- `decile_spread_summary.csv` has top/bottom spread by factor/horizon/year.
- `age_bucket_summary.csv` splits age buckets.
- No empty or all-zero outputs.

## Task 3: Render postmortem report

**Objective:** Create a Chinese HTML report summarizing why rank154 failed as release candidate.

**Files:**
- Create: `scripts/build_rank154_postmortem_report.py`
- Write: `reports/site/paper/rank154_postmortem.html`

**Sections:**
1. Executive verdict.
2. Reproducible plan and data口径.
3. IC/IR factor summary.
4. Decile/long-short spread summary.
5. Long vs short leg attribution.
6. Age bucket findings.
7. Failure lessons and archive status.
8. Candidate follow-up branches.

## Task 4: Publish and verify

**Commands:**

```bash
/usr/bin/python3 scripts/build_rank154_postmortem_report.py
OPENCLAW_PUBLISH_SKIP_BUILDS=1 bash scripts/publish_report_site.sh
curl -I https://jp.jerrypsy.top/momentum/paper/rank154_postmortem.html
```

**Expected:** HTTP 200 and report page loads.

## Task 5: Final user summary

**Objective:** Tell Jerry the plan was landed, link the report, and give the main research conclusion.

**Key message:** rank154 is archived as a failed release candidate but remains useful as a factor-discovery lead, especially around new/young coin trend rotation if supported by age-bucket attribution.
