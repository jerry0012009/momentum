# bot3 optimization loop — maxmom lottery-spike filter fresh intake -> background/P0
- Time: 2026-04-23 06:43 UTC
- Target: `research/quant_digests/2026-04-23_0502_max-momentum-lottery-spike-filter-alpha.md`
- Cycle step: fresh intake first verdict
- Verdict: `background/P0`

## Why this step was the first legal pending action
`BOT2_BOT3_STATE.md` 里当前最前的 `pending` 小点就是这条 fresh intake：回答 `低 MAX 路径 continuation × lottery-spike filter` 是否真的把 plain momentum 提升成可独立排队的 after-cost alpha，而不是只留下 long-leg quality / router 提示。

## Minimal decisive blocker checked
只检查一个最小 blocker：**low-MAX 过滤是否已经形成可独立排队的 after-cost alpha，而不是仅仅改善 plain momentum 的 long leg 质量。**

## Evidence used
直接读取 digest 已落地 artifact：`reports/artifacts/quant_digests/2026-04-23_maxmom_proxy_grid.csv`。

聚焦最小可改变结论的信息：
1. `plain_mom` 的 `top1_bottom1_ls` 在全部 `9/9` 个 lookback × hold 组合里都为负；最好的一格也只有 `-0.641 bps/trade`（`L=24, hold=1`）。
2. `ret_minus_max` 与 `ret_over_maxabs` 两个“去尖刺打分”壳的 `top1_bottom1_ls` 也同样 `0/9` 为正；最好分别只有 `-1.048` 与 `-1.246 bps/trade`，没有把 plain momentum 翻成可收费的独立 long-short alpha。
3. 只有 `mom_lowmax_half` 的 `top1_long` 明显改善：`9/9` 个组合都为正，最好为 `+1.713 bps/trade`（`L=24, hold=4`），最差也仍有 `+0.118 bps/trade`；相比之下 `plain_mom` 的 `top1_long` 仅 `3/9` 为正，最好 `+0.667 bps/trade`。

## Decision
结论是 **不保留为前排新对象**：
- 这条线确实说明“低 MAX 路径比高 MAX 路径更像真 momentum”，但它证明的是 **entry quality filter / router**，不是独立可排队的主 alpha；
- 最关键的独立性门槛没有过：不管是 plain momentum 还是各种去尖刺 score，`top1-bottom1 long-short` 全部仍为负，说明它没有把 momentum 家族提升成新的可独立收费壳；
- 当前 digest 自己的 strongest signal 也集中在 `low-MAX long leg better than plain long`，这更适合作为已有 momentum / breakout / trend-shell 家族的 admission filter，而不是另开一个 fresh intake survivor 名额。

## Runtime-changing conclusion
`低 MAX 路径 continuation × lottery-spike filter` 已完成 first verdict 并收口 `background/P0`：它目前只证明 low-MAX 过滤能改善 plain momentum 的 long-leg 质量，未证明存在可独立排队、能脱离现有 momentum/trend-shell family 的 after-cost alpha。

## State write-back required
- 将当前小点标记为 `done`
- 将其 `result` 写为上述 runtime-changing conclusion
- 同步刷新 `Fresh intake slot` 的 latest result / record

## Notes
这一步没有触发新 rank、层级升级、survivor 锁定或 handoff；因此无需改写 `Surviving candidate`、`Active P2` 或 `Paper launch queue`。
