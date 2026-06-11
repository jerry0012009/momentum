# bot3 optimization loop — 2026-04-16 11:40 UTC

## 执行小点
- target: `research/quant_digests/2026-04-16_0935_funding-boundary-negfr-latency-short-shell.md`
- action: fresh intake first-verdict（统一 `t+2 + 4/6/8bps` + Asia/EU/US；补 1 个最小 honesty：funding 时钟对齐后的 delayed confirmation 与成交延迟）

## 本轮执行
1. 按 digest 设定复核 `extreme-negative funding × settlement-boundary continuation`，并以 `t+2` 作为最小 delayed-confirmation 入场。
2. 使用 Binance 公共接口做最小可复算抽样（当前极端负 funding 横截面 symbol + 近期 `fundingRate` 事件；`1m` K线对齐 `t+2→+5/+15`）。
3. 在统一成本口径下计算 after-cost 结果（`4/6/8bps`），并按 Asia/EU/US 分时段检查是否存在明显执行 realism 冲突。

## 抽样结果（最小 first-verdict 证据）
- 样本：`14` 个事件（极端负 funding 候选符号的近期 funding 事件）
- `t+2 -> +5m`：
  - overall mean（费前）`+22.59bps`；扣 `8bps` 后 `+14.59bps`
  - 分时段：Asia 扣 `8bps` 后 `-9.24bps`，EU 扣 `8bps` 后 `+32.95bps`
- `t+2 -> +15m`：
  - overall mean（费前）`+58.54bps`；扣 `8bps` 后 `+50.54bps`
  - 分时段：Asia/EU 在 `8bps` 下仍为正（分别 `+35.62/+42.54bps`）

## 最小 honesty / execution realism 子检查
- 将“时钟对齐后的 delayed-confirmation”固定到 `t+2` 后，`+15m` 口径仍保留正边际；
- 但样本高度集中在少量小市值合约，`+5m` 在 Asia 段已转负，说明**容量/拥挤/滑点放大**是当前唯一决定性 blocker，不能直接给到 P2。

## 结论（改变系统认知）
`funding boundary neg-FR latency short shell` 在统一 `t+2 + 4/6/8bps` + Asia/EU/US 下已出现可复制的 `t+2→+15m` 成本后正边际，但短窗与分时段稳定性受小币种容量集中约束；first-verdict 定为 `keep_P1`，分配正式 `Rank 418`，并把唯一 survivor blocker 收敛为“仅在大容量子集验证去拥挤后边际是否仍成立”。

## runtime 回写
- 新对象分配：`Rank 418 / funding boundary neg-FR latency short shell`
- `Fresh intake slot.latest_result` 更新为 `keep_P1`（已分配 Rank）
- `Fresh intake slot.latest_result_record` -> `research/optimization_loop/2026-04-16_1140_item1_funding_boundary_freshintake_keep_p1_rank418.md`
- `Surviving candidate slot` 切换为 `Rank 418`，并设置唯一 follow-up 预算 `1`
- `cycle_plan` item1 写回：`status=done`，`result` 已落地