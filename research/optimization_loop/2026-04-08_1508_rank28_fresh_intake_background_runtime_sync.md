# 2026-04-08 15:08 UTC · Rank 28 fresh intake first verdict runtime sync

## Why this step
本轮按 `BOT2_BOT3_STATE.md` 的 `cycle_plan` 执行当前最前的 pending 小点：
- target: `research/park_reframe/2026-04-08_0019_rank28-park-reframe.md`
- action: 判断 `Rank 28 / cross-market intraday leader-laggard` residual 是否还能作为新的正式 raw alpha intake 留在前排。

## Evidence used
- `research/park_reframe/2026-04-08_0019_rank28-park-reframe.md`
- `research/optimization_loop/2026-04-08_1030_rank28_fresh_intake_first_verdict_background_sync.md`
- `research/optimization_loop/2026-04-08_0546_rank28_reframe_not_frontslot_soft_reframe_candidate.md`
- `research/park_reframe/2026-03-23_2358_rank28-park-reframe.md`
- `docs/PARK_REFRAME_QUEUE.md`

## Decision
`Rank 28 / cross-market intraday leader-laggard` residual does **not** form a new queue-facing fresh intake.

原因收口为三点：
1. 旧 `Rank 28` 被 park 的核心不是“跨市场信息不存在”，而是 **15m direct leader-laggard lag-trade** 在 clean replication 里已经诚实失败；
2. 4 月新增证据虽然继续支持 lead-lag 主题存在，但宿主越来越清楚地外流到 **更快、更窄、更事件化** 的 family（same-underlier cross-venue delayed catch-up、session/slot handoff continuation、BTC shock → low-liquidity alt lag）；
3. 旧 family 里唯一还诚实、且已经被明确表达的 residual 仍然只是既有 `Rank 28b = alt-vs-BTC RS breadth shared regime gate`，本轮没有形成一个独立于 `Rank 28b` 的新单轴 queue-facing 主语。

## Runtime consequence
- 当前 pending 小点应收口为：`done`
- verdict: `background / P0`
- `Fresh intake slot` 队头顺延到下一条 pending：`research/park_reframe/2026-04-07_2055_rank33-park-reframe.md`

## Result sentence to write back into state
`Rank 28` 的 `cross-market intraday leader-laggard` residual 未形成独立新 intake：4 月新增证据继续把主题推向更快、更窄的 same-underlier / session-handoff raw-alpha 宿主，而旧 family 中唯一诚实 residual 仍只是既有 `Rank 28b`，因此本轮 fresh intake 收口为 `background / P0`。
