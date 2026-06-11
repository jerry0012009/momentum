# 2026-04-09 05:06 UTC — Rank 5 fresh intake first verdict

- target: `research/park_reframe/2026-03-23_1941_rank5-park-reframe.md`
- action: 作为当前首条 pending fresh intake，判断 `Rank 5` 的 `direct session-tail intraday TSMOM -> first-30m impulse-quality shared continuation gate / sizing layer` 是否已足够从旧 session-tail 主语中升成独立 impulse-quality gate，而不是继续停留在既有 session-clock raw-alpha family 的附属 admission 说明。
- success_criterion: 必须给出明确 first verdict：若对象能把 `first-30m impulse-quality shared continuation gate / sizing layer` 压成一个不被既有 session-clock / close-pocket / intraday continuation family 吸收、且不是单纯靠更少交易换来表面改善的独立 pocket，则写成 `keep_P1`；否则明确写成 `background / P0`。

## 读取的直接证据
1. 原始 park 审计：`research/optimization_loop/2026-03-16_2149_intraday-tsmom-session-park.md`
   - 原 Rank 5 的 direct tail trade clean replication 在 `BTC/ETH/SOL 15m` 上已经明确失败：主读法 `funding_8h_q60 @ 6bps/side` 下 `mean_total_return ≈ -22.74%`，`positive_asset_ratio = 0/3`，时间 / 参数 / 跨资产 / 成本四项稳定性一起 fail。
   - 这说明原主语 `direct session-tail intraday TSMOM` 已有明确 hard negative，不存在翻案空间。
2. 既有窄 reframe：`research/park_reframe/2026-03-19_1334_rank5-park-reframe.md` 与 `docs/PARK_REFRAME_QUEUE.md`
   - `Rank 5b` 已把唯一诚实残余收敛成：`demote direct session-tail intraday TSMOM entry into a first-30m impulse-quality shared continuation gate / sizing layer`。
   - 该残余本来就是 shared gate / sizing layer，而不是独立 raw-alpha pocket。
3. 后续复核：`research/park_reframe/2026-03-23_1941_rank5-park-reframe.md`、`research/optimization_loop/2026-03-30_0130_rank5_double_clock_residual_stays_park_reframe.md`、`research/park_reframe/2026-04-08_1439_rank5-park-reframe.md`
   - 多轮新增证据都指向同一结论：session clock 主题可能还有信息，但抬升的是更上位的 `open-impulse + pre-close reversal` / `same-clock router` / `close-pocket continuation` family，而不是 `Rank 5` 自己还能单独挂板的窄 residual。
   - 最新 4 月复核已明确写出：`唯一诚实残余仍只到既有 Rank 5b`，不足以再派生 `Rank 5c`。

## 本轮 first verdict
`Rank 5` 的 `first-30m impulse-quality shared continuation gate / sizing layer` 仍只是旧 `session-tail intraday TSMOM` 被降级后的 shared admission / sizing 备注层；现有新增证据没有把它压成一个独立、queue-facing 的 impulse-quality pocket，反而持续把主题外流到更大的 `session-clock / close-pocket / intraday continuation` 家族。与此同时，它的“改善叙事”仍主要建立在角色降级与更窄筛选上，而不是已经证明自己相对既有宿主 family 存在单轴独立增量。

## 结果句
`Rank 5` 的 `first-30m impulse-quality shared continuation gate / sizing layer` 仍只是旧 session-tail 主语降级后的 shared admission 备注层，新增证据继续把剩余价值外流到更大的 session-clock / close-pocket family，没有证明它已成长为独立、queue-facing 的 fresh intake pocket，因此 first verdict 收口为 `background / P0`。

## 状态写回意图
- 当前小点应写回：`done`
- 当前小点 result：同上结果句
- Fresh intake runtime 最新结论应更新到 `Rank 5 -> background / P0`

## 说明
- 本轮没有产生新的正式 Rank，也没有层级升级；因此不涉及 rank 分配、survivor / P2 / P3 迁移。
- 本轮属于 guard 后的明确收口，reader-facing 不强制新增独立页面；内部日志足以承载本次 runtime truth。