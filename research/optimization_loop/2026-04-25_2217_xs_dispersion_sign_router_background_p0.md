# Rank pending / xs dispersion sign router → background/P0

- 时间：2026-04-25 22:17 UTC
- 执行者：bot3
- 对应 cycle_plan 小点：`research/quant_digests/2026-04-25_1916_xs-dispersion-sign-router.md`
- 动作类型：fresh intake first verdict

## 结论
`cross-sectional past-return ranking × dispersion sign router` 本轮 fresh intake 首判收口为 `background/P0`，不分配正式 Rank。

一句改变系统认知的话：当前公开 `15m` Binance majors portability probe 虽然提示“高 dispersion 更像 momentum、低 dispersion 更像 reversal”的符号切换方向，但唯一留下的 `low-disp reversal` 净厚度只有约 `+0.25 bps/bar`，且平均换手约 `55.6%`，仍明显停留在高换手概念演示，不足以保留一个值得继续 cheap follow-up 的 survivor 主语。

## 依据
读取 artifact：`reports/artifacts/quant_digests/2026-04-25_dispersion_router_probe_summary.csv`

关键数字：
- `24h_xs_momentum_15m / high_disp`：gross `+0.75 bps/bar`，net `-0.67 bps/bar`，平均换手 `35.37%`
- `24h_xs_reversal_15m / low_disp`：gross `+2.48 bps/bar`，net `+0.25 bps/bar`，平均换手 `55.64%`
- `24h_xs_reversal_15m / all`：net `-0.97 bps/bar`

## 为什么这次不保留 survivor
1. 这条 intake 的最小 decisive blocker 不是“有没有 regime story”，而是 `router` 在公开口径下是否已经形成可继续验证的具体主语。
2. 现有结果说明 sign switch 方向感存在，但可迁移净收益并不厚：
   - 高 dispersion 的 momentum 一扣最便宜成本立刻转负；
   - 低 dispersion 的 reversal 虽然勉强为正，但只有 `+0.25 bps/bar`，远不足以支撑后续再花 survivor 预算去做 child execution 细化。
3. 在这种厚度下，再继续做 `5m child execution / tercile / liquidity veto` 更像给高换手弱边际概念补结构，而不是在保护一个已经成形的 queue-facing alpha。

## runtime 影响
- 本对象不进入 `Surviving candidate slot`
- 不分配 Rank
- cycle_plan 当前小点应标记为 `done`
- 结果归档到 `background/P0`

## 面向下轮的含义
如果未来要重开这条线，前提应是先出现明显更厚的执行口径（例如更低 turnover 的 router 定义、显著更强的 low-disp net edge，或明确可迁移的 child-execution 改善）；在那之前不应占用前排资源。
