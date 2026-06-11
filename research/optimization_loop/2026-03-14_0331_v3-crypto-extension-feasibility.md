# 2026-03-14 03:31 UTC — V3X-C crypto 180d feasibility benchmark

## Why this slice

`V3X-A` / `V3X-B` are already complete. The next unfinished parent task is `V3X-C`:

- extend crypto sample from `45d` to at least `180d / 365d`

That parent task is too large for one honest cron slice, so this run first split it and completed the smallest defensible subtask: benchmark the current v3 visible-line sampler on `180d / 60m` to quantify whether a full crypto rerun fits in a single 30-minute run.

## What I ran

- Counted 180d/60m bar availability for `BTC-USD / ETH-USD / SOL-USD / BNB-USD`
- Benchmarked the current sampler on BTC over the first 6 real snapshot windows, including:
  - `_detect_snapshot_lines`
  - line-by-line candidate event scanning across the subsequent 24 bars
- Projected serial runtime for:
  - one 180d crypto symbol
  - the 4-asset core crypto basket

## Main findings

- `BTC/ETH/SOL/BNB` all have about `4266~4269` rows at `180d / 60m`
- Under current v3 parameters (`window=96`, `step=24`, `confirm=2`, `tol=0.08`), that implies about `171` snapshot points per asset
- BTC benchmark over the first 6 snapshots:
  - average elapsed time ≈ `15.38s / snapshot`
  - median elapsed time ≈ `16.26s / snapshot`
  - average visible lines ≈ `363`
  - average candidate events ≈ `628.5`
- Projected serial runtime:
  - single asset ≈ `43.8 ~ 46.3 min`
  - BTC/ETH/SOL/BNB core4 serial basket ≈ `175 ~ 185 min`

## What this means

- The old unsplit parent task is too large for one honest 30-minute cron slice
- The next sensible order is:
  1. `BTC-only 180d` full rerun page
  2. core4 `180d` page
  3. decide whether `365d` is still worth it

## What this does NOT prove

- No new alpha verdict was produced here
- No claim is made yet about whether breakout family or rebound watch survives in the 180d sample
- This is a feasibility / workload closure, not a performance closure

## Deliverables

- Artifacts: `reports/artifacts/pytrendline_event_validation_v3_crypto_extension_plan_v1/`
- Page: `reports/site/factors/pytrendline_event_validation_v3_crypto_extension_plan_v1/report.html`
