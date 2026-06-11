# 2026-04-01 03:07 UTC — Rank 84 park reframe review

## Context
- Loop: `bot6 park-reframe`
- Scope this round: revisit exactly one parked rank without changing the original `park` verdict
- Selected rank: `Rank 84 / volume-price interaction admission layer`
- Selection reason:
  - Current loop has already spent many recent turns on `Rank 50+`; within the `80~110` band, `Rank 84` has **not** been revisited by park-reframe in the last 7 days
  - It is a clean parked item with a narrow enough residual question: whether the weak `volume × price thrust` interaction deserves a fresh derived hypothesis, or whether its only honest residual has already been consumed elsewhere

## What the original rank was trying to do
- Turn `price thrust + volume participation + wick absorption` into a **shared admission layer** for existing setups
- Intended role: not a standalone alpha, but a cross-lane `allow / deny / size` filter for long and short entries

## Why Rank 84 was parked originally
From the original clean replication (`2026-03-19 09:37 UTC`):
- `baseline mean_total_return ≈ -1.97%`
- `interaction_admission ≈ -1.40%`
- `interaction_sizing ≈ -1.35%`
- `trade retention ≈ 93.55%`
- `3-bar flip-to-fail rate` did **not** show a meaningful improvement

Interpretation:
- It did improve the result **a little**, but only from “slightly bad” to “slightly less bad”
- The gain was too small to claim a real, robust admission edge
- It never produced a clean cross-lane survival story, and it did not meaningfully reduce early failure

So the original `park` was correct: this was not a decisive shared admission layer, only a weak “less bad” filter.

## Hard park or soft park?
- **Classification now:** `soft park, but already leaning hard for the original Rank 84 framing`

Why not hard park outright:
- There *was* a real directional hint: interaction-based gating beat both raw baseline and pure single-volume gating
- The residual is not literally zero

Why it leans hard now:
- The residual is too small to justify reopening Rank 84 in its own name
- The most honest salvage path has already been consumed by nearby queue history, especially `Rank 20b` (`volume-price interaction shared admission layer`)
- Recent external evidence has pushed the same theme upward into either:
  1. more explicit `volume-price interaction` shared admission logic already represented by `Rank 20b`, or
  2. much shorter-horizon `1m/3m` microstructure raw-alpha families, not this 15m shared-gate lineage

## Is there any salvage signal?
Yes, but only a thin one.

### Salvage signal
- Interaction beats `single_volume_gate`, which means the information is not “just more volume = good”
- The only believable residue is: **price progress and volume need to be read jointly**, with wick/absorption acting as a penalty

### Why that signal is still too weak
- It did not produce a strong enough failure-rate reduction
- It did not create a clear setup-specific pocket with honest retention economics
- It does not define a distinct new queue-facing hypothesis beyond what the desk already captured elsewhere

## The single best cut, if forced to make one
If forced to preserve exactly one modification axis, the only honest cut would be:

- **Single modification axis:** demote generic `volume-price interaction` from a broad shared admission thesis into a narrower, already-known `volume-price interaction shared admission layer` role

But this is exactly the problem:
- that cut is **not new anymore**
- it is already substantially represented by existing `Rank 20b`

So the best cut exists, but it does **not** justify a fresh derived hypothesis from `Rank 84`.

## Trade on / Trade off
### Trade on
- Preserve the small but real insight that `volume` only matters when paired with directional price efficiency / thrust
- Keep wick absorption as a penalty, not an after-the-fact storytelling device

### Trade off
- Give up the idea that `Rank 84` still deserves its own queue-facing derived hypothesis
- Accept that whatever residual value remains has already migrated into existing shared-admission language (`Rank 20b`) or into higher-frequency microstructure families

## Why now
- Since the original park, the desk has accumulated more evidence that `volume/flow` themes either:
  - belong in a very narrow shared admission role already captured by existing candidates, or
  - survive only when moved to `1m/3m` raw-alpha / execution families
- That makes it less honest, not more honest, to draft a new `Rank 84b`

## Verdict
- **Final verdict:** `keep_park`
- Original `park` verdict remains intact for audit purposes
- Current reading: `soft park, but for the original Rank 84 framing it is already very close to hard`

## Direct answers required by bot6 brief
- **原 rank 为什么 park？**
  - 因为 clean replication 里 interaction 版本只是“比 baseline 略少亏”，没有形成足够硬的 shared admission edge，也没显著改善 early-fail。
- **它更像 hard park 还是 soft park？**
  - 更像 `soft park，但对原 Rank 84 叙事已明显偏 hard`。
- **有没有可救信号？**
  - 有，但很薄：`price thrust × volume participation` 比单独 volume gate 更有信息，且 wick absorption 确实该当惩罚项。
- **最值得改的唯一一刀是什么？**
  - 把 generic volume-price thesis 收窄成更窄的 `shared admission layer`；但这条唯一诚实残余已基本被 `Rank 20b` 吸收。
- **是否值得形成新的 derived hypothesis？**
  - **不值得。** 当前再写 `Rank 84b` 基本只会重复既有 `Rank 20b` 语义，缺乏 distinctness。

## Queue action
- Do **not** draft `Rank 84b`
- Keep `Rank 84` parked
- Leave top-level `TODO` scheduling unchanged

## Final note for PARK_REFRAME_QUEUE
Suggested queue note:
- `Rank 84 | verdict=keep_park | note=soft park，但对原 shared volume-price interaction admission 读法已明显偏 hard；原 clean replication 只留下很薄的 interaction>single-volume 残余，而这条唯一诚实修改轴已被既有 Rank 20b 基本吸收，近期新证据又把同主题继续上移到 1m/3m microstructure raw-alpha / execution family，当前不诚实再派生 Rank 84b`
