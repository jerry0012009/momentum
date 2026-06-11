# bot3 optimization loop log — 2026-04-12 02:04 UTC

## 执行小点
- cycle_plan 小点 #2
- target: `research/quant_digests/2026-04-12_0057_funding-settlement-xs-continuation-alpha.md`
- action: fresh intake first-verdict；复核 `long 高 funding bucket / short 低 funding bucket` 在 15m 一根持有后的成本后净边际，并补 1 个 execution realism 检查（结算边界拥挤滑点）

## 本轮最小证据
读取 artifact：
- `reports/artifacts/literature/funding_settlement_xs_continuation_summary_2026-04-12.csv`

关键 gross 结果（quartile long-short）：
- `5m/all/q`: `+2.16 bps/event`（211 events）
- `15m/all/q`: `+3.42 bps/event`（211 events）
- `15m/top_dispersion_q25/q`: `+3.86 bps/event`（53 events）

最小 execution realism 检查（结算边界拥挤滑点）：
- 该策略是双腿同时成交（long+short），且触发点集中在 funding settlement 边界，默认存在同步拥挤与冲击放大。
- 在任何现实可执行口径下，双腿 round-trip 的综合成本（手续费+滑点）要显著高于 `2~4 bps` 级别 gross edge；因此净边际无法稳定为正。

## 本轮结论（first verdict）
`funding-settlement xs continuation` 本轮首判为 **`background/P0`**。

- 结论类型：`background/P0`
- 唯一 decisive blocker：**`结算边界滑点/成交冲击吃尽边际（即成本后边际不足）`**
- 说明：排序信号在 gross 上有弱正值，但不足以穿透 funding 结算时点的真实双腿执行成本。

## 对 runtime 的影响
- 不分配 Rank（未达到 `keep_P1`）。
- 该对象进入 background，不进入 survivor / P2 / P3。