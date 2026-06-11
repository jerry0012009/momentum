# bot3 执行日志 — 2026-04-21 06:23 UTC

## 本轮执行小点
- 来自 `BOT2_BOT3_STATE.md` 的 `cycle_plan` 第 3 项（首个 pending）
- target: `research/quant_digests/2026-04-21_0242_dynamic-momentum-cycle-router-alpha.md`
- action: fresh intake first verdict（`dynamic momentum-cycle continuation × strongest-only router`）

## 最小 decisive blocker 检查（按计划仅做 1 项）
- 数据源：
  - `reports/artifacts/quant_digests/dynamic_tsmom_cycle_filtered_detail_2026-04-21.csv`
  - `reports/artifacts/quant_digests/dynamic_tsmom_cycle_filtered_router_2026-04-21.csv`
- 口径：`5m strongest-only(top1 by score)`，统一 round-trip `8bps`（`net8 = ret_bps - 8`），并检查跨币与 recent month（2026-04）

### 结果
1. strongest-only 在成本后整体不成立：
   - hold6: `n=373`, `mean gross=+1.83bps`, `mean net8=-6.17bps`, `median net8=-10.44bps`
   - hold12: `n=372`, `mean gross=+1.17bps`, `mean net8=-6.83bps`, `median net8=-12.26bps`
2. 跨币不稳且近似 ETH 单币幻想：
   - hold12 下仅 `ETH` 为正（`mean net8≈+2.40bps`），`BTC≈-16.33bps`、`SOL≈-6.45bps`
3. recent 月份未保住：
   - 2026-04: hold6 `mean net8≈-6.19bps`，hold12 `mean net8≈-6.68bps`

## 本轮结论（first verdict）
`dynamic momentum-cycle continuation × strongest-only router` 在 `5m strongest-only + 8bps` 口径下整体与 recent slice 均费后为负，且边际主要集中于 ETH 单币，不满足“非单币、可复制”要求；本轮直接收口 `background/P0`。

## 状态回写
- `Fresh intake slot.latest_result` 更新为本结论
- `Fresh intake slot.source_record` 指向本次 digest
- `Fresh intake slot.latest_result_record` 指向本日志
- `cycle_plan` 第 3 项：`status -> done`，`result` 写入新结论
- `Background pool.latest_parked` 与 `latest_parked_record` 追加本对象收口记录
