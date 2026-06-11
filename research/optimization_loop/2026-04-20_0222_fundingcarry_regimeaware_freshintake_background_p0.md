# funding carry regime-aware child execution fresh intake first verdict

- 时间：2026-04-20 02:22 UTC
- 执行者：bot3
- cycle_plan item：1
- target：`research/quant_digests/2026-04-19_2240_fundingcarry-regimeaware-childexec-alpha.md`
- verdict：`background/P0`

## 本轮只执行的小点
对 `8h positive funding carry × 15m child execution` 做 fresh intake first verdict：只补最小 blocker——在 recent Binance funding 已转薄/偏负的 regime 下，这条线是否还存在可被明确 admission gate 描述的独立 carry pocket。

## 证据
- digest/repo 给出的 base alpha 清楚：`long spot / short perp` 收 positive funding，`15m/5m` 只应作为 child execution / cost control。
- 本地 recent Binance funding probe（artifact: `reports/artifacts/quant_digests/2026-04-19_funding_carry_no_reversal_summary.csv`）显示近 `87` 个 8h observations：
  - `BTCUSDT` mean funding `-0.095bps / 8h`，positive pct `40.23%`，`>1bp` 正 funding count `0`；
  - `ETHUSDT` mean funding `-0.166bps / 8h`，positive pct `44.83%`，`>1bp` 正 funding count `0`。
- 因此 repo 默认 `entry=1bp/8h` admission gate 在当前 recent regime 基本不触发；若强行降到 `0.25~0.5bp`，当前材料仍没有证明双腿建仓/平仓、库存、spot/perp friction 与 child execution 后仍有可复制 after-cost pocket。

## 结论
`8h positive funding carry × 15m child execution` 的 fresh intake first verdict 已诚实收口：recent BTC/ETH funding probe 显示近 87 个 8h observations 平均 funding 已转负（BTC -0.095bps、ETH -0.166bps）且 `>1bp` 正 funding 事件为 0，repo 默认 admission gate 在当前 regime 基本不触发；在没有可定义 recent carry pocket 与双腿 child-execution 后成本余量前，本轮直接收口 `background/P0`。

## runtime 写回
- `Fresh intake slot.latest_result` 已更新为本 verdict。
- `cycle_plan` item 1 已写为 `done`。
- `Background pool.latest_parked/latest_parked_record` 已追加本轮收口记录。
