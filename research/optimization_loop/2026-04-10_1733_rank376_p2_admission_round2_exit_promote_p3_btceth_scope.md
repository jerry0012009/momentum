# Bot3 Optimization Loop Log — 2026-04-10 17:33 UTC

## 执行小点
- cycle_plan 项目：#1（当前最前 pending）
- target: `Rank 376 / top-trader smartmoney skew continuation`
- action: `Active P2` admission 第 2 轮（出口决策轮）：围绕上一轮唯一 blocker（`SOL 极值空腿 time-stability 断裂`）做最小收口，比较 `BTC+ETH scoped` 与 `全资产保留 SOL` 两种去向。

## 本轮最小收口检查（不扩展到第二小点）
数据源：
- `/root/clawd/jerry/momentum/reports/artifacts/literature/binance_toptrader_smartmoney_probe_detail_2026-04-10.csv`

固定口径（沿用前轮 execution 壳）：
1. `interval=5m`，`lag=1 bar` 入场，`1h time-stop` 退出；
2. 子腿阈值仅复核上一轮存活集合：`ETH short z<-2.0`、`BTC long z>2.0`、`SOL short z<-2.0`；
3. 成本主口径 `12 bps`，并给出 `16 bps` 压力；
4. time-stability 继续按样本时间中点前后两段（half1/half2）做一致口径复核。

## 关键结果
### 单腿复核（net bps/笔）
- `ETH short z<-2.0`
  - `12 bps`: `+11.24`（half1 `+10.71` / half2 `+14.45`）
  - `16 bps`: `+7.24`（half1 `+6.71` / half2 `+10.45`）
- `BTC long z>2.0`
  - `12 bps`: `+4.25`（half1 `+3.09` / half2 `+4.73`）
  - `16 bps`: `+0.25`（half1 `-0.91` / half2 `+0.73`）
- `SOL short z<-2.0`
  - `12 bps`: `+11.10`（half1 `+21.34` / half2 `-5.70`）
  - `16 bps`: `+7.10`（half1 `+17.34` / half2 `-9.70`）

### scoped vs full（按腿等权的最小比较）
- `BTC+ETH scoped`
  - `12 bps`: `+7.74`（half1 `+6.90` / half2 `+9.59`）
  - `16 bps`: `+3.74`（half1 `+2.90` / half2 `+5.59`）
- `Full（含 SOL）`
  - `12 bps`: `+8.86`（half1 `+11.71` / half2 `+4.49`）
  - `16 bps`: `+4.86`（half1 `+7.71` / half2 `+0.49`）

## 出口决策
- `全资产保留 SOL` 版本仍存在明确稳定性断裂（`SOL short` 在后半段持续转负），不适合作为 paper launch 的默认入场形态。
- 但 `BTC+ETH scoped` 在主口径与压力口径下均保持正净边际，且 time-stability 未见同等级断裂，已满足“足够值得进入 paper trade / paper launch”的门槛。
- 因此本轮不再 `keep_P2`：直接执行 `promote_P3`，并以 **BTC+ETH scoped 版本**进入 `Paper launch queue`，后续按 `P3 launch wiring`（runner + scheduler + first verified run）接线。
- 结论句：`Rank 376` 的唯一 decisive blocker 已收口为 “SOL 子腿稳定性断裂且可通过范围收缩消除”，策略应以 `BTC+ETH scoped` 形态从 `P2` 直接升级到 `P3`。

## 对 runtime 的写回
- `Paper launch queue`：新增 `Rank 376` 为当前接线目标（状态：`queued_handoff_ready`，待 wiring）。
- `Active P2 slot`：`Rank 376` 退出并升级到 `P3`，当前清空为 `none`。
- `cycle_plan` #1：`status -> done`，写入上述结论句。