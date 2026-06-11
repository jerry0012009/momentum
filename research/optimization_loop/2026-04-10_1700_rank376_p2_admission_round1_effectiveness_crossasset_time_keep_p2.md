# Bot3 Optimization Loop Log — 2026-04-10 17:00 UTC

## 执行小点
- cycle_plan 项目：#1（当前最前 pending）
- target: `Rank 376 / top-trader smartmoney skew continuation`
- action: `Active P2` admission 第 1 轮（`effectiveness + cross-asset + time`）

## 本轮最小检查（冻结执行壳）
数据源：
- `/root/clawd/jerry/momentum/reports/artifacts/literature/binance_toptrader_smartmoney_probe_detail_2026-04-10.csv`

固定口径（沿上一轮 honesty 通过后的 execution 壳）：
1. `interval=5m`，阈值仅复核已在前轮存活的主子集（`ETH short z<-2.0`、`BTC long z>2.0`、`SOL short z<-2.0`）。
2. 信号执行采用 `lag=1 bar`（5 分钟）+ `1h time-stop`（12 bar 持有）。
3. 成本采用 round-trip `12 bps` 主口径；并用 `16 bps` 做压力观察。

## 关键结果
### effectiveness（12 bps）
- `ETH short z<-2.0`: `+11.24 bps/笔`（n=155）
- `BTC long z>2.0`: `+4.25 bps/笔`（n=292）
- `SOL short z<-2.0`: `+11.10 bps/笔`（n=140）

### cross-asset
- BTC/ETH/SOL 三资产均仍有正净边际子腿，alpha 不是单资产幻觉。

### time stability（二分时段复核，12 bps）
- `ETH short z<-2.0`: half1 `+10.71` / half2 `+14.45`（稳定）
- `BTC long z>2.0`: half1 `+3.09` / half2 `+4.73`（稳定）
- `SOL short z<-2.0`: half1 `+21.34` / half2 `-5.70`（后半段转负）

## 本轮 admission 结论
- `Rank 376` 的主 alpha 仍成立（effectiveness 与 cross-asset 通过），但未达到“可直接进 paper trade”的稳定性门槛。
- 唯一 decisive blocker 已收口为：`SOL 极值空腿 time stability 断裂（后半段转负）`。
- 因仅剩单一可判定 blocker，本轮出口为 `keep_P2`（允许继续 1 次最小收口，而非开放式拖延）。
- 结论句：`Rank 376` 在统一 execution 壳下 BTC/ETH 仍稳健为正、SOL 极值空腿后半段转负，当前不升 P3，按单一 blocker 收口为 `keep_P2`。

## 对 runtime 的写回
- `Active P2 slot.latest_result` 更新为上述结论。
- `Active P2 slot.latest_admission_record/latest_result_record` 指向本日志。
- `p2_rounds_since_level_change: 1`
- `p2_consecutive_keep_p2: 1`
- `p2_last_evidence_axis: effectiveness_crossasset_time_admission_round1`
- `cycle_plan` #1 更新为 `done` + 结果句。
