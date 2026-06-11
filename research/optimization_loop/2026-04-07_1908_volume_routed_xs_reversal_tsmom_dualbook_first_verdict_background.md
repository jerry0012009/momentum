# 2026-04-07 19:08 UTC — volume-routed XS reversal × TSMOM dual-book first verdict

## 本轮对象
- target: `research/quant_digests/2026-04-07_1830_volume-routed-xs-reversal-tsmom-dualbook-alpha.md`
- action: 判断 `low-volume XS loser-bounce × high-volume TSMOM router` 是否构成独立于既有 `XS reversal / volume-conditioned momentum router` 家族的新 raw alpha 主语

## 结论
`low-volume XS loser-bounce × high-volume TSMOM router` 没有提供独立于既有 `vol-z routed TSMOM / XS reversal dual-book` 家族的新 raw alpha 主语，因此本轮诚实收口为 `background / P0`，不进入 survivor。

## 依据
1. 当前 intake 对象与 `research/quant_digests/2026-04-04_0347_volume-router-tsmom-xsreversal-dualbook-alpha.md` 指向同一个 repo（`PThrower/crypto-start-arb`）与同一套 base shell：`TSMOM + XS reversal` 双书，`volume z-score` 只负责在两本书间路由与缩放。
2. 4 月 7 日这份 digest 的改写重点只是把叙述重心偏向 `low-volume loser-bounce` 这条腿，但对象自己的策略拆解仍保留“低量 reversal / 高量 momentum / tanh(vol_z) 连续路由 / 双书组合”的完整结构，没有引入新的独立 alpha 主语、独立执行壳或新的可迁移成本边界。
3. 因此它更像对既有 `volume router` 家族的一次 desk 化重述，而不是新 intake。继续把它当新鲜对象推进，只会重复占用 fresh intake 配额。

## runtime 决策
- verdict: `background / P0`
- rank: 不分配（未达到 `keep_P1`）
- survivor: 不进入
- slot effect: 仅更新 fresh intake 最新结论；不改动 `Surviving candidate` / `Active P2` / `Paper launch queue`

## 相关旧证据
- `research/quant_digests/2026-04-04_0347_volume-router-tsmom-xsreversal-dualbook-alpha.md`

## 本轮一句话 result
`low-volume XS loser-bounce × high-volume TSMOM router` 没有提供独立于既有 `vol-z routed TSMOM / XS reversal dual-book` 家族的新 raw alpha 主语，因此本轮诚实收口为 `background / P0`。
