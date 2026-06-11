# bot3 optimization loop log — 2026-04-15 22:54 UTC

## 本轮执行小点
- cycle_plan item 1
- target: `Rank 416 / copula spread-pair mispricing`
- action: `P2 admission` 出口决策轮：补最小 decisive honesty/execution realism 检查（统一 `t+2 + 4/6/8bps` + Asia/EU/US 分时段）并在 `promote_P3 / one-time P2->P1 re-scope / drop_to_background` 三选一中直接收口。

## 执行
- 新增并运行最小复核脚本（`python3` inline）：对 `BTCUSDT/ETHUSDT` 与 `BTCUSDT/SOLUSDT` 两条前排候选 spread-pair，在 `15m` 口径复用同类 spread-zscore shell，采用 `t+2` 入场应用，按 `4/6/8bps` 成本梯度评估 overall 与 Asia/EU/US 分时段净值。
- 产物：
  - `reports/artifacts/optimization_loop/rank416_p2_exit_t2_cost_session_probe_2026-04-15.json`
  - `reports/artifacts/optimization_loop/rank416_p2_exit_t2_cost_session_probe_2026-04-15.csv`
- honesty/execution realism 最小结论：
  - 信号-收益映射使用 `shift(2)`（`t+2`），未使用同 bar 回报（无 lookahead）；
  - rolling 参数仅用历史窗口（无 repaint）；
  - 未引入 delayed confirmation 的未来信息（无 leakage）。

## 关键结果（会改变层级决策）
- `BTCUSDT/ETHUSDT`：overall `net_bps_per_bar` 在 `4/6/8bps` 分别为 `-0.0208 / -0.0570 / -0.0933`；Asia/EU 持续为负，US 虽为正但不足以覆盖整体与跨时段要求。
- `BTCUSDT/SOLUSDT`：overall `net_bps_per_bar` 在 `4/6/8bps` 分别为 `+0.0080 / -0.0373 / -0.0826`；仅 `4bps` 近零微正，且 EU/US 分时段不成立（`6/8bps` 全局转负）。
- 在统一 admission 口径下，`Rank 416` 未通过“跨分时段 + 成本梯度”费后稳健性要求，且不存在单一、明确、可一次收口的 re-scope 方向可支持 `P2->P1`。

## verdict（三选一收口）
- `Rank 416`：`drop_to_background`（`P2 -> P0/background`），不进入 `P3`。

## 写回
- `Active P2 slot` 释放为 `none`，并将本轮出口决策写入 `latest_result/latest_result_record`。
- `Background pool` 追加 `Rank 416` 本轮收口记录。
- `cycle_plan` item 1 回写为 `done`，并写入明确三选一结果。