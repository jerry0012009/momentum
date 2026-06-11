# Rank 385 — funding spike × intact 4H corridor midpoint fade fresh intake first-verdict = keep_P1

- 时间：2026-04-11 23:19 UTC
- 执行槽位：Fresh intake slot
- 对象：`research/quant_digests/2026-04-11_2208_funding-governor-4h-midpoint-fade-alpha.md`
- 新分配 Rank：**385**

## 本轮动作
按 cycle_plan 仅执行该 fresh intake first-verdict：复核该对象在可执行口径下是否应保留到 P1，且只锁定一个 decisive blocker。

## 关键证据（最小可复现口径）
- 复核 digest 引用 artifact：`reports/artifacts/literature/funding_4h_corridor_midpoint_probe_summary_2026-04-11.csv`。
- majors 结果在已扣 `8bps` round-trip 成本壳下仍为正：
  - BTCUSDT 5m/15m：`+64.31 / +56.80 bps`；
  - ETHUSDT 5m/15m：`+75.33 / +68.93 bps`；
  - BTC+ETH pool：`+71.50 / +64.89 bps`。
- 但 SOLUSDT(15m) 为 `-69.51 bps`，说明该主语当前是 majors-scoped，不支持全市场无差别外推。

## 本轮结论（改变系统认知）
该对象在 BTC/ETH majors 上已具备可保留的独立 raw alpha 主语（funding spike 但 4H 结构未破时做 midpoint fade），不应直接打回 background；本轮 first-verdict 判定为 **keep_P1**，并分配正式 Rank 385。

## 唯一 decisive blocker（按本轮约束二选一）
- **结构破位后误判延续**：当前“4H close still inside corridor”定义仍可能漏掉 intrabar 破位与 break-retest 延续场景，导致把真实 breakout 误判为可回归 fade；在补上该 veto 前，不进入更高层级。

## 槽位写回
- Fresh intake：`Rank 385` first-verdict 完成并保留 `keep_P1`。
- Surviving candidate：切换为 `Rank 385`，进入唯一一次 follow-up 预算（1 次）。
