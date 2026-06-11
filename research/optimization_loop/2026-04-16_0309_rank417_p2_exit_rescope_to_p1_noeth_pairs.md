# bot3 optimization loop log — 2026-04-16 03:09 UTC

## 执行小点
- cycle_plan item 1
- target: `Rank 417 / cointegration-first pair admission × no-stop intraday spread fade (Asia gate: UTC 0/5/6)`
- action: P2 出口决策轮（连续 2 次 `keep_P2` 后强制收口）

## 结果摘要（会改变系统认知）
`Rank 417` 在不放宽 `t+2 + 4/6/8bps` 与既有 `Asia UTC 0/5/6` 门控下，`leave-top-pair-out` 后仍保留费后正 alpha（`net8=+5.36bps`），但原始 spec 的 `cross-asset concentration` 未被消除，且 ETH-leg 子集持续结构性拖累；本轮执行 `one-time P2->P1 re-scope`，唯一明确新方向为：`non-ETH-leg + pair-cap`，并退出 Active P2。

## 核心证据
数据源：
- `reports/artifacts/quant_digests/2026-04-15_cointegrationfirst_nostop_t2_probe_trades.csv`

统一口径（不变）：
- `t+2` 入场
- round-trip 成本 `4/6/8bps`
- Asia 仅保留 UTC `0/5/6`

门控后总体（`n=78`）：
- `net8 total = +936.70bps`（`+12.01bps/trade`）

pair 贡献（`net8`）：
- `SOLUSDT-XRPUSDT: +615.03bps`
- `XRPUSDT-LTCUSDT: +407.00bps`
- `ADAUSDT-DOGEUSDT: +275.01bps`
- `XRPUSDT-BNBUSDT: +205.19bps`
- `ETHUSDT-LTCUSDT: -23.20bps`
- `ETHUSDT-BNBUSDT: -542.34bps`

最小 concentration 诚实检验：
1) `leave-top-pair-out`（剔除 `SOLUSDT-XRPUSDT`）后：
- `n=60`
- `net8 total = +321.67bps`（`+5.36bps/trade`）
- 说明 alpha 不是单对完全幻觉，但显著降档。

2) pair-cap 重加权（pair 贡献上限设为总收益 35%）后：
- `cap35 net8 total = +570.35bps`（`+7.31bps/trade`）
- 说明组合可在“限集中”约束下保留正值，但原 spec 本身仍未天然通过跨 pair 鲁棒性。

3) 明确 re-scope 方向可执行性：
- 去掉 ETH-leg 后子集：`n=59`, `net8 total=+1502.23bps`（`+25.46bps/trade`）
- 与上面两项一致，指向同一收敛方向：保留非 ETH-leg 对并叠加 pair-cap。

## 最小 honesty / execution realism 核对
- 未新增乐观假设、未改变滑点/费用、未引入新数据；仅对既有逐笔结果做重切片与权重压力测试。
- no-stop 长持有尾部风险仍存在（历史记录 `hold p90≈84.9 bars`）；该风险保留为后续 re-scope 版本的执行约束注记，不再作为本轮第二 blocker 扩张。

## 本轮执行结论
- verdict: `one-time P2->P1 re-scope`
- unique_rescope_direction: `non-ETH-leg pair subset + pair-cap portfolio construction under unchanged t+2 + 4/6/8bps and Asia UTC 0/5/6 gate`
- slot_change: `Active P2 -> none`，`Rank 417` 移入 background 等待按新 spec 重开（可人工 reopen）
- status: `done`

## 尾部执行状态（非阻断）
- homepage publish：待尾部命令执行。
- 邮件通知：待尾部命令执行。
