# Bot3 Optimization Loop Log — 2026-04-14 17:32 UTC

## 执行小点
- cycle_plan #1
- target: `Rank 404 / polymarket latency-negation arb shell`
- action: survivor 唯一 follow-up（按最小 execution realism 口径判定费后净 edge 与可成交性）

## 本轮执行
- 使用上一轮 fresh-intake 已落库的 stale 观测产物：
  - `reports/artifacts/rank404_polymarket_latency_negation_freshintake/latency_stale_probe_20260414_165401.json`
- 新增 follow-up 产物：
  - `reports/artifacts/rank404_polymarket_latency_negation_survivor_followup/survivor_followup_costfloor_summary_20260414_173059.json`

## 关键证据（最小但可决策）
- stale 样本事件数：`6`
- `poly_unchanged` 窗口内 Binance 变动：
  - `max = 10.77 bps`
  - `median = 1.75 bps`
- `poly_trade_age` 最大约：`62.94s`

### 费后下限门槛（偏乐观）
- fees: `7 bps`
- half-spread: `8 bps`
- gas+settlement friction: `5 bps`
- 1-step lag: `3 bps`
- 合计最小成本门槛：`23 bps`

对照结果：
- `max observed move 10.77 bps < 23 bps`
- `margin = -12.23 bps`

## 出口结论
- verdict: **`background / P0`**（不 `promote_P2`）
- 一句话（改变系统认知）：`Rank 404` 在 survivor 唯一 follow-up 下，stale 窗口可观测价格偏移即使按乐观成本下限仍不足以覆盖 `fees+spread+gas+1-step lag`，费后净 edge 不成立，收口到 `background/P0`。

## Runtime 回写要点
- `Surviving candidate slot` 清空（`current_target = none`，follow-up 预算归零）。
- `Background pool.latest_parked` 更新为 `Rank 404` 本次收口结论。
- `cycle_plan #1` 标记 `done` 并写入上述 result。