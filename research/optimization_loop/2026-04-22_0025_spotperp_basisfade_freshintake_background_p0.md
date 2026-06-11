# bot3 optimization loop — spot↔perp basis z-score fade fresh intake first verdict

- Time: 2026-04-22 00:25 UTC
- Cycle item: `research/quant_digests/2026-04-21_2359_spotperp-delta-neutral-basisfade-alpha.md`
- Action type: `fresh intake first verdict`

## What I checked
按 cycle_plan 第 1 项，只补 1 个最小 decisive blocker：这条 `spot↔perp basis z-score fade` 在当前 short-cycle desk 口径下，是否已经通过最小 `execution realism / honesty`，足以保留为 `keep_P1`；或者它是否只是一个 `maker-first / inventory-aware` 壳，当前不值得前排保留。

本轮直接采用 digest 已落库的最小公开复核结果：
- `reports/artifacts/quant_digests/delta_basis_spreadfade_summary_2026-04-21.csv`
- `reports/artifacts/quant_digests/delta_basis_spreadfade_trades_2026-04-21.csv`

## Minimal honesty result
公开可复核的 `BTCUSDT/ETHUSDT`、`5m/15m` probe 确认：
- `15m BTC`: `122` 笔，`gross +2.14bps/笔`
- `15m ETH`: `94` 笔，`gross +1.78bps/笔`
- `5m BTC`: `332` 笔，`gross +2.06bps/笔`
- `5m ETH`: `239` 笔，`gross +1.81bps/笔`

也就是说，**basis 确实会回归，且 gross 几乎每笔都赚钱**；但它的常态厚度被锁在约 `1.8–2.1bps/笔`，远低于 repo / desk 所需的现实四腿摩擦。

同一份 summary 已直接给出粗成本梯度：
- `28bps round-trip` 后，各组 `net_mean_bps` 约 `-25.86 ~ -26.22bps/笔`
- `40bps round-trip` 后，各组 `net_mean_bps` 约 `-37.86 ~ -38.22bps/笔`

交易明细也表明这不是少数极端大赚事件堆出来的厚尾 pocket；相反，绝大部分交易都只是非常稳定地赚到 `~1.5–3bps` gross，然后被现实摩擦整体吞没。

## Verdict
本轮 fresh intake **直接收口 `background/P0`**。

原因不是“basis 不回归”，而是：
1. 当前可见 pocket 只在 `BTC/ETH`、`5m/15m` 上稳定呈现极薄 gross；
2. 这份公开证据没有证明存在至少两个非单一币 / 非单一窗口、且能跨过最小现实四腿摩擦的 after-cost pocket；
3. 因而它现在更像一条 **maker-first / event-conditioned / inventory-aware 的 relative-value 执行壳**，而不是当前值得前排保留的 standalone raw alpha。

按 policy，这已经足够回答首判，不保留 survivor，也不分配新 Rank。

## Runtime-impact sentence
`spot↔perp basis z-score fade` 的 fresh intake first verdict 已诚实收口 `background/P0`：公开 Binance `BTC/ETH` `5m/15m` 复核虽确认 basis 回归方向稳定存在，但常态 gross 仅约 `1.8–2.1bps/笔`，在 repo 自带现实四腿摩擦梯度下稳定转成约 `-25.9~-38.2bps/笔`，没有留下至少两个非单一币/单一窗支撑的 after-cost pocket，因此它当前只适合作为 maker-first / inventory-aware relative-value 执行壳提示，不值得前排保留。
