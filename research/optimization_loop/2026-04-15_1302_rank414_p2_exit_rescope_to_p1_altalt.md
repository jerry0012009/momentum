# Rank 414 P2 exit decision（15m-only 容量/滑点分层）— one-time P2->P1 re-scope

- 时间：2026-04-15 13:02 UTC
- 对象：`Rank 414 / roundtrip regime-stable pairs admission (admission-layer scope)`
- 对应 cycle_plan 小点：item 1（P2 admission round-2，出口决策前置轮）

## 本轮执行
在 `15m-only` 约束下，对 `rank414_tradequality_top8` 做最小高杠杆验证：
1) **容量分层**：按 pair 交易笔数三分位（`cap_low/cap_mid/cap_high`）
2) **滑点分层**：`net8 -> net10 -> net12` 代理（分别对应在 net8 基础上 +2/+4bps 往返摩擦）
3) **maj-alt 边际桶单独审计**：检查该桶在更严成本下是否仍可维持费后正值

## 证据产物
- `reports/artifacts/optimization_loop/rank414_p2_admission_round2_20260415/pair_level_slippage_capacity.csv`
- `reports/artifacts/optimization_loop/rank414_p2_admission_round2_20260415/bucket_slippage_summary.csv`
- `reports/artifacts/optimization_loop/rank414_p2_admission_round2_20260415/capacity_slippage_summary.csv`
- `reports/artifacts/optimization_loop/rank414_p2_admission_round2_20260415/bucket_capacity_slippage_summary.csv`
- `reports/artifacts/optimization_loop/rank414_p2_admission_round2_20260415/overall_slippage_summary.csv`
- `reports/artifacts/optimization_loop/rank414_p2_admission_round2_20260415/meta.json`

## 结果要点
1. **overall（trade-weighted）**
   - `net8 = +0.05869 bps`
   - `net10 = +0.01869 bps`
   - `net12 = -0.02131 bps`（翻负）

2. **bucket**
   - `alt-alt`：`net8/net10/net12 = +0.1063 / +0.0663 / +0.0263`（全程维持正值）
   - `maj-alt`：`net8/net10/net12 = +0.0077 / -0.0323 / -0.0723`（一抬摩擦即翻负）

3. **capacity × bucket（maj-alt 边际）**
   - `maj-alt cap_low`: `net8/net10/net12 = -0.1385 / -0.1785 / -0.2185`（结构性负值）
   - `maj-alt cap_mid`: `+0.0406 / +0.0006 / -0.0395`（接近零轴，抬摩擦即负）
   - `maj-alt cap_high`: `+0.0592 / +0.0192 / -0.0208`（net12 翻负）

## 出口决策
**结论：`one-time P2->P1 re-scope`（不是 promote_P3，也不是直接 drop_to_background/P0）。**

唯一明确 re-scope 方向：
- 将 `Rank 414` 从“全桶 admission-layer”收窄为 **`15m alt-alt only`** 的可执行 spec；
- 明确排除 `maj-alt`（该桶在容量/摩擦分层下表现为唯一 decisive blocker）。

一句会改变系统认知的话：
> `Rank 414` 的真实可执行 alpha 仅在 `15m alt-alt` 子域稳定成立，而 `maj-alt` 在容量/滑点分层下一抬摩擦即翻负，因此本轮必须从 `P2` 收口到一次性 `P1 re-scope（alt-alt only）`，不具备直接升 `P3` 条件。

## 对 conditional P3 handoff 小点的影响
- 由于 item 1 结论不是 `promote_P3`，`cycle_plan item 2`（conditional P3 wiring）前置条件不成立，应标记为 `blocked`（precondition false）。
