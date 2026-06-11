# stablecoin cross-venue gap fresh intake：background/P0

- 时间：2026-04-18 21:20 UTC
- 对象：`research/quant_digests/2026-04-18_2017_stablecoin-crossvenue-gap-shell.md`
- 执行动作：fresh intake 最小首判，只补 `fee tier + top-book size + gap duration` 这一条 honesty / execution realism 轴
- 结论：`inventory-funded stablecoin cross-venue quote-gap convergence` 当前不保留前排，直接收口 `background/P0`

## 本轮读取到的最小证据
- digest 自带公开快检只覆盖 `8` 次采样、`4` 个 stablecoin pairs、`4` 个 venue。
- `USDCUSDT / FDUSDUSDT / FDUSDUSDC` 在快检中都没有正向 cross-venue top-of-book gap；可见 pocket 基本只剩 `TUSDUSDT`。
- `TUSDUSDT` 的正向 pocket 共 `16` 次，median 约 `3.50bps`，`p90/max≈4.00bps`，主要是 `MEXC sell / KuCoin buy` 与少量 `Binance sell / KuCoin buy`。
- 这个 gross 量级只比 summary 里写出的超乐观 break-even 略高：`each_leg_fee=0.5bps` 时 breakeven 约 `3.00bps`，`each_leg_fee=1.0bps` 时 breakeven 约 `2.00bps`；一旦再加最小滑点、未成交、或 inventory rebalance buffer，就会把 `3.5~4.0bps` 的可见 pocket 吃掉大半甚至全部。
- 当前 artifact 只证明“顶档报价曾出现过薄正差”，没有给出能支撑独立策略成立的 top-book size、持续时间分布、成交后可兑现容量，且样本几乎完全被单一标的 `TUSDUSDT` 主导。

## 为什么这一步足以直接收口
本轮要求回答的是：公开 pocket 在双边 fee tier、top-book size、gap duration 口径下，是否还能保住可独立承接的 after-cost 净边际，而不是只剩 maker/VIP 幻觉。

当前答案是否定的：
1. **fee realism 不过关**：唯一可见 pocket 只有 `3.5~4.0bps` gross，离普通 taker + 最小滑点/再平衡 buffer 的可兑现净边际太近。
2. **size realism 缺失**：没有 top-book quantity / depth 证据，无法证明不是仅能成交极薄名义金额的 quote print。
3. **duration realism 缺失**：只有稀疏快照，没有 gap half-life / survive-next-refresh 证据，不能证明 inventory-funded 两腿能在同一机会窗内完成。
4. **distinctness 不足**：如果必须把成立条件收窄到 `单一 TUSDUSDT + maker/VIP + 预布库存 + 极薄顶档`，它更像 monitoring shell / 特定 venue pocket，而不是现在就值得前排保留的独立 raw-alpha front object。

## runtime verdict
- first verdict：`background/P0`
- result sentence：公开 stablecoin cross-venue pocket 目前几乎只剩 `TUSDUSDT` 单一标的的 `3.5~4.0bps` 顶档薄差，且缺少 top-book size 与 gap 持续时间证据，未能证明在诚实成本后仍是可独立承接的 after-cost alpha。
- reader-facing 影响：将该 fresh intake 直接收口到 background，不分配 Rank，不进入 survivor。

## 证据位置
- `research/quant_digests/2026-04-18_2017_stablecoin-crossvenue-gap-shell.md`
- `reports/artifacts/quant_digests/2026-04-18_stablecoin_crossvenue_gap_probe_summary.json`
- `reports/artifacts/quant_digests/2026-04-18_stablecoin_crossvenue_gap_probe_rows.csv`
