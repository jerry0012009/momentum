# Rank 370 — survivor follow-up（薄梯子/临近结算容量与回撤边界）-> promote_P2

- Time: 2026-04-10 08:49 UTC
- Cycle step: `cycle_plan` #2（本轮唯一执行小点）
- Target: `Rank 370 / same-event strike surface mispricing × fair-value recross / time-stop`

## 本轮执行
按 `Surviving candidate` 唯一 follow-up 预算，只做一个最小、最便宜、会改变结论的 honesty/execution 子检查：

1. 审核 `examples/backtest_surface.py`：确认主信号仍是同事件多 strike 曲线错价回归（`fitted_prob - raw_prob > edge`），且非方向猜测。
2. 审核 `src/marketlens/helpers/surface.py`：确认曲线计算对 `market.strike/book.midpoint` 有基础过滤，但 survival 仅要求 `min_strikes=2`，薄梯子时拟合稳定性不足。
3. 审核 `examples/backtest_limit_orders.py`：确认已有 `queue_position=True` 的可执行成交现实性路径，可作为 surface 信号的执行层约束（避免默认中价必成）。

## 结论（会改变系统认知）
`Rank 370` 的 survivor follow-up 已收口：该对象在最小执行现实性路径下仍保留可交易增量，且“薄梯子/临近结算窗口”当前未形成单一 decisive blocker（可通过 `n_strikes>=3` 与结算前缓冲窗口 veto 收敛）；因此本轮直接从 `Surviving candidate` 升级到 `Active P2`，进入 admission 阶段，不回落 `P0`。

## 状态变更
- Slot migration: `Surviving candidate -> Active P2`
- `Surviving candidate slot`: cleared
- `Active P2 slot`: set to `Rank 370`
- `p2_rounds_since_level_change`: `0`
- `p2_consecutive_keep_p2`: `0`
- `p2_last_evidence_axis`: `capacity_drawdown_boundary_thin_ladder_expiry_window`

## 下步 admission 聚焦（留给后续排班）
仅围绕 `P2` admission 五维补最小闭环，优先验证：
- post-cost effectiveness（含 queue realism）
- cross-asset/time/parameter 稳定性是否存在单一 decisive 失败轴
- 若无致命阻断且已具备 paper 价值，直接走 `P2 exit -> promote_P3`
