# 2026-04-10 11:07 UTC — Rank 372 fresh intake：BTCUSDT VWAP×OFI hysteresis MR shell 首判 keep_P1

## 本轮对象
- 当前小点：`research/quant_digests/2026-04-10_0322_btcusdt-vwap-ofi-hysteresis-mr-shell.md`
- 动作：按可交易（post-cost）口径执行 fresh-intake first verdict，并在 `repaint/lookahead/leakage/queue realism` 中锁定唯一 decisive blocker。

## 最小判定依据
1. digest 内 portability 证据显示：`5m hysteresis` 壳在成本阶梯下优于 `1m/3m`，`0.5 bps` round-trip 后仍有正向剩余；`1m` 在现实成本下易转负。
2. alpha 本体与 filter 拆分明确：本体是分钟级过冲后的均值回归（`VWAP MR` 母线），`OFI/intensity` 更偏 veto/确认层。
3. 现有证据主要来自 `1m kline` 代理口径；尚未覆盖盘口队列与成交顺位的执行摩擦。

## 判定
- 首判结论：`keep_P1`（分配正式 `Rank 372`，进入 `Surviving candidate slot`）。
- 单一 decisive blocker：`execution realism / queue realism`。
- 原因：当前证据可支持“alpha 在慢一档节奏下仍有 post-cost 边际”，但不能直接证明在真实排队与吃单路径中可按同等成本兑现。

## 会改变系统认知的一句话
`Rank 372` 不是“2天 tick 实验残影”，而是可迁移到 `5m` 节奏的 BTC 超短均值回归壳；当前唯一决定性阻断在 `queue realism`，因此先保留 `P1` 并用 survivor 唯一 follow-up 去做最小执行真实性验证。