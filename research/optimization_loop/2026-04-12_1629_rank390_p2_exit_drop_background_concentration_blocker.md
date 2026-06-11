# bot3 optimization loop — 2026-04-12 16:29 UTC

## 执行小点
- target: `Rank 390 / passivbot EMA forager bounce`
- action: `P2 exit decision`（在既有 `extreme_top2vol` 作用域上补 1 个最小 honesty/execution realism blocker 检查后，直接给出三选一出口）

## 本轮最小检查（honesty / execution realism）
数据源：`reports/artifacts/literature/passivbot_forager_alt_probe_2026-04-12_detail.csv`

仅在 `variant=alt4_extreme_top2vol` 下复算压力口径，并做最小分解：
- 压力口径均值（bps/笔）：
  - `stress_12bps`: `+7.90`
  - `stress_16bps`: `+3.90`
  - `haircut_tp25_+6bps`: `+3.55`
  - `haircut_tp40_+8bps`: `+2.10`
- 资产分解（`haircut_tp40_+8bps`，bps/笔）：
  - `BNBUSDT +20.00`, `XRPUSDT +20.00`, `ETHUSDT -2.11`, `SOLUSDT -1.14`
- 时间分解（`haircut_tp40_+8bps`，月均 bps/笔）：
  - `2025-10 -9.78`, `2025-11 +7.71`, `2025-12 +0.59`, `2026-01 +20.00`, `2026-02 +20.00`, `2026-03 -18.44`
- 同窗诚实性复核：`signal_time -> entry_time` 固定 `+900s`，无负 lag（未见前视触发）

## 出口决策
- verdict: `drop_to_background (P0)`
- decisive blocker（唯一）：**费后正边际高度集中于少数资产/少数月份，跨资产与时间稳定性不足，不满足 paper launch 的最小可迁移性要求**。

## 结论（会改变系统认知）
`Rank 390` 虽在窄域聚合均值仍为正，但其可执行优势主要由 `BNB/XRP` 少量窗口贡献，`ETH/SOL` 与多个月份在压力口径下转负；因此本轮 `P2 exit decision` 收口为 `drop_to_background`，不进入 `P3 / paper launch queue`。

## 运行态落库
- 层级迁移：`Active P2 -> Background pool(P0)`
- `Active P2 slot.current_target`: `none`
- `Background pool.latest_parked`: 更新为 `Rank 390`
