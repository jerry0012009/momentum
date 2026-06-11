# Rank 381 / perp OI 象限路由 fresh intake first verdict（keep_P1）

- 时间：2026-04-11 11:50 UTC
- 执行器：bot3
- 对象：`research/quant_digests/2026-04-11_0431_perp-oi-quadrant-router-alpha.md`
- 结论：`keep_P1`（分配正式 `Rank 381`），进入 survivor 一次性 follow-up 阶段

## 本轮执行的小点
按 cycle_plan 第 2 项执行 fresh intake first-verdict，不重排、不扩展第二小点。

## 最小证据复核（含 honesty 关注）
基于现有 artifact `binance_perp_oi_quadrant_router_probe_summary_2026-04-11.csv`，聚焦 `15m green+OI_up`：

- hold=2 bars: gross `+12.00 bps`，net(8/10/12bps) = `+4.00 / +2.00 / ~0.00`
- hold=4 bars: gross `+26.87 bps`，net(8/10/12bps) = `+18.87 / +16.87 / +14.87`
- hold=8 bars: gross `+23.45 bps`，net(8/10/12bps) = `+15.45 / +13.45 / +11.45`

同时 `15m red+OI_up` 在 hold=2 bars 为 `-7.23 bps`（追空不优），支持其更适合作为 short-veto overlay 而非独立 short continuation。

## first verdict
`Rank 381` 相比现有 funding/top-trader/liquidation 线，仍有可迁移增量（以简单公开 OI 口径做 bar 语义路由），且在 1h 档粗扣成本后仍有正净边际，因此不应直接丢回背景。

## 唯一 decisive blocker（本轮不升 P2）
当前缺失 **OI 时间戳可执行对齐证明**：尚未证明信号只使用“当时可见”的 OI 数据（避免 `openInterestHist` 聚合口径的发布延迟/回填造成的 confirmation leakage）。

在这一 blocker 未被一次性验证前，不能进入 `P2 admission`。

## 状态动作
- 新分配正式 rank：`Rank 381`
- fresh intake: `done -> keep_P1`
- survivor slot: 由 `none` 切换为 `Rank 381`，并保留唯一 follow-up 预算 1 次