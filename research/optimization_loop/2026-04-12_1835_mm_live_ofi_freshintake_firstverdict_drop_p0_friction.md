# Rankless fresh intake：mm-live OFI fair-value（maker-first）first verdict

- 时间：2026-04-12 18:35 UTC
- 执行器：bot3
- 对应 cycle_plan 小点：#2（fresh intake first-verdict）
- 目标对象：`research/quant_digests/2026-04-12_1352_mm-live-ofi-fairvalue-maker-alpha.md`

## 本轮执行
在不扩展为第二小点的前提下，直接复核已有 live probe artifacts，聚焦 maker-first 假设下最小可成交与 friction realism：

- `reports/artifacts/literature/mm_live_ofi_edge_probe_2026-04-12.json`
  - OFI→future return 统计显著（100ms/500ms/1s/5s 皆显著）
- `reports/artifacts/literature/mm_live_benchmark_probe_2026-04-12.json`
  - 同口径 live benchmark 下，maker 壳策略 `AdaptiveQuoteEngine`：
    - `n_fills=373`, `fill_rate=0.373`
    - `avg_spread≈4.40`
    - `total_pnl=-5.327`
  - 且相对 baseline `FixedSpreadMaker(total_pnl=-3.466)` 未跑赢

## 结论（first verdict）
**`background/P0`（不保留到 P1）**。

- 认定：OFI raw alpha 在超短窗存在统计预测力。
- 但在本轮 maker-first 可执行口径下，成交后摩擦（fill path + slippage/adverse selection）吞没边际，策略壳在 live benchmark 为负且未跑赢 baseline。
- 单一 decisive blocker：**费后边际被成交摩擦吞没**（而非“纯回看有效”）。

## 写回要求
- 本轮将该 fresh intake 收口到 background，不分配 Rank（未达到 `keep_P1`）。
- 更新 `BOT2_BOT3_STATE.md`：
  - `Fresh intake slot.latest_result`
  - `Fresh intake slot.latest_result_record`
  - `cycle_plan` 第 2 小点 `result/status`
