# Cross-engine mapping plan + site wiring

## Why this was chosen now

The nearest unfinished thread in `jerry/momentum` was the just-completed reorganization around **Structure-Event Mainline** vs **Engine Labs**.

That reorg clarified the top-level information architecture, but one high-leverage gap remained in `docs/TODO.md`:

- `A1-A`: draft a **cross-engine unified event schema**
- `A1-A`: add a **Cross-Engine Mapping** page

This was the smallest useful next step because it resolves an active ambiguity:

- `PyIndicators` and `PyTrendline` are **different definition engines**
- but the project's true mainline is now **Structure-Event Alpha Research**
- so the repo needed one explicit bridge page saying what can align, what cannot align, and how both engines should feed the same mainline

## What changed

Main point for this auto run:

1. **Added `docs/CROSS_ENGINE_MAPPING.md`**
   - explains the role split:
     - `PyIndicators` = first event-study source / baseline source
     - `PyTrendline` = explainability baseline / future event-source candidate
   - explains what should and should not be hard-aligned
   - proposes a first **unified event schema v0** with:
     - shared fields (`source_engine`, `event_family`, `event_subtype`, `line_side`, `event_timestamp`, etc.)
     - engine-specific fields left explicitly engine-local
   - proposes a two-layer translation model:
     - engine-native object
     - mainline event object

2. **Added a site mirror page**
   - `reports/site/plans/cross_engine_mapping.html`
   - wired into `scripts/build_plans_site.py`

3. **Wired the new mapping page into the reworked site structure**
   - added `Cross-Engine Mapping` into plan pages
   - added it to the appendix links for:
     - `Structure-Event Mainline`
     - `Engine Lab · PyTrendline`
     - `Engine Lab · PyIndicators`

4. **Updated TODO to mark the two A1-A items complete**
   - cross-engine unified event schema draft
   - Cross-Engine Mapping page

## Validation / evidence

Minimal relevant validation only:

- `./.venv/bin/python -m py_compile scripts/build_plans_site.py scripts/build_trendline_tracks_site.py`
- rebuilt only the needed site outputs:
  - `./.venv/bin/python scripts/build_plans_site.py`
  - `./.venv/bin/python scripts/build_trendline_tracks_site.py`
- published only the changed site pages

Online verification:

- `https://jp.jerrypsy.top/momentum/plans/cross_engine_mapping.html` returns 200 and shows the new mapping note
- `https://jp.jerrypsy.top/momentum/factors/structure_event_mainline/report.html` still renders correctly after wiring the new appendix link
- `https://jp.jerrypsy.top/momentum/factors/trendline_pyindicator_track/report.html` still renders correctly after wiring the new appendix link

## Risks / caveats

- This run adds **planning / mapping clarity**, not new event statistics.
- The unified schema is explicitly a **v0 draft**, not yet enforced in source exports.
- `PyTrendline` still does not emit a full event-study source table; this run only clarifies the bridge design.

## Next recommended step

1. Add a minimal **PyTrendline event-source bridge** export.
2. Emit the smallest comparable fields into the new schema:
   - `source_engine`
   - `event_family`
   - `event_timestamp`
   - `line_side`
   - `engine_line_id`
   - `quality bucket`
3. Then do the first side-by-side comparison:
   - `PyIndicators source`
   - vs `PyTrendline source`
   - under the same mainline framing.

## Commit hash

- `49baa32` — `docs(momentum): add cross-engine mapping plan`

## If not committed, why

This run **was** selectively committed.

I intentionally excluded unrelated dirty files already present in the repo, including:
- reading site pages unrelated to this run
- in-progress `trendline_confirmation_ladder` artifacts
- unrelated workspace-level untracked files outside this coherent change set
