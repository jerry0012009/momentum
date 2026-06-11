# Rank 186 / CME expiry postfix short BTC — fresh intake keep_P1

- Time: 2026-03-26 15:58 UTC
- Slot executed: Fresh intake slot
- Source digest: `research/quant_digests/2026-03-26_1035_cme-expiry-postfix-short-bias.md`
- Verdict: `keep_P1`
- Assigned rank: `186`

## What I checked
- Digest claim is specific enough to count as an exact raw alpha candidate: `last Friday 16:00 London` monthly CME BTC expiry, then `short BTC` for `post 60~120m`.
- Supporting artifact summaries exist and are already reduced to the exact event window rather than a vague expiry-day effect:
  - `reports/artifacts/quant_digests/cme_expiry_postfix_short_20260326/bucket_summary.csv`
  - `reports/artifacts/quant_digests/cme_expiry_postfix_short_20260326/expiry_minus_placebo_summary.csv`
- Minimal cross-check from those artifacts:
  - Binance perp: expiry `post60 = -21.0bp` vs non-expiry Friday same-clock `+15.5bp`, diff `-36.5bp`; `post120` diff `-41.4bp`.
  - Binance spot: expiry `post60 = -20.8bp` vs non-expiry Friday same-clock `+15.4bp`, diff `-36.2bp`; `post120` diff `-41.2bp`.
  - Sample is still small (`14` monthly expiry events vs `47` placebo Fridays), so this is not enough for direct P2 admission.

## Decision
`Rank 186 / CME expiry postfix short BTC` should be kept in the front chain as a survivor candidate, because the current evidence already shows a concrete, exact-time, spot/perp-consistent event-driven short drift that is stronger than a generic “expiry day gets noisy” story.

## Why not park
I did **not** park it because the object is already concrete on all the dimensions that matter for a first verdict:
- exact clock is public and reproducible;
- trade direction is explicit (`short BTC after expiry`);
- holding window is explicit (`60~120m`);
- spot and perp point the same way;
- the edge is framed against same-clock Friday placebo rather than a vague unconditional average.

## Why not promote directly to P2
I did **not** promote directly to P2 because the surviving uncertainty is still the obvious one: monthly-event sample size is structurally small, so the next honest follow-up should first answer whether this pocket survives a slightly broader, still-cheap replication / setup split rather than opening the full five-axis P2 admission tree immediately.

## Survivor follow-up to reserve
The one allowed survivor follow-up should stay narrow:
- expand/clean the event family or extend history enough to test whether the edge is still there beyond the current `14` monthly expiries;
- preferably keep the exact raw alpha fixed (`monthly CME expiry -> post 60~120m short BTC`) rather than broadening into a generic expiry complex.

## Result sentence for runtime
`Rank 186 / CME expiry postfix short BTC` 首判维持 `keep_P1`：当前月度到期后 `60~120m short BTC` 在 Binance spot/perp 相对普通周五同钟窗口都呈现约 `-36bp` 到 `-41bp` 的负漂移差值，已足以保留为 survivor，但月度事件样本仍偏少，暂不直接升 `P2`。
