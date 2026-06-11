# bot3 optimization loop — triangular arb fresh intake 收口 background/P0

- 时间：2026-04-23 19:52 UTC
- 执行对象：`research/quant_digests/2026-04-23_1910_triangular-arb-fee-capacity-reality-check.md`
- 执行动作：fresh intake first verdict
- 对应 cycle_plan 槽位：1

## 本轮读取到的关键 runtime
- `Paper launch queue`: `none`（当前无需 P3 wiring）
- `Active P2 slot`: `none`
- `Surviving candidate slot`: `none`
- 因此前排合法主动作就是 cycle_plan 第一个 pending 的 fresh intake：`triangular arb fee / capacity reality check`

## 最小 decisive blocker
判断它是否留下**至少一个 after-fee、after-capacity、非单交易所 lucky-run 的可独立排队 pocket**，而不是只剩 execution-fee floor / capacity realism 提示。

## 本轮依据
直接采用 digest 内已经落地的最小公开复核：
- Binance Spot `BTCUSDT / LTCBTC / LTCUSDT`
- 约 `60s × 2Hz = 120` 个 snapshot
- 两个闭环方向 `USDT→BTC→LTC→USDT` 与 `USDT→LTC→BTC→USDT`
- 结果：
  - `gross_a_pos_count = 0 / 120`
  - `gross_b_pos_count = 0 / 120`
  - `max gross_a = -4.55 bps`
  - `max gross_b = -4.53 bps`
  - `avg gross_a = -8.00 bps`
  - `avg gross_b = -7.83 bps`
  - 薄腿 `LTCBTC` 平均 spread 约 `14.04 bps`，明显主导摩擦

## 结论
`triangular arb fee / capacity reality check` 本轮 fresh intake first verdict 直接收口 `background/P0`：最小 public live probe 连**无费 gross** 都未出现正闭环（`120/120` snapshot 两个方向均不为正，最佳也仍约 `-4.5bps`），说明当前可见价值没有留下任何 after-fee、after-capacity、非单 venue lucky-run 的独立 tri-arb pocket；它只诚实保留为 `net executable edge / thin-leg veto / multi-leg execution realism` 的 shared execution gate 提示，而不是值得前排保留的新 raw alpha 对象。

## 写回 runtime 的最小必要变化
- `Fresh intake slot.latest_result` 更新为上述 `background/P0` verdict
- `Fresh intake slot.latest_result_record` 指向本日志
- `Background pool.latest_parked` 追加本对象的收口结论
- `Background pool.latest_parked_record` 追加本日志
- `cycle_plan[1]` 写回 result/status=`done`

## 备注
- 本轮没有产生 `keep_P1 / promote_P2 / promote_P3`，因此无需分配新 Rank。
- 本轮结论已改变系统认知，属于真实推进；尾部按要求尝试刷新首页并发送中文邮件摘要。
