# PM-40 Prompt — Factor Page Per-Factor Detail Completeness QA (`rev_2h` Priority)

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository and, if available, on the public deployment server.

This task follows PM-39:

- public URL now returns HTTP 200;
- JSON parsing error caused by NaN payloads was fixed;
- page-level QA passes for overall sections and 76 factors;
- however Jerry reports that `rev_2h` content appears partially missing on the public page.

Before factor interpretation, we must verify that each factor's detail panel is complete, especially the five PM-35 factors.

## 0. PM objective

Add and run per-factor detail completeness QA for the factor-evaluation page.

This PM should answer:

1. Does `rev_2h` exist in every required data source behind the page?
2. Does `rev_2h` have 12/12 evidence in the embedded / consumed payloads?
3. Does `rev_2h` have all expected detail sections available to render?
4. Is the observed missing content a data issue, HTML embedding issue, JS rendering issue, or UI interaction issue?
5. Do all five PM-35 factors pass the same per-factor page completeness checks?
6. Can the public page be verified after repair?

This is a page QA / UI data integrity task. It is not factor interpretation.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify expected_direction.

Do **not** modify factor_values.

Do **not** modify signal panel construction.

Do **not** enter factor interpretation or direction semantics review.

Do **not** run full factor refresh.

Do **not** touch live trading / strategy / broker / execution code.

Do **not** change diagnostics values unless a serialization / page-embedding bug requires regeneration.

## 2. Target factors

Primary target:

```text
rev_2h
```

Also verify all PM-35 factors:

```text
rev_2h
mom_vol_adjusted_20h
range_breakout_vol_confirm_20h
volume_pressure_20h
xs_rank_mom_accel
```

## 3. Required files to inspect first

Read:

```text
docs/factor_library/audits/pm35_controlled_factor_intake_batch01.md
docs/factor_library/audits/pm36_resource_audit_incremental_diagnostics.md
docs/factor_library/audits/pm37_incremental_redundancy_stability_completion.md
docs/factor_library/audits/pm39_public_factor_page_deployment_availability.md
scripts/_build_factor_eval_html.py
scripts/check_factor_evaluation_page_completeness.py
reports/site/factor-library/factor-evaluation.html
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_evidence_matrix.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_unified_profile_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_profile_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_diagnostics_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_fee_sensitivity.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_exposure_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quantile_shape_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_rolling_stability_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_decile_shape_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_capacity_liquidity_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_redundancy_cluster_members.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_marginal_information_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_metadata/factor_bilingual_cards.json
```

## 4. Required diagnosis

For `rev_2h`, check whether it exists in each source:

```text
bilingual_card
quality_scorecard
diagnostics_summary
evidence_matrix
unified_profile_summary
profile_payload
paper_summary
fee_sensitivity
regime_exposure
quantile_shape
rolling_stability
decile_shape
capacity_liquidity
redundancy_summary
cluster_membership
marginal_information
html_embedded_data
public_html_render
```

If any required source is missing, determine whether it is:

```text
SOURCE_DATA_MISSING
PAYLOAD_BUILD_MISSING
HTML_EMBED_MISSING
JS_RENDER_MISSING
UI_INTERACTION_MISSING
PUBLIC_DEPLOY_STALE
```

## 5. Required script

Create or update:

```text
scripts/check_factor_page_detail_completeness.py
```

This script should perform per-factor completeness checks.

Inputs:

```bash
--factor-ids rev_2h,mom_vol_adjusted_20h,range_breakout_vol_confirm_20h,volume_pressure_20h,xs_rank_mom_accel
```

If no factor_ids are supplied, default to all factors from `factor_unified_profile_summary.csv`.

Outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_page_detail_completeness_report.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_page_detail_completeness_report.json
```

Required columns:

```text
factor_id
has_bilingual_card
has_quality_scorecard
has_diagnostics_summary
has_evidence_matrix
has_unified_profile
has_profile_payload
has_paper_summary
has_fee_sensitivity
has_regime_exposure
has_quantile_shape
has_rolling_stability
has_decile_shape
has_capacity_liquidity
has_redundancy_summary
has_cluster_membership
has_marginal_information
has_html_token
has_public_url_token
detail_completeness_rate
detail_status
missing_blocks
suspected_failure_layer
notes_zh
notes_en
```

Allowed `detail_status`:

```text
DETAIL_COMPLETE
DETAIL_COMPLETE_WITH_WARNINGS
DETAIL_INCOMPLETE
DETAIL_BLOCKED
```

Allowed `suspected_failure_layer`:

```text
NONE
SOURCE_DATA_MISSING
PAYLOAD_BUILD_MISSING
HTML_EMBED_MISSING
JS_RENDER_MISSING
UI_INTERACTION_MISSING
PUBLIC_DEPLOY_STALE
UNKNOWN
```

## 6. Public page check

If server/public access is available, verify public page contains target factors and key tokens.

Use:

```bash
curl -L https://jp.jerrypsy.top/momentum/factor-library/factor-evaluation.html -o /tmp/factor-evaluation-public.html
python - <<'PY'
from pathlib import Path
html = Path('/tmp/factor-evaluation-public.html').read_text(encoding='utf-8', errors='ignore')
for token in ['rev_2h', 'Unified Factor Profile', 'evidence_status', 'Paper Portfolio', 'Decile', 'Capacity', 'Redundancy', 'Marginal']:
    print(token, token in html)
