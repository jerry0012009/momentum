# bot3 optimization loop log — 2026-04-15 20:18 UTC

## 执行小点
- cycle_plan item 2
- target: `research/quant_digests/2026-04-15_1148_extremefunding-directional-capture-alpha.md`
- action: fresh intake first-verdict（统一 `t+2 + 4/6/8bps` 成本口径 + 最小 execution realism 检查）

## 结果摘要（会改变系统认知）
`extreme funding directional capture × next-settlement timebox` 在本轮统一口径下不通过 first-verdict：样本仅由单一资产（`SOLUSDT`）驱动，且 `US` 分时段在 `4/6/8bps` 下持续大幅为负，未满足前排保留所需的跨时段稳健性，因此本轮收口 `background/P0`（不进入 survivor，不分配 Rank）。

## 关键证据
复核产物：
- `reports/artifacts/quant_digests/2026-04-15_extremefunding_directional_t2_probe_summary.json`
- `reports/artifacts/quant_digests/2026-04-15_extremefunding_directional_t2_probe_events.csv`

最小可复核口径（Binance perp proxy）：
- 资产池：`BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK`
- 事件触发：`|fundingRate(8h)| >= 0.0008`（对应 digest 的 `0.01%/hr` 极端阈值）
- 方向：`funding>0 -> short`，`funding<0 -> long`
- 执行：`t+2h` 入场，持有 `6h`（近似到下一 funding 结算窗）
- 成本：统一 `4/6/8bps`

汇总结果：
- 事件数：`15`（全部来自 `SOLUSDT`，其余资产无满足阈值事件）
- 全体均值：`net4=+84.95bps`，`net6=+82.95bps`，`net8=+80.95bps`
- 分时段（UTC）均值：
  - `Asia`: `net8 +140.74bps`
  - `EU`: `net8 +325.24bps`
  - `US`: `net8 -527.19bps`

判定要点：
1. **跨资产不可用**：触发完全集中在单一标的，无法支持 desk 级“可迁移/可扩展”首判。
2. **跨时段不稳**：US 时段显著负值，违背统一 first-verdict 对分时段稳健性的最低要求。
3. 因此该 raw alpha 暂不保留前排，直接回收 background，等待后续若有明确 re-scope（如仅限特定时段+资产）再人工 reopen。

## 最小 honesty / execution realism 子检查
- **无前视泄漏**：事件由 funding 时间戳触发，统一 `t+2h` 执行，不使用同一时点后验信息改写入场。
- **执行现实性（最小）**：统一成本梯度 `4/6/8bps` 下，结论方向不变（US 持续显著负）。
- **唯一 decisive blocker**：非成本微调，而是“事件稀疏且单资产集中 + 分时段符号分裂”。

## 本轮执行结论
- verdict: `background/P0`
- rank_assignment: `none`（未达到 `keep_P1`）
- survivor: `not eligible`
- status: `done`
