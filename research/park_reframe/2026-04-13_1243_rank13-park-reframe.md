# 2026-04-13 12:43 UTC — Rank 13 park reframe review

- loop: `bot6 park-reframe`
- source rank: `Rank 13 / partial-moment asymmetry TSMOM gate`
- current authoritative verdict: `park / evidence pool`
- this round verdict: `keep_park`
- original park verdict kept: `yes`

## Why this rank this round
- 本轮按 brief 回到 `Rank 1~37` 范围挑 1 条已 park 条目。
- 最近 `7` 天已复盘过的 `Rank 22 / 31 / 29 / 37 / 4 / 27 / 3 / 33 / 9 / 35 / 32 / 16 / 6 / 34 / 18 / 26 / 12 / 21 / 11 / 25 / 36 / 20 / 23 / 24 / 15 / 10 / 7 / 5 / 1 / 14 / 28` 这批条目，本轮默认避开。
- `Rank 13` 上次 park-reframe 记录是 `2026-04-07 12:32 UTC`，已超过 `7` 天。
- 且 `2026-04-10_0010_tailstate-partialmoment-tsmom-router-alpha.md` 提供了新的 partial-moment 旁证，足够回答：这是不是旧 Rank 13 值得再长出 `Rank 13c` 的新轴。

## Read set used this round
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- prior reframe log:
  - `research/park_reframe/2026-04-07_1232_rank13-park-reframe.md`
- original audit:
  - `research/optimization_loop/2026-03-17_0038_rank13-asymmetry-tsmom-park.md`
- new evidence:
  - `research/quant_digests/2026-04-10_0010_tailstate-partialmoment-tsmom-router-alpha.md`

## 原 rank 为什么 park
`Rank 13` 被 park，不是因为 partial-moment / asymmetry 主题完全没信息，而是因为它被写成 **standalone sign-momentum + partial-moment guard** 以后，clean replication 和稳定性审计一起失败。

基于 `2026-03-17_0038_rank13-asymmetry-tsmom-park.md`：
- primary `pm_guard_100 @ 6bps/side` 仍约 `mean_total_return ≈ -71.90%`
- `positive_asset_ratio = 0/3`
- `mean_max_drawdown ≈ -75.70%`
- 时间、参数、跨标的、成本四类 gate 一起 fail

所以原始被否掉的不是“tail asymmetry 有无信息”，而是：
- **把 partial-moment asymmetry 当成独立 15m crypto sign-momentum rescue line** 这层写法不成立。

## 它更像 hard park 还是 soft park
**本轮仍判：`soft park`，但比 4 月 7 日那轮又更偏硬。**

为什么还不是 hard park：
- 新增的 `2026-04-10 tail-state partial-moment router` 继续说明 partial-moment / tail-state 主题本身仍可能有信息；
- 只是那份新证据把它放在 **trend raw-alpha 的 router / veto / flip layer** 位置上，而不是旧 Rank 13 这种 standalone gate 壳里。

为什么更偏硬：
- 原 Rank 13 唯一诚实 residual 早已被既有 `Rank 13b` 占掉：把 partial-moment 降级成 `RS+/RS- realized-semivariance directional veto / sizing overlay`；
- 4 月 10 日的新 digest 没有给出第二条仍属于旧宿主的单轴修改，反而更明确地把主题抬升到 **新的 TSMOM raw-alpha / router family**。

## 有没有“可救信号”
**有，但它救活的不是旧 Rank 13 本体。**

这轮唯一值得保留的可救信号是：
- partial-moment / tail-state 能区分“该继续跟的趋势”和“更像快反转的坏趋势”；
- 但这更适合：
  1. 作为既有 `Rank 13b` 这类 shared directional overlay；或
  2. 作为新的 `tail-state partial-moment router × intraday TSMOM` raw-alpha 宿主。

也就是说，4 月 10 日新增证据并没有说：
- “旧 Rank 13 的 standalone guard 只差一个小修补”；

它真正说的是：
- “partial-moment 值得服务一个更完整的趋势宿主 / router。”

## 最值得改的唯一一刀是什么
**本轮没有新的唯一一刀。**

更准确地说：
- 旧 Rank 13 唯一诚实的一刀，仍然只是既有 `Rank 13b`：
  - `demote standalone partial-moment asymmetry TSMOM gate into an RS+/RS- directional veto / sizing overlay`
- 本轮新增的 tail-state 证据，没有把这条 residual 收窄成新的 `Rank 13c`；
- 它提供的是一条**更上位的新 raw-alpha/router 宿主**，不是旧 rank 内部第二条未消费的细修改轴。

## 是否值得形成新的 derived hypothesis
**不值得。**

原因：
1. 原 `park` 审计结论没变：旧 Rank 13 的 standalone 写法仍然不成立；
2. 旧 Rank 13 唯一自然 residual 已被 `Rank 13b` 消费；
3. `2026-04-10` 的新 partial-moment 证据，虽然强化了主题未死，但它更像新的 trend-router / raw-alpha 家族，而不是旧 Rank 13 的 `Rank 13c`；
4. 若现在硬写 `Rank 13c`，本质上会把“新宿主”误记到“旧 gate 壳”下面，稀释原 park 审计意义。

## Direct answers required by the brief
- **原 rank 为什么 park？**
  - 因为 standalone sign-momentum + partial-moment guard 在收益、回撤、时间、参数、跨标的、成本上一起失败，只是“少亏”，不是成立的 alpha。
- **它更像 hard park 还是 soft park？**
  - `soft park`，但比上次更偏硬。
- **有没有可救信号？**
  - 有；partial-moment / tail-state 仍有信息，但它更适合服务既有 `Rank 13b` 或新的 trend-router raw-alpha 宿主，而不是旧 Rank 13 本体。
- **最值得改的唯一一刀是什么？**
  - 无新增；原唯一诚实修改轴仍只是既有 `Rank 13b` 的 directional veto / sizing overlay。
- **是否值得形成新的 derived hypothesis？**
  - **不值得。** 当前不诚实再写 `Rank 13c`。

## Final verdict
- `final_status = keep_park`
- `original verdict kept = park`
- short note:
  - `Rank 13` 的 partial-moment 主题没有死，但 4 月 10 日新增证据把它进一步推向新的 trend-router / raw-alpha 宿主，而不是支持从旧 standalone gate 再诚实派生 `Rank 13c`；既有 `Rank 13b` 仍覆盖原 rank 唯一自然 residual。

## Queue action
- keep `Rank 13` parked
- keep existing `Rank 13b` as the only queue-facing residual
- do **not** draft `Rank 13c`
- do **not** modify `docs/TODO.md`

## Git / commit note
- 本轮只做 park-reframe 所需最小文本更新。
- 未做 selective commit；共享工作区可能存在无关脏文件，避免混提。
