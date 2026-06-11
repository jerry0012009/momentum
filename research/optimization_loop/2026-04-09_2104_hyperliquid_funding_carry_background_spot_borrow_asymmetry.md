# Hyperliquid XS funding carry persistence — fresh intake first verdict（background / P0）

- Time (UTC): 2026-04-09 21:04
- Executor: bot3 auto loop
- Policy/State refs: `docs/BOT2_BOT3_POLICY.md`, `docs/BOT2_BOT3_STATE.md`
- Cycle step: `cycle_plan` item 3（first pending）
- Target: `research/quant_digests/2026-04-09_0041_hyperliquid-xs-funding-carry-persistence-alpha.md`

## What was checked (minimal decisive honesty check)
- Re-read the digest to keep the object narrow: `trailing-24h funding rank × next-4h/24h funding persistence` as a **delta-neutral XS carry** idea, not a generic screener.
- Compared it against the existing carry family already in the system (especially prior Hyperliquid funding-rich/cheap crowding work) to test whether this is a genuinely new independent pocket.
- Ran one cheap execution-realism probe on the local repo artifacts (`funding_data_all_coins.csv` + `ohlcv_data_main.csv`): in the sample where the digest’s top-bucket opportunity appears, the positive-funding top bucket is heavily concentrated in names like `HYPE / PUMP / MON / FARTCOIN / XPL / ZRO`, while the crude obvious-spot-candidate share is only about `11.1%` (`2/18`, mainly `BTC/ETH`).

## Why this changes the verdict
The raw alpha statement itself is believable: extreme trailing funding does persist for the next few hours. But the executable book proposed in the digest is **not** yet shown to be desk-realizable as an independent two-sided delta-neutral carry pocket.

The decisive issue is not sign persistence; it is **borrow / short-locate / spot-leg availability asymmetry**:
- The rich-funding side needs `short perp + long spot`, which is sometimes doable when spot exists.
- The cheap-funding side needs `long perp + short spot`, which is exactly where borrow / locate / margin inventory becomes binding.
- In this sample, the names driving the rich top bucket are mostly smaller, crowding-heavy perp names rather than a clean set of obvious spot-borrowable majors.
- So the current evidence still proves **funding persistence**, but not a borrow-aware, fee-aware, capacity-aware **independent carry sleeve** that survives implementation.

## Verdict
`background / P0`（not `keep_P1`）.

## One-line system-changing result
该对象证明了小时 funding 横截面会延续，但当前样本里驱动 edge 的 rich-funding 名单大多不是清晰可借/可对冲的现货腿 universe，因而仍停留在“funding persistence 现象”而非可独立兑现的 borrow-aware XS carry pocket，首判收口为 `background / P0`。

## Runtime writeback required
- Mark `cycle_plan` item 3 as `done` with the above result.
- Advance `Fresh intake slot.current_target` to the next pending intake.
- Refresh `Fresh intake slot.latest_result(_record)` and `Background pool.latest_parked(_record)`.

## Notes
- No rank assignment required because verdict is `background / P0`.
- No `P1/P2/P3` slot migration happened in this step.
- This is consistent with policy’s guard against re-labelling a generic carry-family restatement as a fresh front-slot survivor without a new decisive executable edge.
