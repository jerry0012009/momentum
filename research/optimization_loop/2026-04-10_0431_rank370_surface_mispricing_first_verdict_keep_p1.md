# Rank 370 — same-event strike surface mispricing first verdict: keep_P1

- Time: 2026-04-10 04:31 UTC
- Cycle step: `cycle_plan` #4（本轮唯一执行小点）
- Target: `research/quant_digests/2026-04-08_2336_surface-mispricing-strikecurve-alpha.md`

## 本轮执行
在不重排 `cycle_plan` 的前提下，执行该 fresh intake 的 first verdict，并补 1 个最小 honesty 子检查（执行现实性）：
- 检查 `backtest_surface.py`：信号是 `compute_surface` 拟合同事件多 strike 单调曲线后做 `fair_prob - raw_prob` edge 交易，不是单纯方向猜测。
- 检查 `backtest_limit_orders.py`：回测壳支持 `queue_position=True` 的队列成交仿真，不是默认“中价必成”。

## 结论（会改变系统认知）
`same-event strike surface mispricing × fair-value recross / time-stop` 在当前证据下可作为独立 raw alpha 保留：其核心 edge 来自同事件 strike 曲面横截面错价，而非仅靠不现实成交假设；本轮未出现单一 decisive honesty/execution blocker，因此给出 `keep_P1`，并分配正式 `Rank 370`，进入 `Surviving candidate slot`（follow-up budget=1）。

## 状态变更
- New rank assigned: `370`
- Fresh intake verdict: `keep_P1`
- Slot migration: fresh intake -> surviving candidate

## Next decisive check（留给后续排班）
只做一次最小 follow-up：验证 edge 在最小成交约束下的容量/回撤是否仍成立（尤其是薄梯子与临近结算窗口），若通过再考虑升 `P2`，否则收口到 `background / P0`。
