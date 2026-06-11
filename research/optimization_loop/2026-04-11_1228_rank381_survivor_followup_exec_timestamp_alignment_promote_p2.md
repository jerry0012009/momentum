# Rank 381 survivor follow-up（OI 时间戳可执行对齐）-> promote_P2

- 时间：2026-04-11 12:28 UTC
- 执行器：bot3
- 对象：`Rank 381 / 15m perp price×OI quadrant router`
- 对应 cycle_plan：第 1 项（survivor 唯一一次 follow-up）

## 本轮动作
仅执行 survivor 唯一一次 follow-up：用最小 honesty 子检查验证该对象在“可执行时间戳”口径下是否仍存活，避免 `openInterestHist` 延迟/回填导致 confirmation leakage。

## 最小 honesty 子检查（唯一）
用 Binance 公共接口重跑同一对象的 `15m green+OI_up`：
- `same_bar`：按同根 `ΔOI_z>1.5` 定义（对照）
- `lag1_exec`：严格把 OI shock 信号整体滞后一根 15m（仅用上一根已完成 OI），再评估后续收益

聚合结果（7 币：BTC/ETH/SOL/XRP/DOGE/BNB/ADA）：
- `lag1_exec, hold=2`：`+10.64 bps` gross，扣 `10 bps` 后 `+0.64 bps`
- `lag1_exec, hold=4`：`+14.26 bps` gross，扣 `10 bps` 后 `+4.26 bps`
- `lag1_exec, hold=8`：`+25.84 bps` gross，扣 `10 bps` 后 `+15.84 bps`

结论：在严格可执行（lag1）口径下，`1h~2h` 持有档仍保留正净边际；上一轮唯一 decisive blocker（时间戳可执行对齐）已被解除。

## 出口判定
`Rank 381` survivor follow-up 收口为 **`promote_P2`**（不是 background/P0）。

## 产物
- `/root/clawd/jerry/momentum/reports/artifacts/literature/binance_perp_oi_quadrant_router_followup_exec_lag_probe_2026-04-11.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/binance_perp_oi_quadrant_router_followup_exec_lag_probe_agg_2026-04-11.csv`
