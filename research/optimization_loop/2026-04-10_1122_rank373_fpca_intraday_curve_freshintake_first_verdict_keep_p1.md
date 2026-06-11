# Rank 373 — FPCA intraday-curve slot router（fresh intake first verdict）

- 时间：2026-04-10 11:22 UTC
- 对象：`research/quant_digests/2026-04-10_0558_fpca-intraday-curve-slot-router-alpha.md`
- 执行动作：fresh intake 首判（按 post-cost 可交易口径）+ 最小成本可迁移性判断

## 本轮最小证据
1. digest 内本地 portability probe 已给出：
   - `all-slot sign book` 约 `49.4%`，gross 约 `-0.31 bps/bar`（不可直接当全天候 15m 连续翻仓策略）
   - 但固定时段 pocket 存在显著偏离：如 `01:00 UTC` 约 `63.8%` sign、gross `+3.92 bps`；`02:15 UTC` 约 `57.5%` sign、gross `+2.64 bps`
2. 论文证据与本地 probe 一致指向：edge 形态更接近“固定时段 router”，而不是全时段方向壳。

## 结论（改变系统认知）
`Rank 373`：FPCA intraday-curve alpha 在“固定时段筛选”语义下保留可交易边际，fresh-intake 首判收口为 `keep_P1`；**当前不支持跨资产直接复用**（默认先限 BTC），唯一 decisive blocker 为 `slot stability`（固定 UTC 强槽位随时间漂移，尚未完成 out-of-sample 稳定性闸门）。

## 层级与槽位处理
- 分配新 rank：`Rank 373`
- 本轮将该对象作为最新 `Surviving candidate`
- `followup_budget_remaining` 设为 `1`
- `Rank 372` 由 survivor 前排位移入 background（原因：单 survivor 槽位轮转，不是新负面证据）

## 下一步（留给后续轮次，不在本轮执行）
对 `Rank 373` 做唯一一次 survivor follow-up：最小 OOS 滚动 slot-stability gate（同一固定 UTC 槽位在相邻窗口是否稳定保留方向优势），用于判定 `P2` 入口可行性。