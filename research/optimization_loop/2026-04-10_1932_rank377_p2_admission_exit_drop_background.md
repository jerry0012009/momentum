# 2026-04-10 19:32 UTC · Rank 377 P2 admission exit decision（drop to background）

## 执行动作
- 对象：`Rank 377 / liquid staking basis mean reversion`
- 对齐 `cycle_plan #2`：在 Active P2 admission 轮一次性覆盖 `effectiveness / cross-asset / time / parameter`，并补 1 个最小 honesty blocker 后直接给出口决策。

## 本轮最小新增 honesty 检查（唯一 decisive blocker）
- blocker 设定：`signal->execution timestamp realism`（是否存在 bar-close 同价成交带来的可交易性高估）。
- 做法：在同一策略壳（`15m, lookback=192, entry |z|>=3, exit |z|<=0.5 or max_hold=32`）下，对比：
  1) 旧口径：`close-entry`（信号 bar 收盘价入场）
  2) 新口径：`next-open entry`（下一根开盘入场，避免同 bar 执行幻觉）

## admission 证据
### 1) effectiveness（含成本）
- `WBETHETH direct pair`：
  - close-entry：`93` 笔，gross `+4.80 bps/笔`，net@4bps `+0.80 bps/笔`
  - **next-open**：`93` 笔，gross `+3.70 bps/笔`，**net@4bps `-0.30 bps/笔`（转负）**
- 结论：在更诚实的执行时点下，主交易壳净边际不再为正。

### 2) cross-asset / cross-representation stability
- synthetic 表达（`WBETHUSDT / ETHUSDT` ratio，next-open 同口径）
  - `189` 笔，gross `+5.12 bps/笔`，net@4bps `+1.12 bps/笔`
- 但该表达是双腿执行，真实 round-trip 成本通常高于单腿 `4bps`；按更保守双腿成本口径其净值不稳，不能替代 direct pair 的 admission 通过。

### 3) time stability（next-open 口径）
- first half：`47` 笔，net@4bps `-1.31 bps/笔`
- second half：`46` 笔，net@4bps `+0.73 bps/笔`
- 结论：时段漂移明显，稳健性不足。

### 4) parameter stability（next-open 口径）
- lookback×entry 网格（exit=0.5, hold=32, net@4bps）：
  - `lb96,e2.5` = `-2.03`
  - `lb96,e3.0` = `-1.42`
  - `lb192,e2.5` = `-1.34`
  - `lb192,e3.0` = `-0.30`
  - `lb288,e2.5` = `-2.35`
  - `lb288,e3.0` = `-1.95`
- 结论：参数邻域广泛为负，当前壳不具备 admission 所需稳健度。

## 出口决策
- **verdict：`drop_to_background`（P2 -> P0/background）**
- 一句话改变系统认知：`Rank 377` 在唯一关键 honesty 修正（next-open execution realism）后，direct pair 的 post-cost edge 由正转负且参数/时间稳定性不足，不值得进入 paper trade / P3。

## 对 runtime 的影响
- `Active P2 slot`：清空为 `none`。
- `Background pool`：新增 parked 对象 `Rank 377`（原因为 execution timestamp realism 导致 net edge 失效）。
- `cycle_plan #2`：`status=done`，结果写入 drop 结论。
