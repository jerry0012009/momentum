# 2026-04-18 12:17 UTC — partial-moment TSMOM reversal overlay fresh intake first verdict

## Target
- `research/quant_digests/2026-04-18_0508_partialmoment-tsmom-reversal-overlay.md`

## Why this step
- 按当前 `cycle_plan` 执行最前的 pending 小点（item2）。
- item1 已完成，且当前 `Surviving candidate slot = none`、`Active P2 slot = none`，因此该 conditional fresh intake 前置条件成立。

## Minimal evidence used
- digest 内论文主结论：partial-moment overlay 的价值主要是 `reversal-risk overlay / veto / size-down`，不是新的 raw alpha。
- digest 内 Binance USDⓈ-M `15m/5m` lightweight portability probe：
  - `15m` 上，论文式 `MTSM-S2` 固定动作表对 `BTC/ETH/SOL/BNB` 没有稳定增益，多个主参数点反而显著劣于原始 TSM。
  - `5m` 上，局部资产只能把坏结果变得没那么坏，但并未形成可直接上线的稳定 after-cost 改善；`ETH 5m` 还明显被拖后腿。
- 因而当前唯一诚实可迁移结论是：
  - 可保留的只是 `partial-moment asymmetry` 作为 shared `veto / size-down / hold-shortening` 框架；
  - 不能把它当成新的独立 shared overlay front object，更不能按论文固定 `reverse-all` 动作表直接承接。

## Verdict
`partial-moment reversal veto` 在当前 crypto short-cycle portability 下没有证明自己是一个值得前排保留的新 shared overlay front object：论文式固定动作表在 Binance `15m/5m` 上不增益、且常常劣化母体；当前可诚实保留的只是一条依附既有 trend 母体的 `veto / size-down` 设计提示，因此本轮 fresh intake 直接收口 `background/P0`。

## Runtime impact
- 将该 item 标记为 `done`。
- 更新 `Fresh intake slot` 为本对象的最新结论与记录。
- 追加到 `Background pool.latest_parked` / `latest_parked_record`。
- 不分配 Rank：因为 first verdict 直接是 `background/P0`，未达到 `keep_P1` 或更高。