print('size', len(html.encode('utf-8')))
PY
```

If the public HTML is stale compared to repository HTML, redeploy only `factor-evaluation.html`.

## 7. Optional UI-rendering check

If a headless browser is available, run a browser-level check:

- open public page;
- search/select `rev_2h`;
- confirm detail panel contains expected section headings;
- check console errors.

If browser automation is unavailable, document limitation and rely on source/payload/HTML token checks.

## 8. Repairs allowed

Allowed repairs:

- fix `_build_factor_eval_html.py` if it fails to embed or render sections for some factors;
- sanitize null/NaN fields if they break JS rendering;
- rebuild `factor-evaluation.html`;
- redeploy `factor-evaluation.html`;
- improve QA script.

Not allowed:

- changing factor formula;
- changing factor values;
- changing diagnostics results;
- changing signal code.

## 9. Required audit

Create:

```text
docs/factor_library/audits/pm40_factor_page_detail_completeness_rev2h.md
```

Audit must include:

1. Summary verdict:
   - `FACTOR_PAGE_DETAIL_COMPLETENESS_PASS`
   - `FACTOR_PAGE_DETAIL_COMPLETENESS_PASS_WITH_LIMITATIONS`
   - `FACTOR_PAGE_DETAIL_COMPLETENESS_BLOCKED`
2. Why PM-40 was required after PM-39.
3. `rev_2h` diagnosis.
4. PM-35 five-factor detail completeness table.
5. Whether missing content was source data / payload / HTML / JS / UI / public-deploy issue.
6. Files changed.
7. Local HTML result.
8. Public HTML result.
9. Browser console result if available.
10. Repairs applied.
11. Confirmation no factor formulas / factor_values / signal code changed.
12. Limitations.
13. Recommended next PM: PM-41 post-intake factor interpretation and direction-semantics review.

## 10. Validation

Run:

```bash
python -m py_compile scripts/check_factor_page_detail_completeness.py
python scripts/check_factor_page_detail_completeness.py --factor-ids rev_2h,mom_vol_adjusted_20h,range_breakout_vol_confirm_20h,volume_pressure_20h,xs_rank_mom_accel
python scripts/check_factor_evaluation_page_completeness.py
```

Then:

```bash
python - <<'PY'
import pandas as pd
from pathlib import Path
p = Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_page_detail_completeness_report.csv')
df = pd.read_csv(p)
print(df[['factor_id','detail_status','detail_completeness_rate','missing_blocks','suspected_failure_layer']].to_string(index=False))
assert 'rev_2h' in set(df['factor_id'])
PY
```

## 11. Allowed files to change

Allowed scripts:

```text
scripts/check_factor_page_detail_completeness.py
scripts/check_factor_evaluation_page_completeness.py
scripts/_build_factor_eval_html.py
```

Allowed page only if needed:

```text
reports/site/factor-library/factor-evaluation.html
```

Allowed outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_page_detail_completeness_report.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_page_detail_completeness_report.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_page_completeness_report.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_page_completeness_report.json
```

Allowed audit:

```text
docs/factor_library/audits/pm40_factor_page_detail_completeness_rev2h.md
```

Do not modify:

```text
scripts/factor_formula_registry.py
scripts/factor_ops.py
scripts/build_factor_values.py
scripts/build_phase9b_signal_panel.py
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_*.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_*.json
reports/site/factors/*
reports/site/paper/*
src/momentum/strategies/*
```

## 12. Stop conditions

Stop and report if:

- `rev_2h` is missing from source diagnostics;
- public HTML is stale but deployment path is inaccessible;
- JS render bug cannot be diagnosed without browser automation;
- fixing content requires changing factor diagnostics or factor_values;
- signal/live code would need modification.

## 13. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
fix: verify factor detail page completeness
```

Final response should include:

- commit hash
- summary verdict
- whether `rev_2h` detail content is complete
- root cause if incomplete
- PM-35 five-factor detail completeness summary
- local/public page status
- repairs applied
- confirmation no factor/signal/diagnostic changes
- limitations
- recommended next PM
