# bot3 optimization loop log — 2026-04-15 19:41 UTC

## 执行小点
- cycle_plan item 1
- target: `Rank 415 / BTC anchor × 24h loser basket short`
- action: survivor 唯一 follow-up（15m 定时+drift gate 可行性的最小 decisive 检查）

## 本轮最小检查（围绕唯一 blocker）
- 数据源：`reports/artifacts/quant_digests/2026-04-15_btc_anchor_loser_basket_probe_hourly.csv`
- 额外产物：`reports/artifacts/optimization_loop/2026-04-15_rank415_survivor_drift_gate_threshold_check.json`
- 检查方法（最小/最便宜）：
  1) 先复算 hourly 基线 `gross` 与 `4/6/8bps*turnover` 的净收益；
  2) 用“drift gate 阈值”做乐观上界近似（仅把小额 turnover 置零，不计延后补调的追赶成本），看在分层成本下能否稳住费后正值。

## 结果
- hourly 基线净收益：
  - `net_4bps = +4.72%`
  - `net_6bps = -7.27%`
  - `net_8bps = -19.26%`
- 乐观 drift gate 阈值扫描：
  - 即便阈值抬到 `0.30`（已是强门控），也仅 `6bps` 转正（`+0.79%`），`8bps` 仍显著为负（`-8.51%`）；
  - 要让 `8bps` 非负，需把有效 turnover 压到小时基线的 `<=59.8%`（且这还是“gross 不受损”的乐观上界）。

## 结论（改变系统认知）
`Rank 415` 在其唯一 survivor follow-up 中未能通过分层摩擦稳健性：在对 drift gate 有利的上界近似下，`8bps` 口径仍费后为负，说明当前 spec 仍缺少可落地的单一执行解法；因此本轮直接收口为 `drop_to_background(P0)`，不晋升 `P2`。

## 本轮输出
- verdict: `drop_to_background(P0)`
- slot movement: `Surviving candidate -> Background pool`
- notes: survivor 唯一 follow-up 预算已用尽；后续仅可人工 `reopen`。
